# MVP trusted-host ingress: frozen Qualification environment profile and capture

Status: PROPOSED, non-authorizing. Release, publication and production remain on HOLD. This is not a Qualification verdict, a security clearance, a certification or a production-readiness claim. Basis: architect ruling that the trusted-host boundary is CONDITIONALLY SUFFICIENT for a fixed Linux + Python 3.13 profile, subject to the Qualification environment record below. Hub base `43c526eb`; ingress `tools/mvp_ingress/` with `BOUNDARY.md`.

## Frozen profile

| Item | Frozen value |
|---|---|
| OS | Linux, single host, local filesystem with POSIX owner/mode enforcement (ext4, xfs, btrfs, tmpfs verified set; network, FUSE and FAT-family filesystems fail) |
| Interpreter | CPython 3.13 only. Python 3.11 stays unqualified |
| Ingress | One process, one uid, not root for a qualifying run; state directory `0700`, files `0600`, one owner |
| Supported client | A distinct, unprivileged uid and gid, no capabilities, reaching only the Unix socket through `tools.mvp_ingress.client:submit` |
| IPC | One Unix socket outside the state directory; mode `0600`, owner the ingress uid or the client uid; `0660` only with `--socket-group-policy dedicated` (group members limited to the ingress and client users); never any other-bits |
| ACLs | No POSIX ACL entries on the socket, the state tree or any ancestor of either |
| Ancestors | Every ancestor of the socket and state directory is owned by root or the ingress uid and is not group/other writable (unless sticky) |
| Ptrace | `kernel.yama.ptrace_scope >= 1` and the client holds no capabilities |
| Invocation | `simulate=None` hard-coded in the core; `operation_identity=True` in the executor construction |
| Journal mode | Declared SQLite journal mode for the destination and authority store, checked against the database file header |

A deployment that does not meet every row is outside the profile and is unqualified, not "partially qualified".

## Connectivity condition (open point)

A Unix socket needs write permission on the socket file to connect. A socket `0600` owned by the ingress uid is unreachable to a distinct-uid client, and the socket cannot sit inside the `0700` state directory. The capture reports this as FAIL on `qualification.client_socket_reachable`. A qualifying deployment therefore needs one of: the socket owned by the client uid (the ingress process or its launcher must set that without widening the mode), or mode `0660` with a dedicated group whose only members are the ingress and client users. Which of the two is adopted is an architect decision; the script verifies either but adopts neither silently. ACL-based grants are not allowed.

## The capture script

`python -m tools.mvp_ingress.capture_env_record` (standard library, Python 3.13) writes one deterministic JSON record (sorted keys, no timestamps or pids) with `record_sha256`. Exit status 0 PASS, 1 FAIL, 2 BLOCKED. Run it as root, against the running ingress (`--ingress-pid`), with the client identity, database paths, `--pin` source pins, `--manifest` files and `--journal-mode`. It must be run with the interpreter the ingress uses.

Sections: `platform` (distro, kernel, arch, filesystem type and mount options of the state and socket directories), `python` (interpreter path and sha256, version, all installed distributions), `process_identity`, `ipc`, `filesystem` (stat of the state tree and ancestors), `invocation` (client entry point, hash and imports; AST check of `simulate`), `isolation_limits` (capabilities, yama, user namespaces, LSM, seccomp, no_new_privs), `configuration` (pins, manifest sha256, source sha256, journal mode declared and observed from file headers), `qualification` (client probe results).

Every check is PASS, FAIL or BLOCKED. BLOCKED means the check could not be made (not root, input not given, no xattr support, Yama absent) and is never counted as PASS. Overall is FAIL if any check fails, else BLOCKED if any is blocked, else PASS. ACLs are read as the `system.posix_acl_access` and `system.posix_acl_default` xattrs without following symlinks; `getfacl` is not required and its availability is only recorded. The client probe forks, drops to the client uid, gid and groups, and tries to list or open or stat the state files, unlink in the state directory, signal the ingress and open `/proc/<pid>/mem` and `environ`; each must be denied with EACCES or EPERM, and the socket must be writable by the client.

Not run by the script and still required as separate Qualification evidence: a live propose round trip and adversarial proposals through the client, and any Python 3.11 run.

## What is claimed

For a run whose record is overall PASS, on the exact recorded configuration: the checked ownership, mode, ACL, group, ancestor, ptrace-scope and capability preconditions held at capture time, and an unprivileged distinct-uid client was denied access to the state tree and to the ingress process by the operating system. Together with the existing `BOUNDARY.md` execution observations this supports the architect's conditional-sufficiency ruling for that profile only.

## What is not claimed

- Resistance to root, to the ingress uid, to same-privilege code, or to direct database modification by an authorized file holder.
- Anything about kernels, containers, capability sets, LSM policies or filesystems other than the recorded ones.
- Continuity: the record is a point-in-time capture, not continuous monitoring. Ancestor and ACL state can change afterwards.
- Qualification, certification, security clearance, or production readiness. Production stays on HOLD.
- That the probe is exhaustive. It checks a fixed list of operations; it does not attempt ptrace attach, namespace escape or kernel exploits.

If an untested ACL or ptrace condition can invalidate the client's isolation and the record is BLOCKED or FAIL on it, the boundary is treated as unqualified for that environment.

## Tests

`tests/test_mvp_ingress_env_record.py` (tmp directories only) covers loosened state dir and file modes, a symlink, socket modes, same-uid and uid-0 clients, a writable ancestor, ACL entries on the state dir and a state file (skipped if the filesystem refuses ACLs), unreadable ACLs, yama values 0/1/2/absent, not-root probe, Python 3.11, a non-None `simulate`, a non-stdlib client import, missing pins, journal mismatch, determinism and fail-closed behaviour with no arguments. Two tests need root and skip otherwise.
