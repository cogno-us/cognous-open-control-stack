from copy import deepcopy
import unittest
from tools.lifecycle_inventory import CONTRACT, reconcile


def fixture():
    scope = {'tenant': 'tenant-a', 'environment': 'test'}
    return {'contract': CONTRACT, **scope, 'window_start': 80, 'window_end': 100,
            'required_connectors': ['deployment', 'identity'],
            'connectors': [{'id': x, 'status': 'complete', 'observed_at': 100}
                           for x in ('deployment', 'identity')],
            'agents': [{**scope, 'agent_id': 'a', 'owner': 'operator', 'backup_owner': 'backup',
                        'state': 'active', 'accepted_release': 'sha-1',
                        'bindings': [{'instance_id': 'replica-1', 'workload_id': 'principal-1',
                                      'valid_from': 80, 'valid_until': 120}]}],
            'instances': [{**scope, 'agent_id': 'a', 'instance_id': 'replica-1',
                           'workload_id': 'principal-1', 'release': 'sha-1',
                           'connector': 'deployment', 'observed_at': 100}]}


class InventoryTests(unittest.TestCase):
    def run_packet(self, p):
        return reconcile(p, now=100, max_age=10)

    def kinds(self, p):
        return {f['kind'] for f in self.run_packet(p)['findings']}

    def test_good_supplied_population_does_not_authorize(self):
        p = fixture(); original = deepcopy(p)
        result = self.run_packet(p)
        self.assertEqual(result['review_status'], 'no_supplied_discrepancies')
        for key in ('authorizing', 'deployment_qualified', 'discovery_verified'):
            self.assertIs(result[key], False)
        self.assertEqual(p, original)

    def test_unregistered_replica(self):
        p = fixture(); p['instances'][0]['instance_id'] = 'extra'
        self.assertEqual(self.kinds(p), {'unregistered_replica', 'registration_not_observed'})

    def test_expiry_boundary(self):
        p = fixture(); p['agents'][0]['bindings'][0]['valid_until'] = 100
        self.assertIn('binding_not_current', self.kinds(p))

    def test_missing_owner(self):
        p = fixture(); p['agents'][0]['owner'] = None
        self.assertIn('missing_owner', self.kinds(p))

    def test_stale_catalog_is_not_proven_absent(self):
        p = fixture(); p['instances'] = []
        self.assertEqual(self.kinds(p), {'registration_not_observed'})

    def test_non_active_states_hold(self):
        for state in ('discovered', 'approved', 'suspended', 'retiring', 'retired'):
            with self.subTest(state=state):
                p = fixture(); p['agents'][0]['state'] = state
                self.assertIn('lifecycle_hold', self.kinds(p))
                self.assertEqual(self.run_packet(p)['review_status'], 'hold')

    def test_partial_unavailable_missing_and_stale_discovery(self):
        for mode in ('partial', 'unavailable', 'missing', 'stale'):
            with self.subTest(mode=mode):
                p = fixture()
                if mode == 'missing': p['connectors'].pop()
                elif mode == 'stale': p['connectors'][1]['observed_at'] = 80
                else: p['connectors'][1]['status'] = mode
                r = self.run_packet(p)
                self.assertFalse(r['declared_coverage_current'])
                self.assertEqual(r['incomplete_connectors'], ['identity'])
                self.assertEqual(r['review_status'], 'hold')

    def test_empty_partial_population_stays_partial(self):
        p = fixture(); p['agents'] = []; p['instances'] = []; p['connectors'] = []
        self.assertFalse(self.run_packet(p)['declared_coverage_current'])

    def test_duplicate_binding_identity(self):
        p = fixture(); second = deepcopy(p['agents'][0]); second['agent_id'] = 'b'
        p['agents'].append(second)
        self.assertIn('duplicated_instance_binding', self.kinds(p))

    def test_workload_and_release_mismatch(self):
        p = fixture(); p['instances'][0].update(workload_id='other', release='sha-2')
        self.assertEqual(self.kinds(p), {'workload_identity_mismatch', 'release_mismatch'})

    def test_stale_observation(self):
        p = fixture(); p['instances'][0]['observed_at'] = 80
        self.assertIn('stale_observation', self.kinds(p))

    def test_cross_tenant_rejected(self):
        for key in ('agents', 'instances'):
            p = fixture(); p[key][0]['tenant'] = 'other'
            with self.assertRaises(ValueError): self.run_packet(p)

    def test_duplicate_observation_rejected(self):
        p = fixture(); p['instances'].append(deepcopy(p['instances'][0]))
        with self.assertRaises(ValueError): self.run_packet(p)

    def test_invalid_time_and_contract_rejected(self):
        for key, value in [('window_end', 101), ('window_start', True),
                           ('contract', 'legacy'), ('required_connectors', [])]:
            p = fixture(); p[key] = value
            with self.assertRaises(ValueError): self.run_packet(p)

    def test_unknown_agent(self):
        p = fixture(); p['agents'] = []
        self.assertEqual(self.kinds(p), {'unregistered_agent'})

    def test_unavailable_connector_cannot_supply_records(self):
        p = fixture(); p['connectors'][0]['status'] = 'unavailable'
        with self.assertRaises(ValueError): self.run_packet(p)


if __name__ == '__main__':
    unittest.main()
