"""Worker 19: qualify authority changes after Control Plane revalidation and before effect commit.

The tests use exact accepted hub pins supplied by the runner. Fault injection is only
an event barrier around the real Moltbot Safe DurableRefundDestination.commit().
It does not authorize, deny, commit, deduplicate, or reconcile effects.
"""
from __future__ import annotations

import dataclasses
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Event, Thread

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".authority-effect-work"
NOW = datetime(2026, 8, 8, 1, 0, 0, tzinfo=timezone.utc)
GRANT_EXPIRED = datetime(2026, 8, 9, 0, 0, 1, tzinfo=timezone.utc)
EVIDENCE_EXPIRED = NOW + timedelta(seconds=301)

EXPECTED_PINS = {
    "action_manifest": "46c950bed37fe3812000895430bc0312d29e37ce",
    "control_plane": "248d899634d9db3518e831bc7ab568a48733f825",
    "gax_imx_transport": "9984d9011568ccdf3d562fa9760ad41368947b34",
    "moltbot_safe": "177354e959cc78c59c1a776f018cfbfbf28c927b",
    "replay_bundle": "043830b56595cecddfa65c064afd1c0b95e64792",
}


def _json(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=False)
    return value


def _rows(destination):
    with sqlite3.connect(destination.path) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute("SELECT * FROM effects ORDER BY effect_id")]


@pytest.fixture(scope="module")
def pins():
    import subprocess

    observed = {}
    for name, expected in EXPECTED_PINS.items():
        checkout = WORK / name
        head = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
        ).strip()
        assert head == expected, f"{name}: expected {expected}, got {head}"
        observed[name] = head
    return observed


def _setup(tmp_path):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import (
        load_executor_runtime,
        runtime_proposal_model,
    )
    from experiments.odex_gax_imx_reference.synthetic_fixture import (
        build_synthetic_resolver,
        synthetic_observation_policy,
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
    resolver = build_synthetic_resolver(proposal, now=NOW)
    destination = runtime["DurableRefundDestination"](tmp_path / "destination")
    workflow = cp.BoundedAuthorizationWorkflow(
        manifest=manifest,
        resolver=resolver,
        destination=destination,
        records=cp.BoundedRecordStore(tmp_path / "control-plane.json", "worker19"),
        observation_policy=synthetic_observation_policy(),
    )
    return runtime, cp, manifest, proposal, resolver, destination, workflow


def _authorize(runtime, proposal, resolver, workflow):
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_refund_policy

    cp = runtime["cp"]
    context = resolver.contexts[proposal.authority_context_ref]
    approval_ref = context["grant"]["approval_refs"][0]
    resolver.approvals[approval_ref] = resolver.approvals[approval_ref].model_copy(
        update={
            "proposal_commitment": cp.commitment(
                proposal.model_dump(mode="json", exclude_none=False)
            )
        }
    )
    decision = workflow.decide(proposal, now=NOW)
    assert decision.result == "authorized", decision.reasons
    binding = decision.binding
    values = proposal.model_dump(mode="json", exclude_none=False)
    values.update(
        {
            "institution_id": context["institution"]["institution_id"],
            "authority_domain": context["institution"]["authority_domain"],
            "authority_context_id": proposal.authority_context_ref,
            "proposal_commitment": binding.proposal_commitment,
            "grant_id": binding.grant_id,
            "grant_revision": binding.grant_revision,
            "effective_max_effects": binding.effective_max_effects,
            "requested_permissions": tuple(proposal.requested_permissions),
        }
    )
    operation = runtime["ExecutionOperation"](
        **{
            field.name: values[field.name]
            for field in dataclasses.fields(runtime["ExecutionOperation"])
        }
    )
    envelope = runtime["ExecutionEnvelope"](
        version="0.2.0",
        decision_id=decision.decision_id,
        effect_id=decision.effect_id,
        operation=operation,
    )
    policy = synthetic_refund_policy(operation)
    executor = runtime["PinnedControlPlaneExecutor"](
        workflow=workflow,
        destination=workflow.destination,
        policy=policy,
        observation_clock=lambda: NOW,
    )
    return decision, envelope, executor


def _mutate_or_advance(resolver, proposal, scenario_id):
    context = resolver.contexts[proposal.authority_context_ref]
    grant = context["grant"]
    if scenario_id == "grant-revocation-after-validation":
        grant_id = grant["grant_id"]
        resolver.statuses[grant_id] = resolver.statuses[grant_id].model_copy(
            update={"status": "revoked", "observed_at": NOW.isoformat()}
        )
        return NOW, "grant_not_active"
    if scenario_id == "approval-revocation-after-validation":
        ref = grant["approval_refs"][0]
        resolver.approvals[ref] = resolver.approvals[ref].model_copy(
            update={"status": "revoked", "observed_at": NOW.isoformat()}
        )
        return NOW, "approval_not_active"
    if scenario_id == "policy-version-change-after-validation":
        ref = grant["policy_versions"][0]["ref"]
        resolver.policies[ref] = resolver.policies[ref].model_copy(
            update={"version": "2.0", "observed_at": NOW.isoformat()}
        )
        return NOW, "policy_stale_or_changed"
    if scenario_id == "required-evidence-invalid-after-validation":
        obligation = context["requirement"]["evidence"][0]["obligation_id"]
        resolver.evidence[obligation] = resolver.evidence[obligation].model_copy(
            update={"state": "stale", "observed_at": NOW.isoformat()}
        )
        return NOW, "required_evidence_not_current"
    if scenario_id == "grant-expiry-after-validation":
        return GRANT_EXPIRED, "grant_outside_validity"
    if scenario_id == "evidence-expiry-after-validation":
        return EVIDENCE_EXPIRED, "required_evidence_stale_or_future"
    if scenario_id == "unchanged-authority-control":
        return NOW, None
    raise AssertionError(f"unknown scenario: {scenario_id}")


def _current_assessment(cp, manifest, resolver, proposal, destination, tmp_path, now, scenario_id):
    assessment = cp.BoundedAuthorizationWorkflow(
        manifest=manifest,
        resolver=resolver,
        destination=destination,
        records=cp.BoundedRecordStore(
            tmp_path / f"assessment-{scenario_id}.json", f"assessment-{scenario_id}"
        ),
        observation_policy=cp.ObservationPolicy(max_age_seconds=60),
    ).decide(proposal, now=now)
    return assessment


def _write_evidence(payload):
    out = Path(os.environ["AUTHORITY_EFFECT_RESULTS_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{payload['scenario_id']}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


SCENARIOS = [
    "grant-revocation-after-validation",
    "approval-revocation-after-validation",
    "policy-version-change-after-validation",
    "required-evidence-invalid-after-validation",
    "grant-expiry-after-validation",
    "evidence-expiry-after-validation",
    "unchanged-authority-control",
]


@pytest.mark.parametrize("scenario_id", SCENARIOS, ids=SCENARIOS)
def test_authority_effect_race(tmp_path, monkeypatch, pins, scenario_id):
    runtime, cp, manifest, proposal, resolver, destination, workflow = _setup(tmp_path)
    decision, envelope, executor = _authorize(
        runtime, proposal, resolver, workflow
    )

    reached_commit = Event()
    release_commit = Event()
    original_commit = destination.commit

    def gated_commit(snapshot, *, simulate=None):
        reached_commit.set()
        if not release_commit.wait(10):
            raise TimeoutError("qualification barrier was not released")
        return original_commit(snapshot, simulate=simulate)

    monkeypatch.setattr(destination, "commit", gated_commit)

    outcome = {}
    failure = {}

    def execute():
        try:
            outcome["result"] = executor.execute(
                envelope=envelope,
                proposal=proposal,
                decision=decision,
                now=NOW,
            )
        except BaseException as exc:
            failure["exception"] = repr(exc)

    worker = Thread(target=execute, daemon=True)
    worker.start()
    assert reached_commit.wait(10), "execution did not reach the pre-commit barrier"

    before = _rows(destination)
    assert before == [], "effect committed before the barrier mutation"

    assessment_now, expected_reason = _mutate_or_advance(
        resolver, proposal, scenario_id
    )
    assessment = _current_assessment(
        cp,
        manifest,
        resolver,
        proposal,
        destination,
        tmp_path,
        assessment_now,
        scenario_id,
    )

    if expected_reason is None:
        assert assessment.result == "authorized", assessment.reasons
    else:
        assert assessment.result == "hold", assessment.reasons
        assert expected_reason in assessment.reasons, assessment.reasons

    release_commit.set()
    worker.join(10)
    assert not worker.is_alive(), "execution thread did not complete"
    assert "exception" not in failure, failure

    result = outcome["result"]
    after = _rows(destination)
    effect_committed = (
        len(after) == 1
        and after[0]["effect_id"] == decision.effect_id
        and after[0]["state"] == "applied"
    )
    assert effect_committed, after
    assert result.status in {"executed", "reconciled"}
    assert result.observed_state == "applied"

    changed = expected_reason is not None
    classification = (
        "stronger proposed guarantee not met"
        if changed
        else "existing contract supported"
    )
    payload = {
        "schema_version": "1.0",
        "scenario_id": scenario_id,
        "repetition": int(os.environ.get("AUTHORITY_EFFECT_REPETITION", "0")),
        "component_pins": pins,
        "execution_status": "executed",
        "classification": classification,
        "research_profile_status": "proposed external profile; not adopted Cognous requirement",
        "barrier": {
            "location": "Moltbot Safe DurableRefundDestination.commit entry, before SQLite BEGIN IMMEDIATE",
            "coordination": "threading.Event only; no timing sleep",
            "effect_rows_before_release": before,
        },
        "original_validation_time": NOW.isoformat(),
        "current_assessment_time": assessment_now.isoformat(),
        "current_assessment": _json(assessment),
        "expected_current_reason": expected_reason,
        "original_decision": _json(decision),
        "execution_result": _json(result),
        "destination_effects_after_release": after,
        "observed_property": (
            "current authority remained valid and the effect committed"
            if not changed
            else "current public assessment no longer authorized the proposal, but the already-revalidated execution continued through the real destination commit"
        ),
        "cognous_contract_interpretation": (
            "control case supports the accepted revalidation-and-effect path"
            if not changed
            else "characterization of the validation-to-commit gap; not labeled a violation of an adopted atomic authority/effect guarantee"
        ),
        "research_comparison": (
            "The proposed EBL-Core property requires validation, lifecycle consumption, and protected effect to share a defined linearized ordering. This accepted Cognous path does not provide that stronger ordering for resolver changes introduced after revalidation."
            if changed
            else "No authority change occurred between validation and commit."
        ),
    }
    _write_evidence(payload)
