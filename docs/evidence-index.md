# Evidence index

The canonical evidence for a PR run is the GitHub Actions artifact named **cognous-open-control-stack-reference-evidence**.

Inside the artifact:

- `component-pins.json` — checked-out SHAs observed by the runner.
- `scenario-results.json` — environment, two-run suite outcomes, OpenShell scope, optional-layer checks and known compatibility condition.
- `run-1/*.log`, `run-2/*.log` — raw test output from independent executions.
- `openshell-mock.log` — mocked OpenShell adapter test output.
- `artifact-index.json` — SHA-256 and byte size for generated evidence files.

A green workflow means the listed test commands passed at the pinned revisions; it does not establish production deployment, field efficacy, human-review effort, live sandbox confinement or independent real-world verification.

## Acceptance-matrix coverage

The GAX reference/redelivery suite covers valid refund execution, missing authority, binding substitutions, post-decision revocation, REPORT/REFUSE/NOT_UNDERSTOOD no-effect behavior, duplicate delivery, lost acknowledgement, restart, post-commit interruption, evidence-export retry, partial delivery, lineage divergence and digest tampering. The Control Plane suite supplies T1/T2 approval and authority freshness cases. Replay/Evidence/ODES suites cover reconstruction, import and recipient evidence semantics. BitRep verification and The Index local-chain suites are kept distinct from action authorization.

Any scenario absent from executable component coverage is recorded as unavailable rather than fabricated.
