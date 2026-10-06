# Quickstart

Requirements: Git, Python 3.11+, Node 20+ for the Index local reference tests, and network access to clone the pinned public repositories.

Run exactly:

```bash
python tools/reference_release.py run --results-dir results/reference
```

The runner verifies every checkout SHA, executes the bounded integration and component suites twice in isolated result directories, runs mocked OpenShell qualification separately, and writes `results/reference/artifact-index.json`.

The command never deploys services, writes to a public chain, provisions paid infrastructure or uses production credentials.

Live OpenShell remains opt-in and unexecuted by default. The generated result records the exact command needed when authorized infrastructure already exists.

Review `docs/evidence-index.md` for interpretation rules and `docs/compatibility.md` for the exact producer/consumer pins.
