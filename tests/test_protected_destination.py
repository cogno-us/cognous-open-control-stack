from copy import deepcopy
import json
import os
import multiprocessing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from reference_profiles.assurance_runtime import digest
from reference_profiles.trust_evidence import signed
from reference_profiles.protected_destination import ProtectedDestination


def restored_client(path,config,request,queue):
    runtime=ProtectedDestination(path,clock=lambda:100,**config)
    queue.put(runtime.apply(request))


def crashing_client(path,config,request):
    class CrashBeforeCommit(ProtectedDestination):
        def event(self,c,body):
            super().event(c,body)
            os._exit(73)
    CrashBeforeCommit(path,clock=lambda:100,**config).apply(request)


class DestinationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'destination.db';self.now=100;self.serial=0
        self.keys={p:Ed25519PrivateKey.generate() for p in ('admin','broker','verifier','agent')}
        self.registry={p:{'public_key':k.public_key().public_bytes_raw().hex(),'not_before':0,'expires_at':1000,'revoked_at':None} for p,k in self.keys.items()}
        self.config=dict(registry=self.registry,admin='admin',custodian='broker',verifier='verifier')
        self.runtime=ProtectedDestination.create(self.path,authority_backup_set='authority',destination_backup_set='destination',clock=lambda:self.now,**self.config)
        self.ok('fence',scope='tenant',generation=7);self.view();self.provision()

    def request(self,operation,args,actor=None):
        self.serial+=1;identity='cmd-'+str(self.serial);actor=actor or ('broker' if operation=='execute' else 'admin')
        if operation=='execute' and args.get('verifier_status')=='AUTO':
            d=digest({k:v for k,v in args.items() if k not in ('verifier_status','issuer_claims')})
            args=dict(args,verifier_status=signed(self.keys['verifier'],'verifier','destination-status',{'at':self.now,'expires_at':self.now+1,'command':identity,'request_digest':d,'generation':args['generation'],'active':True}))
        body={'id':identity,'operation':operation,'at':self.now,'arguments':args}
        if operation!='execute':body['sequence']=self.serial
        return signed(self.keys[actor],actor,'destination-command',body)

    def call(self,operation,**args):return self.runtime.apply(self.request(operation,args))
    def ok(self,operation,**args):
        r=self.call(operation,**args);self.assertEqual(r['status'],'accepted',r);return r['result']
    def deny(self,operation,reason,**args):
        r=self.call(operation,**args);self.assertEqual(r.get('reason'),reason,r);self.assertEqual(self.count(),0);return r
    def count(self):
        with self.runtime.connection() as c:return c.execute('SELECT count(*) FROM effects').fetchone()[0]
    def get(self,kind,key):
        with self.runtime.connection() as c:return self.runtime.get(c,kind,key)
    def view(self,**updates):
        a=dict(principal='agent',credential_version='v1',dependency_version='d1',grants=['read','write']);a.update(updates);return self.ok('destination_grants',**a)
    def provision(self,**updates):
        a=dict(id='grant',scope='tenant',generation=7,principal='agent',policy='policy1',target='sink',credential_version='v1',dependency_version='d1',modes={},max_effects=1,expires_at=200);a.update(updates);return self.ok('provision',**a)
    def args(self,**updates):
        a=dict(grant='grant',effect='effect',generation=7,policy='policy1',target='sink',payload='synthetic',verifier_status='AUTO',issuer_claims={'scope':'read-write'});a.update(updates);return a

    def assert_correlated_refusal(self, request, expected_command, reason):
        with self.runtime.connection() as c:
            before=c.execute('SELECT kind,id,body FROM objects ORDER BY kind,id').fetchall()
        result=self.runtime.apply(request)
        self.assertEqual(result['status'],'denied')
        self.assertEqual(result['reason'],reason)
        self.assertEqual(self.count(),0)
        self.runtime=ProtectedDestination(self.path,clock=lambda:self.now,**self.config)
        with self.runtime.connection() as c:
            self.assertEqual(before,c.execute('SELECT kind,id,body FROM objects ORDER BY kind,id').fetchall())
            event=json.loads(c.execute('SELECT body FROM events ORDER BY seq DESC LIMIT 1').fetchone()[0])
        self.assertEqual(event['command'],'unknown')
        self.assertEqual(event['claimed_command'],expected_command)
        self.assertIs(event['command_authenticated'],False)
        self.assertEqual(event['request_digest'],digest(request))
        self.assertEqual(event['status'],'denied')
        self.assertEqual(event['reason'],reason)
        self.assertEqual(event['at'],self.now)

    def test_extra_body_field_retains_untrusted_correlation(self):
        request=self.request('execute',self.args())
        body=dict(request['body'],extra='synthetic')
        request=signed(self.keys['broker'],'broker','destination-command',body)
        self.assert_correlated_refusal(request,body['id'],'INVALID_FIELDS')

    def test_invalid_or_missing_identifier_uses_digest_correlation(self):
        for value in [None, '', ' padded ', 'x'*201, 123, True, [], {}]:
            with self.subTest(identifier=value):
                request=self.request('execute',self.args());body=dict(request['body'],id=value)
                request=signed(self.keys['broker'],'broker','destination-command',body)
                self.assert_correlated_refusal(request,'unknown','INVALID_LABEL')
        request=self.request('execute',self.args());body=dict(request['body']);del body['id']
        request=signed(self.keys['broker'],'broker','destination-command',body)
        self.assert_correlated_refusal(request,'unknown','INVALID_FIELDS')

    def test_forged_identifier_does_not_consume_command_or_authorize(self):
        valid=self.request('execute',self.args());forged=dict(valid,signature='00'*64)
        self.assert_correlated_refusal(forged,valid['body']['id'],'SIGNATURE_INVALID')
        self.assertEqual(self.runtime.apply(valid)['status'],'accepted')
        with self.runtime.connection() as c:
            event=json.loads(c.execute('SELECT body FROM events ORDER BY seq DESC LIMIT 1').fetchone()[0])
        self.assertIs(event['command_authenticated'],True)
        self.assertEqual(self.count(),1)

    def test_non_object_body_is_durably_refused(self):
        for body in [None, [], 'synthetic']:
            with self.subTest(body=body):
                request=signed(self.keys['broker'],'broker','destination-command',body)
                self.assert_correlated_refusal(request,'unknown','INVALID_FIELDS')

    def test_restore_resurrects_revoked_epoch_other_process_refused(self):
        stale=self.request('execute',self.args());snapshot=Path(self.temp.name)/'authority-backup.json';snapshot.write_text(json.dumps(stale))
        self.ok('fence',scope='tenant',generation=8)
        ctx=multiprocessing.get_context('spawn');q=ctx.Queue();p=ctx.Process(target=restored_client,args=(str(self.path),self.config,json.loads(snapshot.read_text()),q));p.start();p.join(10)
        self.assertEqual(p.exitcode,0);self.assertEqual(q.get(timeout=2)['reason'],'AUTHORITY_STORE_BEHIND_FENCE');self.assertEqual(self.count(),0)

    def test_admin_command_stale_even_with_live_signer(self):
        stale=self.request('destination_grants',dict(principal='agent',credential_version='v0',dependency_version='d1',grants=['read','write']))
        self.now=161
        result=self.runtime.apply(stale)
        self.assertEqual(result.get('reason'),'COMMAND_STALE')
        self.assertEqual(self.get('destination-grants','agent')['credential_version'],'v1')

    def test_admin_commands_cannot_roll_back_within_freshness_window(self):
        older=self.request('destination_grants',dict(principal='agent',credential_version='v0',dependency_version='d1',grants=['read','write']))
        self.view(credential_version='v2')
        self.assertEqual(self.runtime.apply(older).get('reason'),'SEQUENCE_REGRESSION')
        self.assertEqual(self.get('destination-grants','agent')['credential_version'],'v2')

    def test_missing_admin_sequence_is_refused(self):
        r=self.request('fence',dict(scope='tenant',generation=8));body=dict(r['body']);del body['sequence']
        r=signed(self.keys['admin'],'admin','destination-command',body)
        self.assertEqual(self.runtime.apply(r)['reason'],'INVALID_FIELDS')
        self.assertEqual(self.get('fence','tenant')['generation'],7)

    def verifier_denial(self,change,reason):
        r=self.request('execute',self.args());body=r['body'];status=body['arguments']['verifier_status']['body']
        status.update(change)
        body['arguments']['verifier_status']=signed(self.keys['verifier'],'verifier','destination-status',status)
        r=signed(self.keys['broker'],'broker','destination-command',body)
        self.assertEqual(self.runtime.apply(r).get('reason'),reason)
        self.assertEqual(self.count(),0)

    def test_verifier_recent_but_not_current_refused(self):self.verifier_denial({'at':99,'expires_at':200},'VERIFIER_NOT_CURRENT')
    def test_verifier_digest_substitution_refused(self):self.verifier_denial({'request_digest':'0'*64},'VERIFIER_BINDING')
    def test_verifier_generation_substitution_refused(self):self.verifier_denial({'generation':8},'VERIFIER_BINDING')
    def test_inactive_verifier_refused(self):self.verifier_denial({'active':False},'VERIFIER_NOT_CURRENT')
    def test_exact_command_replay_reason_is_explicit(self):
        r=self.request('execute',self.args());self.assertEqual(self.runtime.apply(r)['status'],'accepted')
        self.assertEqual(self.runtime.apply(r)['reason'],'COMMAND_REPLAY');self.assertEqual(self.count(),1)

    def test_fence_in_same_backup_set_detected(self):
        with self.assertRaisesRegex(ValueError,'FENCE_IN_SAME_BACKUP_SET'):
            ProtectedDestination.create(Path(self.temp.name)/'bad.db',authority_backup_set='same',destination_backup_set='same',clock=lambda:100,**self.config)

    def test_fence_cannot_decrease(self):self.deny('fence','FENCE_NOT_MONOTONIC',scope='tenant',generation=6)
    def test_unissued_future_generation_refused(self):self.deny('execute','AUTHORITY_STORE_BEHIND_FENCE',**self.args(generation=8))
    def test_hard_pin_default_rotation_holds(self):self.view(credential_version='v2');self.deny('execute','HARD_PIN_CHANGED',**self.args())
    def test_policy_change_holds(self):self.deny('execute','HARD_PIN_CHANGED',**self.args(policy='policy2'))
    def test_target_change_holds(self):self.deny('execute','HARD_PIN_CHANGED',**self.args(target='other'))

    def soft(self):self.provision(id='soft',modes={'credential':'soft','dependency':'soft'})
    def test_soft_pin_equivalent_rotation_proceeds_with_record(self):
        self.soft();self.view(credential_version='v2',dependency_version='d2');r=self.ok('execute',**self.args(grant='soft'))
        self.assertEqual(r['resolution_input']['changed_classes'],['credential','dependency']);self.assertEqual(self.count(),1)
        self.assertEqual(r['resolution_input']['before_digest'],r['resolution_input']['after_digest'])
    def test_soft_pin_rotation_superset_holds(self):
        self.soft();self.view(credential_version='v2',grants=['read','write','admin']);self.deny('execute','SOFT_PIN_SCOPE_WIDENED',**self.args(grant='soft'))
    def test_soft_pin_identical_issuer_claims_broader_destination_role_holds(self):
        self.soft();self.view(grants=['read','write','admin']);self.deny('execute','SOFT_PIN_SCOPE_WIDENED',**self.args(grant='soft'))
    def test_narrowing_is_not_equivalence(self):
        self.soft();self.view(grants=['read']);self.deny('execute','SOFT_PIN_SCOPE_CHANGED',**self.args(grant='soft'))
    def test_soft_pin_destination_unreadable_holds(self):
        self.soft()
        with self.runtime.connection() as c:c.execute("DELETE FROM objects WHERE kind='destination-grants'")
        self.deny('execute','SOFT_PIN_DESTINATION_UNREAD',**self.args(grant='soft'))
    def test_soft_policy_class_forbidden(self):
        a={k:v for k,v in self.get('grant','grant').items() if k not in ('grants','consumed','revoked','custodian','credential_binding_active')};a['id']='bad';a['modes']={'policy':'soft'}
        self.deny('provision','SOFT_CLASS_FORBIDDEN',**a)
    def test_grant_exhaustion_closes_credential_binding(self):
        self.ok('execute',**self.args());self.assertFalse(self.get('grant','grant')['credential_binding_active'])
        r=self.call('execute',**self.args(effect='other'));self.assertEqual(r['reason'],'CREDENTIAL_BINDING_CLOSED');self.assertEqual(self.count(),1)
    def test_exhausted_grant_direct_agent_call_refused(self):
        self.ok('execute',**self.args());r=self.runtime.apply(self.request('execute',self.args(effect='other'),actor='agent'));self.assertEqual(r['reason'],'SIGNER_SCOPE');self.assertEqual(self.count(),1)
    def test_agent_computed_claim_refused(self):
        request=self.request('execute',self.args());request['signature']=digest(request)*2
        self.assertEqual(self.runtime.apply(request).get('reason'),'SIGNATURE_INVALID');self.assertEqual(self.count(),0)
    def test_verifier_unreachable_destination_refuses(self):self.deny('execute','VERIFIER_UNREACHABLE',**self.args(verifier_status=None))
    def test_revocation_closes_credential_binding(self):
        self.ok('revoke',grant='grant');self.deny('execute','CREDENTIAL_BINDING_CLOSED',**self.args())
    def test_expired_credential_refused(self):self.now=200;self.deny('execute','CREDENTIAL_EXPIRED',**self.args())
    def test_verifier_attestation_cannot_be_reused_for_other_command(self):
        first=self.request('execute',self.args());second=self.request('execute',dict(first['body']['arguments']))
        self.assertEqual(self.runtime.apply(second)['reason'],'VERIFIER_BINDING');self.assertEqual(self.count(),0)
    def test_stale_verifier_attestation_refused(self):
        request=self.request('execute',self.args());self.now=101;self.assertEqual(self.runtime.apply(request)['reason'],'VERIFIER_NOT_CURRENT')
    def test_same_custody_key_rejected(self):
        cfg=deepcopy(self.config);cfg['registry']['broker']['public_key']=cfg['registry']['admin']['public_key']
        with self.assertRaisesRegex(ValueError,'CUSTODY_KEY_SEPARATION'):ProtectedDestination(self.path,clock=lambda:100,**cfg)
    def test_resolution_write_failure_has_no_effect(self):
        self.soft();self.view(credential_version='v2')
        with self.runtime.connection() as c:c.execute("CREATE TRIGGER fail_resolution BEFORE INSERT ON objects WHEN NEW.kind='resolution-input' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.call('execute',**self.args(grant='soft'))
        self.assertEqual(self.count(),0);self.assertEqual(self.get('grant','soft')['consumed'],0)
    def test_audit_write_failure_rolls_back_effect_and_consumption(self):
        with self.runtime.connection() as c:c.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.call('execute',**self.args())
        self.assertEqual(self.count(),0);self.assertEqual(self.get('grant','grant')['consumed'],0)
    def test_lost_ack_reopen_preserves_one_effect(self):
        self.ok('execute',**self.args());self.runtime=ProtectedDestination(self.path,clock=lambda:self.now,**self.config)
        self.assertTrue(self.ok('execute',**self.args())['duplicate']);self.assertEqual(self.count(),1)
    def test_effect_id_conflict_refused(self):
        self.ok('execute',**self.args());r=self.call('execute',**self.args(payload='changed'));self.assertEqual(r['reason'],'EFFECT_ID_CONFLICT');self.assertEqual(self.count(),1)
    def test_negative_record_is_durable_and_payload_free(self):
        self.deny('execute','VERIFIER_UNREACHABLE',**self.args(verifier_status=None,payload='PRIVATE-FIXTURE'))
        with self.runtime.connection() as c:rows=c.execute('SELECT body FROM events').fetchall()
        self.assertIn('VERIFIER_UNREACHABLE',rows[-1][0]);self.assertNotIn('PRIVATE-FIXTURE',str(rows))

    def test_concurrent_custodians_share_one_budget(self):
        ctx=multiprocessing.get_context('spawn');q=ctx.Queue()
        requests=[self.request('execute',self.args(effect='effect-'+str(i))) for i in range(2)]
        processes=[ctx.Process(target=restored_client,args=(str(self.path),self.config,r,q)) for r in requests]
        for p in processes:p.start()
        for p in processes:p.join(10);self.assertEqual(p.exitcode,0)
        results=[q.get(timeout=2) for _ in processes]
        self.assertEqual(sum(r['status']=='accepted' for r in results),1);self.assertEqual(self.count(),1)

    def test_crash_before_commit_rolls_back_receipt_and_effect(self):
        request=self.request('execute',self.args());ctx=multiprocessing.get_context('spawn')
        p=ctx.Process(target=crashing_client,args=(str(self.path),self.config,request));p.start();p.join(10)
        self.assertEqual(p.exitcode,73);self.assertEqual(self.count(),0);self.assertEqual(self.get('grant','grant')['consumed'],0)
        self.assertEqual(self.runtime.apply(request)['status'],'accepted');self.assertEqual(self.count(),1)
