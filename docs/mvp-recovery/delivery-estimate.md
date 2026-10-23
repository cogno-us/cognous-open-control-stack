# Artifact 5 - Delivery Estimate

Status: PROPOSED, non-authorizing; HOLD. Architect Q17: accepted as low-confidence planning estimates, not a commitment; total engineering + Qualification + conditional refreeze 25 / 55 / 119 (superseded below: refreeze row now 10 / 10 / 31, totals 35 / 55 / 119 with the low refreeze counted) person-days (effort, not calendar). Track two readiness dates separately: engineering readiness for the demonstration, and independent release acceptance. Person-day figures are assumption-based sizing built from the register's own step estimates and the read-only assessments; confidence LOW. They are effort, not elapsed time, and are not converted to a calendar. Baseline for comparison: the register's full 24-step plan is 170 / 293.5 / 478 person-days (engineering+qualification, excluding refreeze).

| Work package | Low | Central | High | Main uncertainty |
|---|---|---|---|---|
| Fixed configuration + MVP claim docs (1.7 re-scoped) | 2 | 3 | 5 | Route B confirmed by the architect; Qualification verification of its guarantees |
| Composed trace harness at the lock pins | 5 | 8 | 15 | Does the existing refund harness run unchanged at the lock revisions (U) |
| ODES failure repair, or contained-path proof (Replay xfails remain) | 1 | 3 | 8 | Repair vs contained-path proof (Decision 4, Q9) |
| Exact-candidate vehicle (register Q11 runner repair / pin / direct Qualification job, architect Q14) | 3 | 5 | 10 | Qualification's schedule and choice |
| Missing negative tests + OS-kill recovery | 3 | 5 | 8 | Reproduction at Runtime ec728da6 |
| On-path D/R/M and unmediated-surface fixes (3.3/3.5/4.3 slice) | 3 | 8 | 20 | Static-reachability result (U) |
| **Engineering subtotal** | **17** | **32** | **66** | |
| Qualification: pre-registration, run, review, dossier | 8 | 13 | 22 | Controller items R14 (E-6/E-12/E-13), scope-reduction semantics |
| **Refreeze cascade** (F3 repair now required, so a refreeze is planned) | 10 | 10 | 31 | Register M1 contingency 10/31/76; 7 PRs / 7 repos per refreeze observed |

Earliest credible path: fixed configuration with no locked-component change (refreeze 0), Decision 1 = control-plane ingress, Decision 2 = route B, Decision 3 = Replay/Evidence Pack, Decision 4 = repair ODES/Replay or prove the contained safe-UNKNOWN path, followed by a Qualification run; budget for correction and at least one rerun (architect Q17). The critical path is serial through: operator decisions -> Qualification claim freeze -> composed trace and exact-candidate vehicle -> controller run -> dossier -> operator decision. Parallelism is limited by ownership: the Hub cannot author Qualification expectations or verdicts, and component owners fix their own components.

Decisions that materially move the estimate: Ingress/route are ruled (GAX excluded); remaining drivers: Decision 2, Decision 4, Decision 5, and whether the reachability pass finds a reachable unmediated surface (adds locked change + refreeze). Not estimated: paid or human test rows, third-party audit, production readiness.

## Assumptions the architect challenges (Q17)
- Zero refreeze holds only if the selected route has no safety defect requiring a locked-component change.
- One Qualification run is optimistic given the historical inconclusive results and unresolved negative controls: budget for correction and rerun.
- Five central person-days for negative controls may underestimate crash, lost-acknowledgment, concurrent-operation and custody-failure reproduction.
- Five central person-days for the exact-candidate vehicle is plausible only if a direct Qualification job already exists and can be adapted; otherwise uncertain (under investigation).

## Update (Oct 31 operator schedule; architect MVP2 Q17)
Calendar ranges (reasoned elapsed time, not a measured schedule or completion guarantee; assume parallel work and that the single F3 repair closes the journal defect): optimistic 10-14, central 18-25, adverse 30-45+ calendar days. The earlier "refreeze 0" best case is withdrawn because the claim-journal defect needs a locked-component change; the refreeze row now has a central of 10 person-days (low 10 is the architect's contingency floor in the register, high unchanged at 31). Person-day tables are effort, not elapsed time; engineering subtotal 17 / 32 / 66 is unchanged.

The operator's schedule (Oct 24 freeze; Oct 25 Replay repro, inventory, F3 patch ready; Oct 27 F3 regression and harness; Oct 29 exact-candidate battery; Oct 30 refreeze and pin reconciliation; Oct 31 implementation complete and candidate frozen; Nov 3-6 independent acceptance and operator decision) is a target, not a commitment, and is shorter than even the optimistic architect range (10-14 days from Oct 23 is Nov 2-6). It is recorded as the target; the ranges are the reasoned estimate. The F3 refreeze is the principal serial risk and cannot be parallelized away. Independent acceptance is separate from implementation completeness and is not guaranteed by a frozen candidate. See [critical-path.md](critical-path.md). This is not a spending, F3 or deployment authorization.
