# Worker 16 — same-host process-boundary qualification checkpoint

## Baseline and scope

Starting hub commit: `b457b7e1ebcbb323e88e85b913eaafcb5755317a`.
Current `main` was identical when this branch was created. The qualification reads `component-lock.json` at that baseline and checks out the accepted pins exactly. It does not consume PR #6 or any unaccepted recovery branch.

Owned qualification surfaces:

- `tests/test_process_boundary_qualification.py`
- `tools/process_boundary_qualification.py`
- `scenarios/process-boundary-matrix.json`
- `docs/workstreams/process-boundary-checkpoint.md`
- `examples/process-boundary/`
- dedicated CI workflow only for this qualification

The harness uses spawn-based OS processes, explicit events/pipes, bounded waits, independently initialized runtime objects/database connections, the public pinned Control Plane/executor interfaces, and Moltbot Safe's real SQLite destination. Fault hooks only pause immediately before the real destination commit or terminate immediately after it; they do not supply authorization, locking, deduplication or reconciliation.

## Store boundaries

The destination implementation serializes duplicate suppression, exact operation binding and cumulative grant-effect counting through SQLite `BEGIN IMMEDIATE`. This is a same-host shared-database property only.

The duplicate-operation and competing-effect scenarios intentionally give each process an **independent Control Plane JSON store** while both processes share one SQLite destination. Their destination-concurrency result therefore does not depend on concurrent writes to one `BoundedRecordStore`.

The recovery scenarios retain one original Control Plane JSON store across process termination/restart, but do not perform concurrent writers against it.

The shared-store scenario is the only experiment in this workstream where separate processes concurrently append to the **same** public `BoundedRecordStore` JSON file.

## Reviewed qualification evidence

Initial PR #7 head `0f2cbb0fa3d8b602e7c76272ede8265f3f1d1ccf` ran in GitHub Actions run `37562129469` and completed successfully.

Both repetitions reported:

- 5 tests;
- 5 passed;
- 0 failures;
- 0 errors;
- 0 skipped.

Across the two repetitions, evidence classifications were 8 `supported invariant passed` and 2 `unsupported boundary characterized`.

Those results are preserved as the initial process-boundary evidence. The later gate correction does not reinterpret them.

### Destination concurrency

The initial evidence showed one committed effect for duplicate delivery of the same authorized operation and one committed effect when two distinct valid operations competed under the same one-effect grant. These cases used independent Control Plane stores per process and a shared real SQLite destination.

### Process termination

The initial evidence showed:

- after destination commit/process termination, restart observed the original applied effect and did not create a replacement destination effect;
- before commit/process termination, a destination attempt existed without an effect, and restart denied a replacement dispatch after observing absence.

The corrected assertions now additionally require original Control Plane attempt persistence, original decision/effect identity, accepted reconciliation semantics, unchanged destination dispatch history, and non-rewriting of the interrupted attempt by a later reconciliation acknowledgement.

### Shared Control Plane JSON store: observed result

Observed behavior and implementation support are separate conclusions.

**Observed result:** both repetitions demonstrated lost concurrent records when two processes appended to the same `BoundedRecordStore`. In run 1, all four paired decision rounds and all four paired attempt rounds lost one side. Reconciliation rounds also lost records; at least one reconciliation round exhibited a silent lost update where both worker calls returned without an exception but only one token remained. Run 2 again showed lost records across the paired decision, attempt and reconciliation writes. Many losing writers raised `FileNotFoundError` around the shared fixed temporary path.

**Support conclusion:** independently of those observed failures, the public implementation exposes only a process-local `threading.RLock` plus a fixed `.tmp`/`os.replace` JSON write sequence. It exposes no interprocess lock or transactional append contract. Concurrent multi-process use is therefore classified `unsupported boundary characterized`; the observed lost records are evidence of failure within that unsupported boundary, not the sole basis for calling it unsupported.

No SQLite destination serialization guarantee is inferred to protect this JSON store.

## Matrix gate correction

The qualification runner now reads `scenarios/process-boundary-matrix.json`. For every required scenario in each repetition it requires:

- exactly one matching JUnit testcase;
- a passed, non-skipped JUnit result;
- matching scenario evidence for that repetition;
- the exact required scenario identity; and
- evidence classification `supported invariant passed`.

A missing test, skipped/failed required test, missing or malformed evidence, repetition/identity mismatch, or failed required classification makes the qualification exit nonzero. A regression test proves a missing required scenario cannot pass the matrix gate.

Required scenario evidence is classified as passed only after all scenario assertions, including exact content binding and recovery-history assertions, have been evaluated. If an assertion predicate fails, failure evidence is written as `required invariant failed` before the test fails.

## Evidence and command

Run:

```bash
python tools/process_boundary_qualification.py run --results-dir results/process-boundary
```

The runner executes two isolated repetitions, writes JUnit, per-scenario JSON and per-repetition `matrix-gate.json`, then aggregates `results/process-boundary/summary.json`. Required matrix failure produces a nonzero exit even if aggregate pytest execution alone would otherwise appear successful.

CI evidence entry point: the `process-boundary-qualification` artifact, with `summary.json` at its root.

## Explicit limits

These tests do not establish distributed budgets, remote exactly-once delivery, authenticated observations, destination finality, production institutional authentication, live confinement, or recovery under changed authority.

## Proposed later integration

After review, the Governor may add references to this qualification from the shared release runner, acceptance matrix, evidence index/release status and residual-risk register. This branch intentionally does not modify those shared surfaces or `component-lock.json`.
