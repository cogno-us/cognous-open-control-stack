#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "fixtures" / "w0" / "c1-c8-refund-v1.json"
MANIFEST_PATH = ROOT / "fixtures" / "w0" / "sources" / "refund_integration_v1_1.manifest.json"

def canonical_bytes(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

def digest(value):
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()

def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    positive = fixture["positive_control"]
    proposal = positive["proposal"]
    at = parse_ts(fixture["evaluation_at"])

    assert_true(digest(manifest) == fixture["manifest_source"]["canonical_digest"], "manifest canonical digest mismatch")
    assert_true(proposal["manifest_digest"] == fixture["manifest_source"]["canonical_digest"], "proposal manifest digest mismatch")
    assert_true(digest(proposal["payload"]) == proposal["payload_commitment"], "payload commitment mismatch")
    assert_true(digest(proposal) == positive["proposal_commitment"], "proposal commitment mismatch")

    tenant_sub = copy.deepcopy(proposal)
    tenant_sub["tenant_id"] = "tenant-beta"
    expected_sub = next(c for c in fixture["negative_controls"] if c["id"] == "C1-tenant-substitution")
    assert_true(digest(tenant_sub) == expected_sub["expected_commitment"], "tenant substitution digest mismatch")
    assert_true(digest(tenant_sub) != positive["proposal_commitment"], "tenant substitution did not change identity")

    grant = positive["grant"]
    approval = positive["approval"]
    policy = positive["policy"]

    assert_true(proposal["tenant_id"] == grant["tenant_id"] == approval["tenant_id"] == policy["tenant_id"], "tenant join mismatch")
    assert_true(approval["proposal_commitment"] == positive["proposal_commitment"], "approval not bound to proposal")
    assert_true(parse_ts(grant["valid_from"]) <= at < parse_ts(grant["expires_at"]), "grant not fresh at evaluation time")
    assert_true(grant["revoked"] is False, "grant revoked")
    assert_true(approval["approved"] is True, "approval missing")
    assert_true(parse_ts(approval["approved_at"]) <= at < parse_ts(approval["expires_at"]), "approval not fresh at evaluation time")
    assert_true(parse_ts(policy["valid_from"]) <= at < parse_ts(policy["expires_at"]), "policy not fresh at evaluation time")
    assert_true(policy["effect"] == "allow", "policy does not allow")
    assert_true(parse_ts(proposal["not_before"]) <= at < parse_ts(proposal["expires_at"]), "proposal not current at evaluation time")

    ids = {c["id"] for c in fixture["negative_controls"]}
    required = {
        "C1-missing-tenant", "C1-tenant-substitution", "C2-wrong-tenant-grant",
        "C2-expired-grant", "C2-revoked-grant", "C2-expired-approval",
        "C2-policy-deny", "C4-evaluation-error", "C5-lost-ack-fresh-absence",
        "C6-flow-allow-cognous-deny", "C6-result-withheld-after-effect",
        "C7-stop-ack-with-inflight"
    }
    assert_true(required <= ids, "required negative controls missing")
    assert_true(any(c["id"] == "C8-historical-artifact" for c in fixture["historical_controls"]), "historical C8 control missing")

    print(json.dumps({
        "fixture_bundle": fixture["fixture_bundle"],
        "manifest_digest": fixture["manifest_source"]["canonical_digest"],
        "proposal_commitment": positive["proposal_commitment"],
        "tenant_substitution_commitment": expected_sub["expected_commitment"],
        "negative_controls": len(fixture["negative_controls"]),
        "historical_controls": len(fixture["historical_controls"]),
        "result": "PASS"
    }, sort_keys=True))

if __name__ == "__main__":
    main()
