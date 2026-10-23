"""Tests for the 2.3 disposition corrections (architect decisions Q7 to Q10).

Developer-owned, non-authorizing; not independent Qualification evidence. Release and production
remain on HOLD. Covers the typed dispositions (not_applicable, abstained, error), the explicit
failure-path surrogates, input_read semantics and the verify_document crash. Profile /1 semantics
run through the internal registry view as in test_mandatory_manifest_v1.py (no registry code, nothing
activated); /0 behavior is checked through the public function. Synthetic fixtures; no effects.
"""
import copy
import os
import unittest

from tools import mandatory_checks as mc
from tools import registry_records as rr
import test_mandatory_manifest_v1 as v1

S05 = v1.S05
REFUTED_V1 = ('The required input was not read because the governing V1 premise was explicitly refuted '
              'under the applicable supported profile; the refutation and its evidence are retained.')
A, B, C = v1.A, v1.B, v1.C


def manifest_with_surrogate(cid=C, condition='no_items_examined', sources=('s1',)):
    m = v1.make_manifest()
    m['surrogates'] = [dict(check_id=cid, failure_condition=condition, source_ids=list(sources))]
    return v1.redigest(m)


class Base(v1.Base):
    pass


class TypedDispositions(Base):
    def test_abstained_is_a_fifth_outcome_in_profile_1_only(self):
        self.assertEqual(mc.OUTCOMES, ('passed', 'failed', 'not_applicable', 'error'))
        self.assertEqual(mc.OUTCOMES_1, mc.OUTCOMES + ('abstained',))
        m = v1.make_manifest()
        ex = v1.executed_for(m, **{B: dict(outcome='abstained', reason='input_absent:destination_ledger')})
        report = self.seam(executed=ex)
        self.assertEqual(report['counts']['abstained'], 1)
        self.assertEqual(report['counts']['passed'], 2)
        row = next(r for r in report['checks'] if r['check_id'] == B)
        self.assertEqual((row['outcome'], row['reason'], row['result_established']),
                         ('abstained', 'input_absent:destination_ledger', False))

    def test_abstained_is_never_a_pass_and_completeness_is_not_success(self):
        m = v1.make_manifest()
        ex = v1.executed_for(m, **{A: dict(outcome='abstained', reason='tier_unavailable:x'),
                                   B: dict(outcome='error'), C: dict(outcome='failed')})
        report = self.seam(executed=ex)
        self.assertTrue(report['complete'])             # accountable outcomes, nothing more
        self.assertEqual(report['counts']['passed'], 0)
        by = {r['check_id']: r['result_established'] for r in report['checks']}
        self.assertEqual(by, {A: False, B: False, C: True})   # abstained, error, failed
        self.assertNotIn('verdict', str(report))
        # established results: passed and failed only; scope dispositions are neither
        ex = v1.executed_for(m, skip=(B, C), **{A: dict(outcome='passed')})
        report = self.seam(executed=ex, dispositions=[v1.disposition(m, B), v1.disposition(m, C)])
        self.assertEqual([r['result_established'] for r in report['checks']], [True, None, None])
        ex = v1.executed_for(m, **{B: dict(outcome='not_applicable', reason='r.one')})
        row = next(r for r in self.seam(executed=ex)['checks'] if r['check_id'] == B)
        self.assertIsNone(row['result_established'])

    def test_abstained_needs_its_could_not_check_reason(self):
        m = v1.make_manifest()
        for reason in (None, '', '   '):
            ex = v1.executed_for(m, **{B: dict(outcome='abstained', reason=reason)})
            self.refuses_seam('schema_invalid', executed=ex)
        ex = v1.executed_for(m, **{B: dict(outcome='abstained', reason=5)})
        self.refuses_seam('schema_invalid', executed=ex)

    def test_error_may_carry_a_diagnostic_cause_or_none(self):
        m = v1.make_manifest()
        for reason in (None, 'verifier_error:ValueError'):
            ex = v1.executed_for(m, **{B: dict(outcome='error', reason=reason)})
            report = self.seam(executed=ex)
            row = next(r for r in report['checks'] if r['check_id'] == B)
            self.assertEqual((row['outcome'], row['reason'], row['result_established']),
                             ('error', reason, False))
        ex = v1.executed_for(m, **{B: dict(outcome='error', reason='  ')})
        self.refuses_seam('schema_invalid', executed=ex)

    def test_reason_stays_null_for_passed_and_failed(self):
        m = v1.make_manifest()
        for outcome in ('passed', 'failed'):
            ex = v1.executed_for(m, **{B: dict(outcome=outcome, reason='x')})
            self.refuses_seam('schema_invalid', executed=ex)

    def test_untyped_or_lookalike_outcomes_fail_closed(self):
        m = v1.make_manifest()
        for outcome in ('unknown', 'abstain', 'Abstained', 'skipped', 'inapplicable', 'not-applicable',
                        'could_not_check', ''):
            ex = v1.executed_for(m, **{B: dict(outcome=outcome)})
            self.refuses_seam('invalid_outcome', executed=ex)

    def test_abstained_is_not_not_applicable(self):
        m = v1.make_manifest()
        # an abstention reason is not an inapplicability reason, and a not_applicable reason is closed
        ex = v1.executed_for(m, **{B: dict(outcome='not_applicable', reason='input_absent:destination_ledger')})
        self.refuses_seam('not_applicable_reason_not_allowed', executed=ex)
        # an abstained result does not close a check that also has a disposition
        ex = v1.executed_for(m, skip=(C,), **{B: dict(outcome='abstained', reason='x')})
        self.refuses_seam('duplicate_result', executed=ex,
                          dispositions=[v1.disposition(m, B), v1.disposition(m, C)])
        # absence is not abstention either
        self.refuses_seam('skipped_mandatory_check', executed=v1.executed_for(m, skip=(B,)))

    def test_profile_0_is_unchanged_and_refuses_abstained(self):
        m = v1.unconditional_only()
        m0 = copy.deepcopy(m)
        m0.update(profile=mc.PROFILE, schema_version=0)
        del m0['predicates'], m0['surrogates']
        for c in m0['checks']:
            del c['applicability']
        v1.redigest(m0)
        rec = v1.make_record(m0)
        ok = mc.check_completeness(m0, rec, v1.executed_for(m0), floor_check_ids=v1.FLOOR)
        self.assertEqual(ok['counts'], {'passed': 1, 'failed': 0, 'not_applicable': 0, 'error': 0})
        self.assertEqual(set(ok), {'manifest_digest', 'record_digest', 'complete', 'counts', 'checks'})
        self.assertEqual(set(ok['checks'][0]), {'check_id', 'outcome', 'reason'})
        ex = v1.executed_for(m0, **{A: dict(outcome='abstained', reason='x')})
        self.refuses('invalid_outcome', mc.check_completeness, m0, rec, ex, floor_check_ids=v1.FLOOR)
        ex = v1.executed_for(m0, **{A: dict(outcome='error', reason='cause')})
        self.refuses('schema_invalid', mc.check_completeness, m0, rec, ex, floor_check_ids=v1.FLOOR)
        m0s = copy.deepcopy(m0)
        m0s['surrogates'] = []
        self.refuses('schema_invalid', mc.validate_manifest, v1.redigest(m0s))

    def test_refusal_set_is_unchanged(self):
        self.assertEqual(len(mc.REFUSAL_CODES), 26)


class Surrogates(Base):
    def test_valid_surrogate_and_digest_binding(self):
        m = manifest_with_surrogate()
        self.assertEqual(mc.validate_manifest(m), m['digest'])
        self.assertNotEqual(m['digest'], v1.make_manifest()['digest'])
        m['surrogates'][0]['failure_condition'] = 'run_record_unparsed_or_checker_crash'
        self.refuses('digest_mismatch', mc.validate_manifest, m)

    def test_surrogate_shape_is_closed(self):
        bad = [
            lambda s: s.update(extra=1),
            lambda s: s.pop('source_ids'),
            lambda s: s.update(failure_condition='other'),
            lambda s: s.update(failure_condition=None),
            lambda s: s.update(source_ids=[]),
            lambda s: s.update(source_ids=['s2', 's1']),
            lambda s: s.update(source_ids=['s1', 's1']),
            lambda s: s.update(check_id=''),
            lambda s: s.update(check_id=None),
            lambda s: s.update(check_id='chk.nope'),   # not a manifest check
            lambda s: s.update(check_id=A),            # an unconditional check cannot be a surrogate
        ]
        for fn in bad:
            m = manifest_with_surrogate()
            fn(m['surrogates'][0])
            self.refuses('schema_invalid', mc.validate_manifest, v1.redigest(m))
        m = manifest_with_surrogate(sources=('s9',))
        self.refuses('unknown_source', mc.validate_manifest, m)
        m = manifest_with_surrogate()
        m['surrogates'].append(dict(m['surrogates'][0]))
        self.refuses('schema_invalid', mc.validate_manifest, v1.redigest(m))
        m = manifest_with_surrogate()
        m['surrogates'] = None
        self.refuses('schema_invalid', mc.validate_manifest, v1.redigest(m))

    def test_a_surrogate_result_is_abstained_or_error_with_its_trigger(self):
        m = manifest_with_surrogate()
        for outcome in ('abstained', 'error'):
            ex = v1.executed_for(m, **{C: dict(outcome=outcome, reason='tier_unavailable:no_items_examined')})
            report = self.seam(manifest=m, executed=ex)
            row = next(r for r in report['checks'] if r['check_id'] == C)
            self.assertEqual((row['outcome'], row['surrogate'], row['reason'], row['result_established']),
                             (outcome, 'no_items_examined', 'tier_unavailable:no_items_examined', False))
        # negative controls: never an ordinary successful execution
        for outcome, reason in (('passed', None), ('failed', None), ('not_applicable', None)):
            ex = v1.executed_for(m, **{C: dict(outcome=outcome, reason=reason)})
            self.refuses_seam('invalid_outcome', manifest=m, executed=ex)
        # an error surrogate must retain the original trigger, not drop it
        for reason in (None,):
            ex = v1.executed_for(m, **{C: dict(outcome='error', reason=reason)})
            self.refuses_seam('schema_invalid', manifest=m, executed=ex)
        # the same outcomes are fine for a non-surrogate check (control)
        ex = v1.executed_for(m, **{B: dict(outcome='error'), C: dict(outcome='abstained', reason='x')})
        self.assertEqual(self.seam(manifest=m, executed=ex)['counts']['surrogate'], 1)
        ex = v1.executed_for(manifest_with_surrogate(cid=B), **{B: dict(outcome='abstained', reason='x')})
        self.assertEqual(self.seam(manifest=manifest_with_surrogate(cid=B), executed=ex)['counts']['surrogate'], 1)

    def test_surrogate_never_masks_an_error_and_is_tallied_separately(self):
        m = manifest_with_surrogate()
        ex = v1.executed_for(m, **{C: dict(outcome='error', reason='verifier_error:ValueError')})
        report = self.seam(manifest=m, executed=ex)
        self.assertEqual(report['counts']['error'], 1)       # still visible as an error
        self.assertEqual(report['counts']['surrogate'], 1)
        self.assertEqual(report['counts']['passed'], 2)      # not counted as a successful execution
        self.assertEqual([r['surrogate'] for r in report['checks']], [None, None, 'no_items_examined'])

    def test_surrogate_is_no_independent_substitute(self):
        m = manifest_with_surrogate()
        ex = v1.executed_for(m, skip=(B,), **{C: dict(outcome='abstained', reason='x')})
        self.refuses_seam('skipped_mandatory_check', manifest=m, executed=ex)
        # a surrogate may still be closed by its own disposition on a normal run
        ex = v1.executed_for(m, skip=(C,))
        report = self.seam(manifest=m, executed=ex, dispositions=[v1.disposition(m, C)])
        self.assertEqual(report['counts']['surrogate'], 0)
        self.assertIsNone(report['checks'][2]['surrogate'])

    def test_surrogate_cannot_be_a_floor_check(self):
        m = manifest_with_surrogate()
        rec = v1.make_record(v1.unconditional_only())
        self.refuses('floor_check_conditional', mc.check_completeness, m, rec, v1.executed_for(m),
                     floor_check_ids=[A, C])


class CandidateDispositions(unittest.TestCase):
    def setUp(self):
        self.m = v1.load_v1()
        self.digest = mc.validate_manifest(self.m)
        self.by = {c['check_id']: c for c in self.m['checks']}
        self.preds = {p['predicate_id']: p for p in self.m['predicates']}

    def complete(self, executed, dispositions=None):
        return mc._complete(self.m, self.digest, 1, v1.seam_registry(self.m), executed, dispositions)

    def test_digest_pin_and_candidate_status(self):
        self.assertEqual(self.m['digest'],
                         'sha256:60af60a75f731f05838b84da84dabadec01ce0443054933e7bec7530d3b59140')
        self.assertEqual(rr.record_digest(self.m), self.m['digest'])
        self.assertEqual(self.m['manifest_id'], 'ocs-mandatory-manifest-r1-candidate-2')
        with open(v1.V1_MD, encoding='utf-8') as fh:
            text = fh.read()
        self.assertIn(self.m['digest'], text)
        self.assertNotIn('sha256:9ab1cc13', text.split('## Disposition corrections')[0])
        for word in ('CANDIDATE', 'not frozen, adopted or qualified'):
            self.assertIn(word, text)

    def test_the_two_surrogates_are_explicit_and_cited(self):
        sur = self.m['surrogates']
        self.assertEqual([(s['check_id'], s['failure_condition']) for s in sur],
                         [('v1.structure.run-record', 'run_record_unparsed_or_checker_crash'),
                          ('v2.coverage.items-examined', 'no_items_examined')])
        sources = {s['source_id']: s for s in self.m['sources']}
        for s in sur:
            self.assertEqual(self.by[s['check_id']]['applicability']['kind'], 'required_when_applicable')
            for sid in s['source_ids']:
                self.assertEqual(sources[sid]['revision'], v1.VERIFIER_REV)
                self.assertEqual(sources[sid]['path'], 'src/cognous_verify/engine.py')

    def test_surrogate_semantics_on_the_candidate(self):
        conditional = [c for c in self.by if self.by[c]['applicability']['kind'] != 'unconditional']
        keep = {'v1.structure.run-record', 'v2.coverage.items-examined'}
        ex = v1.executed_for(self.m, skip=[c for c in conditional if c not in keep],
                             **{'v1.structure.run-record': dict(outcome='abstained',
                                                                reason='tier_unavailable:run_record_not_parsed'),
                                'v2.coverage.items-examined': dict(outcome='error',
                                                                   reason='verifier_error:KeyError')})
        disp = [dict(check_id=c, predicate=self.by[c]['applicability']['predicate'],
                     justification=self.preds[self.by[c]['applicability']['predicate']]['justifications'][0],
                     evaluator_id=self.by[c]['evaluator_id'], evaluator_version=self.by[c]['evaluator_version'])
                for c in conditional if c not in keep]
        report = self.complete(ex, disp)
        self.assertEqual((report['counts']['surrogate'], report['counts']['abstained'],
                          report['counts']['error'], report['counts']['passed']), (2, 1, 1, 8))
        bad = copy.deepcopy(ex)
        next(e for e in bad if e['check_id'] == 'v1.structure.run-record').update(outcome='passed', reason=None)
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            self.complete(bad, disp)
        self.assertEqual(ctx.exception.code, 'invalid_outcome')

    def test_input_read_is_unconditional_and_refuted_v1_is_not_a_justification(self):
        for kind in self.m['input_kinds']:
            c = self.by['input_read.' + kind]
            self.assertEqual(c['applicability'], {'kind': 'unconditional'})
            self.assertEqual(c['not_applicable_reasons'], [])
        for p in self.m['predicates']:
            self.assertFalse(any(cid.startswith('input_read.') for cid in
                                 [c['check_id'] for c in self.m['checks']
                                  if c['applicability'].get('predicate') == p['predicate_id']]))
            for j in p['justifications']:
                self.assertFalse('v1' in j and 'refut' in j)   # no refuted-V1 exemption code
        conditional = [c for c in self.by if self.by[c]['applicability']['kind'] != 'unconditional']
        base = v1.executed_for(self.m, skip=conditional)
        # the quoted wording as a disposition or a not_applicable reason is refused (negative controls)
        d = dict(check_id='input_read.mandate', predicate='record_class_control_plane_journal',
                 justification=REFUTED_V1, evaluator_id='cognous-verify.rules_journal', evaluator_version=1)
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            self.complete([e for e in base if e['check_id'] != 'input_read.mandate'], [d])
        self.assertEqual(ctx.exception.code, 'inapplicable_not_permitted')
        ex = copy.deepcopy(base)
        next(e for e in ex if e['check_id'] == 'input_read.mandate').update(outcome='not_applicable',
                                                                          reason=REFUTED_V1)
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            self.complete(ex)
        self.assertEqual(ctx.exception.code, 'not_applicable_reason_not_allowed')
        # missing input / unresolved condition is reported as abstained (or error), never passed
        ex = copy.deepcopy(base)
        next(e for e in ex if e['check_id'] == 'input_read.mandate').update(
            outcome='abstained', reason='input_not_read:mandate')
        report = mc._complete(self.m, self.digest, 1, v1.seam_registry(self.m), ex,
                              [dict(check_id=c, predicate=self.by[c]['applicability']['predicate'],
                                    justification=self.preds[self.by[c]['applicability']['predicate']][
                                        'justifications'][0], evaluator_id=self.by[c]['evaluator_id'],
                                    evaluator_version=self.by[c]['evaluator_version'])
                               for c in conditional])
        row = next(r for r in report['checks'] if r['check_id'] == 'input_read.mandate')
        self.assertEqual((row['outcome'], row['result_established']), ('abstained', False))
        self.assertEqual(report['counts']['passed'], 7)

    def test_verify_document_crash_is_error_never_inapplicable(self):
        pred = self.preds['run_record_parsed_without_checker_crash']
        self.assertEqual(pred['justifications'], ['run_record_not_parsed'])
        for p in self.m['predicates']:
            for j in p['justifications']:
                self.assertNotIn('crash', j)
        conditional = [c for c in self.by if self.by[c]['applicability']['kind'] != 'unconditional']
        base = v1.executed_for(self.m, skip=conditional)
        # a crash disposition (the removed code) on v1.structure is refused
        d = dict(check_id='v1.structure', predicate='run_record_parsed_without_checker_crash',
                 justification='checker_crashed_on_run_record', evaluator_id=self.by['v1.structure']['evaluator_id'],
                 evaluator_version=self.by['v1.structure']['evaluator_version'])
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            self.complete(base, [d])
        self.assertEqual(ctx.exception.code, 'justification_not_allowed')
        # control: the not-parsed justification is still source-backed and accepted for that predicate
        self.assertEqual(self.complete(v1.executed_for(self.m, skip=conditional), [
            dict(d, justification='run_record_not_parsed')] + [
            dict(check_id=c, predicate=self.by[c]['applicability']['predicate'],
                 justification=self.preds[self.by[c]['applicability']['predicate']]['justifications'][0],
                 evaluator_id=self.by[c]['evaluator_id'], evaluator_version=self.by[c]['evaluator_version'])
            for c in conditional if c != 'v1.structure'])['counts']['inapplicable'], 50)
        # not_applicable outcome with a crash reason is refused
        ex = v1.executed_for(self.m, skip=['v1.structure'] + [c for c in conditional])
        ex.append(dict(check_id='v1.structure', outcome='not_applicable', reason='checker_crashed_on_run_record',
                       evaluator_id=d['evaluator_id'], evaluator_version=d['evaluator_version']))
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            self.complete(ex)
        self.assertEqual(ctx.exception.code, 'not_applicable_reason_not_allowed')
        # a crash with no recorded outcome for the unproduced checks is incomplete, not inapplicable
        only = v1.executed_for(self.m, skip=[c for c in conditional if c not in ('v1.structure',
                                                                                  'v1.structure.run-record')],
                               **{'v1.structure': dict(outcome='error', reason='verifier_error:ValueError'),
                                  'v1.structure.run-record': dict(outcome='error',
                                                                  reason='verifier_error:ValueError')})
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            self.complete(only)
        self.assertEqual(ctx.exception.code, 'skipped_mandatory_check')
        self.assertNotIn('v1.structure,', str(ctx.exception).split(':', 1)[1] + ',')
        # every check the crash prevented is reported as error: complete, counted as error, no success
        allerr = {c: dict(outcome='error', reason='verifier_error:ValueError') for c in conditional}
        report = self.complete(v1.executed_for(self.m, **allerr))
        self.assertEqual((report['counts']['error'], report['counts']['inapplicable'],
                          report['counts']['surrogate']), (50, 0, 2))
        self.assertTrue(all(r['result_established'] is False for r in report['checks']
                            if r['outcome'] == 'error'))


class V0DataUnchanged(unittest.TestCase):
    def test_v0_data_and_digest(self):
        v0 = v1.load_v0()
        self.assertEqual(v0['digest'], v1.V0_DIGEST)
        self.assertEqual(rr.record_digest(v0), v1.V0_DIGEST)
        self.assertNotIn('surrogates', v0)
        self.assertEqual(mc.validate_manifest(v0, pin=v1.V0_DIGEST), v1.V0_DIGEST)


if __name__ == '__main__':
    unittest.main()
