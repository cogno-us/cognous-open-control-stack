"""Same-host process-boundary qualification for the pinned Cognous stack.

This suite uses spawn-based OS processes, the pinned public Control Plane/executor
interfaces, and Moltbot Safe's real SQLite destination. Fault hooks only stop at
explicit pre/post commit boundaries; they do not authorize, deduplicate, lock, or
reconcile on behalf of the pinned implementations.
"""
from __future__ import annotations

import copy
import dataclasses
import json
import multiprocessing as mp
import os
import shutil
import sqlite3
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".process-boundary-work"
NOW = datetime(2026, 8, 8, 1, tzinfo=timezone.utc)
WAIT = 20


def _json(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=False)
    return copy.deepcopy(value)


def _rows(db_path: Path, table: str) -> list[dict]:
    with sqlite3.connect(db_path) as con:
        con.row_factory = sqlite3.Row
        return [dict(r) for r in con.execute(f"SELECT * FROM {table} ORDER BY rowid")]


def _all_destination_rows(root: Path) -> dict:
    db = root / "refunds.sqlite3"
    if not db.exists():
        return {"effects": [], "attempts": [], "attempt_events": []}
    return {name: _rows(db, name) for name in ("effects", "attempts", "attempt_events")}


def _pins() -> dict:
    lock = json.loads((ROOT / "component-lock.json").read_text())
    actual = {}
    for name in ("action_manifest", "control_plane", "gax_imx_transport", "moltbot_safe", "replay_bundle"):
        spec = lock["components"][name]
        expected = spec["core_interop_sha"] if name == "moltbot_safe" else spec["sha"]
        actual[name] = expected
        checkout = WORK / name
        got = os.popen(f"git -C '{checkout}' rev-parse HEAD").read().strip()
        assert got == expected, f"{name}: expected {expected}, got {got}"
    return {"hub": "b457b7e1ebcbb323e88e85b913eaafcb5755317a", "components": actual}


def _runtime_inputs(variation: str | None = None, *, max_effects: int = 1):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import load_executor_runtime, runtime_proposal_model
    from experiments.odex_gax_imx_reference.synthetic_fixture import build_synthetic_resolver, synthetic_observation_policy

    runtime = load_executor_runtime()
    cp = runtime["cp"]
    manifest = json.loads((WORK / "action_manifest/examples/refund_integration_v1_1.manifest.json").read_text())
    seed = json.loads((WORK / "replay_bundle/examples/bounded_success_reconstruction_v0_2.json").read_text())
    proposal = runtime_proposal_model(seed)
    manifest["actions"][0]["effect_limits"]["max_effects"] = max_effects
    updates = {"manifest_digest": cp.commitment(manifest)}
    if variation:
        updates.update({"correlation_id": variation, "run_id": f"process-boundary-{variation}"})
    proposal = proposal.model_copy(update=updates)
    resolver = build_synthetic_resolver(proposal, now=NOW)
    context = resolver.contexts[proposal.authority_context_ref]
    context["requirement"]["permissions"][0]["max_effects"] = max_effects
    context["grant"]["permissions"][0]["max_effects"] = max_effects
    approval_ref = context["grant"]["approval_refs"][0]
    resolver.approvals[approval_ref] = resolver.approvals[approval_ref].model_copy(update={
        "proposal_commitment": cp.commitment(_json(proposal)),
    })
    return runtime, cp, manifest, proposal, resolver, synthetic_observation_policy()


def _build_envelope(runtime, proposal, resolver, decision):
    binding = decision.binding
    context = resolver.authority_context(proposal.authority_context_ref)
    values = _json(proposal)
    values.update({
        "institution_id": context["institution"]["institution_id"],
        "authority_domain": context["institution"]["authority_domain"],
        "authority_context_id": proposal.authority_context_ref,
        "proposal_commitment": binding.proposal_commitment,
        "grant_id": binding.grant_id,
        "grant_revision": binding.grant_revision,
        "effective_max_effects": binding.effective_max_effects,
        "requested_permissions": tuple(proposal.requested_permissions),
    })
    op = runtime["ExecutionOperation"](**{f.name: values[f.name] for f in dataclasses.fields(runtime["ExecutionOperation"])})
    return runtime["ExecutionEnvelope"]("0.2.0", decision.decision_id, decision.effect_id, op)


def _prepare_case(case_root: Path, *, record_name: str, variation: str | None = None, max_effects: int = 1) -> dict:
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_refund_policy
    runtime, cp, manifest, proposal, resolver, observation_policy = _runtime_inputs(variation, max_effects=max_effects)
    destination = runtime["DurableRefundDestination"](case_root / "destination")
    records = cp.BoundedRecordStore(case_root / record_name, "process-boundary")
    workflow = cp.BoundedAuthorizationWorkflow(manifest=manifest, resolver=resolver, destination=destination, records=records, observation_policy=observation_policy)
    decision = workflow.decide(proposal, now=NOW)
    assert decision.result == "authorized", decision.reasons
    envelope = _build_envelope(runtime, proposal, resolver, decision)
    policy = dataclasses.replace(synthetic_refund_policy(envelope.operation), max_effects=decision.binding.effective_max_effects)
    return {
        "proposal": _json(proposal), "decision": _json(decision), "envelope": _json(envelope),
        "record_path": str(case_root / record_name), "destination_root": str(case_root / "destination"),
        "variation": variation, "max_effects": max_effects, "policy": _json(policy),
        "effect_id": decision.effect_id, "decision_id": decision.decision_id,
        "grant_id": decision.binding.grant_id,
    }


def _open_case(spec: dict):
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_refund_policy
    runtime, cp, manifest, proposal, resolver, observation_policy = _runtime_inputs(spec.get("variation"), max_effects=spec["max_effects"])
    destination = runtime["DurableRefundDestination"](spec["destination_root"])
    records = cp.BoundedRecordStore(spec["record_path"], "process-boundary")
    decision = records.decision(spec["decision_id"])
    if decision is None:
        raise RuntimeError("persisted authorized decision unavailable")
    envelope = _build_envelope(runtime, proposal, resolver, decision)
    policy = dataclasses.replace(synthetic_refund_policy(envelope.operation), max_effects=decision.binding.effective_max_effects)
    workflow = cp.BoundedAuthorizationWorkflow(manifest=manifest, resolver=resolver, destination=destination, records=records, observation_policy=observation_policy)
    executor = runtime["PinnedControlPlaneExecutor"](workflow=workflow, destination=destination, policy=policy, observation_clock=lambda: NOW)
    return runtime, cp, proposal, resolver, destination, workflow, decision, envelope, executor


def _dispatch_worker(spec: dict, start, conn, mode: str, continue_event, output: str):
    pid = os.getpid()
    events = [{"seq": 1, "event": "initialized", "pid": pid}]
    try:
        _, _, proposal, _, destination, _, decision, envelope, executor = _open_case(spec)
        conn.send({"event": "initialized", "pid": pid})
        if not start.wait(WAIT):
            raise TimeoutError("start barrier not released")
        events.append({"seq": 2, "event": "start_released", "pid": pid})
        if mode in {"die_before_commit", "control_before_commit", "die_after_commit"}:
            original = destination.commit
            def hooked(snapshot, *, simulate=None):
                if mode in {"die_before_commit", "control_before_commit"}:
                    conn.send({"event": "pre_commit", "pid": pid, "effect_id": snapshot.effect_id})
                    if not continue_event.wait(WAIT):
                        raise TimeoutError("pre-commit continuation not released")
                    events.append({"seq": len(events)+1, "event": "pre_commit_released", "pid": pid})
                    return original(snapshot, simulate=simulate)
                result = original(snapshot, simulate=simulate)
                conn.send({"event": "post_commit", "pid": pid, "effect_id": snapshot.effect_id})
                conn.close()
                os._exit(91)
            destination.commit = hooked
        result = executor.execute(envelope=envelope, proposal=proposal, decision=decision, now=NOW)
        events.append({"seq": len(events)+1, "event": "execute_returned", "pid": pid})
        Path(output).write_text(json.dumps({"pid": pid, "result": _json(result), "events": events}, indent=2, sort_keys=True))
        conn.send({"event": "done", "pid": pid})
    except BaseException as exc:
        Path(output).write_text(json.dumps({"pid": pid, "error": repr(exc), "traceback": traceback.format_exc(), "events": events}, indent=2, sort_keys=True))
        try:
            conn.send({"event": "error", "pid": pid, "error": repr(exc)})
        except Exception:
            pass
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _spawn(spec: dict, *, mode="normal"):
    ctx = mp.get_context("spawn")
    start = ctx.Event(); cont = ctx.Event()
    parent, child = ctx.Pipe(duplex=False)
    output = str(Path(spec["record_path"]).with_suffix(f".{mode}.{os.getpid()}.result.json"))
    proc = ctx.Process(target=_dispatch_worker, args=(spec, start, child, mode, cont, output))
    proc.start()
    msg = parent.recv() if parent.poll(WAIT) else {"event": "timeout_initialization"}
    assert msg.get("event") == "initialized", msg
    return proc, start, cont, parent, Path(output), [msg]


def _recv(conn, expected: str) -> dict:
    assert conn.poll(WAIT), f"timed out waiting for {expected}"
    msg = conn.recv()
    assert msg.get("event") == expected, msg
    return msg


def _join(proc):
    proc.join(WAIT)
    if proc.is_alive():
        proc.terminate(); proc.join(WAIT)
        pytest.fail("child process exceeded bounded wait")
    return proc.exitcode


def _result(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def _history(path: Path) -> dict:
    if not path.exists():
        return {"unavailable": True}
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"parse_error": repr(exc), "raw": path.read_text(errors="replace")}


def _write_evidence(name: str, payload: dict):
    out = Path(os.environ["PROCESS_BOUNDARY_RESULTS_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": "1.0", "scenario_id": name, "repetition": int(os.environ.get("PROCESS_BOUNDARY_REPETITION", "0")), "pins": _pins(), **payload}
    (out / f"{name}.json").write_text(json.dumps(payload, indent=2, sort_keys=True))


def _assert_effect_matches(effect: dict, envelope: dict):
    op = envelope["operation"]
    assert effect["effect_id"] == envelope["effect_id"]
    assert effect["grant_id"] == op["grant_id"]
    assert effect["target"] == op["target"]
    assert float(effect["amount"]) == float(op["amount"])
    assert effect["unit"] == op["unit"]
    assert json.loads(effect["payload_json"]) == op["payload"]


def test_duplicate_operation_across_processes(tmp_path):
    root = tmp_path / "duplicate"; root.mkdir()
    master = _prepare_case(root, record_name="master.json")
    for name in ("a.json", "b.json"):
        shutil.copy2(root / "master.json", root / name)
    a = {**master, "record_path": str(root / "a.json")}
    b = {**master, "record_path": str(root / "b.json")}
    pa, sa, ca, xa, oa, ea = _spawn(a)
    pb, sb, cb, xb, ob, eb = _spawn(b)
    before = _all_destination_rows(root / "destination")
    sa.set(); sb.set()
    exits = [_join(pa), _join(pb)]
    ra, rb = _result(oa), _result(ob)
    after = _all_destination_rows(root / "destination")
    results = [ra.get("result", {}), rb.get("result", {})]
    passed = exits == [0, 0] and len(after["effects"]) == 1 and sorted(r.get("newly_executed") for r in results) == [False, True]
    _write_evidence("duplicate-operation-across-processes", {
        "classification": "supported invariant passed" if passed else "required invariant failed",
        "processes": [{"pid": pa.pid, "exit_code": exits[0]}, {"pid": pb.pid, "exit_code": exits[1]}],
        "barrier_sequence": ea + eb + [{"event":"simultaneous_start_release"}],
        "store_paths": {"destination": master["destination_root"], "control_plane": [a["record_path"], b["record_path"]]},
        "identities": {"decision_id": master["decision_id"], "effect_id": master["effect_id"], "grant_id": master["grant_id"]},
        "destination_before": before, "destination_after": after, "worker_results": results,
        "retained_record_histories": [_history(Path(a["record_path"])), _history(Path(b["record_path"]))],
        "dispatch_attempts": len(after["attempts"]), "committed_effects": len(after["effects"]),
    })
    assert passed, {"exits": exits, "results": results, "after": after}
    _assert_effect_matches(after["effects"][0], master["envelope"])


def test_competing_effects_one_effect_grant_across_processes(tmp_path):
    root = tmp_path / "competing"; root.mkdir()
    a = _prepare_case(root, record_name="a.json", variation="operation-a", max_effects=1)
    b = _prepare_case(root, record_name="b.json", variation="operation-b", max_effects=1)
    assert a["grant_id"] == b["grant_id"] and a["effect_id"] != b["effect_id"]
    pa, sa, ca, xa, oa, ea = _spawn(a)
    pb, sb, cb, xb, ob, eb = _spawn(b)
    before = _all_destination_rows(root / "destination")
    sa.set(); sb.set()
    exits=[_join(pa),_join(pb)]
    ra, rb = _result(oa), _result(ob)
    after = _all_destination_rows(root / "destination")
    passed = exits == [0,0] and len(after["effects"]) == 1
    _write_evidence("competing-effects-one-effect-grant", {
        "classification": "supported invariant passed" if passed else "required invariant failed",
        "processes": [{"pid":pa.pid,"exit_code":exits[0]},{"pid":pb.pid,"exit_code":exits[1]}],
        "barrier_sequence":ea+eb+[{"event":"simultaneous_start_release"}],
        "store_paths":{"destination":a["destination_root"],"control_plane":[a["record_path"],b["record_path"]]},
        "identities":{"grant_id":a["grant_id"],"operation_a":{"decision_id":a["decision_id"],"effect_id":a["effect_id"]},"operation_b":{"decision_id":b["decision_id"],"effect_id":b["effect_id"]}},
        "destination_before":before,"destination_after":after,"worker_results":[ra.get("result",{}),rb.get("result",{})],
        "retained_record_histories":[_history(Path(a["record_path"])),_history(Path(b["record_path"]))],
        "dispatch_attempts":len(after["attempts"]),"committed_effects":len(after["effects"]),
    })
    assert passed, {"exits":exits,"a":ra,"b":rb,"after":after}
    winner = after["effects"][0]
    source = a if winner["effect_id"] == a["effect_id"] else b
    _assert_effect_matches(winner, source["envelope"])


def test_process_death_after_destination_commit(tmp_path):
    root=tmp_path/"after-commit"; root.mkdir()
    spec=_prepare_case(root,record_name="cp.json")
    p,s,c,x,o,events=_spawn(spec,mode="die_after_commit")
    before=_all_destination_rows(root/"destination")
    s.set()
    events.append(_recv(x,"post_commit"))
    exit_code=_join(p)
    after_death=_all_destination_rows(root/"destination")
    pr,sr,cr,xr,orr,er=_spawn(spec)
    sr.set()
    restart_exit=_join(pr)
    recovered=_result(orr)
    final=_all_destination_rows(root/"destination")
    rr=recovered.get("result",{})
    no_replacement=len(final["effects"])==1 and final["effects"]==after_death["effects"] and rr.get("newly_executed") is False and rr.get("observed_state")=="applied"
    _write_evidence("process-death-after-destination-commit",{
        "classification":"supported invariant passed" if no_replacement and restart_exit==0 else "required invariant failed",
        "processes":[{"pid":p.pid,"exit_code":exit_code,"role":"killed-after-commit"},{"pid":pr.pid,"exit_code":restart_exit,"role":"restart"}],
        "barrier_sequence":events+er,
        "store_paths":{"destination":spec["destination_root"],"control_plane":spec["record_path"]},
        "identities":{"decision_id":spec["decision_id"],"effect_id":spec["effect_id"],"grant_id":spec["grant_id"]},
        "destination_before":before,"destination_after_death":after_death,"destination_after_restart":final,
        "restart_result":rr,"retained_record_history":_history(Path(spec["record_path"])),
        "dispatch_attempts":len(final["attempts"]),"committed_effects":len(final["effects"]),
        "recovery_outcome":"reconciled existing effect" if rr.get("observed_state")=="applied" else "safely unresolved",
    })
    assert exit_code==91 and restart_exit==0 and no_replacement, {"exit":exit_code,"restart":restart_exit,"result":rr,"final":final}
    _assert_effect_matches(final["effects"][0],spec["envelope"])


def test_process_death_before_commit(tmp_path):
    control_root=tmp_path/"precommit-control"; control_root.mkdir()
    control=_prepare_case(control_root,record_name="cp.json")
    pc,sc,cc,xc,oc,ec=_spawn(control,mode="control_before_commit")
    sc.set()
    ec.append(_recv(xc,"pre_commit"))
    control_mid=_all_destination_rows(control_root/"destination")
    cc.set()
    control_exit=_join(pc)
    control_after=_all_destination_rows(control_root/"destination")
    assert control_exit==0 and not control_mid["effects"] and len(control_after["effects"])==1

    root=tmp_path/"before-commit"; root.mkdir()
    spec=_prepare_case(root,record_name="cp.json")
    p,s,c,x,o,events=_spawn(spec,mode="die_before_commit")
    before=_all_destination_rows(root/"destination")
    s.set()
    events.append(_recv(x,"pre_commit"))
    at_barrier=_all_destination_rows(root/"destination")
    cp_at_barrier=_history(Path(spec["record_path"]))
    p.terminate()
    exit_code=_join(p)
    after_death=_all_destination_rows(root/"destination")
    pr,sr,cr,xr,orr,er=_spawn(spec)
    sr.set()
    restart_exit=_join(pr)
    recovered=_result(orr)
    final=_all_destination_rows(root/"destination")
    rr=recovered.get("result",{})
    no_replacement=(not final["effects"] and len(final["attempts"])==len(after_death["attempts"]) and rr.get("newly_executed") is False and rr.get("status")=="denied")
    _write_evidence("process-death-before-commit",{
        "classification":"supported invariant passed" if no_replacement and restart_exit==0 else "required invariant failed",
        "positive_control":{"pid":pc.pid,"exit_code":control_exit,"barrier_sequence":ec,"destination_at_barrier":control_mid,"destination_after_release":control_after},
        "processes":[{"pid":p.pid,"exit_code":exit_code,"role":"terminated-pre-commit"},{"pid":pr.pid,"exit_code":restart_exit,"role":"restart"}],
        "barrier_sequence":events+er,
        "store_paths":{"destination":spec["destination_root"],"control_plane":spec["record_path"]},
        "identities":{"decision_id":spec["decision_id"],"effect_id":spec["effect_id"],"grant_id":spec["grant_id"]},
        "destination_before":before,"destination_at_barrier":at_barrier,"destination_after_death":after_death,"destination_after_restart":final,
        "control_plane_at_barrier":cp_at_barrier,"restart_result":rr,"retained_record_history":_history(Path(spec["record_path"])),
        "dispatch_attempts":len(final["attempts"]),"committed_effects":len(final["effects"]),
        "recovery_outcome":"denied after observed absence with retained prior attempt; absence did not create retry permission" if rr.get("status")=="denied" else "unsupported/unresolved",
    })
    assert restart_exit==0 and no_replacement, {"restart":restart_exit,"result":rr,"final":final}


def _store_append_worker(path: str, field: str, token: str, ready, go, conn):
    from agent_control_plane.bounded import BoundedRecordStore, RuntimeDecision, EffectAttempt, ReconciliationResult
    pid=os.getpid()
    store=BoundedRecordStore(path,"shared-store")
    if field=="decisions":
        value=RuntimeDecision(decision_id=f"decision-{token}",effect_id=f"effect-{token}",result="hold",reasons=[token],decided_at=NOW.isoformat())
    elif field=="attempts":
        value=EffectAttempt(attempt_id=f"attempt-{token}",effect_id=f"effect-{token}",decision_id=f"decision-{token}",started_at=NOW.isoformat(),status="attempted")
    else:
        value=ReconciliationResult(effect_id=f"effect-{token}",reconciled_at=NOW.isoformat(),result="hold",retry_eligible=False,reasons=[token])
    ready.set()
    conn.send({"event":"ready","pid":pid,"field":field,"token":token})
    if not go.wait(WAIT):
        raise TimeoutError("store start barrier not released")
    error=None
    try:
        getattr(store,{"decisions":"append_decision","attempts":"append_attempt","reconciliations":"append_reconciliation"}[field])(value)
    except BaseException as exc:
        error=repr(exc)
    conn.send({"event":"done","pid":pid,"field":field,"token":token,"error":error})
    conn.close()


def test_shared_control_plane_store_behavior(tmp_path):
    ctx=mp.get_context("spawn")
    path=tmp_path/"shared-control-plane.json"
    from agent_control_plane.bounded import BoundedRecordStore
    BoundedRecordStore(path,"shared-store")
    rounds=[]; observed_loss=False
    for field in ("decisions","attempts","reconciliations"):
        for round_no in range(1,5):
            go=ctx.Event(); entries=[]; procs=[]
            for side in ("a","b"):
                ready=ctx.Event(); parent,child=ctx.Pipe(duplex=False)
                token=f"{field}-{round_no}-{side}"
                proc=ctx.Process(target=_store_append_worker,args=(str(path),field,token,ready,go,child))
                proc.start()
                assert ready.wait(WAIT)
                entries.append((proc,parent,token)); procs.append(proc)
            messages=[]
            for proc,parent,token in entries:
                messages.append(_recv(parent,"ready"))
            before=_history(path)
            go.set()
            for proc,parent,token in entries:
                messages.append(_recv(parent,"done"))
            exits=[_join(p) for p in procs]
            after=_history(path)
            values=after.get(field,[]) if isinstance(after,dict) else []
            present={token: any(token in json.dumps(v) for v in values) for _,_,token in entries}
            if not all(present.values()) or any(m.get("error") for m in messages) or exits!=[0,0]:
                observed_loss=True
            rounds.append({"field":field,"round":round_no,"pids":[p.pid for p in procs],"exit_codes":exits,"messages":messages,"present":present,"record_before":before,"record_after":after})
    final=_history(path)
    _write_evidence("shared-control-plane-store",{
        "classification":"unsupported boundary characterized",
        "processes":[{"pid":p} for r in rounds for p in r["pids"]],
        "barrier_sequence":[{"field":r["field"],"round":r["round"],"event":"paired start after both ready"} for r in rounds],
        "store_paths":{"control_plane":str(path)},"observed_loss_or_error":observed_loss,
        "rounds":rounds,"retained_record_history":final,
        "support_boundary":"BoundedRecordStore uses threading.RLock and a fixed .tmp/os.replace write sequence; no interprocess lock or transactional append contract is exposed.",
        "destination_sqlite_inference":"none; SQLite destination serialization is not treated as protection for this JSON store.",
    })
    assert isinstance(final,dict), "shared store became unreadable; evidence retained"
