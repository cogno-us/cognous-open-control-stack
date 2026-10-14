"""All nine addenda through an actual isolated local effect path; no production claims."""
from copy import deepcopy
import hashlib
import json
import multiprocessing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from reference_profiles.assurance_runtime import AssuranceRuntime, LocalWitness, Denied, ZERO, digest, sign_request


def execute_worker(path, keys, manifest, request, output):
    runtime=AssuranceRuntime(path,keys=keys,clock=lambda:100,observe_environment=lambda:manifest)
    output.put(runtime.apply(request))


class IntegratedAssuranceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'runtime.db'; self.now=100; self.serial=0
        roles={'ops':['operator'],'data':['steward'],'review':['reviewer'],'challenge':['reviewer'],
               'eval':['evaluator'],'build':['builder'],'witness':['custodian'],'incident':['incident'],
               'judge':['adjudicator'],'judge2':['adjudicator'],'agent':['agent'],'child':['agent'],'sibling':['agent']}
        self.keys={(a,v):hashlib.sha256(('SYNTHETIC-TEST-KEY-'+a+str(v)).encode()).digest() for a in roles for v in (1,2)}
        self.manifest={'adapter':'sqlite-local/1','network':False,'subprocess':False,'shared_cache':False,'sinks':{'public':['public'],'private':['public','secret']}}
        self.runtime=AssuranceRuntime.create(self.path,stream='synthetic-stream',principals={a:{'roles':r,'version':1} for a,r in roles.items()},keys=self.keys,clock=lambda:self.now,observe_environment=lambda:deepcopy(self.manifest))
        self.witness=LocalWitness.create(Path(self.temp.name)/'witness.db',stream='synthetic-stream')
        self.ok('ops','environment',id='env',manifest=deepcopy(self.manifest),expires_at=1000,max_event_lag=1000,max_checkpoint_age=1000)
        self.new_run('root','agent')
        self.ok('data','ingest',id='public-item',content='Synthetic public response',labels=['public'],parents=[],expires_at=900)
        self.ok('ops','reviewer',id='review',available=True,capacity=8,expires_at=900)
        self.ok('ops','reviewer',id='challenge',available=True,capacity=8,expires_at=900)
        self.grant('root-grant','root')
        self.checkpoint()

    # unittest.TestCase.run is reserved; use helper alias below instead.
    def new_run(self,identity,agent,parent=None,**updates):
        args=dict(id=identity,agent=agent,environment='env',cohort='group',parent=parent,purpose='support',max_steps=20,stall_seconds=500,
                  provenance={'model_ref':'synthetic-model','configuration_digest':ZERO,'assurance':'declared'})
        args.update(updates); return self.ok('ops','run',**args)

    def request(self,actor,operation,args,version=1):
        self.serial+=1
        return sign_request(self.keys[(actor,version)],stream='synthetic-stream',actor=actor,key_version=version,nonce='nonce-'+str(self.serial),expires_at=self.now+1000,operation=operation,arguments=args)

    def call(self,actor,operation,**args): return self.runtime.apply(self.request(actor,operation,args))

    def ok(self,actor,operation,**args):
        result=self.call(actor,operation,**args); self.assertEqual(result['status'],'accepted',result)
        return result['result']

    def denied(self,actor,operation,reason=None,**args):
        result=self.call(actor,operation,**args); self.assertEqual(result['status'],'denied',result)
        if reason: self.assertEqual(result['reason'],reason,result)
        return result

    def grant(self,identity,run,**updates):
        args=dict(id=identity,run=run,sinks=['public','private'],labels=['public','secret'],budget=5,expires_at=800,depth=3,corrects=None)
        args.update(updates); return self.ok('ops','grant',**args)

    def get(self,kind,identity):
        with self.runtime.connection() as conn: return self.runtime.get(conn,kind,identity)

    def proposal(self,**updates):
        args=dict(effect='effect-1',run='root',grant='root-grant',item='public-item',route='public',declassification=None,harness_digest=digest(self.get('meta','harness')))
        args.update(updates); return args

    def queue(self,identity='proposal-1',actor='agent',proposal=None,**updates):
        args=dict(id=identity,proposal=proposal or self.proposal(),reviewer='review',expires_at=700); args.update(updates)
        return self.ok(actor,'queue',**args)

    def approve(self,identity='proposal-1'):
        p=self.get('proposal',identity)
        return self.ok('review','review',proposal=identity,binding_digest=p['binding_digest'],disposition='approve')

    def ready(self,identity='proposal-1',actor='agent',proposal=None):
        self.queue(identity,actor,proposal); self.approve(identity); self.checkpoint()

    def checkpoint(self):
        cp=self.witness.receive(self.runtime.journal(),now=self.now)
        return self.ok('witness','checkpoint',**cp)

    def effects(self):
        with self.runtime.connection() as conn: return [dict(r) for r in conn.execute('SELECT * FROM effects')]

    def test_all_controls_permit_one_exact_local_effect(self):
        self.ready(); result=self.ok('agent','execute',proposal='proposal-1')
        self.assertEqual(result['observed_state'],'applied'); self.assertEqual(len(self.effects()),1)
        evidence=json.loads(self.effects()[0]['evidence'])
        self.assertEqual(evidence['grants'],[{'id':'root-grant','revision':1}])
        self.assertEqual(evidence['binding']['payload_digest'],hashlib.sha256(b'Synthetic public response').hexdigest())
        self.assertFalse(self.call('agent','observe',effect='effect-1',run='root')['authorizing'])

    def test_unregistered_route_and_arbitrary_effect_surface_are_blocked(self):
        self.denied('agent','queue','UNKNOWN_ROUTE',id='p',proposal=self.proposal(route='shell'),reviewer='review',expires_at=700)
        self.denied('agent','shell','ROLE_NOT_PERMITTED',command='irrelevant')
        manifest=dict(self.manifest,network=True)
        self.denied('ops','environment','UNSUPPORTED_SURFACE',id='new',manifest=manifest,expires_at=900,max_event_lag=5,max_checkpoint_age=10)
        self.assertEqual(self.effects(),[])

    def test_environment_drift_and_expired_lease_block_effect(self):
        self.ready(); self.manifest['network']=True
        self.denied('agent','execute','ENVIRONMENT_MISMATCH',proposal='proposal-1')
        self.manifest['network']=False
        with self.runtime.connection() as c:
            e=self.get('environment','env'); e['expires_at']=100; self.runtime.put(c,'environment','env',e)
        self.denied('agent','execute','LEASE_EXPIRED',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_allowed_public_sink_does_not_allow_secret_payload(self):
        self.ok('data','ingest',id='secret',content='SYNTHETIC-CANARY',labels=['secret'],parents=[],expires_at=850)
        self.denied('agent','queue','MISSING_DECLASSIFICATION',id='p',proposal=self.proposal(item='secret'),reviewer='review',expires_at=700)
        self.assertEqual(self.effects(),[])
        self.assertNotIn('SYNTHETIC-CANARY',json.dumps(self.runtime.journal()))

    def test_explicit_exact_declassification_and_scope(self):
        self.ok('data','ingest',id='secret',content='SYNTHETIC-CANARY',labels=['secret'],parents=[],expires_at=850)
        self.ok('data','declassify',id='d',item='secret',sink='public',payload_digest=self.get('item','secret')['content_digest'],expires_at=700)
        self.ready(proposal=self.proposal(item='secret',declassification='d')); self.ok('agent','execute',proposal='proposal-1')
        self.assertEqual(self.effects()[0]['payload'],'SYNTHETIC-CANARY')
        self.denied('agent','queue','DECLASSIFICATION_MISMATCH',id='p2',proposal=self.proposal(effect='e2',item='public-item',declassification='d'),reviewer='review',expires_at=700)

    def test_untrusted_labels_and_derived_label_drop_are_rejected(self):
        self.denied('agent','ingest','ROLE_NOT_PERMITTED',id='x',content='x',labels=['public'],parents=[],expires_at=800)
        self.ok('data','ingest',id='secret',content='SYNTHETIC-CANARY',labels=['secret'],parents=[],expires_at=850)
        self.denied('data','ingest','PROVENANCE_WEAKENED',id='summary',content='summary',labels=['public'],parents=['secret'],expires_at=800)
        self.ok('data','ingest',id='summary',content='summary',labels=['secret'],parents=['secret'],expires_at=800)
        self.denied('agent','queue','MISSING_DECLASSIFICATION',id='p',proposal=self.proposal(item='summary'),reviewer='review',expires_at=700)

    def test_payload_cannot_be_replaced_after_review(self):
        self.ready()
        self.denied('data','ingest','DUPLICATE_ID',id='public-item',content='substituted',labels=['public'],parents=[],expires_at=900)
        self.ok('agent','execute',proposal='proposal-1')
        self.assertEqual(self.effects()[0]['payload'],'Synthetic public response')

    def test_declassification_expiry_after_approval_blocks(self):
        self.ok('data','ingest',id='secret',content='secret',labels=['secret'],parents=[],expires_at=850)
        self.ok('data','declassify',id='d',item='secret',sink='public',payload_digest=self.get('item','secret')['content_digest'],expires_at=101)
        self.ready(proposal=self.proposal(item='secret',declassification='d')); self.now=101
        self.denied('agent','execute','DECLASSIFICATION_MISMATCH',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def child_grant(self,identity='child-grant',run='child-run',agent='child'):
        self.new_run(run,agent,parent='root')
        return self.ok('agent','delegate',id=identity,parent='root-grant',run=run,sinks=['public'],labels=['public'],budget=1,expires_at=600,depth=1)

    def test_attenuated_child_uses_parent_budget(self):
        self.child_grant(); self.ready(actor='child',proposal=self.proposal(run='child-run',grant='child-grant'))
        self.ok('child','execute',proposal='proposal-1')
        self.assertEqual(self.get('grant','root-grant')['used'],1); self.assertEqual(self.get('grant','child-grant')['used'],1)

    def test_delegation_cannot_expand_depth_expiry_scope_or_purpose(self):
        self.new_run('child-run','child',parent='root')
        base=dict(id='g',parent='root-grant',run='child-run',sinks=['public'],labels=['public'],budget=1,expires_at=600,depth=1)
        for update in ({'sinks':['unknown']},{'labels':['new-label']},{'budget':6},{'depth':3},{'expires_at':801}):
            with self.subTest(update=update): self.denied('agent','delegate',**dict(base,**update))
        self.new_run('other-purpose','child',parent='root',purpose='different')
        self.denied('agent','delegate','DELEGATION_SCOPE_MISMATCH',**dict(base,run='other-purpose'))

    def test_parent_revocation_refuses_child_and_names_revision(self):
        self.child_grant(); self.ready(actor='child',proposal=self.proposal(run='child-run',grant='child-grant'))
        self.ok('ops','revoke',grant='root-grant'); self.denied('child','execute','GRANT_REVOKED',proposal='proposal-1')
        event=self.runtime.journal()['events'][-1]['body']
        self.assertIn({'id':'root-grant','revision':2,'status':'revoked'},event['grant_chain']); self.assertEqual(self.effects(),[])

    def test_disabled_parent_identity_invalidates_child_authority(self):
        self.child_grant(); self.ready(actor='child',proposal=self.proposal(run='child-run',grant='child-grant'))
        self.ok('ops','rotate',principal='agent',version=2,enabled=False)
        self.denied('child','execute','AGENT_UNAVAILABLE',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_two_processes_cannot_spend_last_ancestor_budget_twice(self):
        # Configure the fixture's root budget before any delegation/effects.
        with self.runtime.connection() as c:
            g=self.get('grant','root-grant'); g['budget']=1; self.runtime.put(c,'grant','root-grant',g)
        self.child_grant(); self.child_grant('sibling-grant','sibling-run','sibling')
        self.ready('p1','child',self.proposal(effect='e1',run='child-run',grant='child-grant'))
        self.ready('p2','sibling',self.proposal(effect='e2',run='sibling-run',grant='sibling-grant'))
        ctx=multiprocessing.get_context('fork'); output=ctx.Queue()
        processes=[ctx.Process(target=execute_worker,args=(self.path,self.keys,self.manifest,self.request(actor,'execute',{'proposal':p}),output)) for actor,p in [('child','p1'),('sibling','p2')]]
        for process in processes: process.start()
        for process in processes: process.join(10); self.assertEqual(process.exitcode,0)
        results=[output.get(timeout=2) for _ in processes]
        self.assertEqual(sorted(r['status'] for r in results),['accepted','denied']); self.assertEqual(len(self.effects()),1)
        self.assertEqual(self.get('grant','root-grant')['used'],1)

    def test_revoke_before_effect_and_effect_before_revoke_have_distinct_results(self):
        self.ready(); self.ok('ops','revoke',grant='root-grant'); self.denied('agent','execute','GRANT_REVOKED',proposal='proposal-1')
        self.grant('fresh','root'); self.ready('p2',proposal=self.proposal(effect='e2',grant='fresh'))
        self.ok('agent','execute',proposal='p2'); self.ok('ops','revoke',grant='fresh')
        self.assertEqual(self.ok('agent','observe',effect='e2',run='root')['observed_state'],'applied')
        self.assertEqual(len(self.effects()),1)

    def test_slow_observer_cannot_extend_expired_grant(self):
        self.ready()
        calls=[0]
        def delayed():
            calls[0]+=1
            if calls[0]==3: self.now=801
            return deepcopy(self.manifest)
        self.runtime.observe_environment=delayed
        self.denied('agent','execute',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_signature_payload_tampering_audience_and_replay(self):
        request=self.request('agent','progress',{'run':'root'})
        forged=deepcopy(request); forged['body']['arguments']['run']='different'
        self.assertEqual(self.runtime.apply(forged)['reason'],'BAD_SIGNATURE')
        self.assertEqual(self.runtime.apply(request)['status'],'accepted')
        self.assertEqual(self.runtime.apply(request)['reason'],'REPLAYED_REQUEST')
        wrong=sign_request(self.keys[('agent',1)],stream='wrong',actor='agent',key_version=1,nonce='audience',expires_at=500,operation='progress',arguments={'run':'root'})
        self.assertEqual(self.runtime.apply(wrong)['reason'],'AUDIENCE_MISMATCH')

    def test_forged_signed_execution_cannot_create_effect(self):
        self.ready(); request=self.request('agent','execute',{'proposal':'proposal-1'})
        request['body']['nonce']='forged-nonce'
        result=self.runtime.apply(request)
        self.assertEqual(self.effects(),[])
        self.assertEqual(result['reason'],'BAD_SIGNATURE')

    def test_key_rotation_persists_and_old_key_cannot_act(self):
        self.ok('ops','rotate',principal='agent',version=2,enabled=True)
        self.runtime=AssuranceRuntime(self.path,keys=self.keys,clock=lambda:self.now,observe_environment=lambda:deepcopy(self.manifest))
        self.denied('agent','progress','KEY_RETIRED',run='root')
        self.assertEqual(self.runtime.apply(self.request('agent','progress',{'run':'root'},version=2))['status'],'accepted')
        self.denied('ops','rotate','KEY_VERSION_MUST_ADVANCE',principal='agent',version=1,enabled=True)

    def test_same_model_instances_cannot_exchange_authority(self):
        self.new_run('child-run','child',parent='root')
        self.denied('child','queue','INSTANCE_MISMATCH',id='p',proposal=self.proposal(),reviewer='review',expires_at=700)
        self.denied('ops','run','MODEL_ATTESTATION_NOT_ESTABLISHED',id='forged',agent='child',environment='env',cohort='group',parent=None,purpose='support',max_steps=2,stall_seconds=10,provenance={'model_ref':'synthetic-model','configuration_digest':ZERO,'assurance':'verified'})

    def test_missing_or_stale_custody_blocks_effect(self):
        self.ready()
        with self.runtime.connection() as c: c.execute("DELETE FROM objects WHERE kind='checkpoint'")
        self.denied('agent','execute','MISSING_CHECKPOINT',proposal='proposal-1'); self.assertEqual(self.effects(),[])
        with self.runtime.connection() as c:
            env=self.get('environment','env'); env['max_checkpoint_age']=1; self.runtime.put(c,'environment','env',env)
        self.ready('new-proposal',proposal=self.proposal(effect='new-effect'))
        self.now=102; self.denied('agent','execute','CUSTODY_TIME_LAG',proposal='new-proposal')

    def test_event_lag_gate_resumes_only_after_checkpoint(self):
        with self.runtime.connection() as c:
            env=self.get('environment','env'); env['max_event_lag']=2; self.runtime.put(c,'environment','env',env)
        self.ready()
        self.ok('agent','progress',run='root')
        self.denied('agent','execute','CUSTODY_EVENT_LAG',proposal='proposal-1')
        self.checkpoint(); self.ok('agent','execute',proposal='proposal-1'); self.assertEqual(len(self.effects()),1)

    def test_witness_rejects_gap_fork_and_truncation_across_reopen(self):
        journal=self.runtime.journal(); self.witness.receive(journal,now=self.now)
        self.witness=LocalWitness(self.witness.path,stream='synthetic-stream')
        for events in (journal['events'][:-1],journal['events'][1:],list(reversed(journal['events']))):
            with self.assertRaises(Denied): self.witness.receive(dict(journal,events=events),now=self.now)
        forged=deepcopy(journal); forged['events'][0]['body']['actor']='other'
        with self.assertRaises(Denied): self.witness.receive(forged,now=self.now)

    def test_checkpoint_rollback_and_retired_custodian_block(self):
        self.ready(); old={'stream':'synthetic-stream','count':0,'head':ZERO,'observed_at':100}
        self.denied('witness','checkpoint','CHECKPOINT_ROLLBACK',**old)
        self.ok('ops','rotate',principal='witness',version=2,enabled=True)
        self.denied('agent','execute','CUSTODIAN_KEY_RETIRED',proposal='proposal-1')

    def test_review_capacity_unavailable_and_deadline(self):
        self.ok('ops','reviewer',id='review',available=True,capacity=1,expires_at=900)
        self.queue()
        self.denied('agent','queue','REVIEW_CAPACITY_EXHAUSTED',id='p2',proposal=self.proposal(effect='e2'),reviewer='review',expires_at=700)
        self.approve(); self.ok('ops','reviewer',id='review',available=False,capacity=1,expires_at=900)
        self.denied('agent','execute','REVIEWER_UNAVAILABLE',proposal='proposal-1')
        self.ok('ops','reviewer',id='review',available=True,capacity=1,expires_at=900); self.now=700
        self.denied('agent','execute','APPROVAL_UNAVAILABLE',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_same_principal_cannot_review_own_request_even_with_both_roles(self):
        with self.runtime.connection() as c:
            principal=self.get('principal','agent'); principal['roles'].append('reviewer'); self.runtime.put(c,'principal','agent',principal)
        self.ok('ops','reviewer',id='agent',available=True,capacity=1,expires_at=800)
        self.denied('agent','queue','SELF_APPROVAL_FORBIDDEN',id='p',proposal=self.proposal(),reviewer='agent',expires_at=700)
        self.assertEqual(self.effects(),[])

    def test_reviewer_key_rotation_invalidates_prior_review(self):
        self.ready(); self.ok('ops','rotate',principal='review',version=2,enabled=True)
        self.ok('ops','reviewer',id='review',available=True,capacity=8,expires_at=900)
        self.denied('agent','execute','REVIEWER_KEY_CHANGED',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_changed_environment_policy_invalidates_prior_approval(self):
        self.ready()
        self.ok('ops','environment',id='env',manifest=deepcopy(self.manifest),expires_at=1000,max_event_lag=500,max_checkpoint_age=1000)
        self.denied('agent','execute','PROPOSAL_CHANGED',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_exact_review_binding_and_role_separation(self):
        self.queue()
        self.denied('agent','review','ROLE_NOT_PERMITTED',proposal='proposal-1',binding_digest=self.get('proposal','proposal-1')['binding_digest'],disposition='approve')
        self.denied('review','review','PROPOSAL_CHANGED',proposal='proposal-1',binding_digest=ZERO,disposition='approve')
        self.approve(); self.assertEqual(self.get('proposal','proposal-1')['state'],'approved')

    def test_challenge_blocks_approval_and_late_challenge_blocks_execution(self):
        self.queue(); self.ok('challenge','challenge',id='c1',proposal='proposal-1',reason_digest=ZERO)
        self.denied('review','review','UNRESOLVED_CHALLENGE',proposal='proposal-1',binding_digest=self.get('proposal','proposal-1')['binding_digest'],disposition='approve')
        self.ok('review','resolve_challenge',challenge='c1',disposition='override',reason_digest='a'*64)
        self.approve(); self.ok('challenge','challenge',id='c2',proposal='proposal-1',reason_digest=ZERO)
        self.denied('agent','execute','UNRESOLVED_CHALLENGE',proposal='proposal-1')
        self.ok('review','resolve_challenge',challenge='c2',disposition='accept',reason_digest='b'*64)
        self.denied('agent','execute','APPROVAL_UNAVAILABLE',proposal='proposal-1')

    def stop(self): return self.ok('incident','stop',run='root',incident_digest=ZERO,detected_at=self.now)

    def test_stop_covers_children_blocks_new_runs_and_preserves_prior_effect(self):
        self.child_grant(); self.ready(); self.ok('agent','execute',proposal='proposal-1')
        stopped=self.stop(); self.assertEqual(stopped['runs'],['child-run','root'])
        self.assertEqual(stopped['state'],'quiescent-local'); self.assertEqual(len(self.effects()),1)
        args=dict(id='new',agent='child',environment='env',cohort='group',parent=None,purpose='support',max_steps=1,stall_seconds=10,provenance={'model_ref':'m','configuration_digest':ZERO,'assurance':'declared'})
        self.denied('ops','run','COHORT_STOPPED',**args)
        self.assertEqual(self.get('grant','child-grant')['status'],'revoked')

    def test_stopped_run_cannot_receive_fresh_grant(self):
        self.stop()
        self.denied('ops','grant','RUN_STOPPED',id='fresh',run='root',sinks=['public'],labels=['public'],budget=1,expires_at=700,depth=0,corrects=None)
        self.assertNotIn('fresh',self._objects('grant'))

    def test_stop_holds_writer_boundary_before_waiting_execution(self):
        self.ready(); ctx=multiprocessing.get_context('fork')
        entered,release=ctx.Event(),ctx.Event(); output=ctx.Queue()
        request=self.request('incident','stop',{'run':'root','incident_digest':ZERO,'detected_at':100})
        def stop_at_boundary():
            runtime=AssuranceRuntime(self.path,keys=self.keys,clock=lambda:100,observe_environment=lambda:self.manifest)
            original=runtime.event
            def pause(conn,body):
                entered.set()
                if not release.wait(5): raise RuntimeError('test barrier timeout')
                original(conn,body)
            runtime.event=pause; output.put(runtime.apply(request))
        stopper=ctx.Process(target=stop_at_boundary); stopper.start(); self.assertTrue(entered.wait(5))
        # Probe the lock instead of relying on a sleep as the ordering oracle.
        with sqlite3.connect(self.path,timeout=0) as c:
            with self.assertRaises(sqlite3.OperationalError): c.execute('BEGIN IMMEDIATE')
        executor=ctx.Process(target=execute_worker,args=(self.path,self.keys,self.manifest,self.request('agent','execute',{'proposal':'proposal-1'}),output))
        executor.start(); release.set()
        for process in (stopper,executor): process.join(10); self.assertEqual(process.exitcode,0)
        results=[output.get(timeout=2) for _ in range(2)]
        self.assertEqual(sorted(r['status'] for r in results),['accepted','denied']); self.assertEqual(self.effects(),[])

    def test_stop_remains_available_during_observer_outage(self):
        self.ready()
        def unavailable(): raise OSError('synthetic offline')
        self.runtime.observe_environment=unavailable
        self.denied('agent','execute','ENVIRONMENT_UNAVAILABLE',proposal='proposal-1')
        self.assertEqual(self.stop()['state'],'quiescent-local'); self.assertEqual(self.effects(),[])

    def test_restart_requires_review_and_does_not_restore_grants(self):
        incident=self.stop()['incident']
        self.denied('ops','restart','MISSING_RESTART',incident=incident,remediation_digest=ZERO)
        self.ok('review','restart_review',incident=incident,remediation_digest=ZERO,expires_at=300)
        self.ok('ops','restart',incident=incident,remediation_digest=ZERO)
        self.assertEqual(self.get('grant','root-grant')['status'],'revoked')
        self.denied('agent','queue','GRANT_REVOKED',id='p',proposal=self.proposal(),reviewer='review',expires_at=700)
        self.grant('fresh','root'); self.ready(proposal=self.proposal(grant='fresh')); self.ok('agent','execute',proposal='proposal-1')

    def test_old_restart_review_cannot_override_newer_same_time_stop(self):
        first=self.stop()['incident']; self.ok('review','restart_review',incident=first,remediation_digest=ZERO,expires_at=300)
        second=self.stop()['incident']; self.assertNotEqual(first,second)
        self.denied('ops','restart','NEWER_INCIDENT',incident=first,remediation_digest=ZERO)

    def test_stall_and_step_budget_produce_safe_refusal(self):
        self.ready(); self.now=600
        self.denied('agent','execute','RUN_STALLED',proposal='proposal-1')
        self.now=100
        with self.runtime.connection() as c:
            run=self.get('run','root'); run['steps']=run['max_steps']; self.runtime.put(c,'run','root',run)
        self.denied('agent','execute','STEP_BUDGET_EXHAUSTED',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_lost_ack_reopen_observes_and_duplicate_does_not_reapply(self):
        self.ready(); self.ok('agent','execute',proposal='proposal-1')  # caller discards acknowledgment
        self.runtime=AssuranceRuntime(self.path,keys=self.keys,clock=lambda:self.now,observe_environment=lambda:deepcopy(self.manifest))
        self.assertEqual(self.ok('agent','observe',effect='effect-1',run='root')['observed_state'],'applied')
        self.assertTrue(self.ok('agent','execute',proposal='proposal-1')['duplicate']); self.assertEqual(len(self.effects()),1)
        self.assertEqual(self.get('grant','root-grant')['used'],1)

    def test_crash_before_commit_rolls_back_effect_and_budget(self):
        self.ready(); request=self.request('agent','execute',{'proposal':'proposal-1'})
        ctx=multiprocessing.get_context('fork')
        def crash():
            import os
            runtime=AssuranceRuntime(self.path,keys=self.keys,clock=lambda:100,observe_environment=lambda:self.manifest)
            runtime.event=lambda *a:os._exit(71)
            runtime.apply(request)
        process=ctx.Process(target=crash); process.start(); process.join(10); self.assertEqual(process.exitcode,71)
        self.assertEqual(self.effects(),[]); self.assertEqual(self.get('grant','root-grant')['used'],0)
        self.assertEqual(self.runtime.apply(request)['status'],'accepted'); self.assertEqual(len(self.effects()),1)

    def test_crash_after_commit_is_observed_without_reexecution(self):
        self.ready(); request=self.request('agent','execute',{'proposal':'proposal-1'})
        ctx=multiprocessing.get_context('fork')
        def crash():
            import os
            runtime=AssuranceRuntime(self.path,keys=self.keys,clock=lambda:100,observe_environment=lambda:self.manifest)
            result=runtime.apply(request)
            os._exit(72 if result['status']=='accepted' else 73)
        process=ctx.Process(target=crash); process.start(); process.join(10); self.assertEqual(process.exitcode,72)
        self.assertEqual(self.ok('agent','observe',effect='effect-1',run='root')['observed_state'],'applied')
        self.assertTrue(self.ok('agent','execute',proposal='proposal-1')['duplicate']); self.assertEqual(len(self.effects()),1)

    def change(self,identity='change',oracle='oracle',routes=None):
        cases=[{'route':'public','expected_sink':'public'},{'route':'private','expected_sink':'private'},{'route':'new-route','expected_sink':'private'},{'route':'second-route','expected_sink':'private'}]
        if oracle not in self._objects('oracle'):
            self.ok('eval','oracle',id=oracle,cases=cases,max_evaluations=2,min_improvement=1,max_regressions=0)
            self.ok('ops','select_oracle',oracle=oracle)
        harness={'instruction_digest':'a'*64,'routes':routes or {'public':'public','private':'private','new-route':'private','second-route':'private'}}
        self.ok('build','propose_change',id=identity,base_digest=digest(self.get('meta','harness')),harness=harness,oracle=oracle,cause_digest=ZERO)
        return harness

    def _objects(self,kind):
        with self.runtime.connection() as c: return self.runtime.population(c,kind)

    def test_independent_current_oracle_change_admission_and_activation(self):
        harness=self.change(); result=self.ok('eval','evaluate_change',change='change'); self.assertEqual(result['state'],'evaluated')
        self.ok('review','admit_change',change='change',harness_digest=digest(harness)); self.ok('ops','activate_change',change='change')
        self.assertEqual(self.get('meta','harness'),harness)
        self.ready(proposal=self.proposal(route='new-route')); self.ok('agent','execute',proposal='proposal-1')
        self.assertEqual(json.loads(self.effects()[0]['evidence'])['binding']['sink'],'private')

    def test_unsafe_regression_and_evaluation_budget_are_enforced(self):
        self.change(routes={'public':'private','private':'private','new-route':'private','second-route':'private'})
        result=self.ok('eval','evaluate_change',change='change'); self.assertEqual(result['state'],'rejected'); self.assertEqual(result['regressions'],1)
        self.denied('review','admit_change','CHANGE_NOT_INDEPENDENTLY_EVALUATED',change='change',harness_digest=digest(self.get('change','change')['harness']))
        self.change('c2'); self.ok('eval','evaluate_change',change='c2')
        self.change('c3'); self.denied('eval','evaluate_change','EVALUATION_BUDGET_EXHAUSTED',change='c3')

    def test_proposer_cannot_modify_evaluator_or_security_surface(self):
        self.denied('build','oracle','ROLE_NOT_PERMITTED',id='x',cases=[],max_evaluations=1,min_improvement=1,max_regressions=0)
        self.change()
        bad=dict(self.get('change','change')['harness'],policy='weaken')
        self.denied('build','propose_change','INVALID_FIELDS',id='x',base_digest=digest(self.get('meta','harness')),harness=bad,oracle='oracle',cause_digest=ZERO)
        self.denied('build','evaluate_change','ROLE_NOT_PERMITTED',change='change')

    def test_new_oracle_invalidates_old_admission_and_change_invalidates_approval(self):
        self.ready(); harness=self.change(); self.ok('eval','evaluate_change',change='change'); self.ok('review','admit_change',change='change',harness_digest=digest(harness))
        self.ok('eval','oracle',id='new',cases=[{'route':'public','expected_sink':'public'}],max_evaluations=1,min_improvement=1,max_regressions=0)
        self.ok('ops','select_oracle',oracle='new'); self.denied('ops','activate_change','ORACLE_NOT_CURRENT',change='change')
        self.ok('ops','select_oracle',oracle='oracle'); self.ok('ops','activate_change',change='change')
        self.denied('agent','execute','APPROVAL_UNAVAILABLE',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_rollback_uses_current_oracle_and_never_revives_grants_or_approvals(self):
        original=self.get('meta','harness'); self.ready()
        harness=self.change(); self.ok('eval','evaluate_change',change='change'); self.ok('review','admit_change',change='change',harness_digest=digest(harness)); self.ok('ops','activate_change',change='change')
        self.ok('ops','revoke',grant='root-grant')
        cases=[{'route':'public','expected_sink':'public'},{'route':'private','expected_sink':'private'},{'route':'new-route','expected_sink':None},{'route':'second-route','expected_sink':None}]
        self.ok('eval','oracle',id='restoration-rules',cases=cases,max_evaluations=1,min_improvement=1,max_regressions=0); self.ok('ops','select_oracle',oracle='restoration-rules')
        self.ok('build','propose_change',id='restore',base_digest=digest(harness),harness=original,oracle='restoration-rules',cause_digest=ZERO)
        self.ok('eval','evaluate_change',change='restore'); self.ok('review','admit_change',change='restore',harness_digest=digest(original)); self.ok('ops','activate_change',change='restore')
        self.assertEqual(self.get('meta','harness'),original); self.assertEqual(self.get('grant','root-grant')['status'],'revoked')
        self.denied('agent','execute','APPROVAL_UNAVAILABLE',proposal='proposal-1'); self.assertEqual(self.effects(),[])

    def test_new_routes_without_oracle_coverage_cannot_be_admitted(self):
        self.change(routes={'public':'public','private':'private','new-route':'private','second-route':'private','unmeasured':'public'})
        self.denied('eval','evaluate_change','UNEVALUATED_ROUTE',change='change')

    def test_unresolved_challenge_debt_blocks_change_admission(self):
        self.queue(); self.ok('challenge','challenge',id='c',proposal='proposal-1',reason_digest=ZERO)
        harness=self.change(); self.ok('eval','evaluate_change',change='change')
        self.denied('review','admit_change','UNRESOLVED_REVIEW_DEBT',change='change',harness_digest=digest(harness))

    def obligation(self,identity,predicate,expected,effect='effect-1'):
        self.ok('ops','obligation',id=identity,effect=effect,predicate=predicate,expected=expected,due_at=150)

    def test_recourse_distinguishes_compliant_violated_unevaluable_and_evidence_failure(self):
        self.obligation('present','effect_present',True); self.obligation('subjective','subjective','useful')
        self.obligation('missing','exact_payload',ZERO,effect='missing'); self.obligation('evidence','evidence_available',True,effect='missing')
        early=self.ok('judge','recourse',id='early',obligation='present'); self.assertEqual(early['reason'],'OBLIGATION_NOT_DUE')
        self.ready(); self.ok('agent','execute',proposal='proposal-1'); self.now=150
        compliant=self.ok('judge','recourse',id='p',obligation='present'); self.assertEqual(compliant['outcome'],'compliant')
        subjective=self.ok('judge','recourse',id='s',obligation='subjective'); self.assertEqual(subjective['outcome'],'unevaluable')
        missing=self.ok('judge','recourse',id='m',obligation='missing'); self.assertEqual(missing['outcome'],'unevaluable')
        evidence=self.ok('judge','recourse',id='e',obligation='evidence'); self.assertEqual(evidence['outcome'],'violated'); self.assertEqual(evidence['reason'],'EVIDENCE_AVAILABILITY_ONLY')
        self.assertTrue(all(x['authorizing'] is False for x in (compliant,subjective,missing,evidence)))

    def test_remedy_packet_cannot_create_effect_or_restore_authority(self):
        self.obligation('o','effect_present',True); self.now=150
        self.ok('judge','recourse',id='packet',obligation='o'); original=self.get('recourse','packet')
        self.ok('judge','adjudicate',packet='packet',disposition='remedy-approved',reason_digest=ZERO)
        self.assertEqual(self.get('recourse','packet'),original); self.assertEqual(self.effects(),[])
        self.ok('ops','revoke',grant='root-grant')
        self.denied('agent','queue','GRANT_REVOKED',id='p',proposal=self.proposal(),reviewer='review',expires_at=700)
        self.grant('correction','root',corrects='packet'); self.ready(proposal=self.proposal(grant='correction'))
        self.ok('agent','execute',proposal='proposal-1'); self.assertEqual(len(self.effects()),1)
        self.denied('judge','adjudicate','ALREADY_ADJUDICATED',packet='packet',disposition='remedy-approved',reason_digest=ZERO)

    def test_appeal_preserves_history_and_blocks_existing_corrective_grant(self):
        self.obligation('o','effect_present',True); self.now=150
        self.ok('judge','recourse',id='packet',obligation='o'); self.ok('judge','adjudicate',packet='packet',disposition='remedy-approved',reason_digest=ZERO)
        original=self.get('adjudication','packet'); self.grant('corrective','root',corrects='packet')
        self.ready(proposal=self.proposal(grant='corrective'))
        self.ok('ops','appeal',id='appeal',packet='packet',reason_digest=ZERO)
        self.denied('agent','execute','CORRECTION_APPEALED',proposal='proposal-1')
        self.denied('judge','decide_appeal','APPEAL_SEPARATION_REQUIRED',appeal='appeal',disposition='no-remedy',reason_digest=ZERO)
        self.ok('judge2','decide_appeal',appeal='appeal',disposition='no-remedy',reason_digest=ZERO)
        self.denied('agent','execute','CORRECTION_NOT_ADJUDICATED',proposal='proposal-1')
        self.assertEqual(self.get('adjudication','packet'),original); self.assertEqual(self.effects(),[])

    def test_invalid_signed_arguments_are_recorded_without_effects(self):
        self.denied('data','ingest','INVALID_ARGUMENTS',id='bad',content='text',labels=['public'],parents=[{}],expires_at=700)
        event=self.runtime.journal()['events'][-1]['body']
        self.assertEqual(event['reason'],'INVALID_ARGUMENTS'); self.assertTrue(event['authenticated']); self.assertEqual(self.effects(),[])

    def test_missing_runtime_storage_does_not_bootstrap(self):
        self.path.unlink()
        with self.assertRaises(sqlite3.OperationalError): self.call('agent','progress',run='root')
        self.assertFalse(self.path.exists())


if __name__=='__main__': unittest.main()
