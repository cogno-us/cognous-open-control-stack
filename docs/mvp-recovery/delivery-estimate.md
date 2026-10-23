# Artifact 5 - Delivery Estimate

Status: PROPOSED, non-authorizing; HOLD. Architect Q17: accepted as low-confidence planning estimates, not a commitment; total engineering + Qualification + conditional refreeze 25 / 55 / 119 person-days (effort, not calendar). Track two readiness dates separately: engineering readiness for the demonstration, and independent release acceptance. Person-day figures are my assumption-based sizing built from the register's own step estimates and the read-only assessments; confidence LOW. They are effort, not elapsed time, and are not converted to a calendar. Baseline for comparison: the register's full 24-step plan is 170 / 293.5 / 478 person-days (engineering+qualification, excluding refreeze).

| Work package | Low | Central | High | Main uncertainty |
|---|---|---|---|---|
| Fixed configuration + MVP claim docs (1.7 re-scoped) | 2 | 3 | 5 | D2 route choice |
| Composed trace harness at the lock pins | 5 | 8 | 15 | Does the existing refund harness run unchanged at the lock revisions (U) |
| ODES failure fix or exclusion (Replay xfails remain) | 1 | 3 | 8 | Fix vs exclude (D4) |
| Exact-candidate vehicle (Q11 runner repair / pin / alternative) | 3 | 5 | 10 | Qualification's schedule and choice |
| Missing negative tests + OS-kill recovery | 3 | 5 | 8 | Reproduction at Runtime ec728da6 |
| On-path D/R/M and unmediated-surface fixes (3.3/3.5/4.3 slice) | 3 | 8 | 20 | Static-reachability result (U) |
| **Engineering subtotal** | **17** | **32** | **66** | |
| Qualification: pre-registration, run, review, dossier | 8 | 13 | 22 | Controller items R14 (E-6/E-12/E-13), scope-reduction semantics |
| **Refreeze cascade** (only if a locked component changes) | 0 | 10 | 31 | Register M1 contingency 10/31/76; 7 PRs / 7 repos per refreeze observed |

Earliest credible path: fixed configuration with no locked-component change (refreeze 0), D1 = control-plane ingress, D2 = route B, D3 = Replay/Evidence Pack, D4 = exclude or fix ODES, followed by one Qualification run at the exact candidate. The critical path is serial through: operator decisions -> Qualification claim freeze -> composed trace and exact-candidate vehicle -> controller run -> dossier -> operator decision. Parallelism is limited by ownership: the Hub cannot author Qualification expectations or verdicts, and component owners fix their own components.

Decisions that materially move the estimate: D1 (GAX in path adds an exchange PR + F3 + refreeze), D2, D4, D5, and whether the reachability pass finds a reachable unmediated surface (adds locked change + refreeze). Not estimated: paid or human test rows, third-party audit, production readiness.

## Assumptions the architect challenges (Q17)
- Zero refreeze holds only if the selected route has no safety defect requiring a locked-component change.
- One Qualification run is optimistic given the historical inconclusive results and unresolved negative controls: budget for correction and rerun.
- Five central person-days for negative controls may underestimate crash, lost-acknowledgment, concurrent-operation and custody-failure reproduction.
- Five central person-days for the exact-candidate vehicle is plausible only if a direct Qualification job already exists and can be adapted; otherwise uncertain (under investigation).
