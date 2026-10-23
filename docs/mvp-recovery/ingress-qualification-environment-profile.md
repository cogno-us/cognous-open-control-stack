# MVP trusted-host ingress: frozen Qualification environment profile and capture

Status: PROPOSED, non-authorizing. Release, publication and production remain on HOLD. This is not a Qualification verdict, a security clearance, a certification or a production-readiness claim. Basis: architect ruling that the trusted-host boundary is CONDITIONALLY SUFFICIENT for a fixed Linux + Python 3.13 profile, subject to the Qualification environment record below. Hub base `43c526eb`; ingress `tools/mvp_ingress/` with `BOUNDARY.md`.

## Evidence status

No qualifying record exists yet. The only record produced so far came from a stand-in in a development container, not from the real host: a root-owned state directory, a root listener on a 0600 socket, uid/gid 65534 as client, dummy manifest. In that run the record was BLOCKED on ptrace (`/proc/sys/kernel/yama/ptrace_scope` absent, Yama not loaded) and FAIL on `qualification.client_socket_reachable` (a distinct-uid client cannot connect to a 0600 socket owned by the ingress uid). The ingress also ran as root, which the profile now rejects by default. The boundary is therefore **unqualified in that environment**, and nothing in this document changes that. A qualifying record must be captured on the real host, against the real running ingress, as the non-root ingress uid's configuration requires.

## Frozen profile

| Item | Frozen value |
|---|---|
| OS | Linux, single host, local filesystem with POSIX owner/mode enforcement (ext4, xfs, btrfs, tmpfs verified set; network, FUSE and FAT-family filesystems fail) |
| Interpreter | CPython 3.13 only. Python 3.11 stays unqualified. The interpreter that ran the capture must equal the ingress process executable (`/proc/<pid>/exe`); with no `--ingress-pid` this is BLOCKED |
| Ingress | One process, one uid, not root (`--allow-root-ingress` relaxes this for non-qualifying runs only); state directory `0700`, files `0600`, one owner |
| Supported client | A distinct, unprivileged uid and gid, no capabilities, reaching only the Unix socket through `tools.mvp_ingress.client:submit` |
| IPC | One Unix socket outside the state directory; mode `0600`, owner the ingress uid or the client uid; `0660` only with `--socket-group-policy dedicated` (group members limited to the ingress and client users); never any other-bits |
| ACLs | No POSIX ACL entries on the socket, the state tree or any ancestor of either |
| Ancestors | Every ancestor of the socket and state directory is owned by root or the ingress uid and is not group/other writable (unless sticky) |
| Ptrace | `kernel.yama.ptrace_scope >= 1` and the client holds no capabilities. If Yama is absent the check is BLOCKED, not PASS |
| Invocation | `simulate=None` hard-coded in the core; `operation_identity=True` in the executor construction |
| Journal mode | Declared SQLite journal mode for the destination and authority store, checked against the database file header |

A deployment that does not meet every row is outside the profile and is unqualified, not "partially qualified".

## Connectivity condition (open point)

A Unix socket needs write permission on the socket file to connect. A socket `0600` owned by the ingress uid is unreachable to a distinct-uid client, and the socket cannot sit inside the `0700` state directory. The capture reports this as FAIL on `qualification.client_socket_reachable`. A qualifying deployment therefore needs one of: the socket owned by the client uid (the ingress process or its launcher must set that without widening the mode), or mode `0660` with a dedicated group whose only members are the ingress and client users. Which of the two is adopted is an architect decision; the script verifies either but adopts neither silently. ACL-based grants are not allowed.

## The capture script

`python -m tools.mvp_ingress.capture_env_record` (standard library, Python 3.13) writes one deterministic JSON record (sorted keys, no timestamps or pids) with `record_sha256`. Exit status 0 PASS, 1 FAIL, 2 BLOCKED. Run it as root, against the running ingress (`--ingress-pid`), with the client identity, database paths, `--pin` source pins, `--manifest` files and `--journal-mode`. The `python` section describes the capture process (`sys.executable`); `python.interpreter_matches_ingress` FAILs when the ingress executable differs and is BLOCKED without `--ingress-pid`, so run the script with the interpreter the ingress uses.

Sections: `platform` (distro, kernel, arch, filesystem type and mount options of the state and socket directories), `python` (interpreter path and sha256, version, all installed distributions), `process_identity`, `ipc`, `filesystem` (stat of the state tree and ancestors), `invocation` (client entry point, hash and imports; AST check of `simulate`), `isolation_limits` (capabilities, yama, user namespaces, LSM, seccomp, no_new_privs), `configuration` (pins, manifest sha256, source sha256, journal mode declared and observed from file headers), `qualification` (client probe results).

Determinism: the record is a function of the host and the inputs, not of time. Kernel release and version, distro, interpreter path and hash, installed distributions, mounts and sysctl values, the ingress command line, and the command-line arguments are inputs; the same inputs give a byte-identical record. Ingress capabilities are recorded, not judged: only the client's capabilities are checked (must be empty). Manifests are keyed by base name; two `--manifest` files with the same base name are rejected (FAIL). Pins are validated (`name=hex`, 7 to 64 hex digits, no duplicates; malformed is FAIL); `manifest_sha256.<basename>=` and `source_sha256.<path>=` pins are compared with the computed digests (mismatch FAIL); any other pin, such as a component commit, cannot be compared by this script and is BLOCKED unless `--accept-unverified-pins` records it as declared only. `--journal-mode` must be one of wal, delete, truncate, persist and is compared with the SQLite file headers of the destination and the authority store. The `simulate` and `operation_identity` values in the record come from the static scan, not from constants; the scan is best-effort (an AST look at the checked-out sources) and does not see `getattr`, `**` forwarding or dynamic calls, and it is not proof about the running ingress.

The client probe is only conclusive if the client can reach the state directory: before probing, the script requires search (x) permission for the client on every ancestor of the state directory (judged from mode bits; ACLs are rejected separately). Otherwise the state-access check is BLOCKED ("denial may be due to traversal above the state dir"). A probe result other than EACCES/EPERM (for example ENOENT) is inconclusive and never counts as denied. Any exception inside a section becomes a BLOCKED `<section>.exception` check naming the exception type, and any exception escaping the capture makes `main` emit a BLOCKED record.

ACL caveat: an empty `listxattr` result is only meaningful if the filesystem can store POSIX ACLs at all. It is mitigated, not eliminated, by the filesystem allow-list (ext4, xfs, btrfs, tmpfs) and by rejecting `noacl` mounts; a kernel built without ACL support for such a filesystem would still read as empty. The script has no positive xattr-capability probe, because that would mutate the state tree.

Every check is PASS, FAIL or BLOCKED. BLOCKED means the check could not be made (not root, input not given, no xattr support, Yama absent) and is never counted as PASS. Overall is FAIL if any check fails, else BLOCKED if any is blocked, else PASS. ACLs are read as the `system.posix_acl_access` and `system.posix_acl_default` xattrs without following symlinks; `getfacl` is not required and its availability is only recorded. The client probe forks, drops to the client uid, gid and groups, and tries to list or open or stat the state files, unlink in the state directory, signal the ingress and open `/proc/<pid>/mem` and `environ`; each must be denied with EACCES or EPERM, and the socket must be writable by the client.

Not run by the script and still required as separate Qualification evidence: a live propose round trip and adversarial proposals through the client, and any Python 3.11 run.

## What is claimed

For a run whose record is overall PASS, on the exact recorded configuration: the checked ownership, mode, ACL, group, ancestor, ptrace-scope and capability preconditions held at capture time, and an unprivileged distinct-uid client was denied access to the state tree and to the ingress process by the operating system. Together with the existing `BOUNDARY.md` execution observations this is evidence toward the architect's conditional-sufficiency ruling for that profile only; it does not establish the ruling's conditions by itself.

## What is not claimed

- Resistance to root, to the ingress uid, to same-privilege code, or to direct database modification by an authorized file holder.
- Anything about kernels, containers, capability sets, LSM policies or filesystems other than the recorded ones.
- Continuity: the record is a point-in-time capture, not continuous monitoring. Ancestor and ACL state can change afterwards.
- Qualification, certification, security clearance, or production readiness. Production stays on HOLD.
- That the static AST scans are complete; they are best-effort.
- That the probe is exhaustive. It checks a fixed list of operations; it does not attempt ptrace attach, namespace escape or kernel exploits.

If an untested ACL or ptrace condition can invalidate the client's isolation and the record is BLOCKED or FAIL on it, the boundary is treated as unqualified for that environment.

## Tests

`tests/test_mvp_ingress_env_record.py` (tmp directories only) covers loosened state dir and file modes, a symlink, socket modes, same-uid and uid-0 clients, a writable ancestor, ACL entries on the state dir and a state file (skipped if the filesystem refuses ACLs), unreadable ACLs, yama values 0/1/2/absent, not-root probe, Python 3.11, a non-None `simulate`, a non-stdlib client import, missing pins, journal mismatch, determinism and fail-closed behaviour with no arguments.

Added after review: traversal-blocked probe, ENOENT not counted as denied, probe child failure, interpreter match and mismatch, ingress uid mismatch, section and main exception fail-closed, root ingress default, identity range, malformed and compared pins (including `source_sha256.<path>` pins with slashes and a wrong manifest digest), manifests sharing a base name, journal mode validation, scan-derived configuration values, group-writable ancestors (0770, 0720), and the 0660 dedicated-group policy (pass, extra member, gid 0).

The client-probe tests drop privileges and need root; they skip otherwise.
