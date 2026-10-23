# MVP trusted-host ingress: frozen Qualification environment profile and capture

Status: PROPOSED, non-authorizing. Release, publication and production remain on HOLD. This is not a Qualification verdict, a security clearance, a certification or a production-readiness claim. Basis: architect ruling that the trusted-host boundary is CONDITIONALLY SUFFICIENT for a fixed Linux + Python 3.13 profile, subject to the Qualification environment record below, and architect rulings #2 item 4, which fixes the environment profile (dedicated-group socket, Yama ptrace requirement, mandatory non-root ingress). Hub base `43c526eb`; ingress `tools/mvp_ingress/` with `BOUNDARY.md`.

## Evidence status

Captured on an actual run of the real `tools.mvp_ingress.server` (pinned Control Plane `0a41faa9`, Runtime `ec728da6`, pydantic 2.13.5, CPython 3.13.16) in a development container (Ubuntu 24.04.5, kernel 6.18.44-fc-v153, x86_64, ext4), as a dedicated non-root uid with no capabilities (`setpriv`, empty bounding set, `--no-new-privs`), a distinct client uid, an outsider uid, and a dedicated group `ocs-ipc` holding exactly the ingress and client users; socket `0660` owned by the ingress uid in a separate setgid IPC directory. The full record (29 PASS checks and the one BLOCKED) is committed as `ingress-env-record-dev-container-2026-10-23.json`, record_sha256 `5721693cbb8b20e6...`; its `claims` and `profile_supported: false` fields carry the verdict. Result: every check PASS except one. `isolation.ptrace_scope` is **BLOCKED**: `/proc/sys/kernel/yama/ptrace_scope` does not exist in this kernel, so Yama is not available and, per the architect ruling, **the exact profile is UNSUPPORTED in this environment and the boundary test is BLOCKED**. No weaker environment is substituted. The boundary is therefore not qualified here, and nothing in this document changes that.

Limits of this evidence: it is a development container, not the designated qualification host; the manifest digest used was a Control Plane example manifest, not a frozen manifest; the destination and the authority store are the same SQLite file (`atomic/refunds.sqlite3`) because route B keeps both there; component commits are declared pins, not verified against a checkout; the live propose round trip, the adversarial proposals and the supported-ingress lost-acknowledgment test are separate evidence not produced by this script.

**Evidence must be refreshed whenever the execution host, kernel, distro, filesystem, mount options, user/group configuration, capabilities, Yama or other relevant sysctl settings, interpreter, dependency versions or ingress sources change.** A record describes one configuration at one moment.

## Frozen profile

| Item | Frozen value |
|---|---|
| OS | Linux, single host, local filesystem with POSIX owner/mode enforcement (ext4, xfs, btrfs, tmpfs verified set; network, FUSE and FAT-family filesystems fail) |
| Interpreter | CPython 3.13 only. Python 3.11 stays unqualified. The interpreter that ran the capture must equal the ingress process executable (`/proc/<pid>/exe`); with no `--ingress-pid` this is BLOCKED |
| Ingress | One process under a dedicated non-root uid (mandatory, no relaxation flag), effective and permitted capabilities empty (FAIL on any, naming CAP_SYS_PTRACE, CAP_DAC_OVERRIDE, CAP_KILL, CAP_SETUID and similar); state directory `0700`, files `0600`, one owner; the process is verified by command line (`tools.mvp_ingress.server`), uid and executable |
| Supported client | A distinct, unprivileged uid and gid, no capabilities, reaching only the Unix socket through `tools.mvp_ingress.client:submit` |
| IPC | One Unix socket, mode exactly `0660`, owned by the ingress uid (client ownership is not allowed), group a dedicated group (not gid 0, not the ingress or client primary group) whose members plus primary-gid users are exactly the ingress and the designated client. The socket is in a separate IPC directory the client can traverse, outside the state directory, owned by root or the ingress uid and not group/other writable (sticky does not excuse it) so the socket cannot be replaced. Verified, not declared: effective mode/owner/group, actual membership, a real client connection, an outsider uid denied, and SO_PEERCRED from the client's connection equal to the ingress pid, uid and gid |
| ACLs | No POSIX ACL entries on the socket, the state tree or any ancestor of either |
| Ancestors | Every ancestor of the socket and state directory is owned by root or the ingress uid and is not group/other writable (unless sticky) |
| Ptrace | `kernel.yama.ptrace_scope >= 1`, plus the client holds no capabilities, the ingress process identity matches, and dumpability is recorded from the `/proc/<pid>` owner. This alone does not establish complete process isolation. If Yama is absent the profile is UNSUPPORTED and the boundary test is BLOCKED (`profile_supported: false`); a weaker environment is never substituted |
| Invocation | `simulate=None` hard-coded in the core; `operation_identity=True` in the executor construction |
| Journal mode | Declared SQLite journal mode for the destination and authority store, checked against the database file header |

A deployment that does not meet every row is outside the profile and is unqualified, not "partially qualified".

## Socket profile (architect ruling 4(a))

A Unix socket needs write permission on the socket file to connect. The frozen answer is mode `0660` with a dedicated group, created by the ingress inside a setgid IPC directory (owner ingress uid, group the dedicated group, mode `2750`) so the socket inherits the group without the ingress needing `CAP_CHOWN`. Client ownership of the socket is rejected: it would give the client control over a security-relevant filesystem entry. ACL-based grants are rejected by the ACL check.

## The capture script

`python -m tools.mvp_ingress.capture_env_record` (standard library, Python 3.13) writes one deterministic JSON record (sorted keys, no timestamps or pids) with `record_sha256`. Exit status 0 PASS, 1 FAIL, 2 BLOCKED. Run it as root, against the running ingress (`--ingress-pid`), with the actual client identity (`--client-uid`, `--client-gid`), an unrelated `--outsider-uid` (default 65533), database paths, `--pin` source pins, `--manifest` files and `--journal-mode`. The `python` section describes the capture process (`sys.executable`); `python.interpreter_matches_ingress` FAILs when the ingress executable differs and is BLOCKED without `--ingress-pid`, so run the script with the interpreter the ingress uses.

Sections: `platform` (distro, kernel, arch, filesystem type and mount options of the state and socket directories), `python` (interpreter path and sha256, version, all installed distributions), `process_identity`, `ipc`, `filesystem` (stat of the state tree and ancestors), `invocation` (client entry point, hash and imports; AST check of `simulate`), `isolation_limits` (capabilities, yama, user namespaces, LSM, seccomp, no_new_privs), `configuration` (pins, manifest sha256, source sha256, journal mode declared and observed from file headers), `qualification` (client and outsider probe results), and top-level `profile_supported`.

Determinism: the record is a function of the host and the inputs, not of time. Kernel release and version, distro, interpreter path and hash, installed distributions, mounts and sysctl values, the ingress command line, and the command-line arguments are inputs; the same inputs give a byte-identical record. The ingress must hold no effective or permitted capabilities and the client none; the privileged names found are listed in the detail. Manifests are keyed by base name; two `--manifest` files with the same base name are rejected (FAIL). Pins are validated (`name=hex`, 7 to 64 hex digits, no duplicates; malformed is FAIL); `manifest_sha256.<basename>=` and `source_sha256.<path>=` pins are compared with the computed digests (mismatch FAIL); any other pin, such as a component commit, cannot be compared by this script and is BLOCKED unless `--accept-unverified-pins` records it as declared only. `--journal-mode` must be one of wal, delete, truncate, persist and is compared with the SQLite file headers of the destination and the authority store. The `simulate` and `operation_identity` values in the record come from the static scan, not from constants; the scan is best-effort (an AST look at the checked-out sources) and does not see `getattr`, `**` forwarding or dynamic calls, and it is not proof about the running ingress.

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
- Resistance to members of the dedicated socket group other than the designated client (the group is verified to contain only the ingress and the client at capture time); resistance of the IPC channel itself to a compromised client beyond the closed protocol.
- That Yama or capabilities alone isolate the ingress process; they are preconditions, not proof.
- Evidence for any host other than the one captured; evidence is refreshed when the host or settings change.
- Qualification, certification, security clearance, or production readiness. Production stays on HOLD.
- That the static AST scans are complete; they are best-effort.
- That the probe is exhaustive. It checks a fixed list of operations; it does not attempt ptrace attach, namespace escape or kernel exploits.

If an untested ACL or ptrace condition can invalidate the client's isolation and the record is BLOCKED or FAIL on it, the boundary is treated as unqualified for that environment.

## Tests

`tests/test_mvp_ingress_env_record.py` (tmp directories only) covers loosened state dir and file modes, a symlink, socket modes, same-uid and uid-0 clients, a writable ancestor, ACL entries on the state dir and a state file (skipped if the filesystem refuses ACLs), unreadable ACLs, yama values 0/1/2/absent, not-root probe, Python 3.11, a non-None `simulate`, a non-stdlib client import, missing pins, journal mismatch, determinism and fail-closed behaviour with no arguments.

Added for architect rulings #2 item 4: socket mode variants, exact and primary-gid group membership, dedicated-group, owner and no-passwd cases, IPC directory separation and protection, Yama profile flag, ingress capability, dumpability and command-line checks, outsider and peer-credential probes (root-only, with real connections), and the root ingress failure. Each new check has a test for each outcome, and a mutation run of 18 single-condition mutations of the new checks was used to confirm the tests detect them.

Added after review: traversal-blocked probe, ENOENT not counted as denied, probe child failure, interpreter match and mismatch, ingress uid mismatch, section and main exception fail-closed, root ingress default, identity range, malformed and compared pins (including `source_sha256.<path>` pins with slashes and a wrong manifest digest), manifests sharing a base name, journal mode validation, scan-derived configuration values, group-writable ancestors (0770, 0720), and the 0660 dedicated-group policy (pass, extra member, gid 0).

The client-probe tests drop privileges and need root; they skip otherwise.
