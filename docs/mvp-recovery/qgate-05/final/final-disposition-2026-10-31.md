# OCS-MVP-FINAL: final technical disposition

**TECHNICAL MVP FAIL** (frozen gate verdict REJECT). AI-assisted technical result for the bounded synthetic $10 refund MVP at the frozen candidate. Not organizational independence, Q7, certification, Final Tier 1, release or production authority. Same-lineage AI roles (fresh-context, builder-spawned workers); no separate top-level sessions.

## Why FAIL and not PASS
The single authorized frozen run executed completely. The gate rejected it on exactly one check, G-06, because one mandatory battery test failed: `NM-138` = `suites/mvp-chain/test_nc4_03_host_subcases.py::test_developer_optout_can_never_be_pass`. All 47 mandatory oracle acceptance rows are PASS. The failed test is a mandatory entry of the frozen battery, so the frozen rule makes the verdict REJECT; this disposition does not relabel it.

**Nature of the failure (adversarial review, CONFIRMED by code):** a harness-module defect, not a control defect. `_nc4_03_host.py::sub_a_yama` returns PASS (uncapped) when Yama ptrace_scope is 1/2/3 even under `MVP_INGRESS_PROFILE=developer-optout`, while the module's own docstring and frozen spec say every optout status is capped at BLOCKED. The test is right and the module violates its own spec; it was hidden on hosts without Yama (all local dry runs). It cannot cause a false PASS or false FAIL of any oracle row (the run used the approved profile; NC4-03a..d PASS with literal facts). Under a mistaken optout run only NC4-03a (a true kernel fact) would read PASS (LOW).

**Minimum actual blocker:** correcting this needs a separately identified successor candidate (new commit, new commitment, new custody) and new Architect authority. Nothing was repaired, rerun or retried under this directive. The one authorized dispatch is consumed.

## Frozen source tuple and commitment
Qualification `fa12c699939880149ed3997cbc2b11b264b23acd` (merged to main as `b6142518df02d30229df668ccc90f75c74e30609`, tree `c5f9c6328184eb46b2683142f173bc7be8dee78d` identical). Commitment v5 sha256 `814430869c63ab57cae091624c512bb119a3291e39e043827ae180ad59d3ca49`, 216 files. Tuple: Control Plane `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c`, Runtime `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f`, Replay `40012b8c174c6f25685bd5d9bc93ff46cc9a5842`, Evidence Pack `7b9511f2c6d56d424f17b078826594abd29f6c96`, ODES `1a5e1d300250d832e611633f0bf8f762e398c0ec`, Action Manifest `fa170815ef96a54c233d0dd9da821b60debabf8b`, Verifier `c0b8ba1f55b75db787a320f3de0f79342c6f6826`, hub `c897266b7ce4b921889519087fa8b1863b4302e3`. Custody: hub branch `qgate-05/custody-1` @ `992a19161d315cbaf0e105f1ea01a1ceba9a028d` (record independently re-resolved by the adversarial reviewer; the run's own custody check PASS).

## Accepted denominators (script-recomputed)
Oracle v8: 48 rows, 47 mandatory (36 mandatory NC in 7 groups: NC1 5, NC2 7, NC3 4, NC4 8, NC5 5, NC6 4, NC7 3; ENV 1, CHAIN 6, VER 4); KL-01 non-mandatory. Battery v2: 435 mandatory entries (+7 non-mandatory tests: KL-01, D2C-01..06); collected 414 + 22 + 6 = 442; 0 skipped; no retry. (The 42/41/30/260 figures were the historical pre-amendment baseline.)

## Existing evidence reused
None for row acceptance. No frozen-qualification run existed before the dispatch (OBSERVED: the Qualification repo had no battery run; hosted QGATE-02/03 captures are host-feasibility records at other pins/profile with unread artifacts; green PR checks are hygiene/gate-unit CI; builder dry runs have no retained artifact). All 47 rows were UNTESTED at the frozen candidate before the run (crosswalk: `c-crosswalk/`).

## New execution performed
One run: https://github.com/cogno-us/cognous-stack-qualification/actions/runs/41165743705, attempt 1, event push to `qgate-05/run-1` at `fa12c699`, ubuntu24 image 20261026.354.1, kernel 7.0.0-1017-azure, Yama ptrace_scope found 1 / effective 1 (no change). Dispatched 2026-10-31T03:45:36Z. Acceptance job failure (gate exit 1), evidence job success.

## Mandatory rows (oracle) and battery
Oracle: 47 PASS / 0 FAIL / 0 BLOCKED (plus KL-01 PASS, non-mandatory). Battery: 434 PASS / 1 FAIL (NM-138) / 0 skipped. Gate: 18 checks PASS, G-06 FAIL; verdict REJECT, authorizes: false, release: HOLD. G-11 hub environment record: overall PASS, profile_supported true, 31/31 PASS. G-12 commitment (216 files) PASS; G-02c anchor to main PASS.

## $10 MVP demonstration result
Rendered from the retained artifacts (`b-demo/demo-rendering-run-41165743705.md`, `render_demo.py`): governed synthetic $10.00 USD refund authorized by the Control Plane; route-B atomic executor produced exactly 1 applied effect whose id matches the decision; operation identity and journal continuity recorded; chain consistent. Scope per Q14: "The frozen pinned classes compose end-to-end in the qualification harness, while the trusted ingress boundary is separately exercised on the real socket under the same frozen candidate." It is NOT claimed that a live socket request produced the reconstructed Replay, Evidence Pack or Verifier evidence.

## Negative-case outcomes (all PASS in the run)
NC1 revocation incl. NC1-04 reactivation after revocation refused (0 effects). NC2 ambiguous commit / lost-ack / duplicate denied, effect_count 1; NC2-07 REAL OS kill: SIGKILL returncode -9, pid gone, fresh observer, three seams; pre-COMMIT 0 effect rows, reconcile hold (`no_durable_effect_for_claim`), re-presented claim executes exactly once then denied; post-COMMIT 1 effect, claim consumed, reconcile applied, re-presentation denied (no promise of automatic recovery). NC3-04 pruning: Control Plane holds while intact; after pruning it authorizes again (documented limit, disclosed in the row); the destination still refuses with `operation_already_committed`, exactly 1 effect. NC4 trusted-ingress boundary on the real socket under the ratified 2751/0660 profile: NC4-01/02/04 PASS; NC4-03 deterministic set 69 mutations rejected, 13 controls accepted, 0 falsely rejected; NC4-03a..d PASS with literal facts. NC5 tampering and NC6 custody failures refused; NC7 PASS.

## Replay, Evidence Pack, Verifier
Replay bundle: 40 records. Evidence Pack valid. Verifier (pinned): run A and untampered control T0: 22 confirmed, 7 could-not-check (all `v4.ledger.*`), exit 3 ABSTAIN; run B (with the harness-derived ledger): 27 confirmed, 1 could-not-check (`v4.ledger.rows-agree-with-attempts`), exit 3 ABSTAIN; tampered T1: 1 refuted (`v2.journal.decisions`). No refutation of the untampered chain. Verifier ABSTAIN is NOT a Verifier PASS: VER-01 and VER-03 pass because their oracle wording explicitly requires/accepts the abstention (VER-03 requires exit 3 with could-not-check exactly `["v4.ledger.rows-agree-with-attempts"]`), VER-02 and VER-04 are non-abstention rows (no finding / retention).

## Adversarial technical findings (Worker D, fresh-context, CHALLENGED the lead's reading)
F1 MED CONFIRMED: NM-138 defect as above. F2 LOW-MED CONFIRMED: `chain-destination.sqlite` was copied without its `-wal` file (`_chain.py:313`), so the retained copy shows 0 effect rows while the observation, executor export and B-ledger show 1; the $10 effect is not independently corroborated by that file (a gap, not a contradiction). F3 LOW: GitHub artifact digest not captured and job logs unreadable; integrity rests on the evidence job self-verification and git commit `ef407ca3`. F4 LOW: `summary.md` prints "attempt None; workflow sha None" (summarizer key bug; the identity files are correct). F5 LOW: the Control Plane authorizes a duplicate after its ledger is pruned (disclosed limit). Pre-run residuals disclosed earlier (the `/var/lib` base path, floating image label, mutable custody branch) did not cause a failure in this run.

## Raw evidence and immutable references
Qualification branch `qgate-05/evidence-run-1`, commit `ef407ca3c47de22af7cf901147baa5bad226e057`, directory `runs/run-41165743705-attempt-1/` (256 files; `SHA256SUMS` 256/256 verified by the lead and the reviewer; includes junit, console, observations/results, gate verdict, host evidence, kill/pruning/Verifier/Replay/Pack artifacts). Frozen tree: Qualification `fa12c699` / main `b6142518`. Custody: hub `qgate-05/custody-1` @ `992a1916`; Issue #215 comments 6538496248 and the closeout comment.

## Remaining material limitations
Same-lineage AI-assisted technical review only; Q7 formal independence NOT ESTABLISHED. Local dry runs are not evidence. The ingress boundary is exercised separately from the in-process chain (Q14). VER rows rest on Verifier ABSTAIN as the oracle defines. Pruning limit and 2751 stat residual are disclosed accepted limits. The failed test NM-138 stands as a failure of the frozen candidate until a successor candidate is authorized.

## Standing holds (unchanged, none waived)
F3 CLOSED; F3 Q2/Q3 UNRESOLVED; Q7 NOT ESTABLISHED; Final Tier 1 DEFERRED, NOT WAIVED; publication/release/production HOLD; Registry #58/#59 HELD; Control Plane #87 HELD; Ed25519 #26/#34 HELD; constructor tolerance NOT AUTHORIZED; V09 SEPARATE; DEF-OBS-TOL-OVERFLOW-1 OPEN, SEPARATE; R1 DEFERRED.
