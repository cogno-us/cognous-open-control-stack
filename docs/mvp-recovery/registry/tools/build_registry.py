#!/usr/bin/env python3
"""Deterministic generator for the layered informational catalogue (non-authorizing).

    python3 -I docs/mvp-recovery/registry/tools/build_registry.py --sample [--out DIR]

Takes a dataset of un-finalized catalogue content (see load_partitions.py for the shape),
finalizes every record (layer, authority none, non-authorizing, digest), derives the L6
coverage projection, partitions deterministically by layer, source family and ID range,
and writes the root manifest. Stdlib only. It executes no rule and grants no authority.
Output is byte-identical for identical input.
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_ROOT = os.path.dirname(HERE)


def _load(name):
    spec = importlib.util.spec_from_file_location('ocs_catalogue_' + name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _load('validate_registry')

REGISTRY_VERSION = '0.1.0'
SCHEMA_VERSIONS = {'coverage': 'ocs-catalogue/coverage/0', 'crosswalk': 'ocs-catalogue/crosswalk/0',
                   'evidence': 'ocs-catalogue/evidence/0', 'fixtures': 'ocs-catalogue/fixtures/0',
                   'manifest': 'ocs-catalogue/manifest/0', 'partition': 'ocs-catalogue/partition/0',
                   'rules': 'ocs-catalogue/rules/0', 'scenarios': 'ocs-catalogue/scenarios/0',
                   'tests': 'ocs-catalogue/tests/0', 'lineage_sets': 'ocs-catalogue/lineage_sets/0'}
DEFAULT_MAX_PER_PARTITION = 200
# records per committed partition file for the real catalogue (any layer not listed uses DEFAULT_MAX_PER_PARTITION)
REAL_MAX_PER_PARTITION = {'rules': 300, 'scenarios': 300, 'tests': 400, 'fixtures': 300, 'evidence': 1500, 'crosswalk': 2500, 'coverage': 800, 'lineage_sets': 10}
TOOL_FILES = ('build_registry.py', 'validate_registry.py', 'load_partitions.py')
LAYER_ORDER = ('rules', 'scenarios', 'tests', 'fixtures', 'evidence', 'crosswalk', 'coverage', 'lineage_sets')


def tool_revision():
    files = {}
    for name in TOOL_FILES:
        if not os.path.exists(os.path.join(HERE, name)):
            continue
        with open(os.path.join(HERE, name), 'rb') as fh:
            files[name] = V.sha256_bytes(fh.read())
    return {'name': 'ocs-catalogue-tools', 'files': files, 'revision': V.canonical_digest(files)}


def family_of(layer, rec):
    if layer == 'lineage_sets':
        raw = 'L'
    elif layer == 'crosswalk':
        raw = rec['raw_set']
    elif layer == 'evidence':
        raw = rec['source_commitment']['set_id']
    elif layer == 'coverage':
        raw = _id_family(rec['subject_id'])
    else:
        raw = _id_family(rec['catalogue_id'])
    return re.sub(r'[^A-Za-z0-9_]', '_', raw) or 'X'


def _id_family(cid):
    m = re.match(r'[A-Za-z0-9]+-([A-Za-z0-9]+)', cid)
    return m.group(1) if m else 'X'


def finalize(layer, rec):
    out = dict(rec)
    if layer != 'crosswalk':
        out['layer'] = layer
    out.setdefault('annotations', {})
    if layer == 'evidence':
        out.setdefault('relationships', [])
    out['authority'] = 'none'
    if layer != 'crosswalk':
        out['non_authorizing'] = True
        out['digest'] = V.digest_of(out)
    return out


def write_partitions(root, layer, records, max_per, manifest_parts, compact=False):
    fam = {}
    for r in records:
        fam.setdefault(family_of(layer, r), []).append(r)
    for family in sorted(fam):
        recs = sorted(fam[family], key=lambda r: V.entry_key(layer, r))
        for n in range(0, len(recs), max_per):
            chunk = recs[n:n + max_per]
            rel = '%s/%s-%04d.json' % (V.LAYER_DIRS[layer], family, n // max_per + 1)
            env = {'profile': 'ocs-catalogue-partition/0', 'layer': layer, 'partition_id': rel[:-5],
                   'authority': 'none', 'non_authorizing': True, 'records': chunk}
            if compact:
                env['encoding'] = V.ENCODING
                env['strings'], env['shapes'], env['records'] = V.encode_records(chunk)
                data = V.dump_compact(env)
            else:
                data = V.dump_file(env)
            full = os.path.join(root, *rel.split('/'))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'wb') as fh:
                fh.write(data)
            manifest_parts.append({'path': rel, 'layer': layer, 'sha256': V.sha256_bytes(data), 'record_count': len(chunk),
                                   'first_key': V.entry_key(layer, chunk[0]), 'last_key': V.entry_key(layer, chunk[-1])})


def _write_artifact(adir, kind, records, extra_name):
    env = {'profile': 'ocs-catalogue-artifact/0', 'kind': kind, 'authority': 'none', 'non_authorizing': True,
           'encoding': V.ENCODING}
    env['strings'], env['shapes'], env['records'] = V.encode_records(records)
    data = V.dump_compact(env)
    sha = V.sha256_bytes(data)
    name = '%s.%s.json' % (extra_name, sha[7:19])
    os.makedirs(adir, exist_ok=True)
    with open(os.path.join(adir, name), 'wb') as fh:
        fh.write(data)
    return {'artifact_id': extra_name, 'kind': kind, 'path': 'artifacts/' + name, 'sha256': sha, 'record_count': len(records),
            'bytes': len(data), 'committed': False}


def schema_pins(root):
    out = {}
    sdir = os.path.join(root, 'schemas')
    if not os.path.isdir(sdir):
        sdir = os.path.join(REGISTRY_ROOT, 'schemas')
    for fn in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
        if fn.endswith('.json'):
            with open(os.path.join(sdir, fn), 'rb') as fh:
                out[fn] = V.sha256_bytes(fh.read())
    return out


def build(dataset, root, max_per=DEFAULT_MAX_PER_PARTITION, layout='full', artifacts_dir=None):
    """Write the whole catalogue under root. root must not already hold partition files.

    layout 'full' writes every record inline as indented JSON. layout 'compact' writes the same records in the
    interned-shapes encoding, keeps only an index form of the evidence and crosswalk layers in the partitions and
    writes the full evidence records, full crosswalk rows and the G3 relationship rows as content-addressed
    artifacts under artifacts_dir (never committed; the manifest describes and pins them).
    """
    compact = layout == 'compact'
    if compact and not artifacts_dir:
        raise ValueError('the compact layout needs an artifacts directory')
    per = max_per if type(max_per) is dict else {k: max_per for k in LAYER_ORDER}
    layers = {}
    for layer in ('rules', 'scenarios', 'tests', 'fixtures', 'evidence', 'lineage_sets'):
        layers[layer] = [finalize(layer, r) for r in dataset.get(layer, [])]
    kinds = {e['evidence_digest']: e['evidence_kind'] for e in layers['evidence']}
    layers['coverage'] = list(V.derive_coverage(layers['rules'], layers['scenarios'], kinds).values())
    full_crosswalk = [finalize('crosswalk', r) for r in dataset.get('crosswalk', [])]
    external = []
    if compact:
        full_evidence = layers['evidence']
        layers['evidence'] = [V.slim_evidence(e) for e in full_evidence]
        layers['crosswalk'] = [V.slim_crosswalk(r) for r in full_crosswalk]
        external.append(_write_artifact(artifacts_dir, 'evidence_records', sorted(full_evidence, key=lambda e: e['evidence_digest']), 'evidence-records'))
        external.append(_write_artifact(artifacts_dir, 'crosswalk_rows', sorted(full_crosswalk, key=lambda r: V.entry_key('crosswalk', r)), 'crosswalk-rows'))
        external.append(_write_artifact(artifacts_dir, 'relationship_rows', sorted(dataset.get('relationship_rows', []), key=lambda r: r['relationship_id']), 'relationship-rows'))
    else:
        layers['crosswalk'] = full_crosswalk
    parts = []
    for layer in LAYER_ORDER:
        write_partitions(root, layer, layers[layer], per[layer], parts, compact=compact)
    records = []
    for rec in dataset.get('registry_records', []):
        rel = '%s/%s/%s.%s.json' % (V.LAYER_DIRS['rules'], V.SAMPLE_REGISTRY_DIR, rec['registry_id'], rec['digest'][7:19])
        full = os.path.join(root, *rel.split('/'))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'wb') as fh:
            fh.write(V.dump_file(rec))
        records.append({'registry_id': rec['registry_id'], 'record_digest': rec['digest'], 'path': rel})
    per_set = {}
    for r in full_crosswalk:
        per_set.setdefault(r['raw_set'], {})[r['raw_index']] = r['raw_digest']
    inventory = []
    for s in sorted(dataset['source_inventory'], key=lambda s: s['set_id']):
        got = per_set.get(s['set_id'], {})
        ordered = [got[i] for i in sorted(got)]
        inventory.append({'set_id': s['set_id'], 'description': s['description'], 'raw_record_count': len(ordered),
                          'inventory_sha256': V.canonical_digest(ordered),
                          'source_repo_revisions': sorted(s['source_repo_revisions'], key=lambda x: (x['repo'], x['revision']))})
    manifest = {'profile': 'ocs-catalogue-manifest/0', 'schema_version': 0, 'registry_version': dataset.get('registry_version', REGISTRY_VERSION),
                'synthetic_sample': bool(dataset.get('synthetic_sample', False)), 'canonical_profile': 'rfc8785-jcs',
                'status': 'HOLD', 'authority': 'none', 'non_authorizing': True, 'schema_versions': dict(SCHEMA_VERSIONS),
                'layout': layout, 'schema_files': schema_pins(root), 'external_artifacts': external,
                'regeneration': dict(dataset.get('regeneration') or {}),
                'source_inventory': inventory, 'partitions': sorted(parts, key=lambda p: p['path']),
                'layer_counts': {k: len(v) for k, v in sorted(layers.items())}, 'unresolved_accounting': V.unresolved_accounting(layers), 'registry_records': sorted(records, key=lambda r: r['path']),
                'generation_tool': tool_revision(), 'completeness_limitations': list(dataset['completeness_limitations'])}
    if dataset.get('load_problems_summary') is not None:
        manifest['load_problems'] = dataset['load_problems_summary']
    manifest['digest'] = V.digest_of(manifest)
    with open(os.path.join(root, 'manifest.json'), 'wb') as fh:
        fh.write(V.dump_file(manifest))
    return manifest


def refresh_manifest(root):
    """Recompute partition hashes, counts, key ranges and the manifest digest from the files on disk.

    Used by tests (and by operators after a reviewed hand edit) so that one targeted defect
    is not masked by a hash mismatch. The validator never calls it.
    """
    path = os.path.join(root, 'manifest.json')
    manifest = V.read_json(path)
    total = {k: 0 for k in V.LAYER_DIRS}
    for part in manifest['partitions']:
        with open(os.path.join(root, *part['path'].split('/')), 'rb') as fh:
            data = fh.read()
        env = V.RR.loads_strict(data.decode('utf-8'))
        recs = V.decode_records(env['strings'], env['shapes'], env['records']) if 'encoding' in env else env['records']
        part['sha256'] = V.sha256_bytes(data)
        part['record_count'] = len(recs)
        if recs:
            part['first_key'] = V.entry_key(part['layer'], recs[0])
            part['last_key'] = V.entry_key(part['layer'], recs[-1])
        total[part['layer']] += len(recs)
    manifest['layer_counts'] = dict(sorted(total.items()))
    manifest['digest'] = V.digest_of(manifest)
    with open(path, 'wb') as fh:
        fh.write(V.dump_file(manifest))
    return manifest


def main(argv):
    args = list(argv)
    out, sample = REGISTRY_ROOT, False
    while args:
        a = args.pop(0)
        if a == '--sample':
            sample = True
        elif a == '--out' and args:
            out = os.path.abspath(args.pop(0))
        else:
            sys.stderr.write('usage: build_registry.py --sample [--out DIR]\n')
            return 2
    if not sample:
        sys.stderr.write('only --sample is built here; real partitions load through load_partitions.py\n')
        return 2
    sd = _load('sample_data')
    for layer, dirname in V.LAYER_DIRS.items():
        base = os.path.join(out, dirname)
        for dirpath, dirs, files in os.walk(base):
            for fn in files:
                if fn.endswith('.json'):
                    os.remove(os.path.join(dirpath, fn))
    manifest = build(sd.sample_dataset(), out, max_per=sd.SAMPLE_MAX_PER_PARTITION)
    sys.stdout.write('built %s\n' % manifest['digest'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
