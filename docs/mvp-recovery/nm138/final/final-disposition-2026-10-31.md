# OCS-MVP-NM138-REPAIR: final technical disposition (2026-10-31)

# TECHNICAL MVP PASS (bounded, AI-assisted; gate verdict ACCEPT, authorizes false, release HOLD)

Not independence, Q7, certification, Final Tier 1, publication, release or production authority. Same-lineage review is not formal independence.

## 1. NM-138 root cause
`suites/mvp-chain/_nc4_03_host.py::sub_a_yama` (NC4-03a) was the only host probe that did not pass through `_cap`. Under `MVP_INGRESS_PROFILE=developer-optout` on a host with Yama ptrace_scope >= 1 it returned PASS, contradicting the module's own rule (optout status capped at BLOCKED). Qualification-harness defect, isolated to that function (other probes cap; `_ingress.py` skips Yama under optout and cannot PASS); not a Control Plane or Runtime defect. Hidden on hosts without Yama.

## 2. Repair
5 lines in `sub_a_yama`: the PASS now goes through `_cap(PASS, ctx.get("ratified", False), NOT_RATIFIED)`. Fail closed: PASS only when the ratified approved profile was resolved (adversarial review finding MED, fixed before the freeze; the first version defaulted to True). Approved profile status, reason and observed keys unchanged. Changed files in the candidate: `suites/mvp-chain/_nc4_03_host.py`; successor plumbing (names only): `.github/workflows/mvp-acceptance.yml`, `tools/mvp_acceptance_gate.py`, `tools/qgate05_custody_check.py`, `tools/qgate05_evidence_commit.sh`, `tests/test_mvp_acceptance_gate.py`; added `process/mvp-acceptance/NM138-SUCCESSOR-RECORD.md`, `candidate-commitment.proposed.v6.json`, `process/governance/qualification-baseline.proposed.md` digests, `tests/test_nm138_yama_cap_regression.py`.

## 3. Regression
`tests/test_nm138_yama_cap_regression.py`: stdlib unittest, 6 tests with subcases, mocked Yama (absent, 0, 1, 2, 3; approved supported and unsupported; unknown profile fails closed; source guard). Frozen source: 9 subcase failures. Repaired source: all pass, also in a clean venv with only the CI lock; full `python -m unittest discover -s tests` 817 tests OK (3 skipped). CI on the PR head green (CodeQL, Analyze, integrity, validate; `validate-and-build` shows cancelled, as on the QGATE-05 head). An earlier head failed CI (pytest import in a unittest-only CI); fixed by a new commit, no force-push.

## 4-6. Candidate, commitment, custody, PR
- Candidate: `83ab03383a5c1ff49937b5d4aad6378c8e2cfe1f` (Qualification PR #257, merged to main as `86f78ea3d1bd9cf230813fa0941621e38e7605e4`, identical tree `ffd867d4…`). Parent `fa12c699` and commitment v5 `81443086…` untouched.
- Commitment v6 `42b482eec25b9d9c1455b5eefc63fb726d7a8041698831cc3c168ea5809a1846` (218 files; vs v5: 5 changed, 2 added).
- Custody: hub branch `nm138/custody-1` @ `4aef20364caf812b6ff6f5770cd0920401621b66` (path `docs/mvp-recovery/nm138/custody/freeze-commitment.json`), pushed once before the run branch.
- Oracle v8 `498efc12…` (48 rows, 47 mandatory), battery v2 `61228fad…` (435 mandatory, NM-138 mandatory), tuple pins and components unchanged.

## 7. Run
https://github.com/cogno-us/cognous-stack-qualification/actions/runs/41169692260 (attempt 1, push of `nm138/run-1` at `83ab0338`, 2026-10-31T04:42:59Z, ubuntu-24.04 image 20261026.354.1). One execution; no retry.

## 8-11. Results (read from the retained artifacts, not the workflow conclusion)
- Oracle: 48 PASS (47 mandatory + KL-01 non-mandatory), 0 FAIL, 0 BLOCKED, 0 NOT RUN.
- Battery: 435/435 mandatory PASS; junit mvp-chain 414, d2-route-b 22, applicability 6 = 442 tests (435 mandatory + 7 non-mandatory), 0 failures, 0 errors, 0 skipped; collected lists match battery v2 one to one.
- NM-138 (`test_developer_optout_can_never_be_pass`): executed and PASSED (original expectation).
- Gate: 19 checks PASS (G-01..G-15 incl. G-02c main anchor, G-05, G-06, G-07, G-12 v6, G-13); verdict ACCEPT, authorizes false, release HOLD. Custody check PASS (hub head 4aef2036, recomputed commitment equals the record).
- Host: environment record 31/31 PASS, profile_supported true; Yama as found 1, effective 1, action none.
- Only test-status change versus the failed run 41165743705: NM-138 fail to pass. Row statuses identical.

## $10 demonstration (Q14 scope)
Governed synthetic $10 refund authorized; route-B atomic execution; exactly 1 applied effect, claim consumed; operation identity and journal observed. Duplicate and lost-ack cases refuse the second effect. Revocation NC1-01..05 PASS. Unauthorized-effect refusals NC7-01..03 PASS. Real SIGKILL NC2-07 at 3 seams (returncode -9; pre-commit 0 effects, claim issued; post-commit 1 effect, claim consumed; no recovery promised). Pruning NC3-04: Control Plane re-authorizes after pruning (documented limit), destination refuses with `operation_already_committed`, 1 effect. Ingress NC4-01..04 incl. host subcases NC4-03a..d on the approved 2751/0660 profile (literal observed facts). Rendering: `demo-rendering-run-41169692260.md`.
Permitted claim only: "The frozen pinned classes compose end-to-end in the qualification harness, while the trusted ingress boundary is separately exercised on the real socket under the same frozen candidate." Not claimed: a live socket request producing the Replay, Evidence Pack or Verifier evidence.

## Replay, Evidence Pack, Verifier
Replay 40 records, reconstruction complete; Evidence Pack 1 valid bundle, 0 errors. Verifier exit 3 ABSTAIN in both runs: run A 22/29 confirmed, 7 could-not-check (`input_absent`, no ledger supplied); run B 27/28 confirmed, 1 could-not-check (`v4.ledger.rows-agree-with-attempts`); 0 refuted; tamper control refuted. ABSTAIN is not a Verifier PASS; VER-01..04 pass only on their explicit oracle wording (exit 0 or 3, no refutation, the single attributable abstention). Run B's ledger is harness-derived. Say "no refutation; abstained", not "verified".

## 12. Adversarial findings
Pre-freeze review (candidate): no blocker or high; one MED (fail-open default) fixed. Post-run evidence review: no blocker or high; no reason against PASS. LOW/INFO: "48 PASS" includes non-mandatory KL-01; `summary.md` prints "attempt None; sha None" (rendering defect, also in the historical run); `collect-mvp-chain/results.json` is collect-only output (PASS 1, NOT RUN 47), not results; `chain-destination.sqlite` omits its `-wal` (shows 0 rows; the effect fact rests on observations and executor-export, 1 effect); artifact-zip digest not captured (zips unreadable here); journal continuity is observed, not asserted by a row; Evidence Pack `generated_at` is wall-clock so not byte-reproducible. Boundary note: the reviewer briefly created and removed sqlite sidecars in a local view; the preserved evidence commit and the view verified clean afterwards.

## 13. Evidence references
Qualification branch `nm138/evidence-run-1` @ `1719ca351ac6a0f61905930610f4c5aac5defaee`, `runs/run-41169692260-attempt-1/` (256 files in SHA256SUMS, 256/256 verified; SHA256SUMS sha256 `dd55a8d735c093946080988cc820176156685dda3c99da51d39a62c55fcd2cc8`). Historical failed evidence `qgate-05/evidence-run-1` @ `ef407ca3` unchanged.

## 15. Remaining limits and holds
Single synthetic scenario on the hosted bounded profile; Q14 composition; Verifier abstains; same-lineage review only; no production hardening. Holds unchanged, none waived: F3 CLOSED; F3 Q2/Q3 UNRESOLVED; Q7 NOT ESTABLISHED; Final Tier 1 DEFERRED, NOT WAIVED; publication/release/production HOLD; Registry #58/#59, Control Plane #87, Ed25519 #26/#34 HELD; constructor tolerance NOT AUTHORIZED; V09 SEPARATE; DEF-OBS-TOL-OVERFLOW-1 OPEN, SEPARATE; R1 DEFERRED.
