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
    memory = ContextMemory(tmp_path / 'context.db', clock=lambda: BASE.timestamp())
    memory.admit(item_id='context', content='Synthetic context', purposes=['refund'], recipients=[envelope.operation.actor],
                 obligations=['source'], expires_at=BASE.timestamp()+100, source_ref='synthetic:évidence')
    delivery = memory.deliver('context', purpose='refund', recipient=envelope.operation.actor, expected_generation=memory.generation(), callback=lambda _: None)
    gateway = ContextBoundExecutor(memory, executor)
    claim = gateway.provision_claim(delivery_id=delivery['delivery_id'], proposal=proposal, decision=decision, now=BASE)
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
        memory.admit(item_id='new', content='new', purposes=['refund'], recipients=[envelope.operation.actor], obligations=['source'], expires_at=BASE.timestamp()+100, source_ref='new')
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
    restored_memory = ContextMemory(tmp_path / 'restored-context.db', clock=lambda: BASE.timestamp())
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
    memory.admit(item_id='other-context',content='synthetic',purposes=[purpose],recipients=[recipient],obligations=['source'],expires_at=BASE.timestamp()+100,source_ref='synthetic')
    delivery = memory.deliver('other-context',purpose=purpose,recipient=recipient,expected_generation=memory.generation(),callback=lambda _: None)
    with pytest.raises(PermissionError):
        gateway.bind(delivery_id=delivery['delivery_id'],envelope=envelope,claim_id=claim.claim_id)
    assert effects(destination) == 0


def test_claim_deadline_is_capped_by_context(case):
    from datetime import datetime, timedelta
    memory, gateway, destination, envelope, claim, binding = case
    assert datetime.fromisoformat(claim.expires_at) == BASE + timedelta(seconds=100)
    assert invoke(case).status == 'executed'


def test_uncapped_claim_cannot_be_bound_or_used_by_older_binding(case):
    import json
    from datetime import timedelta
    memory, gateway, destination, envelope, claim, binding = case
    # Simulate a prior-version persisted claim. Updating every claim commitment
    # is not needed: the wrapper must reject the excessive deadline first.
    with sqlite3.connect(destination.path) as conn:
        row = json.loads(conn.execute('SELECT claim_json FROM execution_claims_v1 WHERE claim_id=?',(claim.claim_id,)).fetchone()[0])
        row['expires_at']=(BASE+timedelta(seconds=200)).isoformat()
        conn.execute('UPDATE execution_claims_v1 SET claim_json=? WHERE claim_id=?',(json.dumps(row),claim.claim_id))
    with memory.connection() as conn:
        delivery_id=conn.execute('SELECT delivery_id FROM context_actions WHERE id=?',(binding,)).fetchone()[0]
    with pytest.raises(PermissionError,match='exceeds context deadline'):
        gateway.bind(delivery_id=delivery_id,envelope=envelope,claim_id=claim.claim_id)
    with pytest.raises(PermissionError,match='exceeds context deadline'):
        invoke(case)
    assert effects(destination)==0


def test_context_expiry_while_waiting_for_destination_prevents_commit(case, monkeypatch):
    from datetime import timedelta
    memory, gateway, destination, envelope, claim, binding = case
    clock=[BASE]
    memory.clock=lambda: clock[0].timestamp()
    destination.clock=lambda: clock[0]
    entered=threading.Event()
    monkeypatch.setattr(destination,'_transaction_stage',lambda stage: entered.set() if stage=='before_begin' else None)
    results, errors=[],[]
    def execute():
        try: results.append(invoke(case))
        except BaseException as exc: errors.append(exc)
    blocker=sqlite3.connect(destination.path,isolation_level=None)
    blocker.execute('BEGIN IMMEDIATE')
    worker=threading.Thread(target=execute)
    worker.start()
    try:
        assert entered.wait(5)
        clock[0]=BASE+timedelta(seconds=100)
    finally:
        blocker.rollback(); blocker.close()
        worker.join(5)
    assert not worker.is_alive() and not errors
    assert results[0].status=='denied'
    assert destination.claim_state(claim.claim_id)=='issued'
    assert effects(destination)==0


def test_fractional_context_deadline_never_rounds_into_future():
    from decimal import Decimal
    from reference_profiles.context_action import ContextBoundExecutor
    value=BASE.timestamp()+0.1234567
    deadline=ContextBoundExecutor.context_deadline({'expires_at':value})
    assert Decimal(str(deadline.timestamp())) <= Decimal(str(value))


def export_case(case):
    _, gateway, _, envelope, claim, binding = case
    return gateway.export_evidence(binding_id=binding, envelope=envelope, claim_id=claim.claim_id)


def verify_case(case, package, **kwargs):
    from reference_profiles.context_evidence import verify_context_evidence
    _, gateway, _, envelope, claim, binding = case
    return verify_context_evidence(package, binding_id=binding,
                                   envelope_digest=gateway.envelope_digest(envelope),
                                   claim_id=claim.claim_id, effect_id=envelope.effect_id, **kwargs)


def test_context_evidence_preserves_outcome_lineage_after_expiry_and_reopen(case):
    import json
    from reference_profiles.context_action import ContextBoundExecutor
    memory, gateway, destination, envelope, claim, binding = case
    assert verify_case(case, export_case(case))['recorded_outcome'] == 'not_started'
    assert invoke(case).status == 'executed'
    memory.clock = lambda: BASE.timestamp() + 101
    assert memory.purge_expired() == ['context']
    reopened = ContextMemory(memory.path, clock=memory.clock)
    package = ContextBoundExecutor(reopened, gateway.executor).export_evidence(
        binding_id=binding, envelope=envelope, claim_id=claim.claim_id)
    verified = verify_case(case, package, expected_digest=package['sha256'])
    assert verified['recorded_outcome'] == 'executed'
    assert verified['checkpoint_matched']
    assert package['payload']['item_status'] == 'expired'
    assert 'Synthetic context' not in json.dumps(package)
    for flag in ('authorizing', 'model_reliance_verified', 'physical_erasure_verified',
                 'independent_custody_verified', 'consumer_chain_qualified', 'production_ready'):
        assert verified[flag] is False
    assert effects(destination) == 1


def test_finished_denial_never_exports_success(case):
    _, _, destination, _, claim, _ = case
    destination.set_grant_status(claim.grant_id, status='revoked')
    assert invoke(case).status == 'denied'
    package = export_case(case)
    assert package['payload']['binding']['state'] == 'finished'
    assert verify_case(case, package)['recorded_outcome'] == 'denied'
    assert effects(destination) == 0


def test_postcommit_evidence_failure_exports_uncertainty_not_success(case, monkeypatch):
    memory, _, destination, _, _, _ = case
    original = memory.event
    def fail(conn, kind, item, detail):
        if kind == 'bound_action_result':
            raise OSError('synthetic evidence failure')
        return original(conn, kind, item, detail)
    monkeypatch.setattr(memory, 'event', fail)
    with pytest.raises(OSError):
        invoke(case)
    assert effects(destination) == 1
    package = export_case(case)
    assert verify_case(case, package)['recorded_outcome'] == 'unknown'
    assert package['payload']['result'] is None
    with pytest.raises(PermissionError):
        invoke(case)


@pytest.mark.parametrize('mutation', [
    'receipt', 'delivery', 'generation', 'claim', 'effect', 'false_success',
    'premature_success', 'truncated_outcome', 'duplicate_outcome', 'authority',
    'model_reliance', 'physical_erasure', 'incomplete_legacy_outcome',
])
def test_export_negative_controls_reject_rehashed_false_claims(case, mutation):
    from reference_profiles.context_evidence import digest
    assert invoke(case).status == 'executed'
    package = export_case(case)
    p = package['payload']
    if mutation == 'receipt': p['receipt']['content_sha256'] = '0' * 64
    elif mutation == 'delivery': p['delivery']['id'] = 'substituted'
    elif mutation == 'generation': p['delivery']['generation'] += 1
    elif mutation == 'claim': p['binding']['claim_id'] = 'another-claim'
    elif mutation == 'effect': p['result']['effect_id'] = 'another-effect'
    elif mutation == 'false_success': p['result']['observed_state'] = 'unknown'
    elif mutation == 'premature_success': p['binding']['state'] = 'started'
    elif mutation == 'truncated_outcome': p['result'] = None; p['result_count'] = 0
    elif mutation == 'duplicate_outcome': p['result_count'] = 2
    elif mutation == 'authority': p['limits']['authorizing'] = True
    elif mutation == 'model_reliance': p['limits']['model_reliance_verified'] = True
    elif mutation == 'physical_erasure': p['limits']['physical_erasure_verified'] = True
    elif mutation == 'incomplete_legacy_outcome': del p['result']['observed_state']
    # Rehash to isolate semantic checks from the package checksum check.
    package['sha256'] = digest(p)
    with pytest.raises(ValueError):
        verify_case(case, package)


def test_external_checkpoint_detects_coherent_truncation(case):
    from reference_profiles.context_evidence import digest
    assert invoke(case).status == 'executed'
    package = export_case(case)
    checkpoint = package['sha256']
    package['payload']['binding']['state'] = 'started'
    package['payload']['result'] = None
    package['payload']['result_count'] = 0
    package['sha256'] = digest(package['payload'])
    # A self-consistent replacement is not independently authenticated.
    assert verify_case(case, package)['recorded_outcome'] == 'unknown'
    with pytest.raises(ValueError):
        verify_case(case, package, expected_digest=checkpoint)


def test_export_rejects_substitution_in_retained_store(case):
    memory, _, _, _, _, _ = case
    with memory.connection() as conn:
        conn.execute("UPDATE deliveries SET generation=generation+1")
    with pytest.raises(ValueError, match='lineage'):
        export_case(case)


@pytest.mark.skipif(sys.platform != 'linux', reason='qualified same-host Linux process boundary')
def test_competing_processes_use_actual_context_execution_route(case):
    import multiprocessing
    ctx = multiprocessing.get_context('fork')
    ready, start, results = ctx.Queue(), ctx.Event(), ctx.Queue()
    def run():
        ready.put(True)
        if not start.wait(10):
            results.put('start_timeout')
            return
        try:
            results.put(invoke(case).status)
        except PermissionError:
            results.put('binding_refused')
        except Exception as exc:
            results.put(type(exc).__name__)
    workers = [ctx.Process(target=run) for _ in range(2)]
    try:
        for worker in workers: worker.start()
        assert ready.get(timeout=10) and ready.get(timeout=10)
        start.set()
        outcomes = sorted(results.get(timeout=15) for _ in workers)
        for worker in workers:
            worker.join(10)
            assert worker.exitcode == 0
        assert outcomes == ['binding_refused', 'executed']
        assert effects(case[2]) == 1
        assert verify_case(case, export_case(case))['recorded_outcome'] == 'executed'
    finally:
        for worker in workers:
            if worker.is_alive(): worker.terminate()
            worker.join(5)
        ready.close(); results.close()


@pytest.mark.skipif(sys.platform != 'linux', reason='qualified same-host Linux process boundary')
def test_crash_after_started_marker_prevents_restart_dispatch(case):
    import multiprocessing
    from reference_profiles.context_action import ContextBoundExecutor
    memory, gateway, destination, envelope, claim, binding = case
    def crash():
        gateway.executor.execute = lambda **kwargs: os._exit(17)
        invoke(case)
    worker = multiprocessing.get_context('fork').Process(target=crash)
    try:
        worker.start(); worker.join(10)
        assert worker.exitcode == 17
    finally:
        if worker.is_alive(): worker.terminate()
        worker.join(5)
    reopened = ContextMemory(memory.path, clock=lambda: BASE.timestamp())
    restarted = ContextBoundExecutor(reopened, gateway.executor)
    with pytest.raises(PermissionError):
        restarted.execute(binding_id=binding, envelope=envelope, claim_id=claim.claim_id)
    assert effects(destination) == 0
    assert verify_case(case, export_case(case))['recorded_outcome'] == 'unknown'
    assert restarted.reconcile(binding_id=binding, envelope=envelope, claim_id=claim.claim_id).observed_state in ('absent', 'unknown')
