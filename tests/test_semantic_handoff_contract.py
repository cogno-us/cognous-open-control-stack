import copy
from datetime import datetime, timezone
import unittest

from tools.semantic_handoff_contract import PROFILE, commitment, check_acceptance


class SemanticHandoffTests(unittest.TestCase):
    def setUp(self):
        self.proposal = dict(profile=PROFILE, handoff_id='h1', revision=1,
            sender='agent:a', receiver='agent:b', tenant='tenant:demo', task='t1', parent='root',
            operation='synthetic-refund', goal='return declared amount', dictionary_ref='demo-refund/1',
            context_generation='context/7', read_scope=['order:42'], write_scope=['refund:42'],
            preconditions=['order exists'], completion_criteria=['one refund record'],
            required_evidence=['destination receipt'], restrictions=['no notification'],
            deadline='2030-01-02T00:00:00Z', terms=[dict(name='amount', value=10, unit='USD',
            namespace='demo-orders', time_basis='transaction UTC', uncertainty='exact')])
        self.current = commitment(self.proposal)
        self.response = dict(kind='acceptance', sender='agent:b', receiver='agent:a',
            proposal_commitment=self.current, interpretation=copy.deepcopy(self.proposal),
            mapping=dict(version='identity/1', source_dictionary='demo-refund/1',
                target_dictionary='demo-refund/1', normalization='identity', lost=[], unresolved=[]))
        self.now = datetime(2030, 1, 1, tzinfo=timezone.utc)

    def check(self):
        return check_acceptance(self.proposal, self.response, current_commitment=self.current,
            current_context_generation='context/7', now=self.now)

    def test_exact_agreement_does_not_authorize_or_observe(self):
        result = self.check()
        self.assertEqual(result['state'], 'accepted')
        self.assertFalse(result['authorizing'])
        self.assertFalse(result['observed_effect'])

    def test_unit_namespace_time_and_uncertainty_mismatches(self):
        for field, value in [('unit', 'EUR'), ('namespace', 'other-orders'),
                             ('time_basis', 'local wall time'), ('uncertainty', 'estimated')]:
            with self.subTest(field=field):
                self.response['interpretation'] = copy.deepcopy(self.proposal)
                self.response['interpretation']['terms'][0][field] = value
                self.assertEqual(self.check()['state'], 'pending')

    def test_dropped_restriction_and_changed_scope(self):
        for field in ('restrictions', 'write_scope', 'required_evidence'):
            with self.subTest(field=field):
                self.response['interpretation'] = copy.deepcopy(self.proposal)
                self.response['interpretation'][field] = ['different']
                self.assertNotEqual(self.check()['state'], 'accepted')

    def test_missing_or_ambiguous_deadline_blocks(self):
        for value in ('01/02/2030', '2030-01-02T00:00:00', None):
            self.proposal['deadline'] = value
            self.assertEqual(self.check()['state'], 'blocked')

    def test_changed_context_blocks(self):
        self.proposal['context_generation'] = 'context/8'
        self.current = commitment(self.proposal)
        self.assertEqual(self.check()['reason'], 'superseded_contract_or_context')

    def test_superseded_commitment_blocks(self):
        self.current = '0' * 64
        self.assertEqual(self.check()['state'], 'blocked')

    def test_stale_acceptance_after_revision(self):
        self.proposal['revision'] = 2
        self.current = commitment(self.proposal)
        self.assertEqual(self.check()['reason'], 'stale_response')

    def test_clarification_duplicates_do_not_accept(self):
        self.response['kind'] = 'clarification'
        self.assertEqual(self.check()['state'], 'pending')
        self.assertEqual(self.check()['state'], 'pending')

    def test_ack_progress_and_completion_do_not_accept(self):
        for kind in ('transport_ack', 'progress', 'completion_assertion'):
            self.response['kind'] = kind
            self.assertEqual(self.check()['state'], 'pending')

    def test_rejection_is_distinct(self):
        self.response['kind'] = 'rejection'
        self.assertEqual(self.check()['state'], 'rejected')

    def test_lost_or_unresolved_meaning_stays_pending(self):
        for key in ('lost', 'unresolved'):
            self.response['mapping'][key] = ['recipient unclear']
            self.assertEqual(self.check()['state'], 'pending')
            self.response['mapping'][key] = []

    def test_no_implicit_normalization(self):
        self.response['mapping']['normalization'] = 'infer currency'
        self.assertEqual(self.check()['state'], 'blocked')

    def test_dictionary_and_party_mismatch(self):
        self.response['mapping']['target_dictionary'] = 'other/1'
        self.assertEqual(self.check()['reason'], 'dictionary_mismatch')
        self.response['sender'] = 'agent:c'
        self.assertEqual(self.check()['reason'], 'party_mismatch')

    def test_exact_deadline_and_naive_clock(self):
        self.now = datetime(2030, 1, 2, tzinfo=timezone.utc)
        self.assertEqual(self.check()['state'], 'deferred')
        self.now = datetime(2030, 1, 1)
        self.assertEqual(self.check()['state'], 'blocked')

    def test_malformed_quantities_and_unknown_fields(self):
        for value in (True, float('nan'), float('inf'), {}, ''):
            self.proposal['terms'][0]['value'] = value
            self.assertEqual(self.check()['state'], 'blocked')
        self.proposal['terms'][0]['value'] = 10
        self.proposal['undeclared'] = 'not silently ignored'
        self.assertEqual(self.check()['state'], 'blocked')

    def test_duplicate_terms_and_invalid_revision(self):
        self.proposal['terms'].append(copy.deepcopy(self.proposal['terms'][0]))
        self.assertEqual(self.check()['state'], 'blocked')
        self.proposal['terms'].pop()
        self.proposal['revision'] = True
        self.assertEqual(self.check()['state'], 'blocked')

    def test_metadata_commitment_is_deterministic(self):
        self.assertEqual(self.current, commitment(dict(reversed(list(self.proposal.items())))))
        self.proposal['terms'][0]['unit'] = 'EUR'
        self.assertNotEqual(self.current, commitment(self.proposal))

    def test_missing_response_or_contract_is_blocked(self):
        self.response = None
        self.assertEqual(self.check()['state'], 'blocked')
        self.proposal = None
        self.assertEqual(self.check()['state'], 'blocked')


if __name__ == '__main__':
    unittest.main()
