# Process-boundary qualification evidence

This directory is the documentation entry point for Worker 16's same-host process qualification. Runtime evidence is generated rather than committed:

```bash
python tools/process_boundary_qualification.py run --results-dir results/process-boundary
```

The generated root `summary.json` points to two repetition directories. Each contains JUnit, the pytest log, and machine-readable scenario evidence recording process IDs, barriers, exit codes, exact pins, store paths, identities, destination rows and retained record histories.

Results are limited to separate OS processes on one host sharing the same local SQLite destination file. They do not establish distributed or remote guarantees.
