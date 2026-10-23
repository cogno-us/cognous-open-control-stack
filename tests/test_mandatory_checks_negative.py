"""Adversarial negative battery for OCS v0.2 step 2.3 (mandatory-check manifest and completeness).

This is a developer-owned negative battery written against the shared 2.3 interface specification,
not against any implementation. It is not independent Qualification evidence, it does not
qualify, certify or authorize anything, and release and production remain on HOLD.

Each test asserts the exact specified refusal code (or the exact specified report shape). Where the
specification leaves the code for a malformed input open, the test uses `refuses_in` with the
smallest plausible closed set and the ambiguity is listed in the report as an open question.
Standard library only; no effects; fixtures are synthetic.
"""
import copy
import json
import unicodedata
import unittest

from tools import mandatory_checks as mc
from tools import registry_records as rr

REV = 'a' * 40
SRC = 'src.verifier'
CLOSED_REASONS = ['input_not_supplied', 'not_in_scope']
OUTCOMES = ('passed', 'failed', 'not_applicable', 'error')

CID_NOTE = 'check.extra.note'
CID_INPUT = 'input_read.request'
CID_GRANT = 'v1.mandatory.grant'
CID_POLICY = 'v1.mandatory.policy'
FLOOR = {CID_GRANT, CID_POLICY}


def redigest(obj):
    """Recompute the digest where canonicalization allows it; otherwise leave it stale."""
    try:
        obj['digest'] = rr.record_digest(obj)
    except (ValueError, UnicodeEncodeError, RecursionError):
        pass
    return obj


def make_manifest():
    check = lambda cid, kind, ik, ev, ver, reasons: dict(
        check_id=cid, kind=kind, source_id=SRC, input_kind=ik, evaluator_id=ev,
        evaluator_version=ver, not_applicable_reasons=reasons)
    m = dict(profile='ocs-mandatory-manifest/0', schema_version=0, canonical_profile='rfc8785-jcs',
             manifest_id='manifest-1', digest='sha256:' + '0' * 64,
             sources=[dict(source_id=SRC, repository='cogno-us/example', revision=REV,
                           path='docs/x.md', lines='951-955', note='synthetic')],
             input_kinds=['request'],
             not_applicable_reasons=list(CLOSED_REASONS),
             checks=[check(CID_NOTE, 'verifier_check', None, 'ev.note', 2, ['not_in_scope']),
                     check(CID_INPUT, 'input_read', 'request', 'ev.reader', 1, ['input_not_supplied']),
                     check(CID_GRANT, 'verifier_check', None, 'ev.grant', 1, []),
                     check(CID_POLICY, 'verifier_check', None, 'ev.policy', 1, [])])
    return redigest(m)


def make_record(**over):
    def rule(rid, ev, ver, **kw):
        base = dict(rule_id=rid, version=1, **{'class': 'refund'}, profile='bounded', status='required',
                    applicability={'kind': 'always'}, evaluator_id=ev, evaluator_version=ver,
                    failure_disposition='deny', missing_treatment='fail_closed', reason_code='R1',
                    source_ref='src:a')
        base.update(kw)
        return base
    rec = dict(profile=rr.PROFILE, schema_version=0, registry_id='reg-1',
               canonical_profile=rr.CANONICAL_PROFILE, digest='sha256:' + '0' * 64, epoch=1,
               predecessor=None,
               rule_table=[rule(CID_NOTE, 'ev.note', 2), rule(CID_INPUT, 'ev.reader', 1),
                           rule(CID_GRANT, 'ev.grant', 1), rule(CID_POLICY, 'ev.policy', 1)],
               evaluators=[dict(evaluator_id='ev.note', version=2, qualification_ref='q:note'),
                           dict(evaluator_id='ev.reader', version=1, qualification_ref='q:reader'),
                           dict(evaluator_id='ev.grant', version=1, qualification_ref='q:grant'),
                           dict(evaluator_id='ev.policy', version=1, qualification_ref='q:policy')],
               reason_map={'R1': 'hold'}, source_refs=['src:a'], issuer='hub')
    rec.update(over)
    return redigest(rec)


def rule_of(record, rid):
    return next(r for r in record['rule_table'] if r['rule_id'] == rid)


def make_executed(manifest=None, **by_id):
    """All checks passed with the manifest's evaluators; by_id maps check_id -> field overrides."""
    manifest = manifest or make_manifest()
    out = []
    for c in manifest['checks']:
        e = dict(check_id=c['check_id'], outcome='passed', reason=None,
                 evaluator_id=c['evaluator_id'], evaluator_version=c['evaluator_version'])
        e.update(by_id.get(c['check_id'], {}))
        out.append(e)
    return out


_DEFAULT = object()


class Base(unittest.TestCase):
    def refuses(self, code, fn, *args, **kw):
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            fn(*args, **kw)
        self.assertEqual(ctx.exception.code, code)
        return ctx.exception

    def refuses_in(self, codes, fn, *args, **kw):
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            fn(*args, **kw)
        self.assertIn(ctx.exception.code, codes)

    def complete(self, manifest=_DEFAULT, record=_DEFAULT, executed=_DEFAULT, floor=FLOOR, **kw):
        manifest = make_manifest() if manifest is _DEFAULT else manifest
        record = make_record() if record is _DEFAULT else record
        if executed is _DEFAULT:
            executed = make_executed(manifest)
        return mc.check_completeness(manifest, record, executed, floor_check_ids=floor, **kw)

    def refuses_complete(self, code, manifest=_DEFAULT, record=_DEFAULT, executed=_DEFAULT, floor=FLOOR, **kw):
        manifest = make_manifest() if manifest is _DEFAULT else manifest
        record = make_record() if record is _DEFAULT else record
        if executed is _DEFAULT:
            executed = make_executed(manifest)
        return self.refuses(code, mc.check_completeness, manifest, record, executed,
                            floor_check_ids=floor, **kw)

    def mutated(self, fn):
        m = make_manifest()
        fn(m)
        return redigest(m)


class Fixtures(Base):
    def test_fixtures_are_valid(self):
        rr.validate_record(make_record(), floor_mandatory_rule_ids=FLOOR)
        m = make_manifest()
        self.assertEqual(mc.validate_manifest(m), rr.record_digest(m))
        report = self.complete()
        self.assertTrue(report['complete'])

    def test_validate_manifest_is_pure(self):
        m = make_manifest()
        before = copy.deepcopy(m)
        mc.validate_manifest(m)
        self.assertEqual(m, before)

    def test_closed_code_set_exposed_as_exception_code(self):
        self.assertTrue(issubclass(mc.ManifestRefusal, Exception))
        e = self.refuses('schema_invalid', mc.validate_manifest, None)
        self.assertEqual(type(e.code), str)

    def test_loader_precondition_duplicate_keys_never_reach_a_manifest(self):
        text = json.dumps(make_manifest())
        dup = text[:-1] + ', "manifest_id": "other"}'
        with self.assertRaises(ValueError):
            rr.loads_strict(dup)


class ManifestShape(Base):
    def test_non_object_manifests(self):
        for bad in (None, [], 'manifest', 0, True, [make_manifest()], ()):
            self.refuses('schema_invalid', mc.validate_manifest, bad)

    def test_every_member_is_required(self):
        for key in list(make_manifest()):
            m = make_manifest()
            redigest(m)
            del m[key]
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_extra_manifest_members_refused(self):
        for key, value in (('optional', True), ('verdict', 'pass'), ('x', None), ('pin', 'sha256:' + '1' * 64)):
            m = make_manifest()
            m[key] = value
            redigest(m)
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_profile_version_and_canonical_profile(self):
        # '/1' is a supported successor profile since the Q3 repair: a /0 manifest relabelled '/1'
        # still fails the shape (no predicates, no applicability); '/2' is unsupported.
        for key, value in (('profile', 'ocs-mandatory-manifest/1'), ('profile', 'ocs-mandatory-manifest/2'),
                           ('profile', 'ocs-registry-record/0'),
                           ('schema_version', 1), ('schema_version', -1), ('schema_version', '0'),
                           ('canonical_profile', 'json'), ('canonical_profile', 'RFC8785-JCS'),
                           ('manifest_id', ''), ('manifest_id', '   '), ('manifest_id', 7),
                           ('manifest_id', None), ('manifest_id', ['a'])):
            m = self.mutated(lambda x: x.__setitem__(key, value))
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_schema_version_false_is_not_zero(self):
        m = self.mutated(lambda x: x.__setitem__('schema_version', False))
        self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_schema_version_float_and_int_subclass(self):
        class MyInt(int):
            pass
        for bad in (0.0, MyInt(0), float('nan')):
            m = make_manifest()
            m['schema_version'] = bad
            redigest(m)
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_digest_form_is_strict(self):
        good = make_manifest()['digest']
        hexpart = good.split(':')[1]
        for bad in (good.upper(), 'sha256:' + hexpart.upper(), 'sha256:' + hexpart[:-1],
                    'sha256:' + hexpart + '0', 'sha1:' + hexpart, hexpart, ' ' + good,
                    '', None, 5, ['x']):
            m = make_manifest()
            m['digest'] = bad
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_digest_with_trailing_newline_is_refused(self):
        # registry_records.DIGEST_RE ends in `$`, which also matches before a trailing newline,
        # so an implementation that reuses it may report digest_mismatch instead of schema_invalid
        m = make_manifest()
        m['digest'] += '\n'
        self.refuses('schema_invalid', mc.validate_manifest, m)
        self.refuses('pin_mismatch', mc.validate_manifest, make_manifest(), pin=make_manifest()['digest'] + '\n')

    def test_sources_shape(self):
        def put(key, value):
            return self.mutated(lambda m: m['sources'][0].__setitem__(key, value))
        for key, value in (('revision', 'A' * 40), ('revision', 'a' * 39), ('revision', 'a' * 41),
                           ('revision', 'g' * 40), ('revision', 'main'), ('revision', None),
                           ('revision', 7), ('source_id', ''), ('source_id', None), ('repository', None),
                           ('path', 3), ('lines', None), ('note', ['x'])):
            self.refuses('schema_invalid', mc.validate_manifest, put(key, value))

    def test_source_members_exact(self):
        m = self.mutated(lambda x: x['sources'][0].__setitem__('extra', 'x'))
        self.refuses('schema_invalid', mc.validate_manifest, m)
        for key in list(make_manifest()['sources'][0]):
            m = self.mutated(lambda x: x['sources'][0].pop(key))
            self.refuses('schema_invalid', mc.validate_manifest, m)
        m = self.mutated(lambda x: x.__setitem__('sources', [x['sources'][0], 'src']))
        self.refuses('schema_invalid', mc.validate_manifest, m)
        m = self.mutated(lambda x: x.__setitem__('sources', {'a': 1}))
        self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_duplicate_source_id_refused(self):
        def dup(m):
            m['sources'].append(copy.deepcopy(m['sources'][0]))
        self.refuses('schema_invalid', mc.validate_manifest, self.mutated(dup))

    def test_check_members_exact_and_no_optional_flag(self):
        for key, value in (('optional', True), ('optional', False), ('required', False),
                           ('enabled', False), ('skip', True), ('severity', 'low')):
            m = self.mutated(lambda x: x['checks'][0].__setitem__(key, value))
            self.refuses('schema_invalid', mc.validate_manifest, m)
        for key in list(make_manifest()['checks'][0]):
            m = self.mutated(lambda x: x['checks'][0].pop(key))
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_check_field_types(self):
        for key, value in (('check_id', ''), ('check_id', '  '), ('check_id', None), ('check_id', 1),
                           ('kind', 'optional_check'), ('kind', 'VERIFIER_CHECK'), ('kind', None),
                           ('kind', ['verifier_check']), ('source_id', None), ('source_id', ''),
                           ('evaluator_id', ''), ('evaluator_id', None), ('evaluator_id', 4),
                           ('input_kind', 5), ('input_kind', ['request']),
                           ('not_applicable_reasons', None), ('not_applicable_reasons', 'not_in_scope'),
                           ('not_applicable_reasons', [''])):
            m = self.mutated(lambda x: x['checks'][2].__setitem__(key, value))
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_input_read_requires_non_null_input_kind(self):
        m = self.mutated(lambda x: x['checks'][1].__setitem__('input_kind', None))
        self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_checks_must_be_a_list_sorted_by_check_id(self):
        for fn in (lambda m: m.__setitem__('checks', m['checks'][::-1]),
                   lambda m: m['checks'].insert(0, m['checks'].pop()),
                   lambda m: m.__setitem__('checks', tuple(m['checks'])),
                   lambda m: m.__setitem__('checks', None),
                   lambda m: m.__setitem__('checks', {c['check_id']: c for c in m['checks']})):
            self.refuses('schema_invalid', mc.validate_manifest, self.mutated(fn))

    def test_input_kinds_and_reason_sets_sorted_unique_nonempty(self):
        for key, bad in (('input_kinds', ['request', 'request']), ('input_kinds', ['z', 'a']),
                         ('input_kinds', ['']), ('input_kinds', 'request'), ('input_kinds', None),
                         ('not_applicable_reasons', ['not_in_scope', 'input_not_supplied']),
                         ('not_applicable_reasons', ['not_in_scope', 'not_in_scope']),
                         ('not_applicable_reasons', ['']), ('not_applicable_reasons', None),
                         ('not_applicable_reasons', {'not_in_scope': 1})):
            self.refuses('schema_invalid', mc.validate_manifest, self.mutated(lambda m: m.__setitem__(key, bad)))

    def test_check_reason_list_sorted_unique(self):
        for bad in (['not_in_scope', 'input_not_supplied'], ['not_in_scope', 'not_in_scope']):
            m = self.mutated(lambda x: x['checks'][0].__setitem__('not_applicable_reasons', bad))
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_numbers_bools_floats_and_int_subclasses_in_evaluator_version(self):
        class MyInt(int):
            pass
        for bad in (True, False, 0, -1, 1.0, 2.0, MyInt(1), 2 ** 53, 2 ** 64, 10 ** 400, float('nan'),
                    float('inf'), '1', None, [1]):
            m = make_manifest()
            m['checks'][2]['evaluator_version'] = bad
            redigest(m)
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_evaluator_version_at_safe_maximum_is_the_only_big_value_accepted(self):
        m = self.mutated(lambda x: x['checks'][2].__setitem__('evaluator_version', 2 ** 53 - 1))
        self.assertEqual(mc.validate_manifest(m), rr.record_digest(m))

    def test_deeply_nested_garbage_is_a_refusal_not_a_crash(self):
        nested = []
        for _ in range(5000):
            nested = [nested]
        for fn in (lambda m: m['sources'][0].__setitem__('note', nested),
                   lambda m: m.__setitem__('manifest_id', nested),
                   lambda m: m['checks'][0].__setitem__('evaluator_id', nested)):
            m = make_manifest()
            fn(m)
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_non_string_keys_and_non_json_values(self):
        for fn in (lambda m: m.__setitem__(1, 'x'), lambda m: m['sources'][0].__setitem__('note', b'x'),
                   lambda m: m['sources'][0].__setitem__('note', object()),
                   lambda m: m['sources'][0].__setitem__('note', {1, 2})):
            m = make_manifest()
            fn(m)
            self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_lone_surrogate_text_is_refused_cleanly(self):
        m = make_manifest()
        m['manifest_id'] = 'id-\ud800'
        self.refuses('schema_invalid', mc.validate_manifest, m)


class ManifestSemantics(Base):
    def test_duplicate_check_id(self):
        def dup(m):
            m['checks'].insert(1, copy.deepcopy(m['checks'][0]))
        self.refuses('duplicate_check', mc.validate_manifest, self.mutated(dup))

    def test_duplicate_check_id_with_different_content(self):
        def dup(m):
            twin = copy.deepcopy(m['checks'][2])
            twin['evaluator_id'] = 'ev.weaker'
            twin['not_applicable_reasons'] = ['input_not_supplied', 'not_in_scope']
            m['checks'].insert(3, twin)
        self.refuses('duplicate_check', mc.validate_manifest, self.mutated(dup))

    def test_duplicate_check_ids_never_collapse_into_a_complete_report(self):
        m = self.mutated(lambda x: x['checks'].insert(1, copy.deepcopy(x['checks'][0])))
        self.refuses('duplicate_check', self.complete, manifest=m, executed=make_executed(make_manifest()))

    def test_unknown_source(self):
        for sid in ('src.other', 'SRC.VERIFIER', SRC + ' ', ' ' + SRC, SRC + '\u200b'):
            m = self.mutated(lambda x: x['checks'][2].__setitem__('source_id', sid))
            self.refuses('unknown_source', mc.validate_manifest, m)

    def test_source_id_unicode_lookalikes(self):
        def renamed(new):
            def fn(m):
                m['sources'][0]['source_id'] = new
                for c in m['checks']:
                    c['source_id'] = new
                m['checks'][2]['source_id'] = unicodedata.normalize('NFD', new)
            return fn
        composed = 'src.\u00e9'
        self.assertNotEqual(composed, unicodedata.normalize('NFD', composed))
        self.refuses('unknown_source', mc.validate_manifest, self.mutated(renamed(composed)))

    def test_cyrillic_lookalike_source(self):
        m = self.mutated(lambda x: x['checks'][2].__setitem__('source_id', 'src.v\u0435rifier'))
        self.refuses('unknown_source', mc.validate_manifest, m)

    def test_unknown_input_kind(self):
        for kind in ('ghost', 'REQUEST', 'request ', 'requ\u0435st', ''):
            def fn(x, kind=kind):
                x['checks'][1]['input_kind'] = kind
                x['checks'][1]['check_id'] = 'input_read.' + kind  # keep the id rule satisfied
            m = self.mutated(fn)
            self.refuses_in({'unknown_input_kind', 'schema_invalid'} if kind == '' else {'unknown_input_kind'},
                            mc.validate_manifest, m)

    def test_input_kind_normalization_lookalike(self):
        def fn(m):
            m['input_kinds'] = ['req\u00e9']
            m['checks'][1]['input_kind'] = unicodedata.normalize('NFD', 'req\u00e9')
            m['checks'][1]['check_id'] = 'input_read.' + m['checks'][1]['input_kind']
        self.refuses('unknown_input_kind', mc.validate_manifest, self.mutated(fn))

    def test_input_read_check_id_must_be_input_read_dot_kind(self):
        # review N7
        for cid in ('input_read.other', 'input_read.', 'input_read.REQUEST', 'input_read.request ',
                    'check.input.request', 'input_read.requ\u0435st'):
            m = self.mutated(lambda x, cid=cid: x['checks'][1].__setitem__('check_id', cid))
            self.refuses('schema_invalid', mc.validate_manifest, m)
        mc.validate_manifest(make_manifest())

    def test_trailing_newline_on_revision_and_digest_is_refused(self):
        # review N1: `$` would accept a trailing newline
        m = make_manifest()
        m['sources'][0]['revision'] = REV + '\n'
        self.refuses('schema_invalid', mc.validate_manifest, redigest(m))
        m = make_manifest()
        m['digest'] += '\n'
        self.refuses('schema_invalid', mc.validate_manifest, m)

    def test_unknown_input_kind_on_verifier_check_too(self):
        m = self.mutated(lambda x: x['checks'][2].__setitem__('input_kind', 'ghost'))
        self.refuses('unknown_input_kind', mc.validate_manifest, m)

    def test_unknown_reason(self):
        for reason in ('operator_waiver', 'Not_In_Scope', 'not_in_scope ', 'not_in_sc\u043epe'):
            m = self.mutated(lambda x: x['checks'][0].__setitem__('not_applicable_reasons', [reason]))
            self.refuses('unknown_reason', mc.validate_manifest, m)

    def test_check_cannot_widen_the_closed_reason_set(self):
        def fn(m):
            m['not_applicable_reasons'] = ['not_in_scope']
            m['checks'][1]['not_applicable_reasons'] = ['input_not_supplied']
        self.refuses('unknown_reason', mc.validate_manifest, self.mutated(fn))

    def test_nfc_and_nfd_check_ids_are_distinct_checks(self):
        nfc = 'check.caf\u00e9'
        nfd = unicodedata.normalize('NFD', nfc)

        def fn(m):
            for name in (nfc, nfd):
                c = copy.deepcopy(m['checks'][2])
                c['check_id'] = name
                m['checks'].append(c)
            m['checks'].sort(key=lambda c: c['check_id'])
        m = self.mutated(fn)
        self.assertEqual(mc.validate_manifest(m), rr.record_digest(m))
        # executing only one spelling leaves the other one skipped
        rec = make_record()
        for name in (nfc, nfd):
            rec['rule_table'].append(dict(rule_of(rec, CID_GRANT), rule_id=name))
        redigest(rec)
        executed = [e for e in make_executed(m) if e['check_id'] != nfd]
        self.refuses('skipped_mandatory_check', mc.check_completeness, m, rec, executed,
                     floor_check_ids=FLOOR)


class DigestAndPin(Base):
    def test_digest_ignores_key_order(self):
        m = make_manifest()
        shuffled = dict(reversed(list(m.items())))
        shuffled['checks'] = [dict(reversed(list(c.items()))) for c in m['checks']]
        self.assertEqual(mc.validate_manifest(shuffled), mc.validate_manifest(m))

    def test_tamper_without_redigest_is_digest_mismatch(self):
        for fn in (lambda m: m['checks'][2].__setitem__('evaluator_version', 9),
                   lambda m: m['checks'][2].__setitem__('evaluator_id', 'ev.other'),
                   lambda m: m['checks'][2]['not_applicable_reasons'].append('not_in_scope'),
                   lambda m: m['checks'].pop(),
                   lambda m: m['checks'].pop(0),
                   lambda m: m['sources'][0].__setitem__('revision', 'b' * 40),
                   lambda m: m['sources'][0].__setitem__('note', 'edited'),
                   lambda m: m.__setitem__('manifest_id', 'manifest-2'),
                   lambda m: m.__setitem__('not_applicable_reasons', ['not_in_scope'])):
            m = make_manifest()
            fn(m)
            self.refuses_in({'digest_mismatch', 'unknown_reason'}, mc.validate_manifest, m)

    def test_removed_check_without_redigest_is_digest_mismatch(self):
        m = make_manifest()
        m['checks'].pop()
        self.refuses('digest_mismatch', mc.validate_manifest, m)

    def test_digest_over_body_that_includes_digest_member_is_wrong(self):
        import hashlib
        m = make_manifest()
        wrong = 'sha256:' + hashlib.sha256(rr.jcs_bytes(m)).hexdigest()
        m['digest'] = wrong
        self.refuses('digest_mismatch', mc.validate_manifest, m)

    def test_digest_of_a_different_manifest_is_wrong(self):
        other = self.mutated(lambda m: m.__setitem__('manifest_id', 'other'))
        m = make_manifest()
        m['digest'] = other['digest']
        self.refuses('digest_mismatch', mc.validate_manifest, m)

    def test_registry_record_digest_cannot_stand_in(self):
        m = make_manifest()
        m['digest'] = make_record()['digest']
        self.refuses('digest_mismatch', mc.validate_manifest, m)

    def test_pin_matches_and_mismatches(self):
        m = make_manifest()
        self.assertEqual(mc.validate_manifest(m, pin=m['digest']), m['digest'])
        other = 'sha256:' + '1' * 64
        for pin in (other, make_record()['digest']):
            self.refuses('pin_mismatch', mc.validate_manifest, m, pin=pin)

    def test_malformed_pin_is_pin_mismatch_per_specification(self):
        # the specification: pin, when given, is the digest the manifest must have. Any pin that is
        # not None and not equal to the computed digest is a pin_mismatch, including falsy values
        m = make_manifest()
        for pin in ('', 'sha256:' + m['digest'].split(':')[1].upper(), m['digest'][:-1],
                    ' ' + m['digest'], 0, False, b'x'):
            self.refuses('pin_mismatch', mc.validate_manifest, m, pin=pin)

    def test_pin_of_original_does_not_accept_a_tampered_but_redigested_manifest(self):
        original = make_manifest()
        tampered = self.mutated(lambda m: m['checks'].pop())
        self.refuses('pin_mismatch', mc.validate_manifest, tampered, pin=original['digest'])

    def test_pin_is_checked_after_digest(self):
        m = make_manifest()
        m['checks'].pop()
        self.refuses('digest_mismatch', mc.validate_manifest, m, pin=make_manifest()['digest'])

    def test_pin_mismatch_in_completeness(self):
        for pin in ('sha256:' + '2' * 64, make_record()['digest'], '', 0, False, 5, b'x', 'x'):
            self.refuses_complete('pin_mismatch', pin=pin)

    def test_pin_accepted_in_completeness(self):
        m = make_manifest()
        self.assertTrue(self.complete(manifest=m, pin=m['digest'])['complete'])

    def test_pin_is_keyword_only_and_floor_is_required(self):
        m, r = make_manifest(), make_record()
        with self.assertRaises(TypeError):
            mc.validate_manifest(m, m['digest'])
        with self.assertRaises(TypeError):
            mc.check_completeness(m, r, make_executed(m))
        with self.assertRaises(TypeError):
            mc.check_completeness(m, r, make_executed(m), FLOOR)


class FloorAndRecord(Base):
    def test_floor_id_not_in_manifest(self):
        for floor in ({CID_GRANT, 'check.mandatory.absent'}, {'check.mandatory.absent'},
                      {unicodedata.normalize('NFD', 'check.mandatory.gr\u00e9nt')},
                      {CID_GRANT.upper()}, {CID_GRANT + ' '}, {'check.mandatory.gr\u0430nt'}):
            self.refuses_complete('floor_not_in_manifest', floor=floor)

    def test_floor_accepts_collections_but_not_a_superset_of_the_manifest(self):
        for floor in (FLOOR, frozenset(FLOOR), sorted(FLOOR), tuple(sorted(FLOOR))):
            self.assertTrue(self.complete(floor=floor)['complete'])
        floor = FLOOR | {CID_NOTE, CID_INPUT}
        self.assertTrue(self.complete(floor=floor)['complete'])
        self.refuses_complete('floor_not_in_manifest', floor=floor | {'check.zzz'})

    def test_floor_check_removed_from_manifest(self):
        m = self.mutated(lambda x: x['checks'].__setitem__(slice(None), [c for c in x['checks']
                                                                         if c['check_id'] != CID_GRANT]))
        executed = [e for e in make_executed() if e['check_id'] != CID_GRANT]
        self.refuses_complete('floor_not_in_manifest', manifest=m, executed=executed)

    def test_empty_manifest_checks_never_complete(self):
        m = self.mutated(lambda x: x.__setitem__('checks', []))
        self.refuses_complete('floor_not_in_manifest', manifest=m, executed=[])

    def test_manifest_is_validated_before_the_floor(self):
        m = make_manifest()
        m['checks'].pop()
        self.refuses_complete('digest_mismatch', manifest=m, floor={'check.mandatory.absent'})

    def test_floor_is_checked_before_the_record(self):
        rec = make_record()
        rec['digest'] = 'sha256:' + '3' * 64
        self.refuses_complete('floor_not_in_manifest', record=rec, floor={'check.mandatory.absent'})

    def test_record_is_checked_before_results(self):
        rec = make_record()
        rec['digest'] = 'sha256:' + '3' * 64
        self.refuses_complete('registry_record_invalid', record=rec, executed=[])

    def test_record_invalid_variants(self):
        def advisory(r):
            rule_of(r, CID_GRANT)['status'] = 'advisory'

        def predicate(r):
            rule_of(r, CID_POLICY)['applicability'] = {'kind': 'predicate', 'predicate': 'p', 'source_ref': 'src:a'}

        def missing_rule(r):
            r['rule_table'] = [x for x in r['rule_table'] if x['rule_id'] != CID_GRANT]

        def shadow(r):
            r['rule_table'].append(dict(rule_of(r, CID_GRANT), status='advisory'))

        def dup_rule(r):
            r['rule_table'].append(copy.deepcopy(rule_of(r, CID_POLICY)))

        def unqualified(r):
            r['evaluators'][2]['qualification_ref'] = ''

        def unknown_ev(r):
            r['evaluators'] = [e for e in r['evaluators'] if e['evaluator_id'] != 'ev.grant']

        def dup_ev(r):
            r['evaluators'].append(dict(r['evaluators'][2], qualification_ref=''))

        def extra(r):
            r['active'] = True

        for fn in (advisory, predicate, missing_rule, shadow, dup_rule, dup_ev, extra):
            rec = make_record()
            fn(rec)
            redigest(rec)
            self.refuses_complete('registry_record_invalid', record=rec)
        # Q2: an evaluator used by a rule and blank or unlisted keeps its own precise code
        for fn, code in ((unqualified, 'unqualified_evaluator'), (unknown_ev, 'unknown_evaluator')):
            rec = make_record()
            fn(rec)
            redigest(rec)
            self.refuses_complete(code, record=rec)

    def test_record_not_an_object_or_wrong_profile(self):
        for bad in (None, [], 'record', make_manifest()):
            self.refuses_complete('registry_record_invalid', record=bad)
        rec = make_record(profile='ocs-registry-record/1')
        self.refuses_complete('registry_record_invalid', record=rec)

    def test_record_tampered_after_digest(self):
        rec = make_record()
        rule_of(rec, CID_GRANT)['status'] = 'advisory'
        self.refuses_complete('registry_record_invalid', record=rec)

    def test_non_floor_rule_missing(self):
        for rid in (CID_NOTE, CID_INPUT):
            rec = make_record()
            rec['rule_table'] = [x for x in rec['rule_table'] if x['rule_id'] != rid]
            redigest(rec)
            self.refuses_complete('registry_rule_missing', record=rec)

    def test_non_floor_rule_lookalike_ids_do_not_satisfy(self):
        variants = (CID_NOTE.upper(), CID_NOTE + ' ', CID_NOTE.replace('e', '\u0435', 1),
                    CID_NOTE + '\u200b', ' ' + CID_NOTE)
        for variant in variants:
            rec = make_record()
            rule_of(rec, CID_NOTE)['rule_id'] = variant
            redigest(rec)
            self.refuses_complete('registry_rule_missing', record=rec)

    def test_non_floor_rule_unicode_normalization(self):
        nfc = 'check.extra.caf\u00e9'
        nfd = unicodedata.normalize('NFD', nfc)
        m = self.mutated(lambda x: (x['checks'].append(dict(copy.deepcopy(x['checks'][0]), check_id=nfc)),
                                    x['checks'].sort(key=lambda c: c['check_id'])))
        rec = make_record()
        rec['rule_table'].append(dict(rule_of(rec, CID_NOTE), rule_id=nfd))
        redigest(rec)
        self.refuses_complete('registry_rule_missing', manifest=m, record=rec, executed=make_executed(m))

    def test_non_floor_rule_advisory(self):
        for rid in (CID_NOTE, CID_INPUT):
            rec = make_record()
            rule_of(rec, rid)['status'] = 'advisory'
            redigest(rec)
            self.refuses_complete('registry_rule_not_required', record=rec)

    def test_non_floor_rule_conditional_applicability(self):
        for rid in (CID_NOTE, CID_INPUT):
            rec = make_record()
            rule_of(rec, rid)['applicability'] = {'kind': 'predicate', 'predicate': 'when_x',
                                                  'source_ref': 'src:a'}
            redigest(rec)
            self.refuses_complete('registry_rule_not_required', record=rec)

    def test_non_floor_advisory_rule_cannot_hide_behind_floor_membership_of_others(self):
        rec = make_record()
        rule_of(rec, CID_NOTE)['status'] = 'advisory'
        redigest(rec)
        self.refuses_complete('registry_rule_not_required', record=rec, floor=FLOOR | {CID_INPUT})

    def test_same_check_floor_membership_turns_advisory_into_record_invalid(self):
        rec = make_record()
        rule_of(rec, CID_NOTE)['status'] = 'advisory'
        redigest(rec)
        self.refuses_complete('registry_record_invalid', record=rec, floor=FLOOR | {CID_NOTE})

    def test_floor_elsewhere_still_requires_every_manifest_check_to_be_required_always(self):
        rec = make_record()
        rule_of(rec, CID_GRANT)['status'] = 'advisory'
        redigest(rec)
        self.refuses_complete('registry_rule_not_required', record=rec, floor={CID_NOTE})

    def test_floor_elsewhere_still_requires_every_manifest_check_to_have_a_rule(self):
        rec = make_record()
        rec['rule_table'] = [x for x in rec['rule_table'] if x['rule_id'] != CID_POLICY]
        redigest(rec)
        self.refuses_complete('registry_rule_missing', record=rec, floor={CID_NOTE})

    def test_record_rules_not_in_manifest_do_not_matter_but_cannot_substitute(self):
        rec = make_record()
        rec['rule_table'].append(dict(rule_of(rec, CID_NOTE), rule_id='check.unrelated'))
        redigest(rec)
        self.assertTrue(self.complete(record=rec)['complete'])
        m = self.mutated(lambda x: x['checks'].__setitem__(slice(None), [c for c in x['checks']
                                                                         if c['check_id'] != CID_NOTE]))
        self.assertEqual(len(self.complete(manifest=m, record=rec,
                                           executed=make_executed(m))['checks']), 3)


class Evaluators(Base):
    def test_wrong_evaluator_id(self):
        for wrong in ('ev.policy', 'ev.ghost', 'EV.GRANT', 'ev.grant ', 'ev.gr\u0430nt'):
            ex = make_executed(**{CID_GRANT: dict(evaluator_id=wrong)})
            self.refuses_complete('evaluator_mismatch', executed=ex)
        ex = make_executed(**{CID_GRANT: dict(evaluator_id='')})
        self.refuses_complete('schema_invalid', executed=ex)

    def test_wrong_evaluator_version(self):
        rec = make_record()
        rec['evaluators'].append(dict(evaluator_id='ev.grant', version=2, qualification_ref='q:g2'))
        redigest(rec)
        for ver in (2, 99):
            ex = make_executed(**{CID_GRANT: dict(evaluator_version=ver)})
            self.refuses('evaluator_mismatch', mc.check_completeness, make_manifest(), rec, ex,
                         floor_check_ids=FLOOR)
        for ver in (0, -1):
            ex = make_executed(**{CID_GRANT: dict(evaluator_version=ver)})
            self.refuses('schema_invalid', mc.check_completeness,
                         make_manifest(), rec, ex, floor_check_ids=FLOOR)

    def test_evaluator_version_type_tricks_are_refused(self):
        class MyInt(int):
            pass
        for bad in (True, 1.0, MyInt(1), '1', None, [1], float('nan')):
            ex = make_executed(**{CID_GRANT: dict(evaluator_version=bad)})
            self.refuses_complete('schema_invalid', executed=ex)

    def test_higher_qualified_version_does_not_substitute(self):
        rec = make_record()
        rec['evaluators'].append(dict(evaluator_id='ev.grant', version=5, qualification_ref='q:g5'))
        redigest(rec)
        ex = make_executed(**{CID_GRANT: dict(evaluator_version=5)})
        self.refuses('evaluator_mismatch', mc.check_completeness, make_manifest(), rec, ex,
                     floor_check_ids=FLOOR)

    def test_evaluator_swapped_between_checks(self):
        ex = make_executed(**{CID_GRANT: dict(evaluator_id='ev.policy'),
                              CID_POLICY: dict(evaluator_id='ev.grant')})
        self.refuses_complete('evaluator_mismatch', executed=ex)

    def test_mismatch_is_reported_before_qualification(self):
        ex = make_executed(**{CID_GRANT: dict(evaluator_id='ev.unlisted')})
        self.refuses_complete('evaluator_mismatch', executed=ex)

    def _manifest_with_alt_evaluator(self, version=1):
        return self.mutated(lambda m: m['checks'][0].update(evaluator_id='ev.alt', evaluator_version=version))

    def _record_with_alt_rule(self, listed=None, version=1):
        """A record whose rule entry for the first manifest check uses ev.alt (as the manifest does)."""
        rec = make_record()
        rule_of(rec, CID_NOTE).update(evaluator_id='ev.alt', evaluator_version=version)
        if listed is not None:
            rec['evaluators'].append(listed)
        return redigest(rec)

    def test_unqualified_evaluator_empty_reference(self):
        m = self._manifest_with_alt_evaluator()
        rec = self._record_with_alt_rule(dict(evaluator_id='ev.alt', version=1, qualification_ref=''))
        self.refuses_complete('unqualified_evaluator', manifest=m, record=rec, executed=make_executed(m))

    def test_unqualified_evaluator_whitespace_reference(self):
        m = self._manifest_with_alt_evaluator()
        for ref in (' ', '\t', '\n ', '\u00a0'):
            rec = self._record_with_alt_rule(dict(evaluator_id='ev.alt', version=1, qualification_ref=ref))
            self.refuses_complete('unqualified_evaluator', manifest=m, record=rec, executed=make_executed(m))

    def test_evaluator_not_listed_or_only_listed_for_another_version(self):
        m = self._manifest_with_alt_evaluator()
        rec = self._record_with_alt_rule()
        self.refuses_complete('unknown_evaluator', manifest=m, record=rec, executed=make_executed(m))
        rec = self._record_with_alt_rule(dict(evaluator_id='ev.alt', version=2, qualification_ref='q:alt2'))
        self.refuses_complete('unknown_evaluator', manifest=m, record=rec, executed=make_executed(m))

    def test_evaluator_listed_only_under_a_lookalike_id(self):
        m = self._manifest_with_alt_evaluator()
        rec = self._record_with_alt_rule(dict(evaluator_id='ev.\u0430lt', version=1, qualification_ref='q:x'))
        self.refuses_complete('unknown_evaluator', manifest=m, record=rec, executed=make_executed(m))

    def test_qualified_evaluator_passes_when_listed(self):
        m = self._manifest_with_alt_evaluator()
        rec = self._record_with_alt_rule(dict(evaluator_id='ev.alt', version=1, qualification_ref='q:alt'))
        self.assertTrue(self.complete(manifest=m, record=rec, executed=make_executed(m))['complete'])

    def test_unqualified_evaluator_listed_but_used_by_no_rule_is_no_longer_the_binding(self):
        # Q2: the manifest's pair must be the rule's pair, so a manifest evaluator that no rule
        # uses is a rule_evaluator_mismatch (the listing, qualified or not, does not matter).
        m = self._manifest_with_alt_evaluator()
        for ref in ('', 'q:alt'):
            rec = make_record()
            rec['evaluators'].append(dict(evaluator_id='ev.alt', version=1, qualification_ref=ref))
            redigest(rec)
            rr.validate_record(rec, floor_mandatory_rule_ids=FLOOR)
            self.refuses_complete('rule_evaluator_mismatch', manifest=m, record=rec,
                                  executed=make_executed(m))

    def test_a_different_but_qualified_evaluator_is_not_interchangeable(self):
        # Q2: the rule entry names another qualified evaluator than the manifest check.
        for ev, ver in (('ev.policy', 1), ('ev.note', 2), ('ev.grant', 1)):
            rec = make_record()
            rule_of(rec, CID_GRANT).update(evaluator_id=ev, evaluator_version=ver)
            redigest(rec)
            if (ev, ver) == ('ev.grant', 1):
                self.assertTrue(self.complete(record=rec)['complete'])  # same pair: control
                continue
            self.refuses_complete('rule_evaluator_mismatch', record=rec)

    def test_rule_evaluator_mismatch_by_version_only(self):
        rec = make_record()
        rec['evaluators'].append(dict(evaluator_id='ev.grant', version=2, qualification_ref='q:g2'))
        rule_of(rec, CID_GRANT)['evaluator_version'] = 2
        redigest(rec)
        self.refuses_complete('rule_evaluator_mismatch', record=rec)

    def test_rule_evaluator_mismatch_on_a_second_entry_of_the_same_rule(self):
        rec = make_record()
        rec['rule_table'].append(dict(rule_of(rec, CID_GRANT), profile='other',
                                      evaluator_id='ev.policy'))
        redigest(rec)
        self.refuses_complete('rule_evaluator_mismatch', record=rec)

    def test_rule_binding_precedes_executed_checks(self):
        rec = make_record()
        rule_of(rec, CID_GRANT).update(evaluator_id='ev.policy')
        redigest(rec)
        ex = make_executed(**{CID_GRANT: dict(evaluator_id='ev.unlisted')})
        self.refuses_complete('rule_evaluator_mismatch', record=rec, executed=ex)


class RepairNegatives(Base):
    """Q2 and Q3 repair: negative controls through the public function (seam cases are in
    tests/test_mandatory_manifest_v1.py). Developer-owned; not Qualification evidence."""

    def to_v1(self, conditional=None):
        """The fixture manifest as a /1 manifest; `conditional` maps check ids to a predicate id."""
        conditional = conditional or {}

        def edit(m):
            m['profile'] = 'ocs-mandatory-manifest/1'
            m['schema_version'] = 1
            used = sorted(set(conditional.values()))
            m['predicates'] = [dict(predicate_id=p, basis='record_class', source_ids=[SRC],
                                    justifications=['not_in_class']) for p in used]
            m['surrogates'] = []
            for c in m['checks']:
                pred = conditional.get(c['check_id'])
                c['applicability'] = {'kind': 'unconditional'} if pred is None else \
                    {'kind': 'required_when_applicable', 'predicate': pred}
        return self.mutated(edit)

    def test_unconditional_v1_manifest_completes_against_a_v0_record(self):
        m = self.to_v1()
        report = self.complete(manifest=m, executed=make_executed(m))
        self.assertEqual(report['counts']['inapplicable'], 0)
        self.assertTrue(all(c['predicate'] is None for c in report['checks']))

    def test_conditional_check_against_a_v0_record(self):
        m = self.to_v1({CID_NOTE: 'class_note'})
        self.refuses_complete('applicability_unsupported_by_registry', manifest=m,
                              executed=make_executed(m))

    def test_conditional_floor_check(self):
        m = self.to_v1({CID_NOTE: 'class_note'})
        self.refuses_complete('floor_check_conditional', manifest=m, floor=FLOOR | {CID_NOTE},
                              executed=make_executed(m))

    def test_unknown_predicate(self):
        m = self.to_v1({CID_NOTE: 'class_note', CID_INPUT: 'class_note'})
        m['checks'][0]['applicability']['predicate'] = 'class_nope'
        redigest(m)
        self.refuses_complete('unknown_predicate', manifest=m, executed=make_executed(m))

    def test_dispositions_are_refused_for_a_v0_manifest(self):
        self.refuses_complete('schema_invalid', dispositions=[])

    def test_dispositions_for_an_unconditional_v1_check_are_refused_through_the_public_function(self):
        # an unconditional v1 check cannot be closed by a disposition, even against a v0 record
        m = self.to_v1()
        d = dict(check_id=CID_GRANT, predicate='x', justification='y', evaluator_id='ev.grant',
                 evaluator_version=1)
        ex = [e for e in make_executed(m) if e['check_id'] != CID_GRANT]
        self.refuses_complete('inapplicable_not_permitted', manifest=m, executed=ex, dispositions=[d])

    def test_rule_evaluator_mismatch_cases(self):
        for ev, ver in (('ev.policy', 1), ('ev.note', 2), ('ev.grant', 2)):
            rec = make_record()
            rec['evaluators'].append(dict(evaluator_id='ev.grant', version=2, qualification_ref='q:g2'))
            rule_of(rec, CID_GRANT).update(evaluator_id=ev, evaluator_version=ver)
            redigest(rec)
            with self.subTest(ev=ev, ver=ver):
                self.refuses_complete('rule_evaluator_mismatch', record=rec)

    def test_dispositions_default_is_none_and_v0_report_shape_is_unchanged(self):
        report = self.complete()
        self.assertEqual(set(report), {'manifest_digest', 'record_digest', 'complete', 'counts', 'checks'})
        self.assertEqual(set(report['counts']), set(OUTCOMES))
        self.assertTrue(all(set(c) == {'check_id', 'outcome', 'reason'} for c in report['checks']))


class ExecutedResults(Base):
    def test_duplicate_results(self):
        base = make_executed()
        for extra in (dict(base[2]), dict(base[2], outcome='failed'),
                      dict(base[2], outcome='not_applicable', reason='input_not_supplied')):
            self.refuses_complete('duplicate_result', executed=base + [extra])

    def test_duplicate_result_where_first_is_a_failure(self):
        ex = make_executed(**{CID_GRANT: dict(outcome='failed')})
        ex.append(dict(ex[2], outcome='passed'))
        self.refuses_complete('duplicate_result', executed=ex)

    def test_unexpected_check(self):
        for cid in ('check.mandatory.extra', CID_GRANT.upper(), CID_GRANT + ' ', ' ' + CID_GRANT,
                    CID_GRANT + '\u200b', 'check.mandatory.gr\u0430nt'):
            ex = make_executed()
            ex.append(dict(ex[2], check_id=cid))
            self.refuses_complete('unexpected_check', executed=ex)
        ex = make_executed()
        ex.append(dict(ex[2], check_id=''))
        self.refuses_complete('schema_invalid', executed=ex)

    def test_lookalike_cannot_replace_the_real_check(self):
        ex = make_executed()
        ex[2] = dict(ex[2], check_id='check.mandatory.gr\u0430nt')
        self.refuses_complete('unexpected_check', executed=ex)

    def test_unicode_normalized_result_id_does_not_match(self):
        nfc = 'check.extra.caf\u00e9'
        m = self.mutated(lambda x: (x['checks'].append(dict(copy.deepcopy(x['checks'][0]), check_id=nfc)),
                                    x['checks'].sort(key=lambda c: c['check_id'])))
        rec = make_record()
        rec['rule_table'].append(dict(rule_of(rec, CID_NOTE), rule_id=nfc))
        redigest(rec)
        ex = make_executed(m)
        for e in ex:
            if e['check_id'] == nfc:
                e['check_id'] = unicodedata.normalize('NFD', nfc)
        self.refuses_complete('unexpected_check', manifest=m, record=rec, executed=ex)

    def test_unexpected_result_alongside_complete_set(self):
        ex = make_executed()
        ex.insert(0, dict(check_id='check.injected', outcome='passed', reason=None,
                          evaluator_id='ev.grant', evaluator_version=1))
        self.refuses_complete('unexpected_check', executed=ex)

    def test_unexpected_check_precedes_missing_check(self):
        ex = make_executed()[1:] + [dict(make_executed()[0], check_id='check.injected')]
        self.refuses_complete('unexpected_check', executed=ex)

    def test_non_hashable_or_non_text_check_ids_are_refusals(self):
        for cid in (None, 1, ['x'], {'a': 1}, True, b'x'):
            ex = make_executed()
            ex[0] = dict(ex[0], check_id=cid)
            self.refuses_complete('schema_invalid', executed=ex)

    def test_invalid_outcomes(self):
        for bad in ('PASSED', 'pass', 'ok', 'skipped', 'passed ', ' passed', 'Passed', 'not-applicable',
                    'n/a', 'waived', ''):
            ex = make_executed(**{CID_GRANT: dict(outcome=bad)})
            self.refuses_complete('invalid_outcome', executed=ex)

    def test_non_text_outcomes_are_schema_invalid_not_invalid_outcome(self):
        # governor ruling: invalid_outcome is only for an unknown outcome string
        for bad in (None, 1, True, 0, ['passed'], {'a': 1}, b'passed'):
            ex = make_executed(**{CID_GRANT: dict(outcome=bad)})
            self.refuses_complete('schema_invalid', executed=ex)

    def test_invalid_outcome_beats_a_later_skip(self):
        ex = make_executed(**{CID_GRANT: dict(outcome='skipped')})[:-1]
        self.refuses_complete('invalid_outcome', executed=ex)

    def test_not_applicable_reason_not_allowed(self):
        # the reason is in the manifest's closed set but not in this check's own list
        for cid, reason in ((CID_GRANT, 'not_in_scope'), (CID_POLICY, 'input_not_supplied'),
                            (CID_NOTE, 'input_not_supplied'), (CID_INPUT, 'not_in_scope')):
            ex = make_executed(**{cid: dict(outcome='not_applicable', reason=reason)})
            self.refuses_complete('not_applicable_reason_not_allowed', executed=ex)

    def test_not_applicable_reason_outside_closed_set_or_malformed(self):
        for reason in ('operator_waiver', 'NOT_IN_SCOPE', 'not_in_scope ', 'not_in_sc\u043epe',
                       unicodedata.normalize('NFD', 'not_in_sc\u00f3pe'), ''):
            ex = make_executed(**{CID_NOTE: dict(outcome='not_applicable', reason=reason)})
            self.refuses_complete('not_applicable_reason_not_allowed', executed=ex)

    def test_not_applicable_without_a_reason(self):
        ex = make_executed(**{CID_NOTE: dict(outcome='not_applicable', reason=None)})
        self.refuses_complete('not_applicable_reason_not_allowed', executed=ex)

    def test_not_applicable_with_unhashable_or_non_text_reason(self):
        for reason in (1, True, ['not_in_scope'], {'a': 1}, b'not_in_scope'):
            ex = make_executed(**{CID_NOTE: dict(outcome='not_applicable', reason=reason)})
            self.refuses_complete('schema_invalid', executed=ex)

    def test_mandatory_check_with_empty_reason_list_can_never_be_not_applicable(self):
        for cid in (CID_GRANT, CID_POLICY):
            for reason in CLOSED_REASONS + [None]:
                ex = make_executed(**{cid: dict(outcome='not_applicable', reason=reason)})
                self.refuses_complete('not_applicable_reason_not_allowed', executed=ex)

    def test_reason_on_a_non_not_applicable_outcome_is_refused(self):
        for outcome in ('passed', 'failed', 'error'):
            ex = make_executed(**{CID_NOTE: dict(outcome=outcome, reason='not_in_scope')})
            self.refuses_complete('schema_invalid', executed=ex)

    def test_skipped_mandatory_check(self):
        for drop in (CID_GRANT, CID_POLICY, CID_NOTE, CID_INPUT):
            ex = [e for e in make_executed() if e['check_id'] != drop]
            exc = self.refuses_complete('skipped_mandatory_check', executed=ex)
            self.assertIn(drop, str(exc))

    def test_skip_message_lists_every_missing_id(self):
        ex = [e for e in make_executed() if e['check_id'] in (CID_NOTE,)]
        exc = self.refuses_complete('skipped_mandatory_check', executed=ex)
        for cid in (CID_INPUT, CID_GRANT, CID_POLICY):
            self.assertIn(cid, str(exc))
        self.assertNotIn(CID_NOTE, str(exc))

    def test_empty_executed_list_is_all_skipped(self):
        exc = self.refuses_complete('skipped_mandatory_check', executed=[])
        for cid in (CID_NOTE, CID_INPUT, CID_GRANT, CID_POLICY):
            self.assertIn(cid, str(exc))

    def test_executed_container_and_entry_shapes(self):
        base = make_executed()
        bad_containers = (None, {}, 'results', 0, {e['check_id']: e for e in base})
        for bad in bad_containers:
            self.refuses_complete('schema_invalid', executed=bad)
        entry = base[2]
        broken = [dict(entry, verdict='pass'), dict(entry, optional=True),
                  {k: v for k, v in entry.items() if k != 'reason'},
                  {k: v for k, v in entry.items() if k != 'evaluator_version'},
                  {k: v for k, v in entry.items() if k != 'outcome'},
                  {k: v for k, v in entry.items() if k != 'check_id'}, None, 'x', [entry], tuple(entry.items())]
        for bad in broken:
            ex = list(base)
            ex[2] = bad
            self.refuses_complete('schema_invalid', executed=ex)

    def test_results_cannot_be_hidden_by_a_failing_outcome_replacement(self):
        # a failed or error result closes the check as run, it is never a silent skip or a refusal
        ex = make_executed(**{CID_GRANT: dict(outcome='error'), CID_POLICY: dict(outcome='failed')})
        report = self.complete(executed=ex)
        by_id = {c['check_id']: c for c in report['checks']}
        self.assertEqual(by_id[CID_GRANT]['outcome'], 'error')
        self.assertEqual(by_id[CID_POLICY]['outcome'], 'failed')

    def test_inputs_are_not_mutated_by_refusals_or_success(self):
        m, r, ex = make_manifest(), make_record(), make_executed()
        snap = copy.deepcopy((m, r, ex))
        mc.check_completeness(m, r, ex, floor_check_ids=FLOOR)
        self.assertEqual((m, r, ex), snap)
        ex2 = make_executed(**{CID_GRANT: dict(outcome='bogus')})
        snap2 = copy.deepcopy(ex2)
        with self.assertRaises(mc.ManifestRefusal):
            mc.check_completeness(m, r, ex2, floor_check_ids=FLOOR)
        self.assertEqual(ex2, snap2)
        self.assertEqual(m, snap[0])
        self.assertEqual(r, snap[1])


class ReportShape(Base):
    def test_exact_report_members(self):
        report = self.complete()
        self.assertEqual(set(report), {'manifest_digest', 'record_digest', 'complete', 'counts', 'checks'})
        self.assertIs(report['complete'], True)

    def test_digests_are_those_of_the_inputs(self):
        m, r = make_manifest(), make_record()
        report = self.complete(manifest=m, record=r)
        self.assertEqual(report['manifest_digest'], m['digest'])
        self.assertEqual(report['record_digest'], r['digest'])

    def test_no_verdict_grant_pin_or_activation_anywhere(self):
        ex = make_executed(**{CID_GRANT: dict(outcome='failed'), CID_POLICY: dict(outcome='error')})
        report = self.complete(executed=ex)
        banned = ('verdict', 'decision', 'grant', 'authorize', 'approve', 'pass_fail', 'ok', 'pin',
                  'activate', 'activation', 'accepted', 'result', 'status', 'clearance', 'certif')

        def keys(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    yield k
                    yield from keys(v)
            elif isinstance(obj, list):
                for v in obj:
                    yield from keys(v)
        for key in keys(report):
            for word in banned:
                self.assertNotIn(word, key.lower(), key)
        self.assertEqual(set(report['counts']) - set(OUTCOMES), set())
        self.assertEqual(set(report['checks'][0]), {'check_id', 'outcome', 'reason'})

    def test_a_failed_check_does_not_make_the_report_incomplete_or_add_a_verdict(self):
        ex = make_executed(**{CID_GRANT: dict(outcome='failed'), CID_POLICY: dict(outcome='error')})
        report = self.complete(executed=ex)
        self.assertIs(report['complete'], True)
        self.assertEqual(report['counts'].get('failed', 0), 1)
        self.assertEqual(report['counts'].get('error', 0), 1)
        self.assertEqual(report['counts'].get('passed', 0), 2)
        self.assertEqual(report['counts'].get('not_applicable', 0), 0)

    def test_counts_cover_every_check_exactly_once(self):
        ex = make_executed(**{CID_NOTE: dict(outcome='not_applicable', reason='not_in_scope'),
                              CID_INPUT: dict(outcome='not_applicable', reason='input_not_supplied'),
                              CID_GRANT: dict(outcome='failed')})
        report = self.complete(executed=ex)
        self.assertEqual(sum(report['counts'].values()), 4)
        self.assertEqual(report['counts'].get('not_applicable', 0), 2)
        self.assertEqual(report['counts'].get('failed', 0), 1)
        self.assertEqual(report['counts'].get('passed', 0), 1)

    def test_checks_listed_in_manifest_order_regardless_of_result_order(self):
        manifest = make_manifest()
        ex = make_executed(manifest)
        for ordering in (ex[::-1], ex[1:] + ex[:1], [ex[2], ex[0], ex[3], ex[1]]):
            report = self.complete(executed=ordering)
            self.assertEqual([c['check_id'] for c in report['checks']],
                             [c['check_id'] for c in manifest['checks']])
        self.assertEqual([c['check_id'] for c in report['checks']], sorted(c['check_id'] for c in report['checks']))

    def test_not_applicable_reason_is_reported_and_other_reasons_are_null(self):
        ex = make_executed(**{CID_NOTE: dict(outcome='not_applicable', reason='not_in_scope'),
                              CID_GRANT: dict(outcome='failed')})
        report = self.complete(executed=ex)
        by_id = {c['check_id']: c for c in report['checks']}
        self.assertEqual(by_id[CID_NOTE], dict(check_id=CID_NOTE, outcome='not_applicable', reason='not_in_scope'))
        for cid in (CID_INPUT, CID_GRANT, CID_POLICY):
            self.assertIsNone(by_id[cid]['reason'])

    def test_report_contains_no_extra_results_and_is_canonicalizable(self):
        report = self.complete()
        self.assertEqual(len(report['checks']), 4)
        rr.jcs_dumps(report)

    def test_report_is_independent_of_the_executed_objects(self):
        ex = make_executed()
        report = self.complete(executed=ex)
        ex[0]['outcome'] = 'failed'
        self.assertEqual(report['checks'][0]['outcome'], 'passed')

    def test_a_report_is_never_returned_for_an_incomplete_run(self):
        for drop in range(4):
            ex = make_executed()
            del ex[drop]
            with self.assertRaises(mc.ManifestRefusal):
                mc.check_completeness(make_manifest(), make_record(), ex, floor_check_ids=FLOOR)


if __name__ == '__main__':
    unittest.main()
