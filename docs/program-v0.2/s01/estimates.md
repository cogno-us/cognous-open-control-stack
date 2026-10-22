# S01 source-grounded effort estimates

Unit: conventional-equivalent person-days. Columns are low/central/high for design and implementation (I), developer tests (T) and independent qualification (Q, a separately owned effort). AI concurrency can shorten elapsed time, but no measured conversion exists, so none is applied. These are planning estimates: scope drivers are measured (files, lines, tests, pin sites, prior refreeze costs; see [inventory.md](inventory.md) and [defects.md](defects.md)), but the conversion from scope to days uses assumptions that no repository measures. They are not copied from the ISS V6 estimates.

## Assumptions (ASSUMED, to be recalibrated at S03)

| Assumption | Central value | Note |
|---|---|---|
| Gate-critical Python with its tests, including review | about 60 net lines per day | range 30-120 |
| Contract or ADR text, reviewed | about 2 pages per day | range 1-3 |
| Independent qualification cases with negatives | 3-5 cases per day | includes freezing expectations before the candidate |
| Locked-component changes | F3 requalification, refreeze and re-review are separate and not included | each refreeze observed to cost seven PRs in seven repositories |
| Reviewer capacity | one independent reviewer assumed available | not measured |

Shared contract reviews, security evidence and fixtures are counted once, in the step that owns them (canonical profile at 1.3; coverage schema at 1.7; handoff schema at 1.4). Deferred and optional architecture is excluded.

## Step estimates (24 steps; step 4.3 split into its critical-path and remainder parts)

| Step | Work | I L/C/H | T L/C/H | Q L/C/H | Confidence | Scope driver |
|---|---|---|---|---|---|---|
| 1.1 | Inventory and 49-row crosswalk | 1/2/3 | 0/0/0 | 0/0.5/1 | MEDIUM | Mostly done by S01; remaining: finish docs fixes list, refresh baseline pins, independent review of the inventory claims. |
| 1.2 | Authority and separation contract | 3/5/8 | 0.5/1/2 | 1/2/3 | MEDIUM | Contract plus promotion-boundary ADR, refund-chain decision, migration direction (about 1.3k orchestrator LOC of acceptance modules and a 15.9k LOC qualification harness stay where they are in v0.2; only the direction is fixed); path-ownership expectations for Qualification. |
| 1.3 | Registry R0 contract | 5/8/13 | 1/2/4 | 2/3/5 | LOW | Canonical profile freeze across 4 families; three scanners and 369-line procedural check body inventoried; authority-to-effect contract; location ADR; typed-validation and activation contracts. |
| 1.4 | Independent evidence handoff | 2/4/6 | 1/2/3 | 1/2/3 | MEDIUM | Seed is orchestrator candidate.json plus admission.py (about 200 LOC); schema, digest, lock-driven pin intake design for 18 workflows and 34 source files. |
| 1.5 | Identity, state and recovery model | 3/5/8 | 1/2/3 | 1/2/3 | MEDIUM | 18-identifier crosswalk; six enums sharing the word unknown; mapping table from the ODES lifecycle contract; no new state machine. |
| 1.6 | Comparative CA-01 to CA-06 | 2/3/5 | 0/0/0 | 0.5/1/1 | MEDIUM | Most source work done in S01; remaining ADR drafts for CA-01, CA-05, CA-06 and the OpenAPPA pin reconciliation. |
| 1.7 | Minimum profile, frozen qualification entry, coverage schema, overlay target | 3/5/8 | 1/2/3 | 2/3/5 | MEDIUM | Heavy preregistration precedent (127 amendments); coverage-declaration schema and seed inventory; overlay target decision; independent prerequisites. |
| 2.1 | Versioned rule records and bounded store | 4/7/12 | 2/3/5 | 1.5/3/5 | LOW | Reuse reason-registry plus provenance vendoring, RuleRevision (188 LOC), canonical profile. If RuleKind must be extended in two locked components, add 3/5/8 to I and trigger F3 requalification. |
| 2.2 | Source-backed policy and scanner extraction | 4/6/10 | 2/3/5 | 2/3/5 | LOW | Three non-equivalent scanners (tables of 67, 76, 77 keys); reconcile then extract; hub and ergonomics are not locked. |
| 2.3 | Mandatory check manifest and evaluators | 6/10/16 | 3/5/8 | 3/5/8 | LOW | 369 procedural lines (`bounded.py:2239-2607`), 44 verifier check ids; the floor stays code, registry references evaluators. |
| 2.4 | Activation, rollback and freshness | 5/8/14 | 3/5/8 | 3/5/8 | LOW | Extend runtime policy row with digest and epoch, reuse custody epoch and generation fence; local comparator; touches locked runtime and Control Plane (F3 requalification not included). |
| 2.5 | Independent registry equivalence | 0/0/0 | 0/0/0 | 6/10/16 | LOW | Old-versus-registry equivalence per rule class plus negative battery (malformed, incomplete, conflicting, non-monotone). |
| 3.1 | Orchestrator powers contract and lock-driven pins | 4/7/12 | 2/4/6 | 1/2/3 | MEDIUM | 94 workflow lines in 18 files, 101 source lines in 34 files, about 9 tests asserting literals; add a lock-driven profile, keep O5/O6 pins as history. |
| 3.2 | Durable single-host workflow | 6/10/16 | 3/5/8 | 2/4/6 | LOW | New state store and event history (none exists); reuse the synthetic refund runtime (429 lines) and recovery coordinator (144 lines) as references only. |
| 3.3 | Control Plane and Runtime integration | 5/9/15 | 3/5/8 | 3/5/8 | LOW | Five unmediated surfaces to declare or close; R08 and R10 touch locked components; effects must use the existing gate. |
| 3.4 | Qualification handoff integration | 3/5/8 | 2/3/4 | 2/3/5 | MEDIUM | Producer side plus a qualification ingestion job (controller change, refreeze layers). |
| 3.5 | Crash, revocation and reconciliation | 4/7/12 | 3/5/8 | 3/5/8 | LOW | Reconcile-only continuation; re-pin Q6 (169 commits behind) and adversarial suites; M02, M04 in scope. |
| 3.6 | Independent orchestration qualification | 0/1/2 | 0/0/0 | 6/10/16 | LOW | Negative battery over transitions and recovery; reuse adversarial T01, T10, T12-T14 after re-pin. |
| 4.1 | Lock and tuple compatibility | 4/7/11 | 2/3/5 | 2/3/5 | MEDIUM | Manifest normalising lock keys, contract matrix, schema snapshots; registry R4; overlay mechanics. |
| 4.2 | Enforcement coverage observed | 2/3/5 | 2/4/6 | 3/5/8 | MEDIUM | Schema from 1.7; observation of declared paths; removal-detection negatives; independent enumeration. |
| 4.3 (a) | Known-issue closure, critical path (22 items) | 6/11/20 | 3/6/10 | 2/4/7 | LOW | 16 items on and 6 partly on the critical path; several touch locked components (separately authorized). |
| 4.3 (b) | Known-issue closure, remainder (16 items) | 1/2/4 | 0/1/2 | 1/2/3 | MEDIUM | Document-as-limit items and deferrals. |
| 4.4 | Combined adversarial battery | 1/2/3 | 2/4/6 | 5/8/13 | LOW | Reuse adversarial matrix, comparative battery runner. |
| 4.5 | Independent acceptance dossier | 1/2/3 | 0/0/0 | 4/6/10 | MEDIUM | Labelled three-indicator headline (about 30 lines in `v1_validation.py`), original-scope denominator, dossier. |
| 4.6 | Operator decision packet | 1/2/3 | 0/0/0 | 0.5/1/2 | MEDIUM | Non-authorizing packet; reuse ergonomics dashboard. |

## Totals

| Scope | I | T | Q | Total |
|---|---|---|---|---|
| All 24 steps (full v0.2 plan) | 76/131/217 | 36.5/65/104 | 57.5/97.5/157 | 170.0/293.5/478 |
| Minimum independently qualified single-host profile (excludes 2.2 scanner extraction and 4.3 (b)) | 71/123/203 | 34.5/61/97 | 54.5/92.5/149 | 160.0/276.5/449 |

The minimum profile is not total v0.2: it excludes scanner extraction (2.2) and the document-as-limit known-issue closure (4.3 (b)). Optional CA items, remedy vocabulary, a Cedar adapter, a distribution service, a native information-flow evaluator and any locked-component refreeze are excluded from both lines.

## Largest uncertainties

1. Registry location and canonical profile choices (open owner decisions) swing 1.3, 2.1 and 4.1 by more than the stated high values if a locked contract changes.
2. Any change to a locked component (R04, R08, R10, M02, M04, M05, RuleKind extension) adds F3 requalification and a refreeze cascade that these figures exclude.
3. Step 4.3 depends on how many critical-path items are fixed rather than documented.
4. Independent qualification effort assumes expectations are frozen before any candidate exists; late freezes cost more.

## Recalibration

S03 replaces the assumptions with figures from the first completed P1 steps (actual reviewed pages, lines and cases per day) and republishes this page as a revision; this revision is not edited in place.
