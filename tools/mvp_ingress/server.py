"""Designated ingress process: owns the state tree, serves governed proposals on a Unix socket, nothing else.

SPDX-License-Identifier: Apache-2.0

Capability boundary (Linux): the destination, the authority store and every writer capability exist only inside this
process and its owner-only (0700/0600) state tree. A client holds, at most, a connection to the socket; the protocol has
exactly one operation (propose) whose input is a closed JSON schema and whose output is a closed JSON result. There is no
code upload, no object handle, no method name, no path and no executor argument on the wire. A process running as the
ingress uid (or root) is outside this boundary by definition.

    python -m tools.mvp_ingress.server --state-dir DIR --socket PATH --control-plane ROOT --runtime ROOT
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import stat
import struct
import sys

from . import proposal as P
from .core import IngressCore, verify_state_permissions

READ_TIMEOUT = 5.0


def _peer_uid(conn):
    return struct.unpack("3i", conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))[1]


def _read_request(conn):
    conn.settimeout(READ_TIMEOUT)
    buf = b""
    while len(buf) <= P.MAX_REQUEST_BYTES:
        part = conn.recv(P.MAX_REQUEST_BYTES + 1 - len(buf))
        if not part:
            break
        buf += part
        if b"\n" in buf:
            buf = buf.split(b"\n", 1)[0]
            break
    return buf


def _drain(conn, limit=1 << 20):
    """Half-close, then discard what the peer still sends (bounded), so the answer is not lost to a connection reset."""
    try:
        conn.shutdown(socket.SHUT_WR)
        conn.settimeout(0.5)
        seen = 0
        while seen < limit:
            part = conn.recv(65536)
            if not part:
                break
            seen += len(part)
    except OSError:
        pass


def prepare_state_dir(state_dir):
    """Create (or accept only an already-correct) owner-only state directory. umask 077 for everything created after."""
    os.umask(0o077)
    if not os.path.lexists(state_dir):
        os.mkdir(state_dir, 0o700)
    st = os.lstat(state_dir)
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid() or stat.S_IMODE(st.st_mode) != 0o700:
        raise PermissionError("state directory must be an owner-only 0700 directory owned by the ingress uid")


def make_listener(socket_path, *, socket_mode=0o600):
    if os.path.lexists(socket_path):
        raise FileExistsError("socket path exists")
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    old = os.umask(0o777)
    try:
        srv.bind(socket_path)
    finally:
        os.umask(old)
    os.chmod(socket_path, socket_mode)
    srv.listen(8)
    return srv


def serve(core, srv, *, allowed_uids=None, max_requests=None, state_dir=None):
    """Serve serially (the workflow is not re-entrant). ``allowed_uids`` None: socket permissions alone decide who connects."""
    handled = 0
    while max_requests is None or handled < max_requests:
        conn, _ = srv.accept()
        with conn:
            try:
                if allowed_uids is not None and _peer_uid(conn) not in allowed_uids:
                    out = P.result("refused", "PEER_NOT_ALLOWED")
                else:
                    try:
                        raw = _read_request(conn)
                    except (socket.timeout, OSError):
                        out = P.result("refused", "REQUEST_TIMEOUT")
                    else:
                        try:
                            out = core.handle(raw)
                        except Exception:
                            out = P.result("unknown", "OUTCOME_UNKNOWN")
                conn.sendall(json.dumps(out, sort_keys=True).encode("utf-8") + b"\n")
                _drain(conn)
            except OSError:
                pass
        handled += 1
        if state_dir is not None:
            verify_state_permissions(state_dir)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", required=True)
    ap.add_argument("--socket", required=True)
    ap.add_argument("--control-plane", required=True)
    ap.add_argument("--runtime", required=True)
    ap.add_argument("--socket-mode", default="600")
    ap.add_argument("--allow-uid", type=int, action="append", default=None)
    ap.add_argument("--max-requests", type=int, default=None)
    a = ap.parse_args(argv)
    prepare_state_dir(a.state_dir)
    from .synthetic_host import SyntheticHost
    host = SyntheticHost(control_plane_root=a.control_plane, runtime_root=a.runtime, state_dir=a.state_dir)
    core = IngressCore(host, os.path.join(a.state_dir, "ingress.db"))
    verify_state_permissions(a.state_dir)
    srv = make_listener(a.socket, socket_mode=int(a.socket_mode, 8))
    allowed = None if a.allow_uid is None else set(a.allow_uid) | {os.geteuid()}
    print("READY", flush=True)
    try:
        serve(core, srv, allowed_uids=allowed, max_requests=a.max_requests, state_dir=a.state_dir)
    finally:
        srv.close()
        try:
            os.unlink(a.socket)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
