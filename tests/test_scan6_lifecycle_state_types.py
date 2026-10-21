"""Scan 6 T2-2: unhashable or non-string lifecycle state is a typed refusal, not a TypeError."""
import unittest

from tests.test_lifecycle_inventory import fixture
from tools.lifecycle_inventory import reconcile


class StateTypeTests(unittest.TestCase):
    def test_non_string_state_is_refused_with_valueerror(self):
        for state in (['active'], {'a': 1}, [], {'active'}, 1, None, b'active', ('active',)):
            p = fixture()
            p['agents'][0]['state'] = state
            with self.subTest(state=state), self.assertRaisesRegex(ValueError, 'lifecycle state'):
                reconcile(p, now=100, max_age=10)

    def test_valid_state_still_reconciles(self):
        self.assertEqual(reconcile(fixture(), now=100, max_age=10)['review_status'], 'no_supplied_discrepancies')


if __name__ == '__main__':
    unittest.main()
