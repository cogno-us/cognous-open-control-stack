# Artifact 3 - Critical Path

Status: PROPOSED, non-authorizing; HOLD. Locked-component changes, paid tests, deployment and release need the applicable approvals.

## Operator decisions that shape the path
- D1 Ingress: control-plane proposal (recommended, no GAX) vs GAX exchange route (needs a small exchange PR forwarding `runtime_authority_profile`, F3 and refreeze).
- D2 Route and profile: route B atomic executor with operation identity (recommended: only combination shown to hold in-transaction grant check and duplicate protection together) vs route A.
- D3 Evidence path: Replay + Evidence Pack (+ verifier) (recommended) vs Orchestrator handoff (pulls in 1.4/3.1/3.4/#130/Q15).
- D4 ODES: fix the 4 ODES failures (3 declared; one error class, incl. the end-to-end export test and the lost_ack / prior_absence cases) vs remove the ODES export from the MVP evidence chain. Exclusion does not close the ambiguous-commit gap: Replay's own lifecycle conformance also xfails the ambiguous-dispatch / unknown-result fixtures (ER-07-2), so that evidence path needs its own disposition either way.
- D5 Enforcement-coverage inventory (ADR-P08): blocker or documented limit (operator documents conflict: operator-decisions.md "PROPOSED" vs M0 record "mandatory").
- D6 "Real bounded authority": synthetic trusted resolver (stated as such) vs Alvorada Authority Context.
Also: confirm D15's reduced-scope PASS may be cited only with the original-scope denominator.

## Sequence (owners in brackets)
1. [Hub, docs] This planning PR; park Orchestrator #130-#132 and hub #213; docs-only hub #212 may merge.
2. [Operator] Decide D1-D6.
3. [Qualification] Freeze the MVP claim, expectations and negative-control rows before any candidate run (Qualification owns oracles).
4. Parallel after 2-3 (separate owners, no cross-edits):
   - 4a [Orchestrator or Qualification suite] Composed trace harness at the lock pins (re-pin the existing customer_refunds scenario harness; no new service).
   - 4b [ODES/Replay owners] Fix or exclude the lost-ack path (D4).
   - 4c [Hub + Qualification] Exact-candidate vehicle: repair the reference-release runner and re-point the stale 2bb5f10 pin (Q11 requirements in `docs/program-v0.2/s05/q11-...` once merged), or have Qualification run its own exact-candidate job; reconcile or retire the stale `qualification_evidence` expectation in the lock/snapshot/tests.
   - 4d [Component owners] Missing negative tests: operation-ledger pruning, default-route renewal double commit re-measured at Runtime ec728da6, missing-custody through the verifier, OS-kill recovery.
   - 4e [Hub] Static-reachability pass of unmediated effect surfaces (FP-01 #1-#3 (U): surface numbering from the s02 registry-and-effects doc, not re-checked) for the MVP route. If any is reachable: locked-component change -> operator approval -> F3 -> refreeze (7 PRs / 7 repos observed).
5. [Qualification] Controller run at the exact candidate (g9-style; a candidate g9-r10 is reported in the Qualification refreeze log (R/U: not located in the files checked); no run exists); retain results.
6. [Qualification] MVP acceptance dossier; [Operator] candidate decision. Release stays HOLD until the exact candidate passes and the operator authorizes.

## Exact release blockers (evidence)
1. No composed run at the lock; hub reference-release red on every main run since 816 (last pass 804; 41 failing main runs as of d2014f3, 43 on a live query 2026-10-23).
2. Verifier c0b8ba1f never probed; ODES 4 failures (3 declared) on the ambiguous-commit evidence path, and Replay lifecycle xfails (ER-07-2) on the same path.
3. Negative controls exist only as executed/INCONCLUSIVE or non-mandatory rows (revocation SCN-C07, ambiguous commit SCN-C08, duplicate SCN-C09, mediation SCN-D09, tamper D07).
4. No exact-candidate identity for current main (hub text/tools since the tag never ran under a controller).
5. Open scope decisions D1-D6; on-path D/R/M items unverified.
