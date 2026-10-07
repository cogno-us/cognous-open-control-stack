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
