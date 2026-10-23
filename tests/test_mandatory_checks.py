import copy
import unittest

from tools import mandatory_checks as mc
from tools import registry_records as rr

FLOOR = ['chk.a', 'chk.b']
REV = 'a' * 40


def make_manifest(**over):
    manifest = dict(
        profile=mc.PROFILE, schema_version=0, canonical_profile='rfc8785-jcs', manifest_id='m-1',
        digest='sha256:' + '0' * 64,
        sources=[dict(source_id='s1', repository='org/repo', revision=REV, path='docs/x.md',
                      lines='1-2', note=''),
                 dict(source_id='s2', repository='org/repo', revision=REV, path='docs/y.md',
                      lines='', note='n')],
        input_kinds=['kind.a', 'kind.b'],
        not_applicable_reasons=['r.one', 'r.two'],
        checks=[dict(check_id='chk.a', kind='verifier_check', source_id='s1', input_kind=None,
                     evaluator_id='ev.a', evaluator_version=1, not_applicable_reasons=[]),
                dict(check_id='chk.b', kind='input_read', source_id='s2', input_kind='kind.a',
                     evaluator_id='ev.b', evaluator_version=2, not_applicable_reasons=['r.one']),
                dict(check_id='chk.c', kind='input_read', source_id='s2', input_kind='kind.b',
                     evaluator_id='ev.a', evaluator_version=1,
                     not_applicable_reasons=['r.one', 'r.two'])])
    manifest.update(over)
    return redigest(manifest)


def redigest(manifest):
    manifest['digest'] = rr.record_digest(manifest)
    return manifest


def rule(rule_id, evaluator_id, version, **over):
    base = dict(rule_id=rule_id, version=1, **{'class': 'refund'}, profile='bounded',
                status='required', applicability={'kind': 'always'}, evaluator_id=evaluator_id,
                evaluator_version=version, failure_disposition='deny', missing_treatment='fail_closed',
                reason_code='R1', source_ref='src:1')
    base.update(over)
    return base


def make_record(**over):
    record = dict(
        profile=rr.PROFILE, schema_version=0, registry_id='reg-1',
        canonical_profile=rr.CANONICAL_PROFILE, digest='sha256:' + '0' * 64, epoch=1,
        predecessor=None,
        rule_table=[rule('chk.a', 'ev.a', 1), rule('chk.b', 'ev.b', 2), rule('chk.c', 'ev.a', 1)],
        evaluators=[dict(evaluator_id='ev.a', version=1, qualification_ref='q:1'),
                    dict(evaluator_id='ev.b', version=2, qualification_ref='q:2')],
        reason_map={'R1': 'x'}, source_refs=['src:1'], issuer='hub')
    record.update(over)
    record['digest'] = rr.record_digest(record)
    return record


def redigest_record(record):
    record['digest'] = rr.record_digest(record)
    return record


def make_executed():
    return [dict(check_id='chk.a', outcome='passed', reason=None, evaluator_id='ev.a',
                 evaluator_version=1),
            dict(check_id='chk.b', outcome='failed', reason=None, evaluator_id='ev.b',
                 evaluator_version=2),
            dict(check_id='chk.c', outcome='not_applicable', reason='r.two', evaluator_id='ev.a',
                 evaluator_version=1)]


class Base(unittest.TestCase):
    def refuses(self, code, fn, *args, **kwargs):
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)

    def complete(self, manifest=None, record=None, executed=None, floor=FLOOR, **kw):
        return mc.check_completeness(manifest or make_manifest(), record or make_record(),
                                     executed if executed is not None else make_executed(),
                                     floor_check_ids=floor, **kw)


class ManifestValidation(Base):
    def test_positive_returns_digest_and_pin_accepted(self):
        m = make_manifest()
        self.assertEqual(mc.validate_manifest(m), m['digest'])
        self.assertEqual(mc.validate_manifest(m, pin=m['digest']), m['digest'])

    def test_schema_invalid_cases(self):
        def edit(fn):
            m = make_manifest()
            fn(m)
            try:
                return redigest(m)
            except ValueError:  # not canonicalizable: the digest stays stale on purpose
                return m
        cases = [
            'not a dict',
            dict(make_manifest(), digest='sha256:ABC'),
            edit(lambda m: m.update(extra=1)),
            edit(lambda m: m.pop('note', None) or m.pop('manifest_id')),
            edit(lambda m: m.update(profile='other')),
            edit(lambda m: m.update(schema_version=1)),
            edit(lambda m: m.update(schema_version=False)),
            edit(lambda m: m.update(canonical_profile='x')),
            edit(lambda m: m.update(manifest_id=' ')),
            edit(lambda m: m['sources'][0].update(revision='A' * 40)),
            edit(lambda m: m['sources'][0].update(revision='a' * 39)),
            edit(lambda m: m['sources'][0].update(extra='x')),
            edit(lambda m: m['sources'][0].update(lines=None)),
            edit(lambda m: m['sources'].append(dict(m['sources'][0]))),
            edit(lambda m: m.update(input_kinds=['kind.b', 'kind.a'])),
            edit(lambda m: m.update(input_kinds=['kind.a', 'kind.a'])),
            edit(lambda m: m.update(input_kinds=[''])),
            edit(lambda m: m.update(not_applicable_reasons=['r.two', 'r.one'])),
            edit(lambda m: m['checks'].reverse()),
            edit(lambda m: m['checks'][0].update(kind='other')),
            edit(lambda m: m['checks'][1].update(input_kind=None)),
            edit(lambda m: m['checks'][0].update(input_kind=5)),
            edit(lambda m: m['checks'][0].update(evaluator_version=0)),
            edit(lambda m: m['checks'][0].update(evaluator_version=True)),
            edit(lambda m: m['checks'][0].update(evaluator_version=1.0)),
            edit(lambda m: m['checks'][0].update(not_applicable_reasons=['r.two', 'r.one'])),
            edit(lambda m: m['checks'][0].update(not_applicable_reasons='r.one')),
            edit(lambda m: m['checks'][0].update(check_id='')),
            edit(lambda m: m['checks'][0].update(evaluator_id=None)),
            edit(lambda m: m['sources'][0].update(note='\ud800')),
            edit(lambda m: m['checks'][0].update(not_applicable_reasons=[1.5])),
        ]
        for bad in cases:
            with self.subTest(bad=str(bad)[:80]):
                self.refuses('schema_invalid', mc.validate_manifest, bad)

    def test_bad_pin_form_is_pin_mismatch(self):
        for pin in ('x', '', 5, 0, False, b'sha256:' + b'0' * 64, []):
            with self.subTest(pin=pin):
                self.refuses('pin_mismatch', mc.validate_manifest, make_manifest(), pin=pin)

    def test_digest_mismatch_stale_and_altered(self):
        m = make_manifest()
        m['manifest_id'] = 'altered'  # digest now stale
        self.refuses('digest_mismatch', mc.validate_manifest, m)
        m2 = make_manifest()
        m2['digest'] = 'sha256:' + 'f' * 64
        self.refuses('digest_mismatch', mc.validate_manifest, m2)
        m3 = make_manifest()
        m3['checks'][0]['evaluator_version'] = 9  # silent weakening without redigest
        self.refuses('digest_mismatch', mc.validate_manifest, m3)

    def test_pin_mismatch(self):
        self.refuses('pin_mismatch', mc.validate_manifest, make_manifest(), pin='sha256:' + 'e' * 64)

    def test_digest_ignores_key_order(self):
        m = make_manifest()
        reordered = dict(reversed(list(m.items())))
        self.assertEqual(mc.validate_manifest(reordered), m['digest'])

    def test_duplicate_check(self):
        m = make_manifest()
        m['checks'].insert(1, dict(m['checks'][0]))
        self.refuses('duplicate_check', mc.validate_manifest, redigest(m))

    def test_unknown_source(self):
        m = make_manifest()
        m['checks'][0]['source_id'] = 'nope'
        self.refuses('unknown_source', mc.validate_manifest, redigest(m))

    def test_unknown_input_kind(self):
        m = make_manifest()
        m['checks'][1]['input_kind'] = 'kind.zzz'
        self.refuses('unknown_input_kind', mc.validate_manifest, redigest(m))
        m = make_manifest()
        m['checks'][0]['input_kind'] = 'kind.zzz'  # a verifier_check may not name a stranger either
        self.refuses('unknown_input_kind', mc.validate_manifest, redigest(m))

    def test_verifier_check_may_name_a_listed_input_kind(self):
        m = make_manifest()
        m['checks'][0]['input_kind'] = 'kind.a'
        mc.validate_manifest(redigest(m))

    def test_unknown_reason(self):
        m = make_manifest()
        m['checks'][1]['not_applicable_reasons'] = ['r.zzz']
        self.refuses('unknown_reason', mc.validate_manifest, redigest(m))

    def test_step_order_digest_before_semantics(self):
        m = make_manifest()
        m['checks'][0]['source_id'] = 'nope'  # not redigested: digest refusal comes first
        self.refuses('digest_mismatch', mc.validate_manifest, m)

    def test_size_limits(self):
        def many_checks(n):
            checks = [dict(check_id='c%05d' % i, kind='verifier_check', source_id='s1',
                           input_kind=None, evaluator_id='ev.a', evaluator_version=1,
                           not_applicable_reasons=[]) for i in range(n)]
            return redigest(make_manifest(checks=checks))
        mc.validate_manifest(many_checks(mc.MAX_CHECKS))
        self.refuses('schema_invalid', mc.validate_manifest, many_checks(mc.MAX_CHECKS + 1))

        def many_sources(n):
            srcs = [dict(source_id='s%04d' % i, repository='r', revision=REV, path='p', lines='',
                         note='') for i in range(n)]
            return make_manifest(sources=srcs, checks=[])
        mc.validate_manifest(many_sources(mc.MAX_SOURCES))
        self.refuses('schema_invalid', mc.validate_manifest, many_sources(mc.MAX_SOURCES + 1))
        long_text = make_manifest(manifest_id='x' * (mc.MAX_TEXT + 1))
        self.refuses('schema_invalid', mc.validate_manifest, long_text)
        kinds = make_manifest(input_kinds=['k%03d' % i for i in range(mc.MAX_INPUT_KINDS + 1)])
        self.refuses('schema_invalid', mc.validate_manifest, kinds)

    def test_validate_does_not_mutate(self):
        m = make_manifest()
        before = copy.deepcopy(m)
        mc.validate_manifest(m, pin=m['digest'])
        self.assertEqual(m, before)

    def test_refusal_codes_closed_set(self):
        with self.assertRaises(ValueError):
            mc.ManifestRefusal('made_up')


class Completeness(Base):
    def test_positive_report_shape_and_order(self):
        m, r = make_manifest(), make_record()
        report = self.complete(m, r)
        self.assertEqual(set(report), {'manifest_digest', 'record_digest', 'complete', 'counts', 'checks'})
        self.assertIs(report['complete'], True)
        self.assertEqual(report['manifest_digest'], m['digest'])
        self.assertEqual(report['record_digest'], r['digest'])
        self.assertEqual(report['counts'], {'passed': 1, 'failed': 1, 'not_applicable': 1, 'error': 0})
        self.assertEqual(report['checks'], [
            {'check_id': 'chk.a', 'outcome': 'passed', 'reason': None},
            {'check_id': 'chk.b', 'outcome': 'failed', 'reason': None},
            {'check_id': 'chk.c', 'outcome': 'not_applicable', 'reason': 'r.two'}])
        text = repr(report).lower()
        for word in ('verdict', 'grant', 'activate', 'pin_selected'):
            self.assertNotIn(word, text)

    def test_executed_order_does_not_change_report(self):
        report = self.complete(executed=list(reversed(make_executed())))
        self.assertEqual([c['check_id'] for c in report['checks']], ['chk.a', 'chk.b', 'chk.c'])
        self.assertEqual(report, self.complete())

    def test_error_outcome_reported_as_such(self):
        ex = make_executed()
        ex[0]['outcome'] = 'error'
        self.assertEqual(self.complete(executed=ex)['counts']['error'], 1)

    def test_pin_accepted_and_mismatch(self):
        m = make_manifest()
        self.assertTrue(self.complete(m, pin=m['digest'])['complete'])
        self.refuses('pin_mismatch', self.complete, m, pin='sha256:' + 'e' * 64)

    def test_manifest_refusal_propagates(self):
        m = make_manifest()
        m['manifest_id'] = 'altered'
        self.refuses('digest_mismatch', self.complete, m)

    def test_floor_must_be_explicit_collection(self):
        for bad in (None, 'chk.a', {'chk.a': 1}, [], set(), [1], ['']):
            with self.subTest(bad=bad):
                self.refuses('schema_invalid', self.complete, floor=bad)
        with self.assertRaises(TypeError):
            mc.check_completeness(make_manifest(), make_record(), make_executed())

    def test_floor_variants_accepted(self):
        for floor in (('chk.a',), {'chk.a', 'chk.b'}, frozenset(['chk.a']), ['chk.a', 'chk.a']):
            self.assertTrue(self.complete(floor=floor)['complete'])

    def test_floor_not_in_manifest(self):
        self.refuses('floor_not_in_manifest', self.complete, floor=['chk.a', 'chk.zzz'])

    def test_record_invalid_wraps_registry_refusal(self):
        for record in (make_record(epoch=0), {'x': 1}, 'nope'):
            with self.subTest(record=str(record)[:40]):
                self.refuses('registry_record_invalid', self.complete, record=record)
        stale = make_record()
        stale['issuer'] = 'other'  # digest stale
        self.refuses('registry_record_invalid', self.complete, record=stale)
        floats = make_record()
        floats['epoch'] = 1.5
        self.refuses('registry_record_invalid', self.complete, record=floats)

    def test_floor_weakening_in_record(self):
        # advisory floor rule
        rec = make_record()
        rec['rule_table'][0]['status'] = 'advisory'
        self.refuses('registry_record_invalid', self.complete, record=redigest_record(rec))
        # conditional floor rule
        rec = make_record()
        rec['rule_table'][1]['applicability'] = {'kind': 'predicate', 'predicate': 'p',
                                                 'source_ref': 'src:1'}
        self.refuses('registry_record_invalid', self.complete, record=redigest_record(rec))
        # floor rule absent
        rec = make_record()
        del rec['rule_table'][0]
        self.refuses('registry_record_invalid', self.complete, record=redigest_record(rec))

    def test_record_unqualified_evaluator_in_rule_use(self):
        rec = make_record()
        rec['evaluators'][0]['qualification_ref'] = ''
        self.refuses('registry_record_invalid', self.complete, record=redigest_record(rec))

    def test_registry_rule_missing(self):
        rec = make_record()
        del rec['rule_table'][2]  # chk.c is not in the floor, so validate_record passes
        self.refuses('registry_rule_missing', self.complete, record=redigest_record(rec))

    def test_registry_rule_not_required(self):
        rec = make_record()
        rec['rule_table'][2]['status'] = 'advisory'
        self.refuses('registry_rule_not_required', self.complete, record=redigest_record(rec))
        rec = make_record()
        rec['rule_table'][2]['applicability'] = {'kind': 'predicate', 'predicate': 'p',
                                                 'source_ref': 'src:1'}
        self.refuses('registry_rule_not_required', self.complete, record=redigest_record(rec))
        rec = make_record()  # a second, advisory entry for the same rule id in another scope
        rec['rule_table'].append(rule('chk.c', 'ev.a', 1, status='advisory', profile='other'))
        self.refuses('registry_rule_not_required', self.complete, record=redigest_record(rec))

    def test_unexpected_check(self):
        ex = make_executed() + [dict(check_id='chk.extra', outcome='passed', reason=None,
                                     evaluator_id='ev.a', evaluator_version=1)]
        self.refuses('unexpected_check', self.complete, executed=ex)

    def test_duplicate_result(self):
        ex = make_executed()
        ex.append(dict(ex[0]))
        self.refuses('duplicate_result', self.complete, executed=ex)

    def test_skipped_mandatory_check(self):
        ex = make_executed()[:1]
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            self.complete(executed=ex)
        self.assertEqual(ctx.exception.code, 'skipped_mandatory_check')
        self.assertIn('chk.b, chk.c', str(ctx.exception))
        self.refuses('skipped_mandatory_check', self.complete, executed=[])

    def test_invalid_outcome(self):
        for bad in ('ok', 'PASSED', '', 'passed '):
            ex = make_executed()
            ex[0]['outcome'] = bad
            with self.subTest(bad=bad):
                self.refuses('invalid_outcome', self.complete, executed=ex)

    def test_non_text_outcome_is_schema_invalid(self):
        for bad in (None, 1, True, ['passed']):
            ex = make_executed()
            ex[0]['outcome'] = bad
            with self.subTest(bad=bad):
                self.refuses('schema_invalid', self.complete, executed=ex)

    def test_evaluator_mismatch(self):
        ex = make_executed()
        ex[0]['evaluator_version'] = 2  # wrong version
        self.refuses('evaluator_mismatch', self.complete, executed=ex)
        ex = make_executed()
        ex[0]['evaluator_id'] = 'ev.b'  # wrong id
        self.refuses('evaluator_mismatch', self.complete, executed=ex)

    def test_unknown_evaluator(self):
        m = make_manifest()
        m['checks'][0]['evaluator_version'] = 7  # not listed in the record
        redigest(m)
        ex = make_executed()
        ex[0]['evaluator_version'] = 7
        self.refuses('unknown_evaluator', self.complete, manifest=m, executed=ex)

    def test_unqualified_evaluator(self):
        rec = make_record()
        rec['evaluators'].append(dict(evaluator_id='ev.z', version=1, qualification_ref=''))
        redigest_record(rec)
        m = make_manifest()
        m['checks'][0]['evaluator_id'] = 'ev.z'
        redigest(m)
        ex = make_executed()
        ex[0]['evaluator_id'] = 'ev.z'
        self.refuses('unqualified_evaluator', self.complete, manifest=m, record=rec, executed=ex)

    def test_not_applicable_reason_not_allowed(self):
        for reason in ('r.two', 'r.zzz', None, '', '  '):
            ex = make_executed()
            ex[1] = dict(check_id='chk.b', outcome='not_applicable', reason=reason,
                         evaluator_id='ev.b', evaluator_version=2)  # chk.b allows only r.one
            with self.subTest(reason=reason):
                self.refuses('not_applicable_reason_not_allowed', self.complete, executed=ex)
        ex = make_executed()
        ex[0] = dict(check_id='chk.a', outcome='not_applicable', reason='r.one',
                     evaluator_id='ev.a', evaluator_version=1)  # chk.a allows none
        self.refuses('not_applicable_reason_not_allowed', self.complete, executed=ex)

    def test_not_applicable_allowed_reason_passes(self):
        ex = make_executed()
        ex[1] = dict(check_id='chk.b', outcome='not_applicable', reason='r.one',
                     evaluator_id='ev.b', evaluator_version=2)
        self.assertEqual(self.complete(executed=ex)['counts']['not_applicable'], 2)

    def test_executed_shape(self):
        def mutate(fn):
            ex = make_executed()
            fn(ex)
            return ex
        cases = [
            tuple(make_executed()),
            'x',
            mutate(lambda e: e[0].update(extra=1)),
            mutate(lambda e: e[0].pop('reason')),
            mutate(lambda e: e.__setitem__(0, 'x')),
            mutate(lambda e: e[0].update(reason='why')),  # reason on a non-not_applicable outcome
            mutate(lambda e: e[0].update(reason=5)),
            mutate(lambda e: e[0].update(evaluator_version=1.0)),
            mutate(lambda e: e[0].update(evaluator_version=True)),
            mutate(lambda e: e[0].update(check_id=None)),
        ]
        for bad in cases:
            with self.subTest(bad=str(bad)[:80]):
                self.refuses('schema_invalid', self.complete, executed=bad)

    def test_executed_size_limit(self):
        row = dict(check_id='chk.a', outcome='passed', reason=None, evaluator_id='ev.a',
                   evaluator_version=1)
        self.refuses('schema_invalid', self.complete, executed=[dict(row)] * (mc.MAX_EXECUTED + 1))

    def test_floor_size_limit(self):
        floor = ['f%04d' % i for i in range(mc.MAX_FLOOR + 1)]
        self.refuses('schema_invalid', self.complete, floor=floor)

    def test_non_mutation(self):
        m, r, ex = make_manifest(), make_record(), make_executed()
        floor = list(FLOOR)
        snapshot = copy.deepcopy((m, r, ex, floor))
        report = self.complete(m, r, ex, floor=floor)
        self.assertEqual((m, r, ex, floor), snapshot)
        report['checks'][0]['outcome'] = 'error'
        report['counts']['passed'] = 99
        self.assertEqual((m, r, ex, floor), snapshot)
        with self.assertRaises(mc.ManifestRefusal):
            self.complete(m, r, ex[:1], floor=floor)
        self.assertEqual((m, r, ex, floor), snapshot)

    def test_determinism(self):
        first = self.complete()
        for _ in range(3):
            self.assertEqual(self.complete(), first)
        shuffled_floor = self.complete(floor=['chk.b', 'chk.a'])
        self.assertEqual(shuffled_floor, first)

    def test_no_incomplete_report_is_ever_returned(self):
        ex = make_executed()
        for i in range(len(ex)):
            partial = ex[:i] + ex[i + 1:]
            self.refuses('skipped_mandatory_check', self.complete, executed=partial)


if __name__ == '__main__':
    unittest.main()
