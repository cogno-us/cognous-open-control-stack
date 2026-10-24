#!/usr/bin/env python3
"""Loader: consolidation outputs (partitions A, B, C, D, R4 and the G1/G2/G3 overlays) -> layered catalogue dataset (non-authorizing).

    python3 -I load_partitions.py --in OUT_DIR --partitions A B C D R4 [--global-dir OUT_DIR/global] --out ROOT [--layout full|compact]
                                  [--artifacts DIR] [--problems FILE]

The loader reads the REAL output shapes of the partition normalizers and of the global passes. It guesses nothing: a
field that a partition does not state becomes unknown/unresolved, a link that arrives without provenance becomes
UNRESOLVED, a SOURCE_STATED link without a source revision is not kept as SOURCE_STATED, and every defect it meets is
written to the load-problem list (partition, kind, ids, count), never silently repaired.

Partition input shapes handled (one reader, all shapes):
  P.canonical.json     layer keys (rules, logical_scenarios, test_implementations, fixtures) that are an inline list, a
                       pointer list [{file,...}], {shards:[{file}]}, {parts:[{file}]}; or (B, C) a "parts" index whose
                       members carry type/kind; D adds lineage_sets and a post_v01 file; entries of a shard are a list or
                       {entries|rows|records:[...]}.
  P.crosswalk.json     a list of rows, {rows: X}, {parts:[{file}]}, or (C) the "parts" of the canonical index with kind
                       "crosswalk". A row carries raw_index, raw_digest, source_repo, path, native_id, tier and a
                       disposition in one of the forms DISP, DISP:target, DISP(reason) or DISP with an explicit target.
                       Partition A has two raw files (A-hub-governance, A2-hub-governance-extension) with overlapping raw
                       indexes; they are kept as the raw sets "A" and "A2" with their own index ranges.
  P.evidence-index.json  {records|entries: X}, {parts: {name:{file}} | [{file}]} or (C) the canonical index; the evidence
                       identity is the digest of the raw record (digest | record_digest | raw_digest | evidence_digest).
Global overlays (OUT_DIR/global): G1 (id map partition -> global id, 173 ALIAS_OF merges with stated basis, rule types),
G2 (scenario categories, MVP applicability with stated basis, post-V0.1 flag), G3 (relationship rows with provenance).
Generic overlays {"overlay": identity|attributes|relationships, ...} (see the README) remain supported.

Layouts: "full" writes every layer; "compact" writes L1-L4, the crosswalk, the evidence and relationship index summaries
and the manifest, and keeps the bulky evidence records and relationship rows as content-addressed artifacts (see builder).
"""
import glob
import re
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _mod(name):
    spec = importlib.util.spec_from_file_location('ocs_catalogue_' + name, os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


B = _mod('build_registry')
V = B.V

LAYER_KEY = {'rules': 'rules', 'logical_scenarios': 'scenarios', 'test_implementations': 'tests', 'fixtures': 'fixtures'}
TIER_OF = {'rules': 'GOVERNANCE_RULE', 'scenarios': 'LOGICAL_SCENARIO', 'tests': 'TEST_IMPLEMENTATION', 'fixtures': 'FIXTURE'}
NORMATIVE = {'constitutional_floor', 'mandatory', 'conditional', 'advisory', 'principle', 'reason_code_or_refusal_vocabulary',
             'validator_rule', 'requirement_row', 'decision', 'unknown'}
MVP = {'mvp_fixed', 'other_supported_historical_profile', 'requires_unavailable_component', 'needs_migration', 'historical_only', 'unresolved'}
POLARITY = {'positive', 'negative', 'adversarial', 'mutation', 'changed_condition', 'race', 'fault', 'recovery', 'tamper', 'integration', 'unknown'}
KNOWN_DISP = ('CANONICAL', 'ALIAS_OF', 'HISTORICAL_REVISION_OF', 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', 'SOURCE_ONLY_ARTIFACT', 'UNRESOLVED', 'ATTACHED_TO_ENTRY')
# partition C names its execution-evidence rows EVIDENCE_INDEXED:<evidence digest>; same meaning as the shared vocabulary item
DISP_SYNONYM = {'EVIDENCE_INDEXED': 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', 'SOURCE_REFERENCE_ONLY': 'SOURCE_ONLY_ARTIFACT'}
NEW_FORMS = ('ATTACHED_TO', 'SOURCE_REFERENCE_ONLY', 'EVIDENCE_INDEXED')
ATTACH_KIND_DISP = {'parametrized_instance': 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', 'collected_node': 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE',
                    'byte_identical_location': 'ALIAS_OF', 'historical_revision': 'HISTORICAL_REVISION_OF', 'amendment_log_member': 'HISTORICAL_REVISION_OF'}
G2_CLASS = {'logical_governance_scenario': 'logical', 'suite_level_acceptance': 'suite_level_acceptance',
            'adversarial_idea_or_unexecuted_specification': 'adversarial_or_unexecuted_spec', 'fixture_defined_case': 'fixture_defined_case',
            'demo_step': 'demo_step', 'other': 'other'}
G1_TYPE = {'reason_code': 'reason_code_or_refusal_vocabulary'}
EVIDENCE_KIND = {'recorded_execution_result': 'run_result', 'run_result': 'run_result', 'validation_statement_claim': 'validation_claim',
                 'validation_claim': 'validation_claim', 'independent_qualification_record': 'independent_qualification_record'}
EVALUATOR_NOTE = 'unqualified: catalogue entry only; no evaluator'
ANN_KEYS = ('enforcement_boundary', 'enforcement_boundary_stated', 'owner', 'evaluator', 'evaluator_stated', 'classification_basis',
            'constitutional_floor', 'constitutional_floor_as_recorded', 'constitutional_effect', 'status_text_verbatim', 'v01_basis',
            'polarity_basis', 'rule_family', 'family', 'tooling_selftest', 'framework', 'callable_identity', 'expected_result_source',
            'synthetic_or_real', 'storage', 'size_bytes', 'off_profile', 'route_c_ref', 'rule_kind', 'distinction_tags', 'scope',
            'status_token_verbatim', 'version', 'fixture_version', 'basis', 'rule_text_status', 'refund_specific_basis',
            'synthetic_id', 'evaluator_raw', 'record_home_repo', 'record_home_boundary_as_inventoried', 'fixture_origin', 'counted_in_fixture_tier_headline',
            'counted_in_logical_scenario_headline', 'scenario_origin', 'denominator', 'requirement_subkind', 'array_family', 'instance_count')
ANN_MAX = 1500


class LoadRefusal(Exception):
    pass


# ---------------------------------------------------------------------------------------------- reading

READ_LOG = {}


def _read(path):
    """Partition outputs are plain JSON (they may hold numbers with fractions in fields the catalogue never carries).

    Every file read is logged with its sha256 so that the regeneration recipe can pin the exact inputs.
    """
    with open(path, 'rb') as fh:
        data = fh.read()
    READ_LOG[os.path.realpath(path)] = V.sha256_bytes(data)
    return json.loads(data.decode('utf-8'))


def _resolve(base, rel):
    """A pointer's file must stay inside the directory that holds the pointer's partition."""
    if type(rel) is not str or not rel or os.path.isabs(rel) or '\\' in rel or '..' in rel.split('/'):
        raise LoadRefusal('shard pointer %r is not a relative path inside the partition directory' % (rel,))
    root = os.path.realpath(base)
    full = os.path.realpath(os.path.join(base, rel))
    if os.path.commonpath([root, full]) != root:
        raise LoadRefusal('shard pointer %r leaves the partition directory' % rel)
    return full


def _shard(path, pointer=None):
    data = _read(path)
    if type(data) is list:
        out = data
    else:
        for k in ('entries', 'rows', 'records', 'suites'):
            if type(data.get(k)) is list:
                out = data[k]
                break
        else:
            lists = [k for k, v in data.items() if type(v) is list]
            if len(lists) != 1:
                raise LoadRefusal('unrecognised shard shape: %s' % path)
            out = data[lists[0]]
    unit = out
    if type(data) is dict and type(data.get('suites')) is list:
        # a differential-instance file is counted by instances, not by suites
        unit = [i for su in out if type(su) is dict for i in (su.get('instances') or [])]
    if type(pointer) is dict:
        want = pointer.get('sha256')
        if type(want) is str:
            want = want[7:] if want.startswith('sha256:') else want
            if READ_LOG[os.path.realpath(path)] != 'sha256:' + want:
                raise LoadRefusal('shard %s does not match its recorded sha256' % pointer.get('file'))
        for k in ('items', 'count'):
            if type(pointer.get(k)) is int and pointer[k] != len(unit):
                raise LoadRefusal('shard %s holds %d records, its pointer says %d' % (pointer.get('file'), len(unit), pointer[k]))
    return out


def _items(base, node):
    """Resolve an inline list or a pointer structure into a list of records."""
    if type(node) is list:
        out = []
        for item in node:
            if type(item) is dict and 'file' in item and 'canonical_id' not in item:
                out.extend(_shard(_resolve(base, item['file']), item))
            else:
                out.append(item)
        return out
    if type(node) is dict:
        if 'shards' in node:
            return _items(base, node['shards'])
        if type(node.get('parts')) is list:
            return _items(base, node['parts'])
        if type(node.get('parts')) is dict:
            return _items(base, [node['parts'][k] for k in sorted(node['parts'])])
        if 'file' in node:
            return _shard(_resolve(base, node['file']), node)
        for k in ('entries', 'rows', 'records', 'suites'):
            if type(node.get(k)) is list:
                return node[k]
    return []


def read_partition(base, pset):
    d = os.path.join(base, pset)
    canon = _read(os.path.join(d, pset + '.canonical.json'))
    index = canon.get('parts') if type(canon.get('parts')) is list else []
    entries = {}
    for key in LAYER_KEY:
        node = canon.get(key)
        if node is None or node == []:
            node = [p for p in index if p.get('type', p.get('kind')) == key]
        entries[LAYER_KEY[key]] = _items(d, node)
    derived = [p for p in index if p.get('type', p.get('kind')) == 'derived_fixture_artifacts']
    if derived:
        for e in _items(d, derived):
            e = dict(e, derived_scenario_data_artifact=True)
            entries['fixtures'].append(e)
    diff = [p for p in index if p.get('type', p.get('kind')) == 'differential_instances']
    diff_suites = _items(d, diff) if diff else []
    lineage_sets = _items(d, canon['lineage_sets']) if 'lineage_sets' in canon else []
    cw_path = os.path.join(d, pset + '.crosswalk.json')
    if os.path.exists(cw_path):
        cw = _read(cw_path)
        rows = cw if type(cw) is list else _items(d, cw['rows'] if 'rows' in cw else cw)
    else:
        rows = []
    if not rows:
        rows = _items(d, [p for p in index if p.get('kind') == 'crosswalk'])
    ev_path = os.path.join(d, pset + '.evidence-index.json')
    evid = []
    if os.path.exists(ev_path):
        ev = _read(ev_path)
        for k in ('records', 'entries', 'parts'):
            if k in ev:
                evid = _items(d, ev[k] if k != 'parts' else ev)
                break
    post = {}
    pp = os.path.join(d, pset + '.post_v01.json')
    if os.path.exists(pp):
        post = _read(pp)
    return {'entries': entries, 'rows': rows, 'evidence': evid, 'lineage_sets': lineage_sets, 'post': post, 'diff_suites': diff_suites}


# ---------------------------------------------------------------------------------------------- small helpers

def _hex(d):
    d = str(d)
    for pre in ('EVIDENCE:', 'EV:'):
        if d.startswith(pre):
            d = d[len(pre):]
    return d if d.startswith('sha256:') else 'sha256:' + d


def _plain(v):
    try:
        V.RR.jcs_dumps(v)
        return True
    except (ValueError, TypeError):
        return False


def _text(v, default):
    return v if type(v) is str and v.strip() else default


def _refs(v):
    return sorted({x for x in (v if type(v) is list else []) if type(x) is str})


def _strs(v):
    if type(v) is str:
        return [v]
    return [x for x in (v if type(v) is list else []) if type(x) is str]


class Problems:
    def __init__(self):
        self.rows = {}
        self.all_ids = {}

    def add(self, partition, kind, ident=None, detail=None):
        e = self.rows.setdefault((partition, kind), {'partition': partition, 'kind': kind, 'count': 0, 'ids': [], 'detail': detail})
        e['count'] += 1
        if ident is not None:
            self.all_ids.setdefault((partition, kind), []).append(str(ident))
            if len(e['ids']) < 25:
                e['ids'].append(ident)

    all_ids = None

    def as_list(self):
        return [self.rows[k] for k in sorted(self.rows)]

    def full(self):
        """Every problem with every id (the load-problem file)."""
        return [dict(self.rows[k], ids=sorted(set(self.all_ids.get(k, [])))) for k in sorted(self.rows)]

    def summary(self):
        """Committed summary: counts, first ids and a digest over all ids of each problem kind."""
        out = []
        for k in sorted(self.rows):
            e = self.rows[k]
            ids = sorted(set(self.all_ids.get(k, [])))
            out.append({'partition': e['partition'], 'kind': e['kind'], 'count': e['count'], 'first_ids': ids[:5],
                        'ids_sha256': V.canonical_digest(ids), 'detail': str(e['detail'] or '')[:300]})
        return out


def _raw_set(pset, raw_file, problems):
    """A partition may read several raw files whose indexes overlap (A: A-hub-governance.json, A2-hub-governance-extension.json;
    C: C, C2, C3). The leading upper-case token of the raw file name names the raw set; it must belong to the partition."""
    if not raw_file:
        return pset
    m = re.match(r'[A-Z][A-Z0-9]*', str(raw_file))
    if m and m.group(0).startswith(pset):
        return m.group(0)
    problems.add(pset, 'raw_file_not_of_partition', str(raw_file)[:60])
    return pset


def _norm_row(pset, row, problems):
    disp, target, reason = row.get('disposition'), row.get('target'), row.get('unresolved_reason')
    tier = row['tier']
    native_disp = None
    if type(disp) is str and disp.partition(':')[0] in NEW_FORMS:
        # the normalizer's own forms (ATTACHED_TO:<id>, SOURCE_REFERENCE_ONLY, EVIDENCE_INDEXED:<digest>) map to the catalogue's
        # dispositions only through a statement the row makes itself: the retained earlier form, or its attach_kind
        legacy, kind = row.get('disposition_legacy'), row.get('attach_kind')
        head = disp.partition(':')[0]
        want = None
        if head == 'ATTACHED_TO':
            want = ATTACH_KIND_DISP.get(kind)
        elif head in DISP_SYNONYM:
            want = DISP_SYNONYM[head]
        lhead = legacy.partition(':')[0] if type(legacy) is str else None
        if lhead in KNOWN_DISP and (want is None or lhead == want or (head == 'ATTACHED_TO' and kind is None)):
            native_disp, disp = disp, legacy
        elif want is not None:
            tail = disp.partition(':')[2]
            native_disp, disp = disp, want + (':' + tail if tail else '')
        elif head == 'ATTACHED_TO' and kind is None and row.get('target') is not None and type(row.get('relation')) is str:
            # the row itself says: this raw record is additional material attached to an existing entry (relation stated)
            native_disp, disp = disp, 'ATTACHED_TO_ENTRY'
        else:
            problems.add(pset, 'disposition_form_without_mapping', '%s:%s' % (pset, row.get('raw_index')), '%s (attach_kind=%r, legacy=%r)' % (disp.partition(':')[0], kind, legacy))
            native_disp, disp = disp, 'UNRESOLVED(%s cannot be mapped: no attach_kind or earlier form on the row)' % disp.partition(':')[0]
    if type(disp) is not str:
        problems.add(pset, 'row_without_disposition', row.get('raw_index'))
        disp = 'UNRESOLVED'
        reason = 'partition output carries no disposition'
    elif disp.startswith('UNRESOLVED(') and disp.endswith(')'):
        reason, disp, target = disp[len('UNRESOLVED('):-1], 'UNRESOLVED', None
    else:
        head, sep, tail = disp.partition(':')
        head = DISP_SYNONYM.get(head, head)
        disp = DISP_SYNONYM.get(disp, disp)
        if sep and head in KNOWN_DISP:
            # DISP:target; an explicit target member of the row wins over the compound form's tail
            disp, target = head, (target if target is not None else (tail or None))
            if disp == 'UNRESOLVED':
                reason, target = tail or 'unresolved in partition output', None
        elif disp not in KNOWN_DISP:
            problems.add(pset, 'unknown_disposition', disp)
            disp, target, reason = 'UNRESOLVED', None, 'unrecognised disposition %r' % disp
    if disp == 'UNRESOLVED' and not reason:
        reason = _text(row.get('tier_basis'), 'unresolved in partition output')
    raw_set = _raw_set(pset, row.get('raw_file'), problems)
    keep = {}
    for k in ('anchor', 'tier_basis', 'relation', 'level', 'catalogue_scope', 'attach_kind'):
        if type(row.get(k)) is str and row[k] and len(row[k]) <= ANN_MAX:
            keep[k] = row[k]
    if native_disp is not None:
        keep['disposition_as_recorded'] = native_disp
    return {'raw_set': raw_set, 'raw_index': row['raw_index'], 'raw_digest': _hex(row['raw_digest']), 'source_repo': _text(row.get('source_repo'), 'unrecorded'),
            'path': row.get('path') if type(row.get('path')) is str else None, 'native_id': row.get('native_id') if type(row.get('native_id')) is str else None,
            'tier': tier, 'disposition': disp, 'target': target, 'unresolved_reason': reason if disp == 'UNRESOLVED' else None,
            'annotations': keep, '_co': [x for x in ([row.get('co_registered')] if type(row.get('co_registered')) is str else []) + [t for t in (row.get('additional_targets') or []) if type(t) is str]], '_partition': pset, '_raw_file': row.get('raw_file') if type(row.get('raw_file')) is str else None}


# ---------------------------------------------------------------------------------------------- entries

def _repo_of(e):
    r = e.get('source_repo')
    if type(r) is list and r:
        r = r[0]
    if type(r) is str and r:
        return r
    for loc in e.get('locations') or []:
        if type(loc) is dict and type(loc.get('repo')) is str:
            return loc['repo']
        if type(loc) is dict and type(loc.get('source_repo')) is str:
            return loc['source_repo']
    return None


def _cite(repo, rev):
    """A bare 40-hex commit that is the pinned tag commit of its repository is cited as 'tag <name> + commit', like the other sets."""
    if type(rev) is str and re.fullmatch(r'[0-9a-f]{40}', rev) and V.PINNED_TAG_COMMITS.get(repo) == rev[:8]:
        return '%s %s' % (V.TAG_NAME, rev)
    return rev


def _locations(e, repo, revision):
    out = []
    for loc in e.get('locations') or []:
        if type(loc) is str:
            out.append({'repo': repo, 'revision': revision, 'path': loc, 'anchor': None})
        elif type(loc) is dict:
            lrepo = _text(loc.get('repo') or loc.get('source_repo'), repo)
            out.append({'repo': lrepo, 'revision': _cite(lrepo, _text(loc.get('source_revision'), revision)),
                        'path': loc.get('path') if type(loc.get('path')) is str else None,
                        'anchor': loc.get('anchor') if type(loc.get('anchor')) is str else None})
    seen, uniq = set(), []
    for x in out:
        k = (x['repo'], x['revision'], x['path'], x['anchor'])
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    return uniq


NONE_PART = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=None$')


def _drop_absent_parts(text):
    """A partition that renders a record as 'key=value; key=value' writes an absent value as key=None. Such a part says nothing was
    stated, so it is omitted rather than carried as text; every other part is kept exactly. Used for scenario and fixture
    expectations only, never for historical results."""
    if type(text) is not str:
        return text
    for sep in ('; ', ' | '):
        parts = text.split(sep)
        if len(parts) > 1 and any(NONE_PART.match(x) for x in parts):
            text = sep.join(x for x in parts if not NONE_PART.match(x))
    return text


def _statement(e):
    for k in ('expected_outcome', 'rule_text_verbatim', 'expected_outcome_verbatim'):
        v = e.get(k)
        if type(v) is str:
            return v
        if type(v) is list and v and all(type(x) is str for x in v):
            return ' | '.join(v)
    return None


def _annotations(e):
    ann = {}
    for k in ANN_KEYS:
        v = e.get(k)
        if v is None or V.annotation_key_forbidden(k) or not _plain(v):
            continue
        if type(v) is str and (not v.strip() or len(v) > ANN_MAX):
            continue
        if type(v) in (list, dict) and len(json.dumps(v, sort_keys=True)) > ANN_MAX:
            continue
        ann[k] = v
    return ann


def _entry(layer, e, mine, pset, problems):
    cid = e['canonical_id']
    refs = sorted('%s:%d' % (r['raw_set'], r['raw_index']) for r in mine)
    row_aliases = [r['native_id'] for r in mine if r['disposition'] == 'ALIAS_OF' and r['native_id']]
    native = sorted(set(_strs(e.get('native_ids')) or _strs(e.get('fixture_ids')) or _strs(e.get('fixture_id')) or _strs(e.get('scenario_native_id'))))
    aliases = sorted(set(_refs(e.get('aliases')) + _refs(e.get('aliases_source_stated')) + row_aliases))
    lineage = [{'revision_id': r['native_id'] or ('%s:%d' % (r['raw_set'], r['raw_index'])), 'raw_ref': '%s:%d' % (r['raw_set'], r['raw_index']),
                'digest': r['raw_digest'], 'relation': 'HISTORICAL_REVISION'} for r in mine if r['disposition'] == 'HISTORICAL_REVISION_OF']
    repo = _repo_of(e) or next((r['source_repo'] for r in mine if r['source_repo'] != 'unrecorded'), None)
    if repo is None:
        problems.add(pset, 'entry_without_source_repo', cid)
        repo = 'unrecorded'
    revision = _text(e.get('source_revision'), None)
    if revision is None:
        for loc in e.get('locations') or []:
            if type(loc) is dict and type(loc.get('source_revision')) is str:
                revision = loc['source_revision']
                break
    if revision is None:
        problems.add(pset, 'entry_without_source_revision', cid)
        revision = 'unrecorded'
    path = e.get('path') if type(e.get('path')) is str else None
    locs = _locations(e, repo, revision)
    multi_locs = False
    if repo.startswith('multi:'):
        # a combined pseudo-repo is not a repository: cite each constituent with its own repo, path and revision
        real = sorted((l for l in locs if not str(l['repo']).startswith('multi:') and l['repo'] != 'unrecorded' and l['path']), key=lambda l: (l['repo'], l['path'], l['anchor'] or ''))
        if real:
            repo, revision, path = real[0]['repo'], real[0]['revision'], real[0]['path']
            locs = real
            multi_locs = True
        else:
            problems.add(pset, 'multi_repo_without_constituent_locations', cid)
            repo = 'unrecorded'
    if path is None and locs:
        path = locs[0]['path']
    revision = _cite(repo, revision)
    src = {'repo': repo, 'revision': revision, 'path': path, 'anchor': e.get('anchor') if type(e.get('anchor')) is str else None}
    mv = e.get('mvp_applicability')
    mvp = {'value': mv if mv in MVP else 'unresolved',
           'reason': _text(e.get('mvp_applicability_basis'), 'partition output states %s; no basis stated' % (mv if mv in MVP else 'no applicability'))}
    ann = _annotations(e)
    if e.get('reference_only') is True:
        ann['reference_only'] = True
    if e.get('derived_scenario_data_artifact') is True:
        ann['derived_scenario_data_artifact'] = True
        ann['derived_from_raw'] = sorted('%s:%s' % (_raw_set(pset, x.get('raw_file'), problems), x.get('raw_index')) for x in (e.get('derived_from_raw') or []) if type(x) is dict)
    out = {'catalogue_id': cid, 'title': _text(e.get('title'), _text(e.get('anchor'), cid)), 'tier': TIER_OF[layer], 'source': src,
           'native_ids': native, 'aliases': aliases, 'raw_refs': refs, 'lineage': lineage, 'annotations': ann, 'mvp_applicability': mvp,
           'release_scope': 'unknown', '_partition': pset}
    ev = e.get('evidence_digest_refs')
    out['_evidence_raw'] = [x for x in (ev if type(ev) is list else []) if type(x) is str]
    rr = _refs(e.get('rule_refs')) + _refs(e.get('associated_rules'))
    sr = _refs(e.get('scenario_refs')) + _refs(e.get('associated_scenarios'))
    tr = _refs(e.get('test_refs'))
    fr = _refs(e.get('fixture_refs')) + _refs(e.get('data_fixture_refs'))
    verbatim = _statement(e)
    if layer in ('scenarios', 'fixtures'):
        verbatim = _drop_absent_parts(verbatim)
    if layer == 'rules':
        stmt = verbatim
        ident = {'statement_verbatim': stmt} if stmt is not None else {'statement_verbatim': None, 'repo': repo, 'path': path, 'anchor': src['anchor'], 'native_ids': native}
        out.update(rule_ref={'kind': 'source_statement', 'rule_id': native[0] if native else cid, 'version': None, 'rule_digest': V.canonical_digest(ident),
                             'registry_id': None, 'record_digest': None},
                   statement_verbatim=stmt, refund_specific=e.get('refund_specific') if type(e.get('refund_specific')) is bool else None,
                   normative_type='unknown', adoption_status='unknown', scenario_refs=sorted(set(sr)), test_refs=tr, evidence_digest_refs=[])
        out['annotations']['evaluator_qualification_note'] = EVALUATOR_NOTE
        if type(e.get('classification')) is str:
            out['annotations']['partition_classification'] = e['classification']
    elif layer == 'scenarios':
        pol = e.get('polarity')
        out.update(rule_refs=sorted(set(rr)), test_refs=tr, fixture_refs=fr, evidence_digest_refs=[], expected_outcome_verbatim=verbatim,
                   polarity=pol if pol in POLARITY else 'unknown',
                   temporal_or_recovery_flag=e.get('temporal_or_recovery_flag') if type(e.get('temporal_or_recovery_flag')) is bool else False,
                   scenario_family=_text(e.get('scenario_family') or e.get('family'), None),
                   refund_specific=e.get('refund_specific') if type(e.get('refund_specific')) is bool else None, scenario_class='logical')
        out['annotations']['evaluator_qualification_note'] = EVALUATOR_NOTE
        if multi_locs:
            out['locations'] = locs
        out['differential_instance_count'] = sum(1 for r in mine if r['annotations'].get('relation') == 'DIFFERENTIAL_VECTOR_INSTANCE' and r['tier'] == 'PARAMETRIZED_INSTANCE')
    elif layer == 'tests':
        fx = fr
        pc = e.get('parametrization') if type(e.get('parametrization')) is dict else {}
        out.update(scenario_refs=sorted(set(sr)), rule_refs=sorted(set(rr)), fixture_refs=fx, evidence_digest_refs=[],
                   parametrized_instance_count=sum(1 for r in mine if r['tier'] == 'PARAMETRIZED_INSTANCE' and r['disposition'] == 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE'))
    else:
        sha = e.get('content_sha256') or e.get('content_digest_sha256') or e.get('content_digest')
        sha = sha[7:] if type(sha) is str and sha.startswith('sha256:') else sha
        basis = e.get('fixture_identity_basis') or e.get('content_digest_basis') or e.get('digest_basis') or e.get('content_digest_scope')
        locs = locs or [{'repo': repo, 'revision': revision, 'path': path, 'anchor': None}]
        out.update(fixture_identity={'basis': _text(basis, 'unrecorded'), 'content_sha256': 'sha256:' + sha if type(sha) is str and len(sha) == 64 else None},
                   locations=locs, expected_outcome_verbatim=verbatim, evidence_digest_refs=[])
    out['_refs'] = {'rule_refs': rr, 'scenario_refs': sr, 'test_refs': tr, 'fixture_refs': fr}
    return out


def _evidence(pset, e, rows_by_raw, problems):
    dg = next((e[k] for k in ('digest', 'record_digest', 'raw_digest', 'evidence_digest') if type(e.get(k)) is str), None)
    if dg is None:
        problems.add(pset, 'evidence_without_digest', e.get('raw_index'))
        return None
    digest = _hex(dg)
    art = e.get('artifact_location_and_digest') or e.get('artifact') or {}
    if type(art) is not dict:
        art = {}
    kind = str(e.get('evidence_kind', ''))
    verdict = None
    for k in ('verbatim_verdict', 'verdict_verbatim', 'original_verdict_verbatim', 'original_verdict', 'raw_result_and_original_verdict'):
        if type(e.get(k)) is str:
            verdict = e[k]
            break
    path = art.get('path') or art.get('location') or e.get('source_path') or e.get('artifact_location')
    fdig = art.get('file_digest') or art.get('file_digest_sha256') or art.get('sha256') or art.get('artifact_digest') or e.get('artifact_digest')
    rid = e.get('run_id') if type(e.get('run_id')) is str else None
    tid = next((e[k] for k in ('scenario_or_test_id', 'test_or_scenario_id') if type(e.get(k)) is str), None)
    if tid is None:
        tid = (e.get('source_path') or '') + '|' + str(e.get('anchor'))
    repo = _text(e.get('source_repo'), None)
    rev = _text(e.get('source_revision'), None)
    mine = rows_by_raw.get(digest, [])
    if repo is None and mine:
        repo = mine[0]['source_repo']
    if repo is None:
        problems.add(pset, 'evidence_without_source_repo', digest)
    if rev is None:
        problems.add(pset, 'evidence_without_source_revision', digest)
    if type(path) is not str or not path:
        problems.add(pset, 'evidence_without_artifact_path', digest)
        path = (mine[0]['path'] if mine and mine[0]['path'] else 'unrecorded')
    raw_set = mine[0]['raw_set'] if mine else pset
    if 'evidence_kind' in e:
        # exact source vocabulary only; a kind outside it is unknown, never a run result
        ekind = EVIDENCE_KIND.get(e['evidence_kind']) if type(e['evidence_kind']) is str else None
        basis = 'source_stated'
        if ekind is None:
            ekind, basis = 'unknown', 'unrecognised_source_value'
            problems.add(pset, 'evidence_kind_outside_vocabulary', digest, repr(e['evidence_kind'])[:80])
    elif rid is not None and verdict is not None:
        ekind, basis = 'run_result', 'structural: the record names a run and carries a recorded outcome'
    else:
        ekind, basis = 'unknown', 'no kind stated and no run id with a recorded outcome'
        problems.add(pset, 'evidence_kind_unclassified', digest)
    ann = {'execution_identity': [rid, tid], 'evidence_kind_basis': basis}
    for k in ('level', 'verdict_field', 'anchor', 'raw_file', 'is_v01_candidate_run'):
        if type(e.get(k)) in (str, bool) and e.get(k) != '':
            ann[k] = e[k]
    return {'evidence_digest': digest, 'raw_refs': sorted('%s:%d' % (r['raw_set'], r['raw_index']) for r in mine), 'tier': 'EXECUTION_EVIDENCE',
            'evidence_kind': ekind,
            'run_id': rid, 'test_ref': None, 'scenario_ref': None, 'historical_verdict_verbatim': verdict,
            'source_commitment': {'set_id': raw_set, 'repo': repo or 'unrecorded', 'revision': _cite(repo, rev) or 'unrecorded'},
            'artifact_commitment': {'path': path, 'record_digest': digest, 'file_digest': _text(fdig, 'not computed')},
            'current_qualification_effect': 'none', 'annotations': ann}


# ---------------------------------------------------------------------------------------------- assembly

def _blank_rel(field, to, why):
    return {'field': field, 'to': to, 'provenance': 'UNRESOLVED', 'source': None, 'method': None, 'supporting_refs': [], 'confidence_class': None,
            'missing_evidence': why, 'establishes_enforcement': False, 'establishes_test_coverage': False, 'establishes_qualification': False}


def load_all(base, partitions, problems):
    """Read and normalize every partition; no overlay yet. Returns the pre-overlay dataset."""
    data = {'rules': {}, 'scenarios': {}, 'tests': {}, 'fixtures': {}}
    evidence, crosswalk, inventory, lineage_sets, post_digests = {}, [], [], {}, {}
    ev_alias = {}
    for pset in partitions:
        part = read_partition(base, pset)
        rows = [_norm_row(pset, r, problems) for r in part['rows']]
        crosswalk += rows
        by_raw = {}
        for r in rows:
            by_raw.setdefault(r['raw_digest'], []).append(r)
        rows_to, co_to = {}, {}
        for r in rows:
            if r['tier'] == 'EXECUTION_EVIDENCE':
                continue
            if r['target']:
                rows_to.setdefault(r['target'], []).append(r)
            if r['_co'] and r['disposition'] in ('CANONICAL', 'ALIAS_OF'):
                for c in r['_co']:
                    co_to.setdefault(c, []).append(r)
        for suite in part.get('diff_suites') or []:
            n = sum(1 for r in rows if r['target'] == suite.get('suite') and r['annotations'].get('relation') == 'DIFFERENTIAL_VECTOR_INSTANCE')
            if n != len(suite.get('instances') or []):
                problems.add(pset, 'differential_suite_count_differs_from_crosswalk', suite.get('suite'), 'suite lists %d, crosswalk rows %d' % (len(suite.get('instances') or []), n))
        revs = set()
        post_ids = set()
        pv = part['post']
        post_entries = {}
        for key, layer in (('logical_scenarios', 'scenarios'), ('test_implementations', 'tests'), ('fixtures', 'fixtures'), ('rules', 'rules')):
            if type(pv.get(key)) is list:
                post_entries[layer] = [x for x in pv[key] if type(x) is dict and 'canonical_id' in x]
        for layer, items in list(part['entries'].items()) + [(l, x) for l, x in post_entries.items()]:
            is_post = layer in post_entries and items is post_entries[layer]
            for e in items:
                mine = rows_to.get(e['canonical_id'], []) + [r for r in co_to.get(e['canonical_id'], []) if r not in rows_to.get(e['canonical_id'], [])]
                new = _entry(layer, e, mine, pset, problems)
                if is_post:
                    new['release_scope'] = 'post_v0_1'
                    post_ids.add(e['canonical_id'])
                old = data[layer].get(new['catalogue_id'])
                if old is not None:
                    same = old['source']['repo'] == new['source']['repo'] and old['source']['path'] == new['source']['path'] and old['native_ids'] == new['native_ids']
                    if not same:
                        raise LoadRefusal('canonical id %s emitted by two partitions with different identity' % new['catalogue_id'])
                    diff = sorted(k for k in set(old) | set(new) if k not in ('aliases', 'raw_refs', 'lineage', '_refs', '_evidence_raw', '_partition') and old.get(k) != new.get(k))
                    if diff:
                        raise LoadRefusal('canonical id %s emitted by two partitions with different content in %s' % (new['catalogue_id'], diff))
                    for k in ('aliases', 'raw_refs'):
                        old[k] = sorted(set(old[k]) | set(new[k]))
                    old['lineage'] += [l for l in new['lineage'] if l not in old['lineage']]
                    continue
                data[layer][new['catalogue_id']] = new
                revs.add((new['source']['repo'], new['source']['revision']))
        for e in part['evidence']:
            ev = _evidence(pset, e, by_raw, problems)
            if ev is None:
                continue
            evidence[ev['evidence_digest']] = ev
            if type(e.get('canonical_id')) is str:
                ev_alias[e['canonical_id']] = ev['evidence_digest']
            revs.add((ev['source_commitment']['repo'], ev['source_commitment']['revision']))
        for ls in part['lineage_sets'] + (pv.get('lineage_sets') if type(pv.get('lineage_sets')) is list else []):
            lineage_sets[ls['canonical_id']] = dict(ls, _partition=pset, _post=ls in (pv.get('lineage_sets') or []))
        for key in ('items_in_raw_from_non_tag_revision',):
            for it in pv.get(key) or []:
                if type(it) is dict and type(it.get('raw_digest')) is str:
                    post_digests[_hex(it['raw_digest'])] = it.get('reason') or 'source read at a non-tag revision'
        raw_counts = {}
        for r in rows:
            raw_counts.setdefault(r['raw_set'], []).append(r)
        for rs in sorted(raw_counts):
            inventory.append({'set_id': rs, 'partition': pset, 'raw_file': next((r['_raw_file'] for r in raw_counts[rs] if r['_raw_file']), None)})
        data.setdefault('_revs', {})[pset] = revs
    return {'layers': data, 'evidence': evidence, 'crosswalk': crosswalk, 'inventory': inventory, 'lineage_sets': lineage_sets,
            'post_digests': post_digests, 'ev_alias': ev_alias}


def _apply_rows(ds, problems):
    """Resolve crosswalk targets against loaded entries; anything unresolvable becomes UNRESOLVED (never guessed)."""
    layers = ds['layers']
    ids = {}
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        for cid in layers[layer]:
            ids[cid] = layer
    ls = ds['lineage_sets']
    for r in ds['crosswalk']:
        t, d = r['target'], r['disposition']
        if r['tier'] == 'EXECUTION_EVIDENCE':
            if d == 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE':
                dg = r['raw_digest']
                if dg in ds['evidence']:
                    r['target'] = dg
                elif t in ds['ev_alias']:
                    r['target'] = ds['ev_alias'][t]
                else:
                    problems.add(r['_partition'], 'evidence_row_without_evidence_record', '%s:%d' % (r['raw_set'], r['raw_index']))
                    r['disposition'], r['target'], r['unresolved_reason'] = 'UNRESOLVED', None, 'evidence record %s is absent from the evidence index' % dg
            continue
        if t is None:
            continue
        if t in ids:
            continue
        if t in ls and d == 'HISTORICAL_REVISION_OF':
            continue
        problems.add(r['_partition'], 'row_target_not_in_catalogue', '%s:%d -> %s' % (r['raw_set'], r['raw_index'], t), d)
        r['unresolved_reason'] = 'partition row names %s %s, which is not a catalogue entry in the partition output' % (d, t)
        r['disposition'], r['target'] = 'UNRESOLVED', None
    return ds


# ---------------------------------------------------------------------------------------------- global overlays

def _gfiles(d, pattern):
    return sorted(glob.glob(os.path.join(d, pattern)))


def _rows_cols(doc):
    cols = doc['columns']
    return [dict(zip(cols, r)) for r in doc['rows']]


class IdMap:
    def __init__(self):
        self.m = {}
        self.g = {}
        self.fd = {}

    def add(self, partition, pid, gid):
        self.m[(partition, pid)] = gid
        self.g.setdefault(gid, set()).add((partition, pid))
        if pid.startswith('FD-'):
            # derived scenario data artifacts are content addressed, so the same id means the same artifact in any partition
            self.fd.setdefault(pid, set()).add(gid)

    def __call__(self, partition, pid):
        if (partition, pid) in self.m:
            return self.m[(partition, pid)]
        if pid.startswith('FD-') and len(self.fd.get(pid, ())) == 1:
            return next(iter(self.fd[pid]))
        return pid


def apply_g1(ds, g1dir, problems):
    """G1: id map, merges (ALIAS_OF with stated basis), rule types. Returns (idmap, rule_types, candidates)."""
    idm = IdMap()
    for f in _gfiles(g1dir, 'G1.idmap.*.json'):
        for r in _rows_cols(_read(f)):
            idm.add(r['partition'], r['partition_canonical_id'], r['global_id'])
    layers = ds['layers']
    by = {}
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        for cid in layers[layer]:
            by[cid] = layer
    merges = []
    for f in _gfiles(g1dir, 'G1.merges.*.json'):
        merges += _read(f)['merges']
    for m in sorted(merges, key=lambda x: x['merge_id']):
        prov = m.get('provenance') or {}
        basis = ['%s: %s' % (m['merge_id'], m.get('rule') or 'ALIAS_OF')]
        for k in sorted(prov):
            p = prov[k]
            if type(p) is dict:
                basis.append('%s[%s] %s' % (k, p.get('class', '?'), p.get('quote') or p.get('method') or p.get('locator') or ''))
        basis = '; '.join(basis)
        if not any(type(p) is dict and p.get('class') for p in prov.values()):
            raise LoadRefusal('merge %s has no stated provenance' % m['merge_id'])
        into, gone = m['primary']['id'], m['alias']['id']
        layer = by.get(into)
        if layer is None or by.get(gone) != layer:
            problems.add('G1', 'merge_endpoint_not_in_catalogue', m['merge_id'], '%s <- %s' % (into, gone))
            continue
        keep, g = layers[layer][into], layers[layer].pop(gone)
        keep['aliases'] = sorted(set(keep['aliases']) | set(g['aliases']) | set(g['native_ids']) | {gone})
        keep['raw_refs'] = sorted(set(keep['raw_refs']) | set(g['raw_refs']))
        keep['lineage'] += [l for l in g['lineage'] if l not in keep['lineage']]
        mf = keep['annotations'].setdefault('merged_from', [])
        mf.append({'id': gone, 'partition': m['alias']['partition'], 'merge_id': m['merge_id'], 'basis': basis, 'caveat': m.get('caveat'),
                   'provenance': {k: v for k, v in prov.items() if _plain(v)}})
        for k in ('_evidence_raw',):
            keep[k] = keep[k] + [x for x in g[k] if x not in keep[k]]
        for k, v in g['_refs'].items():
            keep['_refs'][k] = keep['_refs'].get(k, []) + [x for x in v if x not in keep['_refs'].get(k, [])]
        by.pop(gone)
        idm.add(m['alias']['partition'], gone, into)
        for r in ds['crosswalk']:
            if r['target'] == gone:
                r['target'] = into
                if r['disposition'] == 'CANONICAL':
                    r['disposition'] = 'ALIAS_OF'
        for r in ds['crosswalk']:
            if gone in r['_co']:
                r['_co'] = [into if c == gone else c for c in r['_co']]
    types = {}
    for f in _gfiles(g1dir, 'G1.rule-types.*.json'):
        for r in _rows_cols(_read(f)):
            types[(r['partition'], r['partition_id'])] = r
    for (pset, pid), r in sorted(types.items()):
        gid = idm(pset, pid)
        rule = layers['rules'].get(gid)
        if rule is None:
            if not r.get('merged_away'):
                problems.add('G1', 'rule_type_for_unknown_rule', pid)
            continue
        nt = G1_TYPE.get(r['normative_type'], r['normative_type'])
        if nt not in NORMATIVE:
            problems.add('G1', 'rule_type_outside_vocabulary', pid, r['normative_type'])
            nt = 'unknown'
        rule['normative_type'] = nt
        rule['_nt_set'] = True
        a = rule['annotations']
        a['normative_type_provenance'] = r['provenance']
        a['normative_type_basis'] = r['basis']
        if r.get('subtype'):
            a['normative_subtype'] = r['subtype']
        if nt == 'constitutional_floor':
            rule['adoption_status'] = 'adopted'
        elif 'PROPOSED_NOT_YET_ADOPTED' in str(r.get('subtype')) or 'NOT YET ADOPTED' in str(rule['annotations'].get('status_text_verbatim', '')).upper():
            rule['adoption_status'] = 'proposed_not_adopted'
    cands = []
    for f in _gfiles(g1dir, 'G1.candidates.*.json'):
        for c in _read(f)['candidates']:
            cands.append(c)
    return idm, cands


def apply_g2(ds, g2dir, idm, problems):
    layers = ds['layers']
    bases = _read(os.path.join(g2dir, 'G2.mvp-bases.json'))
    seen = 0

    def mvp_of(item):
        val = item.get('mvp_applicability')
        bid = item.get('mvp_basis_id')
        if val not in MVP:
            problems.add('G2', 'mvp_value_outside_vocabulary', item.get('canonical_id'), val)
            val = 'unresolved'
        if val == 'unresolved' or not bid:
            return {'value': 'unresolved', 'reason': 'G2: no stated basis for an applicability value (%s)' % (item.get('mvp_relation') or 'unresolved by rule')}
        b = bases.get(bid)
        if b is None:
            problems.add('G2', 'mvp_basis_id_unknown', item.get('canonical_id'), bid)
            return {'value': 'unresolved', 'reason': 'G2 names basis %s that G2.mvp-bases does not define' % bid}
        if b['applicability'] != val:
            problems.add('G2', 'mvp_value_differs_from_basis', item.get('canonical_id'), '%s vs %s' % (val, b['applicability']))
        out = {'value': val, 'reason': 'G2 basis %s [%s, %s confidence]: %s' % (bid, b.get('provenance'), b.get('confidence'), item.get('mvp_relation') or b.get('source')), 'basis_id': bid}
        if type(b.get('source')) is str and b['source'].strip():
            out['source_ref'] = b['source']
        return out

    def flag(item):
        return {'V0.1': 'v0_1', 'post_v01': 'post_v0_1'}.get(item.get('v01_flag'), 'unknown')

    g2_types = {}
    for f in _gfiles(g2dir, 'G2.scenarios.*.json'):
        for it in _read(f):
            gid = idm(it['partition'], it['canonical_id'])
            e = layers['scenarios'].get(gid)
            if e is None:
                problems.add('G2', 'scenario_not_in_catalogue', it['canonical_id'])
                continue
            seen += 1
            cls = G2_CLASS.get(it['scenario_category'])
            if cls is None:
                problems.add('G2', 'scenario_category_outside_vocabulary', it['canonical_id'], it['scenario_category'])
                cls = 'other'
            e['scenario_class'] = cls
            e['annotations']['scenario_category_basis'] = it.get('category_basis_id')
            if it.get('recorded_status_token_verbatim'):
                e['annotations']['recorded_status_token_verbatim'] = it['recorded_status_token_verbatim']
            if it.get('distinction_tags_keyword_derived'):
                e['annotations']['distinction_tags_keyword_derived'] = it['distinction_tags_keyword_derived']
            e['mvp_applicability'] = mvp_of(it)
            e['release_scope'] = flag(it)
    for f in _gfiles(g2dir, 'G2.mvp-other-layers.*.json'):
        for it in _read(f):
            layer = {'L1': 'rules', 'L3': 'tests', 'L4': 'fixtures'}.get(it['layer'])
            gid = idm(it['partition'], it['canonical_id'])
            e = layers[layer].get(gid) if layer else None
            if e is None:
                if not it.get('g1_merged_away'):
                    problems.add('G2', 'entry_not_in_catalogue', it['canonical_id'])
                continue
            seen += 1
            e['mvp_applicability'] = mvp_of(it)
            e['release_scope'] = flag(it)
            if layer == 'rules' and it.get('normative_type'):
                g2_types[gid] = G1_TYPE.get(it['normative_type'], it['normative_type'])
    for gid, t in sorted(g2_types.items()):
        if layers['rules'][gid]['normative_type'] != t and layers['rules'][gid].get('_nt_set'):
            problems.add('G2', 'normative_type_differs_from_g1', gid, '%s vs %s' % (t, layers['rules'][gid]['normative_type']))
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        for cid, e in layers[layer].items():
            if e['release_scope'] == 'unknown' and e['mvp_applicability']['value'] == 'unresolved' and 'G2' not in e['mvp_applicability']['reason']:
                problems.add('G2', 'entry_without_g2_attributes', cid)
    return bases


# ---------------------------------------------------------------------------------------------- relationships (G3) and references

FORWARD = {'rules': ('scenario_refs', 'test_refs', 'evidence_digest_refs', 'related_refs'),
           'scenarios': ('test_refs', 'fixture_refs', 'evidence_digest_refs', 'related_refs'),
           'tests': ('fixture_refs', 'evidence_digest_refs'),
           'fixtures': ('evidence_digest_refs',)}
NON_FORWARD_FIELDS = ('alias_candidates',)
G3_FIELD = {'rule->scenario': ('rules', 'scenario_refs'), 'rule->test_implementation': ('rules', 'test_refs'),
            'rule->evidence': ('rules', 'evidence_digest_refs'), 'scenario->evidence': ('scenarios', 'evidence_digest_refs'),
            'scenario->fixture': ('scenarios', 'fixture_refs'), 'scenario->test_implementation': ('scenarios', 'test_refs'),
            'test_implementation->fixture': ('tests', 'fixture_refs'), 'test_instance->evidence': ('tests', 'evidence_digest_refs'),
            'fixture->evidence': ('fixtures', 'evidence_digest_refs')}
INSTANCE_LEVEL_TYPES = ('differential_instance->scenario',)  # per-instance links stay in the external relationship rows
RANK = {'SOURCE_STATED': 0, 'high': 1, 'medium': 2, 'low': 3, 'heuristic': 4}
TYPED = {'rule_refs': 'rules', 'scenario_refs': 'scenarios', 'test_refs': 'tests', 'fixture_refs': 'fixtures', 'related_refs': None}


def _rank(rec):
    if rec['provenance'] == 'SOURCE_STATED':
        return 0
    if rec['provenance'] == 'DERIVED':
        return RANK.get(rec['confidence_class'], 5)
    return 9


def _rel_from_row(row, field, to, problems):
    prov = row['provenance']
    rec = {'field': field, 'to': to, 'provenance': prov, 'source': None, 'method': None, 'supporting_refs': [], 'confidence_class': None,
           'missing_evidence': None, 'establishes_enforcement': False, 'establishes_test_coverage': False, 'establishes_qualification': False,
           'row_id': row.get('relationship_id')}
    if prov == 'SOURCE_STATED':
        s = row.get('source') or {}
        loc = s.get('location') or s.get('path')
        if not (s.get('repo') and s.get('revision') and loc):
            problems.add('G3', 'source_stated_without_repo_revision_or_location', row.get('relationship_id'))
            rec['provenance'] = 'UNRESOLVED'
            rec['missing_evidence'] = 'G3 reports SOURCE_STATED without a complete source (repo, revision, location); not kept as SOURCE_STATED'
            return rec
        rec['source'] = {'repo': s['repo'], 'revision': s['revision'], 'location': (s['path'] + ' :: ' + s['location']) if s.get('path') and s.get('location') else loc}
    elif prov == 'DERIVED':
        rec['method'] = _text(row.get('method'), 'unrecorded method')
        if not row.get('method'):
            problems.add('G3', 'derived_without_method', row.get('relationship_id'))
        rec['supporting_refs'] = [x for x in (row.get('supporting_references') or []) if type(x) is str and x] or [row.get('relationship_id') or 'unrecorded']
        c = row.get('confidence')
        if c not in ('high', 'medium', 'low', 'heuristic'):
            problems.add('G3', 'derived_without_confidence_class', row.get('relationship_id'))
            c = 'heuristic'
        rec['confidence_class'] = c
    else:
        rec['missing_evidence'] = _text(row.get('missing_evidence'), 'no evidence recorded for this link')
    return rec


def _add_ref(e, field, to):
    cur = e.get(field)
    if cur is None:
        e[field] = [to]
    elif to not in cur:
        e[field] = sorted(set(cur) | {to})


def resolve_refs(ds, idm, problems):
    """Map partition-declared refs to global ids; anything that is not a typed catalogue id becomes an UNRESOLVED placeholder."""
    layers = ds['layers']
    ev_ids = ds['evidence']
    for layer, ents in layers.items():
        for e in ents.values():
            p = e['_partition']
            for field, raw in e['_refs'].items():
                if field not in V.REF_FIELDS[layer] or field == 'evidence_digest_refs':
                    continue
                want = TYPED[field]
                out = set()
                for ref in raw:
                    if ref.startswith('UNRESOLVED'):
                        out.add(ref if ref.startswith('UNRESOLVED:') else 'UNRESOLVED:' + ref[len('UNRESOLVED'):].lstrip(':- '))
                        continue
                    gid = idm(p, ref)
                    if gid in layers[want]:
                        out.add(gid)
                    else:
                        problems.add(p, 'ref_not_a_catalogue_id', '%s.%s -> %s' % (e['catalogue_id'], field, ref), want)
                        if ref.startswith('EXTERNAL_RESOLVED_IN_RETAINED_JUNIT:'):
                            out.add('UNRESOLVED:external test identity named only in a retained JUnit record; no catalogue test entry: %s' % ref[len('EXTERNAL_RESOLVED_IN_RETAINED_JUNIT:'):])
                        else:
                            out.add('UNRESOLVED:not a catalogue %s id: %s' % (want, ref))
                e[field] = sorted(out)
            evs = set()
            for ref in e['_evidence_raw']:
                if ref.startswith('UNRESOLVED'):
                    evs.add('UNRESOLVED:' + ref.split(':', 1)[-1])
                    continue
                d = _hex(ref) if len(ref.replace('sha256:', '')) == 64 else ds['ev_alias'].get(ref)
                if d in ev_ids:
                    evs.add(d)
                else:
                    problems.add(p, 'evidence_ref_not_in_evidence_index', '%s -> %s' % (e['catalogue_id'], ref))
                    evs.add('UNRESOLVED:not an evidence digest in the evidence index: %s' % ref)
            e['evidence_digest_refs'] = sorted(evs)


def apply_g3(ds, g3dir, idm, cands, problems):
    layers = ds['layers']
    manifest = _read(os.path.join(g3dir, 'G3.manifest.json'))
    rows = []
    for sh in manifest['shards']:
        rows += _read(os.path.join(g3dir, sh['file']))
    ev_ids = ds['evidence']
    best = {}
    ext = []
    stats = {}
    cand_pairs = {}
    owner_of = {}
    for layer, ents in layers.items():
        for cid in ents:
            owner_of[cid] = layer

    def ep(p, x, is_to=False):
        if x is None:
            return None
        if x.startswith('EV:'):
            return _hex(x.split(':', 2)[2])
        if x.startswith(('REV:', 'CONFLICT:')):
            return None
        return idm(p, x)

    so_digests = {}
    for cw in ds['crosswalk']:
        if cw['disposition'] == 'SOURCE_ONLY_ARTIFACT':
            so_digests.setdefault(cw['raw_digest'][7:], set()).add(cw['raw_set'])

    def srcrow_ok(sr):
        m = V.SR_RE.match(sr or '')
        return bool(m) and any(x.startswith(m.group(1)) for x in so_digests.get(m.group(2), ()))

    for row in sorted(rows, key=lambda r: r['relationship_id']):
        p = row['partition']
        fr, to = ep(p, row.get('from')), ep(p, row.get('to'), True)
        typ, kind, prov = row['type'], row.get('relation_kind'), row['provenance']
        x = dict(row, from_global=fr, to_global=to)
        ext.append(x)
        key = (typ, kind, prov)
        stats[key] = stats.get(key, 0) + 1
        if fr is None or to is None or kind == 'revision_of':
            if kind != 'revision_of' and prov == 'UNRESOLVED':
                # an unresolved G3 row has no catalogue endpoint; it stays in the relationship artifact and is counted here
                problems.add('G3', 'unresolved_relationship_row_without_endpoint', row['relationship_id'], typ)
            continue
        if kind == 'candidate_equivalent':
            if fr in owner_of and to in owner_of:
                cand_pairs.setdefault((fr, to), []).append(row)
            else:
                problems.add('G3', 'candidate_endpoint_not_in_catalogue', row['relationship_id'])
            continue
        if typ in ('rule->rule', 'scenario->scenario'):
            if kind in ('related_dep', 'references') and fr in owner_of and to in owner_of and owner_of[fr] == owner_of[to]:
                field = 'related_refs'
                rec = _rel_from_row(row, field, to, problems)
                k = (fr, field, to)
                if k not in best or _rank(rec) < _rank(best[k]):
                    best[k] = rec
            elif kind in ('related_dep', 'references'):
                problems.add('G3', 'related_endpoint_not_in_catalogue', row['relationship_id'], '%s -> %s' % (row.get('from'), row.get('to')))
            continue
        if typ in INSTANCE_LEVEL_TYPES:
            continue
        if row.get('from_kind') == 'source_reference' and typ.startswith('source_reference->'):
            # inbound link from a source-only raw record; recorded on the entry it points at, keyed by the raw digest
            if to in owner_of and srcrow_ok(row.get('from')):
                rec = _rel_from_row(row, 'source_reference_refs', row['from'], problems)
                k = (to, 'source_reference_refs', row['from'])
                if k not in best or _rank(rec) < _rank(best[k]):
                    best[k] = rec
            else:
                problems.add('G3', 'source_reference_endpoint_not_in_catalogue', row['relationship_id'], '%s -> %s' % (row.get('from'), row.get('to')))
            continue
        fld = G3_FIELD.get(typ)
        if fld is None:
            problems.add('G3', 'unknown_relationship_type', row['relationship_id'], typ)
            continue
        layer, field = fld
        if fr not in layers[layer]:
            problems.add('G3', 'endpoint_not_in_catalogue', row['relationship_id'], '%s %s' % (typ, row.get('from')))
            continue
        tolayer = {'scenario_refs': 'scenarios', 'test_refs': 'tests', 'fixture_refs': 'fixtures'}.get(field)
        if field == 'evidence_digest_refs':
            if to not in ev_ids:
                problems.add('G3', 'evidence_endpoint_not_in_evidence_index', row['relationship_id'], row.get('to'))
                continue
        elif to not in layers[tolayer]:
            problems.add('G3', 'endpoint_not_in_catalogue', row['relationship_id'], '%s %s' % (typ, row.get('to')))
            continue
        rec = _rel_from_row(row, field, to, problems)
        k = (fr, field, to)
        if k not in best or _rank(rec) < _rank(best[k]):
            best[k] = rec
        if typ == 'rule->scenario':
            rk = (to, 'rule_refs', fr)
            rrec = dict(rec, field='rule_refs', to=fr)
            if rk not in best or _rank(rrec) < _rank(best[rk]):
                best[rk] = rrec
    # attach: forward links add refs; every declared pair gets exactly one relationship record
    for (owner, field, to), rec in sorted(best.items()):
        e = layers[owner_of[owner]][owner]
        _add_ref(e, field, to)
    # mirror rule <-> scenario declarations so both ends agree (the declaring end keeps its own provenance)
    mirrored = 0
    for rid, r in layers['rules'].items():
        for sid in r['scenario_refs']:
            s = layers['scenarios'].get(sid)
            if s is not None and rid not in s['rule_refs']:
                _add_ref(s, 'rule_refs', rid)
                mirrored += 1
    for sid, s in layers['scenarios'].items():
        for rid in s['rule_refs']:
            r = layers['rules'].get(rid)
            if r is not None and sid not in r['scenario_refs']:
                _add_ref(r, 'scenario_refs', sid)
                mirrored += 1
    if mirrored:
        problems.add('catalogue', 'one_sided_rule_scenario_link_mirrored', None, '%d link ends added so that both ends agree; the declaring end keeps its provenance' % mirrored)
    # alias candidates: G1 groups and G3 rows (no merge; DERIVED only)
    acand = {}
    for c in cands:
        mem = []
        for m in c['members']:
            gid = m if type(m) is str else m.get('global_id') or m.get('id')
            if gid in owner_of:
                mem.append(gid)
        reason = c.get('reason') or c.get('source_reason') or c.get('kind')
        conf = c.get('confidence') if c.get('confidence') in ('high', 'medium', 'low', 'heuristic') else 'heuristic'
        method = c.get('method') or c.get('kind')
        for a in sorted(set(mem)):
            for b in sorted(set(mem)):
                if a != b:
                    acand[(a, b)] = {'field': 'alias_candidates', 'to': b, 'provenance': 'DERIVED', 'source': None, 'method': '%s (G1 %s)' % (method, c.get('kind')),
                                     'supporting_refs': [reason], 'confidence_class': conf, 'missing_evidence': None, 'establishes_enforcement': False,
                                     'establishes_test_coverage': False, 'establishes_qualification': False}
    for (a, b), rws in sorted(cand_pairs.items()):
        if (a, b) not in acand:
            r0 = rws[0]
            rec = _rel_from_row(r0, 'alias_candidates', b, problems)
            if rec['provenance'] == 'DERIVED':
                acand[(a, b)] = rec
    for (a, b), rec in sorted(acand.items()):
        layers[owner_of[a]][a].setdefault('_alias_candidates', []).append(rec)
    ds['_relationship_rows'] = ext
    ds['_g3_best'] = best
    ds['_g3_stats'] = stats


def finalize_relationships(ds, problems):
    layers = ds['layers']
    best = ds['_g3_best']
    # reverse look-up for refs that the partition declared on the non-forward end
    fwd_of = {}
    for (owner, field, to), rec in best.items():
        fwd_of[(owner, to)] = rec
    default_n = 0
    for layer, ents in layers.items():
        for cid, e in ents.items():
            rels = []
            acs = {a['to']: a for a in e.pop('_alias_candidates', [])}
            e['alias_candidates'] = sorted(acs)
            for field, to in V.ref_pairs(layer, e):
                if field == 'alias_candidates':
                    rels.append(dict(acs[to]))
                    continue
                rec = best.get((cid, field, to))
                if rec is None and field not in FORWARD[layer]:
                    r2 = fwd_of.get((to, cid))
                    if r2 is not None:
                        rec = dict(r2, field=field, to=to)
                if rec is None and field == 'fixture_refs' and to in layers['fixtures'] and set(layers['fixtures'][to]['annotations'].get('derived_from_raw', [])) & set(e['raw_refs']):
                    # a derived scenario data artifact is, by the partition's own record, the data of the scenario-defining raw record
                    shared = sorted(set(layers['fixtures'][to]['annotations']['derived_from_raw']) & set(e['raw_refs']))
                    rec = {'field': field, 'to': to, 'provenance': 'DERIVED', 'source': None,
                           'method': 'partition derived_fixture_artifacts: the artifact is the data of the scenario-defining raw record the scenario also rests on',
                           'supporting_refs': shared, 'confidence_class': 'medium', 'missing_evidence': None, 'establishes_enforcement': False,
                           'establishes_test_coverage': False, 'establishes_qualification': False}
                if rec is None:
                    if to.startswith('UNRESOLVED:'):
                        rec = _blank_rel(field, to, 'partition output marks this reference unresolved: %s' % to[len('UNRESOLVED:'):])
                    else:
                        rec = _blank_rel(field, to, 'no source location or derivation method was recorded for this link by the partition or the G3 relationship pass')
                        default_n += 1
                rels.append(dict(rec))
            for r in rels:
                if r.get('row_id') is None:
                    r.pop('row_id', None)
            rels.sort(key=lambda r: (r['field'], r['to']))
            e['relationships'] = rels
    if default_n:
        problems.add('catalogue', 'declared_link_without_provenance_row', None, '%d declared links have no G3 row; recorded UNRESOLVED, none promoted' % default_n)


# ---------------------------------------------------------------------------------------------- generic overlays (small fixtures)

def _apply_generic(ds, kind, doc):
    layers = ds['layers']
    if kind == 'identity':
        by = {cid: (l, e) for l in layers for cid, e in layers[l].items()}
        for m in doc.get('merges', []):
            if not str(m.get('basis', '')).strip():
                raise LoadRefusal('merge into %s has no stated basis' % m.get('into'))
            layer, keep = by[m['into']]
            for gone in m['from']:
                g_layer, g = by.pop(gone)
                if g_layer != layer:
                    raise LoadRefusal('merge across layers: %s' % gone)
                keep['aliases'] = sorted(set(keep['aliases']) | set(g['aliases']) | set(g['native_ids']) | {gone})
                keep['raw_refs'] = sorted(set(keep['raw_refs']) | set(g['raw_refs']))
                keep['lineage'] += [l for l in g['lineage'] if l not in keep['lineage']]
                del layers[layer][gone]
                for r in ds['crosswalk']:
                    if r['target'] == gone:
                        r['target'] = m['into']
                        r['disposition'] = 'ALIAS_OF' if r['disposition'] == 'CANONICAL' else r['disposition']
                for l2 in layers:
                    for e in layers[l2].values():
                        for f in V.REF_FIELDS[l2]:
                            v = e.get(f)
                            if type(v) is list and gone in v:
                                e[f] = sorted(set(m['into'] if x == gone else x for x in v))
    elif kind == 'attributes':
        idx = {cid: e for l in layers for cid, e in layers[l].items()}
        for cid, attrs in sorted(doc.get('items', {}).items()):
            if cid in idx:
                for k, v in attrs.items():
                    if k in ('normative_type', 'adoption_status', 'scenario_class', 'release_scope', 'mvp_applicability'):
                        idx[cid][k] = v
                        if k == 'normative_type':
                            idx[cid]['_nt_set'] = True
    elif kind == 'relationships':
        idx = {}
        for l in layers:
            idx.update(layers[l])
        idx.update(ds['evidence'])
        for item in doc.get('items', []):
            e = idx.get(item['owner'])
            if e is None:
                raise LoadRefusal('relationship owner %s is not in the catalogue' % item['owner'])
            rel = {'field': item['field'], 'to': item['to'], 'provenance': item['provenance'], 'source': item.get('source'), 'method': item.get('method'),
                   'supporting_refs': item.get('supporting_refs', []), 'confidence_class': item.get('confidence_class'),
                   'missing_evidence': item.get('missing_evidence'), 'establishes_enforcement': False,
                   'establishes_test_coverage': False, 'establishes_qualification': False}
            ds.setdefault('_generic_rels', {}).setdefault(item['owner'], []).append(rel)
    else:
        raise LoadRefusal('unknown overlay kind %s' % kind)



# ---------------------------------------------------------------------------------------------- MVP-linked overlay (architect ruling Q8)

MVP_ROW_BASIS = 'MB-MVPCHAIN-ROW'


def apply_mvp_links(ds, doc, bases, problems):
    """Apply the pinned overlay of MVP-linked items.

    Each item names one existing entry by catalogue id and by the exact identity it must carry (native id, source repository, source
    path, normative type); a mismatch refuses the load. It adds typed links from that entry to the scenarios that carry the MVP
    requirement (found by native id; each must be a scenario that is mvp_fixed on the MVP expectation-row basis), as G3-shaped rows
    of partition OVERLAY plus the embedded relationship records. Nothing is merged, renamed or removed, a link establishes nothing,
    and only an item that states an applicability changes the applicability of its entry.
    """
    layers = ds['layers']
    scen_by_native = {}
    for cid, e in layers['scenarios'].items():
        for n in e['native_ids']:
            scen_by_native.setdefault(n, []).append(cid)
    if doc.get('profile') != 'ocs-catalogue-overlay/0' or doc.get('non_authorizing') is not True or doc.get('authority') != 'none':
        raise LoadRefusal('the MVP link overlay must be an ocs-catalogue-overlay/0 document, non-authorizing, authority none')
    basis = doc.get('mvp_basis')
    if bases is not None and basis:
        bases[basis['basis_id']] = {k: v for k, v in basis.items() if k != 'basis_id'}
    rows = ds.setdefault('_relationship_rows', [])
    taken = {r['relationship_id'] for r in rows}
    for item in doc.get('links', []):
        e = layers['rules'].get(item['id'])
        if e is None:
            raise LoadRefusal('overlay item %s is not a rule entry of the catalogue' % item['id'])
        want = item['expect']
        if want['native_id'] not in e['native_ids'] or e['source'].get('repo') != want['source_repo'] or e['source'].get('path') != want['source_path'] \
                or e.get('normative_type') != want['normative_type']:
            raise LoadRefusal('overlay item %s does not match the identity it expects (native id, source repository, path, normative type)' % item['id'])
        for native in item['target_native_ids']:
            found = scen_by_native.get(native, [])
            if len(found) != 1:
                raise LoadRefusal('overlay item %s: %s names %d scenarios, exactly one is required' % (item['id'], native, len(found)))
            tgt = layers['scenarios'][found[0]]
            if tgt['mvp_applicability'].get('value') != 'mvp_fixed' or tgt['mvp_applicability'].get('basis_id') != MVP_ROW_BASIS:
                raise LoadRefusal('overlay item %s: scenario %s is not an MVP expectation row' % (item['id'], found[0]))
            row = {'relationship_id': None, 'type': item['row_type'], 'provenance': item['provenance'], 'relation_kind': item['relation_kind'],
                   'from': item['id'], 'from_global': item['id'], 'to': found[0], 'to_global': found[0], 'from_kind': 'rule', 'to_kind': 'scenario',
                   'partition': 'OVERLAY', 'claim_status': 'candidate_link_only_non_authorizing', 'establishes_enforcement': False,
                   'establishes_test_coverage': False, 'establishes_qualification': False}
            if item.get('note'):
                row['note'] = item['note']
            if item['provenance'] == 'SOURCE_STATED':
                row['source'] = dict(item['source'])
            else:
                row.update(method=item['method'], confidence=item['confidence'], supporting_references=list(item['supporting_refs']))
            rid = 'REL-' + V.canonical_digest(['mvp-linked-q8', item['id'], found[0]])[7:23]
            if rid in taken or any((r['field'], r['to']) == ('scenario_refs', found[0]) for r in e['relationships']):
                raise LoadRefusal('overlay item %s already has a link to %s' % (item['id'], found[0]))
            row['relationship_id'] = rid
            taken.add(rid)
            rows.append(row)
            _add_ref(e, 'scenario_refs', found[0])
            e['relationships'].append(_rel_from_row(row, 'scenario_refs', found[0], problems))
            # the links are bidirectional: the MVP scenario lists the entry under rule_refs on the same row
            _add_ref(tgt, 'rule_refs', item['id'])
            tgt['relationships'].append(_rel_from_row(row, 'rule_refs', item['id'], problems))
            tgt['relationships'].sort(key=lambda r: (r['field'], r['to']))
        e['relationships'].sort(key=lambda r: (r['field'], r['to']))
        ann = e['annotations']
        ann['mvp_link_overlay'] = doc['overlay_id']
        ann['mvp_link_kind'] = item['kind']
        if item.get('scope_note'):
            ann['mvp_link_scope'] = item['scope_note']
        if item.get('applicability'):
            e['mvp_applicability'] = dict(item['applicability'])
    rows.sort(key=lambda r: r['relationship_id'])

# ---------------------------------------------------------------------------------------------- assemble

def _lineage_set_records(ds, problems):
    out = []
    members = {}
    for r in ds['crosswalk']:
        if r['disposition'] == 'HISTORICAL_REVISION_OF' and r['target'] in ds['lineage_sets']:
            members.setdefault(r['target'], []).append(r)
    for lid in sorted(ds['lineage_sets']):
        ls = ds['lineage_sets'][lid]
        mem = []
        for r in sorted(members.get(lid, []), key=lambda x: (x['raw_set'], x['raw_index'])):
            mem.append({'revision_id': r['native_id'] or '%s:%d' % (r['raw_set'], r['raw_index']), 'raw_ref': '%s:%d' % (r['raw_set'], r['raw_index']),
                        'digest': r['raw_digest'], 'relation': 'HISTORICAL_REVISION'})
        stated = ls.get('member_count')
        if stated is not None and stated != len(mem):
            problems.add(ls['_partition'], 'lineage_set_member_count_differs_from_crosswalk', lid, 'set states %s, crosswalk rows %d' % (stated, len(mem)))
        first = (members.get(lid) or [None])[0]
        out.append({'catalogue_id': lid, 'title': _text(ls.get('title'), lid), 'tier': 'LINEAGE_SET', 'source': {
            'repo': first['source_repo'] if first else 'unrecorded', 'revision': 'unrecorded', 'path': first['path'] if first else None, 'anchor': None},
            'native_ids': [], 'aliases': [], 'raw_refs': [m['raw_ref'] for m in mem], 'lineage': mem, 'annotations': {'scope': ls.get('scope')} if type(ls.get('scope')) is str else {},
            'release_scope': 'post_v0_1' if ls.get('_post') else 'unknown', 'mvp_applicability': {'value': 'unresolved', 'reason': 'lineage set; no applicability stated'}})
    return out


def assemble(base, partitions, overlays=(), global_dir=None, problems=None):
    """Read, normalize, apply overlays and return the dataset the builder consumes. `problems` collects load defects."""
    problems = problems if problems is not None else Problems()
    READ_LOG.clear()
    ds = load_all(base, partitions, problems)
    _apply_rows(ds, problems)
    revs = ds['layers'].pop('_revs')
    idm = IdMap()
    cands = []
    layers = ds['layers']
    if global_dir:
        idm, cands = apply_g1(ds, os.path.join(global_dir, 'G1'), problems)
    resolve_refs(ds, idm, problems)
    bases = None
    if global_dir:
        bases = apply_g2(ds, os.path.join(global_dir, 'G2'), idm, problems)
        apply_g3(ds, os.path.join(global_dir, 'G3'), idm, cands, problems)
    else:
        ds['_g3_best'] = {}
        ds['_relationship_rows'] = []
    deferred = []
    for kind, path in overlays:
        if kind == 'mvp_links':
            deferred.append(path)
        else:
            _apply_generic(ds, kind, _read(path))
    # without a rule-type overlay the partition's own stated classification is used when it is in the vocabulary
    for e in layers['rules'].values():
        if not e.get('_nt_set'):
            c = e['annotations'].get('partition_classification')
            e['normative_type'] = c if c in NORMATIVE else 'unknown'
            if c == 'constitutional_floor':
                e['adoption_status'] = 'unknown'
                e['normative_type'] = 'unknown'
    for layer in layers:
        for e in layers[layer].values():
            for f in V.REF_FIELDS[layer]:
                e.setdefault(f, [])
    finalize_relationships(ds, problems)
    for owner, rels in ds.get('_generic_rels', {}).items():
        for layer in layers:
            if owner in layers[layer]:
                e = layers[layer][owner]
                have = {(r['field'], r['to']): i for i, r in enumerate(e['relationships'])}
                for rel in rels:
                    k = (rel['field'], rel['to'])
                    if k in have:
                        e['relationships'][have[k]] = rel
                    else:
                        e['relationships'].append(rel)
    ds['overlays'] = []
    for path in deferred:
        with open(path, 'rb') as fh:
            raw = fh.read()
        ds['overlays'].append({'path': 'docs/mvp-recovery/registry/overlays/' + os.path.basename(path), 'sha256': V.sha256_bytes(raw)})
        apply_mvp_links(ds, json.loads(raw.decode('utf-8')), bases, problems)
    # crosswalk: co-registration and post-V0.1 markers; drop private members
    for r in ds['crosswalk']:
        co = r.pop('_co', None)
        r.pop('_partition', None)
        r.pop('_raw_file', None)
        if co:
            gids = sorted({idm(r['raw_set'], c) for c in co})
            # a row that also stands for more than one scenario lists every one of them
            r['annotations']['co_registered'] = gids[0] if len(gids) == 1 else gids
            for gid in gids:
                tgt = layers['scenarios'].get(gid)
                if tgt is None:
                    problems.add(r['raw_set'], 'co_registered_scenario_not_in_catalogue', '%s:%d' % (r['raw_set'], r['raw_index']), gid)
                else:
                    tgt['raw_refs'] = sorted(set(tgt['raw_refs']) | {'%s:%d' % (r['raw_set'], r['raw_index'])})
        if r['raw_digest'] in ds['post_digests']:
            r['annotations']['release_scope'] = 'post_v0_1'
            r['annotations']['post_v0_1_reason'] = ds['post_digests'][r['raw_digest']]
    lineage_sets = _lineage_set_records(ds, problems)
    out_layers = {}
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        recs = []
        for cid in sorted(layers[layer]):
            e = layers[layer][cid]
            for k in [k for k in e if k.startswith('_')]:
                e.pop(k)
            recs.append(e)
        out_layers[layer] = recs
    inventory = []
    seen = set()
    for it in ds['inventory']:
        if it['set_id'] in seen:
            continue
        seen.add(it['set_id'])
        rv = revs.get(it['partition'], set())
        inventory.append({'set_id': it['set_id'], 'description': 'partition output %s%s' % (it['partition'], ' (raw file %s)' % it['raw_file'] if it.get('raw_file') else ''),
                          'source_repo_revisions': [{'repo': a, 'revision': b} for a, b in sorted(rv) if a != 'unrecorded' or b != 'unrecorded'] or [{'repo': 'unrecorded', 'revision': 'unrecorded'}]})
    dataset = {'registry_version': '0.1.0', 'synthetic_sample': False, 'source_inventory': inventory, 'crosswalk': ds['crosswalk'],
               'evidence': sorted(ds['evidence'].values(), key=lambda e: e['evidence_digest']), 'lineage_sets': lineage_sets,
               'relationship_rows': ds.get('_relationship_rows', []), 'mvp_bases': bases, 'load_problems': problems.as_list(),
               'completeness_limitations': [
                   'Loaded from partition outputs; entries absent from those outputs are absent here.',
                   'Relationships that arrive without provenance are recorded UNRESOLVED; none is promoted.',
                   'Attributes not stated by a partition or overlay are unknown or unresolved, not guessed.',
                   'Records that carry no source revision say so (unrecorded) and are counted in the Catalogue Integrity Report.',
                   'Informational catalogue only: non-authorizing, authority none, activates nothing, release and production remain on HOLD.']}
    dataset.update(out_layers)
    root = os.path.realpath(base)
    dataset['overlays'] = ds.get('overlays', [])
    dataset['input_files'] = sorted((os.path.relpath(p, root).replace(os.sep, '/'), d) for p, d in READ_LOG.items())
    return dataset


def regeneration_recipe(files, partitions, base, global_dir, layout, gzip_artifacts=False, overlays=()):
    files = [list(f) for f in files]
    per = {}
    for rel, dg in files:
        parts = rel.split('/')
        key = '/'.join(parts[:2]) if parts[0] == 'global' and len(parts) > 2 else parts[0]
        per.setdefault(key, []).append([rel, dg])
    return {'recipe_version': 1,
            'summary': 'Every committed partition, the manifest and every external artifact are a pure function of the pinned partition outputs and the tool files; rerunning the command on identical inputs reproduces them byte for byte.',
            'command': ['python3', '-I', 'docs/mvp-recovery/registry/tools/load_partitions.py', '--in', '<PARTITION_OUTPUT_DIR>', '--partitions'] + list(partitions) +
                       ['--global-dir', '<PARTITION_OUTPUT_DIR>/global', '--out', '<CATALOGUE_DIR>', '--layout', layout] + (['--gzip-artifacts'] if gzip_artifacts else ['--artifacts', '<ARTIFACT_DIR>']) + [x for o in overlays for x in ('--overlay', o['path'])],
            'inputs': {'partitions': list(partitions), 'global_passes': sorted(d for d in os.listdir(global_dir) if d in ('G1', 'G2', 'G3')) if global_dir else [],
                       'input_file_count': len(files), 'input_files_sha256': V.canonical_digest(files),
                       'per_input_directory_sha256': {k: V.canonical_digest(v) for k, v in sorted(per.items())}, **({'overlays': [dict(o) for o in overlays]} if overlays else {})},
            'verification': ['python3 -I docs/mvp-recovery/registry/tools/validate_registry.py --root <CATALOGUE_DIR>' + ('' if gzip_artifacts else ' --artifacts <ARTIFACT_DIR>'),
                             'python3 -I docs/mvp-recovery/registry/tools/generate_reports.py --root <CATALOGUE_DIR> --check']}


def main(argv):
    args = list(argv)
    opts = {'layout': 'compact', 'partitions': ['A', 'B', 'C', 'D', 'R4'], 'global': None, 'artifacts': None, 'problems': None, 'in': None, 'out': None}
    try:
        while args:
            a = args.pop(0)
            if a == '--partitions':
                opts['partitions'] = []
                while args and not args[0].startswith('--'):
                    opts['partitions'].append(args.pop(0))
            elif a == '--gzip-artifacts':
                opts['gzip'] = True
            elif a == '--overlay':
                opts.setdefault('overlay', []).append(args.pop(0))
            elif a in ('--in', '--out', '--global-dir', '--layout', '--artifacts', '--problems'):
                opts[{'--global-dir': 'global'}.get(a, a[2:])] = args.pop(0)
            else:
                raise IndexError
        if opts.get('gzip') and not opts['artifacts'] and opts['out']:
            opts['artifacts'] = os.path.join(opts['out'], 'artifacts')
        if not opts['in'] or not opts['out'] or opts['layout'] not in ('full', 'compact') or (opts['layout'] == 'compact' and not opts['artifacts']):
            raise IndexError
    except IndexError:
        sys.stderr.write('usage: load_partitions.py --in DIR [--partitions A B ...] [--global-dir DIR] --out ROOT [--layout full|compact] [--artifacts DIR] [--gzip-artifacts] [--overlay FILE] [--problems FILE]\n')
        return 2
    base = os.path.abspath(opts['in'])
    gdir = os.path.abspath(opts['global']) if opts['global'] else None
    problems = Problems()
    try:
        ds = assemble(base, opts['partitions'], overlays=[('mvp_links', os.path.abspath(p)) for p in opts.get('overlay', [])], global_dir=gdir, problems=problems)
    except LoadRefusal as exc:
        sys.stderr.write('load refused: %s\n' % exc)
        return 1
    out = os.path.abspath(opts['out'])
    os.makedirs(out, exist_ok=True)
    sdir = os.path.join(out, 'schemas')
    if not os.path.isdir(sdir):
        import shutil
        shutil.copytree(os.path.join(B.REGISTRY_ROOT, 'schemas'), sdir)
    for dirname in V.LAYER_DIRS.values():
        for dirpath, dirs, files in os.walk(os.path.join(out, dirname)):
            for fn in files:
                if fn.endswith('.json'):
                    os.remove(os.path.join(dirpath, fn))
    ds['regeneration'] = regeneration_recipe(ds['input_files'], opts['partitions'], base, gdir, opts['layout'], bool(opts.get('gzip')), ds.get('overlays', ()))
    if opts.get('gzip') and opts['artifacts'] and os.path.isdir(opts['artifacts']):
        for fn in os.listdir(opts['artifacts']):
            if fn.endswith('.json.gz'):
                os.remove(os.path.join(opts['artifacts'], fn))
    ds['load_problems_summary'] = problems.summary()
    manifest = B.build(ds, out, max_per=B.REAL_MAX_PER_PARTITION, layout=opts['layout'], artifacts_dir=os.path.abspath(opts['artifacts']) if opts['artifacts'] else None,
                       artifacts_gzip=bool(opts.get('gzip')))
    if opts['problems']:
        with open(opts['problems'], 'wb') as fh:
            fh.write(V.dump_file({'load_problems': problems.full()}))
    sys.stdout.write('built %s (%s layout); %d load problem kind(s)\n' % (manifest['digest'], opts['layout'], len(problems.rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
