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
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)
HUB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(DEFAULT_ROOT)))

LAYER_DIRS = {'rules': 'rules', 'scenarios': 'scenarios', 'tests': 'tests', 'fixtures': 'fixtures',
              'evidence': 'evidence-index', 'crosswalk': 'crosswalk', 'coverage': 'reports', 'lineage_sets': 'lineage-sets'}
LINEAGE_PREFIX = 'L-'
NAMESPACE = {'rules': 'R-', 'scenarios': 'S-', 'tests': 'T-', 'fixtures': 'F-'}
# derived scenario data artifacts (partition B) are fixtures-layer entries with their own FD- namespace; they are not F- fixtures
EXTRA_PREFIXES = {'fixtures': ('FD-',)}
ENTRY_LAYERS = ('rules', 'scenarios', 'tests', 'fixtures')
SCHEMA_FILES = {'rules': 'rules', 'scenarios': 'scenarios', 'tests': 'tests', 'fixtures': 'fixtures',
                'evidence': 'evidence', 'crosswalk': 'crosswalk', 'coverage': 'coverage', 'lineage_sets': 'lineage_sets'}
ENCODING = 'ocs-interned-shapes/0'
TIER_NAMESPACE = {'GOVERNANCE_RULE': 'rules', 'LOGICAL_SCENARIO': 'scenarios',
                  'TEST_IMPLEMENTATION': 'tests', 'FIXTURE': 'fixtures'}
ANNOTATION_FORBIDDEN_RE = __import__('re').compile(
    r'(authori|qualif|verdict|status_current|current_status|approv|clearance|' + 'cert' + 'if|attest|accredit|release_status|production_status|ready)', __import__('re').I)
SOURCE_ONLY_TIERS = ('RULE_ADJACENT', 'SOURCE_ONLY_ARTIFACT')
ID_RE = __import__('re').compile(r'[!-~]+')
# source-stated descriptive keys that merely contain a trigger stem; they carry quoted text, not a status
ANNOTATION_ALLOWED = {'evaluator_qualification_note', 'evaluator_stated', 'verdict_field', 'original_verdict_field', 'qualification_note'}


def annotation_key_forbidden(key):
    return type(key) is str and bool(ANNOTATION_FORBIDDEN_RE.search(key)) and key not in ANNOTATION_ALLOWED


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


def dump_compact(obj):
    """Compact file form for large partitions: sorted keys, no indentation, trailing newline."""
    RR.jcs_dumps(obj)
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode('utf-8')


def encode_records(recs, min_len=16):
    """Lossless interned-shapes codec: returns (strings, shapes, body).

    A string value is stored as '~N' (index into strings) or literally ('~' is doubled when a literal
    string starts with it); a list is [-1, items...]; an object is [shape_id, values...] where the
    shape is its sorted key list. Deterministic: strings by (-count, text), shapes by first use.
    """
    cnt = {}

    def walk(o):
        t = type(o)
        if t is str:
            if len(o) >= min_len:
                cnt[o] = cnt.get(o, 0) + 1
        elif t is list:
            for x in o:
                walk(x)
        elif t is dict:
            for v in o.values():
                walk(v)
    for r in recs:
        walk(r)
    table = sorted((x for x, c in cnt.items() if c >= 2), key=lambda x: (-cnt[x], x))
    idx = {x: i for i, x in enumerate(table)}
    shapes, shape_ids = [], {}

    def enc(o):
        t = type(o)
        if t is str:
            if o in idx:
                return '~%d' % idx[o]
            return '~' + o if o[:1] == '~' else o
        if t is list:
            return [-1] + [enc(x) for x in o]
        if t is dict:
            keys = tuple(sorted(o))
            if keys not in shape_ids:
                shape_ids[keys] = len(shapes)
                shapes.append(list(keys))
            return [shape_ids[keys]] + [enc(o[k]) for k in keys]
        return o
    return table, shapes, [enc(r) for r in recs]


def decode_records(strings, shapes, body):
    def dec(v):
        t = type(v)
        if t is str:
            if v[:1] == '~':
                return v[1:] if v[1:2] == '~' else strings[int(v[1:])]
            return v
        if t is list:
            head = v[0]
            if head == -1:
                return [dec(x) for x in v[1:]]
            keys = shapes[head]
            if type(head) is not int or head < 0 or len(keys) != len(v) - 1:
                raise ValueError('bad shape reference')
            return {k: dec(x) for k, x in zip(keys, v[1:])}
        return v
    return [dec(r) for r in body]


CW_KEEP_ANN = ('catalogue_scope', 'level', 'relation', 'tier_basis', 'co_registered', 'post_v0_1_reason', 'release_scope', 'attach_kind', 'disposition_as_recorded')
CW_NATIVE_KEPT = ('ALIAS_OF', 'HISTORICAL_REVISION_OF', 'UNRESOLVED')
VERDICT_INDEX_MAX = 80
EV_KEEP_ANN = ('is_v01_candidate_run', 'level', 'execution_identity')


def slim_crosswalk(full):
    """The committed crosswalk row derived from the full row (path, native_id and most annotations stay external)."""
    o = {k: v for k, v in full.items() if k not in ('path', 'native_id', 'annotations')}
    if full.get('disposition') in CW_NATIVE_KEPT:
        o['native_id'] = full.get('native_id')
    o['annotations'] = {k: v for k, v in (full.get('annotations') or {}).items() if k in CW_KEEP_ANN}
    return o


def slim_evidence(full):
    """The committed evidence index entry derived from the full finalized entry."""
    o = {k: v for k, v in full.items() if k not in ('annotations', 'historical_verdict_verbatim', 'digest')}
    v = full.get('historical_verdict_verbatim')
    keep = v is not None and len(v) <= VERDICT_INDEX_MAX and '\n' not in v
    o['annotations'] = {k: x for k, x in (full.get('annotations') or {}).items() if k in EV_KEEP_ANN}
    # the record digest equals the evidence digest and the file digest stays with the external full record
    o['artifact_commitment'] = {'path': (full.get('artifact_commitment') or {}).get('path')}
    # a short single-line verdict is quoted verbatim in the index; a longer one stays in the external record (digest only here)
    o['historical_verdict_verbatim'] = v if keep else None
    o['historical_verdict_sha256'] = None if (v is None or keep) else sha256_bytes(v.encode('utf-8'))
    o['full_record_digest'] = full['digest']
    o['digest'] = digest_of(o)
    return o


def raw_ref(raw_set, index):
    return '%s:%d' % (raw_set, index)


def entry_key(layer, rec):
    if layer in ENTRY_LAYERS or layer == 'lineage_sets':
        return rec.get('catalogue_id')
    if layer == 'evidence':
        return rec.get('evidence_digest')
    if layer == 'coverage':
        return rec.get('subject_id')
    return '%s:%08d' % (rec.get('raw_set'), rec.get('raw_index')) if type(rec.get('raw_index')) is int else None


# related_refs: same-layer links stated or derived by the G3 pass; alias_candidates: same-layer entries that a
# partition or G1 flags as possibly the same thing but that were NOT merged (no merge without a stated basis)
# source_reference_refs: inbound links from source-only raw records (SR:<partition>:<raw digest>) that a partition or G3 ties
# to this entry; the source-only record itself stays a SOURCE_ONLY_ARTIFACT crosswalk row and never becomes an entry
REF_FIELDS = {'rules': ('scenario_refs', 'test_refs', 'evidence_digest_refs', 'related_refs', 'alias_candidates', 'source_reference_refs'),
              'scenarios': ('rule_refs', 'test_refs', 'fixture_refs', 'evidence_digest_refs', 'related_refs', 'alias_candidates', 'source_reference_refs'),
              'tests': ('scenario_refs', 'rule_refs', 'fixture_refs', 'evidence_digest_refs', 'alias_candidates', 'source_reference_refs'),
              'fixtures': ('evidence_digest_refs', 'alias_candidates', 'source_reference_refs'),
              'evidence': ('test_ref', 'scenario_ref')}
SR_RE = re.compile(r'^SR:([A-Za-z0-9]{1,8}):([0-9a-f]{64})\Z')
FLOORS = __import__('re').compile(r'^CR-0(0[1-9]|[12][0-9]|3[0-5])$')


def ref_pairs(layer, rec):
    """The (field, target) pairs an entry declares; each needs exactly one relationship record.
    """
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
    acc['evidence_unrecorded_source_revisions'] = sum(1 for e in layers['evidence'] if (e.get('source_commitment') or {}).get('revision') == 'unrecorded')
    acc['entries_with_unrecorded_source_revision'] = sum(1 for l in ('rules', 'scenarios', 'tests', 'fixtures') for e in layers[l]
                                                          if str((e.get('source') or {}).get('revision')) == 'unrecorded')
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


REGISTRY_FAMILIES = {'0.1': 'runtime-authority-reasons/0.1', '0.2': 'runtime-authority-reasons/0.2'}


def _family(e):
    return str((e.get('annotations') or {}).get('rule_family') or '')


def _registry_version(e):
    for ver, prefix in REGISTRY_FAMILIES.items():
        if _family(e).startswith(prefix):
            return ver
    return None


def compute_denominators(layers):
    """The separate denominators, computed from the entries only. The manifest commits to this result and the validator
    recomputes it, so a count cannot be inflated, merged into a headline or dropped without a refusal."""
    rules, classes = {}, {}
    for e in layers['rules']:
        rules[e['normative_type']] = rules.get(e['normative_type'], 0) + 1
    for e in layers['scenarios']:
        classes[e['scenario_class']] = classes.get(e['scenario_class'], 0) + 1
    ev = layers['evidence']
    verdicts = {}
    for e in ev:
        v = e['historical_verdict_verbatim']
        key = v if v is not None else ('(none recorded)' if e.get('historical_verdict_sha256') is None else '(long verdict text: digest in the index, text in the external record)')
        verdicts[key] = verdicts.get(key, 0) + 1
    # an execution identity is one (run, test node); a run is the larger unit and is reported apart under its own name
    node_ids = set()
    for e in ev:
        ident = (e.get('annotations') or {}).get('execution_identity')
        if type(ident) is list and len(ident) == 2:
            node_ids.add((ident[0], ident[1]))
        elif e.get('run_id') is not None:
            node_ids.add((e['run_id'], (e.get('artifact_commitment') or {}).get('path')))
    runs = {e['run_id'] for e in ev if e.get('run_id') is not None}
    runs_with_results = {e['run_id'] for e in ev if e['evidence_kind'] == 'run_result' and e.get('run_id') is not None}
    scope = {'v0_1': 0, 'post_v0_1_reported_apart': 0, 'release_scope_not_stated': 0}
    for e in layers['scenarios']:
        if e['scenario_class'] == 'logical':
            key = {'v0_1': 'v0_1', 'post_v0_1': 'post_v0_1_reported_apart'}.get(e.get('release_scope'), 'release_scope_not_stated')
            scope[key] += 1
    # the adversarial-or-unexecuted class is three different things; each is its own figure and none is added to another
    cats = {'spec_cases': 0, 'unexecuted_other': 0, 'adversarial': 0, 'category_not_stated': 0}
    for e in layers['scenarios']:
        if e['scenario_class'] == 'adversarial_or_unexecuted_spec':
            basis = str((e.get('annotations') or {}).get('scenario_category_basis') or '')
            cats[{'CAT-SPEC696': 'spec_cases', 'CAT-UNEXEC': 'unexecuted_other', 'CAT-ADV': 'adversarial'}.get(basis, 'category_not_stated')] += 1
    classes.pop('adversarial_or_unexecuted_spec', None)
    classes.pop('logical', None)
    for k, v in scope.items():
        if v:
            classes['logical:' + k] = v
    for k, v in cats.items():
        if v:
            classes['adversarial_or_unexecuted_spec:' + k] = v
    ten = {'1_canonical_rules_by_normative_type': dict(sorted(rules.items())),
           '2_logical_governance_scenarios': scope,
           '3_suite_level_acceptance_scenarios': classes.get('suite_level_acceptance', 0),
           '4_adversarial_ideas_or_unexecuted_specifications': cats,
           '5_test_implementations': len(layers['tests']),
           '6_parametrized_test_instances': sum(e['parametrized_instance_count'] for e in layers['tests']),
           '7_fixtures_and_input_vectors': len(layers['fixtures']),
           '8_historical_execution_records': sum(1 for r in layers['crosswalk'] if r['tier'] == 'EXECUTION_EVIDENCE'),
           '9_distinct_execution_identities': {'distinct_run_and_test_node_pairs': len(node_ids), 'distinct_runs': len(runs),
                                               'distinct_runs_with_run_results': len(runs_with_results)},
           '10_historical_verdicts_verbatim': dict(sorted(verdicts.items()))}
    # the reason-code registry has two labelled versions that are kept as distinct entries; the 0.1 code names are a subset of the 0.2 names
    by_ver = {'0.1': [], '0.2': []}
    for e in layers['rules']:
        v = _registry_version(e)
        if v:
            by_ver[v].append(e)
    names = set()
    for v, es in by_ver.items():
        for e in es:
            for n in e.get('native_ids', []):
                names.add(n[:-len('@' + v)] if n.endswith('@' + v) else n)
    registries = {'runtime_authority_reasons_entries_label_0_1': len(by_ver['0.1']), 'runtime_authority_reasons_entries_label_0_2': len(by_ver['0.2']),
                  'distinct_registry_code_names': len(names),
                  'rule_entries_resting_on_raw_set_B': sum(1 for e in layers['rules'] if any(str(x).startswith('B:') for x in e.get('raw_refs', []))),
                  'headline': 'none by design: entries and distinct code names are different denominators and are never one number'}
    diff = sum(e.get('differential_instance_count', 0) for e in layers['scenarios'])
    # the rule headline: mvp_fixed governance rules by normative type; requirement rows (partition D rows such as SCN-C07) are never in it
    fixed = {}
    for e in layers['rules']:
        if e['mvp_applicability']['value'] == 'mvp_fixed':
            fixed[e['normative_type']] = fixed.get(e['normative_type'], 0) + 1
    rows = [e for e in layers['rules'] if e['normative_type'] == 'requirement_row']
    headline = {'mvp_fixed_rules_excluding_requirement_rows': sum(v for k, v in fixed.items() if k != 'requirement_row'),
                'mvp_fixed_rules_by_normative_type': dict(sorted(fixed.items())),
                'requirement_rows_in_the_rule_layer_reported_apart': len(rows),
                'requirement_rows_mvp_fixed': fixed.get('requirement_row', 0)}
    return {'ten_denominators': ten, 'scenario_classes_reported_separately': dict(sorted(classes.items())), 'rule_code_registries': registries,
            'rule_headline': headline, 'differential_vector_instances_not_scenarios': diff}


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
        if 'pattern' in schema and not re.fullmatch(schema['pattern'], value):
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

LAST_WARNINGS = []


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
        if 'encoding' in env:
            try:
                if env['encoding'] != ENCODING or type(env.get('strings')) is not list or type(env.get('shapes')) is not list:
                    raise ValueError('unknown encoding or missing tables')
                env = dict(env)
                env['records'] = decode_records(env['strings'], env['shapes'], env['records'])
            except (ValueError, TypeError, IndexError, KeyError) as exc:
                rep.add('partition_unreadable', '%s: undecodable compact records (%s)' % (rel, type(exc).__name__))
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


def check_schema_pins(root, manifest, rep):
    """The schemas are part of the commitment: pinned by the manifest and by the validator's own copy."""
    pins = manifest.get('schema_files')
    sdir = os.path.join(root, 'schemas')
    found = {}
    for fn in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
        if fn.endswith('.json'):
            with open(os.path.join(sdir, fn), 'rb') as fh:
                found[fn] = sha256_bytes(fh.read())
    if type(pins) is not dict or pins != found:
        rep.add('schema_not_pinned', 'schema files differ from the manifest pins (%s)' % ', '.join(sorted(
            k for k in set(found) | set(pins if type(pins) is dict else {}) if (pins or {}).get(k) != found.get(k))) or 'no pins')
    own = os.path.join(DEFAULT_ROOT, 'schemas')
    if os.path.isdir(own) and os.path.realpath(own) != os.path.realpath(sdir):
        for fn in sorted(os.listdir(own)):
            if fn.endswith('.json'):
                with open(os.path.join(own, fn), 'rb') as fh:
                    if found.get(fn) != sha256_bytes(fh.read()):
                        rep.add('schema_not_pinned', '%s differs from the validator\'s own schema copy' % fn)


def _gunzip_limited(packed, limit):
    import zlib
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    out = d.decompress(packed, limit + 1)
    if len(out) > limit or d.unconsumed_tail or not d.eof or d.unused_data:
        raise ValueError('gzip content is not exactly the committed size')
    return out


def _artifact_records(path, rep, art):
    try:
        with open(path, 'rb') as fh:
            data = fh.read()
    except OSError:
        rep.add('artifact_missing', art.get('path'))
        return None
    if str(art.get('path')).endswith('.gz') or art.get('gzip_sha256') is not None:
        # a committed artifact: the uncompressed content digest is authoritative; the gzip file digest is pinned as well, but
        # compressors differ between builds, so a different gzip of identical content is a warning and never a pass for other content
        packed = data
        try:
            data = _gunzip_limited(packed, art['bytes'])
        except (ValueError, OSError, KeyError, TypeError, __import__('zlib').error):
            rep.add('artifact_unreadable', '%s: not a gzip stream of the recorded size' % art.get('path'))
            return None
        if (sha256_bytes(packed) != art.get('gzip_sha256') or len(packed) != art.get('gzip_bytes')) and sha256_bytes(data) == art.get('sha256'):
            LAST_WARNINGS.append('WARNING artifact %s: the gzip file differs from its recorded gzip_sha256 but the decompressed content matches its recorded sha256 (a different compressor build); content digest taken as authoritative' % art.get('path'))
    if sha256_bytes(data) != art.get('sha256'):
        rep.add('artifact_hash_mismatch', art.get('path'))
        return None
    try:
        env = RR.loads_strict(data.decode('utf-8'))
        recs = decode_records(env['strings'], env['shapes'], env['records']) if env.get('encoding') == ENCODING else env['records']
    except (ValueError, TypeError, IndexError, KeyError, AttributeError):
        rep.add('artifact_unreadable', art.get('path'))
        return None
    if len(recs) != art.get('record_count'):
        rep.add('artifact_count_mismatch', '%s: manifest %s, file %d' % (art.get('path'), art.get('record_count'), len(recs)))
    return recs


def _artifact_file(adir, root, art):
    """Where an artifact is read from: a supplied directory by base name, else (committed artifacts) inside the catalogue root."""
    rel = str(art.get('path'))
    if adir is not None:
        return os.path.join(adir, os.path.basename(rel))
    if os.path.isabs(rel) or '\\' in rel or '..' in rel.split('/'):
        return os.path.join(root, '__refused__')
    return os.path.join(root, *rel.split('/'))


INSTANCE_ROW_TYPES = ('differential_instance->scenario',)
ROW_FLAGS = ('establishes_enforcement', 'establishes_test_coverage', 'establishes_qualification')


def _unique(recs, keyfn, rep, what, artifact):
    out = {}
    for r in recs:
        k = keyfn(r)
        if k in out:
            rep.add('artifact_duplicate_key', '%s: %s repeats %s' % (artifact, what, k))
        out[k] = r
    return out


def _row_view(row):
    """What an embedded relationship record must say about itself, given the G3 row it names."""
    prov = row.get('provenance')
    view = {'provenance': prov, 'source': None, 'method': None, 'supporting_refs': [], 'confidence_class': None, 'missing_evidence': None}
    if prov == 'SOURCE_STATED':
        src = row.get('source') or {}
        loc = src.get('location') or src.get('path')
        if src.get('repo') and src.get('revision') and loc:
            view['source'] = {'repo': src['repo'], 'revision': src['revision'],
                              'location': (src['path'] + ' :: ' + src['location']) if src.get('path') and src.get('location') else loc}
        else:
            view.update(provenance='UNRESOLVED', missing_evidence='G3 reports SOURCE_STATED without a complete source (repo, revision, location); not kept as SOURCE_STATED')
    elif prov == 'DERIVED':
        view['method'] = str(row.get('method') or 'unrecorded method')
        view['supporting_refs'] = [x for x in (row.get('supporting_references') or []) if type(x) is str and x] or [row.get('relationship_id') or 'unrecorded']
        view['confidence_class'] = row.get('confidence') if row.get('confidence') in ('high', 'medium', 'low', 'heuristic') else 'heuristic'
    else:
        view['missing_evidence'] = str(row.get('missing_evidence') or 'no evidence recorded for this link')
    return view


def _check_relationship_rows(recs, layers, rep, name, manifest=None):
    rows = _unique(recs, lambda r: r.get('relationship_id'), rep, 'relationship_id', name)
    for rid, row in rows.items():
        if type(rid) is not str or not re.fullmatch(r'REL-[0-9a-f]{16}', rid) or row.get('provenance') not in ('SOURCE_STATED', 'DERIVED', 'UNRESOLVED') \
                or type(row.get('type')) is not str or any(row.get(f) is not False for f in ROW_FLAGS):
            rep.add('artifact_row_schema', '%s: %s is not a well-formed relationship row (provenance, type and false establishes_* flags are required)' % (name, rid))
    if manifest is not None:
        _check_overlay_rows(rows, layers, rep, name, manifest)
    embedded, pairs = _embedded_and_pairs(layers)
    for rid, uses in embedded.items():
        row = rows.get(rid)
        if row is None:
            rep.add('artifact_index_mismatch', '%s: relationship row %s is absent' % (name, rid))
            continue
        want = _row_view(row)
        for owner, rel in uses:
            for k, v in want.items():
                if rel.get(k) != v:
                    rep.add('artifact_index_mismatch', '%s %s: embedded %s differs from relationship row %s' % (owner, (rel.get('field'), rel.get('to')), k, rid))
            for f in ROW_FLAGS:
                if rel.get(f) is not False or row.get(f) is not False:
                    rep.add('artifact_index_mismatch', '%s %s: %s must be false in the embedded record and in row %s' % (owner, (rel.get('field'), rel.get('to')), f, rid))
            kind = row.get('relation_kind')
            if kind in MVP_LINK_KINDS:
                _check_mvp_link(owner, rel, row, layers, rep, name)
            ends = (row.get('from_global'), row.get('to_global'))
            if rel.get('field') == 'source_reference_refs':
                ok = ends[0] == rel.get('to') and ends[1] == owner
            else:
                ok = frozenset(ends) == frozenset((owner, rel.get('to')))
            if not ok:
                rep.add('artifact_index_mismatch', '%s %s: endpoints of relationship row %s are %s' % (owner, (rel.get('field'), rel.get('to')), rid, ends))
    classes = classify_relationship_rows(rows, layers, embedded, pairs, rep, name)
    got = {'total': len(rows), 'by_class': classes, 'by_type_provenance_kind': _tpk(rows), 'revision_of_sources': _revision_sources(rows),
           'entry_placeholder_relationships': unresolved_accounting(layers)['unresolved_relationships']}
    want = (manifest or {}).get('relationship_row_accounting')
    if want is None:
        rep.add('artifact_count_mismatch', '%s: the manifest commits no relationship_row_accounting' % name)
    elif want != got:
        rep.add('artifact_count_mismatch', '%s: relationship rows %s differ from the committed accounting %s' % (name, json.dumps(got, sort_keys=True)[:300], json.dumps(want, sort_keys=True)[:300]))
    return classes


MVP_LINK_KINDS = {'mvp_requirement_row_link': ('requirement_row->scenario', 'requirement_row', 'DERIVED'),
                  'mvp_requirement_named_by_row': ('rule->scenario', None, 'DERIVED')}


def _check_mvp_link(owner, rel, row, layers, rep, name):
    """An MVP link is typed: a requirement row links to an MVP scenario as requirement_row->scenario, a rule as rule->scenario."""
    want_type, want_nt, want_prov = MVP_LINK_KINDS[row.get('relation_kind')]
    rule_id, scn_id = (owner, rel.get('to')) if rel.get('field') == 'scenario_refs' else (rel.get('to'), owner)
    ent = next((e for e in layers['rules'] if e.get('catalogue_id') == rule_id), None)
    tgt = next((e for e in layers['scenarios'] if e.get('catalogue_id') == scn_id), None)
    mv = (tgt or {}).get('mvp_applicability') or {}
    nt = (ent or {}).get('normative_type')
    if ent is None or tgt is None or row.get('type') != want_type or row.get('provenance') != want_prov \
            or (want_nt is not None and nt != want_nt) or (want_nt is None and nt == 'requirement_row') \
            or mv.get('value') != 'mvp_fixed' or mv.get('basis_id') != 'MB-MVPCHAIN-ROW' or rel.get('field') not in ('scenario_refs', 'rule_refs'):
        rep.add('mvp_link_untyped', '%s: %s -> %s is not a typed %s link to an MVP expectation-row scenario' % (name, rule_id, scn_id, want_type))


OVERLAY_BASIS = 'MB-ARCH-MVP-ROW'


def _pinned_overlays(manifest, rep=None):
    """The pinned MVP-link overlay documents named in manifest.regeneration, read from the repository and checked against their pin.

    Returns a list of parsed documents (a pinned file that is missing, altered or not named in the command is refused and left out)."""
    reg = manifest.get('regeneration') if type(manifest.get('regeneration')) is dict else {}
    pins = (reg.get('inputs') or {}).get('overlays') if type(reg.get('inputs')) is dict else None
    pins = pins if type(pins) is list else []
    cmd = reg.get('command') if type(reg.get('command')) is list else []
    named = [cmd[i + 1] for i, c in enumerate(cmd[:-1]) if c == '--overlay']
    out = []
    if rep is not None and sorted(named) != sorted(str(p.get('path')) for p in pins if type(p) is dict):
        rep.add('overlay_pin_mismatch', 'the --overlay arguments of the regeneration command and the pinned overlay inputs differ')
    for pin in pins:
        path = str(pin.get('path')) if type(pin) is dict else ''
        parts = path.split('/')
        if not path or os.path.isabs(path) or '..' in parts or '' in parts or '\\' in path:
            if rep is not None:
                rep.add('overlay_unreadable', '%s: the overlay path leaves the repository' % path)
            continue
        try:
            with open(os.path.join(HUB_ROOT, *parts), 'rb') as fh:
                raw = fh.read()
            doc = json.loads(raw.decode('utf-8'))
        except (OSError, ValueError):
            if rep is not None:
                rep.add('overlay_unreadable', '%s: the pinned overlay file cannot be read' % path)
            continue
        if sha256_bytes(raw) != pin.get('sha256'):
            if rep is not None:
                rep.add('overlay_pin_mismatch', '%s: the committed overlay file does not match the sha256 pinned in the manifest regeneration inputs' % path)
            continue
        if type(doc) is dict:
            out.append(doc)
    return out


def _overlay_expected(manifest, layers, rep=None):
    """{(rule catalogue id, scenario catalogue id): (type, provenance, relation_kind)} and {rule id: item} for the pinned overlays."""
    pairs, items = {}, {}
    scn = {}
    for e in layers['scenarios']:
        for n in e.get('native_ids', []):
            scn.setdefault(n, []).append(e.get('catalogue_id'))
    for doc in _pinned_overlays(manifest, rep):
        for it in doc.get('links', []) if type(doc.get('links')) is list else []:
            if type(it) is not dict:
                continue
            items[it.get('id')] = dict(it, _overlay_id=doc.get('overlay_id'))
            for n in it.get('target_native_ids', []):
                for sid in scn.get(n, []):
                    pairs[(it.get('id'), sid)] = (it.get('row_type'), it.get('provenance'), it.get('relation_kind'))
    return pairs, items


def _check_overlay_rows(rows, layers, rep, name, manifest):
    """The OVERLAY-partition rows, and every row of an MVP link kind, must be exactly the pinned overlay items (no extra, none missing)."""
    pairs, _items = _overlay_expected(manifest, layers)
    have = {}
    for rid, row in rows.items():
        if row.get('partition') == 'OVERLAY' or row.get('relation_kind') in MVP_LINK_KINDS:
            key = (row.get('from_global'), row.get('to_global'))
            if key in have:
                rep.add('overlay_rows_mismatch', '%s: duplicate overlay row for %s' % (name, key))
            have[key] = (row.get('type'), row.get('provenance'), row.get('relation_kind'))
            if row.get('partition') != 'OVERLAY' or key not in pairs or pairs[key] != have[key]:
                rep.add('overlay_rows_mismatch', '%s: row %s (%s -> %s, %s) is not an item of the pinned overlay' % (name, rid, key[0], key[1], row.get('relation_kind')))
    for key in sorted(set(pairs) - set(have), key=str):
        rep.add('overlay_rows_mismatch', '%s: overlay link %s -> %s has no OVERLAY row' % (name, key[0], key[1]))


def check_overlay(manifest, layers, rep):
    """MVP applicability granted by the overlay basis is allowed only on a rule that carries an overlay link and is listed in the overlay."""
    _pairs, items = _overlay_expected(manifest, layers, rep)
    for e in layers['rules']:
        cid = e.get('catalogue_id')
        ann = e.get('annotations') or {}
        mv = e.get('mvp_applicability') or {}
        item = items.get(cid)
        if mv.get('basis_id') == OVERLAY_BASIS:
            if item is None or not item.get('applicability') or ann.get('mvp_link_overlay') != item.get('_overlay_id') \
                    or not any(r.get('field') == 'scenario_refs' for r in e.get('relationships', []) if type(r) is dict) or mv != item.get('applicability'):
                rep.add('mvp_basis_misapplied', '%s: basis %s needs an overlay link, a listing in the pinned overlay and the applicability the overlay states' % (cid, OVERLAY_BASIS))
        if ann.get('mvp_link_overlay') is not None and item is None:
            rep.add('mvp_basis_misapplied', '%s: carries an overlay link annotation but is not listed in the pinned overlay' % cid)
    for cid, item in items.items():
        if not any(e.get('catalogue_id') == cid for e in layers['rules']):
            rep.add('mvp_basis_misapplied', '%s: overlay item names no rule entry' % cid)


def check_alias_collisions(layers, rep):
    """In the rule layer an alias must not equal the native id of another rule (a retained id never impersonates a distinct source identity).

    Scoped to rules: scenario and fixture entries legitimately keep the same short names as aliases across sources."""
    native = {}
    for e in layers['rules']:
        for n in e.get('native_ids', []):
            native.setdefault(n, set()).add(e.get('catalogue_id'))
    for e in layers['rules']:
        for a in e.get('aliases', []):
            if native.get(a, set()) - {e.get('catalogue_id')}:
                rep.add('alias_collides_native_id', 'rules %s: alias %r is the native id of another rule' % (e.get('catalogue_id'), a))


KIND_OF_PREFIX = (('R-', 'rule'), ('S-', 'scenario'), ('T-', 'test_implementation'), ('F-', 'fixture'), ('FD-', 'fixture'))
PAIR_FIELDS = {'candidate_equivalent': ('alias_candidates',), 'scenario_test': ('test_refs', 'scenario_refs')}
ROW_CLASSES = ('embedded', 'instance', 'unresolved', 'revision_of', 'pair_recorded', 'refused')


def _kind_of(x):
    for pre, kind in KIND_OF_PREFIX:
        if str(x).startswith(pre):
            return kind
    return 'evidence' if str(x).startswith('sha256:') else None


def classify_relationship_rows(rows, layers, embedded, pairs, rep=None, name=''):
    """Assign every G3 relationship row to exactly one class and, with rep, check the row against that class's signature.

    The classes are embedded (named by an entry's relationship record and compared elsewhere), instance (a differential
    instance of a suite scenario), unresolved (a stated gap, never a link), revision_of (a lineage revision of a scenario)
    and pair_recorded (its endpoints are already recorded by an embedded relationship). A row that fits none of them, or
    that fails the signature of its class, is refused. Returns {class: count}.
    """
    def bad(code, rid, why):
        if rep is not None:
            rep.add(code, '%s: relationship row %s %s' % (name, rid, why))
    ids = {}
    for layer in ENTRY_LAYERS:
        for e in layers[layer]:
            ids[e.get('catalogue_id')] = (layer, e)
    ev_digests = {e.get('evidence_digest') for e in layers['evidence']}
    hist = {}
    for r in layers['crosswalk']:
        if r.get('disposition') == 'HISTORICAL_REVISION_OF':
            hist.setdefault(r.get('raw_digest'), []).append(r.get('target'))
    lineage = {}
    for layer in ('scenarios', 'lineage_sets'):
        for e in layers[layer]:
            for l in e.get('lineage', []):
                if type(l) is dict:
                    lineage.setdefault(e.get('catalogue_id'), set()).add(l.get('digest'))
    counts = dict.fromkeys(ROW_CLASSES, 0)
    per_scenario = {}

    def known(x):
        return x in ids or x in ev_digests or bool(SR_RE.match(str(x))) or bool(re.fullmatch(r'sha256:[0-9a-f]{64}', str(x)))
    for rid, row in rows.items():
        a, b = row.get('from_global'), row.get('to_global')
        prov = row.get('provenance')
        if rid in embedded:
            counts['embedded'] += 1
            continue
        if row.get('type') in INSTANCE_ROW_TYPES:
            cls = 'instance'
        elif row.get('relation_kind') == 'revision_of':
            cls = 'revision_of'
        elif prov == 'UNRESOLVED':
            cls = 'unresolved'
        elif a is not None and b is not None and frozenset((a, b)) in pairs:
            cls = 'pair_recorded'
        else:
            counts['refused'] += 1
            bad('artifact_orphan_row', rid, '(%s -> %s, %s) is neither embedded nor of an accounted class' % (a, b, prov))
            continue
        counts[cls] += 1
        has = lambda *keys: any(row.get(k) not in (None, [], '', {}) for k in keys)
        if cls == 'instance':
            tgt = ids.get(b)
            if prov != 'DERIVED' or row.get('relation_kind') != 'differential_instance_membership' or has('source') \
                    or not str(a).startswith('DI:') or row.get('from') != a or tgt is None or tgt[0] != 'scenarios' \
                    or row.get('type') != 'differential_instance->scenario':
                bad('artifact_row_signature', rid, 'is not a derived differential-instance membership of an existing scenario')
            else:
                per_scenario[b] = per_scenario.get(b, 0) + 1
        elif cls == 'unresolved':
            if has('source', 'method', 'assertions', 'supporting_references') or type(row.get('missing_evidence')) is not str or not row['missing_evidence'].strip():
                bad('artifact_row_signature', rid, 'is an unresolved row that carries a source, a method or no missing-evidence reason')
            if any(x is not None and not known(x) for x in (a, b)):
                bad('artifact_row_signature', rid, 'is an unresolved row naming an endpoint that is not in the catalogue')
        elif cls == 'revision_of':
            src = row.get('source') if type(row.get('source')) is dict else {}
            rev = str(b if b is not None else row.get('to'))
            owner = ids.get(a)
            digest = 'sha256:' + rev[4:] if rev.startswith('REV:') else None
            ok = prov == 'SOURCE_STATED' and row.get('type') == 'scenario->scenario' and owner is not None and owner[0] == 'scenarios' \
                and digest in hist and (digest in lineage.get(a, ()) or any(str(t).split('-', 1)[-1] == str(a).split('-', 1)[-1] for t in hist.get(digest, ()))) \
                and src.get('repo') == (owner[1].get('source') or {}).get('repo') and src.get('revision') and (src.get('location') or src.get('path'))
            if not ok:
                bad('artifact_row_signature', rid, 'is not a stated revision of its scenario that the lineage records and the crosswalk carry')
        else:
            kinds = (_kind_of(a), _kind_of(b))
            fields = PAIR_FIELDS.get(row.get('relation_kind'), ())
            recorded = {rel.get('provenance') for rel in pairs.get(frozenset((a, b)), []) if rel.get('field') in fields}
            if None in kinds or row.get('type') != '%s->%s' % kinds and row.get('type') != '%s->%s' % kinds[::-1] or recorded != {prov} \
                    or _row_view(row)['provenance'] != prov:
                bad('artifact_row_signature', rid, 'does not match the relationship already recorded for %s and %s' % (a, b))
    for sid, e in ((k, v[1]) for k, v in ids.items() if v[0] == 'scenarios'):
        if per_scenario.get(sid, 0) != (e.get('differential_instance_count') or 0):
            bad('artifact_row_signature', sid, 'has %d differential-instance rows, the scenario records %s' % (per_scenario.get(sid, 0), e.get('differential_instance_count') or 0))
    return counts


def relationship_row_accounting(rows, layers):
    """The committed accounting of the G3 relationship rows: the class of every row and the (type, provenance, relation_kind) counts."""
    embedded, pairs = _embedded_and_pairs(layers)
    return {'total': len(rows), 'by_class': classify_relationship_rows(rows, layers, embedded, pairs), 'by_type_provenance_kind': _tpk(rows), 'revision_of_sources': _revision_sources(rows),
            'entry_placeholder_relationships': unresolved_accounting(layers)['unresolved_relationships']}


def _tpk(rows):
    by = {}
    for row in rows.values():
        k = (row.get('type'), row.get('provenance'), row.get('relation_kind'), row.get('method'), row.get('confidence'))
        by[k] = by.get(k, 0) + 1
    return [{'type': k[0], 'provenance': k[1], 'relation_kind': k[2], 'method': k[3], 'confidence': k[4], 'rows': n}
            for k, n in sorted(by.items(), key=lambda kv: tuple(str(x) for x in kv[0]))]


def _revision_sources(rows):
    by = {}
    for row in rows.values():
        if row.get('relation_kind') == 'revision_of':
            src = row.get('source') if type(row.get('source')) is dict else {}
            k = (src.get('repo'), src.get('revision'))
            by[k] = by.get(k, 0) + 1
    return [{'repo': k[0], 'revision': k[1], 'rows': n} for k, n in sorted(by.items(), key=lambda kv: tuple(str(x) for x in kv[0]))]


def _embedded_and_pairs(layers):
    embedded, pairs = {}, {}
    for layer in REF_FIELDS:
        for e in layers[layer]:
            owner = e.get('catalogue_id') or e.get('evidence_digest')
            for rel in e.get('relationships', []):
                pairs.setdefault(frozenset((owner, rel.get('to'))), []).append(rel)
                if rel.get('row_id') is not None:
                    embedded.setdefault(rel['row_id'], []).append((owner, rel))
    return embedded, pairs


def check_artifacts(adir, manifest, layers, rep, root=None, schemas=None):
    """Verify the external, content-addressed artifacts against the committed index (supplied, or committed beside the manifest)."""
    for art in manifest.get('external_artifacts', []):
        recs = _artifact_records(_artifact_file(adir, root, art), rep, art)
        if recs is None:
            continue
        kind = art.get('kind')
        name = str(art.get('path'))
        try:
            if kind == 'evidence_records':
                full = _unique(recs, lambda r: r['evidence_digest'], rep, 'evidence_digest', name)
                if schemas and 'evidence' in schemas:
                    for r in recs:
                        for err in schema_errors(r, 'evidence', schemas, 'evidence %s' % r.get('evidence_digest'))[:3]:
                            rep.add('artifact_row_schema', '%s: %s' % (name, err))
                if set(full) != {e['evidence_digest'] for e in layers['evidence']}:
                    rep.add('artifact_index_mismatch', 'evidence artifact and index cover different records')
                for e in layers['evidence']:
                    f = full.get(e['evidence_digest'])
                    if f is None:
                        continue
                    if digest_of(f) != f.get('digest') or f.get('digest') != e.get('full_record_digest') or slim_evidence(f) != e:
                        rep.add('artifact_index_mismatch', 'evidence %s: full record does not match its index entry' % e['evidence_digest'])
            elif kind == 'crosswalk_rows':
                full = _unique(recs, lambda r: entry_key('crosswalk', r), rep, 'crosswalk row', name)
                if schemas and 'crosswalk' in schemas:
                    for r in recs:
                        for err in schema_errors(r, 'crosswalk', schemas, 'row %s' % entry_key('crosswalk', r))[:3]:
                            rep.add('artifact_row_schema', '%s: %s' % (name, err))
                if set(full) != {entry_key('crosswalk', r) for r in layers['crosswalk']}:
                    rep.add('artifact_index_mismatch', 'crosswalk artifact and committed crosswalk cover different rows')
                by_id = {l: {e.get('catalogue_id'): e for e in layers[l]} for l in ENTRY_LAYERS}
                for r in layers['crosswalk']:
                    f = full.get(entry_key('crosswalk', r))
                    if f is None:
                        continue
                    if slim_crosswalk(f) != r:
                        rep.add('artifact_index_mismatch', 'crosswalk row %s differs from its full row' % entry_key('crosswalk', r))
                    # the native id and the path that only the full row carries must agree with the entry it names
                    tgt = next((by_id[l].get(f.get('target')) for l in ENTRY_LAYERS if f.get('target') in by_id[l]), None)
                    if tgt is not None and f.get('disposition') in ('CANONICAL', 'ALIAS_OF') and f.get('native_id') is not None:
                        known = set(tgt.get('native_ids', [])) | set(tgt.get('aliases', [])) | {tgt.get('title'), (tgt.get('source') or {}).get('path')}
                        known |= {l.get('path') for l in tgt.get('locations', []) if type(l) is dict}
                        if f['native_id'] not in known:
                            rep.add('artifact_index_mismatch', 'crosswalk row %s: native id %r is not carried by %s' % (entry_key('crosswalk', r), f['native_id'], f.get('target')))
            elif kind == 'relationship_rows':
                _check_relationship_rows(recs, layers, rep, name, manifest)
            else:
                rep.add('artifact_unknown_kind', str(kind))
        except (KeyError, TypeError, AttributeError):
            rep.add('artifact_unreadable', '%s: malformed records' % art.get('path'))


# The revisions the real catalogue may cite, pinned here so that they are covered by the validator's own bytes. Tag commits first,
# then the two post-tag heads that the dataset names separately. Values are commit-hash prefixes; a recorded revision must contain
# a 40-hex hash that starts with the prefix pinned for its repository, or read exactly "unrecorded".
TAG_NAME = 'review-v0.1-g8-r10-20261022'
PINNED_TAG_COMMITS = {'cogno-us/cognous-open-control-stack': 'a2d9396c', 'cogno-us/cognous-institutional-governance': '9b5ab721',
                      'cogno-us/cognous-control-plane': '0a41faa9', 'cogno-us/cognous-action-manifest': 'fa170815',
                      'cogno-us/cognous-execution-runtime': 'ec728da6', 'cogno-us/cognous-replay-bundle': '028f63d1',
                      'cogno-us/cognous-governance-evidence-pack': 'a3ebbb90', 'cogno-us/open-decision-evidence-standard': 'e86a25a1',
                      'cogno-us/cognous-open-control-stack-verifier': 'c0b8ba1f', 'cogno-us/cognous-stack-qualification': '195c728f',
                      'cogno-us/cognous-governed-exchange': '7f7569b0', 'cogno-us/cognous-open-control-stack-ergonomics': '54807212'}
PINNED_POST_TAG = {'cogno-us/cognous-stack-qualification': ('4298247e', 'c106b869')}


def _pinned_revision(repo, rev, entry=False):
    """A pinned repository with a revision that carries one of its pinned hashes (or, for an entry, exactly "unrecorded")."""
    if repo not in PINNED_TAG_COMMITS:
        return False
    if rev == 'unrecorded':
        return entry
    hashes = re.findall(r'(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])', str(rev))
    ok = {PINNED_TAG_COMMITS.get(repo)} | set(PINNED_POST_TAG.get(repo, ()))
    return any(h[:8] in ok for h in hashes)


def check_source_pins(manifest, layers, rep):
    inv = [(r.get('repo'), r.get('revision')) for s_ in manifest.get('source_inventory', []) if type(s_) is dict for r in s_.get('source_repo_revisions', []) if type(r) is dict]
    real = any(repo in PINNED_TAG_COMMITS for repo, _ in inv)
    if manifest.get('synthetic_sample') is True and real:
        rep.add('synthetic_flag_on_real_catalogue', 'the manifest names pinned repositories of the real catalogue but claims synthetic_sample')
    # a small fixture that names none of the pinned repositories is not the real catalogue; its manifest digest is pinned by the reviewer
    for repo, rev in (inv if real and manifest.get('synthetic_sample') is False else []):
        if rev == 'unrecorded' and repo in PINNED_TAG_COMMITS or (repo == 'unrecorded' and rev == 'unrecorded'):
            continue
        if not _pinned_revision(repo, rev):
            rep.add('source_revision_not_pinned', 'inventory names %s @ %s, which is not in the validator-pinned list' % (repo, rev))
    if real and manifest.get('synthetic_sample') is False:
        # every cited source must be a pinned repository carrying a pinned hash, or read exactly "unrecorded"
        for layer in ENTRY_LAYERS + ('lineage_sets',):
            for e in layers[layer]:
                cites = [e.get('source')] + [l for l in e.get('locations', []) if type(l) is dict]
                for c in cites:
                    c = c if type(c) is dict else {}
                    if not _pinned_revision(c.get('repo'), c.get('revision'), True):
                        rep.add('source_revision_not_pinned', '%s %s cites %s @ %s, which is not in the validator-pinned list' % (layer, e.get('catalogue_id'), c.get('repo'), c.get('revision')))
        for e in layers['evidence']:
            c = e.get('source_commitment') if type(e.get('source_commitment')) is dict else {}
            if not _pinned_revision(c.get('repo'), c.get('revision'), True):
                rep.add('source_revision_not_pinned', 'evidence %s cites %s @ %s, which is not in the validator-pinned list' % (e.get('evidence_digest'), c.get('repo'), c.get('revision')))
    # a combined pseudo-repository is not a repository
    for layer in ENTRY_LAYERS:
        for e in layers[layer]:
            places = [(e.get('source') or {}).get('repo')] + [l.get('repo') for l in e.get('locations', []) if type(l) is dict]
            if any(str(x).startswith('multi:') for x in places):
                rep.add('pseudo_repo', '%s %s cites a combined multi: pseudo-repository' % (layer, e.get('catalogue_id')))
    for e in layers['evidence']:
        if str((e.get('source_commitment') or {}).get('repo')).startswith('multi:'):
            rep.add('pseudo_repo', 'evidence %s cites a combined multi: pseudo-repository' % e.get('evidence_digest'))


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
                bad = sorted(k for k in ann if annotation_key_forbidden(k))
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
            if not cid.startswith((NAMESPACE[layer],) + EXTRA_PREFIXES.get(layer, ())):
                rep.add('namespace_mismatch', '%s id %s lacks prefix %s' % (layer, cid, NAMESPACE[layer]))
            if not ID_RE.fullmatch(cid):
                rep.add('id_form', '%s id %r must be printable ASCII without whitespace' % (layer, cid))
        ids[layer] = seen
    seen = set()
    for r in layers['lineage_sets']:
        cid = r.get('catalogue_id') if type(r) is dict else None
        if cid in seen:
            rep.add('duplicate_id', 'lineage_sets %s' % cid)
        seen.add(cid)
        if type(cid) is not str or not cid.startswith(LINEAGE_PREFIX):
            rep.add('namespace_mismatch', 'lineage set id %s lacks prefix %s' % (cid, LINEAGE_PREFIX))
    ids['lineage_sets'] = seen
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
        if not ref.startswith((prefix,) + EXTRA_PREFIXES.get(layer, ())) or ref not in ids[layer]:
            rep.add('unresolved_reference', '%s.%s -> %s (typed %s)' % (owner, field, ref, layer))


def _evidence_refs(rep, owner, refs, ids):
    for ref in refs:
        if type(ref) is str and not ref.startswith('UNRESOLVED:') and ref not in ids['evidence']:
            rep.add('unresolved_reference', '%s.evidence_digest_refs -> %s' % (owner, ref))


def check_references(layers, ids, rep):
    by = {layer: {r['catalogue_id']: r for r in layers[layer] if type(r) is dict and 'catalogue_id' in r} for layer in ENTRY_LAYERS + ('lineage_sets',)}
    for r in layers['rules']:
        o = r.get('catalogue_id')
        _refs(rep, o, 'scenario_refs', r.get('scenario_refs', []), 'scenarios', ids)
        _refs(rep, o, 'test_refs', r.get('test_refs', []), 'tests', ids)
        _evidence_refs(rep, o, r.get('evidence_digest_refs', []), ids)
    for r in layers['scenarios']:
        o = r.get('catalogue_id')
        _refs(rep, o, 'rule_refs', r.get('rule_refs', []), 'rules', ids)
        _refs(rep, o, 'test_refs', r.get('test_refs', []), 'tests', ids)
        _refs(rep, o, 'fixture_refs', r.get('fixture_refs', []), 'fixtures', ids)
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
    # related_refs and alias_candidates stay inside one layer and never name the entry itself
    for layer in ENTRY_LAYERS:
        for r in layers[layer]:
            o = r.get('catalogue_id')
            for field in ('related_refs', 'alias_candidates'):
                _refs(rep, o, field, r.get(field, []), layer, ids)
                if o in r.get(field, []):
                    rep.add('unresolved_reference', '%s.%s names itself' % (o, field))
    # a source reference names a source-only crosswalk row by partition and raw digest, and that row must exist
    sr_rows = {}
    for cw in layers['crosswalk']:
        if type(cw) is dict and cw.get('disposition') == 'SOURCE_ONLY_ARTIFACT' and type(cw.get('raw_digest')) is str:
            sr_rows.setdefault(cw['raw_digest'][7:], set()).add(str(cw.get('raw_set')))
    for layer in ENTRY_LAYERS:
        for r in layers[layer]:
            for ref in r.get('source_reference_refs', []) if type(r.get('source_reference_refs')) is list else []:
                if type(ref) is not str or ref.startswith('UNRESOLVED:'):
                    continue
                m = SR_RE.match(ref)
                sets = sr_rows.get(m.group(2)) if m else None
                if not m or not sets or not any(x.startswith(m.group(1)) for x in sets):
                    rep.add('unresolved_reference', '%s.source_reference_refs -> %s (no SOURCE_ONLY_ARTIFACT crosswalk row)' % (r.get('catalogue_id'), ref))
    # no list may repeat a target
    for layer in REF_FIELDS:
        for r in layers[layer]:
            for field in REF_FIELDS[layer]:
                val = r.get(field)
                strs = [v for v in val if type(v) is str] if type(val) is list else []
                if len(set(strs)) != len(strs):
                    rep.add('duplicate_ref', '%s.%s repeats a target' % (r.get('catalogue_id') or r.get('evidence_digest'), field))
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
                if key in seen:
                    rep.add('relationship_duplicate', '%s %s' % (owner, key))
                seen[key] = rel
                prov = rel.get('provenance')
                src = rel.get('source')
                if prov == 'SOURCE_STATED':
                    if not src or rel.get('method') is not None or rel.get('supporting_refs') or rel.get('confidence_class') is not None or rel.get('missing_evidence') is not None:
                        rep.add('relationship_provenance', '%s %s: SOURCE_STATED needs exact source repo, revision and location and nothing derived' % (owner, key))
                    elif any(str(src.get(k, '')).strip() in ('', 'unrecorded') for k in ('repo', 'revision', 'location')):
                        rep.add('relationship_provenance', '%s %s: SOURCE_STATED cannot carry an unrecorded source revision or location' % (owner, key))
                elif prov == 'DERIVED':
                    if src is not None or not rel.get('method') or not rel.get('supporting_refs') or rel.get('confidence_class') is None or rel.get('missing_evidence') is not None:
                        rep.add('relationship_provenance', '%s %s: DERIVED needs method, supporting refs and confidence class, and no source claim' % (owner, key))
                elif prov == 'UNRESOLVED':
                    if not str(rel.get('missing_evidence') or '').strip() or src is not None or rel.get('method') is not None:
                        rep.add('relationship_provenance', '%s %s: UNRESOLVED must name the missing evidence' % (owner, key))
                for flag in ('establishes_enforcement', 'establishes_test_coverage', 'establishes_qualification'):
                    if rel.get(flag) is not False:
                        rep.add('relationship_provenance', '%s %s: %s must be false' % (owner, key, flag))
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
        index_form = 'full_record_digest' in e
        if type(art) is not dict or not art.get('path') or (not art.get('record_digest') and not index_form):
            rep.add('evidence_commitment_missing', '%s lacks an artifact commitment' % o)
        elif art.get('path') == 'unrecorded':
            rep.add('evidence_commitment_missing', '%s names no artifact path ("unrecorded"); an evidence entry that claims a commitment must name one' % o)
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
    raw_rows = {raw_ref(r.get('raw_set'), r.get('raw_index')): r for r in rows if type(r) is dict}
    referenced = {layer: {} for layer in ENTRY_LAYERS + ('lineage_sets',)}
    evid_rows = {}
    canonical_rows = {}
    co_rows = {}
    diff_rows = {}
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
            if layer is None and type(target) is str and target.startswith(LINEAGE_PREFIX):
                layer = 'lineage_sets'
            if tier not in ('RULE_REVISION', 'HISTORICAL_REVISION') or layer is None or target not in by[layer]:
                rep.add('crosswalk_tier_mismatch' if layer else 'unresolved_reference', '%s HISTORICAL_REVISION_OF %s' % (ref, target))
                continue
            entry = by[layer][target]
            if not any(l.get('raw_ref') == ref and l.get('digest') == r.get('raw_digest') for l in entry.get('lineage', [])):
                rep.add('revision_not_retained', '%s: revision is not in the lineage of %s' % (ref, target))
            referenced[layer].setdefault(target, set()).add(ref)
        elif disp == 'ATTACHED_TO_ENTRY':
            # a raw record recorded as attached to an existing entry (a baseline outcome on its fixture, a rule note); never a new entry
            layer = next((l for l in ENTRY_LAYERS if type(target) is str and target.startswith((NAMESPACE[l],) + EXTRA_PREFIXES.get(l, ()))), None)
            if tier in ('EXECUTION_EVIDENCE', 'PARAMETRIZED_INSTANCE', 'COLLECTED_NODE') or layer is None or target not in by[layer]:
                rep.add('unresolved_reference' if layer else 'crosswalk_tier_mismatch', '%s ATTACHED_TO_ENTRY %s (tier %s)' % (ref, target, tier))
                continue
            referenced[layer].setdefault(target, set()).add(ref)
        elif disp == 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE':
            if tier == 'PARAMETRIZED_INSTANCE' and (r.get('annotations') or {}).get('relation') == 'DIFFERENTIAL_VECTOR_INSTANCE':
                # a recorded differential vector instance belongs to its differential scenario, not to a test
                if type(target) is not str or target not in by['scenarios']:
                    rep.add('unresolved_reference', '%s -> %s' % (ref, target))
                    continue
                referenced['scenarios'].setdefault(target, set()).add(ref)
                diff_rows.setdefault(target, []).append(ref)
            elif tier in ('PARAMETRIZED_INSTANCE', 'COLLECTED_NODE'):
                if target not in by['tests']:
                    rep.add('unresolved_reference', '%s -> %s' % (ref, target))
                    continue
                referenced['tests'].setdefault(target, set()).add(ref)
                if tier == 'PARAMETRIZED_INSTANCE':
                    evid_rows.setdefault(('inst', target), []).append(ref)
            elif tier == 'EXECUTION_EVIDENCE':
                if target not in ids['evidence']:
                    rep.add('unresolved_reference', '%s -> %s' % (ref, target))
                    continue
                evid_rows.setdefault(('ev', target), []).append(ref)
            else:
                rep.add('crosswalk_tier_mismatch', '%s: tier %s cannot be a test instance, collected node or execution occurrence' % (ref, tier))
        elif disp == 'SOURCE_ONLY_ARTIFACT':
            if tier not in SOURCE_ONLY_TIERS or target is not None:
                rep.add('crosswalk_tier_mismatch', '%s: SOURCE_ONLY_ARTIFACT needs a null target and a tier that is not a canonical, revision or evidence tier (found %s); use UNRESOLVED with a reason instead' % (ref, tier))
        elif disp == 'UNRESOLVED':
            if target is not None or not r.get('unresolved_reason'):
                rep.add('crosswalk_tier_mismatch', '%s: UNRESOLVED needs a null target and a reason' % ref)
        if tier == 'EXECUTION_EVIDENCE' and disp not in ('TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', 'UNRESOLVED'):
            rep.add('evidence_as_rule', '%s: execution evidence cannot have disposition %s' % (ref, disp))
        cos = (r.get('annotations') or {}).get('co_registered')
        for co in ([] if cos is None else cos if type(cos) is list else [cos]):
            # one raw record that also stands for a scenario (a fixture file that defines a case)
            clayer = next((l for l in ENTRY_LAYERS if type(co) is str and co.startswith(NAMESPACE[l])), None)
            if clayer != 'scenarios' or co not in by[clayer]:
                rep.add('unresolved_reference', '%s co_registered %s is not a scenario entry' % (ref, co))
            else:
                referenced[clayer].setdefault(co, set()).add(ref)
                co_rows.setdefault(co, []).append(ref)
    # every entry's raw_refs equal the crosswalk rows that point at it
    for layer in ENTRY_LAYERS + ('lineage_sets',):
        for cid, entry in by[layer].items():
            want = referenced[layer].get(cid, set())
            have = set(entry.get('raw_refs', []))
            if want != have:
                rep.add('raw_refs_mismatch', '%s: raw_refs %s differ from crosswalk %s' % (cid, sorted(have), sorted(want)))
            ref_only = layer == 'fixtures' and (entry.get('annotations') or {}).get('reference_only') is True
            if layer != 'lineage_sets' and not ref_only and cid not in canonical_rows and cid not in co_rows and not (layer == 'scenarios' and diff_rows.get(cid)):
                rep.add('crosswalk_row_missing', '%s has no CANONICAL or co-registered crosswalk row' % cid)
            if layer == 'lineage_sets' and not entry.get('lineage'):
                rep.add('revision_not_retained', '%s carries no lineage' % cid)
            for l in entry.get('lineage', []):
                row = raw_rows.get(l.get('raw_ref'))
                if row is None or row.get('raw_digest') != l.get('digest') or row.get('disposition') != 'HISTORICAL_REVISION_OF' or row.get('target') != cid:
                    rep.add('lineage_without_crosswalk_row', '%s lineage %s does not point at a HISTORICAL_REVISION_OF crosswalk row with the same digest' % (cid, l.get('raw_ref')))
    for sid, entry in by['scenarios'].items():
        n = len(diff_rows.get(sid, []))
        if entry.get('differential_instance_count', 0) != n:
            rep.add('instance_count_mismatch', '%s: differential_instance_count %s, crosswalk rows %d' % (sid, entry.get('differential_instance_count', 0), n))
    for tid, entry in by['tests'].items():
        n = len(evid_rows.get(('inst', tid), []))
        if entry.get('parametrized_instance_count') != n:
            rep.add('instance_count_mismatch', '%s: count %s, crosswalk rows %d' % (tid, entry.get('parametrized_instance_count'), n))
    for e in layers['evidence']:
        want = set(evid_rows.get(('ev', e.get('evidence_digest')), []))
        if want != set(e.get('raw_refs', [])):
            rep.add('raw_refs_mismatch', '%s: evidence raw_refs differ from crosswalk' % e.get('evidence_digest'))


def check_directives(layers, manifest, rep):
    """The seven standing refusals, each stated against the catalogue itself (not only against its derivation)."""
    by = {l: {r.get('catalogue_id'): r for r in layers[l] if type(r) is dict} for l in ('rules', 'scenarios', 'tests', 'fixtures')}
    kinds = {e.get('evidence_digest'): e.get('evidence_kind') for e in layers['evidence'] if type(e) is dict}
    field_of = {'implementation_coverage': 'test_refs', 'test_coverage': 'evidence_digest_refs', 'independent_qualification': 'evidence_digest_refs'}
    for row in layers['coverage']:
        if type(row) is not dict:
            continue
        sid = row.get('subject_id')
        subj = by.get(row.get('subject_layer'), {}).get(sid)
        if subj is None:
            continue
        prov = _provenance_of(subj)
        a = row.get('assessments') or {}
        # 1. a derived link is a candidate only: it is never implemented, tested or independently qualified coverage
        for name, field in field_of.items():
            st = (a.get(name) or {}).get('status')
            if st in ('source_stated_link', 'source_stated_record'):
                for b in (a[name].get('basis_refs') or []):
                    if prov.get((field, b)) != 'SOURCE_STATED':
                        rep.add('derived_reported_as_coverage', '%s: %s rests on %s whose link is %s, not SOURCE_STATED' % (sid, name, b, prov.get((field, b))))
                    if name == 'independent_qualification' and kinds.get(b) != 'independent_qualification_record':
                        rep.add('derived_reported_as_coverage', '%s: independent qualification rests on %s, which is not an independent qualification record' % (sid, b))
        if 'independently_qualified' in (row.get('states') or []) and (a.get('independent_qualification') or {}).get('status') != 'source_stated_record':
            rep.add('derived_reported_as_coverage', '%s: states say independently_qualified without a source-stated qualification record' % sid)
        for st, nm in (('implemented', 'implementation_coverage'), ('tested', 'test_coverage')):
            if st in (row.get('states') or []) and (a.get(nm) or {}).get('status') != 'source_stated_link':
                rep.add('derived_reported_as_coverage', '%s: state %s without a SOURCE_STATED link on the subject itself' % (sid, st))
        # 2. an unresolved relationship never serves as a basis for any established coverage, and never leaves completeness
        unresolved = {(r.get('field'), r.get('to')) for r in subj.get('relationships', []) if r.get('provenance') == 'UNRESOLVED'}
        for name, field in field_of.items():
            for b in (a.get(name) or {}).get('basis_refs') or []:
                if (field, b) in unresolved:
                    rep.add('unresolved_became_established', '%s: %s uses %s, an UNRESOLVED relationship' % (sid, name, b))
        if (unresolved or (subj.get('mvp_applicability') or {}).get('value') == 'unresolved') and (a.get('catalogue_completeness') or {}).get('status') != 'has_unresolved':
            rep.add('unresolved_hidden_from_completeness', '%s: unresolved items present but completeness is not reported as has_unresolved' % sid)
        # 3. a historical verdict never becomes a current coverage or applicability statement
        if set(row) & {'verdict', 'historical_verdict_verbatim', 'result', 'pass', 'passed', 'outcome'}:
            rep.add('historical_result_assigned_to_current', '%s: coverage row carries a verdict-shaped member' % sid)
    ev_ids = set(kinds)
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        for e in layers[layer]:
            mv = e.get('mvp_applicability') or {}
            for k in ('basis_id', 'source_ref', 'reason'):
                if type(mv.get(k)) is str and (mv[k] in ev_ids or re.search(r'\bPASS\b', mv[k])):
                    rep.add('historical_result_assigned_to_current', '%s %s: applicability %s names a historical run result' % (layer, e.get('catalogue_id'), k))
    for e in layers['evidence']:
        if type(e) is dict and e.get('current_qualification_effect') != 'none':
            rep.add('historical_result_assigned_to_current', '%s: a historical record cannot carry a current qualification effect' % e.get('evidence_digest'))
    # 4. suite-level rows and differential suites are not logical scenarios
    for sid, e in by['scenarios'].items():
        if e.get('scenario_class') == 'logical' and e.get('differential_instance_count', 0) > 0:
            rep.add('suite_rows_counted_as_logical', '%s: a differential suite with instance rows is not a logical scenario' % sid)
    # 5. instances, collected nodes and repeated executions are never entries of their own
    for r in layers['crosswalk']:
        if type(r) is dict and r.get('tier') in ('PARAMETRIZED_INSTANCE', 'COLLECTED_NODE', 'EXECUTION_EVIDENCE') and r.get('disposition') in ('CANONICAL', 'ALIAS_OF', 'ATTACHED_TO_ENTRY'):
            rep.add('instances_counted_as_unique', '%s:%s: tier %s cannot be an entry or an attachment target of its own' % (r.get('raw_set'), r.get('raw_index'), r.get('tier')))
    # 6. normative rules, reason codes and advisory principles stay distinct
    reg = {'0.1': set(), '0.2': set()}
    for e in layers['rules']:
        ver = _registry_version(e)
        if ver and e.get('normative_type') in ('mandatory', 'constitutional_floor', 'conditional'):
            rep.add('normative_vocabulary_conflated', '%s: a code-registry entry cannot be typed %s' % (e.get('catalogue_id'), e.get('normative_type')))
        if ver == '0.2' and any(n.endswith('@0.1') for n in list(e.get('native_ids', [])) + list(e.get('aliases', []))):
            rep.add('registry_versions_merged', '%s: a 0.2 entry carries a 0.1 identity; the two labels stay distinct entries' % e.get('catalogue_id'))
        if ver == '0.1' and not all(n.endswith('@0.1') for n in e.get('native_ids', [])):
            rep.add('registry_versions_merged', '%s: a 0.1 entry carries a non-0.1 identity' % e.get('catalogue_id'))
    # the committed denominators equal the recomputed ones; nothing is merged into a headline
    want = compute_denominators(layers)
    if manifest.get('denominators') != want:
        rep.add('denominator_mismatch', 'manifest denominators differ from the recomputed denominators')
    if len(want['ten_denominators']) != 10:
        rep.add('denominator_mismatch', 'the ten denominators must stay separate')
    # 7. unresolved records stay in the completeness accounting, per layer as well as in total
    if manifest.get('unresolved_by_layer') != unresolved_by_layer(layers):
        rep.add('unresolved_accounting_mismatch', 'manifest per-layer unresolved accounting differs from the entries')


def unresolved_by_layer(layers):
    out = {}
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        n_rel = n_ph = n_mvp = 0
        for e in layers[layer]:
            rels = [r for r in e.get('relationships', []) if r.get('provenance') == 'UNRESOLVED']
            n_rel += len(rels)
            n_ph += sum(1 for _, t in ref_pairs(layer, e) if t.startswith('UNRESOLVED:'))
            n_mvp += (e.get('mvp_applicability') or {}).get('value') == 'unresolved'
        out[layer] = {'unresolved_relationships': n_rel, 'unresolved_placeholders': n_ph, 'unresolved_mvp_applicability': n_mvp}
    out['crosswalk'] = {'unresolved_rows': sum(1 for r in layers['crosswalk'] if r.get('disposition') == 'UNRESOLVED')}
    out['evidence'] = {'kind_unknown': sum(1 for e in layers['evidence'] if e.get('evidence_kind') == 'unknown'),
                       'unrecorded_source_revision': sum(1 for e in layers['evidence'] if (e.get('source_commitment') or {}).get('revision') == 'unrecorded')}
    return out


def check_mvp(layers, rep):
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        for r in layers[layer]:
            mv = r.get('mvp_applicability')
            if type(mv) is not dict or type(mv.get('value')) is not str or not str(mv.get('reason', '')).strip():
                rep.add('mvp_applicability_unclassified', '%s %s' % (layer, r.get('catalogue_id')))
            elif mv['value'] != 'unresolved' and (len(str(mv.get('basis_id') or '').strip()) < 3 or len(str(mv.get('source_ref') or '').strip()) < 8):
                # whether the named source really says so cannot be mechanised; a missing basis can be refused
                rep.add('mvp_basis_missing', '%s %s: %s needs a basis id and a source reference' % (layer, r.get('catalogue_id'), mv['value']))
    for r in layers['rules']:
        # a requirement row is not a governance rule: it is linked to MVP scenarios and is never mvp_fixed itself
        if r.get('normative_type') == 'requirement_row' and (r.get('mvp_applicability') or {}).get('value') == 'mvp_fixed':
            rep.add('requirement_row_mvp_fixed', '%s: a requirement row cannot be mvp_fixed as a rule; it carries typed links to MVP scenarios' % r.get('catalogue_id'))
    for layer in ENTRY_LAYERS:
        for r in layers[layer]:
            ann = r.get('annotations') or {}
            for m in ann.get('merged_from', []) if type(ann.get('merged_from')) is list else []:
                if type(m) is not dict or m.get('id') not in r.get('aliases', []) or not str(m.get('basis', '')).strip():
                    rep.add('merge_basis_missing', '%s %s: a merge must retain the merged id as an alias and state its basis' % (layer, r.get('catalogue_id')))


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
        parts = str(item.get('path', '')).split('/')
        if os.path.isabs(str(item.get('path', ''))) or '..' in parts or '' in parts or '\\' in str(item.get('path', '')):
            rep.add('registry_record_unreadable', '%s: path leaves the registry root' % item.get('path'))
            continue
        path = os.path.join(root, *parts)
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


TRACKED_ATTRIBUTES = ('scenario_class', 'normative_type', 'adoption_status', 'mvp_applicability', 'release_scope')


def check_previous(prev_root, layers, rep):
    perrs, _ = validate(prev_root)
    if perrs:
        rep.add('previous_invalid', '%s: the previous registry does not validate itself (%d finding(s), first %s)' % (prev_root, len(perrs), perrs[0][0]))
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
            transitions = [t for t in (cur.get('annotations') or {}).get('attribute_transitions', []) if type(t) is dict]
            if cur.get('digest') != r.get('digest') and r.get('digest') not in {l.get('digest') for l in cur.get('lineage', [])} | {t.get('previous_digest') for t in transitions}:
                rep.add('historical_overwritten', '%s changed without retaining its previous digest in lineage or in a recorded transition' % cid)
            if not set(r.get('aliases', [])) <= set(cur.get('aliases', [])):
                rep.add('alias_not_retained', '%s dropped aliases' % cid)
            for f in TRACKED_ATTRIBUTES:
                if f in r and r.get(f) != cur.get(f):
                    if not any(t.get('field') == f and t.get('from') == r.get(f) and t.get('to') == cur.get(f) and t.get('previous_digest') == r.get('digest')
                               and str(t.get('basis', '')).strip() for t in transitions):
                        rep.add('attribute_changed_without_transition', '%s: %s changed from %r to %r with no recorded transition (field, from, to, previous_digest, basis)' % (
                            cid, f, r.get(f), cur.get(f)))
    now = {r.get('evidence_digest'): r for r in layers['evidence']}
    for r in players['evidence']:
        if r.get('evidence_digest') not in now:
            rep.add('historical_removed', 'evidence %s' % r.get('evidence_digest'))
        elif now[r['evidence_digest']].get('digest') != r.get('digest') and now[r['evidence_digest']].get('full_record_digest', now[r['evidence_digest']].get('digest')) != r.get('full_record_digest', r.get('digest')):
            rep.add('historical_overwritten', 'evidence %s changed' % r.get('evidence_digest'))
        elif now[r['evidence_digest']].get('historical_verdict_sha256') != r.get('historical_verdict_sha256') and r.get('historical_verdict_verbatim') is None:
            rep.add('historical_overwritten', 'evidence %s verdict changed' % r.get('evidence_digest'))
    cur_rows = {entry_key('crosswalk', r): r for r in layers['crosswalk']}
    for r in players['crosswalk']:
        cur = cur_rows.get(entry_key('crosswalk', r))
        if cur is None:
            rep.add('historical_removed', 'crosswalk row %s' % entry_key('crosswalk', r))
        elif cur.get('raw_digest') != r.get('raw_digest'):
            rep.add('historical_overwritten', 'raw record %s changed digest' % entry_key('crosswalk', r))


def validate(root, previous=None, artifacts=None):
    """Return the sorted list of (code, message) refusals for the catalogue at root."""
    rep = Report()
    del LAST_WARNINGS[:]
    schemas = load_schemas(root, rep)
    if rep.errors:
        return rep.sorted(), None
    manifest, layers = load_registry(root, rep, schemas)
    if manifest is None or type(manifest) is not dict:
        return rep.sorted(), None
    try:
        check_schema_pins(root, manifest, rep)
        check_manifest_counts(manifest, layers, rep)
        check_source_pins(manifest, layers, rep)
        check_digests_and_authority(layers, rep)
        ids = check_ids(layers, rep)
        by = check_references(layers, ids, rep)
        check_relationships(layers, rep)
        check_accounting(layers, manifest, rep)
        check_evidence(layers, manifest, rep)
        check_crosswalk(layers, ids, by, manifest, rep)
        check_mvp(layers, rep)
        check_alias_collisions(layers, rep)
        check_overlay(manifest, layers, rep)
        check_coverage(layers, rep)
        check_directives(layers, manifest, rep)
        check_registry_records(root, manifest, layers, rep)
        if artifacts:
            check_artifacts(artifacts, manifest, layers, rep, schemas=schemas)
        elif any(a.get('committed') is True for a in manifest.get('external_artifacts', []) if type(a) is dict):
            check_artifacts(None, manifest, layers, rep, root=root, schemas=schemas)
        if previous:
            check_previous(previous, layers, rep)
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        rep.add('record_schema', 'structure too malformed to check further: %s' % type(exc).__name__)
    return rep.sorted(), manifest


def main(argv):
    args = list(argv)
    root, previous, artifacts = DEFAULT_ROOT, None, None
    while args:
        a = args.pop(0)
        if a == '--root' and args:
            root = os.path.abspath(args.pop(0))
        elif a == '--previous' and args:
            previous = os.path.abspath(args.pop(0))
        elif a == '--artifacts' and args:
            artifacts = os.path.abspath(args.pop(0))
        else:
            sys.stderr.write('usage: validate_registry.py [--root DIR] [--previous DIR] [--artifacts DIR]\n')
            return 2
    errors, manifest = validate(root, previous, artifacts)
    if errors:
        for code, message in errors:
            sys.stdout.write('REFUSED %s: %s\n' % (code, message))
        sys.stdout.write('catalogue validation failed: %d finding(s); non-authorizing; HOLD\n' % len(errors))
        return 1
    for w in LAST_WARNINGS:
        sys.stdout.write(w + '\n')
    counts = manifest['layer_counts']
    sys.stdout.write('catalogue consistent: %s; manifest %s\n' % (
        ', '.join('%s=%d' % (k, counts[k]) for k in sorted(counts)), manifest['digest']))
    ext = manifest.get('external_artifacts', [])
    if ext:
        checked = artifacts or all(a.get('committed') is True for a in ext)
        sys.stdout.write('%d external artifact(s) %s\n' % (len(ext), 'verified against the index' if checked else 'NOT checked (pass --artifacts DIR)'))
    sys.stdout.write('informational only; authority none; no rule was executed; HOLD\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
