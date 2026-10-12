# Evidence index

## Selected generation (current lock)

The selected source of truth is [component-lock.json](../component-lock.json) at this hub revision. Its `merged-producers-v1` default generation is evidenced by [full-candidate CI 37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916): tested hub source `7e43d55c6cc0123a191480a9e6870d6452affa83`, accepted hub merge `f801546d5272104b02a240e1126b3f92f26486f2`, 35 acceptance scenarios with required suites run twice. GitHub artifact `full-candidate-gate` (artifact ID `11513869868`) records SHA-256 `5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7`. The digest refers to the GitHub artifact archive, not to this page or a document inside the archive. See the [detached collateral manifest](../collateral/evidence-snapshot.json) for exact file hashes, selected Control Plane/executor pins and the frozen collateral snapshot date of 2026-10-09. The frozen snapshot's `accepted_hub_pin` is its historical source anchor, not a claim that it equals current `main` HEAD.

**Separate, non-additive populations:** [optional C1 CI 37682165860](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860) reports 73 passing tests at reviewed hub source `e926bbd70126ae9664bb4189bfe12eec4c18336b`; C1 is not enabled by the default release. The earlier persistence-generation [CI 37616662337](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37616662337) reports 915 Python tests in each of two repetitions at source `7c7eaa0a72401a789c0a5adac59f68d59b94ff19`; it is historical, not another current release-count claim. Artifact digests and source metadata can be checked independently using the GitHub Actions artifact listings. Raw artifact contents require separate extraction and inspection; metadata alone does not revalidate constituent JUnit cases, destination stores or exact test totals.

The default C0 profile revalidates before dispatch but retains a check-to-commit race. Optional C1 is same-host SQLite-local; C2/C3 and external settlement remain unqualified. Effect-ID deduplication is not equivalent-business-intent deduplication. Operational trust [orchestrator #30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30) remains **HOLD / NOT ESTABLISHED** and is not upgraded by collateral validation.

## Historical evidence navigation (not selected default release counts)

| Scope | Evidence and provenance |
|---|---|
| Separate accepted protected worker, fixed compatible-host scope | [Completed review](workstreams/protected-qualification-checkpoint.md#completed-compatible-host-review), [campaign](../examples/protected-qualification/ci-37621009389/campaign/summary.json), [host profile](../examples/protected-qualification/ci-37621009389/host-profile.json), [provenance](../examples/protected-qualification/ci-37621009389/provenance.json); earlier local/Ubuntu 24.04 attempts remain blocked |
| Accepted persistence-generation qualification | [Verified summary](../examples/control-plane-store-adoption/qualification-summary.json), [CI run 37616662337](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37616662337); tested head `7c7eaa0…`, accepted merge `41c2eec…`, artifact `11479891871` |
| Latest committed full/research execution before PR #8 persistence adoption | [Worker 14d summary](../examples/worker14d-recovery/qualification-summary.json), [artifact index](../examples/worker14d-recovery/artifact-index.json), [source hashes](../examples/worker14d-recovery/source-hashes.json), [archive instructions](../examples/worker14d-recovery/README.md), [checkpoint](workstreams/recovery-authority-checkpoint.md#worker-14d--completed-local-qualification-pending-review) |
| Separate accepted same-host process qualification | [Worker 16 checkpoint](workstreams/process-boundary-checkpoint.md), [evidence directory](../examples/process-boundary/); keeps destination serialization separate from unsupported shared JSON-store writes |
| Earlier accepted observation-validation integration | [Batch 4C accepted results](../examples/batch4c-accepted/scenario-results.json), [artifact index](../examples/batch4c-accepted/artifact-index.json), [checkpoint](workstreams/batch4c-integration-checkpoint.md); these precede the selected GAX recovery-export repair |
| Focused late-commit execution at its recorded pins | [Checkpoint](workstreams/late-commit-checkpoint.md), [local summary](../examples/batch4c-late-commit/qualification-summary.json) |
| Historical changed-authority export failure | [Failure summary](../examples/batch4c-recovery-authority/qualification-summary.json); preserved, not current qualification |

PR #8 persistence adoption is accepted. Both CI repetitions passed 915 Python tests with zero failures, errors or skips. All 35 matrix entries satisfied their gates; equivalent-intent duplication remains characterized, not prevented. Artifact SHA-256: `0b10fd9d0ce779232d38f0ba67ed9123ff084ec759ac51cc44a65188ea79d42e`. For other component acceptances not selected by the hub, use [support status](release-status.md).
Compare each run's lock/source hashes before applying its claims. Earlier accepted
evidence is not automatically evidence for a later pin set. Checkpoints retain
historical pending/blocked language; current navigation does not rewrite them.

## Evidence produced by a reference run

The canonical evidence for a PR run is the GitHub Actions artifact named **cognous-open-control-stack-reference-evidence**.

Inside the artifact:

- `component-pins.json` — checked-out SHAs observed by the runner.
- `scenario-results.json` — final release-gate state, per-scenario matrix results, two representative runs, optional-layer state and compatibility disclosures.
- `scenario-matrix-results.json` — each acceptance scenario resolved to actual collected JUnit test identifiers in run 1 and run 2, with passed/failed/skipped/missing/unexecuted status.
- `skip-accounting.json` — every collected pytest skip with its upstream reason and whether it is required coverage.
- `representative-repeatability.json` — normalized comparison of the two isolated transported workflows; generated IDs/timestamps are intentionally excluded.
- `run-1/representative/*` and `run-2/representative/*` — transport evidence, retained recipient outcome, Replay reconstruction, Governance Evidence Pack, ODES, IMX successor, expected-versus-observed assertion result and the independent SQLite stores for each run.
- `run-1/*.xml`, `run-2/*.xml` — JUnit evidence used by the acceptance-matrix resolver, including `control_plane_store.xml` for repaired shared-store persistence.
- `run-N/control-plane-store-evidence/*.json` — upstream spawned-process persistence evidence for concurrent writes/readers and before/after-replacement termination.
- `run-1/*.log`, `run-2/*.log` — raw component/adapter test output.
- `openshell-mock.log` and `openshell-mock.xml` — mocked OpenShell adapter qualification only.
- `artifact-index.json` — SHA-256 and byte size for generated evidence files.

`scenario-results.json` records `dependency_status`, the exact lock, historical test-only pins,
per-repetition test totals, `candidate_qualification_passed` and `release_qualified`.
An unmerged Alvorada candidate always leaves `release_qualified=false`.
`run-N/gax-observation-results.json` records actual effect/artifact identities and
recovery state; `run-N/research-qualification/` retains the six absence probes
and the characterized equivalent-intent duplicate.

A green workflow means the enforced representative assertions, required scenario coverage, two-run repeatability comparison and pinned suites passed. It does not establish production deployment, field efficacy, human-review effort, live sandbox confinement or independent real-world verification.

## Transported representative evidence

The evidence-producing reference operation is queued and delivered through `LocalDurableTransport`. `AcceptedGaxRecipientAdapter` performs the accepted recipient assessment and invokes the pinned GAX/Control Plane/executor path. The runner then reads the retained workflow association for that exact governed message and consumes original artifacts through the public retained-artifact API.

A separate direct `run_exchange()` execution is not used as evidence for the transported operation.

The enforced representative gate asserts:

- exactly one destination effect;
- the destination effect ID equals the retained workflow/transport identity;
- target, amount, unit, payload and grant match the authorized operation;
- destination state is `applied`;
- `newly_executed=true` and `unresolved_delivery=false`;
- decision/effect/executor-attempt identity remains consistent through transport, Replay and ODES;
- required Replay, Governance Evidence Pack, ODES and IMX artifacts exist.

## Acceptance-matrix semantics

`scenarios/acceptance-matrix.json` is executable input, not narrative documentation. Every required test reference must resolve to actual collected JUnit cases and pass in both isolated repetitions. Parameterized references resolve to all collected parameter instances.

A missing required reference, required skip, failure or unexecuted required scenario makes the release gate fail. Optional upstream skips are retained in `skip-accounting.json` with their original pytest reason.

The matrix includes pinned transport-integration coverage from `test_governed_message_transport_integration.py`, in addition to component and transport-adapter suites.

## Historical committed representative snapshots

Files under `examples/reference-release/` and `examples/batch4c/` are historical snapshots, not current qualification. Their original provenance is preserved. The candidate snapshot under `examples/batch4c-integration/` is also historical.
`examples/batch4c-accepted/` preserves the earlier accepted observation-validation
run. `examples/worker14d-recovery/` and its archive also precede persistence adoption.
The current summary links the verified CI artifact; use the table above.

## Historical corrected gate result

Corrected CI run `37462562745` at head `0d672092...` passed all 18 required scenarios in both repetitions. `skip-accounting.json` contains zero skips. The 11 unique skips seen in the earlier baseline were integration-fixture wiring gaps, not accepted optional coverage: seven Replay pinned-producer tests were enabled by the ARB producer roots, three lost-ack Evidence Pack/ODES tests were enabled by the pinned Replay lost-ack fixture, and the remaining accepted-GAX Evidence Pack import was enabled by the pinned GAX, Control Plane and Moltbot roots.

At that historical revision, the transport interface did not expose the original GAX-produced Replay artifact. The evidence artifact therefore preserves the original producer Replay ID separately from the regenerated Replay ID. The regenerated Replay is derived only from retained Control Plane/executor records, and its ID/digest is enforced through Governance Evidence Pack and ODES; it is never relabeled as the original bundle.
