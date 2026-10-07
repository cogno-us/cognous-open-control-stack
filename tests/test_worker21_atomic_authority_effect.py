"""Worker 21 cross-repository qualification of the proposed local atomic profile."""
from __future__ import annotations

import dataclasses
import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".worker21-work"
BASE = datetime(2026, 8, 8, 1, 0, tzinfo=timezone.utc)


class MutableClock:
    def __init__(self, value):
        self.value = value
    def __call__(self):
        return self.value


class BarrierDestinationMixin:
    def install_barrier(self, stage):
        self._barrier_stage = stage
        self._barrier_entered = threading.Event()
        self._barrier_release = threading.Event()

    def _transaction_stage(self, stage):
        if getattr(self, "_barrier_stage", None) == stage:
            self._barrier_entered.set()
            assert self._barrier_release.wait(10)


def effect_rows(destination):
    with sqlite3.connect(destination.path) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute("SELECT * FROM effects ORDER BY effect_id")]


def setup_case(tmp_path, *, barrier=False, before_provision=None):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import (
        load_executor_runtime, runtime_proposal_model,
    )
    from experiments.odex_gax_imx_reference.synthetic_fixture import (
        build_synthetic_resolver, synthetic_observation_policy, synthetic_refund_policy,
    )
    from engine.local_authority_effect import (
        AtomicAuthorityEffectDestination, AtomicLocalControlPlaneExecutor,
    )

    runtime = load_executor_runtime()
    cp = runtime["cp"]
    manifest = json.loads(
        (WORK / "action_manifest/examples/refund_integration_v1_1.manifest.json").read_text()
    )
    seed = json.loads(
        (WORK / "replay_bundle/examples/bounded_success_reconstruction_v0_2.json").read_text()
    )
    proposal = runtime_proposal_model(seed)
    resolver = build_synthetic_resolver(proposal, now=BASE)
    workflow = cp.BoundedAuthorizationWorkflow(
        manifest=manifest,
        resolver=resolver,
        destination=cp.LocalRefundDestination(tmp_path / "control-plane-destination.json"),
        records=cp.BoundedRecordStore(tmp_path / "control-plane.json", "worker21"),
        observation_policy=synthetic_observation_policy(),
    )
    decision = workflow.decide(proposal, now=BASE)
    assert decision.result == "authorized", decision.reasons

    context = resolver.contexts[proposal.authority_context_ref]
    values = proposal.model_dump(mode="json", exclude_none=False)
    values.update({
        "institution_id": context["institution"]["institution_id"],
        "authority_domain": context["institution"]["authority_domain"],
        "authority_context_id": proposal.authority_context_ref,
        "proposal_commitment": decision.binding.proposal_commitment,
        "grant_id": decision.binding.grant_id,
        "grant_revision": decision.binding.grant_revision,
        "effective_max_effects": decision.binding.effective_max_effects,
        "requested_permissions": tuple(proposal.requested_permissions),
    })
    operation = runtime["ExecutionOperation"](**{
        f.name: values[f.name] for f in dataclasses.fields(runtime["ExecutionOperation"])
    })
    envelope = runtime["ExecutionEnvelope"](
        version="0.2.0",
        decision_id=decision.decision_id,
        effect_id=decision.effect_id,
        operation=operation,
    )

    clock = MutableClock(BASE)
    if barrier:
        class BarrierDestination(BarrierDestinationMixin, AtomicAuthorityEffectDestination):
            pass
        destination = BarrierDestination(tmp_path / "atomic", clock=clock)
        destination.install_barrier("after_begin")
    else:
        destination = AtomicAuthorityEffectDestination(tmp_path / "atomic", clock=clock)

    executor = AtomicLocalControlPlaneExecutor(
        workflow=workflow,
        destination=destination,
        policy=synthetic_refund_policy(operation),
    )
    if before_provision is not None:
        before_provision(resolver)
    claim = executor.provision_claim(
        proposal=proposal,
        decision=decision,
        now=BASE,
        claim_id="worker21-claim",
    )
    return clock, proposal, decision, envelope, destination, executor, claim



def _inject_issuance_interleaving(kind):
    def install(resolver):
        original = resolver.authority_effect_snapshot
        injected = {"done": False}

        def snapshot(ref):
            if not injected["done"]:
                injected["done"] = True
                context = resolver.contexts[ref]
                grant = context["grant"]
                if kind == "approval":
                    approval_ref = grant["approval_refs"][0]
                    resolver.approvals[approval_ref] = resolver.approvals[approval_ref].model_copy(
                        update={"status": "revoked"}
                    )
                elif kind == "policy":
                    policy_ref = grant["policy_versions"][0]["ref"]
                    resolver.policies[policy_ref] = resolver.policies[policy_ref].model_copy(
                        update={"status": "superseded"}
                    )
                else:
                    raise AssertionError(kind)
            return original(ref)

        resolver.authority_effect_snapshot = snapshot
    return install


@pytest.mark.parametrize(
    ("kind", "message"),
    [
        ("approval", "approval projection is not active"),
        ("policy", "policy projection is not active"),
    ],
)
def test_actual_claim_provisioning_rejects_post_resolve_invalidation(tmp_path, kind, message):
    from engine.local_authority_effect import AtomicAuthorityEffectDestination

    with pytest.raises(PermissionError, match=message):
        setup_case(
            tmp_path,
            before_provision=_inject_issuance_interleaving(kind),
        )

    # The invalid snapshot must never cross the handoff into the authoritative store.
    reopened = AtomicAuthorityEffectDestination(tmp_path / "atomic", clock=lambda: BASE)
    assert reopened.claim_state("worker21-claim") is None
    assert effect_rows(reopened) == []


def mutate(destination, claim, kind):
    if kind == "grant":
        destination.set_grant_status(claim.grant_id, status="revoked")
    elif kind == "approval":
        destination.set_approval_status(claim.approval_state[0].approval_ref, status="revoked")
    elif kind == "policy":
        destination.set_policy_state(claim.policy_state[0].ref, version="worker21-changed")
    elif kind == "evidence":
        target = next(item for item in claim.evidence_state if item.required)
        destination.set_evidence_state(target.obligation_id, state="stale")
    else:
        raise AssertionError(kind)


@pytest.mark.parametrize("kind", ["grant", "approval", "policy", "evidence"])
def test_invalidation_transaction_first_prevents_effect(tmp_path, kind):
    _, _, _, envelope, destination, executor, claim = setup_case(tmp_path)
    mutate(destination, claim, kind)
    result = executor.execute(envelope=envelope, claim_id=claim.claim_id)
    assert result.status == "denied"
    assert destination.claim_state(claim.claim_id) == "issued"
    assert effect_rows(destination) == []


@pytest.mark.parametrize("kind", ["grant", "approval", "policy", "evidence"])
def test_effect_transaction_first_preserves_effect_then_invalidation(tmp_path, kind):
    _, _, _, envelope, destination, executor, claim = setup_case(tmp_path, barrier=True)
    result_box = {}
    error_box = {}
    writer_done = threading.Event()

    def run_effect():
        try:
            result_box["value"] = executor.execute(envelope=envelope, claim_id=claim.claim_id)
        except BaseException as exc:
            error_box["effect"] = repr(exc)

    def run_writer():
        try:
            mutate(destination, claim, kind)
        except BaseException as exc:
            error_box["writer"] = repr(exc)
        finally:
            writer_done.set()

    effect = threading.Thread(target=run_effect, daemon=True)
    effect.start()
    assert destination._barrier_entered.wait(10)

    writer = threading.Thread(target=run_writer, daemon=True)
    writer.start()

    # The execution transaction already owns the SQLite write boundary.
    destination._barrier_release.set()
    effect.join(10)
    writer.join(10)
    assert not effect.is_alive() and not writer.is_alive()
    assert writer_done.is_set()
    assert not error_box, error_box
    assert result_box["value"].status == "executed"
    assert destination.claim_state(claim.claim_id) == "consumed"
    assert len(effect_rows(destination)) == 1


def test_grant_expiry_first_prevents_effect(tmp_path):
    clock, _, _, envelope, destination, executor, claim = setup_case(tmp_path)
    clock.value = datetime.fromisoformat(claim.expires_at) + timedelta(microseconds=1)
    result = executor.execute(envelope=envelope, claim_id=claim.claim_id)
    assert result.status == "denied"
    assert effect_rows(destination) == []


def test_evidence_expiry_first_prevents_effect(tmp_path):
    clock, _, _, envelope, destination, executor, claim = setup_case(tmp_path)
    evidence = next(item for item in claim.evidence_state if item.required)
    clock.value = datetime.fromisoformat(evidence.observed_at) + timedelta(
        seconds=evidence.max_age_seconds + 1
    )
    result = executor.execute(envelope=envelope, claim_id=claim.claim_id)
    assert result.status == "denied"
    assert effect_rows(destination) == []


def test_actual_provisioned_claim_reconciliation_is_exactly_bound(tmp_path):
    _, _, _, envelope, destination, executor, claim = setup_case(tmp_path)
    result = executor.execute(envelope=envelope, claim_id=claim.claim_id)
    assert result.status == "executed"

    with sqlite3.connect(destination.path) as conn:
        conn.execute(
            """INSERT INTO effects
            (effect_id,operation_digest,grant_id,target,amount,unit,payload_json,state)
            VALUES(?,?,?,?,?,?,?,?)""",
            (
                "unrelated-effect",
                "sha256:" + "b" * 64,
                "unrelated-grant",
                "urn:cognous:synthetic-account:other",
                1.0,
                "USD",
                '{"refund_reason":"other"}',
                "applied",
            ),
        )

    wrong_effect = destination.reconcile_claim(claim.claim_id, "unrelated-effect")
    assert wrong_effect["status"] == "hold"
    assert wrong_effect["reason"] == "claim_effect_binding_mismatch"

    own = destination.reconcile_claim(claim.claim_id, envelope.effect_id)
    assert own["status"] == "applied"

    with sqlite3.connect(destination.path) as conn:
        conn.execute(
            "UPDATE effects SET operation_digest=? WHERE effect_id=?",
            ("sha256:" + "c" * 64, envelope.effect_id),
        )
    wrong_operation = destination.reconcile_claim(claim.claim_id, envelope.effect_id)
    assert wrong_operation["status"] == "hold"
    assert wrong_operation["reason"] == "retained_effect_operation_binding_mismatch"


@pytest.mark.parametrize("mutation", ["decision_id", "target", "amount", "payload"])
def test_integrated_recovery_rejects_substituted_envelope_with_original_effect_id(tmp_path, mutation):
    _, _, _, envelope, destination, executor, claim = setup_case(tmp_path)
    executed = executor.execute(envelope=envelope, claim_id=claim.claim_id)
    assert executed.status == "executed"

    if mutation == "decision_id":
        substituted = dataclasses.replace(
            envelope, decision_id="decision-substituted"
        )
        expected = "claim_decision_binding_mismatch"
    elif mutation == "target":
        substituted = dataclasses.replace(
            envelope,
            operation=dataclasses.replace(
                envelope.operation,
                target="urn:cognous:synthetic-account:substituted",
            ),
        )
        expected = "claim_operation_binding_mismatch"
    elif mutation == "amount":
        substituted = dataclasses.replace(
            envelope,
            operation=dataclasses.replace(envelope.operation, amount=51.0),
        )
        expected = "claim_operation_binding_mismatch"
    else:
        from engine.safe_executor import commitment
        payload = {"refund_reason": "substituted"}
        substituted = dataclasses.replace(
            envelope,
            operation=dataclasses.replace(
                envelope.operation,
                payload=payload,
                payload_commitment=commitment(payload),
            ),
        )
        expected = "claim_operation_binding_mismatch"

    recovered = executor.reconcile(claim_id=claim.claim_id, envelope=substituted)
    assert recovered.status == "observed"
    assert recovered.observed_state == "unknown"
    assert recovered.observation["status"] == "hold"
    assert recovered.observation["reason"] == expected
    assert recovered.observation["retry_eligible"] is False


def test_integrated_recovery_preserves_exact_original_envelope(tmp_path):
    _, _, _, envelope, destination, executor, claim = setup_case(tmp_path)
    executed = executor.execute(envelope=envelope, claim_id=claim.claim_id)
    assert executed.status == "executed"

    recovered = executor.reconcile(claim_id=claim.claim_id, envelope=envelope)
    assert recovered.status == "observed"
    assert recovered.observed_state == "applied"
    assert recovered.observation["status"] == "applied"
    assert recovered.observation["effect_id"] == envelope.effect_id


def test_unchanged_authority_control(tmp_path):
    _, _, _, envelope, destination, executor, claim = setup_case(tmp_path)
    result = executor.execute(envelope=envelope, claim_id=claim.claim_id)
    assert result.status == "executed"
    assert destination.claim_state(claim.claim_id) == "consumed"
    assert len(effect_rows(destination)) == 1
