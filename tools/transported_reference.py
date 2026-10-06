#!/usr/bin/env python3
"""Generate and enforce one transported Cognous reference workflow.

The operation is executed only through LocalDurableTransport ->
AcceptedGaxRecipientAdapter. Evidence is reconstructed from the retained
transport/GAX records for that same operation; no second direct run_exchange
call is made by this hub script.
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
    TransactionalExchangeStore,
    _build_resolver,
    export_odes_reference,
    import_replay_bundle,
    load_actual_pinned_moltbot_helpers,
    make_message,
    make_successor_packet,
    parse_time,
    reconstruction_dict,
    runtime_proposal_model,
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

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--replay",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)

    manifest=load_json(args.manifest)
    bundle=load_json(args.replay)
    proposal=runtime_proposal_model(bundle)
    resolver=_build_resolver(proposal,now=parse_time(EVAL))
    h=load_actual_pinned_moltbot_helpers()
    destination=h.DurableRefundDestination(out/"destination")
    exchange_path=out/"gax-exchange.sqlite"
    registry=LocalRegistry({"refund-sender"},{"refund-recipient"},"refund-recipient")
    handler=AcceptedGaxRecipientAdapter(
        bundle=bundle,
        registry=registry,
        evaluation_time=EVAL,
        manifest=manifest,
        exchange_store_path=exchange_path,
        resolver=resolver,
        destination=destination,
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
    governed=make_message(bundle,message_id="transport-reference-1")
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
    producer_refs=json.loads(inbox["producer_refs_json"]) if inbox.get("producer_refs_json") else {}
    if not assessment or not execution:
        raise AssertionError("transported recipient outcome was not retained")

    association=TransactionalExchangeStore(exchange_path).workflow_for_message(governed)
    if association is None:
        raise AssertionError(
            "accepted transport/GAX interface did not retain the workflow association "
            "required to reconstruct Control Plane/executor evidence"
        )
    for required in ("cp_record","proposal","moltbot","decision_id","effect_id","attempt_id"):
        if not association.get(required):
            raise AssertionError(f"retained workflow association missing {required}")

    reconstructed=import_replay_bundle(
        association["cp_record"],
        association["proposal"],
        association["moltbot"],
    )
    reconstruction=reconstruction_dict(reconstructed)
    odes=export_odes_reference(manifest,reconstruction)
    facts=dict(odes["odes_package"].get("provenance",{}).get("execution_facts",{}))
    facts["pending_effects"]=[] if facts.get("destination_observed")=="applied" else [
        x.get("effect_id") for x in facts.get("destination_effects",[]) if x.get("effect_id")
    ]
    facts["unresolved_delivery"]=bool(
        facts.get("destination_observed") in {"partial","unknown"} or
        facts.get("acknowledgement_summary")=="unknown"
    )
    successor=make_successor_packet(
        governed,
        facts=facts,
        state_version=1,
        current_bundle=reconstruction,
    )

    reconstruction_path=out/"reconstruction-bundle.json"
    dump(reconstruction_path,reconstruction)
    dump(out/"odes-reference.json",odes)
    dump(out/"imx-successor.json",successor)
    dump(out/"transport-evidence.json",transport.evidence(governed["message_id"]))
    dump(out/"recipient-inbox.json",{
        "message_id":inbox["message_id"],
        "content_commitment":inbox["content_commitment"],
        "received_at":inbox["received_at"],
        "assessment":assessment,
        "execution":execution,
        "producer_refs":producer_refs,
    })

    pack=build_evidence_pack_from_files(args.manifest,reconstruction_path)
    dump_evidence_pack(pack,out/"governance-evidence-pack.json")
    (out/"governance-evidence-pack.md").write_text(
        render_traceable_markdown(pack),encoding="utf-8"
    )

    effect_rows=rows(Path(destination.path),"effects")
    attempt_rows=rows(Path(destination.path),"attempts")
    op=association["request"]["operation"]
    expected_effect_id=association["effect_id"]
    expected_attempt_id=association["attempt_id"]
    failures=[]

    def require(condition, message):
        if not condition:
            failures.append(message)

    require(len(effect_rows)==1,f"expected exactly one destination effect, observed {len(effect_rows)}")
    effect=effect_rows[0] if effect_rows else {}
    require(effect.get("effect_id")==expected_effect_id,"destination effect_id differs from retained workflow effect_id")
    require(effect.get("target")==op.get("target"),"destination target differs from authorized operation")
    require(float(effect.get("amount",-1))==float(op.get("amount",-2)),"destination amount differs from authorized operation")
    require(effect.get("unit")==op.get("unit"),"destination unit differs from authorized operation")
    require(json.loads(effect.get("payload_json","null"))==op.get("payload"),"destination payload differs from authorized operation")
    require(effect.get("grant_id")==op.get("grant_id"),"destination grant differs from authorized operation")
    require(effect.get("state")=="applied","destination state is not applied")
    require(execution.get("newly_executed") is True,"recipient execution did not report newly_executed=true")
    require(execution.get("destination_observed")=="applied","recipient destination observation is not applied")
    require(facts.get("unresolved_delivery") is False,"transported successful operation is incorrectly unresolved")
    require(producer_refs.get("effect_id")==expected_effect_id,"transport producer effect_id mismatch")
    require(producer_refs.get("decision_id")==association["decision_id"],"transport producer decision_id mismatch")
    require(producer_refs.get("executor_attempt_id")==expected_attempt_id,"transport producer executor attempt_id mismatch")
    require(execution.get("effect_id")==expected_effect_id,"recipient execution effect_id mismatch")
    require(execution.get("decision_id")==association["decision_id"],"recipient execution decision_id mismatch")
    require(execution.get("attempt_id")==expected_attempt_id,"recipient execution attempt_id mismatch")

    odes_effect_ids=[
        x.get("effect_id") for x in facts.get("destination_effects",[])
        if isinstance(x,dict) and x.get("effect_id")
    ]
    require(odes_effect_ids==[expected_effect_id],f"ODES destination effect identity mismatch: {odes_effect_ids}")
    require(facts.get("executor_attempt_ids")==[expected_attempt_id],"ODES executor attempt identity mismatch")
    # The accepted transport adapter retains the original GAX-generated Replay bundle ID
    # but not the original Replay artifact itself. Reconstruct a new Replay artifact only
    # from the retained CP/executor records, preserve both identities, and enforce the
    # regenerated artifact's identity/digest through Evidence Pack and ODES.
    original_replay_id=producer_refs.get("reconstruction_bundle_id")
    regenerated_replay_id=reconstruction.get("bundle_id")
    pack_dict=load_json(out/"governance-evidence-pack.json")
    pack_replay_ids=[x.get("bundle_id") for x in pack_dict.get("replay_bundles",[]) if isinstance(x,dict)]
    input_artifacts=pack_dict.get("metadata",{}).get("traceable_import",{}).get("input_artifacts",[])
    replay_inputs=[x for x in input_artifacts if x.get("artifact_role")=="reconstruction_bundle"]
    require(bool(original_replay_id),"transport did not retain original GAX Replay bundle identifier")
    require(bool(regenerated_replay_id),"regenerated Replay bundle lacks bundle_id")
    require(pack_replay_ids==[regenerated_replay_id],"Evidence Pack Replay bundle identity differs from regenerated Replay")
    require(len(replay_inputs)==1 and replay_inputs[0].get("artifact_id")==regenerated_replay_id,
            "Evidence Pack input artifact identity differs from regenerated Replay")
    replay_digest=(replay_inputs[0].get("hash") if replay_inputs else None)
    odes_replay_digest=odes.get("odes_package",{}).get("provenance",{}).get("source_artifacts",{}).get("reconstruction_bundle_digest")
    require(bool(replay_digest) and replay_digest==odes_replay_digest,
            "Replay canonical digest differs between Evidence Pack and ODES")
    require(producer_refs.get("successor_packet_id")==successor.get("packet_id"),"successor identity differs from transport producer reference")
    require(any(r.get("attempt_id")==expected_attempt_id and r.get("effect_id")==expected_effect_id for r in attempt_rows),
            "destination attempt history lacks retained workflow effect/attempt identity")

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
        "unresolved_delivery":facts.get("unresolved_delivery"),
        "identity_consistent":not failures,
    }
    retention_gap={
        "status":"implemented_with_disclosed_gap",
        "original_gax_reconstruction_bundle_id":original_replay_id,
        "original_gax_reconstruction_artifact_retained_by_transport":False,
        "regenerated_reconstruction_bundle_id":regenerated_replay_id,
        "relationship":"regenerated_from_retained_control_plane_and_executor_records",
        "reason":"AcceptedGaxRecipientAdapter retains the original Replay bundle identifier but does not expose or retain the original Replay artifact in transport evidence."
    }
    result={
        "status":"passed" if not failures else "failed",
        "failures":failures,
        "expected":{
            "effect_count":1,
            "operation":{
                "target":op.get("target"),
                "amount":op.get("amount"),
                "unit":op.get("unit"),
                "payload":op.get("payload"),
                "grant_id":op.get("grant_id"),
            },
            "destination_state":"applied",
            "newly_executed":True,
            "unresolved_delivery":False,
        },
        "observed":{
            "effect_id":expected_effect_id,
            "decision_id":association["decision_id"],
            "executor_attempt_id":expected_attempt_id,
            **normalized,
        },
        "normalized":normalized,
        "replay_retention":retention_gap,
        "artifacts":{
            "transport_evidence":"transport-evidence.json",
            "recipient_inbox":"recipient-inbox.json",
            "reconstruction":"reconstruction-bundle.json",
            "evidence_pack":"governance-evidence-pack.json",
            "odes":"odes-reference.json",
            "successor":"imx-successor.json",
        },
    }
    dump(out/"expected-vs-observed.json",result)
    if failures:
        raise AssertionError("; ".join(failures))
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
