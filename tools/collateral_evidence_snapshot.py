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
import unicodedata
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
EXPECTED_LOCK_SHA256 = "dcd3ab9e4e737c7e50f4bc38c2439438f156da64c9eb1e46725f477973da59ff"
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
# Boundary wording. Text is folded first (fold_text), then a claim term is accepted only when a
# negation scopes it: earlier in the same comma/"or" piece with no finite verb in between, in an
# earlier piece of the same noun list, or as a trailing "... remain unqualified/outside". A hard
# boundary (sentence punctuation, but, however, yet, and, ...) ends every scope. Conservative on
# purpose: it can refuse a benign rewording, never accept an unnegated claim.
# LEGACY_TERMS are scanned in the manifest strings; ASSERTION_TERMS (affirmative claims) are scanned
# in the manifest strings and in the bodies of the hashed documents, whose prose legitimately names
# authorization, settlement and production in descriptive sentences.
LEGACY_TERMS = r"production|certif|\bready\b|readiness|authoriz|authoris|complian|settlement|exactly-once|guarantee"
ASSERTION_TERMS = "|".join((
    r"production[\s-]*(?:ready|grade|quality|safe|hardened)", r"\bprod[\s-]*ready",
    r"ready\s+(?:for|to)\s+(?:prod\b|production|live|deploy|go-live|use\b|customers?)",
    r"(?:approved|cleared|authori[sz]ed|accepted|suitable|fit|safe|ok|okay|licensed)\s+(?:\w+\s+){0,2}?(?:for|to)\s+(?:production|prod\b|live|customers?|deploy|enterprise|use\b)",
    r"\blive\s+(?:customers?|traffic|payments?|use)", r"enterprise[\s-]*(?:grade|ready|class)",
    r"certif", r"complian(?:t|ce)\b", r"\bsecure\b", r"\bsafe\b", r"\baudited\b", r"\baudit[\s-]*ready\b",
    r"\bdeployable\b", r"\battested\b", r"\bvalidated\s+for\b", r"battle[\s-]*tested",
    r"\bguaranteed?\b", r"\bexactly-once\b",
))
CLAIM_TERMS = re.compile(LEGACY_TERMS + "|" + ASSERTION_TERMS)
ASSERTION_RE = re.compile(ASSERTION_TERMS)
HARD_BOUNDARY = re.compile(
    r"[.;:!?\n]|\b(?:but|however|yet|and|although|though|whereas|while|except|instead|rather|still|nevertheless|nonetheless|then)\b")
SOFT_BOUNDARY = re.compile(r"[,()\[\]]|\bor\b| - ")
NEGATION_WORDS = {"no", "not", "never", "without", "neither", "nor", "none", "nothing", "cannot", "unqualified", "nobody",
                  "isn't", "aren't", "wasn't", "weren't", "doesn't", "don't", "didn't", "won't", "can't", "couldn't",
                  "shouldn't", "hasn't", "haven't", "hadn't", "wouldn't", "mustn't"}
QUANTIFIER_NEGATIONS = {"no", "none", "neither", "nothing", "nobody", "nor"}
STOP_VERBS = {"is", "are", "was", "were", "be", "been", "being", "am", "has", "have", "had", "will", "would", "can", "could",
              "may", "might", "should", "must", "shall", "remain", "remains", "remained", "become", "becomes", "became",
              "provides", "provide", "offers", "offer", "delivers", "deliver", "ships", "ship", "gives", "give", "makes",
              "make", "means", "mean", "stays", "stay", "states", "says"}
TRAILING_NEGATION = re.compile(
    r"\b(?:remains?|remained|are|is|must\s+be|stays?|be)\s+(?:not\b|unqualified|outside|unsupported|excluded|unestablished|unclaimed|out\s+of\s+scope|qualified\s+separately)")
TOKEN = re.compile(r"[a-z0-9][a-z0-9'/\-]*")
_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−⁃﹘﹣－"), "-")
_LOOKALIKES = {ord(pair[0]): pair[1] for pair in (
    # Cyrillic
    "аa", "еe", "оo", "рp", "сc", "уy", "хx", "іi", "јj", "ѕs",
    "ԁd", "һh", "ԛq", "ԝw", "кk", "мm", "нh", "тt", "вb", "ӏl",
    "їi", "ґr",
    # Greek
    "αa", "εe", "οo", "ρp", "νv", "ιi", "κk", "τt", "υu", "χx",
    "ηn", "μm", "βb", "γy", "ωw", "ςs", "σo",
    # Latin small capitals and dotless/script forms
    "ᴀa", "ʙb", "ᴄc", "ᴅd", "ᴇe", "ꜰf", "ɢg", "ʜh", "ɪi", "ᴊj",
    "ᴋk", "ʟl", "ᴍm", "ɴn", "ᴏo", "ᴘp", "ʀr", "ꜱs", "ᴛt", "ᴜu",
    "ᴠv", "ᴡw", "ʏy", "ᴢz", "ıi", "ɡg", "ɑa", "ɩi",
)}


def fold_text(text: str) -> str:
    """Casefolded Latin-lookalike form for matching: NFKC, format characters (zero-width, soft
    hyphen, bidi), variation selectors and combining marks dropped, Cyrillic/Greek/small-cap
    lookalikes mapped to Latin, dash and apostrophe variants unified, blanks collapsed."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch) not in ("Cf", "Mn", "Me", "Cc"))
    text = text.casefold().translate(_LOOKALIKES).translate(_DASHES)
    text = unicodedata.normalize("NFKC", text).replace("’", "'").replace("ʼ", "'").replace("‘", "'")
    return re.sub(r"[ \t\r\f\v]+", " ", text)


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


def _tokens(piece: str):
    return [(m.group(0), m.start(), m.end()) for m in TOKEN.finditer(piece)]


def _negation_spans(piece: str):
    """Negation tokens of a piece, without 'not only/just' and the 'no' of 'no-op' (one token)."""
    spans = []
    toks = _tokens(piece)
    for i, (word, start, end) in enumerate(toks):
        if word not in NEGATION_WORDS:
            continue
        nxt = toks[i + 1][0] if i + 1 < len(toks) else ""
        if word in ("not", "nor") and nxt in ("only", "just", "merely", "simply", "solely", "even"):
            continue
        spans.append((word, start, end))
    return spans


def _verbs_between(piece: str, lo: int, hi: int) -> int:
    return sum(1 for word, start, _ in _tokens(piece) if lo <= start < hi and word in STOP_VERBS)


def _scoped(pieces: list[str], index: int, start: int) -> bool:
    """Does a negation scope the term that starts at piece[index][start:]?"""
    piece = pieces[index]
    # A prefix negates the word itself (non-authorizing).
    if re.search(r"(?:\bnon-?|\bun-?|\bnot-)$", piece[:start]):
        return True
    for word, _, n_end in _negation_spans(piece):
        if n_end > start:
            continue
        verbs = _verbs_between(piece, n_end, start)
        gap = len(_tokens(piece[n_end:start]))
        if verbs == 0 or (word in QUANTIFIER_NEGATIONS and verbs <= 1 and gap <= 8):
            return True
    if _verbs_between(piece, 0, start):
        return False
    # Noun list: an earlier piece negates and only verbless pieces lie between.
    for back in range(index - 1, -1, -1):
        earlier = pieces[back]
        spans = _negation_spans(earlier)
        if spans and _verbs_between(earlier, spans[-1][2], len(earlier)) == 0:
            return True
        if _verbs_between(earlier, 0, len(earlier)):
            return False
    return False


def _trailing_negation(pieces: list[str], index: int, start: int, end: int) -> bool:
    """'<term list> remain unqualified/outside ...' later in the segment with only nouns between."""
    if _verbs_between(pieces[index], 0, start):
        return False
    rest = pieces[index][end:]
    for later in range(index + 1, len(pieces) + 1):
        match = TRAILING_NEGATION.search(rest)
        if match:
            return _verbs_between(rest, 0, match.start()) == 0
        if _verbs_between(rest, 0, len(rest)) or later >= len(pieces):
            return False
        rest = rest + " , " + pieces[later]
    return False


def boundary_wording_findings(text: str, terms: re.Pattern = CLAIM_TERMS) -> list[str]:
    """Clauses that use a production/certification/readiness/authorization/settlement/guarantee term
    that no negation scopes. Matching runs on fold_text(text); a hard boundary ends a negated scope."""
    found = []
    for segment in HARD_BOUNDARY.split(fold_text(text)):
        pieces = SOFT_BOUNDARY.split(segment)
        for index, piece in enumerate(pieces):
            hit = next((m for m in terms.finditer(piece)
                        if not (_scoped(pieces, index, m.start()) or _trailing_negation(pieces, index, m.start(), m.end()))), None)
            if hit:
                found.append(segment.strip())
                break
    return found


def body_wording_findings(text: str) -> list[str]:
    """Affirmative-claim terms only, for the bodies of the hashed documents."""
    return boundary_wording_findings(text, ASSERTION_RE)


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


IDENTITY_LINE = re.compile(r"^> \*\*Evidence snapshot:\*\*(?P<fields>.*)$", re.M)
IDENTITY_FIELD = re.compile(r"`(?P<name>[a-z_]+)=(?P<value>[^`\n]*)`")


def _check_document_identity(doc_id: str, version: Any, text: str) -> None:
    """Exactly one inline identity line; its document_id and version fields equal the manifest row
    exactly (no substring match: version=2.0.10 is not version=2.0.1) and it carries the pin and the
    lock digest as whole tokens."""
    lines = IDENTITY_LINE.findall(text)
    _require(len(lines) == 1, f"{doc_id} must carry exactly one inline snapshot identity line")
    fields: dict[str, list[str]] = {}
    for match in IDENTITY_FIELD.finditer(lines[0]):
        fields.setdefault(match.group("name"), []).append(match.group("value"))
    _require(fields.get("document_id") == [doc_id], f"{doc_id} missing inline snapshot identity")
    _require(type(version) is str and fields.get("version") == [version], f"{doc_id} version differs from its inline identity")
    for token in (EXPECTED_HUB_PIN, EXPECTED_LOCK_SHA256):
        _require(re.search(r"(?<![0-9A-Za-z])" + token + r"(?![0-9A-Za-z])", lines[0]) is not None, f"{doc_id} missing pin/digest")


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
    _require(lock.get("selected_control_plane") == "0a41faa972699f7ec3063967a14cd9bdd3e67d27", "selected Control Plane pin drift")
    _require(lock.get("selected_execution_runtime") == "ec728da6dc301a664b331ac8986afd6e850a1273", "selected Execution Runtime pin drift")

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
        _check_document_identity(doc_id, doc.get("version"), text)
        findings = body_wording_findings(text)
        _require(not findings, f"{doc_id} body has an unnegated boundary claim: {[f[:120] for f in findings[:1]]}")

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
