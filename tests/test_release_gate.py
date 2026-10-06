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


def test_interface_cleanup_lock_uses_accepted_revisions():
    lock=json.loads((ROOT/"component-lock.json").read_text(encoding="utf-8"))
    components=lock["components"]
    assert components["gax_imx_transport"]["sha"]=="6bcde026a804c7377f5e39f57ca6dd00b3c3292d"
    assert components["moltbot_safe"]["core_interop_sha"]=="1d308faf664c504b6e310db3c7a310153ef7b067"
    assert components["moltbot_safe"]["accepted_sha"]=="1d308faf664c504b6e310db3c7a310153ef7b067"
    assert components["replay_bundle"]["sha"]=="f63ce914504dd06813c4ccd199b0570dbd8dd427"
    assert components["odes"]["sha"]=="cba83a1c06f718a8afd76178f36e5cc15896347d"
    assert components["governance_evidence_pack"]["sha"]=="f1a76187b72d5b7c9fded12580ba081cb9cba338"
    assert any("GAX retained artifacts 1.0.0"==x for x in components["gax_imx_transport"]["interfaces"])


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
