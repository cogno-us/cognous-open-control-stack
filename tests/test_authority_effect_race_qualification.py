"""Worker 19: deterministic authority-to-effect race qualification.

This is qualification, not a runtime repair.  It deliberately pauses the accepted
Moltbot Safe destination immediately before its real SQLite effect commit, after
the accepted Control Plane has completed execution-time authority resolution.
Authority then changes deterministically, a separate effect-free assessment
records what current authorization would say, and only then is the original
commit released.

An effect after the mutation is NOT labeled an existing-contract violation merely
from timestamps.  The evidence records invocation/completion order and treats the
paper's atomic/linearized Redemption rule as a stronger proposed property unless
the accepted Cognous contract independently states it.
"""
from __future__ import annotations

import copy
import dataclasses
import json
import os
import sqlite3
import subprocess
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".authority-effect-race-work"
BASE = datetime(2026, 8, 8, 1, 0, 0, tzinfo=timezone.utc)
WAIT = 10
HUB_BASELINE = "5a9ae5de4d445febe1105087a8b650e33f00eee3"
SOURCE = {
    "title": "From Intent to Execution Grant: An Execution-Boundary Conformance Profile for High-Risk AI Actions",
    "locator": "sections 3.3.7, 3.3.8, 4.7 and 6.4",
    "status": "proposed external profile; not an adopted Cognous requirement",
    "proposed_property": (
        "validation, grant/lifecycle consumption, and protected effect share one "
        "logical linearization point with respect to decision-relevant state"
    ),
}


def as_json(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=False)
    return copy.deepcopy(value)


def sqlite_rows(destination, table):
    with sqlite3.connect(destination.path) as con:
        con.row_factory = sqlite3.Row
        return [dict(r) for r in con.execute(f"SELECT * FROM {table} ORDER BY rowid")]


class ResolverProbe:
    """Transparent resolver proxy that counts all authority observations."""

    METHODS = (
        "authority_context", "grant_status", "identity_status", "issuer_mandate",
        "approval_status", "policy_status", "conflict_status", "evidence_status",
        "role_mapping",
    )

    def __init__(self, inner):
        self.inner = inner
        self.calls = []
        self._lock = threading.Lock()

    @property
    def authenticated(self):
        return self.inner.authenticated

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def _call(self, name, *args):
        with self._lock:
            self.calls.append({"index": len(self.calls) + 1, "method": name, "args": list(args)})
        return getattr(self.inner, name)(*args)

    def authority_context(self, ref): return self._call("authority_context", ref)
    def grant_status(self, grant_id): return self._call("grant_status", grant_id)
    def identity_status(self, acting_identity, principal): return self._call("identity_status", acting_identity, principal)
    def issuer_mandate(self, issuer, issuer_role): return self._call("issuer_mandate", issuer, issuer_role)
    def approval_status(self, approval_ref): return self._call("approval_status", approval_ref)
    def policy_status(self, ref): return self._call("policy_status", ref)
    def conflict_status(self, requirement_id): return self._call("conflict_status", requirement_id)
    def evidence_status(self, obligation_id): return self._call("evidence_status", obligation_id)
    def role_mapping(self, institution_id): return self._call("role_mapping", institution_id)


class OrderedLog:
    def __init__(self):
        self.items = []
        self._lock = threading.Lock()

    def add(self, event, **fields):
        with self._lock:
            self.items.append({"sequence": len(self.items) + 1, "event": event, **fields})


@pytest.fixture(scope="module")
def pins():
    lock = json.loads((ROOT / "component-lock.json").read_text())
    expected = {
        "action_manifest": lock["components"]["action_manifest"]["sha"],
        "control_plane": lock["components"]["control_plane"]["sha"],
        "moltbot_safe": lock["components"]["moltbot_safe"]["core_interop_sha"],
        "replay_bundle": lock["components"]["replay_bundle"]["sha"],
        "gax_imx_transport": lock["components"]["gax_imx_transport"]["sha"],
    }
    actual = {}
    for name, sha in expected.items():
        got = subprocess.check_output(
            ["git", "-C", str(WORK / name), "rev-parse", "HEAD"], text=True
        ).strip()
        assert got == sha, f"{name}: expected {sha}, got {got}"
        actual[name] = got
    return {"hub": HUB_BASELINE, "components": actual}


def setup_case(tmp_path):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import (
        load_executor_runtime, runtime_proposal_model,
    )
    from experiments.odex_gax_imx_reference.synthetic_fixture import (
        build_synthetic_resolver, synthetic_observation_policy, synthetic_refund_policy,
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
    inner = build_synthetic_resolver(proposal, now=BASE)

    # Bind the approval to this exact proposal before the initial decision.
    approval_ref = inner.contexts[proposal.authority_context_ref]["grant"]["approval_refs"][0]
    inner.approvals[approval_ref] = inner.approvals[approval_ref].model_copy(update={
        "proposal_commitment": cp.commitment(
            proposal.model_dump(mode="json", exclude_none=False)
        )
    })
    resolver = ResolverProbe(inner)
    destination = runtime["DurableRefundDestination"](tmp_path / "destination")
    workflow = cp.BoundedAuthorizationWorkflow(
        manifest=manifest,
        resolver=resolver,
        destination=destination,
        records=cp.BoundedRecordStore(tmp_path / "control-plane.json", proposal.run_id),
        observation_policy=synthetic_observation_policy(),
    )
    decision = workflow.decide(proposal, now=BASE)
    assert decision.result == "authorized", decision.reasons

    context = inner.contexts[proposal.authority_context_ref]
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
    policy = dataclasses.replace(
        synthetic_refund_policy(operation),
        max_effects=decision.binding.effective_max_effects,
    )
    executor = runtime["PinnedControlPlaneExecutor"](
        workflow=workflow,
        destination=destination,
        policy=policy,
        observation_clock=lambda: BASE,
    )
    return runtime, manifest, proposal, inner, resolver, destination, workflow, decision, envelope, executor


def authority_snapshot(inner):
    groups = ("statuses", "identities", "mandates", "approvals", "policies", "conflicts", "evidence")
    return {
        "contexts": copy.deepcopy(inner.contexts),
        **{
            name: {k: as_json(v) for k, v in getattr(inner, name).items()}
            for name in groups
        },
    }


def refresh_unrelated(inner, at, *, exclude=()):
    for group in ("statuses", "identities", "mandates", "approvals", "policies", "conflicts", "evidence"):
        if group in exclude:
            continue
        values = getattr(inner, group)
        for key, value in list(values.items()):
            values[key] = value.model_copy(update={"observed_at": at.isoformat()})


def mutate(inner, scenario):
    """Apply exactly one decision-relevant mutation and return assessment time."""
    if scenario == "grant-revocation-after-validation":
        at = BASE + timedelta(seconds=1)
        values = inner.statuses
        key = next(iter(values))
        values[key] = values[key].model_copy(update={"status": "revoked", "observed_at": at.isoformat()})
        return at, "grant_not_active"

    if scenario == "approval-revocation-after-validation":
        at = BASE + timedelta(seconds=1)
        values = inner.approvals
        key = next(iter(values))
        values[key] = values[key].model_copy(update={"status": "revoked", "observed_at": at.isoformat()})
        return at, "approval_not_active"

    if scenario == "policy-version-change-after-validation":
        at = BASE + timedelta(seconds=1)
        values = inner.policies
        key = next(iter(values))
        values[key] = values[key].model_copy(update={
            "version": "worker19-changed-policy-version",
            "observed_at": at.isoformat(),
        })
        return at, "policy_stale_or_changed"

    if scenario == "required-evidence-invalid-after-validation":
        at = BASE + timedelta(seconds=1)
        values = inner.evidence
        key = next(iter(values))
        values[key] = values[key].model_copy(update={"state": "stale", "observed_at": at.isoformat()})
        return at, "required_evidence_not_current"

    if scenario == "grant-expiry-after-validation":
        context = inner.contexts[next(iter(inner.contexts))]
        expires = datetime.fromisoformat(context["grant"]["expires_at"].replace("Z", "+00:00"))
        at = expires + timedelta(seconds=1)
        refresh_unrelated(inner, at)
        return at, "grant_outside_validity"

    if scenario == "evidence-expiry-after-validation":
        # Advance trusted evaluation time while retaining the required evidence's
        # original observation time. Refresh unrelated mutable status records so
        # this scenario isolates evidence freshness rather than generic staleness.
        required = inner.contexts[next(iter(inner.contexts))]["requirement"]["evidence"]
        max_age = min(int(x["max_age_seconds"]) for x in required if x.get("required"))
        at = BASE + timedelta(seconds=max_age + 1)
        refresh_unrelated(inner, at, exclude=("evidence",))
        return at, "required_evidence_stale_or_future"

    if scenario == "unchanged-authority-control":
        return BASE, None

    raise AssertionError(scenario)


def assess_current(runtime, manifest, proposal, resolver, tmp_path, at):
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_observation_policy
    cp = runtime["cp"]
    assessment = cp.BoundedAuthorizationWorkflow(
        manifest=manifest,
        resolver=resolver,
        destination=cp.LocalRefundDestination(tmp_path / "assessment-destination.json"),
        records=cp.BoundedRecordStore(tmp_path / "assessment-control-plane.json", proposal.run_id),
        observation_policy=synthetic_observation_policy(),
    )
    return assessment.decide(proposal, now=at)


CASES = [
    "grant-revocation-after-validation",
    "approval-revocation-after-validation",
    "policy-version-change-after-validation",
    "required-evidence-invalid-after-validation",
    "grant-expiry-after-validation",
    "evidence-expiry-after-validation",
    "unchanged-authority-control",
]


@pytest.mark.parametrize("scenario", CASES)
def test_authority_effect_race(tmp_path, monkeypatch, pins, scenario):
    (
        runtime, manifest, proposal, inner, resolver, destination, workflow,
        decision, envelope, executor,
    ) = setup_case(tmp_path)
    log = OrderedLog()
    commit_entered = threading.Event()
    release_commit = threading.Event()
    finished = threading.Event()
    original_commit = destination.commit
    effect_clock = [BASE]
    result_box = {}
    error_box = {}

    def blocked_commit(snapshot, *, simulate=None):
        log.add(
            "effect_commit_invoked",
            effect_id=snapshot.effect_id,
            authority_resolver_calls=len(resolver.calls),
            controlled_time=effect_clock[0].isoformat(),
        )
        commit_entered.set()
        if not release_commit.wait(WAIT):
            raise TimeoutError("worker19 commit barrier was not released")
        log.add(
            "effect_commit_released",
            effect_id=snapshot.effect_id,
            authority_resolver_calls=len(resolver.calls),
            controlled_time=effect_clock[0].isoformat(),
        )
        value = original_commit(snapshot, simulate=simulate)
        log.add(
            "effect_commit_completed",
            effect_id=snapshot.effect_id,
            controlled_time=effect_clock[0].isoformat(),
        )
        return value

    monkeypatch.setattr(destination, "commit", blocked_commit)

    def execute_original():
        log.add("execution_invoked", decision_id=decision.decision_id, effect_id=decision.effect_id)
        try:
            result_box["result"] = executor.execute(
                envelope=envelope, proposal=proposal, decision=decision, now=BASE
            )
            log.add("execution_completed", status=result_box["result"].status)
        except BaseException as exc:
            error_box["error"] = repr(exc)
            log.add("execution_failed", error=repr(exc))
        finally:
            finished.set()

    before_authority = authority_snapshot(inner)
    before_effects = sqlite_rows(destination, "effects")
    before_attempts = sqlite_rows(destination, "attempts")
    worker = threading.Thread(target=execute_original, daemon=True)
    worker.start()

    assert commit_entered.wait(WAIT), "destination commit boundary was not reached"
    calls_at_commit_entry = len(resolver.calls)
    attempts_at_pause = sqlite_rows(destination, "attempts")
    effects_at_pause = sqlite_rows(destination, "effects")
    log.add(
        "mutation_invoked",
        scenario=scenario,
        effects_at_pause=len(effects_at_pause),
        destination_attempts_at_pause=len(attempts_at_pause),
    )

    assessment_time, expected_reason = mutate(inner, scenario)
    effect_clock[0] = assessment_time
    after_authority = authority_snapshot(inner)
    log.add("mutation_completed", scenario=scenario, controlled_time=assessment_time.isoformat())

    current = assess_current(runtime, manifest, proposal, resolver, tmp_path, assessment_time)
    log.add(
        "current_authority_assessment_completed",
        result=current.result,
        reasons=current.reasons,
    )
    calls_after_assessment = len(resolver.calls)

    # The original in-flight execution is still blocked at the destination commit.
    assert not finished.is_set()
    assert sqlite_rows(destination, "effects") == []
    release_commit.set()
    assert finished.wait(WAIT), "in-flight execution did not finish after barrier release"
    worker.join(timeout=WAIT)

    after_effects = sqlite_rows(destination, "effects")
    after_attempts = sqlite_rows(destination, "attempts")
    result = result_box.get("result")
    post_release_extra_resolver_calls = len(resolver.calls) - calls_after_assessment

    expected_current = (
        current.result == "authorized" and not current.reasons
        if scenario == "unchanged-authority-control"
        else current.result == "hold" and expected_reason in current.reasons
    )
    original_effect_committed = (
        len(after_effects) == 1
        and after_effects[0]["effect_id"] == decision.effect_id
        and after_effects[0]["state"] == "applied"
    )
    no_inflight_reread_after_mutation = post_release_extra_resolver_calls == 0

    if scenario == "unchanged-authority-control":
        classification = "existing contract supported"
        proposed_outcome = "not_adverse_control"
    else:
        classification = "unqualified boundary characterized"
        proposed_outcome = "not_met" if original_effect_committed else "met_or_blocked"

    evidence = {
        "schema_version": "1.0",
        "scenario_id": scenario,
        "repetition": int(os.environ.get("AUTHORITY_EFFECT_RACE_REPETITION", "0")),
        "hub_baseline": HUB_BASELINE,
        "component_pins": pins,
        "research_oracle": SOURCE,
        "classification": classification,
        "existing_contract_violation_reproduced": False,
        "stronger_proposed_guarantee": {
            "status": proposed_outcome,
            "reason": (
                "accepted implementation has no established linearized authority/effect transaction; "
                "the original validated dispatch committed after the decision-relevant mutation"
                if scenario != "unchanged-authority-control" and original_effect_committed
                else "control or no adverse effect"
            ),
        },
        "ordering": log.items,
        "authority_observations": {
            "before": before_authority,
            "after_mutation": after_authority,
            "current_effect_free_assessment": as_json(current),
            "resolver_calls_at_commit_entry": calls_at_commit_entry,
            "resolver_calls_after_assessment": calls_after_assessment,
            "post_release_extra_resolver_calls": post_release_extra_resolver_calls,
        },
        "dispatch_status": {
            "control_plane_decision": as_json(decision),
            "destination_attempts_before": before_attempts,
            "destination_attempts_at_pause": attempts_at_pause,
            "destination_attempts_after": after_attempts,
            "execution_result": as_json(result) if result is not None else None,
            "execution_error": error_box.get("error"),
        },
        "authoritative_destination_state": {
            "effects_before": before_effects,
            "effects_at_pause": effects_at_pause,
            "effects_after": after_effects,
            "effect_count": len(after_effects),
        },
        "assertions": {
            "pause_is_before_effect_commit": effects_at_pause == [],
            "current_assessment_matches_mutation": expected_current,
            "original_effect_committed": original_effect_committed,
            "no_inflight_authority_reread_after_mutation": no_inflight_reread_after_mutation,
            "execution_returned_without_exception": not error_box,
        },
        "claim_boundary": {
            "supported_by_existing_contract": (
                "execution-time authority is revalidated before destination dispatch; exact operation "
                "binding and local destination commit controls remain exercised"
            ),
            "unqualified": (
                "ordering of decision-relevant authority/policy/evidence changes after final revalidation "
                "but before protected destination commit"
            ),
            "not_claimed": [
                "EBL-Core conformance",
                "distributed linearizability",
                "production revocation enforcement",
                "complete mediation",
                "external effect finality",
            ],
        },
    }
    out = Path(os.environ.get("AUTHORITY_EFFECT_RACE_RESULTS_DIR", tmp_path / "evidence"))
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{scenario}.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")

    # Qualification assertions establish the observed ordering. They do not make
    # the stronger proposed guarantee an accepted Cognous pass criterion.
    assert effects_at_pause == []
    assert expected_current, as_json(current)
    assert no_inflight_reread_after_mutation
    assert not error_box, error_box
    assert original_effect_committed
    assert result is not None
    assert result.status in {"executed", "reconciled"}
