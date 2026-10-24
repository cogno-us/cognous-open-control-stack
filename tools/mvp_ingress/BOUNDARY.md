# MVP trusted-host ingress: what the boundary guarantees and what it does not

Worker D1, branch `mvp-ingress` (hub worktree `/tmp/wk/o31/D1/hub`). Module `tools/mvp_ingress/`, tests `tests/test_mvp_ingress_boundary.py`.
Pinned tuple used: Control Plane `0a41faa9` (unpatched; Worker A's journal fix not yet available), Runtime `ec728da6`, pydantic 2.13.5. Linux, Python 3.13.
This is an engineering description with execution observations. It is not a Qualification verdict, a security clearance, a certification or a production-readiness claim. Production stays on HOLD.

## Where it lives and why

`tools/mvp_ingress/` in the hub repo (non-locked). Reasons: smallest footprint (6 new files, nothing existing edited); no locked component changes (Control Plane, Runtime, Verifier, Replay, Evidence Pack untouched); it only composes the pinned components through their public classes; Orchestrator and GAX are not imported. `tools/` is already an importable package in the hub, so tests import it without path changes.

## The boundary as built

One designated ingress process (`python -I tools/mvp_ingress/launch.py ... --allow-uid UID`, Python >= 3.11; see "Import isolation") is the only holder of:
- the destination write path (Runtime route B `OperationIdentityAtomicAuthorityEffectDestination`, synthetic SQLite),
- the authority-store and authority-writer capabilities (`set_grant_status`, `set_approval_status`, `set_policy_state`, `set_evidence_state`, `remove_authoritative_state`),
- claim provisioning and execution (`provision_claim`, `execute_claim_atomic`),
- the Control Plane workflow, its record store and the fixed synthetic resolver.

All of that lives in a state tree created by the ingress: directory `0700`, files `0600`, one owner (the ingress uid), `umask 077`. The server refuses to start if the state directory is not already an owner-only directory, and re-verifies the whole tree (`verify_state_permissions`: owner, mode, no symlinks, no odd file types) after each request has been served, not before it; on failure the server raises and exits, so no further request is accepted. The check detects a loosened tree after the fact; it does not undo what an earlier request did.

The only client-reachable surface is one Unix socket with one operation. Request: a closed JSON schema `mvp-refund-proposal/1` with exactly six members (`schema`, `request_id`, `customer_id`, `amount`, `unit`, `refund_reason`), at most 4096 bytes. Response: a closed JSON object `{schema, outcome, code, request_id, reasons}`; `outcome` is one of `executed`, `refused`, `held`, `unknown`; `code` is from a fixed list in `proposal.py`; `reasons` are filtered Control Plane vocabulary tokens. No object, handle, path, method name, executor argument or exception text crosses the wire.

Pipeline inside the ingress: parse and validate, reserve `request_id` in an ingress ledger, build the `RuntimeProposal` from a fixed template (only business members come from the client; actor, principal, manifest, adapter, action, authority context and requirement are fixed), Control Plane `decide`, then real `provision_claim` through the Control Plane claim path into the route B destination, then route B `execute` with `operation_identity=True` and `simulate=None` hard-coded (an AST test asserts the only `simulate=` keyword in the core is the constant `None`). The operation id is derived by the Runtime from the persisted issuer-approved decision, never from the client.

Result mapping: `executed` only when the Runtime returns `executed` with acknowledgement. A denial before dispatch is `refused` (`DUPLICATE_OPERATION` for `operation_already_committed`, otherwise `EXECUTION_DENIED`). Anything else after dispatch (`unknown`, `partial`, `failed`, `observed`, unacknowledged `executed`, an exception, an unrecognised status) is `unknown`. A reserved `request_id` is never executed again once the pipeline got as far as claim provisioning, and an in-flight reservation left by a crash is never re-executed: no blind retry. A Control Plane `hold` or `deny` happens before any claim exists, so that `request_id` is released and may be resubmitted.

## What was verified by execution (first report: 190 tests; after review fixes: 205 tests, 160 of them parametrized adversarial cases, all passing on Python 3.13 on both unpatched CP 0a41faa9 and patched CP df4794c8 and merged CP main 7a4bcd40)

- Valid proposal: decision, claim provisioned and consumed, exactly one effect, route B, result `executed`.
- Replay (same content, other content, other amount, same `request_id`): `REPLAY`, no second effect, no second claim.
- Proposal not matching the approved synthetic authority (amount, request id, customer, reason, class-reference-looking ids): `held`, no claim, no effect.
- Adversarial input, each refused with a closed code and a zero-effect, zero-claim, zero-ledger-row check afterwards, then the one legitimate proposal still executes exactly once:
  - `simulate` with 14 value types (`"lost_ack"`, `null`, booleans, numbers, empty and nested values),
  - 50 forbidden or unknown member names (claim fields, authority-writer names, `provision_claim`, `execute_claim_atomic`, `$ref`, `__class__`, SQL, path, executor, policy),
  - hand-built claim (alone, nested, merged with a valid proposal), method-call style bodies, class references in scalar positions,
  - path traversal and injection in both id members (`../`, `/`, `\`, NUL, newline, unicode lookalikes, RTL override, `~`, `file://`, shell and template metacharacters, over-length),
  - oversized (5 KB, 1 MB), duplicate members, 4000-deep nesting, truncated, non-UTF-8, BOM, pickle header, NaN and Infinity, non-object roots, missing members.
- A peer that sends a partial request and never closes gets `REQUEST_TIMEOUT` and no effect.
- State tree permissions on a running, used ingress: directory `0700`, every file `0600`, single owner; the verifier itself is tested against loosened modes, a symlink and a foreign owner; the server refuses a `0755` state directory.
- Second process as uid 65534 (dropped from root, no supplementary groups), through the declared client only: `listdir`, open and read-only or read-write sqlite of the destination, the ledger, the run record, `stat`, `chmod`, `rename`, `/proc/<pid>/mem` and `kill` of the ingress all fail (`PermissionError` or sqlite `OperationalError`); its adversarial proposals get `UNKNOWN_MEMBER` (x3) and `BAD_ID`; its one valid proposal is `executed`, its replay `REPLAY`; the destination ends with exactly one effect and one consumed claim; nothing planted in the state tree; the ingress still running.
- Peer uid allow-list (mandatory): with socket mode `0666` and `--allow-uid 4242`, uid 65534 gets `PEER_NOT_ALLOWED` and causes no effect; without any `--allow-uid` (or with a negative, non-integer or `(uid_t)-1` value) the ingress refuses to start before touching state, and the ingress's own uid is not implicitly allowed. Peer credentials are read with `SO_PEERCRED` and checked before any request byte is read; unreadable credentials refuse.
- Default socket mode is `0600` (owner only). This means a distinct-uid client cannot connect by default: a deployment needs mode `0660` with a shared group, or `0666`, in every case with an explicit `--allow-uid` for each client uid. The unprivileged tests use `0666`.
- Full hub test suite on 3.13 with the new tests skipped (no component env): no failures.

Additional observations after review: the same suite passed against the patched Control Plane df4794c8 (202 passed at eab0d2e; 205 passed at the final commit on both CP 0a41faa9 and merged main 7a4bcd40); a restart on an existing state tree returns `REPLAY` for a settled or in-flight id, and kill -9 at random points (including after claim issuance and before the effect) never re-executed a request and left at most one effect (independent reviewer observations on CP 0a41faa9, `/tmp/wk/o31/D1/REVIEW.md`). Deleting the ledger and restarting is outside the profile: route B still denied the second execution, but one extra issued claim was left.

Not verified by execution (at the time of the first report): Python 3.11 integration (the only pydantic 2.13.5 copy, `/tmp/wk/mvp/H/pyd`, is built for CPython 3.13 and no new venv was permitted; the 3.11 unit tests passed); a real `lost_ack` or UNKNOWN outcome through the live route (unreachable by design, so UNKNOWN mapping is covered with a fake executor only); Verifier assessment of the records this ingress produces.

## What the boundary guarantees, and for whom

For a client that (a) runs as a different uid from the ingress, (b) holds no root or `CAP_DAC_OVERRIDE`/`CAP_SYS_PTRACE`/`CAP_KILL`-equivalent privilege, and (c) can reach only the socket, the only things it can do are send bytes to the closed parser and receive a closed result. It cannot pass `simulate`, an authority-writer call, a claim, a claim-execution call, an object or class reference, a path or SQL; every such attempt is refused with a closed code and leaves no effect, claim or ledger row. It cannot read or write the destination or authority store because the operating system denies it, not because a convention asks it not to. This is a capability boundary (file ownership plus process separation). It held against the one tested configuration: a single unprivileged second process (uid 65534, groups dropped) on this host, run from root. Other kernels, container settings and capability sets were not tested.

## Profile requirements (deployment conditions, checked or captured)

- Supported client: a distinct unprivileged uid reaching only the socket (see above).
- Every ancestor directory of the state directory and of the socket path must be owned by root or the ingress uid and must not be writable by group or other, unless sticky. The server checks this at startup (`check_parents`) and refuses to start otherwise; the test plants a world-writable non-sticky parent for each path. Without this a non-owner with write access to a parent could rename or replace the state tree or the socket.
- `check_parents` is a startup-only check, not continuous. It examines the resolved path once and then the original path strings are used; ancestors are not re-verified afterwards. It checks owner and mode bits only and ignores POSIX ACLs and group memberships of root-equivalent groups. The state directory itself is covered by `prepare_state_dir` and the per-request tree verification, and the socket file by its mode.
- Socket mode and the allow-list must be set deliberately for the intended client uids.

## Operator procedure: `inflight` ledger rows

A row in `ingress.db` table `requests` with state `inflight` means the pipeline began and did not settle (crash, kill, or a bug). The request id is permanently refused (`REPLAY`) and is treated as outcome unknown. Do not delete the row to retry. The operator reconciles first as the owner uid: read the destination `effects` and `execution_claims_v1` tables (and the Runtime `reconcile_claim` result) for that request's effect. Only after establishing that no effect was committed and the claim is unconsumed may a new, separately approved request be issued; the old request id stays burned. SIGTERM is handled by raising `SystemExit` wherever the main thread is, including between claim issuance and the effect; that leaves an `inflight` row and a burned request id exactly as `kill -9` does, with no re-execution (a unit test sends SIGTERM mid-flight and shows a replay is refused with no provisioning or execute call). A SIGTERM before the handler is installed (during startup) leaves a stale socket, which the next start replaces. Observed: kill -9 at random points never re-executed a request (see below).

## Shutdown

Clean SIGTERM removes the socket file and exits 0. A stale socket file (nothing listening) is replaced at startup under an flock on `socket.lock` in the state directory, so two concurrent starts sharing a state directory cannot unlink each other's live socket (tested at the listener level, 20 rounds, exactly one winner); a live one, or a non-socket file, is refused. Cleanup removes the socket only if it is still the inode this process bound, so an ingress whose socket was deleted and re-bound by another process does not remove the new one. Two ingresses with different state directories use different lock files and are not serialized against each other. After SIGKILL the stale socket remains until the next start.

## Static check limits

The `simulate` check is a static AST scan of the package source. It does not catch `getattr`, `**` forwarding of non-literal dicts, or dynamically built strings; today `core.py` uses `getattr` only on result objects and `**` only on dict literals, which a reviewer must keep true.

## Import isolation (launcher)

The only supported start command is `python -I tools/mvp_ingress/launch.py --state-dir DIR --socket PATH --control-plane ROOT --runtime ROOT --allow-uid UID` (`--allow-uid` repeatable and mandatory). `python -m tools.mvp_ingress.server` is no longer a supported entry point (the module refuses to run as `__main__`), and the environment record marks it non-compliant. Reason: with the hub as working directory or on `PYTHONPATH` that form put the hub root ahead of the standard library, so a hub-root `json.py` (or a package or extension module shadowing an ingress import, or a planted `__pycache__` .pyc with a matching header) was imported instead of the committed code; the `*.py` digest and the git tree id do not establish which module a running process imported.

Precise coverage of the launcher (a mitigation of these paths; installed packages are trusted except the checked modules):
- `-I`: no working directory, script directory, `PYTHON*` variables or user site on `sys.path`. `PYTHONPATH` is ignored, so the hash-locked dependencies must be installed in the interpreter's own site-packages.
- A fresh private `sys.pycache_prefix` (set before further imports) means no bytecode cache beside any source is read or written, for the ingress and the components; the launcher also refuses to start if any `__pycache__` or `.pyc` exists under `tools/mvp_ingress`.
- The hub root is appended (computed from the launcher's own path), `tools.mvp_ingress` and each ingress module must resolve to the committed `.py` file (checked before any of them runs), then the hub root is removed again.
- `synthetic_host` appends the Control Plane and Runtime roots after the standard library and site-packages, and refuses (exit 2) unless `agent_control_plane`, `engine` and `tests`, and any other module named like a top-level module of those roots, resolve under the operator-supplied roots. Other installed packages (site-packages, the standard library) are trusted.

Regression tests: `tests/test_mvp_ingress_isolation.py`, `tests/test_mvp_ingress_peer_allowlist.py`. Non-authorizing. Not covered: code running as an allowed uid, the ingress uid or root; a tampered interpreter, standard library or site-packages (including a stray package other than the checked ones); a hostile file placed in a component root itself; the host (Yama `ptrace_scope` etc.). Client uids are bound by configuration only.

## What it does not guarantee

- No isolation from code running as the ingress uid or as root. Such code can open the destination, write the authority tables, call `provision_claim`/`execute_claim_atomic` and pass `simulate` directly. Same-uid clients, shared-uid containers, in-process library use, and anything with `ptrace`/`DAC_OVERRIDE` are outside the boundary. An in-process Python API was deliberately not offered as a supported client, because a Python object offers no capability boundary.
- Enforceability is conditional on deployment: the supported client must be a separate uid, and the socket mode and allow-list must be set so that only intended uids can connect. A deployment that runs the client as the ingress uid has no boundary, whatever the code does. The qualification environment must capture the actual uids, socket mode, directory and file modes (`stat` output) and kernel/container settings (`yama.ptrace_scope`, capabilities, user namespaces); only the tested configuration was observed.
- No defence against a trusted proposer abusing what the fixed authority already permits (the synthetic approval admits exactly one operation: `case-1`, `customer-001`, $10 USD, `duplicate`; any other proposal is held).
- No authentication of clients beyond socket permissions and the mandatory explicit peer-uid allow-list (`SO_PEERCRED`, Linux only; the client uid is bound by configuration, not authenticated further); no confidentiality of the socket channel (local host only).
- No denial-of-service protection beyond a 4096-byte request cap, a 5 s read timeout and serial handling; the request read has a monotonic total deadline (default 5 s, `--read-timeout`) and the post-reply drain has its own total deadline (0.5 s) and byte cap (1 MiB), so a connected client can occupy the single worker for at most about the read deadline plus the drain deadline per connection; queued clients wait that long.
- Authority changes (revocation, approval withdrawal, policy change) are not exposed through the client interface and no admin channel was built; they must be made by the owner uid out of band. The ingress consults the synthetic resolver per proposal and route B re-checks authoritative state at effect time, as before.
- Authority is the Control Plane's fixed, synthetic, trusted resolver fixture (`tests.test_runtime_authority.setup_flow`, loaded from an explicitly given Control Plane checkout) with a fixed synthetic clock: not production IAM, not institutional delegation. The ingress imports Control Plane test fixtures; that dependency should be replaced by a frozen fixture module before any wider use.
- Audit-record integrity: the unpatched Control Plane still writes the claim-stage journal record that the pinned Verifier refutes (Worker A's scope). This ingress neither fixes nor masks it.
- Nothing here establishes ambiguous-commit, lost-acknowledgement, revocation-race or evidence-tampering behaviour; those remain Qualification's controls.

## Enforceable for all supported clients, or only by convention?

Enforceable by operating-system mechanisms for the supported client class defined above (a distinct, unprivileged uid reaching only the socket), and demonstrated against such a client. By convention only for any client outside that class (same uid, root, shared uid, in-process). The MVP profile must therefore state "supported client = distinct unprivileged uid via the socket" as a condition, and Qualification should run the unprivileged-process test in the exact Linux environment. On that definition the stop condition ("trusted-host profile cannot be enforced as defined") is not triggered; if the target environment cannot run the client under a distinct uid, it is.
