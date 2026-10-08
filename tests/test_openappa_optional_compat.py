"""W4 optional OpenAPPA compatibility qualification."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest

from tools.openappa_compat import (
    OPENAPPA_SHA,
    OPENAPPA_VERSION,
    PROFILE,
    OpenAppaCompatibilityError,
    build_operation_identity,
    context_admission,
    dispatch_join,
    load_wire,
    parse_decision,
    prepare_openappa,
    result_admission,
)
from tools.optional_execution import BASE, run_case, setup
from tools.optional_execution_profile import prepare

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".w4-openappa-work"


@pytest.fixture(scope="module")
def deps():
    WORK.mkdir(exist_ok=True)
    env, _, _ = prepare(WORK)
    os.environ.update(env)
    sys.path[:0] = env["PYTHONPATH"].split(os.pathsep)
    appa = prepare_openappa(WORK)
    return appa, load_wire(appa)


def _authorized_identity(tmp_path):
    workflow, resolver, proposal, decision, envelope, policy = setup(tmp_path, WORK)
    assert decision.result == "authorized"
    identity = build_operation_identity(proposal, envelope, "tenant-alpha")
    return identity


def test_selected_pin_and_wire_are_real(deps):
    appa, wire = deps
    assert OPENAPPA_VERSION == "0.31.1"
    assert OPENAPPA_SHA == "4debcfb695f4f74d0d9a92ebdad15ebcc578c991"
    assert wire.PROTOCOL == 1
    assert (appa / "LICENSE.md").is_file()


def test_flow_allow_and_cognous_allow_are_conjoined(tmp_path, deps):
    _, wire = deps
    identity = _authorized_identity(tmp_path / "setup")
    appa = parse_decision(wire, '{"protocol":1,"decision":"allow_call"}')
    joined = dispatch_join(identity=identity, appa_decision=appa, cognous_authorized=True)
    assert joined["dispatch"] is True
    assert joined["authority_effect_of_openappa"] == "none"


def test_openappa_denial_blocks_dispatch(tmp_path, deps):
    _, wire = deps
    identity = _authorized_identity(tmp_path / "setup")
    appa = parse_decision(
        wire,
        '{"protocol":1,"decision":"deny_call","feedback":"blocked"}',
    )
    joined = dispatch_join(identity=identity, appa_decision=appa, cognous_authorized=True)
    assert joined["dispatch"] is False
    assert joined["flow_allowed"] is False


def test_cognous_denial_blocks_even_when_openappa_allows(tmp_path, deps):
    _, wire = deps
    identity = _authorized_identity(tmp_path / "setup")
    appa = parse_decision(wire, '{"protocol":1,"decision":"allow_call"}')
    joined = dispatch_join(identity=identity, appa_decision=appa, cognous_authorized=False)
    assert joined["dispatch"] is False
    assert joined["reason"] == "cognous_denied"


def test_incomplete_identity_fails_closed(tmp_path, deps):
    _, wire = deps
    identity = _authorized_identity(tmp_path / "setup")
    del identity["payload_commitment"]
    appa = parse_decision(wire, '{"protocol":1,"decision":"allow_call"}')
    joined = dispatch_join(identity=identity, appa_decision=appa, cognous_authorized=True)
    assert joined == {"dispatch": False, "reason": "incomplete_evidence"}


def test_unsupported_openappa_protocol_is_unusable(deps):
    _, wire = deps
    with pytest.raises(OpenAppaCompatibilityError, match="openappa_decision_unusable"):
        parse_decision(wire, '{"protocol":2,"decision":"allow_call"}')


def test_incoming_context_and_outgoing_result_are_separate(deps):
    _, wire = deps
    incoming = context_admission(
        wire=wire,
        body='{"protocol":1,"decision":"context","text":"bounded context"}',
        context_value={"task": "refund"},
        trajectory_id="tenant-alpha:run-1",
    )
    assert incoming["context_admitted"] is True
    blocked = context_admission(
        wire=wire,
        body='{"protocol":1,"decision":"refuse","detail":"no context"}',
        context_value={"task": "refund"},
        trajectory_id="tenant-alpha:run-1",
    )
    assert blocked["context_admitted"] is False


def test_result_withholding_preserves_applied_effect(tmp_path, deps):
    _, wire = deps
    value = run_case("refund-intent", "allowed", tmp_path / "executed", WORK)
    assert value["qualified"] is True
    assert len(value["effect_ids"]) == 1
    effect_id = value["effect_ids"][0]
    identity = {"effect_id": effect_id}
    admission = result_admission(
        wire=wire,
        body='{"protocol":1,"decision":"block","reason":"withhold"}',
        identity=identity,
        result_value={"refund": "applied"},
        effect_applied=True,
    )
    assert admission["result_admitted"] is False
    assert admission["result_state"] == "withheld"
    assert admission["effect_state"] == "applied"
    assert admission["attempt_effect_id"] == effect_id


def test_openappa_not_added_to_core_component_lock():
    lock = json.loads((ROOT / "component-lock.json").read_text())
    assert "openappa" not in lock["components"]
    assert lock["runtime_profile"] == "merged-producers-v1"
    assert PROFILE == "cognous-openappa-optional/0.1"
