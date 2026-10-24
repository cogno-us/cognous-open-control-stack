"""Tests for the MVP ingress Qualification environment record capture (standard library plus pytest, tmp dirs only).

SPDX-License-Identifier: Apache-2.0

Non-authorizing. These tests exercise the capture script's PASS / FAIL / BLOCKED logic on temporary directories. They do
not run the ingress and do not assert any property of a production host.
"""
from __future__ import annotations

import json
import os
import hashlib
import socket
import sqlite3
import struct
import types

import pytest

from tools.mvp_env_record import capture_env_record as mod

ME = os.getuid()
CLIENT = 65534 if ME != 65534 else 65533


def _env(tmp_path, *, state_mode=0o700, file_mode=0o600, sock_mode=0o660, wal=True):
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
    s.listen(64)
    man = tmp_path / "manifest.json"
    man.write_text("{}")
    return s, ["--state-dir", str(state), "--socket", sp, "--ingress-uid", str(ME), "--ingress-gid", str(os.getgid()),
               "--client-uid", str(CLIENT), "--client-gid", str(CLIENT), "--db", str(state / "dest.db"),
               "--authority-store", str(state / "authority.db"), "--journal-mode", "wal" if wal else "delete",
               "--pin", "control_plane=0a41faa9", "--accept-unverified-pins", "--manifest", str(man)]


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


def _fake_socket(monkeypatch, sp, gid=None, uid=None):
    real = os.lstat

    def fake(path, *a, **k):
        st = real(path, *a, **k)
        if str(path) == sp:
            return os.stat_result((st.st_mode, st.st_ino, st.st_dev, st.st_nlink, st.st_uid if uid is None else uid,
                                   st.st_gid if gid is None else gid, st.st_size, 0, 0, 0))
        return st
    monkeypatch.setattr(mod.os, "lstat", fake)


DEDICATED_GID = 4242
NAMES = {ME: "ingr", CLIENT: "cli"}


@pytest.fixture(autouse=True)
def ipc_identity(monkeypatch):
    """Stand-in identities for the unprivileged tmp environment: a dedicated group 4242 holding exactly ingr and cli."""
    real_name = mod._name_uid
    monkeypatch.setattr(mod, "_name_uid", lambda u: NAMES.get(u) or real_name(u))
    monkeypatch.setattr(mod, "_group_members", lambda g: ["ingr", "cli"] if g == DEDICATED_GID else [])
    real_lstat = os.lstat

    def fake(path, *a, **k):
        st = real_lstat(path, *a, **k)
        if str(path).endswith(".sock"):
            return os.stat_result((st.st_mode, st.st_ino, st.st_dev, st.st_nlink, st.st_uid, DEDICATED_GID, st.st_size, 0, 0, 0))
        return st
    monkeypatch.setattr(mod.os, "lstat", fake)


@pytest.fixture
def env(tmp_path):
    s, argv = _env(tmp_path)
    yield tmp_path, argv
    s.close()


def test_clean_tmp_environment_passes_the_file_level_checks(env):
    _, argv = env
    rec = _run(argv)
    for cid in ("filesystem.state_tree_owner_only", "ipc.socket_mode_owner_group", "identity.client_distinct_unprivileged",
                "filesystem.no_extra_group_access", "configuration.journal_mode", "invocation.simulate_fixed_none",
                "invocation.operation_identity_fixed_true", "invocation.client_entry_point", "configuration.pins_and_manifests"):
        assert _st(rec, cid) == "PASS", cid
    assert _st(rec, "filesystem.no_acl_entries") in ("PASS", "BLOCKED")  # BLOCKED if the tmp filesystem has no xattr support
    assert rec["overall"] != "PASS" or all(c["status"] == "PASS" for c in rec["checks"])


def test_no_arguments_fails_closed_never_pass(capsys):
    rec = _run([])
    assert rec["overall"] in ("BLOCKED", "FAIL")
    for cid in ("identity.declared", "filesystem.state_tree_owner_only", "filesystem.no_acl_entries", "ipc.socket_mode_owner_group",
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
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "FAIL"
    s.close()


def test_socket_0600_fails(tmp_path):
    s, argv = _env(tmp_path, sock_mode=0o600)
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "FAIL"
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
def test_root_client_probe_denies_state_and_foreign_group_socket(env):
    tmp, argv = env
    _open_path_to(tmp)
    rec = _run(argv)
    assert _st(rec, "qualification.client_capabilities_empty") == "PASS"
    assert _st(rec, "qualification.client_denied_state_access") == "PASS"
    # the real socket group is gid 0 and the client is not in it: it cannot connect. The record must say FAIL, not PASS.
    assert _st(rec, "qualification.client_socket_reachable") == "FAIL"


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_root_client_probe_flags_loosened_state_dir(tmp_path):
    s, argv = _env(tmp_path, state_mode=0o755)
    _open_path_to(tmp_path)
    rec = _run(argv)
    assert _st(rec, "qualification.client_denied_state_access") == "FAIL"
    s.close()


# ---- review round 1 ------------------------------------------------------------------------------------------------

def test_untraversable_for_detects_missing_search_bit(tmp_path):
    d = tmp_path / "a"
    (d / "b").mkdir(parents=True)
    os.chmod(d, 0o700)
    os.chmod(d / "b", 0o755)
    me = os.getuid()
    assert mod.untraversable_for(str(d / "b"), me + 1, {me + 1}) == [str(d)] or str(d) in mod.untraversable_for(str(d / "b"), me + 1, {me + 1})
    assert str(d) not in mod.untraversable_for(str(d / "b"), me, {os.getgid()})
    os.chmod(d, 0o750)  # group search only
    assert str(d) in mod.untraversable_for(str(d / "b"), me + 1, {me + 1})
    assert str(d) not in mod.untraversable_for(str(d / "b"), me + 1, {os.stat(d).st_gid})


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_probe_denial_behind_untraversable_ancestor_is_blocked_not_pass(tmp_path):
    s, argv = _env(tmp_path, state_mode=0o755)  # loose state dir ...
    _open_path_to(tmp_path)
    os.chmod(tmp_path, 0o700)                   # ... hidden behind a 0700 ancestor
    rec = _run(argv)
    assert _st(rec, "qualification.client_denied_state_access") == "BLOCKED"
    assert "traversal" in next(c["detail"] for c in rec["checks"] if c["id"] == "qualification.client_denied_state_access")
    s.close()


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_probe_enoent_is_not_counted_as_denied(tmp_path):
    s, argv = _env(tmp_path)  # 0700 state dir: its own probes are denied; only the missing file gives ENOENT
    _open_path_to(tmp_path)
    other = tmp_path / "other"
    other.mkdir(mode=0o755)
    k = argv.index("--db")
    argv = argv[:k] + ["--db", str(other / "missing.db")] + argv[k + 2:]
    rec = _run(argv)
    assert _st(rec, "qualification.client_denied_state_access") == "BLOCKED"
    res = next(c for c in rec["checks"] if c["id"] == "qualification.client_denied_state_access")["data"]["results"]
    assert any(v.startswith("error:ENOENT") for v in res.values())
    s.close()


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_probe_child_failure_is_blocked_and_parent_survives(env, monkeypatch):
    _, argv = env
    monkeypatch.setattr(mod.os, "setresuid", lambda *a: (_ for _ in ()).throw(OSError(1, "boom")))
    rec = _run(argv)
    assert _st(rec, "qualification.client_denied_state_access") == "BLOCKED"
    assert rec["overall"] != "PASS"


def test_interpreter_match_pass_mismatch_and_no_pid(env, monkeypatch):
    _, argv = env
    assert _st(_run(argv), "python.interpreter_matches_ingress") == "BLOCKED"
    argv = argv + ["--ingress-pid", str(os.getpid())]
    assert _st(_run(argv), "python.interpreter_matches_ingress") == "PASS"
    monkeypatch.setattr(mod, "_proc_exe", lambda pid: "/usr/bin/python3.11")
    assert _st(_run(argv), "python.interpreter_matches_ingress") == "FAIL"
    monkeypatch.setattr(mod, "_proc_exe", lambda pid: None)
    assert _st(_run(argv), "python.interpreter_matches_ingress") == "BLOCKED"


def test_ingress_process_uid_mismatch_fails(env):
    _, argv = env
    i = argv.index("--ingress-uid")
    argv = argv[:i] + ["--ingress-uid", str(ME + 1)] + argv[i + 2:] + ["--ingress-pid", str(os.getpid())]
    assert _st(_run(argv), "identity.ingress_process") == "FAIL"


def test_section_exception_becomes_blocked_check(env, monkeypatch):
    _, argv = env
    monkeypatch.setattr(mod, "mountinfo", lambda p: (_ for _ in ()).throw(RuntimeError("x")))
    rec = _run(argv)
    assert any(c["id"] == "platform.exception" and c["status"] == "BLOCKED" and "RuntimeError" in c["detail"] for c in rec["checks"])
    assert rec["overall"] != "PASS"


def test_main_emits_blocked_record_on_exception(env, monkeypatch, capsys):
    _, argv = env
    monkeypatch.setattr(mod, "build_record", lambda a: (_ for _ in ()).throw(ValueError("x")))
    rc = mod.main(argv)
    out = json.loads(capsys.readouterr().out)
    assert rc == 2 and out["overall"] == "BLOCKED" and out["checks"][0]["id"] == "capture.exception"


def test_root_ingress_fails(env):
    _, argv = env
    i = argv.index("--ingress-uid")
    root_argv = argv[:i] + ["--ingress-uid", "0"] + argv[i + 2:]
    if CLIENT == 0:
        pytest.skip("n/a")
    assert _st(_run(root_argv), "identity.ingress_not_root") == "FAIL"
    assert _st(_run(argv + ["--ingress-uid", "30033"]), "identity.ingress_not_root") == "PASS"


def test_identity_range_and_missing_validation(env):
    _, argv = env
    assert _st(_run(argv + ["--client-uid", "-5"]), "identity.declared") == "FAIL"
    assert _st(_run(argv + ["--client-gid", "4294967295"]), "identity.declared") == "FAIL"
    i = argv.index("--ingress-gid")
    assert _st(_run(argv[:i] + argv[i + 2:]), "identity.declared") == "BLOCKED"


@pytest.mark.parametrize("pin", ["noequals", "=abc1234", "name=", "name=XYZ", "name=abc"])
def test_malformed_pin_fails(env, pin):
    _, argv = env
    assert _st(_run(argv + ["--pin", pin]), "configuration.pins_and_manifests") == "FAIL"


def test_pin_digest_compared_with_manifest_and_unverified_pins_block(env):
    tmp, argv = env
    good = hashlib.sha256(b"{}").hexdigest()
    a = argv + ["--pin", "manifest_sha256.manifest.json=" + good]
    assert _st(_run(a), "configuration.pins_and_manifests") == "PASS"
    assert _st(_run(a + ["--pin", "manifest_sha256.manifest.json=" + "0" * 64]), "configuration.pins_and_manifests") == "FAIL"
    no_accept = [x for x in a if x != "--accept-unverified-pins"]
    assert _st(_run(no_accept), "configuration.pins_and_manifests") == "BLOCKED"
    rec = _run(a)
    assert rec["configuration"]["pins_unverified"] == ["control_plane"]


def test_journal_mode_value_validated(env):
    _, argv = env
    i = argv.index("--journal-mode")
    bad = argv[:i] + ["--journal-mode", "bogus"] + argv[i + 2:]
    assert _st(_run(bad), "configuration.journal_mode") == "FAIL"


def test_configuration_values_come_from_the_scan_not_constants(env, tmp_path):
    _, argv = env
    root = tmp_path / "repo"
    (root / "tools/mvp_ingress").mkdir(parents=True)
    (root / "tools/mvp_ingress/core.py").write_text("f(simulate=x)\n")
    (root / "tools/mvp_ingress/synthetic_host.py").write_text("g(operation_identity=False)\n")
    (root / "tools/mvp_ingress/client.py").write_text("def submit():\n    pass\n")
    cfg = _run(argv + ["--repo-root", str(root)])["configuration"]
    assert cfg["simulate"] == "NOT_ESTABLISHED" and cfg["operation_identity"] == "NOT_ESTABLISHED"
    cfg = _run(argv)["configuration"]
    assert cfg["simulate"] == "fixed_none_by_static_scan"


@pytest.mark.parametrize("mode", [0o770, 0o720])
def test_ancestor_group_writable_fails(tmp_path, mode):
    s, argv = _env(tmp_path)
    os.chmod(tmp_path / "sock", mode)
    assert _st(_run(argv), "filesystem.ancestors_not_writable_by_others") == "FAIL"
    s.close()


def test_pin_name_may_contain_slash_for_source_paths(env):
    _, argv = env
    dig = hashlib.sha256(open(os.path.join(mod.parser().get_default("repo_root"), "tools/mvp_ingress/core.py"), "rb").read()).hexdigest()
    a = argv + ["--pin", "source_sha256.tools/mvp_ingress/core.py=" + dig]
    assert _st(_run(a), "configuration.pins_and_manifests") == "PASS"
    wrong = argv + ["--pin", "source_sha256.tools/mvp_ingress/core.py=" + "1" * 64]
    assert _st(_run(wrong), "configuration.pins_and_manifests") == "FAIL"


def test_wrong_manifest_digest_alone_fails(env):
    _, argv = env
    a = argv + ["--pin", "manifest_sha256.manifest.json=" + "0" * 64]
    assert _st(_run(a), "configuration.pins_and_manifests") == "FAIL"


def test_manifests_with_same_base_name_are_rejected(env, tmp_path):
    _, argv = env
    d = tmp_path / "other"
    d.mkdir()
    (d / "manifest.json").write_text("{\"x\": 1}")
    assert _st(_run(argv + ["--manifest", str(d / "manifest.json")]), "configuration.pins_and_manifests") == "FAIL"


# ---- architect rulings #2 item 4 ---------------------------------------------------------------------------------

def _sp(argv):
    return argv[argv.index("--socket") + 1]


def test_socket_0660_dedicated_group_exact_membership_passes(env):
    _, argv = env
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "PASS"


def test_socket_mode_variants_fail(tmp_path):
    for mode in (0o666, 0o600, 0o640, 0o770, 0o664):
        sub = tmp_path / ("m%o" % mode)
        sub.mkdir()
        s, argv = _env(sub, sock_mode=mode)
        assert _st(_run(argv), "ipc.socket_mode_owner_group") == "FAIL", oct(mode)
        s.close()


def test_socket_extra_or_missing_group_member_fails(env, monkeypatch):
    _, argv = env
    monkeypatch.setattr(mod, "_group_members", lambda g: ["ingr", "cli", "mallory"])
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "FAIL"
    monkeypatch.setattr(mod, "_group_members", lambda g: ["ingr"])
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "FAIL"


def test_socket_group_membership_includes_primary_gid_users(env, monkeypatch):
    _, argv = env
    real = mod._group_members.__wrapped__ if hasattr(mod._group_members, "__wrapped__") else None
    class P:  # a user whose primary gid is the dedicated group counts as a member
        def __init__(self, n, g): self.pw_name, self.pw_gid = n, g
    monkeypatch.undo()  # drop autouse patches, use the real function with fake pwd/grp
    monkeypatch.setattr(mod.pwd, "getpwall", lambda: [P("intruder", 4242)])
    monkeypatch.setattr(mod.grp, "getgrall", lambda: [types.SimpleNamespace(gr_gid=4242, gr_mem=["ingr", "cli"])])
    assert sorted(mod._group_members(4242)) == ["cli", "ingr", "intruder"]


def test_duplicate_gid_group_entries_are_unioned(monkeypatch):
    """getgrgid sees only the first /etc/group entry for a gid; a second entry with the same gid must still count."""
    monkeypatch.undo()
    entries = [types.SimpleNamespace(gr_gid=4242, gr_mem=["ingr", "cli"]), types.SimpleNamespace(gr_gid=7, gr_mem=["other"]),
               types.SimpleNamespace(gr_gid=4242, gr_mem=["mallory"])]
    monkeypatch.setattr(mod.grp, "getgrall", lambda: entries)
    monkeypatch.setattr(mod.grp, "getgrgid", lambda g: entries[0])
    monkeypatch.setattr(mod.pwd, "getpwall", lambda: [types.SimpleNamespace(pw_name="root", pw_gid=0)])
    assert mod._group_members(4242) == ["cli", "ingr", "mallory"]


def test_duplicate_gid_extra_member_fails_the_socket_check(env, monkeypatch):
    _, argv = env
    monkeypatch.setattr(mod, "_group_members", lambda g: ["cli", "ingr", "mallory"])
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "FAIL"


def test_non_enumerable_passwd_is_blocked(env, monkeypatch):
    monkeypatch.undo()
    monkeypatch.setattr(mod.pwd, "getpwall", lambda: [])
    monkeypatch.setattr(mod.grp, "getgrall", lambda: [])
    assert mod._group_members(4242) is None

    def boom():
        raise OSError("nss")
    monkeypatch.setattr(mod.pwd, "getpwall", boom)
    assert mod._group_members(4242) is None


def test_group_membership_none_makes_socket_check_blocked(env, monkeypatch):
    _, argv = env
    monkeypatch.setattr(mod, "_group_members", lambda g: None)
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "BLOCKED"


def _with(argv, flag, val):
    i = argv.index(flag)
    return argv[:i] + [flag, str(val)] + argv[i + 2:]


INGRESS_GID = 5555


@pytest.mark.parametrize("which", ["gid0", "ingress_primary", "client_primary"])
def test_socket_group_not_dedicated_fails(env, monkeypatch, which):
    """Membership is made exactly right for every gid, so only the dedicated-group rule can fail (it was masked before)."""
    _, argv = env
    argv = _with(argv, "--ingress-gid", INGRESS_GID)
    monkeypatch.setattr(mod, "_group_members", lambda g: ["ingr", "cli"])
    gid = {"gid0": 0, "ingress_primary": INGRESS_GID, "client_primary": CLIENT}[which]
    _fake_socket(monkeypatch, _sp(argv), gid=gid)
    rec = _run(argv)
    assert _st(rec, "ipc.socket_mode_owner_group") == "FAIL"
    assert "not a dedicated group" in next(c["detail"] for c in rec["checks"] if c["id"] == "ipc.socket_mode_owner_group")
    _fake_socket(monkeypatch, _sp(argv), gid=DEDICATED_GID)
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "PASS"  # control: same membership, dedicated gid


def test_socket_owned_by_client_fails(env, monkeypatch):
    _, argv = env
    _fake_socket(monkeypatch, _sp(argv), uid=CLIENT)
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "FAIL"


def test_socket_group_without_passwd_names_is_blocked(env, monkeypatch):
    _, argv = env
    monkeypatch.setattr(mod, "_name_uid", lambda u: None)
    assert _st(_run(argv), "ipc.socket_mode_owner_group") == "BLOCKED"


def test_socket_inside_state_dir_fails(tmp_path):
    s, argv = _env(tmp_path)
    inner = tmp_path / "state" / "ipc"
    inner.mkdir(mode=0o700)
    s2 = socket.socket(socket.AF_UNIX)
    s2.bind(str(inner / "i.sock"))
    i = argv.index("--socket")
    argv = argv[:i] + ["--socket", str(inner / "i.sock")] + argv[i + 2:]
    assert _st(_run(argv), "ipc.directory_separate_and_protected") == "FAIL"
    s.close(); s2.close()


def test_ipc_directory_protection(tmp_path, monkeypatch):
    s, argv = _env(tmp_path)
    assert _st(_run(argv), "ipc.directory_separate_and_protected") == "PASS"
    for mode in (0o770, 0o720, 0o1777):
        os.chmod(tmp_path / "sock", mode)
        assert _st(_run(argv), "ipc.directory_separate_and_protected") == "FAIL", oct(mode)
    os.chmod(tmp_path / "sock", 0o755)
    real = os.lstat
    d = str(tmp_path / "sock")

    def fake(path, *a, **k):
        st = real(path, *a, **k)
        if str(path) == d:
            return os.stat_result((st.st_mode, st.st_ino, st.st_dev, st.st_nlink, CLIENT, st.st_gid, st.st_size, 0, 0, 0))
        return st
    monkeypatch.setattr(mod.os, "lstat", fake)
    assert _st(_run(argv), "ipc.directory_separate_and_protected") == "FAIL"
    s.close()


@pytest.mark.parametrize("value,want,supported", [("0\n", "FAIL", False), ("1\n", "PASS", True), ("3\n", "PASS", True), (None, "BLOCKED", False)])
def test_ptrace_profile_supported_flag(env, monkeypatch, value, want, supported):
    _, argv = env
    real = mod._read
    monkeypatch.setattr(mod, "_read", lambda p: value if p.endswith("ptrace_scope") else real(p))
    rec = _run(argv)
    assert _st(rec, "isolation.ptrace_scope") == want and rec["profile_supported"] is supported
    if value is None:
        assert "UNSUPPORTED" in next(c["detail"] for c in rec["checks"] if c["id"] == "isolation.ptrace_scope")
        assert rec["overall"] != "PASS"


def _fake_proc(monkeypatch, pid=424242, uid=ME, capeff="0" * 16, capprm="0" * 16, cmdline="python -m tools.mvp_ingress.server"):
    real = mod._read
    status = "Uid:\t{0}\t{0}\t{0}\t{0}\nGid:\t1\t1\t1\t1\nGroups:\t1\nCapEff:\t{1}\nCapPrm:\t{2}\nCapBnd:\t{1}\nNoNewPrivs:\t1\nSeccomp:\t0\n".format(uid, capeff, capprm)

    def fake(path):
        if path == "/proc/%d/status" % pid:
            return status
        if path == "/proc/%d/cmdline" % pid:
            return cmdline.replace(" ", "\0")
        return real(path)
    monkeypatch.setattr(mod, "_read", fake)
    monkeypatch.setattr(mod, "_proc_exe", lambda p: os.path.realpath(mod.sys.executable))
    monkeypatch.setattr(mod, "_proc_owner", lambda p: ME)
    return pid


def test_ingress_capabilities_must_be_empty(env, monkeypatch):
    _, argv = env
    pid = _fake_proc(monkeypatch)
    assert _st(_run(argv + ["--ingress-pid", str(pid)]), "isolation.ingress_capabilities") == "PASS"
    for name, bit in (("CAP_SYS_PTRACE", 19), ("CAP_DAC_OVERRIDE", 1), ("CAP_KILL", 5), ("CAP_SETUID", 7)):
        _fake_proc(monkeypatch, capeff="%016x" % (1 << bit))
        rec = _run(argv + ["--ingress-pid", str(pid)])
        assert _st(rec, "isolation.ingress_capabilities") == "FAIL"
        assert name in next(c["detail"] for c in rec["checks"] if c["id"] == "isolation.ingress_capabilities")
    _fake_proc(monkeypatch, capprm="%016x" % (1 << 7))
    assert _st(_run(argv + ["--ingress-pid", str(pid)]), "isolation.ingress_capabilities") == "FAIL"
    assert _st(_run(argv), "isolation.ingress_capabilities") == "BLOCKED"


def test_ingress_dumpability(env, monkeypatch):
    _, argv = env
    pid = _fake_proc(monkeypatch)
    a = argv + ["--ingress-pid", str(pid)]
    rec = _run(a)
    assert _st(rec, "isolation.ingress_dumpability") == "PASS"
    d = next(c["detail"] for c in rec["checks"] if c["id"] == "isolation.ingress_dumpability")
    assert "dump-owner consistent" in d and "client_denied_ingress_process" in d
    monkeypatch.setattr(mod, "_proc_owner", lambda p: 0)
    assert _st(_run(a), "isolation.ingress_dumpability") == "PASS"
    monkeypatch.setattr(mod, "_proc_owner", lambda p: ME + 77)
    assert _st(_run(a), "isolation.ingress_dumpability") == "FAIL"
    monkeypatch.setattr(mod, "_proc_owner", lambda p: None)
    assert _st(_run(a), "isolation.ingress_dumpability") == "BLOCKED"
    assert _st(_run(argv), "isolation.ingress_dumpability") == "BLOCKED"


def test_ingress_command_line_identity(env, monkeypatch):
    _, argv = env
    pid = _fake_proc(monkeypatch)
    assert _st(_run(argv + ["--ingress-pid", str(pid)]), "identity.ingress_command") == "PASS"
    _fake_proc(monkeypatch, cmdline="python -m http.server")
    assert _st(_run(argv + ["--ingress-pid", str(pid)]), "identity.ingress_command") == "FAIL"
    assert _st(_run(argv), "identity.ingress_command") == "BLOCKED"


def test_outsider_must_be_an_outsider(env):
    _, argv = env
    assert _st(_run(argv + ["--outsider-uid", str(CLIENT)]), "qualification.outsider_denied_socket") == "FAIL"
    assert _st(_run(argv + ["--outsider-uid", str(ME)]), "qualification.outsider_denied_socket") == "FAIL"


def test_not_root_blocks_peer_and_outsider_checks(env, monkeypatch):
    _, argv = env
    monkeypatch.setattr(mod.os, "geteuid", lambda: 1000)
    rec = _run(argv)
    assert _st(rec, "ipc.peer_credentials") == "BLOCKED" and _st(rec, "qualification.outsider_denied_socket") == "BLOCKED"


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_root_peer_credentials_and_outsider(env):
    tmp, argv = env
    _open_path_to(tmp)
    sp = _sp(argv)
    os.chown(sp, 0, CLIENT)  # real group = the client's group: the client can connect, an outsider cannot
    rec = _run(argv + ["--ingress-pid", str(os.getpid())])
    assert _st(rec, "qualification.client_socket_reachable") == "PASS"
    assert _st(rec, "qualification.outsider_denied_socket") == "PASS"
    assert _st(rec, "ipc.peer_credentials") == "PASS"
    # wrong ingress pid: the credentials of the listener do not match
    rec = _run(argv + ["--ingress-pid", "1"])
    assert _st(rec, "ipc.peer_credentials") == "FAIL"
    # right pid, wrong declared uid or gid
    for flag in ("--ingress-uid", "--ingress-gid"):
        i = argv.index(flag)
        wrong = argv[:i] + [flag, "4321"] + argv[i + 2:] + ["--ingress-pid", str(os.getpid())]
        assert _st(_run(wrong), "ipc.peer_credentials") == "FAIL", flag


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_root_outsider_allowed_when_socket_is_world_connectable(env):
    tmp, argv = env
    _open_path_to(tmp)
    os.chmod(_sp(argv), 0o666)
    os.chown(_sp(argv), 0, CLIENT)
    assert _st(_run(argv), "qualification.outsider_denied_socket") == "FAIL"


# ---- review round 2: outsider conclusiveness, label, sticky ancestors
@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_root_outsider_stopped_by_ipc_directory_is_blocked_not_pass(env):
    tmp, argv = env
    _open_path_to(tmp)
    os.chown(_sp(argv), 0, CLIENT)
    os.chmod(tmp / "sock", 0o750)  # the outsider cannot traverse the IPC directory
    rec = _run(argv)
    assert _st(rec, "qualification.outsider_denied_socket") == "BLOCKED"
    assert "not conclusive for the socket" in next(c["detail"] for c in rec["checks"] if c["id"] == "qualification.outsider_denied_socket")
    assert _st(rec, "qualification.outsider_denied_by_ipc_directory") == "PASS"
    assert rec["qualification_outsider_probe"]["traversal_blocked_above_socket"]


@pytest.mark.skipif(os.geteuid() != 0, reason="client probe drops privileges and needs root")
def test_root_outsider_traversable_dir_has_no_directory_check(env):
    tmp, argv = env
    _open_path_to(tmp)
    os.chown(_sp(argv), 0, CLIENT)
    rec = _run(argv)
    assert _st(rec, "qualification.outsider_denied_socket") == "PASS"
    assert all(c["id"] != "qualification.outsider_denied_by_ipc_directory" for c in rec["checks"])


def test_evidence_label_is_required(env):
    _, argv = env
    for a in (argv, argv + ["--label", "   "]):
        rec = _run(a)
        assert _st(rec, "capture.evidence_label") == "BLOCKED" and rec["overall"] != "PASS" and "evidence_label" not in rec
    rec = _run(argv + ["--label", "development container; NOT the qualification host; example manifest; boundary unqualified"])
    assert _st(rec, "capture.evidence_label") == "PASS" and rec["evidence_label"].startswith("development container")


def test_label_does_not_rescue_a_failing_record(tmp_path):
    s, argv = _env(tmp_path, sock_mode=0o666)
    assert _run(argv + ["--label", "x"])["overall"] == "FAIL"
    s.close()


def test_sticky_ancestor_exemption_is_root_owned_and_non_direct_only(tmp_path, monkeypatch):
    s, argv = _env(tmp_path)
    os.chmod(tmp_path / "sock", 0o1777)  # direct parent of the socket: no sticky excuse
    assert _st(_run(argv), "filesystem.ancestors_not_writable_by_others") == "FAIL"
    os.chmod(tmp_path / "sock", 0o755)
    real = os.lstat
    up = str(tmp_path.parent)  # tmp_path itself directly holds the state dir

    def fake(owner):
        def f(path, *a, **k):
            st = real(path, *a, **k)
            if str(path) == up:
                return os.stat_result(((st.st_mode & ~0o7777) | 0o1777, st.st_ino, st.st_dev, st.st_nlink, owner, st.st_gid, st.st_size, 0, 0, 0))
            return st
        return f
    monkeypatch.setattr(mod.os, "lstat", fake(0))
    assert _st(_run(argv), "filesystem.ancestors_not_writable_by_others") == "PASS"
    monkeypatch.setattr(mod.os, "lstat", fake(ME + 1000))  # sticky but not root-owned (and not the ingress uid)
    assert _st(_run(argv), "filesystem.ancestors_not_writable_by_others") == "FAIL"
    s.close()


def test_sticky_ancestor_owned_by_ingress_uid_still_fails(tmp_path, monkeypatch):
    """Sticky non-direct ancestor owned by the ingress uid (an allowed owner) is excused only if root-owned."""
    s, argv = _env(tmp_path)
    argv = _with(argv, "--ingress-uid", 30033)  # non-root, so owner == ingress uid is distinct from root
    real = os.lstat
    up = str(tmp_path.parent)

    def f(path, *a, **k):
        st = real(path, *a, **k)
        if str(path) == up:
            return os.stat_result(((st.st_mode & ~0o7777) | 0o1777, st.st_ino, st.st_dev, st.st_nlink, 30033, st.st_gid, st.st_size, 0, 0, 0))
        return st
    monkeypatch.setattr(mod.os, "lstat", f)
    rec = _run(argv)
    assert _st(rec, "filesystem.ancestors_not_writable_by_others") == "FAIL"
    s.close()
