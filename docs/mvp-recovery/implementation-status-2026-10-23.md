# OCS MVP implementation status (2026-10-23)

Status: non-authorizing status record. Release, publication and production remain on HOLD. Nothing here is a Qualification verdict, a security clearance, a certification or a production-readiness claim; the builder does not self-certify, and Qualification owns oracles and verdicts. This file records facts with source labels and does not rewrite earlier mvp-recovery records.

Labels:
- VERIFIED: read or executed by the author of this record in this session (GitHub REST metadata read, or a file read at a named revision).
- REPORTED: stated by a PR description, a worker report or an operator message; not independently re-run here.
- UNVERIFIED: not established by anyone; stated so that it is not assumed.

Scope of the MVP is unchanged (see [mvp-definition.md](mvp-definition.md)): matched $10 synthetic refund, Linux single host, Control Plane ingress, route B atomic executor with operation identity (journal mode), trusted-host boundary, Replay and Evidence Pack reconstruction, and a separate bounded Verifier assessment.

## 1. Operator-authorized F3 changes

Both changes are reported (operator messages, not re-read here) to have been authorized by the operator for the exact scope stated. Neither authorization extends to any other change.

### 1.1 Control Plane F3 (cognous-control-plane PR #83)

| Item | Record | Label |
|---|---|---|
| Authorization | Operator authorization of the exact F3 package | REPORTED (operator message) |
| Scope | Claim-stage journal repair: bind the claim-stage check to stage `claim`, the decision and a distinct `check_ref` in `src/agent_control_plane/local_authority_effect.py`, plus new `tests/test_claim_journal_stage.py`; nothing else | REPORTED (PR description); VERIFIED that the old-to-new diff touches only those two files (+10/-2 in the source file) per the pin reconciliation record |
| PR state | #83 closed, merged | VERIFIED (GitHub REST) |
| Base | `0a41faa972699f7ec3063967a14cd9bdd3e67d27` | VERIFIED |
| PR head | `df4794c8d81489cc574174ee2b0b0b55aaa78c4d` | VERIFIED |
| Merged revision | `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c` | VERIFIED |
| Defect addressed | `provision_local_execution_claim` recorded the claim check without stage and `check_ref`, so the pinned Verifier refuted real claim-provisioning records (`journal_check_reused`, `resolution_check_not_in_journal`) | REPORTED (F3 package); reproduced pre-patch in the Verifier assessment (REPORTED: retained output of that run, not re-run here) |
| Evidence | New tests 13 passed / 1 skipped, 8 fail with the patch reverted; mutation checks detected; no-claim record hashes byte-identical before and after; independent review APPROVE-WITH-NOTES | REPORTED |
| Known caveat in that evidence | Full suite showed 2 failures (E024, E025) identical before and after the patch; the installed Action Manifest was not the pin `fa170815`; to be re-verified at the pin | REPORTED |
| Verifier after the patch | Overall ABSTAIN, not ACCEPT (see section 4) | REPORTED (Verifier assessment) |

### 1.2 Replay F3 (cognous-replay-bundle PR #78)

| Item | Record | Label |
|---|---|---|
| Authorization | Operator authorization under the continuous-execution authorization | REPORTED (operator message) |
| Scope | Admit the Runtime `failure_class` member on route B pre-dispatch denial exports (security-generation profiles, denied and non-attempted results only, closed six-value Runtime vocabulary, only together with `failure_record_id`; recovery-report branch unchanged; unknown is never converted to denial); re-tie the P2 Control Plane pin from `0a41faa9` to `7a4bcd40` with fixtures re-captured | REPORTED (PR description) |
| PR state | #78 closed, merged | VERIFIED (GitHub REST) |
| Base | `028f63d1` | REPORTED |
| PR head | `6fe83a27c66b50b8c27dcc094a6ae83614f5fa71` | VERIFIED |
| Merged revision | `ab421ad0fdc6a24999273adf82455968953598ae` | VERIFIED |
| Evidence | Full suite 1294 passed, 13 skipped, 8 xfailed (the same 8 retained), 0 failed, against a baseline of 1251/13/8; 43 new tests, each predicate clause mutation-checked; denial chain on Control Plane `7a4bcd40`: base REFUSED, branch reconstruction complete; independent review approve-with-notes | REPORTED |

## 2. Pin cascade status

Source: `PIN-RECONCILIATION.md` (Control Plane `0a41faa9` to `7a4bcd40`), plus the merge facts below.

### 2.1 Merged so far

| Change | PR | Merged revision | Label |
|---|---|---|---|
| Control Plane F3 | cognous-control-plane #83 | `7a4bcd40` | VERIFIED |
| Replay F3 and P2 re-tie | cognous-replay-bundle #78 | `ab421ad0` | VERIFIED |
| Evidence Pack P2 re-pin (Replay `ab421ad0`, Control Plane `7a4bcd40`; pin and fixture change only) | cognous-governance-evidence-pack #63 | `79ae34d9dc0ca37cabd67b10793a46a972b986fd` | VERIFIED merged; evidence REPORTED (373 passed, 1 skipped at baseline and on branch; denial chain through the Pack imports and validates) |
| Hub Oct-31 mvp-recovery documentation (schedule, investigation findings, architect rulings; docs only) | cognous-open-control-stack #216 | `349732fa` | VERIFIED merged (merge commit title and file list read in the hub history); this is not the pin reconciliation |
| Hub Control Plane pin reconciliation (metadata-only pins, dated notes) | none yet; local branch `ocs-cp-7a4bcd40-pin` only | not merged | REPORTED (PIN-RECONCILIATION.md); the hub lock on `origin/main` still selects Control Plane `0a41faa9` (VERIFIED, read) |
| Hub trusted-host ingress | cognous-open-control-stack #217 | `43c526eb` | VERIFIED merged |

### 2.2 What remains

| Item | State | Label |
|---|---|---|
| ODES re-pin (open-decision-evidence-standard #139) | Merged at `eae95dd3` (head `1f0989e8`); required checks passed on the exact head; independent review approve-with-notes. Replay `ab421ad0` and Control Plane `7a4bcd40` pins; 4 historical failures unchanged. | VERIFIED (GitHub REST) / REPORTED (review) |
| Exchange re-pin | Not started. Needs the Replay, Pack and ODES shas in the same profile change. Exchange is outside the stated MVP scope | REPORTED |
| Verifier provenance bump | Optional. The vendored reason registry bytes are identical at `7a4bcd40`; a provenance-only bump needs its own F3 and is not required if "registry unchanged between the two shas" is accepted | REPORTED |
| Qualification profile r14 | Not started. Needs a new profile file, refreeze-log entries, workflow pins and test literals, with an owner-authorized refreeze. Frozen profiles and `results/` are not rewritten | REPORTED |
| Hub lock reconciliation | The lock entries for Replay, Pack and ODES (and Exchange if kept) move only after the merges above. Until then the lock may select Control Plane `7a4bcd40` while a component in the same lock still accepts only `0a41faa9` in its P2 profile; whether to land the hub change alone or together with the follow-up is a governor decision | REPORTED |

## 3. Open mandatory failures (preserved, not relabelled)

None of these is resolved by this record. A failed mandatory control is a failure.

| Item | Record | Label |
|---|---|---|
| NC1-04 approval terminality | FAIL. Kept as a failure | REPORTED (operator message); no evidence file was re-read for this record |
| ODES historical failures | 4 failures, the same set before and after the re-pin; not relabelled | REPORTED (PR description of #139) |
| ODES exporter `recovery_observations` defect | `export_cognous_stack_package` fails on Replay bundles carrying a route B recovery report because `_extract_replay_inputs` rebuilds the executor export without `recovery_observations`. Pre-existing at ODES `e86a25a1` and Replay `028f63d1`; reproduced, not fixed. Denied and executed bundles export | REPORTED (PR description of #139) |
| Exchange and route C identity mismatch at Control Plane `7a4bcd40` | Under investigation | REPORTED (operator message); cause UNVERIFIED |
| Route C flakiness | Under investigation | REPORTED (operator message); cause UNVERIFIED |

## 4. Trusted-host ingress (hub PR #217)

Source: `tools/mvp_ingress/BOUNDARY.md` at hub `origin/main` (`43c526e`), which this section summarizes; that file governs.

What was built (VERIFIED by reading BOUNDARY.md at `43c526e`; execution results below are REPORTED by it):
- One designated ingress process holds the destination write path, the authority-store and authority-writer capabilities, claim provisioning and execution, and the Control Plane workflow, inside an owner-only state tree (directory `0700`, files `0600`).
- The only client surface is one Unix socket and one closed JSON operation (`mvp-refund-proposal/1`, six members, at most 4096 bytes); the response is a closed object with outcome `executed`, `refused`, `held` or `unknown`.
- `simulate=None` is hard-coded; the operation id is derived by the Runtime, not the client; a reserved `request_id` is never executed again once claim provisioning was reached (no blind retry); ambiguous outcomes map to `unknown`.

Reported execution observations: 205 boundary tests passed on Python 3.13 against Control Plane `0a41faa9` and merged `7a4bcd40`; a second process as uid 65534 could not read or write the destination or authority store and got only closed codes; kill -9 at random points never re-executed a request.

Boundary and limits (as stated in BOUNDARY.md):
- The boundary holds for a distinct unprivileged uid that can reach only the socket, and it was observed in one tested configuration only. Same-uid clients, root, shared-uid containers, in-process use and anything with `ptrace` or `DAC_OVERRIDE` are outside it. A deployment whose client runs as the ingress uid has no boundary.
- The default socket mode is `0600`; a distinct-uid client needs a deliberate mode and allow-list.
- Parent-directory checks run at startup only; they ignore ACLs.
- The authority is the Control Plane's fixed synthetic fixture, imported from Control Plane test code; it is not production IAM. Only one operation is admitted (`case-1`, `customer-001`, $10 USD, `duplicate`); anything else is held.
- No client authentication beyond socket permissions and the optional peer-uid list; no channel confidentiality; denial-of-service protection is limited to a request cap, a read deadline and serial handling.
- No admin channel for authority changes; the owner uid must make them out of band. A request row left `inflight` is permanently refused and must be reconciled by the owner before any new, separately approved request.
- The `simulate` check is a static AST scan with stated blind spots.
- Ambiguous-commit, lost-acknowledgement, revocation-race and evidence-tampering behaviour remain Qualification's controls.
- Python 3.11 integration was not run, and a real `lost_ack` outcome through the live route is unreachable by design (UNKNOWN mapping is covered with a fake executor).

## 5. Verifier assessment (route B)

Source: `VERIFIER-ASSESSMENT.md` (Worker G). Observations only; no PASS or acceptance is declared. Pins: Verifier `c0b8ba1f`, Control Plane pre-patch `0a41faa9` and post-patch `df4794c8`, Runtime `ec728da6`, pydantic 2.13.5. Label for this section: REPORTED (retained outputs of that run; not re-run for this record).

- Post-patch, executed and lost-ack scenarios: exit 3 ABSTAIN, 27 confirmed, 1 could-not-check, 0 refuted of 28 checks. Pre-patch the same scenarios were exit 1 reject with two refutations (`v2.lifecycle.journal_protocol` `journal_check_reused`; `v2.profile.operation-identity` `resolution_check_not_in_journal`).
- The one non-confirmed check is V4 `v4.ledger.rows-agree-with-attempts`, reason `attempt_rows_not_in_record` (read the extension `x-reason`; the closed field reads `tier_unavailable`). The attempt layer exists at the destination; the route B run record does not carry it.
- Q5(d) is only partly established. The Verifier-owned condition (applicable checks retained, explicit V4 abstention) is observed. Directive criteria 2 (grant changes and duplicate protection), 4 (UNKNOWN and no blind retry), 5 (Replay and Evidence Pack reconstruction) and 7 (negative controls on the exact candidate) are not evidenced by the Verifier output and depend on destination-side rows, Replay, Evidence Pack and Qualification.
- Claim text must not say "all other V4 checks pass". Of the V4 checks, four are confirmed, one abstains and two have no items on this route (`v4.ledger.acknowledged-attempts-have-rows`, `v4.ledger.observations-agree`).
- A Verifier exit 3 is an abstention, not an acceptance. An exit 0 or 3 does not attest that an effect committed or was refused: the run record is identical in shape for executed, lost-ack and refused-at-effect, and a consistent rewrite of both ledger rows and counts turned exit 3 into exit 0 in a probe. The ledger is trusted by deployment.
- The assessment used the Control Plane fixture amount of 50 USD, not the matched $10 profile, a harness-only `simulate="lost_ack"` for the lost-ack case, and the local F3 commit `df4794c8` rather than the merged `7a4bcd40`. It must be regenerated with the $10 fixture, the frozen ingress and the merged revision before any claim text cites it.

## 6. Known limitations

- Runtime CI skips the route B tests that need the local-authority-effect contract at its pinned Control Plane (`2ea9528e`), so the claim-journal fix is not exercised by Runtime CI unless a separate Runtime pin decision is made (REPORTED, PIN-RECONCILIATION.md; Runtime has no `0a41faa9` reference).
- Python 3.11 integration was not run (REPORTED, #217 description and BOUNDARY.md).
- ODES was not exercised in the supported chain here (REPORTED); its re-pin evidence is a full-suite run with the failures in section 3.
- Pydantic 2.12 or later is required for correct Control Plane serialization; 2.11.9 produces false Verifier refusals (REPORTED, builder preamble).
- Replay, Evidence Pack and ODES reconstruction of the route B chain through the live ingress on the merged tuple is UNVERIFIED in this record.
- The exact candidate tuple is not frozen by this record; freezing is a later, separately authorized step.

## 7. What this record does not do

It does not change the component lock, any locked component, any acceptance criterion or any release state. It does not declare a Qualification outcome. Release, publication and production remain on HOLD until independent Qualification and explicit operator approval.
