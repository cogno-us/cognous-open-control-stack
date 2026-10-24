# MVP program crosswalk: 24 steps and S01-S12 (concise)

Status: builder-side, non-authorizing, documentation-only. Release, publication and production HOLD. No qualification, certification or readiness claim. The original program is unchanged. Companion to [mvp-scope-adoption-record.md](mvp-scope-adoption-record.md), whose items (a)-(c) are OPERATOR-APPROVED (coordinator's reading of the operator's reply), prospective, from 2026-10-24; nothing else is adopted by it, including baseline adoption, the delegation record, the successor host-security profile and U6/U7/U10. Basis: hub main `7661983849474784469f029297fd5bbcccd03ffe`. Labels: V verified, R reported, I inferred. Dispositions come from the PROPOSED [scope-reduction-register.md](scope-reduction-register.md) (V; A kept/narrowed, B reduced, C deferred, D removed). Delivered subsets are MVP candidates "merged on main", not qualified, and never satisfy the original exit unless stated.

## 1. The 24 steps
| Step | MVP disposition | Delivered MVP subset | Original exit still incomplete |
|---|---|---|---|
| 1.1 Inventory, 49-row crosswalk | C, superseded by register | s01 packet in tree (V); PRs #195/#196 (R) | none needed for MVP |
| 1.2 Authority/separation | B | docs (#197/#199, R); short frozen statement in MVP claim; M0 approved (V record) | refund-chain migration to Orchestrator (M0 row 5), deferred for the MVP only |
| 1.3 Registry R0 contract | C | contract docs (R) | feature work; fixed pinned config used instead |
| 1.4 Evidence handoff | B | producer side (orch #124/#125/#127, R); Replay + Evidence Pack path | Orchestrator handoff excluded (Q7) |
| 1.5 Identity/state/recovery | B | mapped onto ODES lifecycle (#198, R) | review/freeze residual; workstream not in modules.md (I) |
| 1.6 Comparative CA-01..06 | C | docs | extensions |
| 1.7 Minimum profile / entry | A re-scoped | MVP definition and environment profile; not frozen | registry L1/L2, coverage manifest, overlay text |
| 2.1 Rule records/store | C | candidate #204 (merged, V per prior report) | `/1` successor, store use |
| 2.2 Scanner extraction | C | analysis #205-#208 | extraction, migration |
| 2.3 Mandatory check manifest | C; invariant kept | `/0` + evaluator #209/#211; #213 open (V) | `/1`, dispositions |
| 2.4 Activation/rollback | C | none (design only) | all |
| 2.5 Registry equivalence | C | none | all |
| 3.1 Orchestrator powers | B | orch #124 (R) | handoff only if later adopted |
| 3.2 Durable workflow | C | #126/#128 (R); #132 parked | durable unknown-outcome via Runtime + Replay is EXISTING, to verify |
| 3.3 CP/Runtime integration | A narrowed | ingress #217, launcher #230-#232 (V); route C exclusion checks Qual #223 merged (V) | surfaces beyond the MVP route |
| 3.4 Qualification handoff | B | orch #125/#127 (R); #130 parked | not on MVP path |
| 3.5 Crash/revocation/reconcile | A re-scoped on CP/Runtime | Runtime F3 #144 in tuple (V manifest); lost-ack asserts Qual #223 (V) | OS-kill, pruning negatives (R) |
| 3.6 Orchestration qualification | C, replaced by MVP Qualification Contract | Qual #223 acceptance job (V merged) | Orchestrator qualification |
| 4.1 Lock/tuple compatibility | A one fixed tuple | candidate manifest and validator #228/#231/#233 (V); Qual #226 merged (V); hub #223 open | generalized manifest, overlay |
| 4.2 Enforcement coverage | A profile-bounded | `BOUNDARY.md`, launcher allowlist (V) | completed static reachability inventory: NOT FOUND (see adoption record section 6); Coverage Manifest C |
| 4.3 D/R/M closure | split A/C | s01 audit; limitations record | off-path items remain documented limits |
| 4.4 Adversarial battery | A cut | Qual mvp-chain in #223 (V merged); oracle v7 draft Qual #225 open (V) | registry/Orchestrator cases |
| 4.5 Acceptance dossier | A renamed | final-report template (hub #243 open, V) | dossier not produced |
| 4.6 Operator decision packet | A | none; #245 draft delegation record only (V open) | decision; release HOLD |

## 2. Twelve-sprint summary (S01-S12, original exits unchanged per `mini-sprints.md`, V)
| Sprint | Steps | Delivered MVP subset | Original exit incomplete |
|---|---|---|---|
| S01 | 1.1, 1.6 | source packet and comparative docs | S01 acceptance recorded in #193 (not found) |
| S02 | 1.2-1.4 | authority statement, M0 record; Replay/Pack handoff | registry/handoff contracts as full freeze |
| S03 | 1.5, 1.7 | MVP definition and environment profile | frozen profile; independent oracle freeze is Qualification's |
| S04 | 2.1, 2.2 | candidate and analysis only | deterministic rule identities in use |
| S05 | 2.3, 2.4 | `/0` manifest and evaluator candidate | fail-closed qualified rule selection |
| S06 | 2.5 | none | independent registry evidence |
| S07 | 3.1, 3.4 | producer pins/handoff candidates (R) | lock-driven admission qualified; parked #130 |
| S08 | 3.2, 3.3 | ingress, launcher, boundary doc | durable workflow; full in-scope mediation inventory |
| S09 | 3.5, 3.6 | Runtime F3, lost-ack assertions (Qual) | independent orchestration qualification |
| S10 | 4.1-4.3 | fixed candidate manifest; limitations record | frozen tuple (not frozen), residual dispositions |
| S11 | 4.4, 4.5 | acceptance job; draft oracle v7 | raw/mandatory/original-scope triple |
| S12 | 4.6 | none | decision packet; HOLD |

## 3. Original steps vs MVP-only additions
MVP-only: trusted-host ingress and launcher, F3 repairs (Runtime #144, Control Plane #83), candidate manifest and validator, six-layer informational catalogue (L1 rules, L2 scenarios, L3 tests, L4 fixtures, L5 evidence index, L6 derived coverage; `authority: none`, satisfies no step 2.1-2.5 exit), successor distinct-UID trusted-host profile (Qualification #225 draft). Removed MVP dependency edges and the scoped M0 row 5 supersession are in the adoption record. Unresolved items and owners: adoption record section 5.
