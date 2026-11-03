#!/usr/bin/env python3
"""Independent verifier for the QGATE-05 candidate-freeze record (second implementation; shares no code with build_freeze_record.py).

TRUSTED VERIFIER (Hub P1 item 10, csf_ffe0c01223ab0e3abc4653cf). This file lives in the Hub and never imports, execs or runs Python from the
candidate Qualification tree to establish provenance. Provenance is established FIRST, fail-fast, from two independently supplied anchors
(--qualification-revision SHA40 and --expect-commitment-sha256 HEX64, both REQUIRED; neither is read from the candidate or from the record):
  1. the candidate is a real Git checkout (a .git directory is required);
  2. the exact commit (HEAD resolved to a commit object, object bytes re-hashed in-process) equals --qualification-revision;
  3. the exact tree (the commit's tree and every subtree re-hashed in-process; optional --qualification-tree-id anchor);
  4. clean state (the working tree equals that tree byte-for-byte, mode-for-mode; nothing extra, nothing missing; computed in-process, not by git status);
  5. the committed candidate-commitment file digest equals --expect-commitment-sha256, and the record's own claims equal both anchors.
Git is invoked only for object reads (rev-parse, cat-file, ls-tree) with an allow-listed environment and repo-config overrides, so no
repo-controlled helper (fsmonitor, filter, textconv, external diff, hook, alias) can run. There is NO self-attested or unanchored mode.
Only after the provenance block passes are candidate JSON/data files read (as data). Candidate Python is NOT executed by default; the optional
--crosscheck-candidate-gate runs the gate's commit_files() read-only (python -I -B, empty environment, throw-away copy of the verified tree) only
after provenance and every byte check passed, and the evidence records candidate_code_executed accordingly.
Exit 0 only when every check passes; 1 on any mismatch; 2 on usage or unreadable input.

    python3 verify_freeze_record.py --qualification-tree DIR --record record.json --qualification-revision SHA40
        --expect-commitment-sha256 HEX64 [--qualification-tree-id SHA40] [--evidence-out FILE.json]
        [--require-approved] [--require-final-tree] [--crosscheck-candidate-gate]
"""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile
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


def sp(root, rel):
    """Resolve a record/tree-supplied relative path under root; absolute, drive, '..' or empty components are refused (data only, never code)."""
    if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel or "\0" in rel or any(c in ("", ".", "..") for c in rel.split("/")):
        raise ValueError("unsafe relative path: %r" % (rel,))
    return root / rel


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
    bat = json.loads(sp(root, bat_rel).read_text())
    ora_rel = bat["oracle"]["expectations_in_force"]
    ora = json.loads(sp(root, ora_rel).read_text())
    cm = json.loads(sp(root, com_rel).read_text())
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
        "oracle": {"path": ora_rel, "version": "v" + re.search(r"expectations\.proposed\.v([0-9]+)", ora_rel).group(1), "sha256": hf(sp(root, ora_rel))},
        "battery": {"path": bat_rel, "version": "v" + re.search(r"\.v([0-9]+)\.json$", bat_rel).group(1), "sha256": hf(sp(root, bat_rel))},
        "commitment": {"path": com_rel, "candidate_version": cm["candidate_version"], "sha256": hf(sp(root, com_rel)), "sha256_basis": "sha256 of the file bytes (gate sha256_file)",
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


# ---------------------------------------------------------------------------------------------------------------------------------------------
# Trusted provenance (runs BEFORE any candidate data is interpreted and never executes candidate code). Fail-fast.
# ---------------------------------------------------------------------------------------------------------------------------------------------
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
GIT_HARDENING = ("allow-listed environment (no inherited GIT_*), GIT_CONFIG_NOSYSTEM/GLOBAL/SYSTEM disabled, GIT_NO_REPLACE_OBJECTS, "
                 "--no-replace-objects, -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.untrackedCache=false -c core.attributesFile=/dev/null "
                 "-c diff.external= -c protocol.allow=never; only rev-parse/cat-file/ls-tree (no status, diff, checkout, filters, textconv, hooks); "
                 "object bytes re-hashed in-process; working-tree cleanliness computed in-process")


class ProvenanceError(Exception):
    pass


def git_env():
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.devnull, "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0", "GIT_NO_REPLACE_OBJECTS": "1", "GIT_OPTIONAL_LOCKS": "0", "GIT_ATTR_NOSYSTEM": "1",
           "GIT_PAGER": "cat", "GIT_EXTERNAL_DIFF": "", "GIT_ASKPASS": "/bin/false"}
    return env


def git(gitdir, *args, stdin=None):
    cmd = ["git", "--git-dir=" + str(gitdir), "--no-replace-objects", "--no-pager",
           "-c", "core.fsmonitor=false", "-c", "core.hooksPath=" + os.devnull, "-c", "core.untrackedCache=false", "-c", "core.attributesFile=" + os.devnull,
           "-c", "diff.external=", "-c", "protocol.allow=never", "-c", "core.alternateRefsCommand="] + list(args)
    p = subprocess.run(cmd, capture_output=True, input=stdin, cwd="/", env=git_env(), timeout=300)
    if p.returncode != 0:
        raise ProvenanceError("git %s failed: %s" % (args[0], p.stderr.decode("utf-8", "replace").strip()[:200]))
    return p.stdout


def obj_ok(kind, sha, raw):
    return hashlib.sha1(b"%s %d\0" % (kind.encode(), len(raw)) + raw).hexdigest() == sha


def git_blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def read_object(gitdir, kind, sha):
    raw = git(gitdir, "cat-file", kind, sha)
    if not obj_ok(kind, sha, raw):
        raise ProvenanceError("%s object %s fails its own hash (corrupt or substituted object)" % (kind, sha))
    return raw


def parse_tree(raw):
    out, i = [], 0
    while i < len(raw):
        sp_ = raw.index(b" ", i)
        nul = raw.index(b"\0", sp_)
        out.append((raw[i:sp_].decode(), raw[sp_ + 1:nul].decode("utf-8", "surrogateescape"), raw[nul + 1:nul + 21].hex()))
        i = nul + 21
    return out


def walk_tree(gitdir, tree_sha, prefix=""):
    """All blob/symlink entries of the tree, every (sub)tree object re-hashed. Returns {path: (mode, sha)}."""
    entries = {}
    for mode, name, sha in parse_tree(read_object(gitdir, "tree", tree_sha)):
        path = prefix + name
        if mode == "40000":
            entries.update(walk_tree(gitdir, sha, path + "/"))
        elif mode in ("100644", "100755", "120000"):
            entries[path] = (mode, sha)
        else:
            raise ProvenanceError("unsupported tree entry mode %s at %s (submodule or special entry)" % (mode, path))
    return entries


def worktree_state(root, entries):
    """Compare the working tree with the tree entries. Returns (problems, bytes_by_path_not_kept). The top-level .git directory is the only skipped path."""
    problems, seen = [], set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
            dirnames[:] = [d for d in dirnames if d != ".git"]
            filenames = [f for f in filenames if f != ".git"]
        for d in list(dirnames):
            if os.path.islink(os.path.join(dirpath, d)):
                dirnames.remove(d)
                filenames.append(d)
        for f in filenames:
            rel = (rel_dir + "/" + f) if rel_dir else f
            full = os.path.join(dirpath, f)
            seen.add(rel)
            if rel not in entries:
                problems.append("untracked or extra: " + rel)
                continue
            mode, sha = entries[rel]
            if os.path.islink(full):
                data = os.readlink(full).encode("utf-8", "surrogateescape")
                good_mode = mode == "120000"
            else:
                data = Path(full).read_bytes()
                good_mode = mode in ("100644", "100755") and (os.stat(full).st_mode & 0o111 != 0) == (mode == "100755")
            if not good_mode:
                problems.append("type/mode differs: " + rel)
            elif git_blob_sha(data) != sha:
                problems.append("content differs: " + rel)
    for rel in sorted(set(entries) - seen):
        problems.append("missing: " + rel)
    return problems


def provenance(root, args, rec):
    """Raises ProvenanceError on the FIRST failing step. Returns the evidence dict. Candidate Python is never executed or imported."""
    ev = {}
    gitdir = root / ".git"
    steps = []

    def ok(name, detail=""):
        steps.append(name)
        print("OK    provenance: " + name + (" (" + detail + ")" if detail else ""))

    if not root.is_dir():
        raise ProvenanceError("candidate path is not a directory")
    if gitdir.is_symlink() or not gitdir.is_dir():
        raise ProvenanceError("candidate is not a real Git checkout (.git directory required; missing, symlink or gitfile)")
    ok("candidate is a real Git checkout (.git directory)")
    if git(gitdir, "rev-parse", "--show-object-format").decode().strip() != "sha1":
        raise ProvenanceError("object format is not sha1")
    head = git(gitdir, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    if not HEX40.fullmatch(head):
        raise ProvenanceError("HEAD did not resolve to a 40-hex commit")
    craw = read_object(gitdir, "commit", head)
    if head != args.qualification_revision:
        raise ProvenanceError("exact commit mismatch: checkout HEAD %s != --qualification-revision %s" % (head, args.qualification_revision))
    ok("exact commit equals --qualification-revision", head)
    m = re.match(rb"tree ([0-9a-f]{40})\n", craw)
    if not m:
        raise ProvenanceError("commit object has no tree header")
    tree = m.group(1).decode()
    entries = walk_tree(gitdir, tree)
    if args.qualification_tree_id and tree != args.qualification_tree_id:
        raise ProvenanceError("exact tree mismatch: %s != --qualification-tree-id %s" % (tree, args.qualification_tree_id))
    ok("exact tree of the commit re-derived and every tree object re-hashed" + (" and equals --qualification-tree-id" if args.qualification_tree_id else ""), tree)
    problems = worktree_state(root, entries)
    if problems:
        raise ProvenanceError("working tree is not clean relative to the exact tree: " + "; ".join(problems[:5]) + (" (+%d more)" % (len(problems) - 5) if len(problems) > 5 else ""))
    ok("clean state: working tree equals the exact tree (%d files; no extra, missing or modified file)" % len(entries))
    rev = rec.get("qualification", {}).get("revision")
    if rev != args.qualification_revision:
        raise ProvenanceError("record qualification.revision %r != --qualification-revision" % (rev,))
    com_rel = rec.get("commitment", {}).get("path")
    sp(root, com_rel)
    if com_rel not in entries or entries[com_rel][0] == "120000":
        raise ProvenanceError("commitment file %r is not a regular file of the exact tree" % (com_rel,))
    digest = hf(root / com_rel)
    if digest != args.expect_commitment_sha256:
        raise ProvenanceError("commitment digest mismatch: tree has %s, --expect-commitment-sha256 is %s" % (digest, args.expect_commitment_sha256))
    if rec.get("commitment", {}).get("sha256") != args.expect_commitment_sha256:
        raise ProvenanceError("record commitment.sha256 != --expect-commitment-sha256")
    ok("expected commitment digest equals the exact tree's commitment file and the record", digest)
    ev.update({"commit": head, "tree": tree, "clean": True, "tracked_file_count": len(entries), "commitment_sha256": digest,
               "anchors": {"qualification_revision": args.qualification_revision, "expect_commitment_sha256": args.expect_commitment_sha256,
                           "qualification_tree_id": args.qualification_tree_id or None}, "provenance_steps": steps})
    return ev, sorted(entries)


def crosscheck_gate(root, cm, cm_rel, tree_entries):
    """OPT-IN, runs only after provenance and every byte check passed. Executes the (anchored, byte-verified) candidate gate read-only in an
    isolated throw-away copy: python -I -B, empty environment, cwd outside the tree. Never used to establish provenance."""
    work = Path(tempfile.mkdtemp(prefix="freeze-crosscheck-"))
    try:
        cp = work / "tree"
        for rel in tree_entries:
            dst = cp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / rel, dst)
        code = ("import sys, json; from pathlib import Path; sys.dont_write_bytecode = True; sys.path.insert(0, %r); import mvp_acceptance_gate as g; "
                "print(json.dumps({'files': g.commit_files(Path(%r)), 'file': g.COMMITMENT_FILE}))" % (str(cp / "tools"), str(cp)))
        env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
        p = subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True, text=True, cwd=str(work), env=env, timeout=300)
        if p.returncode != 0:
            check(False, "gate commit_files() ran read-only (crosscheck)", p.stderr[-300:])
            return
        out = json.loads(p.stdout.strip().splitlines()[-1])
        present, committed = set(out["files"]), set(cm["files"])
        check(present == committed, "gate commit_files() == committed list (crosscheck; no uncommitted or missing file)",
              "uncommitted=%s missing=%s" % (sorted(present - committed)[:10], sorted(committed - present)[:10]))
        check(out["file"] == cm_rel, "gate COMMITMENT_FILE equals the record's commitment path (crosscheck)", "%s vs %s" % (out["file"], cm_rel))
    finally:
        shutil.rmtree(work, ignore_errors=True)


def tree_checks(root, cm):
    for rel, d in sorted(cm["files"].items()):
        p = sp(root, rel)
        if p.is_symlink() or not p.is_file():
            check(False, "committed file present and regular: " + rel)
        elif hf(p) != d:
            check(False, "committed file bytes match: " + rel)
    check(not [f for f in cm["files"] if any((root.joinpath(*Path(f).parts[:i])).is_symlink() for i in range(1, len(Path(f).parts) + 1))], "no symlink in or above committed set")
    check(not [c for c in cm.get("must_remain_absent", []) if sp(root, c).exists() or sp(root, c).is_symlink()], "must_remain_absent files absent")
    caches = [str(q.relative_to(root)) for q in root.rglob("__pycache__") if ".git" not in q.parts]
    check(not caches, "no __pycache__ directory in the tree", str(caches[:5]))
    print("OK    per-file bytes checked: %d files" % len(cm["files"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--qualification-tree", required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("--qualification-revision", required=True, help="independently supplied 40-hex commit of the candidate (REQUIRED)")
    ap.add_argument("--expect-commitment-sha256", required=True, help="independently supplied sha256 of the candidate commitment file (REQUIRED)")
    ap.add_argument("--qualification-tree-id", help="optional independently supplied 40-hex tree id of the candidate commit")
    ap.add_argument("--evidence-out", help="write the evidence JSON here (exact commit/tree, anchors, result)")
    ap.add_argument("--require-approved", action="store_true")
    ap.add_argument("--require-final-tree", action="store_true")
    ap.add_argument("--crosscheck-candidate-gate", action="store_true", help="after all anchored checks pass, ALSO run the gate's commit_files() in isolation (executes candidate code)")
    args = ap.parse_args()
    if not HEX40.fullmatch(args.qualification_revision) or not HEX64.fullmatch(args.expect_commitment_sha256) or (
            args.qualification_tree_id and not HEX40.fullmatch(args.qualification_tree_id)):
        print("anchors must be a full lowercase 40-hex commit (and optional tree) and a 64-hex sha256; branch names, tags and abbreviations are refused", file=sys.stderr)
        return 2
    root = Path(args.qualification_tree).resolve()
    raw = Path(args.record).read_bytes()
    try:
        rec = json.loads(raw)
    except Exception as e:
        print("unreadable record: %s" % e, file=sys.stderr)
        return 2
    evidence = {"schema": "cognous.ocs-qgate-05-trusted-freeze-verification/1", "mode": "trusted-anchored",
                "verifier": {"path": "docs/mvp-recovery/qgate-05/freeze/verify_freeze_record.py", "sha256": hf(__file__)},
                "record": {"path": os.path.basename(args.record), "sha256": h(raw)}, "git_invocation": GIT_HARDENING,
                "candidate_code_executed": False, "qualifying": False}

    def finish(code, extra=None):
        evidence["result"] = "PASS" if code == 0 else "FAIL"
        evidence["failing_checks"] = list(FAILS)
        evidence["qualifying"] = code == 0 and evidence.get("provenance_complete") is True
        evidence.update(extra or {})
        if args.evidence_out:
            Path(args.evidence_out).write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
        return code

    try:
        ev, tracked = provenance(root, args, rec)
    except (ProvenanceError, ValueError, OSError, subprocess.SubprocessError) as e:
        print("FAIL  provenance: %s" % e)
        print("verify_freeze_record: FAIL (provenance not established; no candidate data interpreted, no candidate code executed)")
        FAILS.append("provenance")
        return finish(1, {"provenance_complete": False, "provenance_error": str(e)})
    evidence.update(ev)
    evidence["provenance_complete"] = True
    print("EVIDENCE qualification_commit=%s qualification_tree=%s commitment_sha256=%s" % (ev["commit"], ev["tree"], ev["commitment_sha256"]))
    check(raw == (json.dumps(rec, indent=2, sort_keys=True) + "\n").encode(), "record is in canonical serialization")
    check(rec.get("schema") == "cognous.ocs-mvp-qgate-05-freeze-record/1", "schema")
    rev = rec.get("qualification", {}).get("revision")
    check(isinstance(rev, str) and HEX40.fullmatch(rev) is not None, "qualification revision is 40-hex")
    check(rev == args.qualification_revision, "qualification revision equals --qualification-revision")
    try:
        exp, cm, bat = expected_record(root, rec, args)
        compare(exp, rec)
        check(rec["commitment"]["sha256"] == args.expect_commitment_sha256 == hf(sp(root, rec["commitment"]["path"])), "commitment sha256 equals the externally supplied value")
        limitations_ok(rec)
        tree_checks(root, cm)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as e:
        check(False, "candidate data readable and well-formed", repr(e)[:200])
        print("verify_freeze_record: FAIL (%d failing checks)" % len(FAILS))
        return finish(1)
    if args.crosscheck_candidate_gate:
        if FAILS:
            print("SKIP  gate crosscheck: earlier checks failed; candidate code is not executed")
        else:
            evidence["candidate_code_executed"] = True
            crosscheck_gate(root, cm, rec["commitment"]["path"], tracked)
    else:
        print("SKIP  gate commit_files() crosscheck not requested; no candidate code executed")
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
    return finish(1 if FAILS else 0, {"verified_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})


if __name__ == "__main__":
    sys.exit(main())
