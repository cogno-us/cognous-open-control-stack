"""Regression tests for the trusted QGATE-05 freeze verifier (P1 item 10, csf_ffe0c01223ab0e3abc4653cf).

Invariant: no byte of Python from the candidate Qualification tree is imported or executed before the candidate's exact commit, exact tree,
clean state and commitment digest have been matched, fail-fast, against anchors supplied independently of the candidate and of the record.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

FREEZE = Path(__file__).resolve().parents[1] / "docs/mvp-recovery/qgate-05/freeze"
VERIFIER = FREEZE / "verify_freeze_record.py"
BUILDER = FREEZE / "build_freeze_record.py"
ORDER = ("control_plane", "runtime", "replay", "evidence_pack", "odes", "verifier", "action_manifest", "hub")
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def git(tree, *args):
    env = dict(os.environ, **GIT_ENV)
    return subprocess.run(["git", "-C", str(tree), *args], check=True, capture_output=True, text=True, env=env).stdout.strip()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Candidate:
    """A synthetic Qualification checkout whose tools/mvp_acceptance_gate.py writes a marker file when imported."""

    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.tree = self.tmp / "cand"
        self.marker = self.tmp / "MARKER_candidate_code_ran"
        t = self.tree
        for d in ("tools", "process/mvp-chain", "process/mvp-acceptance"):
            (t / d).mkdir(parents=True)
        (t / "tools/mvp_acceptance_gate.py").write_text(
            "import pathlib\npathlib.Path(%r).write_text('executed at import')\n"
            "COMMITMENT_FILE='process/mvp-acceptance/candidate-commitment.proposed.v1.json'\n"
            "def commit_files(root):\n    return []\n" % str(self.marker))
        self.shas = {n: ("%02x" % (i + 1)) * 20 for i, n in enumerate(ORDER)}
        comp = {"components": {n: {"sha": s} for n, s in self.shas.items()}}
        self.w("process/mvp-chain/tuple-pin.proposed.json", comp)
        self.w("process/mvp-acceptance/candidate-identity.inputs.json", comp)
        self.w("process/mvp-acceptance/expectations.proposed.v1.json", {"rows": [
            {"id": "VER-01", "all": [{"obs": "chain.verifier.A.exit_code", "value": [0]}]},
            {"id": "VER-03", "all": [{"obs": "chain.verifier.B.exit_code", "value": 1}], "not_applicable_if": [{"value": [0]}]}]})
        oracle_rel = "process/mvp-acceptance/expectations.proposed.v1.json"
        self.w("process/mvp-acceptance/mandatory-battery.proposed.v1.json",
               {"oracle": {"expectations_in_force": oracle_rel, "unchanged_files_sha256": {oracle_rel: sha256(t / oracle_rel)}}, "tests": []})
        self.w("process/mvp-acceptance/candidate-commitment.proposed.v1.json", {"candidate_version": "x", "files": {}})
        git(t, "init", "-q")
        git(t, "add", "-A")
        git(t, "commit", "-qm", "candidate")
        self.commit = git(t, "rev-parse", "HEAD")
        self.treeid = git(t, "rev-parse", "HEAD^{tree}")
        self.commitment = "process/mvp-acceptance/candidate-commitment.proposed.v1.json"
        self.digest = sha256(t / self.commitment)
        self.record = self.tmp / "record.json"
        self.build_record()

    def w(self, rel, obj):
        (self.tree / rel).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")

    def build_record(self):
        args = [sys.executable, "-I", "-B", str(BUILDER), "--qualification-tree", str(self.tree), "--qualification-revision", self.commit,
                "--prepared-utc", "test", "--out", str(self.record)]
        for n in ORDER:
            args += ["--" + n.replace("_", "-"), self.shas[n]]
        p = subprocess.run(args, capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr

    def run(self, revision="__commit__", digest="__digest__", extra=(), tree=None, record=None, tree_id=None, evidence=None):
        a = [sys.executable, "-I", "-B", str(VERIFIER), "--qualification-tree", str(tree or self.tree), "--record", str(record or self.record)]
        if revision is not None:
            a += ["--qualification-revision", self.commit if revision == "__commit__" else revision]
        if digest is not None:
            a += ["--expect-commitment-sha256", self.digest if digest == "__digest__" else digest]
        if tree_id:
            a += ["--qualification-tree-id", tree_id]
        if evidence:
            a += ["--evidence-out", str(evidence)]
        return subprocess.run(a + list(extra), capture_output=True, text=True, cwd="/")


@pytest.fixture
def cand(tmp_path):
    return Candidate(tmp_path)


def provenance_failed(p):
    return p.returncode == 1 and "FAIL  provenance:" in p.stdout and "no candidate code executed" in p.stdout


def test_positive_exact_revision_passes_without_executing_candidate_code(cand, tmp_path):
    ev = tmp_path / "ev.json"
    p = cand.run(tree_id=cand.treeid, evidence=ev)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "verify_freeze_record: PASS (0 failing checks)" in p.stdout
    assert not cand.marker.exists(), "candidate gate was imported/executed"
    e = json.loads(ev.read_text())
    assert e["result"] == "PASS" and e["qualifying"] is True and e["candidate_code_executed"] is False
    assert e["mode"] == "trusted-anchored"


def test_evidence_records_exact_commit_and_tree(cand, tmp_path):
    ev = tmp_path / "ev.json"
    p = cand.run(evidence=ev)
    assert p.returncode == 0, p.stdout
    e = json.loads(ev.read_text())
    assert e["commit"] == cand.commit == git(cand.tree, "rev-parse", "HEAD")
    assert e["tree"] == cand.treeid == git(cand.tree, "rev-parse", "HEAD^{tree}")
    assert e["commitment_sha256"] == cand.digest and e["clean"] is True
    assert e["anchors"]["qualification_revision"] == cand.commit and e["anchors"]["expect_commitment_sha256"] == cand.digest
    assert e["verifier"]["sha256"] == sha256(VERIFIER) and e["record"]["sha256"] == sha256(cand.record)
    assert "EVIDENCE qualification_commit=%s qualification_tree=%s" % (cand.commit, cand.treeid) in p.stdout


def test_lane_reproducer_wrong_revision_no_anchor_match_never_runs_candidate_code(cand):
    """Converted item10 reproducer: wrong revision; base verifier imported the candidate gate anyway (marker written)."""
    p = cand.run(revision="f" * 40)
    assert provenance_failed(p), p.stdout
    assert "exact commit mismatch" in p.stdout
    assert not cand.marker.exists(), "candidate import marker executed before provenance was established"


def test_malicious_candidate_never_executes_even_with_all_anchors_correct(cand):
    assert cand.run().returncode == 0
    assert not cand.marker.exists()


def test_wrong_tree_id_anchor_fails_fast(cand):
    p = cand.run(tree_id="0" * 40)
    assert provenance_failed(p) and "exact tree mismatch" in p.stdout
    assert not cand.marker.exists()


@pytest.mark.parametrize("anchor", ["main", "master", "HEAD", "v1", "abc1234", "F" * 40, "refs/heads/main", ""])
def test_branch_tag_abbreviation_anchors_refused(cand, anchor):
    p = cand.run(revision=anchor)
    assert p.returncode == 2 and "refused" in p.stderr
    assert not cand.marker.exists()


def test_required_anchors_are_required(cand):
    assert cand.run(revision=None).returncode == 2
    assert cand.run(digest=None).returncode == 2
    assert not cand.marker.exists()


def test_branch_substitution_head_on_other_commit_fails(cand):
    (cand.tree / "extra.txt").write_text("x")
    git(cand.tree, "add", "-A")
    git(cand.tree, "commit", "-qm", "second")
    git(cand.tree, "branch", cand.commit[:12])  # branch named like the anchor prefix
    p = cand.run()  # anchors still name the first commit, checkout HEAD is the second
    assert provenance_failed(p) and "exact commit mismatch" in p.stdout
    git(cand.tree, "checkout", "-q", "-b", "lookalike", cand.commit)
    git(cand.tree, "reset", "-q", "--hard", "HEAD~0")
    assert cand.run().returncode == 0  # genuinely at the anchored commit: still passes
    assert not cand.marker.exists()


def test_tag_substitution_annotated_tag_object_or_tag_named_like_sha_fails(cand):
    (cand.tree / "extra.txt").write_text("x")
    git(cand.tree, "add", "-A")
    git(cand.tree, "commit", "-qm", "second")
    second = git(cand.tree, "rev-parse", "HEAD")
    git(cand.tree, "tag", cand.commit, second)  # lightweight tag named exactly like the anchor, pointing at a different commit
    p = cand.run()
    assert provenance_failed(p) and "exact commit mismatch" in p.stdout
    git(cand.tree, "tag", "-a", "-m", "m", "annot", second)
    tag_object = git(cand.tree, "rev-parse", "annot")
    assert tag_object != second
    p = cand.run(revision=tag_object)  # annotated tag OBJECT id is not the commit
    assert provenance_failed(p) and "exact commit mismatch" in p.stdout
    assert not cand.marker.exists()


def test_replace_ref_substitution_is_ignored(cand):
    (cand.tree / "extra.txt").write_text("x")
    git(cand.tree, "add", "-A")
    git(cand.tree, "commit", "-qm", "second")
    second = git(cand.tree, "rev-parse", "HEAD")
    git(cand.tree, "reset", "-q", "--hard", cand.commit)
    git(cand.tree, "replace", cand.commit, second)  # would make `git` show the second commit's content for HEAD
    p = cand.run()
    assert p.returncode == 0, p.stdout  # real objects are used; replacement refs do not change the anchored commit/tree
    assert not cand.marker.exists()


def test_dirty_tree_modified_untracked_deleted_fail(cand):
    gate = cand.tree / "tools/mvp_acceptance_gate.py"
    original = gate.read_bytes()
    gate.write_bytes(original + b"# tampered\n")
    p = cand.run()
    assert provenance_failed(p) and "not clean" in p.stdout and "content differs" in p.stdout
    gate.write_bytes(original)
    (cand.tree / "untracked.py").write_text("print(1)\n")
    p = cand.run()
    assert provenance_failed(p) and "untracked or extra: untracked.py" in p.stdout
    (cand.tree / "untracked.py").unlink()
    (cand.tree / "process/mvp-chain/tuple-pin.proposed.json").unlink()
    p = cand.run()
    assert provenance_failed(p) and "missing:" in p.stdout
    assert not cand.marker.exists()


def test_dirty_tree_exec_bit_and_gitignored_extra_file_fail(cand):
    (cand.tree / ".git/info/exclude").write_text("hidden.py\n")  # git status would not report this ignored file
    (cand.tree / "hidden.py").write_text("print(1)\n")
    p = cand.run()
    assert provenance_failed(p) and "untracked or extra: hidden.py" in p.stdout
    (cand.tree / "hidden.py").unlink()
    gate = cand.tree / "tools/mvp_acceptance_gate.py"
    gate.chmod(0o755)
    p = cand.run()
    assert provenance_failed(p) and "type/mode differs" in p.stdout
    assert not cand.marker.exists()


def test_missing_git_directory_fails(cand, tmp_path):
    import shutil
    plain = tmp_path / "plain"
    shutil.copytree(cand.tree, plain, ignore=shutil.ignore_patterns(".git"))
    p = cand.run(tree=plain)
    assert provenance_failed(p) and "not a real Git checkout" in p.stdout
    # a gitfile (".git" as a file pointing elsewhere) is also refused
    (plain / ".git").write_text("gitdir: %s\n" % (cand.tree / ".git"))
    p = cand.run(tree=plain)
    assert provenance_failed(p) and "not a real Git checkout" in p.stdout
    assert not cand.marker.exists()


def test_wrong_commitment_digest_fails(cand):
    p = cand.run(digest="0" * 64)
    assert provenance_failed(p) and "commitment digest mismatch" in p.stdout
    assert not cand.marker.exists()


def test_record_claims_must_equal_anchors(cand, tmp_path):
    rec = json.loads(cand.record.read_text())
    rec["qualification"]["revision"] = "e" * 40
    bad = tmp_path / "bad-record.json"
    bad.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    p = cand.run(record=bad)
    assert provenance_failed(p) and "record qualification.revision" in p.stdout
    rec = json.loads(cand.record.read_text())
    rec["commitment"]["path"] = "../../outside.json"
    bad.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    p = cand.run(record=bad)
    assert provenance_failed(p) and "unsafe relative path" in p.stdout
    assert not cand.marker.exists()


def test_failed_run_never_emits_qualifying_evidence(cand, tmp_path):
    ev = tmp_path / "ev.json"
    p = cand.run(revision="f" * 40, evidence=ev)
    assert p.returncode == 1
    e = json.loads(ev.read_text())
    assert e["result"] == "FAIL" and e["qualifying"] is False and e["provenance_complete"] is False and e["candidate_code_executed"] is False


def test_no_unanchored_skip_gate_or_crosscheck_mode_exists(cand):
    for flag in ("--skip-gate", "--unanchored", "--allow-unanchored", "--crosscheck-candidate-gate"):
        p = cand.run(extra=[flag])
        assert p.returncode == 2 and "unrecognized arguments" in p.stderr
    src = VERIFIER.read_text()
    for needle in ("skip_gate", "crosscheck", "mvp_acceptance_gate", "commit_files(", "tempfile"):
        assert needle not in src.replace("no gate call, no commit_files() cross-check", "").replace("(no gate import", ""), needle
    assert not cand.marker.exists()


def test_hostile_git_config_and_attributes_never_execute(cand):
    """Repo-controlled fsmonitor, filter, textconv, external diff, alias and hook helpers must not run."""
    m = cand.tmp / "MARKER_git_helper"
    (cand.tree / ".gitattributes").write_text("*.py filter=x diff=x\n")
    git(cand.tree, "add", ".gitattributes")
    git(cand.tree, "commit", "-qm", "attrs")
    cand.commit = git(cand.tree, "rev-parse", "HEAD")
    cand.build_record()
    cfg = cand.tree / ".git/config"
    cfg.write_text(cfg.read_text() + "[core]\n\tfsmonitor = touch %s\n[filter \"x\"]\n\tclean = touch %s\n\tsmudge = touch %s\n"
                   "[diff \"x\"]\n\ttextconv = touch %s\n[diff]\n\texternal = touch %s\n" % ((m,) * 5))
    hooks = cand.tree / ".git/hooks"
    hooks.mkdir(exist_ok=True)
    for name in ("post-checkout", "post-index-change", "reference-transaction", "pre-auto-gc"):
        h = hooks / name
        h.write_text("#!/bin/sh\ntouch %s\n" % m)
        h.chmod(0o755)
    p = cand.run()
    assert p.returncode == 0, p.stdout + p.stderr
    assert not m.exists(), "a repo-controlled git helper ran"
    assert not cand.marker.exists()


def test_git_hardening_has_no_lazy_fetch_and_evidence_text_is_accurate(cand, tmp_path):
    src = VERIFIER.read_text()
    assert '"GIT_NO_LAZY_FETCH": "1"' in src and "protocol.allow=never" in src
    ev = tmp_path / "ev.json"
    assert cand.run(evidence=ev).returncode == 0
    gi = json.loads(ev.read_text())["git_invocation"]
    assert "GIT_NO_LAZY_FETCH=1" in gi and "no ls-tree" in gi and "only rev-parse/cat-file" in gi
    assert "ls-tree" not in src.split("Git is invoked only for object reads")[1].split("\n")[0]


def test_fifo_at_tracked_path_is_refused_not_hung(cand):
    gate = cand.tree / "tools/mvp_acceptance_gate.py"
    gate.unlink()
    os.mkfifo(gate)
    p = subprocess.run([sys.executable, "-I", "-B", str(VERIFIER), "--qualification-tree", str(cand.tree), "--record", str(cand.record),
                        "--qualification-revision", cand.commit, "--expect-commitment-sha256", cand.digest], capture_output=True, text=True, cwd="/", timeout=60)
    assert provenance_failed(p) and "special file" in p.stdout


def test_extra_empty_directory_is_a_mismatch(cand):
    (cand.tree / "tools/emptydir").mkdir()
    p = cand.run()
    assert provenance_failed(p) and "extra empty directory: tools/emptydir" in p.stdout


def test_eol_converted_checkout_fails_closed(cand):
    gate = cand.tree / "tools/mvp_acceptance_gate.py"
    gate.write_bytes(gate.read_bytes().replace(b"\n", b"\r\n"))
    p = cand.run()
    assert provenance_failed(p) and "content differs" in p.stdout


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(qualification="not-a-dict"),
    lambda r: r.update(commitment=["x"]),
    lambda r: r.update(qualification={"revision": 5}),
    lambda r: r.update(battery=None),
])
def test_malformed_record_yields_fail_evidence_not_traceback(cand, tmp_path, mutate):
    rec = json.loads(cand.record.read_text())
    mutate(rec)
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    ev = tmp_path / "ev.json"
    p = cand.run(record=bad, evidence=ev)
    assert p.returncode == 1 and "Traceback" not in p.stderr, p.stdout + p.stderr
    e = json.loads(ev.read_text())
    assert e["result"] == "FAIL" and e["qualifying"] is False and e["candidate_code_executed"] is False
    assert not cand.marker.exists()


def test_malformed_record_after_provenance_yields_fail_evidence(cand, tmp_path):
    rec = json.loads(cand.record.read_text())
    rec["owner_approval"] = "oops"  # reaches the post-provenance code with a wrongly typed field
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    ev = tmp_path / "ev.json"
    p = cand.run(record=bad, evidence=ev)
    assert p.returncode == 1 and "Traceback" not in p.stderr, p.stdout + p.stderr
    e = json.loads(ev.read_text())
    assert e["result"] == "FAIL" and e["qualifying"] is False


def test_non_dict_record_yields_fail_evidence(cand, tmp_path):
    bad = tmp_path / "list.json"
    bad.write_text("[]\n")
    ev = tmp_path / "ev.json"
    p = cand.run(record=bad, evidence=ev)
    assert p.returncode == 1 and "Traceback" not in p.stderr
    assert json.loads(ev.read_text())["qualifying"] is False


def test_evidence_records_options_and_isolation(cand, tmp_path):
    ev = tmp_path / "ev.json"
    cand.run(evidence=ev)
    e = json.loads(ev.read_text())
    assert e["options"] == {"require_approved": False, "require_final_tree": False} and e["isolated_interpreter"] is True
    cand.run(evidence=ev, extra=["--require-approved", "--require-final-tree"])
    e = json.loads(ev.read_text())
    assert e["options"] == {"require_approved": True, "require_final_tree": True}
    assert e["result"] == "FAIL" and e["qualifying"] is False  # synthetic record is unfrozen: --require-approved must fail


def test_refuses_to_run_without_isolated_interpreter(cand):
    p = subprocess.run([sys.executable, "-B", str(VERIFIER), "--qualification-tree", str(cand.tree), "--record", str(cand.record),
                        "--qualification-revision", cand.commit, "--expect-commitment-sha256", cand.digest], capture_output=True, text=True, cwd="/")
    assert p.returncode == 2 and "must run isolated" in p.stderr
    assert not cand.marker.exists()


# ---- historical record --------------------------------------------------------------------------------------------------------------------
HISTORICAL = FREEZE / "freeze-record.fa12c699.json"
HISTORICAL_SHA256 = "21618898049e03dbbcc6c412f0dfff9be2eff564e8ec07ef16c7cdf08d93d0b5"


def test_historical_freeze_record_is_preserved_unchanged():
    assert sha256(HISTORICAL) == HISTORICAL_SHA256


def test_new_dated_reverification_evidence_binds_historical_record():
    files = sorted((FREEZE / "evidence").glob("freeze-record.fa12c699.trusted-reverification.*.json"))
    assert files, "missing new dated re-verification evidence"
    e = json.loads(files[-1].read_text())
    assert e["schema"] == "cognous.ocs-qgate-05-trusted-freeze-verification/1" and e["mode"] == "trusted-anchored"
    assert e["result"] == "PASS" and e["qualifying"] is True
    assert e["record"]["sha256"] == HISTORICAL_SHA256
    assert e["commit"] == "fa12c699939880149ed3997cbc2b11b264b23acd" and len(e["tree"]) == 40
    assert e["anchors"]["qualification_revision"] == e["commit"]
    assert e["candidate_code_executed"] is False
    assert e["verifier"]["sha256"] == sha256(VERIFIER), "verifier changed: add a NEW dated re-verification evidence file"
    assert e["options"] == {"require_approved": True, "require_final_tree": True} and e["isolated_interpreter"] is True
    assert json.loads(HISTORICAL.read_text())["qualification"]["revision"] == e["commit"]


@pytest.mark.skipif(not os.environ.get("QUALIFICATION_CHECKOUT_FA12C699"), reason="set QUALIFICATION_CHECKOUT_FA12C699 to a clean checkout to re-verify live")
def test_live_reverification_of_historical_record():
    root = os.environ["QUALIFICATION_CHECKOUT_FA12C699"]
    rec = json.loads(HISTORICAL.read_text())
    p = subprocess.run([sys.executable, "-I", "-B", str(VERIFIER), "--qualification-tree", root, "--record", str(HISTORICAL), "--qualification-revision",
                        rec["qualification"]["revision"], "--expect-commitment-sha256", rec["commitment"]["sha256"], "--require-approved", "--require-final-tree"],
                       capture_output=True, text=True, cwd="/")
    assert p.returncode == 0, p.stdout[-2000:]
