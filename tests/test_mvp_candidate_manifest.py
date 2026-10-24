"""Tests for the OCS MVP candidate manifest validator (standard library plus pytest).

SPDX-License-Identifier: Apache-2.0

Non-authorizing. The validator checks internal consistency and file hashes. It gives no verdict about the candidate.
"""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from tools.mvp_candidate_manifest import validate_candidate_manifest as v

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/mvp-package/candidate-manifest.json"


@pytest.fixture()
def good():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture()
def tree(tmp_path):
    """A scratch copy of just the files the manifest hashes, so file tampering never touches the repository."""
    for rel in ("component-lock.json", "docs/mvp-package/requirements-mvp-py313.txt",
                "docs/mvp-recovery/ingress-qualification-environment-profile.md", "tools/mvp_ingress/BOUNDARY.md",
                "tools/mvp_env_record/capture_env_record.py", "docs/mvp-recovery/registry/catalogue-v0.1/manifest.json"):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, dst)
    for p in (ROOT / "tools/mvp_ingress").glob("*.py"):
        shutil.copy(p, tmp_path / "tools/mvp_ingress" / p.name)
    return tmp_path


def errs(m, root=ROOT):
    return v.validate(m, root)


def has(errors, text):
    return any(text in e for e in errors)


def comp(m, name):
    return next(c for c in m["components"] if c["component"] == name)


def test_committed_manifest_validates():
    assert errs(json.loads(MANIFEST.read_text(encoding="utf-8"))) == []


def test_cli_exit_codes(tmp_path, capsys):
    assert v.main(["--print-sha256"]) == 0
    assert "manifest_sha256" in capsys.readouterr().out
    bad = tmp_path / "m.json"
    bad.write_text("{not json", encoding="utf-8")
    assert v.main(["--manifest", str(bad)]) == 2
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["status"] = "OTHER"
    bad.write_text(json.dumps(m), encoding="utf-8")
    assert v.main(["--manifest", str(bad)]) == 1


def test_validation_is_deterministic(good):
    assert errs(good) == errs(copy.deepcopy(good))


def test_pinned_values_are_the_directed_ones(good):
    assert comp(good, "control_plane")["revision"] == "7a4bcd40b3b49e61ff3c294dcca53b52f460b22c"
    assert comp(good, "runtime")["revision"] == "c5e97e87dd239c821b1b4a406a55dcd03c5bc61f"
    assert comp(good, "verifier")["revision"] == "c0b8ba1f55b75db787a320f3de0f79342c6f6826"
    assert good["later_documentation_revisions"][0]["revision"].startswith("39d46b49")
    assert good["registry_catalogue"]["manifest_digest"]["status"] == "superseded-pending"
    assert good["evidence_and_test_runs"]["status"] == "not yet produced"


@pytest.mark.parametrize("bad", ["7a4bcd40", "7A4BCD40B3B49E61FF3C294DCCA53B52F460B22C", "7a4bcd40b3b49e61ff3c294dcca53b52f460b22", "z" * 40, "", None])
def test_rejects_non_full_hex_sha(good, bad):
    comp(good, "control_plane")["revision"] = bad
    assert has(errs(good), "control_plane")


def test_rejects_duplicate_component(good):
    good["components"].append(copy.deepcopy(comp(good, "runtime")))
    assert has(errs(good), "duplicate component")


def test_rejects_missing_component(good):
    good["components"] = [c for c in good["components"] if c["component"] != "replay"]
    assert has(errs(good), "component replay missing")


def test_rejects_duplicate_json_key(tmp_path):
    p = tmp_path / "m.json"
    p.write_text(MANIFEST.read_text(encoding="utf-8").replace('"provisional": true,', '"provisional": true, "provisional": true,'), encoding="utf-8")
    with pytest.raises(ValueError):
        v.load_manifest(p)
    assert v.main(["--manifest", str(p)]) == 2


def test_rejects_later_verifier_as_pin(good):
    comp(good, "verifier")["revision"] = "39d46b494558e271439966bec98b26dc4d040cc4"
    assert has(errs(good), "must not be 39d46b49")


def test_rejects_later_verifier_missing_or_implicitly_qualified(good):
    g2 = copy.deepcopy(good)
    g2["later_documentation_revisions"] = []
    assert has(errs(g2), "must be recorded as a later documentation revision")
    good["later_documentation_revisions"][0]["implicitly_qualified"] = True
    assert has(errs(good), "implicitly_qualified false")


def test_rejects_wrong_status_or_provisional(good):
    good["status"] = "QUALIFIED"
    good["provisional"] = False
    e = errs(good)
    assert has(e, "status must be exactly UNQUALIFIED") and has(e, "provisional must be true")


@pytest.mark.parametrize("path,value", [
    (("authorization", "qualification_verdict"), "PASS"),
    (("authorization", "frozen"), True),
    (("authorization", "release"), "GO"),
    (("authorization", "production"), "READY"),
    (("authorization", "authorizing"), True),
])
def test_rejects_authorization_tampering(good, path, value):
    good[path[0]][path[1]] = value
    assert errs(good)


@pytest.mark.parametrize("text", [
    "all checks PASS for this tuple",
    "this tuple is qualified",
    "the tuple is frozen",
    "the tuple was accepted",
    "certified for use",
    "compliant with the standard",
    "production-ready",
])
def test_rejects_verdict_and_assurance_wording(good, text):
    good["status_note"] = text
    assert has(errs(good), "status_note")


def test_rejects_verdict_like_key_with_value(good):
    good["evidence_and_test_runs"]["overall_result"] = "good"
    assert has(errs(good), "verdict-like")


def test_rejects_evidence_identities_present(good):
    good["evidence_and_test_runs"]["qualification_run_ids"] = ["run-1"]
    good["evidence_and_test_runs"]["status"] = "produced"
    e = errs(good)
    assert has(e, "qualification_run_ids") and has(e, "must be 'not yet produced'")


def test_rejects_commitment_set(good):
    good["qualification_references"]["candidate_commitment_sha256"] = "a" * 64
    assert has(errs(good), "candidate_commitment_sha256 must be null")


def test_rejects_hub_lock_not_marked_stale(good):
    good["hub_lock_notice"]["stale"] = False
    good["hub_lock_notice"]["describes_qualified_mvp"] = True
    e = errs(good)
    assert has(e, "stale must be true") and has(e, "describes_qualified_mvp must be false")


def test_rejects_missing_required_field(good):
    del good["registry_catalogue"]
    assert has(errs(good), "missing required field registry_catalogue")


def test_catalogue_digest_status_rules(good):
    d = good["registry_catalogue"]["manifest_digest"]
    d["status"] = "frozen"
    assert has(errs(good), "status must be one of")
    d["status"] = "superseded"
    assert has(errs(good), "requires a sha256")
    d["successor_value"] = "sha256:" + "b" * 64
    assert errs(good) == []
    d["status"] = "superseded-pending"
    assert has(errs(good), "only when status is superseded")
    d["successor_value"] = None
    d["status"] = "current"
    assert errs(good) == []  # the repository digest equals the recorded value today
    d["value"] = "sha256:" + "c" * 64
    assert has(errs(good), "catalogue digest in the repository")


def test_tampered_fixture_hashes_refused(good, tree):
    assert errs(good, tree) == []
    (tree / "tools/mvp_env_record/capture_env_record.py").write_text("tampered\n")
    assert has(errs(good, tree), "capture_script: sha256 differs")


def test_tampered_ingress_tree_refused(good, tree):
    with (tree / "tools/mvp_ingress/core.py").open("a") as f:
        f.write("# tamper\n")
    assert has(errs(good, tree), "ingress tree digest")


def test_new_or_removed_ingress_file_refused(good, tree):
    (tree / "tools/mvp_ingress/extra.py").write_text("x = 1\n")
    assert has(errs(good, tree), "ingress tree digest")
    (tree / "tools/mvp_ingress/extra.py").unlink()
    (tree / "tools/mvp_ingress/client.py").unlink()
    assert has(errs(good, tree), "ingress tree digest")


def test_tampered_lock_files_refused(good, tree):
    (tree / "component-lock.json").write_text("{}\n")
    (tree / "docs/mvp-package/requirements-mvp-py313.txt").write_text("pydantic==1\n")
    e = errs(good, tree)
    assert has(e, "hub lock file hash differs") and has(e, "dependency lock: sha256 differs") and has(e, "not found in the lock file")


def test_dependency_pin_mismatch_refused(good):
    good["runtime_and_dependencies"]["dependency_lock"]["pins"]["pydantic"] = "9.9.9"
    assert has(errs(good), "pydantic==9.9.9 not found")


def test_python_version_and_flag_refused(good):
    good["runtime_and_dependencies"]["python"] = "3.12"
    good["runtime_and_dependencies"]["dependency_lock"]["install_flag"] = ""
    e = errs(good)
    assert has(e, "python must be 3.13") and has(e, "install_flag")


def test_ingress_digest_algorithm_matches_recorded_value():
    got = v.ingress_tree_digest(ROOT / "tools/mvp_ingress")
    assert got == "ea37100d0827aea08c1c83303c911234e193854978d3313ae6d106688f2a9058"


def test_online_ancestry_logic(good, monkeypatch):
    seen = {}

    def fake(repo, sha):
        seen[repo] = sha
        return ("ahead" if sha.startswith("c0b8") else "identical"), ""

    monkeypatch.setattr(v, "_gh_compare", fake)
    assert v.validate(good, ROOT, online=True) == []
    assert len(seen) == 8
    monkeypatch.setattr(v, "_gh_compare", lambda r, s: ("diverged", ""))
    assert has(v.validate(good, ROOT, online=True), "not an ancestor of main")
    monkeypatch.setattr(v, "_gh_compare", lambda r, s: (None, "boom"))
    assert has(v.validate(good, ROOT, online=True), "lookup failed")


def test_tool_has_no_network_effects_offline():
    src = (ROOT / "tools/mvp_candidate_manifest/validate_candidate_manifest.py").read_text()
    assert "import socket" not in src and "urllib" not in src and "requests" not in src
