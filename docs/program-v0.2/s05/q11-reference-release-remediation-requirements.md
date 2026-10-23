# Q11: reference-release runner remediation, Hub coordination record and requirements

**Non-authorizing record. Release, publication and production remain on HOLD.** Nothing here claims clearance, certification, qualification or readiness. This is a Hub-side coordination record: it states requirements and requests. The Hub does not direct or modify independent oracles or verdicts, and nothing here is posted to the Qualification repository.

Rulings applied: architect Q1-Q4 ([disposition record](architect-disposition-q1-q17.md)). The full original report text is not on disk; this record is reconstructed from the evidence index (`COMMANDS.txt`, `workflow-runs-all.tsv`, `main-runs-qualref.txt`, `upstream-checks.txt`, and the CI-equivalent logs). Items marked "reported" come from the diagnostic attempts and were not re-verified when writing this record.

## 1. Classification

- Hub orchestration gap: the Hub's reference-release workflow no longer produces a passing run.
- The runner (the reusable workflow and `reference_release.py` overlay) is owned by the Qualification repository. The fix belongs there, under Qualification's own independent review (Q1).
- Historical failing runs are preserved as evidence and are not re-run, edited or hidden.

## 2. Exact evidence

| Fact | Evidence |
|---|---|
| Last success on main | Run 804, push, `bf77ce8` (#165), 2026-10-19, with Qualification ref `78b3f42` |
| Failure series | Every main run from 816 (`ddb5c95`) through 983 (`4bb81cf`) in `main-runs-qualref.txt` is failure, all with Qualification ref `2bb5f10`; the index lists 41 failing main runs after 804 (816 to 983) |
| Probable trigger (not proven) | Component-lock bump `4d88010` "Update the component lock to current mains and add the verifier", merged as #166 (`ddb5c95`). The first failing main run (816) follows it, and the index shows no main runs between 804 and 816 |
| Runs reproduced | Hub `4bb81cf09c67cb90caba76e24f34604f84650997` (run 983) and `c6ef5315b6ce3d52c17588397165f9473673c60d` (run 980), both the failing tip of main at their time |
| Reproduction | `COMMANDS.txt`: clone Hub at the revision; clone Qualification at `2bb5f10d5d24df27cbf8bfeec0f91bf004c2505d`; `install_suite.py` overlay (76 files); clean Python 3.11 venv; `GITHUB_ACTIONS=true venv-ci/bin/python tools/reference_release.py run --results-dir results/reference` |
| Failure | `RuntimeError: focused Replay/ODES preflight failed; see preflight logs` (runner exit 1) |
| ODES preflight | 1 failed, 3092 passed, 1 skipped: `test_evaluation_never_imports_replay_and_works_where_it_cannot_be_imported`; the `-I` subprocess raised `ModuleNotFoundError: No module named 'odes'` |
| Replay preflight | 32 failed, 1220 passed, 12 skipped, 8 xfailed (4bb81cf run); `-I` subprocesses raised `ModuleNotFoundError: No module named 'agent_replay_bundle'` |
| Pinned component tuple | From `component-lock.json`: replay_bundle `028f63d1c001f99580583888fa4b4e46d77a267b`, odes `e86a25a1d660e74533337d38744e2934200a50ae`, control_plane `0a41faa972699f7ec3063967a14cd9bdd3e67d27`, moltbot_safe `ec728da6dc301a664b331ac8986afd6e850a1273` |
| Upstream component checks | `upstream-checks.txt`: component-local and cross-component checks success for replay-bundle `028f63d` and `2a7963b` and for ODES `e86a25a` and `4bf1212`; the failure is in the Hub runner path, not in those upstream checks |

## 3. Why the `-I` failures occur (inference)

This section is an inference from the diagnostic attempts, not a verified root cause. Distinguishing fact: the non-editable install (`_attempt2-noneditable`) still left 1 ODES and 1 Replay preflight failure, while the editable installs (`_attempt3-editable-pyc`, `_attempt4-sitecustomize-failed`, `fix-B`) gave 0 preflight failures.

The preflight runs the component suites with the runner's venv. Tests that start `python -I` subprocesses cannot see the runner's checkout paths or `PYTHONPATH`, and the distributions were not installed into that environment from the exact pinned checkouts. This is a packaging gap in the test environment, not a defect to hide by weakening isolation (Q4).

## 4. Further items behind the preflight failure (reported)

Diagnostic attempts under `attempts/` (non-CI, diagnostic only) reached further stages once the preflight was bypassed or the packages installed (`pip install --no-deps --no-build-isolation -e` of the replay and ODES checkouts, then `--reuse-checkouts` after `git clean -fdx`). They indicate these further items, which Qualification may confirm or refute:

1. Editable install from the exact pinned checkout is needed (an installed, not path-injected, distribution), and then the checkouts must be clean.
2. Bytecode pollution: stale `__pycache__`/`.pyc` in reused checkouts can alter results; checkouts should be cleaned or bytecode disabled for the preflight.
3. Relocated test paths: tests resolve paths relative to the original checkout location and fail when the overlay or checkouts sit elsewhere.
4. Qualification pin mismatch: `reference-release.yml` pins Qualification `2bb5f10`, while the last-success run 804 used `78b3f42`. Other Hub workflows pin other SHAs (for example `78b3f42`, `47f28db`, `4a57a30`, `2bb5f10`), and `component-lock.json` carries no Qualification pin, so there is no single tuple to compare against. Whether `2bb5f10` is stale is for Qualification and the reviewed re-pin PR to settle.
5. GAX `runtime_authority_profile`: the security-runtime profile now requires a trusted `runtime_authority_profile`; the representative and research-qualification stages in the fix-B attempt raised `ValueError: security-runtime profile requires trusted runtime_authority_profile`. Synthetic fixtures must explicitly opt into test time. The fix-B attempt still ended with `release_gate_passed: false`.

## 5. Integration behavior requirements requested from Qualification

Phrased as requests and requirements for Qualification's own decision, review and verdict.

| # | Requirement | Basis |
|---|---|---|
| R1 | Release evidence is produced in explicit, versioned profile mode; default mode is retired from normative use | Q2 |
| R2 | Historical default-mode invocations remain reproducible and are not silently reinterpreted; if removal would break supported consumers, deprecate first and version the interface | Q2 |
| R3 | A declared deterministic synthetic-clock profile is used only for reproducible synthetic tests and never to establish real-time freshness | Q3 |
| R4 | Fixtures whose freshness assumptions are invalid are regenerated, preserving predecessors and their hashes; real freshness assertions use an independently justified clock and source timestamp | Q3 |
| R5 | Qualification accepts (or rejects) the replacement fixtures through its own process | Q3 |
| R6 | The runner installs the exact pinned distributions properly (from the exact pinned checkouts) in the test environment, with clean checkouts | Q4 |
| R7 | Python isolation (`-I`) is not weakened to hide a packaging error; Replay/ODES owners may separately propose installation-independent `-I` tests (optional hardening, not a prerequisite) | Q4 |
| R8 | The runner supplies the trusted `runtime_authority_profile` for the security-runtime profile and opts synthetic fixtures into test time explicitly | Evidence 4.5 |
| R9 | The Qualification revision referenced by `reference-release.yml` (`2bb5f10`; last success used `78b3f42`) and the other differing Hub workflow pins are reconciled by a reviewed change; the component lock carries no Qualification pin | Evidence 4.4 |

Source tuple requested: Hub `4bb81cf09c67cb90caba76e24f34604f84650997` (or the current main at request time) with `component-lock.json` as listed in section 2.

## 6. Requested priority

High for Qualification's queue because every Hub main run since 816 fails, which blocks release-evidence runs. The priority is a request; Qualification sets its own schedule.

## 7. Sequence

1. Qualification fixes the runner in its repository under its own independent review (Q1).
2. The repaired runner passes against the exact candidate; Qualification requalifies it.
3. The Hub re-pins through a separate reviewed PR. No Hub pin change is made before then.
4. Historical failing runs stay as they are.

The Hub does not edit Qualification's runner, oracles, expectations or verdicts, and posts nothing to Qualification issue trackers from this record.
