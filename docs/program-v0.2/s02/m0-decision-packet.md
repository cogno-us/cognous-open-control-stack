# M0 decision packet (one page; proposed, non-authorizing)

For the operator. Approving M0 is the operator's act, recorded in a versioned successor decision document linked from controller #193. A merge of any document here does not approve an ADR or M0. Release and production remain on HOLD. Nothing here starts implementation; steps from 2.1 onward need the M0 outcome and their own authorization.

## What M0 covers

Steps 1.1 to 1.7 as contracts: [S02 proposals](adr-proposals.md), [contracts 1.2 to 1.4](contracts/README.md), [S03 drafts for 1.5 and 1.7](../s03/README.md), [workflow state reconciliation](../s03/workflow-state-reconciliation.md), [F3 change proposals](f3-change-proposals.md), [estimates](estimates-m0-m1-m2.md). Static reading only; nothing was executed.

## Decisions requested

Rows 1 to 12 are the S02 and S03 decisions; rows 13 to 20 are the eight mandatory decisions of the AOI addendum ([aoi/README.md](../aoi/README.md) section 6).

| # | Decision | Recommendation | If approved | If not decided |
|---|---|---|---|---|
| 1 | ADR-P01 canonical JSON: JCS for new commitments, legacy kept as a named profile | Approve | Step 1.3 freezes one profile; no locked change needed for registry or handoff digests (FP-02) | Steps 1.3, 1.4 stay open |
| 2 | ADR-P02 scanners: reconcile all three, classify differences, then one normative behavior | Approve | Step 2.2 starts with classification; any behavior change returns for approval | 2.2 blocked |
| 3 | ADR-P03 registry location: hub-owned immutable digest-pinned artifact | Approve | No new repository or pin carrier | 1.3 and 2.1 blocked |
| 4 | ADR-P04 overlay objective: fewer sequential layers | Approve; step 1.7 measures depth first | Target fixed as a number | 4.1 mechanics blocked |
| 5 | ADR-P05 ownership: one bounded refund scenario migrates to the Orchestrator; Qualification keeps independent expectations | Approve | Steps 3.1, 3.4 scoped; estimates remain LOW confidence | 3.x blocked |
| 6 | ADR-P06 path-ownership proposals (settings changes are yours alone) | Review the path classes | Operator applies settings, or declines | No settings change |
| 7 | ADR-P07 reconcile-only, P08 coverage mandatory, P09 OpenAPPA optional | Approve | Frozen into the minimum profile | Profile open |
| 8 | M1 rule family ([1.3 section 8](contracts/1.3-registry-r0.md)) | Scanner family for the two unlocked consumers; verifier is a named M2 exclusion | M1 needs no locked change except the opt-in context member | Estimate keeps the conservative assumption |
| 9 | SP-01 stable identity: select the existing ODES `operation_id` profile | Approve | No new identifier | Identity open |
| 10 | Effect-surface designations for the five surfaces ([seed](../s03/coverage-seed.json)) | Security review after a static reachability pass | Classes become part of the frozen profile | 1.7 and 4.2 open |
| 11 | F3 packages FP-01 to FP-04 | Review; none starts without separate authorization | Each is scoped and costed | No locked change proposed further |
| 12 | Workflow vocabulary: 12 `workflow.*` states; effect and decision records stay referenced | Approve | Step 3.2 vocabulary fixed | 3.2 open |
| 13 | AOI envelope and canonical JSON profile ([aoi/](../aoi/README.md)) | Reuse the step 1.3 profile; name an owner for the envelope's pin carrier | Steps 1.2 and 1.4 freeze the envelope | 1.4 envelope open |
| 14 | AOI identity references and proof-of-binding source | Reuse existing identifiers; agent attestation UNSUPPORTED by default | Identity fields typed | Identity fields open |
| 15 | AOI required event classes and missing-field semantics | Adopt the C02 states; a missing required field is a typed outcome | Step 1.7 declaration frozen | 1.7 open |
| 16 | Which approval-bearing and state-changing paths apply to M1 | Only those the one bounded refund scenario exercises | Human-review fields scoped; estimate delta can be settled | Delta not folded into totals |
| 17 | Enforcement versus observation minimum across the five surfaces | Enforcement per decision 10 stays the gate; observation reported separately | Claim wording frozen | 4.2 open |
| 18 | Integrity, custody and redaction boundaries | Custody stays in each store; redaction and retention declared per field | Per-field policy frozen | Redaction policy open |
| 19 | Which AOI parts need locked-component F3 changes | None for the recommended minimum; FP-05 contingent | Scope costed only if needed | No locked change proposed |
| 20 | Optional OTel and ISS linkage in the qualified profile | OTel contract-only; ISS only after an ISS-owned accepted export | Deferred items named | Stay out of M1 and M2 |

Already decided by the controller and not re-asked: the handoff adds evidence only and selects no pin; static analysis only for this run; Qualification's decisions stay Qualification's.

## What is still open or unverified

- Reachability of each effect surface from the profile path (static pass not yet done); the S01 count of four subclasses was low (6 direct, 12 total by a syntax-tree scan).
- Scanner differences are measured but not classified (deliberate, defect or omission); the hub scanner's rule bodies are not itemized.
- The 44 verifier check identifiers and the Control Plane check bodies are not itemized; Control Plane and ODES disagree on refusal input types (5 versus 11).
- The AGT repository code and the OpenAPPA how-it-works page were not retrievable; claims that depend on them stay unmade.
- Qualification-owned items (R14 probe verdict and impact, hash coverage, scope-reduction semantics, applicability, comparator digests) are listed for Qualification's own decision; this packet does not touch its controller.

## Estimates (central person-days; planning ranges, not commitments)

M0 51; M1 164; M2 75 (a separately labelled AOI delta of +16.5 M0 and +31 M1 central is in [aoi/estimate-delta.md](../aoi/estimate-delta.md) and is not included until row 16 is decided); contingency for refreeze and requalification separate (M1 31, M2 23). The migration scope in decision 5 and the family in decision 8 can move these; recalibration happens at S03 with measured throughput.
