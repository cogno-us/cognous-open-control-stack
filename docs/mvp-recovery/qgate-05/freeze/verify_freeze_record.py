#!/usr/bin/env python3
"""Independent verifier for the QGATE-05 candidate-freeze record (second implementation; shares no code with build_freeze_record.py).

Re-derives every field from the Qualification tree, compares it with the record, checks the commitment against the tree, and runs the gate's
own commit_files() read-only in a subprocess (python -B, no bytecode written into the tree) to prove the committed list equals the files
present. Exit 0 only when every check passes; 1 on any mismatch; 2 on usage or unreadable input.

    python3 verify_freeze_record.py --qualification-tree DIR --record record.json [--qualification-revision SHA40]
        [--expect-commitment-sha256 HEX64] [--require-approved] [--require-final-tree] [--skip-gate]
"""
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path

ORDER = ("control_plane", "runtime", "replay", "evidence_pack", "odes", "verifier", "action_manifest", "hub")
FAILS = []


def h(b):
    return hashlib.sha256(b).hexdigest()


def hf(p):
    return h(Path(p).read_bytes())


def check(ok, name, detail=""):
    print(("OK    " if ok else "FAIL  ") + name + (": " + detail if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def top_version(root, d, stem):
    best = None
    for q in (root / d).iterdir():
        m = re.fullmatch(re.escape(stem) + r"\.v([0-9]+)\.json", q.name)
        if m and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), d + "/" + q.name)
    return best[1]


def expected_record(root, rec, args):
    """Everything derivable from the tree. Free inputs taken from the record itself: tuple shas (then validated against the pins), prepared_*."""
    pin = json.loads((root / "process/mvp-chain/tuple-pin.proposed.json").read_text())
    idn = json.loads((root / "process/mvp-acceptance/candidate-identity.inputs.json").read_text())
    tup = rec.get("tuple", {})
    check(list(tup) == list(ORDER) or sorted(tup) == sorted(ORDER), "tuple names exactly the 8 components", str(sorted(tup)))
    for n in ORDER:
        s = tup.get(n)
        check(isinstance(s, str) and re.fullmatch(r"[0-9a-f]{40}", s) is not None and s.lower() not in ("main", "master", "head"), f"tuple.{n} is full 40-hex", str(s))
        check(pin["components"][n]["sha"] == s, f"tuple.{n} equals tuple-pin", f"{pin['components'][n]['sha']} vs {s}")
        check(idn["components"][n]["sha"] == s, f"tuple.{n} equals identity inputs", f"{idn['components'][n]['sha']} vs {s}")
    check(set(pin["components"]) == set(ORDER) and set(idn["components"]) == set(ORDER), "pin and identity inputs name exactly the 8 components")

    bat_rel = rec["battery"]["path"]
    com_rel = rec["commitment"]["path"]
    check(bat_rel == top_version(root, "process/mvp-acceptance", "mandatory-battery.proposed"), "battery path is the highest version in the tree", bat_rel)
    check(com_rel == top_version(root, "process/mvp-acceptance", "candidate-commitment.proposed"), "commitment path is the highest version in the tree", com_rel)
    bat = json.loads((root / bat_rel).read_text())
    ora_rel = bat["oracle"]["expectations_in_force"]
    ora = json.loads((root / ora_rel).read_text())
    cm = json.loads((root / com_rel).read_text())
    files = cm["files"]
    listing = "".join("%s\t%s\n" % (k, files[k]) for k in sorted(files))

    rows = ora["rows"]
    mand = [r for r in rows if r.get("mandatory", True)]
    grp = {}
    for r in mand:
        m = re.match(r"(NC[0-9]+)-", r["id"])
        if m:
            grp[m.group(1)] = grp.get(m.group(1), 0) + 1
    kinds = {}
    for t in bat["tests"]:
        kinds[t["kind"]] = kinds.get(t["kind"], 0) + 1
    byid = {r["id"]: r for r in rows}
    v1 = [c for c in byid["VER-01"]["all"] if c["obs"] == "chain.verifier.A.exit_code"]
    v3 = [c for c in byid["VER-03"]["all"] if c["obs"] == "chain.verifier.B.exit_code"]

    # fixed texts, deliberately re-typed here (independent of the builder)
    q14p = "The frozen pinned classes compose end-to-end in the qualification harness, while the trusted ingress boundary is separately exercised on the real socket under the same frozen candidate."
    q14x = "A live socket request produced the reconstructed Replay, Evidence Pack, and Verifier evidence."
    holds = ["F3 engineering CLOSED", "F3 Q2/Q3 UNRESOLVED", "Q7 NOT ESTABLISHED", "Final Tier 1 DEFERRED, NOT WAIVED", "publication/release/production HOLD", "Registry #58/#59 HELD",
             "Control Plane #87 HELD", "constructor tolerance NOT AUTHORIZED", "Ed25519 #26/#34 HELD", "V09 SEPARATE", "DEF-OBS-TOL-OVERFLOW-1 OPEN, SEPARATE", "R1 DEFERRED"]
    exp = {
        "tuple": dict(tup),
        "tuple_checks": {"all_40_hex": True, "none_is_a_branch_name": True, "present_in_tuple_pin": True, "present_in_identity_inputs": True,
                         "tuple_pin_sha256": hf(root / "process/mvp-chain/tuple-pin.proposed.json"),
                         "identity_inputs_sha256": hf(root / "process/mvp-acceptance/candidate-identity.inputs.json")},
        "qualification": {"repository": "cogno-us/cognous-stack-qualification", "revision": rec.get("qualification", {}).get("revision")},
        "oracle": {"path": ora_rel, "version": "v" + re.search(r"expectations\.proposed\.v([0-9]+)", ora_rel).group(1), "sha256": hf(root / ora_rel)},
        "battery": {"path": bat_rel, "version": "v" + re.search(r"\.v([0-9]+)\.json$", bat_rel).group(1), "sha256": hf(root / bat_rel)},
        "commitment": {"path": com_rel, "candidate_version": cm["candidate_version"], "sha256": hf(root / com_rel), "sha256_basis": "sha256 of the file bytes (gate sha256_file)",
                       "file_count": len(files), "file_listing_sha256": h(listing.encode()),
                       "file_listing_basis": "sha256 over lines '<path>\\t<sha256>\\n' sorted by path"},
        "host_profile": {"runner": "GitHub-hosted ubuntu-24.04", "python": "CPython 3.13", "ipc_directory_mode": "2751",
                         "ipc_scope": "bounded synthetic test only (Architect ruling D3)", "socket_mode": "0660", "peer_uid_allowlist": True,
                         "accepted_residual": "an outsider can stat a known socket name; no connect, listing or state disclosure",
                         "production": "NOT production; not a production host profile", "mode_2750_evidence": "the 2750 evidence is immutable and is not reinterpreted",
                         "yama_ptrace_scope": "as-found value recorded; raised to 1 with sudo sysctl -w kernel.yama.ptrace_scope=1 only if below 1; never lowered; if Yama is absent nothing is faked and the boundary rows are BLOCKED"},
        "q14_equivalence_scope": {"status": "ACCEPTED (Architect ruling Q14)", "permitted_claim": q14p, "prohibited_claim": q14x,
                                  "vehicle": "(A) exact-pin in-process composed chain (Control Plane, route-B execution, Replay, Evidence Pack, Verifier) + (B) separate real-socket ingress and peer-boundary negative controls, both bound to the same frozen tuple and commitment"},
        "oracle_ver_disposition": {"VER-01_exit_codes_accepted": v1[0].get("value") if v1 else None,
                                   "VER-03_applicable_only_when_exit_not_equal": (byid["VER-03"].get("not_applicable_if") or [{}])[0].get("value"),
                                   "VER-03_required_exit": v3[0].get("value") if v3 else None},
        "denominators": {"oracle_rows": len(rows), "mandatory_oracle_rows": len(mand),
                         "non_mandatory_oracle_rows": sorted(r["id"] for r in rows if r.get("mandatory", True) is False),
                         "mandatory_nc_rows": sum(grp.values()), "negative_control_groups": len(grp), "negative_control_group_sizes": dict(sorted(grp.items())),
                         "battery_entries": len(bat["tests"]), "battery_entries_by_kind": dict(sorted(kinds.items())), "unique_governance_claims": len(mand),
                         "non_mandatory_battery_tests": len(bat.get("non_mandatory_tests", [])), "pending_rows": len(bat.get("pending_rows", [])),
                         "declared_not_applicable": len(bat.get("declared_not_applicable", [])),
                         "note": "recomputed from the files; prior baseline counts (42/41/30/7/260) are historical, not targets; battery entries are inventory, not coverage"},
        "standing_holds": holds,
    }
    return exp, cm, bat


def compare(exp, rec):
    for k, v in exp.items():
        check(rec.get(k) == v, "field " + k + " equals value re-derived from the tree",
              json.dumps({kk: (rec.get(k) or {}).get(kk) for kk in v if isinstance(v, dict) and (rec.get(k) or {}).get(kk) != v[kk]}, sort_keys=True)[:400] if isinstance(v, dict) else "")


def limitations_ok(rec):
    L = " || ".join(rec.get("limitations", []))
    needs = {"same-lineage": "Same-lineage", "no formal independence": "no formal independence", "VER ABSTAIN": "V4 ABSTAIN", "inventory not coverage": "not governance coverage",
             "KL-01": "KL-01", "ODES": "pin-checked only", "local dry runs": "Local dry runs", "OS kill": "actual process death", "Q14": "Q14",
             "F-01 main-landing prerequisite": "Qualification main BEFORE qgate-05/run-1 is pushed", "F-03 custody branch prerequisite": "hub branch qgate-05/custody-1",
             "F-06 /var/lib unproven": "Residual F-06", "F-09 artifact digest / evidence branch not server-enforced": "Residual F-09", "F-10 ABSTAIN vocabulary": "ABSTAIN is not in the oracle status vocabulary",
             "F-11 NC4-03b/c wording": "Residual F-11", "F-12 floating image / action pins": "Residual F-12"}
    for name, frag in needs.items():
        check(frag in L, "limitation present: " + name)


def gate_check(root, cm, cm_rel, args):
    if args.skip_gate:
        print("SKIP  gate commit_files check (--skip-gate)")
        return
    code = ("import sys, json; from pathlib import Path; sys.dont_write_bytecode = True; sys.path.insert(0, %r); import mvp_acceptance_gate as g; "
            "print(json.dumps({'files': g.commit_files(Path(%r)), 'file': g.COMMITMENT_FILE}))" % (str(root / "tools"), str(root)))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True, cwd="/", env=env)
    if p.returncode != 0:
        check(False, "gate commit_files() ran read-only", p.stderr[-300:])
        return
    out = json.loads(p.stdout.strip().splitlines()[-1])
    present, committed = set(out["files"]), set(cm["files"])
    check(present == committed, "gate commit_files() == committed list (no uncommitted or missing file)",
          "uncommitted=%s missing=%s" % (sorted(present - committed)[:10], sorted(committed - present)[:10]))
    check(out["file"] == cm_rel, "gate COMMITMENT_FILE equals the record's commitment path", "%s vs %s" % (out["file"], cm_rel))
    check(not any(True for _ in (root / "tools").glob("__pycache__")), "gate invocation left no __pycache__ in tools/")


def tree_checks(root, cm):
    for rel, d in sorted(cm["files"].items()):
        p = root / rel
        if p.is_symlink() or not p.is_file():
            check(False, "committed file present and regular: " + rel)
        elif hf(p) != d:
            check(False, "committed file bytes match: " + rel)
    check(not [f for f in cm["files"] if any((root.joinpath(*Path(f).parts[:i])).is_symlink() for i in range(1, len(Path(f).parts) + 1))], "no symlink in or above committed set")
    check(not [c for c in cm.get("must_remain_absent", []) if (root / c).exists() or (root / c).is_symlink()], "must_remain_absent files absent")
    caches = [str(q.relative_to(root)) for q in root.rglob("__pycache__") if ".git" not in q.parts]
    check(not caches, "no __pycache__ directory in the tree", str(caches[:5]))
    print("OK    per-file bytes checked: %d files" % len(cm["files"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--qualification-tree", required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("--qualification-revision")
    ap.add_argument("--expect-commitment-sha256")
    ap.add_argument("--require-approved", action="store_true")
    ap.add_argument("--require-final-tree", action="store_true")
    ap.add_argument("--skip-gate", action="store_true")
    args = ap.parse_args()
    root = Path(args.qualification_tree).resolve()
    raw = Path(args.record).read_bytes()
    try:
        rec = json.loads(raw)
    except Exception as e:
        print("unreadable record: %s" % e, file=sys.stderr)
        return 2
    check(raw == (json.dumps(rec, indent=2, sort_keys=True) + "\n").encode(), "record is in canonical serialization")
    check(rec.get("schema") == "cognous.ocs-mvp-qgate-05-freeze-record/1", "schema")
    rev = rec.get("qualification", {}).get("revision")
    check(isinstance(rev, str) and re.fullmatch(r"[0-9a-f]{40}", rev) is not None, "qualification revision is 40-hex")
    if args.qualification_revision:
        check(rev == args.qualification_revision, "qualification revision equals --qualification-revision")
    if (root / ".git").exists():
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        check(head == rev, "tree git HEAD equals qualification revision", head)
        st = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"], capture_output=True, text=True).stdout.strip()
        check(st == "", "qualification tree is clean (no modified or untracked file)", st[:200])
    exp, cm, bat = expected_record(root, rec, args)
    compare(exp, rec)
    if args.expect_commitment_sha256:
        check(rec["commitment"]["sha256"] == args.expect_commitment_sha256 == hf(root / rec["commitment"]["path"]), "commitment sha256 equals the externally supplied value")
    limitations_ok(rec)
    tree_checks(root, cm)
    gate_check(root, cm, rec["commitment"]["path"], args)
    oa = rec.get("owner_approval", {})
    filled = all(oa.get(k) for k in ("approver_role", "approver_session", "approved_at_utc")) and oa.get("approved") is True and oa.get("statement_acknowledged") is True
    check(oa.get("statement_required") is not None and "not an independent certification" in oa["statement_required"], "approval statement text present")
    if rec.get("frozen") is True:
        check(filled and rec.get("status") == "FROZEN-TECHNICAL", "frozen=true only with a complete Owner approval and status FROZEN-TECHNICAL")
    else:
        check(rec.get("frozen") is False and not oa.get("approved"), "unfrozen record carries no approval", str(oa))
    if args.require_approved:
        check(rec.get("frozen") is True and filled, "--require-approved: record is approved and frozen")
    if args.require_final_tree:
        check(exp["denominators"]["pending_rows"] == 0, "--require-final-tree: no pending placeholder rows", str(exp["denominators"]["pending_rows"]))
    print("verify_freeze_record: %s (%d failing checks)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
