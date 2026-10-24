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
        self.assertEqual(den['2_logical_governance_scenarios']['v0_1'] + den['2_logical_governance_scenarios']['release_scope_not_stated'], 2)
        self.assertEqual(den['3_suite_level_acceptance_scenarios'], 1)
        self.assertEqual(den['4_adversarial_ideas_or_unexecuted_specifications']['category_not_stated'], 1)
        self.assertEqual(len(self.dataset['scenarios']), 5)
        self.assertEqual(len(den), 10)
        self.assertFalse([k for k in d if 'total' in k or k == 'scenario_count'])
        self.assertIn('none by design', d['headline_scenario_count'])

    def test_suite_level_rows_do_not_inflate_logical_total(self):
        self.mutate('scenarios', 'S-SYN-suite-1-00000003', lambda r: r.__setitem__('scenario_class', 'logical'))
        self.assertEqual(self.report()['denominators']['2_logical_governance_scenarios']['v0_1'], 3)
        self.mutate('scenarios', 'S-SYN-suite-1-00000003', lambda r: r.__setitem__('scenario_class', 'suite_level_acceptance'))
        self.assertEqual(self.report()['denominators']['2_logical_governance_scenarios']['v0_1'], 2)

    def test_instances_and_repeated_runs_do_not_inflate_unique_counts(self):
        den = self.report()['denominators']
        self.assertEqual(den['5_test_implementations'], 1)
        self.assertEqual(den['6_parametrized_test_instances'], 2)
        self.assertEqual(den['8_historical_execution_records'], 2)
        self.assertEqual(den['9_distinct_execution_identities']['distinct_run_and_test_node_pairs'], 1)
        self.assertEqual(den['9_distinct_execution_identities']['distinct_runs'], 1)
        self.assertEqual(den['2_logical_governance_scenarios']['v0_1'], 2)

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
                {'raw_index': 2, 'raw_digest': 'e' * 64, 'source_repo': 'o/r', 'path': 't.py', 'native_id': 't.py::t[1]', 'tier': 'PARAMETRIZED_INSTANCE', 'disposition': 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE:T-Z-t-1'},
                {'raw_index': 3, 'raw_digest': dg, 'source_repo': 'o/r', 'path': 'run.json', 'native_id': None, 'tier': 'EXECUTION_EVIDENCE', 'disposition': 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE:' + dg},
                {'raw_index': 4, 'raw_digest': '1' * 64, 'source_repo': 'o/r', 'path': 'x.md', 'native_id': None, 'tier': 'RULE_ADJACENT', 'disposition': 'SOURCE_ONLY_ARTIFACT'},
                {'raw_index': 5, 'raw_digest': '2' * 64, 'source_repo': 'o/r', 'path': 'x.md', 'native_id': None, 'tier': 'LOGICAL_SCENARIO', 'disposition': 'UNRESOLVED(no identity)'}]
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



def _rewrite_manifest(root, fn):
    path = Path(root) / 'manifest.json'
    m = V.read_json(str(path))
    fn(m)
    m['digest'] = V.digest_of(m)
    path.write_bytes(V.dump_file(m))


class ReviewFixes(Base):
    """Regression tests for the independent review of the first tooling revision: each fails on the old behaviour."""

    def _crosswalk_row(self, fn_pick):
        rel = next(p for p in self.parts('crosswalk'))
        return rel

    # HIGH 1: canonical-tier records cannot silently become source-only
    def test_canonical_tier_cannot_be_source_only(self):
        def go(recs):
            for r in recs:
                if r['raw_set'] == 'SYN1' and r['raw_index'] == 0:
                    r['disposition'], r['target'] = 'SOURCE_ONLY_ARTIFACT', None
        self.edit('crosswalk', go, redigest=False)
        self.assertIn('crosswalk_tier_mismatch', codes(self.root))

    def test_non_canonical_tier_may_be_source_only(self):
        self.assertEqual(codes(self.root), set())  # the sample already carries a RULE_ADJACENT source-only row

    def test_fixture_tier_cannot_be_source_only_either(self):
        def go(recs):
            for r in recs:
                if r['raw_set'] == 'SYN1' and r['raw_index'] == 9:
                    r['disposition'], r['target'] = 'SOURCE_ONLY_ARTIFACT', None
        self.edit('crosswalk', go, redigest=False)
        self.assertIn('crosswalk_tier_mismatch', codes(self.root))

    # HIGH 2: the schemas are pinned
    def test_weakened_schema_is_refused(self):
        path = self.root / 'schemas' / 'evidence.schema.json'
        sch = json.loads(path.read_text())
        sch['$defs']['relationship']['properties']['establishes_enforcement'] = {'type': 'boolean'}
        path.write_text(json.dumps(sch, indent=2) + '\n')
        self.assertIn('schema_not_pinned', codes(self.root))

    def test_schema_pin_removed_from_manifest_is_refused(self):
        _rewrite_manifest(self.root, lambda m: m.__setitem__('schema_files', {}))
        self.assertIn('schema_not_pinned', codes(self.root))

    def test_repinned_but_weakened_schema_differs_from_the_validators_own_copy(self):
        path = self.root / 'schemas' / 'rules.schema.json'
        sch = json.loads(path.read_text())
        sch['properties']['normative_type'] = {'type': 'string'}
        path.write_text(json.dumps(sch, indent=2) + '\n')
        _rewrite_manifest(self.root, lambda m: m.__setitem__('schema_files', B.schema_pins(str(self.root))))
        self.assertIn('schema_not_pinned', codes(self.root))

    def test_mvp_applicability_value_is_enumerated_everywhere(self):
        for name in ('rules', 'scenarios', 'tests', 'fixtures', 'evidence', 'lineage_sets'):
            sch = json.loads((REG / 'schemas' / (name + '.schema.json')).read_text())
            self.assertIn('enum', sch['$defs']['mvp_applicability']['properties']['value'], name)

    # MEDIUM 3: alias candidates get the full relationship checks
    def _alias_pair(self):
        return 'R-SYN-floor-a-00000001', 'R-SYN-reason-c-00000003'

    def test_alias_candidates_baseline_is_valid(self):
        a, b = self._alias_pair()
        self.assertEqual(self.entry('rules', a)['alias_candidates'], [b])
        self.assertEqual(codes(self.root), set())

    def test_alias_candidate_needs_its_provenance_record(self):
        a, b = self._alias_pair()
        self.mutate('rules', a, lambda r: r['relationships'].__setitem__(slice(None), [x for x in r['relationships'] if x['field'] != 'alias_candidates']))
        self.assertIn('relationship_missing', codes(self.root))

    def test_alias_candidate_relationship_without_reference_is_orphan(self):
        a, b = self._alias_pair()
        self.mutate('rules', a, lambda r: r.__setitem__('alias_candidates', []))
        self.assertIn('relationship_orphan', codes(self.root))

    def test_alias_candidate_source_stated_needs_source(self):
        a, b = self._alias_pair()
        def go(r):
            for x in r['relationships']:
                if x['field'] == 'alias_candidates':
                    x.update(provenance='SOURCE_STATED', source=None, method=None, supporting_refs=[], confidence_class=None)
        self.mutate('rules', a, go)
        self.assertIn('relationship_provenance', codes(self.root))

    def test_alias_candidate_target_must_resolve_in_the_same_layer(self):
        a, b = self._alias_pair()
        def go(r):
            r['alias_candidates'] = ['S-SYN-case-1-00000001']
            for x in r['relationships']:
                if x['field'] == 'alias_candidates':
                    x['to'] = 'S-SYN-case-1-00000001'
        self.mutate('rules', a, go)
        self.assertIn('unresolved_reference', codes(self.root))

    def test_alias_candidate_flag_cannot_be_flipped(self):
        a, b = self._alias_pair()
        def go(r):
            for x in r['relationships']:
                if x['field'] == 'alias_candidates':
                    x['establishes_qualification'] = True
        self.mutate('rules', a, go)
        self.assertIn('relationship_provenance', codes(self.root))
        self.assertIn('record_schema', codes(self.root))

    # MEDIUM 4: unrecorded commitments are refused or counted, never silent
    def test_unrecorded_artifact_path_is_refused(self):
        self.mutate('evidence', V.canonical_digest({'synthetic_raw_record': 'evidence-2'}),
                    lambda r: r['artifact_commitment'].__setitem__('path', 'unrecorded'))
        self.assertIn('evidence_commitment_missing', codes(self.root))

    def test_source_stated_link_with_unrecorded_revision_is_refused(self):
        def go(r):
            for x in r['relationships']:
                if x['provenance'] == 'SOURCE_STATED':
                    x['source']['revision'] = 'unrecorded'
        self.mutate('scenarios', 'S-SYN-case-1-00000001', go)
        self.assertIn('relationship_provenance', codes(self.root))

    def test_unrecorded_evidence_revisions_are_counted_in_the_manifest(self):
        ds = S.sample_dataset()
        ds['evidence'][1]['source_commitment']['revision'] = 'unrecorded'
        out = Path(self.tmp.name) / 'unrec'
        out.mkdir()
        shutil.copytree(REG / 'schemas', out / 'schemas')
        m = B.build(ds, str(out), max_per=S.SAMPLE_MAX_PER_PARTITION)
        self.assertEqual(m['unresolved_accounting']['evidence_unrecorded_source_revisions'], 1)
        self.assertEqual(codes(out), set())

    # MEDIUM 6: manifest record paths stay inside the registry
    def test_registry_record_path_cannot_leave_the_root(self):
        _rewrite_manifest(self.root, lambda m: m['registry_records'][0].__setitem__('path', '../outside.json'))
        self.assertIn('registry_record_unreadable', codes(self.root))

    # LOW 10: forbidden annotation keys are matched case-insensitively and broadly
    def test_forbidden_annotation_keys_are_broad(self):
        for key in ('Authority', 'QualificationStatus', 'verdict', 'cert' + 'ified_by', 'Approved_by', 'release_status', 'authorised'):
            self.setUp()
            self.mutate('tests', 'T-SYN-test-1-00000001', lambda r, key=key: r['annotations'].__setitem__(key, 'x'))
            self.assertIn('authority_promotion', codes(self.root), key)

    def test_descriptive_source_keys_are_allowed(self):
        self.mutate('tests', 'T-SYN-test-1-00000001', lambda r: r['annotations'].__setitem__('evaluator_qualification_note', 'unqualified: catalogue entry only; no evaluator'))
        self.assertEqual(codes(self.root), set())

    # LOW 11: a trailing newline does not satisfy a digest pattern
    def test_digest_with_trailing_newline_is_refused(self):
        d = V.canonical_digest({'synthetic_raw_record': 'evidence-2'})
        self.mutate('evidence', d, lambda r: r['artifact_commitment'].__setitem__('record_digest', d + '\n'))
        self.assertIn('record_schema', codes(self.root))

    # LOW 12: duplicate targets in a reference list
    def test_duplicate_reference_targets_are_refused(self):
        self.mutate('scenarios', 'S-SYN-case-1-00000001', lambda r: r['rule_refs'].append(r['rule_refs'][0]))
        self.assertIn('duplicate_ref', codes(self.root))

    # LOW 13: identifiers are printable ASCII without whitespace
    def test_identifier_forms(self):
        for bad in ('R-SYN-floor-a-00000001 ', ' R-SYN-floor-a-00000001', 'R-SYN-floör-a'):
            self.setUp()
            self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r, bad=bad: r.__setitem__('catalogue_id', bad))
            self.assertIn('id_form', codes(self.root), repr(bad))

    # LOW 9: a non-unresolved applicability value needs a basis that names a source
    def test_mvp_value_without_basis_is_refused(self):
        def go(r):
            r['mvp_applicability'].pop('basis_id', None)
        self.mutate('rules', 'R-SYN-reg-b-00000002', go)
        self.assertIn('mvp_basis_missing', codes(self.root))

    def test_mvp_value_without_source_reference_is_refused(self):
        self.mutate('rules', 'R-SYN-reg-b-00000002', lambda r: r['mvp_applicability'].pop('source_ref', None))
        self.assertIn('mvp_basis_missing', codes(self.root))

    # MEDIUM 7 (validator side): a merge keeps the merged id as an alias and states its basis
    def test_merge_without_basis_is_refused(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r['annotations'].__setitem__('merged_from', [{'id': 'SYN-A-legacy', 'basis': ' '}]))
        self.assertIn('merge_basis_missing', codes(self.root))

    def test_merge_must_retain_the_merged_id(self):
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r['annotations'].__setitem__('merged_from', [{'id': 'R-SYN-gone-00000000', 'basis': 'stated'}]))
        self.assertIn('merge_basis_missing', codes(self.root))

    # MEDIUM 8: lineage and --previous
    def test_lineage_must_point_at_a_crosswalk_row(self):
        def go(r):
            r['lineage'][0]['raw_ref'] = 'SYN1:99'
        self.mutate('rules', 'R-SYN-reg-b-00000002', go)
        self.assertIn('lineage_without_crosswalk_row', codes(self.root))

    def _previous(self):
        prev = Path(self.tmp.name) / 'previous'
        shutil.copytree(self.root, prev)
        return prev

    def test_previous_attribute_change_needs_a_recorded_transition(self):
        prev = self._previous()
        self.mutate('scenarios', 'S-SYN-case-1-00000001', lambda r: r.__setitem__('scenario_class', 'other'))
        self.assertIn('attribute_changed_without_transition', codes(self.root, prev))

    def test_previous_attribute_change_with_a_transition_is_allowed(self):
        prev = self._previous()
        before = self.entry('scenarios', 'S-SYN-case-1-00000001')['digest']
        def go(r):
            r['scenario_class'] = 'other'
            r['annotations']['attribute_transitions'] = [{'field': 'scenario_class', 'from': 'logical', 'to': 'other', 'previous_digest': before,
                                                          'basis': 'reclassified by a stated ruling'}]
        self.mutate('scenarios', 'S-SYN-case-1-00000001', go)
        self.assertEqual(codes(self.root, prev), set())

    def test_previous_registry_must_itself_validate(self):
        prev = self._previous()
        m = V.read_json(str(prev / 'manifest.json'))
        path = prev / next(p['path'] for p in m['partitions'] if p['layer'] == 'rules')
        env = V.read_json(str(path))
        env['records'].append(dict(env['records'][0]))
        path.write_bytes(V.dump_file(env))
        self.assertIn('previous_invalid', codes(self.root, prev))

    def test_previous_unchanged_is_clean(self):
        self.assertEqual(codes(self.root, self._previous()), set())


class SampleCoversNewShapes(Base):
    def test_lineage_set_is_validated_and_needs_its_rows(self):
        self.assertEqual(self.entry('lineage_sets', 'L-SYN-log-00000001')['tier'], 'LINEAGE_SET')
        def go(recs):
            for r in recs:
                if r['raw_set'] == 'SYN2' and r['raw_index'] == 2:
                    r['target'] = 'F-SYN-fixture-1-00000001'
        self.edit('crosswalk', go, redigest=False)
        self.assertTrue(codes(self.root) & {'crosswalk_tier_mismatch', 'revision_not_retained', 'raw_refs_mismatch', 'lineage_without_crosswalk_row'})

    def test_co_registered_scenario_needs_no_own_canonical_row(self):
        self.assertEqual(codes(self.root), set())
        def go(recs):
            for r in recs:
                if r['raw_set'] == 'SYN2' and r['raw_index'] == 4:
                    r['annotations'].pop('co_registered')
        self.edit('crosswalk', go, redigest=False)
        self.assertTrue(codes(self.root) & {'crosswalk_row_missing', 'raw_refs_mismatch'})

    def test_co_registration_must_name_a_scenario(self):
        def go(recs):
            for r in recs:
                if r['raw_set'] == 'SYN2' and r['raw_index'] == 4:
                    r['annotations']['co_registered'] = 'R-SYN-floor-a-00000001'
        self.edit('crosswalk', go, redigest=False)
        self.assertIn('unresolved_reference', codes(self.root))

    def test_reference_only_fixture_has_no_raw_record_but_others_must(self):
        self.mutate('fixtures', 'F-SYN-fixture-2-00000002', lambda r: r['annotations'].pop('reference_only', None) if 'reference_only' in r['annotations'] else None)
        self.assertEqual(codes(self.root), set())
        self.mutate('fixtures', 'F-SYN-ref-only-00000003', lambda r: r['annotations'].pop('reference_only'))
        self.assertIn('crosswalk_row_missing', codes(self.root))

    def test_scenario_fixture_refs_are_typed(self):
        self.mutate('scenarios', 'S-SYN-cofix-1-00000005', lambda r: r.__setitem__('fixture_refs', ['R-SYN-floor-a-00000001']))
        self.assertIn('unresolved_reference', codes(self.root))


class CompactLayout(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'compact'
        self.art = Path(self.tmp.name) / 'artifacts'
        self.root.mkdir()
        shutil.copytree(REG / 'schemas', self.root / 'schemas')
        self.manifest = B.build(S.sample_dataset(), str(self.root), max_per=S.SAMPLE_MAX_PER_PARTITION, layout='compact', artifacts_dir=str(self.art))

    def run_codes(self, artifacts=True):
        errors, _ = V.validate(str(self.root), artifacts=str(self.art) if artifacts else None)
        return {c for c, _ in errors}

    def test_compact_catalogue_validates_with_and_without_artifacts(self):
        self.assertEqual(self.run_codes(), set())
        self.assertEqual(self.run_codes(artifacts=False), set())
        self.assertEqual(self.manifest['layout'], 'compact')
        self.assertEqual(sorted(a['kind'] for a in self.manifest['external_artifacts']), ['crosswalk_rows', 'evidence_records', 'relationship_rows'])
        self.assertTrue(all(a['committed'] is False for a in self.manifest['external_artifacts']))

    def test_compact_partitions_are_encoded_and_smaller_per_record_than_plain(self):
        parts = [p for p in self.manifest['partitions'] if p['layer'] == 'rules']
        env = json.loads((self.root / parts[0]['path']).read_text())
        self.assertEqual(env['encoding'], V.ENCODING)
        self.assertIn('strings', env)

    def test_compact_build_is_byte_identical(self):
        other = Path(self.tmp.name) / 'again'
        other_art = Path(self.tmp.name) / 'again-art'
        other.mkdir()
        shutil.copytree(REG / 'schemas', other / 'schemas')
        B.build(S.sample_dataset(), str(other), max_per=S.SAMPLE_MAX_PER_PARTITION, layout='compact', artifacts_dir=str(other_art))
        a = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*.json')}
        b = {str(p.relative_to(other)): p.read_bytes() for p in other.rglob('*.json')}
        self.assertEqual(a, b)
        self.assertEqual({p.name: p.read_bytes() for p in self.art.iterdir()}, {p.name: p.read_bytes() for p in other_art.iterdir()})

    def test_same_logical_records_in_full_and_compact(self):
        full = Path(self.tmp.name) / 'full'
        full.mkdir()
        shutil.copytree(REG / 'schemas', full / 'schemas')
        B.build(S.sample_dataset(), str(full), max_per=S.SAMPLE_MAX_PER_PARTITION)
        fm = V.read_json(str(full / 'manifest.json'))
        self.assertEqual(fm['layer_counts'], self.manifest['layer_counts'])
        self.assertEqual(fm['source_inventory'], self.manifest['source_inventory'])
        self.assertEqual(fm['unresolved_accounting'], self.manifest['unresolved_accounting'])
        rules_full = [r for p in fm['partitions'] if p['layer'] == 'rules' for r in V.read_json(str(full / p['path']))['records']]
        env = [json.loads((self.root / p['path']).read_text()) for p in self.manifest['partitions'] if p['layer'] == 'rules']
        rules_compact = [r for e in env for r in V.decode_records(e['strings'], e['shapes'], e['records'])]
        self.assertEqual(rules_full, rules_compact)

    def test_artifact_tamper_is_refused(self):
        art = next(p for p in self.art.iterdir() if p.name.startswith('evidence-records'))
        art.write_bytes(art.read_bytes() + b' ')
        self.assertIn('artifact_hash_mismatch', self.run_codes())
        self.assertEqual(self.run_codes(artifacts=False), set())

    def test_missing_artifact_is_refused_when_supplied(self):
        next(p for p in self.art.iterdir() if p.name.startswith('crosswalk-rows')).unlink()
        self.assertIn('artifact_missing', self.run_codes())

    def test_index_that_disagrees_with_its_full_record_is_refused(self):
        part = next(p for p in self.manifest['partitions'] if p['layer'] == 'evidence')
        path = self.root / part['path']
        env = json.loads(path.read_text())
        recs = V.decode_records(env['strings'], env['shapes'], env['records'])
        recs[0]['run_id'] = 'tampered'
        recs[0]['digest'] = V.digest_of(recs[0])
        env['strings'], env['shapes'], env['records'] = V.encode_records(recs)
        path.write_bytes(V.dump_compact(env))
        B.refresh_manifest(str(self.root))
        self.assertIn('artifact_index_mismatch', self.run_codes())
        self.assertEqual(self.run_codes(artifacts=False), set())

    def test_codec_is_lossless_for_awkward_values(self):
        recs = [{'a': '~', 'b': '~1', 'c': '~~x', 'd': ['~', ['~1', None, True, 0, -1]], 'e': {'k': 'café ☃', 'l': []}, 'f': 'long string value repeated'},
                {'a': '~', 'b': '', 'c': 'long string value repeated', 'd': [], 'e': {}, 'f': 'long string value repeated'}]
        strings, shapes, body = V.encode_records(recs, min_len=3)
        self.assertEqual(V.decode_records(strings, shapes, body), recs)
        self.assertEqual(V.encode_records(recs, min_len=3), (strings, shapes, body))

    def test_undecodable_compact_partition_is_refused(self):
        part = next(p for p in self.manifest['partitions'] if p['layer'] == 'rules')
        path = self.root / part['path']
        env = json.loads(path.read_text())
        env['shapes'] = []
        path.write_bytes(V.dump_compact(env))
        B.refresh_manifest(str(self.root)) if False else None
        self.assertTrue(self.run_codes(artifacts=False) & {'partition_unreadable', 'partition_hash_mismatch'})


class LoaderResolution(unittest.TestCase):
    """Reference resolution in the loader: external test identities, derived artifacts across partitions."""
    def _ds(self, refs, extra_fixture=True):
        sc = {'catalogue_id': 'S-x', '_partition': 'C', '_refs': refs, '_evidence_raw': []}
        return {'layers': {'rules': {}, 'scenarios': {'S-x': sc}, 'tests': {}, 'fixtures': {'F-merged': {'catalogue_id': 'F-merged', '_partition': 'C', '_refs': {}, '_evidence_raw': []}} if extra_fixture else {}}, 'evidence': set(), 'ev_alias': {}}, sc

    def test_a_junit_only_test_identity_becomes_an_unresolved_placeholder_with_its_reason(self):
        ds, sc = self._ds({'test_refs': ['EXTERNAL_RESOLVED_IN_RETAINED_JUNIT:suite::test_a']})
        problems = L.Problems()
        L.resolve_refs(ds, L.IdMap(), problems)
        self.assertEqual(len(sc['test_refs']), 1)
        self.assertTrue(sc['test_refs'][0].startswith('UNRESOLVED:external test identity named only in a retained JUnit record'))
        self.assertIn('suite::test_a', sc['test_refs'][0])
        self.assertEqual(problems.rows[('C', 'ref_not_a_catalogue_id')]['count'], 1)

    def test_a_derived_artifact_id_from_another_partition_resolves_through_its_merge(self):
        idm = L.IdMap()
        idm.add('B', 'FD-sha256-aaaaaaaaaaaaaaaa', 'F-merged')
        ds, sc = self._ds({'fixture_refs': ['FD-sha256-aaaaaaaaaaaaaaaa']})
        problems = L.Problems()
        L.resolve_refs(ds, idm, problems)
        self.assertEqual(sc['fixture_refs'], ['F-merged'])
        self.assertEqual(problems.rows, {})

    def test_an_ordinary_id_is_never_resolved_across_partitions(self):
        idm = L.IdMap()
        idm.add('B', 'F-local', 'F-merged')
        ds, sc = self._ds({'fixture_refs': ['F-local']})
        L.resolve_refs(ds, idm, L.Problems())
        self.assertTrue(sc['fixture_refs'][0].startswith('UNRESOLVED:'))

    def test_an_ambiguous_derived_artifact_id_is_not_guessed(self):
        idm = L.IdMap()
        idm.add('B', 'FD-sha256-bbbbbbbbbbbbbbbb', 'F-merged')
        idm.add('C', 'FD-sha256-bbbbbbbbbbbbbbbb', 'F-other')
        ds, sc = self._ds({'fixture_refs': ['FD-sha256-bbbbbbbbbbbbbbbb']})
        L.resolve_refs(ds, idm, L.Problems())
        self.assertTrue(sc['fixture_refs'][0].startswith('UNRESOLVED:'))

    def test_one_raw_row_listing_two_scenarios_registers_both(self):
        row = {'raw_file': 'R4-x.json', 'raw_index': 3, 'raw_digest': 'ab' * 32, 'disposition': 'CANONICAL', 'target': 'S-a', 'tier': 'LOGICAL_SCENARIO',
               'additional_targets': ['S-b'], 'source_repo': 'o/r', 'native_id': 'n'}
        out = L._norm_row('R4', row, L.Problems())
        self.assertEqual(out['_co'], ['S-b'])


class RealShapes(Base):
    """Crosswalk forms emitted by the re-normalized partitions: attachments, differential instances, multi-scenario rows."""
    def _row_edit(self, ref, fn):
        def go(recs):
            for r in recs:
                if (r['raw_set'], r['raw_index']) == ref:
                    fn(r)
        self.edit('crosswalk', go, redigest=False)

    def test_attached_to_entry_resolves_to_an_existing_entry(self):
        self._row_edit(('SYN2', 1), lambda r: r.update(disposition='ATTACHED_TO_ENTRY', native_id=None))
        self.assertEqual(codes(self.root), set())

    def test_attached_to_entry_needs_a_real_entry(self):
        self._row_edit(('SYN2', 1), lambda r: r.update(disposition='ATTACHED_TO_ENTRY', target='F-SYN-nowhere-00000009'))
        self.assertTrue(codes(self.root) & {'unresolved_reference', 'raw_refs_mismatch'})

    def test_execution_evidence_cannot_be_attached_to_an_entry(self):
        self._row_edit(('SYN2', 0), lambda r: r.update(disposition='ATTACHED_TO_ENTRY', target='F-SYN-fixture-1-00000001'))
        self.assertTrue(codes(self.root) & {'crosswalk_tier_mismatch', 'evidence_as_rule', 'unresolved_reference'})

    def _as_differential_instance(self):
        def go(r):
            r.update(tier='PARAMETRIZED_INSTANCE', disposition='TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', target='S-SYN-cofix-1-00000005', native_id=None)
            r['annotations']['relation'] = 'DIFFERENTIAL_VECTOR_INSTANCE'
        self._row_edit(('SYN2', 1), go)
        self.mutate('fixtures', 'F-SYN-fixture-1-00000001', lambda r: r.__setitem__('raw_refs', [x for x in r['raw_refs'] if x != 'SYN2:1']))

    def test_differential_instance_rows_must_match_the_scenario_count(self):
        self._as_differential_instance()
        self.mutate('scenarios', 'S-SYN-cofix-1-00000005', lambda r: r.__setitem__('raw_refs', sorted(set(r['raw_refs']) | {'SYN2:1'})))
        self.assertIn('instance_count_mismatch', codes(self.root))

    def test_differential_instance_rows_with_a_matching_count_are_accepted(self):
        self._as_differential_instance()
        def fix(r):
            r['raw_refs'] = sorted(set(r['raw_refs']) | {'SYN2:1'})
            r['differential_instance_count'] = 1
        self.mutate('scenarios', 'S-SYN-cofix-1-00000005', fix)
        self.assertEqual(codes(self.root), set())

    def test_differential_instance_must_name_a_scenario(self):
        self._as_differential_instance()
        self._row_edit(('SYN2', 1), lambda r: r.__setitem__('target', 'T-SYN-nowhere-00000009'))
        self.assertIn('unresolved_reference', codes(self.root))

    def test_one_raw_row_may_stand_for_several_scenarios_but_each_must_exist(self):
        self._row_edit(('SYN2', 4), lambda r: r['annotations'].__setitem__('co_registered', ['S-SYN-cofix-1-00000005']))
        self.assertEqual(codes(self.root), set())
        self._row_edit(('SYN2', 4), lambda r: r['annotations'].__setitem__('co_registered', ['S-SYN-cofix-1-00000005', 'S-SYN-missing-00000099']))
        self.assertIn('unresolved_reference', codes(self.root))

    def test_fd_artifact_namespace_is_fixture_layer_only(self):
        self.mutate('fixtures', 'F-SYN-ref-only-00000003', lambda r: r.__setitem__('catalogue_id', 'FD-sha256-' + 'a' * 64))
        self.mutate('scenarios', 'S-SYN-cofix-1-00000005', lambda r: r.__setitem__('catalogue_id', 'FD-sha256-' + 'b' * 64))
        self.assertIn('namespace_mismatch', codes(self.root))

    def test_differential_file_pointer_counts_instances_not_suites(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'diff.json'
            f.write_text(json.dumps({'suites': [{'suite': 'S-a', 'instances': [1, 2]}, {'suite': 'S-b', 'instances': [3]}]}))
            sha = hashlib.sha256(f.read_bytes()).hexdigest()
            self.assertEqual(len(L._shard(str(f), {'file': 'diff.json', 'sha256': sha, 'items': 3})), 2)
            with self.assertRaises(L.LoadRefusal):
                L._shard(str(f), {'file': 'diff.json', 'sha256': sha, 'items': 2})


class DirectiveNegatives(Base):
    """The seven standing refusals. Each test builds a forged catalogue and expects the validator to refuse it by a named code."""
    SC1 = 'S-SYN-case-1-00000001'

    def _unrefresh(self):
        pass

    def test_derived_links_cannot_be_reported_as_independently_qualified_coverage(self):
        def derive(r):
            for rel in r['relationships']:
                if rel['field'] == 'evidence_digest_refs':
                    rel.update(provenance='DERIVED', source=None, method='run id grouping', supporting_refs=['SYN1:10'], confidence_class='medium')
        self.mutate('scenarios', self.SC1, derive)
        self.recover()
        self.assertEqual(codes(self.root), set())
        ev = self.dataset['evidence'][0]['evidence_digest']
        def forge(r):
            r['states'] = ['defined', 'implemented', 'tested', 'independently_qualified']
            r['assessments']['test_coverage'] = {'status': 'source_stated_link', 'basis_refs': [ev]}
            r['assessments']['independent_qualification'] = {'status': 'source_stated_record', 'basis_refs': [ev]}
        self.mutate('coverage', self.SC1, forge)
        self.assertIn('derived_reported_as_coverage', codes(self.root))

    def test_a_run_result_is_not_an_independent_qualification_record_even_when_source_stated(self):
        ev = self.dataset['evidence'][0]['evidence_digest']
        def forge(r):
            r['states'] = r['states'] + ['independently_qualified']
            r['assessments']['independent_qualification'] = {'status': 'source_stated_record', 'basis_refs': [ev]}
        self.mutate('coverage', self.SC1, forge)
        self.assertIn('derived_reported_as_coverage', codes(self.root))

    def test_unresolved_relationships_cannot_silently_become_established_mappings(self):
        def unresolve(r):
            for rel in r['relationships']:
                if rel['field'] == 'test_refs':
                    rel.update(provenance='UNRESOLVED', source=None, method=None, supporting_refs=[], confidence_class=None, missing_evidence='no source states this link')
        self.mutate('rules', 'R-SYN-reg-b-00000002', unresolve)
        # the coverage rows are deliberately not re-derived: they still claim an implementation on that link
        self.assertIn('unresolved_became_established', codes(self.root))

    def test_unresolved_items_cannot_leave_the_completeness_assessment(self):
        def unresolve(r):
            for rel in r['relationships']:
                if rel['field'] == 'test_refs':
                    rel.update(provenance='UNRESOLVED', source=None, method=None, supporting_refs=[], confidence_class=None, missing_evidence='no source states this link')
        self.mutate('rules', 'R-SYN-reg-b-00000002', unresolve)
        self.recover()
        def hide(r):
            r['assessments']['catalogue_completeness'] = {'status': 'complete', 'basis_refs': []}
        self.mutate('coverage', 'R-SYN-reg-b-00000002', hide)
        self.assertTrue(codes(self.root) & {'unresolved_hidden_from_completeness', 'coverage_inferred'})
        self.assertIn('unresolved_hidden_from_completeness', codes(self.root))

    def test_historical_pass_cannot_be_assigned_to_the_current_mvp(self):
        ev = self.dataset['evidence'][0]['evidence_digest']
        self.mutate('evidence', ev, lambda r: r.__setitem__('historical_verdict_verbatim', 'PASS'))
        def assign(r):
            r['mvp_applicability'] = {'value': 'mvp_fixed', 'reason': 'ran once', 'basis_id': ev, 'source_ref': 'results/run-1.json'}
        self.mutate('scenarios', self.SC1, assign)
        self.assertIn('historical_result_assigned_to_current', codes(self.root))

    def test_a_historical_record_cannot_carry_a_current_qualification_effect(self):
        ev = self.dataset['evidence'][0]['evidence_digest']
        self.mutate('evidence', ev, lambda r: r.__setitem__('current_qualification_effect', 'qualifies_current_candidate'))
        self.assertTrue(codes(self.root) & {'historical_result_assigned_to_current', 'record_schema'})

    def test_suite_level_rows_cannot_inflate_logical_scenario_totals(self):
        # a suite-level row relabelled as logical must change the recomputed denominator, and a committed count that was not recomputed is refused
        self.mutate('scenarios', 'S-SYN-suite-1-00000003', lambda r: r.__setitem__('scenario_class', 'logical'))
        self.assertEqual(V.read_json(str(self.root / 'manifest.json'))['denominators']['ten_denominators']['2_logical_governance_scenarios']['v0_1'], 3)
        _rewrite_manifest(self.root, lambda m: m['denominators']['ten_denominators']['2_logical_governance_scenarios'].__setitem__('v0_1', 2))
        self.assertIn('denominator_mismatch', codes(self.root))

    def test_a_differential_suite_with_instance_rows_is_not_a_logical_scenario(self):
        def go(r):
            r.update(tier='PARAMETRIZED_INSTANCE', disposition='TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', target='S-SYN-cofix-1-00000005', native_id=None)
            r['annotations']['relation'] = 'DIFFERENTIAL_VECTOR_INSTANCE'
        def edit(recs):
            for r in recs:
                if (r['raw_set'], r['raw_index']) == ('SYN2', 1):
                    go(r)
        self.edit('crosswalk', edit, redigest=False)
        self.mutate('fixtures', 'F-SYN-fixture-1-00000001', lambda r: r.__setitem__('raw_refs', [x for x in r['raw_refs'] if x != 'SYN2:1']))
        def fix(r):
            r['raw_refs'] = sorted(set(r['raw_refs']) | {'SYN2:1'})
            r['differential_instance_count'] = 1
            r['scenario_class'] = 'logical'
        self.mutate('scenarios', 'S-SYN-cofix-1-00000005', fix)
        self.assertIn('suite_rows_counted_as_logical', codes(self.root))

    def test_parametrized_instances_cannot_inflate_unique_test_or_scenario_counts(self):
        def go(recs):
            for r in recs:
                if (r['raw_set'], r['raw_index']) == ('SYN1', 7):
                    r['disposition'], r['target'] = 'CANONICAL', 'T-SYN-test-1-00000001'
        self.edit('crosswalk', go, redigest=False)
        found = codes(self.root)
        self.assertIn('instances_counted_as_unique', found)
        self.assertIn('crosswalk_tier_mismatch', found)

    def test_repeated_executions_cannot_become_entries_or_inflate_the_instance_count(self):
        self.mutate('tests', 'T-SYN-test-1-00000001', lambda r: r.__setitem__('parametrized_instance_count', 99))
        self.assertIn('instance_count_mismatch', codes(self.root))
        def go(recs):
            for r in recs:
                if (r['raw_set'], r['raw_index']) == ('SYN1', 10):
                    r['disposition'] = 'ALIAS_OF'
                    r['target'] = 'T-SYN-test-1-00000001'
        self.edit('crosswalk', go, redigest=False)
        self.assertIn('instances_counted_as_unique', codes(self.root))

    def test_normative_rules_stay_distinct_from_reason_codes_and_advisory_principles(self):
        def conflate(r):
            r['annotations']['rule_family'] = 'runtime-authority-reasons/0.2 registry code'
            r['normative_type'] = 'mandatory'
        self.mutate('rules', 'R-SYN-reason-c-00000003', conflate)
        self.assertIn('normative_vocabulary_conflated', codes(self.root))
        self.assertEqual(self.dataset['rules'][2]['normative_type'], 'reason_code_or_refusal_vocabulary')
        self.setUp()
        by_type = V.read_json(str(self.root / 'manifest.json'))['denominators']['ten_denominators']['1_canonical_rules_by_normative_type']
        self.assertEqual((by_type['reason_code_or_refusal_vocabulary'], by_type['mandatory'], by_type['advisory']), (1, 1, 1))
        _rewrite_manifest(self.root, lambda m: m['denominators']['ten_denominators']['1_canonical_rules_by_normative_type'].update(mandatory=2, reason_code_or_refusal_vocabulary=0))
        self.assertIn('denominator_mismatch', codes(self.root))

    def test_unresolved_records_cannot_disappear_from_completeness_accounting(self):
        _rewrite_manifest(self.root, lambda m: m['unresolved_by_layer']['crosswalk'].__setitem__('unresolved_rows', 0))
        self.assertIn('unresolved_accounting_mismatch', codes(self.root))
        self.setUp()
        _rewrite_manifest(self.root, lambda m: m['unresolved_accounting'].__setitem__('crosswalk_unresolved_rows', 0))
        self.assertIn('unresolved_accounting_mismatch', codes(self.root))
        self.setUp()
        def drop(recs):
            recs[:] = [r for r in recs if not (r['raw_set'] == 'SYN1' and r['raw_index'] == 12)]
        self.edit('crosswalk', drop, redigest=False)
        self.assertIn('crosswalk_row_missing', codes(self.root))


class RegistryVersions(Base):
    """The 0.1 and 0.2 reason-code registries: entries and distinct code names are different denominators, never one headline."""
    def _make(self):
        def one(r):
            r['annotations']['rule_family'] = 'runtime-authority-reasons/0.1 registry code (pinned original-121 label; distinct entry)'
            r['native_ids'] = ['code_a@0.1']
        def two(r):
            r['annotations']['rule_family'] = 'runtime-authority-reasons/0.2 registry code'
            r['native_ids'] = ['code_a']
        self.mutate('rules', 'R-SYN-reason-c-00000003', one)
        self.mutate('rules', 'R-SYN-reg-b-00000002', lambda r: (two(r), r.__setitem__('normative_type', 'reason_code_or_refusal_vocabulary')))

    def test_entries_and_code_names_are_reported_as_separate_denominators(self):
        self._make()
        reg = V.read_json(str(self.root / 'manifest.json'))['denominators']['rule_code_registries']
        self.assertEqual((reg['runtime_authority_reasons_entries_label_0_1'], reg['runtime_authority_reasons_entries_label_0_2'], reg['distinct_registry_code_names']), (1, 1, 1))
        self.assertIn('none by design', reg['headline'])
        manifest, layers = R._load(str(self.root))
        out = R.denominators(manifest, layers)
        self.assertEqual(out['rule_code_registries'], reg)
        self.assertFalse([k for k in out if 'total' in k])

    def test_a_zero_point_two_entry_cannot_absorb_a_zero_point_one_identity(self):
        self._make()
        self.assertEqual(codes(self.root), set())
        self.mutate('rules', 'R-SYN-reg-b-00000002', lambda r: r.__setitem__('native_ids', ['code_a', 'code_a@0.1']))
        self.assertIn('registry_versions_merged', codes(self.root))

    def test_a_zero_point_one_entry_must_keep_its_own_label(self):
        self._make()
        self.mutate('rules', 'R-SYN-reason-c-00000003', lambda r: r.__setitem__('native_ids', ['code_a@0.1', 'code_a']))
        self.assertIn('registry_versions_merged', codes(self.root))


class SourceReferences(Base):
    """Source-only raw records stay SOURCE_ONLY_ARTIFACT rows; entries may record inbound links to them by raw digest."""
    def _link(self, ref, prov='DERIVED'):
        def go(r):
            r['source_reference_refs'] = [ref]
            r['relationships'].append({'field': 'source_reference_refs', 'to': ref, 'provenance': 'DERIVED', 'source': None, 'method': 'index entry matched by id',
                                       'supporting_refs': ['SYN1:11'], 'confidence_class': 'medium', 'missing_evidence': None, 'establishes_enforcement': False,
                                       'establishes_test_coverage': False, 'establishes_qualification': False})
        self.mutate('rules', 'R-SYN-reg-b-00000002', go)

    def setUp(self):
        super().setUp()
        row = next(r for r in self.dataset['crosswalk'] if (r['raw_set'], r['raw_index']) == ('SYN1', 11))
        self.sr = 'SR:SYN1:' + row['raw_digest'][7:]

    def test_a_source_reference_to_a_source_only_row_validates(self):
        self._link(self.sr)
        self.assertEqual(codes(self.root), set())

    def test_a_source_reference_without_a_source_only_row_is_refused(self):
        self._link('SR:SYN1:' + '0' * 64)
        self.assertIn('unresolved_reference', codes(self.root))

    def test_a_source_reference_to_a_canonical_row_is_refused(self):
        row = next(r for r in self.dataset['crosswalk'] if (r['raw_set'], r['raw_index']) == ('SYN1', 0))
        self._link('SR:SYN1:' + row['raw_digest'][7:])
        self.assertIn('unresolved_reference', codes(self.root))

    def test_a_source_reference_needs_its_provenance_record(self):
        self._link(self.sr)
        self.mutate('rules', 'R-SYN-reg-b-00000002', lambda r: r.__setitem__('relationships', [x for x in r['relationships'] if x['field'] != 'source_reference_refs']))
        self.assertIn('relationship_missing', codes(self.root))


class GzipArtifacts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'registry'
        self.root.mkdir()
        shutil.copytree(REG / 'schemas', self.root / 'schemas')
        self.manifest = B.build(S.sample_dataset(), str(self.root), max_per=S.SAMPLE_MAX_PER_PARTITION, layout='compact',
                                artifacts_dir=str(self.root / 'artifacts'), artifacts_gzip=True)

    def codes(self):
        errors, _ = V.validate(str(self.root))
        return {c for c, _ in errors}

    def art(self, kind):
        return next(a for a in self.manifest['external_artifacts'] if a['kind'] == kind)

    def test_committed_gzip_artifacts_validate_without_an_artifacts_argument(self):
        self.assertEqual(self.codes(), set())
        for a in self.manifest['external_artifacts']:
            self.assertTrue(a['committed'] and a['path'].endswith('.json.gz'))
            self.assertEqual(a['compression'], {'format': 'gzip', 'level': 9, 'mtime': 0, 'embedded_name': None})

    def test_the_manifest_pins_both_the_uncompressed_content_and_the_gzip_file(self):
        import gzip
        import hashlib
        a = self.art('crosswalk_rows')
        packed = (self.root / a['path']).read_bytes()
        self.assertEqual('sha256:' + hashlib.sha256(packed).hexdigest(), a['gzip_sha256'])
        self.assertEqual(len(packed), a['gzip_bytes'])
        raw = gzip.decompress(packed)
        self.assertEqual('sha256:' + hashlib.sha256(raw).hexdigest(), a['sha256'])
        self.assertEqual(len(raw), a['bytes'])

    def test_gzip_output_is_deterministic_with_mtime_zero_and_no_name(self):
        data = b'{"a": 1}\n' * 100
        one, two = B.gzip_bytes(data), B.gzip_bytes(data)
        self.assertEqual(one, two)
        self.assertEqual(one[4:8], b'\x00\x00\x00\x00')
        self.assertEqual(one[3] & 0x08, 0)

    def test_a_changed_gzip_file_is_refused(self):
        a = self.art('evidence_records')
        path = self.root / a['path']
        data = bytearray(path.read_bytes())
        data[-12] ^= 0xFF
        path.write_bytes(bytes(data))
        self.assertTrue(self.codes() & {'artifact_hash_mismatch', 'artifact_unreadable'})

    def test_a_repacked_gzip_with_other_content_is_refused(self):
        a = self.art('evidence_records')
        (self.root / a['path']).write_bytes(B.gzip_bytes(b'{"records": []}'))
        self.assertIn('artifact_hash_mismatch', self.codes())

    def test_a_missing_gzip_artifact_is_refused(self):
        os.remove(self.root / self.art('relationship_rows')['path'])
        self.assertIn('artifact_missing', self.codes())

    def test_an_artifact_path_cannot_leave_the_catalogue_root(self):
        def go(m):
            m['external_artifacts'][0]['path'] = '../outside.json.gz'
        _rewrite_manifest(self.root, go)
        self.assertTrue(self.codes() & {'artifact_missing', 'record_schema', 'artifact_hash_mismatch'})

    def test_a_gzip_bomb_beyond_the_recorded_size_is_refused(self):
        import gzip
        a = self.art('crosswalk_rows')
        big = gzip.compress(b'0' * (a['bytes'] + 5000), mtime=0)
        (self.root / a['path']).write_bytes(big)
        def go(m):
            for x in m['external_artifacts']:
                if x['kind'] == 'crosswalk_rows':
                    x['gzip_sha256'] = V.sha256_bytes(big)
                    x['gzip_bytes'] = len(big)
        _rewrite_manifest(self.root, go)
        self.assertIn('artifact_unreadable', self.codes())


class CommittedRealCatalogue(unittest.TestCase):
    CAT = REG / 'catalogue-v0.1'

    def setUp(self):
        # the real catalogue is committed to this repository: its absence is a failure, never a skip
        self.assertTrue((self.CAT / 'manifest.json').exists(), 'the committed real catalogue is missing')

    def test_real_catalogue_validates_offline_with_its_committed_artifacts(self):
        errors, manifest = V.validate(str(self.CAT))
        self.assertEqual(errors, [])
        self.assertTrue(all(a['committed'] and a['path'].endswith('.json.gz') for a in manifest['external_artifacts']))
        self.assertEqual({s['set_id']: s['raw_record_count'] for s in manifest['source_inventory']},
                         {'A': 2863, 'A2': 3655, 'B': 2316, 'C': 11360, 'C2': 346, 'C3': 3112, 'D': 26110, 'R4': 2075})
        self.assertEqual(manifest['denominators']['rule_code_registries']['distinct_registry_code_names'], 164)
        self.assertEqual(manifest['denominators']['rule_code_registries']['rule_entries_resting_on_raw_set_B'], 384)

    def test_real_catalogue_schemas_are_the_registry_schemas_and_reports_are_current(self):
        for p in sorted((REG / 'schemas').glob('*.json')):
            self.assertEqual(p.read_bytes(), (self.CAT / 'schemas' / p.name).read_bytes(), p.name)
        out = R.render(str(self.CAT))
        for name, data in out.items():
            self.assertEqual(data, (self.CAT / 'reports' / 'generated' / name).read_bytes(), name)

    def test_no_committed_file_is_over_the_single_file_limit(self):
        biggest = max(p.stat().st_size for p in self.CAT.rglob('*') if p.is_file())
        self.assertLess(biggest, 20 * 1024 * 1024)


class MvpLinkedOverlay(unittest.TestCase):
    """Architect ruling Q8: nine MVP-linked items are resolved by exact identity through a pinned overlay; nothing is collapsed."""
    CAT = REG / 'catalogue-v0.1'
    OVERLAY = REG / 'overlays' / 'mvp-linked-q8.json'
    JOURNAL = ['R-ver-verifier-finding-journal-check-reused-7bb16c1d', 'R-rep-execution-attempt-lifecycle-journal-check-reused-e2f329a1',
               'R-odes-control-plane-journal-journal-check-reused-7b5d4063']
    DECISION = ['R-ver-verifier-finding-decision-result-inconsistent-5e16d519', 'R-odes-control-plane-journal-decision-result-inconsiste-4cfee360']
    SCN = {'R-SCN-C07-c4d3e6c3': 5, 'R-SCN-C08-c68c1f0f': 4, 'R-SCN-C09-4f95d76e': 3, 'R-SCN-D09-d91c9f4c': 3}

    @classmethod
    def setUpClass(cls):
        rep = V.Report()
        cls.manifest, cls.layers = V.load_registry(str(cls.CAT), rep, V.load_schemas(str(cls.CAT), rep))
        cls.rules = {e['catalogue_id']: e for e in cls.layers['rules']}
        cls.scns = {e['catalogue_id']: e for e in cls.layers['scenarios']}

    def test_the_journal_and_decision_records_remain_distinct_entries(self):
        for group in (self.JOURNAL, self.DECISION):
            self.assertEqual(len(set(group)), len(group))
            for cid in group:
                e = self.rules[cid]
                self.assertEqual(len(e['native_ids']), 1)
                self.assertNotIn('merged_from', e['annotations'])
                self.assertEqual(e['aliases'], [])
        repos = {self.rules[c]['source']['repo'] for c in self.JOURNAL}
        self.assertEqual(len(repos), 3)
        # all three journal records are associated with the same MVP journal-integrity row, each by its own link
        for cid in self.JOURNAL:
            self.assertIn('S-VER-02-1dda9a4b', self.rules[cid]['scenario_refs'])
        for cid in self.DECISION:
            self.assertIn('S-NC5-04-76664db5', self.rules[cid]['scenario_refs'])

    def test_applicability_is_resolved_only_where_the_row_exercises_the_enforcement_path(self):
        for cid in self.JOURNAL + self.DECISION[:1]:
            self.assertEqual(self.rules[cid]['mvp_applicability']['value'], 'mvp_fixed', cid)
            self.assertEqual(self.rules[cid]['mvp_applicability']['basis_id'], 'MB-Q8-ROW')
        odes = self.rules[self.DECISION[1]]
        self.assertEqual(odes['mvp_applicability']['value'], 'unresolved')
        link = next(r for r in odes['relationships'] if r['to'] == 'S-NC5-04-76664db5')
        self.assertEqual((link['provenance'], link['confidence_class']), ('DERIVED', 'low'))
        self.assertIn('equivalence', link['method'])

    def test_links_establish_nothing_and_carry_method_or_source(self):
        for cid in self.JOURNAL + self.DECISION + list(self.SCN):
            for r in self.rules[cid]['relationships']:
                if r['to'] in self.scns and r['field'] == 'scenario_refs' and (r['to'].startswith(('S-NC', 'S-VER'))):
                    self.assertIs(r['establishes_enforcement'], False)
                    self.assertIs(r['establishes_test_coverage'], False)
                    self.assertIs(r['establishes_qualification'], False)
                    self.assertIn(r['provenance'], ('SOURCE_STATED', 'DERIVED'))
                    self.assertTrue(r['source'] if r['provenance'] == 'SOURCE_STATED' else (r['method'] and r['supporting_refs']))

    def test_scn_rows_are_typed_scenario_links_and_never_mvp_fixed_rules(self):
        art = next(a for a in self.manifest['external_artifacts'] if a['kind'] == 'relationship_rows')
        rep = V.Report()
        rows = {r['relationship_id']: r for r in V._artifact_records(V._artifact_file(None, str(self.CAT), art), rep, art)}
        self.assertEqual(rep.errors, [])
        typed = [r for r in rows.values() if r['relation_kind'] == 'mvp_requirement_row_link']
        self.assertEqual(len(typed), sum(self.SCN.values()))
        for r in typed:
            self.assertEqual((r['type'], r['provenance'], r['partition']), ('requirement_row->scenario', 'SOURCE_STATED', 'OVERLAY'))
            self.assertIn(r['from_global'], self.SCN)
            self.assertEqual(self.scns[r['to_global']]['mvp_applicability']['basis_id'], 'MB-MVPCHAIN-ROW')
        for cid, n in self.SCN.items():
            e = self.rules[cid]
            self.assertEqual(e['normative_type'], 'requirement_row')
            self.assertNotEqual(e['mvp_applicability']['value'], 'mvp_fixed')
            self.assertEqual(sum(1 for r in typed if r['from_global'] == cid), n)
            self.assertEqual(len(e['scenario_refs']), n)
        self.assertIn('route B', self.rules['R-SCN-D09-d91c9f4c']['annotations']['mvp_link_scope'])

    def test_requirement_rows_stay_out_of_the_rule_headline(self):
        head = self.manifest['denominators']['rule_headline']
        self.assertEqual(head['requirement_rows_mvp_fixed'], 0)
        self.assertNotIn('requirement_row', {self.rules[c]['normative_type'] for c in self.rules if self.rules[c]['mvp_applicability']['value'] == 'mvp_fixed'})
        self.assertEqual(head['mvp_fixed_rules_excluding_requirement_rows'], 9)
        self.assertEqual(head['requirement_rows_in_the_rule_layer_reported_apart'], 134)

    def test_everything_else_keeps_its_unresolved_applicability(self):
        changed = set(self.JOURNAL + self.DECISION[:1])
        fixed_rules = {c for c, e in self.rules.items() if e['mvp_applicability']['value'] == 'mvp_fixed'}
        self.assertEqual(len(fixed_rules - changed), 5)
        self.assertEqual(sum(1 for e in self.rules.values() if e['annotations'].get('mvp_link_overlay')), 9)

    def test_the_overlay_is_pinned_in_the_regeneration_inputs(self):
        pinned = self.manifest['regeneration']['inputs']['overlays']
        self.assertEqual(pinned, [{'path': 'docs/mvp-recovery/registry/overlays/mvp-linked-q8.json', 'sha256': V.sha256_bytes(self.OVERLAY.read_bytes())}])
        self.assertIn('--overlay', self.manifest['regeneration']['command'])

    def test_reports_carry_the_unresolved_applicability_sentence(self):
        for name in ('catalogue-integrity-report.md', 'governance-coverage-report.md'):
            text = (self.CAT / 'reports' / 'generated' / name).read_text()
            self.assertIn('not evidence that requirements are unimplemented and not a coverage claim', text)

    # ---- the loader refuses an overlay that does not match the exact identity ----
    def _mini(self):
        rule = {'catalogue_id': 'R-X', 'native_ids': ['SCN-C07'], 'source': {'repo': 'a/b', 'path': 'p.json'}, 'normative_type': 'requirement_row',
                'relationships': [], 'annotations': {}, 'scenario_refs': [], 'mvp_applicability': {'value': 'unresolved', 'reason': 'x'}}
        scn = {'catalogue_id': 'S-Y', 'native_ids': ['NC1-01'], 'relationships': [], 'rule_refs': [], 'mvp_applicability': {'value': 'mvp_fixed', 'basis_id': 'MB-MVPCHAIN-ROW', 'reason': 'x', 'source_ref': 'some source'}}
        item = {'id': 'R-X', 'kind': 'requirement_row_to_mvp_scenario', 'expect': {'native_id': 'SCN-C07', 'source_repo': 'a/b', 'source_path': 'p.json', 'normative_type': 'requirement_row'},
                'target_native_ids': ['NC1-01'], 'row_type': 'requirement_row->scenario', 'relation_kind': 'mvp_requirement_row_link', 'provenance': 'SOURCE_STATED',
                'source': {'repo': 'a/b', 'revision': '1' * 40, 'path': 'd.md', 'location': 'line 1'}, 'applicability': None, 'note': None}
        doc = {'profile': 'ocs-catalogue-overlay/0', 'overlay_id': 't', 'non_authorizing': True, 'authority': 'none', 'links': [item]}
        return {'layers': {'rules': {'R-X': rule}, 'scenarios': {'S-Y': scn}}}, doc

    def test_the_loader_applies_a_matching_item_as_a_typed_bidirectional_link(self):
        ds, doc = self._mini()
        L.apply_mvp_links(ds, doc, None, L.Problems())
        self.assertEqual(ds['layers']['rules']['R-X']['scenario_refs'], ['S-Y'])
        self.assertEqual(ds['layers']['scenarios']['S-Y']['rule_refs'], ['R-X'])
        self.assertEqual([r['type'] for r in ds['_relationship_rows']], ['requirement_row->scenario'])
        self.assertEqual(ds['layers']['rules']['R-X']['mvp_applicability']['value'], 'unresolved')

    def test_the_loader_refuses_a_mismatched_identity_a_missing_target_or_a_non_mvp_target(self):
        for edit in (lambda d, ds: d['links'][0]['expect'].update(native_id='SCN-C99'), lambda d, ds: d['links'][0]['expect'].update(source_repo='x/y'),
                     lambda d, ds: d['links'][0]['expect'].update(source_path='other.json'), lambda d, ds: d['links'][0]['expect'].update(normative_type='mandatory'),
                     lambda d, ds: d['links'][0].update(id='R-NOPE'), lambda d, ds: d['links'][0].update(target_native_ids=['NC9-99']),
                     lambda d, ds: ds['layers']['scenarios']['S-Y']['mvp_applicability'].update(value='unresolved'),
                     lambda d, ds: d.update(authority='granted')):
            ds, doc = self._mini()
            edit(doc, ds)
            with self.assertRaises(L.LoadRefusal):
                L.apply_mvp_links(ds, doc, None, L.Problems())

    # ---- validator ----
    def test_the_validator_refuses_a_requirement_row_that_is_mvp_fixed(self):
        layers = {'rules': [{'catalogue_id': 'R-X', 'normative_type': 'requirement_row', 'mvp_applicability': {'value': 'mvp_fixed', 'reason': 'r', 'basis_id': 'MB-X', 'source_ref': 'some source'}}],
                  'scenarios': [], 'tests': [], 'fixtures': []}
        rep = V.Report()
        V.check_mvp(layers, rep)
        self.assertIn('requirement_row_mvp_fixed', {c for c, _ in rep.sorted()})

    def test_the_validator_refuses_an_untyped_mvp_link(self):
        rule = self.rules['R-SCN-C07-c4d3e6c3']
        rel = next(r for r in rule['relationships'] if r['to'] == 'S-NC1-01-06539300')
        rid = rel['row_id']
        art = next(a for a in self.manifest['external_artifacts'] if a['kind'] == 'relationship_rows')
        rep = V.Report()
        row = next(r for r in V._artifact_records(V._artifact_file(None, str(self.CAT), art), rep, art) if r['relationship_id'] == rid)
        for field, value in (('type', 'rule->scenario'), ('provenance', 'DERIVED')):
            rep = V.Report()
            V._check_mvp_link('R-SCN-C07-c4d3e6c3', rel, dict(row, **{field: value}), self.layers, rep, 'x')
            self.assertIn('mvp_link_untyped', {c for c, _ in rep.sorted()}, field)
        rep = V.Report()
        V._check_mvp_link('R-SCN-C07-c4d3e6c3', rel, row, self.layers, rep, 'x')
        self.assertEqual(rep.sorted(), [])
        rep = V.Report()
        V._check_mvp_link('R-SCN-C07-c4d3e6c3', dict(rel, to=next(c for c, e in self.scns.items() if e['mvp_applicability']['value'] == 'unresolved')), row, self.layers, rep, 'x')
        self.assertIn('mvp_link_untyped', {c for c, _ in rep.sorted()})


class ArtifactDeepChecks(unittest.TestCase):
    """The committed artifacts are compared field by field with the embedded copies; a tampered artifact with consistent hashes still fails."""
    REL = 'REL-' + 'a' * 16

    def setUp(self):
        import copy as _copy
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'registry'
        self.root.mkdir()
        shutil.copytree(REG / 'schemas', self.root / 'schemas')
        ds = S.sample_dataset()
        rule = next(r for r in ds['rules'] if r['catalogue_id'] == 'R-SYN-floor-a-00000001')
        rel = next(x for x in rule['relationships'] if x['field'] == 'test_refs')
        rel['row_id'] = self.REL
        self.row = {'relationship_id': self.REL, 'type': 'rule->test_implementation', 'provenance': 'DERIVED', 'method': rel['method'],
                    'supporting_references': list(rel['supporting_refs']), 'confidence': rel['confidence_class'], 'from': rule['catalogue_id'],
                    'to': rel['to'], 'from_global': rule['catalogue_id'], 'to_global': rel['to'], 'from_kind': 'rule', 'to_kind': 'test_implementation',
                    'partition': 'SYN', 'relation_kind': 'x', 'claim_status': 'candidate_link_only_non_authorizing', 'establishes_enforcement': False,
                    'establishes_test_coverage': False, 'establishes_qualification': False}
        # one legitimate row of every unembedded class: instance, unresolved, revision_of and pair_recorded
        suite = next(x for x in ds['scenarios'] if x['catalogue_id'] == 'S-SYN-suite-1-00000003')
        suite['differential_instance_count'] = 2
        suite['raw_refs'] = list(suite['raw_refs']) + ['SYN1:17', 'SYN1:18']
        for i in (17, 18):
            ds['crosswalk'].append(dict(S._row('SYN1', i, 'di-%d' % i, 'PARAMETRIZED_INSTANCE', 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', suite['catalogue_id']),
                                        annotations={'relation': 'DIFFERENTIAL_VECTOR_INSTANCE'}))
        case2 = next(x for x in ds['scenarios'] if x['catalogue_id'] == 'S-SYN-case-2-00000002')
        rev = S._d('rev-c')
        case2['raw_refs'] = list(case2['raw_refs']) + ['SYN1:16']
        case2['lineage'] = [{'revision_id': 'SYN-CASE-2@earlier', 'raw_ref': 'SYN1:16', 'digest': rev, 'relation': 'HISTORICAL_REVISION'}]
        ds['crosswalk'].append(S._row('SYN1', 16, 'rev-c', 'RULE_REVISION', 'HISTORICAL_REVISION_OF', case2['catalogue_id'], 'SYN-CASE-2@earlier'))
        flags = {'establishes_enforcement': False, 'establishes_test_coverage': False, 'establishes_qualification': False,
                 'partition': 'SYN', 'claim_status': 'candidate_link_only_non_authorizing'}
        derived = dict(flags, provenance='DERIVED', method='a method', confidence='high', supporting_references=['a reference'])
        self.extra = {
            'instance1': dict(derived, relationship_id='REL-b' + '0' * 15, type='differential_instance->scenario', relation_kind='differential_instance_membership',
                              **{'from': 'DI:SYN:1', 'from_global': 'DI:SYN:1', 'to': suite['catalogue_id'], 'to_global': suite['catalogue_id'],
                                 'from_kind': 'differential_instance', 'to_kind': 'scenario'}),
            'instance2': dict(derived, relationship_id='REL-b' + '0' * 14 + '1', type='differential_instance->scenario', relation_kind='differential_instance_membership',
                              **{'from': 'DI:SYN:2', 'from_global': 'DI:SYN:2', 'to': suite['catalogue_id'], 'to_global': suite['catalogue_id'],
                                 'from_kind': 'differential_instance', 'to_kind': 'scenario'}),
            'unresolved': dict(flags, relationship_id='REL-c' + '0' * 15, type='scenario->test_implementation', provenance='UNRESOLVED', relation_kind='no_scenario_link',
                               missing_evidence='no test links this scenario', **{'from': 'S-SYN-case-1-00000001', 'from_global': 'S-SYN-case-1-00000001',
                                                                                 'to': None, 'to_global': None, 'from_kind': 'scenario', 'to_kind': 'test_implementation'}),
            'revision': dict(flags, relationship_id='REL-d' + '0' * 15, type='scenario->scenario', provenance='SOURCE_STATED', relation_kind='revision_of',
                             source={'repo': case2['source']['repo'], 'revision': case2['source']['revision'], 'location': 'rev:$.x', 'path': 'a/b.json'},
                             **{'from': case2['catalogue_id'], 'from_global': case2['catalogue_id'], 'to': 'REV:' + rev[7:], 'to_global': None,
                                'from_kind': 'scenario', 'to_kind': 'scenario_revision'}),
            'pair': dict(derived, relationship_id='REL-e' + '0' * 15, type='rule->rule', relation_kind='candidate_equivalent',
                         **{'from': 'R-SYN-floor-a-00000001', 'from_global': 'R-SYN-floor-a-00000001', 'to': 'R-SYN-reason-c-00000003', 'to_global': 'R-SYN-reason-c-00000003',
                            'from_kind': 'rule', 'to_kind': 'rule'}),
        }
        ds['relationship_rows'] = [self.row] + list(self.extra.values())
        self.manifest = B.build(ds, str(self.root), max_per=S.SAMPLE_MAX_PER_PARTITION, layout='compact', artifacts_dir=str(self.root / 'artifacts'), artifacts_gzip=True)

    def codes(self):
        errors, _ = V.validate(str(self.root))
        return {c for c, _ in errors}

    def tamper(self, kind, fn, recommit=True):
        """Rewrite one artifact and keep every hash in the manifest consistent, so only a field comparison can notice.

        With recommit the committed relationship-row accounting is recomputed from the tampered rows as well (an attacker who
        also rewrites the manifest); without it the manifest still holds the accounting of the original rows.
        """
        art = next(a for a in self.manifest['external_artifacts'] if a['kind'] == kind)
        path = self.root / art['path']
        import gzip
        env = json.loads(gzip.decompress(path.read_bytes()))
        recs = V.decode_records(env['strings'], env['shapes'], env['records'])
        fn(recs)
        env['strings'], env['shapes'], env['records'] = V.encode_records(recs)
        data = V.dump_compact(env)
        packed = B.gzip_bytes(data)
        path.write_bytes(packed)
        def go(m):
            for x in m['external_artifacts']:
                if x['kind'] == kind:
                    x.update(sha256=V.sha256_bytes(data), bytes=len(data), gzip_sha256=V.sha256_bytes(packed), gzip_bytes=len(packed), record_count=len(recs))
            if kind == 'relationship_rows' and recommit:
                rep = V.Report()
                _, layers = V.load_registry(str(self.root), rep, V.load_schemas(str(self.root), rep))
                m['relationship_row_accounting'] = V.relationship_row_accounting({r['relationship_id']: r for r in recs if r.get('relationship_id') is not None and type(r) is dict}, layers)
        _rewrite_manifest(self.root, go)

    def test_baseline_is_clean(self):
        self.assertEqual(self.codes(), set())

    def test_flipping_an_establishes_flag_in_the_artifact_with_consistent_hashes_fails(self):
        self.tamper('relationship_rows', lambda recs: recs[0].__setitem__('establishes_enforcement', True))
        self.assertTrue(self.codes() & {'artifact_index_mismatch', 'artifact_row_schema'})

    def test_changed_method_confidence_or_provenance_in_the_artifact_fails(self):
        for field, value in (('method', 'a different method'), ('confidence', 'low'), ('supporting_references', ['other']), ('provenance', 'UNRESOLVED')):
            self.setUp()
            self.tamper('relationship_rows', lambda recs: recs[0].__setitem__(field, value))
            self.assertIn('artifact_index_mismatch', self.codes(), field)

    def test_changed_endpoints_in_the_artifact_fail(self):
        self.tamper('relationship_rows', lambda recs: recs[0].__setitem__('to_global', 'T-SYN-other-00000009'))
        self.assertIn('artifact_index_mismatch', self.codes())

    def test_duplicate_relationship_ids_are_refused_not_collapsed(self):
        self.tamper('relationship_rows', lambda recs: recs.append(dict(recs[0], method='second copy')))
        self.assertIn('artifact_duplicate_key', self.codes())

    def test_a_row_that_nothing_embeds_and_nothing_accounts_for_is_an_orphan(self):
        extra = dict(self.row, relationship_id='REL-' + 'b' * 16, to_global='S-SYN-spec-1-00000004', to='S-SYN-spec-1-00000004', from_global='R-SYN-reason-c-00000003', **{'from': 'R-SYN-reason-c-00000003'})
        self.tamper('relationship_rows', lambda recs: recs.append(extra))
        self.assertIn('artifact_orphan_row', self.codes())

    def test_an_unembedded_row_with_no_catalogue_endpoint_is_accounted(self):
        extra = dict(self.row, relationship_id='REL-' + 'c' * 16, to_global=None, to=None, provenance='UNRESOLVED', missing_evidence='x')
        for k in ('method', 'supporting_references', 'confidence'):
            extra.pop(k)
        self.tamper('relationship_rows', lambda recs: recs.append(extra))
        self.assertEqual(self.codes(), set())

    # ---- the unembedded rows: every class has a signature, and the manifest commits the counts (review of dba7b15d, MEDIUM) ----
    def _edit_row(self, key, fn, recommit=True):
        rid = self.extra[key]['relationship_id']
        def go(recs):
            fn(next(r for r in recs if r['relationship_id'] == rid))
        self.tamper('relationship_rows', go, recommit)

    def _append(self, row, recommit=True):
        self.tamper('relationship_rows', lambda recs: recs.append(row), recommit)

    def _fake(self, **kw):
        base = dict(self.extra['pair'], relationship_id='REL-f' + '0' * 15)
        base.update(kw)
        return base

    def _invented_source(self):
        return {'repo': 'cogno-us/cognous-stack-qualification', 'revision': 'review-v0.1-g8-r10-20261022 8a8a3be5', 'location': 'invented :: x', 'path': 'invented'}

    def test_the_manifest_commits_the_class_and_type_counts_of_the_relationship_rows(self):
        acc = self.manifest['relationship_row_accounting']
        self.assertEqual(acc['total'], 6)
        self.assertEqual(acc['by_class'], {'embedded': 1, 'instance': 2, 'unresolved': 1, 'revision_of': 1, 'pair_recorded': 1, 'refused': 0})
        self.assertEqual(sum(x['rows'] for x in acc['by_type_provenance_kind']), 6)
        self.assertEqual(acc['revision_of_sources'][0]['rows'], 1)

    def test_a_manifest_without_the_accounting_is_refused(self):
        def go(m):
            del m['relationship_row_accounting']
        _rewrite_manifest(self.root, go)
        self.assertIn('artifact_count_mismatch', self.codes())

    def test_flipping_an_unresolved_none_endpoint_row_to_source_stated_fails(self):
        def go(r):
            r.update(provenance='SOURCE_STATED', source=self._invented_source(), claim_status='established')
        self._edit_row('unresolved', go)
        self.assertTrue(self.codes() & {'artifact_orphan_row', 'artifact_row_signature'})

    def test_an_unresolved_row_cannot_carry_a_source_a_method_or_lose_its_reason(self):
        for fn in (lambda r: r.__setitem__('source', self._invented_source()), lambda r: r.__setitem__('method', 'invented'),
                   lambda r: r.__setitem__('missing_evidence', ''), lambda r: r.pop('missing_evidence'),
                   lambda r: r.__setitem__('from_global', 'R-not-a-real-id')):
            self.setUp()
            self._edit_row('unresolved', fn)
            self.assertIn('artifact_row_signature', self.codes())

    def test_rewriting_the_source_of_a_revision_of_row_fails(self):
        self._edit_row('revision', lambda r: r.__setitem__('source', {'repo': 'x', 'revision': 'y', 'location': 'z'}))
        self.assertIn('artifact_row_signature', self.codes())

    def test_a_revision_of_row_must_name_a_revision_the_lineage_and_crosswalk_carry(self):
        self._edit_row('revision', lambda r: r.__setitem__('to', 'REV:' + '1' * 64))
        self.assertIn('artifact_row_signature', self.codes())
        self.setUp()
        self._edit_row('revision', lambda r: r.update(provenance='DERIVED'))
        self.assertIn('artifact_row_signature', self.codes())
        self.setUp()
        self._edit_row('revision', lambda r: r.update({'from': 'S-SYN-case-1-00000001', 'from_global': 'S-SYN-case-1-00000001'}))
        self.assertIn('artifact_row_signature', self.codes())

    def test_changing_provenance_confidence_or_method_of_an_unembedded_derived_row_is_caught(self):
        # an attacker who also recommits the counts is stopped by the signature for provenance and type; one who leaves the manifest alone by the committed counts
        for key in ('pair', 'instance1'):
            for field, value in (('confidence', 'low'), ('method', 'another method'), ('provenance', 'UNRESOLVED')):
                self.setUp()
                self._edit_row(key, lambda r: r.__setitem__(field, value), recommit=False)
                self.assertIn('artifact_count_mismatch', self.codes(), (key, field))
        self.setUp()
        self._edit_row('pair', lambda r: r.update(provenance='SOURCE_STATED', source=self._invented_source()))
        self.assertTrue(self.codes() & {'artifact_row_signature', 'artifact_orphan_row'})

    def test_editing_endpoints_or_names_of_an_instance_row_fails(self):
        self._edit_row('instance1', lambda r: r.update(to_global='S-SYN-case-1-00000001', to='S-SYN-case-1-00000001'))
        self.assertIn('artifact_row_signature', self.codes())
        self.setUp()
        self._edit_row('instance1', lambda r: r.update(**{'from': 'invented', 'from_global': 'invented'}))
        self.assertIn('artifact_row_signature', self.codes())
        self.setUp()
        self._edit_row('instance1', lambda r: r.update(source=self._invented_source()))
        self.assertIn('artifact_row_signature', self.codes())

    def test_instance_rows_must_total_the_recorded_count_per_scenario(self):
        self._append(dict(self.extra['instance1'], relationship_id='REL-b' + '0' * 13 + '99', **{'from': 'DI:SYN:9', 'from_global': 'DI:SYN:9'}))
        self.assertIn('artifact_row_signature', self.codes())
        self.setUp()
        rid = self.extra['instance2']['relationship_id']
        self.tamper('relationship_rows', lambda recs: recs.remove(next(r for r in recs if r['relationship_id'] == rid)))
        self.assertIn('artifact_row_signature', self.codes())

    def test_each_exemption_cannot_be_abused_to_add_a_fake_source_stated_row(self):
        src = self._invented_source()
        fakes = {
            'instance_type': self._fake(type='differential_instance->scenario', provenance='SOURCE_STATED', source=src),
            'revision_kind': self._fake(relation_kind='revision_of', provenance='SOURCE_STATED', source=src),
            'unknown_endpoint': self._fake(to_global='R-not-a-real-id', to='R-not-a-real-id', provenance='SOURCE_STATED', source=src),
            'none_endpoint': self._fake(to_global=None, to=None, provenance='SOURCE_STATED', source=src),
            'recorded_pair': self._fake(provenance='SOURCE_STATED', source=src, type='rule->rule'),
            'plain_orphan': self._fake(to_global='S-SYN-spec-1-00000004', to='S-SYN-spec-1-00000004'),
        }
        for name, row in fakes.items():
            self.setUp()
            self._append(row)
            self.assertTrue(self.codes() & {'artifact_orphan_row', 'artifact_row_signature'}, name)

    def test_an_unknown_endpoint_is_refused_not_exempted(self):
        self._append(self._fake(to_global='R-not-a-real-id', to='R-not-a-real-id'))
        self.assertIn('artifact_orphan_row', self.codes())

    def test_a_pair_recorded_row_must_match_the_recorded_relationship(self):
        self._edit_row('pair', lambda r: r.__setitem__('type', 'scenario->test_implementation'))
        self.assertIn('artifact_row_signature', self.codes())
        self.setUp()
        self._edit_row('pair', lambda r: r.__setitem__('relation_kind', 'unknown_kind'))
        self.assertIn('artifact_row_signature', self.codes())

    def test_deleting_an_unembedded_row_changes_a_committed_count(self):
        for key in ('unresolved', 'revision', 'pair', 'instance1'):
            self.setUp()
            rid = self.extra[key]['relationship_id']
            self.tamper('relationship_rows', lambda recs: recs.remove(next(r for r in recs if r['relationship_id'] == rid)), recommit=False)
            self.assertIn('artifact_count_mismatch', self.codes(), key)

    def test_changed_evidence_path_in_the_artifact_fails(self):
        def go(recs):
            recs[0]['artifact_commitment']['path'] = 'other/location.json'
        self.tamper('evidence_records', go)
        self.assertIn('artifact_index_mismatch', self.codes())

    def test_duplicate_evidence_record_is_refused(self):
        self.tamper('evidence_records', lambda recs: recs.append(copy.deepcopy(recs[0])))
        self.assertIn('artifact_duplicate_key', self.codes())

    def test_changed_crosswalk_native_id_in_the_artifact_fails(self):
        def go(recs):
            for r in recs:
                if (r['raw_set'], r['raw_index']) == ('SYN1', 0):
                    r['native_id'] = 'a name the entry never carried'
        self.tamper('crosswalk_rows', go)
        self.assertIn('artifact_index_mismatch', self.codes())

    def test_duplicate_crosswalk_row_in_the_artifact_is_refused(self):
        self.tamper('crosswalk_rows', lambda recs: recs.append(copy.deepcopy(recs[0])))
        self.assertTrue(self.codes() & {'artifact_duplicate_key', 'artifact_count_mismatch', 'artifact_index_mismatch'})

    def test_a_malformed_crosswalk_row_in_the_artifact_fails_the_schema(self):
        self.tamper('crosswalk_rows', lambda recs: recs[0].__setitem__('authority', 'granted'))
        self.assertIn('artifact_row_schema', self.codes())

    def test_a_different_gzip_of_identical_content_warns_but_does_not_fail(self):
        import gzip
        art = next(a for a in self.manifest['external_artifacts'] if a['kind'] == 'crosswalk_rows')
        path = self.root / art['path']
        data = gzip.decompress(path.read_bytes())
        other = gzip.compress(data, compresslevel=1, mtime=5)
        self.assertNotEqual(other, path.read_bytes())
        path.write_bytes(other)
        errors, _ = V.validate(str(self.root))
        self.assertEqual(errors, [])
        self.assertTrue(any('gzip file differs' in w for w in V.LAST_WARNINGS))

    def test_content_tamper_is_never_waved_through_as_a_gzip_difference(self):
        import gzip
        art = next(a for a in self.manifest['external_artifacts'] if a['kind'] == 'crosswalk_rows')
        path = self.root / art['path']
        data = bytearray(gzip.decompress(path.read_bytes()))
        data[len(data) // 2] ^= 0x01
        path.write_bytes(gzip.compress(bytes(data), mtime=0))
        self.assertTrue(self.codes() & {'artifact_hash_mismatch', 'artifact_unreadable'})

    def test_the_cli_prints_the_warning_line(self):
        import gzip
        import io
        import contextlib
        art = next(a for a in self.manifest['external_artifacts'] if a['kind'] == 'evidence_records')
        path = self.root / art['path']
        path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=0))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = V.main(['--root', str(self.root)])
        self.assertEqual(rc, 0)
        self.assertIn('WARNING artifact', buf.getvalue())


class SourcePins(Base):
    """The real catalogue's source revisions are pinned inside the validator; a combined pseudo-repository is refused."""
    def _real(self, repo='cogno-us/cognous-control-plane', rev='review-v0.1-g8-r10-20261022 0a41faa972699f7ec3063967a14cd9bdd3e67d27', sample=False):
        def go(m):
            m['synthetic_sample'] = sample
            for inv in m['source_inventory']:
                inv['source_repo_revisions'] = [{'repo': repo, 'revision': rev}]
        _rewrite_manifest(self.root, go)
        # the entries cite the same pinned source, as the real catalogue's entries do
        cite = {'repo': repo, 'revision': rev}
        for layer in ('rules', 'scenarios', 'tests', 'fixtures', 'lineage_sets'):
            self.edit(layer, lambda recs: [(r['source'].update(cite), [l.update(cite) for l in r.get('locations', [])]) for r in recs])
        self.edit('evidence', lambda recs: [r['source_commitment'].update(cite) for r in recs])

    def test_a_pinned_tag_commit_is_accepted(self):
        self._real()
        self.assertEqual(codes(self.root), set())

    def test_a_revision_outside_the_pinned_list_is_refused(self):
        self._real(rev='review-v0.1-g8-r10-20261022 ' + 'f' * 40)
        self.assertIn('source_revision_not_pinned', codes(self.root))

    def test_a_pinned_repository_with_a_free_text_revision_is_refused(self):
        self._real(rev='main')
        self.assertIn('source_revision_not_pinned', codes(self.root))

    def test_the_two_named_post_tag_heads_are_accepted(self):
        self._real(repo='cogno-us/cognous-stack-qualification', rev='4298247e860126d04d0bc44e1f2aef0fde1c4c97')
        self.assertEqual(codes(self.root), set())

    def test_an_entry_citing_an_unpinned_revision_or_repository_is_refused(self):
        self._real()
        self.assertEqual(codes(self.root), set())
        cases = (('rules', 'R-SYN-floor-a-00000001', {'revision': 'review-v0.1-g8-r10-20261022 ' + 'f' * 40}),
                 ('rules', 'R-SYN-floor-a-00000001', {'revision': 'main'}),
                 ('scenarios', 'S-SYN-case-1-00000001', {'repo': 'cogno-us/evil-fork'}),
                 ('tests', 'T-SYN-test-1-00000001', {'repo': 'example/synthetic-source'}))
        for layer, cid, change in cases:
            self.setUp()
            self._real()
            self.mutate(layer, cid, lambda r: r['source'].update(change))
            self.assertIn('source_revision_not_pinned', codes(self.root), (cid, change))

    def test_an_entry_or_evidence_record_may_read_unrecorded_but_only_for_a_pinned_repository(self):
        self._real()
        self.mutate('rules', 'R-SYN-floor-a-00000001', lambda r: r['source'].update(revision='unrecorded'))
        self.assertEqual(codes(self.root) - {'unresolved_accounting_mismatch'}, set())
        ev = self.dataset['evidence'][0]['evidence_digest']
        self.mutate('evidence', ev, lambda r: r['source_commitment'].update(repo='cogno-us/evil-fork', revision='unrecorded'))
        self.assertIn('source_revision_not_pinned', codes(self.root))

    def test_a_multi_repository_location_with_an_unpinned_revision_is_refused(self):
        self._real()
        self.mutate('fixtures', 'F-SYN-fixture-1-00000001', lambda r: r.__setitem__('locations', [{'repo': 'cogno-us/cognous-control-plane', 'revision': 'tip', 'path': 'a'}]))
        self.assertIn('source_revision_not_pinned', codes(self.root))

    def test_a_catalogue_naming_real_repositories_cannot_claim_to_be_a_synthetic_sample(self):
        self._real(sample=True)
        self.assertIn('synthetic_flag_on_real_catalogue', codes(self.root))

    def test_a_multi_pseudo_repository_is_refused_in_entries_and_evidence(self):
        self.mutate('scenarios', 'S-SYN-case-1-00000001', lambda r: r['source'].__setitem__('repo', 'multi:a/b,c/d'))
        self.assertIn('pseudo_repo', codes(self.root))
        self.setUp()
        ev = self.dataset['evidence'][0]['evidence_digest']
        self.mutate('evidence', ev, lambda r: r['source_commitment'].__setitem__('repo', 'multi:a/b,c/d'))
        self.assertIn('pseudo_repo', codes(self.root))


class ReportVerdictRendering(Base):
    """Composite historical verdicts are quoted without their unrecorded parts, in the report only."""
    def test_absent_parts_are_omitted_and_the_rendering_has_no_none_text(self):
        self.assertEqual(R._omit_absent_parts(' | expected_safety_property=None'), '(no recorded part)')
        self.assertEqual(R._omit_absent_parts('execution_status=executed | expected_safety_property=None'), 'execution_status=executed')
        self.assertEqual(R._omit_absent_parts('schema_valid=False; reference_errors=None; oracle_satisfied=True'), 'schema_valid=False; oracle_satisfied=True')
        self.assertEqual(R._omit_absent_parts('PASS'), 'PASS')
        self.assertEqual(R._omit_absent_parts('a=1 | b=2'), 'a=1 | b=2')

    def test_the_report_drops_the_absent_part_and_says_so_while_the_evidence_data_is_unchanged(self):
        ev = next(e for e in self.dataset['evidence'] if e['evidence_kind'] == 'run_result')
        raw = 'execution_status=executed | expected_safety_property=None'
        self.mutate('evidence', ev['evidence_digest'], lambda r: r.__setitem__('historical_verdict_verbatim', raw))
        manifest, layers = R._load(str(self.root))
        out = R.denominators(manifest, layers)
        quoted = out['denominators']['10_historical_verdicts_verbatim']
        self.assertEqual(quoted['quoted_from_historical_records_not_a_current_result']['execution_status=executed'], 1)
        self.assertNotIn(raw, quoted['quoted_from_historical_records_not_a_current_result'])
        self.assertIn('unrecorded', quoted['note'])
        self.assertNotIn('None', json.dumps(out))
        self.assertEqual(next(e for e in layers['evidence'] if e['evidence_digest'] == ev['evidence_digest'])['historical_verdict_verbatim'], raw)


class DenominatorRefinements(Base):
    def test_spec_cases_unexecuted_and_adversarial_are_three_figures_not_one(self):
        for basis in ('CAT-SPEC696', 'CAT-UNEXEC', 'CAT-ADV'):
            self.setUp()
            self.mutate('scenarios', 'S-SYN-spec-1-00000004', lambda r: r['annotations'].__setitem__('scenario_category_basis', basis))
            four = V.read_json(str(self.root / 'manifest.json'))['denominators']['ten_denominators']['4_adversarial_ideas_or_unexecuted_specifications']
            key = {'CAT-SPEC696': 'spec_cases', 'CAT-UNEXEC': 'unexecuted_other', 'CAT-ADV': 'adversarial'}[basis]
            self.assertEqual(four[key], 1)
            self.assertEqual(sum(four.values()), 1)
        classes = V.read_json(str(self.root / 'manifest.json'))['denominators']['scenario_classes_reported_separately']
        self.assertNotIn('adversarial_or_unexecuted_spec', classes)
        self.assertNotIn('logical', classes)

    def test_post_v01_logical_scenarios_are_counted_apart(self):
        self.mutate('scenarios', 'S-SYN-case-2-00000002', lambda r: r.__setitem__('release_scope', 'post_v0_1'))
        two = V.read_json(str(self.root / 'manifest.json'))['denominators']['ten_denominators']['2_logical_governance_scenarios']
        self.assertEqual((two['v0_1'], two['post_v0_1_reported_apart']), (1, 1))
        classes = V.read_json(str(self.root / 'manifest.json'))['denominators']['scenario_classes_reported_separately']
        self.assertEqual((classes['logical:v0_1'], classes['logical:post_v0_1_reported_apart']), (1, 1))

    def test_execution_identities_are_run_and_test_node_pairs_and_runs_are_named_runs(self):
        def ident(r):
            r['annotations']['execution_identity'] = ['run-1', 'suite.py::test_a']
        ev = self.dataset['evidence'][0]['evidence_digest']
        self.mutate('evidence', ev, ident)
        nine = V.read_json(str(self.root / 'manifest.json'))['denominators']['ten_denominators']['9_distinct_execution_identities']
        self.assertEqual(set(nine), {'distinct_run_and_test_node_pairs', 'distinct_runs', 'distinct_runs_with_run_results'})
        self.assertGreaterEqual(nine['distinct_run_and_test_node_pairs'], 1)
        self.assertNotIn('263', json.dumps(nine))

    def test_two_nodes_of_one_run_are_two_identities_and_one_run(self):
        evs = [e['evidence_digest'] for e in self.dataset['evidence']]
        self.mutate('evidence', evs[0], lambda r: (r.__setitem__('run_id', 'run-1'), r['annotations'].__setitem__('execution_identity', ['run-1', 'a.py::t1'])))
        self.mutate('evidence', evs[1], lambda r: (r.__setitem__('run_id', 'run-1'), r['annotations'].__setitem__('execution_identity', ['run-1', 'a.py::t2'])))
        nine = V.read_json(str(self.root / 'manifest.json'))['denominators']['ten_denominators']['9_distinct_execution_identities']
        self.assertEqual(nine['distinct_run_and_test_node_pairs'], 2)
        self.assertEqual(nine['distinct_runs'], 1)


class LoaderRound2(unittest.TestCase):
    def test_absent_parts_are_omitted_not_stringified(self):
        self.assertEqual(L._drop_absent_parts('expected_outcome=accept; expected_refusal=None; reason=because'), 'expected_outcome=accept; reason=because')
        self.assertEqual(L._drop_absent_parts('execution_status=unexecuted; observed_outcome=None; expected_safety_property=holds'), 'execution_status=unexecuted; expected_safety_property=holds')
        self.assertEqual(L._drop_absent_parts('a=1 | b=None | c=3'), 'a=1 | c=3')

    def test_other_text_is_kept_exactly(self):
        for t in ('type=None is quoted from a source message', 'plain text', 'a=1; b=2'):
            self.assertEqual(L._drop_absent_parts(t), t)
        self.assertEqual(L._drop_absent_parts('reason=value=None is fine'), 'reason=value=None is fine')
        self.assertIsNone(L._drop_absent_parts(None))

    def test_multi_pseudo_repo_is_replaced_by_each_constituent_location(self):
        e = {'canonical_id': 'S-x', 'source_repo': 'multi:o/a,o/b', 'source_revision': 'a' * 40, 'anchor': '/s/x',
             'locations': [{'source_repo': 'o/b', 'path': 'docs/b.json', 'source_revision': 'b' * 40, 'anchor': '/s/x'},
                           {'source_repo': 'o/a', 'path': 'docs/a.json', 'source_revision': 'a' * 40, 'anchor': '/s/x'}]}
        out = L._entry('scenarios', e, [], 'C', L.Problems())
        self.assertEqual((out['source']['repo'], out['source']['path'], out['source']['revision']), ('o/a', 'docs/a.json', 'a' * 40))
        self.assertEqual([(l['repo'], l['path'], l['revision']) for l in out['locations']], [('o/a', 'docs/a.json', 'a' * 40), ('o/b', 'docs/b.json', 'b' * 40)])
        self.assertNotIn('multi:', json.dumps(out))

    def test_multi_without_constituent_locations_is_reported_not_guessed(self):
        problems = L.Problems()
        out = L._entry('scenarios', {'canonical_id': 'S-y', 'source_repo': 'multi:o/a,o/b', 'source_revision': 'a' * 40}, [], 'C', problems)
        self.assertEqual(out['source']['repo'], 'unrecorded')
        self.assertIn(('C', 'multi_repo_without_constituent_locations'), problems.rows)

    def test_a_bare_pinned_tag_commit_is_cited_with_the_tag(self):
        repo = 'cogno-us/cognous-replay-bundle'
        self.assertEqual(L._cite(repo, '028f63d1c001f99580583888fa4b4e46d77a267b'), 'review-v0.1-g8-r10-20261022 028f63d1c001f99580583888fa4b4e46d77a267b')
        self.assertEqual(L._cite(repo, 'f' * 40), 'f' * 40)
        self.assertEqual(L._cite(repo, 'unrecorded'), 'unrecorded')
        self.assertEqual(L._cite('other/repo', '028f63d1c001f99580583888fa4b4e46d77a267b'), '028f63d1c001f99580583888fa4b4e46d77a267b')


class LoaderReview(unittest.TestCase):
    def setUp(self):
        Loader.setUp(self)

    def _canon(self):
        return json.loads((self.base / 'Z' / 'Z.canonical.json').read_text())

    def _set_canon(self, c):
        (self.base / 'Z' / 'Z.canonical.json').write_text(json.dumps(c))

    # MEDIUM 5: exact evidence vocabulary
    def _ev(self, **kw):
        e = {'digest': 'ab' * 32, 'artifact_location_and_digest': {'path': 'run.json'}, 'source_repo': 'o/r', 'source_revision': 'f' * 40}
        e.update(kw)
        problems = L.Problems()
        return L._evidence('Z', e, {}, problems), problems

    def test_non_independent_self_check_is_not_an_independent_record(self):
        ev, problems = self._ev(evidence_kind='non_independent_self_check', run_id='r1', verbatim_verdict='PASS')
        self.assertEqual(ev['evidence_kind'], 'unknown')
        self.assertNotEqual(ev['evidence_kind'], 'independent_qualification_record')
        self.assertIn(('Z', 'evidence_kind_outside_vocabulary'), problems.rows)

    def test_exact_vocabulary_maps(self):
        self.assertEqual(self._ev(evidence_kind='recorded_execution_result')[0]['evidence_kind'], 'run_result')
        self.assertEqual(self._ev(evidence_kind='validation_statement_claim')[0]['evidence_kind'], 'validation_claim')
        self.assertEqual(self._ev(evidence_kind='independent_qualification_record')[0]['evidence_kind'], 'independent_qualification_record')

    def test_unknown_kind_never_becomes_a_run_result(self):
        ev, problems = self._ev(evidence_kind='something_new', run_id='r1', verbatim_verdict='PASS')
        self.assertEqual(ev['evidence_kind'], 'unknown')

    def test_missing_kind_is_classified_by_structure_or_left_unknown(self):
        ev, _ = self._ev(run_id='r1', original_verdict='PASS')
        self.assertEqual(ev['evidence_kind'], 'run_result')
        self.assertIn('structural', ev['annotations']['evidence_kind_basis'])
        ev, problems = self._ev()
        self.assertEqual(ev['evidence_kind'], 'unknown')
        self.assertIn(('Z', 'evidence_kind_unclassified'), problems.rows)

    def test_verdict_prefers_the_verbatim_field(self):
        ev, _ = self._ev(evidence_kind='recorded_execution_result', raw_result_and_original_verdict='free text', verbatim_verdict='the_verdict')
        self.assertEqual(ev['historical_verdict_verbatim'], 'the_verdict')

    # MEDIUM 6: shard pointers
    def test_pointer_cannot_leave_the_partition_directory(self):
        (self.base / 'outside.json').write_text(json.dumps({'entries': []}))
        for bad in ('../outside.json', '/etc/hostname', 'parts/../../outside.json'):
            c = self._canon()
            c['rules'] = [{'file': bad}]
            self._set_canon(c)
            with self.assertRaises(L.LoadRefusal):
                L.assemble(str(self.base), ['Z'])

    def test_pointer_sha256_and_count_are_verified(self):
        import hashlib
        data = (self.base / 'Z' / 'parts' / 'L1.json').read_bytes()
        good = hashlib.sha256(data).hexdigest()
        c = self._canon()
        c['rules'] = [{'file': 'parts/L1.json', 'sha256': good, 'items': 1}]
        self._set_canon(c)
        self.assertEqual(len(L.assemble(str(self.base), ['Z'])['rules']), 1)
        c['rules'] = [{'file': 'parts/L1.json', 'sha256': '0' * 64, 'items': 1}]
        self._set_canon(c)
        with self.assertRaises(L.LoadRefusal):
            L.assemble(str(self.base), ['Z'])
        c['rules'] = [{'file': 'parts/L1.json', 'sha256': good, 'items': 7}]
        self._set_canon(c)
        with self.assertRaises(L.LoadRefusal):
            L.assemble(str(self.base), ['Z'])

    # MEDIUM 7: same id, different content
    def test_same_id_same_identity_but_different_content_is_refused(self):
        shutil.copytree(self.base / 'Z', self.base / 'Y')
        for fn in ('canonical', 'crosswalk', 'evidence-index'):
            (self.base / 'Y' / ('Z.%s.json' % fn)).rename(self.base / 'Y' / ('Y.%s.json' % fn))
        p = json.loads((self.base / 'Y' / 'parts' / 'L1.json').read_text())
        p['entries'][0]['classification'] = 'advisory'
        (self.base / 'Y' / 'parts' / 'L1.json').write_text(json.dumps(p))
        with self.assertRaises(L.LoadRefusal):
            L.assemble(str(self.base), ['Z', 'Y'])

    def test_same_id_with_identical_content_merges_refs_only(self):
        shutil.copytree(self.base / 'Z', self.base / 'Y')
        for fn in ('canonical', 'crosswalk', 'evidence-index'):
            (self.base / 'Y' / ('Z.%s.json' % fn)).rename(self.base / 'Y' / ('Y.%s.json' % fn))
        ds = L.assemble(str(self.base), ['Z', 'Y'])
        self.assertEqual(len(ds['rules']), 1)

    def test_merge_basis_and_provenance_are_retained(self):
        g1 = Path(self.tmp.name) / 'G1'
        g1.mkdir()
        def ent(cid):
            return {'catalogue_id': cid, 'aliases': [], 'native_ids': [cid + '-native'], 'raw_refs': [], 'lineage': [], 'annotations': {},
                    '_evidence_raw': [], '_refs': {}}
        ds = {'layers': {'rules': {'R-A': ent('R-A'), 'R-B': ent('R-B')}, 'scenarios': {}, 'tests': {}, 'fixtures': {}}, 'crosswalk': []}
        (g1 / 'G1.merges.000.json').write_text(json.dumps({'merges': [{
            'merge_id': 'M-1', 'rule': 'ALIAS_OF', 'caveat': None, 'primary': {'id': 'R-A', 'partition': 'Z'}, 'alias': {'id': 'R-B', 'partition': 'Z'},
            'provenance': {'identity': {'class': 'SOURCE_STATED', 'quote': 'the same row', 'locator': 'o/r@f path#1'},
                           'check': {'class': 'DERIVED', 'method': 'digest equal'}}}]}))
        L.apply_g1(ds, str(g1), L.Problems())
        merged = ds['layers']['rules']['R-A']['annotations']['merged_from'][0]
        self.assertIn('R-B', ds['layers']['rules']['R-A']['aliases'])
        self.assertEqual(merged['id'], 'R-B')
        self.assertIn('SOURCE_STATED', merged['basis'])
        self.assertEqual(merged['provenance']['identity']['locator'], 'o/r@f path#1')
        self.assertEqual(merged['provenance']['check']['method'], 'digest equal')

    def test_merge_without_stated_provenance_is_refused(self):
        g1 = Path(self.tmp.name) / 'G1b'
        g1.mkdir()
        (g1 / 'G1.merges.000.json').write_text(json.dumps({'merges': [{'merge_id': 'M-1', 'primary': {'id': 'R-A', 'partition': 'Z'}, 'alias': {'id': 'R-B', 'partition': 'Z'}, 'provenance': {}}]}))
        with self.assertRaises(L.LoadRefusal):
            L.apply_g1({'layers': {'rules': {}, 'scenarios': {}, 'tests': {}, 'fixtures': {}}, 'crosswalk': []}, str(g1), L.Problems())

    # real-shape dispositions
    def test_partition_c_evidence_disposition_is_understood(self):
        row = {'raw_index': 3, 'raw_digest': 'ab' * 32, 'tier': 'EXECUTION_EVIDENCE', 'disposition': 'EVIDENCE_INDEXED:' + 'ab' * 32}
        out = L._norm_row('C', row, L.Problems())
        self.assertEqual((out['disposition'], out['target']), ('TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', 'ab' * 32))

    def test_unknown_disposition_is_unresolved_and_reported(self):
        problems = L.Problems()
        out = L._norm_row('C', {'raw_index': 1, 'raw_digest': 'cd' * 32, 'tier': 'FIXTURE', 'disposition': 'MADE_UP'}, problems)
        self.assertEqual(out['disposition'], 'UNRESOLVED')
        self.assertIn(('C', 'unknown_disposition'), problems.rows)

    def test_loader_cli_builds_a_compact_catalogue_that_validates(self):
        out = Path(self.tmp.name) / 'cli-out'
        art = Path(self.tmp.name) / 'cli-art'
        rc = L.main(['--in', str(self.base), '--partitions', 'Z', '--out', str(out), '--layout', 'compact', '--artifacts', str(art),
                     '--problems', str(Path(self.tmp.name) / 'problems.json')])
        self.assertEqual(rc, 0)
        errors, manifest = V.validate(str(out), artifacts=str(art))
        self.assertEqual(errors, [])
        rec = manifest['regeneration']
        self.assertEqual(rec['inputs']['partitions'], ['Z'])
        self.assertGreater(rec['inputs']['input_file_count'], 0)
        out2 = Path(self.tmp.name) / 'cli-out2'
        art2 = Path(self.tmp.name) / 'cli-art2'
        L.main(['--in', str(self.base), '--partitions', 'Z', '--out', str(out2), '--layout', 'compact', '--artifacts', str(art2)])
        self.assertEqual(V.read_json(str(out / 'manifest.json'))['digest'], V.read_json(str(out2 / 'manifest.json'))['digest'])

    def test_raw_set_comes_from_the_raw_file_name(self):
        pr = L.Problems()
        self.assertEqual(L._raw_set('A', 'A2-hub-governance-extension.json', pr), 'A2')
        self.assertEqual(L._raw_set('A', 'A-hub-governance.json', pr), 'A')
        self.assertEqual(L._raw_set('C', 'C3', pr), 'C3')
        self.assertEqual(L._raw_set('C', None, pr), 'C')
        self.assertEqual(L._raw_set('C', 'D-other.json', pr), 'C')
        self.assertIn(('C', 'raw_file_not_of_partition'), pr.rows)

    def test_normalizer_forms_map_only_through_the_rows_own_statement(self):
        pr = L.Problems()
        base = {'raw_index': 1, 'raw_digest': 'ab' * 32}
        out = L._norm_row('D', dict(base, tier='PARAMETRIZED_INSTANCE', disposition='ATTACHED_TO:T-x', attach_kind='parametrized_instance',
                                    disposition_legacy='TEST_INSTANCE_OR_EXECUTION_OCCURRENCE:T-x'), pr)
        self.assertEqual((out['disposition'], out['target']), ('TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', 'T-x'))
        out = L._norm_row('D', dict(base, tier='FIXTURE', disposition='ATTACHED_TO:F-x', attach_kind='byte_identical_location'), pr)
        self.assertEqual((out['disposition'], out['target']), ('ALIAS_OF', 'F-x'))
        out = L._norm_row('D', dict(base, tier='RULE_ADJACENT', disposition='SOURCE_REFERENCE_ONLY'), pr)
        self.assertEqual(out['disposition'], 'SOURCE_ONLY_ARTIFACT')
        out = L._norm_row('C', dict(base, tier='FIXTURE', disposition='ATTACHED_TO', target='F-y'), pr)
        self.assertEqual((out['disposition'], out['target']), ('UNRESOLVED', None))
        self.assertIn(('C', 'disposition_form_without_mapping'), pr.rows)

    def test_loader_cli_refuses_missing_arguments(self):
        self.assertEqual(L.main(['--in', str(self.base)]), 2)


if __name__ == '__main__':
    unittest.main()
