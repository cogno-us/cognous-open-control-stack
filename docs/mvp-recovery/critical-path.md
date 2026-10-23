# Artifact 3 - Critical Path

Status: PROPOSED, non-authorizing; HOLD. Locked-component changes, paid tests, deployment and release need the applicable approvals.

## Decisions (architect rulings; operator adoption pending)
- Decision 1 Ingress: control-plane proposal; GAX excluded (Q6).
- Decision 2 Route: route B with operation identity, synthetic SQLite (Q5).
- Decision 3 Evidence: Replay + Evidence Pack with a bounded verifier tested at its exact pin; Orchestrator handoff excluded; ODES only as an evidence-format dependency (Q7).
- Decision 4 Ambiguous commit / ODES: repair and qualify, or prove the runtime keeps `UNKNOWN`, prevents blind retry and requires reconciliation; do not simply exclude (Q9). Failing both: the MVP stays a demonstration and cannot pass the safe-retry / ambiguous-effect claim.
- Decision 5 Enforcement inventory: MVP blocker, bounded to the selected route; reachable unmediated path is a release blocker (Q10).
- Decision 6 Authority: trusted synthetic resolver, limitation stated in the claim (Q8).
- `journal_check_reused`: reproduced in a builder harness (see [investigation-findings.md](investigation-findings.md); not a Qualification result); earlier text: unconfirmed until verified directly; a pre-claim capture is an explicitly limited demonstration only and cannot satisfy a claim needing an issued, verified claim record; if the selected evidence path requires claim issuance, the gap is a release blocker (Q12).
- g8-r10: cite the reduced 39-row verdict only with the original 75-row result and the post-observation selection statement (Q11).
- Operator actions: adopt the exact bounded profile; accept the authority limitation; approve any material ODES exclusion; no waiver of reachable unmediated paths; approve each locked-component package and refreeze; separate release decision (HOLD).

## Oct 31 operator schedule (targets, not commitments)

Source: operator directive "Revised delivery directive" (Oct 31 target). The dates are targets, not confirmed worker commitments, and assume the known journal fix does not expose further critical defects. The architect's reasoned elapsed-time ranges (optimistic 10-14, central 18-25, adverse 30-45+ calendar days; see [delivery-estimate.md](delivery-estimate.md)) are longer than the eight days from Oct 23 to Oct 31. The two are not reconciled here: the operator's dates are a target; the architect's ranges are the reasoned estimate. The principal serial risk is the Control Plane F3 repair and refreeze. Implementation completeness on Oct 31 (a frozen candidate) is not independent acceptance; acceptance is separate (Nov 3-6) and contingent on Qualification passing.

| Date | Deliverable | Owner |
|---|---|---|
| Oct 24 | Freeze MVP scope, mandatory negatives and exact supported profile | Qualification + Hub |
| Oct 25 | Replay claim-record reproduction; effect-route inventory; F3 patch ready (not applied to the locked repo before operator authorization) | Replay + Control Plane |
| Oct 27 | Control Plane F3 regression passing; integration harness implemented | Component + Qualification |
| Oct 29 | Exact-candidate integration and synthetic negative battery run | Qualification |
| Oct 30 | Refreeze and Hub pin reconciliation; final regression | Component owners + Hub |
| Oct 31 | Implementation complete; exact candidate frozen | Engineering lead |
| Nov 3-6 | Independent acceptance dossier and operator decision | Qualification + operator |

### Workstreams (parallel, separate files, no cross-edits)
- A Control Plane F3 (Control Plane owner): minimal claim-journal repair for `stage`/`check_ref` through the real claim path; regression with the pinned Verifier; compatibility with existing records; exact F3 authorization package for the operator. Modified locally only until the operator authorizes the exact package.
- B Qualification harness (Qualification owner): `suites/mvp-chain/` pinned to the exact tuple, the supported scenario and six mandatory negative controls; Qualification keeps oracle and verdict ownership. Harness sub-workers build code and test cases only and report raw observations and exit codes.
- C Replay and evidence (Replay owner): reproduce Replay on the claim-issued record; independent reconstruction of pre-claim and post-claim evidence; fix only demonstrated MVP-blocking defects; keep historical failures.
- D Integration and reachability (Hub): refund harness for the tuple; trusted-host ingress restrictions; static inventory of reachable effect surfaces; operation identity, duplicate prevention and UNKNOWN/no-blind-retry validation.

### Serial dependencies
Oct 24 freeze -> (A, C, D in parallel) -> operator F3 authorization -> F3 merge and component tests -> refreeze and pin reconciliation -> exact-candidate battery on the refrozen tuple -> acceptance dossier -> operator decision. The battery cannot run on the final tuple before the refreeze; earlier runs are rehearsals only. The F3 refreeze is the principal serial risk (7 PRs / 7 repos observed per refreeze).

### Stop conditions (escalate; do not continue the affected path)
- A reachable unmediated effect path inside the supported interface.
- Authority bypass or duplicated effects through the supported path.
- The claim-journal defect needs materially broader changes than the bounded F3 package.
- Essential custody or reconstruction cannot be established.
- The trusted-host profile cannot be enforced as defined (then the operator decides on a MAC package, architect Q10).
A failed mandatory control means the implementation is not complete; it is reported as failed, not relabelled. Off-path problems are preserved and deferred. No readiness claim: production, release and publication HOLD are unchanged.

## Parked PRs (Q15; branches and evidence preserved, not merged)
Orchestrator #130 (`execution_standing` rename), #131 (checkpoint interface), #132 (lifecycle 3.2-A); hub #213 (2.3 dispositions). Reason: off the adopted MVP critical path; no Orchestrator observation wire is in the MVP; the rename is kept in the parked work and applied before that wire's future freeze. Hub #212 (docs-only decision record) is not parked.

## Sequence (owners in brackets)
1. [Hub, docs] This planning PR; record parking of #130-#132 and #213; docs-only hub #212 may merge.
2. [Operator] Adopt the exact bounded MVP profile (Decisions 1-6 as ruled).
2a. [Hub, read-only, immediate, parallel] Two narrow investigations ordered by the architect: static effect-reachability of the chosen route, and a reproducible exact-candidate harness assessment (verifier, ambiguous-commit path, `journal_check_reused`, g9-r10). Their findings decide whether the MVP can be qualified on unchanged locked components or needs a bounded F3 package.
3. [Qualification] Freeze the MVP claim, expectations and negative-control rows before any candidate run (Qualification owns oracles).
4. Parallel after 2-3 (separate owners, no cross-edits):
   - 4a [Orchestrator or Qualification suite] Composed trace harness at the lock pins (re-pin the existing customer_refunds scenario harness; no new service).
   - 4b [ODES/Replay owners] Repair and qualify the ODES/Replay evidence failure, or prove the contained safe-`UNKNOWN`/reconciliation path on the selected runtime (Decision 4, Q9); exclusion of a required evidence contract needs operator approval (Q7).
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
5. Decisions 1-6 are ruled by the architect and await operator adoption; on-path D/R/M items unverified; the two ordered investigations are pending.
