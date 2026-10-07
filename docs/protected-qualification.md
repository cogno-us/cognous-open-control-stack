# Protected local worker qualification

Profile `protected-local-worker/0.1.0` qualifies a **separate Linux bubblewrap
fixture**, not the OpenShell adapter or a production deployment. The accepted
reference release and its component lock are unchanged. The profile is an
additional qualification candidate until its dedicated workflow produces a
successful complete report and that evidence is reviewed.

## Boundary and ownership

The trusted host owns the synthetic authority resolver, approval fixture,
Control Plane store, executor and SQLite destination. A fixed synthetic worker
runs with separate mount, process and network namespaces, dropped capabilities,
a cleared environment, read-only system runtime mounts and fresh temporary
storage. No host workspace, destination, authority store or credential canary is
mounted. The worker receives only a scenario selector, private probe path names
and the port of a controlled loopback sink. Those path names are not capabilities.

The worker attempts reads and writes of the private canary and destination
paths and connects to the host sink. It emits a bounded request; **it cannot
supply authority, execute host commands or supply the qualification verdict**.
The parent checks the probes and namespace identities before dispatch. Host
canary hashes, sink connection counts and destination reads independently check
for effects. Destination inspection uses a separate SQLite connection opened
with `mode=ro`; executor acknowledgement alone never closes a case.

The oracle is independent of the worker, not of the trusted host/operator or
underlying destination implementation. Canary files are synthetic capability
fixtures, not evidence of actual production credential isolation. No third-party
service, real credential, real refund or external attack target is used.

## Required cases

Each case gets a new destination, record store, worker process and temporary
filesystem. The fixed campaign runs exactly two repetitions of these six cases:

| Case | Expected result |
|---|---|
| Authorized control | Exactly one applied row matching the approved effect, target, amount, unit and payload |
| Payload substitution | Self-consistent altered payload commitment still denied by original proposal binding; zero effects |
| Target substitution | Altered destination denied; zero effects |
| Adapter substitution | Alternate adapter denied; zero effects |
| Missing authority | Current resolver context removed after decision; zero effects |
| Forged success | Worker assertion ignored; direct destination inspection remains empty |

Every invocation also requires all private-path read/write probes denied, zero
prohibited host sink connections, different network/mount/PID namespace IDs,
unchanged host canaries and no previous-worker temporary state. The authorized
control prevents a blanket-deny configuration from passing.

Instruction-like payloads are deterministic data substitutions. No model is
called. This tests binding enforcement, **not prompt-injection resistance of a
model**, all possible tools, external network destinations or a general attacker.
The direct file and host-loopback probes cover only these declared alternate
paths. The trusted parent retains direct destination access by design.

## Run and evidence

Requires Linux with permitted bubblewrap namespaces, `/usr/bin/python3`, and a
host Python with `pydantic>=2,<3` (plus `pytest>=8,<9` for verifier tests).
Do not weaken host restrictions to obtain a green run. A denied namespace
preflight is blocked qualification, not an exemption or a skipped pass.

```bash
python tools/protected_qualification.py --clone --results-dir results/protected
```

`--clone` checks out only missing dependencies at the existing selected lock
revisions. Existing checkouts must match and be clean, including untracked files;
no checkout is overwritten. Use a fresh evidence directory. Results from earlier
attempts are preserved. The runner performs no package installation.

The summary records pins, source hashes, host and worker namespace IDs, raw
worker output, actual destination rows, executor results and failure details.
Only a complete two-repetition pass sets `qualified=true`; missing prerequisites,
malformed output, timeouts and verifier failures return nonzero. Worker launch
is limited to ten seconds per invocation; the fixed campaign has twelve worker
invocations. CI also imposes a job timeout. These are fixed-probe limits, not a
resource-confinement claim for arbitrary agent workloads.

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_protected_qualification.py
```

Verifier and direct adapter tests can pass when namespaces are unavailable.
Their success **does not qualify isolation**. The dedicated workflow retains
both test results and the separate campaign summary even on failure.

## Remaining work

Live OpenShell confinement requires its own accepted deployment/image profile
and executed evidence. This fixture does not advance the executor pin, establish
production resolver freshness, implement intent deduplication, permit retry,
prove distributed guarantees or demonstrate containment of arbitrary programs.
Broader credential/API/maintenance/recovery-path inventories belong to a named
deployment. Production non-bypassability remains unqualified.

## CI host applicability

The current candidate targets GitHub-hosted `ubuntu-22.04` explicitly. The earlier
`ubuntu-24.04` run is retained as blocked, not relabeled or counted as a pass.
The namespace flags, private-path/network probes and all acceptance conditions
are unchanged. No sysctl, AppArmor, privilege escalation for the worker, or
network-sharing override is added. A host-profile artifact records OS, kernel,
UID, bubblewrap version and observable user-namespace policy. A successful run
would apply only to that recorded environment and fixed probe campaign.
