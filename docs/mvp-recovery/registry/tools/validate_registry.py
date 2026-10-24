#!/usr/bin/env python3
"""Deterministic offline validator for the layered informational governance catalogue.

Run:  python3 -I docs/mvp-recovery/registry/tools/validate_registry.py [--root DIR] [--previous DIR]

Non-authorizing. Standard library only. Reads files under the registry root and the
hub's tools/registry_records.py (canonical JSON and digest conventions). It never
executes a rule, a scenario or a test, opens no network connection, spawns no process,
writes nothing and grants no authority. Exit 0 means the catalogue is internally
consistent; it is not a qualification statement, an activation or a release decision.
"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)
HUB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(DEFAULT_ROOT)))

LAYER_DIRS = {'rules': 'rules', 'scenarios': 'scenarios', 'tests': 'tests', 'fixtures': 'fixtures',
              'evidence': 'evidence-index', 'crosswalk': 'crosswalk', 'coverage': 'reports'}
NAMESPACE = {'rules': 'R-', 'scenarios': 'S-', 'tests': 'T-', 'fixtures': 'F-'}
ENTRY_LAYERS = ('rules', 'scenarios', 'tests', 'fixtures')
SCHEMA_FILES = {'rules': 'rules', 'scenarios': 'scenarios', 'tests': 'tests', 'fixtures': 'fixtures',
                'evidence': 'evidence', 'crosswalk': 'crosswalk', 'coverage': 'coverage'}
TIER_NAMESPACE = {'GOVERNANCE_RULE': 'rules', 'LOGICAL_SCENARIO': 'scenarios',
                  'TEST_IMPLEMENTATION': 'tests', 'FIXTURE': 'fixtures'}
ANNOTATION_FORBIDDEN = {'authority', 'authorizes', 'authorized', 'qualification_status', 'current_status',
                        'current_qualification', 'approval_status'}
SAMPLE_REGISTRY_DIR = 'registry-records'


def _load_registry_records():
    path = os.path.join(HUB_ROOT, 'tools', 'registry_records.py')
    spec = importlib.util.spec_from_file_location('ocs_registry_records', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RR = _load_registry_records()


# --- helpers shared with the generator ------------------------------------------------------

def digest_of(obj):
    """sha256:<hex> over RFC 8785 canonical JSON of obj without its own 'digest' member."""
    return RR.record_digest(obj)


def sha256_bytes(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def canonical_digest(obj):
    return 'sha256:' + hashlib.sha256(RR.jcs_bytes(obj)).hexdigest()


def read_json(path):
    with open(path, 'rb') as fh:
        return RR.loads_strict(fh.read().decode('utf-8'))


def dump_file(obj):
    """Stable file form: sorted keys, 1-space indent, trailing newline, UTF-8, no floats."""
    RR.jcs_dumps(obj)  # refuses floats, lone surrogates, non-string keys
    return (json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False) + '\n').encode('utf-8')


def raw_ref(raw_set, index):
    return '%s:%d' % (raw_set, index)


def entry_key(layer, rec):
    if layer in ENTRY_LAYERS:
        return rec.get('catalogue_id')
    if layer == 'evidence':
        return rec.get('evidence_digest')
    if layer == 'coverage':
        return rec.get('subject_id')
    return '%s:%08d' % (rec.get('raw_set'), rec.get('raw_index')) if type(rec.get('raw_index')) is int else None


REF_FIELDS = {'rules': ('scenario_refs', 'test_refs', 'evidence_digest_refs'),
              'scenarios': ('rule_refs', 'test_refs', 'evidence_digest_refs'),
              'tests': ('scenario_refs', 'rule_refs', 'fixture_refs', 'evidence_digest_refs'),
              'fixtures': ('evidence_digest_refs',),
              'evidence': ('test_ref', 'scenario_ref')}
FLOORS = __import__('re').compile(r'^CR-0(0[1-9]|[12][0-9]|3[0-5])$')


def ref_pairs(layer, rec):
    """The (field, target) pairs an entry declares; each needs exactly one relationship record."""
    pairs = []
    for field in REF_FIELDS[layer]:
        val = rec.get(field)
        if type(val) is list:
            pairs.extend((field, v) for v in val if type(v) is str)
        elif type(val) is str:
            pairs.append((field, val))
    return pairs


def _provenance_of(e):
    out = {}
    for rel in e.get('relationships', []):
        out[(rel['field'], rel['to'])] = rel['provenance']
    return out


def unresolved_accounting(layers):
    """Counts that keep every unresolved item visible; the manifest commits to them."""
    acc = {'crosswalk_unresolved_rows': 0, 'unresolved_relationships': 0, 'unresolved_reference_placeholders': 0,
           'entries_with_unresolved_mvp_applicability': 0}
    acc['crosswalk_unresolved_rows'] = sum(1 for r in layers['crosswalk'] if r.get('disposition') == 'UNRESOLVED')
    for layer in REF_FIELDS:
        for e in layers[layer]:
            for rel in e.get('relationships', []):
                if rel.get('provenance') == 'UNRESOLVED':
                    acc['unresolved_relationships'] += 1
            acc['unresolved_reference_placeholders'] += sum(1 for _, t in ref_pairs(layer, e) if t.startswith('UNRESOLVED:'))
            if layer != 'evidence' and e.get('mvp_applicability', {}).get('value') == 'unresolved':
                acc['entries_with_unresolved_mvp_applicability'] += 1
    return acc


def derive_coverage(rules, scenarios, evidence_kind):
    """Pure derivation of the L6 rows from explicit, provenance-bearing links.

    Four separate assessments, none inferred from another. A DERIVED link is only ever a
    candidate: it never establishes implementation or test coverage, and nothing here can
    produce independent qualification from a historical run result.
    """
    rows = {}
    for layer, items in (('rules', rules), ('scenarios', scenarios)):
        for e in items:
            prov = _provenance_of(e)
            tests = [t for t in e['test_refs'] if t.startswith('T-')]
            evid = [d for d in e['evidence_digest_refs'] if d in evidence_kind]
            impl_s = sorted(t for t in tests if prov.get(('test_refs', t)) == 'SOURCE_STATED')
            impl_d = sorted(t for t in tests if prov.get(('test_refs', t)) == 'DERIVED')
            runs_s = sorted(d for d in evid if evidence_kind[d] == 'run_result' and prov.get(('evidence_digest_refs', d)) == 'SOURCE_STATED')
            runs_d = sorted(d for d in evid if evidence_kind[d] == 'run_result' and prov.get(('evidence_digest_refs', d)) == 'DERIVED')
            qual = sorted(d for d in evid if evidence_kind[d] == 'independent_qualification_record' and prov.get(('evidence_digest_refs', d)) == 'SOURCE_STATED')
            unresolved = sorted('%s->%s' % k for k, v in prov.items() if v == 'UNRESOLVED')
            if e['mvp_applicability']['value'] == 'unresolved':
                unresolved.append('mvp_applicability')
            pick = lambda s, d: ('source_stated_link', s) if s else (('derived_candidate_only', d) if d else ('none', []))
            ic, ib = pick(impl_s, impl_d)
            tc, tb = pick(runs_s, runs_d)
            states = ['defined']
            if impl_s:
                states.append('implemented')
            if runs_s:
                states.append('tested')
            if qual:
                states.append('independently_qualified')
            if e['mvp_applicability']['value'] in ('requires_unavailable_component', 'historical_only'):
                states.append('excluded_or_unsupported')
            row = {'layer': 'coverage', 'subject_id': e['catalogue_id'], 'subject_layer': layer, 'states': states,
                   'assessments': {
                       'catalogue_completeness': {'status': 'has_unresolved' if unresolved else 'complete', 'basis_refs': unresolved},
                       'implementation_coverage': {'status': ic, 'basis_refs': ib},
                       'test_coverage': {'status': tc, 'basis_refs': tb},
                       'independent_qualification': {'status': 'source_stated_record' if qual else 'none', 'basis_refs': qual}},
                   'mvp_applicability': e['mvp_applicability']['value'],
                   'status_note': 'derived_projection_not_a_qualification_claim',
                   'authority': 'none', 'non_authorizing': True, 'annotations': {}}
            row['digest'] = digest_of(row)
            rows[e['catalogue_id']] = row
    return rows


# --- schema subset (type, enum, const, pattern, required, properties, items, $ref ...) -----------

def _type_ok(value, name):
    if name == 'string':
        return type(value) is str
    if name == 'integer':
        return type(value) is int
    if name == 'boolean':
        return type(value) is bool
    if name == 'null':
        return value is None
    if name == 'object':
        return type(value) is dict
    if name == 'array':
        return type(value) is list
    return False


def check_schema(value, schema, defs, where, errs):
    import re
    if '$ref' in schema:
        schema = defs[schema['$ref'].split('/')[-1]]
    if 'const' in schema and (value != schema['const'] or type(value) is not type(schema['const'])):
        errs.append('%s: must be %r' % (where, schema['const']))
        return
    if 'enum' in schema and value not in schema['enum']:
        errs.append('%s: not in the closed set' % where)
        return
    if 'oneOf' in schema:
        if not any(not _sub(value, s, defs) for s in schema['oneOf']):
            errs.append('%s: matches no allowed form' % where)
        return
    if 'type' in schema:
        names = schema['type'] if type(schema['type']) is list else [schema['type']]
        if not any(_type_ok(value, n) for n in names):
            errs.append('%s: wrong type' % where)
            return
    if type(value) is str:
        if 'pattern' in schema and not re.match(schema['pattern'], value):
            errs.append('%s: bad form' % where)
        if schema.get('minLength', 0) > len(value):
            errs.append('%s: empty' % where)
    if type(value) is int and 'minimum' in schema and value < schema['minimum']:
        errs.append('%s: below minimum' % where)
    if type(value) is list:
        if schema.get('minItems', 0) > len(value):
            errs.append('%s: too few items' % where)
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            errs.append('%s: duplicate items' % where)
        if 'items' in schema:
            for i, v in enumerate(value):
                check_schema(v, schema['items'], defs, '%s[%d]' % (where, i), errs)
    if type(value) is dict:
        props = schema.get('properties', {})
        for key in schema.get('required', []):
            if key not in value:
                errs.append('%s: missing member %s' % (where, key))
        if schema.get('additionalProperties') is False:
            for key in sorted(value):
                if key not in props:
                    errs.append('%s: unknown member %s' % (where, key))
        for key, sub in props.items():
            if key in value:
                check_schema(value[key], sub, defs, '%s.%s' % (where, key), errs)


def _sub(value, schema, defs):
    out = []
    check_schema(value, schema, defs, '', out)
    return out


# --- the validator ------------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.errors = []

    def add(self, code, message):
        self.errors.append((code, message))

    def sorted(self):
        return sorted(set(self.errors))


def load_schemas(root, rep):
    schemas = {}
    for name in sorted(set(SCHEMA_FILES.values()) | {'partition', 'manifest'}):
        try:
            schemas[name] = read_json(os.path.join(root, 'schemas', name + '.schema.json'))
        except (OSError, ValueError) as exc:
            rep.add('schema_missing', '%s: %s' % (name, exc))
    return schemas


def schema_errors(value, name, schemas, where):
    sch = schemas[name]
    out = []
    check_schema(value, sch, sch.get('$defs', {}), where, out)
    return out


def load_registry(root, rep, schemas):
    """Return (manifest, {layer: [records]}); records carry no file metadata."""
    try:
        manifest = read_json(os.path.join(root, 'manifest.json'))
    except (OSError, ValueError) as exc:
        rep.add('manifest_unreadable', str(exc))
        return None, {}
    if 'manifest' in schemas:
        for e in schema_errors(manifest, 'manifest', schemas, 'manifest'):
            rep.add('manifest_schema', e)
    if type(manifest) is dict and type(manifest.get('digest')) is str:
        try:
            if digest_of(manifest) != manifest['digest']:
                rep.add('manifest_digest_mismatch', 'manifest digest differs from its canonical digest')
        except ValueError as exc:
            rep.add('manifest_schema', str(exc))
    layers = {k: [] for k in LAYER_DIRS}
    listed = set()
    for part in manifest.get('partitions', []) if type(manifest) is dict else []:
        if type(part) is not dict or type(part.get('path')) is not str:
            continue
        rel = part['path']
        listed.add(rel)
        layer = part.get('layer')
        if layer not in LAYER_DIRS or not rel.startswith(LAYER_DIRS[layer] + '/') or '..' in rel.split('/'):
            rep.add('partition_misplaced', '%s is not a partition of layer %s' % (rel, layer))
            continue
        full = os.path.join(root, *rel.split('/'))
        try:
            with open(full, 'rb') as fh:
                data = fh.read()
        except OSError:
            rep.add('partition_missing', rel)
            continue
        if sha256_bytes(data) != part.get('sha256'):
            rep.add('partition_hash_mismatch', rel)
        try:
            env = RR.loads_strict(data.decode('utf-8'))
        except ValueError as exc:
            rep.add('partition_unreadable', '%s: %s' % (rel, exc))
            continue
        if 'partition' in schemas:
            for e in schema_errors(env, 'partition', schemas, rel):
                rep.add('partition_schema', e)
        if type(env) is not dict or type(env.get('records')) is not list:
            continue
        if env.get('layer') != layer:
            rep.add('partition_misplaced', '%s declares layer %r, manifest says %r' % (rel, env.get('layer'), layer))
        recs = env['records']
        if part.get('record_count') != len(recs):
            rep.add('partition_count_mismatch', '%s: manifest %s, file %d' % (rel, part.get('record_count'), len(recs)))
        keys = [entry_key(layer, r) if type(r) is dict else None for r in recs]
        if keys != sorted(k for k in keys if k is not None) or None in keys:
            rep.add('partition_order', '%s: records must carry keys in ascending order' % rel)
        elif recs and (keys[0] != part.get('first_key') or keys[-1] != part.get('last_key')):
            rep.add('partition_range_mismatch', rel)
        for i, r in enumerate(recs):
            layers[layer].append(r)
            if layer in schemas or SCHEMA_FILES[layer] in schemas:
                for e in schema_errors(r, SCHEMA_FILES[layer], schemas, '%s[%d]' % (rel, i)):
                    rep.add('record_schema', e)
    for layer, dirname in sorted(LAYER_DIRS.items()):
        base = os.path.join(root, dirname)
        for dirpath, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in (SAMPLE_REGISTRY_DIR, 'generated')]
            for fn in sorted(files):
                rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, '/')
                if rel.endswith('.json') and rel not in listed:
                    rep.add('partition_unlisted', rel)
    return manifest, layers


def check_manifest_counts(manifest, layers, rep):
    counts = manifest.get('layer_counts')
    if type(counts) is dict:
        expected = {k: len(v) for k, v in layers.items()}
        if counts != expected:
            rep.add('layer_count_mismatch', 'manifest %s, found %s' % (json.dumps(counts, sort_keys=True), json.dumps(expected, sort_keys=True)))


def check_digests_and_authority(layers, rep):
    for layer, recs in layers.items():
        for r in recs:
            if type(r) is not dict:
                continue
            key = entry_key(layer, r)
            if layer != 'crosswalk' and type(r.get('digest')) is str:
                try:
                    if digest_of(r) != r['digest']:
                        rep.add('digest_mismatch', '%s %s' % (layer, key))
                except ValueError as exc:
                    rep.add('record_schema', '%s %s: %s' % (layer, key, exc))
            if r.get('authority') != 'none' or (layer != 'crosswalk' and r.get('non_authorizing') is not True):
                rep.add('authority_promotion', '%s %s must carry authority none and non_authorizing true' % (layer, key))
            ann = r.get('annotations')
            if type(ann) is dict:
                bad = sorted(set(ann) & ANNOTATION_FORBIDDEN)
                if bad:
                    rep.add('authority_promotion', '%s %s annotations carry %s' % (layer, key, bad))


def check_ids(layers, rep):
    ids = {}
    for layer in ENTRY_LAYERS:
        seen = set()
        for r in layers[layer]:
            cid = r.get('catalogue_id') if type(r) is dict else None
            if type(cid) is not str:
                continue
            if cid in seen:
                rep.add('duplicate_id', '%s %s' % (layer, cid))
            seen.add(cid)
            if not cid.startswith(NAMESPACE[layer]):
                rep.add('namespace_mismatch', '%s id %s lacks prefix %s' % (layer, cid, NAMESPACE[layer]))
        ids[layer] = seen
    seen = set()
    for r in layers['evidence']:
        d = r.get('evidence_digest')
        if d in seen:
            rep.add('duplicate_id', 'evidence %s' % d)
        seen.add(d)
    ids['evidence'] = seen
    seen = set()
    for r in layers['crosswalk']:
        k = entry_key('crosswalk', r)
        if k in seen:
            rep.add('crosswalk_duplicate_row', k)
        seen.add(k)
    seen = set()
    for r in layers['coverage']:
        k = r.get('subject_id')
        if k in seen:
            rep.add('duplicate_id', 'coverage %s' % k)
        seen.add(k)
    return ids


def _refs(rep, owner, field, refs, layer, ids):
    prefix = NAMESPACE[layer]
    for ref in refs:
        if type(ref) is not str or ref.startswith('UNRESOLVED:'):
            continue
        if not ref.startswith(prefix) or ref not in ids[layer]:
            rep.add('unresolved_reference', '%s.%s -> %s (typed %s)' % (owner, field, ref, layer))


def _evidence_refs(rep, owner, refs, ids):
    for ref in refs:
        if type(ref) is str and not ref.startswith('UNRESOLVED:') and ref not in ids['evidence']:
            rep.add('unresolved_reference', '%s.evidence_digest_refs -> %s' % (owner, ref))


def check_references(layers, ids, rep):
    by = {layer: {r['catalogue_id']: r for r in layers[layer] if type(r) is dict and 'catalogue_id' in r} for layer in ENTRY_LAYERS}
    for r in layers['rules']:
        o = r.get('catalogue_id')
        _refs(rep, o, 'scenario_refs', r.get('scenario_refs', []), 'scenarios', ids)
        _refs(rep, o, 'test_refs', r.get('test_refs', []), 'tests', ids)
        _evidence_refs(rep, o, r.get('evidence_digest_refs', []), ids)
    for r in layers['scenarios']:
        o = r.get('catalogue_id')
        _refs(rep, o, 'rule_refs', r.get('rule_refs', []), 'rules', ids)
        _refs(rep, o, 'test_refs', r.get('test_refs', []), 'tests', ids)
        _evidence_refs(rep, o, r.get('evidence_digest_refs', []), ids)
    for r in layers['tests']:
        o = r.get('catalogue_id')
        _refs(rep, o, 'scenario_refs', r.get('scenario_refs', []), 'scenarios', ids)
        _refs(rep, o, 'rule_refs', r.get('rule_refs', []), 'rules', ids)
        _refs(rep, o, 'fixture_refs', r.get('fixture_refs', []), 'fixtures', ids)
        _evidence_refs(rep, o, r.get('evidence_digest_refs', []), ids)
    for r in layers['fixtures']:
        _evidence_refs(rep, r.get('catalogue_id'), r.get('evidence_digest_refs', []), ids)
    for r in layers['evidence']:
        o = r.get('evidence_digest')
        for field, layer in (('test_ref', 'tests'), ('scenario_ref', 'scenarios')):
            ref = r.get(field)
            if type(ref) is str:
                _refs(rep, o, field, [ref], layer, ids)
    # rule <-> scenario links must agree in both directions (unresolved placeholders excepted)
    for rid, rule in by['rules'].items():
        for sid in rule.get('scenario_refs', []):
            sc = by['scenarios'].get(sid)
            if sc is not None and rid not in sc.get('rule_refs', []):
                rep.add('link_not_bidirectional', '%s lists %s but %s does not list %s' % (rid, sid, sid, rid))
    for sid, sc in by['scenarios'].items():
        for rid in sc.get('rule_refs', []):
            rule = by['rules'].get(rid)
            if rule is not None and sid not in rule.get('scenario_refs', []):
                rep.add('link_not_bidirectional', '%s lists %s but %s does not list %s' % (sid, rid, rid, sid))
    return by


def check_relationships(layers, rep):
    for layer in REF_FIELDS:
        for e in layers[layer]:
            owner = e.get('catalogue_id') or e.get('evidence_digest')
            rels = e.get('relationships', [])
            seen = {}
            for rel in rels:
                key = (rel.get('field'), rel.get('to'))
                if rel.get('field') == 'alias_candidates':
                    continue
                if key in seen:
                    rep.add('relationship_duplicate', '%s %s' % (owner, key))
                seen[key] = rel
                prov = rel.get('provenance')
                src = rel.get('source')
                if prov == 'SOURCE_STATED':
                    if not src or rel.get('method') is not None or rel.get('supporting_refs') or rel.get('confidence_class') is not None or rel.get('missing_evidence') is not None:
                        rep.add('relationship_provenance', '%s %s: SOURCE_STATED needs exact source repo, revision and location and nothing derived' % (owner, key))
                elif prov == 'DERIVED':
                    if src is not None or not rel.get('method') or not rel.get('supporting_refs') or rel.get('confidence_class') is None or rel.get('missing_evidence') is not None:
                        rep.add('relationship_provenance', '%s %s: DERIVED needs method, supporting refs and confidence class, and no source claim' % (owner, key))
                elif prov == 'UNRESOLVED':
                    if not str(rel.get('missing_evidence') or '').strip() or src is not None or rel.get('method') is not None:
                        rep.add('relationship_provenance', '%s %s: UNRESOLVED must name the missing evidence' % (owner, key))
                if prov in ('SOURCE_STATED', 'DERIVED') and str(rel.get('to', '')).startswith('UNRESOLVED:'):
                    rep.add('unresolved_promoted', '%s %s: an unresolved target cannot be reported as %s' % (owner, key, prov))
            declared = set(ref_pairs(layer, e))
            for key in sorted(declared - set(seen)):
                rep.add('relationship_missing', '%s %s has no provenance record' % (owner, key))
            for key in sorted(set(seen) - declared):
                rep.add('relationship_orphan', '%s %s has provenance but no reference' % (owner, key))
    for e in layers['rules']:
        if e.get('normative_type') == 'constitutional_floor' and (e.get('adoption_status') != 'adopted' or not any(FLOORS.match(n) for n in e.get('native_ids', []))):
            rep.add('floor_misclassified', '%s: only adopted CR-001..CR-035 identities may be constitutional_floor' % e.get('catalogue_id'))
    for e in layers['scenarios']:
        if e.get('scenario_class') == 'suite_level_acceptance' and e.get('rule_refs') is None:
            rep.add('record_schema', 'scenario without rule_refs')


def check_accounting(layers, manifest, rep):
    if manifest.get('unresolved_accounting') != unresolved_accounting(layers):
        rep.add('unresolved_accounting_mismatch', 'manifest commitment %s differs from found %s' % (
            json.dumps(manifest.get('unresolved_accounting'), sort_keys=True), json.dumps(unresolved_accounting(layers), sort_keys=True)))


def check_evidence(layers, manifest, rep):
    sets = {s.get('set_id'): s for s in manifest.get('source_inventory', []) if type(s) is dict}
    for e in layers['evidence']:
        o = e.get('evidence_digest')
        sc = e.get('source_commitment')
        if type(sc) is dict and sc.get('set_id') not in sets:
            rep.add('evidence_commitment_missing', '%s names source set %s that the manifest inventory does not commit' % (o, sc.get('set_id')))
        art = e.get('artifact_commitment')
        if type(art) is not dict or not art.get('path') or not art.get('record_digest'):
            rep.add('evidence_commitment_missing', '%s lacks an artifact commitment' % o)
        if e.get('tier') != 'EXECUTION_EVIDENCE':
            rep.add('evidence_as_rule', '%s is not tier EXECUTION_EVIDENCE' % o)
    rule_ids = {r.get('catalogue_id') for r in layers['rules']}
    for e in layers['evidence']:
        if e.get('evidence_digest') in rule_ids:
            rep.add('evidence_as_rule', e.get('evidence_digest'))
    for layer in ENTRY_LAYERS:
        for r in layers[layer]:
            if r.get('tier') == 'EXECUTION_EVIDENCE' or 'historical_verdict_verbatim' in r:
                rep.add('evidence_as_rule', '%s %s carries execution evidence' % (layer, r.get('catalogue_id')))


def check_crosswalk(layers, ids, by, manifest, rep):
    rows = layers['crosswalk']
    # raw accounting: exactly one row per raw index per source set, and the inventory commitment
    per_set = {}
    for r in rows:
        if type(r) is dict and type(r.get('raw_index')) is int:
            per_set.setdefault(r.get('raw_set'), {}).setdefault(r['raw_index'], []).append(r)
    inventory = {s.get('set_id'): s for s in manifest.get('source_inventory', []) if type(s) is dict}
    for set_id in sorted(set(per_set) | set(inventory)):
        inv = inventory.get(set_id)
        if inv is None:
            rep.add('crosswalk_unknown_set', set_id)
            continue
        got = per_set.get(set_id, {})
        n = inv.get('raw_record_count')
        for i in range(n if type(n) is int else 0):
            if i not in got:
                rep.add('crosswalk_row_missing', '%s:%d has no crosswalk row' % (set_id, i))
        for i in sorted(got):
            if type(n) is int and i >= n:
                rep.add('crosswalk_row_extra', '%s:%d is beyond the committed raw count %s' % (set_id, i, n))
            if len(got[i]) > 1:
                rep.add('crosswalk_duplicate_row', '%s:%d' % (set_id, i))
        if all(i in got for i in range(n if type(n) is int else 0)):
            digests = [got[i][0].get('raw_digest') for i in range(n)]
            if canonical_digest(digests) != inv.get('inventory_sha256'):
                rep.add('inventory_commitment_mismatch', '%s: raw digests no longer match the committed inventory' % set_id)
    referenced = {layer: {} for layer in ENTRY_LAYERS}
    evid_rows = {}
    canonical_rows = {}
    for r in rows:
        if type(r) is not dict:
            continue
        ref = raw_ref(r.get('raw_set'), r.get('raw_index'))
        tier, disp, target = r.get('tier'), r.get('disposition'), r.get('target')
        native = r.get('native_id')
        if disp == 'CANONICAL':
            layer = TIER_NAMESPACE.get(tier)
            if layer is None:
                rep.add('crosswalk_tier_mismatch', '%s: tier %s cannot be CANONICAL' % (ref, tier))
                continue
            if target not in by[layer]:
                rep.add('unresolved_reference', '%s -> %s' % (ref, target))
                continue
            if target in canonical_rows:
                rep.add('crosswalk_duplicate_canonical', '%s has CANONICAL rows %s and %s' % (target, canonical_rows[target], ref))
            canonical_rows[target] = ref
            referenced[layer].setdefault(target, set()).add(ref)
        elif disp == 'ALIAS_OF':
            layer = TIER_NAMESPACE.get(tier) or next((l for l in ENTRY_LAYERS if type(target) is str and target.startswith(NAMESPACE[l])), None)
            if tier in ('EXECUTION_EVIDENCE', 'PARAMETRIZED_INSTANCE') or layer is None or target not in by[layer]:
                rep.add('unresolved_reference' if layer else 'crosswalk_tier_mismatch', '%s ALIAS_OF %s' % (ref, target))
                continue
            entry = by[layer][target]
            if native is not None and native not in entry.get('aliases', []) and native not in entry.get('native_ids', []):
                rep.add('alias_not_retained', '%s: native id %r is not retained on %s' % (ref, native, target))
            referenced[layer].setdefault(target, set()).add(ref)
        elif disp == 'HISTORICAL_REVISION_OF':
            layer = next((l for l in ENTRY_LAYERS if type(target) is str and target.startswith(NAMESPACE[l])), None)
            if tier not in ('RULE_REVISION', 'HISTORICAL_REVISION') or layer is None or target not in by[layer]:
                rep.add('crosswalk_tier_mismatch' if layer else 'unresolved_reference', '%s HISTORICAL_REVISION_OF %s' % (ref, target))
                continue
            entry = by[layer][target]
            if not any(l.get('raw_ref') == ref and l.get('digest') == r.get('raw_digest') for l in entry.get('lineage', [])):
                rep.add('revision_not_retained', '%s: revision is not in the lineage of %s' % (ref, target))
            referenced[layer].setdefault(target, set()).add(ref)
        elif disp == 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE':
            if tier == 'PARAMETRIZED_INSTANCE':
                if target not in by['tests']:
                    rep.add('unresolved_reference', '%s -> %s' % (ref, target))
                    continue
                referenced['tests'].setdefault(target, set()).add(ref)
                evid_rows.setdefault(('inst', target), []).append(ref)
            elif tier == 'EXECUTION_EVIDENCE':
                if target not in ids['evidence']:
                    rep.add('unresolved_reference', '%s -> %s' % (ref, target))
                    continue
                evid_rows.setdefault(('ev', target), []).append(ref)
            else:
                rep.add('crosswalk_tier_mismatch', '%s: tier %s cannot be a test instance or execution occurrence' % (ref, tier))
        elif disp == 'SOURCE_ONLY_ARTIFACT':
            if tier == 'EXECUTION_EVIDENCE' or target is not None:
                rep.add('crosswalk_tier_mismatch', '%s: SOURCE_ONLY_ARTIFACT needs a null target and a non-evidence tier' % ref)
        elif disp == 'UNRESOLVED':
            if target is not None or not r.get('unresolved_reason'):
                rep.add('crosswalk_tier_mismatch', '%s: UNRESOLVED needs a null target and a reason' % ref)
        if tier == 'EXECUTION_EVIDENCE' and disp not in ('TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', 'UNRESOLVED'):
            rep.add('evidence_as_rule', '%s: execution evidence cannot have disposition %s' % (ref, disp))
    # every entry's raw_refs equal the crosswalk rows that point at it
    for layer in ENTRY_LAYERS:
        for cid, entry in by[layer].items():
            want = referenced[layer].get(cid, set())
            have = set(entry.get('raw_refs', []))
            if want != have:
                rep.add('raw_refs_mismatch', '%s: raw_refs %s differ from crosswalk %s' % (cid, sorted(have), sorted(want)))
            if cid not in canonical_rows:
                rep.add('crosswalk_row_missing', '%s has no CANONICAL crosswalk row' % cid)
    for tid, entry in by['tests'].items():
        n = len(evid_rows.get(('inst', tid), []))
        if entry.get('parametrized_instance_count') != n:
            rep.add('instance_count_mismatch', '%s: count %s, crosswalk rows %d' % (tid, entry.get('parametrized_instance_count'), n))
    for e in layers['evidence']:
        want = set(evid_rows.get(('ev', e.get('evidence_digest')), []))
        if want != set(e.get('raw_refs', [])):
            rep.add('raw_refs_mismatch', '%s: evidence raw_refs differ from crosswalk' % e.get('evidence_digest'))


def check_mvp(layers, rep):
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        for r in layers[layer]:
            mv = r.get('mvp_applicability')
            if type(mv) is not dict or type(mv.get('value')) is not str or not str(mv.get('reason', '')).strip():
                rep.add('mvp_applicability_unclassified', '%s %s' % (layer, r.get('catalogue_id')))


def check_coverage(layers, rep):
    kinds = {e.get('evidence_digest'): e.get('evidence_kind') for e in layers['evidence']}
    try:
        want = derive_coverage(layers['rules'], layers['scenarios'], kinds)
    except (KeyError, TypeError):
        rep.add('coverage_underivable', 'rule or scenario entries are too malformed to project')
        return
    have = {r.get('subject_id'): r for r in layers['coverage'] if type(r) is dict}
    for sid in sorted(set(want) | set(have)):
        if sid not in have:
            rep.add('coverage_missing', sid)
        elif sid not in want:
            rep.add('coverage_extra', sid)
        elif have[sid] != want[sid]:
            rep.add('coverage_inferred', '%s: row differs from the explicit-link derivation (states %s, derived %s)' % (sid, have[sid].get('states'), want[sid]['states']))


def check_registry_records(root, manifest, layers, rep):
    recs = {}
    for item in manifest.get('registry_records', []):
        path = os.path.join(root, *str(item.get('path', '')).split('/'))
        try:
            rec = read_json(path)
        except (OSError, ValueError) as exc:
            rep.add('registry_record_unreadable', '%s: %s' % (item.get('path'), exc))
            continue
        try:
            computed = RR.validate_record(rec, floor_mandatory_rule_ids=[], pin=item.get('record_digest'))
        except RR.RegistryRefusal as exc:
            rep.add('registry_record_refused', '%s: %s' % (item.get('path'), exc.code))
            continue
        if computed != item.get('record_digest') or rec['registry_id'] != item.get('registry_id'):
            rep.add('registry_record_refused', '%s: identity differs from the manifest' % item.get('path'))
            continue
        for rule in rec['rule_table']:
            if rule['status'] != 'advisory':
                rep.add('authority_promotion', '%s rule %s is not advisory' % (item.get('path'), rule['rule_id']))
        recs[(rec['registry_id'], computed)] = {rule['rule_id']: rule for rule in rec['rule_table']}
    for r in layers['rules']:
        ref = r.get('rule_ref')
        if type(ref) is not dict:
            continue
        o = r.get('catalogue_id')
        if ref.get('kind') == 'registry_record':
            table = recs.get((ref.get('registry_id'), ref.get('record_digest')))
            rule = table.get(ref.get('rule_id')) if table else None
            if rule is None:
                rep.add('unresolved_reference', '%s rule_ref names a registry rule that is not in a pinned record' % o)
            elif canonical_digest(rule) != ref.get('rule_digest') or rule['version'] != ref.get('version'):
                rep.add('rule_digest_mismatch', '%s: rule_digest differs from the pinned registry rule' % o)
        elif ref.get('registry_id') is not None or ref.get('record_digest') is not None:
            rep.add('rule_ref_inconsistent', '%s: a source statement carries no registry identity' % o)


def check_previous(prev_root, layers, rep):
    prep = Report()
    schemas = load_schemas(prev_root, prep)
    pm, players = load_registry(prev_root, prep, schemas)
    if pm is None:
        rep.add('previous_unreadable', prev_root)
        return
    for layer in ENTRY_LAYERS:
        now = {r['catalogue_id']: r for r in layers[layer] if type(r) is dict and 'catalogue_id' in r}
        for r in players[layer]:
            cid = r.get('catalogue_id')
            cur = now.get(cid)
            if cur is None:
                rep.add('historical_removed', '%s %s existed in the previous registry' % (layer, cid))
                continue
            kept = {(l.get('revision_id'), l.get('raw_ref'), l.get('digest')) for l in cur.get('lineage', [])}
            for l in r.get('lineage', []):
                if (l.get('revision_id'), l.get('raw_ref'), l.get('digest')) not in kept:
                    rep.add('historical_overwritten', '%s lost lineage %s' % (cid, l.get('revision_id')))
            if cur.get('digest') != r.get('digest') and r.get('digest') not in {l.get('digest') for l in cur.get('lineage', [])}:
                rep.add('historical_overwritten', '%s changed without retaining its previous digest in lineage' % cid)
            if not set(r.get('aliases', [])) <= set(cur.get('aliases', [])):
                rep.add('alias_not_retained', '%s dropped aliases' % cid)
    now = {r.get('evidence_digest'): r for r in layers['evidence']}
    for r in players['evidence']:
        if r.get('evidence_digest') not in now:
            rep.add('historical_removed', 'evidence %s' % r.get('evidence_digest'))
        elif now[r['evidence_digest']].get('digest') != r.get('digest'):
            rep.add('historical_overwritten', 'evidence %s changed' % r.get('evidence_digest'))
    cur_rows = {entry_key('crosswalk', r): r for r in layers['crosswalk']}
    for r in players['crosswalk']:
        cur = cur_rows.get(entry_key('crosswalk', r))
        if cur is None:
            rep.add('historical_removed', 'crosswalk row %s' % entry_key('crosswalk', r))
        elif cur.get('raw_digest') != r.get('raw_digest'):
            rep.add('historical_overwritten', 'raw record %s changed digest' % entry_key('crosswalk', r))


def validate(root, previous=None):
    """Return the sorted list of (code, message) refusals for the catalogue at root."""
    rep = Report()
    schemas = load_schemas(root, rep)
    if rep.errors:
        return rep.sorted(), None
    manifest, layers = load_registry(root, rep, schemas)
    if manifest is None or type(manifest) is not dict:
        return rep.sorted(), None
    try:
        check_manifest_counts(manifest, layers, rep)
        check_digests_and_authority(layers, rep)
        ids = check_ids(layers, rep)
        by = check_references(layers, ids, rep)
        check_relationships(layers, rep)
        check_accounting(layers, manifest, rep)
        check_evidence(layers, manifest, rep)
        check_crosswalk(layers, ids, by, manifest, rep)
        check_mvp(layers, rep)
        check_coverage(layers, rep)
        check_registry_records(root, manifest, layers, rep)
        if previous:
            check_previous(previous, layers, rep)
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        rep.add('record_schema', 'structure too malformed to check further: %s' % type(exc).__name__)
    return rep.sorted(), manifest


def main(argv):
    args = list(argv)
    root, previous = DEFAULT_ROOT, None
    while args:
        a = args.pop(0)
        if a == '--root' and args:
            root = os.path.abspath(args.pop(0))
        elif a == '--previous' and args:
            previous = os.path.abspath(args.pop(0))
        else:
            sys.stderr.write('usage: validate_registry.py [--root DIR] [--previous DIR]\n')
            return 2
    errors, manifest = validate(root, previous)
    if errors:
        for code, message in errors:
            sys.stdout.write('REFUSED %s: %s\n' % (code, message))
        sys.stdout.write('catalogue validation failed: %d finding(s); non-authorizing; HOLD\n' % len(errors))
        return 1
    counts = manifest['layer_counts']
    sys.stdout.write('catalogue consistent: %s; manifest %s\n' % (
        ', '.join('%s=%d' % (k, counts[k]) for k in sorted(counts)), manifest['digest']))
    sys.stdout.write('informational only; authority none; no rule was executed; HOLD\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
