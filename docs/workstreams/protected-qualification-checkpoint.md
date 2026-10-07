# Protected qualification checkpoint

## Scope and starting point

Starting hub main: `86ab24c42e9ebc92b3704d0e446c45de7101ee71`.
Branch: `governor/protected-qualification`.

Adds a separate qualification candidate for a fixed synthetic worker in Linux
bubblewrap namespaces, with host-owned pinned Control Plane/executor dispatch and
read-only destination verification. See [the profile](../protected-qualification.md).
This is not an OpenShell implementation or qualification, a model-behavior test,
or production non-bypassability. Component lock, shared release runner/matrix,
upstream runtime repositories and previously accepted evidence remain unchanged.

## Actual local validation

Python 3.12.14, pytest 8.4.2, pydantic 2.13.5; exact selected dependency revisions
were cloned and checked before importing their supported public integration.

- **17 tests passed**, zero failures/errors/skips. Includes six actual pinned
  executor/independent-destination cases, eight verifier fault cases, unexpected
  request rejection, missing-isolation failure handling and evidence preservation.
- Dedicated isolated campaign: **BLOCKED**, exit 1, `qualified=false`.
  The first worker timed out after ten seconds and reported
  `bwrap: open /proc/74/ns/ns failed: No such file or directory`.
  Its destination remained empty. No isolated case or repetition passed.
- A preliminary minimal namespace probe reported a denied NETLINK_ROUTE socket.
  Host restrictions were not weakened. This is local prerequisite evidence only.
- Earlier runner attempt is retained separately from final local attempt.

Evidence: [verifier JUnit](../../examples/protected-qualification/local-verifier-tests.xml),
[final local isolation attempt](../../examples/protected-qualification/final-local-isolation-attempt/summary.json),
[earlier attempt](../../examples/protected-qualification/local-isolation-attempt/summary.json).
Reports carry hashes of the source actually executed; neither is replaced by an
anticipated CI result. No new isolated-qualification pass is claimed.

## Review and remaining gate

The dedicated workflow installs bubblewrap without disabling host security,
checks exact dependencies, runs verifier tests, then requires two isolated
repetitions of all six scenarios. Missing prerequisites, timeouts and missing or
unsafe observations fail the gate. All available evidence is uploaded on failure.

The PR remains a qualification candidate until the complete isolated campaign
succeeds and its final-head evidence is reviewed. Live OpenShell, real credential
isolation, arbitrary-agent resource confinement, deployment API/maintenance
bypass, production authority and distributed behavior remain unqualified.
No self-merge or deployment.

## Reviewed first CI result

Candidate head `9866e0a080fffee5527121e2b6965995a1364a66`:

- [Reference CI 37620063453](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37620063453)
  completed successfully. This review checked workflow status, not its raw test totals.
- [Protected CI 37620063545](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37620063545)
  passed all **17 verifier/adapter tests**, then **blocked** on its first worker:
  `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`.
- The worker exited 1; destination rows before dispatch remained empty. Zero
  isolated cases passed and zero full repetitions completed. `qualified=false`.
- Artifact `11481811458` was downloaded. Its archive SHA-256 matched GitHub's
  `8db695d85e21a4deec4b0b200143f2a5076ed3ad741c63118d4fc489c79a9f27`.
  The exact summary and verifier JUnit are retained under
  [ci-37620063545](../../examples/protected-qualification/ci-37620063545/).
  Actions tested merge ref `9f4e57e1e2bbd7f0fbb85a214d72798d9e89ef82`,
  distinguished from the PR source head in the provenance record.

### Blocker and decision

The observed failure is namespace loopback configuration, before the campaign
worker executes or any executor dispatch. The log alone does not establish the
precise host security mechanism that denied it. Ubuntu 24.04 documents restricted
unprivileged user namespaces, which is a plausible explanation, not a verified
host-policy diagnosis for this run:
<https://discourse.ubuntu.com/t/ubuntu-24-04-lts-noble-numbat-release-notes/39890>.

Retain the draft and failed gate. Do not remove network isolation, add elevated
runtime execution, disable AppArmor/sysctl restrictions, mark the campaign
optional, or substitute adapter tests for its missing evidence. The next
prerequisite is an approved qualification host where this namespace profile is
permitted, or an explicitly scoped alternative confinement profile. A different
profile needs its own evidence and cannot relabel this Ubuntu 24.04 result.

This update preserves the failed evidence and records the release decision;
it does not implement an isolation workaround or claim a new pass.
