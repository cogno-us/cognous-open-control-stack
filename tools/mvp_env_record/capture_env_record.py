"""Qualification environment record capture for the MVP trusted-host ingress (standard library only, Python 3.13).

SPDX-License-Identifier: Apache-2.0

Emits a deterministic JSON record (sorted keys, no timestamps, no pids) of the platform, interpreter, process identity,
IPC, filesystem, invocation, isolation and configuration facts the architect's Qualification environment record requires,
and verifies the enforceable preconditions of the trusted-host boundary. Every check is PASS, FAIL or BLOCKED. A check that
cannot be performed (not root, tool or file missing, input not given, filesystem without xattr support) is BLOCKED, never
PASS. The overall status is FAIL if any check FAILs, else BLOCKED if any check is BLOCKED, else PASS.

Each live probe (the client probe and the outsider probe) opens one real connection to the ingress and consumes one accept,
so the ingress must be started with --max-requests large enough to cover them (at least 2 plus any other connections), or it
may exit before the capture finishes.

Non-authorizing. This is an environment capture and precondition verification, not a Qualification verdict, a security
clearance, a certification or a production-readiness claim. It does not claim resistance to root, to the ingress uid, to
same-privilege code or to direct database modification by an authorized file holder. Release stays on HOLD.

    python -m tools.mvp_ingress.capture_env_record --state-dir DIR --socket PATH --ingress-pid PID \
        --client-uid UID --client-gid GID --db DESTINATION.db --authority-store STORE --journal-mode wal \
        --label "development container; NOT the qualification host" --pin control_plane=0a41faa9 --pin runtime=ec728da6 --manifest MANIFEST.json
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import errno
import grp
import hashlib
import importlib.metadata as md
import json
import os
import platform
import pwd
import shutil
import socket
import struct
import stat
import subprocess
import sys

SCHEMA = "mvp-ingress-env-record/1"
PASS, FAIL, BLOCKED = "PASS", "FAIL", "BLOCKED"
ACL_XATTRS = ("system.posix_acl_access", "system.posix_acl_default")
JOURNAL_MODES = ("wal", "delete", "truncate", "persist")
ENFORCEABLE_FS = {"ext4", "xfs", "btrfs", "tmpfs"}
NO_UNIX_PERMS_FS = {"vfat", "exfat", "ntfs", "ntfs3", "9p", "virtiofs", "nfs", "nfs4", "cifs", "smb3", "fuseblk", "fuse",
                    "iso9660", "squashfs"}
CAP_DAC_OVERRIDE, CAP_DAC_READ_SEARCH, CAP_KILL, CAP_SYS_PTRACE = 1, 2, 5, 19
SOCKET_MODE = 0o660
PRIVILEGED_CAPS = {"CAP_CHOWN": 0, "CAP_DAC_OVERRIDE": 1, "CAP_DAC_READ_SEARCH": 2, "CAP_FOWNER": 3, "CAP_SETGID": 6, "CAP_SETUID": 7,
                   "CAP_KILL": 5, "CAP_SYS_PTRACE": 19, "CAP_SYS_ADMIN": 21}
PTRACE_CAPS = {"CAP_DAC_OVERRIDE": CAP_DAC_OVERRIDE, "CAP_DAC_READ_SEARCH": CAP_DAC_READ_SEARCH, "CAP_KILL": CAP_KILL,
               "CAP_SYS_PTRACE": CAP_SYS_PTRACE}


def _chk(cid, status, detail, **data):
    return {"id": cid, "status": status, "detail": detail, "data": data}


@contextlib.contextmanager
def _section(checks, name):
    """Fail closed: any exception inside a section becomes a BLOCKED check naming the exception type."""
    try:
        yield
    except Exception as exc:  # noqa: BLE001
        checks.append(_chk("%s.exception" % name, BLOCKED, "section raised %s; its checks are incomplete" % type(exc).__name__))


def untraversable_for(path, uid, groups):
    """Ancestor directories of ``path`` (``path`` itself is not examined) where the client lacks search (x) permission,
    judged from owner/group/other mode bits only (POSIX ACLs are rejected by a separate check)."""
    bad = []
    for d in reversed(ancestors(path)):
        st = os.lstat(d)
        bit = 0o100 if st.st_uid == uid else 0o010 if st.st_gid in groups else 0o001
        if not st.st_mode & bit:
            bad.append(d)
    return bad


def _proc_exe(pid):
    try:
        return os.path.realpath(os.readlink("/proc/%d/exe" % pid))
    except OSError:
        return None


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for part in iter(lambda: f.read(1 << 16), b""):
            h.update(part)
    return h.hexdigest()


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def _stat_row(path):
    try:
        st = os.lstat(path)
    except OSError as exc:
        return {"path": path, "error": errno.errorcode.get(exc.errno, str(exc.errno))}
    return {"path": path, "type": {stat.S_IFDIR: "dir", stat.S_IFREG: "file",
            stat.S_IFSOCK: "socket", stat.S_IFLNK: "symlink"}.get(stat.S_IFMT(st.st_mode), "other"),
            "mode": format(stat.S_IMODE(st.st_mode), "04o"), "uid": st.st_uid, "gid": st.st_gid}


def _name_uid(uid):
    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError:
        return None


def _group_members(gid):
    """Names that hold group ``gid``: supplementary members of EVERY /etc/group entry carrying that gid (getgrgid sees only
    the first of duplicate-gid entries) plus users whose primary group it is. Returns None, so the caller reports BLOCKED,
    when passwd cannot be enumerated (getpwall raises or is empty). Limit: only what the NSS getgrall/getpwall calls
    enumerate; a directory service that does not enumerate (for example LDAP/SSSD without enumeration) is invisible and the
    result is then not exact, so the profile expects local /etc/passwd and /etc/group."""
    names = set()
    for g in grp.getgrall():
        if g.gr_gid == gid:
            names.update(g.gr_mem)
    try:
        pw = pwd.getpwall()
    except Exception:  # noqa: BLE001
        return None
    if not pw:
        return None
    names.update(p.pw_name for p in pw if p.pw_gid == gid)
    return sorted(names)


def parse_status(text):
    out = {}
    for line in (text or "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def cap_names(hexmask):
    m = int(hexmask, 16)
    return sorted(n for n, b in {**PTRACE_CAPS, **PRIVILEGED_CAPS}.items() if m >> b & 1)


def mountinfo(path):
    """Return (mount point, fstype, options, super options) of the mount holding ``path`` (longest prefix), or None."""
    text = _read("/proc/self/mountinfo")
    if text is None:
        return None
    real, best = os.path.realpath(path), None
    for line in text.splitlines():
        left, _, right = line.partition(" - ")
        f, r = left.split(), right.split()
        if len(f) < 6 or len(r) < 3:
            continue
        mp = f[4].encode().decode("unicode_escape")
        if real == mp or real.startswith(mp.rstrip("/") + "/") or mp == "/":
            if best is None or len(mp) >= len(best[0]):
                best = (mp, r[0], f[5], r[2])
    return best


def ancestors(path):
    cur, out = os.path.dirname(os.path.realpath(path)), []
    while True:
        out.append(cur)
        if cur == os.path.dirname(cur):
            return out
        cur = os.path.dirname(cur)


def acl_state(path):
    """('none'|'present'|'unreadable', detail). Reads the POSIX ACL xattr names without following symlinks."""
    try:
        names = os.listxattr(path, follow_symlinks=False)
    except OSError as exc:
        return "unreadable", errno.errorcode.get(exc.errno, str(exc.errno))
    hit = sorted(n for n in names if n in ACL_XATTRS)
    return ("present", ",".join(hit)) if hit else ("none", "")


def walk_tree(state_dir):
    out = [state_dir]
    for root, dirs, files in os.walk(state_dir, followlinks=False):
        out.extend(os.path.join(root, n) for n in sorted(dirs) + sorted(files))
    return sorted(set(out))


def _proc_owner(pid):
    """Owner uid of /proc/<pid>: the process uid if dumpable, root if the process is non-dumpable. None if unreadable."""
    try:
        return os.stat("/proc/%d" % pid).st_uid
    except OSError:
        return None


def client_probe(args, paths, uid=None, gid=None, role="client"):
    """Drop to a uid/gid in a child (root only) and run access probes. role "client": the designated client, full probe;
    role "outsider": an unrelated uid, socket connect only. Returns (status, results)."""
    uid = args.client_uid if uid is None else uid
    gid = args.client_gid if gid is None else gid
    if os.geteuid() != 0:
        return None, "not root: cannot drop to the client uid"
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        res = {}
        try:
            name = _name_uid(uid) if role == "client" else None
            groups = os.getgrouplist(name, gid) if name else [gid]
            os.setgroups(groups)
            os.setresgid(gid, gid, gid)
            os.setresuid(uid, uid, uid)
            res["groups"] = sorted(groups)
            res["capeff"] = parse_status(_read("/proc/self/status")).get("CapEff")

            def deny(label, fn):
                try:
                    fn()
                    res[label] = "allowed"
                except OSError as exc:
                    res[label] = "denied" if exc.errno in (errno.EACCES, errno.EPERM) else "error:" + errno.errorcode.get(exc.errno, "?")
            try:  # a real connection: SO_PEERCRED on the connecting side reports the credentials of the listener
                c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                c.settimeout(3)
                try:
                    c.connect(paths["socket"])
                    res["socket_connect"] = "connected"
                    res["peercred"] = list(struct.unpack("3i", c.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))))
                finally:
                    c.close()
            except OSError as exc:
                res["socket_connect"] = "denied" if exc.errno in (errno.EACCES, errno.EPERM) else "error:" + errno.errorcode.get(exc.errno, "?")
            if role == "outsider":
                raise SystemExit  # only the connect probe applies to an outsider
            deny("listdir_state_dir", lambda: os.listdir(paths["state_dir"]))
            deny("unlink_in_state_dir", lambda: os.unlink(os.path.join(paths["state_dir"], ".probe-nonexistent")))
            for i, p in enumerate(paths["files"]):
                deny("open_file_%d" % i, lambda p=p: os.close(os.open(p, os.O_RDONLY)))
                deny("stat_file_%d" % i, lambda p=p: os.stat(p))
            if paths.get("ingress_pid"):
                deny("kill0_ingress", lambda: os.kill(paths["ingress_pid"], 0))
                deny("open_proc_mem", lambda: os.close(os.open("/proc/%d/mem" % paths["ingress_pid"], os.O_RDONLY)))
                deny("open_proc_environ", lambda: os.close(os.open("/proc/%d/environ" % paths["ingress_pid"], os.O_RDONLY)))
        except SystemExit:
            pass
        except BaseException as exc:  # noqa: BLE001 - reported to the parent, which fails closed
            res["probe_error"] = type(exc).__name__
        finally:
            try:
                os.write(w, json.dumps(res, sort_keys=True).encode())
            finally:
                os._exit(0)
    os.close(w)
    data = b""
    while True:
        part = os.read(r, 65536)
        if not part:
            break
        data += part
    os.close(r)
    os.waitpid(pid, 0)
    try:
        return True, json.loads(data.decode())
    except ValueError:
        return None, "probe child produced no result"


def _journal_from_header(path):
    try:
        with open(path, "rb") as f:
            head = f.read(100)
    except OSError as exc:
        return None, errno.errorcode.get(exc.errno, str(exc.errno))
    if head[:16] != b"SQLite format 3\x00":
        return None, "not_sqlite"
    return ("wal" if head[18] == 2 and head[19] == 2 else "rollback_family" if head[18] == 1 else "unknown"), ""


def _ast_simulate_and_identity(core_path):
    tree = ast.parse(open(core_path, encoding="utf-8").read())
    sims, ids = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "simulate":
                    sims.append(isinstance(kw.value, ast.Constant) and kw.value.value is None)
                if kw.arg == "operation_identity":
                    ids.append(isinstance(kw.value, ast.Constant) and kw.value.value is True)
    return sims, ids


def build_record(args):
    checks, rec = [], {"schema": SCHEMA}
    add = checks.append
    label = (args.label or "").strip()
    if label:
        rec["evidence_label"] = label
        add(_chk("capture.evidence_label", PASS, "evidence label recorded: %s" % label))
    else:
        add(_chk("capture.evidence_label", BLOCKED, "--label is required: state what environment this record is (for example development container, not the qualification host; manifest kind; boundary qualified or not); without it the record cannot PASS"))
    root = os.path.realpath(args.repo_root)
    state_dir = os.path.abspath(args.state_dir) if args.state_dir else None
    sock = os.path.abspath(args.socket) if args.socket else None
    ing_uid, ing_gid, ing_proc, tree, jm, files = args.ingress_uid, args.ingress_gid, None, [], {}, []
    sims_ok = ids_ok = None  # None: not established by the AST scan

    # ---- Platform
    with _section(checks, "platform"):
        osr = {}
        for line in (_read("/etc/os-release") or "").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                osr[k] = v.strip('"')
        mounts = {}
        for label, p in (("state_dir", state_dir), ("socket_dir", os.path.dirname(sock) if sock else None)):
            mounts[label] = mountinfo(p) if p and os.path.exists(p) else None
        rec["platform"] = {"distro": {"id": osr.get("ID"), "version_id": osr.get("VERSION_ID"), "pretty_name": osr.get("PRETTY_NAME")},
                           "kernel_release": platform.release(), "kernel_version": platform.version(), "arch": platform.machine(),
                           "filesystems": {k: ({"mount_point": v[0], "fstype": v[1], "mount_options": v[2], "super_options": v[3]} if v else None)
                                           for k, v in sorted(mounts.items())}}
        if platform.system() != "Linux":
            add(_chk("platform.linux", FAIL, "not Linux"))
        else:
            add(_chk("platform.linux", PASS, "Linux %s %s" % (platform.release(), platform.machine())))
        for label, v in sorted(mounts.items()):
            if v is None:
                add(_chk("platform.fs_enforces_unix_perms.%s" % label, BLOCKED, "path not given, missing, or mountinfo unreadable"))
            elif v[1] in ENFORCEABLE_FS and "noacl" not in (v[2] + "," + v[3]).split(","):
                add(_chk("platform.fs_enforces_unix_perms.%s" % label, PASS, "fstype %s" % v[1], fstype=v[1]))
            elif v[1] in NO_UNIX_PERMS_FS:
                add(_chk("platform.fs_enforces_unix_perms.%s" % label, FAIL, "fstype %s does not reliably enforce unix owner/mode" % v[1], fstype=v[1]))
            else:
                add(_chk("platform.fs_enforces_unix_perms.%s" % label, BLOCKED, "fstype %s is not in the verified set %s" % (v[1], sorted(ENFORCEABLE_FS)), fstype=v[1]))

    # ---- Python
    with _section(checks, "python"):
        dists = sorted((d.metadata["Name"] or "", d.version) for d in md.distributions())
        interp = os.path.realpath(sys.executable)
        try:
            interp_digest = _sha256_file(interp)
        except OSError:
            interp_digest = None
        import sqlite3
        rec["python"] = {"executable": interp, "executable_sha256": interp_digest, "version": platform.python_version(),
                         "implementation": platform.python_implementation(), "version_string": sys.version,
                         "sqlite_library_version": sqlite3.sqlite_version, "distributions": [list(x) for x in dists],
                         "qualified_profile": "3.13", "unqualified": ["3.11"]}
        rec["python"]["describes"] = ("the capture process interpreter (sys.executable); it counts for the ingress only if "
                                      "python.interpreter_matches_ingress is PASS")
        if sys.version_info[:2] == (3, 13) and platform.python_implementation() == "CPython":
            add(_chk("python.profile", PASS, "CPython %s" % platform.python_version()))
        else:
            add(_chk("python.profile", FAIL, "only CPython 3.13 is the qualified profile; got %s %s (3.11 stays unqualified)" % (platform.python_implementation(), platform.python_version())))
        rec["python"]["pydantic_installed"] = next((v for n, v in dists if n.lower() == "pydantic"), None)

    # ---- Process identity
    with _section(checks, "process_identity"):
        if args.ingress_pid:
            st = parse_status(_read("/proc/%d/status" % args.ingress_pid))
            if st:
                ing_proc = {"uid": [int(x) for x in st["Uid"].split()], "gid": [int(x) for x in st["Gid"].split()],
                            "groups": [int(x) for x in st.get("Groups", "").split()], "capeff": st["CapEff"], "capprm": st["CapPrm"],
                            "capbnd": st["CapBnd"], "no_new_privs": st.get("NoNewPrivs"), "seccomp": st.get("Seccomp"),
                            "cmdline": (_read("/proc/%d/cmdline" % args.ingress_pid) or "").replace("\0", " ").strip(),
                            "exe": _proc_exe(args.ingress_pid)}
                if ing_uid is None:
                    ing_uid = ing_proc["uid"][1]
                if ing_gid is None:
                    ing_gid = ing_proc["gid"][1]
        rec["process_identity"] = {"ingress_uid": ing_uid, "ingress_gid": ing_gid, "ingress_user": _name_uid(ing_uid) if ing_uid is not None else None,
                                   "client_uid": args.client_uid, "client_gid": args.client_gid,
                                   "client_user": _name_uid(args.client_uid) if args.client_uid is not None else None,
                                   "ingress_process": ing_proc, "capture_process": {"euid": os.geteuid(), "egid": os.getegid()}}
        ids_given = (ing_uid, ing_gid, args.client_uid, args.client_gid)
        if any(v is None for v in ids_given):
            add(_chk("identity.declared", BLOCKED, "ingress uid and gid (or --ingress-pid) and client uid and gid must all be given"))
        elif any(not 0 <= v < 2 ** 32 - 1 for v in ids_given):
            add(_chk("identity.declared", FAIL, "uid/gid out of range: %s" % (ids_given,)))
        else:
            add(_chk("identity.declared", PASS, "ingress %s:%s client %s:%s" % (ing_uid, ing_gid, args.client_uid, args.client_gid)))
            bad = [m for m, c in (("client uid == ingress uid", args.client_uid == ing_uid), ("client uid is 0", args.client_uid == 0),
                                  ("client gid == ingress gid", ing_gid is not None and args.client_gid == ing_gid)) if c]
            add(_chk("identity.client_distinct_unprivileged", FAIL if bad else PASS, "; ".join(bad) or "client uid/gid differ from ingress and uid is not 0"))
            if ing_uid != 0:
                add(_chk("identity.ingress_not_root", PASS, "ingress uid %s" % ing_uid))
            else:
                add(_chk("identity.ingress_not_root", FAIL, "ingress runs as uid 0; the profile requires a dedicated non-root ingress uid"))
        if args.ingress_pid:
            if ing_proc is None:
                add(_chk("identity.ingress_process", BLOCKED, "cannot read /proc/%d/status" % args.ingress_pid))
            else:
                ok = len(set(ing_proc["uid"])) == 1 and ing_proc["uid"][0] == ing_uid
                add(_chk("identity.ingress_process", PASS if ok else FAIL, "real/effective/saved uid %s, expected %s" % (ing_proc["uid"], ing_uid)))
        else:
            add(_chk("identity.ingress_process", BLOCKED, "--ingress-pid not given: process ownership of the running ingress not verified"))
        if not args.ingress_pid:
            add(_chk("identity.ingress_command", BLOCKED, "--ingress-pid not given: the ingress command line is not verified"))
        elif ing_proc is None:
            add(_chk("identity.ingress_command", BLOCKED, "cannot read the ingress process"))
        else:
            toks = ing_proc["cmdline"].split()
            launcher = os.path.realpath(os.path.join(args.repo_root, "tools", "mvp_ingress", "launch.py"))
            idx = next((i for i, t in enumerate(toks) if os.path.isabs(t) and os.path.realpath(t) == launcher), None)
            allow = sorted({int(toks[i + 1]) for i, t in enumerate(toks[:-1]) if t == "--allow-uid" and toks[i + 1].isdigit()})
            if idx is None:
                add(_chk("identity.ingress_command", FAIL, "NON-COMPLIANT: the supported form is `python -I <repo-root>/tools/mvp_ingress/launch.py`; "
                         "`python -m tools.mvp_ingress.server` or another launcher path is not supported: %s" % ing_proc["cmdline"][:120]))
            elif "-I" not in toks[1:idx]:
                add(_chk("identity.ingress_command", FAIL, "NON-COMPLIANT: the launcher is not run in isolated mode (-I)"))
            elif not allow or allow != list(args.allow_uid):
                add(_chk("identity.ingress_command", FAIL, "ingress --allow-uid values %s differ from the declared --allow-uid %s" % (allow, list(args.allow_uid))))
            else:
                add(_chk("identity.ingress_command", PASS, "ingress runs the isolated launcher of this repo root with --allow-uid %s" % allow))
        mine = os.path.realpath(sys.executable)
        if not args.ingress_pid:
            add(_chk("python.interpreter_matches_ingress", BLOCKED, "--ingress-pid not given: the python section describes the capture process, not the ingress"))
        elif ing_proc is None or not ing_proc.get("exe"):
            add(_chk("python.interpreter_matches_ingress", BLOCKED, "cannot read the ingress executable (/proc/%d/exe)" % args.ingress_pid))
        elif ing_proc["exe"] != mine:
            add(_chk("python.interpreter_matches_ingress", FAIL, "ingress exe %s != capture interpreter %s" % (ing_proc["exe"], mine)))
        else:
            add(_chk("python.interpreter_matches_ingress", PASS, "ingress exe equals capture interpreter %s" % mine))

    # ---- IPC
    with _section(checks, "ipc"):
        ipc = {"socket_path": sock, "stat": _stat_row(sock) if sock else None, "connection_policy": {
            "peer_uid_allow_list": args.allow_uid, "socket_policy": "mode 0660, owner ingress uid, dedicated group of exactly the ingress and client identities, socket in a separate IPC directory"}}
        rec["ipc"] = ipc
    # ---- Filesystem
    with _section(checks, "filesystem"):
        files = [p for p in (args.db, args.authority_store, args.ledger) if p]
        fsrec = {"state_dir": state_dir, "tree": [], "ancestors": [], "paths": {"destination_db": args.db, "authority_store": args.authority_store, "ledger": args.ledger}}
        rec["filesystem"] = fsrec
        tree = []
        if state_dir and os.path.isdir(state_dir):
            try:
                tree = walk_tree(state_dir)
            except OSError:
                tree = [state_dir]
            fsrec["tree"] = [_stat_row(p) for p in tree]
        if sock:
            fsrec["ancestors"] = [_stat_row(p) for p in sorted(set(ancestors(sock) + (ancestors(state_dir) if state_dir else [])))]
        for label, p in (("state_dir", state_dir), ("socket", sock)):
            if not p or not os.path.lexists(p):
                add(_chk("filesystem.%s_present" % label, BLOCKED, "path not given or does not exist"))
        if state_dir and os.path.lexists(state_dir) and ing_uid is not None:
            bad = []
            for p in tree:
                st = os.lstat(p)
                want = 0o700 if p == state_dir else None
                if stat.S_ISLNK(st.st_mode) or not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
                    bad.append("%s: symlink or special file" % p)
                if st.st_uid != ing_uid:
                    bad.append("%s: owner uid %d != ingress uid" % (p, st.st_uid))
                m = stat.S_IMODE(st.st_mode)
                if stat.S_ISDIR(st.st_mode) and m != 0o700:
                    bad.append("%s: directory mode %04o != 0700" % (p, m))
                if stat.S_ISREG(st.st_mode) and m != 0o600:
                    bad.append("%s: file mode %04o != 0600" % (p, m))
                if m & 0o077:
                    bad.append("%s: group/other bits set" % p)
            add(_chk("filesystem.state_tree_owner_only", FAIL if bad else PASS, "; ".join(sorted(set(bad))[:8]) or "%d entries: dirs 0700, files 0600, one owner, no group/other bits, no symlinks" % len(tree), entries=len(tree)))
        else:
            add(_chk("filesystem.state_tree_owner_only", BLOCKED, "state dir missing or ingress uid unknown"))
        # state dir parents and socket dir parents (same rule as server.check_parents)
        if sock and ing_uid is not None:
            bad = []
            for p in sorted(set(ancestors(sock) + (ancestors(state_dir) if state_dir else []))):
                st = os.lstat(p)
                if not stat.S_ISDIR(st.st_mode) or st.st_uid not in (0, ing_uid):
                    bad.append("%s: not a dir owned by root or ingress uid" % p)
                # Deliberate rule: a group/other-writable ancestor is excused only if it is sticky AND root-owned AND not the
                # directory that directly holds the socket or the state dir (a root-owned sticky dir such as /tmp stops others
                # renaming or deleting root/ingress-owned entries beneath it). The direct parents get no sticky excuse, the
                # same as the IPC-directory rule (ipc.directory_separate_and_protected).
                direct = p in (os.path.dirname(sock), os.path.dirname(state_dir) if state_dir else None)
                sticky_ok = bool(st.st_mode & stat.S_ISVTX) and st.st_uid == 0 and not direct
                if stat.S_IMODE(st.st_mode) & 0o022 and not sticky_ok:
                    bad.append("%s: group/other writable and not (sticky, root-owned and not a direct parent)" % p)
            add(_chk("filesystem.ancestors_not_writable_by_others", FAIL if bad else PASS, "; ".join(bad[:6]) or "every ancestor of socket and state dir is root/ingress-owned and not go+w (sticky only excuses a root-owned, non-direct-parent ancestor)"))
        else:
            add(_chk("filesystem.ancestors_not_writable_by_others", BLOCKED, "socket path or ingress uid not given"))
        # sqlite journal mode from file headers (no database is opened)
        jm = {}
        for label, p in (("destination_db", args.db), ("authority_store", args.authority_store), ("ledger", args.ledger)):
            if p:
                jm[label] = _journal_from_header(p)
    # ---- Socket checks
    with _section(checks, "socket_checks"):
        if sock and os.path.lexists(sock) and ing_uid is not None and args.client_uid is not None:
            st = os.lstat(sock)
            m = stat.S_IMODE(st.st_mode)
            probs, inconclusive = [], []
            if not stat.S_ISSOCK(st.st_mode):
                probs.append("not a socket")
            if st.st_uid != ing_uid:
                probs.append("socket owner uid %d is not the ingress uid %d (client ownership is not allowed)" % (st.st_uid, ing_uid))
            if m != SOCKET_MODE:
                probs.append("socket mode %04o is not 0660" % m)
            if st.st_gid == 0 or st.st_gid in (ing_gid, args.client_gid):
                probs.append("socket group %d is not a dedicated group (gid 0, the ingress primary gid or the client primary gid)" % st.st_gid)
            iname, cname = _name_uid(ing_uid), _name_uid(args.client_uid)
            if not iname or not cname:
                inconclusive.append("ingress or client uid has no passwd entry: group membership cannot be compared")
            else:
                gm = _group_members(st.st_gid)
                members = set(gm or ())
                if gm is None:
                    inconclusive.append("passwd is not enumerable (getpwall empty or failing): group %d membership cannot be established" % st.st_gid)
                elif members != {iname, cname}:
                    probs.append("socket group %d members %s != exactly {%s, %s} (members plus primary-gid users)" % (st.st_gid, sorted(members), iname, cname))
            add(_chk("ipc.socket_mode_owner_group", FAIL if probs else BLOCKED if inconclusive else PASS,
                     "; ".join(probs or inconclusive) or "socket 0660 owner uid %d dedicated group %d with exactly the ingress and client users" % (st.st_uid, st.st_gid)))
        else:
            add(_chk("ipc.socket_mode_owner_group", BLOCKED, "socket missing or identities not given"))
        if sock and state_dir and os.path.lexists(os.path.dirname(sock)) and os.path.lexists(state_dir) and ing_uid is not None:
            ipc_dir, real_state = os.path.realpath(os.path.dirname(sock)), os.path.realpath(state_dir)
            probs = []
            if ipc_dir == real_state or ipc_dir.startswith(real_state + os.sep):
                probs.append("socket directory is the state directory or inside it")
            dst = os.lstat(ipc_dir)
            if dst.st_uid not in (0, ing_uid):
                probs.append("IPC directory owner uid %d is neither root nor the ingress uid" % dst.st_uid)
            if stat.S_IMODE(dst.st_mode) & 0o022:
                probs.append("IPC directory %04o is group/other writable (the socket could be replaced; sticky does not excuse it)" % stat.S_IMODE(dst.st_mode))
            add(_chk("ipc.directory_separate_and_protected", FAIL if probs else PASS, "; ".join(probs) or "IPC directory %s is outside the state tree, owner %d, not group/other writable" % (ipc_dir, dst.st_uid)))
        else:
            add(_chk("ipc.directory_separate_and_protected", BLOCKED, "socket directory, state dir or ingress uid not available"))
        # extra group access: group bits and group membership on the state dir / socket
        if state_dir and os.path.lexists(state_dir) and ing_uid is not None and args.client_uid is not None:
            name = _name_uid(args.client_uid)
            if name is None:
                add(_chk("filesystem.no_extra_group_access", BLOCKED, "client uid has no passwd entry: supplementary groups unknown"))
            else:
                cg = set(os.getgrouplist(name, args.client_gid))
                probs = []
                for p in [state_dir] + tree[1:]:
                    st = os.lstat(p)
                    if st.st_gid in cg and stat.S_IMODE(st.st_mode) & 0o070:
                        probs.append("%s: client holds group %d with group bits %04o" % (p, st.st_gid, stat.S_IMODE(st.st_mode)))
                add(_chk("filesystem.no_extra_group_access", FAIL if probs else PASS, "; ".join(probs[:6]) or "client groups %s grant nothing on the state tree" % sorted(cg), client_groups=sorted(cg)))
        else:
            add(_chk("filesystem.no_extra_group_access", BLOCKED, "state dir or identities not given"))
        # ACLs
        targets = ([state_dir] + tree[1:] if state_dir and os.path.lexists(state_dir) else []) + ([sock] if sock and os.path.lexists(sock) else []) + \
            (sorted(set(ancestors(sock) + (ancestors(state_dir) if state_dir else []))) if sock or state_dir else [])
        targets = sorted(set(targets))
        acl_rows, bad, unread = {}, [], []
        for p in targets:
            s, d = acl_state(p)
            acl_rows[p] = s
            if s == "present":
                bad.append("%s: %s" % (p, d))
            elif s == "unreadable":
                unread.append("%s: %s" % (p, d))
        rec["isolation_acl"] = {"method": "os.listxattr(follow_symlinks=False) for %s" % " and ".join(ACL_XATTRS), "getfacl_available": shutil.which("getfacl") is not None, "paths": acl_rows}
        if not targets:
            add(_chk("filesystem.no_acl_entries", BLOCKED, "no socket or state dir to inspect"))
        elif bad:
            add(_chk("filesystem.no_acl_entries", FAIL, "; ".join(bad[:6])))
        elif unread:
            add(_chk("filesystem.no_acl_entries", BLOCKED, "ACL xattrs could not be read (permission or unsupported): " + "; ".join(unread[:6])))
        else:
            add(_chk("filesystem.no_acl_entries", PASS, "no POSIX ACL xattr on %d paths (socket, state tree, ancestors)" % len(targets), paths=len(targets)))

    # ---- Isolation limits
    with _section(checks, "isolation_limits"):
        ptrace = _read("/proc/sys/kernel/yama/ptrace_scope")
        iso = {"yama_ptrace_scope": ptrace.strip() if ptrace else None,
               "unprivileged_userns_clone": (_read("/proc/sys/kernel/unprivileged_userns_clone") or "").strip() or None,
               "max_user_namespaces": (_read("/proc/sys/user/max_user_namespaces") or "").strip() or None,
               "lsm": (_read("/sys/kernel/security/lsm") or "").strip() or None,
               "selinux_enforce": (_read("/sys/fs/selinux/enforce") or "").strip() or None,
               "proc_mount_options": (mountinfo("/proc") or (None, None, None, None))[2:],
               "capture_process": {k: parse_status(_read("/proc/self/status")).get(k) for k in ("CapEff", "CapPrm", "CapBnd", "NoNewPrivs", "Seccomp")},
               "capture_uid_map": (_read("/proc/self/uid_map") or "").split(),
               "container_markers": sorted(m for m, ok in (("/.dockerenv", os.path.exists("/.dockerenv")), ("/run/.containerenv", os.path.exists("/run/.containerenv"))) if ok)}
        rec["isolation_limits"] = iso
        if ptrace is None:
            rec["profile_supported"] = False
            add(_chk("isolation.ptrace_scope", BLOCKED, "UNSUPPORTED: /proc/sys/kernel/yama/ptrace_scope is absent (Yama not available); the exact profile is unsupported and the boundary test is BLOCKED; no weaker environment is substituted"))
        elif ptrace.strip() in ("1", "2", "3"):
            rec["profile_supported"] = True
            add(_chk("isolation.ptrace_scope", PASS, "kernel.yama.ptrace_scope=%s" % ptrace.strip(), value=ptrace.strip()))
        else:
            rec["profile_supported"] = False
            add(_chk("isolation.ptrace_scope", FAIL, "kernel.yama.ptrace_scope=%s (profile requires >= 1)" % ptrace.strip(), value=ptrace.strip()))
        iso["fs_suid_dumpable"] = (_read("/proc/sys/fs/suid_dumpable") or "").strip() or None
        if ing_proc:
            iso["ingress_capabilities"] = {"CapEff": ing_proc["capeff"], "CapPrm": ing_proc["capprm"], "CapBnd": ing_proc["capbnd"],
                                           "privileged_in_effective": cap_names(ing_proc["capeff"]), "privileged_in_permitted": cap_names(ing_proc["capprm"])}
            bad = int(ing_proc["capeff"], 16) != 0 or int(ing_proc["capprm"], 16) != 0
            add(_chk("isolation.ingress_capabilities", FAIL if bad else PASS,
                     "ingress CapEff=%s CapPrm=%s (must both be 0); privileged effective=%s permitted=%s" % (ing_proc["capeff"], ing_proc["capprm"], cap_names(ing_proc["capeff"]) or "none", cap_names(ing_proc["capprm"]) or "none")))
        else:
            add(_chk("isolation.ingress_capabilities", BLOCKED, "--ingress-pid not given or process unreadable"))
        if args.ingress_pid and ing_uid is not None:
            owner = _proc_owner(args.ingress_pid)
            iso["ingress_proc_dir_owner_uid"] = owner
            if owner is None:
                add(_chk("isolation.ingress_dumpability", BLOCKED, "cannot stat /proc/%d" % args.ingress_pid))
            elif owner == ing_uid:
                add(_chk("isolation.ingress_dumpability", PASS, "dump-owner consistent: /proc entry owned by the ingress uid (dumpable). Not proof of isolation; the stronger evidence is the denied /proc/<pid>/mem and environ opens in qualification.client_denied_ingress_process", dumpable=True))
            elif owner == 0:
                add(_chk("isolation.ingress_dumpability", PASS, "dump-owner consistent: /proc entry owned by root (non-dumpable). Not proof of isolation; the stronger evidence is the denied /proc/<pid>/mem and environ opens in qualification.client_denied_ingress_process", dumpable=False))
            else:
                add(_chk("isolation.ingress_dumpability", FAIL, "dump-owner inconsistent: /proc entry owner uid %d is neither the ingress uid nor root" % owner))
        else:
            add(_chk("isolation.ingress_dumpability", BLOCKED, "--ingress-pid or ingress uid not given"))
        # client-side probe
        probe_paths = {"socket": sock, "state_dir": state_dir, "files": files, "ingress_pid": args.ingress_pid}
        if not (sock and state_dir) or args.client_uid is None or args.client_gid is None:
            pstat, pres = None, "socket, state dir or client identity not given"
        else:
            pstat, pres = client_probe(args, probe_paths)
            ostat, ores = client_probe(args, probe_paths, uid=args.outsider_uid, gid=args.outsider_uid, role="outsider")
        rec["qualification"] = {"client_probe": pres if pstat else None, "not_run_by_this_script": [
            "live propose round trip through client.submit (positive execution result)", "adversarial proposals against the running ingress",
            "Python 3.11 (unqualified)"]}
        if not (sock and state_dir) or args.client_uid is None or args.client_gid is None:
            ostat, ores = None, "socket, state dir or client identity not given"
        # outsider: a uid that is neither the ingress nor the client nor in the dedicated group must not connect
        oname = _name_uid(args.outsider_uid)
        gmem = set((_group_members(os.lstat(sock).st_gid) or ()) if sock and os.path.lexists(sock) else ())
        if args.outsider_uid in (ing_uid, args.client_uid) or (oname and oname in gmem):
            add(_chk("qualification.outsider_denied_socket", FAIL, "outsider uid %d is the ingress, the client or a group member: not an outsider" % args.outsider_uid))
        elif not ostat or "probe_error" in ores:
            add(_chk("qualification.outsider_denied_socket", BLOCKED, str(ores if not ostat else "probe child failed: %s" % ores["probe_error"])))
        else:
            sc = ores.get("socket_connect")
            # The outsider's denial is evidence about the socket's own mode/group only if the outsider can traverse every
            # ancestor of the socket (including the IPC directory). Otherwise the directory stopped it.
            o_blocked = untraversable_for(sock, args.outsider_uid, {args.outsider_uid})
            rec_o = {"connect": sc, "traversal_blocked_above_socket": o_blocked}
            rec["qualification_outsider_probe"] = rec_o
            if sc == "connected":
                add(_chk("qualification.outsider_denied_socket", FAIL, "outsider uid %d connected to the socket" % args.outsider_uid, **rec_o))
            elif sc == "denied" and o_blocked:
                add(_chk("qualification.outsider_denied_socket", BLOCKED,
                         "not conclusive for the socket: outsider uid %d lacks search (x) on %s, so the directory denied it before the socket's own mode/group was consulted; probe by a path the outsider can reach" % (args.outsider_uid, o_blocked), **rec_o))
                add(_chk("qualification.outsider_denied_by_ipc_directory", PASS,
                         "directory-level denial proven: outsider uid %d cannot traverse %s. This is not evidence about the socket mode or group" % (args.outsider_uid, o_blocked), **rec_o))
            else:
                add(_chk("qualification.outsider_denied_socket", PASS if sc == "denied" else BLOCKED,
                         "outsider uid %d connect: %s (outsider can traverse every ancestor, so the socket's own mode/group decided)" % (args.outsider_uid, sc), **rec_o))
        if pstat and "probe_error" not in pres and state_dir:
            cname = _name_uid(args.client_uid)
            cgroups = set(os.getgrouplist(cname, args.client_gid)) if cname else {args.client_gid}
            blocked_dirs = untraversable_for(state_dir, args.client_uid, cgroups)
            pres["traversal_blocked_above_state_dir"] = blocked_dirs
        else:
            blocked_dirs = []
        if not pstat:
            for cid in ("qualification.client_capabilities_empty", "qualification.client_socket_reachable", "qualification.client_denied_state_access",
                        "qualification.client_denied_ingress_process", "ipc.peer_credentials"):
                add(_chk(cid, BLOCKED, str(pres)))
        else:
            if "probe_error" in pres:
                for cid in ("qualification.client_capabilities_empty", "qualification.client_socket_reachable", "qualification.client_denied_state_access", "qualification.client_denied_ingress_process", "ipc.peer_credentials"):
                    add(_chk(cid, BLOCKED, "probe child failed: %s" % pres["probe_error"]))
            else:
                add(_chk("qualification.client_capabilities_empty", PASS if int(pres["capeff"], 16) == 0 else FAIL, "client CapEff=%s" % pres["capeff"]))
                sc = pres.get("socket_connect")
                add(_chk("qualification.client_socket_reachable", PASS if sc == "connected" else FAIL if sc == "denied" else BLOCKED,
                         "client uid %d connect to the socket: %s" % (args.client_uid, sc), connect=sc))
                pc = pres.get("peercred")
                if sc != "connected" or not pc:
                    add(_chk("ipc.peer_credentials", BLOCKED, "no connection, so no SO_PEERCRED evidence"))
                elif not args.ingress_pid:
                    add(_chk("ipc.peer_credentials", BLOCKED, "--ingress-pid not given: SO_PEERCRED %s cannot be tied to the ingress process" % pc))
                else:
                    bad = [n for n, ok in (("pid", pc[0] == args.ingress_pid), ("uid", pc[1] == ing_uid), ("gid", ing_gid is None or pc[2] == ing_gid)) if not ok]
                    add(_chk("ipc.peer_credentials", FAIL if bad else PASS, "SO_PEERCRED from a real connection (pid, uid, gid)=%s; ingress pid/uid/gid=%s/%s/%s; mismatch: %s" % (pc, args.ingress_pid, ing_uid, ing_gid, bad or "none"), peercred=pc))
                sk = sorted(k for k in pres if k.startswith(("listdir_", "unlink_", "open_file_", "stat_file_")))
                res = {k: pres[k] for k in sk}
                if blocked_dirs:
                    add(_chk("qualification.client_denied_state_access", BLOCKED, "denial may be due to traversal above the state dir: client lacks search (x) on %s" % blocked_dirs, results=res))
                elif any(v == "allowed" for v in res.values()):
                    add(_chk("qualification.client_denied_state_access", FAIL, "client was allowed: %s" % sorted(k for k, v in res.items() if v == "allowed"), results=res))
                elif any(v != "denied" for v in res.values()):
                    add(_chk("qualification.client_denied_state_access", BLOCKED, "inconclusive: %s" % sorted(k for k, v in res.items() if v != "denied"), results=res))
                else:
                    add(_chk("qualification.client_denied_state_access", PASS, "all %d state-access probes denied (EACCES/EPERM)" % len(res), results=res))
                pk = sorted(k for k in pres if k in ("kill0_ingress", "open_proc_mem", "open_proc_environ"))
                if not pk:
                    add(_chk("qualification.client_denied_ingress_process", BLOCKED, "--ingress-pid not given"))
                else:
                    res = {k: pres[k] for k in pk}
                    st = "FAIL" if "allowed" in res.values() else PASS if all(v == "denied" for v in res.values()) else BLOCKED
                    add(_chk("qualification.client_denied_ingress_process", st, str(res), results=res))

    # ---- Invocation
    with _section(checks, "invocation"):
        client_py, core_py = os.path.join(root, "tools/mvp_ingress/client.py"), os.path.join(root, "tools/mvp_ingress/core.py")
        inv = {"client_entry_point": "tools.mvp_ingress.client:submit", "server_entry_point": "python -I tools/mvp_ingress/launch.py",
               "static_scan_note": "best-effort AST scan of the checked-out sources; it is not proof about the running ingress"}
        rec["invocation"] = inv
        try:
            tree_ast = ast.parse(open(client_py, encoding="utf-8").read())
            mods = sorted({(n.module or "").split(".")[0] if isinstance(n, ast.ImportFrom) else a.name.split(".")[0] for n in ast.walk(tree_ast)
                           if isinstance(n, (ast.Import, ast.ImportFrom)) for a in (n.names if isinstance(n, ast.Import) else [None]) if not (isinstance(n, ast.ImportFrom) and n.level)})
            has_submit = any(isinstance(n, ast.FunctionDef) and n.name == "submit" for n in ast.walk(tree_ast))
            nonstd = [m for m in mods if m not in sys.stdlib_module_names and m != "__future__"]
            inv["client_sha256"], inv["client_imports"] = _sha256_file(client_py), mods
            add(_chk("invocation.client_entry_point", PASS if has_submit and not nonstd else FAIL, "submit defined=%s, non-stdlib imports=%s" % (has_submit, nonstd)))
        except (OSError, SyntaxError):
            add(_chk("invocation.client_entry_point", BLOCKED, "cannot read/parse %s" % client_py))
        try:
            sims, _ = _ast_simulate_and_identity(core_py)
            _, ids = _ast_simulate_and_identity(os.path.join(root, "tools/mvp_ingress/synthetic_host.py"))
            inv["core_sha256"] = _sha256_file(core_py)
            sims_ok, ids_ok = bool(sims) and all(sims), bool(ids) and all(ids)
            add(_chk("invocation.simulate_fixed_none", PASS if sims_ok else FAIL, "best-effort static scan: simulate= keywords in core.py: %d, all constant None: %s (does not see getattr, ** forwarding or dynamic calls)" % (len(sims), sims_ok)))
            add(_chk("invocation.operation_identity_fixed_true", PASS if ids_ok else FAIL, "best-effort static scan: operation_identity= keywords in synthetic_host.py: %d, all constant True: %s" % (len(ids), ids_ok)))
        except (OSError, SyntaxError):
            for cid in ("invocation.simulate_fixed_none", "invocation.operation_identity_fixed_true"):
                add(_chk(cid, BLOCKED, "cannot read/parse %s" % core_py))

    # ---- Configuration
    with _section(checks, "configuration"):
        import re
        pins, bad_pins = {}, []
        for pin in args.pin:
            name, eq, val = pin.partition("=")
            if not eq or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_./\-]*", name) or not re.fullmatch(r"[0-9a-f]{7,64}", val) or name in pins:
                bad_pins.append(pin)
            else:
                pins[name] = val
        manifests, dup_manifests = {}, []
        for m in args.manifest:
            key = os.path.basename(m)
            if key in manifests:
                dup_manifests.append(key)
            try:
                manifests[key] = _sha256_file(m)
            except OSError:
                manifests[key] = None
        srcdir = os.path.join(root, "tools/mvp_ingress")
        srcs = {}
        if os.path.isdir(srcdir):
            for n in sorted(os.listdir(srcdir)):
                if n.endswith(".py"):
                    srcs["tools/mvp_ingress/" + n] = _sha256_file(os.path.join(srcdir, n))
        rec["configuration"] = {"source_pins": dict(sorted(pins.items())), "manifest_sha256": dict(sorted(manifests.items())),
                                "ingress_source_sha256": srcs,
                                "operation_identity": ("fixed_true_by_static_scan" if ids_ok else "NOT_ESTABLISHED"),
                                "simulate": ("fixed_none_by_static_scan" if sims_ok else "NOT_ESTABLISHED"),
                                "journal_mode_declared": args.journal_mode,
                                "journal_mode_observed_from_file_header": {k: v[0] for k, v in sorted(jm.items())}}
        mismatch, unverified = [], []
        for name, val in sorted(pins.items()):
            if name.startswith("manifest_sha256."):
                got = manifests.get(name.split(".", 1)[1])
                if got != val:
                    mismatch.append(name)
            elif name.startswith("source_sha256."):
                got = srcs.get(name.split(".", 1)[1])
                if got is None or got != val:
                    mismatch.append(name)
            else:
                unverified.append(name)
        rec["configuration"]["pins_unverified"] = unverified
        if bad_pins or mismatch or dup_manifests:
            add(_chk("configuration.pins_and_manifests", FAIL, "malformed or duplicate pins %s; digest mismatches %s; manifests with the same base name %s" % (bad_pins, mismatch, sorted(set(dup_manifests)))))
        elif not pins or not manifests or not all(manifests.values()):
            add(_chk("configuration.pins_and_manifests", BLOCKED, "give at least one --pin and --manifest FILE (all readable)"))
        elif unverified and not args.accept_unverified_pins:
            add(_chk("configuration.pins_and_manifests", BLOCKED, "pins %s cannot be compared with anything this script can read; use manifest_sha256.<file>= or source_sha256.<path>= pins, or --accept-unverified-pins to record them as declared only" % unverified))
        else:
            add(_chk("configuration.pins_and_manifests", PASS, "pins %s; manifests %s; unverified (declared only): %s" % (sorted(pins), sorted(manifests), unverified)))
        if args.journal_mode is not None and args.journal_mode.lower() not in JOURNAL_MODES:
            add(_chk("configuration.journal_mode", FAIL, "--journal-mode %r is not one of %s" % (args.journal_mode, list(JOURNAL_MODES))))
        elif args.journal_mode is None or not (set(jm) - {"ledger"}):
            add(_chk("configuration.journal_mode", BLOCKED, "--journal-mode and --db or --authority-store must be given"))
        else:
            want = "wal" if args.journal_mode.lower() == "wal" else "rollback_family"
            # the declared mode governs the destination and the authority store; the ingress ledger is recorded only
            miss = {k: v for k, v in jm.items() if k != "ledger" and v[0] != want}
            unk = {k: v for k, v in miss.items() if v[0] is None}
            add(_chk("configuration.journal_mode", FAIL if len(miss) > len(unk) else BLOCKED if unk else PASS,
                     "declared %s; observed %s" % (args.journal_mode, {k: (v[0] or v[1]) for k, v in sorted(jm.items())})))

    checks.sort(key=lambda c: c["id"])
    overall = FAIL if any(c["status"] == FAIL for c in checks) else BLOCKED if any(c["status"] == BLOCKED for c in checks) else PASS
    rec["checks"] = checks
    rec["overall"] = overall
    rec["claims"] = {"non_authorizing": True, "release": "HOLD", "not_claimed": [
        "resistance to root", "resistance to the ingress uid", "resistance to same-privilege code",
        "resistance to direct database modification by an authorized file holder", "security clearance, certification or production readiness"]}
    body = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    rec["record_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    return rec


def parser():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--state-dir"), p.add_argument("--socket"), p.add_argument("--ingress-pid", type=int)
    p.add_argument("--ingress-uid", type=int), p.add_argument("--ingress-gid", type=int)
    p.add_argument("--client-uid", type=int), p.add_argument("--client-gid", type=int)
    p.add_argument("--db"), p.add_argument("--authority-store"), p.add_argument("--ledger")
    p.add_argument("--journal-mode"), p.add_argument("--pin", action="append", default=[], help="name=value source pin")
    p.add_argument("--manifest", action="append", default=[]), p.add_argument("--allow-uid", type=int, action="append", default=[])
    p.add_argument("--outsider-uid", type=int, default=65533, help="an unrelated uid expected to be denied the socket")
    p.add_argument("--accept-unverified-pins", action="store_true", help="pass pins that cannot be compared, recording them as declared only")
    p.add_argument("--repo-root", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    p.add_argument("--label", help="REQUIRED self-label of the evidence (environment kind, manifest kind, qualification state); the record is BLOCKED without it")
    p.add_argument("--out", help="write the record here (default stdout)")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    args.allow_uid = sorted(args.allow_uid)
    try:
        rec = build_record(args)
    except Exception as exc:  # noqa: BLE001 - fail closed with a BLOCKED record, never a traceback and never PASS
        rec = {"schema": SCHEMA, "overall": BLOCKED, "checks": [_chk("capture.exception", BLOCKED, "capture raised %s" % type(exc).__name__)],
               "claims": {"non_authorizing": True, "release": "HOLD"}}
    text = json.dumps(rec, sort_keys=True, indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return {PASS: 0, FAIL: 1, BLOCKED: 2}[rec["overall"]]


if __name__ == "__main__":
    sys.exit(main())
