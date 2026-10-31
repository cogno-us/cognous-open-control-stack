# QGATE-03: host verdict

Non-authorizing. Not MVP qualification, not certification (Q7 NOT ESTABLISHED), not a host designation. Candidate PROVISIONAL, UNFROZEN, UNQUALIFIED. No weaker or successor profile adopted; Yama untouched.

## Verdict: HOST CANDIDATE — REMAINING GAPS

Basis, all from the run's own recorded outcome (run 41153041401, see `d-run-evidence-reference.md`): the real ingress started through the supported launcher on GitHub-hosted ubuntu-24.04 under a dedicated non-root uid; the **unmodified** capture script ran against it and wrote a record with `overall=BLOCKED`, which by the script's rule means **no check FAILED** and at least one was BLOCKED. So no mandatory original-profile requirement was demonstrated unsatisfiable (not HOST INCOMPATIBLE), and the host cannot be called qualified while a check is BLOCKED (not HOST QUALIFIED). The QGATE-02 ACL FAIL did not recur on the relocated chain (no FAIL anywhere).

**Confidence limits (read before relying on this):** the builder could not read the log or artifact `13023553992`; the per-check statuses below are therefore UNREAD, not inferred. Yama `ptrace_scope = 1` (H-13) rests on the operator's reading of the QGATE-02 artifact plus the absence of any FAIL here; it was not re-read by the builder. If the artifact shows something other than "no FAIL", this verdict must be re-derived, and INCONCLUSIVE would be the fallback.

## ACL failure disposition (Worker C, `acl-failure-analysis.md`)

The QGATE-02 FAIL can only have come from a POSIX ACL on `/opt` or `/` (the only existing ancestors of the nonexistent test paths); exact path and ACL remain UNKNOWN to the builder. The profile fixes no base directory, so QGATE-03 used a root-owned `/var/lib/qgate03-ocs` (disclosed relocation, nothing removed, weakened or bypassed; read-only `diagnostics/` records every ancestor's ACL xattrs in the artifact). Classification: **incomplete test setup for the QGATE-02 chain, not an established platform incompatibility**; whether `/opt` itself carries an image ACL is answered only by the `diagnostics/` files. If `/` or `/var/lib` carried an ACL the capture would have FAILed here; it did not.

## H-01..H-30 matrix (profile requirements from `../qgate-02/host-profile-requirements-matrix.md`)

Run-level result: **FAIL: none; PASS: unknown count; BLOCKED: at least one, ids UNREAD.** No row below can be reported as PASS or BLOCKED by the builder without reading the artifact.

| Req | Area | QGATE-03 observed status |
|---|---|---|
| H-01 | Kernel / OS | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-02 | Kernel / OS (distro, kernel) | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-03 | Filesystem | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-04 | Interpreter | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-05 | Interpreter (ingress equality) | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-06 | Interpreter / dependencies | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-07 | Launcher / ingress support | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-08 | Launcher (isolation) | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-09 | Process and UID separation (ingress) | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-10 | Process and UID separation (client) | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-11 | Peer-UID allowlist | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-12 | Process capabilities | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-13 | Ptrace / Yama | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-14 | Ptrace / dumpability | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-15 | Process isolation (denials) | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-16 | Socket permissions | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-17 | IPC directory | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-18 | Outsider denial | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-19 | Peer credentials | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-20 | State-directory permissions | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-21 | State-directory group access | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-22 | ACLs | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-23 | Ancestors | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-24 | Invocation constraints | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-25 | Journal mode | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-26 | Host identity: evidence label | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-27 | Provenance: pins and manifests | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-28 | Provenance: record hash and envelope | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-29 | Freshness and scope | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |
| H-30 | Not-run-by-script evidence | not FAIL (no check failed in the run); PASS vs BLOCKED per id UNREAD |

## Remaining gaps and unknowns (classified)

1. **Per-check results**: UNREAD (artifact unreadable to the builder). Operator action: attach artifact `13023553992`.
2. **IPC directory mode 2750 vs 2751**: at the profile's 2750 the outsider cannot traverse, so `qualification.outsider_denied_socket` can only be BLOCKED (dry-run sandbox behaviour, DERIVED from the script, not observed on the runner). A supplementary 2751 record (not the verdict basis) is in the artifact. Which value governs is an Architect/operator decision; the profile was not changed.
3. **Component commit pins**: declared only (`--accept-unverified-pins`); source identity is carried by provenance/`cp_head`/`rt_head`, not by the capture.
4. **Not environment-scope** (not required to pass here): declarative, Qualification-gate-owned and not-run-by-script evidence (live propose round trip, adversarial proposals, Python 3.11, OS-kill), per `h-matrix-reconciliation.md`.
5. **Peer-UID controls** (positive client, negative non-allowlisted group member, negative outsider): recorded in `peer-uid-controls.json`; results UNREAD.
6. **Same-lineage only**: builder, workers and reviewers share one lineage; D1 roles remain NOT YET INSTANTIATED.

## Next accountable action

Operator downloads artifact `13023553992` (expires 2027-01-29) and attaches it; the per-id matrix and this verdict are then confirmed or corrected without any new run. The operator/Architect rules on the IPC-directory mode (2750 vs 2751). No second run is requested or authorized.
