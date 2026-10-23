"""Tests for the MVP ingress Qualification environment record capture (standard library plus pytest, tmp dirs only).

SPDX-License-Identifier: Apache-2.0

Non-authorizing. These tests exercise the capture script's PASS / FAIL / BLOCKED logic on temporary directories. They do
not run the ingress and do not assert any property of a production host.
"""
from __future__ import annotations

import json
import os
import socket
import sqlite3
import struct
import types

import pytest

from tools.mvp_ingress import capture_env_record as mod

ME = os.getuid()
CLIENT = 65534 if ME != 65534 else 65533


def _env(tmp_path, *, state_mode=0o700, file_mode=0o600, sock_mode=0o600, wal=True):
    state = tmp_path / "state"
    state.mkdir(mode=0o700)
    for name in ("dest.db", "authority.db"):
        c = sqlite3.connect(state / name)
        if wal:
            c.execute("pragma journal_mode=wal")
        c.execute("create table t(x)")
        c.commit()
        c.close()
        for ext in ("", "-wal", "-shm"):
            if (state / (name + ext)).exists():
                os.chmod(state / (name + ext), file_mode)
    os.chmod(state, state_mode)
    sockdir = tmp_path / "sock"
    sockdir.mkdir(mode=0o755)
    sp = str(sockdir / "i.sock")
    s = socket.socket(socket.AF_UNIX)
    s.bind(sp)
    os.chmod(sp, sock_mode)
    man = tmp_path / "manifest.json"
    man.write_text("{}")
    return s, ["--state-dir", str(state), "--socket", sp, "--ingress-uid", str(ME), "--ingress-gid", str(os.getgid()),
               "--client-uid", str(CLIENT), "--client-gid", str(CLIENT), "--db", str(state / "dest.db"),
               "--authority-store", str(state / "authority.db"), "--journal-mode", "wal" if wal else "delete",
               "--pin", "control_plane=0a41faa9", "--manifest", str(man)]


def _open_path_to(tmp_path):
    """Make the tmp tree traversable by the unprivileged probe, so the state dir's own mode is what decides."""
    for p in [tmp_path, *tmp_path.parents]:
        if str(p) in ("/", "/tmp"):
            break
        os.chmod(p, 0o755)


def _run(argv):
    return mod.build_record(mod.parser().parse_args(argv))


def _st(rec, cid):
    return next(c["status"] for c in rec["checks"] if c["id"] == cid)


@pytest.fixture
def env(tmp_path):
    s, argv = _env(tmp_path)
    yield tmp_path, argv
    s.close()


def test_clean_tmp_environment_passes_the_file_level_checks(env):
    _, argv = env
    rec = _run(argv)
    for cid in ("filesystem.state_tree_owner_only", "ipc.socket_mode_owner", "identity.client_distinct_unprivileged",
                "filesystem.no_extra_group_access", "configuration.journal_mode", "invocation.simulate_fixed_none",
                "invocation.operation_identity_fixed_true", "invocation.client_entry_point", "configuration.pins_and_manifests"):
        assert _st(rec, cid) == "PASS", cid
    assert _st(rec, "filesystem.no_acl_entries") in ("PASS", "BLOCKED")  # BLOCKED if the tmp filesystem has no xattr support
    assert rec["overall"] != "PASS" or all(c["status"] == "PASS" for c in rec["checks"])


def test_no_arguments_fails_closed_never_pass(capsys):
    rec = _run([])
    assert rec["overall"] in ("BLOCKED", "FAIL")
    for cid in ("identity.declared", "filesystem.state_tree_owner_only", "filesystem.no_acl_entries", "ipc.socket_mode_owner",
                "qualification.client_socket_reachable", "qualification.client_denied_state_access", "configuration.journal_mode"):
        assert _st(rec, cid) == "BLOCKED", cid
    assert mod.main([]) in (1, 2)


def test_record_is_deterministic_and_has_required_sections(env):
    _, argv = env
    a, b = _run(argv), _run(argv)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    for sec in ("platform", "python", "process_identity", "ipc", "filesystem", "invocation", "isolation_limits", "configuration", "qualification", "checks"):
        assert sec in a
    assert "pid" not in json.dumps(a["process_identity"]["capture_process"])
    assert a["python"]["unqualified"] == ["3.11"]
    assert "resistance to root" in a["claims"]["not_claimed"]


def test_state_dir_loosened_mode_fails(tmp_path):
    s, argv = _env(tmp_path, state_mode=0o755)
    assert _st(_run(argv), "filesystem.state_tree_owner_only") == "FAIL"
    s.close()


def test_file_group_readable_fails(tmp_path):
    s, argv = _env(tmp_path, file_mode=0o640)
    assert _st(_run(argv), "filesystem.state_tree_owner_only") == "FAIL"
    s.close()


def test_symlink_in_state_tree_fails(env):
    tmp, argv = env
    os.symlink("/etc/passwd", tmp / "state" / "link")
    assert _st(_run(argv), "filesystem.state_tree_owner_only") == "FAIL"


def test_socket_world_writable_fails(tmp_path):
    s, argv = _env(tmp_path, sock_mode=0o666)
    assert _st(_run(argv), "ipc.socket_mode_owner") == "FAIL"
    s.close()


def test_socket_group_mode_needs_dedicated_policy(tmp_path):
    s, argv = _env(tmp_path, sock_mode=0o660)
    assert _st(_run(argv), "ipc.socket_mode_owner") == "FAIL"
    s.close()


def test_client_same_uid_as_ingress_fails(env):
    _, argv = env
    argv = argv + ["--client-uid", str(ME), "--client-gid", str(os.getgid())]
    assert _st(_run(argv), "identity.client_distinct_unprivileged") == "FAIL"


def test_client_uid_zero_fails(env):
    _, argv = env
    assert _st(_run(argv + ["--client-uid", "0"]), "identity.client_distinct_unprivileged") == "FAIL"


def test_ancestor_writable_by_others_fails(tmp_path):
    s, argv = _env(tmp_path)
    os.chmod(tmp_path / "sock", 0o777)
    assert _st(_run(argv), "filesystem.ancestors_not_writable_by_others") == "FAIL"
    s.close()


def test_journal_mode_mismatch_fails(tmp_path):
    s, argv = _env(tmp_path, wal=False)
    argv = argv[:argv.index("--journal-mode") + 1] + ["wal"] + argv[argv.index("--journal-mode") + 2:]
    assert _st(_run(argv), "configuration.journal_mode") == "FAIL"
    s.close()


def _acl_blob(uid):
    e = lambda tag, perm, i: struct.pack("<HHI", tag, perm, i)  # noqa: E731
    return struct.pack("<I", 2) + e(1, 7, 0xFFFFFFFF) + e(2, 4, uid) + e(4, 0, 0xFFFFFFFF) + e(0x10, 4, 0xFFFFFFFF) + e(0x20, 0, 0xFFFFFFFF)


def test_acl_entry_on_socket_or_state_dir_fails(env):
    tmp, argv = env
    target = str(tmp / "state")
    try:
        os.setxattr(target, "system.posix_acl_access", _acl_blob(CLIENT))
    except OSError as exc:
        pytest.skip("cannot set a POSIX ACL on this tmp filesystem: %s" % exc)
    assert _st(_run(argv), "filesystem.no_acl_entries") == "FAIL"


def test_acl_on_state_file_fails(env):
    tmp, argv = env
    try:
        os.setxattr(str(tmp / "state" / "dest.db"), "system.posix_acl_access", _acl_blob(CLIENT))
    except OSError as exc:
        pytest.skip("cannot set a POSIX ACL: %s" % exc)
    assert _st(_run(argv), "filesystem.no_acl_entries") == "FAIL"


def test_unreadable_acl_is_blocked_not_pass(env, monkeypatch):
    _, argv = env

    def boom(*a, **k):
        raise OSError(95, "not supported")
    monkeypatch.setattr(mod.os, "listxattr", boom)
    assert _st(_run(argv), "filesystem.no_acl_entries") == "BLOCKED"


@pytest.mark.parametrize("value,want", [("0\n", "FAIL"), ("1\n", "PASS"), ("2\n", "PASS"), (None, "BLOCKED")])
def test_ptrace_scope(env, monkeypatch, value, want):
    _, argv = env
    real = mod._read
    monkeypatch.setattr(mod, "_read", lambda p: value if p.endswith("ptrace_scope") else real(p))
    assert _st(_run(argv), "isolation.ptrace_scope") == want


def test_not_root_blocks_client_probe(env, monkeypatch):
    _, argv = env
    monkeypatch.setattr(mod.os, "geteuid", lambda: 1000)
    rec = _run(argv)
    for cid in ("qualification.client_capabilities_empty", "qualification.client_socket_reachable",
                "qualification.client_denied_state_access", "qualification.client_denied_ingress_process"):
        assert _st(rec, cid) == "BLOCKED", cid
    assert rec["overall"] != "PASS"


def test_python_311_is_fail(env, monkeypatch):
    _, argv = env
    fake = types.SimpleNamespace(version_info=(3, 11, 9, "final", 0), executable=mod.sys.executable, version="3.11.9",
                                 stdlib_module_names=mod.sys.stdlib_module_names, stdout=mod.sys.stdout)
    monkeypatch.setattr(mod.platform, "python_version", lambda: "3.11.9")
    monkeypatch.setattr(mod, "sys", fake)
    assert _st(_run(argv), "python.profile") == "FAIL"


def test_non_none_simulate_in_core_fails(env, tmp_path):
    _, argv = env
    root = tmp_path / "repo"
    (root / "tools/mvp_ingress").mkdir(parents=True)
    (root / "tools/mvp_ingress/core.py").write_text("f(simulate='lost_ack')\n")
    (root / "tools/mvp_ingress/synthetic_host.py").write_text("g(operation_identity=True)\n")
    (root / "tools/mvp_ingress/client.py").write_text("import json\ndef submit():\n    pass\n")
    rec = _run(argv + ["--repo-root", str(root)])
    assert _st(rec, "invocation.simulate_fixed_none") == "FAIL"
    assert _st(rec, "invocation.operation_identity_fixed_true") == "PASS"


def test_non_stdlib_client_import_fails(env, tmp_path):
    _, argv = env
    root = tmp_path / "repo"
    (root / "tools/mvp_ingress").mkdir(parents=True)
    (root / "tools/mvp_ingress/core.py").write_text("f(simulate=None)\n")
    (root / "tools/mvp_ingress/synthetic_host.py").write_text("g(operation_identity=False)\n")
    (root / "tools/mvp_ingress/client.py").write_text("import pydantic\ndef submit():\n    pass\n")
    rec = _run(argv + ["--repo-root", str(root)])
    assert _st(rec, "invocation.client_entry_point") == "FAIL"
    assert _st(rec, "invocation.operation_identity_fixed_true") == "FAIL"


def test_missing_pins_are_blocked(env):
    _, argv = env
    i = argv.index("--pin")
    assert _st(_run(argv[:i] + argv[i + 2:]), "configuration.pins_and_manifests") == "BLOCKED"


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_root_client_probe_denies_state_but_not_socket_when_0600_foreign_owner(env):
    tmp, argv = env
    _open_path_to(tmp)
    rec = _run(argv)
    assert _st(rec, "qualification.client_capabilities_empty") == "PASS"
    assert _st(rec, "qualification.client_denied_state_access") == "PASS"
    # socket 0600 owned by the ingress uid: a distinct-uid client cannot connect. The record must say FAIL, not PASS.
    assert _st(rec, "qualification.client_socket_reachable") == "FAIL"


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_root_client_probe_flags_loosened_state_dir(tmp_path):
    s, argv = _env(tmp_path, state_mode=0o755)
    _open_path_to(tmp_path)
    rec = _run(argv)
    assert _st(rec, "qualification.client_denied_state_access") == "FAIL"
    s.close()
