# Developer quickstart

**Read [Start here](start-here.md) first.** The example checkout below reproduces an **earlier pinned documentation checkpoint** at `5737267d94d2b445735c95e8480a31de73a2abe8`; it is not a test of the current `main` release. For current selection and claims, independently inspect [component-lock.json](../component-lock.json) and [release status](release-status.md). Do not mix test counts, source pins or optional profiles across checkpoint generations.

Use a disposable local checkout for the bounded synthetic refund workflow.
The reference CI uses Ubuntu, Python 3.11 and Node 20. For the closest reproduction,
use Linux with Git, Python 3.11 (including `venv` and `pip`), Node 20 and npm.
Python 3.12 was also used in the recorded local qualification; other platforms or
newer versions are not qualified by this documentation audit.

Network access must allow GitHub clones and Python/npm package downloads. The
runner installs dependencies and the `agep` CLI into the active Python environment,
so activate a virtual environment and keep its `bin` directory on `PATH`.
No production credentials, Docker or OpenShell installation is required for the
default mocked-adapter reference run.

```bash
git clone https://github.com/cogno-us/cognous-open-control-stack.git
cd cognous-open-control-stack
# Reproduce the accepted baseline described by this documentation:
git checkout 5737267d94d2b445735c95e8480a31de73a2abe8
python3.11 -m venv .venv
source .venv/bin/activate
python tools/reference_release.py --help
python tools/reference_release.py run --results-dir results/reference
```

The runner checks out exact component SHAs, including separately pinned historical
test dependencies, then executes two isolated repetitions, negative/recovery suites
and separate mocked OpenShell tests. Allow time for clones and dependency installs.
It does not deploy services, write to a public chain or provision infrastructure.

**Local write behavior:** the runner deletes/recreates the specified results
directory. Without `--reuse-checkouts`, it also replaces `.reference-work/`.
Choose a new results path to preserve a prior run and do not keep personal changes
in runner-owned checkouts. `--reuse-checkouts` requires exact locked HEADs and clean
tracked files; it is not a way to substitute newer component versions.

## Read the result

Start with `results/reference/scenario-results.json`: inspect `release_qualified`,
actual pins, test totals and each required scenario. Then inspect
`scenario-matrix-results.json`, `representative-repeatability.json`,
`skip-accounting.json` and `artifact-index.json`. The [evidence index](evidence-index.md)
explains the retained artifacts and CI download names. A command returning before
setup completes is not a passing qualification.

Separate same-host qualification has its own runner and baseline:
[Worker 16 command and scope](workstreams/process-boundary-checkpoint.md#evidence-and-command).
It does not qualify shared-store concurrency at the selected Control Plane pin.
Live OpenShell is a separate, unqualified deployment boundary; see
[support status](release-status.md) before interpreting optional live commands.

## Documentation verification

The [public README/collateral checkpoint](workstreams/public-readmes-collateral-checkpoint.md)
records this update's link, shell-syntax, CLI/example and available component checks.
The full reference and protected-worker campaigns were not rerun for prose changes;
accepted executed evidence remains linked above at its original sources and environment.
