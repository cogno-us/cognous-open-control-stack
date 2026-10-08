import copy
import unittest
from reference_profiles.provenance_groups import AXES, CONTRACT, summarize


def receipt(name, snapshot):
    return {'receipt_id': name, 'dependencies': {a: [snapshot] if a == 'data_snapshot' else ['shared'] for a in AXES}}


def packet(receipts):
    return {'contract': CONTRACT, 'claim_ref': 'claim-1', 'scenario_ref': 'stale-cache',
            'failure_axes': ['data_snapshot'], 'basis_ref': 'review-1', 'receipts': receipts}


class ProvenanceGroupsTests(unittest.TestCase):
    def test_many_receipts_do_not_inflate_groups(self):
        result = summarize(packet([receipt(str(i), 'cache') for i in range(100)] +
                                  [receipt('a', 'source-a'), receipt('b', 'source-b')]))
        self.assertEqual(result['declared_group_count'], 3)
        self.assertEqual(sorted(len(g['receipt_ids']) for g in result['groups']), [1, 1, 100])
        self.assertEqual(result['independence'], 'not_established')
        self.assertFalse(result['authorizes_action'])

    def test_shared_provider_collapses_different_snapshots(self):
        p = packet([receipt('a', 'one'), receipt('b', 'two')])
        p['failure_axes'].append('provider')
        self.assertEqual(summarize(p)['declared_group_count'], 1)

    def test_transitive_overlap_is_one_group(self):
        p = packet([receipt('a', 'one'), receipt('b', 'two'), receipt('c', 'three')])
        p['receipts'][1]['dependencies']['data_snapshot'] = ['one', 'three']
        self.assertEqual(summarize(p)['declared_group_count'], 1)

    def test_unknown_relevant_lineage_not_counted(self):
        p = packet([receipt('a', 'one')])
        p['receipts'][0]['dependencies']['data_snapshot'] = None
        r = summarize(p)
        self.assertEqual(r['declared_group_count'], 0)
        self.assertEqual(r['unestablished_receipts'], ['a'])

    def test_unknown_unselected_axis_still_no_independence(self):
        p = packet([receipt('a', 'one')])
        p['receipts'][0]['dependencies']['provider'] = None
        self.assertEqual(summarize(p)['independence'], 'not_established')

    def test_duplicate_receipt_rejected(self):
        with self.assertRaises(ValueError):
            summarize(packet([receipt('a', 'one'), receipt('a', 'two')]))

    def test_missing_axes_rejected(self):
        p = packet([receipt('a', 'one')])
        del p['receipts'][0]['dependencies']['tool']
        with self.assertRaises(ValueError):
            summarize(p)

    def test_invalid_declarations_rejected(self):
        for axes in ([], ['provider', 'provider'], ['seed'], 'provider', [None]):
            with self.subTest(axes=axes):
                p = packet([])
                p['failure_axes'] = axes
                with self.assertRaises(ValueError):
                    summarize(p)

    def test_invalid_dependencies_rejected(self):
        for value in ([], '', [''], ['x', 'x'], [3], {}):
            with self.subTest(value=value):
                p = packet([receipt('a', 'one')])
                p['receipts'][0]['dependencies']['provider'] = value
                with self.assertRaises(ValueError):
                    summarize(p)

    def test_input_preserved_and_order_invariant(self):
        p = packet([receipt('z', 'one'), receipt('a', 'two')])
        before = copy.deepcopy(p)
        r = summarize(p)
        self.assertEqual(p, before)
        p['receipts'].reverse()
        self.assertEqual(r, summarize(p))

    def test_unknown_fields_and_blank_basis_rejected(self):
        for field, value in [('witness_count', 3), ('basis_ref', ' '), ('contract', 'old')]:
            p = packet([])
            p[field] = value
            with self.assertRaises(ValueError):
                summarize(p)

    def test_empty_population_is_not_evidence(self):
        r = summarize(packet([]))
        self.assertEqual(r['receipt_count'], 0)
        self.assertEqual(r['declared_group_count'], 0)
        self.assertEqual(r['independence'], 'not_established')


if __name__ == '__main__':
    unittest.main()
