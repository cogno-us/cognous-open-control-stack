# Investigation findings: route B effect reachability and exact-candidate harness (2026-10-23)

Status: record of two read-only investigations ordered by the architect (Q-series, MVP recovery). Non-authorizing; release, publication and production remain on HOLD. This is not a Qualification verdict and not an independent reproduction. Labels: VERIFIED = reproduced by execution in a scratch harness during this programme (still a builder observation, not a Qualification result); REPORTED = stated in a worker report or a repository document and not re-checked; UNVERIFIED = not established. Scratch evidence: `/tmp/wk/mvp/H/` (harness, `run/claim2.py`), `/tmp/wk/mvp/R/` (reachability source copies), `/tmp/wk/mvp/B/`.

Python note: Control Plane serialization and the Verifier need pydantic >= 2.12 (Qualification lock: 2.13.5); pydantic 2.11.9 gives false Verifier refusals. The harness used a 2.13.5 copy.

## 1. Exact-candidate harness (investigation H)

| # | Finding | Label |
|---|---|---|
| H1 | `journal_check_reused` is reproduced on a record issued through the real claim path: `provision_local_execution_claim` calls `workflow._resolve(frozen, now, inputs=inputs)` without `stage`/`check_ref` (Control Plane `local_authority_effect.py` about lines 361-362), then `_record_check(..., 'claim')`. The decision path (`bounded.py` about 1634-1639) and the effect path (about 1684-1689) pass `stage`/`check_ref`. Control run without a claim does not show the defect. | VERIFIED (execution, `H/run/claim2.py`; line numbers from source reading) |
| H2 | The pinned Verifier (c0b8ba1f) cannot ACCEPT a route B record: it ABSTAINs on `v4.ledger.rows-agree-with-attempts`. Whether the cause is an inherent absence of an attempt layer on route B (architect Q5 treats this as conditionally legitimate) is not yet established by Qualification. | VERIFIED (ABSTAIN observed); cause UNVERIFIED |
| H3 | No Qualification job currently runs the MVP chain (Control Plane ingress, route B, Replay/Evidence Pack, Verifier) at the exact tuple. | REPORTED (workflow and tree inspection) |
| H4 | The four ODES failures (of 3094 tests; 1 skipped) are `test_control_legacy_export_is_digest_identical_to_the_retained_example`, `test_explicit_export_end_to_end`, and the two `lost_ack.package.json` / `prior_absence.package.json` semantic-layer cases. The two package cases are stale examples. Whether the MVP chain consumes them is UNVERIFIED (architect Q15 requires establishing this first). | REPORTED (junit from a 2026-10-21 run); stale-example characterization REPORTED |
| H5 | `g9-r10` is a manifest placeholder: the refreeze-log amendment 127 records manifest digests "as the candidate g9-r10"; no run of it exists or is decided. | REPORTED (repository document, `B/kl.md`) |
| H6 | Replay behavior on the claim-issued record has not been run. | UNVERIFIED (Replay reproduction pending, architect Q4) |

## 2. Effect reachability of route B (investigation R)

| # | Finding | Label |
|---|---|---|
| R1 | Static inventory of effect-capable entry points on the selected route: 16 numbered items (#1-#16), each to be classified as mediated, disabled or excluded by Qualification. Item-level classification lives in the investigation report, not in this repository. | REPORTED (source reading) |
| R2 | Unmediated surfaces found: `provision_claim` / `execute_claim_atomic` (claim authenticity is an unkeyed hash); the `simulate` parameter; authority writers (`set_grant_status` and similar); raw SQL on the destination. | REPORTED (source reading) |
| R3 | Legacy surfaces are gated by the atomic-marker check at `engine/safe_executor.py` lines 773-779 of the runtime. | REPORTED (source reading) |
| R4 | Trusted-host narrowing (architect Q9): a single designated ingress process holds destination write access and authority-writer capability, fixes operation identity and `simulate=None`, and does not expose claim APIs. Enforcement for the supported client is not yet tested. In-process callers and the database file holder remain outside the guarantee. | Proposal; enforcement UNVERIFIED |
| R5 | D09 (bypass and interruption) evidence exists at Runtime `4a83b175`, not at the candidate Runtime `ec728da6`; it is comparative material only and the controls must be re-run (architect Q13). | REPORTED (matrix and refreeze log) |
| R6 | D09 `route_inventory` reports four issues; the report does not enumerate their identities. | REPORTED; identities UNVERIFIED |

## 3. Classification (architect Q1)
The claim-journal defect is an evidence-integrity and release-assurance defect on the supported route. It is not, by itself, evidence of unauthorized execution or an effect-time authorization bypass.
