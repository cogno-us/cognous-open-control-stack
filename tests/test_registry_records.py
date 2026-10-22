import copy
import json
import os
import tempfile
import unittest

from tools import registry_records as rr

FLOOR = {'check.mandatory.grant', 'check.mandatory.policy'}


def make_record(epoch=1, predecessor=None, **over):
    rules = [
        dict(rule_id='check.mandatory.grant', version=1, **{'class': 'refund'}, profile='bounded',
             status='required', applicability={'kind': 'always'}, evaluator_id='ev.grant',
             evaluator_version=1, failure_disposition='deny', missing_treatment='fail_closed',
             reason_code='R1', source_ref='src:grant'),
        dict(rule_id='check.mandatory.policy', version=1, **{'class': 'refund'}, profile='bounded',
             status='required', applicability={'kind': 'always'}, evaluator_id='ev.policy',
             evaluator_version=1, failure_disposition='hold', missing_treatment='fail_closed',
             reason_code='R2', source_ref='src:policy'),
        dict(rule_id='check.optional.note', version=1, **{'class': 'refund'}, profile='bounded',
             status='advisory', applicability={'kind': 'predicate', 'predicate': 'has_note',
                                               'source_ref': 'src:note'},
             evaluator_id='ev.note', evaluator_version=2, failure_disposition='require_evidence',
             missing_treatment='fail_closed', reason_code='R2', source_ref='src:note'),
    ]
    record = dict(profile=rr.PROFILE, schema_version=0, registry_id='reg-1',
                  canonical_profile=rr.CANONICAL_PROFILE, digest='sha256:' + '0' * 64, epoch=epoch,
                  predecessor=predecessor, rule_table=rules,
                  evaluators=[dict(evaluator_id='ev.grant', version=1, qualification_ref='q:1'),
                              dict(evaluator_id='ev.policy', version=1, qualification_ref='q:2'),
                              dict(evaluator_id='ev.note', version=2, qualification_ref='q:3')],
                  reason_map={'R1': 'grant missing', 'R2': 'policy hold'},
                  source_refs=['src:grant', 'src:policy', 'src:note'], issuer='hub')
    record.update(over)
    record['digest'] = rr.record_digest(record)
    return record


def redigest(record):
    record['digest'] = rr.record_digest(record)
    return record


class Canonical(unittest.TestCase):
    def test_keys_sorted_and_compact(self):
        self.assertEqual(rr.jcs_dumps({'b': 1, 'a': [True, None, 'x']}), '{"a":[true,null,"x"],"b":1}')

    def test_sort_is_by_utf16_code_unit(self):
        # U+1F600 is the surrogate pair D83D DE00 and sorts before U+FB33 in UTF-16
        self.assertEqual(rr.jcs_dumps({'דּ': 1, '\U0001f600': 2}), '{"\U0001f600":2,"דּ":1}')

    def test_string_escapes(self):
        self.assertEqual(rr.jcs_dumps('a"\\\n\x01\x7f'), '"a\\"\\\\\\n\\u0001\x7f"')

    def test_floats_bool_ints_and_bad_types_refused(self):
        for bad in (1.5, float('nan'), 2 ** 60, (1,), {1: 2}, b'x', {'a': object()}):
            with self.assertRaises(ValueError):
                rr.jcs_dumps(bad)

    def test_lone_surrogate_refused(self):
        with self.assertRaises(UnicodeEncodeError):
            rr.jcs_dumps('\ud800')

    def test_digest_independent_of_key_order(self):
        a = make_record()
        b = dict(reversed(list(a.items())))
        self.assertEqual(rr.record_digest(a), rr.record_digest(b))

    def test_strict_loader(self):
        for bad in ('{"a":1,"a":2}', '{"a":1.0}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(ValueError):
                rr.loads_strict(bad)


class Validation(unittest.TestCase):
    def ok(self, record, pin=None):
        return rr.validate_record(record, floor_mandatory_rule_ids=FLOOR, pin=pin)

    def refused(self, record, code, pin=None):
        with self.assertRaises(rr.RegistryRefusal) as ctx:
            self.ok(record, pin)
        self.assertEqual(ctx.exception.code, code)

    def test_valid_record(self):
        record = make_record()
        self.assertEqual(self.ok(record), record['digest'])

    def test_pin_match_and_mismatch(self):
        record = make_record()
        self.ok(record, pin=record['digest'])
        self.refused(record, 'pin_mismatch', pin='sha256:' + '1' * 64)

    def test_tamper_detected(self):
        record = make_record()
        record['rule_table'][2]['status'] = 'required'
        self.refused(record, 'digest_mismatch')

    def test_unknown_member_and_missing_member(self):
        record = make_record()
        record['extra'] = 1
        self.refused(record, 'schema_invalid')
        record = make_record()
        del record['issuer']
        self.refused(record, 'schema_invalid')
        record = make_record()
        record['rule_table'][0]['note'] = 'x'
        self.refused(redigest(record), 'schema_invalid')

    def test_unknown_canonical_profile(self):
        self.refused(make_record(canonical_profile='legacy-sorted-json'), 'unknown_canonical_profile')

    def test_types_in_typed_positions(self):
        self.refused(make_record(epoch=True), 'schema_invalid')
        self.refused(make_record(epoch=None), 'schema_invalid')
        self.refused(make_record(epoch=0), 'schema_invalid')
        record = make_record()
        record['rule_table'][0]['version'] = True
        self.refused(redigest(record), 'schema_invalid')
        record = make_record()
        record['rule_table'][0]['status'] = ['required']
        self.refused(redigest(record), 'schema_invalid')
        record = make_record()
        record['rule_table'][0]['applicability'] = None
        self.refused(redigest(record), 'schema_invalid')

    def test_missing_input_must_fail_closed(self):
        record = make_record()
        record['rule_table'][0]['missing_treatment'] = 'skip'
        self.refused(redigest(record), 'schema_invalid')

    def test_mandatory_rule_absent(self):
        record = make_record()
        del record['rule_table'][0]
        self.refused(redigest(record), 'mandatory_check_missing')

    def test_mandatory_rule_advisory_or_conditional(self):
        record = make_record()
        record['rule_table'][0]['status'] = 'advisory'
        self.refused(redigest(record), 'mandatory_check_not_required')
        record = make_record()
        record['rule_table'][0]['applicability'] = {'kind': 'predicate', 'predicate': 'p',
                                                    'source_ref': 'src:grant'}
        self.refused(redigest(record), 'mandatory_check_conditional')

    def test_floor_must_be_explicit(self):
        with self.assertRaises(TypeError):
            rr.validate_record(make_record())
        with self.assertRaises(rr.RegistryRefusal):
            rr.validate_record(make_record(), floor_mandatory_rule_ids=None)

    def test_duplicate_or_shadowed_rule(self):
        record = make_record()
        clone = copy.deepcopy(record['rule_table'][2])
        clone['version'] = 2
        record['rule_table'].append(clone)
        self.refused(redigest(record), 'duplicate_or_shadowed_rule')

    def test_same_rule_other_scope_is_not_shadowing(self):
        record = make_record()
        clone = copy.deepcopy(record['rule_table'][2])
        clone['profile'] = 'other'
        record['rule_table'].append(clone)
        self.ok(redigest(record))

    def test_unknown_unqualified_evaluator(self):
        record = make_record()
        record['rule_table'][2]['evaluator_version'] = 9
        self.refused(redigest(record), 'unknown_evaluator')
        record = make_record()
        record['evaluators'][0]['qualification_ref'] = ' '
        self.refused(redigest(record), 'unqualified_evaluator')

    def test_dangling_references(self):
        record = make_record()
        record['rule_table'][0]['reason_code'] = 'R9'
        self.refused(redigest(record), 'schema_invalid')
        record = make_record()
        record['rule_table'][0]['source_ref'] = 'src:none'
        self.refused(redigest(record), 'schema_invalid')

    def test_succession(self):
        first = make_record()
        rr.check_succession(first, None)
        second = make_record(epoch=2, predecessor=first['digest'])
        rr.check_succession(second, first)
        for rec, code in ((make_record(epoch=1, predecessor=first['digest']), 'epoch_not_increasing'),
                          (make_record(epoch=2, predecessor='sha256:' + '2' * 64), 'predecessor_mismatch'),
                          (make_record(epoch=2, predecessor=None), 'predecessor_mismatch')):
            with self.assertRaises(rr.RegistryRefusal) as ctx:
                rr.check_succession(rec, first)
            self.assertEqual(ctx.exception.code, code)
        with self.assertRaises(rr.RegistryRefusal):
            rr.check_succession(second, None)


class Store(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = os.path.join(self.tmp.name, 'store')

    def store(self, **kw):
        args = dict(max_records=3, max_record_bytes=65536, floor_mandatory_rule_ids=FLOOR)
        args.update(kw)
        return rr.RegistryStore(self.dir, **args)

    def refused(self, fn, code):
        with self.assertRaises(rr.RegistryRefusal) as ctx:
            fn()
        self.assertEqual(ctx.exception.code, code)

    def test_publish_load_latest_history(self):
        store = self.store()
        first = make_record()
        second = make_record(epoch=2, predecessor=first['digest'])
        store.publish(first)
        store.publish(second)
        self.assertEqual(store.latest(), second)
        self.assertEqual(store.load(first['digest']), first)
        self.assertEqual(store.list_digests(), [first['digest'][7:], second['digest'][7:]])
        self.assertIsNone(store.load('sha256:' + '9' * 64))

    def test_explicit_bounds_required(self):
        with self.assertRaises(TypeError):
            rr.RegistryStore(self.dir, floor_mandatory_rule_ids=FLOOR)
        with self.assertRaises(ValueError):
            self.store(max_records=0)

    def test_pin_enforced_on_publish(self):
        self.refused(lambda: self.store().publish(make_record(), pin='sha256:' + '3' * 64), 'pin_mismatch')
        self.assertEqual(self.store().list_digests(), [])

    def test_downgrade_fork_and_republish_refused(self):
        store = self.store()
        first = make_record()
        store.publish(first)
        self.refused(lambda: store.publish(first), 'epoch_not_increasing')
        fork = make_record(epoch=2, predecessor='sha256:' + '4' * 64)
        self.refused(lambda: store.publish(fork), 'predecessor_mismatch')

    def test_published_file_is_read_only_and_republish_after_removal(self):
        store = self.store()
        first = make_record()
        store.publish(first)
        path = os.path.join(self.dir, store._name(first))
        self.assertEqual(os.stat(path).st_mode & 0o222, 0)
        os.chmod(path, 0o644)
        os.remove(path)
        # same name now absent; a different valid record with the same epoch cannot slip in
        store.publish(first)

    def test_count_and_size_bounds(self):
        store = self.store(max_records=1)
        first = make_record()
        store.publish(first)
        self.refused(lambda: store.publish(make_record(epoch=2, predecessor=first['digest'])),
                     'store_bound_exceeded')
        self.refused(lambda: self.store(max_record_bytes=10, max_records=5).publish(make_record(epoch=1)),
                     'store_bound_exceeded')

    def test_floor_enforced_on_publish(self):
        record = make_record()
        record['rule_table'][0]['status'] = 'advisory'
        self.refused(lambda: self.store().publish(redigest(record)), 'mandatory_check_not_required')

    def test_tampered_file_detected_on_load(self):
        store = self.store()
        first = make_record()
        store.publish(first)
        path = os.path.join(self.dir, store._name(first))
        os.chmod(path, 0o644)
        tampered = copy.deepcopy(first)
        tampered['issuer'] = 'attacker'
        with open(path, 'w') as handle:
            json.dump(tampered, handle)
        self.refused(store.latest, 'digest_mismatch')

    def test_renamed_file_detected(self):
        store = self.store()
        first = make_record()
        store.publish(first)
        os.rename(os.path.join(self.dir, store._name(first)), os.path.join(self.dir, '000000000007-' + first['digest'][7:] + '.json'))
        self.refused(store.latest, 'store_integrity')

    def test_unexpected_file_and_symlink_refused(self):
        store = self.store()
        with open(os.path.join(self.dir, 'x.json'), 'w') as handle:
            handle.write('{}')
        self.refused(store.list_digests, 'store_integrity')
        os.remove(os.path.join(self.dir, 'x.json'))
        first = make_record()
        store.publish(first)
        target = os.path.join(self.dir, store._name(first))
        link = os.path.join(self.dir, '000000000002-' + 'a' * 64 + '.json')
        os.symlink(target, link)
        self.refused(store.latest, 'store_integrity')

    def test_non_strict_json_in_store_refused(self):
        store = self.store()
        name = '000000000001-' + 'b' * 64 + '.json'
        with open(os.path.join(self.dir, name), 'w') as handle:
            handle.write('{"a":1,"a":2}')
        self.refused(store.latest, 'store_integrity')


if __name__ == '__main__':
    unittest.main()
