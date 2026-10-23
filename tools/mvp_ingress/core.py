"""Ingress core: proposal -> Control Plane decision -> real claim provisioning -> route B execute -> structured result.

SPDX-License-Identifier: Apache-2.0

Lives only inside the designated ingress process. It is not importable by, or reachable from, a client: clients speak the
socket protocol in ``server.py`` and receive only the JSON result built by ``proposal.result``. The core hard-codes
``simulate=None``; no code path passes a caller-supplied value to the executor, destination, claim or authority writers.
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
import stat as _stat
import time

from . import proposal as P


class Ledger:
    """Ingress-owned request ledger. A reserved request id is never executed twice, whatever the outcome of the first."""

    def __init__(self, path):
        self.path = str(path)
        c = self._conn()
        try:
            c.execute("CREATE TABLE IF NOT EXISTS requests(request_id TEXT PRIMARY KEY, digest TEXT NOT NULL,"
                      " state TEXT NOT NULL, outcome TEXT, code TEXT, reserved_at REAL NOT NULL)")
        finally:
            c.close()

    def _conn(self):
        return sqlite3.connect(self.path, timeout=10, isolation_level=None)

    def reserve(self, request_id, digest) -> bool:
        c = self._conn()
        try:
            c.execute("INSERT INTO requests(request_id,digest,state,reserved_at) VALUES(?,?,'inflight',?)",
                      (request_id, digest, time.time()))
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            c.close()

    def release(self, request_id):
        c = self._conn()
        try:
            c.execute("DELETE FROM requests WHERE request_id=? AND state='inflight'", (request_id,))
        finally:
            c.close()

    def settle(self, request_id, outcome, code):
        c = self._conn()
        try:
            c.execute("UPDATE requests SET state='settled', outcome=?, code=? WHERE request_id=?", (outcome, code, request_id))
        finally:
            c.close()

    def rows(self):
        c = self._conn()
        try:
            return c.execute("SELECT request_id,state,outcome,code FROM requests ORDER BY request_id").fetchall()
        finally:
            c.close()


class IngressCore:
    def __init__(self, host, ledger_path):
        # host supplies: build_proposal(fields), workflow, executor, envelope(decision, proposal), now
        self._host = host
        self._ledger = Ledger(ledger_path)

    def handle(self, raw: bytes) -> dict:
        try:
            fields = P.parse(raw)
        except P.Refusal as refusal:
            return P.result("refused", refusal.code)
        except Exception:
            return P.result("refused", "MALFORMED_JSON")
        request_id = fields["request_id"]
        digest = hashlib.sha256(bytes(raw)).hexdigest()
        if not self._ledger.reserve(request_id, digest):
            return P.result("refused", "REPLAY", request_id=request_id)
        out = self._run(fields, request_id)
        if out.pop("_burn"):
            self._ledger.settle(request_id, out["outcome"], out["code"])
        else:
            self._ledger.release(request_id)
        return out

    def _run(self, fields, request_id) -> dict:
        host = self._host
        # Stage 1: Control Plane decision. Nothing has been issued or executed yet, so a failure here is a plain refusal.
        try:
            proposal = host.build_proposal(fields)
            decision = host.workflow.decide(proposal, now=host.now)
        except Exception:
            return {**P.result("refused", "DECISION_REFUSED", request_id=request_id), "_burn": False}
        if decision.result == "hold":
            return {**P.result("held", "DECISION_HELD", request_id=request_id, reasons=decision.reasons), "_burn": False}
        if decision.result != "authorized":
            return {**P.result("refused", "DECISION_REFUSED", request_id=request_id, reasons=decision.reasons), "_burn": False}
        # Stage 2: real claim provisioning (Control Plane claim path into the route B destination).
        try:
            claim = host.executor.provision_claim(proposal=proposal, decision=decision, now=host.now)
        except Exception:
            return {**P.result("refused", "CLAIM_REFUSED", request_id=request_id), "_burn": True}
        # Stage 3: route B execute, simulate fixed to None. Any surprise after this point is UNKNOWN, never a refusal.
        try:
            res = host.executor.execute(envelope=host.envelope(decision, proposal), claim_id=claim.claim_id, simulate=None)
        except Exception:
            return {**P.result("unknown", "OUTCOME_UNKNOWN", request_id=request_id), "_burn": True}
        status = getattr(res, "status", None)
        if status == "executed" and getattr(res, "acknowledged", False) is True:
            return {**P.result("executed", "EXECUTED", request_id=request_id), "_burn": True}
        if status == "denied" and getattr(res, "attempted", True) is False:
            code = "DUPLICATE_OPERATION" if getattr(res, "error", None) == "operation_already_committed" else "EXECUTION_DENIED"
            return {**P.result("refused", code, request_id=request_id), "_burn": True}
        return {**P.result("unknown", "OUTCOME_UNKNOWN", request_id=request_id), "_burn": True}


def verify_state_permissions(root, *, uid=None):
    """Raise PermissionError unless ``root`` is a real directory 0700 and every entry is owned by ``uid`` (default: this
    process), not a symlink, with directories 0700 and files 0600. Returns the number of entries checked."""
    uid = os.geteuid() if uid is None else uid
    count = 0
    stack = [str(root)]
    while stack:
        path = stack.pop()
        st = os.lstat(path)
        count += 1
        if _stat.S_ISLNK(st.st_mode):
            raise PermissionError("symlink in state tree")
        if st.st_uid != uid:
            raise PermissionError("state entry not owned by the ingress uid")
        if _stat.S_ISDIR(st.st_mode):
            if _stat.S_IMODE(st.st_mode) != 0o700:
                raise PermissionError("state directory mode is not 0700")
            stack.extend(os.path.join(path, n) for n in os.listdir(path))
        elif _stat.S_ISREG(st.st_mode):
            if _stat.S_IMODE(st.st_mode) != 0o600:
                raise PermissionError("state file mode is not 0600")
        else:
            raise PermissionError("unexpected file type in state tree")
    return count
