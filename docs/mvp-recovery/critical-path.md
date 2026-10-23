# Artifact 3 - Critical Path

Status: PROPOSED, non-authorizing; HOLD. Locked-component changes, paid tests, deployment and release need the applicable approvals.

## Decisions (architect rulings; operator adoption pending)
- D1 Ingress: control-plane proposal; GAX excluded (Q6).
- D2 Route: route B with operation identity, synthetic SQLite (Q5).
- D3 Evidence: Replay + Evidence Pack with a bounded verifier tested at its exact pin; Orchestrator handoff excluded; ODES only as an evidence-format dependency (Q7).
- D4 Ambiguous commit / ODES: repair and qualify, or prove the runtime keeps `UNKNOWN`, prevents blind retry and requires reconciliation; do not simply exclude (Q9). Failing both: the MVP stays a demonstration and cannot pass the safe-retry / ambiguous-effect claim.
- D5 Enforcement inventory: MVP blocker, bounded to the selected route; reachable unmediated path is a release blocker (Q10).
- D6 Authority: trusted synthetic resolver, limitation stated in the claim (Q8).
- `journal_check_reused`: unconfirmed until verified directly; a pre-claim capture is an explicitly limited demonstration only and cannot satisfy a claim needing an issued, verified claim record; if the selected evidence path requires claim issuance, the gap is a release blocker (Q12).
- g8-r10: cite the reduced 39-row verdict only with the original 75-row result and the post-observation selection statement (Q11).
- Operator actions: adopt the exact bounded profile; accept the authority limitation; approve any material ODES exclusion; no waiver of reachable unmediated paths; approve each locked-component package and refreeze; separate release decision (HOLD).

## Parked PRs (Q15; branches and evidence preserved, not merged)
Orchestrator #130 (`execution_standing` rename), #131 (checkpoint interface), #132 (lifecycle 3.2-A); hub #213 (2.3 dispositions). Reason: off the adopted MVP critical path; no Orchestrator observation wire is in the MVP; the rename is kept in the parked work and applied before that wire's future freeze. Hub #212 (docs-only decision record) is not parked.

## Sequence (owners in brackets)
1. [Hub, docs] This planning PR; record parking of #130-#132 and #213; docs-only hub #212 may merge.
2. [Operator] Adopt the exact bounded MVP profile (D1-D6 as ruled).
2a. [Hub, read-only, immediate, parallel] Two narrow investigations ordered by the architect: static effect-reachability of the chosen route, and a reproducible exact-candidate harness assessment (verifier, ambiguous-commit path, `journal_check_reused`, g9-r10). Their findings decide whether the MVP can be qualified on unchanged locked components or needs a bounded F3 package.
3. [Qualification] Freeze the MVP claim, expectations and negative-control rows before any candidate run (Qualification owns oracles).
4. Parallel after 2-3 (separate owners, no cross-edits):
   - 4a [Orchestrator or Qualification suite] Composed trace harness at the lock pins (re-pin the existing customer_refunds scenario harness; no new service).
   - 4b [ODES/Replay owners] Repair and qualify the ODES/Replay evidence failure, or prove the contained safe-`UNKNOWN`/reconciliation path on the selected runtime (D4, Q9); exclusion of a required evidence contract needs operator approval (Q7).
   - 4c [Qualification] Exact-candidate vehicle (Q14): prefer a direct, independently controlled exact-candidate job in `cogno-us/cognous-stack-qualification` with immutable pins, input commitments and retained raw artifacts; no bypass of relevant checks and no weaker separate oracle; Qualification expressly accepts its equivalence and coverage. Repairing `reference_release.py` and re-pointing the stale 2bb5f10 pin (Q11 requirements in `docs/program-v0.2/s05/`, hub #212) stays necessary for the broader Hub infrastructure but does not automatically block the MVP.
   - 4d [Component owners] Missing negative tests: operation-ledger pruning, default-route renewal double commit re-measured at Runtime ec728da6, missing-custody through the verifier, OS-kill recovery.
   - 4e [Hub] Static effect-reachability inventory of the MVP route (Q10; FP-01 surface numbering from the s02 registry-and-effects doc (U)). A reachable unmediated path is a release blocker. For each blocker first assess whether the MVP can be safely narrowed without falsifying its purpose; otherwise request a bounded F3 package; operator approves each locked-component package, exact revisions and refreeze (7 PRs / 7 repos observed). A locked change may also be needed for a demonstrated safety defect in the route, unresolved ambiguous-effect behaviour, missing mandatory custody or incorrect authority revalidation (Q16).
5. [Qualification] Controller run at the exact candidate (g9-style; the reported g9-r10 candidate stays unverified until its existence, revision and results are established; no run exists); retain results.
6. [Qualification] MVP acceptance dossier; [Operator] candidate decision. Release stays HOLD until the exact candidate passes and the operator authorizes.

## Exact release blockers (evidence)
1. No composed run at the lock; hub reference-release red on every main run since 816 (last pass 804; 41 failing main runs as of d2014f3, 43 on a live query 2026-10-23).
2. Verifier c0b8ba1f never probed; ODES 4 failures (3 declared) on the ambiguous-commit evidence path, and Replay lifecycle xfails (ER-07-2) on the same path.
3. Negative controls exist only as executed/INCONCLUSIVE or non-mandatory rows (revocation SCN-C07, ambiguous commit SCN-C08, duplicate SCN-C09, mediation SCN-D09, tamper D07).
4. No exact-candidate identity for current main (hub text/tools since the tag never ran under a controller).
5. D1-D6 are ruled by the architect and await operator adoption; on-path D/R/M items unverified; the two ordered investigations are pending.
