"""MVP trusted-host ingress: governed-proposal boundary tests (synthetic effects, Linux, single host).

SPDX-License-Identifier: Apache-2.0

Two layers:
* unit tests (no components needed): closed schema, closed codes, UNKNOWN / no-blind-retry mapping, simulate pinned to None,
  client module surface;
* integration tests (need the pinned components): set MVP_INGRESS_CP_ROOT and MVP_INGRESS_RUNTIME_ROOT to checkouts of the
  Control Plane and Runtime, and put pydantic >= 2.12 first on PYTHONPATH. They start a separate ingress process and talk to
  it only through the declared socket protocol. The unprivileged-client tests need root (they drop to uid 65534) and skip
  otherwise. Nothing here claims protection against code running as the ingress uid or root.
"""
from __future__ import annotations

import ast
import json
import os
import pathlib
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time

import pytest

from tools.mvp_ingress import client as client_mod
from tools.mvp_ingress import proposal as P
from tools.mvp_ingress.core import IngressCore, Ledger, verify_state_permissions

HUB = pathlib.Path(__file__).resolve().parents[1]
CP = os.environ.get("MVP_INGRESS_CP_ROOT")
RT = os.environ.get("MVP_INGRESS_RUNTIME_ROOT")
needs_components = pytest.mark.skipif(not (CP and RT), reason="set MVP_INGRESS_CP_ROOT and MVP_INGRESS_RUNTIME_ROOT")
needs_root = pytest.mark.skipif(os.geteuid() != 0, reason="needs root to drop to an unprivileged uid")

GOOD = {"schema": P.SCHEMA, "request_id": "case-1", "customer_id": "customer-001", "amount": 10, "unit": "USD",
        "refund_reason": "duplicate"}
RESULT_KEYS = {"schema", "outcome", "code", "request_id", "reasons"}


def good(**changes):
    return {**GOOD, **changes}


def jb(value):
    return json.dumps(value).encode()


# ----------------------------------------------------------------------------------------------------------------- unit
class FakeResult:
    def __init__(self, status, attempted=True, acknowledged=False, error=None):
        self.status, self.attempted, self.acknowledged, self.error = status, attempted, acknowledged, error


class FakeDecision:
    def __init__(self, result="authorized", reasons=()):
        self.result, self.reasons = result, list(reasons)


class FakeHost:
    now = object()

    def __init__(self, decision=None, provision=None, execute=None):
        self.calls = {"decide": 0, "provision": 0, "execute": []}
        host = self

        class Workflow:
            def decide(self, proposal, now):
                host.calls["decide"] += 1
                return decision or FakeDecision()

        class Executor:
            def provision_claim(self, *, proposal, decision, now):
                host.calls["provision"] += 1
                if isinstance(provision, Exception):
                    raise provision
                return type("Claim", (), {"claim_id": "claim-x"})()

            def execute(self, **kwargs):
                host.calls["execute"].append(kwargs)
                if isinstance(execute, Exception):
                    raise execute
                return execute

        self.workflow, self.executor = Workflow(), Executor()

    def build_proposal(self, fields):
        return fields

    def envelope(self, decision, proposal):
        return "envelope"


def fake_core(tmp_path, **kw):
    host = FakeHost(**kw)
    return host, IngressCore(host, tmp_path / "ingress.db")


def sub(tmp_path, name):
    (tmp_path / name).mkdir()
    return tmp_path / name


def assert_closed(out):
    assert set(out) == RESULT_KEYS
    assert out["schema"] == P.RESULT_SCHEMA and out["outcome"] in P.OUTCOMES and out["code"] in P.CODES
    assert isinstance(out["reasons"], list) and all(isinstance(r, str) for r in out["reasons"])
    json.dumps(out)  # plain data only: no object handle can be in a result


def test_executed_maps_and_simulate_is_pinned_to_none(tmp_path):
    host, core = fake_core(tmp_path, execute=FakeResult("executed", acknowledged=True))
    out = core.handle(jb(GOOD))
    assert_closed(out)
    assert (out["outcome"], out["code"]) == ("executed", "EXECUTED")
    [kwargs] = host.calls["execute"]
    assert kwargs["simulate"] is None and set(kwargs) == {"envelope", "claim_id", "simulate"}


@pytest.mark.parametrize("res", [FakeResult("unknown"), FakeResult("partial", acknowledged=True), FakeResult("failed"),
                                 FakeResult("observed"), FakeResult("executed", acknowledged=False), None,
                                 RuntimeError("boom after dispatch")])
def test_ambiguous_outcomes_are_unknown_and_never_retried(tmp_path, res):
    host, core = fake_core(tmp_path, execute=res)
    first = core.handle(jb(GOOD))
    assert_closed(first)
    assert (first["outcome"], first["code"]) == ("unknown", "OUTCOME_UNKNOWN")
    again = core.handle(jb(GOOD))
    assert (again["outcome"], again["code"]) == ("refused", "REPLAY")
    assert len(host.calls["execute"]) == 1 and host.calls["provision"] == 1
    other = core.handle(jb(good(amount=11)))  # same request id, other content: still the same reservation
    assert other["code"] == "REPLAY" and len(host.calls["execute"]) == 1


def test_denied_before_dispatch_is_a_refusal_and_duplicate_operation_has_its_own_code(tmp_path):
    host, core = fake_core(tmp_path, execute=FakeResult("denied", attempted=False, error="operation_already_committed"))
    out = core.handle(jb(GOOD))
    assert (out["outcome"], out["code"]) == ("refused", "DUPLICATE_OPERATION")
    host, core = fake_core(sub(tmp_path, "b"), execute=FakeResult("denied", attempted=False, error="PRIVATE DETAIL"))
    out = core.handle(jb(GOOD))
    assert (out["outcome"], out["code"]) == ("refused", "EXECUTION_DENIED")
    assert "PRIVATE" not in json.dumps(out)


def test_decision_hold_and_deny_stop_before_any_claim_and_may_be_resubmitted(tmp_path):
    host, core = fake_core(tmp_path, decision=FakeDecision("hold", ["status_unreadable", "Not A Code!"]))
    out = core.handle(jb(GOOD))
    assert (out["outcome"], out["code"], out["reasons"]) == ("held", "DECISION_HELD", ["status_unreadable"])
    assert host.calls["provision"] == 0 and host.calls["execute"] == []
    assert core.handle(jb(GOOD))["code"] == "DECISION_HELD"  # nothing issued, so the id was released
    host, core = fake_core(sub(tmp_path, "d"), decision=FakeDecision("deny"))
    assert core.handle(jb(GOOD))["code"] == "DECISION_REFUSED"
    assert host.calls["provision"] == 0


def test_claim_provisioning_failure_is_a_refusal_with_no_execute(tmp_path):
    host, core = fake_core(tmp_path, provision=PermissionError("secret path /x"))
    out = core.handle(jb(GOOD))
    assert (out["outcome"], out["code"]) == ("refused", "CLAIM_REFUSED") and "secret" not in json.dumps(out)
    assert host.calls["execute"] == []
    assert core.handle(jb(GOOD))["code"] == "REPLAY"


def test_ledger_reservation_is_durable_and_inflight_is_never_re_executed(tmp_path):
    ledger = Ledger(tmp_path / "l.db")
    assert ledger.reserve("case-1", "d")  # a crash after this point leaves an in-flight reservation
    host = FakeHost(execute=FakeResult("executed", acknowledged=True))
    core = IngressCore(host, tmp_path / "l.db")  # a new process opening the same ledger
    assert core.handle(jb(GOOD))["code"] == "REPLAY" and host.calls["decide"] == 0


def test_core_source_never_forwards_a_caller_value_as_simulate():
    tree = ast.parse((HUB / "tools/mvp_ingress/core.py").read_text())
    uses = [n for n in ast.walk(tree) if isinstance(n, ast.keyword) and n.arg == "simulate"]
    assert len(uses) == 1 and isinstance(uses[0].value, ast.Constant) and uses[0].value.value is None
    banned = ("set_grant_status", "set_approval_status", "set_policy_state", "set_evidence_state",
              "remove_authoritative_state", "execute_claim_atomic")
    for path in (HUB / "tools/mvp_ingress").glob("*.py"):
        assert not [b for b in banned if b in path.read_text()], path.name


def test_declared_client_module_is_standard_library_only():
    tree = ast.parse((HUB / "tools/mvp_ingress/client.py").read_text())
    roots = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    roots |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert roots <= {"__future__", "json", "socket"}


def test_permission_verifier_is_not_vacuous(tmp_path):
    root = tmp_path / "s"
    root.mkdir(mode=0o700)
    f = root / "x.db"
    f.write_text("x")
    os.chmod(root, 0o700)
    os.chmod(f, 0o600)
    assert verify_state_permissions(root) == 2
    os.chmod(f, 0o640)
    with pytest.raises(PermissionError):
        verify_state_permissions(root)
    os.chmod(f, 0o600)
    os.chmod(root, 0o750)
    with pytest.raises(PermissionError):
        verify_state_permissions(root)
    os.chmod(root, 0o700)
    os.symlink("/etc/passwd", root / "link")
    with pytest.raises(PermissionError):
        verify_state_permissions(root)
    os.unlink(root / "link")
    with pytest.raises(PermissionError):
        verify_state_permissions(root, uid=os.geteuid() + 1)


# ------------------------------------------------------------------------------------------------------- integration
class Ingress:
    def __init__(self, base: pathlib.Path, *, socket_mode="600", allow_uid=None):
        self.base = base
        base.mkdir(exist_ok=True)
        os.chmod(base, 0o755)
        self.state = base / "state"
        self.sock = str(base / "ingress.sock")
        cmd = [sys.executable, "-m", "tools.mvp_ingress.server", "--state-dir", str(self.state), "--socket", self.sock,
               "--control-plane", CP, "--runtime", RT, "--socket-mode", socket_mode]
        for uid in allow_uid or []:
            cmd += ["--allow-uid", str(uid)]
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(HUB)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        self.proc = subprocess.Popen(cmd, cwd=str(HUB), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        line = self.proc.stdout.readline()
        if line.strip() != "READY":
            self.proc.kill()
            raise RuntimeError("ingress did not start: " + self.proc.stderr.read()[-2000:])

    def raw(self, data: bytes, *, timeout=20.0) -> dict:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect(self.sock)
            try:
                s.sendall(data + b"\n")
                s.shutdown(socket.SHUT_WR)
            except (BrokenPipeError, ConnectionResetError):
                pass  # server answered (and closed) before reading all of an oversized body
            out = b""
            while True:
                try:
                    part = s.recv(4096)
                except ConnectionResetError:
                    break
                if not part:
                    break
                out += part
        return json.loads(out)

    def submit(self, proposal):
        return client_mod.submit(self.sock, proposal)

    def observe(self):
        """Owner-side read of the destination and the ingress ledger (the test is the operator, not a client)."""
        uri = (self.state / "atomic" / "refunds.sqlite3").resolve().as_uri() + "?mode=ro"
        c = sqlite3.connect(uri, uri=True)
        try:
            effects = c.execute("SELECT count(*) FROM effects").fetchone()[0]
            claims = c.execute("SELECT state, count(*) FROM execution_claims_v1 GROUP BY state").fetchall()
        finally:
            c.close()
        return {"effects": effects, "claims": dict(claims), "ledger": Ledger(self.state / "ingress.db").rows()}

    def stop(self):
        self.proc.terminate()
        try:
            self.proc.wait(10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


@pytest.fixture
def ingress():
    base = pathlib.Path(tempfile.mkdtemp(prefix="mvp-ingress-"))
    srv = Ingress(base)
    try:
        yield srv
    finally:
        srv.stop()
        shutil.rmtree(base, ignore_errors=True)


EMPTY = {"effects": 0, "claims": {}, "ledger": []}


@needs_components
def test_valid_proposal_runs_decision_claim_and_route_b_and_returns_closed_data(ingress):
    out = ingress.submit(GOOD)
    assert_closed(out)
    assert (out["outcome"], out["code"], out["request_id"]) == ("executed", "EXECUTED", "case-1")
    seen = ingress.observe()
    assert seen["effects"] == 1 and seen["claims"] == {"consumed": 1}
    assert seen["ledger"] == [("case-1", "settled", "executed", "EXECUTED")]


@needs_components
def test_replayed_and_reused_proposals_cause_no_second_effect(ingress):
    assert ingress.submit(GOOD)["outcome"] == "executed"
    for variant in (GOOD, good(refund_reason="other"), good(amount=11)):
        out = ingress.submit(variant)
        assert_closed(out)
        assert (out["outcome"], out["code"]) == ("refused", "REPLAY")
    seen = ingress.observe()
    assert seen["effects"] == 1 and seen["claims"] == {"consumed": 1}


@needs_components
@pytest.mark.parametrize("changes", [{"amount": 11}, {"amount": 9.99}, {"request_id": "case-2"}, {"customer_id": "customer-002"},
                                     {"refund_reason": "other reason"},
                                     {"request_id": "builtins.eval"}, {"customer_id": "engine.safe_executor.ExecutionEnvelope"}])
def test_proposal_not_matching_the_approved_authority_is_held_with_no_claim_and_no_effect(ingress, changes):
    out = ingress.submit(good(**changes))
    assert_closed(out)
    assert (out["outcome"], out["code"]) == ("held", "DECISION_HELD") and out["reasons"]
    assert ingress.observe() == EMPTY


_COUNTER = iter(range(10_000))


def expect(code, raw):
    return pytest.param(raw, code, id=f"{code}-{next(_COUNTER):03d}")


SIMULATE = [jb(good(simulate=v)) for v in ("lost_ack", "timeout", "", None, True, False, 0, 1, [], {}, {"mode": "lost_ack"},
                                          ["lost_ack"], "None", "LOST_ACK")]
FORBIDDEN_MEMBERS = ["claim", "claim_id", "claim_json", "claim_commitment", "budget_id", "attempt_id", "operation_id",
                     "operation_issuer", "decision", "decision_id", "effect_id", "binding", "grant_id", "grant_status",
                     "grant_revision", "approval_status", "policy_state", "evidence_state", "set_grant_status",
                     "set_approval_status", "set_policy_state", "set_evidence_state", "remove_authoritative_state",
                     "provision_claim", "execute_claim_atomic", "execute", "method", "call", "op", "destination", "executor",
                     "policy", "workflow", "resolver", "sql", "query", "path", "actor", "principal", "adapter_id", "action_id",
                     "authority_context_ref", "requirement_id", "manifest_digest", "payload", "target", "__class__", "__proto__",
                     "$ref", "$type", "__import__", "engine.safe_executor.ExecutionEnvelope"]
HAND_BUILT_CLAIM = {
    "profile": "urn:cognous:profiles:local-authority-effect:0.1.0-proposed", "claim_id": "claim-forged", "decision_id": "d",
    "effect_id": "e", "grant_id": "g", "grant_revision": "1", "grant_status": "active", "budget_id": "b", "max_effects": 99,
    "operation_commitment": "sha256:" + "0" * 64, "claim_commitment": "sha256:" + "1" * 64,
    "source": "trusted_control_plane_workflow", "authorizing_by_possession": True}
CASES = (
    [expect("UNKNOWN_MEMBER", r) for r in SIMULATE]
    + [expect("UNKNOWN_MEMBER", jb(good(**{m: "x"}))) for m in FORBIDDEN_MEMBERS]
    + [expect("UNKNOWN_MEMBER", jb(good(claim=HAND_BUILT_CLAIM))),
       expect("UNKNOWN_MEMBER", jb(HAND_BUILT_CLAIM)),
       expect("UNKNOWN_MEMBER", jb({**HAND_BUILT_CLAIM, **GOOD})),
       expect("UNKNOWN_MEMBER", jb(good(set_grant_status={"grant_id": "x", "status": "active", "revision": "9"}))),
       expect("UNKNOWN_MEMBER", jb(good(remove_authoritative_state=["grant", "urn:cognous:grant:1"]))),
       expect("UNKNOWN_MEMBER", jb(good(execute_claim_atomic={"claim_id": "c", "simulate": "lost_ack"}))),
       expect("UNKNOWN_MEMBER", jb({"method": "provision_claim", "params": {"claim": HAND_BUILT_CLAIM}})),
       expect("UNKNOWN_MEMBER", jb({"method": "execute_claim_atomic", "params": ["claim-1", {}, "lost_ack"]})),
       expect("UNKNOWN_MEMBER", jb({"__class__": "engine.local_authority_effect.AtomicAuthorityEffectDestination"}))]
    # object / class references where a scalar is expected
    + [expect("BAD_TYPE", jb(good(**{k: v}))) for k, v in [
        ("request_id", {"__class__": "builtins.object"}), ("customer_id", ["os.system"]), ("amount", {"$ref": "#/amount"}),
        ("unit", {"__import__": "os"}), ("refund_reason", ["a"]), ("schema", {"x": 1}), ("amount", "10"), ("amount", True),
        ("amount", None), ("amount", [10]), ("request_id", 5), ("customer_id", None), ("unit", 1)]]
    + [expect("BAD_ID", jb(good(request_id=v))) for v in (
        "!!python/object/apply:os.system", "case 1", "", "-case", ".case", "x" * 65, "ｃａｓｅ-1", "case-1\n",
        "case/1", "../case-1", "a..b", "%2e%2e%2fetc", "case\x00", "case\u202e1", "a;b", "a|b", "a`b", "$(id)", "{{x}}")]
    # path traversal in ids (both id members)
    + [expect("BAD_ID", jb(good(customer_id=v))) for v in (
        "../../etc/passwd", "..", "/etc/passwd", "a/b", "a\\b", "customer-001/../customer-002", "customer-001/", "~root",
        "customer-001\x00", "customer-001\n", "C:\\x", "file:///etc/passwd", "customer 001", "a" * 65)]
    + [expect("BAD_VALUE", jb(good(**{k: v}))) for k, v in [
        ("amount", 0), ("amount", -10), ("amount", 1e9), ("amount", 1e400), ("unit", "EUR"), ("unit", "usd"),
        ("refund_reason", "Duplicate"), ("refund_reason", "../x"), ("refund_reason", ""), ("refund_reason", "a" * 65)]]
    + [expect("SCHEMA_MISMATCH", jb(good(schema=s))) for s in ("mvp-refund-proposal/2", "", "mvp-refund-proposal/1 ")]
    # malformed, oversized, duplicate, non-object
    + [expect("DUPLICATE_MEMBER", b'{"schema":"%s","request_id":"case-1","customer_id":"customer-001","amount":10,"amount":1000,'
                                  b'"unit":"USD","refund_reason":"duplicate"}' % P.SCHEMA.encode()),
       expect("DUPLICATE_MEMBER", b'{"schema":"%s","request_id":"case-1","request_id":"case-2","customer_id":"customer-001",'
                                  b'"amount":10,"unit":"USD","refund_reason":"duplicate"}' % P.SCHEMA.encode()),
       expect("DUPLICATE_MEMBER", b'{"simulate":"a","simulate":"b"}'),
       expect("TOO_LARGE", b"x" * 5000),
       expect("TOO_LARGE", jb(good(refund_reason="a" * 5000))),
       expect("TOO_LARGE", jb(good(blob="z" * 1_000_000))),
       expect("TOO_LARGE", b"[" * 100000),
       expect("MALFORMED_JSON", b"[" * 4000),
       expect("UNKNOWN_MEMBER", b'{"a":' * 600 + b"1" + b"}" * 600),  # legal deep nesting: parsed, then closed-schema refusal
       expect("MALFORMED_JSON", b""),
       expect("MALFORMED_JSON", b"{"),
       expect("MALFORMED_JSON", b"\xff\xfe{}"),
       expect("MALFORMED_JSON", b"\x80\x04\x95\x00\x00\x00\x00\x00\x00\x00\x00."),  # pickle protocol 4 header
       expect("MALFORMED_JSON", b"{'schema': 'mvp-refund-proposal/1'}"),
       expect("MALFORMED_JSON", b"\xef\xbb\xbf" + jb(GOOD)),
       expect("BAD_VALUE", jb(GOOD).replace(b"10", b"NaN")),
       expect("BAD_VALUE", jb(GOOD).replace(b"10", b"Infinity")),
       expect("NOT_OBJECT", b"[]"), expect("NOT_OBJECT", b'"x"'), expect("NOT_OBJECT", b"1"), expect("NOT_OBJECT", b"null"),
       expect("NOT_OBJECT", jb([GOOD])), expect("NOT_OBJECT", b"true"),
       expect("MISSING_MEMBER", jb({k: v for k, v in GOOD.items() if k != "unit"})),
       expect("MISSING_MEMBER", jb({"schema": P.SCHEMA})),
       expect("MISSING_MEMBER", b"{}")]
)


@needs_components
@pytest.mark.parametrize("raw,code", CASES)
def test_adversarial_input_is_refused_with_a_closed_code_and_causes_no_effect(ingress, raw, code):
    out = ingress.raw(raw)
    assert_closed(out)
    assert (out["outcome"], out["code"]) == ("refused", code)
    assert ingress.observe() == EMPTY
    # the ingress is still healthy and the one legitimate proposal still works exactly once afterwards
    assert ingress.submit(GOOD)["outcome"] == "executed"
    assert ingress.observe()["effects"] == 1


@needs_components
def test_slow_or_truncated_peer_gets_a_closed_refusal_and_no_effect(ingress):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(30)
        s.connect(ingress.sock)
        s.sendall(b'{"schema":')  # no newline, never closes: the server's own read timeout must fire
        out = json.loads(s.recv(4096))
    assert (out["outcome"], out["code"]) == ("refused", "REQUEST_TIMEOUT")
    assert ingress.observe() == EMPTY


@needs_components
def test_state_tree_is_single_owner_0700_dirs_0600_files_while_running_and_after_use(ingress):
    ingress.submit(good(simulate="lost_ack"))
    assert ingress.submit(GOOD)["outcome"] == "executed"
    assert (os.stat(ingress.state).st_mode & 0o777) == 0o700 and os.stat(ingress.state).st_uid == os.geteuid()
    assert verify_state_permissions(ingress.state) >= 10
    names = {p.name for p in ingress.state.rglob("*")}
    assert {"refunds.sqlite3", "ingress.db", "run.json"} <= names
    modes = {oct(p.lstat().st_mode & 0o777) for p in ingress.state.rglob("*") if p.is_file()}
    assert modes == {"0o600"}


@needs_components
def test_ingress_refuses_a_state_directory_that_is_not_owner_only(tmp_path):
    base = tmp_path / "b"
    base.mkdir()
    (base / "state").mkdir(mode=0o755)
    os.chmod(base / "state", 0o755)
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(HUB), os.environ.get("PYTHONPATH", "")]))
    p = subprocess.run([sys.executable, "-m", "tools.mvp_ingress.server", "--state-dir", str(base / "state"), "--socket",
                        str(base / "s.sock"), "--control-plane", CP, "--runtime", RT], cwd=str(HUB), env=env,
                       capture_output=True, text=True, timeout=60)
    assert p.returncode != 0 and "PermissionError" in p.stderr and not (base / "s.sock").exists()


PROBE = r'''
import json, os, sqlite3, sys
sys.dont_write_bytecode = True
state, client_path, sock = sys.argv[1], sys.argv[2], sys.argv[3]
import importlib.util
spec = importlib.util.spec_from_file_location("declared_client", client_path)
cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
out = {"uid": os.getuid(), "euid": os.geteuid()}
def attempt(name, fn):
    try:
        fn(); out[name] = "SUCCEEDED"
    except Exception as e:
        out[name] = type(e).__name__
attempt("listdir_state", lambda: os.listdir(state))
attempt("open_destination", lambda: open(os.path.join(state, "atomic", "refunds.sqlite3"), "rb"))
attempt("sqlite_destination_rw", lambda: sqlite3.connect(os.path.join(state, "atomic", "refunds.sqlite3")).execute("DELETE FROM effects"))
attempt("sqlite_destination_ro", lambda: sqlite3.connect("file:" + os.path.join(state, "atomic", "refunds.sqlite3") + "?mode=ro", uri=True).execute("SELECT * FROM effects"))
attempt("sqlite_ledger", lambda: sqlite3.connect(os.path.join(state, "ingress.db")).execute("DELETE FROM requests"))
attempt("create_in_state", lambda: open(os.path.join(state, "planted"), "w"))
attempt("open_run_record", lambda: open(os.path.join(state, "cp", "run.json"), "rb"))
attempt("stat_destination", lambda: os.stat(os.path.join(state, "atomic", "refunds.sqlite3")))
attempt("chmod_state", lambda: os.chmod(state, 0o777))
attempt("rename_state", lambda: os.rename(state, state + ".moved"))
attempt("ptrace_like_proc_mem", lambda: open("/proc/%s/mem" % sys.argv[4], "rb").read(1))
attempt("kill_ingress", lambda: os.kill(int(sys.argv[4]), 9))
results = []
for body in json.loads(sys.argv[5]):
    results.append(cl.submit(sock, body))
out["results"] = results
print(json.dumps(out))
'''


@needs_components
@needs_root
def test_unprivileged_second_process_reaches_only_the_declared_interface():
    base = pathlib.Path(tempfile.mkdtemp(prefix="mvp-ingress-np-"))
    srv = None
    try:
        srv = Ingress(base, socket_mode="666")
        shutil.copy(HUB / "tools/mvp_ingress/client.py", base / "client.py")
        (base / "probe.py").write_text(PROBE)
        for f in ("client.py", "probe.py"):
            os.chmod(base / f, 0o644)
        attack = [good(simulate="lost_ack"), good(claim=HAND_BUILT_CLAIM), good(set_grant_status="revoked"),
                  good(request_id="../../x"), GOOD, GOOD]

        def drop():
            os.setgroups([])
            os.setgid(65534)
            os.setuid(65534)
        env = {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent"}
        p = subprocess.run(["/usr/bin/python3", "-I", str(base / "probe.py"), str(srv.state), str(base / "client.py"), srv.sock,
                            str(srv.proc.pid), json.dumps(attack)], preexec_fn=drop, env=env, capture_output=True, text=True,
                           timeout=120)
        assert p.returncode == 0, p.stderr
        out = json.loads(p.stdout)
        assert out["uid"] == out["euid"] == 65534
        for name in ("listdir_state", "open_destination", "sqlite_destination_rw", "sqlite_destination_ro", "sqlite_ledger",
                     "create_in_state", "open_run_record", "stat_destination", "chmod_state", "rename_state",
                     "ptrace_like_proc_mem", "kill_ingress"):
            assert out[name] in ("PermissionError", "OperationalError"), (name, out[name])
        codes = [(r["outcome"], r["code"]) for r in out["results"]]
        assert codes == [("refused", "UNKNOWN_MEMBER")] * 3 + [("refused", "BAD_ID"), ("executed", "EXECUTED"),
                                                                ("refused", "REPLAY")]
        for r in out["results"]:
            assert_closed(r)
        seen = srv.observe()
        assert seen["effects"] == 1 and seen["claims"] == {"consumed": 1}
        assert not (srv.state / "planted").exists() and srv.proc.poll() is None
        assert verify_state_permissions(srv.state) >= 10
    finally:
        if srv:
            srv.stop()
        shutil.rmtree(base, ignore_errors=True)


@needs_components
@needs_root
def test_peer_uid_allow_list_is_enforced_in_addition_to_socket_permissions():
    base = pathlib.Path(tempfile.mkdtemp(prefix="mvp-ingress-al-"))
    srv = None
    try:
        srv = Ingress(base, socket_mode="666", allow_uid=[4242])
        shutil.copy(HUB / "tools/mvp_ingress/client.py", base / "client.py")
        os.chmod(base / "client.py", 0o644)
        code = ("import importlib.util,json,sys;s=importlib.util.spec_from_file_location('c',sys.argv[1]);m=importlib.util."
                "module_from_spec(s);s.loader.exec_module(m);print(json.dumps(m.submit(sys.argv[2],json.loads(sys.argv[3]))))")

        def drop():
            os.setgroups([])
            os.setgid(65534)
            os.setuid(65534)
        p = subprocess.run(["/usr/bin/python3", "-I", "-c", code, str(base / "client.py"), srv.sock, json.dumps(GOOD)],
                           preexec_fn=drop, env={"PATH": "/usr/bin"}, capture_output=True, text=True, timeout=60)
        assert json.loads(p.stdout)["code"] == "PEER_NOT_ALLOWED", p.stderr
        assert srv.observe() == EMPTY
    finally:
        if srv:
            srv.stop()
        shutil.rmtree(base, ignore_errors=True)


@needs_components
def test_socket_is_owner_only_by_default(ingress):
    assert (os.stat(ingress.sock).st_mode & 0o777) == 0o600
