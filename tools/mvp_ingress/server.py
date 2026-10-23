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
import signal
import socket
import stat
import time
import struct
import sys

from . import proposal as P
from .core import IngressCore, verify_state_permissions

READ_TIMEOUT = 5.0


def _peer_uid(conn):
    return struct.unpack("3i", conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))[1]


def _read_request(conn, timeout=None):
    """Read one request line under a monotonic TOTAL deadline (a trickling peer cannot extend it byte by byte)."""
    deadline = time.monotonic() + (READ_TIMEOUT if timeout is None else timeout)
    buf = b""
    while len(buf) <= P.MAX_REQUEST_BYTES:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise socket.timeout("total deadline")
        conn.settimeout(remaining)
        part = conn.recv(P.MAX_REQUEST_BYTES + 1 - len(buf))
        if not part:
            break
        buf += part
        if b"\n" in buf:
            buf = buf.split(b"\n", 1)[0]
            break
    return buf


def _drain(conn, limit=1 << 20, total=0.5):
    """Half-close, then discard what the peer still sends, bounded by BOTH a byte cap and a total deadline."""
    try:
        conn.shutdown(socket.SHUT_WR)
        deadline = time.monotonic() + total
        seen = 0
        while seen < limit:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            conn.settimeout(remaining)
            part = conn.recv(min(65536, limit - seen))
            if not part:
                break
            seen += len(part)
    except OSError:
        pass


def check_parents(*paths):
    """Refuse unless every ancestor directory of each path is owned by root or this uid and is not writable by group or
    other (a sticky directory is accepted). Otherwise a non-owner could rename or replace the state tree or the socket."""
    me = os.geteuid()
    for path in paths:
        parent = os.path.dirname(os.path.realpath(os.path.abspath(path)))
        while True:
            st = os.lstat(parent)
            if not stat.S_ISDIR(st.st_mode) or st.st_uid not in (0, me):
                raise PermissionError("ancestor directory is not a directory owned by root or the ingress uid")
            if stat.S_IMODE(st.st_mode) & 0o022 and not st.st_mode & stat.S_ISVTX:
                raise PermissionError("ancestor directory is writable by a non-owner and not sticky")
            if parent == os.path.dirname(parent):
                break
            parent = os.path.dirname(parent)


def prepare_state_dir(state_dir):
    """Create (or accept only an already-correct) owner-only state directory. umask 077 for everything created after."""
    os.umask(0o077)
    if not os.path.lexists(state_dir):
        os.mkdir(state_dir, 0o700)
    st = os.lstat(state_dir)
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid() or stat.S_IMODE(st.st_mode) != 0o700:
        raise PermissionError("state directory must be an owner-only 0700 directory owned by the ingress uid")


def make_listener(socket_path, *, socket_mode=0o600, lock_path=None):
    """Bind the socket. Probe/unlink/bind runs under an flock on ``lock_path`` (a file in the state dir) so two concurrent
    starts cannot unlink each other's live socket. Returns (listener, (st_dev, st_ino)) for ownership-checked cleanup."""
    import fcntl
    lock = None
    if lock_path is not None:
        lock = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        if os.path.lexists(socket_path):
            probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                probe.connect(socket_path)
            except (ConnectionRefusedError, FileNotFoundError):
                if not stat.S_ISSOCK(os.lstat(socket_path).st_mode):
                    raise FileExistsError("socket path exists and is not a socket")
                os.unlink(socket_path)  # stale: nothing is listening
            except OSError:
                raise FileExistsError("socket path exists") from None
            else:
                raise FileExistsError("a live ingress already listens on this socket")
            finally:
                probe.close()
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        old = os.umask(0o777)
        try:
            srv.bind(socket_path)
        finally:
            os.umask(old)
        os.chmod(socket_path, socket_mode)
        srv.listen(8)
        st = os.lstat(socket_path)
        return srv, (st.st_dev, st.st_ino)
    finally:
        if lock is not None:
            os.close(lock)


def unlink_if_ours(socket_path, ident):
    """Remove the socket file only if it is still the inode this process bound."""
    try:
        st = os.lstat(socket_path)
        if (st.st_dev, st.st_ino) == ident and stat.S_ISSOCK(st.st_mode):
            os.unlink(socket_path)
    except OSError:
        pass


def serve(core, srv, *, allowed_uids=None, max_requests=None, state_dir=None, read_timeout=None):
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
                        raw = _read_request(conn, read_timeout)
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
    ap.add_argument("--read-timeout", type=float, default=READ_TIMEOUT)
    ap.add_argument("--max-requests", type=int, default=None)
    a = ap.parse_args(argv)
    check_parents(a.state_dir, a.socket)
    prepare_state_dir(a.state_dir)
    from .synthetic_host import SyntheticHost
    host = SyntheticHost(control_plane_root=a.control_plane, runtime_root=a.runtime, state_dir=a.state_dir)
    core = IngressCore(host, os.path.join(a.state_dir, "ingress.db"))
    verify_state_permissions(a.state_dir)
    srv, ident = make_listener(a.socket, socket_mode=int(a.socket_mode, 8),
                               lock_path=os.path.join(a.state_dir, "socket.lock"))
    allowed = None if a.allow_uid is None else set(a.allow_uid) | {os.geteuid()}
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))  # clean shutdown removes the socket file
    print("READY", flush=True)
    try:
        serve(core, srv, allowed_uids=allowed, max_requests=a.max_requests, state_dir=a.state_dir,
              read_timeout=a.read_timeout)
    finally:
        srv.close()
        unlink_if_ours(a.socket, ident)
    return 0


if __name__ == "__main__":
    sys.exit(main())
