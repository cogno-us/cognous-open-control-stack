"""End-to-end structured-state gates on the inherited synthetic effect path."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import test_federated_governance as fixtures
from reference_profiles.assurance_runtime import digest, ZERO
from reference_profiles.operational_state import OperationalStateRuntime


class OperationalTests(unittest.TestCase):
    # Reuse setup helpers without rediscovering the entire inherited test suite.
    for _name in ('call','ok','deny','get','effects','fact','relation','mandate','consent','perceive','episode','ready','checkpoint'):
        locals()[_name] = getattr(fixtures.GovernanceTests, _name)

    def setUp(self):
        with patch.object(fixtures, 'FederatedGovernanceRuntime', OperationalStateRuntime):
            fixtures.GovernanceTests.setUp(self)
        self.contract()
        self.sample('left'); self.sample('right')

    def contract(self, **updates):
        a=dict(run='run',version=1,principal='agent',action='sqlite-insert',resource='public',context='synthetic',decisions=['allow'],required_obligations=['review'],completed_obligations=['review'],spatial=dict(crs='synthetic-grid',expected_crs='synthetic-grid',resolution=1,max_resolution=2,uncertainty=1,max_uncertainty=2,observed_at=100,expires_at=450,evidence_digest=ZERO),population=dict(cohort='cohort',groups=['left','right'],minimum_count=10,max_gap_ppm=100000,max_age=200))
        a.update(updates);return self.ok('ops','execution_contract',**a)

    def sample(self, group, **updates):
        a=dict(id='sample-'+str(self.serial),cohort='cohort',group=group,observed_at=100,total=100,positive=50,expected_ppm=500000,evidence_digest=ZERO);a.update(updates)
        return self.ok('eval','population_sample',**a)

    def block(self):
        self.ok('review','blocker',id='block',run='run',prerequisite='approval-missing',resolver='second',fallback='wait',evidence_digest=digest({'approved':True}))

    def handoff(self, state=None, **updates):
        with self.runtime.connection() as c: actual=self.runtime.blocker_state(c,'run')
        a=dict(id='handoff',run='run',predecessor=ZERO,state=actual if state is None else state,summary_digest=ZERO);a.update(updates)
        return self.call('agent','handoff',**a)

    def execute_denied(self, reason):
        self.deny('agent','execute',reason,proposal='proposal');self.assertEqual(self.effects(),0)
        self.assertEqual(self.runtime.journal()['events'][-1]['body']['reason'],reason)

    def test_permitted_and_duplicate_effect(self):
        self.ready();self.ok('agent','execute',proposal='proposal');self.assertEqual(self.effects(),1)
        self.block();self.ok('agent','execute',proposal='proposal');self.assertEqual(self.effects(),1)

    def test_blocker_after_review_blocks_effect(self):
        self.ready();self.block();self.execute_denied('UNRESOLVED_BLOCKER')

    def test_missing_handoff_state_rejected(self):
        self.block();self.assertEqual(self.handoff(state={}).get('reason'),'HANDOFF_STATE_LOSS')

    def test_softened_handoff_state_rejected(self):
        self.block();state={'block':self.get('blocker','block')};state['block']['status']='caveat'
        self.assertEqual(self.handoff(state=state)['reason'],'HANDOFF_STATE_LOSS')

    def test_preserved_handoff_does_not_resolve(self):
        self.ready();self.block();self.assertEqual(self.handoff()['status'],'accepted');self.execute_denied('UNRESOLVED_BLOCKER')

    def test_handoff_chain_rejects_stale_predecessor(self):
        self.handoff();self.assertEqual(self.handoff(id='second')['reason'],'HANDOFF_PREDECESSOR')

    def test_only_designated_resolver_with_exact_evidence(self):
        self.block();self.deny('review','resolve_blocker','BLOCKER_RESOLVER',blocker='block',evidence={'approved':True})
        self.deny('second','resolve_blocker','BLOCKER_EVIDENCE',blocker='block',evidence={'approved':False})
        self.ok('second','resolve_blocker',blocker='block',evidence={'approved':True});self.ready();self.ok('agent','execute',proposal='proposal')

    def test_resolution_does_not_restore_old_binding(self):
        self.ready();self.block();self.ok('second','resolve_blocker',blocker='block',evidence={'approved':True});self.execute_denied('GOVERNANCE_CHANGED')

    def test_policy_deny_overrides_allow(self):
        self.ready();self.contract(version=2,decisions=['allow','deny']);self.execute_denied('POLICY_DENY')

    def test_approval_is_not_allow(self):
        self.ready();self.contract(version=2,decisions=['approve']);self.execute_denied('POLICY_AWAIT_APPROVAL')

    def test_pending_obligation_blocks(self):
        self.ready();self.contract(version=2,completed_obligations=[]);self.execute_denied('POLICY_OBLIGATION_PENDING')

    def test_contract_revision_fences_review(self):
        self.ready();self.contract(version=2);self.execute_denied('GOVERNANCE_CHANGED')

    def test_contract_cannot_rollback(self):
        self.deny('ops','execution_contract','CONTRACT_VERSION',**{k:v for k,v in self.get('execution-contract','run').items() if k!='actor'})

    def test_spatial_crs_mismatch(self):
        self.ready();s=self.get('execution-contract','run')['spatial'];s['crs']='other';self.contract(version=2,spatial=s);self.execute_denied('SPATIAL_UNSUPPORTED')

    def test_spatial_uncertainty_exceeded(self):
        self.ready();s=self.get('execution-contract','run')['spatial'];s['uncertainty']=3;self.contract(version=2,spatial=s);self.execute_denied('SPATIAL_UNSUPPORTED')

    def test_spatial_resolution_exceeded(self):
        self.ready();s=self.get('execution-contract','run')['spatial'];s['resolution']=3;self.contract(version=2,spatial=s);self.execute_denied('SPATIAL_UNSUPPORTED')

    def test_spatial_expiry(self):
        self.ready();s=self.get('execution-contract','run')['spatial'];s['expires_at']=101;self.contract(version=2,spatial=s);self.now=101;self.execute_denied('SPATIAL_TIME')

    def test_population_alarm_blocks_effect(self):
        self.ready();self.sample('left',positive=90);self.execute_denied('POPULATION_ALARM')

    def test_benign_sample_cannot_erase_live_alarm(self):
        self.ready();self.sample('left',positive=90);self.sample('left');self.execute_denied('POPULATION_ALARM')

    def test_population_missing_group_is_unknown(self):
        self.ready();p=self.get('execution-contract','run')['population'];p['groups'].append('missing');self.contract(version=2,population=p);self.execute_denied('POPULATION_INDETERMINATE')

    def test_population_small_sample_is_unknown(self):
        self.ready();self.sample('left',total=2,positive=1);self.execute_denied('POPULATION_INDETERMINATE')

    def test_population_stale_sample_is_unknown(self):
        self.ready();self.now=300;self.execute_denied('POPULATION_INDETERMINATE')

    def test_population_new_evidence_invalidates_review(self):
        self.ready();self.sample('left');self.execute_denied('GOVERNANCE_CHANGED')

    def test_agent_cannot_assert_monitor_or_contract(self):
        self.deny('agent','population_sample','ROLE_NOT_PERMITTED');self.deny('agent','execution_contract','ROLE_NOT_PERMITTED')

    def test_feedback_never_grants_authority(self):
        self.ok('agent','opportunity',id='opp',run='run',mode='act',benefit=100,interruption=2,privacy=1,misunderstanding=1,evidence_digest=ZERO)
        before=self.get('grant','grant');r=self.ok('review','opportunity_feedback',id='feedback',opportunity='opp',accepted=True,burden=2,evidence_digest=ZERO)
        self.assertFalse(r['permission_changed']);self.assertEqual(before,self.get('grant','grant'));self.assertEqual(self.effects(),0)

    def test_silence_is_recorded(self):
        self.ok('agent','opportunity',id='silent',run='run',mode='silent',benefit=0,interruption=0,privacy=0,misunderstanding=0,evidence_digest=ZERO)
        self.assertEqual(self.get('opportunity','silent')['mode'],'silent');self.assertEqual(self.effects(),0)

    def test_lineage_record_is_not_identity_proof(self):
        r=self.ok('agent','lineage_claim',run='run',item='item',checkpoint=100,content_digest=digest('synthetic text'));self.assertFalse(r['identity_established'])

    def test_lineage_pre_acquisition_rejected(self):
        self.deny('agent','lineage_claim','LINEAGE_TIME',run='run',item='item',checkpoint=99,content_digest=digest('synthetic text'))

    def test_lineage_false_memory_rejected(self):
        self.deny('agent','lineage_claim','LINEAGE_CONTENT',run='run',item='item',checkpoint=100,content_digest=digest('invented memory'))

    def test_lineage_revoked_consent_rejected(self):
        self.consent(enabled=False);self.deny('agent','lineage_claim','CONSENT_UNAVAILABLE',run='run',item='item',checkpoint=100,content_digest=digest('synthetic text'))

    def test_blocker_survives_reopen(self):
        self.ready();self.block();self.runtime=OperationalStateRuntime(self.path,keys=self.keys,clock=lambda:self.now,observe_environment=lambda:deepcopy(self.manifest));self.execute_denied('UNRESOLVED_BLOCKER')


class ReportingTests(unittest.TestCase):
    def report(self):
        from reference_profiles.operational_state import REPORT_FIELDS, ASSURANCE_AXES
        return {'disclosures':{f:'not-applicable: deterministic fixture' for f in REPORT_FIELDS},'claims':{f:{'status':'not-established','evidence_digest':None} for f in ASSURANCE_AXES}}

    def test_functional_success_does_not_establish_security(self):
        from reference_profiles.operational_state import assess_report
        r=self.report();r['claims']['functional']={'status':'supported','evidence_digest':ZERO}
        result=assess_report(r);self.assertEqual(result['claims']['security']['status'],'not-established');self.assertFalse(result['reference_release_authorized'])

    def test_missing_reporting_dimension_rejected(self):
        from reference_profiles.operational_state import assess_report
        r=self.report();del r['disclosures']['budget_human_input']
        with self.assertRaises(ValueError):assess_report(r)

    def test_unsupported_claim_cannot_be_marked_supported_without_evidence(self):
        from reference_profiles.operational_state import assess_report
        r=self.report();r['claims']['security']['status']='supported'
        with self.assertRaises(ValueError):assess_report(r)
