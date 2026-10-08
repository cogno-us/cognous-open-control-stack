#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


    # Execute data-driven refusal cases, not merely their presence in the bundle.
    # These are fixture-level checks; they are not runtime integration proofs.
    def fixture_admissible(candidate):
        p = candidate["proposal"]
        g = candidate["grant"]
        a = candidate["approval"]
        pol = candidate["policy"]
        tenant = p.get("tenant_id")
        return (
            isinstance(tenant, str) and bool(tenant.strip())
            and tenant == g.get("tenant_id") == a.get("tenant_id") == pol.get("tenant_id")
            and a.get("proposal_commitment") == digest(p)
            and g.get("revoked") is False
            and a.get("approved") is True
            and pol.get("effect") == "allow"
            and pol.get("action_id") == p.get("action_id")
            and g.get("principal") == p.get("principal")
            and g.get("scope") in p.get("requested_permissions", [])
            and parse_ts(g["valid_from"]) <= at < parse_ts(g["expires_at"])
            and parse_ts(a["approved_at"]) <= at < parse_ts(a["expires_at"])
            and parse_ts(pol["valid_from"]) <= at < parse_ts(pol["expires_at"])
            and parse_ts(p["not_before"]) <= at < parse_ts(p["expires_at"])
        )

    assert_true(fixture_admissible(positive), "positive fixture is not admissible")
    exercised = []
    for case in fixture["negative_controls"]:
        if "mutation" not in case:
            continue
        mutated = copy.deepcopy(positive)
        for dotted_path, value in case["mutation"].items():
            keys = dotted_path.split(".")
            node = mutated
            for key in keys[:-1]:
                node = node[key]
            node[keys[-1]] = value
        assert_true(not fixture_admissible(mutated), "negative mutation admitted: " + case["id"])
        exercised.append(case["id"])
    assert_true(len(exercised) >= 7, "not enough executable negative mutations")

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
        "fixture_digest": digest(fixture),
        "manifest_digest": fixture["manifest_source"]["canonical_digest"],
        "proposal_commitment": positive["proposal_commitment"],
        "tenant_substitution_commitment": expected_sub["expected_commitment"],
        "negative_controls": len(fixture["negative_controls"]),
        "exercised_mutations": exercised,
        "nonexecuted_contract_assertions": [c["id"] for c in fixture["negative_controls"] if "mutation" not in c],
        "historical_controls": len(fixture["historical_controls"]),
        "result": "PASS"
    }, sort_keys=True))

if __name__ == "__main__":
    main()
