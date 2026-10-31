# OCS-MVP-QGATE-03: synthetic ingress configuration (Worker B)

Status: TEST-ONLY, non-authorizing. Not a qualification, not a security clearance, not a production-readiness claim. The runner is a platform host candidate only; the profile is not qualified and the original QGATE-02 failure stays preserved. Standing holds are unchanged (F3 CLOSED, Q2/Q3 UNRESOLVED, Q7 NOT ESTABLISHED, candidate PROVISIONAL/UNFROZEN/UNQUALIFIED, Tier 1 DEFERRED not waived, publication/release/production HOLD).

Script: `.github/qgate-03/run_integration.sh REPO_ROOT CP_ROOT RT_ROOT EVDIR` (bash + Python stdlib; run as root, e.g. under `sudo`). It calls `.github/qgate-03/diagnostics.sh EVDIR` (Worker C) when present, immediately before the capture. Nothing under `tools/**`, the Control Plane or the Runtime is modified.

## Dry-run status

`bash -n` passes. The script was exercised twice in the throwaway sandbox (root, no Yama, Python 3.13.18, ext4, pydantic 2.13.5): the real launcher started, the unmodified capture script ran, the three controls ran, and every account and directory was removed. Those runs are dry runs, not evidence. Observed there: capture overall BLOCKED (only `isolation.ptrace_scope`, Yama absent in the sandbox, and `qualification.outsider_denied_socket`, see below); all other checks PASS. This says nothing about the GitHub-hosted runner.

## What it creates (all removed in a trap at the end)

| Item | Value |
|---|---|
| Accounts (real `groupadd` + `useradd --system --no-create-home --shell /usr/sbin/nologin`, uid = gid = first free id from `QG3_UID_BASE`, default 61200) | `qg3-ingress` (ingress), `qg3-client` (designated client), `qg3-outsider` (unrelated), `qg3-wrong` (control only) |
| Dedicated group | `qg3-ipc` (own gid, not any user's primary group); members exactly `qg3-ingress` and `qg3-client` at capture time. `qg3-wrong` joins only after the capture, for the negative control |
| Base directory | `QG3_BASE`, default `/var/lib/qgate03-ocs`, created by the script with `mkdir -m 0755`, root-owned, never ACL-modified. The script refuses to run (and refuses to delete) if it already exists |
| Sources | `BASE/src/{hub,cp,rt}`: root-owned, `go-w`, copied with tar (no `.git`, no bytecode). `hub` holds only `tools/mvp_ingress` and `tools/mvp_env_record`; the capture script's and ingress sources' sha256 are compared with the checkout (`copy-verify-hub.out`) |
| State directory | `BASE/state`, `0700`, owned by the ingress uid; the ingress creates its `0600` files (umask 077) |
| IPC directory | `BASE/ipc`, owner the ingress uid, group `qg3-ipc`, mode `2750` (profile value, variable `QG3_IPC_MODE`), no ACL set. Owner is the ingress uid because it must create the socket; the setgid bit gives the socket the dedicated group without `CAP_CHOWN` |
| Socket | `BASE/ipc/ingress.sock`, created by the ingress, `--socket-mode 660` |
| Synthetic manifest | `EVDIR/synthetic-manifest.json` (a one-line JSON stating it is synthetic and not a frozen manifest) |

Why `/var/lib` and a copy. `/opt` is where QGATE-02 saw an ACL entry; the base is a single variable. `/var/lib` (root-owned, normally no ACL) is the default because the capture script checks ACLs on every ancestor of socket and state dir and the script must not remove or change an ACL on a pre-existing system directory. UNVERIFIED: whether `/var/lib`, `/var` or `/` carry an ACL on the runner (Worker C's finding decides; override with `QG3_BASE` if needed). The copy exists because the checkout under `/home/runner` is normally mode 0750 and the ingress uid could not read it; it also keeps the sources root-owned and non-writable, and the capture script's `--repo-root` is the copy so its source digests and AST scans describe exactly what the ingress runs.

## Commands (exact forms)

Ingress (real supported launcher, empty capabilities), started directly so `$!` is the ingress pid:

```
env -i PATH=/usr/bin:/bin LANG=C.UTF-8 HOME=/nonexistent [LD_LIBRARY_PATH=...] \
 setpriv --reuid=I --regid=I --clear-groups --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs \
 $PY -I -B BASE/src/hub/tools/mvp_ingress/launch.py --state-dir BASE/state --socket BASE/ipc/ingress.sock \
   --control-plane BASE/src/cp --runtime BASE/src/rt --socket-mode 660 --allow-uid CLIENT_UID --max-requests 10
```

`--max-requests 10` (variable `QG3_MAXREQ`) covers the capture's client probe (one accept; the outsider is stopped by the directory and does not reach accept) plus two controls, with margin. A READY line is awaited for up to 90 s.

Capture (unmodified, as root, cwd = the hub copy, same `$PY`):

```
env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 $PY -B -m tools.mvp_env_record.capture_env_record \
 --state-dir S --socket SOCK --ingress-pid PID --ingress-uid I --ingress-gid I --client-uid C --client-gid C --allow-uid C \
 --outsider-uid O --db S/atomic/refunds.sqlite3 --authority-store S/atomic/refunds.sqlite3 --ledger S/ingress.db \
 --journal-mode wal --pin control_plane=<CP sha> --pin runtime=<RT sha> --pin manifest_sha256.synthetic-manifest.json=<sha> \
 --pin source_sha256.tools/mvp_ingress/<each module>.py=<sha> --manifest EVDIR/synthetic-manifest.json --accept-unverified-pins \
 --repo-root BASE/src/hub --label "github-hosted ubuntu-24.04 QGATE-03 synthetic ingress; unfrozen; NOT qualified" \
 --out EVDIR/capture-record.json
```

What each flag is bound to: `--ingress-pid` the launcher process (command line must be `python -I <abs launcher>` with matching `--allow-uid`; exe must equal the capture interpreter); uid/gid flags the created accounts; `--allow-uid` the same list given to the ingress; `--outsider-uid` the unrelated account; `--db`/`--authority-store` the same SQLite file (route B keeps destination and authority there), `--ledger` the ingress ledger (recorded only); `--journal-mode wal` the mode the Runtime sets (observed in the dev-container record, header checked by the script); verified pins: manifest digest and ingress source digests (computed from the copy); `--accept-unverified-pins` is used ONLY for the two component commits `control_plane` and `runtime` (the script cannot compare them; they are declared, and `git rev-parse HEAD` of the checkouts is saved as `git-head-*.out` when `.git` exists).

Controls (separate file `EVDIR/peer-uid-controls.json`, via `tools.mvp_ingress.client:submit` only, each as the named uid under `setpriv` with an empty bounding set and `--no-new-privs`): proposals are schema-valid but do not match the synthetic approval (request id `qg3-ctl-<name>`, amount 10.01), so no claim or effect is expected.
- positive: designated client accepted, result is not `PEER_NOT_ALLOWED` (observed in dry run: `held`, `DECISION_HELD`).
- negative A: dedicated-group member that is not the allow-listed uid reaches the socket and gets `PEER_NOT_ALLOWED`.
- negative B: outsider is denied at connect (EACCES). With IPC directory 2750 this is a directory-level denial, not a statement about the socket's own mode.
- A control that cannot run is written as `NOT-RUN`; nothing new was built to reach the ingress.

## Privileges and why

The script needs root: `useradd`/`groupadd`/`gpasswd`/`userdel`/`groupdel`, `chown`, and the capture script itself (it drops to the client and outsider uid, reads `/proc/<pid>`, and enumerates passwd/group). Real accounts are the minimum the approved capture procedure requires, because it enumerates `/etc/passwd` and `/etc/group` through `pwd`/`grp`; this is a disclosed, temporary change to the runner's account database, reverted in the trap. No sysctl, security policy, ACL, mount or network setting is changed.

## What is synthetic

Accounts, directories, the manifest, the Control Plane's fixed synthetic resolver fixture used by `synthetic_host`, the Runtime's synthetic SQLite route B destination, proposals. No network, no secrets, no production interface, no refund chain. The control proposals do not run the approved case.

## UNVERIFIED assumptions and risks

1. Interpreter equality: capture and ingress must use the same `$PY`. The script defaults to `python3.13`/`python3`/`python` on PATH; under `sudo` PATH may differ from the workflow's `setup-python`, so the workflow should pass `PY` (and keep `LD_LIBRARY_PATH`, which the script forwards to the ingress and controls if set). It records `python-version.*`; if not 3.13 the capture reports FAIL for `python.profile`.
2. Dependencies: `launch.py` runs `-I`, which ignores `PYTHONPATH`, so pydantic 2.13.5 (and whatever the Control Plane test fixtures import, `cryptography` was present in the sandbox) must be in the chosen interpreter's own site-packages and readable by the ingress uid (`/opt/hostedtoolcache` permissions unverified; `preflight-ingress-deps.*` records it). Failure shows as the ingress not starting; the capture then records BLOCKED/FAIL and the script still finishes.
3. Yama: not set or relaxed here; `isolation.ptrace_scope` reports the runner's value (QGATE-02 facts: 1, second-hand).
4. Outsider conclusiveness: with the profile's `2750` IPC directory the outsider cannot traverse it, so `qualification.outsider_denied_socket` is expected BLOCKED (not conclusive for the socket) with `qualification.outsider_denied_by_ipc_directory` PASS. Making it conclusive needs a more permissive directory mode than the profile states; not done.
5. ACLs: if `/var/lib`, `/var` or `/` carry an ACL entry on the runner, `filesystem.no_acl_entries` FAILs and is preserved as the failure. No ACL is touched. `getfacl` may be absent; the script only logs it when present (a nonzero rc on `base-ancestors-before`/`setup-stat` for that reason is harmless).
6. `/home/runner` mode and ancestor traversal of `EVDIR` are irrelevant to the ingress (root writes all evidence); client traversal is required only above the state dir (`/var/lib` and `BASE`, 0755).
7. Account id collisions are avoided by scanning for free uid/gid values; supplementary-group enumeration by NSS is assumed local files.
8. `userdel` removes each user's private group; the script only calls `groupdel` for groups still present. Cleanup is best-effort and its status is in `cleanup-*.rc` and `cleanup-residue-check.out`.
9. The copy deliberately differs from "run in the checkout": paths in the record are `BASE/src/hub`, not the checkout path. Source digests are identical (verified in `copy-verify-hub.out`).
10. The static AST scans, SO_PEERCRED and denial probes are as described in the profile; this run is one point-in-time observation of a synthetic ingress, not qualification.
