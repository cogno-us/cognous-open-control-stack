# Evidence index

The canonical evidence for a PR run is the GitHub Actions artifact named **cognous-open-control-stack-reference-evidence**.

Inside the artifact:

- `component-pins.json` — checked-out SHAs observed by the runner.
- `scenario-results.json` — final release-gate state, per-scenario matrix results, two representative runs, optional-layer state and compatibility disclosures.
- `scenario-matrix-results.json` — each acceptance scenario resolved to actual collected JUnit test identifiers in run 1 and run 2, with passed/failed/skipped/missing/unexecuted status.
- `skip-accounting.json` — every collected pytest skip with its upstream reason and whether it is required coverage.
- `representative-repeatability.json` — normalized comparison of the two isolated transported workflows; generated IDs/timestamps are intentionally excluded.
- `run-1/representative/*` and `run-2/representative/*` — transport evidence, retained recipient outcome, Replay reconstruction, Governance Evidence Pack, ODES, IMX successor, expected-versus-observed assertion result and the independent SQLite stores for each run.
- `run-1/*.xml`, `run-2/*.xml` — JUnit evidence used by the acceptance-matrix resolver.
- `run-1/*.log`, `run-2/*.log` — raw component/adapter test output.
- `openshell-mock.log` and `openshell-mock.xml` — mocked OpenShell adapter qualification only.
- `artifact-index.json` — SHA-256 and byte size for generated evidence files.

A green workflow means the enforced representative assertions, required scenario coverage, two-run repeatability comparison and pinned suites passed. It does not establish production deployment, field efficacy, human-review effort, live sandbox confinement or independent real-world verification.

## Transported representative evidence

The evidence-producing reference operation is queued and delivered through `LocalDurableTransport`. `AcceptedGaxRecipientAdapter` performs the accepted recipient assessment and invokes the pinned GAX/Control Plane/executor path. The runner then reads the retained workflow association for that exact governed message and reconstructs downstream evidence from those retained records.

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

## Committed representative snapshots

The committed files under `examples/reference-release/` are reviewer conveniences and are regenerated from a successful corrected CI artifact. Their manifest records the source workflow/artifact digest. The complete CI artifact remains authoritative.

## Corrected gate result

Corrected CI run `37462562745` at head `0d672092...` passed all 18 required scenarios in both repetitions. `skip-accounting.json` contains zero skips. The 11 unique skips seen in the earlier baseline were integration-fixture wiring gaps, not accepted optional coverage: seven Replay pinned-producer tests were enabled by the ARB producer roots, three lost-ack Evidence Pack/ODES tests were enabled by the pinned Replay lost-ack fixture, and the remaining accepted-GAX Evidence Pack import was enabled by the pinned GAX, Control Plane and Moltbot roots.

The transport interface does not expose the original GAX-produced Replay artifact. The evidence artifact therefore preserves the original producer Replay ID separately from the regenerated Replay ID. The regenerated Replay is derived only from retained Control Plane/executor records, and its ID/digest is enforced through Governance Evidence Pack and ODES; it is never relabeled as the original bundle.
