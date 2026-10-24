"""Validator, generator, reports and loader of the layered informational catalogue.

Synthetic data only. Every test builds or copies the small sample into a temporary root, applies
one targeted defect and checks that the validator refuses it with the expected code.
Non-authorizing; nothing here executes a rule, a scenario or a test.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'docs/mvp-recovery/registry'
TOOLS = REG / 'tools'


def _load(name):
    spec = importlib.util.spec_from_file_location('t_' + name, TOOLS / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _load('validate_registry')
B = _load('build_registry')
S = _load('sample_data')
R = _load('generate_reports')
L = _load('load_partitions')


def codes(root, previous=None):
    errors, _ = V.validate(str(root), previous and str(previous))
    return {c for c, _ in errors}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'registry'
        self.root.mkdir()
        shutil.copytree(REG / 'schemas', self.root / 'schemas')
        self.dataset = S.sample_dataset()
        B.build(self.dataset, str(self.root), max_per=S.SAMPLE_MAX_PER_PARTITION)

    def parts(self, layer):
        m = V.read_json(str(self.root / 'manifest.json'))
        return [p['path'] for p in m['partitions'] if p['layer'] == layer]

    def edit(self, layer, fn, redigest=True, refresh=True):
        """Apply fn(records) to every partition of a layer; keep digests and hashes consistent unless told not to."""
        for rel in self.parts(layer):
            path = self.root / rel
            env = V.read_json(str(path))
            fn(env['records'])
            if redigest and layer != 'crosswalk':
                for r in env['records']:
                    r['digest'] = V.digest_of(r)
            path.write_bytes(V.dump_file(env))
        if refresh:
            B.refresh_manifest(str(self.root))

    def recover(self):
        """Re-derive the coverage partitions after a deliberate change to entries or links."""
        layers = {l: [r for rel in self.parts(l) for r in V.read_json(str(self.root / rel))['records']] for l in ('rules', 'scenarios', 'evidence')}
        rows = V.derive_coverage(layers['rules'], layers['scenarios'], {e['evidence_digest']: e['evidence_kind'] for e in layers['evidence']})
        def go(recs):
            recs[:] = [rows[r['subject_id']] for r in recs]
        self.edit('coverage', go, redigest=False)

    def entry(self, layer, cid):
        for rel in self.parts(layer):
            for r in V.read_json(str(self.root / rel))['records']:
                if r.get('catalogue_id') == cid or r.get('evidence_digest') == cid or r.get('subject_id') == cid:
                    return r
        raise KeyError(cid)

    def mutate(self, layer, cid, fn, **kw):
        def go(recs):
            for r in recs:
                if r.get('catalogue_id') == cid or r.get('evidence_digest') == cid or r.get('subject_id') == cid:
                    fn(r)
        self.edit(layer, go, **kw)


class Baseline(Base):
    def test_sample_validates(self):
        self.assertEqual(codes(self.root), set())

    def test_committed_registry_validates_and_is_reproducible(self):
        errors, manifest = V.validate(str(REG))
        self.assertEqual(errors, [])
        self.assertEqual(manifest['status'], 'HOLD')
        self.assertEqual(manifest['authority'], 'none')
        self.assertTrue(manifest['synthetic_sample'])
        out = Path(self.tmp.name) / 'rebuilt'
        out.mkdir()
        B.build(S.sample_dataset(), str(out), max_per=S.SAMPLE_MAX_PER_PARTITION)
        for p in sorted(out.rglob('*.json')):
            self.assertEqual(p.read_bytes(), (REG / p.relative_to(out)).read_bytes(), str(p))

    def test_committed_reports_current(self):
        self.assertEqual(R.main(['--root', str(REG), '--check']), 0)

    def test_rebuild_is_byte_identical(self):
        other = Path(self.tmp.name) / 'again'
        other.mkdir()
        B.build(S.sample_dataset(), str(other), max_per=S.SAMPLE_MAX_PER_PARTITION)
        a = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*.json') if 'schemas' not in p.parts}
        b = {str(p.relative_to(other)): p.read_bytes() for p in other.rglob('*.json')}
        self.assertEqual(a, b)

    def test_partitioned_not_one_giant_file(self):
        self.assertGreater(len(self.parts('crosswalk')), 1)
        self.assertTrue(all(p.startswith('rules/') for p in self.parts('rules')))

    def test_layer_counts_and_inventory(self):
        m = V.read_json(str(self.root / 'manifest.json'))
        self.assertEqual(m['layer_counts']['crosswalk'], sum(s['raw_record_count'] for s in m['source_inventory']))

    def test_validator_has_no_execution_surface(self):
        text = (TOOLS / 'validate_registry.py').read_text()
        for word in ('subprocess', 'socket', 'urllib', 'os.system', 'requests'):
            self.assertNotIn(word, text)

    def test_registry_record_contract_untouched_and_valid(self):
        rec = S.sample_dataset()['registry_records'][0]
        self.assertEqual(V.RR.validate_record(rec, floor_mandatory_rule_ids=[]), rec['digest'])
        self.assertEqual(set(rec), V.RR.RECORD_FIELDS)


class FailureModes(Base):
    def test_broken_reference(self):
        self.mutate('scenarios', 'S-SYN-case-1-00000001', lambda r: r['rule_refs'].append('R-SYN-nope-00000000'))
        self.assertIn('unresolved_reference', codes(self.root))

    def test_wrong_namespace_reference(self):
        self.mutate('scenarios', 'S-SYN-case-1-00000001', lambda r: r.__setitem__('test_refs', ['R-SYN-floor-a-00000001']))
        self.assertIn('unresolved_reference', codes(self.root))

    def test_duplicate_id(self):
        def dup(recs):
            recs.insert(1, copy.deepcopy(recs[0]))
        self.edit('rules', lambda recs: dup(recs) if recs[0]['catalogue_id'] == 'R-SYN-floor-a-00000001' else None)
        self.assertIn('duplicate_id', codes(self.root))

    def test_namespace_mismatch(self):
        self.mutate('fixtures', 'F-SYN-fixture-1-00000001', lambda r: r.__setitem__('catalogue_id', 'X-SYN-fixture-1'))
        self.assertIn('namespace_mismatch', codes(self.root))

    def test_changed_digest_detected(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r.__setitem__('title', 'changed'), redigest=False)
        self.assertIn('digest_mismatch', codes(self.root))

    def test_changed_partition_bytes_detected(self):
        rel = self.parts('rules')[0]
        p = self.root / rel
        env = V.read_json(str(p))
        env['records'][0]['title'] = 'edited after hashing'
        p.write_bytes(V.dump_file(env))
        self.assertIn('partition_hash_mismatch', codes(self.root))

    def test_manifest_tamper_detected(self):
        p = self.root / 'manifest.json'
        m = V.read_json(str(p))
        m['registry_version'] = '9.9.9'
        p.write_bytes(V.dump_file(m))
        self.assertIn('manifest_digest_mismatch', codes(self.root))

    def test_unlisted_partition(self):
        (self.root / 'rules' / 'EXTRA-0001.json').write_bytes(b'{}\n')
        self.assertIn('partition_unlisted', codes(self.root))

    def test_authority_promotion(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r.__setitem__('authority', 'granted'))
        self.assertIn('authority_promotion', codes(self.root))

    def test_non_authorizing_flag_cannot_be_dropped(self):
        self.mutate('scenarios', 'S-SYN-case-1-00000001', lambda r: r.__setitem__('non_authorizing', False))
        self.assertIn('authority_promotion', codes(self.root))

    def test_authority_hidden_in_annotations(self):
        self.mutate('tests', 'T-SYN-test-1-00000001', lambda r: r['annotations'].__setitem__('authority', 'full'))
        self.assertIn('authority_promotion', codes(self.root))

    def test_required_registry_rule_is_refused(self):
        rec_path = next((self.root / 'rules' / 'registry-records').glob('*.json'))
        rec = V.read_json(str(rec_path))
        rec['rule_table'][0]['status'] = 'required'
        rec['digest'] = V.digest_of(rec)
        rec_path.write_bytes(V.dump_file(rec))
        found = codes(self.root)
        self.assertTrue({'registry_record_refused', 'authority_promotion'} & found)

    def test_missing_crosswalk_row(self):
        def drop(recs):
            recs[:] = [r for r in recs if not (r['raw_set'] == 'SYN1' and r['raw_index'] == 5)]
        self.edit('crosswalk', drop)
        found = codes(self.root)
        self.assertIn('crosswalk_row_missing', found)

    def test_duplicate_crosswalk_row(self):
        def dup(recs):
            if recs and recs[0]['raw_set'] == 'SYN1' and recs[0]['raw_index'] == 0:
                recs.insert(1, copy.deepcopy(recs[0]))
        self.edit('crosswalk', dup)
        self.assertIn('crosswalk_duplicate_row', codes(self.root))

    def test_changed_raw_digest_breaks_inventory_commitment(self):
        def change(recs):
            for r in recs:
                if r['raw_set'] == 'SYN1' and r['raw_index'] == 11:
                    r['raw_digest'] = 'sha256:' + 'ab' * 32
        self.edit('crosswalk', change)
        self.assertIn('inventory_commitment_mismatch', codes(self.root))

    def test_link_not_bidirectional(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: (r['scenario_refs'].clear(), r['relationships'].clear()) if False else None)
        def unlink(r):
            r['rule_refs'].remove('R-SYN-floor-a-00000001')
            r['relationships'] = [x for x in r['relationships'] if x['to'] != 'R-SYN-floor-a-00000001']
        self.mutate('scenarios', 'S-SYN-case-1-00000001', unlink)
        self.assertIn('link_not_bidirectional', codes(self.root))

    def test_alias_dropped(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r.__setitem__('aliases', []))
        self.assertIn('alias_not_retained', codes(self.root))

    def test_merged_fixture_copy_keeps_alias_and_location(self):
        self.mutate('fixtures', 'F-SYN-fixture-1-00000001', lambda r: r.__setitem__('raw_refs', ['SYN1:9']))
        self.assertIn('raw_refs_mismatch', codes(self.root))

    def test_revision_dropped_from_lineage(self):
        self.mutate('rules', 'R-SYN-reg-b-00000002', lambda r: r.__setitem__('lineage', []))
        self.assertIn('revision_not_retained', codes(self.root))

    def test_historical_revision_overwritten_across_versions(self):
        prev = Path(self.tmp.name) / 'prev'
        shutil.copytree(self.root, prev)
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r.__setitem__('title', 'rewritten'))
        self.assertIn('historical_overwritten', codes(self.root, prev))
        # retaining the earlier digest in lineage is the accepted way to revise
        def keep(r):
            r['lineage'].append({'revision_id': 'earlier', 'raw_ref': 'SYN1:0', 'digest': self.entry_prev(prev), 'relation': 'HISTORICAL_REVISION'})
        self.mutate('rules', 'R-SYN-floor-a-00000001', keep)
        self.assertNotIn('historical_overwritten', codes(self.root, prev))

    def entry_prev(self, prev):
        for rel in V.read_json(str(prev / 'manifest.json'))['partitions']:
            if rel['layer'] == 'rules':
                for r in V.read_json(str(prev / rel['path']))['records']:
                    if r['catalogue_id'] == 'R-SYN-floor-a-00000001':
                        return r['digest']

    def test_entry_removed_since_previous(self):
        prev = Path(self.tmp.name) / 'prev'
        shutil.copytree(self.root, prev)
        self.edit('fixtures', lambda recs: recs.clear())
        self.assertIn('historical_removed', codes(self.root, prev))

    def test_mvp_applicability_must_be_classified(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r['mvp_applicability'].__setitem__('value', 'probably'))
        self.assertIn('record_schema', codes(self.root))
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r['mvp_applicability'].update(value='unresolved', reason=''))
        self.assertIn('record_schema', codes(self.root))

    def test_all_six_mvp_values_accepted(self):
        for i, v in enumerate(['mvp_fixed', 'other_supported_historical_profile', 'requires_unavailable_component', 'needs_migration', 'historical_only', 'unresolved']):
            self.mutate('fixtures', 'F-SYN-fixture-1-00000001', lambda r, v=v: r['mvp_applicability'].update(value=v))
            self.assertNotIn('record_schema', codes(self.root))

    def test_execution_evidence_cannot_be_a_rule(self):
        def promote(recs):
            for r in recs:
                if r['raw_set'] == 'SYN2' and r['raw_index'] == 0:
                    r['disposition'] = 'CANONICAL'
                    r['target'] = 'R-SYN-floor-a-00000001'
        self.edit('crosswalk', promote)
        self.assertTrue({'evidence_as_rule', 'crosswalk_tier_mismatch'} & codes(self.root))

    def test_verdict_field_in_rule_layer_refused(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r.__setitem__('historical_verdict_verbatim', 'PASS'))
        self.assertTrue({'record_schema', 'evidence_as_rule'} & codes(self.root))

    def test_evidence_keeps_source_and_artifact_commitments(self):
        e = self.dataset['evidence'][0]['evidence_digest']
        self.mutate('evidence', e, lambda r: r['source_commitment'].__setitem__('set_id', 'NOT-COMMITTED'))
        self.assertIn('evidence_commitment_missing', codes(self.root))
        self.mutate('evidence', e, lambda r: r['source_commitment'].__setitem__('set_id', 'SYN1'))
        self.mutate('evidence', e, lambda r: r['artifact_commitment'].__setitem__('path', ''))
        self.assertIn('record_schema', codes(self.root))

    def test_historical_verdict_has_no_current_effect(self):
        e = self.dataset['evidence'][0]['evidence_digest']
        self.mutate('evidence', e, lambda r: r.__setitem__('current_qualification_effect', 'qualified'))
        self.assertIn('record_schema', codes(self.root))

    def test_layer_count_mismatch(self):
        p = self.root / 'manifest.json'
        m = V.read_json(str(p))
        m['layer_counts']['rules'] += 1
        m['digest'] = V.digest_of(m)
        p.write_bytes(V.dump_file(m))
        self.assertIn('layer_count_mismatch', codes(self.root))

    def test_registry_rule_digest_pinned(self):
        self.mutate('rules', 'R-SYN-reg-b-00000002', lambda r: r['rule_ref'].__setitem__('rule_digest', 'sha256:' + '1' * 64))
        self.assertIn('rule_digest_mismatch', codes(self.root))

    def test_floor_only_for_adopted_cr_identities(self):
        self.mutate('rules', 'R-SYN-reason-c-00000003', lambda r: r.__setitem__('normative_type', 'constitutional_floor'))
        self.assertIn('floor_misclassified', codes(self.root))
        self.mutate('rules', 'R-SYN-reason-c-00000003', lambda r: r.update(normative_type='constitutional_floor', adoption_status='adopted', native_ids=['CR-007']))
        self.assertNotIn('floor_misclassified', codes(self.root))


class ProvenanceAndAssessments(Base):
    def test_every_reference_needs_a_relationship_record(self):
        self.mutate('scenarios', 'S-SYN-case-1-00000001', lambda r: r.__setitem__('relationships', []))
        self.assertIn('relationship_missing', codes(self.root))

    def test_orphan_relationship(self):
        def add(r):
            rel = copy.deepcopy(r['relationships'][0])
            rel['to'] = 'T-SYN-ghost-00000000'
            rel['field'] = 'test_refs'
            r['relationships'].append(rel)
        self.mutate('scenarios', 'S-SYN-case-1-00000001', add)
        self.assertIn('relationship_orphan', codes(self.root))

    def test_source_stated_needs_exact_source(self):
        self.mutate('scenarios', 'S-SYN-case-1-00000001', lambda r: r['relationships'][0].__setitem__('source', None))
        self.assertIn('relationship_provenance', codes(self.root))

    def test_derived_cannot_masquerade_as_source_stated(self):
        def disguise(r):
            for rel in r['relationships']:
                if rel['provenance'] == 'DERIVED':
                    rel['provenance'] = 'SOURCE_STATED'
        self.mutate('rules', 'R-SYN-floor-a-00000001', disguise)
        self.assertIn('relationship_provenance', codes(self.root))

    def test_derived_needs_method_support_and_confidence(self):
        def strip(r):
            for rel in r['relationships']:
                if rel['provenance'] == 'DERIVED':
                    rel['method'] = None
        self.mutate('rules', 'R-SYN-floor-a-00000001', strip)
        self.assertIn('relationship_provenance', codes(self.root))

    def test_relationship_flags_always_false(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r['relationships'][0].__setitem__('establishes_test_coverage', True))
        self.assertIn('record_schema', codes(self.root))

    def test_unresolved_cannot_silently_become_established(self):
        def promote(r):
            for rel in r['relationships']:
                if rel['to'].startswith('UNRESOLVED:'):
                    rel.update(provenance='SOURCE_STATED', missing_evidence=None,
                               source={'repo': 'r', 'revision': 'v', 'location': 'l'})
        self.mutate('tests', 'T-SYN-test-1-00000001', promote)
        self.assertIn('unresolved_promoted', codes(self.root))

    def test_unresolved_must_name_missing_evidence(self):
        def blank(r):
            for rel in r['relationships']:
                if rel['provenance'] == 'UNRESOLVED':
                    rel['missing_evidence'] = ' '
        self.mutate('tests', 'T-SYN-test-1-00000001', blank)
        self.assertIn('relationship_provenance', codes(self.root))

    def test_unresolved_cannot_vanish_from_accounting(self):
        def drop(r):
            r['scenario_refs'] = [x for x in r['scenario_refs'] if not x.startswith('UNRESOLVED:')]
            r['relationships'] = [x for x in r['relationships'] if not x['to'].startswith('UNRESOLVED:')]
        self.mutate('tests', 'T-SYN-test-1-00000001', drop)
        self.assertIn('unresolved_accounting_mismatch', codes(self.root))

    def test_unresolved_crosswalk_row_cannot_be_relabelled(self):
        def relabel(recs):
            for r in recs:
                if r['raw_set'] == 'SYN1' and r['raw_index'] == 12:
                    r.update(disposition='SOURCE_ONLY_ARTIFACT', unresolved_reason=None, tier='RULE_ADJACENT')
        self.edit('crosswalk', relabel)
        self.assertIn('unresolved_accounting_mismatch', codes(self.root))

    def test_coverage_assessments_are_separate(self):
        rows = {r['subject_id']: r for r in S_rows(self.root, self)}
        a = rows['R-SYN-floor-a-00000001']['assessments']
        self.assertEqual(a['implementation_coverage']['status'], 'derived_candidate_only')
        self.assertEqual(a['test_coverage']['status'], 'none')
        self.assertEqual(a['independent_qualification']['status'], 'none')
        self.assertNotIn('implemented', rows['R-SYN-floor-a-00000001']['states'])
        c1 = rows['S-SYN-case-1-00000001']
        self.assertIn('implemented', c1['states'])
        self.assertIn('tested', c1['states'])
        self.assertNotIn('independently_qualified', c1['states'])
        self.assertEqual(c1['assessments']['independent_qualification']['status'], 'none')
        self.assertEqual('has_unresolved', rows['S-SYN-suite-1-00000003']['assessments']['catalogue_completeness']['status'])
        self.assertEqual('complete', rows['S-SYN-case-2-00000002']['assessments']['catalogue_completeness']['status'])
        self.assertIn('excluded_or_unsupported', rows['S-SYN-case-2-00000002']['states'])

    def test_derived_link_cannot_be_reported_as_qualified_or_tested(self):
        # make the scenario's evidence link DERIVED, then try to forge coverage that claims more
        def derive(r):
            for rel in r['relationships']:
                if rel['field'] == 'evidence_digest_refs':
                    rel.update(provenance='DERIVED', source=None, method='run id grouping', supporting_refs=['SYN1:10'], confidence_class='medium')
        self.mutate('scenarios', 'S-SYN-case-1-00000001', derive)
        self.recover()
        self.assertEqual(codes(self.root), set())
        row = {r['subject_id']: r for r in S_rows(self.root, self)}['S-SYN-case-1-00000001']
        self.assertEqual(row['assessments']['test_coverage']['status'], 'derived_candidate_only')
        self.assertNotIn('tested', row['states'])
        def forge(r):
            r['states'] = ['defined', 'implemented', 'tested', 'independently_qualified']
            r['assessments']['independent_qualification'] = {'status': 'source_stated_record', 'basis_refs': ['x']}
        self.mutate('coverage', 'S-SYN-case-1-00000001', forge)
        self.assertIn('coverage_inferred', codes(self.root))

    def test_historical_pass_does_not_transfer(self):
        ev = self.dataset['evidence'][0]['evidence_digest']
        self.mutate('evidence', ev, lambda r: r.__setitem__('historical_verdict_verbatim', 'PASS'))
        self.assertEqual(codes(self.root), set())
        row = {r['subject_id']: r for r in S_rows(self.root, self)}['S-SYN-case-1-00000001']
        self.assertEqual(row['assessments']['independent_qualification']['status'], 'none')
        def forge(r):
            r['states'] = r['states'] + ['independently_qualified']
        self.mutate('coverage', 'S-SYN-case-1-00000001', forge)
        self.assertIn('coverage_inferred', codes(self.root))

    def test_validation_claim_is_not_a_run_result(self):
        # a validation claim linked from a scenario never counts as tested
        claim = self.dataset['evidence'][1]['evidence_digest']
        def link(r):
            r['evidence_digest_refs'] = [claim]
            r['relationships'] = [x for x in r['relationships'] if x['field'] != 'evidence_digest_refs']
            rel = copy.deepcopy(r['relationships'][0])
            rel.update(field='evidence_digest_refs', to=claim)
            r['relationships'].append(rel)
        self.mutate('scenarios', 'S-SYN-case-1-00000001', link)
        self.recover()
        self.assertEqual(codes(self.root), set())
        row = {r['subject_id']: r for r in S_rows(self.root, self)}['S-SYN-case-1-00000001']
        self.assertNotIn('tested', row['states'])

    def test_coverage_row_missing_or_extra(self):
        self.edit('coverage', lambda recs: recs.pop(0))
        self.assertIn('coverage_missing', codes(self.root))


def S_rows(root, case):
    return [r for rel in case.parts('coverage') for r in V.read_json(str(root / rel))['records']]


class Denominators(Base):
    def report(self):
        manifest, layers = R._load(str(self.root))
        return R.denominators(manifest, layers)

    def test_separate_denominators_no_headline(self):
        d = self.report()
        den = d['denominators']
        self.assertEqual(den['2_logical_governance_scenarios'], 2)
        self.assertEqual(den['3_suite_level_acceptance_scenarios'], 1)
        self.assertEqual(den['4_adversarial_ideas_or_unexecuted_specifications'], 1)
        self.assertEqual(len(self.dataset['scenarios']), 4)
        self.assertEqual(len(den), 10)
        self.assertFalse([k for k in d if 'total' in k or k == 'scenario_count'])
        self.assertIn('none by design', d['headline_scenario_count'])

    def test_suite_level_rows_do_not_inflate_logical_total(self):
        self.mutate('scenarios', 'S-SYN-suite-1-00000003', lambda r: r.__setitem__('scenario_class', 'logical'))
        self.assertEqual(self.report()['denominators']['2_logical_governance_scenarios'], 3)
        self.mutate('scenarios', 'S-SYN-suite-1-00000003', lambda r: r.__setitem__('scenario_class', 'suite_level_acceptance'))
        self.assertEqual(self.report()['denominators']['2_logical_governance_scenarios'], 2)

    def test_instances_and_repeated_runs_do_not_inflate_unique_counts(self):
        den = self.report()['denominators']
        self.assertEqual(den['5_test_implementations'], 1)
        self.assertEqual(den['6_parametrized_test_instances'], 2)
        self.assertEqual(den['8_historical_execution_records'], 2)
        self.assertEqual(den['9_distinct_execution_identities'], 1)
        self.assertEqual(den['2_logical_governance_scenarios'], 2)

    def test_reason_codes_distinct_from_normative_rules(self):
        by_type = self.report()['denominators']['1_canonical_rules_by_normative_type']
        self.assertEqual(by_type['reason_code_or_refusal_vocabulary'], 1)
        self.assertEqual(by_type['mandatory'], 1)

    def test_reports_name_manifest_and_source_revisions(self):
        files = R.render(str(self.root))
        manifest = V.read_json(str(self.root / 'manifest.json'))
        self.assertEqual(sorted(files), ['catalogue-integrity-report.json', 'catalogue-integrity-report.md', 'denominator-report.json',
                                         'denominator-report.md', 'governance-coverage-report.json', 'governance-coverage-report.md'])
        for name, data in files.items():
            text = data.decode()
            self.assertIn(manifest['digest'], text)
            self.assertIn(S.REV, text)
        integ = json.loads(files['catalogue-integrity-report.json'])
        self.assertEqual(integ['unresolved_accounting'], manifest['unresolved_accounting'])
        self.assertIn('SYN1', integ['by_partition_raw_set'])

    def test_reports_refuse_an_invalid_catalogue(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r.__setitem__('authority', 'granted'))
        with self.assertRaises(SystemExit):
            R.render(str(self.root))

    def test_report_generation_is_deterministic(self):
        self.assertEqual(R.render(str(self.root)), R.render(str(self.root)))


class Loader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name) / 'out'
        d = self.base / 'Z'
        (d / 'parts').mkdir(parents=True)
        dg = 'ab' * 32
        entries = {'rules': [{'canonical_id': 'R-Z-a-1', 'source_repo': 'o/r', 'source_revision': 'f' * 40, 'path': 'a.md', 'native_ids': ['A'],
                              'aliases': [], 'classification': 'mandatory', 'test_refs': ['T-Z-t-1'], 'evidence_digest_refs': [dg],
                              'mvp_applicability': 'unresolved', 'owner': None}],
                   'logical_scenarios': [], 'fixtures': [],
                   'test_implementations': [{'canonical_id': 'T-Z-t-1', 'source_repo': 'o/r', 'path': 't.py', 'native_ids': ['t.py::t'],
                                             'associated_scenarios': ['UNRESOLVED:none:t']}]}
        (d / 'parts' / 'L1.json').write_text(json.dumps({'entries': entries['rules']}))
        (d / 'parts' / 'L3.json').write_text(json.dumps({'entries': entries['test_implementations']}))
        (d / 'Z.canonical.json').write_text(json.dumps({'rules': [{'file': 'parts/L1.json'}], 'logical_scenarios': [], 'fixtures': [],
                                                        'test_implementations': [{'file': 'parts/L3.json'}], 'layout': 'p'}))
        rows = [{'raw_index': 0, 'raw_digest': 'c' * 64, 'source_repo': 'o/r', 'path': 'a.md', 'native_id': 'A', 'tier': 'GOVERNANCE_RULE', 'disposition': 'CANONICAL:R-Z-a-1'},
                {'raw_index': 1, 'raw_digest': 'd' * 64, 'source_repo': 'o/r', 'path': 't.py', 'native_id': 't.py::t', 'tier': 'TEST_IMPLEMENTATION', 'disposition': 'CANONICAL', 'target': 'T-Z-t-1'},
                {'raw_index': 2, 'raw_digest': 'e' * 64, 'source_repo': 'o/r', 'path': 't.py', 'native_id': 't.py::t[1]', 'tier': 'PARAMETRIZED_INSTANCE', 'disposition': 'ATTACHED_TO:T-Z-t-1'},
                {'raw_index': 3, 'raw_digest': dg, 'source_repo': 'o/r', 'path': 'run.json', 'native_id': None, 'tier': 'EXECUTION_EVIDENCE', 'disposition': 'EVIDENCE_INDEXED:' + dg},
                {'raw_index': 4, 'raw_digest': '1' * 64, 'source_repo': 'o/r', 'path': 'x.md', 'native_id': None, 'tier': 'RULE_ADJACENT', 'disposition': 'SOURCE_REFERENCE_ONLY'},
                {'raw_index': 5, 'raw_digest': '2' * 64, 'source_repo': 'o/r', 'path': 'x.md', 'native_id': None, 'tier': 'LOGICAL_SCENARIO', 'disposition': 'UNRESOLVED:no identity'}]
        (d / 'Z.crosswalk.json').write_text(json.dumps({'rows': rows}))
        (d / 'Z.evidence-index.json').write_text(json.dumps({'entries': [{'digest': dg, 'evidence_kind': 'recorded_execution_result',
                                                                          'raw_result_and_original_verdict': 'XFAIL',
                                                                          'artifact_location_and_digest': {'path': 'run.json', 'record_digest_sha256': dg, 'file_digest': 'not computed'}}]}))

    def load(self, overlays=()):
        ds = L.assemble(str(self.base), ['Z'], overlays)
        out = Path(self.tmp.name) / 'reg'
        shutil.copytree(REG / 'schemas', out / 'schemas')
        B.build(ds, str(out))
        return ds, out

    def test_loads_and_validates(self):
        ds, out = self.load()
        self.assertEqual(codes(out), set())
        rule = ds['rules'][0]
        self.assertEqual(rule['normative_type'], 'mandatory')
        self.assertEqual(rule['mvp_applicability']['value'], 'unresolved')
        self.assertEqual(ds['tests'][0]['parametrized_instance_count'], 1)
        self.assertEqual(ds['evidence'][0]['historical_verdict_verbatim'], 'XFAIL')

    def test_links_without_provenance_load_as_unresolved_never_established(self):
        ds, out = self.load()
        for rel in ds['rules'][0]['relationships']:
            self.assertEqual(rel['provenance'], 'UNRESOLVED')
            self.assertFalse(rel['establishes_test_coverage'])
        cov = {r['subject_id']: r for r in S_rows(out, type('X', (), {'parts': lambda s, l: [p['path'] for p in V.read_json(str(out / 'manifest.json'))['partitions'] if p['layer'] == l]})())}
        self.assertEqual(cov['R-Z-a-1']['assessments']['implementation_coverage']['status'], 'none')

    def test_overlay_relationship_and_attributes(self):
        d = Path(self.tmp.name) / 'ov'
        d.mkdir()
        (d / 'g2.json').write_text(json.dumps({'overlay': 'attributes', 'items': {'R-Z-a-1': {'normative_type': 'principle', 'release_scope': 'v0_1'}}}))
        (d / 'g3.json').write_text(json.dumps({'overlay': 'relationships', 'items': [{'owner': 'R-Z-a-1', 'field': 'test_refs', 'to': 'T-Z-t-1', 'provenance': 'DERIVED',
                                                                                      'method': 'exact-id match', 'supporting_refs': ['T-Z-t-1'], 'confidence_class': 'high'}]}))
        ds, out = self.load([('attributes', str(d / 'g2.json')), ('relationships', str(d / 'g3.json'))])
        self.assertEqual(ds['rules'][0]['normative_type'], 'principle')
        self.assertEqual(codes(out), set())

    def test_merge_needs_basis(self):
        d = Path(self.tmp.name) / 'ov'
        d.mkdir()
        (d / 'g1.json').write_text(json.dumps({'overlay': 'identity', 'merges': [{'into': 'R-Z-a-1', 'from': [], 'basis': ''}]}))
        with self.assertRaises(L.LoadRefusal):
            L.assemble(str(self.base), ['Z'], [('identity', str(d / 'g1.json'))])

    def test_same_id_different_identity_refused(self):
        shutil.copytree(self.base / 'Z', self.base / 'Y')
        for fn in ('canonical', 'crosswalk', 'evidence-index'):
            (self.base / 'Y' / ('Z.%s.json' % fn)).rename(self.base / 'Y' / ('Y.%s.json' % fn))
        p = json.loads((self.base / 'Y' / 'parts' / 'L1.json').read_text())
        p['entries'][0]['path'] = 'other.md'
        (self.base / 'Y' / 'parts' / 'L1.json').write_text(json.dumps(p))
        with self.assertRaises(L.LoadRefusal):
            L.assemble(str(self.base), ['Z', 'Y'])


if __name__ == '__main__':
    unittest.main()
