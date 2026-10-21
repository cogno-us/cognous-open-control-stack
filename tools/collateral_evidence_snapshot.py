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
from datetime import datetime, timedelta, timezone
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
EXPECTED_DOCUMENT_SCOPES = {
    'cognous-business-collateral': 'business-facing bounded synthetic release collateral',
    'cognous-one-page-overview': 'one-page bounded synthetic release summary',
    'cognous-release-status': 'bounded synthetic release status',
}
EXPECTED_SNAPSHOT_VERSION = "1.0.3"
EXPECTED_C1_REVIEWED_SHAS = {
    "control_plane_reviewed_source_sha": "73e3c65acc47dc43593dcb0420d14032ed410b14",
    "execution_runtime_reviewed_source_sha": "b1525a7982e52ebb530457f94d5517de032ca4c4",
}
GENERATED_AT_FLOOR = datetime(2026, 10, 1, tzinfo=timezone.utc)
C1_MEMBERS = {"id", "status", "workflow_run", "passed_tests", "failures", "errors", "skips", "scope", *EXPECTED_C1_REVIEWED_SHAS}
EXT_MEMBERS = {"id", "status", "required_profile_cases", "aggregate_negative_unit_checks", "scope"}
# Boundary wording: a claim term may appear only inside a negated clause. Conservative on purpose
# (a sentence or semicolon clause must carry a negation before the term); it can refuse a benign
# rewording, never accept an unnegated claim.
CLAIM_TERMS = re.compile(r"production|certif|\bready\b|readiness|authoriz|complian|settlement|exactly-once|guarantee", re.I)
NEGATION = re.compile(r"\b(?:no|not|never|without|neither|nor|unqualified|cannot|none)\b", re.I)
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
    properties, additionalProperties false and items. Other keywords are not applied: minItems is
    left to the exact inventory checks below, which are stricter (exact documents, profiles and
    limitations) and keep their specific messages."""
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
        for i, item in enumerate(value):
            if "items" in schema:
                _check_schema(item, schema["items"], f"{where}[{i}]")
    elif kind == "integer":
        _require(type(value) is int, f"{where} must be an integer")
    elif kind == "string":
        _require(type(value) is str, f"{where} must be a string")
        if "pattern" in schema:
            _require(re.search(schema["pattern"], value) is not None, f"{where} does not match its pattern")
    if "enum" in schema:
        _require(any(type(value) is type(e) and value == e for e in schema["enum"]), f"{where} is not an allowed value")
    if "const" in schema:
        _require(type(value) is type(schema["const"]) and value == schema["const"], f"{where} must be {schema['const']!r}")


def _strings(value: Any):
    if type(value) is str:
        yield value
    elif type(value) is dict:
        for item in value.values():
            yield from _strings(item)
    elif type(value) is list:
        for item in value:
            yield from _strings(item)


def boundary_wording_findings(text: str) -> list[str]:
    """Clauses that use a production/certification/readiness/authorization/settlement/guarantee term
    without an earlier negation in the same sentence or semicolon clause."""
    found = []
    for clause in re.split(r"[.;\n]", text):
        for match in CLAIM_TERMS.finditer(clause):
            if not NEGATION.search(clause[: match.start()]):
                found.append(clause.strip())
                break
    return found


def _check_boundary_wording(data: dict[str, Any]) -> None:
    for text in _strings(data):
        findings = boundary_wording_findings(text)
        _require(not findings, f"unnegated boundary claim: {findings[:1]}")


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
    _require(GENERATED_AT_FLOOR <= generated <= datetime.now(timezone.utc) + timedelta(days=1),
             "generated_at outside the plausible snapshot window")
    _require(data.get("version") == EXPECTED_SNAPSHOT_VERSION, "snapshot version drift")

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
    rows = data.get("separate_profile_evidence", [])
    _require(len(rows) == len(profiles) == 2, "exact separate profile inventory required")
    c1 = profiles.get("c1-same-host-authority-effect", {})
    _require(set(c1) == C1_MEMBERS, "C1 evidence members changed")
    for member, expected_sha in EXPECTED_C1_REVIEWED_SHAS.items():
        _require(c1.get(member) == expected_sha, f"C1 {member} drift")
    _require(c1.get("status") == "separate_optional_profile_ci", "C1 evidence must remain separate")
    for member in ("workflow_run", "passed_tests", "failures", "errors", "skips"):
        _exact_int(c1.get(member), f"C1 {member} must be an integer")
    _require(c1.get("workflow_run") == EXPECTED_C1_RUN, "wrong C1 workflow run")
    _require(c1.get("passed_tests") == EXPECTED_C1_PASSED, "wrong C1 pass count")
    _require(c1.get("failures") == c1.get("errors") == c1.get("skips") == 0, "C1 result totals drift")

    ext = profiles.get("v1-reference-extension-evidence/5", {})
    _require(set(ext) == EXT_MEMBERS, "extension evidence members changed")
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
        _require(doc.get("evidence_scope") == EXPECTED_DOCUMENT_SCOPES.get(doc_id), f"{doc_id} evidence_scope drift")
        expected = doc.get("document_sha256", "")
        _require(bool(SHA64.fullmatch(expected)), f"{doc_id} has invalid sha256")
        path = contained_file(root, doc["path"])
        _require(path.is_file(), f"missing document: {doc['path']}")
        _require(sha256_file(path) == expected, f"document tampering/drift: {doc['path']}")
        text = path.read_text(encoding="utf-8")
        _require(f"document_id={doc_id}" in text, f"{doc_id} missing inline snapshot identity")
        _require(f"version={doc.get('version')}" in text, f"{doc_id} version differs from its inline identity")
        _require(EXPECTED_HUB_PIN in text and EXPECTED_LOCK_SHA256 in text, f"{doc_id} missing pin/digest")

    for old in data.get("historical_snapshots", []):
        _require(old.get("status") == "historical", "historical snapshot relabeled/supersession drift")
        _require(old.get("document_id") not in seen, "historical/current document_id collision")
        path = contained_file(root, old["path"])
        _require(path.is_file(), f"missing historical snapshot: {old['path']}")

    limits = "\n".join(data.get("limitations", []))
    _require("No C2/C3" in limits, "C2/C3 limitation missing")
    _require("Effect-ID deduplication is not business-intent deduplication." in limits, "dedupe limitation missing")
    _check_boundary_wording(data)
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
