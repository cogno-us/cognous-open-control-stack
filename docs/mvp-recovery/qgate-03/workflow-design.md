# QGATE-03 workflow design (OCS-MVP-QGATE-03, Worker D)

Status: prepared, NOT executed. Non-authorizing. This is a platform host feasibility observation of GitHub-hosted ubuntu-24.04 with a synthetic ingress. It is not qualification, certification, a host designation, or a refund battery, and it changes no standing hold.

Workflow: `.github/workflows/qgate-03-host-integration.yml`. It calls only `.github/qgate-03/run_integration.sh REPO_ROOT CP_ROOT RT_ROOT EVDIR` (Worker B), which may call `diagnostics.sh` (Worker C).

## Trigger rationale
- `push: tags: ['qgate-03-run-1']` is the only trigger. No branches, paths, pull_request, workflow_dispatch or schedule, so routine PR/branch pushes cannot execute it (QGATE-02's branch+paths trigger re-executed on later pushes to its files).
- Job guard: `github.run_attempt == 1 && github.ref == 'refs/tags/qgate-03-run-1'`.
- The hub is checked out at the tagged commit; the tag therefore pins exactly what runs.

## Preventing repeat execution
1. A tag name already on the remote cannot be pushed again without deleting it first.
2. `run_attempt == 1` makes "Re-run jobs" a skipped job.
3. `concurrency` group `qgate-03-run-1`, `cancel-in-progress: false`.
Deleting and re-pushing the tag, force-moving it, or editing and re-tagging (including another tag name added to the trigger) is an UNAUTHORIZED second run. A workflow file at the tagged commit is what runs, so any fix requires a new authorization.

## The single deliberate start
`git tag qgate-03-run-1 <exact-commit> && git push origin qgate-03-run-1`
(`<exact-commit>` is the reviewed branch HEAD containing the workflow, run_integration.sh and diagnostics.sh.) Do not push the tag alongside other refs.

## What the job does
Checkout hub (tag), Control Plane @ 7a4bcd40b3b49e61ff3c294dcca53b52f460b22c and Runtime @ c5e97e87dd239c821b1b4a406a55dcd03c5bc61f into `_qgate03/cp` and `_qgate03/rt` (all `persist-credentials: false`); setup-python 3.13; `pip install --require-hashes -r docs/mvp-package/requirements-mvp-py313.txt` (13 pinned packages incl. pydantic 2.13.5, cryptography 50.0.0, pytest 8.3.5; lock sha256 recorded). Provenance is written to `EVDIR/provenance.txt` (hub sha, workflow sha, tree ids of tools/mvp_env_record and tools/mvp_ingress, CP/RT HEAD, python path/version/sha256, requirements sha256, run id/attempt, ImageOS, ImageVersion, RUNNER_NAME raw, pip freeze). Integration runs `sudo -n -E env PATH=$PATH bash .github/qgate-03/run_integration.sh ...`, exit code saved in `EVDIR/integration.rc`. Same interpreter for root and ingress: the setup-python 3.13 `python` is first on PATH and PATH is passed through sudo; run_integration.sh must use `python` from PATH (not a system python3) so that installed deps are visible. UNVERIFIED until Worker B's script is reviewed.

Shell is `bash {0}` (no `-e`), unlike QGATE-02 where `bash -e` aborted before checksums on a non-zero capture. Steps that must not abort end with `exit 0`.

`if: always()` steps: Checksums (SHA256SUMS over EVDIR, excluding itself, after chown to the runner user), Summary (read-only parse of `capture-record.json`: PASS/FAIL/BLOCKED counts, overall, profile_supported to the job summary; raw checks JSON in the log), upload artifact `qgate03-raw-evidence` (retention 90 days, `if-no-files-found: warn`), then a final Verdict step that fails the job if `integration.rc != 0` or capture overall != PASS. Evidence is uploaded either way and failure is not masked. A FAIL/BLOCKED result is a valid, preserved outcome, not a reason to rerun.

## Safety review
- No sysctl, Yama, ACL or security-policy change in the workflow; network only for checkout and pip. No new actions (pinned SHAs as in QGATE-02), no secrets, `contents: read`.
- `${{ }}` uses: only `github.workspace` (env, upload path) and `github.run_attempt`/`github.ref` in `if`. No untrusted inputs (no PR titles, branch names, issue text). Tag name is a fixed literal match. Other values come from env vars used quoted.
- sudo executes repo code as root on an ephemeral runner; accepted for the single bounded run, content governed by the reviewed tagged commit.

## Preserved on failure
All EVDIR files (pip install output, provenance, integration stdout/stderr, rc files, diagnostics, capture record and output as written by run_integration.sh, SHA256SUMS) are uploaded even if earlier steps fail. Runner logs remain. If pip install fails, integration still runs and records what happens.

## Known limits
- Single runner image instance; ImageVersion is recorded, not controlled; results do not generalize.
- Artifact upload can fail independently (evidence then only in logs); checksums are of EVDIR as uploaded, not signed.
- Checkout of the two public repos relies on pinned SHAs being reachable.
- The workflow cannot validate run_integration.sh behaviour; it was not executed here (only YAML parse validated).
- QGATE-02 second-hand facts (7 PASS/23 BLOCKED/1 FAIL, ACL under /opt) are not asserted; any failure of the original profile is preserved, not waived.
