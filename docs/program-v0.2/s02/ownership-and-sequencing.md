# Orchestrator–Qualification ownership and sequencing

Proposed, documentation only. Applies [ADR-P05](adr-proposals.md#adr-p05-refund-chain-ownership-and-migration-order).

## Three separate changes

S01 found that the separation-of-powers problem is partly reversed implementation ownership: Qualification owns most integration assembly (`suites/v1-scenarios`, 15,932 lines, 303 tests; `run_matched_refund.py`) and does not execute or consume the orchestrator, while the orchestrator holds about 1.3k lines of acceptance and verdict-like modules ([s01/defects.md](../s01/defects.md) PD-A02). The program therefore separates three changes and does not combine them in one implementation sprint.

| Change | Owner after v0.2 | Effect on other owner |
|---|---|---|
| A. Migrate engineering integration responsibility | Orchestrator (engineering) | Qualification stops being the assembly owner for the migrated path; its history stays |
| B. Retain frozen independent tests, oracles and verdicts | Qualification | Producer cannot edit expectations or verdict logic |
| C. Operational workflow coordination (durable state, bounded authority) | Orchestrator | Adds no verdict power; no permission or grant authority |

Order: A with a source-preserving handoff first, then C. Doing C first would add a third execution path while the existing duplication remains. B is a standing boundary, not a work item for engineering.

## Dependency corrections that follow

| Step | Was | Now | Reason |
|---|---|---|---|
| 3.4 Qualification handoff integration | 1.4, 3.2, 3.3 | 1.4, 3.1 | The source-preserving handoff is established over the existing candidate and admission seed (orchestrator `o6-q5/candidate.json`, `admission.py`) before coordination exists |
| 3.2 Durable single-host workflow | 3.1 | 3.1, 3.4 | Operational coordination follows the handoff |

3.3, 3.5 and 3.6 keep their prerequisites (3.3: 3.1, 3.2; 3.5: 3.2, 3.3; 3.6: 3.4, 3.5), so the graph stays acyclic. Sprint packaging follows: S07 holds 3.1 and 3.4, S08 holds 3.2 and 3.3, S09 is unchanged. The registry and orchestration tracks have disjoint owners and no dependency between them until step 4.1, so they may proceed in parallel once separately authorized; a sprint number is packaging, not ordering.

Step 3.4 also names a Qualification ingestion job. That job is a Qualification controller change and is Qualification's decision, not an engineering deliverable; engineering delivers the producer side only.

## Qualification-owned items

Listed so Qualification can decide independently under its own controller. Engineering does not edit expectations, oracles or verdict logic in this workstream, and this package does not post to or change Qualification's controller.

| Item | Evidence | What the independent review asks Qualification to prioritise |
|---|---|---|
| R14 probe verdict | Probe job reports PASS whenever any case ran, `tools/v1_validation.py:678-681`; 17 retained probe records PASS with return code 1; g8-r10 has none (PD-F03) | Fix, and an impact assessment of claims that rely on affected job-level verdicts. It does not automatically invalidate every historical result |
| Scope-reduction disclosure | No rule requires a disclosure record before a row becomes non-mandatory; 36 scope-reduction rows are machine-recorded (PD-E02, PARTIAL) | Decide a check and the verdict semantics |
| Frozen-input hash coverage | `requirements.json` (131 rows) is outside the freeze-manifest hashes; `qualification_file_hashes` has 2 entries (PD-A05) | Assess the freeze boundary before new integrated results are relied on |
| Applicability decisions | prp and tfa jobs NOT RUN; wiki-derived suite not collected (PD-F01, PD-F02) | Decide NOT APPLICABLE versus a suite versus a component change |
| Comparator digests | No workflow runs the comparators tests; two digest generators, four digest locations (PD-F04) | Wire a test into an existing tooling job |

## Carried-forward obligations

| Obligation | Source | Handling in this package |
|---|---|---|
| Orchestrator recovery evidence is pinned behind the selected tuple (Q6 on runtime `1b0a9e32`, 169 commits behind) | PD-L07 | Historical acceptance is not evidence for a new tuple; step 3.5 re-pins before citing |
| Source identity does not bind every input that influences a verdict | PD-A05 | Qualification-owned (above); step 1.7 lists it as an independent prerequisite |
| Earlier OpenAPPA and AGT integrations exist | PD-C02 | Step 1.6 states reused, incomplete and justified-new work ([ADR-P09](adr-proposals.md#adr-p09-openappa)) |
| Overloaded `action_id`, `effect_id` changing with `grant_revision`, two attempt-id namespaces | PD-L03 | Step 1.5 identity crosswalk; reconcile contracts, add no universal identity service |
| Critical-path membership is not a mandate to change code | [s01/issues-disposition.md](../s01/issues-disposition.md) | Step 4.3 records for each item: fix, explicit claim-scope exclusion, or deferral. A security or functional blocker cannot be closed by documentation alone |
| Evidence labels | S01 | VERIFIED means read at source at the stated revision; it supports static architectural observation, not exploitability, execution correctness or runtime isolation |
