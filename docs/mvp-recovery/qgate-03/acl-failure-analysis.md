# QGATE-03 Worker C: analysis of the QGATE-02 `filesystem.no_acl_entries` FAIL

Non-authorizing. Analysis from sources only. The raw artifact 13010567298 was not readable, so the exact observed path and ACL are UNKNOWN. Labels: SOURCE (read in a file), DERIVED (follows from source by the stated reasoning), UNKNOWN. Line numbers refer to `tools/mvp_env_record/capture_env_record.py` (CER), `.github/qgate-02/runner_probe.py` (P), `.github/workflows/qgate-02-host-feasibility.yml` (W) and `docs/mvp-recovery/ingress-qualification-environment-profile.md` (PROFILE). Preserved: the original FAIL stands as recorded; nothing here reinterprets it as a pass.

## 1. Path walked and expected ACL state

- SOURCE: PROFILE ACL row: "No POSIX ACL entries on the socket, the state tree or any ancestor of either." Expected: no `system.posix_acl_access` and no `system.posix_acl_default` xattr on any of them (CER 45, 184-191).
- SOURCE: W invoked the capture with `--state-dir /opt/qgate02-nonexistent/state --socket /opt/qgate02-nonexistent/ipc/ingress.sock`, no ingress, no uids.
- SOURCE: the ACL targets are `[state_dir]+tree` (only if state_dir exists), `[sock]` (only if it exists), plus `ancestors(sock)` and `ancestors(state_dir)` (CER 559-561). `ancestors(p)` starts at `dirname(realpath(p))` and walks to `/` inclusive (CER 175-181); `realpath` is non-strict, so nonexistent components are kept.
- DERIVED: neither the state dir nor the socket existed, so the target set is exactly four paths: `/opt/qgate02-nonexistent/ipc`, `/opt/qgate02-nonexistent`, `/opt`, `/`. The two `qgate02-nonexistent` paths cannot hold an xattr (listxattr gives ENOENT, classed "unreadable", CER 186-188). Verdict order is FAIL if any `present`, else BLOCKED if any `unreadable` (CER 573-577), so the ENOENT entries would have produced BLOCKED, and a FAIL means a `present` ACL on `/opt` or on `/`.
- DERIVED: the operator's phrase "an ACL entry under /opt" therefore most plausibly means `/opt` itself (the only existing path in the set apart from `/`). `/` is not excluded by the sources; only the operator's second-hand wording favours `/opt`. The exact path is UNKNOWN.
- SOURCE: the check is not a path-by-path decision of which ancestors matter: it is every ancestor to `/`.
- DERIVED: with no ingress, `filesystem.ancestors_not_writable_by_others` is BLOCKED (`ing_uid` None, CER 481, 496) and the nonexistent dirs would otherwise raise on `lstat`; this does not affect the ACL check.

## 2. Actual observed ACL and candidate explanations

Actual ACL (type, entries, access vs default): UNKNOWN. Candidates, ranked by plausibility from the sources only (none is established):

1. The stock runner image (or its provisioning) leaves an access and/or default ACL on `/opt` (or `/`). DERIVED as the leading candidate because it is the only mechanism that does not require the probe to have touched `/opt`. Plausibility rests on the FAIL being on an existing path outside the probe's reach; no source states the image contents (UNKNOWN). Discriminator: a `system.posix_acl_access`/`default` xattr on `/opt` in a fresh job BEFORE any probe or capture step, and the same on a fresh job with the probe skipped. Diagnostics here record exactly this with `diag-*-pyxattr.txt`.
2. A default or access ACL on `/` or on another root-owned ancestor. Same discriminator; differs from (1) in WHICH path carries it, readable in the path-specific files.
3. The QGATE-02 probe left an ACL on `/opt`. DERIVED as unlikely: P runs first (W step (1), probe, then step (2), capture; same VM, sequential), but the only `setfacl` is `setfacl -m u:61002:r` on the FILE `/opt/qgate02-probe/acl-control.txt` (P 153, 162-163), never on a directory; the other P operations on `/opt` are `makedirs`/`chmod 0755` on `BASE` itself (P 283-284, 378-379) and a `rmtree(BASE)` in `finally` (P 386). P never modifies `/opt`'s own mode, owner or xattrs. The file ACL is removed with the directory. Residual risk: if P's cleanup failed, only `/opt/qgate02-probe` would remain, which is not an ancestor of the capture's paths. The probe also cannot make `/opt` inherit anything. Discriminator: `/opt` xattrs before the probe step versus after; the probe's own `probe.cleanup` field.
4. The capture walking nonexistent ancestors. DERIVED as an explanation of path SELECTION only, not of an ACL: it explains why `/opt` and `/` are examined at all (the dirs were never created), not why one carries an ACL. Missing paths produce BLOCKED, not FAIL.
5. Filesystem artefact: a mislabelled or non-ACL-capable xattr result. DERIVED as unlikely: `listxattr` returning the ACL names is a positive indication (PROFILE caveat concerns false EMPTY results, not false positives). Discriminator: raw hex of the xattr value.

Candidate-independent note: the ACL could be a trivial default ACL equal to the mode bits (some tools only store extended entries; a minimal ACL is normally represented by mode bits alone and does not appear as an xattr). The hex dump distinguishes an extended entry (entries beyond user::/group::/other::) from a degenerate one. UNKNOWN which applies. The script does not distinguish; it FAILs on mere presence (CER 566-567).

## 3. Real security incompatibility, or incomplete test setup?

- SOURCE/DERIVED: QGATE-02 passed non-existent paths and no ingress. The profile's requirement is on the real state tree and IPC directory chain. The capture, by script design, includes `/` and every existing ancestor, so an ACL on `/opt` is a property of the chosen BASE PATH's chain, not of the runner's ability to host the profile in general.
- DERIVED: the failure is a real, correctly reported violation of the ACL row for that specific chain (`/opt/...`): the script behaved as written, and under the profile an ACL on any ancestor leaves the boundary unqualified. It is not a script defect and must not be weakened.
- DERIVED: whether it is a PLATFORM incompatibility is NOT established. It becomes one only if every acceptable ancestor chain on the runner carries an ACL (in particular if `/` does), or if no ACL-free chain can be built without altering a pre-existing path. That has not been observed. It is therefore best described as "failed on the QGATE-02 path chain; platform verdict undetermined", not "incomplete test setup" in the sense of an excuse: the setup also never exercised an existing, scaffolded directory pair, so the check could only ever be FAIL or BLOCKED there (ENOENT paths cannot PASS).
- Consequence for the QGATE-03 expectation: even with a clean chain, a PASS needs state dir and socket to exist (CER 459, 559-561), so paths must be scaffolded, as the matrix (H-22/H-23) already notes.

## 4. Does an approved existing configuration resolve it?

- SOURCE: PROFILE and CER fix no base directory. The requirement is: no ACL on the socket, the state tree, and EVERY ancestor of the state dir and the socket (to `/`, inclusive, CER 175-181, 559-561); ancestors must be owned by root or the ingress uid and not group/other writable, with sticky excused only for a root-owned non-direct-parent (CER 482-494).
- DERIVED: yes, in principle, if some existing, profile-conformant chain is ACL-free. The state and IPC directories may be created under any root-owned directory chain that has no ACL on any ancestor (for example a new subtree under `/srv`, `/var/lib` or a new top-level path), with the directories themselves created fresh (state `0700`/ingress-owned, IPC `2750`). Creating NEW directories with default settings is not a change to a pre-existing path, provided the parent has no default ACL (a parent default ACL would be inherited and would itself FAIL).
- SOURCE/DERIVED: this does NOT free `/`: every candidate chain includes `/` and probably `/var`, `/srv`, etc. Each needs an ACL-free check: the whole chain, not only the listed ancestors and not only the state tree. The diagnostics decide which chains qualify. Which one is ACL-free is UNKNOWN until the diagnostics run.
- STOP/ESCALATE: if the diagnostics show an ACL on `/` (or on every viable chain), no existing approved configuration resolves it; resolving it would require removing or altering an ACL on a pre-existing system path, which is forbidden. In that case report a platform blocker and do not proceed. Likewise do not remove the ACL from `/opt`, do not exclude `/opt` or `/` in the check, and do not edit the capture script.

## 5. Would avoiding `/opt` violate the controlling profile?

- SOURCE: searched PROFILE, `tools/mvp_ingress/BOUNDARY.md`, `tools/mvp_env_record/`, and `tools/mvp_ingress/*.py` for `/opt`, `/srv`, `/var/lib`: no match. PROFILE fixes no base directory. `/opt` appears only in the QGATE-02 workflow (W, nonexistent test path), the probe (P 29), and the matrix as an example of root-owned paths (H-23: "`/opt/...` style root-owned paths avoid it") and as a recorded dev-container path (`/opt/ocs-real/ipc`, H-17).
- DERIVED: avoiding `/opt` does not violate the controlling profile. The profile constrains ownership, mode, ACLs, filesystem type and ancestor writability, not location. Choosing another conformant location is a choice of test fixture, not a weaker or successor profile. The choice must be recorded and every row of the profile must still be evaluated on it.
- Caution (DERIVED): relocation must not be used to dodge a real ACL finding that applies to `/`; the ACL check is run unmodified on the new chain and the original QGATE-02 FAIL is preserved in the record.

## What would discriminate (observation list)

1. Per-path xattr hex and `getfacl -p` for `/`, `/opt`, `/var`, `/var/lib`, `/srv`, `/tmp`, `/home` and every ancestor of QG03_STATE_DIR / QG03_SOCKET_DIR in a fresh job BEFORE any QGATE-03 step creates anything (`.github/qgate-03/diagnostics.sh EVDIR`).
2. The same read after any scaffold step, to detect a default ACL inherited into new directories.
3. Mount fstype/options for each ancestor (an `acl`-capable fs, and `noacl` rejection per CER 342).
4. Reading the retained QGATE-02 artifact (`capture-record.json` -> `isolation_acl.paths`, which maps each examined path to `none`/`present`/`unreadable`) would settle the exact path directly if it ever becomes readable: that field is SOURCE (CER 570), but its content is UNKNOWN here.

## Verdict summary

Exact path: UNKNOWN (`/opt` or `/`, DERIVED). Observed ACL: UNKNOWN. Security incompatibility: NOT ESTABLISHED; failure is real for the QGATE-02 chain. Resolution: possible by relocating state and IPC dirs to an ACL-free, root-owned chain if one exists; STOP/ESCALATE if `/` or all viable chains carry an ACL. Avoiding `/opt` is permitted by the profile.
