# Architect rulings, third set (2026-10-23, rulings 1-8), known limitations and the Oct 24-31 critical path

Status: non-authorizing record. Release, publication and production remain on HOLD. Nothing in this document is a Qualification verdict, an independent acceptance, a security clearance, a certification or a production-readiness claim. The author did not self-certify and did not re-run any test for this record. Qualification owns oracles and verdicts. Earlier records are not rewritten: [architect-rulings.md](architect-rulings.md), [architect-rulings-2.md](architect-rulings-2.md), [implementation-status-2026-10-23.md](implementation-status-2026-10-23.md), [mvp-definition.md](mvp-definition.md).

Labels (as in the implementation status record):
- REPORTED: stated by an operator message, a PR description or a worker report; not independently re-run or re-read here.
- VERIFIED: read by the author of this record in this session. In this record only the hub documents named above were read (at hub `main` `7b38ae62`). Every PR number, head sha and test count below that is not in those documents is REPORTED.
- UNVERIFIED: not established by anyone.

## 1. Architect rulings of 2026-10-23 (1-8) and dispositions

Source of the rulings and dispositions: operator message to the author of this record (REPORTED). The rulings are architectural decisions, not reproductions or verdicts.

| # | Subject | Ruling as summarized | Disposition | Label |
|---|---|---|---|---|
| 1 | NC1-04 Runtime F3 | Option A: a bounded Runtime F3 repair. | Pending operator approval of the exact patch. Candidate: PR #144 in `cogno-us/cognous-execution-runtime`, head `d291eda7`. No approval is recorded here; the PR is not treated as accepted. NC1-04 approval terminality stays a FAIL until independently requalified. | REPORTED |
| 2 | NC4-03 predicate | The predicate needs correction; the guarantee being tested must remain unchanged. | Correction proposed via Qualification PR #222, under independent review. The review outcome is not known to this record. A predicate change that weakens or redefines the guarantee is not acceptable under this ruling. | REPORTED |
| 3 | Verifier claims | Keep the Verifier claims narrow. | The narrow evidence claim in [mvp-definition.md](mvp-definition.md) stands. V4 `v4.ledger.rows-agree-with-attempts` abstains (`attempt_rows_not_in_record`); an ABSTAIN is not a PASS. Claim text must not say "all other V4 checks pass". | REPORTED (ruling); VERIFIED (the existing claim text) |
| 4 | Denied-second-execute | Accepted, with a no-retry proof. | The second execute after a denial is accepted as behavior only with a proof that no retry occurs. The proof is required, not yet independently established in this record. | REPORTED |
| 5 | Exchange / route C | Excluded from the MVP profile. | Needs a separate applicability mapping and a verified exclusion (that the MVP chain does not consume Exchange or route C). Until the exclusion is verified it is a claim, not a fact. Route C defects stay registered (section 2). | REPORTED |
| 6 | ODES recovery export | Deferred. | Not in the MVP chain; the exporter defect is registered, not fixed (section 2). | REPORTED |
| 7 | Qualification job | An exact-tuple Qualification job is required, with zero unexplained skips in the mandatory battery. | Every skip must carry a recorded explanation; an unexplained skip is a failure of the battery, not a pass. Skip counts are not retrospectively re-denominated. | REPORTED |
| 8 | Trusted-host boundary | Conditionally sufficient for the MVP. | Supported scope is Linux with Python 3.13 only. Hub PR #219 holds the environment record, with two decisions still open: the socket policy and the `ptrace` question. The conditions in [mvp-definition.md](mvp-definition.md) remain the stop conditions. | REPORTED |

## 2. Known limitations and defect register

Nothing below is resolved by this record. A failed mandatory control is a failure and is not relabelled.

| Item | Record | Label |
|---|---|---|
| Route C identity mismatch | 5 of 32 cases mismatch identity at Control Plane `7a4bcd40`. Raw result retained, unchanged. Cause UNVERIFIED. | REPORTED |
| Route C determinism flake | About 1 run in 5 differs. Raw, unchanged; not averaged away. Cause UNVERIFIED. Outside the MVP profile only if ruling 5 exclusion is verified. | REPORTED |
| ODES exporter `recovery_observations` drop | `export_cognous_stack_package` fails on Replay bundles carrying a route B recovery report, because `_extract_replay_inputs` rebuilds the executor export without `recovery_observations`. Pre-existing; reproduced, not fixed. Denied and executed bundles export. | REPORTED (PR description of ODES #139, via the status record) |
| ODES historical failures | 4 failures, the same set before and after the re-pin. Not relabelled. | REPORTED |
| Python 3.11 | Unqualified. Integration was not run. Only Python 3.13 is in scope. | REPORTED |
| Runtime CI skips | Runtime CI skips 33 route B tests at its pinned Control Plane `2ea9528e`, so the claim-journal fix is not exercised by Runtime CI without a separate Runtime pin decision. The exact-tuple Qualification job (ruling 7) must cover this gap, with the skips explained. | REPORTED |
| Ingress boundary scope | Holds only for a distinct unprivileged uid that can reach only the socket, observed in one tested configuration. Same-uid clients, root, shared-uid containers, in-process use and anything with `ptrace` or `DAC_OVERRIDE` are outside it. | VERIFIED (BOUNDARY.md as summarized in the status record, not re-read here) / REPORTED (observations) |
| V4 abstention | Verifier abstains on V4 attempt-ledger agreement because route B does not emit the attempt layer in the run record. Complete V4 ledger conformance is not claimed. | REPORTED (Verifier assessment) |
| Policy-writer reversibility | The authority/policy writer can change or revert policy; this is a residual trust-boundary limitation, not closed by the MVP. | REPORTED |
| Evidence-writer reversibility | The evidence writer can alter or revert evidence (a consistent rewrite of ledger rows and counts turned a Verifier exit 3 into exit 0 in a probe). Residual trust-boundary limitation; same-host custody, no external anchor. | REPORTED |
| `remove_authoritative_state` | Out of scope for the MVP; no claim is made about it. | REPORTED |
| Superseded fixtures | The $50 Control Plane fixture and harness-only `simulate="lost_ack"` used in the earlier Verifier assessment are superseded for claim purposes. The assessment must be regenerated with the matched $10 fixture, the frozen ingress and the merged revision before any claim cites it. | REPORTED |
| Pydantic | 2.12 or later required; 2.11.9 gives false Verifier refusals. | REPORTED |
| Replay / Evidence Pack / ODES reconstruction through the live ingress on the merged tuple | UNVERIFIED. | UNVERIFIED |

## 3. Critical path, Oct 24-31

Every date below is a TARGET, not a verified date and not a commitment. Dependencies are operator and independent-reviewer actions that this record does not control. A slip in any item moves everything after it; [delivery-estimate.md](delivery-estimate.md) ranges still apply.

| Target | Step | Depends on | Stop or fail condition |
|---|---|---|---|
| Oct 24 | Operator decision on exact Runtime F3 patch (PR #144, head `d291eda7`, ruling 1). | Operator | No approval: NC1-04 stays FAIL; no refreeze. |
| Oct 24-25 | Independent review of Qualification PR #222 (ruling 2); confirm the guarantee text is unchanged. | Independent reviewer | Guarantee changed or review rejects: predicate not accepted. |
| Oct 25-26 | Applicability mapping and verified exclusion for Exchange / route C (ruling 5); no-retry proof for denied-second-execute (ruling 4). | Qualification | Exclusion not verifiable: route C returns to the MVP risk set. |
| Oct 26-27 | Close or explicitly carry the open decisions in hub PR #219 (socket policy, `ptrace`) (ruling 8). | Operator, governor | Boundary conditions cannot be enforced: profile does not hold. |
| Oct 27-28 | Pin cascade and tuple refreeze (Runtime pin decision, hub lock reconciliation, Qualification profile r14), owner-authorized. | Operator | Pin mismatch unresolved. |
| Oct 28-30 | Exact-tuple Qualification job, mandatory battery, zero unexplained skips (ruling 7); regenerate Verifier assessment with the $10 fixture and merged revision. | Qualification | Any unexplained skip, or any mandatory FAIL, is recorded as such. |
| Oct 30-31 | Acceptance dossier with outcomes PASS, FAIL, ABSTAIN, INCONCLUSIVE, BLOCKED, NOT RUN; operator release decision. | Independent reviewer, operator | Release stays on HOLD unless independently accepted and explicitly approved. |

## 4. What this record does not do

It does not approve PR #144, accept PR #222, change the component lock, any locked component or any acceptance criterion, declare a Qualification outcome, or lift the release HOLD. Wording on clearance, certification and production readiness is intentionally absent: none is claimed.
