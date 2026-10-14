"""Bounded actual local paths; no external identity, sink or custody qualification."""
from copy import deepcopy
from dataclasses import asdict, replace
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from reference_profiles.context_memory import ContextMemory
from reference_profiles.payload_disclosure import PayloadDisclosureGate
from reference_profiles.context_journal import export_context_journal, assess_context_journal, prefix_digest
from reference_profiles.resolver_assurance import CONTRACT, ObjectBinding, SourceProfile, resolve_observations, sign_fixture
from reference_profiles.resolver_revision_ledger import RevisionLedger


class RevisionMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'revisions.db'
        self.ledger = RevisionLedger.create(self.path)
        self.profile = SourceProfile('source', 'v1', ObjectBinding('org','domain','grant','g1','scope'), b'synthetic-fixture-key-only-000000', 30, 0, 1)
        self.record = {'contract': CONTRACT, 'source_id':'source', 'profile_version':'v1', 'binding':asdict(self.profile.binding),
                       'revision':3, 'status':'CURRENT_VALID', 'observed_at':95, 'effective_at':90, 'valid_until':120, 'facts_digest':'a'*64}

    def resolve(self, record=None, profile=None, response=None):
        p = profile or self.profile
        return resolve_observations((p,), lambda _: response if response is not None else sign_fixture(p, record or self.record), now=100, revision_ledger=self.ledger)

    def test_restart_rejects_rollback(self):
        self.assertEqual(self.resolve()['classification'], 'CURRENT_VALID')
        self.ledger = RevisionLedger(self.path)
        result = self.resolve(dict(self.record, revision=2))
        self.assertEqual(result['classification'], 'STALE'); self.assertTrue(result['hold'])
        self.assertFalse(result['authorizes_execution'])

    def test_fresh_revocation_advances_floor(self):
        self.resolve(dict(self.record, revision=4, status='REVOKED'))
        self.assertEqual(self.resolve()['classification'], 'STALE')

    def test_authenticated_unknown_advances_floor(self):
        self.resolve(dict(self.record, revision=4, status='UNKNOWN'))
        self.assertEqual(self.resolve()['classification'], 'STALE')

    def test_same_revision_conflict_stays_blocked_after_reopen(self):
        self.resolve()
        self.assertEqual(self.resolve(dict(self.record, facts_digest='b'*64))['classification'], 'CONFLICT')
        self.ledger = RevisionLedger(self.path)
        self.assertEqual(self.resolve()['classification'], 'CONFLICT')
        self.assertEqual(self.resolve(dict(self.record, revision=4))['classification'], 'CURRENT_VALID')

    def test_key_rotation_does_not_reset_revision_floor(self):
        self.resolve()
        p = replace(self.profile, version='v2', key=b'new-synthetic-fixture-key-00000000')
        result = self.resolve(dict(self.record, profile_version='v2', revision=2), profile=p)
        self.assertEqual(result['classification'], 'STALE')
        # Old key responses cannot authenticate under the new configured profile.
        self.assertEqual(self.resolve(profile=p, response=sign_fixture(self.profile,self.record))['classification'], 'UNAUTHENTICATED')

    def test_malformed_or_unauthenticated_record_cannot_poison_floor(self):
        for changes in ({'revision':100, 'facts_digest':'bad'}, {'revision':100, 'status':'unsupported'}, {'revision':100, 'observed_at':True}):
            self.assertTrue(self.resolve(dict(self.record, **changes))['hold'])
        forged = sign_fixture(self.profile, dict(self.record, revision=100)); forged['mac'] = '0'*64
        self.assertTrue(self.resolve(response=forged)['hold'])
        self.assertEqual(self.resolve()['classification'], 'CURRENT_VALID')

    def test_missing_ledger_fails_closed_without_recreation(self):
        self.resolve(); self.path.unlink()
        self.assertEqual(self.resolve()['classification'], 'UNKNOWN')
        self.assertFalse(self.path.exists())

    def test_existing_ledger_cannot_be_reinitialized(self):
        self.resolve()
        with self.assertRaises(FileExistsError): RevisionLedger.create(self.path)
        self.assertEqual(self.resolve(dict(self.record, revision=2))['classification'], 'STALE')

    def test_corrupt_ledger_fails_closed(self):
        self.path.write_bytes(b'not a sqlite database')
        self.assertEqual(self.resolve()['classification'], 'UNKNOWN')

    def test_scope_isolation(self):
        self.resolve(dict(self.record, revision=9))
        p = replace(self.profile, binding=replace(self.profile.binding, object_id='g2'))
        self.assertEqual(self.resolve(dict(self.record,binding=asdict(p.binding)),profile=p)['classification'], 'CURRENT_VALID')

    def test_concurrent_updates_cannot_lower_persisted_floor(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda rev:self.resolve(dict(self.record, revision=rev)), [6,4,9,7]))
        self.assertTrue(all(r['classification'] in ('CURRENT_VALID','STALE') for r in results))
        self.ledger = RevisionLedger(self.path)
        self.assertEqual(self.resolve(dict(self.record, revision=8))['classification'], 'STALE')
        self.assertEqual(self.resolve(dict(self.record, revision=9))['classification'], 'CURRENT_VALID')


class DisclosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.now = 100; self.policy = None; self.received = []
        self.gate = PayloadDisclosureGate(sink_id='synthetic-public-sink', exposure='public', policy_version='v1', resolve=lambda _: deepcopy(self.policy))
        self.memory = ContextMemory(Path(self.temp.name)/'context.db', clock=lambda:self.now, disclosure_gate=self.gate)
        self.receipt = self.admit('private', 'SYNTHETIC-CANARY-DO-NOT-DISCLOSE')

    def admit(self, identity, content):
        return self.memory.admit(item_id=identity, content=content, purposes=['support'], recipients=['viewer'], obligations=['retain-source'], expires_at=200, source_ref='synthetic:source')

    def policy_for(self, content, receipt):
        check = self.gate.check(content=content, receipt=receipt, purpose='support', recipient='viewer', clock=lambda:self.now)
        return {'binding':check['binding'], 'grant_id':'synthetic-disclosure', 'grant_revision':1, 'status':'active', 'valid_from':90, 'expires_at':150}

    def deliver(self, identity='private'):
        return self.memory.deliver(identity, purpose='support', recipient='viewer', expected_generation=self.memory.generation(), callback=self.received.append)

    def test_permitted_recipient_does_not_permit_secret_payload(self):
        redacted = self.admit('redacted','Public summary')
        self.policy = self.policy_for('Public summary',redacted)
        with self.assertRaisesRegex(PermissionError,'DISCLOSURE_BINDING_MISMATCH'): self.deliver()
        self.assertEqual(self.received, [])
        self.assertEqual(self.deliver('redacted')['state'], 'delivered')
        self.assertEqual(self.received,['Public summary'])

    def test_exact_permitted_payload_reaches_actual_callback(self):
        self.policy = self.policy_for('SYNTHETIC-CANARY-DO-NOT-DISCLOSE',self.receipt)
        self.assertEqual(self.deliver()['state'],'delivered')
        self.assertEqual(len(self.received),1)

    def test_binding_dimensions_are_enforced(self):
        original = self.policy_for('SYNTHETIC-CANARY-DO-NOT-DISCLOSE',self.receipt)
        for field in original['binding']:
            self.policy = deepcopy(original); self.policy['binding'][field]='substituted'
            with self.subTest(field=field), self.assertRaises(PermissionError): self.deliver()
        self.assertEqual(self.received,[])

    def test_revoked_policy_retains_negative_binding_without_content(self):
        self.policy = self.policy_for('SYNTHETIC-CANARY-DO-NOT-DISCLOSE',self.receipt)
        self.policy.update(status='revoked',grant_revision=2)
        with self.assertRaisesRegex(PermissionError,'DISCLOSURE_REVOKED'): self.deliver()
        with self.memory.connection() as conn:
            event = json.loads(conn.execute("SELECT detail FROM events WHERE kind='disclosure_check'").fetchone()[0])
            self.assertEqual(conn.execute('SELECT count(*) FROM deliveries').fetchone()[0],0)
        self.assertEqual(event['grant_revision'],2); self.assertFalse(event['allowed'])
        self.assertEqual(event['binding'],self.policy['binding'])
        self.assertNotIn('SYNTHETIC-CANARY-DO-NOT-DISCLOSE',json.dumps(event))
        self.assertEqual(self.received,[])

    def test_missing_malformed_expired_future_unknown_policy_blocks(self):
        original = self.policy_for('SYNTHETIC-CANARY-DO-NOT-DISCLOSE',self.receipt)
        for policy in (None, {}, dict(original,grant_revision=True), dict(original,expires_at=100), dict(original,valid_from=101), dict(original,status='unrecognized')):
            self.policy = policy
            with self.subTest(policy=policy), self.assertRaises(PermissionError): self.deliver()
        self.assertEqual(self.received,[])

    def test_resolver_failure_and_mutation_do_not_permit(self):
        def unavailable(_): raise RuntimeError('private failure text')
        self.gate.resolve=unavailable
        with self.assertRaisesRegex(PermissionError,'POLICY_UNAVAILABLE'): self.deliver()
        def mutating(binding):
            binding['payload_sha256']='changed'
            return {'binding':binding,'grant_id':'x','grant_revision':1,'status':'active','valid_from':90,'expires_at':150}
        self.gate.resolve=mutating
        with self.assertRaisesRegex(PermissionError,'DISCLOSURE_BINDING_MISMATCH'): self.deliver()
        self.assertEqual(self.received,[])

    def test_parent_restrictions_still_block_derived_content(self):
        with self.assertRaises(PermissionError):
            self.memory.admit(item_id='child',content='summary',purposes=['support'],recipients=['other'],obligations=['retain-source'],expires_at=180,source_ref='synthetic:derived',parents=['private'])
        self.assertEqual(self.received,[])

    def test_policy_expiry_during_resolver_blocks_before_callback(self):
        self.policy = self.policy_for('SYNTHETIC-CANARY-DO-NOT-DISCLOSE',self.receipt)
        def delayed(_):
            self.now = 150
            return deepcopy(self.policy)
        self.gate.resolve=delayed
        with self.assertRaisesRegex(PermissionError,'DISCLOSURE_EXPIRED_OR_NOT_YET_VALID'): self.deliver()
        self.assertEqual(self.received,[])

    def test_context_expiry_during_resolver_blocks_before_callback(self):
        self.policy = self.policy_for('SYNTHETIC-CANARY-DO-NOT-DISCLOSE',self.receipt)
        self.policy['expires_at']=300
        def delayed(_):
            self.now=200
            return deepcopy(self.policy)
        self.gate.resolve=delayed
        with self.assertRaisesRegex(PermissionError,'current use not permitted'): self.deliver()
        self.assertEqual(self.received,[])

    def test_callback_failure_remains_unknown(self):
        self.policy = self.policy_for('SYNTHETIC-CANARY-DO-NOT-DISCLOSE',self.receipt)
        def fail(_): raise RuntimeError('lost acknowledgment')
        result=self.memory.deliver('private',purpose='support',recipient='viewer',expected_generation=self.memory.generation(),callback=fail)
        self.assertEqual(result['state'],'unknown')
        self.assertFalse(result['authorizing'])


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.memory = ContextMemory(Path(self.temp.name)/'context.db',clock=lambda:100)
        self.memory.admit(item_id='x',content='SYNTHETIC-PRIVATE',purposes=['support'],recipients=['viewer'],obligations=['source'],expires_at=200,source_ref='synthetic:source')
        self.memory.deliver('x',purpose='support',recipient='viewer',expected_generation=self.memory.generation(),callback=lambda _:None)
        self.package = export_context_journal(self.memory)
        self.count = len(self.package['events'])
        self.checkpoint = {'count':self.count,'sha256':prefix_digest(self.package['events'])}

    def assess(self, package=None, **kwargs):
        return assess_context_journal(self.package if package is None else package, expected_count=self.count, checkpoint=self.checkpoint, **kwargs)

    def test_retained_complete_prefix_is_non_authorizing(self):
        result=self.assess()
        for field in ('record_coverage','checkpoint_match','custody_lag'): self.assertEqual(result[field],'compliant')
        for field in ('authorizing','capture_completeness_verified','independent_custody_verified','production_ready'): self.assertIs(result[field],False)
        self.assertNotIn('SYNTHETIC-PRIVATE',json.dumps(self.package))

    def test_missing_journal_is_unevaluable_not_compliant(self):
        result=assess_context_journal(None,expected_count=self.count,checkpoint=self.checkpoint)
        self.assertEqual(result['record_coverage'],'unevaluable')

    def test_deleted_reordered_duplicate_and_truncated_records_fail(self):
        for transform in (lambda e:e[1:],lambda e:e[:-1],lambda e:list(reversed(e)),lambda e:e+[e[-1]]):
            package=deepcopy(self.package); package['events']=transform(package['events'])
            self.assertEqual(self.assess(package)['record_coverage'],'violated')

    def test_coherent_rewrite_fails_trusted_checkpoint(self):
        package=deepcopy(self.package); package['events'][0]['detail']['receipt']['source_ref']='substituted'
        self.assertEqual(self.assess(package)['checkpoint_match'],'violated')

    def test_uncommitted_tail_has_explicit_lag(self):
        cp={'count':1,'sha256':prefix_digest(self.package['events'][:1])}
        result=assess_context_journal(self.package,expected_count=self.count,checkpoint=cp)
        self.assertEqual(result['custody_lag'],'violated'); self.assertEqual(result['uncommitted_events'],self.count-1)
        result=assess_context_journal(self.package,expected_count=self.count,checkpoint=cp,max_uncommitted_events=self.count-1)
        self.assertEqual(result['custody_lag'],'compliant')
        self.assertFalse(result['independent_custody_verified'])

    def test_stored_gap_is_detected_by_real_export(self):
        with self.memory.connection() as conn: conn.execute('DELETE FROM events WHERE seq=2')
        self.assertEqual(self.assess(export_context_journal(self.memory))['record_coverage'],'violated')

    def test_restart_export_matches_retained_prefix(self):
        reopened=ContextMemory(self.memory.path,clock=lambda:100)
        self.assertEqual(self.assess(export_context_journal(reopened))['checkpoint_match'],'compliant')

    def test_invalid_checkpoint_and_bool_counts_rejected(self):
        for count,cp,lag in ((True,self.checkpoint,0),(self.count,dict(self.checkpoint,count=True),0),(self.count,dict(self.checkpoint,count=99),0),(self.count,self.checkpoint,True)):
            with self.assertRaises(ValueError): assess_context_journal(self.package,expected_count=count,checkpoint=cp,max_uncommitted_events=lag)

    def test_malformed_or_inflated_package_fails(self):
        for change in ('limits','seq','nan','extra'):
            package=deepcopy(self.package)
            if change=='limits': package['limits']['authorizing']=True
            if change=='seq': package['events'][0]['seq']=True
            if change=='nan': package['events'][-1]['detail']['x']=float('nan')
            if change=='extra': package['production_ready']=True
            self.assertEqual(self.assess(package)['record_coverage'],'violated')


if __name__ == '__main__': unittest.main()
