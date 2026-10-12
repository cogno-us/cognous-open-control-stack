# PV-FINAL-RUN — independent selected-lock clean-room reproduction

**Date:** 2026-10-10  
**Issue:** [#85](https://github.com/cogno-us/cognous-open-control-stack/issues/85)  
**Frozen reviewed hub source:** `62c93784f34f6ad0a3f63a5efac04a948e826ae1` (PR #84 integrated draft)  
**Result:** **BLOCKED — no independent selected-lock execution performed.**  
**Operational trust:** [#30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30) **HOLD**.

## Method and observed environment

A direct attempt was made from the available Linux execution environment to reach GitHub for a disposable clone. Preflight commands were:

```sh
pwd
python3 --version
node --version
git --version
git ls-remote https://github.com/cogno-us/cognous-open-control-stack.git HEAD
uname -srm
command -v python3.11
command -v npm
npm --version
getent hosts github.com
```

Observed: working directory `/`; Python `3.13.5`; Node `v22.16.0`; Git `2.47.3`; Linux `6.18.44 x86_64`; npm `10.9.2`; `python3.11` absent from PATH; `getent hosts github.com` returned no address. The `git ls-remote` attempt exited **128** with `fatal: unable to access 'https://github.com/cogno-us/cognous-open-control-stack.git/': Could not resolve host: github.com`. The command did not obtain a remote ref, clone a checkout, or run any test. No credentials were used.

As a read-only fallback, the connected GitHub repository interface returned issue #85, PR #84, frozen commit metadata, and exact-ref content for `README.md`, `component-lock.json`, `docs/release-status.md`, `docs/quickstart.md`, `docs/architecture.md`, and `tools/reference_release.py`. The frozen commit metadata identifies the integration of the prior PV-ARTIFACT report. Top-level `AGENTS.md`, `CONTRACTS.md`, `development/README.md`, and `.github/copilot-instructions.md` returned not-found at that ref; this is **not** a complete recursive search for repository instructions. None of the GitHub-interface content was executed locally.

## Exact selection and reproduction boundary

The user-specified PR #84 candidate is exactly `62c93784f34f6ad0a3f63a5efac04a948e826ae1`, **not** necessarily the current `origin/main`. The frozen selected `component-lock.json` fetched through the GitHub interface has Git **blob SHA** `b3bf15918ec7eaccd10c486b61926351d392dd04`; this is *not* a locally recomputed SHA-256 content digest. The prior PV-ARTIFACT report gives content SHA-256 `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`, **document-derived, not recomputed here**.

The quickstart requires disposable Linux with Python 3.11, Node 20, GitHub/package-registry access, a fresh results path, and exact selected pins. A suitable independent reproduction would use:

```sh
git clone https://github.com/cogno-us/cognous-open-control-stack.git cognous-pv-final
cd cognous-pv-final
git checkout --detach 62c93784f34f6ad0a3f63a5efac04a948e826ae1
git rev-parse HEAD
sha256sum component-lock.json
python3.11 --version
node --version
npm --version
uname -a
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip --version
python tools/reference_release.py run --results-dir results/pv-final-85
```

**These reproduction commands are proposed, NOT executed in this run.** The fetched runner source indicates that it clones exact selected and historical dependency pins, installs pip/npm dependencies, uses two isolated repetitions, and emits suite/matrix/representative evidence. Its default path must not be conflated with an explicitly selected candidate `--profile` or `--batch` invocation. The runner refuses a nonempty results directory and ordinarily replaces `.reference-work`; disposable-checkout isolation is mandatory.

## Evidence status: verified here versus previously reported

| Acceptance item | Independent result for issue #85 |
| --- | --- |
| Frozen source identity | Exact commit exists via GitHub commit API; no local HEAD available |
| Exact selected component pins | Lock content read from frozen ref; no local pinned component clones or checkout SHA verification |
| Local SHA-256 of original lock bytes | **Unavailable**; prior report gives an unverified-in-this-run digest |
| Python 3.11 / Node 20 runner | **Unavailable**; host has Python 3.13 / Node 22 |
| Dependency installation and fresh full reference runner | **Not run**; DNS blocks clone |
| Both isolated repetitions and negative/denial tests | **Not run or independently inspected for a new execution** |
| Scenario matrix / required-case qualification | **No new matrix** |
| Repeatability, JUnit XML, skip accounting, expected-vs-observed JSON | **No new generated files** |
| Synthetic SQLite effects, attempts, events for allow/deny/timeout/unknown | **No new SQLite files**; no fresh read-only destination inspection |
| CI run URL or evidence archive for fresh issue #85 reproduction | **None**, because no run was executed |
| Prior PR #82 artifact inspection | Separately reported, not substituted for the required fresh run |

The integrated prior [PV-ARTIFACT report](../workstreams/pv-artifact-evidence-inspection-2026-10-10.md) reports selected candidate **35 scenarios (34 passed, one characterized)** from historical selected evidence, and newer preview evidence with two repetitions of **1014 passed**. Those numbers and its archived SQLite assertions are **prior-worker findings**, not independently reproduced or recomputed by PV-FINAL-RUN. The characterized business-intent equivalence case is not duplicate prevention. Optional C1's **73** previously reported tests and historical **915** tests are separate populations; neither is added to this run. No new test count exists.

## Decision and residual limitations

**BLOCKED, not PASS and not FAIL of the underlying software.** A network-enabled disposable Linux runner with Python 3.11, Node 20 and package registry reachability is needed to execute the command above, capture the local SHA-256 and exact dependency SHAs, preserve raw output, independently inspect both repetitions and SQLite state for positive/negative/timeout/unknown cases, and link the generated archive. Until then no independent clean-room reproduction claim is justified.

Preserved boundaries: C0 is effect-time revalidation with a residual check-to-destination-commit race, **not** destination-commit atomicity. C1 is optional cooperating **same-host** SQLite and not the default-selected end-to-end profile. No C2/C3, remote exactly-once, business-intent deduplication, real settlement, production credentials, institutional adoption, independent operational verification or production release claims. Operational trust #30 remains **HOLD**.

This report is the only path added by this worker. No changes to PR #84, `component-lock.json`, runtime, institutional authority, production effects, credentials, release permissions or historical artifacts. No merge performed.
