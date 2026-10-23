# Artifact 4 - Qualification Contract (proposal to Qualification)

Status: PROPOSED requirements from the Hub to the independent Qualification owner (`cogno-us/cognous-stack-qualification`). The Hub does not author verdicts or modify oracles; Qualification freezes expectations before the candidate runs. Non-authorizing; HOLD. Statuses are kept separate: PASS, FAIL, BLOCKED, NOT RUN, NOT APPLICABLE; historical results (g8-r10 etc.) stay intact.

## Claim under test
The exact claim in mvp-definition.md at one exact candidate identity (hub revision, `component-lock.json` digest, Qualification revision, profile). No reuse of g8-r10 for a different hub, lock or Qualification revision; g8-r10 results remain evidence for the g8 tuple only. Reuse of component-level results is allowed only where Qualification confirms the candidate identity and scope still apply (all 11 lock repos are identical to g8 on main except two docs-only commits).

## Suite (smallest set; Qualification decides final rows)
1. One composed trace at the lock pins: propose -> authority evaluation -> authorize/refuse/hold -> boundary effect -> export -> Replay import -> Evidence Pack import -> independent verification (verifier only if D3 keeps it).
2. Mandatory negative controls, each as a mandatory row (not INCONCLUSIVE/non-mandatory): unauthorized execution; revocation/approval withdrawal before effect (state the C0 race plainly or run on the in-transaction profile fixed by D2); stale or mismatched authority and consequence; missing, invalid or expired evidence; ambiguous commit and lost acknowledgment (including an OS-level process kill); replay and duplicate effect with operation identity; evidence tampering and missing custody; unmediated paths within the declared profile (closed inventory + removal detection).
3. Pre-existing coverage reusable if identity applies: SC-NATIVE-F5B (36 cases x2), matched-refund (20/20, currently non-mandatory), component suites (control plane, runtime, Replay, evidence pack, action manifest).
4. Known failures stay visible: ODES 4 declared failures (or exclusion from chain), Replay lifecycle xfails under ER-07-2, route-B `journal_check_reused` limit, SCN-D09 raw-SQL/OpenShell out of model.

## Reporting
Per-claim PASS/FAIL/BLOCKED/NOT RUN/NOT APPLICABLE; the headline carries the original-scope denominator, not only a reduced-scope PASS (g8-r10 pre-reduction verdict is INCOMPLETE: 40 PASS, 30 INCONCLUSIVE, 5 NOT RUN of 75). Synthetic-clock use never establishes real-time freshness. Exactly-pinned candidate; no builder self-certification; third-party audit status stated plainly.

## Out of scope (NOT APPLICABLE or excluded from the claim)
Registry/`/1`, 58-check catalogue, scanner migration, Orchestrator lifecycle/store/checkpoint, Coverage Manifest, drift, OTel, ISS V6, additional adapters, GAX exchange route (unless D1).
