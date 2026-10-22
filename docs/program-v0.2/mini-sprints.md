# S01–S12 proposed mini-sprint packaging

Mini-sprints package the 24 program steps; they add no new normative obligations or automatic execution authority. One bounded producer PR and separately owned qualification evidence where relevant. Freeze contracts and independent expectations before candidate acceptance; serialize canonical source/schema/state mutations. A failed or missing prerequisite is a stop, not a waiver.

| Sprint | Steps | Reviewable output | Entry | Exit | Stop and rollback |
|---|---|---|---|---|---|
| S01 | 1.1,1.6 | Exact source/49-row crosswalk, comparative review | read-only sources | closed inventory and open decisions | unsupported source claim; preserve originals |
| S02 | 1.2–1.4 | Authority/registry/handoff contracts | S01 | reviewed typed freeze | ambiguous authority or dual verdict |
| S03 | 1.5,1.7 | Lifecycle/profile and independent test freeze | S02 | nonproduction profile and oracle | unresolved required mapping |
| S04 | 2.1–2.2 | Registry store and rule extraction | S03 | deterministic rule identities | missing/altered mandatory check |
| S05 | 2.3–2.4 | Resolver and activation | S04 | fail-closed qualified rule selection | unauthorized activation |
| S06 | 2.5 | Independent registry evidence | S04–S05 exact candidate | scoped results and raw negatives | no transferred/historical pass |
| S07 | 3.1,3.4 | Orchestrator powers and source-preserving handoff | S03 | lock-driven pins; one-way producer evidence | excessive authority / self-certified outcome |
| S08 | 3.2–3.3 | Durable workflow and enforcement | S07, S02 | bounded state transitions; in-scope paths mediated, prevented or excluded | unbounded tasks / unmediated effect path |
| S09 | 3.5–3.6 | Recovery and independent qualification | S08 | truthful unknown and no blind retry | uncertain commit unacknowledged |
| S10 | 4.1–4.3 | Compatibility, bypass and known limits | S06, S09 | frozen tuple, explicit residuals | unmediated effect path |
| S11 | 4.4–4.5 | Adverse tests and independent acceptance | S10 | separate raw-suite/mandatory/original-scope | unrun applicable mandatory test |
| S12 | 4.6 | Final bounded decision packet | S11 | exact candidate/residual/HOLD dossier | no implicit release or deployment |

Separate development and independent qualification PRs whenever they affect the same feature; no PR can qualify itself. Rollback preserves historical facts and does not reverse committed external effects.

S01 review draft: the [S01 source packet](s01/README.md) carries the inventory, crosswalk, defect register, comparative assessment and estimates for review; acceptance of S01 is recorded in controller #193, not here.

**M0 contractual gate (proposed, S02 package):** S02 and S03 together form the M0 gate. A separately reviewed M0 gate precedes implementation of any step from 2.1 onward; passing it is not authorization to start work or release. The registry track (S04–S06) and the orchestration track (S07–S09) have disjoint owners and may proceed in parallel when separately authorized; sprint numbers are packaging, not ordering. See [s02/README.md](s02/README.md).
