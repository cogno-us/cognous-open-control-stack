"""Bounded candidate integration; never changes the accepted component lock."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles/merged-consumer-chain.json"


def run(command, *, env, log, timeout=150):
    with log.open("w") as output:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            output.write("\nQualification process group exceeded time limit.\n")
            return 124


def junit_passes(path):
    if not path.exists():
        return False, {}
    try:
        cases = list(ET.parse(path).getroot().iter("testcase"))
        counts = {"tests": len(cases), "failures": 0, "errors": 0, "skipped": 0}
        for case in cases:
            for key, tag in (("failures", "failure"), ("errors", "error"), ("skipped", "skipped")):
                counts[key] += int(case.find(tag) is not None)
        return bool(cases) and not any(counts[key] for key in ("failures", "errors", "skipped")), counts
    except ET.ParseError:
        return False, {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", choices=["recovery", "transport"], required=True)
    parser.add_argument("--work", default=str(ROOT / ".merged-chain-work"))
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if list(out.iterdir()):
        raise SystemExit("Choose an empty output directory; retained evidence is not overwritten.")
    work = Path(args.work).resolve()
    profile = json.loads(PROFILE.read_text())
    actual = {}
    for name, spec in profile["components"].items():
        actual[name] = subprocess.check_output(["git", "-C", str(work / name), "rev-parse", "HEAD"], text=True, timeout=10).strip()
        if actual[name] != spec["sha"]:
            raise SystemExit(f"{name}: expected {spec['sha']}, got {actual[name]}")
        dirty = subprocess.check_output(["git", "-C", str(work / name), "diff", "--name-only", "HEAD", "--", "*.py", "*.json"], text=True, timeout=10).strip()
        if dirty:
            raise SystemExit(f"{name}: modified tracked source inputs: {dirty}")
    env = os.environ.copy()
    manifest = str(work / "action_manifest/examples/refund_integration_v1_1.manifest.json")
    replay = str(work / "replay_bundle/examples/bounded_success_reconstruction_v0_2.json")
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": os.pathsep.join(map(str, [ROOT, work / "control_plane/src", work / "moltbot_safe", work / "gax_imx_transport", work / "replay_bundle/src", work / "governance_evidence_pack/src", work / "odes/src"])),
        "GAX_RUNTIME_COMPATIBILITY_PROFILE": profile["runtime_profile"],
        "COGNOUS_QUALIFICATION_WORK": str(work),
        "COGNOUS_QUALIFICATION_LOCK": str(PROFILE),
        "MOLTBOT_SAFE_CONTROL_PLANE_ROOT": str(work / "control_plane"),
        "MOLTBOT_SAFE_ROOT": str(work / "moltbot_safe"),
        "MOLTBOT_SAFE_MANIFEST_FIXTURE": manifest,
        "UPSTREAM_MANIFEST_EXAMPLE": manifest,
        "UPSTREAM_REPLAY_SUCCESS_EXAMPLE": replay,
    })
    results = []
    normalized = []
    for repetition in (1, 2):
        folder = out / f"run-{repetition}"
        folder.mkdir()
        env["BATCH4C_RESULTS_DIR"] = str(folder / "scenarios")
        if args.batch == "recovery":
            junit = folder / "recovery.xml"
            command = [sys.executable, "-m", "pytest", "-q", "tests/test_research_qualification.py", "--junitxml", str(junit)]
        else:
            command = [sys.executable, "tools/transported_reference.py", "--manifest", manifest, "--replay", replay, "--out", str(folder / "workflow")]
        code = run(command, env=env, log=folder / "execution.log")
        evidence_ok, counts = (False, {})
        if args.batch == "recovery":
            evidence_ok, counts = junit_passes(junit)
        elif code == 0:
            expected = folder / "workflow/expected-vs-observed.json"
            if expected.exists():
                record = json.loads(expected.read_text())
                evidence_ok = record.get("status") == "passed" and record.get("failures") == []
                normalized.append(record.get("normalized"))
        results.append({"repetition": repetition, "returncode": code, "passed": code == 0 and evidence_ok, "counts": counts})
    repeatable = args.batch == "recovery" or (len(normalized) == 2 and normalized[0] is not None and normalized[0] == normalized[1])
    summary = {"profile": profile["profile"], "profile_sha256": hashlib.sha256(PROFILE.read_bytes()).hexdigest(), "batch": args.batch, "actual_pins": actual, "python": sys.version, "results": results, "normalized_transport_repeatable": repeatable if args.batch == "transport" else None, "candidate_batch_passed": all(r["passed"] for r in results) and repeatable, "full_reference_release_qualified": False}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))
    return 0 if summary["candidate_batch_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
