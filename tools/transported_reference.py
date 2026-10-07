#!/usr/bin/env python3
"""Generate and enforce one transported Cognous reference workflow.

The operation is executed only through LocalDurableTransport ->
AcceptedGaxRecipientAdapter. The hub consumes the versioned retained-artifact
interface exposed by Alvorada; it does not regenerate Replay/ODES artifacts or
read the exchange database to reconstruct them.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from experiments.governed_message_transport import (
    AcceptedGaxRecipientAdapter,
    LocalDurableTransport,
    Route,
    TrustedRouteTable,
)
from experiments.odex_gax_imx_reference.gax_ref_runtime import (
    LocalRegistry,
    load_executor_runtime,
    make_message,
    parse_time,
    runtime_proposal_model,
)
from experiments.odex_gax_imx_reference.synthetic_fixture import (
    build_synthetic_resolver,
    synthetic_refund_policy,
    synthetic_observation_policy,
    synthetic_observation_clock,
)
from agent_governance_evidence_pack.importer import build_evidence_pack_from_files
from agent_governance_evidence_pack.loader import dump_evidence_pack
from agent_governance_evidence_pack.trace_renderer import render_traceable_markdown

EVAL="2026-08-08T01:00:00Z"

def load_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True),encoding="utf-8")

def rows(path: Path, table: str):
    with sqlite3.connect(path) as con:
        con.row_factory=sqlite3.Row
        return [dict(r) for r in con.execute(f"SELECT * FROM {table} ORDER BY rowid")]

def routes():
    return TrustedRouteTable([
        Route(
            route_id="accepted-gax-local",
            sender_endpoint_ref="local://refund-sender",
            sender_identity_ref="urn:cognous:transport-identity:refund-sender",
            expected_sender_claim="refund-sender",
            recipient_endpoint_ref="local://refund-recipient",
            recipient_identity_ref="urn:cognous:transport-identity:refund-recipient",
            expected_recipient_claim="refund-recipient",
            configured_identity_authenticated=False,
        )
    ])

def first_record(bundle: dict, record_type: str) -> dict:
    matches=[
        r.get("data")
        for r in bundle.get("records",[])
        if isinstance(r,dict) and r.get("record_type")==record_type and isinstance(r.get("data"),dict)
    ]
    if len(matches)!=1:
        raise AssertionError(f"expected exactly one {record_type} record, observed {len(matches)}")
    return matches[0]

def _check_binding(require, proposal, execution, bundle, refs, transport, inbox_refs,
                   effects, attempts, facts):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import load_executor_runtime

    decision=first_record(bundle,"runtime_decision")
    envelope=first_record(bundle,"execution_envelope")
    result=first_record(bundle,"execution_result")
    replay_proposal=first_record(bundle,"runtime_proposal")
    replay_attempt=first_record(bundle,"destination_attempt")
    replay_effect=first_record(bundle,"destination_effect")
    operation=envelope["operation"]
    binding=decision.get("binding") or {}
    require(replay_proposal==proposal,"Replay proposal differs from original submitted proposal")
    commitment=load_executor_runtime()["commitment"](proposal)
    for source in (binding,operation):
        require(source.get("proposal_commitment")==commitment,"original proposal commitment mismatch")
    for key in ("decision_id","effect_id"):
        expected=execution.get(key)
        require(isinstance(expected,str) and bool(expected),f"recipient missing required {key}")
        for label, source in (("retained refs",refs),("transport",transport.get("producer_refs",{})),
                              ("inbox",inbox_refs),("Replay decision",decision),
                              ("Replay envelope",envelope),("Replay result",result),
                              ("Replay attempt",replay_attempt)):
            require(bool(source.get(key)) and source.get(key)==expected,f"{label} {key} mismatch/missing")
        for row in attempts:
            require(row.get(key)==expected,f"destination attempt {key} mismatch")
    for source in (inbox_refs,transport.get("producer_refs",{})):
        for key,value in refs.items():
            require(key in source and source[key]==value,f"transport/inbox retained reference {key} mismatch")
    aid=execution.get("attempt_id")
    require(isinstance(aid,str) and bool(aid),"recipient missing required attempt_id")
    for label, source in (("retained",refs),("transport",transport.get("producer_refs",{})),("inbox",inbox_refs)):
        identity=source.get("attempt_identity") or {}
        require(identity.get("namespace")=="executor" and identity.get("owner")=="cogno-us/moltbot-safe" and identity.get("attempt_id")==aid,
                f"{label} executor attempt identity mismatch")
        require(source.get("executor_attempt_ids")==[aid],f"{label} executor attempt list mismatch")
    require(result.get("attempt_id")==aid and replay_attempt.get("attempt_id")==aid,"Replay executor attempt mismatch")
    require(len(attempts)==1 and attempts[0].get("attempt_id")==aid,"destination executor attempt mismatch")
    require(replay_effect==effects[0] if len(effects)==1 else False,"Replay destination effect differs from actual destination")
    require(replay_attempt==attempts[0] if len(attempts)==1 else False,"Replay destination attempt differs from actual destination")
    for key in ("target","amount","unit","payload"):
        require(key in proposal and operation.get(key)==proposal[key],f"submitted operation {key} mismatch")
        if key!="payload":
            require(key in binding and binding[key]==proposal[key],f"decision operation {key} mismatch")
    grant=binding.get("grant_id")
    require(bool(grant) and operation.get("grant_id")==grant,"decision grant mismatch/missing")
    require(result.get("newly_executed") is True,"Replay result is not newly executed")
    # Check fields only in their owning namespaces; Control Plane attempt IDs differ.
    def inspect(value):
        if isinstance(value,list):
            for item in value: inspect(item)
        elif isinstance(value,dict):
            for key in ("decision_id","effect_id"):
                if key in value:
                    require(value[key]==execution.get(key),f"nested evidence {key} mismatch")
            for key in ("target","amount","unit","payload","grant_id"):
                if key in value:
                    require(value[key]==(grant if key=="grant_id" else proposal[key]),f"nested evidence operation {key} mismatch")
            for item in value.values(): inspect(item)
    for record in bundle["records"]:
        inspect(record["data"])
        kind=record["record_type"]
        if kind in ("destination_attempt","destination_attempt_event"):
            require(record["data"].get("attempt_id")==aid,f"{kind} attempt mismatch")
    inspect(facts)
    require(transport.get("retained_artifact_summary",{}).get("producer_refs")==refs,
            "transport retained artifact references mismatch")


def _check_commitments(require, reconstruction, odes, successor, refs, commitments,
                       replay_digest, odes_replay_digest):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import digest
    from agent_governance_evidence_pack.importer import sha256
    from odes import evaluate_recipient_package

    artifacts=(
        ("reconstruction_bundle","reconstruction_digest",reconstruction),
        ("odes_package","odes_package_digest",odes.get("odes_package")),
        ("recipient_validation","odes_validation_digest",odes.get("recipient_validation")),
        ("successor_packet","successor_packet_digest",{k:v for k,v in successor.items() if k!="packet_digest"}),
    )
    for name,ref,value in artifacts:
        require(isinstance(value,dict) and bool(value),f"missing required {name}")
        actual=digest(value)
        require(commitments.get(name)==actual,f"{name} actual content commitment mismatch/missing")
        require(refs.get(ref)==actual,f"{name} actual content reference mismatch/missing")
        if name=="successor_packet":
            require(successor.get("packet_digest")==actual,"successor actual content digest mismatch")
    require(sha256(reconstruction)==replay_digest==odes_replay_digest,
            "actual Replay canonical digest differs from Evidence Pack/ODES")
    package=odes["odes_package"]
    policy={
        "now":"2026-10-06T00:00:00Z", "purpose":"audit",
        "relying_party":"recipient.example.org", "status_inputs":{},
        "supported_profiles":[package["profile"]["implementation_profile"]],
        "trusted_digests":[], "trusted_key_refs":[], "evaluation_scope":"audit",
        "status_max_age_seconds":300, "allow_unauthenticated_informational_inspection":False,
    }
    actual_validation=evaluate_recipient_package(package,policy)
    require(actual_validation==odes.get("recipient_validation"),"fresh ODES validation differs from retained validation")
    require(actual_validation.get("package_content_integrity",{}).get("status")=="pass","fresh ODES content integrity failed")
    for key in ("integrity_authentication_checks","authority_status_and_freshness"):
        require(actual_validation.get(key,{}).get("status")=="unavailable",f"fresh ODES {key} improperly available")


def evaluate_gate(**inputs):
    try:
        return _evaluate_gate(**inputs)
    except (KeyError, TypeError, ValueError, AssertionError) as exc:
        return {"status":"failed", "failures":[f"required evidence malformed or unavailable: {exc}"],
                "normalized":None, "expected":{"complete_required_evidence":True},
                "observed":{"complete_required_evidence":False}}


def _evaluate_gate(*, submitted_proposal, delivery, assessment, execution, retained,
                  transport_evidence, inbox_refs, effect_rows, attempt_rows, pack_dict):
    """The release runner and adversarial regressions share this evidence gate."""
    export=retained["artifact_export"]
    reconstruction=export["reconstruction_bundle"]
    odes=export["odes"]
    successor=export["successor_packet"]
    refs=export["producer_refs"]
    commitments=export["content_commitments"]
    envelope=first_record(reconstruction,"execution_envelope")
    op=envelope["operation"]
    expected_effect_id=execution.get("effect_id")
    expected_decision_id=execution.get("decision_id")
    attempt_identity=refs.get("attempt_identity") or {}
    expected_attempt_id=execution.get("attempt_id")
    facts=dict(odes["odes_package"].get("provenance",{}).get("execution_facts",{}))
    failures=[]

    def require(condition, message):
        if not condition:
            failures.append(message)

    require(export.get("export_profile")=="urn:cognous:profiles:gax-retained-artifacts", "wrong retained artifact profile")
    require(export.get("export_version")=="1.1.0", "wrong current retained artifact version")
    require(delivery.get("transport_state")=="DELIVERED","transport not delivered")
    require(retained.get("producer_refs")==inbox_refs,"retained outer producer references mismatch")
    require(len(effect_rows)==1,f"expected exactly one destination effect, observed {len(effect_rows)}")
    effect=effect_rows[0] if effect_rows else {}
    require(effect.get("effect_id")==expected_effect_id,"destination effect_id differs from retained artifact effect_id")
    require(effect.get("target")==op.get("target"),"destination target differs from authorized operation")
    require(float(effect.get("amount",-1))==float(op.get("amount",-2)),"destination amount differs from authorized operation")
    require(effect.get("unit")==op.get("unit"),"destination unit differs from authorized operation")
    require(json.loads(effect.get("payload_json","null"))==op.get("payload"),"destination payload differs from authorized operation")
    require(effect.get("grant_id")==op.get("grant_id"),"destination grant differs from authorized operation")
    require(effect.get("state")=="applied","destination state is not applied")
    require(execution.get("newly_executed") is True,"recipient execution did not report newly_executed=true")
    require(execution.get("destination_observed")=="applied","recipient destination observation is not applied")
    require(attempt_identity.get("namespace")=="executor","successful execution attempt is not retained in executor namespace")

    original_replay_id=reconstruction.get("bundle_id")
    require(bool(original_replay_id) and refs.get("reconstruction_bundle_id")==original_replay_id,"retained Replay identity mismatch")
    require(bool(commitments.get("reconstruction_bundle")),"retained Replay content commitment unavailable")
    require(commitments.get("reconstruction_bundle")==refs.get("reconstruction_digest"),"retained Replay commitment mismatch")
    require(commitments.get("odes_package")==refs.get("odes_package_digest"),"retained ODES commitment mismatch")
    require(commitments.get("recipient_validation")==refs.get("odes_validation_digest"),"retained ODES validation commitment mismatch")
    require(isinstance(successor,dict),"retained successor artifact unavailable")
    if isinstance(successor,dict):
        require(bool(successor.get("packet_id")) and successor.get("packet_id")==refs.get("successor_packet_id"),"retained successor identity mismatch")
        require(successor.get("packet_digest")==refs.get("successor_packet_digest"),"retained successor digest mismatch")
        require(commitments.get("successor_packet")==successor.get("packet_digest"),"retained successor commitment mismatch")

    odes_effect_ids=[
        x.get("effect_id") for x in facts.get("destination_effects",[])
        if isinstance(x,dict) and x.get("effect_id")
    ]
    require(odes_effect_ids==[expected_effect_id],f"ODES destination effect identity mismatch: {odes_effect_ids}")
    require(expected_attempt_id in (facts.get("attempt_namespaces",{}).get("executor") or facts.get("executor_attempt_ids",[])),
            "ODES executor attempt namespace does not retain the execution attempt")

    pack_replay_ids=[x.get("bundle_id") for x in pack_dict.get("replay_bundles",[]) if isinstance(x,dict)]
    input_artifacts=pack_dict.get("metadata",{}).get("traceable_import",{}).get("input_artifacts",[])
    replay_inputs=[x for x in input_artifacts if x.get("artifact_role")=="reconstruction_bundle"]
    require(pack_replay_ids==[original_replay_id],"Evidence Pack Replay identity differs from retained original Replay")
    require(len(replay_inputs)==1 and replay_inputs[0].get("artifact_id")==original_replay_id,
            "Evidence Pack input identity differs from retained original Replay")
    replay_digest=(replay_inputs[0].get("hash") if replay_inputs else None)
    odes_replay_digest=odes.get("odes_package",{}).get("provenance",{}).get("source_artifacts",{}).get("reconstruction_bundle_digest")
    require(bool(replay_digest) and replay_digest==odes_replay_digest,
            "retained Replay canonical digest differs between Evidence Pack and ODES")

    recipient=odes.get("recipient_validation") or {}
    require(recipient.get("package_content_integrity",{}).get("status")=="pass","retained ODES package integrity did not pass")
    require(recipient.get("integrity_authentication_checks",{}).get("status")=="unavailable",
            "retained ODES evidence incorrectly promoted content integrity to authentication")
    require(recipient.get("authority_status_and_freshness",{}).get("status")=="unavailable",
            "retained ODES evidence incorrectly invented current authority/status evidence")

    require(any(r.get("attempt_id")==expected_attempt_id and r.get("effect_id")==expected_effect_id for r in attempt_rows),
            "destination attempt history lacks retained effect/attempt identity")

    require(successor.get("unresolved_delivery") is False,"successor delivery remains unresolved")
    require(successor.get("pending_effects") == [],"successor has pending or missing effects")
    require(retained.get("result_state")=="original_complete", "retained result is not original_complete")
    require(export.get("state")=="original_complete", "export is not original_complete")
    _check_binding(require, submitted_proposal, execution, reconstruction, refs,
                   transport_evidence, inbox_refs, effect_rows, attempt_rows, facts)
    _check_commitments(require, reconstruction, odes, successor, refs, commitments,
                       replay_digest, odes_replay_digest)

    normalized={
        "transport_state":delivery.get("transport_state"),
        "assessment_handling":assessment.get("permitted_handling"),
        "effect_count":len(effect_rows),
        "operation":{
            "target":effect.get("target"),
            "amount":effect.get("amount"),
            "unit":effect.get("unit"),
            "payload":json.loads(effect.get("payload_json","null")) if effect else None,
            "grant_id":effect.get("grant_id"),
        },
        "destination_state":effect.get("state"),
        "newly_executed":execution.get("newly_executed"),
        "identity_consistent":not failures,
        "executor_attempt_namespace":attempt_identity.get("namespace"),
        "unresolved_delivery":successor.get("unresolved_delivery"),
        "pending_effects":successor.get("pending_effects"),
    }
    continuity={
        "status":"implemented",
        "retained_result_state":retained.get("result_state"),
        "original_replay_artifact_retained":True,
        "reconstruction_bundle_id":original_replay_id,
        "reconstruction_commitment":commitments.get("reconstruction_bundle"),
        "odes_package_commitment":commitments.get("odes_package"),
        "odes_validation_commitment":commitments.get("recipient_validation"),
        "successor_packet_id":refs.get("successor_packet_id"),
        "successor_packet_commitment":commitments.get("successor_packet"),
        "relationship":export.get("lineage",{}).get("relationship"),
    }
    result={
        "status":"passed" if not failures else "failed",
        "failures":failures,
        "expected":{
            "decision_id":expected_decision_id,
            "effect_id":expected_effect_id,
            "executor_attempt_id":expected_attempt_id,
            "executor_attempt_namespace":"executor",
            "operation":{**{k:submitted_proposal[k] for k in ("target","amount","unit","payload")},
                         "grant_id":first_record(reconstruction,"runtime_decision")["binding"]["grant_id"]},
            "unresolved_delivery":False,
            "pending_effects":[],
            "effect_count":1,
            "destination_state":"applied",
            "newly_executed":True,
            "retained_result_state":"original_complete",
            "original_replay_artifact_retained":True,
        },
        "observed":{
            "effect_id":refs.get("effect_id"),
            "decision_id":refs.get("decision_id"),
            "executor_attempt_id":attempt_identity.get("attempt_id"),
            **normalized,
        },
        "normalized":normalized,
        "artifact_continuity":continuity,
        "artifacts":{
            "transport_evidence":"transport-evidence.json",
            "recipient_inbox":"recipient-inbox.json",
            "retained_artifacts":"retained-artifacts.json",
            "reconstruction":"reconstruction-bundle.json",
            "evidence_pack":"governance-evidence-pack.json",
            "odes":"odes-reference.json",
            "successor":"imx-successor.json",
        },
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--replay",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)

    manifest=load_json(args.manifest)
    seed_bundle=load_json(args.replay)
    proposal=runtime_proposal_model(seed_bundle)
    resolver=build_synthetic_resolver(proposal,now=parse_time(EVAL))
    runtime=load_executor_runtime()
    destination=runtime["DurableRefundDestination"](out/"destination")
    exchange_path=out/"gax-exchange.sqlite"
    registry=LocalRegistry({"refund-sender"},{"refund-recipient"},"refund-recipient")
    handler=AcceptedGaxRecipientAdapter(
        bundle=seed_bundle,
        registry=registry,
        evaluation_time=EVAL,
        manifest=manifest,
        exchange_store_path=exchange_path,
        resolver=resolver,
        destination=destination,
        execution_policy_factory=synthetic_refund_policy,
        observation_policy=synthetic_observation_policy(),
        observation_clock=synthetic_observation_clock,
    )
    transport=LocalDurableTransport(
        sender_store_path=out/"transport-sender.sqlite",
        recipient_store_path=out/"transport-recipient.sqlite",
        routes=routes(),
        recipient_handler=handler,
        max_attempts=3,
        base_backoff_seconds=1,
        attempt_id_factory=lambda:"transport-reference-attempt-1",
        ack_id_factory=lambda:"transport-reference-ack-1",
    )
    governed=make_message(seed_bundle,message_id="transport-reference-1")
    transport.queue(
        governed,
        route_id="accepted-gax-local",
        sender_endpoint_ref="local://refund-sender",
        now=EVAL,
        correlation_id="corr-reference",
    )
    delivery=transport.deliver(governed["message_id"],now=EVAL)
    if delivery.get("transport_state")!="DELIVERED":
        raise AssertionError(f"transport did not deliver: {delivery}")

    inbox=transport.recipient_store.inbox_record(governed["message_id"])
    if not inbox:
        raise AssertionError("transport recipient inbox record is missing")
    assessment=json.loads(inbox["assessment_json"]) if inbox.get("assessment_json") else None
    execution=json.loads(inbox["execution_json"]) if inbox.get("execution_json") else None
    if not assessment or not execution:
        raise AssertionError("transported recipient outcome was not retained")

    retained=transport.retained_artifacts(governed["message_id"])
    if retained.get("result_state")!="original_complete":
        raise AssertionError(f"expected original_complete retained artifacts, got {retained}")
    export=retained.get("artifact_export")
    if not isinstance(export,dict):
        raise AssertionError("retained artifact export is unavailable")

    reconstruction=export["reconstruction_bundle"]
    odes={
        "odes_package":export["odes"]["odes_package"],
        "recipient_validation":export["odes"].get("recipient_validation"),
        "exchange_metadata":export["odes"].get("exchange_metadata",{}),
    }
    successor=export["successor_packet"]
    refs=export["producer_refs"]
    commitments=export["content_commitments"]

    reconstruction_path=out/"reconstruction-bundle.json"
    dump(reconstruction_path,reconstruction)
    dump(out/"odes-reference.json",odes)
    dump(out/"imx-successor.json",successor)
    dump(out/"retained-artifacts.json",retained)
    dump(out/"transport-evidence.json",transport.evidence(governed["message_id"]))
    dump(out/"recipient-inbox.json",{
        "message_id":inbox["message_id"],
        "content_commitment":inbox["content_commitment"],
        "received_at":inbox["received_at"],
        "assessment":assessment,
        "execution":execution,
        "producer_refs":json.loads(inbox["producer_refs_json"]) if inbox.get("producer_refs_json") else {},
    })

    pack=build_evidence_pack_from_files(args.manifest,reconstruction_path)
    dump_evidence_pack(pack,out/"governance-evidence-pack.json")
    (out/"governance-evidence-pack.md").write_text(
        render_traceable_markdown(pack),encoding="utf-8"
    )

    effect_rows=rows(Path(destination.path),"effects")
    attempt_rows=rows(Path(destination.path),"attempts")
    gate_inputs=dict(
        submitted_proposal=proposal.model_dump(mode="json", exclude_none=False),
        delivery=delivery, assessment=assessment, execution=execution, retained=retained,
        transport_evidence=transport.evidence(governed["message_id"]),
        inbox_refs=json.loads(inbox["producer_refs_json"]),
        effect_rows=effect_rows, attempt_rows=attempt_rows,
        pack_dict=load_json(out/"governance-evidence-pack.json"),
    )
    dump(out/"gate-inputs.json",gate_inputs)
    result=evaluate_gate(**gate_inputs)
    failures=result["failures"]
    dump(out/"expected-vs-observed.json",result)
    if failures:
        raise AssertionError("; ".join(failures))
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
