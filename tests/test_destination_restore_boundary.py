"""S3 / lane C: passing characterizations are not rollback-safety acceptance.

Only synthetic local SQLite commits are observed. The append-only test witness
is outside the restore set, never consulted by admission, and is NOT an anchor.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from reference_profiles.assurance_runtime import digest
from reference_profiles.protected_destination import ProtectedDestination
from reference_profiles.trust_evidence import signed

ROOT = Path(__file__).resolve().parents[1]


def backup(source, target):
    # Explicit consistent SQLite backup, with no live callers during restore.
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
        src.backup(dst)
    return hashlib.sha256(target.read_bytes()).hexdigest()


def state(path):
    with sqlite3.connect(path) as c:
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {t: sorted(c.execute('SELECT * FROM "' + t + '"').fetchall(), key=repr) for t in tables}


def witness(path, effect):
    # Observer of successful synthetic commits; never used as an admission input.
    with path.open('a') as f:
        f.write(json.dumps({'synthetic_commit_observed': effect}) + '\n')


def observations(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


@pytest.fixture
def report(request):
    record = {'case': request.node.name, 'observer_is_production_control': False,
              'production_authorized': False, 'full_restore_prevention': 'BLOCKED'}
    yield record
    if os.environ.get('RESTORE_BOUNDARY_RESULTS'):
        root = Path(os.environ['RESTORE_BOUNDARY_RESULTS']); root.mkdir(parents=True, exist_ok=True)
        (root / (request.node.name + '.json')).write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')


class Case:
    def __init__(self, root):
        self.root = root; self.path = root / 'destination.db'; self.serial = 0
        self.now = 100; self.observer = root / 'outside-restore-witness.jsonl'
        self.keys = {p: Ed25519PrivateKey.generate() for p in ('admin', 'broker', 'verifier')}
        self.config = dict(registry={p: {'public_key': k.public_key().public_bytes_raw().hex(),
            'not_before': 0, 'expires_at': 1000, 'revoked_at': None} for p, k in self.keys.items()},
            admin='admin', custodian='broker', verifier='verifier')
        self.runtime = ProtectedDestination.create(self.path, authority_backup_set='authority',
            destination_backup_set='destination', clock=lambda: self.now, **self.config)
        self.ok('fence', scope='tenant', generation=7)
        self.ok('destination_grants', principal='agent', credential_version='v1', dependency_version='d1', grants=['write'])
        self.ok('provision', id='grant', scope='tenant', generation=7, principal='agent', policy='policy',
            target='sink', credential_version='v1', dependency_version='d1', modes={}, max_effects=1, expires_at=200)

    def restart(self):
        self.runtime = ProtectedDestination(self.path, clock=lambda: self.now, **self.config)

    def command(self, operation, **args):
        self.serial += 1; identity = 'cmd-' + str(self.serial)
        actor = 'broker' if operation == 'execute' else 'admin'
        if operation == 'execute':
            args = dict(grant='grant', effect='effect', generation=7, policy='policy', target='sink',
                        payload='synthetic', issuer_claims={}, **args)
            d = digest({k: v for k, v in args.items() if k not in ('verifier_status', 'issuer_claims')})
            args['verifier_status'] = signed(self.keys['verifier'], 'verifier', 'destination-status',
                dict(at=self.now, expires_at=self.now+1, command=identity, request_digest=d, generation=7, active=True))
        body = dict(id=identity, operation=operation, at=self.now, arguments=args)
        if operation != 'execute': body['sequence'] = self.serial
        return signed(self.keys[actor], actor, 'destination-command', body)

    def apply(self, command):
        before = state(self.path)['effects']
        result = self.runtime.apply(command)
        after = state(self.path)['effects']
        added = [row for row in after if row not in before]
        assert len(added) <= 1
        for row in added: witness(self.observer, row[0])
        return result

    def ok(self, operation, **args):
        result = self.apply(self.command(operation, **args)); assert result['status'] == 'accepted', result
        return result

    def snapshot(self):
        snap = self.root / 'snapshot.db'; self.snapshot_hash = backup(self.path, snap); return snap

    def restore(self, snap, report):
        report.update(snapshot_scope='complete destination: objects/fence/grants/commands/admin-sequence/effects/events',
                      restore_scope='complete destination', snapshot_sha256=self.snapshot_hash,
                      before_restore=state(self.path), witness_before_restore=observations(self.observer))
        backup(snap, self.path); self.restart()
        report['after_restore'] = state(self.path)
        assert report['after_restore'] == state(snap)

    def finish(self, report, result, expected, count, interpretation):
        assert result.get('reason', result['status']) == expected
        assert len(observations(self.observer)) == count
        report.update(expected_admission=expected, observed_admission=result,
            final_state=state(self.path), cumulative_effect_observations=observations(self.observer),
            interpretation=interpretation)


@pytest.fixture
def case(tmp_path):
    return Case(tmp_path)


@pytest.mark.parametrize('change,expected', [('fence','AUTHORITY_STORE_BEHIND_FENCE'),
    ('revoke','CREDENTIAL_BINDING_CLOSED'), ('consume','COMMAND_REPLAY')])
def test_authority_only_restore(case, report, change, expected):
    old = case.command('execute')
    authority = case.root / 'authority.json'; authority.write_text(json.dumps({'pending_command': old}))
    snapshot_bytes = authority.read_bytes()
    if change == 'fence': case.ok('fence', scope='tenant', generation=8)
    elif change == 'revoke': case.ok('revoke', grant='grant')
    else: assert case.apply(old)['status'] == 'accepted'
    authority.write_text(json.dumps({'pending_command': None, 'advanced_state': change}))
    authority_before = json.loads(authority.read_text())
    before = state(case.path)
    authority.write_bytes(snapshot_bytes)  # authority-side pending queue restored, destination untouched
    case.restart()
    assert state(case.path) == before
    result = case.apply(json.loads(authority.read_text())['pending_command'])
    case.finish(report, result, expected, int(change == 'consume'), 'protection conditional on current destination survival')
    report.update(snapshot_scope='authority-side signed pending-command JSON fixture only; no institutional service',
        restore_scope='authority fixture only', snapshot_sha256=hashlib.sha256(snapshot_bytes).hexdigest(),
        before_restore=before, after_restore=before, authority_before_restore=authority_before,
        authority_after_restore=json.loads(authority.read_text()),
        audit_evidence='all pre-restore destination events survive; denial appended')
    # Restart preserves refusal; no extra effect may appear.
    case.restart(); assert case.apply(old)['reason'] == expected
    assert len(observations(case.observer)) == int(change == 'consume')


@pytest.mark.parametrize('change', ['fence','revoke'])
def test_full_restore_before_invalidation(case, report, change):
    old = case.command('execute'); snap = case.snapshot()
    if change == 'fence': case.ok('fence', scope='tenant', generation=8)
    else: case.ok('revoke', grant='grant')
    assert case.apply(old)['status'] == 'denied'
    case.restore(snap, report)
    result = case.apply(old)
    case.finish(report, result, 'accepted', 1, 'LIMITATION: restored fence/revocation admits old signed command')
    assert result['result']['duplicate'] is False
    report['audit_evidence'] = 'invalidation and denial erased; restored history plus new acceptance remain'
    case.restart(); assert case.apply(old)['reason'] == 'COMMAND_REPLAY'
    assert len(observations(case.observer)) == 1


def test_full_restore_before_consumption_lost_ack(case, report):
    old = case.command('execute'); snap = case.snapshot()
    assert case.apply(old)['result']['duplicate'] is False  # ACK deliberately discarded
    case.restore(snap, report)
    assert state(case.path)['effects'] == []
    result = case.apply(old)
    case.finish(report, result, 'accepted', 2, 'LIMITATION: two historical synthetic commits; restored table contains one')
    assert result['result']['duplicate'] is False
    assert len(state(case.path)['effects']) == 1
    report['audit_evidence'] = 'first acceptance and consumption erased; second acceptance retained'
    case.restart(); assert case.apply(old)['reason'] == 'COMMAND_REPLAY'
    assert len(observations(case.observer)) == 2


def test_current_destination_lost_ack_and_postcommit_restore(case, report):
    old = case.command('execute'); assert case.apply(old)['result']['duplicate'] is False
    snap = case.snapshot()
    assert case.apply(old)['reason'] == 'COMMAND_REPLAY'
    case.restore(snap, report)
    assert case.apply(old)['reason'] == 'COMMAND_REPLAY'
    # A new command identity for the exact effect reconciles without consumption.
    retry = case.command('execute'); result = case.apply(retry)
    assert result['result']['duplicate'] is True
    case.finish(report, result, 'accepted', 1, 'protection conditional on postcommit effect/command records surviving')
    report['audit_evidence'] = 'original acceptance survives; only denial after snapshot lost; duplicate acceptance appended'
    case.restart(); assert case.apply(retry)['reason'] == 'COMMAND_REPLAY'
    assert len(observations(case.observer)) == 1


def test_old_admin_command_after_full_restore(case, report):
    old = case.command('destination_grants', principal='agent', credential_version='v0', dependency_version='d1', grants=['write'])
    snap = case.snapshot()
    assert case.apply(old)['status'] == 'accepted'
    case.ok('destination_grants', principal='agent', credential_version='v2', dependency_version='d1', grants=['write'])
    assert case.apply(old)['reason'] == 'COMMAND_REPLAY'
    case.restore(snap, report)
    result = case.apply(old)
    case.finish(report, result, 'accepted', 0, 'LIMITATION: admin command and sequence memory roll back within freshness window')
    report['audit_evidence'] = 'v0/v2 acceptance and replay refusal erased; restored v0 acceptance retained'
    case.restart(); assert case.apply(old)['reason'] == 'COMMAND_REPLAY'
    # Advancing the trusted clock still blocks an unseen old command.
    stale = deepcopy(old); stale['body']['id'] = 'unseen-old-admin'
    stale = signed(case.keys['admin'], 'admin', 'destination-command', stale['body'])
    case.now = 161
    assert case.apply(stale)['reason'] == 'COMMAND_STALE'


@pytest.fixture(scope='module')
def c1_dependencies():
    sys.dont_write_bytecode = True
    from tools.optional_execution_profile import prepare
    work = ROOT / '.optional-work'; env, pins, lock_hash = prepare(work)
    # Reuse the repository's exact selected optional-profile import conventions.
    os.environ.update(env); sys.path[:0] = env['PYTHONPATH'].split(os.pathsep)
    return work, pins, lock_hash


@pytest.mark.parametrize('scope', ['authority-only', 'full-before-revoke', 'full-before-consume', 'full-after-consume'])
def test_same_host_c1_restore(tmp_path, report, c1_dependencies, scope):
    from tools.optional_execution import setup, BASE
    from engine.local_authority_effect import AtomicAuthorityEffectDestination, AtomicLocalControlPlaneExecutor
    work, pins, lock_hash = c1_dependencies
    workflow, resolver, proposal, decision, envelope, policy = setup(tmp_path, work)
    root = tmp_path / 'atomic'; observer = tmp_path / 'outside-c1-restore-witness.jsonl'
    destination = AtomicAuthorityEffectDestination(root, clock=lambda: BASE)
    executor = AtomicLocalControlPlaneExecutor(workflow=workflow, destination=destination, policy=policy)
    claim = executor.provision_claim(proposal=proposal, decision=decision, now=BASE)
    snap = tmp_path / 'c1-snapshot.db'
    snapshot_hash = backup(destination.path, snap)

    def execute():
        before_effects = state(destination.path)['effects']
        result = executor.execute(envelope=envelope, claim_id=claim.claim_id)
        added = [row for row in state(destination.path)['effects'] if row not in before_effects]
        assert len(added) == int(result.newly_executed)
        for row in added: witness(observer, envelope.effect_id)
        return result

    if scope in ('authority-only', 'full-before-revoke'):
        authority_file = tmp_path / 'resolver-context-snapshot.json'
        authority_file.write_text(json.dumps(resolver.contexts))
        authority_snapshot = json.loads(authority_file.read_text())
        resolver.contexts[proposal.authority_context_ref]['grant']['status'] = 'revoked'
        destination.set_grant_status(claim.grant_id, status='revoked')
        assert execute().status == 'denied'
    else:
        assert execute().newly_executed
        if scope == 'full-after-consume': snapshot_hash = backup(destination.path, snap)
    before = state(destination.path)
    if scope == 'authority-only': resolver.contexts = json.loads(authority_file.read_text())
    else: backup(snap, destination.path)
    destination = AtomicAuthorityEffectDestination(root, clock=lambda: BASE)
    executor = AtomicLocalControlPlaneExecutor(workflow=workflow, destination=destination, policy=policy)
    after = state(destination.path)
    assert after == (before if scope == 'authority-only' else state(snap))
    assert destination.claim_state(claim.claim_id) == ('consumed' if scope == 'full-after-consume' else 'issued')
    result = execute()
    expected_count = 2 if scope == 'full-before-consume' else (0 if scope == 'authority-only' else 1)
    assert len(observations(observer)) == expected_count
    assert result.newly_executed == (scope in ('full-before-revoke', 'full-before-consume'))
    if scope == 'authority-only': assert result.status == 'denied'
    # Reopen once more: retained claim/effect state persists after the restore run.
    destination = AtomicAuthorityEffectDestination(root, clock=lambda: BASE)
    executor = AtomicLocalControlPlaneExecutor(workflow=workflow, destination=destination, policy=policy)
    assert not execute().newly_executed
    assert len(observations(observer)) == expected_count
    report.update(snapshot_scope='resolver contexts only' if scope == 'authority-only' else 'complete same-host C1 SQLite store',
        restore_scope=scope, snapshot_sha256=(hashlib.sha256(authority_file.read_bytes()).hexdigest() if scope == 'authority-only' else snapshot_hash),
        expected_admission='denied' if scope == 'authority-only' else 'new effect' if scope in ('full-before-revoke', 'full-before-consume') else 'no new effect',
        observed_admission={'status': result.status, 'newly_executed': result.newly_executed},
        before_restore=before, after_restore=after, final_state=state(destination.path),
        cumulative_effect_observations=observations(observer), component_pins=pins, component_lock_sha256=lock_hash,
        audit_evidence='all SQLite tables recorded; full restore loses all post-snapshot records, including claim/effect evidence',
        interpretation='LIMITATION' if scope in ('full-before-revoke','full-before-consume') else 'protection conditional on retained destination state')
