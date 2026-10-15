#!/usr/bin/env python3
"""Regenerate the S4 frozen manifest and exact-selected provenance from local Git objects.
Clone component-lock repositories into COMPONENTS_ROOT/<component> first; no fetch or publishing occurs.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tomllib
import zipfile

BASE = '592919dd95396f3f6164cf0ceec1fd15c065691b'
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def sha(b):
    return hashlib.sha256(b).hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def read(repo, revision, path):
    return git(repo, 'show', revision + ':' + path)


def paths(repo, revision):
    return git(repo, 'ls-tree', '-rz', '--name-only', revision).decode().rstrip('\0').split('\0')


def manifest():
    all_paths = paths(REPO, BASE)
    # This defines the proposal once; the generated manifest is the explicit allowlist.
    excluded_prefixes = ('examples/', 'collateral/', 'benchmarks/', '.github/', '.oss-scanner/',
                         'docs/private-evaluator/', 'docs/workstreams/', 'docs/verification/')
    included = [p for p in all_paths if not p.startswith(excluded_prefixes) and p != '.gitignore']
    original = json.loads(read(REPO, BASE, 'docs/releases/selected-notices.json'))
    copies = {n['retained_path']: n for c in original['components'] for n in c['notices']}
    required = ['LICENSE', 'NOTICE'] + sorted(copies)
    rows = []
    for p in included:
        evidence = ['LICENSE', 'NOTICE']
        reason = 'Hub documentation or qualification source under hub license evidence; rights review pending'
        if p in copies:
            evidence = [p]
            reason = 'Original selected-component notice retained byte-for-byte; not component source'
        rows.append(dict(path=p, source_commit=BASE, sha256=sha(read(REPO, BASE, p)),
                         licensing_state='evidence_verified', license_evidence=evidence,
                         inclusion_rationale=reason))
    lock = json.loads(read(REPO, BASE, 'component-lock.json'))
    external = [dict(component=k, repository=c['repository'], selected_sha=c.get('sha', c.get('accepted_sha')),
                     redistributed=False, rights_accepted=False,
                     licensing_state='unresolved' if k in ('prp', 'tfa') else 'notice_evidence_only',
                     later_licensing_head_not_selected=c.get('licensing_head')) for k,c in lock['components'].items()]
    save('manifest.json', dict(schema='cognous.publication-inventory/1', lane='S4 / D', source_commit=BASE,
        package_scope='Hub-only documentation and qualification-source review kit; all generated example payloads excluded; not a complete offline runnable distribution',
        rights_acceptance='pending_accountable_review', reference_release_authorized=False,
        production_deployment_authorized=False, required_notices=required, files=rows,
        excluded_files=[dict(path=p, source_commit=BASE, sha256=sha(read(REPO, BASE, p)),
            reason='Outside bounded review-kit allowlist; preserved in tracked source; separate rights and S5 safety review required') for p in all_paths if p not in included],
        external_components=external))


def dependency_manifest(p):
    n = PurePosixPath(p).name.lower()
    return (n in {'pyproject.toml','package.json','package-lock.json','pnpm-lock.yaml','yarn.lock',
                  'poetry.lock','uv.lock','cargo.toml','cargo.lock','go.mod','go.sum','gemfile','gemfile.lock',
                  'package.swift','package.resolved','bun.lockb','bun.lock'}
            or n.startswith('requirements') and n.endswith(('.txt','.lock'))
            or n.endswith(('.csproj','.gradle','.gradle.kts','.podspec')))


def audit_components(root):
    lock = json.loads(read(REPO, BASE, 'component-lock.json'))
    previous = json.loads(read(REPO, BASE, 'docs/releases/selected-notices.json'))
    expected = {c['component']:c for c in previous['components']}
    ledger = []
    for key, c in lock['components'].items():
        repo = root / key
        revision = c.get('sha', c.get('accepted_sha'))
        ps = paths(repo, revision)
        notices = [p for p in ps if any(n in PurePosixPath(p).name.lower() for n in ('license','licence','notice','copying','copyright'))]
        if set(notices) != {n['path'] for n in expected[key]['notices']}:
            raise ValueError('notice path difference ' + key)
        nr = []
        for old in expected[key]['notices']:
            raw = read(repo, revision, old['path'])
            blob = sha(raw)
            if (blob != old['sha256'] or raw != read(REPO, BASE, old['retained_path'])
                    or git(repo, 'rev-parse', revision + ':' + old['path']).decode().strip() != old['blob_sha']):
                raise ValueError('notice provenance mismatch ' + key + '/' + old['path'])
            terms = ('MIT' if raw.lstrip().startswith(b'MIT License') else 'Apache-2.0' if b'Apache License' in raw[:100] else 'CC-BY-4.0' if b'Creative Commons Attribution 4.0' in raw[:1000] else 'attribution/scope notice; original text controls')
            nr.append(dict(old, reverified_against_selected_git_object=True, terms_observed=terms))
        deps = []
        for p in ps:
            if dependency_manifest(p):
                b = read(repo, revision, p)
                declarations = []
                name = PurePosixPath(p).name
                if name == 'package.json':
                    obj = json.loads(b)
                    for scope in ('dependencies','devDependencies','peerDependencies','optionalDependencies'):
                        declarations.extend(dict(scope=scope, name=n, requirement=r) for n,r in obj.get(scope,{}).items())
                elif name == 'pyproject.toml':
                    obj = tomllib.loads(b.decode())
                    for scope, values in [('project.dependencies',obj.get('project',{}).get('dependencies',[])),
                                          ('build-system.requires',obj.get('build-system',{}).get('requires',[]))]:
                        declarations.extend(dict(scope=scope, requirement=r) for r in values)
                    for scope, values in obj.get('project',{}).get('optional-dependencies',{}).items():
                        declarations.extend(dict(scope='project.optional-dependencies.'+scope, requirement=r) for r in values)
                elif name.startswith('requirements') and name.endswith('.txt'):
                    declarations = [dict(scope='requirements file',requirement=line.strip()) for line in b.decode().splitlines() if line.strip() and not line.lstrip().startswith('#')]
                deps.append(dict(path=p, sha256=sha(b), bytes=len(b), redistributed=False, declarations=declarations,
                                 source_url=f'https://raw.githubusercontent.com/{c["repository"]}/{revision}/{p}',
                                 coverage='manifest surface inventoried; transitive package rights not accepted'))
        # Read all PRP/TFA textual source for license indicators, but retain only paths/hashes publicly.
        text_scan = []
        if key in ('prp','tfa'):
            for p in ps:
                if PurePosixPath(p).suffix.lower() in ('.md','.yaml','.yml','.json','.py'):
                    b = read(repo, revision, p)
                    terms = sorted(set(re.findall(r'(?i)\b(?:licen[cs]e|copyright|cc0|public domain|apache|mit)\b', b.decode(errors='replace'))))
                    text_scan.append(dict(path=p, sha256=sha(b), licensing_terms_present=terms))
        pdfs = [dict(path=p, sha256=sha(read(repo, revision, p)), bytes=len(read(repo, revision, p)),
                     disposition='excluded; authoritative rights evidence required') for p in ps if p.lower().endswith('.pdf')]
        ledger.append(dict(component=key, repository=c['repository'], selected_sha=revision,
            tree_sha=git(repo,'rev-parse',revision+'^{tree}').decode().strip(), tracked_file_count=len(ps),
            notices=nr, security_paths=[p for p in ps if PurePosixPath(p).name.lower()=='security.md'],
            dependency_manifests=deps, selected_pdf_inventory=pdfs, textual_license_indicator_scan=text_scan,
            redistributed=False, rights_accepted=False,
            later_licensing_head_not_applied=c.get('licensing_head')))
    hub_deps = []
    for p in paths(REPO,BASE):
        if dependency_manifest(p):
            raw=read(REPO,BASE,p)
            hub_deps.append(dict(path=p,sha256=sha(raw),declarations=[line.strip().rstrip('\\').strip() for line in raw.decode().splitlines() if re.match(r'^[A-Za-z0-9_-]+==',line)],dependency_package_bytes_redistributed=False))
    save('dependencies.json',dict(source_commit=BASE,hub_dependency_manifests=hub_deps,
        s4_checker_dependencies='Python 3.11/3.12 standard library only; no pip/npm installs required or performed for S4 checks',
        reproduction_dependencies='Other hub qualification tools install dependencies and fetch components separately; their complete resolved environment is outside this package',
        transitive_clearance=False,component_declaration_source='selected-provenance.json dependency_manifests declarations and lock surfaces'))
    save('selected-provenance.json',dict(source_commit=BASE,lock_sha256=sha(read(REPO,BASE,'component-lock.json')),
        method='Complete local exact-commit Git trees; notice bytes compared to original retained copies and Git blob IDs',
        components=ledger))


def audit_artifacts():
    result = []
    for p in paths(REPO, BASE):
        if not (p.startswith(('examples/','collateral/','benchmarks/')) or p.lower().endswith(('.pdf','.zip','.tar.xz','.tar.gz','.tgz','.docx'))):
            continue
        b = read(REPO,BASE,p)
        row = dict(path=p,sha256=sha(b),bytes=len(b),redistributed=False,
                   source_archive_exposure=True,rights_acceptance='pending')
        if tarfile.is_tarfile(io.BytesIO(b)):
            members=[]
            with tarfile.open(fileobj=io.BytesIO(b)) as t:
                for m in t:
                    entry=dict(path=m.name,type=m.type.decode('ascii',errors='replace'),bytes=m.size)
                    if m.isfile():
                        raw=t.extractfile(m).read()
                        entry['sha256']=sha(raw)
                        entry['embedded_pdf']=raw.startswith(b'%PDF-')
                    members.append(entry)
            row['archive_members']=members
            row['inspection']='members enumerated and regular bytes hashed without extraction; not semantic/IP clearance'
        elif b.startswith(b'PK\x03\x04'):
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                row['archive_members']=[dict(path=n,sha256=sha(z.read(n))) for n in z.namelist() if not n.endswith('/')]
        else:
            row['inspection']='tracked bytes hashed; synthetic/generated classification from location, not semantic clearance'
        result.append(row)
    save('excluded-artifacts.json',dict(source_commit=BASE,artifacts=result,
        note='Custom-package exclusions do not remove tracked files from GitHub tag/source archives. No release/tag made.'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--components-root',type=Path,required=True)
    args=p.parse_args()
    manifest()
    audit_components(args.components_root.resolve())
    audit_artifacts()
    print('Generated frozen manifest, selected provenance and excluded artifact inventory')
