#!/usr/bin/env python3
"""Validate the detached collateral evidence snapshot.

This checker is intentionally stdlib-only and bounded to release/collateral drift.
It does not execute or authorize runtime effects.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HUB_PIN = "f7d03c719b9be3b9c3fe0fe300df642b0f408d98"
EXPECTED_LOCK_SHA256 = "dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc"
EXPECTED_DEFAULT_GENERATION = "merged-producers-v1/full-candidate-gate"
EXPECTED_DEFAULT_SCENARIOS = 35
EXPECTED_DEFAULT_RUN = 37694032916
EXPECTED_DEFAULT_ARTIFACT = "5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7"
EXPECTED_C1_RUN = 37682165860
EXPECTED_C1_PASSED = 73
EXPECTED_EXTENSION_PROFILE_CASES = 91
EXPECTED_EXTENSION_GATE_CHECKS = 26
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


class SnapshotError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SnapshotError(message)


def validate_data(data: dict[str, Any], root: Path = ROOT) -> None:
    _require(data.get("schema_version") == "collateral-evidence-snapshot/1", "wrong schema version")
    _require(data.get("document_id") == "cognous-collateral-evidence-snapshot", "wrong manifest document_id")
    _require(data.get("snapshot_status") == "current", "snapshot must be current")

    generated = datetime.fromisoformat(data["generated_at"])
    _require(generated.tzinfo is not None and generated.utcoffset() is not None, "generated_at must be timezone-aware")

    pin = data.get("accepted_hub_pin", "")
    _require(bool(SHA40.fullmatch(pin)), "accepted hub pin must be a 40-char sha")
    _require(pin == EXPECTED_HUB_PIN, "accepted hub pin drift")

    lock = data.get("component_lock", {})
    _require(lock.get("path") == "component-lock.json", "wrong component-lock path")
    _require(lock.get("sha256") == EXPECTED_LOCK_SHA256, "manifest component-lock digest drift")
    _require(sha256_file(root / "component-lock.json") == EXPECTED_LOCK_SHA256, "repository component-lock digest drift")
    _require(lock.get("runtime_profile") == "merged-producers-v1", "wrong selected runtime profile")
    _require(lock.get("selected_control_plane") == "d3dadee70bd319812b207389ab1e0f6efe511916", "selected Control Plane pin drift")
    _require(lock.get("selected_execution_runtime") == "c3c3ee7188b9367cf70b08074b9c40a5c70c94ac", "selected Execution Runtime pin drift")

    generation = data.get("evidence_generation", {})
    _require(generation.get("id") == EXPECTED_DEFAULT_GENERATION, "wrong default evidence generation")
    _require(generation.get("status") == "accepted_default_release", "wrong default evidence status")
    _require(generation.get("workflow_run") == EXPECTED_DEFAULT_RUN, "wrong default workflow run")
    _require(generation.get("acceptance_scenarios") == EXPECTED_DEFAULT_SCENARIOS, "wrong default scenario count")
    _require(generation.get("artifact_sha256") == EXPECTED_DEFAULT_ARTIFACT, "wrong default artifact digest")

    profiles = {item.get("id"): item for item in data.get("separate_profile_evidence", [])}
    c1 = profiles.get("c1-same-host-authority-effect", {})
    _require(c1.get("status") == "separate_optional_profile_ci", "C1 evidence must remain separate")
    _require(c1.get("workflow_run") == EXPECTED_C1_RUN, "wrong C1 workflow run")
    _require(c1.get("passed_tests") == EXPECTED_C1_PASSED, "wrong C1 pass count")
    _require(c1.get("failures") == c1.get("errors") == c1.get("skips") == 0, "C1 result totals drift")

    ext = profiles.get("v1-reference-extension-evidence/4", {})
    _require(ext.get("status") == "separate_contract_population", "extension evidence must remain separate")
    _require(ext.get("required_profile_cases") == EXPECTED_EXTENSION_PROFILE_CASES, "wrong extension profile count")
    _require(ext.get("aggregate_negative_unit_checks") == EXPECTED_EXTENSION_GATE_CHECKS, "wrong extension gate count")

    levels = data.get("assurance_levels", {})
    _require("check-to-commit race" in levels.get("C0", ""), "C0 must disclose check-to-commit race")
    _require("same-host" in levels.get("C1", "") and "not enabled by default" in levels.get("C1", ""), "C1 scope drift")
    _require(levels.get("C2") == "unqualified" and levels.get("C3") == "unqualified", "C2/C3 must remain unqualified")

    seen: set[str] = set()
    for doc in data.get("documents", []):
        doc_id = doc.get("document_id", "")
        _require(doc_id not in seen, f"duplicate current document_id: {doc_id}")
        seen.add(doc_id)
        _require(doc.get("status") == "current", f"{doc_id} must be current")
        expected = doc.get("document_sha256", "")
        _require(bool(SHA64.fullmatch(expected)), f"{doc_id} has invalid sha256")
        path = root / doc["path"]
        _require(path.is_file(), f"missing document: {doc['path']}")
        _require(sha256_file(path) == expected, f"document tampering/drift: {doc['path']}")
        text = path.read_text(encoding="utf-8")
        _require(f"document_id={doc_id}" in text, f"{doc_id} missing inline snapshot identity")
        _require(EXPECTED_HUB_PIN in text and EXPECTED_LOCK_SHA256 in text, f"{doc_id} missing pin/digest")

    for old in data.get("historical_snapshots", []):
        _require(old.get("status") == "historical", "historical snapshot relabeled/supersession drift")
        _require(old.get("document_id") not in seen, "historical/current document_id collision")
        path = root / old["path"]
        _require(path.is_file(), f"missing historical snapshot: {old['path']}")

    limits = "\n".join(data.get("limitations", []))
    _require("No C2/C3" in limits, "C2/C3 limitation missing")
    _require("Effect-ID deduplication is not business-intent deduplication." in limits, "dedupe limitation missing")


def validate_manifest(path: Path, root: Path = ROOT) -> None:
    validate_data(load_manifest(path), root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("--manifest", default="collateral/evidence-snapshot.json")
    args = parser.parse_args()
    validate_manifest(ROOT / args.manifest)
    print("collateral evidence snapshot: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
