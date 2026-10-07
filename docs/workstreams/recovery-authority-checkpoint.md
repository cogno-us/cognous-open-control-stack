# Batch 4C — recovery-authority qualification

Current Worker 14d handoff is appended below. The original blocked checkpoint is
preserved as historical evidence against its original pins.

## Historical Worker 14c checkpoint

Current main inspected: `8a591d5e61627a85c948d39e59c870526aab2639`.
PR #5 was checked once and was open at exact head
`5e1095dd74030129f670e9c490fbc7c63209d922`. This batch branches from that
head on `worker14c/recovery-authority-qualification` and targets
`worker14c/late-commit-qualification`; it depends on PR #5. No pins or upstream
implementations changed. Repository contributing/governance instructions and the
late-commit checkpoint were inspected before edits.

## Executed boundary and result

Ten transported cases independently change grant revocation, grant expiry, policy
version, mandatory evidence freshness, or approval status after an original
unknown-acknowledgement attempt. Each change is exercised against a real SQLite
applied effect and an interrupted attempt with observed absence. Fault injection
only controls the original destination commit: accepted `lost_ack` for applied,
and a timeout before commit for absence. Authorization and reconciliation remain
in the pinned public implementations.

Expiry advances trusted time from `2026-08-08T01:00:00+00:00` to
`2026-08-09T00:00:00+00:00`. Grant/identity/mandate/approval/policy/conflict/evidence
status fixtures are explicitly refreshed; the original grant expiry remains
unchanged and message lifetime remains valid. A separate public Control Plane
assessment, in a separate record store, verifies exactly the intended rejection
reason in every case. It never dispatches.

Both isolated repetitions: **19 tests: 14 passed, 5 failed, 0 errors, 0 skipped**.
Of these, the ten new cases have **5 passed and 5 failed**; the nine existing
research tests pass. Existing hub release-gate regressions: **74 passed**, zero
failures/errors/skips. Five new required matrix entries each resolve to both
applied/absence tests in both runs and each **fails**. Normal CI executes them.
No xfail, skip, relaxed assertion or successful release claim is used.

All five applied cases hit the same upstream integration defect:
`ImportContractError: denied execution result contradicts retained effect evidence`.
The accepted GAX `resume_original` invokes current authorization, which denies
before destination observation. Its export pipeline combines that denied result
with the original retained applied effect; Replay refuses the inconsistent import.
There is no returned recovery result or successful derivative for these cases.
The blocked path is stopped; no upstream repair is attempted here.

The actual oracle still contains exactly the original applied effect. Across all
ten cases, original dispatch count is one, destination rows are unchanged,
recovery performs zero destination observation queries, and owning Control Plane
records are unchanged. Historical retained reads, transport redelivery, GAX
`recover`, public Evidence Pack import/validation and ODES validation stay
non-effecting and preserve original artifacts. ODES authority and authentication
remain unavailable; historical authorization is not current permission.

The five absence cases return denied recovery, preserve the original pending
effect and unknown acknowledgement, keep unresolved delivery true, and never
permit retry. Their derivative export does not represent a newly accepted
observation. In the expiry case the original observation is historical, not fresh
at recovery time. GAX `resume_original` provides no fresh observation under the
changed authority in this execution. The public executor has a separate
reconciliation API, but this batch does not substitute it for the transported
GAX route or claim its recovery-boundary qualification. Cancellation, termination
and finality are not established by absence.

## Evidence and smallest reproduction

[Qualification summary](../../examples/batch4c-recovery-authority/qualification-summary.json)
contains the unchanged full lock, actual totals, failed required matrix resolution,
and matching normalized outcomes across runs.
[Artifact index](../../examples/batch4c-recovery-authority/artifact-index.json) and
[source hashes](../../examples/batch4c-recovery-authority/source-hashes.json)
identify the raw JUnit/logs and all ten per-case records per repetition. Records
include trusted times, original artifacts/identities, changed resolver inputs,
refreshed fixture list, actual destination rows, dispatch/query counts, public
authority decision, returned recovery or exact exception, commitments and
expected-versus-observed assertions. Earlier evidence remains historical to this
new authority scenario and is not relabeled as its qualification.

With the unchanged accepted `.reference-work` checkouts, the smallest failing
case is `tests/test_research_qualification.py::test_recovery_authority[applied-revocation]`.
Use the same PYTHONPATH and Moltbot roots configured by
`tools/research_qualification.py`, then run `python -m pytest -q` with that one
quoted node ID. The original attempt commits once and loses acknowledgement;
revoke only the synthetic grant status; call public `handler.resume_original`.
The exception is reproduced without any replacement effect. The focused runner
`python tools/research_qualification.py --out results/authority-new-run` executes
all 19 research tests and must currently return nonzero. Full local stack
qualification was not repeated. Final-head CI is checked once after publication;
its observed status is recorded in the PR handoff, never inferred from local tests.

## Next bounded task

Review the reproduction and request a bounded upstream correction to the
GAX/Replay recovery export boundary: distinguish current dispatch denial from
historical applied evidence without erasing the effect or renewing authority.
Only after an accepted repair and separately authorized pin update should these
same required tests be rerun. Keep this PR blocked in the meantime.

Separate-process qualification, cancellation/termination/finality, live OpenShell
and matching worker-image review, production authentication, distributed
guarantees and independent real-world verification remain pending. Equivalent
business-intent deduplication remains a characterized limitation. No deployment,
self-merge, upstream edits, dependency changes or private material.


## Worker 14d — completed local qualification, pending review

Inspected remote PR #6 head `07c250ed4f6fae448dff3d77c7db3a5c5d056531`;
no later Worker 14c work existed. Accepted main
`1f682ab9e2111349a777d77b832c764e1a10cb02` was merged without rewriting
history locally as `8b09c90f3fc3a2c2fa5c02e1df4e668ebd6be1ec`.
Git push credentials were unavailable; API publication uses identical merge tree
`5f344f0e6abe830eeac72f6109d17df95eac9c82` at merge commit
`dce38fad9cfab66bca073c5273ddc24b9ba861ac` with both original parents.
Worker 16 files are preserved. The same remote heads were rechecked before push.

Only selected GAX advances to `c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df`,
reviewed source `b724a065e2668c2018c72ed1caa4cbbd58e60c6a`.
Prior acceptance metadata is retained in the lock. All other selected pins,
including executor `177354e959cc78c59c1a776f018cfbfbf28c927b` and Control Plane
`2ea9528eeb87e14ff10f05de06473122b9df540f`, and all historical pins are unchanged.

Ten changed-authority cases pass through the actual public transport/GAX/Control
Plane/executor path. Each verifies the precise rejection reason using a separate
public Control Plane assessment. The recovery producer's actual reason is
`authorization-critical inputs changed before effect`; it is retained verbatim,
not invented as a more specific producer assertion. Evaluation timestamps are
compared as timezone-aware instants (`Z` and `+00:00` are equivalent).

`recovery_denied_derivative` retains historical Replay/ODES/successor content and
producer refs exactly, with separately attributed current denial/result/reason/time
and source lineage. Owning Control Plane files are required to exist and remain
unchanged. There is no observation/replacement dispatch or renewed authorization.
Unknown acknowledgement remains unknown. Prior-attempt absence remains pending
and unresolved, without retry permission. Valid-authority late-commit controls
perform two measured observations, preserve `observed_absent`, false retry
eligibility and `reconciled_derivative`, and do not dispatch a replacement.
Replay's contradiction check is unchanged.

Validation (Python 3.12):

- Focused `pytest -q tests/test_research_qualification.py -k recovery_authority`:
  10 passed, 9 deselected (the deselected cases run in both full research runs).
- `python tools/research_qualification.py --out examples/worker14d-recovery/final-run-1`
  and the corresponding `final-run-2`: 19 passed each; zero failures/errors/skips.
- `PYTHONDONTWRITEBYTECODE=1 python tools/reference_release.py run --reuse-checkouts
  --results-dir examples/worker14d-recovery/full`: 843 passed per repetition;
  zero failures/errors/skips. Hub gate regressions: 74 passed per repetition.
  All 30 required matrix entries resolve/pass in both runs; repeatability and
  mocked OpenShell checks pass. Live OpenShell is unexecuted.

The reuse option verifies exact locked HEADs and rejects dirty tracked checkouts.
It was added after a historical clone failed with proxy CONNECT 403; missing
historical checkouts were cloned from already fetched local repositories at exact
historical SHAs. No pin substitution. Earlier attempts exposed a missing `agep`
CLI on PATH, timestamp/reason assertion-format errors, and a stale gate SHA
expectation. These diagnostics are archived, never counted as passing runs.
The installed `agep` entrypoint was made available on PATH; generated tracked
bytecode was restored in disposable checkouts before the final run.

[Summary](../../examples/worker14d-recovery/qualification-summary.json),
[source hashes](../../examples/worker14d-recovery/source-hashes.json), and
[artifact index](../../examples/worker14d-recovery/artifact-index.json) bind commands,
exact sources, totals, artifact identities and raw archive members. Extract
`raw-evidence.tar.xz` into an empty directory to inspect raw evidence.

Equivalent-intent duplicate effects remain a characterized limitation. Shared
Control Plane JSON-store concurrency remains unsupported with observed record
loss at this selected pin. Batch B is independent and cannot alter these pins or
evidence. Hub adoption of its repair requires later separate qualification.
No self-merge. Final-head CI will be checked once and recorded in the PR handoff.
