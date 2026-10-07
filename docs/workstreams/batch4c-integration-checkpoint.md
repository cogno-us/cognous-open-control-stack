# Batch 4C — Worker 14c bounded integration checkpoint

Starting PR #4 head: `23a42f41c4937360a841e122282dd9aafbf7ef43`.
Branch: `worker14b/batch4c-qualification`. No hub AGENTS.md; CONTRIBUTING and GOVERNANCE read.
Repository checkpoint continuity used; no project-history reconstruction or adjacent edits.

## Dependency gate

Alvorada PR #6 was **open, unmerged** at the single dependency check.
Candidate head: `8836136c8b17a5eeda65467d06976d2164927515`.
Tests run **37551082772: completed / success**. No polling and no upstream merge.
The candidate contains the correction retaining the original attempted effect as pending
and unresolved after fresh observed absence, without retry eligibility.
Previously accepted Alvorada: `6bcde026a804c7377f5e39f57ca6dd00b3c3292d`.

## Exact selected pins

| Component | SHA | Status |
|---|---|---|
| action_manifest | `46c950bed37fe3812000895430bc0312d29e37ce` | accepted supplied revision |
| control_plane | `2ea9528eeb87e14ff10f05de06473122b9df540f` | accepted supplied revision |
| constitutional_authority | `fb3d97938969a89e149e8ff8db2756091d1233fc` | accepted supplied revision |
| gax_imx_transport | `8836136c8b17a5eeda65467d06976d2164927515` | candidate, unmerged PR #6 |
| moltbot_safe | `177354e959cc78c59c1a776f018cfbfbf28c927b` | accepted supplied revision |
| replay_bundle | `274543f1cd7171784a923a8e37015017a0d8bc9d` | accepted supplied revision |
| governance_evidence_pack | `812194b9a89a5fa21e675200fcb4e0089666f1b6` | accepted supplied revision |
| odes | `226adb0e3cde5377ac9db6f7e5857bfa7e65e30a` | accepted supplied revision |
| bitrep | `5b5077dafde232a7801cb425c4efddcffb468723` | unchanged baseline |
| the_index | `d5e45d275cb301d9684b543e93b05997991d1cf2` | unchanged baseline |
| prp | `cb137f028e92448a56e785e3d4ea074b444fa225` | unchanged baseline |
| research_intelligence | `30c7274b49c07a0df4c8ca7b281f2e3f8ae68dee` | unchanged baseline |
| tfa | `442d07b4891870abb1756fcb11c24ccf187706f4` | unchanged baseline |

## Changes

- Explicit fixture ObservationPolicy and timezone-aware clocks reach transport/GAX/executor.
- Hub consumes original retained artifacts via public APIs and enforces export profile 1.1.0.
- Updated absence probes require false retry eligibility and explicit rejected/unavailable observations.
- Added the pinned transported lifecycle suite to both repetitions and required matrix coverage.
- Original artifacts survive redelivery; evidence-only derivatives do not replace execution.
- Candidate status is embedded in execution evidence, independently of test success.
- Historical versions and evidence remain attributed to their original revisions.

## Qualification

Final command: `PATH="/root/.local/bin:$PATH" python tools/reference_release.py run --results-dir results/batch4c-final`.
Python 3.12.14. Two isolated repetitions with separate stores and subprocesses:

| Evidence | Repetition 1 | Repetition 2 |
|---|---:|---:|
| Python passed | 831 | 831 |
| Python failed / errors / skipped | 0 / 0 / 0 | 0 / 0 / 0 |
| Local-chain passed | 20 | 20 |
| Local-chain failed / skipped | 0 / 0 | 0 / 0 |
| Required matrix entries passing | 24 | 24 |
| Transported representative | passed | passed |

Normalized representative repeatability: **passed**. OpenShell mock: **120 passed,
0 failed/errors/skipped**. Candidate qualification passed; **release_qualified=false**
because Alvorada remains unmerged. No CI success is inferred from these local results.

[Complete executed evidence](../../examples/batch4c-integration/scenario-results.json),
[JUnit/scenario resolution](../../examples/batch4c-integration/scenario-matrix-results.json),
[commitment/hash index](../../examples/batch4c-integration/artifact-index.json), and
[repeatability](../../examples/batch4c-integration/representative-repeatability.json).
Original artifacts, gate inputs, effect/destination rows, scenario records, raw logs
and JUnit are retained for both runs. Source hashes bind the executed code and lock.

The two-proposal characterization produces **two** effects; replay produces no third.
Stale/incomplete/wrong-effect/unavailable observations hold with retry_eligible=false.
Interrupted-attempt absence preserves the original pending effect and unresolved delivery;
applied recovery clears pending delivery without replacement and retains earlier rejection
and unknown acknowledgement history. Held/denied before an attempt has no pending effect.
Original redelivery and evidence-only derivatives preserve their distinct identities.

Final-head CI: to be checked once immediately after publication and recorded in PR #4.
No workflow polling is part of this checkpoint.

Initial diagnostic full run exposed hub environment wiring and stale scenario
references, not a proved upstream defect: historical suites received v2 producers;
v2 suite roots were absent; two references used the old lost-ack test name.
Its totals per repetition were {'errors': 42, 'failures': 36, 'passed': 658, 'skipped': 95, 'tests': 831}.
The representative and normalized repeatability passed, but the aggregate gate
failed. These diagnostic results are not final qualification.

The runner now preserves test-only historical pins in separate environments,
sets explicit v2 roots, runs each upstream suite from its expected working directory,
and executes historical/v2 Evidence Pack coverage in separate processes. Two stale
matrix references now resolve to the renamed lost-ack test, retaining unknown
acknowledgement while allowing accepted applied evidence to resolve delivery.
No assertion was removed to obtain a pass. Focused corrected component runs:
Replay 213; ODES 106; historical Evidence Pack 168; v2 Evidence Pack 43 passed.


## Remaining blockers and next bounded task

Alvorada acceptance and final-head hub CI/review remain required for release acceptance.
Do not self-merge. Deferred Alvorada PR #2 stays excluded.

Next bounded task: after Governor acceptance of Alvorada PR #6, verify its merge contains
the prior-attempt absence correction, replace only the candidate transport pin with the
full accepted merge SHA, and rerun the same two-repetition qualification. If still unmerged,
leave the candidate checkpoint intact.

Separate pending work: remaining Batch 4C in-flight/late-commit and recovery-authority
scenarios; separate-process boundaries not already demonstrated; live OpenShell qualification
and matching worker-image review; production authentication; distributed guarantees;
independent real-world verification. Equivalent business intent under distinct valid
proposals and a multi-use grant remains a characterized two-effect limitation.
Same-effect deduplication does not establish business-intent deduplication.
