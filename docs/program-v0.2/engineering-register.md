# OCS v0.2 engineering register — proposed 24-step decomposition

This stable program defines intended work, not current execution. The original **49-row** scope inventory is retained unchanged in [original-register.md](original-register.md). The S01 [crosswalk](s01/crosswalk.md) maps every original identifier to one or more steps or a justified explicit deferral; this register does not silently replace the original rows. Preliminary source-grounded estimates are in [s01/estimates.md](s01/estimates.md) and the JSON mirror. Tier 1 routine, Tier 2 substantive, Tier 3 critical.

| Step | Phase | Sprint | Work | Prerequisites | Risk tier | Minimum exit requirement |
|---|---|---|---|---|---|---|
| 1.1 | P1 | S01 | Inventory and 49-row crosswalk | — | 3 | source inventory |
| 1.2 | P1 | S02 | Authority and separation contract | 1.1 | 3 | exclusive powers and forbidden transitions; promotion-boundary ADR table; migration direction between orchestrator and qualification; canonical refund-chain decision |
| 1.3 | P1 | S02 | Registry R0 contract | 1.1,1.2,1.6 | 3 | rule-floor, evaluator and activation contracts; authority-to-effect consistency contract; canonical JSON profile freeze (one owner); registry-location ADR; typed-validation and activation-refusal contract |
| 1.4 | P1 | S02 | Independent evidence handoff | 1.2,1.3 | 3 | typed pins, digest and raw evidence envelope; lock-driven pin intake design; decision whether the handoff replaces or only supplements refreeze authorship |
| 1.5 | P1 | S03 | Identity, state and recovery model | 1.2 | 3 | stable distinct lifecycle identities; identity crosswalk; mapping table sourced from the ODES lifecycle contracts with workflow states namespaced apart from attempt and observation states |
| 1.6 | P1 | S01 | Comparative CA-01 to CA-06 | 1.1 | 3 | source-backed disposition per CA item as deltas on existing OpenAPPA, AGT and OPA artifacts; reconciled OpenAPPA revision table |
| 1.7 | P1 | S03 | Minimum profile and frozen qualification entry | 1.3,1.4,1.5,1.6 | 3 | independent prerequisites and exclusions; enforcement-coverage declaration schema and seed inventory; pin-overlay target decision; named deployment profiles |
| 2.1 | P2 | S04 | Versioned rule records and bounded store | 1.3,1.7 | 3 | canonical digest, integrity, refusal |
| 2.2 | P2 | S04 | Source-backed policy/scanner extraction | 2.1 | 3 | scanner reconciliation of the three implementations, then complete old-new rule crosswalk |
| 2.3 | P2 | S05 | Mandatory check manifest/evaluators | 2.1 | 3 | no skipped mandatory check |
| 2.4 | P2 | S05 | Activation, rollback and freshness | 1.3,2.3 | 3 | authenticated selected epoch reusing existing commit-bound mechanisms; local active-rule-set acknowledgement and mismatch detection |
| 2.5 | P2 | S06 | Independent registry equivalence | 2.2,2.3,2.4 | 3 | frozen raw comparison and negatives |
| 3.1 | P3 | S07 | Orchestrator runtime powers contract | 1.2,1.4,1.5,1.7 | 3 | no competing permission or verdict; lock-driven orchestrator pins as a precondition, historical O5/O6 pins preserved as history |
| 3.2 | P3 | S07 | Durable single-host workflow | 3.1 | 2 | bounded restartable lifecycle |
| 3.3 | P3 | S08 | Control Plane/Runtime integration | 3.1,3.2 | 3 | effects mediated by the existing gate or declared unmediated; no new gate |
| 3.4 | P3 | S08 | Qualification handoff integration | 1.4,3.2,3.3 | 3 | immutable producer observations |
| 3.5 | P3 | S09 | Crash/revocation/reconciliation | 3.2,3.3 | 3 | no blind retry; truthful unknown; reconcile-only continuation unless a locked contract change is separately authorized; evidence re-pinned to the locked tuple |
| 3.6 | P3 | S09 | Independent orchestration qualification | 3.4,3.5 | 3 | separate authority and negative battery |
| 4.1 | P4 | S10 | Lock/tuple compatibility | 1.7,2.5,3.6 | 2 | exact pinned source closure; normalised lock keys; registry R4 integration; pin-overlay mechanics |
| 4.2 | P4 | S10 | Enforcement coverage and security | 1.7,3.3,3.5 | 3 | declared mediated/unmediated paths observed against the 1.7 schema with independent enumeration |
| 4.3 | P4 | S10 | D/R/M known issue and controller closure | 1.1,2.5,3.6 | 3 | each residual honestly dispositioned using the per-item ownership table in s01/issues-disposition.md |
| 4.4 | P4 | S11 | Combined adversarial battery | 2.5,3.6,4.2 | 3 | source-frozen adverse testing including integrated registry-mutation and authority-boundary failures |
| 4.5 | P4 | S11 | Independent v0.2 acceptance dossier | 4.1,4.3,4.4 | 3 | mandatory/raw/original-scope separate, as a labelled headline triple with a defined original-scope denominator |
| 4.6 | P4 | S12 | Operator candidate decision packet | 4.5 | 3 | no automatic release; HOLD |

Every step additionally requires source identification, an implementation owner, a separate independent qualification owner where required, exact-pin/test evidence, entry conditions, a bounded PR, environment and risk verification, and stop/reversal conditions specified in the [machine-readable mirror](engineering-register.json). Preliminary acceptance language is proposed, not frozen independent oracle material.

## Revision record

Revision r2-s01 answers defects in [s01/defects.md](s01/defects.md). No step was added, removed or renumbered.

| Step | Change | Defect ids |
|---|---|---|
| 1.2 | Exit adds promotion-boundary ADR table, migration direction and canonical refund-chain decision | PD-A01, PD-A02, PD-A08, PD-C05 |
| 1.3 | Adds dependency 1.6; exit adds authority-to-effect contract, canonical JSON profile freeze, registry-location ADR, typed validation and activation refusal | PD-B01, PD-B02, PD-B07, PD-H02 |
| 1.4 | Adds dependency 1.3 (one canonical profile owner); exit adds lock-driven pin intake and refreeze-authorship decision | PD-A03, PD-A04, PD-B02 |
| 1.5 | Exit adds identity crosswalk and mapping table sourced from ODES lifecycle contracts | PD-L01, PD-L03 |
| 1.6 | Tier 2 to 3; exit restated as deltas on existing OpenAPPA, AGT and OPA artifacts | PD-C02, PD-C06 |
| 1.7 | Exit adds coverage-declaration schema, overlay target decision and deployment profiles | PD-C01, PD-C03, PD-L09 |
| 2.2 | Exit adds scanner reconciliation before extraction | PD-B03 |
| 2.3 | Prerequisite 2.2 removed (catalogues are independent) | PD-B04 |
| 2.4 | Adds dependency 1.3; exit reuses existing commit-bound mechanisms and adds local acknowledgement | PD-B05, PD-H02 |
| 3.1 | Exit adds lock-driven orchestrator pins as a precondition | PD-A04 |
| 3.3, 3.5 | Mediation stated as existing gate or declared unmediated; continuation is reconcile-only unless a locked contract change is authorized; evidence re-pinned | PD-L04, PD-L06, PD-L07 |
| 4.1 | Adds dependency 1.7; exit adds registry R4 and overlay mechanics | PD-B06, PD-C01 |
| 4.2 | Adds dependency 1.7 (schema); this step observes | PD-C03 |
| 4.3 | Tier 2 to 3; exit uses the per-item ownership table | PD-D01 |
| 4.4, 4.5 | Exits add integrated registry-mutation tests; labelled headline triple | PD-B09, PD-E01 |

