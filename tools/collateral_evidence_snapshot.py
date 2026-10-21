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

import importlib.util


def _bounded_input():
    """The sibling bounded loader, found by path so the import works however this file is loaded."""
    spec = importlib.util.spec_from_file_location("_snapshot_bounded_input", Path(__file__).with_name("bounded_input.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BOUNDED = _bounded_input()
bounded_loads, read_bytes = _BOUNDED.loads, _BOUNDED.read_bytes

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "collateral-evidence-snapshot-v1.schema.json"
# A current snapshot can only describe a lock the hub has accepted.
ALLOWED_QUALIFICATION_STATUS = ("accepted",)
EXPECTED_HUB_PIN = "f7d03c719b9be3b9c3fe0fe300df642b0f408d98"
EXPECTED_LOCK_SHA256 = "0de22fb41eb9b5e2df47e655e72f6a07583812d19b5ba321dbeece831483386f"
EXPECTED_DEFAULT_GENERATION = "merged-producers-v1/full-candidate-gate"
EXPECTED_DEFAULT_SCENARIOS = 35
EXPECTED_DEFAULT_RUN = 37694032916
EXPECTED_DEFAULT_ARTIFACT = "5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7"
EXPECTED_C1_RUN = 37682165860
EXPECTED_C1_PASSED = 73
EXPECTED_EXTENSION_PROFILE_CASES = 111
EXPECTED_EXTENSION_GATE_CHECKS = 30
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


EXPECTED_DOCUMENTS = {'cognous-business-collateral': 'collateral/business-collateral.md', 'cognous-one-page-overview': 'collateral/one-page-overview.md', 'cognous-release-status': 'docs/release-status.md'}
EXPECTED_HISTORICAL = {'cognous-release-status-pre-merged-adoption': 'docs/release-status-before-merged-adoption.md'}


class SnapshotError(ValueError):
    pass


def contained_file(root, value):
    from pathlib import PurePosixPath
    if type(value) is not str or not value or "\\" in value:
        raise SnapshotError("unsafe document path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(c in ("", ".", "..") for c in value.split("/")):
        raise SnapshotError("unsafe document path")
    path = root
    for part in p.parts:
        path = path / part
        if path.is_symlink():
            raise SnapshotError("symlink document path")
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise SnapshotError("document outside repository or missing")
    if path.stat().st_size > 4 * 1024 * 1024:
        raise SnapshotError("document exceeds byte budget")
    return path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    """Read through the bounded loader: byte and depth budgets, duplicate members refused."""
    try:
        return bounded_loads(read_bytes(path))
    except (ValueError, UnicodeDecodeError) as exc:
        raise SnapshotError(f"manifest is not bounded strict JSON: {exc}") from exc


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SnapshotError(message)


def _check_schema(value: Any, schema: dict[str, Any], where: str) -> None:
    """The few schema keywords the snapshot schema uses: type, const, pattern, required,
    properties, additionalProperties false, items and minItems. Other keywords are not applied."""
    kind = schema.get("type")
    if kind == "object":
        _require(type(value) is dict, f"{where} must be an object")
        for name in schema.get("required", []):
            _require(name in value, f"{where}.{name} is required")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for name in value:
                _require(name in props, f"{where}.{name} is not a declared member")
        for name, sub in props.items():
            if name in value:
                _check_schema(value[name], sub, f"{where}.{name}")
    elif kind == "array":
        _require(type(value) is list, f"{where} must be an array")
        _require(len(value) >= schema.get("minItems", 0), f"{where} has too few items")
        for i, item in enumerate(value):
            if "items" in schema:
                _check_schema(item, schema["items"], f"{where}[{i}]")
    elif kind == "string":
        _require(type(value) is str, f"{where} must be a string")
        if "pattern" in schema:
            _require(re.search(schema["pattern"], value) is not None, f"{where} does not match its pattern")
    if "const" in schema:
        _require(type(value) is type(schema["const"]) and value == schema["const"], f"{where} must be {schema['const']!r}")


def _exact_int(value: Any, message: str) -> None:
    _require(type(value) is int, message)


def _lock_claims(data: dict[str, Any], root: Path) -> None:
    """Claims the snapshot derives from component-lock.json must equal the lock's own record."""
    lock = bounded_loads(read_bytes(root / "component-lock.json"))
    evidence = lock.get("qualification_evidence", {})
    comp = lock.get("components", {})
    gen, cl = data["evidence_generation"], data["component_lock"]
    _require(cl.get("qualification_status") in ALLOWED_QUALIFICATION_STATUS, "qualification_status not allowed")
    _require(cl["qualification_status"] == lock.get("qualification_status"), "qualification_status differs from the lock")
    _require(cl.get("runtime_profile") == lock.get("runtime_profile"), "runtime_profile differs from the lock")
    _require(cl.get("selected_control_plane") == comp.get("control_plane", {}).get("sha"), "selected Control Plane differs from the lock")
    _require(cl.get("selected_execution_runtime") == comp.get("moltbot_safe", {}).get("accepted_sha"), "selected Execution Runtime differs from the lock")
    for key, lock_key in (
        ("tested_source_sha", "reviewed_source_sha"),
        ("accepted_hub_merge", "accepted_hub_merge"),
        ("workflow_run", "workflow_run"),
        ("acceptance_scenarios", "matrix_scenarios"),
        ("artifact_sha256", "candidate_gate_artifact_sha256"),
    ):
        _require(gen.get(key) == evidence.get(lock_key) and type(gen.get(key)) is type(evidence.get(lock_key)),
                 f"evidence_generation.{key} differs from the lock's qualification_evidence")


def validate_data(data: dict[str, Any], root: Path = ROOT) -> None:
    _require(type(data) is dict, "manifest must be a JSON object")
    try:
        schema = bounded_loads(read_bytes(SCHEMA_PATH))
    except (OSError, ValueError) as exc:
        raise SnapshotError(f"snapshot schema unreadable: {exc}") from exc
    _check_schema(data, schema, "$")
    _require(data.get("schema_version") == "collateral-evidence-snapshot/1", "wrong schema version")
    _require(data.get("document_id") == "cognous-collateral-evidence-snapshot", "wrong manifest document_id")
    _require(data.get("snapshot_status") == "current", "snapshot must be current")

    try:
        generated = datetime.fromisoformat(data["generated_at"])
    except ValueError as exc:
        raise SnapshotError("generated_at is not an ISO timestamp") from exc
    _require(generated.tzinfo is not None and generated.utcoffset() is not None, "generated_at must be timezone-aware")

    pin = data.get("accepted_hub_pin", "")
    _require(bool(SHA40.fullmatch(pin)), "accepted hub pin must be a 40-char sha")
    _require(pin == EXPECTED_HUB_PIN, "accepted hub pin drift")

    lock = data.get("component_lock", {})
    _require(lock.get("path") == "component-lock.json", "wrong component-lock path")
    _require(lock.get("sha256") == EXPECTED_LOCK_SHA256, "manifest component-lock digest drift")
    _require(sha256_file(root / "component-lock.json") == EXPECTED_LOCK_SHA256, "repository component-lock digest drift")
    _require(lock.get("runtime_profile") == "security-runtime-p2-20261018", "wrong selected runtime profile")
    _require(lock.get("selected_control_plane") == "2bac7875391cad0a431fa0d75208b7ade39743e3", "selected Control Plane pin drift")
    _require(lock.get("selected_execution_runtime") == "6b16962db140590b808f02b5c2cb11a217aec46f", "selected Execution Runtime pin drift")

    for member in ("tested_source_sha", "accepted_hub_merge"):
        _require(bool(SHA40.fullmatch(str(data["evidence_generation"].get(member)))), f"{member} must be a 40-char sha")
    _require(bool(SHA64.fullmatch(str(data["evidence_generation"].get("artifact_sha256")))), "artifact_sha256 must be a sha256")

    generation = data.get("evidence_generation", {})
    _exact_int(generation.get("workflow_run"), "workflow_run must be an integer")
    _exact_int(generation.get("acceptance_scenarios"), "acceptance_scenarios must be an integer")
    _require(generation.get("id") == EXPECTED_DEFAULT_GENERATION, "wrong default evidence generation")
    _require(generation.get("status") == "accepted_default_release", "wrong default evidence status")
    _require(generation.get("workflow_run") == EXPECTED_DEFAULT_RUN, "wrong default workflow run")
    _require(generation.get("acceptance_scenarios") == EXPECTED_DEFAULT_SCENARIOS, "wrong default scenario count")
    _require(generation.get("artifact_sha256") == EXPECTED_DEFAULT_ARTIFACT, "wrong default artifact digest")

    profiles = {item.get("id"): item for item in data.get("separate_profile_evidence", [])}
    c1 = profiles.get("c1-same-host-authority-effect", {})
    _require(c1.get("status") == "separate_optional_profile_ci", "C1 evidence must remain separate")
    for member in ("workflow_run", "passed_tests", "failures", "errors", "skips"):
        _exact_int(c1.get(member), f"C1 {member} must be an integer")
    _require(c1.get("workflow_run") == EXPECTED_C1_RUN, "wrong C1 workflow run")
    _require(c1.get("passed_tests") == EXPECTED_C1_PASSED, "wrong C1 pass count")
    _require(c1.get("failures") == c1.get("errors") == c1.get("skips") == 0, "C1 result totals drift")

    ext = profiles.get("v1-reference-extension-evidence/5", {})
    _require(ext.get("status") == "separate_contract_population", "extension evidence must remain separate")
    for member in ("required_profile_cases", "aggregate_negative_unit_checks"):
        _exact_int(ext.get(member), f"extension {member} must be an integer")
    _require(ext.get("required_profile_cases") == EXPECTED_EXTENSION_PROFILE_CASES, "wrong extension profile count")
    _require(ext.get("aggregate_negative_unit_checks") == EXPECTED_EXTENSION_GATE_CHECKS, "wrong extension gate count")

    levels = data.get("assurance_levels", {})
    _require("check-to-commit race" in levels.get("C0", ""), "C0 must disclose check-to-commit race")
    _require("same-host" in levels.get("C1", "") and "not enabled by default" in levels.get("C1", ""), "C1 scope drift")
    _require(levels.get("C2") == "unqualified" and levels.get("C3") == "unqualified", "C2/C3 must remain unqualified")

    for key, expected in (("documents", EXPECTED_DOCUMENTS), ("historical_snapshots", EXPECTED_HISTORICAL)):
        rows = data.get(key)
        _require(type(rows) is list and len(rows) == len(expected), "exact document inventory required")
        _require({row.get("document_id"): row.get("path") for row in rows} == expected,
                 "document identities or canonical paths changed")
    seen: set[str] = set()
    for doc in data.get("documents", []):
        doc_id = doc.get("document_id", "")
        _require(doc_id not in seen, f"duplicate current document_id: {doc_id}")
        seen.add(doc_id)
        _require(doc.get("status") == "current", f"{doc_id} must be current")
        expected = doc.get("document_sha256", "")
        _require(bool(SHA64.fullmatch(expected)), f"{doc_id} has invalid sha256")
        path = contained_file(root, doc["path"])
        _require(path.is_file(), f"missing document: {doc['path']}")
        _require(sha256_file(path) == expected, f"document tampering/drift: {doc['path']}")
        text = path.read_text(encoding="utf-8")
        _require(f"document_id={doc_id}" in text, f"{doc_id} missing inline snapshot identity")
        _require(EXPECTED_HUB_PIN in text and EXPECTED_LOCK_SHA256 in text, f"{doc_id} missing pin/digest")

    for old in data.get("historical_snapshots", []):
        _require(old.get("status") == "historical", "historical snapshot relabeled/supersession drift")
        _require(old.get("document_id") not in seen, "historical/current document_id collision")
        path = contained_file(root, old["path"])
        _require(path.is_file(), f"missing historical snapshot: {old['path']}")

    limits = "\n".join(data.get("limitations", []))
    _require("No C2/C3" in limits, "C2/C3 limitation missing")
    _require("Effect-ID deduplication is not business-intent deduplication." in limits, "dedupe limitation missing")
    _lock_claims(data, root)


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
