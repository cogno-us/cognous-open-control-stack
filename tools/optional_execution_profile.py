#!/usr/bin/env python3
"""Run a selected optional synthetic profile against the accepted component lock."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ("control_plane", "moltbot_safe", "action_manifest", "gax_imx_transport", "replay_bundle")


def prepare(work):
    lock_bytes = (ROOT / "component-lock.json").read_bytes()
    lock = json.loads(lock_bytes)
    pins = {}
    for name in COMPONENTS:
        spec = lock["components"][name]
        sha = spec.get("sha") or spec["accepted_sha"]
        dest = work / name
        if not dest.exists():
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", "https://github.com/" + spec["repository"] + ".git", str(dest)], check=True, timeout=180)
            subprocess.run(["git", "checkout", "--quiet", "--detach", sha], cwd=dest, check=True, timeout=60)
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dest, text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=dest, text=True)
        if actual != sha or dirty:
            raise RuntimeError(f"{name}: checkout must be clean and match {sha}; use a fresh work directory")
        pins[name] = sha
    env = os.environ.copy()
    env.update(PYTHONPATH=os.pathsep.join([str(ROOT), str(work / "control_plane/src"), str(work / "moltbot_safe"), str(work / "gax_imx_transport")]),
               PYTHONDONTWRITEBYTECODE="1", MOLTBOT_SAFE_CONTROL_PLANE_ROOT=str(work / "control_plane"),
               MOLTBOT_SAFE_ROOT=str(work / "moltbot_safe"), GAX_RUNTIME_COMPATIBILITY_PROFILE="merged-producers-v1")
    return env, pins, hashlib.sha256(lock_bytes).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", required=True, choices=["atomic-authority-effect", "refund-intent"])
    ap.add_argument("--work-dir", type=Path, default=ROOT / ".optional-work")
    ap.add_argument("--results-dir", type=Path, required=True)
    ap.add_argument("--scenario", choices=["allowed", "revoked", "same-intent", "distinct-intent"])
    ap.add_argument("--execute", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    out, work = args.results_dir.resolve(), args.work_dir.resolve()
    if args.execute:
        from tools.optional_execution import run_case
        value = run_case(args.profile, args.scenario, out, work)
        (out / "result.json").write_text(json.dumps(value, indent=2) + "\n")
        return 0 if value["qualified"] else 1
    if args.scenario:
        ap.error("scenario selection is internal; each profile runs its complete small batch")
    out.mkdir(parents=True, exist_ok=False)
    work.mkdir(parents=True, exist_ok=True)
    env, pins, digest = prepare(work)
    from tools.worker21_authority_effect_qualification import run
    scenarios = ["allowed", "revoked"]
    if args.profile == "refund-intent":
        scenarios += ["same-intent", "distinct-intent"]
    records = []
    for scenario in scenarios:
        rec = run([sys.executable, str(Path(__file__).resolve()), "--execute", "--profile", args.profile,
                   "--scenario", scenario, "--work-dir", str(work), "--results-dir", str(out / scenario)], env=env, timeout=90)
        (out / (scenario + ".log")).write_text(rec["output"])
        records.append({"scenario": scenario, "returncode": rec["returncode"]})
    summary = {"schema_version": "1.0.0", "profile": args.profile, "tested_revisions": pins,
               "component_lock_sha256": digest, "results": records,
               "qualified": all(r["returncode"] == 0 for r in records),
               "scope": "synthetic same-host SQLite only", "consumer_chain_qualified": False,
               "default_profile_changed": False, "production_ready": False}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if summary["qualified"] else 1


if __name__ == "__main__":
    # Permit direct script invocation without requiring an editable hub install.
    sys.path.insert(0, str(ROOT))
    raise SystemExit(main())
