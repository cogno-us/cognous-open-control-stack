"""Scan 5 F-T1-1 / F-T2-4: scoped, Unicode-folded boundary wording over manifest strings and document bodies."""
import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("snapshot_scan5", ROOT / "tools" / "collateral_evidence_snapshot.py")
snap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snap)
DATA = json.loads((ROOT / "collateral" / "evidence-snapshot.json").read_text(encoding="utf-8"))

CLAIMS = {
    "contrast after negation": "No C2/C3 is claimed, but this release is production ready and certified.",
    "cyrillic homoglyphs": "This build is prоdуction-grade and сertified",
    "zero width space": "This build is produ​ction-grade",
    "soft hyphen": "This build is produ­ction-grade",
    "small capitals": "This build is pʀoduction ready",
    "non-breaking hyphen": "This build is production‑ready",
    "live customers and secure": "This build is approved for live customers and enterprise-grade secure",
    "not only": "Not only is it ready, it is certified.",
    "not a demo": "This is not a demo, it is certified for production.",
    "no-op": "A no-op release is production ready.",
    "safe and audited": "The release is safe and audited.",
    "deployable": "The build is deployable.",
    "compliant": "The build is compliant.",
    "ready for prod": "It is ready for prod.",
    "attested": "The build is attested and certified.",
    "and ends scope": "It does not claim C2 and is production ready.",
}
NEGATED = [
    "No production or external settlement claim",
    "not a C1/C2/C3 release claim",
    "No C2/C3, external settlement, production authority, distributed exactly-once or compliance claim is made.",
    "This build does not claim production readiness.",
    "No release is certified for production.",
    "A non-authorizing note",
    "bounded synthetic default release; local SQLite destination; no production or external settlement claim",
]


@pytest.mark.parametrize("name", sorted(CLAIMS))
def test_claim_is_found_by_the_scan(name):
    assert snap.boundary_wording_findings(CLAIMS[name]) != []


@pytest.mark.parametrize("name", sorted(CLAIMS))
def test_claim_in_a_limitation_is_refused(name):
    data = copy.deepcopy(DATA)
    data["limitations"].append(CLAIMS[name])
    with pytest.raises(snap.SnapshotError, match="unnegated boundary claim"):
        snap.validate_data(data, ROOT)


@pytest.mark.parametrize("text", NEGATED)
def test_negated_wording_is_accepted(text):
    assert snap.boundary_wording_findings(text) == []


def test_current_documents_have_no_body_findings():
    for row in DATA["documents"]:
        text = (ROOT / row["path"]).read_text(encoding="utf-8")
        assert snap.body_wording_findings(text) == [], row["path"]


def test_fold_text_maps_lookalikes_and_drops_invisible_characters():
    assert snap.fold_text("PRоD​UCtION‑Ready") == "production-ready"


@pytest.fixture()
def tree(tmp_path):
    for name in ("component-lock.json", "collateral", "docs"):
        src = ROOT / name
        shutil.copytree(src, tmp_path / name) if src.is_dir() else shutil.copy(src, tmp_path / name)
    return tmp_path


def rewrite(tree, index, edit):
    data = copy.deepcopy(DATA)
    row = data["documents"][index]
    path = tree / row["path"]
    path.write_text(edit(path.read_text(encoding="utf-8")), encoding="utf-8")
    row["document_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return data


def test_unmodified_copy_validates(tree):
    snap.validate_data(copy.deepcopy(DATA), tree)


def test_version_prefix_is_not_the_identity(tree):
    data = rewrite(tree, 0, lambda t: t.replace("`version=2.0.1`", "`version=2.0.10`"))
    with pytest.raises(snap.SnapshotError, match="version differs"):
        snap.validate_data(data, tree)


def test_identity_outside_the_identity_line_is_refused(tree):
    data = rewrite(tree, 0, lambda t: t.replace("`version=2.0.1`", "`version=9.9.9`") + "\nversion=2.0.1 document_id=cognous-business-collateral\n")
    with pytest.raises(snap.SnapshotError, match="version differs"):
        snap.validate_data(data, tree)


def test_second_identity_line_is_refused(tree):
    first = (ROOT / DATA["documents"][0]["path"]).read_text(encoding="utf-8").splitlines()[4]
    data = rewrite(tree, 0, lambda t: t + "\n" + first + "\n")
    with pytest.raises(snap.SnapshotError, match="exactly one"):
        snap.validate_data(data, tree)


def test_pin_must_be_on_the_identity_line(tree):
    pin = snap.EXPECTED_HUB_PIN
    data = rewrite(tree, 0, lambda t: t.replace("accepted hub source `" + pin + "`", "accepted hub source `unpinned`") + "\n" + pin + "\n")
    with pytest.raises(snap.SnapshotError, match="pin/digest"):
        snap.validate_data(data, tree)


@pytest.mark.parametrize("index", [0, 1, 2])
def test_body_claim_is_refused_even_with_matching_digest(tree, index):
    data = rewrite(tree, index, lambda t: t + "\nThis release is production ready and certified for settlement.\n")
    with pytest.raises(snap.SnapshotError, match="body has an unnegated boundary claim"):
        snap.validate_data(data, tree)
