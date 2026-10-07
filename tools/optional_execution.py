"""Explicit synthetic execution profiles; no consumer evidence conformance implied."""
from __future__ import annotations
import dataclasses
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = datetime(2026, 8, 8, 1, 0, tzinfo=timezone.utc)
PROFILES = ("atomic-authority-effect", "refund-intent")


def setup(root, work):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import load_executor_runtime, runtime_proposal_model
    from experiments.odex_gax_imx_reference.synthetic_fixture import build_synthetic_resolver
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_observation_policy, synthetic_refund_policy
    from engine.safe_executor import commitment
    runtime = load_executor_runtime()
    cp = runtime["cp"]
    manifest = json.loads(
        (work / "action_manifest/examples/refund_integration_v1_1.manifest.json").read_text()
    )
    seed = json.loads(
        (work / "replay_bundle/examples/bounded_success_reconstruction_v0_2.json").read_text()
    )
    proposal = runtime_proposal_model(seed)
    manifest["actions"][0]["effect_limits"]["max_effects"] = 3
    proposal = proposal.model_copy(update={"manifest_digest": commitment(manifest)})
    resolver = build_synthetic_resolver(proposal, now=BASE)
    context = resolver.contexts[proposal.authority_context_ref]
    context["requirement"]["permissions"][0]["max_effects"] = 3
    context["grant"]["permissions"][0]["max_effects"] = 3
    workflow = cp.BoundedAuthorizationWorkflow(
        manifest=manifest,
        resolver=resolver,
        destination=cp.LocalRefundDestination(root / "control-plane-destination.json"),
        records=cp.BoundedRecordStore(root / "control-plane.json", "worker21"),
        observation_policy=synthetic_observation_policy(),
    )
    decision = workflow.decide(proposal, now=BASE)
    if decision.result != "authorized":
        raise RuntimeError(str(decision.reasons))

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

    policy = dataclasses.replace(synthetic_refund_policy(operation), max_effects=3)
    return workflow, resolver, proposal, decision, envelope, policy


def run_case(profile, scenario, root, work):
    if profile not in PROFILES:
        raise ValueError("unknown execution profile")
    allowed = {"atomic-authority-effect": {"allowed", "revoked"},
               "refund-intent": {"allowed", "revoked", "same-intent", "distinct-intent"}}
    if scenario not in allowed[profile]:
        raise ValueError("unsupported scenario")
    # Never migrate, erase, or implicitly reuse a destination.
    root.mkdir(parents=True, exist_ok=False)
    workflow, resolver, proposal, decision, envelope, policy = setup(root, work)
    from engine.safe_executor import DurableRefundDestination, snapshot_envelope, commitment
    if profile == "atomic-authority-effect":
        from engine.local_authority_effect import AtomicAuthorityEffectDestination, AtomicLocalControlPlaneExecutor
        destination = AtomicAuthorityEffectDestination(root / "destination", clock=lambda: BASE)
        executor = AtomicLocalControlPlaneExecutor(workflow=workflow, destination=destination, policy=policy)
        claim = executor.provision_claim(proposal=proposal, decision=decision, now=BASE)
        if scenario == "revoked":
            destination.set_grant_status(claim.grant_id, status="revoked")
        result = executor.execute(envelope=envelope, claim_id=claim.claim_id)
        sidecar = {"claim_state": destination.claim_state(claim.claim_id),
                   "reconciliation": dataclasses.asdict(executor.reconcile(claim_id=claim.claim_id, envelope=envelope))}
        outcomes = [dataclasses.asdict(result)]
    else:
        from engine.refund_intent import RefundIntent, RefundIntentRegistry
        from engine.control_plane_adapter import PinnedControlPlaneExecutor
        destination = DurableRefundDestination(root / "destination")
        registry = RefundIntentRegistry(destination)
        intent = RefundIntent(envelope.operation.institution_id, envelope.operation.authority_domain,
                              proposal.payload["customer_id"], "synthetic-domain-request-1")
        registry.provision(intent, snapshot_envelope(envelope))
        executor = PinnedControlPlaneExecutor(workflow=workflow, destination=destination,
                                              policy=policy, observation_clock=lambda: BASE)
        if scenario == "revoked":
            resolver.statuses[envelope.operation.grant_id].status = "revoked"
        result = executor.execute(envelope=envelope, proposal=proposal, decision=decision, now=BASE, refund_intent=intent)
        outcomes = [dataclasses.asdict(result)]
        if scenario in {"same-intent", "distinct-intent"}:
            other = proposal.model_copy(update={"correlation_id": "synthetic-replan"})
            context = resolver.contexts[proposal.authority_context_ref]
            ref = context["grant"]["approval_refs"][0]
            digest = commitment(other.model_dump(mode="json", exclude_none=False))
            resolver.approvals[ref] = resolver.approvals[ref].model_copy(update={"proposal_commitment": digest})
            fresh = workflow.decide(other, now=BASE)
            if fresh.result != "authorized":
                raise RuntimeError(str(fresh.reasons))
            second = dataclasses.replace(envelope, decision_id=fresh.decision_id, effect_id=fresh.effect_id,
                                         operation=dataclasses.replace(envelope.operation, proposal_commitment=digest))
            if second.effect_id == envelope.effect_id:
                raise RuntimeError("replan did not get a distinct effect identity")
            chosen = intent if scenario == "same-intent" else dataclasses.replace(intent, request_id="synthetic-domain-request-2")
            if scenario == "distinct-intent":
                registry.provision(chosen, snapshot_envelope(second))
            result2 = executor.execute(envelope=second, proposal=other, decision=fresh, now=BASE, refund_intent=chosen)
            outcomes.append(dataclasses.asdict(result2))
        sidecar = registry.export_intent(intent)
    with sqlite3.connect(destination.path.as_uri() + "?mode=ro", uri=True) as conn:
        effects = conn.execute("SELECT effect_id FROM effects ORDER BY effect_id").fetchall()
    expected = 0 if scenario == "revoked" else (2 if scenario == "distinct-intent" else 1)
    valid = len(effects) == expected and result.newly_executed == (scenario != "revoked")
    if len(outcomes) == 2:
        valid = valid and outcomes[1]["newly_executed"] == (scenario == "distinct-intent")
    return {"schema_version": "1.0.0", "profile": profile, "scenario": scenario,
            "synthetic": True, "qualified": valid, "effect_ids": [v[0] for v in effects],
            "outcomes": outcomes, "profile_evidence": sidecar,
            "consumer_chain_qualified": False, "production_ready": False}
