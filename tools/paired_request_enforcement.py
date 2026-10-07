#!/usr/bin/env python3
"""Run Worker 22 paired-request enforcement qualification at exact accepted pins."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "component-lock.json").read_text(encoding="utf-8"))
MATRIX = ROOT / "scenarios/paired-request-enforcement-matrix.v2.json"
WORK = ROOT / ".worker22-paired-work"
NAMES = ("action_manifest", "control_plane", "gax_imx_transport", "moltbot_safe", "replay_bundle")
EXPECTED_BASELINE = "f801546d5272104b02a240e1126b3f92f26486f2"

EXPECTED_PINS = {
    "action_manifest": "46c950bed37fe3812000895430bc0312d29e37ce",
    "control_plane": "d3dadee70bd319812b207389ab1e0f6efe511916",
    "gax_imx_transport": "a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf",
    "moltbot_safe": "c3c3ee7188b9367cf70b08074b9c40a5c70c94ac",
    "replay_bundle": "459e4ba62fca49364aebb0050cd5fb2dd5a71bfa",
}


def validate_selected_pins(lock):
    selected = {
        name: lock["components"][name][
            "core_interop_sha" if name == "moltbot_safe" else "sha"
        ]
        for name in NAMES
    }
    if selected != EXPECTED_PINS:
        raise RuntimeError("selected baseline pins changed; qualify a new baseline explicitly")


def run(cmd, *, cwd=None, env=None, timeout=180):
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "returncode": proc.returncode,
            "seconds": round(time.time() - started, 3),
            "output": proc.stdout,
        }
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        return {
            "command": cmd,
            "returncode": 124,
            "seconds": round(time.time() - started, 3),
            "output": out + "\nTIMEOUT",
        }


def checkout(name):
    spec = LOCK["components"][name]
    key = "core_interop_sha" if name == "moltbot_safe" else "sha"
    sha = spec[key]
    dest = WORK / name
    shutil.rmtree(dest, ignore_errors=True)
    rec = run(["git", "clone", "-q", f"https://github.com/{spec['repository']}.git", str(dest)], timeout=120)
    if rec["returncode"]:
        raise RuntimeError(rec["output"])
    rec = run(["git", "checkout", "-q", "--detach", sha], cwd=dest, timeout=60)
    if rec["returncode"]:
        raise RuntimeError(rec["output"])
    got = run(["git", "rev-parse", "HEAD"], cwd=dest, timeout=30)["output"].strip()
    if got != sha:
        raise RuntimeError(f"{name}: expected {sha}, got {got}")
    return dest, sha


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def junit_counts(path):
    out = {key: 0 for key in ("tests", "failures", "errors", "skipped")}
    if path.exists():
        for suite in ET.parse(path).getroot().iter("testsuite"):
            for key in out:
                out[key] += int(suite.get(key, 0))
    out["passed"] = out["tests"] - out["failures"] - out["errors"] - out["skipped"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["run"])
    ap.add_argument("--results-dir", default="results/paired-request-enforcement")
    args = ap.parse_args()

    out = (ROOT / args.results_dir).resolve()
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)

    validate_selected_pins(LOCK)
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    if matrix.get("hub_baseline") != EXPECTED_BASELINE:
        raise RuntimeError("paired-request matrix baseline mismatch")
    if matrix.get("reporting_rules", {}).get("scheduled_denominator") != len(matrix.get("cases", [])):
        raise RuntimeError("scheduled denominator must match matrix cases")

    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir()
    components, pins = {}, {}
    for name in NAMES:
        components[name], pins[name] = checkout(name)

    dependency_install = run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "pytest>=8",
            "pytest-timeout>=2",
            "pydantic>=2",
        ],
        timeout=120,
    )
    if dependency_install["returncode"]:
        raise RuntimeError(dependency_install["output"])

    env = os.environ.copy()
    env["GAX_RUNTIME_COMPATIBILITY_PROFILE"] = LOCK["runtime_profile"]
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(ROOT),
            str(components["control_plane"] / "src"),
            str(components["gax_imx_transport"]),
            str(components["moltbot_safe"]),
            env.get("PYTHONPATH", ""),
        ]
    )
    env["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"] = str(components["control_plane"])
    env["MOLTBOT_SAFE_ROOT"] = str(components["moltbot_safe"])
    env["UPSTREAM_MANIFEST_EXAMPLE"] = str(
        components["action_manifest"] / "examples/refund_integration_v1_1.manifest.json"
    )
    env["WORKER22_REPLAY_EXAMPLE"] = str(
        components["replay_bundle"] / "examples/bounded_success_reconstruction_v0_2.json"
    )
    env["WORKER22_RESULTS_DIR"] = str(out / "cases")

    junit = out / "junit.xml"
    test_run = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            str(ROOT / "tests/test_paired_request_enforcement.py"),
            "--timeout=20",
            "--timeout-method=thread",
            "--junitxml",
            str(junit),
        ],
        env=env,
        timeout=150,
    )
    (out / "pytest.log").write_text(test_run["output"], encoding="utf-8")

    cases = []
    case_dir = out / "cases"
    if case_dir.exists():
        for path in sorted(case_dir.glob("*.json")):
            try:
                cases.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception as exc:
                cases.append(
                    {
                        "case_id": path.stem,
                        "scheduled": True,
                        "evaluable": False,
                        "qualification_passed": False,
                        "artifact_error": f"{type(exc).__name__}: {exc}",
                    }
                )

    scheduled_ids = {case["id"] for case in matrix["cases"]}
    observed_ids = {case.get("case_id") for case in cases}
    missing = sorted(scheduled_ids - observed_ids)
    unexpected = sorted(x for x in observed_ids - scheduled_ids if x)
    failed_records = [
        case.get("case_id")
        for case in cases
        if case.get("scheduled") is True and case.get("qualification_passed") is False
    ]
    evaluable = sum(1 for case in cases if case.get("evaluable") is True)

    summary = {
        "schema_version": "1.1.0",
        "hub_baseline": EXPECTED_BASELINE,
        "component_pins": pins,
        "selected_source_contains_optional_profiles": True,
        "decision_input_sidecar_used_as_authority": False,
        "atomic_authority_effect_profile_enabled": False,
        "refund_intent_profile_enabled": False,
        "matrix": "scenarios/paired-request-enforcement-matrix.v2.json",
        "scheduled_cases": len(matrix["cases"]),
        "evaluable_cases": evaluable,
        "case_records": cases,
        "missing_case_records": missing,
        "unexpected_case_records": unexpected,
        "pytest": junit_counts(junit),
        "pytest_exit": test_run["returncode"],
        "qualification_passed": (
            test_run["returncode"] == 0
            and not missing
            and not unexpected
            and not failed_records
        ),
        "claim_limits": [
            "constructed unsafe requests are not observed model compromise",
            "denial is not model resistance",
            "tool failure is not authorization success",
            "disclosure coverage is unavailable in the accepted refund adapter",
            "task completion is not measured",
            "same-business-intent deduplication is not selected hub behavior",
            "paired replay here is an experimental comparison, not Replay Bundle reconstruction",
        ],
    }
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    artifacts = {}
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "artifact-digests.json":
            artifacts[str(path.relative_to(out))] = sha256_file(path)
    digest_path = out / "artifact-digests.json"
    digest_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "algorithm": "sha256",
                "artifacts": artifacts,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "qualification_passed": summary["qualification_passed"],
                "scheduled": summary["scheduled_cases"],
                "evaluable": summary["evaluable_cases"],
                "pytest": summary["pytest"],
                "results_dir": str(out),
            },
            indent=2,
        )
    )
    return 0 if summary["qualification_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
