# QGATE-03: host verdict

Non-authorizing. Not MVP qualification, not certification (Q7 NOT ESTABLISHED), not a host designation. Candidate PROVISIONAL, UNFROZEN, UNQUALIFIED. No weaker or successor profile adopted; Yama untouched.

## Verdict: INCONCLUSIVE

Evidence cannot support a reliable determination from what the builder could read. Read facts only (run 41153041401, `d-run-evidence-reference.md`): the workflow's own annotation reports `integration.rc=0, capture overall=BLOCKED`; the primary `capture-record.json` exists, so the capture ran after the ingress was started (setup/ingress start precedes the capture in `run_integration.sh`). That is all. It does **not** establish that the host satisfies the original profile, because `overall=BLOCKED` is also what the capture emits for a crashed section (`capture.exception`), for absent Yama, and for any single unobservable check; and `integration.rc=0` is near-vacuous (the script exits 0 on every path). It also does not establish incompatibility: by the script's rule `BLOCKED` means no check FAILED. So: not HOST QUALIFIED, not HOST INCOMPATIBLE, and a positive "HOST CANDIDATE" is not supportable without the per-check record.

**What would change it:** the operator attaches artifact `13023553992` (`capture-record.json`, `peer-uid-controls.json`, `diagnostics/`). If it shows Yama `ptrace_scope = 1` PASS and only declared, out-of-scope or 2750-mode-related checks BLOCKED with no `*.exception`, the verdict becomes HOST CANDIDATE — REMAINING GAPS without any new run. Worker review (`adversarial-postreview.md`) recommended this downgrade; the builder concurs.

## ACL failure disposition (Worker C, `acl-failure-analysis.md`)

The QGATE-02 FAIL can only have come from a POSIX ACL on `/opt` or `/` (the only existing ancestors of the nonexistent test paths); exact path and ACL remain UNKNOWN to the builder. The profile fixes no base directory, so QGATE-03 used a root-owned `/var/lib/qgate03-ocs` (disclosed relocation, nothing removed, weakened or bypassed; read-only `diagnostics/` records every ancestor's ACL xattrs in the artifact). Classification: **undetermined**. The QGATE-02 failure is real for its `/opt` chain; whether it reflects an image ACL on `/opt` or `/` or something else is answered only by the `diagnostics/` files (UNREAD). Re-running on `/var/lib` was a profile-conformant relocation, not a resolution of the `/opt` finding. The overall result here (no FAIL is possible but unconfirmed, see above) does not prove the ACL check passed.

## H-01..H-30 matrix (profile requirements from `../qgate-02/host-profile-requirements-matrix.md`)

Run-level result as read: `overall=BLOCKED`. Per-requirement results: **UNREAD** for all 30 (not inferred). The column below is a placeholder for the operator, not coverage.

| Req | Area | QGATE-03 observed status |
|---|---|---|
| H-01 | Kernel / OS | UNREAD |
| H-02 | Kernel / OS (distro, kernel) | UNREAD |
| H-03 | Filesystem | UNREAD |
| H-04 | Interpreter | UNREAD |
| H-05 | Interpreter (ingress equality) | UNREAD |
| H-06 | Interpreter / dependencies | UNREAD |
| H-07 | Launcher / ingress support | UNREAD |
| H-08 | Launcher (isolation) | UNREAD |
| H-09 | Process and UID separation (ingress) | UNREAD |
| H-10 | Process and UID separation (client) | UNREAD |
| H-11 | Peer-UID allowlist | UNREAD |
| H-12 | Process capabilities | UNREAD |
| H-13 | Ptrace / Yama | UNREAD |
| H-14 | Ptrace / dumpability | UNREAD |
| H-15 | Process isolation (denials) | UNREAD |
| H-16 | Socket permissions | UNREAD |
| H-17 | IPC directory | UNREAD |
| H-18 | Outsider denial | UNREAD |
| H-19 | Peer credentials | UNREAD |
| H-20 | State-directory permissions | UNREAD |
| H-21 | State-directory group access | UNREAD |
| H-22 | ACLs | UNREAD |
| H-23 | Ancestors | UNREAD |
| H-24 | Invocation constraints | UNREAD |
| H-25 | Journal mode | UNREAD |
| H-26 | Host identity: evidence label | UNREAD |
| H-27 | Provenance: pins and manifests | UNREAD |
| H-28 | Provenance: record hash and envelope | UNREAD |
| H-29 | Freshness and scope | UNREAD |
| H-30 | Not-run-by-script evidence | UNREAD |

## Remaining gaps and unknowns (classified)

1. **Per-check results**: UNREAD (artifact unreadable to the builder). Operator action: attach artifact `13023553992`.
2. **IPC directory mode 2750 vs 2751**: at the profile's 2750 the outsider cannot traverse, so `qualification.outsider_denied_socket` can only be BLOCKED (dry-run sandbox behaviour, DERIVED from the script, not observed on the runner). A supplementary 2751 record (not the verdict basis) is in the artifact. Which value governs is an Architect/operator decision; the profile was not changed.
3. **Component commit pins**: declared only (`--accept-unverified-pins`); source identity is carried by provenance/`cp_head`/`rt_head`, not by the capture.
4. **Not environment-scope** (not required to pass here): declarative, Qualification-gate-owned and not-run-by-script evidence (live propose round trip, adversarial proposals, Python 3.11, OS-kill), per `h-matrix-reconciliation.md`.
5. **Script change after the precheck**: `run_integration.sh` was fixed (pins from the checkout, fatal copy mismatch, diagnostics env) after the precheck's reviewed commit `ed6df28`; that fix and the trigger change were reviewed only by the builder, with a sandbox dry run.
5b. **Peer-UID controls** (positive client, negative non-allowlisted group member, negative outsider): recorded in `peer-uid-controls.json`; results UNREAD.
6. **Same-lineage only**: builder, workers and reviewers share one lineage; D1 roles remain NOT YET INSTANTIATED.

## Next accountable action

Operator downloads artifact `13023553992` (expires 2027-01-29) and attaches it; the per-id matrix and this verdict are then confirmed or corrected without any new run. The operator/Architect rules on the IPC-directory mode (2750 vs 2751). No second run is requested or authorized.
