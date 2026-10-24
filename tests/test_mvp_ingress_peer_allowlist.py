"""MVP ingress explicit peer-uid allowlist (SO_PEERCRED): fail closed, no default, no implicit entry, no wildcard.

SPDX-License-Identifier: Apache-2.0

Non-authorizing engineering tests. A peer with the ingress uid, or root, is outside this boundary by definition.
"""
from __future__ import annotations

import json
import os
import pathlib
import socket
import struct
import subprocess
import sys

import pytest

from tools.mvp_ingress import proposal as P
from tools.mvp_ingress import server as S

HUB = pathlib.Path(__file__).resolve().parents[1]
LAUNCH = [sys.executable, "-I", "-B", str(HUB / "tools/mvp_ingress/launch.py")]
needs_py311 = pytest.mark.skipif(sys.version_info < (3, 11), reason="launcher requires Python >= 3.11")
ME = os.geteuid()
LAST = None


class Core:
    def __init__(self):
        self.calls = []

    def handle(self, raw):
        self.calls.append(raw)
        return {"schema": P.SCHEMA, "outcome": "refused", "code": "SCHEMA_MISMATCH",
                                                               "request_id": None, "reasons": []}


class Spy:
    """Wraps the server end of the socketpair and records recv/sendall order (to prove nothing is read before the decision)."""
    def __init__(self, sock, log):
        self._s, self._log = sock, log

    def recv(self, *a, **k):
        self._log.append("recv")
        return self._s.recv(*a, **k)

    def sendall(self, *a, **k):
        self._log.append("sendall")
        return self._s.sendall(*a, **k)

    def __getattr__(self, name):
        return getattr(self._s, name)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self._s.close()


class OneShot:
    """Listener stand-in: accept() hands out one end of a real AF_UNIX socketpair (real SO_PEERCRED on the other end)."""
    def __init__(self):
        self.client, self.server = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        self.log = []

    def accept(self):
        return Spy(self.server, self.log), None


def _round(allowed, monkeypatch=None, peer=None):
    global LAST
    core, srv = Core(), OneShot()
    LAST = srv
    srv.client.sendall(b'{"x":1}\n')
    if peer is not None:
        monkeypatch.setattr(S, "_peer_uid", lambda conn: peer)
    S.serve(core, srv, allowed_uids=allowed, max_requests=1, read_timeout=2)
    srv.client.settimeout(2)
    out = json.loads(srv.client.recv(65536).split(b"\n")[0])
    return core, out


@pytest.mark.parametrize("bad", [None, [], (), set(), [-1], [2 ** 32 - 1], [True], ["0"], [1.0], [0, -1]])
def test_allowlist_must_be_explicit_concrete_uids(bad):
    with pytest.raises(ValueError):
        S.validate_allowed_uids(bad)
    with pytest.raises(ValueError):
        S.serve(Core(), OneShot(), allowed_uids=bad, max_requests=1)


def test_unauthorized_peer_is_rejected_before_any_request_processing(monkeypatch):
    core, out = _round({ME + 1}, monkeypatch=None)  # real SO_PEERCRED: this process is not in the allowlist
    assert out["code"] == "PEER_NOT_ALLOWED" and out["outcome"] == "refused" and core.calls == []


def test_injected_foreign_credentials_are_rejected_without_reading_the_request(monkeypatch):
    core, out = _round({ME}, monkeypatch, peer=ME + 4242)
    assert out["code"] == "PEER_NOT_ALLOWED" and core.calls == []
    assert LAST.log[0] == "sendall"  # the refusal is sent before any byte of the request is consumed (drain happens after)


def test_ingress_uid_is_not_implicitly_allowed():
    core, out = _round({ME + 1})
    assert out["code"] == "PEER_NOT_ALLOWED" and core.calls == []


def test_authorized_peer_is_served():
    core, out = _round({ME})
    assert len(core.calls) == 1 and out["code"] != "PEER_NOT_ALLOWED"


@pytest.mark.parametrize("exc", [OSError("x"), AttributeError("x"), ValueError("x"), TypeError("x"), struct.error("x")])
def test_unreadable_peer_credentials_fail_closed(monkeypatch, exc):
    def boom(conn):
        raise exc
    monkeypatch.setattr(S, "_peer_uid", boom)
    core, srv = Core(), OneShot()
    srv.client.sendall(b'{"x":1}\n')
    S.serve(core, srv, allowed_uids={ME}, max_requests=1, read_timeout=2)  # returns normally: no crash
    assert core.calls == [] and "recv" not in srv.log[:srv.log.index("sendall") if "sendall" in srv.log else None]


@needs_py311
@pytest.mark.parametrize("extra", [[], ["--allow-uid", "-1"], ["--allow-uid", "x"]])
def test_ingress_refuses_to_start_without_a_valid_allowlist(tmp_path, extra):
    base = tmp_path / "b"
    base.mkdir(mode=0o755)
    p = subprocess.run(LAUNCH + ["--state-dir", str(base / "state"), "--socket", str(base / "s.sock"), "--control-plane", "/nonexistent",
                                 "--runtime", "/nonexistent"] + extra, cwd=str(tmp_path), capture_output=True, text=True, timeout=60)
    assert p.returncode == 2 and ("allowlist" in p.stderr or "invalid" in p.stderr), p.stderr[-300:]
    assert not (base / "state").exists() and not (base / "s.sock").exists()
