# OCS v0.2 engineering register — proposed 24-step decomposition

This stable program defines intended work, not current execution. The original **49-row** scope inventory is retained unchanged in [original-register.md](original-register.md). S01 must map every original identifier to one or more steps or a justified explicit deferral; this new register does not silently replace the original rows. Estimates are unestimated until source-backed review. Tier 1 routine, Tier 2 substantive, Tier 3 critical.

| Step | Phase | Sprint | Work | Prerequisites | Risk tier | Minimum exit requirement |
|---|---|---|---|---|---|---|
| 1.1 | P1 | S01 | Inventory and 49-row crosswalk | — | 3 | source inventory |
| 1.2 | P1 | S02 | Authority and separation contract | 1.1 | 3 | exclusive powers and forbidden transitions |
| 1.3 | P1 | S02 | Registry R0 contract | 1.1,1.2 | 3 | rule-floor/evaluator/activation contracts |
| 1.4 | P1 | S02 | Independent evidence handoff | 1.2 | 3 | typed pins, digest and raw evidence envelope |
| 1.5 | P1 | S03 | Identity, state and recovery model | 1.2 | 3 | stable distinct lifecycle identities |
| 1.6 | P1 | S01 | Comparative CA-01 to CA-06 | 1.1 | 2 | source-backed disposition |
| 1.7 | P1 | S03 | Minimum profile and frozen qualification entry | 1.3,1.4,1.5,1.6 | 3 | independent prerequisites and exclusions |
| 2.1 | P2 | S04 | Versioned rule records and bounded store | 1.3,1.7 | 3 | canonical digest, integrity, refusal |
| 2.2 | P2 | S04 | Source-backed policy/scanner extraction | 2.1 | 3 | complete old-new rule crosswalk |
| 2.3 | P2 | S05 | Mandatory check manifest/evaluators | 2.1,2.2 | 3 | no skipped mandatory check |
| 2.4 | P2 | S05 | Activation, rollback and freshness | 2.3 | 3 | authenticated selected epoch |
| 2.5 | P2 | S06 | Independent registry equivalence | 2.2,2.3,2.4 | 3 | frozen raw comparison and negatives |
| 3.1 | P3 | S07 | Orchestrator runtime powers contract | 1.2,1.4,1.5,1.7 | 3 | no competing permission or verdict |
| 3.2 | P3 | S07 | Durable single-host workflow | 3.1 | 2 | bounded restartable lifecycle |
| 3.3 | P3 | S08 | Control Plane/Runtime integration | 3.1,3.2 | 3 | effects mediated by existing gate |
| 3.4 | P3 | S08 | Qualification handoff integration | 1.4,3.2,3.3 | 3 | immutable producer observations |
| 3.5 | P3 | S09 | Crash/revocation/reconciliation | 3.2,3.3 | 3 | no blind retry; truthful unknown |
| 3.6 | P3 | S09 | Independent orchestration qualification | 3.4,3.5 | 3 | separate authority and negative battery |
| 4.1 | P4 | S10 | Lock/tuple compatibility | 2.5,3.6 | 2 | exact pinned source closure |
| 4.2 | P4 | S10 | Enforcement coverage and security | 3.3,3.5 | 3 | declared mediated/unmediated paths |
| 4.3 | P4 | S10 | D/R/M known issue and controller closure | 1.1,2.5,3.6 | 2 | each residual honestly dispositioned |
| 4.4 | P4 | S11 | Combined adversarial battery | 2.5,3.6,4.2 | 3 | source-frozen adverse testing |
| 4.5 | P4 | S11 | Independent v0.2 acceptance dossier | 4.1,4.3,4.4 | 3 | mandatory/raw/original-scope separate |
| 4.6 | P4 | S12 | Operator candidate decision packet | 4.5 | 3 | no automatic release; HOLD |

Every step additionally requires source identification, an implementation owner, a separate independent qualification owner where required, exact-pin/test evidence, entry conditions, a bounded PR, environment and risk verification, and stop/reversal conditions specified in the [machine-readable mirror](engineering-register.json). Preliminary acceptance language is proposed, not frozen independent oracle material.
