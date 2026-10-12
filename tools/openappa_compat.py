"""Bounded optional OpenAPPA compatibility helpers for Cognous V1.

This module is deliberately hub-owned qualification code. It does not add
OpenAPPA to the core component lock, and an OpenAPPA decision never issues
Cognous authority.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

OPENAPPA_REPOSITORY = "archestra-ai/OpenAPPA"
OPENAPPA_VERSION = "0.31.1"
OPENAPPA_SHA = "4debcfb695f4f74d0d9a92ebdad15ebcc578c991"
PROFILE = "cognous-openappa-optional/0.1"
WIRE_RELATIVE = Path("integrations/kagent/appa-kagent-adk/src/appa_kagent_adk/wire.py")
ALLOWED_CALL_DECISION = "allow_call"
ADMITTED_RESULT_DECISIONS = frozenset({"ack", "deliver_value", "replace_output"})
WITHHELD_RESULT_DECISIONS = frozenset({"block"})
ADMITTED_CONTEXT_DECISIONS = frozenset({"ack", "context"})
WITHHELD_CONTEXT_DECISIONS = frozenset({"refuse", "block"})


class OpenAppaCompatibilityError(RuntimeError):
    """The optional profile cannot make a bounded supported decision."""


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def prepare_openappa(work_dir: Path) -> Path:
    """Clone and pin the exact optional OpenAPPA source revision."""
    dest = work_dir / "openappa"
    if not dest.exists():
        subprocess.run(
            ["git", "clone", "--quiet", "--no-checkout",
             "https://github.com/archestra-ai/OpenAPPA.git", str(dest)],
            check=True, timeout=180,
        )
        subprocess.run(["git", "checkout", "--quiet", "--detach", OPENAPPA_SHA],
                       cwd=dest, check=True, timeout=90)
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dest, text=True).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=dest, text=True
    )
    if actual != OPENAPPA_SHA or dirty:
        raise OpenAppaCompatibilityError(
            f"OpenAPPA checkout must be clean at {OPENAPPA_SHA}; got {actual}"
        )
    if not (dest / WIRE_RELATIVE).is_file():
        raise OpenAppaCompatibilityError("pinned OpenAPPA wire parser is absent")
    return dest


def load_wire(openappa_root: Path):
    path = openappa_root / WIRE_RELATIVE
    spec = importlib.util.spec_from_file_location("cognous_openappa_pinned_wire", path)
    if spec is None or spec.loader is None:
        raise OpenAppaCompatibilityError("cannot load pinned OpenAPPA wire parser")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if getattr(module, "PROTOCOL", None) != 1:
        raise OpenAppaCompatibilityError("unsupported OpenAPPA wire protocol")
    return module


def parse_decision(wire, body: str) -> dict[str, Any]:
    try:
        decision = wire.parse_decision(body)
    except Exception as exc:
        raise OpenAppaCompatibilityError(f"openappa_decision_unusable:{exc}") from exc
    return {
        "kind": decision.kind,
        "feedback": decision.feedback,
        "reason": decision.reason,
        "output": decision.output,
        "value": decision.value,
    }


def build_operation_identity(proposal, envelope, tenant_id: str) -> dict[str, Any]:
    """Map one exact Cognous operation to the optional OpenAPPA tool identity."""
    operation = envelope.operation
    payload = proposal.payload
    identity = {
        "profile": PROFILE,
        "tenant_id": tenant_id,
        "manifest_id": proposal.manifest_id,
        "manifest_version": proposal.manifest_version,
        "manifest_digest": proposal.manifest_digest,
        "action_id": proposal.action_id,
        "adapter_id": proposal.adapter_id,
        "target": proposal.target,
        "payload_commitment": canonical_digest(payload),
        "proposal_commitment": operation.proposal_commitment,
        "effect_id": envelope.effect_id,
        "openappa_tool": "mcp:cognous/refund.issue.routine",
        "openappa_root_id": f"{tenant_id}:{proposal.run_id}",
        "destination": "authoritative-local-sqlite",
    }
    required = (
        "tenant_id", "manifest_id", "manifest_version", "manifest_digest",
        "action_id", "adapter_id", "target", "payload_commitment",
        "proposal_commitment", "effect_id", "openappa_tool",
        "openappa_root_id", "destination",
    )
    if any(identity.get(name) in (None, "") for name in required):
        raise OpenAppaCompatibilityError("incomplete_operation_identity")
    return identity


def dispatch_join(*, identity: dict[str, Any], appa_decision: dict[str, Any],
                  cognous_authorized: bool) -> dict[str, Any]:
    """Strict AND gate. OpenAPPA permission is flow-only and non-authorizing."""
    required = {
        "tenant_id", "action_id", "adapter_id", "target", "payload_commitment",
        "proposal_commitment", "effect_id", "openappa_tool", "destination",
    }
    if not required.issubset(identity) or any(identity.get(k) in (None, "") for k in required):
        return {"dispatch": False, "reason": "incomplete_evidence"}
    flow_allowed = appa_decision.get("kind") == ALLOWED_CALL_DECISION
    return {
        "dispatch": bool(flow_allowed and cognous_authorized),
        "flow_allowed": flow_allowed,
        "cognous_authorized": bool(cognous_authorized),
        "reason": "conjunction_satisfied" if flow_allowed and cognous_authorized
                  else ("openappa_denied_or_unusable" if not flow_allowed else "cognous_denied"),
        "authority_effect_of_openappa": "none",
    }


def result_admission(*, wire, body: str, identity: dict[str, Any],
                     result_value: Any, effect_applied: bool) -> dict[str, Any]:
    """Separate post-effect result gate; withholding cannot erase an effect."""
    decision = parse_decision(wire, body)
    result_commitment = canonical_digest(result_value)
    kind = decision["kind"]
    if kind in ADMITTED_RESULT_DECISIONS:
        admitted = True
        state = "admitted"
    elif kind in WITHHELD_RESULT_DECISIONS:
        admitted = False
        state = "withheld"
    else:
        admitted = False
        state = "unsupported_decision_fail_closed"
    return {
        "attempt_effect_id": identity["effect_id"],
        "result_commitment": result_commitment,
        "decision": decision,
        "result_admitted": admitted,
        "result_state": state,
        "effect_state": "applied" if effect_applied else "not_applied",
        "authority_effect_of_openappa": "none",
    }


def context_admission(*, wire, body: str, context_value: Any,
                      trajectory_id: str) -> dict[str, Any]:
    """Separate incoming-context gate. Unusable/unsupported input fails closed."""
    if not trajectory_id:
        raise OpenAppaCompatibilityError("missing_trajectory_identity")
    decision = parse_decision(wire, body)
    kind = decision["kind"]
    commitment = canonical_digest(context_value)
    if kind in ADMITTED_CONTEXT_DECISIONS:
        admitted = True
        state = "admitted"
    elif kind in WITHHELD_CONTEXT_DECISIONS:
        admitted = False
        state = "withheld"
    else:
        admitted = False
        state = "unsupported_decision_fail_closed"
    return {
        "trajectory_id": trajectory_id,
        "context_commitment": commitment,
        "decision": decision,
        "context_admitted": admitted,
        "context_state": state,
        "authority_effect_of_openappa": "none",
    }
