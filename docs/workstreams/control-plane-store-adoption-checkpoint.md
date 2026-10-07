# Worker 14e — Control Plane store-adoption qualification checkpoint

## Status

**Blocked before pin advancement.** The accepted Control Plane persistence repair
`248d899634d9db3518e831bc7ab568a48733f825` is not yet stack-qualified.

Starting hub SHA: `f8afac8fae9ebcedb207c46cdaba51728a918d5b`.

Branch: `worker14e/control-plane-store-adoption`.

The hub `main` branch was inspected once and was identical to the supplied
baseline. No open hub pull request existed at inspection time. The repository
README and CONTRIBUTING guidance, `component-lock.json`,
`docs/workstreams/recovery-authority-checkpoint.md` and
`docs/workstreams/process-boundary-checkpoint.md` were read before edits.
Upstream `docs/record-store-persistence.md` and
`docs/workstreams/store-concurrency-checkpoint.md` were read at the accepted
repair revision.

## Upstream repair reviewed

Accepted repair: `248d899634d9db3518e831bc7ab568a48733f825`.

Reviewed source: `2fe2abee8096c19607be7f77c817e641ce7f1aec`.

The accepted repair is one commit ahead of the reviewed source. Its persistence
contract keeps existing JSON records in place, validates without migration,
reloads under a stable Linux sidecar `flock`, preserves raw historical fields,
uses atomic same-directory replacement, propagates persistence/locking failures,
and explicitly excludes whole-workflow transactions, distributed guarantees and
exactly-once delivery.

The upstream checkpoint reports 20/20 concurrency qualification tests in each
final repetition and 145/145 component tests locally on Python 3.12. The supplied
handoff states final-head CI passed 145 tests on Python 3.11 and 3.12. The GitHub
combined-status endpoint exposed no separate legacy commit statuses for the
accepted SHA during this worker's one-time check, so this checkpoint preserves
the supplied CI statement rather than inventing an additional status result.

## Hub selected runtime

The hub still selects Control Plane
`2ea9528eeb87e14ff10f05de06473122b9df540f` as the runtime dependency.
Historical Control Plane fixture dependency
`283500652d47a692fb0b99a1172a6d5faffbd9a7` is separately recorded as
historical compatibility only.

No historical example, prior qualification artifact or source-attributed evidence
is relabeled in this branch.

## Compatibility findings

Adoption cannot be qualified by changing only the hub runtime pin.

The accepted downstream contracts encode the prior runtime Control Plane SHA as
an exact producer compatibility restriction:

1. Replay `274543f1cd7171784a923a8e37015017a0d8bc9d` defines
   `CONTROL_PLANE_V2_REVISION` as
   `2ea9528eeb87e14ff10f05de06473122b9df540f` and binds producer profile
   2.0.0 to that exact revision in `PRODUCER_COMPATIBILITY`.
2. ODES `226adb0e3cde5377ac9db6f7e5857bfa7e65e30a` defines the same exact
   Control Plane revision in `PINNED_V2_REVISIONS`.
3. Governance Evidence Pack `812194b9a89a5fa21e675200fcb4e0089666f1b6`
   defines the same exact revision in `V2_REVISIONS`, uses it to detect the v2
   bundle path, and includes it in the accepted Control Plane source set.
4. The accepted Alvorada/GAX producer documentation and CI are likewise pinned
   to the prior Control Plane revision.

These are supported-producer compatibility mappings, not historical fixtures.
The exact revision is part of current v2 validation. Advancing only
`component-lock.json` would therefore produce a source revision that current
Replay/ODES/Evidence Pack compatibility logic does not accept as the current v2
combination.

This blocker is distinct from historical examples containing the old SHA. Those
artifacts must remain unchanged.

## Precise pin changes

None.

The proposed hub runtime pin remains
`2ea9528eeb87e14ff10f05de06473122b9df540f`. Historical dependencies and all
other selected component pins remain unchanged.

## Qualification execution

The persistence repair itself is accepted upstream, but the stack adoption gate
was intentionally stopped before full execution because current consumer
contracts reject the proposed producer revision by exact mapping.

Accordingly:

- no two-run stack release evidence is claimed;
- no JUnit is fabricated;
- no persistence scenario is reclassified as stack-qualified;
- Worker 16's earlier shared-store record-loss evidence remains historical and
  unchanged against its original selected pin;
- the existing accepted recovery-authority, late-commit, tamper, provenance,
  transport, evidence-only and repeatability evidence remains attributed to its
  original pins.

A machine-readable blocked result is stored under
`examples/control-plane-store-adoption/qualification-summary.json`.

## Smallest bounded follow-up

A separate compatibility batch is required before this adoption qualification can
resume. It should update only the current v2 producer-compatibility mappings in
the owning consumers to admit the accepted Control Plane persistence repair while
preserving historical mappings and fixtures:

- Replay: add the repaired Control Plane revision as an explicitly supported
  producer-2.0.0 Control Plane revision, with positive/negative revision tests.
- ODES: add a separately accurate accepted v2 mapping for the repaired revision;
  do not rewrite old packages or profile evidence.
- Governance Evidence Pack: accept the repaired revision in current v2 source
  validation while retaining prior accepted and historical source identities.
- Alvorada/GAX: update only its current accepted Control Plane dependency and
  compatibility assertions after the three consumer changes are accepted.

The follow-up must demonstrate that no schema, decision/effect identity,
observation semantics, recovery semantics or producer attribution changed merely
because persistence implementation changed.

Only after those owning repositories publish accepted compatible revisions should
Worker 14e (or a successor) advance the hub runtime pin and execute the requested
two isolated full qualifications plus the new persistence matrix gates.

## Required persistence qualification after compatibility clears

The resumed adoption batch must independently establish:

- concurrent initialization without overwrite;
- same-type and mixed decision/attempt/observation/reconciliation writes;
- every successful append retained exactly;
- historical lifecycle preservation;
- complete readers;
- stale instances unable to overwrite newer writes;
- valid store across termination before/after replacement;
- sidecar lock ownership released after process death;
- explicit persistence failures.

It must keep independent-store/shared-destination qualification distinct from
concurrent writers on one shared Control Plane store. Individual record
transactions may be protected; the whole decide/execute/reconcile workflow is not
atomic.

Existing execution/recovery gates must then still pass: same-effect duplicate
suppression, cumulative local effect limits, pre-commit absence with
`retry_eligible=false`, post-commit recovery retaining original identities,
unchanged interrupted acknowledgement history, no replacement dispatch after
uncertainty or fresh absence, changed-authority denial separated from historical
effect evidence, accepted observations distinct from rejected evidence, Replay /
ODES / successor continuity, and separate Control Plane/executor attempt
namespaces.

Equivalent business intent under distinct valid proposals remains a characterized
limitation, not a safety pass.

## Support boundaries retained

The repair's supported boundary is cooperating writers on documented local Linux
filesystems. All writers must use the repaired implementation and the same stable
sidecar/canonical path assumptions. There is no distributed/network-filesystem
guarantee, whole-workflow transaction, remote exactly-once delivery, authenticated
observation, destination-finality or live OpenShell confinement claim.

No deployment, paid provisioning, public-chain write, DOCX change, deferred
Alvorada PR #2 consumption, self-merge or unrelated refactoring is part of this
branch.
