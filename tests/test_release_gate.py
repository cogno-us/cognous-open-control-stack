import json
from pathlib import Path

from tools.release_gate import resolve_matrix

ROOT=Path(__file__).resolve().parents[1]


def test_nonexistent_required_reference_blocks_release():
    matrix={
        "scenarios":[{
            "id":"missing-required",
            "required":True,
            "coverage_scope":"component",
            "tests":["suite::test_does_not_exist"],
            "expected":"must resolve",
        }]
    }
    cases=[
        {"suite":"suite","repetition":1,"name":"test_real","test_id":"suite::test_real","status":"passed","reason":"","evidence_path":"run-1/suite.xml","classname":"x"},
        {"suite":"suite","repetition":2,"name":"test_real","test_id":"suite::test_real","status":"passed","reason":"","evidence_path":"run-2/suite.xml","classname":"x"},
    ]
    ok,resolved=resolve_matrix(matrix,cases)
    assert ok is False
    assert resolved[0]["status"]=="missing"
    assert len(resolved[0]["missing"])==2


def test_interface_cleanup_lock_uses_declared_revisions():
    lock=json.loads((ROOT/"component-lock.json").read_text(encoding="utf-8"))
    components=lock["components"]
    assert lock["qualification_status"]=="accepted"
    gax=components["gax_imx_transport"]
    assert gax["acceptance_status"]=="accepted_merged"
    assert gax["accepted_sha"]=="9984d9011568ccdf3d562fa9760ad41368947b34"
    assert gax["sha"]=="9984d9011568ccdf3d562fa9760ad41368947b34"
    assert gax["reviewed_source_sha"]=="ee2dde3062468b07723d92a040bc1f0bafafd50e"
    assert gax["merged_pr"]==8
    assert gax["previous_acceptance"]["sha"]=="c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df"
    assert components["control_plane"]["sha"]=="248d899634d9db3518e831bc7ab568a48733f825"
    assert components["moltbot_safe"]["core_interop_sha"]=="177354e959cc78c59c1a776f018cfbfbf28c927b"
    assert components["replay_bundle"]["sha"]=="043830b56595cecddfa65c064afd1c0b95e64792"
    assert components["odes"]["sha"]=="0486b645e99c46d9cd16ca34b1ba7c653a6b3024"
    assert components["governance_evidence_pack"]["sha"]=="de6b9e071df49fc3e0c1254d39b5c94cced554f0"
    interfaces=components["governance_evidence_pack"]["interfaces"]
    assert "manifest/reconstruction transformation 0.3.1 (current persistence generation)" in interfaces
    assert "manifest/reconstruction transformation 0.3.0 (previous selected producer-2.0.0 generation)" in interfaces
    assert "manifest/reconstruction transformation 0.2.6 (historical legacy transformation)" in interfaces
    assert any("GAX retained artifacts 1.1.0"==x for x in gax["interfaces"])

def test_required_artifact_and_timeout_recovery_qualification_scenarios_present():
    matrix=json.loads((ROOT/"scenarios/acceptance-matrix.json").read_text(encoding="utf-8"))
    scenarios={item["id"]:item for item in matrix["scenarios"]}
    required={
        "original_artifact_continuity",
        "post_effect_evidence_recovery",
        "timeout_retry_qualification",
    }
    assert required <= set(scenarios)
    for scenario_id in required:
        assert scenarios[scenario_id]["required"] is True
        assert scenarios[scenario_id]["tests"]

# Exercise the very same function used by the transported release runner, using
# evidence produced by a real pinned transport execution (never mocked digests).
import copy
import os
import subprocess
import sys
import pytest


@pytest.fixture(scope="module")
def transported_inputs(tmp_path_factory):
    out=tmp_path_factory.mktemp("transported-gate")
    work=ROOT/".reference-work"
    subprocess.run([
        sys.executable,str(ROOT/"tools/transported_reference.py"),
        "--manifest",str(work/"action_manifest/examples/refund_integration_v1_1.manifest.json"),
        "--replay",str(work/"replay_bundle/examples/bounded_success_reconstruction_v0_2.json"),
        "--out",str(out),
    ],check=True,capture_output=True,text=True,env=os.environ.copy())
    return json.loads((out/"gate-inputs.json").read_text())


def evaluate(inputs):
    from tools.transported_reference import evaluate_gate
    return evaluate_gate(**inputs)


def test_real_transported_gate_passes(transported_inputs):
    result=evaluate(transported_inputs)
    assert result["status"]=="passed",result["failures"]
    assert result["normalized"]["unresolved_delivery"] is False
    assert result["normalized"]["pending_effects"]==[]


@pytest.mark.parametrize("source",["execution","inbox_refs","transport","retained","decision","envelope","result","attempt","destination"])
@pytest.mark.parametrize("identity",["decision_id","effect_id"])
def test_substituted_identities_fail(transported_inputs,source,identity):
    data=copy.deepcopy(transported_inputs)
    export=data["retained"]["artifact_export"]
    record_types={"decision":"runtime_decision","envelope":"execution_envelope","result":"execution_result","attempt":"destination_attempt"}
    if source in record_types:
        target=next(r["data"] for r in export["reconstruction_bundle"]["records"] if r["record_type"]==record_types[source])
    elif source=="transport":target=data["transport_evidence"]["producer_refs"]
    elif source=="retained":target=export["producer_refs"]
    elif source=="destination":target=data["attempt_rows"][0]
    else:target=data[source]
    target[identity]="substituted"
    assert evaluate(data)["status"]=="failed"


@pytest.mark.parametrize("source",["execution","inbox_refs","transport","retained","destination","replay"])
def test_substituted_attempt_fails(transported_inputs,source):
    data=copy.deepcopy(transported_inputs); export=data["retained"]["artifact_export"]
    if source=="execution":data[source]["attempt_id"]="substituted"
    elif source=="destination":data["attempt_rows"][0]["attempt_id"]="substituted"
    elif source=="replay":
        next(r["data"] for r in export["reconstruction_bundle"]["records"] if r["record_type"]=="execution_result")["attempt_id"]="substituted"
    else:
        target=export["producer_refs"] if source=="retained" else data["transport_evidence"]["producer_refs"] if source=="transport" else data[source]
        target["attempt_identity"]["attempt_id"]="substituted"
    assert evaluate(data)["status"]=="failed"


@pytest.mark.parametrize("artifact,ref",[("reconstruction_bundle","reconstruction_digest"),("odes_package","odes_package_digest"),("recipient_validation","odes_validation_digest"),("successor_packet","successor_packet_digest")])
@pytest.mark.parametrize("mutation",["content","copied_labels","missing_commitment","missing_reference"])
def test_actual_artifact_commitment_required(transported_inputs,artifact,ref,mutation):
    data=copy.deepcopy(transported_inputs); export=data["retained"]["artifact_export"]
    obj=export["odes"][artifact] if artifact in ("odes_package","recipient_validation") else export[artifact]
    if mutation=="content":obj["tampered"]="changed without updating commitment"
    elif mutation=="copied_labels":
        export["content_commitments"][artifact]=export["producer_refs"][ref]="sha256:"+"0"*64
        if artifact=="successor_packet":obj["packet_digest"]=export["producer_refs"][ref]
    elif mutation=="missing_commitment":del export["content_commitments"][artifact]
    else:del export["producer_refs"][ref]
    result=evaluate(data)
    assert result["status"]=="failed"
    assert any(f"{artifact} actual content" in failure for failure in result["failures"])


@pytest.mark.parametrize("key",["decision_id","effect_id","attempt_id"])
def test_missing_execution_identity_fails(transported_inputs,key):
    data=copy.deepcopy(transported_inputs);del data["execution"][key]
    assert evaluate(data)["status"]=="failed"


@pytest.mark.parametrize("field,value",[("unresolved_delivery",True),("pending_effects",["unresolved"]),("unresolved_delivery",None),("pending_effects",None)])
def test_success_with_unresolved_successor_fails(transported_inputs,field,value):
    data=copy.deepcopy(transported_inputs)
    data["retained"]["artifact_export"]["successor_packet"][field]=value
    result=evaluate(data)
    assert result["status"]=="failed"
    expected="successor delivery remains unresolved" if field=="unresolved_delivery" else "successor has pending or missing effects"
    assert expected in result["failures"]


@pytest.mark.parametrize("key,value",[("target","substituted"),("amount",999),("unit","EUR"),("payload",{"changed":True})])
def test_original_proposal_binding_required(transported_inputs,key,value):
    data=copy.deepcopy(transported_inputs);data["submitted_proposal"][key]=value
    assert evaluate(data)["status"]=="failed"


def test_fresh_validator_detects_recommitted_validation_lie(transported_inputs):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import digest
    data=copy.deepcopy(transported_inputs); export=data["retained"]["artifact_export"]
    export["odes"]["recipient_validation"]["tampered"]="recommitted"
    value=digest(export["odes"]["recipient_validation"])
    export["producer_refs"]["odes_validation_digest"]=value
    export["content_commitments"]["recipient_validation"]=value
    result=evaluate(data)
    assert "fresh ODES validation differs from retained validation" in result["failures"]


def test_component_failure_blocks_release_even_when_matrix_passes():
    from tools.reference_release import release_passes
    assert release_passes([{"returncode":0}],[{"returncode":0}],True,True,{"returncode":0})
    assert not release_passes([{"returncode":0},{"returncode":1}],[{"returncode":0}],True,True,{"returncode":0})


@pytest.mark.parametrize("field",["attempt_identity","decision_id","effect_id","reconstruction_bundle_id","successor_packet_id"])
def test_missing_retained_identity_fails(transported_inputs,field):
    data=copy.deepcopy(transported_inputs)
    del data["retained"]["artifact_export"]["producer_refs"][field]
    assert evaluate(data)["status"]=="failed"


def test_wrong_attempt_namespace_fails(transported_inputs):
    data=copy.deepcopy(transported_inputs)
    data["retained"]["artifact_export"]["producer_refs"]["attempt_identity"]["namespace"]="control_plane"
    assert evaluate(data)["status"]=="failed"


@pytest.mark.parametrize("field,value",[("newly_executed",False),("destination_observed","unknown")])
def test_success_flags_required(transported_inputs,field,value):
    data=copy.deepcopy(transported_inputs);data["execution"][field]=value
    assert evaluate(data)["status"]=="failed"


@pytest.mark.parametrize("mutation",["extra_effect","no_effect","not_applied","missing_bundle"])
def test_required_success_evidence(transported_inputs,mutation):
    data=copy.deepcopy(transported_inputs)
    if mutation=="extra_effect":data["effect_rows"].append(copy.deepcopy(data["effect_rows"][0]))
    elif mutation=="no_effect":data["effect_rows"]=[]
    elif mutation=="not_applied":data["effect_rows"][0]["state"]="partial"
    else:del data["retained"]["artifact_export"]["reconstruction_bundle"]
    assert evaluate(data)["status"]=="failed"


def test_characterization_is_not_rendered_as_safety_pass():
    matrix={"scenarios":[{"id":"limitation","required":True,"classification":"characterization","tests":["research::case"]}]}
    cases=[{"suite":"research","name":"case","test_id":"research::case","repetition":rep,
            "status":"passed","reason":"","evidence_path":"fixture.xml"} for rep in (1,2)]
    gate, results=resolve_matrix(matrix,cases)
    assert gate is True  # Required reproduction executed, not a safety guarantee.
    assert results[0]["status"]=="characterized"
    assert results[0]["safety_outcome"]=="not_established"
    cases[1]["status"]="failed"
    gate, results=resolve_matrix(matrix,cases)
    assert gate is False
    assert results[0]["status"]=="failed"


def test_junit_parsing_retains_research_failure(tmp_path):
    from tools.release_gate import parse_junit
    report=tmp_path/"research.xml"
    report.write_text('<testsuites><testsuite><testcase name="stale"><failure message="unsafe retry"/></testcase></testsuite></testsuites>')
    cases=parse_junit(report,"research_qualification",1)
    assert cases[0]["status"]=="failed"
    assert cases[0]["reason"]=="unsafe retry"


@pytest.mark.parametrize("version", [None, "1.0.0", "2.0.0"])
def test_current_artifact_profile_required(transported_inputs, version):
    data=copy.deepcopy(transported_inputs)
    data["retained"]["artifact_export"]["export_version"]=version
    assert evaluate(data)["status"]=="failed"
