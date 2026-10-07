import dataclasses
import os
from pathlib import Path
import sqlite3
import sys
import threading
import pytest
from tools.optional_execution_profile import prepare
from tools.optional_execution import BASE, setup
from reference_profiles.context_memory import ContextMemory

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.optional-work'


@pytest.fixture(scope='module', autouse=True)
def dependencies():
    env, _, _ = prepare(WORK)
    os.environ.update(env)
    sys.path[:0] = env['PYTHONPATH'].split(os.pathsep)


@pytest.fixture
def case(tmp_path):
    from engine.local_authority_effect import AtomicAuthorityEffectDestination, AtomicLocalControlPlaneExecutor
    from reference_profiles.context_action import ContextBoundExecutor
    workflow, resolver, proposal, decision, envelope, policy = setup(tmp_path, WORK)
    destination = AtomicAuthorityEffectDestination(tmp_path / 'destination', clock=lambda: BASE)
    executor = AtomicLocalControlPlaneExecutor(workflow=workflow, destination=destination, policy=policy)
    claim = executor.provision_claim(proposal=proposal, decision=decision, now=BASE)
    memory = ContextMemory(tmp_path / 'context.db', clock=lambda: 100)
    memory.admit(item_id='context', content='Synthetic context', purposes=['refund'], recipients=[envelope.operation.actor],
                 obligations=['source'], expires_at=200, source_ref='synthetic:source')
    delivery = memory.deliver('context', purpose='refund', recipient=envelope.operation.actor, expected_generation=memory.generation(), callback=lambda _: None)
    gateway = ContextBoundExecutor(memory, executor)
    binding = gateway.bind(delivery_id=delivery['delivery_id'], envelope=envelope, claim_id=claim.claim_id)
    return memory, gateway, destination, envelope, claim, binding


def effects(destination):
    with sqlite3.connect(destination.path) as conn:
        return conn.execute('SELECT count(*) FROM effects').fetchone()[0]


def invoke(case):
    memory, gateway, destination, envelope, claim, binding = case
    return gateway.execute(binding_id=binding, envelope=envelope, claim_id=claim.claim_id)


def test_delivered_context_bound_to_actual_effect(case):
    assert invoke(case).status == 'executed'
    memory, gateway, destination, envelope, claim, binding = case
    assert effects(destination) == 1
    memory.revoke('context')
    assert gateway.reconcile(binding_id=binding, envelope=envelope, claim_id=claim.claim_id).observed_state == 'applied'
    with pytest.raises(PermissionError):
        invoke(case)
    assert effects(destination) == 1


@pytest.mark.parametrize('change', ['revoked','generation','payload','claim','authority'])
def test_changed_context_or_operation_cannot_execute(case, change):
    memory, gateway, destination, envelope, claim, binding = case
    if change == 'revoked':
        memory.revoke('context')
    elif change == 'generation':
        memory.admit(item_id='new', content='new', purposes=['refund'], recipients=[envelope.operation.actor], obligations=['source'], expires_at=200, source_ref='new')
    elif change == 'payload':
        envelope = dataclasses.replace(envelope, operation=dataclasses.replace(envelope.operation, amount=70))
    elif change == 'authority':
        destination.set_grant_status(claim.grant_id, status='revoked')
    if change == 'authority':
        assert invoke(case).status == 'denied'
    else:
        with pytest.raises(PermissionError):
            gateway.execute(binding_id=binding, envelope=envelope, claim_id='other' if change == 'claim' else claim.claim_id)
    assert effects(destination) == 0


def test_context_lock_orders_cooperating_revocation_after_effect(case, monkeypatch):
    memory, gateway, destination, envelope, claim, binding = case
    entered, release, revoked = threading.Event(), threading.Event(), threading.Event()
    original = gateway.executor.execute
    def pause(**kwargs):
        entered.set()
        assert release.wait(5)
        return original(**kwargs)
    monkeypatch.setattr(gateway.executor, 'execute', pause)
    results, errors = [], []
    def execute():
        try: results.append(invoke(case))
        except BaseException as exc: errors.append(exc)
    def revoke():
        try:
            memory.revoke('context')
            revoked.set()
        except BaseException as exc: errors.append(exc)
    first = threading.Thread(target=execute)
    first.start()
    assert entered.wait(5)
    # Probe the held write lock directly; no sleep is used as an ordering oracle.
    with sqlite3.connect(memory.path, timeout=0) as conn:
        with pytest.raises(sqlite3.OperationalError, match='locked'):
            conn.execute('BEGIN IMMEDIATE')
    writer = threading.Thread(target=revoke)
    writer.start()
    release.set()
    first.join(5); writer.join(5)
    assert not first.is_alive() and not writer.is_alive() and not errors
    assert results[0].status == 'executed' and revoked.is_set()
    assert effects(destination) == 1


def test_postcommit_recording_failure_retains_no_retry_and_recovery(case, monkeypatch):
    memory, gateway, destination, envelope, claim, binding = case
    original = memory.event
    def fail(conn, kind, item, detail):
        if kind == 'bound_action_result': raise OSError('synthetic record failure')
        return original(conn, kind, item, detail)
    monkeypatch.setattr(memory, 'event', fail)
    with pytest.raises(OSError): invoke(case)
    assert effects(destination) == 1
    with pytest.raises(PermissionError): invoke(case)
    assert gateway.reconcile(binding_id=binding, envelope=envelope, claim_id=claim.claim_id).observed_state == 'applied'


def test_restore_preserves_consumed_atomic_claim_and_context_binding(case, tmp_path):
    from reference_profiles.sqlite_recovery import snapshot, restore
    from engine.local_authority_effect import AtomicAuthorityEffectDestination, AtomicLocalControlPlaneExecutor
    from reference_profiles.context_action import ContextBoundExecutor
    memory, gateway, destination, envelope, claim, binding = case
    assert invoke(case).status == 'executed'
    snapshot(destination.path, tmp_path / 'destination-backup')
    snapshot(memory.path, tmp_path / 'context-backup')
    target = tmp_path / 'restored-destination'
    target.mkdir()
    restore(tmp_path / 'destination-backup', target / 'refunds.sqlite3')
    restore(tmp_path / 'context-backup', tmp_path / 'restored-context.db')
    restored_destination = AtomicAuthorityEffectDestination(target, clock=lambda: BASE)
    restored_executor = AtomicLocalControlPlaneExecutor(workflow=gateway.executor.workflow, destination=restored_destination, policy=gateway.executor.policy)
    restored_memory = ContextMemory(tmp_path / 'restored-context.db', clock=lambda: 100)
    restored = ContextBoundExecutor(restored_memory, restored_executor)
    with pytest.raises(PermissionError):
        restored.execute(binding_id=binding, envelope=envelope, claim_id=claim.claim_id)
    assert restored_executor.execute(envelope=envelope, claim_id=claim.claim_id).status == 'denied'
    assert restored.reconcile(binding_id=binding, envelope=envelope, claim_id=claim.claim_id).observed_state == 'applied'
    assert effects(restored_destination) == 1


def test_restore_preserves_intent_dispatch_ownership(case, tmp_path):
    from reference_profiles.sqlite_recovery import snapshot, restore
    from engine.refund_intent import RefundIntent, RefundIntentRegistry, IntentRefundDestination
    from engine.safe_executor import DurableRefundDestination, snapshot_envelope
    _, _, _, envelope, _, _ = case
    original = DurableRefundDestination(tmp_path / 'intent')
    intent = RefundIntent(envelope.operation.institution_id, envelope.operation.authority_domain, envelope.operation.payload['customer_id'], 'synthetic-request')
    registry = RefundIntentRegistry(original)
    frozen = snapshot_envelope(envelope)
    registry.provision(intent, frozen)
    IntentRefundDestination(original, intent).commit(frozen)
    snapshot(original.path, tmp_path / 'intent-backup')
    target = tmp_path / 'restored-intent'
    target.mkdir()
    restore(tmp_path / 'intent-backup', target / 'refunds.sqlite3')
    restored = DurableRefundDestination(target)
    with pytest.raises(PermissionError):
        IntentRefundDestination(restored, intent).commit(dataclasses.replace(frozen, effect_id='replanned'))
    assert RefundIntentRegistry(restored).export_intent(intent)['dispatch_started']
    assert effects(restored) == 1


@pytest.mark.parametrize('purpose,recipient', [('marketing',None), ('refund','another-worker')])
def test_delivery_cannot_be_repurposed_for_different_action_or_actor(case, purpose, recipient):
    memory, gateway, destination, envelope, claim, _ = case
    recipient = recipient or envelope.operation.actor
    memory.admit(item_id='other-context',content='synthetic',purposes=[purpose],recipients=[recipient],obligations=['source'],expires_at=200,source_ref='synthetic')
    delivery = memory.deliver('other-context',purpose=purpose,recipient=recipient,expected_generation=memory.generation(),callback=lambda _: None)
    with pytest.raises(PermissionError):
        gateway.bind(delivery_id=delivery['delivery_id'],envelope=envelope,claim_id=claim.claim_id)
    assert effects(destination) == 0
