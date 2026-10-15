# Nonselected remediation full-reference qualification

Status: **BLOCKED — broader full-reference qualification failed.** The prior
23-case remediation qualification remains unchanged within its original scope.

Starting hub main: `0e82e8f057950c21bffef1ecb4e62326fd9a50b8`.
The separate `profiles/remediation-full-reference-20261015.json` derives its
thirteen component pins from the unapplied owner proposal. It is explicitly
`selected=false`, `qualification_status=candidate`, with both release and
production authorizations false. Existing locks, profiles, selection proposal,
acceptance matrix and frozen publication kit remain unchanged.

The existing reference runner executes authority, exchange, consumer and registry
batches twice. The separate workflow checks out its exact PR head and retains
failed-run artifacts. The aggregator accepts an explicit profile path and keeps
its historical default. No failure, skip or incompatible historical fixture is
converted into current candidate qualification. Prior 23-case bounded evidence
retains its original scope.

Reproduction (each batch needs an isolated checkout, or run serially with exact
clean reusable component checkouts):

```bash
python tools/reference_release.py run --profile profiles/remediation-full-reference-20261015.json --batch authority --results-dir results/remediation-full-authority
python tools/reference_release.py run --reuse-checkouts --profile profiles/remediation-full-reference-20261015.json --batch exchange --results-dir results/remediation-full-exchange
python tools/reference_release.py run --reuse-checkouts --profile profiles/remediation-full-reference-20261015.json --batch consumers --results-dir results/remediation-full-consumers
python tools/reference_release.py run --reuse-checkouts --profile profiles/remediation-full-reference-20261015.json --batch registry --results-dir results/remediation-full-registry
python -m tools.aggregate_full_candidate --profile profiles/remediation-full-reference-20261015.json --artifacts results --out aggregate-results
```

Use an artifacts directory containing only these four batches for aggregation.
The aggregator requires all batches, exact profile hashes, mandatory suites, two
repetitions, representative repeatability and the unchanged acceptance matrix.
Optional protocol checks are static JSON checks only. Existing mock/local, C0 race,
cooperative C1 and restore-characterization boundaries are unchanged. This work
does not exercise real settlement, production identity, independent acceptance
or a deployed external restore anchor.

Publication and production HOLD. Operational trust HOLD / NOT ESTABLISHED.
This new profile/tooling/report is outside the frozen 206-file publication kit
and its earlier inventory and screening. No release, selection or settings change.

## Executed diagnostic results

Execution used local Python 3.12 at tooling head
`f5f0744e159790801a4be3d9e83d5d53d05786c9`; no hosted execution or new CI pass
is claimed. The initial authority setup was interrupted before tests; the resumed
run reused exact tracked-clean checkouts. All four batches then completed twice.
The consumer batch was repeated after correcting the local virtualenv PATH.
Original failed logs remain retained; the table uses that corrected consumer run.
Counts below enumerate raw JUnit testcase elements, including any subtest
representations emitted by pytest; they are not asserted to be independent cases.

| Batch | Elements per repetition | Passed | Failed | Errors | Skipped | Disposition |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Authority | 155 | 87 | 0 | 68 | 0 | BLOCKED |
| Exchange | 109 | 45 | 50 | 14 | 0 | BLOCKED |
| Consumers, corrected PATH | 737 | 621 | 0 | 97 | 19 | BLOCKED |
| Registry | 82 | 82 | 0 | 0 | 0 | PASS, bounded scope |

Both repetitions have the same counts in each batch. The registry also ran
20 Node tests per repetition with zero failures/skips. Optional protocols received
static JSON checks only. The authority batch's separate OpenShell mock suite
reported 120 testcase elements: 112 passed, eight failed. It is outside the
155-element per-repetition counts above. No failed or skipped scope is accepted.
The aggregate rejected the failed batch reports with exit 1; the acceptance
matrix was not declared resolved or qualified. Nine existing aggregate gate tests
passed, including negative controls. All component tracked-source checkouts
remained clean after execution.

## Observed blockers and repair boundaries

1. **Dated synthetic time is not migrated to the current service clock.** Actual
   CP records in the representative exchange have result `hold` with
   `grant_outside_validity`, `approval_status_stale_or_future`,
   `required_evidence_stale_or_future` and other stale-input reasons. This is
   consistent with August fixtures evaluated in October. The representative
   consequently has no execution envelope; the material gate rejects that absence.
   All 68 authority errors originate in this failed transported fixture. The
   OpenShell integrated fixture also receives `hold` where it expects authorization.
   This establishes harness incompatibility, not a newly established authorization
   bypass or a basis for weakening freshness checks. A migrated fixture must use
   an explicit, declared synthetic service clock, as the bounded S1 harness does.
2. **Historical producer qualification is fed the new generation.** GAX's
   qualification fixture explicitly requires `merged-producers-v1`, while the new
   profile selects `typed-refusal-candidate-20261015`. Replay's historical example
   generator rejects executor `309e194c...` as the wrong pinned producer. Evidence
   Pack's historical merged generator rejects the new Replay HEAD; ODES's analogous
   historical generator also fails setup. The consumer errors are 19 Replay,
   26 Evidence Pack and 52 ODES per repetition. Preserve those historical tests at
   their original exact input pairs; add explicitly current-generation suites rather
   than relabeling their commitments or replacing their expected constants.
3. **Local PATH issue, resolved and retained as environmental evidence.** The
   first consumer attempt could not find `agep`, producing 14 CLI failures per
   repetition. Prepending the qualification virtualenv's bin directory resolved
   all 14 in the complete rerun. It did not resolve the 97 generation errors or
   the 19 declared skips. No component repair is inferred from this PATH correction.

Next scoped engineering: preserve historical suite inputs in the runner, migrate
current-generation synthetic clock fixtures in their owning test surfaces, add
mandatory current typed-refusal suites to broader qualification, and rerun the
unchanged acceptance matrix and actual representative destination assertions.
Do not broaden consumer revision allowlists, patch provenance strings, remove
semantic comparisons, reset ownership stores or turn setup errors into passes.
The complete corrected full-reference run remains a prerequisite for broader
claims; the existing seven-component 23-case pass is not invalidated or extended.

[Machine results](remediation-full-reference-2026-10-15.json) record the profile
and tool hashes, per-repetition counts, failing suites, aggregate rejection and
hashes of retained raw evidence. Raw logs include process/environment diagnostics
and remain outside the proposed public report population pending screening.
These local follow-up files are outside the frozen publication kit and earlier
scan coverage. Automatic approval review blocked the public branch push; no PR
or hosted result is claimed for this follow-up. The local changes are reviewable.

Candidate nonselected; selected lock and all four previous profiles byte-identical.
Both authorizations false; publication/production and operational trust HOLD.
