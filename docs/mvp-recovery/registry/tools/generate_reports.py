#!/usr/bin/env python3
"""Generate the Catalogue Integrity, Governance Coverage and Denominator reports (non-authorizing).

    python3 -I docs/mvp-recovery/registry/tools/generate_reports.py [--root DIR] [--out DIR] [--check]

Reads a catalogue that validates, names its exact manifest digest and source revisions in each
report, and writes reports/generated/*.json and *.md. Deterministic and offline. The reports
are informational: there is no combined scenario headline, no qualification statement and no
pass-rate; the four coverage assessments and the ten denominators are reported separately.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location('ocs_catalogue_validate_registry', os.path.join(HERE, 'validate_registry.py'))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

# short revisions named by the assembly brief for tag review-v0.1-g8-r10-20261022; each is looked for in the revisions the
# partitions recorded (a prefix match on a 40-hex revision); the report states found / not found, it never assumes
DECLARED_REVISIONS = (('hub', 'a2d9396c'), ('institutional-governance', '9b5ab721'), ('control-plane', '0a41faa9'), ('action-manifest', 'fa170815'),
                      ('execution-runtime', 'ec728da6'), ('replay-bundle', '028f63d1'), ('governance-evidence-pack', 'a3ebbb90'),
                      ('open-decision-evidence-standard', 'e86a25a1'), ('verifier', 'c0b8ba1f'), ('stack-qualification tag commit', '195c728f'),
                      ('stack-qualification main', '4298247e'), ('governed-exchange', '7f7569b0'), ('ergonomics', '54807212'))
DECLARED_TAG = 'review-v0.1-g8-r10-20261022'
ROWS_INLINE_MAX = 200
NOTE = 'Informational only. Non-authorizing; authority none; activates nothing; no rule, scenario or test was executed; release and production remain on HOLD.'


def _ratio(num, den):
    if not den:
        return None
    return '%d.%04d' % divmod(num * 10000 // den, 10000)


def _load(root):
    errors, manifest = V.validate(root)
    if errors:
        raise SystemExit('refusing to report on a catalogue that does not validate (%d finding(s))' % len(errors))
    schemas = {}
    rep = V.Report()
    _, layers = V.load_registry(root, rep, V.load_schemas(root, rep))
    return manifest, layers


def _head(manifest, title):
    return {'report': title, 'note': NOTE, 'catalogue_manifest_digest': manifest['digest'], 'registry_version': manifest['registry_version'],
            'synthetic_sample': manifest['synthetic_sample'],
            'source_revisions': [{'set_id': s['set_id'], 'repo_revisions': s['source_repo_revisions'], 'raw_record_count': s['raw_record_count'],
                                  'inventory_sha256': s['inventory_sha256']} for s in manifest['source_inventory']],
            'authority': 'none', 'non_authorizing': True}


def _recorded_revisions(manifest, layers):
    import re
    seen = {}
    for s_ in manifest['source_inventory']:
        for rr in s_['source_repo_revisions']:
            seen.setdefault((rr['repo'], rr['revision']), set()).add(s_['set_id'])
    for layer in V.ENTRY_LAYERS:
        for e in layers[layer]:
            src = e.get('source') or {}
            seen.setdefault((src.get('repo'), src.get('revision')), set()).add('entries')
    tokens = set()
    for (_, rev) in seen:
        tokens.update(re.findall(r'[0-9a-f]{40}', str(rev)))
        tokens.update(re.findall(r'(?<![0-9a-f])[0-9a-f]{8}(?![0-9a-f])', str(rev)))
    return seen, tokens


def revision_table(manifest, layers):
    seen, tokens = _recorded_revisions(manifest, layers)
    found = []
    for name, short in DECLARED_REVISIONS:
        hit = sorted(t for t in tokens if t.startswith(short))
        found.append({'component': name, 'declared_short_revision': short, 'declared_tag': DECLARED_TAG,
                      'status': 'found_in_recorded_revisions' if hit else 'not_found_in_recorded_revisions', 'matching_recorded_revisions': hit})
    return {'declared_revisions_checked_against_recorded': found,
            'recorded_repo_revisions': sorted([{'repo': str(k[0]), 'revision': str(k[1]), 'seen_in': sorted(v)} for k, v in seen.items()], key=lambda x: (x['repo'], x['revision']))}


def integrity(manifest, layers):
    cw = layers['crosswalk']
    by_set = {}
    for r in cw:
        d = by_set.setdefault(r['raw_set'], {'raw': 0, 'by_disposition': {}, 'by_tier': {}, 'unresolved': 0})
        d['raw'] += 1
        d['by_disposition'][r['disposition']] = d['by_disposition'].get(r['disposition'], 0) + 1
        d['by_tier'][r['tier']] = d['by_tier'].get(r['tier'], 0) + 1
        d['unresolved'] += r['disposition'] == 'UNRESOLVED'
    canonical = {k: len(layers[k]) for k in V.ENTRY_LAYERS}
    absorbed = {k: sum(len(e['raw_refs']) for e in layers[k]) for k in V.ENTRY_LAYERS}
    per_layer = {k: {'raw_records_absorbed': absorbed[k], 'canonical': canonical[k], 'dedup_ratio_raw_to_canonical': _ratio(absorbed[k], canonical[k])}
                 for k in V.ENTRY_LAYERS}
    prov = {}
    for layer in V.REF_FIELDS:
        for e in layers[layer]:
            for rel in e['relationships']:
                row = prov.setdefault(layer, {'SOURCE_STATED': 0, 'DERIVED': 0, 'UNRESOLVED': 0})
                row[rel['provenance']] += 1
    out = _head(manifest, 'Catalogue Integrity Report')
    inv = {s_['set_id']: s_['raw_record_count'] for s_ in manifest['source_inventory']}
    out.update({'raw_record_accounting': {'per_raw_set': dict(sorted(inv.items())), 'raw_records_in_inventory': sum(inv.values()), 'crosswalk_rows': len(cw),
                                          'each_raw_record_has_exactly_one_crosswalk_row': len(cw) == sum(inv.values()),
                                          'note': 'Checked by the validator per raw index and per committed inventory digest. Partition A has two raw files, reported as raw sets A and A2.'},
                'source_revisions_report': revision_table(manifest, layers),
                'layout': manifest.get('layout'), 'external_artifacts': manifest.get('external_artifacts', []), 'regeneration': manifest.get('regeneration', {}),
                'load_problems': manifest.get('load_problems', []),
                'unrecorded_source_revisions': {'entries_without_recorded_revision': manifest['unresolved_accounting'].get('entries_with_unrecorded_source_revision'),
                                                'evidence_without_recorded_revision': manifest['unresolved_accounting'].get('evidence_unrecorded_source_revisions'),
                                                'crosswalk_rows_with_unrecorded_source_repo': sum(1 for r in cw if r.get('source_repo') == 'unrecorded')},
                'validator': 'validate_registry.py: no findings', 'layer_counts': manifest['layer_counts'],
                'partition_count': len(manifest['partitions']), 'by_layer': per_layer,
                'by_partition_raw_set': {k: by_set[k] for k in sorted(by_set)},
                'note_on_totals': 'Per-set figures are not summed into a corpus total; global identity decisions are in the crosswalk.',
                'relationship_provenance_by_layer': {k: prov[k] for k in sorted(prov)},
                'unresolved_accounting': manifest['unresolved_accounting'],
                'generation_tool': manifest['generation_tool'], 'completeness_limitations': manifest['completeness_limitations']})
    return out


def coverage(manifest, layers):
    tally, states = {}, {}
    for r in layers['coverage']:
        sl = states.setdefault(r['subject_layer'], {})
        for st in r['states']:
            sl[st] = sl.get(st, 0) + 1
        layer = tally.setdefault(r['subject_layer'], {})
        for name, a in r['assessments'].items():
            c = layer.setdefault(name, {})
            c[a['status']] = c.get(a['status'], 0) + 1
    out = _head(manifest, 'Governance Coverage Report')
    out.update({'assessments_are_separate': 'catalogue_completeness, implementation_coverage, test_coverage and independent_qualification are never inferred from one another; a historical verdict never transfers to a new candidate; a DERIVED link is a candidate only.',
                'by_subject_layer': {k: {n: dict(sorted(v.items())) for n, v in sorted(t.items())} for k, t in sorted(tally.items())},
                'states_by_subject_layer': {k: dict(sorted(v.items())) for k, v in sorted(states.items())},
                'rows': [{'subject_id': r['subject_id'], 'states': r['states'], 'assessments': {k: v['status'] for k, v in r['assessments'].items()},
                          'mvp_applicability': r['mvp_applicability']} for r in layers['coverage']] if len(layers['coverage']) <= ROWS_INLINE_MAX else
                        'omitted: %d rows are in the committed coverage partitions (reports/)' % len(layers['coverage'])})
    return out


def denominators(manifest, layers):
    rules = {}
    for e in layers['rules']:
        rules[e['normative_type']] = rules.get(e['normative_type'], 0) + 1
    classes = {}
    for e in layers['scenarios']:
        classes[e['scenario_class']] = classes.get(e['scenario_class'], 0) + 1
    ev = layers['evidence']
    verdicts = {}
    for e in ev:
        v = e['historical_verdict_verbatim']
        key = v if v is not None else ('(none recorded)' if e.get('historical_verdict_sha256') is None else '(long verdict text: digest in the index, text in the external record)')
        verdicts[key] = verdicts.get(key, 0) + 1
    identities = {(e['run_id'], e['test_ref'], e['scenario_ref']) for e in ev if e['evidence_kind'] == 'run_result' and e['run_id'] is not None}
    scope = {}
    for layer in V.ENTRY_LAYERS:
        for e in layers[layer]:
            scope.setdefault(layer, {})
            scope[layer][e['release_scope']] = scope[layer].get(e['release_scope'], 0) + 1
    out = _head(manifest, 'Denominator Report')
    out.update({'headline_scenario_count': 'none by design: scenario denominators are reported separately and never combined',
                'denominators': {
                    '1_canonical_rules_by_normative_type': dict(sorted(rules.items())),
                    '2_logical_governance_scenarios': classes.get('logical', 0),
                    '3_suite_level_acceptance_scenarios': classes.get('suite_level_acceptance', 0),
                    '4_adversarial_ideas_or_unexecuted_specifications': classes.get('adversarial_or_unexecuted_spec', 0),
                    '5_test_implementations': len(layers['tests']),
                    '6_parametrized_test_instances': sum(e['parametrized_instance_count'] for e in layers['tests']),
                    '7_fixtures_and_input_vectors': len(layers['fixtures']),
                    '8_historical_execution_records': sum(1 for r in layers['crosswalk'] if r['tier'] == 'EXECUTION_EVIDENCE'),
                    '9_distinct_execution_identities': len(identities),
                    '10_historical_verdicts_verbatim': dict(sorted(verdicts.items()))},
                'scenario_classes_reported_separately': dict(sorted(classes.items())),
                'evidence_kinds': dict(sorted({k: sum(1 for e in ev if e['evidence_kind'] == k) for k in {e['evidence_kind'] for e in ev}}.items())),
                'release_scope_by_layer': {k: dict(sorted(v.items())) for k, v in sorted(scope.items())},
                'reason_codes_and_vocabularies_are_not_counted_as_normative_obligations': rules.get('reason_code_or_refusal_vocabulary', 0),
                'unresolved_accounting': manifest['unresolved_accounting']})
    return out


def render(root):
    manifest, layers = _load(root)
    files = {}
    for name, fn in (('catalogue-integrity-report', integrity), ('governance-coverage-report', coverage), ('denominator-report', denominators)):
        data = fn(manifest, layers)
        files[name + '.json'] = V.dump_file(data)
        files[name + '.md'] = to_md(data).encode('utf-8')
    return files


def to_md(data):
    lines = ['# %s' % data['report'], '', data['note'], '', 'Catalogue manifest: `%s` (registry %s%s)' % (
        data['catalogue_manifest_digest'], data['registry_version'], ', synthetic sample' if data['synthetic_sample'] else ''), '']
    lines.append('Source revisions:')
    for s in data['source_revisions']:
        lines.append('- %s: %s; %d raw records; inventory `%s`' % (s['set_id'], ', '.join('%s@%s' % (r['repo'], r['revision']) for r in s['repo_revisions']), s['raw_record_count'], s['inventory_sha256']))
    lines += ['', '```json']
    body = {k: v for k, v in data.items() if k not in ('report', 'note', 'catalogue_manifest_digest', 'registry_version', 'synthetic_sample', 'source_revisions')}
    import json
    lines.append(json.dumps(body, indent=1, sort_keys=True, ensure_ascii=False))
    lines.append('```')
    return '\n'.join(lines) + '\n'


def main(argv):
    args = list(argv)
    root, out, check = ROOT, None, False
    while args:
        a = args.pop(0)
        if a == '--root' and args:
            root = os.path.abspath(args.pop(0))
        elif a == '--out' and args:
            out = os.path.abspath(args.pop(0))
        elif a == '--check':
            check = True
        else:
            sys.stderr.write('usage: generate_reports.py [--root DIR] [--out DIR] [--check]\n')
            return 2
    out = out or os.path.join(root, 'reports', 'generated')
    files = render(root)
    if check:
        bad = [n for n, b in sorted(files.items()) if not os.path.exists(os.path.join(out, n)) or open(os.path.join(out, n), 'rb').read() != b]
        for n in bad:
            sys.stdout.write('STALE %s\n' % n)
        return 1 if bad else 0
    os.makedirs(out, exist_ok=True)
    for n, b in sorted(files.items()):
        with open(os.path.join(out, n), 'wb') as fh:
            fh.write(b)
    sys.stdout.write('wrote %d report files\n' % len(files))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
