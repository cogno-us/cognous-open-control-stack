"""D-H1: nested snapshot members are validated as strictly as the top level (non-authorizing)."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("snapshot_nested", ROOT / "tools" / "collateral_evidence_snapshot.py")
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)
DATA = json.loads((ROOT / "collateral" / "evidence-snapshot.json").read_text(encoding="utf-8"))


def mutate(fn):
    data = copy.deepcopy(DATA)
    fn(data)
    return data


def set_path(*path, value):
    def apply(data):
        node = data
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
    return apply


def c1(data):
    return data["separate_profile_evidence"][0]


MUTATIONS = {
    "generation scope": set_path("evidence_generation", "scope", value="production-ready certified external settlement"),
    "generation extra member": set_path("evidence_generation", "production_authorized", value=True),
    "lock extra member": set_path("component_lock", "certified", value=True),
    "document evidence_scope": set_path("documents", 0, "evidence_scope", value="certified for production"),
    "document extra member": set_path("documents", 0, "approved", value=True),
    "document version": set_path("documents", 0, "version", value="9.9.9"),
    "c1 scope": lambda d: c1(d).__setitem__("scope", "production certified"),
    "c1 cp sha zeros": lambda d: c1(d).__setitem__("control_plane_reviewed_source_sha", "0" * 40),
    "c1 er sha zeros": lambda d: c1(d).__setitem__("execution_runtime_reviewed_source_sha", "0" * 40),
    "c1 extra member": lambda d: c1(d).__setitem__("certified", True),
    "assurance C0": set_path("assurance_levels", "C0", value="atomic and production ready"),
    "assurance C1": set_path("assurance_levels", "C1", value="same-host; not enabled by default; certified"),
    "version": set_path("version", value="0.0.0"),
    "generated_at future": set_path("generated_at", value="2999-01-01T00:00:00+00:00"),
    "generated_at naive": set_path("generated_at", value="2026-10-20T00:00:00"),
    "limitation claim": lambda d: d["limitations"].append("The reference is production ready and certified."),
    "extra profile entry": lambda d: d["separate_profile_evidence"].append({"id": "prod", "status": "production"}),
    "historical extra member": set_path("historical_snapshots", 0, "current", value=True),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_nested_mutation_is_refused(name):
    with pytest.raises(snapshot.SnapshotError):
        snapshot.validate_data(mutate(MUTATIONS[name]), ROOT)


def test_current_snapshot_still_validates():
    snapshot.validate_data(copy.deepcopy(DATA), ROOT)


def test_boundary_wording_accepts_negations_and_refuses_claims():
    f = snapshot.boundary_wording_findings
    assert f("No production or external settlement claim") == []
    assert f("not a C1/C2/C3 release claim") == []
    assert f("bounded synthetic; production ready") != []
    assert f("certified for production") != []
