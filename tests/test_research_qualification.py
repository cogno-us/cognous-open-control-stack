"""Batch 4C observation repair: real pinned Control Plane / Moltbot interfaces.

Only observation fault injection is synthetic. No replacement authorization,
execution, reconciliation, or deduplication implementation is supplied here.
Required invariants fail the gate (never xfail).
"""
import copy
import dataclasses
import json
import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".reference-work"
NOW = datetime(2026, 8, 8, 1, tzinfo=timezone.utc)
SOURCE = {
    "title": "When a Timeout Is Not a Failure: Authority, Evidence, and Recovery in Consequential AI Execution",
    "author": "Jonathan Chadbourne / JCEE Labs",
    "version": "Technical Note 001, Public Release v0.1.1",
    "date": "2026-10-06",
    "locator": "pp. 1-3, sections 2-6",
    "status": "source-reported; JCEE campaigns not independently reproduced",
}


def json_value(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=False)
    return value


def rows(destination):
    with sqlite3.connect(destination.path) as con:
        con.row_factory = sqlite3.Row
        return [dict(r) for r in con.execute("SELECT * FROM effects ORDER BY effect_id")]


@pytest.fixture(scope="module")
def pins():
    lock = json.loads((ROOT / "component-lock.json").read_text())
    actual = {}
    for name in ("action_manifest", "control_plane", "gax_imx_transport", "moltbot_safe", "replay_bundle", "odes", "governance_evidence_pack"):
        spec = lock["components"][name]
        expected = spec["core_interop_sha"] if name == "moltbot_safe" else spec["sha"]
        head = subprocess.check_output(["git", "-C", str(WORK / name), "rev-parse", "HEAD"], text=True).strip()
        assert head == expected, f"{name}: wrong pinned checkout"
        actual[name] = head
    return {"lock": lock, "exercised_component_heads": actual}


def setup_case(tmp_path, *, max_effects=1):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import load_executor_runtime, runtime_proposal_model
    from experiments.odex_gax_imx_reference.synthetic_fixture import build_synthetic_resolver, synthetic_observation_policy
    runtime = load_executor_runtime()
    cp = runtime["cp"]
    manifest = json.loads((WORK / "action_manifest/examples/refund_integration_v1_1.manifest.json").read_text())
    seed = json.loads((WORK / "replay_bundle/examples/bounded_success_reconstruction_v0_2.json").read_text())
    proposal = runtime_proposal_model(seed)
    # New declared synthetic multi-use manifest; recompute its actual binding.
    manifest["actions"][0]["effect_limits"]["max_effects"] = max_effects
    proposal = proposal.model_copy(update={"manifest_digest": cp.commitment(manifest)})
    resolver = build_synthetic_resolver(proposal, now=NOW)
    context = resolver.contexts[proposal.authority_context_ref]
    context["requirement"]["permissions"][0]["max_effects"] = max_effects
    context["grant"]["permissions"][0]["max_effects"] = max_effects
    destination = runtime["DurableRefundDestination"](tmp_path / "destination")
    workflow = cp.BoundedAuthorizationWorkflow(
        manifest=manifest, resolver=resolver, destination=destination,
        records=cp.BoundedRecordStore(tmp_path / "control-plane.json", "batch4c"),
        observation_policy=synthetic_observation_policy(),
    )
    return runtime, proposal, resolver, destination, workflow


def authorize(runtime, proposal, resolver, workflow):
    # Supply a separately bound current approval for THIS proposal, retaining
    # the real approval check. Never disable review or reuse a mismatched approval.
    cp = runtime["cp"]
    ref = resolver.contexts[proposal.authority_context_ref]["grant"]["approval_refs"][0]
    resolver.approvals[ref] = resolver.approvals[ref].model_copy(update={
        "proposal_commitment": cp.commitment(json_value(proposal)),
    })
    decision = workflow.decide(proposal, now=NOW)
    assert decision.result == "authorized", decision.reasons
    binding = decision.binding
    context = resolver.authority_context(proposal.authority_context_ref)
    values = json_value(proposal)
    values.update({
        "institution_id": context["institution"]["institution_id"],
        "authority_domain": context["institution"]["authority_domain"],
        "authority_context_id": proposal.authority_context_ref,
        "proposal_commitment": binding.proposal_commitment,
        "grant_id": binding.grant_id, "grant_revision": binding.grant_revision,
        "effective_max_effects": binding.effective_max_effects,
        "requested_permissions": tuple(proposal.requested_permissions),
    })
    operation = runtime["ExecutionOperation"](**{
        f.name: values[f.name] for f in dataclasses.fields(runtime["ExecutionOperation"])
    })
    envelope = runtime["ExecutionEnvelope"](
        version="0.2.0", decision_id=decision.decision_id,
        effect_id=decision.effect_id, operation=operation,
    )
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_refund_policy
    policy = dataclasses.replace(synthetic_refund_policy(operation), max_effects=binding.effective_max_effects)
    executor = runtime["PinnedControlPlaneExecutor"](workflow=workflow, destination=workflow.destination, policy=policy, observation_clock=lambda: NOW)
    return decision, envelope, executor, json_value(resolver.approvals[ref])


def record(tmp_path, pins, scenario_id, *, classification, expected, observed,
           before, after, identities, fault, safety_outcome, limitation, setup):
    payload = {
        "schema_version": "1.0", "scenario_id": scenario_id,
        "source_requirement": SOURCE, "component_pins": pins,
        "classification": classification, "execution_status": "executed",
        "safety_outcome": safety_outcome,
        "characterization_outcome": "confirmed" if classification == "characterization" else None,
        "expected_safety_property": expected, "observed_outcome": observed,
        "destination_before": before, "destination_after": after,
        "identities": identities, "setup": setup, "fault_injection": fault,
        "evaluation_time": NOW.isoformat(),
        "evidence_scope": "actual pinned Control Plane plus Moltbot local SQLite destination; caller-supplied synthetic authority; no transport or remote authority exercised",
        "remaining_limitation": limitation,
    }
    # Write BEFORE assertions: a failing invariant retains its reproduction.
    out = Path(os.environ.get("BATCH4C_RESULTS_DIR", str(tmp_path / "evidence")))
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{scenario_id}.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def test_replanned_equivalent_intent_multi_use_grant(tmp_path, pins):
    runtime, first, resolver, destination, workflow = setup_case(tmp_path, max_effects=3)
    second = first.model_copy(update={"correlation_id": "same-refund-new-plan", "run_id": "replanned-run"})
    before = rows(destination)
    history = []
    for proposal in (first, second):
        decision, envelope, executor, approval = authorize(runtime, proposal, resolver, workflow)
        assert decision.binding.effective_max_effects == 3
        result = executor.execute(envelope=envelope, proposal=proposal, decision=decision, now=NOW)
        history.append({"proposal": json_value(proposal), "decision": json_value(decision),
                        "approval": approval, "envelope": json_value(envelope), "execution": json_value(result)})
        assert result.newly_executed is True, json_value(result)
    after = rows(destination)
    # Same-ID replay is the control: it must not create a third effect.
    duplicate = executor.execute(envelope=envelope, proposal=second, decision=decision, now=NOW)
    final = rows(destination)
    record(tmp_path, pins, "4c-replanned-equivalent-intent", classification="characterization",
           expected="Business intent duplication is measured, not presumed prevented; repeated same effect identity must not add an effect.",
           observed={"authorized_operations": history, "same_identity_replay": json_value(duplicate),
                     "effect_count_after_two_proposals": len(after), "effect_count_after_same_id_replay": len(final)},
           before=before, after=final, identities=history, fault="none; proposal correlation_id and run_id changed, business payload unchanged",
           safety_outcome="not_established",
           limitation="Two valid separately approved effects for one stated refund intent. Effect-key idempotency is not business-intent deduplication.",
           setup={"grant_max_effects": 3, "separate_current_bound_approvals": True,
                  "shared_destination": "one SQLite effects table", "transaction": "BEGIN IMMEDIATE; unique effect_id; per-grant count within transaction"})
    assert history[0]["decision"]["effect_id"] != history[1]["decision"]["effect_id"]
    assert history[0]["decision"]["binding"]["proposal_commitment"] != history[1]["decision"]["binding"]["proposal_commitment"]
    assert len(after) == 2, "characterization changed: re-review supported scope"
    assert final == after and duplicate.newly_executed is False
    for row in final:
        assert row["state"] == "applied"
        assert row["target"] == first.target and row["amount"] == first.amount and row["unit"] == first.unit
        assert json.loads(row["payload_json"]) == first.payload


@pytest.mark.parametrize("evidence", ["unavailable", "unknown", "stale", "incomplete", "wrong_operation", "authoritative_absence"])
def test_absence_evidence_does_not_invent_retry_permission(tmp_path, pins, monkeypatch, evidence):
    from engine.control_plane_adapter import ControlPlaneRefundDestinationAdapter
    from engine.producer_contract import snapshot_envelope
    runtime, proposal, resolver, destination, workflow = setup_case(tmp_path)
    decision, envelope, executor, approval = authorize(runtime, proposal, resolver, workflow)
    result = None
    if evidence != "authoritative_absence":
        result = executor.execute(envelope=envelope, proposal=proposal, decision=decision, now=NOW)
        assert result.newly_executed is True
    before = rows(destination)
    snapshot = snapshot_envelope(envelope)
    adapter = ControlPlaneRefundDestinationAdapter(
        snapshot=snapshot, destination=destination, policy=executor.policy,
        trusted_institution_id=snapshot.operation.institution_id,
        trusted_authority_domain=snapshot.operation.authority_domain,
        observation_clock=lambda: NOW,
    )
    cp = runtime["cp"]
    # Fix the producer's clock to make stale/unknown comparisons reproducible.
    monkeypatch.setattr(cp, "_now", lambda: NOW)
    genuine = adapter.observe(decision.effect_id)
    if evidence != "authoritative_absence":
        assert len(before) == 1 and genuine.state == "applied"
        assert genuine.effect_id == decision.effect_id
        assert genuine.destination_state["operation_digest"] == snapshot.operation.digest
    fault_observation = genuine.model_copy(deep=True)
    if evidence == "unknown":
        fault_observation = fault_observation.model_copy(update={"state": "unknown", "destination_state": {}})
    elif evidence in {"stale", "incomplete", "wrong_operation"}:
        fault_observation = fault_observation.model_copy(update={"state": "absent", "destination_state": {}})
        if evidence == "stale": fault_observation.observed_at = "2000-01-01T00:00:00+00:00"
        if evidence == "incomplete": fault_observation.observed_at = ""
        if evidence == "wrong_operation": fault_observation.effect_id = "different-operation-effect"
    fault_observation = cp.EffectObservation.model_validate(json_value(fault_observation))
    def injected_observation(effect_id):
        assert effect_id == decision.effect_id
        if evidence == "unavailable": raise OSError("injected observation channel unavailable")
        return fault_observation
    if evidence != "authoritative_absence":
        # Inject only the observation returned at the real adapter boundary;
        # actual pinned reconcile() and durable destination remain unchanged.
        monkeypatch.setattr(adapter, "observe", injected_observation)
    recovery = cp.BoundedAuthorizationWorkflow(manifest=workflow.manifest, resolver=resolver,
        destination=adapter, records=workflow.records, observation_policy=workflow.observation_policy)
    error = None
    reconciliation = None
    try:
        reconciliation = recovery.reconcile(decision.effect_id, now=NOW)
    except OSError as exc:
        error = str(exc)
    after = rows(destination)
    safe = (after == before and reconciliation is not None
            and reconciliation.retry_eligible is False
            and reconciliation.result == ("observed_absent" if evidence == "authoritative_absence" else "hold"))
    record(tmp_path, pins, f"4c-absence-{evidence}", classification="required_safety_invariant",
           expected="Unavailable/unknown/stale/incomplete/wrong-operation evidence must not become absence or safe_to_retry; observation creates no effect.",
           observed={"genuine_observation": json_value(genuine),
                     "injected_observation": None if evidence in {"unavailable", "authoritative_absence"} else json_value(fault_observation),
                     "reconciliation": json_value(reconciliation), "exception": error},
           before=before, after=after,
           identities={"proposal": json_value(proposal), "decision": json_value(decision),
                       "execution": json_value(result), "approval": approval, "envelope": json_value(envelope)},
           fault="none" if evidence == "authoritative_absence" else "ControlPlaneRefundDestinationAdapter.observe return/exception only",
           safety_outcome="passed" if safe else "failed",
           limitation="Observation contract has no source-authentication or coverage/finality fields. Local SQLite absence is a point-in-time lookup, not proof of no in-flight future commit; observed_absent never permits retry.",
           setup={"observation_source": "actual bound local SQLite adapter" if evidence == "authoritative_absence" else "explicit injected adapter observation",
                  "coverage": "one effect key in one local database", "current_time": NOW.isoformat(),
                  "dispatch_during_reconciliation": False})
    assert after == before
    assert reconciliation.retry_eligible is False
    if evidence in {"unavailable", "stale", "incomplete", "wrong_operation"}:
        assert reconciliation.observation_accepted is False
    if evidence == "unavailable":
        assert reconciliation.observation is None
    if evidence == "authoritative_absence":
        assert before == [] and genuine.state == "absent"
        assert genuine.effect_id == decision.effect_id
        assert genuine.observed_at == NOW.isoformat()
        assert reconciliation.result == "observed_absent"
        assert reconciliation.retry_eligible is False
    elif evidence == "unavailable":
        assert reconciliation.result == "hold" and reconciliation.retry_eligible is False
    else:
        assert reconciliation.result == "hold", f"{evidence} evidence promoted to {reconciliation.result}"


@pytest.mark.parametrize("late_state", ["applied", "partial"])
def test_original_late_commit_never_permits_replacement(tmp_path, pins, monkeypatch, late_state):
    """Synthetic destination latency, real authorized dispatch and SQLite commit.

    A worker retains the original frozen request after the caller times out. An
    event (not a sleep) releases its real commit only after absence/recovery.
    This is one process with a delayed destination thread, not process-boundary
    or distributed qualification. No cancellation/termination API is invented.
    """
    from threading import Event, Thread
    from experiments.governed_message_transport import AcceptedGaxRecipientAdapter, LocalDurableTransport
    from experiments.odex_gax_imx_reference.gax_ref_runtime import (
        LocalRegistry, digest, make_message, load_executor_runtime, runtime_proposal_model)
    from experiments.odex_gax_imx_reference.synthetic_fixture import (
        build_synthetic_resolver, synthetic_refund_policy,
        synthetic_observation_policy, synthetic_observation_clock)
    from tools.transported_reference import routes

    runtime = load_executor_runtime()
    manifest = json.loads((WORK / "action_manifest/examples/refund_integration_v1_1.manifest.json").read_text())
    seed = json.loads((WORK / "replay_bundle/examples/bounded_success_reconstruction_v0_2.json").read_text())
    destination = runtime["DurableRefundDestination"](tmp_path / "destination")
    handler = AcceptedGaxRecipientAdapter(
        bundle=seed, registry=LocalRegistry({"refund-sender"}, {"refund-recipient"}, "refund-recipient"),
        evaluation_time=NOW.isoformat(), manifest=manifest,
        exchange_store_path=tmp_path / "exchange.sqlite",
        resolver=build_synthetic_resolver(runtime_proposal_model(seed), now=NOW),
        destination=destination, execution_policy_factory=synthetic_refund_policy,
        observation_policy=synthetic_observation_policy(), observation_clock=synthetic_observation_clock)
    transport = LocalDurableTransport(sender_store_path=tmp_path / "sender.sqlite",
        recipient_store_path=tmp_path / "recipient.sqlite", routes=routes(), recipient_handler=handler,
        max_attempts=3, base_backoff_seconds=1)
    message = make_message(seed, message_id="late-commit-" + late_state)
    transport.queue(message, route_id="accepted-gax-local", sender_endpoint_ref="local://refund-sender",
                    now=NOW.isoformat(), correlation_id="late-commit")
    release, finished = Event(), Event()
    original_commit = destination.commit
    original_observe = destination.observe_bound
    observations = []
    def record_observation(snapshot):
        observations.append(snapshot.effect_id)
        return original_observe(snapshot)
    monkeypatch.setattr(destination, "observe_bound", record_observation)
    calls, outcomes, errors, workers = [], [], [], []

    def delayed_commit(snapshot, *, simulate=None):
        calls.append({"effect_id": snapshot.effect_id, "decision_id": snapshot.decision_id,
                      "operation_digest": snapshot.operation.digest})
        def complete_original():
            try:
                if not release.wait(10):
                    raise TimeoutError("test barrier not released")
                outcomes.append(original_commit(snapshot, simulate="partial" if late_state == "partial" else None))
            except BaseException as exc:
                errors.append(repr(exc))
            finally:
                finished.set()
        worker = Thread(target=complete_original, daemon=True)
        workers.append(worker)
        worker.start()
        raise TimeoutError("synthetic caller timeout; original destination request remains in flight")

    monkeypatch.setattr(destination, "commit", delayed_commit)
    try:
        delivery = transport.deliver(message["message_id"], now=NOW.isoformat())
        original = transport.retained_artifacts(message["message_id"])["artifact_export"]
        effect_id = original["producer_refs"]["effect_id"]
        before = rows(destination)
        queries_before_absence = len(observations)
        absence = handler.resume_original(message, delivery_time=NOW.isoformat())
        repeated_absence = handler.resume_original(message, delivery_time=NOW.isoformat())
        absence_query_count = len(observations) - queries_before_absence
        precommit = rows(destination)
        calls_before_release = list(calls)
        completed_before_release = finished.is_set()
        transport.deliver(message["message_id"], now=NOW.isoformat(), force=True)
        redelivered_before = transport.retained_artifacts(message["message_id"])["artifact_export"]
        release.set()
        assert finished.wait(10), "original destination worker did not finish"
        for worker in workers:
            worker.join(timeout=10)
        after_commit = rows(destination)
        recovered = handler.resume_original(message, delivery_time=NOW.isoformat())
        after_recovery = rows(destination)
        transport.deliver(message["message_id"], now=NOW.isoformat(), force=True)
        redelivered_after = transport.retained_artifacts(message["message_id"])["artifact_export"]
        payload = {
            "schema_version":"1.0", "scenario_id":"4c-late-commit-"+late_state,
            "classification":"required_safety_invariant", "execution_status":"executed",
            "scope":"same-process deterministic delayed destination thread; real pinned transport/GAX/executor/SQLite",
            "component_pins":pins, "trusted_evaluation_time":NOW.isoformat(),
            "fault":"timeout after scheduling original commit; event release after two absence recoveries",
            "delivery":delivery, "original_artifacts":original,
            "absence_observation_queries": absence_query_count,
            "absence_recovery":absence, "repeated_absence_recovery":repeated_absence,
            "post_commit_recovery":recovered, "destination_before":before,
            "destination_precommit":precommit, "destination_after_commit":after_commit,
            "destination_after_recovery":after_recovery,
            "dispatch_calls_before_release":calls_before_release, "dispatch_calls_total":calls,
            "completed_before_release":completed_before_release,
            "original_worker_outcomes":outcomes, "original_worker_errors":errors,
            "redelivery_original_equal":redelivered_before == original == redelivered_after,
            "original_export_commitment":digest(original),
            "recomputed_replay_commitment":digest(original["reconstruction_bundle"]),
            "cancellation_requested":False, "termination_confirmed":False, "rollback_performed":False,
            "limitations":["no cancellation or termination guarantee", "no authority-change qualification",
                           "no separate-process or distributed guarantee", "no authenticated external observation"]}
        out = Path(os.environ.get("BATCH4C_RESULTS_DIR", str(tmp_path / "evidence")))
        out.mkdir(parents=True, exist_ok=True)
        (out / (payload["scenario_id"]+".json")).write_text(json.dumps(payload, indent=2, sort_keys=True))
        assert not completed_before_release and not errors
        assert absence_query_count == 2
        assert before == precommit == []
        assert len(calls_before_release) == len(calls) == 1
        assert calls[0]["effect_id"] == effect_id
        assert len(outcomes) == 1 and outcomes[0]["duplicate"] is False
        assert len(after_commit) == 1 and after_commit == after_recovery
        assert after_commit[0]["effect_id"] == effect_id and after_commit[0]["state"] == late_state
        operation = next(r["data"]["operation"] for r in original["reconstruction_bundle"]["records"]
                         if r["record_type"] == "execution_envelope")
        assert all(after_commit[0][k] == operation[k] for k in ("target", "amount", "unit", "grant_id"))
        assert json.loads(after_commit[0]["payload_json"]) == operation["payload"]
        assert original["successor_packet"]["pending_effects"] == [effect_id]
        assert original["successor_packet"]["unresolved_delivery"] is True
        for result in (absence, repeated_absence):
            assert result["execution"]["newly_executed"] is False
            assert result["execution"]["attempt_status"] == "denied"
            assert result["artifact_export"]["state"] == "reconciled_derivative"
            facts = result["execution_facts"]
            assert facts["pending_effects"] == [effect_id] and facts["unresolved_delivery"] is True
            assert facts["reconciliations"][-1]["result"] == "observed_absent"
            assert facts["reconciliations"][-1]["retry_eligible"] is False
        assert recovered["execution"]["effect_id"] == effect_id
        assert recovered["execution"]["newly_executed"] is False
        facts = recovered["execution_facts"]
        assert facts["destination_observed"] == late_state
        assert facts["unresolved_delivery"] is (late_state == "partial")
        assert facts["pending_effects"] == ([] if late_state == "applied" else [effect_id])
        assert any(a["status"] == "unknown" and not a["acknowledgement"]
                   for a in facts["control_plane_attempt_transitions"])
        assert redelivered_before == original == redelivered_after
        assert original["producer_refs"]["reconstruction_digest"] == digest(original["reconstruction_bundle"])
    finally:
        release.set()
        for worker in workers:
            worker.join(timeout=10)


@pytest.mark.parametrize("authority_change", ["revocation", "expiry", "policy", "evidence", "approval"])
@pytest.mark.parametrize("effect_state", ["applied", "absent"])
def test_recovery_authority(tmp_path, pins, monkeypatch, authority_change, effect_state):
    """Changed authority denies resume before observation; original facts survive."""
    from datetime import timedelta
    from experiments.governed_message_transport import AcceptedGaxRecipientAdapter, LocalDurableTransport
    from experiments.odex_gax_imx_reference.gax_ref_runtime import (
        LocalRegistry, digest, make_message, load_executor_runtime, runtime_proposal_model)
    from experiments.odex_gax_imx_reference.synthetic_fixture import (
        build_synthetic_resolver, synthetic_refund_policy, synthetic_observation_policy)
    from agent_governance_evidence_pack import import_manifest_reconstruction, validate_evidence_pack
    from odes import evaluate_recipient_package
    from tools.transported_reference import routes

    runtime = load_executor_runtime()
    cp = runtime["cp"]
    manifest = json.loads((WORK / "action_manifest/examples/refund_integration_v1_1.manifest.json").read_text())
    seed = json.loads((WORK / "replay_bundle/examples/bounded_success_reconstruction_v0_2.json").read_text())
    proposal = runtime_proposal_model(seed)
    resolver = build_synthetic_resolver(proposal, now=NOW)
    clock = [NOW]
    destination = runtime["DurableRefundDestination"](tmp_path / "destination")
    handler = AcceptedGaxRecipientAdapter(bundle=seed,
        registry=LocalRegistry({"refund-sender"}, {"refund-recipient"}, "refund-recipient"),
        manifest=manifest, exchange_store_path=tmp_path / "exchange.sqlite", resolver=resolver,
        destination=destination, execution_policy_factory=synthetic_refund_policy,
        observation_policy=synthetic_observation_policy(), observation_clock=lambda: clock[0])
    transport = LocalDurableTransport(sender_store_path=tmp_path / "sender.sqlite",
        recipient_store_path=tmp_path / "recipient.sqlite", routes=routes(), recipient_handler=handler,
        max_attempts=3, base_backoff_seconds=1)
    message = make_message(seed, message_id=f"authority-{effect_state}-{authority_change}",
                           expires_at="2026-08-10T00:00:00Z")
    commit, observe = destination.commit, destination.observe_bound
    dispatches, queries = [], []

    def unknown_ack(snapshot, *, simulate=None):
        dispatches.append({"effect_id": snapshot.effect_id, "decision_id": snapshot.decision_id})
        if effect_state == "applied":
            return commit(snapshot, simulate="lost_ack")
        raise TimeoutError("synthetic interruption before destination commit")

    def observed(snapshot):
        queries.append({"effect_id": snapshot.effect_id, "at": clock[0].isoformat()})
        return observe(snapshot)

    monkeypatch.setattr(destination, "commit", unknown_ack)
    monkeypatch.setattr(destination, "observe_bound", observed)
    transport.queue(message, route_id="accepted-gax-local", sender_endpoint_ref="local://refund-sender",
                    now=NOW.isoformat(), correlation_id="recovery-authority")
    delivery = transport.deliver(message["message_id"], now=NOW.isoformat())
    original = transport.retained_artifacts(message["message_id"])["artifact_export"]
    effect_id = original["producer_refs"]["effect_id"]
    before = rows(destination)
    # These are trusted synthetic status fixtures, not replacement authorization logic.
    groups = ("statuses", "identities", "mandates", "approvals", "policies", "conflicts", "evidence")
    def authority_inputs():
        return {"contexts": copy.deepcopy(resolver.contexts), **{
            name: {k: json_value(v) for k, v in getattr(resolver, name).items()} for name in groups}}
    original_inputs = authority_inputs()
    refreshed = []
    if authority_change == "expiry":
        clock[0] = datetime(2026, 8, 9, tzinfo=timezone.utc)
        for group in groups:
            values = getattr(resolver, group)
            for key, value in values.items():
                values[key] = value.model_copy(update={"observed_at": clock[0].isoformat()})
                refreshed.append(group + ":" + key)
    else:
        group, field, value = {
            "revocation": ("statuses", "status", "revoked"),
            "policy": ("policies", "version", "changed-policy-version"),
            "evidence": ("evidence", "observed_at", (NOW - timedelta(seconds=301)).isoformat()),
            "approval": ("approvals", "status", "revoked"),
        }[authority_change]
        values = getattr(resolver, group)
        key = next(iter(values))
        values[key] = values[key].model_copy(update={field: value})
    expected_reason = {"revocation": "grant_not_active", "expiry": "grant_outside_validity",
        "policy": "policy_stale_or_changed", "evidence": "required_evidence_stale_or_future",
        "approval": "approval_not_active"}[authority_change]
    # A separate public assessment proves the intended check is reached, with no dispatch.
    assessment_workflow = cp.BoundedAuthorizationWorkflow(manifest=manifest, resolver=resolver,
        destination=cp.LocalRefundDestination(tmp_path / "assessment-destination.json"),
        records=cp.BoundedRecordStore(tmp_path / "assessment-record.json", proposal.run_id),
        observation_policy=synthetic_observation_policy())
    current_decision = assessment_workflow.decide(proposal, now=clock[0])
    def cp_snapshot():
        return {p.name: p.read_text() for p in sorted(tmp_path.glob("control-plane-*.json"))}
    cp_before = cp_snapshot()
    query_count = len(queries)
    from agent_replay_bundle.importers import ImportContractError
    recovery_error = None
    try:
        recovered = handler.resume_original(message, delivery_time=clock[0].isoformat())
    except ImportContractError as exc:
        recovery_error = {"type": type(exc).__name__, "message": str(exc)}
    cp_after = cp_snapshot()
    after = rows(destination)
    recovery_queries = len(queries) - query_count
    # Historical reads, redelivery and public evidence export must not mutate either store.
    retained = transport.retained_artifacts(message["message_id"])["artifact_export"]
    transport.deliver(message["message_id"], now=clock[0].isoformat(), force=True)
    evidence_only = handler.recover(message, delivery_time=clock[0].isoformat())
    pack = import_manifest_reconstruction(manifest, retained["reconstruction_bundle"])
    pack_validation = validate_evidence_pack(pack)
    package = retained["odes"]["odes_package"]
    validation = evaluate_recipient_package(package, {
        "now": clock[0].isoformat(), "purpose": "audit", "relying_party": "recipient.example.org",
        "status_inputs": {}, "supported_profiles": [package["profile"]["implementation_profile"]],
        "trusted_digests": [], "trusted_key_refs": [], "evaluation_scope": "audit",
        "status_max_age_seconds": 300, "allow_unauthenticated_informational_inspection": False})
    if recovery_error is not None:
        checks = {
            "recovery_returns_preserving_original_effect": (False, True),
            "intended_authority_check_only": (sorted(current_decision.reasons), [expected_reason]),
            "one_original_dispatch": (len(dispatches), 1),
            "destination_unchanged": (before == after == rows(destination), True),
            "applied_original_still_exists": ([r["effect_id"] for r in after], [effect_id]),
            "denied_before_destination_query": (recovery_queries, 0),
            "cp_unchanged": (cp_before == cp_after == cp_snapshot(), True),
            "original_export_preserved": (original == retained == evidence_only.artifact_export ==
                transport.retained_artifacts(message["message_id"])["artifact_export"], True),
            "evidence_pack_valid": (pack_validation.valid, True),
            "odes_integrity": (validation["package_content_integrity"]["status"], "pass"),
            "current_permission_unavailable": (validation["authority_status_and_freshness"]["status"], "unavailable"),
            "replay_commitment": (digest(original["reconstruction_bundle"]), original["producer_refs"]["reconstruction_digest"]),
        }
        payload = {"scenario_id": f"4c-authority-{effect_state}-{authority_change}",
            "component_pins": pins, "trusted_original_time": NOW.isoformat(),
            "trusted_recovery_time": clock[0].isoformat(), "authority_before": original_inputs,
            "authority_after": authority_inputs(), "refreshed_unrelated_statuses": refreshed,
            "original_delivery": delivery, "original_artifacts": original,
            "original_export_commitment": digest(original), "evidence_pack_commitment": digest(json_value(pack)),
            "destination_before": before, "destination_after": after, "dispatch_calls": dispatches,
            "observation_queries": queries, "recovery_query_count": recovery_queries,
            "current_authority_assessment": json_value(current_decision), "recovery_error": recovery_error,
            "returned_recovery": None, "odes_validation": validation,
            "cp_before_commitment": digest(cp_before), "cp_after_commitment": digest(cp_after),
            "assertions": {k: {"observed": v[0], "expected": v[1], "passed": v[0] == v[1]} for k, v in checks.items()},
            "blocked_path": "Accepted GAX resume_original -> pipeline -> Replay import rejects denied result with retained applied evidence; no successful recovery or derivative claimed."}
        out = Path(os.environ.get("BATCH4C_RESULTS_DIR", str(tmp_path / "evidence")))
        out.mkdir(parents=True, exist_ok=True)
        (out / (payload["scenario_id"] + ".json")).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        pytest.fail(f"upstream recovery export defect: {recovery_error}")
    facts = recovered["execution_facts"]
    commitments = {}
    for name, export in (("original", original), ("derivative", recovered["artifact_export"])):
        commitments[name] = {"export": digest(export), "producer_refs": export["producer_refs"],
            "replay": digest(export["reconstruction_bundle"]),
            "odes": digest(export["odes"]["odes_package"]),
            "successor": digest({k: v for k, v in export["successor_packet"].items() if k != "packet_digest"})}
    checks = {
        "intended_authority_check_only": (sorted(current_decision.reasons), [expected_reason]),
        "original_attempt_count": (len(dispatches), 1),
        "destination_count": (len(after), 1 if effect_state == "applied" else 0),
        "destination_unchanged": (before == after == rows(destination), True),
        "denied_before_destination_query": (recovery_queries, 0),
        "recovery_denied": (recovered["execution"]["attempt_status"], "denied"),
        "no_replacement": (recovered["execution"]["newly_executed"], False),
        "same_effect": (recovered["execution"]["effect_id"], effect_id),
        "same_decision": (recovered["execution"]["decision_id"], original["producer_refs"]["decision_id"]),
        "unknown_ack_retained": (any(a["status"] == "unknown" and not a["acknowledgement"]
            for a in facts["control_plane_attempt_transitions"]), True),
        "historical_observation_preserved": (facts["destination_observed"], "applied" if effect_state == "applied" else "absent"),
        "unresolved_delivery": (facts["unresolved_delivery"], effect_state == "absent"),
        "pending_original": (facts["pending_effects"], [effect_id] if effect_state == "absent" else []),
        "no_retry_permission": (any(r["retry_eligible"] for r in facts["reconciliations"]), False),
        "recovery_no_cp_append_when_authority_denied": (cp_before == cp_after, True),
        "evidence_only_cp_unchanged": (cp_after == cp_snapshot(), True),
        "original_export_preserved": (original == retained == evidence_only.artifact_export ==
            transport.retained_artifacts(message["message_id"])["artifact_export"], True),
        "evidence_pack_valid": (pack_validation.valid, True),
        "odes_integrity": (validation["package_content_integrity"]["status"], "pass"),
        "current_authority_not_asserted": (validation["authority_status_and_freshness"]["status"], "unavailable"),
        "independent_authentication_unavailable": (validation["integrity_authentication_checks"]["status"], "unavailable"),
    }
    derivative = recovered["artifact_export"]
    lineage = derivative["lineage"]
    current = lineage["recovery_result"]
    checks.update({
        "derivative_state": (derivative["state"], "recovery_denied_derivative"),
        "lineage_relationship": (lineage["relationship"], "recovery_denial_derivative"),
        "source_artifact": (lineage["source_artifact_commitment"], digest(original)),
        "source_checkpoint_present": (bool(lineage["source_checkpoint_commitment"]), True),
        "evaluation_time": (datetime.fromisoformat(lineage["recovery_evaluated_at"].replace("Z", "+00:00")).isoformat(), clock[0].isoformat()),
        "current_status": (current["status"], "denied"),
        "current_reason": (current["error"], "authorization-critical inputs changed before effect"),
        "lineage_reason": (lineage["recovery_reason"], current["error"]),
        "current_effect": (current["effect_id"], effect_id),
        "current_decision": (current["decision_id"], original["producer_refs"]["decision_id"]),
        "no_new_observation": (bool(current["observation"]), False),
        "no_new_cp_evidence": (bool(current["control_plane_evidence"]), False),
        "owning_cp_records_exist": (bool(cp_before), True),
    })
    for key in ("destination_observation_performed", "replacement_dispatch_performed",
                "renewed_authorization", "effect_reexecution"):
        checks["lineage_" + key] = (lineage[key], False)
    for key in ("reconstruction_bundle", "odes", "successor_packet", "producer_refs"):
        checks["derivative_preserves_" + key] = (derivative[key] == original[key], True)
    for name, values in commitments.items():
        for key, ref in (("replay", "reconstruction_digest"), ("odes", "odes_package_digest"),
                         ("successor", "successor_packet_digest")):
            checks[f"{name}_{key}_commitment"] = (values[key], values["producer_refs"][ref])
    payload = {"scenario_id": f"4c-authority-{effect_state}-{authority_change}",
        "component_pins": pins, "trusted_original_time": NOW.isoformat(),
        "trusted_recovery_time": clock[0].isoformat(), "authority_before": original_inputs,
        "authority_after": authority_inputs(), "refreshed_unrelated_statuses": refreshed,
        "original_delivery": delivery, "original_artifacts": original,
        "destination_before": before, "destination_after": after, "dispatch_calls": dispatches,
        "observation_queries": queries, "recovery_query_count": recovery_queries,
        "current_authority_assessment": json_value(current_decision),
        "recovery_execution": recovered["execution"], "recovery_assessment": recovered["assessment"],
        "recovery_facts": facts, "derivative_lineage": recovered["artifact_export"].get("lineage"),
        "commitments": commitments, "evidence_pack_commitment": digest(json_value(pack)), "odes_validation": validation,
        "cp_before_commitment": digest(cp_before), "cp_after_commitment": digest(cp_after),
        "assertions": {k: {"observed": v[0], "expected": v[1], "passed": v[0] == v[1]} for k, v in checks.items()},
        "limitation": "Transport/GAX resume_original revalidates authority before observation; no fresh effect-free observation under changed authority demonstrated through that path. Historical observation is not current permission or finality."}
    out = Path(os.environ.get("BATCH4C_RESULTS_DIR", str(tmp_path / "evidence")))
    out.mkdir(parents=True, exist_ok=True)
    (out / (payload["scenario_id"] + ".json")).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    for name, (actual, expected) in checks.items():
        assert actual == expected, name
