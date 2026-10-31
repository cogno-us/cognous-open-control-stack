# QGATE-03 Worker A: H-01..H-30 reconciliation (original profile and controls)

Status: DRAFT, read-only extraction, non-authorizing. Not a Qualification verdict. Same-lineage output, NOT independent certification. Nothing here changes a requirement, the capture script, the launcher, or any hold. Holds preserved: F3 CLOSED (Q2/Q3 UNRESOLVED); Q7 NOT ESTABLISHED; candidate PROVISIONAL, UNFROZEN, UNQUALIFIED; Tier 1 DEFERRED, NOT WAIVED; publication/release/production HOLD. The runner is a PLATFORM HOST CANDIDATE; the profile is NOT fully qualified.

Basis: hub `/home/claude/cognous-open-control-stack`, branch `qgate-03/host-integration-feasibility`, base `ac08527306f5c1bfadc5a4c881d5b6d085a3cacf`. Every file below was OPENED in this session; citations are `file:line`, marked [V] verified by opening it, or UNVERIFIED. Abbreviations: PROFILE = docs/mvp-recovery/ingress-qualification-environment-profile.md; CER = tools/mvp_env_record/capture_env_record.py; MATRIX = docs/mvp-recovery/qgate-02/host-profile-requirements-matrix.md; BOUNDARY, LAUNCH, SERVER = tools/mvp_ingress/BOUNDARY.md, launch.py, server.py; REC = docs/mvp-recovery/ingress-env-record-dev-container-2026-10-23.json; RECON = docs/mvp-recovery/mvp-readiness-reconciliation-2026-10-30.md.

Label convention: SUPPLIED (operator, second-hand), DERIVED (my reading of CER logic, with a local run as cross-check), OBSERVED (I ran/read it), INFERENCE (my reading, not stated), UNVERIFIED.

## 0. Method and limits

- [V] The "exact requirement" column below is copied verbatim from the MATRIX criterion column by script (MATRIX lines 23-52, one row per H-id); it is not reworded. MATRIX line numbers were re-checked here against the same CER line numbers (CER:306-806 read in full; the matrix's cited lines match this checkout, whose CER sha256 is the one the matrix recorded: MATRIX:11, not recomputed by me, UNVERIFIED).
- SUPPLIED totals: 7 PASS / 23 BLOCKED / 1 FAIL, overall FAIL, profile_supported true. No per-id mapping is supplied and none is invented: the "QGATE-02 status" column says "per-id UNKNOWN" and gives only the DERIVED expectation.
- Acceptance rule applied as given: PASS only if all 31 checks PASS; any FAIL = REJECT; any BLOCKED = INCOMPLETE. Nothing further is derived.
- Check-id vocabulary: CER can emit 34 fixed ids; the committed REC holds 31 [V, REC parsed: 31 checks, overall BLOCKED, profile_supported false, only isolation.ptrace_scope BLOCKED]. The REC set lacks filesystem.state_dir_present, filesystem.socket_present, qualification.outsider_denied_by_ipc_directory. A fully configured run emits the REC set (31) when the outsider can traverse the IPC dir, and 32 ids when the IPC dir blocks the outsider (section 5, point 1).

## 1. DERIVED expected result of the QGATE-02 no-ingress run

Assumed invocation (DERIVED from the supplied facts): unmodified CER as root, `--state-dir` and `--socket` under `/opt/qgate02-nonexistent`, `--label` given, NO `--ingress-pid`, and not all of `--ingress-uid/--ingress-gid/--client-uid/--client-gid` given. Reason for the last assumption: counting emitted ids, `identity.client_distinct_unprivileged` and `identity.ingress_not_root` are emitted only when `identity.declared` PASSes (CER:393-401); without them the nonexistent-path run emits exactly 31 ids, matching 7+23+1. With all four ids declared, my local run emitted 28 checks including `filesystem.exception` and `isolation_limits.exception` (FileNotFoundError on `os.lstat` of the nonexistent ancestors), which does not match 31 (OBSERVED locally, throwaway run in the scratchpad; no repo file written). Note the supplied "synthetic UID separation observed" therefore most plausibly refers to the runner probe, not to capture flags (INFERENCE).

OBSERVED cross-check: the same invocation on this sandbox (no /opt ACL, no Yama) gave 31 checks: 6 PASS / 25 BLOCKED. Adding Yama = 1 (PASS) and an ACL on an /opt ancestor (BLOCKED to FAIL) gives 7 / 23 / 1, exactly the supplied totals. The mapping is DERIVED, not proof;.

DERIVED PASS (7): capture.evidence_label, platform.linux, python.profile, isolation.ptrace_scope, invocation.client_entry_point, invocation.simulate_fixed_none, invocation.operation_identity_fixed_true.
DERIVED FAIL (1): filesystem.no_acl_entries (see H-22).
DERIVED BLOCKED (23): configuration.journal_mode, configuration.pins_and_manifests, filesystem.ancestors_not_writable_by_others, filesystem.no_extra_group_access, filesystem.socket_present, filesystem.state_dir_present, filesystem.state_tree_owner_only, identity.declared, identity.ingress_command, identity.ingress_process, ipc.directory_separate_and_protected, ipc.peer_credentials, ipc.socket_mode_owner_group, isolation.ingress_capabilities, isolation.ingress_dumpability, platform.fs_enforces_unix_perms.socket_dir, platform.fs_enforces_unix_perms.state_dir, python.interpreter_matches_ingress, qualification.client_capabilities_empty, qualification.client_denied_ingress_process, qualification.client_denied_state_access, qualification.client_socket_reachable, qualification.outsider_denied_socket.
Roll-up: FAIL present, so overall FAIL, exit 1; profile_supported true (Yama 1). Preserve: this original failure is not waived by anything below.

## 2. Per-requirement table

Columns: exact requirement (verbatim MATRIX criterion); capture check id(s); QGATE-02 status (per-id UNKNOWN; DERIVED expectation for the no-ingress run); QGATE-03 reachability and inputs. "Reachable" means the check can return PASS/FAIL (not BLOCKED) in a QGATE-03 run configured as in section 4; whether it PASSes is not claimed unless stated.

### H-01 (Kernel / OS) [MATRIX:23, V]

- Exact requirement (verbatim): "Linux, single host, local filesystem with POSIX owner/mode enforcement". Single host also: CAPS "Linux, CPython 3.13, single host".
- Governing source (per MATRIX): PROFILE:19; CAPS:6; MANIFEST:18
- Capture check id(s): platform.linux
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: PASS (runner is Linux)
- QGATE-03: Reachable, unchanged: PASS. No input. 'Single host' is declarative and NOT observable (script tests OS name only, CER:335-338).

### H-02 (Kernel / OS (distro, kernel)) [MATRIX:24, V]

- Exact requirement (verbatim): No distro or kernel version is required by the profile. The only evidence is the dev container: "Ubuntu 24.04.5, kernel 6.18.44-fc-v153, x86_64, ext4". R3 item 8 requires the record to cover "platform (distribution, kernel, architecture, filesystem type)".
- Governing source (per MATRIX): PROFILE:7; R3:94; REC `platform`
- Capture check id(s): none (recording only, CER:331-334)
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: n/a (no check)
- QGATE-03: NOT observable as a check. Distro/kernel/arch are recorded in `platform`; nothing constrains them. Declarative. Evidence = the record fields.

### H-03 (Filesystem) [MATRIX:25, V]

- Exact requirement (verbatim): "ext4, xfs, btrfs, tmpfs verified set; network, FUSE and FAT-family filesystems fail"; `noacl` mounts rejected. Applies to the state directory and socket directory mounts. Unlisted filesystem types are BLOCKED.
- Governing source (per MATRIX): PROFILE:19, 46; CER:47-48 (sets)
- Capture check id(s): platform.fs_enforces_unix_perms.state_dir; platform.fs_enforces_unix_perms.socket_dir
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED x2 (paths under /opt/qgate02-nonexistent do not exist, so mountinfo is None, CER:330,341)
- QGATE-03: Reachable once the real state dir and the socket's directory exist (`--state-dir`, `--socket`; the socket file itself need not exist, the check uses `dirname(sock)`). PASS only on ext4/xfs/btrfs/tmpfs without `noacl`; FAIL on fuse/nfs/vfat etc.; BLOCKED on any other type (e.g. overlay) (CER:342-347). The base path must therefore sit on a verified-set mount. Which fstype the hosted runner offers is UNVERIFIED.

### H-04 (Interpreter) [MATRIX:26, V]

- Exact requirement (verbatim): "CPython 3.13 only. Python 3.11 stays unqualified."
- Governing source (per MATRIX): PROFILE:20; CAPS:6, 17; R3:92
- Capture check id(s): python.profile
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: PASS (assumes the runner interpreter used was CPython 3.13; it is the only way the supplied 7 PASS can be reached, see section 1)
- QGATE-03: Reachable, same result: PASS iff the capture interpreter is CPython 3.13. Input: run the capture with the 3.13 interpreter (must also be the ingress interpreter, H-05).

### H-05 (Interpreter (ingress equality)) [MATRIX:27, V]

- Exact requirement (verbatim): "The interpreter that ran the capture must equal the ingress process executable (`/proc/<pid>/exe`); with no `--ingress-pid` this is BLOCKED".
- Governing source (per MATRIX): PROFILE:20, 38; CER:362-363
- Capture check id(s): python.interpreter_matches_ingress
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (no --ingress-pid, CER:429-430)
- QGATE-03: Reachable with `--ingress-pid`: PASS iff realpath(/proc/PID/exe) == realpath(sys.executable) (CER:428-436). Inputs: PID of the python process itself (not a sudo/shell wrapper), capture launched with the same interpreter path (absolute path; under sudo the PATH differs, so do not rely on `python`).

### H-06 (Interpreter / dependencies) [MATRIX:28, V]

- Exact requirement (verbatim): Exact interpreter and dependency versions recorded; dependency hash lock in `dependency-manifest.md`. Hub script records all installed distributions and `pydantic_installed`; no check compares them to the lock.
- Governing source (per MATRIX): R3:94; CER:351-368; QINIT:11
- Capture check id(s): none (recording only, CER:351-368)
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: n/a (no check)
- QGATE-03: NOT observable by the capture script: distributions and `pydantic_installed` are recorded, never compared with `docs/mvp-package/requirements-mvp-py313.txt`. Comparison is outside the 31 checks (matrix says the Qualification gate; gate UNAVAILABLE). Any lock comparison B performs is supplementary evidence, not an acceptance check.

### H-07 (Launcher / ingress support) [MATRIX:29, V]

- Exact requirement (verbatim): Only supported start command: `python -I tools/mvp_ingress/launch.py --state-dir DIR --socket PATH --control-plane ROOT --runtime ROOT --allow-uid UID`; `-m tools.mvp_ingress.server` "is no longer a supported entry point" and the record "marks it non-compliant".
- Governing source (per MATRIX): BOUNDARY:74, 13; MANIFEST:82, 85; server.py:230-233 (refuses `__main__`)
- Capture check id(s): identity.ingress_command
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (no --ingress-pid, CER:410-411)
- QGATE-03: Reachable with `--ingress-pid`: FAIL unless cmdline contains the ABSOLUTE path of `<repo-root>/tools/mvp_ingress/launch.py`, `-I` before it, and `--allow-uid` values equal (as a sorted set) to the declared `--allow-uid` values; PASS otherwise (CER:414-427). Inputs: ingress started exactly as in section 4, `--allow-uid` repeated identically on the capture command, `--repo-root` equal to the checkout the launcher was run from (default = the script's own checkout, CER:819). Tokens are split on whitespace, so paths with spaces break the match (CER:415).

### H-08 (Launcher (isolation)) [MATRIX:30, V]

- Exact requirement (verbatim): `-I` drops cwd, script dir, `PYTHON*` and user site; private `sys.pycache_prefix`; refuses if bytecode present; every ingress module must load from the committed `.py` of this checkout; hash-locked dependencies must be in the interpreter's own site-packages.
- Governing source (per MATRIX): BOUNDARY:77-80; launch.py:31-38, 67-94
- Capture check id(s): none
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: n/a (no check)
- QGATE-03: NOT a capture check. Enforced by launch.py at start (exit 2 on refusal: launch.py:36-38, 83-85, 87, 94). Indirect evidence only: the ingress prints READY (server.py:220) and stays up. A pre-existing `__pycache__` or `.pyc` under `tools/mvp_ingress` makes the launcher refuse (launch.py:83-85), so no step before the launch may byte-compile that directory. Launcher accepts >= 3.11 (launch.py:36); 3.13 only via H-04/H-05.

### H-09 (Process and UID separation (ingress)) [MATRIX:31, V]

- Exact requirement (verbatim): "One process under a dedicated non-root uid (mandatory, no relaxation flag)"; process verified "by command line, uid and executable"; real, effective and saved uid equal the ingress uid.
- Governing source (per MATRIX): PROFILE:21; CER:402-409
- Capture check id(s): identity.declared; identity.ingress_not_root; identity.ingress_process
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: identity.declared BLOCKED (CER:389-390); identity.ingress_not_root NOT EMITTED (only emitted when identity.declared passes, CER:393-401); identity.ingress_process BLOCKED (CER:408-409)
- QGATE-03: identity.declared / identity.ingress_not_root: reachable with `--ingress-uid` `--ingress-gid` `--client-uid` `--client-gid` (or `--ingress-pid`, which derives ingress uid/gid from /proc/PID/status, CER:380-383); declarative arithmetic, not process evidence. identity.ingress_process: needs `--ingress-pid`; PASS iff real/effective/saved uid all equal the ingress uid (CER:406-407). Ingress uid must not be 0.

### H-10 (Process and UID separation (client)) [MATRIX:32, V]

- Exact requirement (verbatim): "A distinct, unprivileged uid and gid, no capabilities, reaching only the Unix socket through `tools.mvp_ingress.client:submit`." Client uid not equal to ingress uid, not 0, client gid not ingress gid.
- Governing source (per MATRIX): PROFILE:22; BOUNDARY:51, 98
- Capture check id(s): identity.client_distinct_unprivileged; qualification.client_capabilities_empty; invocation.client_entry_point
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: client_distinct NOT EMITTED (same reason as ingress_not_root); client_capabilities_empty BLOCKED (CER:668-670, client identity not given); invocation.client_entry_point PASS (static scan of the hub's client.py)
- QGATE-03: client_distinct: reachable with client + ingress uid/gid (client uid != ingress uid, != 0, client gid != ingress gid). client_capabilities_empty: reachable as ROOT with `--client-uid --client-gid --socket --state-dir` (the probe forks, drops to the client uid, reads CapEff of the child, CER:209-228, 676). It proves the probe child dropped privileges, not that a real client runs capability-free (INFERENCE). invocation.client_entry_point: PASS now and later (needs `--repo-root`).

### H-11 (Peer-UID allowlist) [MATRIX:33, V]

- Exact requirement (verbatim): Mandatory: `--allow-uid UID` (repeatable); the ingress "refuses to start before touching state" without it; the ingress's own uid is not implicitly allowed; peer credentials read via `SO_PEERCRED` and checked before any request byte is read. The capture script requires the ingress command-line `--allow-uid` values to equal the declared `--allow-uid` values.
- Governing source (per MATRIX): BOUNDARY:41, 13, 82; server.py:148-156, 160-176, 203-208; MANIFEST:82
- Capture check id(s): identity.ingress_command (allow-uid equality only)
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED
- QGATE-03: Reachable only as equality of the ingress cmdline `--allow-uid` values with the declared ones (CER:424-425), see H-07. NOT observable by the capture: that the ingress actually refuses non-allowed peers before reading a byte (server.py:160-176; behaviour belongs to tests, not the record), and that the allow list contains the client uid (not checked). `ipc.connection_policy.peer_uid_allow_list` is recorded from the flag (CER:441). The ingress's own uid is not implicitly allowed (BOUNDARY:41).

### H-12 (Process capabilities) [MATRIX:34, V]

- Exact requirement (verbatim): "effective and permitted capabilities empty (FAIL on any, naming CAP_SYS_PTRACE, CAP_DAC_OVERRIDE, CAP_KILL, CAP_SETUID and similar)"; client "no capabilities".
- Governing source (per MATRIX): PROFILE:21, 22, 42; CER:606-608
- Capture check id(s): isolation.ingress_capabilities; qualification.client_capabilities_empty
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: both BLOCKED (CER:610; client probe inputs missing)
- QGATE-03: isolation.ingress_capabilities: reachable with `--ingress-pid`; FAIL if CapEff or CapPrm nonzero (CER:606-608). Needs an ingress that really holds none (non-root uid after exec; REC evidence used `setpriv`, empty bounding set, no-new-privs, PROFILE:7). client part: see H-10. CapInh, CapAmb, CapBnd, NoNewPrivs, Seccomp are NOT tested (recorded only, CER:589, 604-605); not observable as pass/fail.

### H-13 (Ptrace / Yama) [MATRIX:35, V]

- Exact requirement (verbatim): "`kernel.yama.ptrace_scope >= 1`"; "If Yama is absent the profile is UNSUPPORTED and the boundary test is BLOCKED (`profile_supported: false`); a weaker environment is never substituted." CAPS: "If Yama is unavailable the profile is unsupported and the boundary test is BLOCKED; no weaker substitute."
- Governing source (per MATRIX): PROFILE:26, 7; CAPS:22; MANIFEST:89; QINIT:17
- Capture check id(s): isolation.ptrace_scope
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: PASS (operator-supplied fact: ptrace_scope = 1; value 1/2/3 PASS, CER:596-598)
- QGATE-03: Reachable, unchanged: PASS while the value is 1-3 at capture time. Absent -> BLOCKED + profile_supported=false; 0 -> FAIL (CER:593-601). No sysctl change is allowed (common fields), so the value is whatever the runner has; re-read at capture time, not assumed.

### H-14 (Ptrace / dumpability) [MATRIX:36, V]

- Exact requirement (verbatim): "dump-owner consistency is recorded from the `/proc/<pid>` owner (`isolation.ingress_dumpability`; this is consistency, not proof of isolation ...)". "This alone does not establish complete process isolation."
- Governing source (per MATRIX): PROFILE:26, 62; CAPS:22
- Capture check id(s): isolation.ingress_dumpability
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (CER:622-623)
- QGATE-03: Reachable with `--ingress-pid` and an ingress uid: PASS iff owner of /proc/PID is the ingress uid or root (CER:611-621). Consistency only, not isolation (PROFILE:26).

### H-15 (Process isolation (denials)) [MATRIX:37, V]

- Exact requirement (verbatim): The unprivileged client is denied, by EACCES/EPERM: listing/open/stat of state files, unlink in the state dir, signalling the ingress (`kill 0`), and opening `/proc/<pid>/mem` and `/proc/<pid>/environ`; the socket must be writable by the client.
- Governing source (per MATRIX): PROFILE:48, 26
- Capture check id(s): qualification.client_denied_state_access; qualification.client_denied_ingress_process; qualification.client_socket_reachable
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: all BLOCKED (CER:667-670)
- QGATE-03: Reachable as ROOT with: `--client-uid --client-gid --state-dir --socket --ingress-pid`; `--db`, `--authority-store`, `--ledger` (each existing path becomes an open/stat probe, CER:445, 251-253). client_socket_reachable needs a LISTENING ingress with the client allowed to connect (mode 0660 + dedicated group). client_denied_state_access is BLOCKED if the client lacks `x` on any ancestor of the state dir (CER:660-664, 691) and on any non-EACCES/EPERM result (CER:694-695). client_denied_ingress_process needs the PID (kill 0, /proc/PID/mem, /proc/PID/environ, CER:254-257). The probes consume one accept (client) of the ingress (CER:11-13).

### H-16 (Socket permissions) [MATRIX:38, V]

- Exact requirement (verbatim): "One Unix socket, mode exactly `0660`, owned by the ingress uid (client ownership is not allowed), group a dedicated group (not gid 0, not the ingress or client primary group) whose members plus primary-gid users are exactly the ingress and the designated client."
- Governing source (per MATRIX): PROFILE:23, 34; CER:51, 506-529
- Capture check id(s): ipc.socket_mode_owner_group
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (socket missing, CER:528-529)
- QGATE-03: Reachable with a live socket plus `--ingress-uid/--ingress-gid` (or pid) and `--client-uid/--client-gid`: needs mode exactly 0660 (ingress must be started with `--socket-mode 660`, default is 600, server.py:202), owner = ingress uid, group = a dedicated group (not 0, not ingress gid, not client gid) whose members from every /etc/group entry plus primary-gid users from passwd equal exactly {ingress user, client user} (CER:504-527). Ingress and client uids need passwd entries, else BLOCKED (CER:517-518); passwd must be enumerable (CER:522-523). Group + users are created by the runner setup (B).

### H-17 (IPC directory) [MATRIX:39, V]

- Exact requirement (verbatim): Socket in "a separate IPC directory the client can traverse, outside the state directory, owned by root or the ingress uid and not group/other writable (sticky does not excuse it)". Frozen socket profile text: "setgid IPC directory (owner ingress uid, group the dedicated group, mode `2750`) so the socket inherits the group without the ingress needing `CAP_CHOWN`".
- Governing source (per MATRIX): PROFILE:23, 34; REC `filesystem.ancestors` (`/opt/ocs-real/ipc` mode 2750, uid 30033, gid 30004)
- Capture check id(s): ipc.directory_separate_and_protected
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (CER:541-542)
- QGATE-03: Reachable once the IPC directory and state dir exist and an ingress uid is known (the socket file need not exist): FAIL if the IPC dir is the state dir or inside it, owner not root/ingress, or mode & 022 (CER:530-540). The check does NOT test the exact mode, the setgid bit or the group. Profile text says setgid, owner ingress uid, group dedicated, 2750 (PROFILE:34); see section 5 on 2751.

### H-18 (Outsider denial) [MATRIX:40, V]

- Exact requirement (verbatim): "Outsider denial counts for the socket only if the outsider can traverse every ancestor including the IPC directory; otherwise `qualification.outsider_denied_socket` is BLOCKED ('not conclusive for the socket') and `qualification.outsider_denied_by_ipc_directory` records that directory-level denial is what was proven." Verified: "an outsider uid denied", default outsider uid 65533.
- Governing source (per MATRIX): PROFILE:9, 23, 44; CER:636-659, 817 (`--outsider-uid` default)
- Capture check id(s): qualification.outsider_denied_socket; qualification.outsider_denied_by_ipc_directory
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: outsider_denied_socket BLOCKED (CER:634-635 / 641-642); outsider_denied_by_ipc_directory NOT EMITTED
- QGATE-03: Reachable as ROOT with a live socket and `--outsider-uid` (default 65533; must not be the ingress, the client, or a member of the socket group, else FAIL, CER:637-640). Outcome depends on the IPC dir mode: if the outsider lacks `x` on any ancestor (e.g. 2750) -> outsider_denied_socket = BLOCKED and outsider_denied_by_ipc_directory = PASS (CER:652-656), i.e. the run cannot be overall PASS; if the outsider can traverse every ancestor -> socket's own mode/group decides, PASS when denied (CER:657-659). With 2750 the ids emitted are 32 (REC set + outsider_denied_by_ipc_directory), see section 5.

### H-19 (Peer credentials) [MATRIX:41, V]

- Exact requirement (verbatim): "SO_PEERCRED from the client's connection equal to the ingress pid, uid and gid".
- Governing source (per MATRIX): PROFILE:23
- Capture check id(s): ipc.peer_credentials
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (CER:681-682 / probe inputs missing)
- QGATE-03: Reachable with a live socket, a successful client connection and `--ingress-pid`: PASS iff SO_PEERCRED (pid, uid, gid) on the client's connection equals ingress pid/uid/gid (CER:683-687). The pid must be the listening python process.

### H-20 (State-directory permissions) [MATRIX:42, V]

- Exact requirement (verbatim): "state directory `0700`, files `0600`, one owner"; no symlinks or special files; no group/other bits; owner = ingress uid.
- Governing source (per MATRIX): PROFILE:21; BOUNDARY:19
- Capture check id(s): filesystem.state_tree_owner_only
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (state dir missing, CER:477-478)
- QGATE-03: Reachable once the ingress has created/used its state tree and the ingress uid is known: every dir 0700, every file 0600, owner = ingress uid, no symlinks/special files, no group/other bits (CER:460-476). Checks the tree AS FOUND; every file the ingress and SQLite leave (socket.lock, ingress.db, atomic/refunds.sqlite3 and any -wal/-shm sidecar) is part of it; a loose mode is a genuine FAIL, not a defect of the check (modes not observed by me, UNVERIFIED).

### H-21 (State-directory group access) [MATRIX:43, V]

- Exact requirement (verbatim): Client's groups grant nothing on the state tree (group bits).
- Governing source (per MATRIX): PROFILE:48 (implicit); CER:544-557
- Capture check id(s): filesystem.no_extra_group_access
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (CER:556-557)
- QGATE-03: Reachable with the state tree present, ingress uid and client uid/gid known; client uid needs a passwd entry (else BLOCKED, CER:546-547). FAIL if a client group matches a state-tree entry's gid with any group bit set (CER:553).

### H-22 (ACLs) [MATRIX:44, V]

- Exact requirement (verbatim): "No POSIX ACL entries on the socket, the state tree or any ancestor of either." ACL grants are rejected.
- Governing source (per MATRIX): PROFILE:24, 34, 46
- Capture check id(s): filesystem.no_acl_entries
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: FAIL (DERIVED: consistent with the supplied 'ACL entry under /opt'). ACL presence is tested before unreadability (CER:566-576), so FAIL means at least one path among /opt/qgate02-nonexistent/ipc, /opt/qgate02-nonexistent, /opt, / carries system.posix_acl_access or system.posix_acl_default; the nonexistent children could only give BLOCKED (ENOENT = unreadable).
- QGATE-03: Reachable: PASS iff NO ancestor of the actual socket and state paths up to `/`, and no socket/state-tree entry, carries a POSIX ACL xattr (CER:559-578). Needs the real `--state-dir` / `--socket` paths. Depends on where the paths are placed: a base under an ACL-bearing ancestor reproduces the QGATE-02 FAIL. ACL removal/weakening is forbidden (common fields), so the only legal lever is the choice of path (section 6). Which runner directories carry ACLs is UNVERIFIED (not readable here).

### H-23 (Ancestors) [MATRIX:45, V]

- Exact requirement (verbatim): "Every ancestor of the socket and state directory is owned by root or the ingress uid and is not group/other writable. The sticky exemption is deliberate and narrow: only a sticky, root-owned ancestor that is not the direct parent of the socket or state dir (for example `/tmp`)."
- Governing source (per MATRIX): PROFILE:25; BOUNDARY:56-57; server.py:73-88
- Capture check id(s): filesystem.ancestors_not_writable_by_others
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (CER:495-496, ingress uid not given)
- QGATE-03: Reachable with `--socket`, `--state-dir` and an ingress uid: FAIL if any ancestor of either path is not a directory owned by root/ingress uid, or is group/other-writable unless (sticky AND root-owned AND not the direct parent of socket or state dir) (CER:480-494). The socket file need not exist. See section 6 for `/opt`.

### H-24 (Invocation constraints) [MATRIX:46, V]

- Exact requirement (verbatim): "`simulate=None` hard-coded in the core; `operation_identity=True` in the executor construction."
- Governing source (per MATRIX): PROFILE:27, 42; BOUNDARY:23, 70
- Capture check id(s): invocation.simulate_fixed_none; invocation.operation_identity_fixed_true; invocation.client_entry_point
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: PASS x3 (static AST scans of the hub checkout, CER:719, 727-728)
- QGATE-03: Reachable, unchanged: PASS (also OBSERVED locally on this checkout, section 1). Best-effort static scan only, not proof about the running ingress (PROFILE:42).

### H-25 (Journal mode) [MATRIX:47, V]

- Exact requirement (verbatim): "Declared SQLite journal mode for the destination and authority store, checked against the database file header." `--journal-mode` one of wal, delete, truncate, persist.
- Governing source (per MATRIX): PROFILE:28, 42; CER:46, 785-795
- Capture check id(s): configuration.journal_mode
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (CER:787-788)
- QGATE-03: Reachable with `--journal-mode wal` plus existing SQLite files given as `--db` and/or `--authority-store` (`--ledger` is recorded only, not enforced, CER:792). The synthetic ingress constructs `<state-dir>/atomic/refunds.sqlite3` at startup (synthetic_host.py:125; Runtime constructor creates the table, /tmp/claude-0/rt/engine/operation_identity_atomic_destination.py:26-33 at c5e97e87), so the file should exist before the capture; WAL mode of that file is INFERENCE from REC (both stores `wal`) because I did not find the PRAGMA in the destination class. Header check: wal = bytes 18 and 19 == 2; delete/truncate/persist are indistinguishable (CER:288-290). Destination and authority store are the same file in route B (PROFILE:11).

### H-26 (Host identity: evidence label) [MATRIX:48, V]

- Exact requirement (verbatim): `--label` "is required (what environment, which manifest, qualified or not); without it `capture.evidence_label` is BLOCKED and the record cannot PASS."
- Governing source (per MATRIX): PROFILE:42; CER:309-314, 820
- Capture check id(s): capture.evidence_label
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: PASS (this is one of the 7; the run must have passed `--label`)
- QGATE-03: Reachable: PASS iff `--label` non-empty (CER:309-314). Declarative text, never FAIL. Input: `--label` stating hosted-runner synthetic run, not the qualification host, boundary not qualified.

### H-27 (Provenance: pins and manifests) [MATRIX:49, V]

- Exact requirement (verbatim): Pins validated (`name=hex`, 7-64 hex digits, no duplicates); `manifest_sha256.<basename>=` and `source_sha256.<path>=` pins compared with computed digests; any other pin (component commit) "cannot be compared by this script and is BLOCKED unless `--accept-unverified-pins` records it as declared only". At least one `--pin` and one readable `--manifest` required.
- Governing source (per MATRIX): PROFILE:42; PROFILE:11 ("component commits are declared pins, not verified against a checkout"); CER:733-784
- Capture check id(s): configuration.pins_and_manifests
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: BLOCKED (no pins, no manifest, CER:779-780)
- QGATE-03: Reachable with `--pin name=hex` (7-64 hex, no duplicates), `--manifest FILE`. `manifest_sha256.<basename>=<sha256>` and `source_sha256.<repo-relative path>=<sha256>` pins are COMPARED (FAIL on mismatch). Component-commit pins (`control_plane=7a4bcd40...`, `runtime=c5e97e87...`) cannot be compared by the script: BLOCKED unless `--accept-unverified-pins`, then PASS with the pins recorded as 'declared only' (CER:765-784). So a PASS here does NOT verify the Control Plane / Runtime checkouts. Candidate manifest sha256 (OBSERVED now): 64ea8304fcc3c68917d87fba44c32178c129abf5622751feef08e83ce740ad04 (docs/mvp-package/candidate-manifest.json).

### H-28 (Provenance: record hash and envelope) [MATRIX:50, V]

- Exact requirement (verbatim): Record is deterministic (sorted keys, no timestamps or pids) with `record_sha256`; exit status 0 PASS, 1 FAIL, 2 BLOCKED. Overall FAIL if any FAIL, else BLOCKED if any BLOCKED, else PASS.
- Governing source (per MATRIX): PROFILE:38, 42, 48; CER:797-806, 839
- Capture check id(s): none (record_sha256 and exit status are computed over the record, CER:797-806, 839)
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: n/a (no check; derived run exit status 2 locally, would be 1 on the runner because of the FAIL)
- QGATE-03: NOT a check. Overall: FAIL if any FAIL, else BLOCKED if any BLOCKED, else PASS; exit 1/2/0. The acceptance rule given for QGATE-03 (PASS only if all 31 checks PASS; any FAIL REJECT; any BLOCKED INCOMPLETE) is a mapping of that roll-up, not something the script emits. 'Envelope' is not a term in the script or profile (UNVERIFIED).

### H-29 (Freshness and scope) [MATRIX:51, V]

- Exact requirement (verbatim): "Evidence must be refreshed whenever the execution host, kernel, distro, filesystem, mount options, user/group configuration, capabilities, Yama or other relevant sysctl settings, interpreter, dependency versions or ingress sources change." A capture at the refrozen tuple is required before it counts.
- Governing source (per MATRIX): PROFILE:9, 13, 63
- Capture check id(s): none
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: n/a (no check)
- QGATE-03: NOT observable by the script. Satisfied only in the sense that a new capture at the refrozen tuple is produced by the QGATE-03 run; the script records no pins unless given (H-27).

### H-30 (Not-run-by-script evidence) [MATRIX:52, V]

- Exact requirement (verbatim): Separate Qualification evidence still required: "a live propose round trip and adversarial proposals through the client, and any Python 3.11 run".
- Governing source (per MATRIX): PROFILE:50; CER:631-633
- Capture check id(s): none
- QGATE-02 status: per-id UNKNOWN (totals only). DERIVED for the no-ingress run: n/a (no check)
- QGATE-03: NOT observable in an environment-only scope: live propose round trip, adversarial proposals via the client, Python 3.11 run are separate Qualification evidence (PROFILE:50, CER:631-633). Out of scope for QGATE-03 (no refund battery).

## 3. What stays unobservable in an environment-only scope

Even with a real ingress, state tree, socket, client uid, outsider uid, pins and manifests, the capture script cannot produce a PASS/FAIL for:
- H-02 (distro/kernel/arch), H-28 (record hash and exit status), H-29 (freshness) and the "single host" part of H-01: declarative; recorded, not checked.
- H-06: no comparison with the hash lock (only recorded distributions).
- H-08: launcher internals; only indirect (READY printed, process alive).
- H-11 (behavioural part): that non-allowed peers are refused; allow list must contain the client; only cmdline equality is checked.
- H-12 extras: CapInh, CapAmb, CapBnd, NoNewPrivs, Seccomp are recorded, not tested.
- H-14: consistency only, not isolation (PROFILE:26, 62).
- H-24: static scan only (PROFILE:42, 65).
- H-27: component commits (control_plane, runtime) cannot be compared; at best "declared only" with `--accept-unverified-pins`. Pin of the Runtime checkout used (OBSERVED: /tmp/claude-0/rt HEAD = c5e97e87dd239c821b1b4a406a55dcd03c5bc61f, matches the supplied pin) is outside the script's view.
- H-30: live propose round trip, adversarial proposals, Python 3.11: separate Qualification evidence; out of scope.
- Anything about continuity: the record is point-in-time (PROFILE:60).
- Evidence needing the Qualification gate (`mvp_acceptance_gate.py`, UNAVAILABLE; MATRIX:14): verdict mapping beyond the stated acceptance rule is not derived here.

## 4. Proposed command lines (PROPOSAL; B owns the script)

Preconditions (all INFERENCE from CER/SERVER/LAUNCH, verified by reading, not by running an ingress):
- Everything runs as root (`sudo`). The capture needs euid 0 to fork and `setresuid` into the client/outsider uids; otherwise client_capabilities_empty, client_socket_reachable, ipc.peer_credentials, client_denied_state_access, client_denied_ingress_process and outsider_denied_socket are BLOCKED (CER:214-215, 667-670). The ingress itself must NOT be root (identity.ingress_not_root FAIL, CER:401) and must hold empty CapEff/CapPrm.
- Use ONE absolute interpreter path (CPython 3.13, hash-locked dependencies installed in that interpreter's own site-packages, since `-I` ignores PYTHONPATH, BOUNDARY:77) for both the ingress and the capture: python.interpreter_matches_ingress compares realpath(/proc/PID/exe) with realpath(sys.executable) (CER:428-436). `sudo` resets PATH, so a bare `python` may resolve elsewhere.
- No `__pycache__` or `.pyc` may exist under `tools/mvp_ingress` (LAUNCH:83-85).
- The ingress uid needs read access to the checkout, Control Plane root and Runtime root. The client uid needs `x` on every ancestor of the state dir and the IPC dir; the outsider needs `x` on every ancestor only if its denial is to be conclusive for the socket (CER:647, 660-664).
- Directories prepared before launch (B): base dir root-owned, not go+w, no ACL; `STATE` mode 0700 owned by the ingress uid (the server also creates it, SERVER:90-97); `IPC` outside STATE, owner ingress uid, group = dedicated group, setgid, mode per section 5 (PROFILE:34 says 2750); dedicated group with exactly two members (ingress, client user), outsider not in it.

Launcher form (matches BOUNDARY:74, LAUNCH:5, SERVER:11; the capture requires exactly this shape, CER:416-427):
```
setpriv --reuid=$ING_UID --regid=$ING_GID --clear-groups --bounding-set=-all --inh-caps=-all --no-new-privs \
  $PY -I $REPO/tools/mvp_ingress/launch.py \
  --state-dir $BASE/state --socket $BASE/ipc/ingress.sock \
  --control-plane $CP_ROOT --runtime $RT_ROOT \
  --socket-mode 660 --allow-uid $CLIENT_UID --max-requests 4 &
ING_PID=$!   # setpriv execs, so $! is the python process; do NOT capture the PID of sudo/bash/su
```
(`setpriv` with empty bounding set and `--no-new-privs` is how the REC evidence ingress was started, PROFILE:7 [V]; exact flags are B's call.) Notes: `--allow-uid` is mandatory and repeatable, the ingress uid is not implicitly allowed (SERVER:148-157, BOUNDARY:41); the launcher path must be absolute (CER:417); `-I` must precede it (CER:422); `-m tools.mvp_ingress.server` is refused and FAILs the check (SERVER:230-233, CER:419-421). `-B` is not required by any source (see section 5). `--max-requests` must be at least 2 (CER:11-13); with an IPC directory that blocks the outsider only the client probe is accepted, so an ingress started with `--max-requests 2` is still blocking in `accept()` after the capture: the harness must SIGTERM it (clean exit removes the socket, SERVER:219, 225-226). Wait for the `READY` line before capturing (SERVER:220).

Capture form (profile text PROFILE:38 uses `python -m tools.mvp_env_record.capture_env_record`; the script form below needs no cwd and works under `-I`, since the script is stdlib-only; the `-m` form needs the checkout as cwd, which `-I` drops):
```
sudo $PY -I $REPO/tools/mvp_env_record/capture_env_record.py \
  --repo-root $REPO \
  --state-dir $BASE/state --socket $BASE/ipc/ingress.sock \
  --ingress-pid $ING_PID --ingress-uid $ING_UID --ingress-gid $ING_GID \
  --client-uid $CLIENT_UID --client-gid $CLIENT_GID --outsider-uid 65533 \
  --allow-uid $CLIENT_UID \
  --db $BASE/state/atomic/refunds.sqlite3 --authority-store $BASE/state/atomic/refunds.sqlite3 \
  --ledger $BASE/state/ingress.db --journal-mode wal \
  --pin control_plane=7a4bcd40b3b49e61ff3c294dcca53b52f460b22c --pin runtime=c5e97e87dd239c821b1b4a406a55dcd03c5bc61f \
  --pin manifest_sha256.candidate-manifest.json=64ea8304fcc3c68917d87fba44c32178c129abf5622751feef08e83ce740ad04 \
  --manifest $REPO/docs/mvp-package/candidate-manifest.json --accept-unverified-pins \
  --label "QGATE-03: GitHub-hosted ubuntu-24.04, synthetic ingress; platform host candidate; NOT the qualification host; boundary NOT qualified" \
  --out $EVDIR/capture-record.json ; echo $? > $EVDIR/capture.rc
```
Flag map: `--ingress-pid` H-05/07/09/12/14/15/19; `--ingress-uid/--ingress-gid` H-09/16/17/20/21/23 (also derivable from the pid); `--client-uid/--client-gid` H-10/15/16/21; `--outsider-uid` H-18; `--allow-uid` H-07/H-11 (must equal the launcher's set exactly; the outsider and root must not be in it); `--db/--authority-store/--ledger` H-15 (probe files) and H-25; `--journal-mode` H-25; `--pin/--manifest/--accept-unverified-pins` H-27; `--label` H-26; `--repo-root` H-07/H-24/H-27 (default is the script's own checkout, CER:819). `--accept-unverified-pins` is a script flag, not a relaxation of a requirement: it lets the component-commit pins count as "declared only" (CER:781-784). Whether to use it is the Architect's call; without it configuration.pins_and_manifests is BLOCKED and the acceptance rule yields INCOMPLETE. Digest pins are compared for real, so use them for what can be compared; the manifest digest above is OBSERVED now (sha256sum) and must be recomputed at run time.

## 5. Places where profile text and script/launcher disagree (or are silent)

1. IPC directory mode, 2750 vs 2751. PROFILE:9 and :34 [V] say `2750`; REC records 2750 (uid 30033, gid 30004) [V]; the only hub mention of 2751 is RECON:58 [V] ("Doc contradictions: IPC directory 2750 (hub) vs 2751 (Qualification)"); the Qualification text itself is UNAVAILABLE here, so 2751 is UNVERIFIED as a requirement. CER does not test the exact mode, the setgid bit or the directory group (CER:535-540: owner root/ingress and no go+w only), so the script accepts 2750 and 2751 alike. CONSEQUENCE (DERIVED from CER:647-656): with 2750 an outsider uid has no `x`, so `qualification.outsider_denied_socket` is BLOCKED ("not conclusive for the socket") and `qualification.outsider_denied_by_ipc_directory` PASS; a BLOCKED can never be counted as PASS (PROFILE:48), so an otherwise perfect run is INCOMPLETE, not PASS. A PASS on outsider_denied_socket requires the outsider to traverse every ancestor (for example `o+x` on the IPC dir, such as 2751), which is NOT the profile's stated mode. I do not change the requirement; this is a decision/blocker for the Architect: run at 2750 (expected INCOMPLETE on this id by design, honest) or at a mode that differs from the profile text (deviation to be recorded, not silently adopted).
2. Ingress verification wording. PROFILE:21 says the process is verified by command line `tools.mvp_ingress.server`; CER:416-427 requires the launcher form and FAILs `-m` (message at CER:420-421); BOUNDARY:74 and SERVER:230-233 say `-m ...server` is unsupported/refused. PROFILE:21 is stale; the script and launcher agree with each other.
3. `-B`. Neither CER nor LAUNCH nor BOUNDARY requires `-B`; CER checks only `-I` (CER:422); LAUNCH sets `sys.dont_write_bytecode = True` and a private `pycache_prefix` itself (LAUNCH:31-34). The only `-B` in the hub is the candidate manifest's validator hygiene (candidate-manifest.json:81 [V]). So `python -I -B launch.py` is not a stated requirement; `python -I launch.py` is the supported form. Adding `-B` would pass the CER command check (it only looks for `-I` before the launcher token) but is not required (INFERENCE).
4. Stale `-m` wording in CER's own docstring: CER:19 says `python -m tools.mvp_ingress.capture_env_record` (the script moved to tools/mvp_env_record/, PROFILE:82), and its example (CER:19-21) has no `--allow-uid`, so following the docstring against a compliant ingress yields identity.ingress_command FAIL (`not allow`, CER:424). PROFILE:38 gives `python -m tools.mvp_env_record.capture_env_record`. The script form in section 4 avoids both.
5. Launcher interpreter floor: LAUNCH:36 and BOUNDARY:13 accept Python >= 3.11; PROFILE:20 is CPython 3.13 only. Only python.profile / interpreter_matches_ingress enforce 3.13.
6. Sticky ancestors: SERVER:83 and BOUNDARY:56 accept ANY sticky ancestor; CER:486-494 and PROFILE:25 accept only a sticky, root-owned ancestor that is not the direct parent of the socket or state dir. The stricter CER rule decides the capture result.
7. Socket mode: server default `600` (SERVER:202, BOUNDARY:42); profile requires exactly 0660 (PROFILE:23), so `--socket-mode 660` is mandatory in the launcher line; BOUNDARY:42 also names 0666, which the profile excludes.
8. Peer allow list: absent from the PROFILE frozen table (PROFILE:17-28), mandatory in BOUNDARY:41/SERVER:148-157 and checked by CER only as cmdline-vs-declared equality (CER:424-425).
9. Check-id count: "31" is the committed-record count; the script's id vocabulary is 34 (section 0). The acceptance wording "all 31 checks" matches the REC set only; at IPC dir 2750 the emitted set has 32 ids (extra qualification.outsider_denied_by_ipc_directory).
10. PROFILE:3 cites "architect rulings #2 item 4" (not in this repo per MATRIX:79, UNVERIFIED by me).

## 6. Is `/opt` allowed as a base path?

- By the ancestors rule alone: ALLOWED. PROFILE:25 [V] requires every ancestor of the socket and state dir to be owned by root or the ingress uid and not group/other-writable; the sticky exemption applies only to a sticky, root-owned ancestor that is not the direct parent of the socket/state dir. A standard `/opt` (root-owned, 0755, not sticky) passes without needing the exemption (CER:482-494). A dedicated `/opt/<name>` created root-owned 0755 (and its `ipc`/`state` children) therefore satisfies H-23 provided the ingress uid does not need sticky excuses. The sticky exemption can never rescue the DIRECT parent: `BASE/ipc` and the parent of `state` get no sticky excuse.
- By the profile as a whole: NOT forbidden by any row, and not prescribed either (no row names a base path). The REC used `/opt/ocs-real/...` [V, REC filesystem.paths], so `/opt` is the profile's own precedent.
- But H-22 is the live problem: QGATE-02's FAIL is, per the supplied facts, an ACL entry under `/opt`. DERIVED reading: some directory on the path (`/opt` or `/`, since the children did not exist) carries a POSIX ACL xattr (CER:559-578 checks all ancestors of socket and state dir including `/`). A QGATE-03 run that places the base anywhere beneath that same ancestor reproduces the FAIL (REJECT). I cannot read the runner here, so which ancestor holds the ACL is UNVERIFIED (C's read-only diagnostics, `.github/qgate-03/diagnostics.sh`, exists in the tree but I did not execute or rely on it).
- Removing, weakening or bypassing the ACL is forbidden. The only in-scope lever is the choice of paths (a root-owned, ACL-free chain, possibly on a mount such as tmpfs if the chain above its mount point is also ACL-free and the filesystem passes H-03; creating a mount is not a sysctl/security-policy change but is a B/Architect decision, INFERENCE). If every available ancestor chain from `/` carries an ACL (for instance `/` itself), the profile cannot PASS on this runner and that is a blocker to report, not to engineer around.
- A path under the runner user's workspace (`/home/runner/work/...`) is unlikely to pass H-23 unless owned by root/ingress and not go+w along the whole chain (INFERENCE, MATRIX H-23).

## 7. Blockers and decisions to hand to the Architect

1. IPC directory mode (section 5.1): 2750 as stated makes `qualification.outsider_denied_socket` BLOCKED by design, so overall result cannot exceed INCOMPLETE; any other mode is a deviation from PROFILE:34 that is not mine to make.
2. H-22 ACL under `/opt`: the original FAIL must be preserved; a new run can only avoid it through path choice; if the ACL sits on `/` or on every usable ancestor the profile is unsatisfiable on this runner (REJECT).
3. H-27: component-commit pins can only be "declared only" (`--accept-unverified-pins`) or BLOCKED; otherwise INCOMPLETE.
4. Items classed unobservable in section 3 (H-02, H-06, H-08, H-28 to H-30 and parts of H-11/H-12/H-14/H-24) cannot move any check's status; they do not change the PASS/REJECT/INCOMPLETE outcome.
5. Whether the ingress ledger/state files and WAL sidecars come out 0600 under the runner's umask, whether the base filesystem is in the verified set, the real owner of runner directories, and runner Python 3.13 provisioning are all UNVERIFIED here; each is a genuine observation the capture will make.
6. Yama stays whatever the runner has (SUPPLIED 1); no sysctl is permitted, so a runner whose value later reads 0 or absent yields FAIL/BLOCKED honestly.

## 8. Verification ledger

[V] opened in full this session: /tmp/claude-0/qgate03-common.md; PROFILE (1-82); CER (1-843); MATRIX (1-104); BOUNDARY (1-98); LAUNCH (1-97); SERVER (1-233); REC (parsed with `python3 -I`; check ids and statuses; `ipc.connection_policy`; `filesystem.paths`; `post_capture_annotations`); synthetic_host.py:105-135 (destination at :125); /tmp/claude-0/rt/engine/operation_identity_atomic_destination.py:20-33 (Runtime HEAD c5e97e87dd239c821b1b4a406a55dcd03c5bc61f); RECON:58 and candidate-manifest.json:81 (by `grep -n`, line text read); docs/mvp-recovery/qgate-02/d2-run-evidence-reference.md (head, run identity only).
OBSERVED by running (read-only, outputs to the scratchpad, no repo file written): CER on this sandbox with nonexistent `/opt/qgate02-nonexistent` paths, with and without uid declarations; sha256 of candidate-manifest.json.
UNVERIFIED: CAPS, QINIT, R3 and `dependency-manifest.md` citations (taken from MATRIX only); `mvp_acceptance_gate.py` (unavailable); the 2751 Qualification text; the raw QGATE-02 artifact 13010567298 (unreadable); runner ACL, filesystem, umask, ownership and Python facts; whether the destination's WAL pragma comes from the Runtime (not located); `setpriv` flags (from PROFILE:7 description only).
