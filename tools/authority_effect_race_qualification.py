#!/usr/bin/env python3
"""Run Worker 19 authority/effect race qualification at exact accepted pins."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "component-lock.json").read_text())
MATRIX = json.loads((ROOT / "scenarios/authority-effect-race-matrix.json").read_text())
WORK = ROOT / ".authority-effect-race-work"
COMPONENTS = ("action_manifest", "control_plane", "gax_imx_transport", "moltbot_safe", "replay_bundle")
BASELINE = "5a9ae5de4d445febe1105087a8b650e33f00eee3"


def run(cmd, *, cwd=None, env=None):
    started = time.time()
    p = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {
        "command": cmd,
        "cwd": str(cwd or ROOT),
        "returncode": p.returncode,
        "seconds": round(time.time() - started, 3),
        "output": p.stdout,
    }


def checkout(name):
    spec = LOCK["components"][name]
    key = "core_interop_sha" if name == "moltbot_safe" else "sha"
    sha = spec[key]
    dest = WORK / name
    if dest.exists():
        shutil.rmtree(dest)
    rec = run(["git", "clone", "-q", f"https://github.com/{spec['repository']}.git", str(dest)])
    if rec["returncode"]:
        raise RuntimeError(rec["output"])
    rec = run(["git", "checkout", "-q", "--detach", sha], cwd=dest)
    if rec["returncode"]:
        raise RuntimeError(rec["output"])
    actual = run(["git", "rev-parse", "HEAD"], cwd=dest)["output"].strip()
    if actual != sha:
        raise RuntimeError(f"{name}: expected {sha}, got {actual}")
    return dest, sha


def junit_counts(path):
    counts = {k: 0 for k in ("tests", "failures", "errors", "skipped")}
    if path.exists():
        for suite in ET.parse(path).getroot().iter("testsuite"):
            for key in counts:
                counts[key] += int(suite.get(key, 0))
    counts["passed"] = counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
    return counts


def gate_evidence(evidence_dir, repetition):
    expected = {item["id"] for item in MATRIX["cases"]}
    files = {p.stem: p for p in evidence_dir.glob("*.json")} if evidence_dir.exists() else {}
    missing = sorted(expected - set(files))
    unexpected = sorted(set(files) - expected)
    records = {}
    failures = []
    for scenario_id in sorted(expected & set(files)):
        try:
            data = json.loads(files[scenario_id].read_text())
        except Exception as exc:
            failures.append(f"{scenario_id}: invalid JSON: {exc}")
            continue
        records[scenario_id] = data
        if data.get("scenario_id") != scenario_id:
            failures.append(f"{scenario_id}: scenario identity mismatch")
        if data.get("repetition") != repetition:
            failures.append(f"{scenario_id}: repetition mismatch")
        if data.get("hub_baseline") != BASELINE:
            failures.append(f"{scenario_id}: hub baseline mismatch")
        assertions = data.get("assertions") or {}
        for required in (
            "pause_is_before_effect_commit",
            "current_assessment_matches_mutation",
            "original_effect_committed",
            "no_inflight_authority_reread_after_mutation",
            "execution_returned_without_exception",
        ):
            if assertions.get(required) is not True:
                failures.append(f"{scenario_id}: required observation {required} not true")
        if scenario_id == "unchanged-authority-control":
            if data.get("classification") != "existing contract supported":
                failures.append(f"{scenario_id}: positive control classification mismatch")
        else:
            if data.get("classification") != "unqualified boundary characterized":
                failures.append(f"{scenario_id}: race classification mismatch")
            if (data.get("stronger_proposed_guarantee") or {}).get("status") != "not_met":
                failures.append(f"{scenario_id}: proposed-property outcome not retained as not_met")
            if data.get("existing_contract_violation_reproduced") is not False:
                failures.append(f"{scenario_id}: must not relabel proposed-property failure as existing-contract violation")
    if missing:
        failures.append("missing evidence: " + ",".join(missing))
    if unexpected:
        failures.append("unexpected evidence: " + ",".join(unexpected))
    return {
        "passed": not failures,
        "expected_scenarios": sorted(expected),
        "missing": missing,
        "unexpected": unexpected,
        "failures": failures,
        "records": records,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["run"])
    ap.add_argument("--results-dir", default="results/authority-effect-race")
    args = ap.parse_args()

    if MATRIX.get("hub_baseline") != BASELINE:
        raise RuntimeError("matrix baseline does not match selected Worker 19 baseline")
    if MATRIX.get("repetitions") != 2:
        raise RuntimeError("matrix must require exactly two repetitions")

    out = (ROOT / args.results_dir).resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir()
    roots = {}
    pins = {}
    for name in COMPONENTS:
        roots[name], pins[name] = checkout(name)

    dep = run([sys.executable, "-m", "pip", "install", "-q", "pytest>=8", "pydantic>=2"])
    if dep["returncode"]:
        raise RuntimeError(dep["output"])

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([
        str(ROOT),
        str(roots["control_plane"] / "src"),
        str(roots["gax_imx_transport"]),
        str(roots["moltbot_safe"]),
        env.get("PYTHONPATH", ""),
    ])
    env["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"] = str(roots["control_plane"])
    env["MOLTBOT_SAFE_ROOT"] = str(roots["moltbot_safe"])
    env["MOLTBOT_SAFE_MANIFEST_FIXTURE"] = str(
        roots["action_manifest"] / "examples/refund_integration_v1_1.manifest.json"
    )
    env["UPSTREAM_CONTROL_PLANE_ROOT"] = str(roots["control_plane"])
    env["UPSTREAM_MOLTBOT_SAFE_ROOT"] = str(roots["moltbot_safe"])
    env["UPSTREAM_GAX_ROOT"] = str(roots["gax_imx_transport"])
    env["UPSTREAM_REPLAY_SUCCESS_EXAMPLE"] = str(
        roots["replay_bundle"] / "examples/bounded_success_reconstruction_v0_2.json"
    )

    runs = []
    overall = 0
    for repetition in (1, 2):
        rdir = out / f"run-{repetition}"
        evidence = rdir / "evidence"
        junit = rdir / "junit.xml"
        rdir.mkdir()
        renv = env.copy()
        renv["AUTHORITY_EFFECT_RACE_RESULTS_DIR"] = str(evidence)
        renv["AUTHORITY_EFFECT_RACE_REPETITION"] = str(repetition)
        rec = run([
            sys.executable,
            "-m",
            "pytest",
            "-q",
            str(ROOT / "tests/test_authority_effect_race_qualification.py"),
            "--junitxml",
            str(junit),
        ], env=renv)
        (rdir / "pytest.log").write_text(rec["output"], encoding="utf-8")
        gate = gate_evidence(evidence, repetition)
        (rdir / "matrix-gate.json").write_text(
            json.dumps({k: v for k, v in gate.items() if k != "records"}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        passed = rec["returncode"] == 0 and gate["passed"]
        if not passed:
            overall = 1
        runs.append({
            "repetition": repetition,
            "pytest_returncode": rec["returncode"],
            "totals": junit_counts(junit),
            "matrix_gate_passed": gate["passed"],
            "qualification_repetition_passed": passed,
            "seconds": rec["seconds"],
            "records": gate["records"],
        })

    classification_totals = {}
    proposed_not_met = 0
    existing_violations = 0
    for repetition in runs:
        for record in repetition["records"].values():
            classification = record.get("classification")
            classification_totals[classification] = classification_totals.get(classification, 0) + 1
            if (record.get("stronger_proposed_guarantee") or {}).get("status") == "not_met":
                proposed_not_met += 1
            if record.get("existing_contract_violation_reproduced"):
                existing_violations += 1

    summary = {
        "schema_version": "1.0",
        "hub_baseline": BASELINE,
        "component_pins": pins,
        "paper_status": "proposed external profile; not adopted as Cognous requirement by this qualification",
        "paper_property_tested": MATRIX["research_oracle"]["proposed_property"],
        "qualification_exit": overall,
        "classification_totals": classification_totals,
        "stronger_proposed_guarantee_not_met_observations": proposed_not_met,
        "existing_contract_violations_reproduced": existing_violations,
        "runs": runs,
        "supported_claim": (
            "At the selected pins, current authority is revalidated before dispatch. "
            "The tested in-flight path performs no authority reread after final validation."
        ),
        "unqualified_boundary": (
            "Decision-relevant authority/policy/evidence changes after final validation "
            "but before destination effect commit have no established atomic ordering contract."
        ),
        "bounded_repair_recommendation": (
            "First define the desired linearization point and authoritative state. Then couple "
            "current-condition validation to effect commit using a transactional or version-conditional "
            "commit/lease/claim mechanism. Do not treat an extra uncoordinated recheck as atomicity."
        ),
        "limitations": [
            "single-host synthetic qualification only",
            "no distributed guarantee",
            "no production institutional authentication",
            "no live OpenShell confinement claim",
            "no complete-mediation claim",
            "no EBL-Core conformance claim",
            "no external-world finality claim",
        ],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "results_dir": str(out),
        "qualification_exit": overall,
        "classification_totals": classification_totals,
        "stronger_proposed_guarantee_not_met_observations": proposed_not_met,
        "existing_contract_violations_reproduced": existing_violations,
        "test_totals": {str(r["repetition"]): r["totals"] for r in runs},
    }, indent=2))
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
