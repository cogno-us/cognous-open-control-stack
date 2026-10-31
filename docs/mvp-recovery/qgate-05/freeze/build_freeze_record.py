#!/usr/bin/env python3
"""Build the OCS-MVP-QGATE-05 candidate-freeze record (PROPOSED, never a certification).

Standard library only, deterministic (no clock, no network, no randomness): the same tree and arguments always give the same bytes.
It reads a Qualification tree, never writes into it, and does not import the gate. `verify_freeze_record.py` is an independent
second implementation; do not share code between them.

    python3 build_freeze_record.py --qualification-tree DIR --qualification-revision SHA40 --prepared-utc 2026-10-31 \
        --control-plane SHA --runtime SHA --replay SHA --evidence-pack SHA --odes SHA --verifier SHA --action-manifest SHA --hub SHA \
        [--commitment REL] [--battery REL] [--prepared-by TEXT] --out record.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HEX40 = re.compile(r"[0-9a-f]{40}")
TUPLE = ("control_plane", "runtime", "replay", "evidence_pack", "odes", "verifier", "action_manifest", "hub")
BRANCHISH = {"main", "master", "head", "develop", "trunk", "latest"}

Q14_PERMITTED = "The frozen pinned classes compose end-to-end in the qualification harness, while the trusted ingress boundary is separately exercised on the real socket under the same frozen candidate."
Q14_PROHIBITED = "A live socket request produced the reconstructed Replay, Evidence Pack, and Verifier evidence."

STANDING_HOLDS = [
    "F3 engineering CLOSED",
    "F3 Q2/Q3 UNRESOLVED",
    "Q7 NOT ESTABLISHED",
    "Final Tier 1 DEFERRED, NOT WAIVED",
    "publication/release/production HOLD",
    "Registry #58/#59 HELD",
    "Control Plane #87 HELD",
    "constructor tolerance NOT AUTHORIZED",
    "Ed25519 #26/#34 HELD",
    "V09 SEPARATE",
    "DEF-OBS-TOL-OVERFLOW-1 OPEN, SEPARATE",
    "R1 DEFERRED",
]

HOST_PROFILE = {
    "runner": "GitHub-hosted ubuntu-24.04",
    "python": "CPython 3.13",
    "ipc_directory_mode": "2751",
    "ipc_scope": "bounded synthetic test only (Architect ruling D3)",
    "socket_mode": "0660",
    "peer_uid_allowlist": True,
    "accepted_residual": "an outsider can stat a known socket name; no connect, listing or state disclosure",
    "production": "NOT production; not a production host profile",
    "mode_2750_evidence": "the 2750 evidence is immutable and is not reinterpreted",
    "yama_ptrace_scope": "as-found value recorded; raised to 1 with sudo sysctl -w kernel.yama.ptrace_scope=1 only if below 1; never lowered; if Yama is absent nothing is faked and the boundary rows are BLOCKED",
}

LIMITATIONS = [
    "Same-lineage AI roles prepared, built and reviewed this candidate; there is no formal independence and no independent certification.",
    "VER-01 accepts exit 0 or 3 and VER-03 is applicable only on exit 3 (Verifier abstain) attributable to v4.ledger.rows-agree-with-attempts: VER rows PASS on a V4 ABSTAIN where the oracle so states; that is not 'all V4 checks pass'.",
    "The battery inventory is test inventory, not governance coverage: supplementary entries substantiate single claims and no combined pass rate exists.",
    "KL-01 is a non-mandatory known-limitation row and cannot change the verdict.",
    "ODES is pin-checked only; the chain never imports or exercises it.",
    "Local dry runs, builder runs and any run outside the single GitHub-hosted run are not evidence.",
    "Synthetic fault injection is supplementary only and supports no wording that promises recovery after actual process death (ruling A1); the real OS-level kill row is a separate mandatory row.",
    "Q14 equivalence scope applies: the composed chain and the real-socket ingress controls are separate vehicles bound to the same tuple and commitment.",
    "Prerequisites that the run cannot check before it starts (F-01, F-03): the anchor gate G-02c compares every frozen file (oracle v8 and the other frozen files, as listed by battery v2) with its blob on Qualification main, so the exact freeze tree must be on Qualification main BEFORE qgate-05/run-1 is pushed, otherwise G-02c is INCOMPLETE and the single run ends INCOMPLETE whatever the rows do; and the custody record must already be on the hub branch qgate-05/custody-1 (pushed once, never force-pushed) before that push, otherwise the custody step fails and the run is spent.",
    "Residual F-06: the base path /var/lib/qgate05-ocs has never run on a GitHub-hosted runner; it is an Architect-stated relocation after the /opt ACL FAIL of QGATE-03, so the G-11 ACL and ancestor-writability checks are unproven there until the single run.",
    "Residual F-09: the upload-artifact digest and id are not captured (only SHA256SUMS inside the artifact); the evidence branch is append-only by script (new run directory, fast-forward only, no force, refuses an existing run directory), not enforced server-side, and a push rejected by a ruleset leaves the evidence-branch-exists guard unset.",
    "Residual F-10: VER-01 and VER-03 are oracle PASS while the Verifier disposition is exit 3 ABSTAIN (VER-03 requires it); ABSTAIN is not in the oracle status vocabulary, so a row-level reader sees PASS; the categories (PASS, FAIL, BLOCKED, ABSTAIN) are reported separately by tools/qgate05_summarize.py and G-07.",
    "Residual F-11: NC4-03b's title says 'no capabilities' but the probe drops only the client and outsider to CapEff 0 (the ingress's own capability set is judged in the environment record, NC4-01 and G-11); NC4-03c requires that the outsider can stat the known socket name (the D3 accepted residual), so a stricter host would FAIL that row rather than false-pass.",
    "Residual F-12: the runner image is the floating label ubuntu-24.04 (ImageOS and ImageVersion are recorded in run-identity.json and the host snapshot); the action pins (checkout 11d5960a, setup-python a26af69b, upload-artifact ea165f8d, download-artifact d3f86a10) could not be verified from the build environment; other workflows (catalog-validation, migration-integrity) trigger on the same push and are noise.",
]

APPROVAL_STATEMENT = ("This is an AI-assisted technical approval of a candidate freeze by the designated Qualification Owner session. "
                      "It is not an independent certification, not a Qualification verdict, not Tier 1, not Q7, and not a release, publication or production authorization.")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(Path(p).read_bytes())


def die(msg: str):
    print("build_freeze_record: " + msg, file=sys.stderr)
    raise SystemExit(2)


def latest(root: Path, directory: str, stem: str) -> str:
    best = None
    for p in (root / directory).iterdir():
        m = re.fullmatch(re.escape(stem) + r"\.v(\d+)\.json", p.name)
        if m and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), f"{directory}/{p.name}")
    if best is None:
        die(f"no {stem}.vN.json in {directory}")
    return best[1]


def version_of(rel: str, pattern: str) -> str:
    m = re.search(pattern, rel)
    if not m:
        die(f"cannot derive a version label from {rel}")
    return "v" + m.group(1)


def listing_hash(files: dict) -> str:
    text = "".join(f"{k}\t{files[k]}\n" for k in sorted(files))
    return sha256_bytes(text.encode())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--qualification-tree", required=True)
    ap.add_argument("--qualification-revision", required=True)
    ap.add_argument("--prepared-utc", required=True, help="date/time text recorded verbatim (no clock is read)")
    ap.add_argument("--prepared-by", default="Worker D (AI, same lineage as the builder; does not satisfy Architect D1 role separation)")
    ap.add_argument("--commitment", help="repo-relative commitment file; default: highest candidate-commitment.proposed.vN.json")
    ap.add_argument("--battery", help="repo-relative battery file; default: highest mandatory-battery.proposed.vN.json")
    for n in TUPLE:
        ap.add_argument("--" + n.replace("_", "-"), required=True, dest=n)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    root = Path(a.qualification_tree).resolve()
    rev = a.qualification_revision
    if not HEX40.fullmatch(rev):
        die("qualification revision must be 40 lower-case hex")
    if (root / ".git").exists():
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        if head != rev:
            die(f"tree HEAD {head} != qualification revision {rev}")

    shas = {n: getattr(a, n) for n in TUPLE}
    for n, s in shas.items():
        if not HEX40.fullmatch(s) or s in BRANCHISH:
            die(f"{n}: '{s}' is not a full 40-hex lower-case sha")
    pin = json.loads((root / "process/mvp-chain/tuple-pin.proposed.json").read_text())
    ident = json.loads((root / "process/mvp-acceptance/candidate-identity.inputs.json").read_text())
    for n in TUPLE:
        for label, doc in (("tuple-pin", pin), ("identity inputs", ident)):
            got = doc["components"][n]["sha"]
            if got != shas[n]:
                die(f"{n}: supplied {shas[n]} != {label} {got}")
    if set(pin["components"]) != set(TUPLE) or set(ident["components"]) != set(TUPLE):
        die("tuple pin / identity inputs do not name exactly the 8 components")

    battery_rel = a.battery or latest(root, "process/mvp-acceptance", "mandatory-battery.proposed")
    commit_rel = a.commitment or latest(root, "process/mvp-acceptance", "candidate-commitment.proposed")
    battery = json.loads((root / battery_rel).read_text())
    oracle_rel = battery["oracle"]["expectations_in_force"]
    oracle_sha = sha256_file(root / oracle_rel)
    recorded = battery["oracle"]["unchanged_files_sha256"].get(oracle_rel)
    if recorded != oracle_sha:
        die(f"battery records {recorded} for {oracle_rel} but the file is {oracle_sha}")
    oracle = json.loads((root / oracle_rel).read_text())
    commitment = json.loads((root / commit_rel).read_text())
    files = commitment["files"]

    rows = oracle["rows"]
    mandatory = [r for r in rows if r.get("mandatory", True)]
    nc_groups: dict = {}
    for r in mandatory:
        m = re.match(r"(NC\d+)-", r["id"])
        if m:
            nc_groups[m.group(1)] = nc_groups.get(m.group(1), 0) + 1
    kinds: dict = {}
    for t in battery["tests"]:
        kinds[t["kind"]] = kinds.get(t["kind"], 0) + 1
    by_id = {r["id"]: r for r in rows}

    def ops(rid, obs):
        return [c for c in by_id.get(rid, {}).get("all", []) if c.get("obs") == obs]

    ver01 = ops("VER-01", "chain.verifier.A.exit_code")
    ver03 = ops("VER-03", "chain.verifier.B.exit_code")

    rec = {
        "schema": "cognous.ocs-mvp-qgate-05-freeze-record/1",
        "record_id": f"ocs-mvp-qgate-05-freeze-record-{rev[:8]}",
        "status": "PROPOSED",
        "frozen": False,
        "status_note": "Technical candidate-freeze record (Architect decision D4). It is NOT a freeze until the designated Qualification Owner fills owner_approval and sets frozen true. "
                       "Not a Qualification verdict, certification, Tier 1, Q7, security clearance, release, publication or production authorization.",
        "prepared_utc": a.prepared_utc,
        "prepared_by": a.prepared_by,
        "tuple": dict(shas),
        "tuple_checks": {"all_40_hex": True, "none_is_a_branch_name": True, "present_in_tuple_pin": True, "present_in_identity_inputs": True,
                         "tuple_pin_sha256": sha256_file(root / "process/mvp-chain/tuple-pin.proposed.json"),
                         "identity_inputs_sha256": sha256_file(root / "process/mvp-acceptance/candidate-identity.inputs.json")},
        "qualification": {"repository": "cogno-us/cognous-stack-qualification", "revision": rev},
        "oracle": {"path": oracle_rel, "version": version_of(oracle_rel, r"expectations\.proposed\.v(\d+)"), "sha256": oracle_sha},
        "battery": {"path": battery_rel, "version": version_of(battery_rel, r"\.v(\d+)\.json$"), "sha256": sha256_file(root / battery_rel)},
        "commitment": {"path": commit_rel, "candidate_version": commitment["candidate_version"], "sha256": sha256_file(root / commit_rel),
                       "sha256_basis": "sha256 of the file bytes (gate sha256_file)", "file_count": len(files), "file_listing_sha256": listing_hash(files),
                       "file_listing_basis": "sha256 over lines '<path>\\t<sha256>\\n' sorted by path"},
        "host_profile": HOST_PROFILE,
        "q14_equivalence_scope": {"status": "ACCEPTED (Architect ruling Q14)", "permitted_claim": Q14_PERMITTED, "prohibited_claim": Q14_PROHIBITED,
                                  "vehicle": "(A) exact-pin in-process composed chain (Control Plane, route-B execution, Replay, Evidence Pack, Verifier) + (B) separate real-socket ingress and peer-boundary negative controls, both bound to the same frozen tuple and commitment"},
        "limitations": list(LIMITATIONS),
        "oracle_ver_disposition": {"VER-01_exit_codes_accepted": ver01[0].get("value") if ver01 else None,
                                   "VER-03_applicable_only_when_exit_not_equal": (by_id.get("VER-03", {}).get("not_applicable_if") or [{}])[0].get("value"),
                                   "VER-03_required_exit": ver03[0].get("value") if ver03 else None},
        "denominators": {
            "oracle_rows": len(rows), "mandatory_oracle_rows": len(mandatory),
            "non_mandatory_oracle_rows": sorted(r["id"] for r in rows if not r.get("mandatory", True)),
            "mandatory_nc_rows": sum(nc_groups.values()), "negative_control_groups": len(nc_groups), "negative_control_group_sizes": dict(sorted(nc_groups.items())),
            "battery_entries": len(battery["tests"]), "battery_entries_by_kind": dict(sorted(kinds.items())),
            "unique_governance_claims": len(mandatory),
            "non_mandatory_battery_tests": len(battery.get("non_mandatory_tests", [])),
            "pending_rows": len(battery.get("pending_rows", [])),
            "declared_not_applicable": len(battery.get("declared_not_applicable", [])),
            "note": "recomputed from the files; prior baseline counts (42/41/30/7/260) are historical, not targets; battery entries are inventory, not coverage",
        },
        "standing_holds": list(STANDING_HOLDS),
        "owner_approval": {
            "approved": False, "approver_role": None, "approver_session": None, "approved_at_utc": None,
            "statement_required": APPROVAL_STATEMENT, "statement_acknowledged": False,
        },
    }
    Path(a.out).write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
