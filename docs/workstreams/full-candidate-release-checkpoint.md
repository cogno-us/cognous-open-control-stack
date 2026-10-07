# Full merged-chain release candidate

Baseline: hub `147b952c3fff593c732d8bac7654ad904e80ff40` (accepted PR #22). The smaller merged-chain qualification passed on Linux Python 3.11/3.12. Its upstream component revisions are accepted merges; the default hub release lock has not advanced.

This change introduces [a complete candidate lock](../../profiles/full-release-candidate.json) and explicit `--profile` / `--batch` options for the reference runner. Four independent Linux jobs cover authority, exchange, consumers and registry. Every existing suite retains two repetitions. The unchanged acceptance matrix is resolved only after all four complete reports are present and agree on the candidate profile digest. Missing batches, repetitions, required JUnit evidence, OpenShell mock results, Index chain runs or static optional-package checks block aggregation.

Historical compatibility tests retain their original producer combinations. The newer Replay, Evidence Pack and ODES implementations additionally run their exact merged-producer qualification suites. Existing GAX artifact assertions use the accepted merged-profile qualification file. The default accepted release invocation remains available.

Each child command has a four-minute process-group timeout; each batch has an eighteen-minute job limit. Candidate batches omit redundant diagnostic preflights: the same complete suites still execute twice as required by the release gate. Existing evidence directories are not overwritten. Logs, JUnit, scenarios and per-batch reports are retained in CI artifacts.

Local validation: aggregate-gate and transported-release-gate tests run against the merged dependencies. Full matrix CI results are recorded in the PR; no execution is inferred from these local checks.

The accepted `component-lock.json` is unchanged. A green aggregate proves the scoped candidate matrix, not production readiness or atomic/refund-intent profile composition. The selected workflow remains the bounded producer path. Actual identity separation, remote authority propagation, destination deployment qualification and independent operational review remain outside this synthetic reference.
