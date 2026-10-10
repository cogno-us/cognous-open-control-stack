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

## Current selected lock: clean-checkout verification (PV-3)

This is a **separate, current-selected procedure**. Do not use the historical
`5737267d94d2b445735c95e8480a31de73a2abe8` checkout above to claim
current `main` qualification. Record the exact hub HEAD and SHA-256 of its
unmodified `component-lock.json` before running. Run only in a disposable Linux
checkout with GitHub and package-registry access, Python 3.11 and Node 20.

```bash
git clone https://github.com/cogno-us/cognous-open-control-stack.git cognous-pv3
cd cognous-pv3
git switch --detach origin/main
git rev-parse HEAD | tee pv3-hub-head.txt
sha256sum component-lock.json | tee pv3-component-lock.sha256
python3.11 --version
node --version
npm --version
uname -a
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip --version
python tools/reference_release.py run --results-dir results/pv3-selected
```

The runner deletes/recreates `results/pv3-selected` and, unless checkout reuse
is explicitly selected, `.reference-work/`. Verify the checked-out component
SHAs against `results/pv3-selected/scenario-results.json` and the original
lock. Inspect the generated `artifact-index.json`, JUnit XML, suite logs,
`scenario-matrix-results.json`, `representative-repeatability.json`,
`skip-accounting.json` and each repetition's
`representative/expected-vs-observed.json`. Preserve the exact commands,
OS/tool versions, hub SHA, lock digest, runner results and CI/artifact URLs.
The selected runner reports the pinned sources used; historical dependency pins
are not interchangeable with selected producer pins.

**Evidence decision:** record `PASS` only when an executed selected-lock run
qualifies all required gates *and* its underlying evidence is inspected.
A missing clone, dependency, artifact, destination-state assertion or required
test is `BLOCKED` or `FAIL`, never inferred `PASS` from a workflow badge.
For the synthetic refund, inspect the direct SQLite destination state and
separate allowed/denied attempts, timeout or unknown acknowledgement, effect-ID
deduplication and the business-intent duplicate limitation. The default
bounded integration does **not** activate logical refund-intent deduplication.
Describe mocked/fixture checks separately from actual pinned producer runs;
none of these exercises establishes real payment-processor behavior.

The October 10, 2026 issue [PV-3 (#69)](https://github.com/cogno-us/cognous-open-control-stack/issues/69)
records completed-success CI at preview head
`e4bc5092e2b0d6544ace33b9615d2830f4b8f3fe`: [reference evidence](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38069611285),
[full candidate](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38069611359),
and [merged candidate](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38069611361).
Those are **CI run conclusions**, not independent clean-checkout verification
or inspected artifact-content/destination-state proof in this PV-3 workstream.
The independent run remains **BLOCKED** pending network-enabled reproduction
and artifact qualification. Operational trust [#30](https://github.com/cogno-us/cognous-open-control-stack/issues/30)
remains **HOLD**. C0 revalidation is not destination-commit atomicity;
optional same-host C1 does not establish cross-host C2/C3 guarantees.

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
