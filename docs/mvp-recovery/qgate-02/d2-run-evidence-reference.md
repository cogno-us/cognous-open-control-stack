# QGATE-02 D2: GitHub-hosted ubuntu-24.04 feasibility run, evidence reference

Non-authorizing. Not qualification, not certification, not a host designation. Candidate PROVISIONAL, UNFROZEN, UNQUALIFIED.

## Run identity (source: GitHub REST API, read by the builder)

| Item | Value |
|---|---|
| Run | https://github.com/cogno-us/cognous-open-control-stack/actions/runs/41125818207 (run id `41125818207`, attempt 1, event `push`) |
| Job | `observe`, job id `124303935866`, label `ubuntu-24.04`, runner group "GitHub Actions", runner id `1000003094` |
| Workflow revision | commit `14d792f4bbbca8504d483be1a7e9119297329946` on `qgate-02/d1-d2-host-feasibility`; workflow blob `c22470d9f323ae0b8f5c2d294a299abff19851ba`, sha256 `575c5ba5147c39a5f92c2188498c126410dbb83aeb162a0b617278ae62fabd57` |
| Probe | `.github/qgate-02/runner_probe.py`, blob `16be56db3e0444bccd08a93e0f8dc61000cfa67d`, sha256 `69447a5b35f6b739bd7fc7055d0c77dc5299dd8fee4d088daf3e93812de46a0e` |
| Accepted capture script (unmodified) | `tools/mvp_env_record/capture_env_record.py`, sha256 `faf8f26117b9e0d4616528250b97099c037117fd5df60c7032ac8347464af461`; `tools/mvp_env_record` tree `b446e30a` and `tools/mvp_ingress` tree `656b506d` unchanged from `dff727a9` |
| Timing | started 2026-10-30T20:46:10Z, completed 20:46:21Z |
| Conclusion | job **failure**: step 4 "Observe" exited with code 1 (annotation "Process completed with exit code 1"); upload step succeeded |
| Retries | none. One execution only, as authorized. The `run_attempt == 1` guard and the absence of `workflow_dispatch` prevent a re-run from executing |

## Raw evidence (immutable reference)

| Item | Value |
|---|---|
| Artifact | `qgate02-d2-raw-evidence`, artifact id `13010567298` |
| Size / digest | 7588 bytes, GitHub-reported `sha256:412eb8649a05ff272c17b932c002920e5da2e5ccebd13be59321849f0d211c3f` |
| Retention | created 2026-10-30T20:46:19Z, **expires 2027-01-28T20:46:10Z** |
| Intended contents | `provenance.txt`, `probe-record.json`, `probe-stdout/stderr.txt`, `capture-record.json`, `capture-stdout/stderr.txt`, `SHA256SUMS` (see workflow). **Not verified**: the builder could not open the artifact |

## What the builder could and could not read

- Read: run, job, step, runner and artifact metadata and the failure annotation (REST API, `api.github.com`).
- **Not readable from the builder's environment**: the job log and the artifact zip. Both are served from `productionresultssa16.blob.core.windows.net`, which the session's egress policy denies (HTTP 403 to CONNECT, recorded by the proxy). The denial was reported, not retried and not routed around.
- Consequently **no runner observation (kernel, Yama value, capabilities, probe results) is recorded in this PR**. None is inferred or fabricated.

## Unverified explanation of the failure (inference, not observation)

The step exited 1 after about one second under `bash -eo pipefail`. The accepted capture script exits 1 when any check is FAIL (2 when BLOCKED), so a FAIL on the runner would abort the step before the later `sha256sum`, leaving the probe and capture records written but `SHA256SUMS` possibly absent. Equally possible: a probe or `sudo` error. The log or artifact is needed to say which. A local dry run of the same commands (not evidence, different kernel and sandbox) produced capture exit 2 (BLOCKED), 31 checks.

## Deviations and gaps recorded

- The workflow did not reach its own checksum step reliably (see above); the integrity anchor is therefore GitHub's artifact digest, not `SHA256SUMS`.
- Ingress-dependent checks were intentionally not run (no ingress; the real ingress needs pinned Control Plane and Runtime checkouts, outside this authorization).
- No host-profile requirement can be recorded as passed, failed or demonstrably impossible from this run as seen by the builder.
