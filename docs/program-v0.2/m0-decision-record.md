# M0 decision record (operator, 2026-10-22)

**Successor decision document** for the [M0 decision packet](s02/m0-decision-packet.md), as [operator-decisions.md](operator-decisions.md) requires. Release and production remain on HOLD. This record authorizes the implementation scope in section 3 and nothing else.

## 1. What was decided, and how it was given

In the session on 2026-10-22 the operator (André de Lima) was asked whether to approve the M0 packet recommendations, rows 1 to 20, as written, and answered "Approve all as recommended". This record is the builder's transcription of that answer. The source is the session transcript; no other review is implied. If a row below misstates what was intended, a successor record supersedes it.

Recorded interpretation: where the packet's recommendation is "Approve", the row is approved. Where the recommendation is "Review" (rows 6, 10, 11), the recommendation is followed literally: the item is accepted as review input, it is not adopted as a final designation, and the cited follow-up still applies.

## 2. Outcome by row

| # | Subject | Outcome |
|---|---|---|
| 1 | ADR-P01 canonical JSON: JCS for new commitments, legacy kept as a named profile | Approved |
| 2 | ADR-P02 scanners: reconcile all three, classify differences, then one normative behavior | Approved; any behavior change still returns to the operator |
| 3 | ADR-P03 registry location: hub-owned immutable digest-pinned artifact | Approved |
| 4 | ADR-P04 overlay objective: fewer sequential layers | Approved; step 1.7 measures layer depth first and fixes a number |
| 5 | ADR-P05 ownership: one bounded refund scenario migrates to the Orchestrator; Qualification keeps independent expectations | Approved |
| 6 | ADR-P06 path-ownership proposals | Reviewed as proposals; no repository setting is changed by this record |
| 7 | ADR-P07 reconcile-only, P08 coverage mandatory, P09 OpenAPPA optional | Approved |
| 8 | M1 rule family | Scanner family for the two unlocked consumers (hub, ergonomics); the verifier copy is a named M2 exclusion |
| 9 | SP-01 stable identity: existing ODES `operation_id` profile | Approved |
| 10 | Effect-surface designations for the five surfaces | Accepted as review input; security review after a static reachability pass remains required before the classes enter the frozen profile |
| 11 | F3 packages FP-01 to FP-05 | Reviewed; none starts without separate authorization |
| 12 | Workflow vocabulary: 12 `workflow.*` states | Approved |
| 13 | AOI envelope and canonical JSON profile | Approved: reuse the step 1.3 profile. The pin carrier's owner is open and is named in the step 1.4 contract work |
| 14 | AOI identity references | Approved: reuse existing identifiers; agent attestation UNSUPPORTED by default |
| 15 | AOI event classes and missing-field semantics | Approved |
| 16 | M1 approval-bearing and state-changing paths | Approved: only those the one bounded refund scenario exercises. The AOI estimate delta is therefore included in planning from the successor estimate revision |
| 17 | Enforcement versus observation minimum | Approved: enforcement stays the gate; observation is reported separately |
| 18 | Integrity, custody and redaction boundaries | Approved: custody stays in each store; per-field redaction and retention declared in the profile |
| 19 | AOI locked-component F3 changes | Approved as recommended: none for the minimum; FP-05 contingent |
| 20 | Optional OTel and ISS linkage | Approved as recommended: OTel contract-only; ISS only after an ISS-owned accepted export; both outside M1 |

## 3. Implementation scope authorized

The operator chose to start both of these in parallel:

- **Step 2.1**, versioned rule records and a bounded store, in the hub, per [contract 1.3](s02/contracts/1.3-registry-r0.md).
- **Step 3.1**, lock-driven Orchestrator admission pins, per [contract 1.4](s02/contracts/1.4-evidence-handoff.md) section 5. The historical `o6-q5` constants stay as history.

Constraints that continue to bind: synthetic SQLite and no network, subprocess or production credential effect; no locked-component code change (any such change needs its own F3 authorization, packages FP-01 to FP-05); no edit to Qualification expectations, oracles, verdict logic or its controller #218; one PR per bounded change, with a test for each behavior change; no pin selection by the handoff; no release.

## 4. What this record does not do

It does not freeze Qualification's independent expectations (Qualification's decision), does not change repository settings, does not select or advance any pin, does not adopt an Engineering Constitution revision, and does not lift HOLD. Implementation PRs are candidate work: they do not qualify themselves and are not accepted until independently qualified.
