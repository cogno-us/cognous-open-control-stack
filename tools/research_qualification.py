#!/usr/bin/env python3
"""Run the bounded Batch 4C checkpoint against existing locked checkouts.

Does not clone, update pins, or repair failing upstream behavior. A nonzero
pytest exit remains nonzero; the report preserves failures before returning.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if list(out.iterdir()):
        raise SystemExit("Choose an empty evidence directory; previous evidence is preserved.")
    work = ROOT / ".reference-work"
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(map(str, [ROOT, work / "control_plane/src",
        work / "moltbot_safe", work / "gax_imx_transport", work / "replay_bundle/src",
        work / "odes/src", work / "governance_evidence_pack/src"]))
    env["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"] = str(work / "control_plane")
    env["MOLTBOT_SAFE_ROOT"] = str(work / "moltbot_safe")
    env["BATCH4C_RESULTS_DIR"] = str(out / "scenarios")
    command = [sys.executable, "-m", "pytest", "-q", str(ROOT / "tests/test_research_qualification.py"),
               "--junitxml", str(out / "research_qualification.xml")]
    run = subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / "pytest.log").write_text(run.stdout)
    scenarios = [json.loads(p.read_text()) for p in sorted((out / "scenarios").glob("*.json"))]
    totals = {key: 0 for key in ("tests", "failures", "errors", "skipped")}
    if (out / "research_qualification.xml").exists():
        for suite in ET.parse(out / "research_qualification.xml").getroot().iter("testsuite"):
            for key in totals: totals[key] += int(suite.get(key, 0))
    report = {
        "schema_version": "1.0", "scope": "Batch 4C observation, late-commit and recovery-authority qualification",
        "starting_baseline": "5e1095dd74030129f670e9c490fbc7c63209d922",
        "command": command, "exit_code": run.returncode, "test_totals": totals,
        "release_ready": False, "complete_batch_executed": False,
        "scenarios": scenarios,
        "unexecuted": ["4c-cross-process", "cancellation/termination/finality"],
        "unsupported_boundaries": ["remote/cross-host exactly-once", "authenticated observation source", "observation coverage/finality proof"],
    }
    (out / "results.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"results": str(out / "results.json"), "totals": totals,
                      "exit_code": run.returncode, "release_ready": False}, indent=2))
    return run.returncode


if __name__ == "__main__":
    raise SystemExit(main())
