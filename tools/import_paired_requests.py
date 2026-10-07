#!/usr/bin/env python3
"""Import recorded model-selected requests for later paired qualification.

This importer performs no model calls and grants no authority. It preserves raw
requests, normalized requests, provenance, and injection-exposure metadata.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

REQUIRED = {"request_id", "raw_request", "normalized_request", "provenance", "injection_exposure"}
NORMALIZED_REQUIRED = {
    "action_id", "target", "payload", "actor", "principal",
    "institution_id", "authority_domain", "operation_identity",
}

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="JSONL recorded requests")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    rows = []
    for n, line in enumerate(Path(args.input).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = sorted(REQUIRED - set(row))
        if missing:
            raise SystemExit(f"line {n}: missing {missing}")
        norm = row["normalized_request"]
        if not isinstance(norm, dict):
            raise SystemExit(f"line {n}: normalized_request must be an object")
        missing_norm = sorted(NORMALIZED_REQUIRED - set(norm))
        if missing_norm:
            raise SystemExit(f"line {n}: normalized_request missing {missing_norm}")
        row["request_source"] = "model-selected"
        row["normalized_sha256"] = hashlib.sha256(canonical(norm).encode("utf-8")).hexdigest()
        rows.append(row)
    out = {
        "schema_version": "1.0.0",
        "count": len(rows),
        "records": rows,
        "note": (
            "Imported observations are not proof of prompt-injection success; "
            "exposure is reported only from supplied provenance."
        ),
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
