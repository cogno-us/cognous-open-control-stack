"""Closed proposal schema and closed result codes for the MVP ingress (pure; no Control Plane or Runtime imports).

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import json
import math
import re

SCHEMA = "mvp-refund-proposal/1"
RESULT_SCHEMA = "mvp-ingress-result/1"
MAX_REQUEST_BYTES = 4096
MEMBERS = ("schema", "request_id", "customer_id", "amount", "unit", "refund_reason")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_REASON = re.compile(r"^[a-z][a-z _-]{0,63}$")

OUTCOMES = ("executed", "refused", "held", "unknown")
# Closed vocabulary. Every code the ingress can return is listed here; nothing is derived from caller or exception text.
CODES = frozenset({
    "EXECUTED",
    "TOO_LARGE", "MALFORMED_JSON", "NOT_OBJECT", "DUPLICATE_MEMBER", "UNKNOWN_MEMBER", "MISSING_MEMBER",
    "BAD_TYPE", "BAD_VALUE", "BAD_ID", "SCHEMA_MISMATCH", "REQUEST_TIMEOUT",
    "REPLAY", "INGRESS_UNAVAILABLE", "PEER_NOT_ALLOWED",
    "DECISION_HELD", "DECISION_REFUSED", "CLAIM_REFUSED", "EXECUTION_DENIED", "DUPLICATE_OPERATION",
    "OUTCOME_UNKNOWN",
})


class Refusal(Exception):
    """Syntactic refusal with a closed code; carries no caller-controlled text."""

    def __init__(self, code: str):
        assert code in CODES
        super().__init__(code)
        self.code = code


def result(outcome: str, code: str, *, request_id: str | None = None, reasons=()) -> dict:
    assert outcome in OUTCOMES and code in CODES
    safe = [r for r in reasons if isinstance(r, str) and re.fullmatch(r"[a-z0-9_.:-]{1,64}", r)][:8]
    return {"schema": RESULT_SCHEMA, "outcome": outcome, "code": code, "request_id": request_id, "reasons": safe}


def _pairs(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise Refusal("DUPLICATE_MEMBER")
        seen[key] = value
    return seen


def _no_constant(_name):
    raise Refusal("BAD_VALUE")


def parse(raw: bytes) -> dict:
    """Parse and validate one proposal. Raises Refusal (closed code). Never evaluates, imports or resolves anything."""
    if not isinstance(raw, (bytes, bytearray)):
        raise Refusal("BAD_TYPE")
    if len(raw) > MAX_REQUEST_BYTES:
        raise Refusal("TOO_LARGE")
    try:
        text = bytes(raw).decode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_no_constant)
    except Refusal:
        raise
    except (ValueError, RecursionError):
        raise Refusal("MALFORMED_JSON") from None
    if not isinstance(value, dict):
        raise Refusal("NOT_OBJECT")
    if any(k not in MEMBERS for k in value):
        raise Refusal("UNKNOWN_MEMBER")
    if any(k not in value for k in MEMBERS):
        raise Refusal("MISSING_MEMBER")
    if not isinstance(value["schema"], str):
        raise Refusal("BAD_TYPE")
    if value["schema"] != SCHEMA:
        raise Refusal("SCHEMA_MISMATCH")
    for key in ("request_id", "customer_id"):
        if not isinstance(value[key], str):
            raise Refusal("BAD_TYPE")
        if not _ID.fullmatch(value[key]) or ".." in value[key]:
            raise Refusal("BAD_ID")
    amount = value["amount"]
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise Refusal("BAD_TYPE")
    try:
        if not math.isfinite(amount) or amount <= 0 or amount > 1_000_000:
            raise Refusal("BAD_VALUE")
    except OverflowError:  # an integer too large for a float
        raise Refusal("BAD_VALUE") from None
    if not isinstance(value["unit"], str) or not isinstance(value["refund_reason"], str):
        raise Refusal("BAD_TYPE")
    if value["unit"] != "USD":
        raise Refusal("BAD_VALUE")
    if not _REASON.fullmatch(value["refund_reason"]):
        raise Refusal("BAD_VALUE")
    return value
