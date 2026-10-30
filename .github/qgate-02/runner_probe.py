#!/usr/bin/env python3
"""OCS-MVP-QGATE-02 / D2: non-effecting, synthetic observation of a GitHub-hosted runner.

SPDX-License-Identifier: Apache-2.0

Purpose: record, as raw observations, whether the host properties the ORIGINAL OCS Linux host profile requires
(docs/mvp-recovery/ingress-qualification-environment-profile.md) can be observed or satisfied on this runner. It is NOT the
accepted capture script (tools/mvp_env_record/capture_env_record.py, which the workflow also invokes unmodified), it does not
start the real ingress, it never changes a sysctl or any security policy, it uses only numeric uids/gids in a throwaway
directory that it removes, and it never contacts the network or touches credentials. Standard library only.

It makes NO pass/fail/qualification judgement about the host. Each observation carries one of OBSERVED / ERROR /
NOT_OBSERVED. The feasibility verdict is derived separately, by a person, from the raw record.
"""
import ctypes
import errno
import hashlib
import json
import os
import platform
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time

BASE = "/opt/qgate02-probe"
ING_UID, ING_GID = 61001, 61001
CLI_UID, CLI_GID = 61002, 61002
OUT_UID, OUT_GID = 61003, 61003
WRONG_UID, WRONG_GID = 61004, 61004      # member of the IPC group but not on the allowlist
YAMA_UID, YAMA_GID = 61005, 61005
IPC_GID = 61010                          # the "dedicated group"; deliberately has no /etc/group entry
ENV_WHITELIST = ("GITHUB_RUN_ID", "GITHUB_RUN_NUMBER", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA", "GITHUB_REF", "GITHUB_REPOSITORY",
                 "GITHUB_WORKFLOW", "GITHUB_WORKFLOW_REF", "GITHUB_WORKFLOW_SHA", "GITHUB_EVENT_NAME", "GITHUB_JOB",
                 "GITHUB_SERVER_URL", "RUNNER_OS", "RUNNER_ARCH", "RUNNER_ENVIRONMENT", "RUNNER_NAME", "ImageOS", "ImageVersion")

OBS = {}


def rec(key, value, status="OBSERVED"):
    OBS[key] = {"status": status, "value": value}


def err(e):
    return "%s:%s" % (errno.errorcode.get(getattr(e, "errno", None) or 0, "E?"), e)


def readf(path, limit=65536):
    try:
        with open(path, "rb") as f:
            return f.read(limit).decode("utf-8", "replace")
    except OSError as e:
        return {"error": err(e)}


def run(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"cmd": cmd, "rc": p.returncode, "stdout": p.stdout[-8000:], "stderr": p.stderr[-2000:]}
    except (OSError, subprocess.SubprocessError) as e:
        return {"cmd": cmd, "error": "%s: %s" % (type(e).__name__, e)}


def status_fields(pid="self"):
    out = {}
    t = readf("/proc/%s/status" % pid)
    if isinstance(t, dict):
        return t
    for line in t.splitlines():
        k, _, v = line.partition(":")
        if k in ("Uid", "Gid", "Groups", "CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb", "NoNewPrivs", "Seccomp", "Name"):
            out[k] = v.strip()
    return out


def sha256_file(p):
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(65536), b""):
                h.update(b)
        return h.hexdigest()
    except OSError as e:
        return "ERROR " + err(e)


# ---------------------------------------------------------------- platform / provenance
def observe_platform():
    rec("provenance.env", {k: os.environ.get(k) for k in ENV_WHITELIST})
    osr = {}
    t = readf("/etc/os-release")
    if isinstance(t, str):
        for line in t.splitlines():
            if "=" in line:
                k, _, v = line.partition("=")
                osr[k] = v.strip('"')
    rec("platform.os_release", osr)
    u = os.uname()
    rec("platform.uname", {"sysname": u.sysname, "release": u.release, "version": u.version, "machine": u.machine})
    rec("platform.proc_version", readf("/proc/version"))
    rec("platform.python", {"version": sys.version, "executable": sys.executable, "sqlite": __import__("sqlite3").sqlite_version})
    rec("platform.virt", run(["systemd-detect-virt"]))
    rec("platform.container_markers", {"dockerenv": os.path.exists("/.dockerenv"), "cgroup": readf("/proc/1/cgroup", 2000)})
    rec("platform.python_candidates", {
        "which": {n: shutil.which(n) for n in ("python3", "python3.13", "python3.12", "setpriv", "getfacl", "setfacl", "sudo")},
        "hostedtoolcache_python": sorted(os.listdir("/opt/hostedtoolcache/Python")) if os.path.isdir("/opt/hostedtoolcache/Python") else None})


def observe_security():
    yama_dir = "/proc/sys/kernel/yama"
    rec("security.yama_dir_listing", sorted(os.listdir(yama_dir)) if os.path.isdir(yama_dir) else {"error": "absent"})
    ps = readf(yama_dir + "/ptrace_scope")
    rec("security.yama_ptrace_scope", ps.strip() if isinstance(ps, str) else ps, "OBSERVED" if isinstance(ps, str) else "NOT_OBSERVED")
    for name, p in (("lsm_list", "/sys/kernel/security/lsm"), ("userns_apparmor_restrict", "/proc/sys/kernel/apparmor_restrict_unprivileged_userns"),
                    ("userns_clone", "/proc/sys/kernel/unprivileged_userns_clone"), ("max_user_namespaces", "/proc/sys/user/max_user_namespaces"),
                    ("unprivileged_bpf_disabled", "/proc/sys/kernel/unprivileged_bpf_disabled"), ("kptr_restrict", "/proc/sys/kernel/kptr_restrict"),
                    ("protected_symlinks", "/proc/sys/fs/protected_symlinks"), ("protected_hardlinks", "/proc/sys/fs/protected_hardlinks"),
                    ("lsm_current", "/proc/self/attr/current")):
        v = readf(p)
        rec("security." + name, v.strip() if isinstance(v, str) else v, "OBSERVED" if isinstance(v, str) else "NOT_OBSERVED")
    rec("process.self_status", status_fields())
    rec("process.self_id", {"uid": os.getuid(), "euid": os.geteuid(), "gid": os.getgid(), "groups": os.getgroups()})
    rec("process.sudo_noninteractive", run(["sudo", "-n", "true"]))


# ---------------------------------------------------------------- filesystem
def mount_for(path):
    best = None
    real = os.path.realpath(path)
    for line in (readf("/proc/self/mountinfo") if isinstance(readf("/proc/self/mountinfo"), str) else "").splitlines():
        f = line.split()
        if " - " not in line or len(f) < 10:
            continue
        mp = f[4].replace("\\040", " ")
        if real == mp or real.startswith(mp.rstrip("/") + "/"):
            if best is None or len(mp) >= len(best["mount_point"]):
                i = f.index("-")
                best = {"mount_point": mp, "mount_options": f[5], "fstype": f[i + 1], "source": f[i + 2], "super_options": f[i + 3]}
    return best


def observe_filesystem():
    rec("filesystem.mount_base", mount_for(os.path.dirname(BASE)))
    rec("filesystem.mount_tmp", mount_for("/tmp"))
    rec("filesystem.mount_workspace", mount_for(os.getcwd()))


def observe_acl_positive_control():
    """Positive xattr/ACL capability probe on a throwaway file (the accepted capture script has none, by its own caveat)."""
    p = os.path.join(BASE, "acl-control.txt")
    with open(p, "w") as f:
        f.write("x")
    res = {"setfacl_present": shutil.which("setfacl") is not None}
    try:
        os.setxattr(p, "user.qgate02", b"1")
        res["user_xattr_set"] = True
    except OSError as e:
        res["user_xattr_set"] = err(e)
    if res["setfacl_present"]:
        res["setfacl"] = run(["setfacl", "-m", "u:%d:r" % CLI_UID, p])
        try:
            res["listxattr_after"] = sorted(os.listxattr(p, follow_symlinks=False))
        except OSError as e:
            res["listxattr_after"] = err(e)
    rec("filesystem.acl_positive_control", res)


# ---------------------------------------------------------------- identity / IPC (numeric ids only, nothing added to /etc)
def drop_to(uid, gid, groups):
    os.setgroups(groups)
    os.setresgid(gid, gid, gid)
    os.setresuid(uid, uid, uid)


def child(fn, uid, gid, groups, *a):
    """Fork; in the child drop to (uid, gid, groups), run fn, write one JSON object to a pipe. Returns (pid, readfile)."""
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        signal.alarm(30)
        out = {}
        try:
            drop_to(uid, gid, groups)
            out["identity"] = {"uid": os.getuid(), "euid": os.geteuid(), "gid": os.getgid(), "groups": os.getgroups(), "status": status_fields()}
            out["result"] = fn(*a)
        except BaseException as e:   # noqa: BLE001 - probe must always report
            out["exception"] = "%s: %s" % (type(e).__name__, e)
        os.write(w, json.dumps(out, default=str).encode())
        os._exit(0)
    os.close(w)
    return pid, os.fdopen(r, "r")


def collect(pid, rf):
    data = rf.read()
    _, st = os.waitpid(pid, 0)
    try:
        d = json.loads(data) if data else {"exception": "no output"}
    except ValueError:
        d = {"exception": "unparseable", "raw": data[:500]}
    d["wait_status"] = st
    return d


def ingress_main(sock_path, state_dir, allow, nreq):
    os.makedirs(state_dir, mode=0o700, exist_ok=True)
    os.chmod(state_dir, 0o700)
    with open(os.path.join(state_dir, "ledger.db"), "w") as f:
        f.write("synthetic")
    os.chmod(os.path.join(state_dir, "ledger.db"), 0o600)
    try:
        ctypes.CDLL(None, use_errno=True).prctl(38, 1, 0, 0, 0)  # PR_SET_NO_NEW_PRIVS (restricts only; changes no policy)
    except OSError:
        pass
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(sock_path)
    os.chmod(sock_path, 0o660)
    s.listen(4)
    s.settimeout(20)
    st = os.stat(sock_path)
    ready = {"pid": os.getpid(), "socket_mode": oct(st.st_mode & 0o7777), "socket_uid": st.st_uid, "socket_gid": st.st_gid,
             "status": status_fields(), "peer_log": []}
    # tell the parent we are ready through a marker file inside the IPC dir's parent (parent polls)
    with open(sock_path + ".ready", "w") as f:
        json.dump({"pid": os.getpid()}, f)
    for _ in range(nreq):
        try:
            c, _a = s.accept()
        except socket.timeout:
            ready["peer_log"].append({"accept": "timeout"})
            break
        c.settimeout(5)
        pid, uid, gid = struct.unpack("3i", c.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
        verdict = "accepted" if uid in allow else "refused_not_allowlisted"
        ready["peer_log"].append({"peer_pid": pid, "peer_uid": uid, "peer_gid": gid, "verdict": verdict})
        try:
            c.sendall(verdict.encode())
        except OSError:
            pass
        c.close()
    return ready


def client_main(sock_path, state_dir, ingress_pid, label):
    res = {"label": label}
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(sock_path)
        s.sendall(b"hello")
        res["connect"] = "connected"
        res["reply"] = s.recv(64).decode()
        res["own_pid"] = os.getpid()
    except OSError as e:
        res["connect"] = err(e)
    for name, fn in (("listdir_state", lambda: os.listdir(state_dir)), ("open_state_file", lambda: open(os.path.join(state_dir, "ledger.db")).close()),
                     ("open_proc_mem", lambda: os.open("/proc/%d/mem" % ingress_pid, os.O_RDONLY)),
                     ("open_proc_environ", lambda: os.open("/proc/%d/environ" % ingress_pid, os.O_RDONLY)),
                     ("kill_0_ingress", lambda: os.kill(ingress_pid, 0))):
        try:
            fn()
            res[name] = "ALLOWED"
        except OSError as e:
            res[name] = err(e)
    libc = ctypes.CDLL(None, use_errno=True)
    libc.ptrace.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p]
    libc.ptrace.restype = ctypes.c_long
    ctypes.set_errno(0)
    r = libc.ptrace(16, ingress_pid, None, None)     # PTRACE_ATTACH on a different-uid process
    res["ptrace_attach_ingress"] = "ATTACHED(unexpected)" if r == 0 else errno.errorcode.get(ctypes.get_errno(), "E?")
    if r == 0:
        libc.ptrace(17, ingress_pid, None, None)
    return res


def observe_ipc():
    ipc = os.path.join(BASE, "ipc")
    state = os.path.join(BASE, "state")
    os.makedirs(BASE, mode=0o755, exist_ok=True)
    os.chmod(BASE, 0o755)
    os.mkdir(ipc)
    os.chown(ipc, ING_UID, IPC_GID)
    os.chmod(ipc, 0o2750)                              # setgid so the socket inherits the dedicated group (profile: IPC dir 2750)
    os.mkdir(state)
    os.chown(state, ING_UID, ING_GID)
    os.chmod(state, 0o700)
    sock = os.path.join(ipc, "ingress.sock")
    st = os.stat(ipc)
    chain, p = [], os.path.realpath(ipc)
    while True:
        s = os.stat(p)
        chain.append({"path": p, "mode": oct(s.st_mode & 0o7777), "uid": s.st_uid, "gid": s.st_gid,
                      "group_or_other_writable": bool(s.st_mode & 0o022), "sticky": bool(s.st_mode & 0o1000)})
        if p == "/":
            break
        p = os.path.dirname(p)
    rec("ipc.directory_created", {"mode": oct(st.st_mode & 0o7777), "uid": st.st_uid, "gid": st.st_gid, "ancestor_chain": chain})
    # NOTE: ingress child must be able to write into ipc (owner), and the ready marker must be readable by root parent.
    ipid, irf = child(ingress_main, ING_UID, ING_GID, [IPC_GID], sock, state, {CLI_UID}, 2)
    ready = None
    for _ in range(100):
        if os.path.exists(sock + ".ready"):
            ready = json.load(open(sock + ".ready"))
            break
        time.sleep(0.1)
    if not ready:
        rec("ipc.ingress_stand_in", {"error": "stand-in server did not become ready"}, "ERROR")
        os.kill(ipid, signal.SIGKILL)
        collect(ipid, irf)
        return
    pid = ready["pid"]
    roles = {}
    for label, uid, gid, groups in (("outsider", OUT_UID, OUT_GID, []), ("designated_client", CLI_UID, CLI_GID, [IPC_GID]),
                                    ("group_member_not_allowlisted", WRONG_UID, WRONG_GID, [IPC_GID])):
        cp, crf = child(client_main, uid, gid, groups, sock, state, pid, label)
        roles[label] = collect(cp, crf)
    ing = collect(ipid, irf)
    rec("ipc.stand_in_ingress", ing)
    rec("ipc.client_roles", roles)
    try:
        ss = os.stat(sock)
        rec("ipc.socket_final_stat", {"mode": oct(ss.st_mode & 0o7777), "uid": ss.st_uid, "gid": ss.st_gid})
    except OSError as e:
        rec("ipc.socket_final_stat", err(e), "ERROR")


def yama_target():
    time.sleep(8)
    return {}


def yama_tracer(target_pid):
    libc = ctypes.CDLL(None, use_errno=True)
    libc.ptrace.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p]
    libc.ptrace.restype = ctypes.c_long
    ctypes.set_errno(0)
    r = libc.ptrace(16, target_pid, None, None)
    e = ctypes.get_errno()
    out = {"attach_rc": r, "errno": errno.errorcode.get(e, e) if r != 0 else 0}
    if r == 0:
        try:
            os.waitpid(target_pid, 0)
        except OSError:
            pass
        libc.ptrace(17, target_pid, None, None)
    return out


def observe_yama_behaviour():
    """Behavioural check of Yama (not just its sysctl value): a same-uid, non-descendant process tries PTRACE_ATTACH on a sibling.
    Yama scope 1 denies this (EPERM); scope 0 or absent Yama permits it. Read-only observation; no policy is changed."""
    tp, trf = child(yama_target, YAMA_UID, YAMA_GID, [])
    time.sleep(0.5)
    xp, xrf = child(yama_tracer, YAMA_UID, YAMA_GID, [], tp)
    tracer = collect(xp, xrf)
    try:
        os.kill(tp, signal.SIGKILL)
    except OSError:
        pass
    collect(tp, trf)
    rec("security.yama_behaviour_same_uid_sibling_attach", tracer)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "qgate02-probe-record.json"
    rec("probe.script_sha256", sha256_file(os.path.abspath(__file__)))
    rec("probe.capture_script_sha256", sha256_file("tools/mvp_env_record/capture_env_record.py"))
    rec("probe.started_epoch", int(time.time()))
    try:
        observe_platform()
        observe_security()
        observe_filesystem()
        shutil.rmtree(BASE, ignore_errors=True)
        os.makedirs(BASE, mode=0o755)
        os.chmod(BASE, 0o755)
        for name, fn in (("acl", observe_acl_positive_control), ("ipc", observe_ipc), ("yama", observe_yama_behaviour)):
            try:
                fn()
            except BaseException as e:    # noqa: BLE001
                rec("probe.section_exception." + name, "%s: %s" % (type(e).__name__, e), "ERROR")
    finally:
        rec("probe.cleanup", "removed" if (shutil.rmtree(BASE, ignore_errors=True) or not os.path.exists(BASE)) else "FAILED")
    rec("probe.finished_epoch", int(time.time()))
    with open(out, "w") as f:
        json.dump(OBS, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: (v["status"]) for k, v in sorted(OBS.items())}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
