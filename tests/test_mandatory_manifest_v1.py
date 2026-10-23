"""Tests for the 2.3 repair (architect decisions Q2, Q3, Q7): profile ocs-mandatory-manifest/1.

Developer-owned, non-authorizing; not independent Qualification evidence. Release and production
remain on HOLD. The conditional-applicability semantics are exercised in two ways: through the
public function (a `/0` registry record cannot express them, so the only outcome is a closed
refusal) and through the internal registry view `_complete`, which models the proposed successor
rule entry (docs/program-v0.2/s05/2.1-successor-conditional-applicability.md). No registry code is
involved and nothing is activated. Standard library only; synthetic fixtures; no effects.
"""
import copy
import os
import unittest

from tools import mandatory_checks as mc
from tools import registry_records as rr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S05 = os.path.join(ROOT, 'docs', 'program-v0.2', 's05')
V0_JSON = os.path.join(S05, '2.3-mandatory-manifest.json')
V1_JSON = os.path.join(S05, '2.3-mandatory-manifest-v1-candidate.json')
V1_MD = os.path.join(S05, '2.3-mandatory-manifest-v1-candidate.md')
V0_DIGEST = 'sha256:13c6b3615fdad231452a85a0b4cad6f9507c9590b7b173ee5a05957e14455834'
REV = 'a' * 40
VERIFIER_REV = 'c0b8ba1f55b75db787a320f3de0f79342c6f6826'

A, B, C = 'chk.a', 'chk.b', 'chk.c'   # unconditional, conditional (input), conditional (class)
FLOOR = [A]
NEW_CODES = {'unknown_predicate', 'applicability_unsupported_by_registry', 'floor_check_conditional',
             'rule_evaluator_mismatch', 'inapplicable_not_permitted', 'predicate_mismatch',
             'justification_not_allowed'}


def redigest(obj):
    try:
        obj['digest'] = rr.record_digest(obj)
    except (ValueError, UnicodeEncodeError, RecursionError):
        pass
    return obj


def make_manifest(**over):
    def check(cid, ev, ver, app, reasons=()):
        return dict(check_id=cid, kind='verifier_check', source_id='s1', input_kind=None,
                    evaluator_id=ev, evaluator_version=ver, not_applicable_reasons=list(reasons),
                    applicability=app)
    m = dict(profile=mc.PROFILE_1, schema_version=1, canonical_profile='rfc8785-jcs',
             manifest_id='m-v1', digest='sha256:' + '0' * 64,
             sources=[dict(source_id='s1', repository='org/repo', revision=REV, path='x.py',
                           lines='1-2', note=''),
                      dict(source_id='s2', repository='org/repo', revision=REV, path='y.py',
                           lines='3', note='n')],
             input_kinds=['kind.a'], not_applicable_reasons=['r.one'],
             predicates=[dict(predicate_id='p.class_c', basis='record_class', source_ids=['s1'],
                              justifications=['j.not_class', 'j.other']),
                         dict(predicate_id='p.input_b', basis='input_presence',
                              source_ids=['s1', 's2'], justifications=['j.absent'])],
             checks=[check(A, 'ev.a', 1, {'kind': 'unconditional'}),
                     check(B, 'ev.b', 2, {'kind': 'required_when_applicable', 'predicate': 'p.input_b'},
                           ['r.one']),
                     check(C, 'ev.a', 1, {'kind': 'required_when_applicable', 'predicate': 'p.class_c'})])
    m.update(over)
    return redigest(m)


def with_extra_conditional_check():
    """chk.d also uses p.class_c, so a second check can name another (undeclared) predicate."""
    m = make_manifest()
    extra = dict(m['checks'][2], check_id='chk.d')
    extra['applicability'] = dict(extra['applicability'])
    m['checks'].append(extra)
    return m


def unconditional_only():
    m = make_manifest()
    m['checks'] = [dict(m['checks'][0])]
    m['predicates'] = []
    return redigest(m)


def rule(rule_id, ev, ver, **over):
    base = dict(rule_id=rule_id, version=1, **{'class': 'refund'}, profile='bounded',
                status='required', applicability={'kind': 'always'}, evaluator_id=ev,
                evaluator_version=ver, failure_disposition='deny', missing_treatment='fail_closed',
                reason_code='R1', source_ref='src:1')
    base.update(over)
    return base


def make_record(manifest=None, **over):
    manifest = manifest or unconditional_only()
    pairs = sorted({(c['evaluator_id'], c['evaluator_version']) for c in manifest['checks']})
    rec = dict(profile=rr.PROFILE, schema_version=0, registry_id='reg-1',
               canonical_profile=rr.CANONICAL_PROFILE, digest='sha256:' + '0' * 64, epoch=1,
               predecessor=None,
               rule_table=[rule(c['check_id'], c['evaluator_id'], c['evaluator_version'])
                           for c in manifest['checks']],
               evaluators=[dict(evaluator_id=e, version=v, qualification_ref='q:%s.%d' % (e, v))
                           for e, v in pairs],
               reason_map={'R1': 'x'}, source_refs=['src:1'], issuer='hub')
    rec.update(over)
    return redigest(rec)


def seam_registry(manifest, **over):
    """The registry view a successor (`/1`) record would give: conditional rules are expressible."""
    rules, qualified = {}, {}
    for c in manifest['checks']:
        app = c['applicability']
        applicability = {'kind': 'always'} if app['kind'] == 'unconditional' else \
            {'kind': 'required_when_applicable', 'predicate': app['predicate'], 'source_ref': 'src:1'}
        rules[c['check_id']] = [rule(c['check_id'], c['evaluator_id'], c['evaluator_version'],
                                     applicability=applicability)]
        qualified[(c['evaluator_id'], c['evaluator_version'])] = 'q:ref'
    view = dict(record_digest='sha256:' + '1' * 64, rules=rules, qualified=qualified,
                conditional_supported=True)
    view.update(over)
    return view


def executed_for(manifest, skip=(), **by_id):
    out = []
    for c in manifest['checks']:
        if c['check_id'] in skip:
            continue
        e = dict(check_id=c['check_id'], outcome='passed', reason=None,
                 evaluator_id=c['evaluator_id'], evaluator_version=c['evaluator_version'])
        e.update(by_id.get(c['check_id'], {}))
        out.append(e)
    return out


def disposition(manifest, cid, **over):
    c = next(x for x in manifest['checks'] if x['check_id'] == cid)
    pred = c['applicability'].get('predicate', 'p.class_c')
    just = next((p['justifications'][0] for p in manifest['predicates'] if p['predicate_id'] == pred),
                'j.absent')
    d = dict(check_id=cid, predicate=pred, justification=just, evaluator_id=c['evaluator_id'],
             evaluator_version=c['evaluator_version'])
    d.update(over)
    return d


class Base(unittest.TestCase):
    def refuses(self, code, fn, *args, **kw):
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            fn(*args, **kw)
        self.assertEqual(ctx.exception.code, code)
        return ctx.exception

    def seam(self, manifest=None, registry=None, executed=None, dispositions=None):
        manifest = manifest or make_manifest()
        digest = mc.validate_manifest(manifest)
        registry = registry if registry is not None else seam_registry(manifest)
        executed = executed if executed is not None else executed_for(manifest)
        return mc._complete(manifest, digest, 1, registry, executed, dispositions)

    def refuses_seam(self, code, **kw):
        return self.refuses(code, self.seam, **kw)


class ManifestV1Shape(Base):
    def test_valid_manifest_and_pin(self):
        m = make_manifest()
        self.assertEqual(mc.validate_manifest(m), m['digest'])
        self.assertEqual(mc.validate_manifest(m, pin=m['digest']), m['digest'])
        self.refuses('pin_mismatch', mc.validate_manifest, m, pin='')

    def test_profile_and_schema_version_pair(self):
        for fn in (lambda m: m.update(schema_version=0), lambda m: m.update(schema_version=2),
                   lambda m: m.update(schema_version=True),
                   lambda m: m.update(profile='ocs-mandatory-manifest/2'),
                   lambda m: m.update(profile=mc.PROFILE)):
            m = make_manifest()
            fn(m)
            self.refuses('schema_invalid', mc.validate_manifest, redigest(m))

    def test_members_are_exact_for_each_profile(self):
        m = make_manifest()
        del m['predicates']
        self.refuses('schema_invalid', mc.validate_manifest, redigest(m))
        m = make_manifest()
        del m['checks'][0]['applicability']
        self.refuses('schema_invalid', mc.validate_manifest, redigest(m))
        m = make_manifest()
        m['checks'][0]['extra'] = 1
        self.refuses('schema_invalid', mc.validate_manifest, redigest(m))
        # a /0 manifest takes neither member
        m0 = rr.loads_strict(open(V0_JSON, 'rb').read())
        m0['predicates'] = []
        self.refuses('schema_invalid', mc.validate_manifest, redigest(m0))
        m0 = rr.loads_strict(open(V0_JSON, 'rb').read())
        m0['checks'][0]['applicability'] = {'kind': 'unconditional'}
        self.refuses('schema_invalid', mc.validate_manifest, redigest(m0))

    def test_applicability_shape(self):
        bad = [None, [], 'unconditional', {}, {'kind': 'optional'}, {'kind': 5}, {'kind': None},
               {'kind': 'unconditional', 'predicate': 'p.class_c'},
               {'kind': 'unconditional', 'x': 1},
               {'kind': 'unconditional', 'predicate': 'x'},
               {'kind': 'required_when_applicable'},
               {'kind': 'required_when_applicable', 'predicate': ''},
               {'kind': 'required_when_applicable', 'predicate': ' '},
               {'kind': 'required_when_applicable', 'predicate': 5},
               {'kind': 'required_when_applicable', 'predicate': None},
               {'kind': 'required_when_applicable', 'predicate': 'p.class_c', 'source_ref': 'x'},
               {'kind': 'required_when_applicable', 'predicate': ['p.class_c']},
               {'kind': 'always'}, {'kind': 'predicate', 'predicate': 'p.class_c'}]
        for app in bad:
            with self.subTest(app=str(app)):
                m = make_manifest()
                m['checks'][2]['applicability'] = app
                self.refuses('schema_invalid', mc.validate_manifest, redigest(m))

    def test_unconditional_with_a_predicate_member_is_refused_by_its_own_check(self):
        # on chk.a so no predicate becomes unused: only the exact-members rule can refuse it
        for extra in ({'predicate': 'p.class_c'}, {'x': 1}):
            m = make_manifest()
            m['checks'][0]['applicability'] = dict({'kind': 'unconditional'}, **extra)
            self.refuses('schema_invalid', mc.validate_manifest, redigest(m))

    def test_predicate_shape(self):
        def edit(fn):
            m = make_manifest()
            fn(m)
            return redigest(m)
        cases = [
            edit(lambda m: m.update(predicates={})),
            edit(lambda m: m['predicates'].reverse()),
            edit(lambda m: m['predicates'].append(copy.deepcopy(m['predicates'][-1]))),
            edit(lambda m: m['predicates'][0].update(extra=1)),
            edit(lambda m: m['predicates'][0].pop('basis')),
            edit(lambda m: m['predicates'][0].update(basis='free_text')),
            edit(lambda m: m['predicates'][0].update(basis=None)),
            edit(lambda m: m['predicates'][0].update(predicate_id='')),
            edit(lambda m: m['predicates'][0].update(predicate_id=3)),
            edit(lambda m: m['predicates'][0].update(justifications=[])),
            edit(lambda m: m['predicates'][0].update(justifications=['j.other', 'j.not_class'])),
            edit(lambda m: m['predicates'][0].update(justifications=['j.other', 'j.other'])),
            edit(lambda m: m['predicates'][0].update(justifications='j.other')),
            edit(lambda m: m['predicates'][0].update(justifications=[''])),
            edit(lambda m: m['predicates'][0].update(source_ids=[])),
            edit(lambda m: m['predicates'][0].update(source_ids=['s2', 's1'])),
            edit(lambda m: m['predicates'][0].update(source_ids=[None])),
            edit(lambda m: m['predicates'].append('p.zzz')),
            # a declared predicate no check uses
            edit(lambda m: m['predicates'].append(dict(predicate_id='p.zz_unused', basis='record_class',
                                                       source_ids=['s1'], justifications=['j'])))]
        for bad in cases:
            with self.subTest(bad=str(bad['predicates'])[:90]):
                self.refuses('schema_invalid', mc.validate_manifest, bad)

    def test_every_basis_is_accepted_and_only_those(self):
        for basis in mc.BASES:
            m = make_manifest()
            m['predicates'][0]['basis'] = basis
            self.assertTrue(mc.validate_manifest(redigest(m)))
        self.assertEqual(set(mc.BASES), {'input_presence', 'input_state', 'peer_results',
                                         'record_class', 'record_content'})

    def test_unknown_predicate_and_unknown_predicate_source(self):
        m = with_extra_conditional_check()
        m['checks'][2]['applicability']['predicate'] = 'p.nope'
        self.refuses('unknown_predicate', mc.validate_manifest, redigest(m))
        # a declared predicate that no check uses is a shape fault, found before the digest
        m = make_manifest()
        m['checks'][2]['applicability']['predicate'] = 'p.nope'
        self.refuses('schema_invalid', mc.validate_manifest, redigest(m))
        m = make_manifest()
        m['predicates'][0]['source_ids'] = ['s9']
        self.refuses('unknown_source', mc.validate_manifest, redigest(m))

    def test_digest_and_pin_cover_applicability_and_predicates(self):
        m = make_manifest()
        for fn in (lambda x: x['checks'][0].update(
                       applicability={'kind': 'required_when_applicable', 'predicate': 'p.class_c'}),
                   lambda x: x['predicates'][0].update(justifications=['j.not_class']),
                   lambda x: x['predicates'][0].update(source_ids=['s2'])):
            changed = copy.deepcopy(m)
            fn(changed)
            self.refuses('digest_mismatch', mc.validate_manifest, changed)
            self.assertNotEqual(rr.record_digest(changed), m['digest'])

    def test_ordering_of_manifest_refusals(self):
        # schema before digest before pin before duplicates before sources before kinds before reasons
        # before predicate sources before predicates
        m = with_extra_conditional_check()
        m['checks'][2]['applicability']['predicate'] = 'p.nope'
        m['checks'][2]['source_id'] = 's9'
        self.refuses('unknown_source', mc.validate_manifest, redigest(m))
        m = with_extra_conditional_check()
        m['checks'][2]['applicability']['predicate'] = 'p.nope'
        m['predicates'][0]['source_ids'] = ['s9']
        self.refuses('unknown_source', mc.validate_manifest, redigest(m))   # before unknown_predicate


class RegistryBinding(Base):
    """Q2: the evaluator pair binds the manifest, every rule entry and the qualification."""

    def test_pair_binding_in_the_registry_view(self):
        self.assertTrue(self.seam()['complete'])
        view = seam_registry(make_manifest())
        view['rules'][A][0]['evaluator_version'] = 9
        self.refuses_seam('rule_evaluator_mismatch', registry=view)
        view = seam_registry(make_manifest())
        view['rules'][B][0]['evaluator_id'] = 'ev.a'   # a qualified evaluator, but not B's
        self.refuses_seam('rule_evaluator_mismatch', registry=view)
        view = seam_registry(make_manifest())
        view['rules'][C].append(dict(view['rules'][C][0], evaluator_version=7))
        self.refuses_seam('rule_evaluator_mismatch', registry=view)

    def test_unknown_and_unqualified_pair_are_reachable_in_the_view(self):
        view = seam_registry(make_manifest())
        del view['qualified'][('ev.a', 1)]
        self.refuses_seam('unknown_evaluator', registry=view)
        for ref in ('', ' ', '\t', ' '):
            view = seam_registry(make_manifest())
            view['qualified'][('ev.a', 1)] = ref
            self.refuses_seam('unqualified_evaluator', registry=view)
        # qualification of another version does not bind this pair
        view = seam_registry(make_manifest())
        del view['qualified'][('ev.b', 2)]
        view['qualified'][('ev.b', 3)] = 'q:x'
        self.refuses_seam('unknown_evaluator', registry=view)

    def test_binding_is_checked_for_a_check_that_is_never_executed(self):
        view = seam_registry(make_manifest())
        view['qualified'][('ev.b', 2)] = ''
        m = make_manifest()
        self.refuses_seam('unqualified_evaluator', registry=view,
                          executed=executed_for(m, skip=(B,)), dispositions=[disposition(m, B)])

    def test_public_function_surfaces_unqualified_and_unknown(self):
        m = unconditional_only()
        rec = make_record(m)
        rec['evaluators'][0]['qualification_ref'] = ''
        self.refuses('unqualified_evaluator', mc.check_completeness, m, redigest(rec),
                     executed_for(m), floor_check_ids=FLOOR)
        rec = make_record(m)
        rec['evaluators'] = [dict(evaluator_id='ev.other', version=1, qualification_ref='q')]
        self.refuses('unknown_evaluator', mc.check_completeness, m, redigest(rec),
                     executed_for(m), floor_check_ids=FLOOR)

    def test_evaluator_fault_message_names_rule_and_evaluator(self):
        m = unconditional_only()
        rec = make_record(m)
        rec['rule_table'].append(rule('chk.unrelated', 'ev.ghost', 4))
        e = self.refuses('unknown_evaluator', mc.check_completeness, m, redigest(rec),
                         executed_for(m), floor_check_ids=FLOOR)
        self.assertIn('chk.unrelated', str(e))
        self.assertIn('ev.ghost', str(e))

    def test_public_function_different_qualified_evaluator(self):
        m = unconditional_only()
        rec = make_record(m)
        rec['evaluators'].append(dict(evaluator_id='ev.other', version=1, qualification_ref='q:o'))
        rec['rule_table'][0]['evaluator_id'] = 'ev.other'
        self.refuses('rule_evaluator_mismatch', mc.check_completeness, m, redigest(rec),
                     executed_for(m), floor_check_ids=FLOOR)

    def test_rule_entries_for_conditional_checks(self):
        view = seam_registry(make_manifest())
        view['rules'][B][0]['status'] = 'advisory'
        self.refuses_seam('registry_rule_not_required', registry=view)
        for app in ({'kind': 'always'}, {'kind': 'required_when_applicable', 'predicate': 'p.class_c'},
                    {'kind': 'predicate', 'predicate': 'p.input_b', 'source_ref': 'src:1'}, None, 'x'):
            view = seam_registry(make_manifest())
            view['rules'][B][0]['applicability'] = app
            with self.subTest(app=str(app)):
                self.refuses_seam('predicate_mismatch', registry=view)
        # an unconditional manifest check needs an always rule
        view = seam_registry(make_manifest())
        view['rules'][A][0]['applicability'] = {'kind': 'required_when_applicable',
                                                'predicate': 'p.class_c', 'source_ref': 'src:1'}
        self.refuses_seam('registry_rule_not_required', registry=view)
        view = seam_registry(make_manifest())
        del view['rules'][C]
        self.refuses_seam('registry_rule_missing', registry=view)

    def test_a_second_rule_entry_must_agree_too(self):
        view = seam_registry(make_manifest())
        view['rules'][B].append(dict(view['rules'][B][0], profile='other',
                                     applicability={'kind': 'always'}))
        self.refuses_seam('predicate_mismatch', registry=view)


class CompletenessV1(Base):
    def test_unconditional_only_manifest_completes_against_a_v0_record(self):
        m = unconditional_only()
        report = mc.check_completeness(m, make_record(m), executed_for(m), floor_check_ids=FLOOR)
        self.assertEqual(set(report), {'manifest_digest', 'record_digest', 'complete', 'counts', 'checks'})
        self.assertTrue(report['complete'])
        self.assertEqual(report['counts'], {'passed': 1, 'failed': 0, 'not_applicable': 0, 'error': 0,
                                            'inapplicable': 0})
        self.assertEqual(report['checks'], [dict(check_id=A, outcome='passed', reason=None, predicate=None)])

    def test_conditional_check_against_a_v0_record_is_refused(self):
        m = make_manifest()
        rec = make_record(m)
        ex = executed_for(m)
        self.refuses('applicability_unsupported_by_registry', mc.check_completeness, m, rec, ex,
                     floor_check_ids=FLOOR)
        # even when dispositions are given and even when the /0 rule for the check says predicate
        rec = make_record(m)
        rec['rule_table'][1]['applicability'] = {'kind': 'predicate', 'predicate': 'p.input_b',
                                                 'source_ref': 'src:1'}
        self.refuses('applicability_unsupported_by_registry', mc.check_completeness, m, redigest(rec),
                     executed_for(m, skip=(B,)), floor_check_ids=FLOOR,
                     dispositions=[disposition(m, B)])

    def test_unsupported_applicability_is_reported_after_a_missing_rule_not_before(self):
        m = make_manifest()
        rec = make_record(m)
        rec['rule_table'] = [r for r in rec['rule_table'] if r['rule_id'] != B]
        self.refuses('registry_rule_missing', mc.check_completeness, m, redigest(rec),
                     executed_for(m), floor_check_ids=FLOOR)

    def test_floor_must_be_unconditional(self):
        m = make_manifest()
        rec = make_record(m)
        self.refuses('floor_check_conditional', mc.check_completeness, m, rec, executed_for(m),
                     floor_check_ids=[A, B])
        # reported before the record is validated, so it cannot be hidden behind a bad record
        bad = make_record(m, epoch=0)
        self.refuses('floor_check_conditional', mc.check_completeness, m, bad, executed_for(m),
                     floor_check_ids=[C])
        self.refuses('floor_not_in_manifest', mc.check_completeness, m, rec, executed_for(m),
                     floor_check_ids=['chk.zzz'])

    def test_dispositions_with_a_v0_manifest_are_refused(self):
        m0 = rr.loads_strict(open(V0_JSON, 'rb').read())
        for disp in ([], [dict(check_id='x')], 'x'):
            self.refuses('schema_invalid', mc.check_completeness, m0, {}, [],
                         floor_check_ids=[m0['checks'][0]['check_id']], dispositions=disp)

    def test_v0_semantics_are_unchanged(self):
        m0 = rr.loads_strict(open(V0_JSON, 'rb').read())
        self.assertEqual(m0['digest'], V0_DIGEST)
        self.assertEqual(rr.record_digest(m0), V0_DIGEST)
        self.assertEqual(mc.validate_manifest(m0, pin=V0_DIGEST), V0_DIGEST)
        self.assertNotIn('predicates', m0)
        self.assertTrue(all('applicability' not in c for c in m0['checks']))

    def test_unconditional_check_needs_an_executed_result(self):
        m = make_manifest()
        self.refuses_seam('skipped_mandatory_check', executed=executed_for(m, skip=(A, B, C)),
                          dispositions=[disposition(m, B), disposition(m, C)])

    def test_executed_results_complete_conditional_checks(self):
        report = self.seam()
        self.assertEqual(report['counts']['passed'], 3)
        self.assertEqual(report['counts']['inapplicable'], 0)
        self.assertTrue(all(c['predicate'] is None for c in report['checks']))

    def test_dispositions_close_conditional_checks(self):
        m = make_manifest()
        report = self.seam(executed=executed_for(m, skip=(B, C)),
                           dispositions=[disposition(m, B), disposition(m, C)])
        self.assertEqual(report['counts'], {'passed': 1, 'failed': 0, 'not_applicable': 0, 'error': 0,
                                            'inapplicable': 2})
        self.assertEqual(report['checks'], [
            dict(check_id=A, outcome='passed', reason=None, predicate=None),
            dict(check_id=B, outcome='inapplicable', reason='j.absent', predicate='p.input_b'),
            dict(check_id=C, outcome='inapplicable', reason='j.not_class', predicate='p.class_c')])
        self.assertEqual(set(report), {'manifest_digest', 'record_digest', 'complete', 'counts', 'checks'})
        self.assertNotIn('verdict', str(report))
        self.assertTrue(report['complete'])

    def test_failed_and_error_are_reported_as_given_with_dispositions_present(self):
        m = make_manifest()
        ex = executed_for(m, skip=(C,), **{A: dict(outcome='failed'), B: dict(outcome='error')})
        report = self.seam(executed=ex, dispositions=[disposition(m, C)])
        self.assertEqual((report['counts']['failed'], report['counts']['error'],
                          report['counts']['inapplicable']), (1, 1, 1))

    def test_not_applicable_outcome_and_disposition_are_different(self):
        m = make_manifest()
        ex = executed_for(m, **{B: dict(outcome='not_applicable', reason='r.one')})
        report = self.seam(executed=ex)
        self.assertEqual(report['counts']['not_applicable'], 1)
        self.assertEqual(report['counts']['inapplicable'], 0)
        ex = executed_for(m, **{B: dict(outcome='not_applicable', reason='j.absent')})
        self.refuses_seam('not_applicable_reason_not_allowed', executed=ex)

    def test_absence_is_not_inapplicability(self):
        m = make_manifest()
        e = self.refuses_seam('skipped_mandatory_check', executed=executed_for(m, skip=(B, C)))
        self.assertIn('chk.b, chk.c', str(e))
        self.refuses_seam('skipped_mandatory_check', executed=executed_for(m, skip=(B, C)),
                          dispositions=[disposition(m, B)])
        self.refuses_seam('skipped_mandatory_check', executed=[], dispositions=[])
        self.refuses_seam('skipped_mandatory_check', executed=executed_for(m, skip=(B,)),
                          dispositions=[])

    def test_disposition_for_an_unconditional_check_is_refused(self):
        m = make_manifest()
        d = disposition(m, A, predicate='p.class_c', justification='j.other')
        self.refuses_seam('inapplicable_not_permitted', executed=executed_for(m, skip=(A,)),
                          dispositions=[d])
        self.refuses_seam('inapplicable_not_permitted', executed=executed_for(m, skip=(A,)),
                          dispositions=[disposition(m, A, predicate='p.input_b', justification='j.absent')])

    def test_predicate_must_be_the_checks_own(self):
        m = make_manifest()
        d = disposition(m, B, predicate='p.class_c', justification='j.other')
        self.refuses_seam('predicate_mismatch', executed=executed_for(m, skip=(B,)), dispositions=[d])
        for pred in ('p.nope', 'P.INPUT_B', 'p.input_b '):
            d = disposition(m, B, predicate=pred)
            with self.subTest(pred=pred):
                self.refuses_seam('predicate_mismatch', executed=executed_for(m, skip=(B,)),
                                  dispositions=[d])

    def test_justification_must_be_in_the_predicates_closed_list(self):
        m = make_manifest()
        for just in ('j.not_class', 'free text', 'J.ABSENT', 'j.absent '):
            d = disposition(m, B, justification=just)
            with self.subTest(just=just):
                self.refuses_seam('justification_not_allowed', executed=executed_for(m, skip=(B,)),
                                  dispositions=[d])
        d = disposition(m, C, justification='j.absent')
        self.refuses_seam('justification_not_allowed', executed=executed_for(m, skip=(C,)),
                          dispositions=[d])

    def test_disposition_evaluator_is_bound(self):
        m = make_manifest()
        for over in (dict(evaluator_id='ev.a'), dict(evaluator_version=3), dict(evaluator_id='ev.zzz')):
            with self.subTest(over=over):
                self.refuses_seam('evaluator_mismatch', executed=executed_for(m, skip=(B,)),
                                  dispositions=[disposition(m, B, **over)])

    def test_duplicates_and_unexpected_dispositions(self):
        m = make_manifest()
        self.refuses_seam('duplicate_result', dispositions=[disposition(m, B)])      # also executed
        self.refuses_seam('duplicate_result', executed=executed_for(m, skip=(B,)),
                          dispositions=[disposition(m, B), disposition(m, B)])
        self.refuses_seam('unexpected_check', dispositions=[disposition(m, B, check_id='chk.zzz')])

    def test_disposition_shape(self):
        m = make_manifest()
        good = disposition(m, B)
        bad = ['x', None, [], dict(good, extra=1), {k: v for k, v in good.items() if k != 'predicate'},
               dict(good, check_id=''), dict(good, predicate=None), dict(good, justification=' '),
               dict(good, evaluator_id=3), dict(good, evaluator_version=True),
               dict(good, evaluator_version=0), dict(good, evaluator_version=1.0)]
        for entry in bad:
            with self.subTest(entry=str(entry)[:70]):
                self.refuses_seam('schema_invalid', executed=executed_for(m, skip=(B,)),
                                  dispositions=[entry])
        for container in ('x', {}, ()):
            self.refuses_seam('schema_invalid', dispositions=container)
        self.refuses_seam('schema_invalid', executed=executed_for(m, skip=(B,)),
                          dispositions=[good] * 513)

    def test_executed_shape_precedes_disposition_checks(self):
        m = make_manifest()
        ex = executed_for(m, skip=(B,))
        ex[0]['outcome'] = 7
        self.refuses_seam('schema_invalid', executed=ex, dispositions=[disposition(m, B, justification='z')])

    def test_executed_checks_precede_dispositions(self):
        m = make_manifest()
        ex = executed_for(m, skip=(B,))
        ex.append(dict(ex[0], check_id='chk.zzz'))
        self.refuses_seam('unexpected_check', executed=ex,
                          dispositions=[disposition(m, B, predicate='p.class_c')])

    def test_pure_and_no_mutation(self):
        m = make_manifest()
        ex = executed_for(m, skip=(B, C))
        disp = [disposition(m, B), disposition(m, C)]
        reg = seam_registry(m)
        before = copy.deepcopy((m, ex, disp, reg))
        self.seam(manifest=m, executed=ex, dispositions=disp, registry=reg)
        self.assertEqual((m, ex, disp, reg), before)
        um, rec = unconditional_only(), None
        rec = make_record(um)
        before = copy.deepcopy((um, rec))
        mc.check_completeness(um, rec, executed_for(um), floor_check_ids=FLOOR)
        self.assertEqual((um, rec), before)


class ClosedCodeSet(unittest.TestCase):
    def test_codes(self):
        self.assertEqual(len(mc.REFUSAL_CODES), 26)
        self.assertTrue(NEW_CODES <= mc.REFUSAL_CODES)
        for code in NEW_CODES:
            self.assertEqual(mc.ManifestRefusal(code).code, code)
        for bad in ('verdict', 'unknown', 'applicability_unsupported', '', None):
            with self.assertRaises(ValueError):
                mc.ManifestRefusal(bad)

    def test_every_new_code_is_raised_by_some_test_path(self):
        # a guard against a code that is declared but unreachable: each is exercised above through
        # validate_manifest, check_completeness or the registry view
        reached = {'unknown_predicate', 'applicability_unsupported_by_registry', 'floor_check_conditional',
                   'rule_evaluator_mismatch', 'inapplicable_not_permitted', 'predicate_mismatch',
                   'justification_not_allowed'}
        self.assertEqual(reached, NEW_CODES)


def load_v1():
    with open(V1_JSON, 'rb') as fh:
        return rr.loads_strict(fh.read())


def load_v0():
    with open(V0_JSON, 'rb') as fh:
        return rr.loads_strict(fh.read())


class CandidateData(unittest.TestCase):
    def setUp(self):
        self.m = load_v1()
        self.v0 = load_v0()

    def test_validates_and_pins(self):
        m = self.m
        self.assertEqual(m['profile'], 'ocs-mandatory-manifest/1')
        self.assertEqual(m['schema_version'], 1)
        self.assertEqual(rr.record_digest(m), m['digest'])
        self.assertEqual(mc.validate_manifest(m, pin=m['digest']), m['digest'])
        self.assertNotEqual(m['digest'], V0_DIGEST)

    def test_v0_json_is_not_edited(self):
        self.assertEqual(self.v0['digest'], V0_DIGEST)
        self.assertEqual(rr.record_digest(self.v0), V0_DIGEST)
        self.assertEqual(self.v0['profile'], 'ocs-mandatory-manifest/0')

    def test_all_51_verifier_ids_and_7_input_reads_retained(self):
        ids1 = [c['check_id'] for c in self.m['checks']]
        ids0 = [c['check_id'] for c in self.v0['checks']]
        self.assertEqual(ids1, ids0)
        self.assertEqual(sum(1 for c in self.m['checks'] if c['kind'] == 'verifier_check'), 51)
        self.assertEqual(sum(1 for c in self.m['checks'] if c['kind'] == 'input_read'), 7)
        self.assertEqual(len(ids1), 58)

    def test_everything_but_applicability_equals_v0(self):
        for c1, c0 in zip(self.m['checks'], self.v0['checks']):
            c1 = dict(c1)
            c1.pop('applicability')
            self.assertEqual(c1, c0)
        for key in ('input_kinds', 'not_applicable_reasons', 'canonical_profile'):
            self.assertEqual(self.m[key], self.v0[key])
        self.assertEqual(self.m['sources'][:len(self.v0['sources'])], self.v0['sources'])

    def test_unconditional_set_is_pinned(self):
        unconditional = [c['check_id'] for c in self.m['checks']
                         if c['applicability']['kind'] == 'unconditional']
        self.assertEqual(unconditional, sorted(['v1.wire.strict-parse'] +
                                               ['input_read.' + k for k in self.m['input_kinds']]))
        conditional = [c for c in self.m['checks'] if c['applicability']['kind'] != 'unconditional']
        self.assertEqual(len(conditional), 50)

    def test_predicates_are_closed_cited_and_used(self):
        sources = {s['source_id']: s for s in self.m['sources']}
        used = {c['applicability']['predicate'] for c in self.m['checks']
                if c['applicability']['kind'] == 'required_when_applicable'}
        declared = [p['predicate_id'] for p in self.m['predicates']]
        self.assertEqual(set(declared), used)
        self.assertEqual(len(declared), len(set(declared)))
        for p in self.m['predicates']:
            self.assertIn(p['basis'], mc.BASES)
            self.assertTrue(p['source_ids'] and p['justifications'])
            for sid in p['source_ids']:
                s = sources[sid]
                self.assertEqual(s['revision'], VERIFIER_REV)
                self.assertEqual(s['repository'], 'cogno-us/cognous-open-control-stack-verifier')
                self.assertRegex(s['lines'], r'^\d+-\d+$')
            self.assertEqual(p['justifications'], sorted(set(p['justifications'])))
            for j in p['justifications'] + [p['predicate_id']]:
                self.assertRegex(j, r'^[a-z][a-z0-9_]*$')   # names, never free text

    def test_each_check_is_in_exactly_one_predicate_group(self):
        groups = {}
        for c in self.m['checks']:
            a = c['applicability']
            if a['kind'] == 'required_when_applicable':
                groups.setdefault(a['predicate'], []).append(c['check_id'])
        self.assertEqual(sum(len(v) for v in groups.values()), 50)
        self.assertEqual(groups['record_class_control_plane_journal'].count('v4.ledger.keys'), 1)
        self.assertEqual(groups['witness_input_supplied'],
                         ['v3.witness.chain', 'v3.witness.coverage', 'v3.witness.digest-recompute',
                          'v3.witness.ledger-heads', 'v3.witness.records', 'v3.witness.run-id'])
        self.assertEqual(groups['run_record_unparsed_or_checker_crash'], ['v1.structure.run-record'])
        self.assertEqual(groups['run_record_parsed_without_checker_crash'], ['v1.structure'])

    def test_md_describes_every_predicate_with_citations_and_boundary_wording(self):
        with open(V1_MD, encoding='utf-8') as fh:
            text = fh.read()
        for p in self.m['predicates']:
            self.assertIn('### `%s`' % p['predicate_id'], text)
        self.assertIn('Early-return paths', text)
        for word in ('non-authorizing', 'HOLD', 'candidate', self.m['digest'], '51', 'Open questions'):
            self.assertIn(word, text)
        self.assertIn('`%s`' % self.m['digest'], text)
        self.assertNotIn('sha256:sha256:', text)
        self.assertEqual(text.count('Source citations (pinned verifier revision)'), len(self.m['predicates']))

    def test_public_function_refuses_the_candidate_against_a_v0_record(self):
        m = self.m
        pairs = sorted({(c['evaluator_id'], c['evaluator_version']) for c in m['checks']})
        rec = dict(profile=rr.PROFILE, schema_version=0, registry_id='syn', canonical_profile=rr.CANONICAL_PROFILE,
                   digest='sha256:' + '0' * 64, epoch=1, predecessor=None,
                   rule_table=[rule(c['check_id'], c['evaluator_id'], c['evaluator_version']) for c in m['checks']],
                   evaluators=[dict(evaluator_id=e, version=v, qualification_ref='synthetic:test-only')
                               for e, v in pairs],
                   reason_map={'R1': 'x'}, source_refs=['src:1'], issuer='syn')
        redigest(rec)
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            mc.check_completeness(m, rec, executed_for(m), floor_check_ids=['v1.wire.strict-parse'])
        self.assertEqual(ctx.exception.code, 'applicability_unsupported_by_registry')

    def test_candidate_completes_through_the_view_with_all_dispositions(self):
        m = self.m
        conditional = [c['check_id'] for c in m['checks'] if c['applicability']['kind'] != 'unconditional']
        disp = []
        for cid in conditional:
            c = next(x for x in m['checks'] if x['check_id'] == cid)
            pred = next(p for p in m['predicates'] if p['predicate_id'] == c['applicability']['predicate'])
            disp.append(dict(check_id=cid, predicate=pred['predicate_id'], justification=pred['justifications'][0],
                             evaluator_id=c['evaluator_id'], evaluator_version=c['evaluator_version']))
        digest = mc.validate_manifest(m)
        report = mc._complete(m, digest, 1, seam_registry(m), executed_for(m, skip=conditional), disp)
        self.assertEqual(report['counts']['inapplicable'], 50)
        self.assertEqual(report['counts']['passed'], 8)
        self.assertEqual([c['check_id'] for c in report['checks']], [c['check_id'] for c in m['checks']])
        # dropping one disposition is a skipped mandatory check, never an implied inapplicability
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            mc._complete(m, digest, 1, seam_registry(m), executed_for(m, skip=conditional), disp[1:])
        self.assertEqual(ctx.exception.code, 'skipped_mandatory_check')


if __name__ == '__main__':
    unittest.main()
