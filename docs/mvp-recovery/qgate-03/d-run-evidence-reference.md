# QGATE-03: integration run evidence reference

Non-authorizing. Not qualification, not certification, not a host designation. Candidate PROVISIONAL, UNFROZEN, UNQUALIFIED. Same-lineage AI work; Q7 NOT ESTABLISHED.

## Run identity (source: GitHub REST API read by the builder)

| Item | Value |
|---|---|
| Run | https://github.com/cogno-us/cognous-open-control-stack/actions/runs/41153041401 (run id `41153041401`, attempt 1, event `push`, branch `qgate-03/run-1`) |
| Execution revision | commit `70b6ef2367d99a4fbfee375a77fd68e01ca88196` (the exact head later reviewed; CP `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c` and Runtime `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f` checked out at those pins by the workflow) |
| Job | `integrate`, job id `124393680401`, label `ubuntu-24.04`, runner id `1000003136`, 2026-10-31T00:59:05Z to 00:59:24Z |
| Steps | checkout x3, setup-python, hash-locked install, provenance, **integration: success**, checksums, summary, **artifact upload: success**, final verdict step: **failure** (by design, after the upload) |
| Verdict-step annotation (workflow's own words) | "QGATE-03 not PASS (integration.rc=0, capture overall=BLOCKED). Evidence uploaded; failure preserved." |
| Executions | exactly one. Branch `qgate-03/run-1` must never be pushed again (a further push would be an unauthorized second run) |

## Trigger deviation from the reviewed design (disclosed)

The design reviewed in `adversarial-precheck.md` used a tag trigger. Pushing the tag failed twice with a transport disconnect (no run started), and creating the ref through the REST API was refused by the session proxy ("Write access to this GitHub API path is not permitted"); that was not worked around. The trigger was then changed, in a commit that only edits the trigger, the guard and comments (`workflow-design.md` updated), to a push to the dedicated one-purpose branch `qgate-03/run-1`. This delta was reviewed only by the builder.

## Raw evidence (immutable reference)

| Item | Value |
|---|---|
| Artifact | `qgate03-raw-evidence`, id `13023553992`, 88052 bytes |
| Digest (GitHub-reported) | `sha256:0d14b95b5872f9272c3e240de1f4a198eee3f0a79fc7f2a4ee2c1078724650aa` |
| Retention | created 2026-10-31T00:59:20Z, **expires 2027-01-29T00:59:03Z** |
| Contents | `capture-record.json` (the capture script's own record), `capture-record-supp-ipc2751.json` (supplementary, not the verdict basis), `peer-uid-controls.json`, `diagnostics/`, `provenance.txt`, per-command `.out/.err/.rc`, `SHA256SUMS` (designed contents; **not read by the builder**) |

## What the builder could and could not read

- Read: run, job, step and artifact metadata and the annotations above.
- **Not readable**: the job log and the artifact zip (served from a blob host the session egress policy denies; reported, not worked around). Therefore no individual check result, no `getfacl` output and no peer-UID control result is recorded here as an observation.
- Established with the workflow's own recorded outcome: `integration.rc=0`; a `capture-record.json` exists (the capture only runs after the ingress started) with `overall=BLOCKED`. By the capture script's semantics ("overall is FAIL if any check fails, else BLOCKED if any is blocked, else PASS") this means **zero FAIL and at least one BLOCKED**.
