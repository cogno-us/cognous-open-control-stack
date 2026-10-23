"""Declared client interface: submit one JSON proposal, receive one JSON result. Standard library only.

SPDX-License-Identifier: Apache-2.0

This module imports nothing from the Control Plane, the Runtime or the ingress core and holds no handle to them. It is
the whole supported client surface; everything else a process could do with the socket is just bytes into the same parser.
"""
from __future__ import annotations

import json
import socket

MAX_RESPONSE_BYTES = 8192


def submit_bytes(socket_path: str, raw: bytes, *, timeout: float = 15.0) -> dict:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect(socket_path)
        s.sendall(raw + b"\n")
        s.shutdown(socket.SHUT_WR)
        chunks, size = [], 0
        while True:
            part = s.recv(4096)
            if not part:
                break
            chunks.append(part)
            size += len(part)
            if size > MAX_RESPONSE_BYTES:
                raise ValueError("response too large")
    return json.loads(b"".join(chunks).decode("utf-8"))


def submit(socket_path: str, proposal: dict, *, timeout: float = 15.0) -> dict:
    """Send a proposal (a JSON-serialisable dict). Returns the result dict (outcome executed/refused/held/unknown)."""
    return submit_bytes(socket_path, json.dumps(proposal, allow_nan=False).encode("utf-8"), timeout=timeout)
