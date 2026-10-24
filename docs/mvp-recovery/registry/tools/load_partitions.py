#!/usr/bin/env python3
"""Loader contract: consolidation outputs -> layered catalogue dataset -> build (non-authorizing).

    python3 -I load_partitions.py --in OUT_DIR --partitions A B C D R4 [--overlay DIR ...] --out ROOT

Input shape (see the registry README for the full contract). For each partition P, under OUT_DIR/P/:
  P.canonical.json     {"rules":X,"logical_scenarios":X,"test_implementations":X,"fixtures":X}; X is either a
                       list of entries or a pointer {"file":"parts/...","count":n,"sha256":hex} to a shard
                       {"entries":[...]}.  Non-layer keys (for example "layout") are ignored.
  P.crosswalk.json     {"parts":[{"file":...}]} of shards {"rows":[...]} or {"rows":[...]} inline. Rows carry
                       raw_index, raw_digest, source_repo, path, native_id, tier and disposition (either the
                       catalogue vocabulary plus "target", or the legacy CANONICAL:<id> / ATTACHED_TO:<id> /
                       EVIDENCE_INDEXED:<digest> / SOURCE_REFERENCE_ONLY / UNRESOLVED:<reason> forms).
  P.evidence-index.json  the same pointer/shard pattern with entries carrying digest, evidence_kind, raw_index,
                       artifact_location_and_digest and the verbatim verdict fields.
Overlays (OUT_DIR/global/G1, G2, G3 or any --overlay dir): *.json files of one of three kinds, applied in the
order G1 identity, G2 attributes, G3 relationships:
  {"overlay":"identity","merges":[{"into":id,"from":[id...],"basis":"source-stated lineage ..."}]}
  {"overlay":"attributes","items":{id:{normative_type,adoption_status,scenario_class,release_scope,mvp_applicability:{value,reason}}}}
  {"overlay":"relationships","items":[{"owner":id,"field":f,"to":ref,"provenance":P,...provenance members...}]}
Rules the loader enforces: nothing is guessed. A missing attribute becomes unknown/unresolved; a link that arrives
without provenance becomes UNRESOLVED (never SOURCE_STATED or DERIVED); a merge needs a stated basis; two
partitions that emit the same canonical id are merged only when repo, path and native ids are identical,
otherwise the load refuses. Partition totals are never summed before this identity pass.
"""
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


class LoadRefusal(Exception):
    pass


def _read(path):
    with open(path, 'rb') as fh:
        return V.RR.loads_strict(fh.read().decode('utf-8'))


def _shard(path, key):
    data = _read(path)
    return data if type(data) is list else data.get(key, [])


def _items(base, node, key):
    """Resolve an inline list or a pointer/parts structure into a list of records."""
    if type(node) is list:
        out = []
        for item in node:
            out.extend(_items(base, item, key) if type(item) is dict and 'file' in item else [item])
        return out
    if type(node) is dict and 'file' in node:
        return _shard(os.path.join(base, node['file']), key)
    if type(node) is dict and type(node.get('parts')) is list:
        out = []
        for part in node['parts']:
            out.extend(_shard(os.path.join(base, part['file']), key))
        return out
    if type(node) is dict and type(node.get(key)) is list:
        return node[key]
    return []


def _hex(d):
    d = str(d)
    for pre in ('EVIDENCE:', 'EV:'):
        if d.startswith(pre):
            d = d[len(pre):]
    return d if d.startswith('sha256:') else 'sha256:' + d


def _norm_row(pset, row):
    disp, target, reason = row.get('disposition'), row.get('target'), row.get('unresolved_reason')
    known_disp = ('CANONICAL', 'ALIAS_OF', 'HISTORICAL_REVISION_OF', 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', 'SOURCE_ONLY_ARTIFACT', 'UNRESOLVED')
    if type(disp) is str and ':' in disp and disp.split(':', 1)[0] in known_disp and target is None:
        disp, _, target = disp.partition(':')
        target = target or None
        if disp == 'UNRESOLVED':
            reason, target = target or 'unresolved in partition output', None
    legacy = row.get('disposition_legacy') or (disp if type(disp) is str and disp not in known_disp else None)
    tier = row['tier']
    if legacy:
        head, _, tail = legacy.partition(':')
        if head == 'CANONICAL':
            disp, target = 'CANONICAL', tail
        elif head == 'ATTACHED_TO':
            target = tail
            disp = ('TEST_INSTANCE_OR_EXECUTION_OCCURRENCE' if tier == 'PARAMETRIZED_INSTANCE'
                    else 'HISTORICAL_REVISION_OF' if tier in ('RULE_REVISION', 'HISTORICAL_REVISION') else 'ALIAS_OF')
        elif head == 'EVIDENCE_INDEXED':
            disp, target = 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', tail
        elif head == 'SOURCE_REFERENCE_ONLY':
            disp, target = 'SOURCE_ONLY_ARTIFACT', None
        elif head == 'UNRESOLVED':
            disp, target, reason = 'UNRESOLVED', None, tail or 'unresolved in partition output'
    if disp == 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE' and tier == 'EXECUTION_EVIDENCE' and target and not target.startswith('sha256:'):
        target = _hex(target)
    known = {'raw_index', 'raw_digest', 'source_repo', 'path', 'native_id', 'tier', 'disposition', 'target', 'unresolved_reason'}
    return {'raw_set': pset, 'raw_index': row['raw_index'], 'raw_digest': _hex(row['raw_digest']), 'source_repo': row.get('source_repo') or 'unrecorded',
            'path': row.get('path'), 'native_id': row.get('native_id'), 'tier': tier, 'disposition': disp, 'target': target,
            'unresolved_reason': reason, 'annotations': {k: row[k] for k in sorted(row) if k not in known and _plain(row[k])}}


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


def load_partition(base, pset):
    d = os.path.join(base, pset)
    canon = _read(os.path.join(d, pset + '.canonical.json'))
    rows = [_norm_row(pset, r) for r in _items(d, _read(os.path.join(d, pset + '.crosswalk.json')), 'rows')]
    evid = _items(d, _read(os.path.join(d, pset + '.evidence-index.json')), 'entries')
    entries = {}
    for key, layer in LAYER_KEY.items():
        entries[layer] = _items(d, canon.get(key, []), 'entries')
    return entries, rows, evid


def _entry(layer, e, rows_to, pset):
    cid = e['canonical_id']
    mine = rows_to.get(cid, [])
    refs = sorted('%s:%d' % (pset, r['raw_index']) for r in mine)
    aliases = sorted(set(_refs(e.get('aliases')) + [r['native_id'] for r in mine if r['disposition'] == 'ALIAS_OF' and r['native_id']]))
    native = sorted({x for x in _refs(e.get('native_ids'))})
    lineage = [{'revision_id': r['native_id'] or ('%s:%d' % (pset, r['raw_index'])), 'raw_ref': '%s:%d' % (pset, r['raw_index']),
                'digest': r['raw_digest'], 'relation': 'HISTORICAL_REVISION'} for r in mine if r['disposition'] == 'HISTORICAL_REVISION_OF']
    src = {'repo': _text(e.get('source_repo'), 'unrecorded'), 'revision': _text(e.get('source_revision'), 'unrecorded'),
           'path': e.get('path') if type(e.get('path')) is str else None, 'anchor': e.get('anchor') if type(e.get('anchor')) is str else None}
    mv = e.get('mvp_applicability')
    mvp = mv if type(mv) is dict else {'value': mv if mv in MVP else 'unresolved',
                                       'reason': _text(e.get('mvp_applicability_basis'), 'no basis stated in partition output')}
    known = {'canonical_id', 'title', 'source_repo', 'source_revision', 'path', 'anchor', 'aliases', 'native_ids', 'lineage', 'mvp_applicability',
             'rule_refs', 'scenario_refs', 'test_refs', 'associated_scenarios', 'fixture_refs', 'evidence_digest_refs', 'expected_outcome',
             'polarity', 'refund_specific', 'scenario_family', 'layer', 'raw_digests', 'type'}
    ann = {k: e[k] for k in sorted(e) if k not in known and _plain(e[k]) and k not in V.ANNOTATION_FORBIDDEN}
    out = {'catalogue_id': cid, 'title': _text(e.get('title'), _text(e.get('anchor'), cid)), 'tier': TIER_OF[layer], 'source': src,
           'native_ids': native, 'aliases': aliases, 'raw_refs': refs, 'lineage': lineage, 'annotations': ann,
           'mvp_applicability': mvp, 'release_scope': 'unknown'}
    ev = sorted(_hex(x) for x in _refs(e.get('evidence_digest_refs')))
    verbatim = e.get('expected_outcome') if type(e.get('expected_outcome')) is str else None
    if layer == 'rules':
        cls = e.get('classification')
        out.update(rule_ref={'kind': 'source_statement', 'rule_id': native[0] if native else cid, 'version': None,
                             'rule_digest': V.canonical_digest({'catalogue_id': cid, 'raw_digests': [r['raw_digest'] for r in mine]}),
                             'registry_id': None, 'record_digest': None},
                   statement_verbatim=verbatim, refund_specific=e.get('refund_specific') if type(e.get('refund_specific')) is bool else None,
                   normative_type=cls if cls in NORMATIVE else 'unknown', adoption_status='unknown',
                   scenario_refs=_refs(e.get('scenario_refs')), test_refs=_refs(e.get('test_refs')), evidence_digest_refs=ev)
    elif layer == 'scenarios':
        pol = e.get('polarity')
        out.update(rule_refs=_refs(e.get('rule_refs')), test_refs=_refs(e.get('test_refs')), evidence_digest_refs=ev,
                   expected_outcome_verbatim=verbatim, polarity=pol if pol in POLARITY else 'unknown',
                   temporal_or_recovery_flag=bool(e.get('temporal_or_recovery_flag')) if type(e.get('temporal_or_recovery_flag')) is bool else False,
                   scenario_family=e.get('scenario_family') if type(e.get('scenario_family')) is str else None,
                   refund_specific=e.get('refund_specific') if type(e.get('refund_specific')) is bool else None, scenario_class='logical')
    elif layer == 'tests':
        out.update(scenario_refs=_refs(e.get('scenario_refs')) + _refs(e.get('associated_scenarios')), rule_refs=_refs(e.get('rule_refs')),
                   fixture_refs=_refs(e.get('fixture_refs')), evidence_digest_refs=ev,
                   parametrized_instance_count=sum(1 for r in mine if r['disposition'] == 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE'))
        out['scenario_refs'] = sorted(set(out['scenario_refs']))
    else:
        sha = e.get('content_sha256')
        locs = _refs(e.get('locations')) or _refs(e.get('location')) or ([src['path']] if src['path'] else ['unrecorded'])
        out.update(fixture_identity={'basis': _text(e.get('fixture_identity_basis'), 'unrecorded'), 'content_sha256': _hex(sha) if type(sha) is str and len(sha) in (64, 71) else None},
                   locations=[{'repo': src['repo'], 'revision': src['revision'], 'path': p, 'anchor': None} for p in locs],
                   expected_outcome_verbatim=verbatim, evidence_digest_refs=ev)
    return out


def _evidence(pset, e, rows_to):
    digest = _hex(e['digest'])
    art = e.get('artifact_location_and_digest') or {}
    kind = str(e.get('evidence_kind', ''))
    mine = rows_to.get(digest, [])
    verdict = e.get('raw_result_and_original_verdict')
    return {'evidence_digest': digest, 'raw_refs': sorted('%s:%d' % (pset, r['raw_index']) for r in mine), 'tier': 'EXECUTION_EVIDENCE',
            'evidence_kind': 'independent_qualification_record' if 'independent' in kind else ('validation_claim' if 'claim' in kind or 'statement' in kind else 'run_result'),
            'run_id': e.get('run_id') if type(e.get('run_id')) is str else None,
            'test_ref': e.get('test_ref') if type(e.get('test_ref')) is str else None,
            'scenario_ref': e.get('scenario_ref') if type(e.get('scenario_ref')) is str else None,
            'historical_verdict_verbatim': verdict if type(verdict) is str else None,
            'source_commitment': {'set_id': pset, 'repo': _text(e.get('source_repo'), 'unrecorded'), 'revision': _text(e.get('source_revision'), 'unrecorded')},
            'artifact_commitment': {'path': _text(art.get('path'), 'unrecorded'), 'record_digest': _hex(art.get('record_digest_sha256') or e['digest']),
                                    'file_digest': _text(art.get('file_digest'), 'not computed')},
            'current_qualification_effect': 'none', 'annotations': {}}


def assemble(base, partitions, overlays=()):
    data = {'rules': {}, 'scenarios': {}, 'tests': {}, 'fixtures': {}}
    evidence, crosswalk, inventory = {}, [], []
    for pset in partitions:
        entries, rows, evid = load_partition(base, pset)
        rows_to = {}
        for r in rows:
            if r['target']:
                rows_to.setdefault(r['target'], []).append(r)
        crosswalk += rows
        revs = set()
        for layer, items in entries.items():
            for e in items:
                new = _entry(layer, e, rows_to, pset)
                old = data[layer].get(new['catalogue_id'])
                if old is not None:
                    same = old['source']['repo'] == new['source']['repo'] and old['source']['path'] == new['source']['path'] and old['native_ids'] == new['native_ids']
                    if not same:
                        raise LoadRefusal('canonical id %s emitted by two partitions with different identity' % new['catalogue_id'])
                    for k in ('aliases', 'raw_refs'):
                        old[k] = sorted(set(old[k]) | set(new[k]))
                    old['lineage'] += [l for l in new['lineage'] if l not in old['lineage']]
                    continue
                data[layer][new['catalogue_id']] = new
                revs.add((new['source']['repo'], new['source']['revision']))
        for e in evid:
            ev = _evidence(pset, e, rows_to)
            evidence[ev['evidence_digest']] = ev
            revs.add((ev['source_commitment']['repo'], ev['source_commitment']['revision']))
        inventory.append({'set_id': pset, 'description': 'partition output %s' % pset,
                          'source_repo_revisions': [{'repo': a, 'revision': b} for a, b in sorted(revs)] or [{'repo': 'unrecorded', 'revision': 'unrecorded'}]})
    ds = {'registry_version': '0.1.0', 'synthetic_sample': False, 'source_inventory': inventory, 'crosswalk': crosswalk,
          'evidence': sorted(evidence.values(), key=lambda e: e['evidence_digest']),
          'completeness_limitations': [
              'Loaded from partition outputs; entries absent from those outputs are absent here.',
              'Relationships that arrive without provenance are recorded UNRESOLVED; none is promoted.',
              'Attributes not stated by a partition or overlay are unknown or unresolved, not guessed.',
              'Informational catalogue only: non-authorizing, authority none, activates nothing, release and production remain on HOLD.']}
    for layer in data:
        ds[layer] = list(data[layer].values())
    for kind, path in overlays:
        _apply(ds, kind, _read(path))
    _default_relationships(ds)
    return ds


def _all(ds):
    for layer in V.REF_FIELDS:
        for e in ds[layer]:
            yield layer, e


def _apply(ds, kind, doc):
    if kind == 'identity':
        by = {e['catalogue_id']: (l, e) for l, e in _all(ds) if 'catalogue_id' in e}
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
                ds[layer] = [e for e in ds[layer] if e['catalogue_id'] != gone]
                for r in ds['crosswalk']:
                    if r['target'] == gone:
                        r['target'] = m['into']
                        r['disposition'] = 'ALIAS_OF' if r['disposition'] == 'CANONICAL' else r['disposition']
                for _, e in _all(ds):
                    for f in V.REF_FIELDS[_]:
                        pass
                _rewrite(ds, gone, m['into'])
    elif kind == 'attributes':
        idx = {e['catalogue_id']: e for _, e in _all(ds) if 'catalogue_id' in e}
        for cid, attrs in sorted(doc.get('items', {}).items()):
            if cid in idx:
                for k, v in attrs.items():
                    if k in ('normative_type', 'adoption_status', 'scenario_class', 'release_scope', 'mvp_applicability'):
                        idx[cid][k] = v
    elif kind == 'relationships':
        idx = {}
        for l, e in _all(ds):
            idx[e.get('catalogue_id') or e.get('evidence_digest')] = e
        for item in doc.get('items', []):
            e = idx.get(item['owner'])
            if e is None:
                raise LoadRefusal('relationship owner %s is not in the catalogue' % item['owner'])
            rel = {'field': item['field'], 'to': item['to'], 'provenance': item['provenance'], 'source': item.get('source'), 'method': item.get('method'),
                   'supporting_refs': item.get('supporting_refs', []), 'confidence_class': item.get('confidence_class'),
                   'missing_evidence': item.get('missing_evidence'), 'establishes_enforcement': False,
                   'establishes_test_coverage': False, 'establishes_qualification': False}
            e.setdefault('relationships', []).append(rel)
    else:
        raise LoadRefusal('unknown overlay kind %s' % kind)


def _rewrite(ds, gone, into):
    for layer, e in _all(ds):
        for f in V.REF_FIELDS[layer]:
            v = e.get(f)
            if type(v) is list and gone in v:
                e[f] = sorted(set(into if x == gone else x for x in v))
            elif v == gone:
                e[f] = into
        for rel in e.get('relationships', []):
            if rel['to'] == gone:
                rel['to'] = into


def _default_relationships(ds):
    for layer, e in _all(ds):
        have = {(r['field'], r['to']) for r in e.get('relationships', [])}
        e.setdefault('relationships', [])
        for f, t in V.ref_pairs(layer, e):
            if (f, t) not in have:
                e['relationships'].append({'field': f, 'to': t, 'provenance': 'UNRESOLVED', 'source': None, 'method': None, 'supporting_refs': [],
                                           'confidence_class': None, 'establishes_enforcement': False, 'establishes_test_coverage': False,
                                           'establishes_qualification': False,
                                           'missing_evidence': 'no source location or derivation method was recorded for this link by the partition output'})
        e['relationships'].sort(key=lambda r: (r['field'], r['to']))


def main(argv):
    args = list(argv)
    base = out = None
    parts, overlays = [], []
    while args:
        a = args.pop(0)
        if a == '--in':
            base = os.path.abspath(args.pop(0))
        elif a == '--out':
            out = os.path.abspath(args.pop(0))
        elif a == '--partitions':
            while args and not args[0].startswith('--'):
                parts.append(args.pop(0))
        elif a == '--overlay':
            odir = os.path.abspath(args.pop(0))
            for fn in sorted(os.listdir(odir)):
                if fn.endswith('.json'):
                    doc = _read(os.path.join(odir, fn))
                    if type(doc) is dict and 'overlay' in doc:
                        overlays.append((doc['overlay'], os.path.join(odir, fn)))
        else:
            sys.stderr.write('usage: load_partitions.py --in DIR --partitions P... [--overlay DIR] --out ROOT\n')
            return 2
    if not (base and out and parts):
        sys.stderr.write('--in, --out and --partitions are required\n')
        return 2
    order = {'identity': 0, 'attributes': 1, 'relationships': 2}
    overlays.sort(key=lambda o: (order.get(o[0], 9), o[1]))
    try:
        ds = assemble(base, parts, overlays)
    except LoadRefusal as exc:
        sys.stdout.write('LOAD REFUSED: %s\n' % exc)
        return 1
    os.makedirs(out, exist_ok=True)
    schemas_out = os.path.join(out, 'schemas')
    os.makedirs(schemas_out, exist_ok=True)
    for fn in sorted(os.listdir(os.path.join(B.REGISTRY_ROOT, 'schemas'))):
        with open(os.path.join(B.REGISTRY_ROOT, 'schemas', fn), 'rb') as src, open(os.path.join(schemas_out, fn), 'wb') as dst:
            dst.write(src.read())
    m = B.build(ds, out)
    sys.stdout.write('loaded %s\n' % m['digest'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
