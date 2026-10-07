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

## Expected qualification boundaries

The destination implementation is expected to serialize duplicate suppression, exact operation binding and cumulative grant-effect counting through SQLite `BEGIN IMMEDIATE`. That is a host-local shared-database property only.

The public Control Plane `BoundedRecordStore` is a JSON file store guarded by `threading.RLock` and a fixed `.tmp`/`os.replace` write sequence. The qualification therefore exercises it separately across processes. No result from the SQLite destination is treated as evidence that the JSON Control Plane store is process-safe.

## Evidence and command

Run:

```bash
python tools/process_boundary_qualification.py run --results-dir results/process-boundary
```

The runner executes two isolated repetitions, writes JUnit plus per-scenario JSON, aggregates `results/process-boundary/summary.json`, and exits nonzero if any required invariant test fails.

CI evidence entry point: the `process-boundary-qualification` artifact, with `summary.json` at its root.

## Findings

Pending first branch-head CI execution. This checkpoint must be updated with observed classifications, exact totals, final SHA and CI state before handoff. Unsafe or unsupported outcomes will remain visible; they will not be converted into passing claims.

## Explicit limits

These tests do not establish distributed budgets, remote exactly-once delivery, authenticated observations, destination finality, production institutional authentication, live confinement, or recovery under changed authority.

## Proposed later integration

After review, the Governor may add references to this qualification from the shared release runner, acceptance matrix, evidence index/release status and residual-risk register. This branch intentionally does not modify those shared surfaces or `component-lock.json`.
