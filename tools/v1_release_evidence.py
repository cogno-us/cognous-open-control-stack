#!/usr/bin/env python3
"""Gate complete same-revision evidence for seven synthetic v1 extension batches."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'v1-reference-extension-evidence/4'
BATCHES = {
    'environment': ('test_reference_environment', 6, None),
    'governed-context': ('test_context_memory_profile', 21, 'result.json'),
    'institutional-review': ('test_institutional_review_profile', 16, 'result.json'),
    'temporal-refund': ('test_temporal_refund_profile', 15, 'trajectory.json'),
    'context-action': ('test_context_action_profile', 16, 'result.json'),
    'notification': ('test_notification_profile', 8, 'result.json'),
    'recovery': ('test_sqlite_recovery_profile', 9, None),
}
DEMO_PROFILES = {'governed-context':'governed-context/1','institutional-review':'institutional-review/1',
                 'temporal-refund':'two-step-synthetic-refund/1','context-action':'context-action/2','notification':'synthetic-notification/1'}
DEPENDENT = {'temporal-refund', 'context-action', 'notification'}
COMPONENTS = ('control_plane','moltbot_safe','action_manifest','gax_imx_transport','replay_bundle')


def require(condition, message):
    if not condition: raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), 'symlink artifact rejected')
        if path.is_file() and path != root / 'batch-report.json':
            result[path.relative_to(root).as_posix()] = sha(path)
    return result


def evidence(root, batch, lock_path):
    module, expected, demo = BATCHES[batch]
    root = Path(root)
    tree = ET.parse(root / 'tests.xml')
    cases = list(tree.getroot().iter('testcase'))
    require(len(cases) == expected, 'test population mismatch')
    identities = [(c.get('classname'), c.get('name')) for c in cases]
    require(len(set(identities)) == expected and all(name and cls and cls.split('.')[-1] == module for cls,name in identities), 'test identity mismatch')
    require(not any(c.find(tag) is not None for c in cases for tag in ('failure','error','skipped')), 'failed, errored, or skipped required case')
    # Also reject suite-level failures/errors that lack a normal testcase.
    require(not list(tree.getroot().iter('failure')) and not list(tree.getroot().iter('error'))
            and not list(tree.getroot().iter('skipped')), 'JUnit contains unsuccessful result')
    environment = json.loads((root / 'environment.json').read_text())
    require(environment['schema_version'] == '1.0.0' and environment['purpose'] == 'local-reference-prerequisites', 'environment contract mismatch')
    require(environment['component_lock_sha256'] == sha(lock_path), 'environment lock mismatch')
    require(environment['reference_prerequisites_observed'] is True and environment['deployment_qualified'] is False
            and environment['authorizing'] is False, 'unsupported environment assurance')
    checks = environment['checks']
    require(len(checks) == 5 and {c['id'] for c in checks} == {'linux','python','wal','competing_writer_excluded','rollback_preserved'}
            and all(c['status'] == 'observed' for c in checks), 'missing or unverified prerequisites')
    require(environment['environment']['os'] == 'Linux', 'unqualified OS')
    require(environment['environment']['python'].split('.')[:2] in (['3','11'],['3','12']), 'unqualified Python')
    if demo:
        value = json.loads((root / batch / demo).read_text())
        require(value['profile'] == DEMO_PROFILES[batch], 'demonstration profile mismatch')
        require(value['qualified'] is True and value['production_ready'] is False, 'demonstration failed or inflated scope')
    if batch in DEPENDENT:
        provenance = json.loads((root / batch / 'provenance.json').read_text())
        lock = json.loads(Path(lock_path).read_text())
        pins = {name: lock['components'][name].get('sha') or lock['components'][name]['accepted_sha'] for name in COMPONENTS}
        require(provenance['tested_revisions'] == pins and provenance['component_lock_sha256'] == sha(lock_path), 'component provenance mismatch')
        require(type(provenance['returncode']) is int and provenance['returncode'] == 0, 'demonstration interrupted or failed')
    return {'tests': expected, 'passed': expected, 'failures': 0, 'errors': 0, 'skipped': 0,
            'environment': environment['environment']}


def record(root, batch, revision, lock_path):
    root = Path(root)
    require(batch in BATCHES, 'unknown batch')
    require(len(revision) == 40 and all(c in '0123456789abcdef' for c in revision), 'full source revision required')
    values = evidence(root, batch, lock_path)
    report = dict(contract=CONTRACT, batch=batch, source_revision=revision, component_lock_sha256=sha(lock_path),
                  results=values, artifacts=inventory(root), authorizing=False, production_ready=False)
    with (root / 'batch-report.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return report


def aggregate(root, revision, lock_path, jobs_status="success"):
    root = Path(root)
    result = dict(contract=CONTRACT, source_revision=revision, component_lock_sha256=sha(lock_path),
                  jobs_status=jobs_status, scheduled_batches=len(BATCHES), scheduled_tests=sum(v[1] for v in BATCHES.values()),
                  results=[], errors=[], valid=False, authorizing=False, production_ready=False,
                  full_default_release_qualified=False)
    try:
        require(jobs_status == 'success', 'required batch jobs did not all succeed')
        paths = list(root.glob('*/batch-report.json'))
        require(len(paths) == len(BATCHES), 'missing or unexpected batch reports')
        require({p.name for p in root.iterdir()} == {p.parent.name for p in paths}, 'unreported artifact directory or file')
        seen = set()
        for path in sorted(paths):
            report = json.loads(path.read_text())
            batch = report['batch']
            require(batch in BATCHES and batch not in seen, 'duplicate or unexpected batch')
            seen.add(batch)
            require(report['contract'] == CONTRACT and report['source_revision'] == revision, 'mixed revision or contract')
            require(report['component_lock_sha256'] == sha(lock_path), 'mixed component lock')
            require(report['authorizing'] is False and report['production_ready'] is False, 'unsupported scope')
            require(report['artifacts'] == inventory(path.parent), 'missing, changed, or unexpected artifacts')
            derived = evidence(path.parent, batch, lock_path)
            require(report['results'] == derived, 'producer totals differ from derived results')
            result['results'].append(dict(batch=batch, **derived))
        require(seen == set(BATCHES), 'incomplete coverage')
        result['valid'] = True
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
        result['errors'].append(str(exc))
    result['verified_batches'] = len(result['results'])
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=('record','aggregate'))
    ap.add_argument('--results-dir',type=Path,required=True)
    ap.add_argument('--batch',choices=BATCHES)
    ap.add_argument('--revision')
    ap.add_argument('--jobs-status', choices=('success','failure','cancelled','skipped'))
    ap.add_argument('--lock',type=Path,default=ROOT / 'component-lock.json')
    args = ap.parse_args()
    revision = args.revision or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if args.command == 'record':
        if not args.batch: ap.error('record requires --batch')
        result = record(args.results_dir,args.batch,revision,args.lock)
    else:
        if not args.jobs_status: ap.error('aggregate requires --jobs-status from the scheduler')
        result = aggregate(args.results_dir,revision,args.lock,args.jobs_status)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if args.command == 'record' or result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
