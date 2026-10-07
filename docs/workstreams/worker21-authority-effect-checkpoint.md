# Worker 21 - proposed atomic authority/effect integration qualification

## Baseline and evidence

Starting hub main: `502fd12cb49d30f8ea8e12d7968612d55d326f16`.

Worker 19 hub PR #14 was reviewed at final documentation head
`18a05b58ca1e3f5c4c2914fe09ab51f3d7af0016`. Its exact-head authority-effect
qualification run `37634412359` completed successfully. The earlier executed
run `37634121102` retained two repetitions of seven cases and the reported
artifact digest
`sha256:9c5f24455f396ed39a1830e7f8ae3beb2b27b4be62e1a73542d7f68806fe6ced`.

Worker 19 evidence is not modified by this branch.

## Proposed upstream revisions

This qualification uses proposed revisions without advancing `component-lock.json`:

- Control Plane Worker 21 PR #12:
  `73e3c65acc47dc43593dcb0420d14032ed410b14`
- Moltbot Safe Worker 21 PR #17:
  `9d5285cf3938409f0c2ec5b4f344bde15edbc527`

Supporting accepted pins remain the existing hub revisions for Manifest, Alvorada
and Replay.

## Contract under test

The hardened opt-in profile defines an explicit authority handoff. The Control
Plane source excludes its invalidating writers while it performs final
resolution, captures one coherent authority snapshot, rejects non-active/current
projections, constructs the exact claim and provisions it into the local store.
Only after that callback returns does one local SQLite database become
authoritative for mutable grant, approval, policy and evidence state, execution
claims, shared effect budgets and protected synthetic effects. Another ordinary
recheck without this handoff is not treated as sufficient.

Every invalidating writer in the profile and execution use SQLite
`BEGIN IMMEDIATE`. Execution reads trusted time only after acquiring that
transaction, validates the current authoritative state and atomically records the
attempt, consumes the claim, increments the budget and inserts the effect.

A claim is materialized by the proposed Control Plane API only from a persisted
authorized decision plus a fresh resolution. Claim possession is not executable
authority outside the participating store.

## Qualification program

The runner first executes the proposed upstream focused suites, including:

- exact claim binding/tamper checks;
- grant, approval, policy and evidence invalidation;
- grant/evidence expiry and lock-wait time semantics;
- one-claim concurrent process redemption;
- competing effects against a shared budget;
- process termination before, during and after the transaction;
- lost acknowledgement/restart;
- operation substitution;
- missing authoritative state;
- legacy-path rejection and legacy non-regression.

The hub integration tests then exercise real Control Plane claim materialization
and executor provisioning through the proposed Moltbot Safe atomic destination.
They inject approval revocation and policy supersession after successful final
`_resolve()` but before the coherent snapshot returns; both must be rejected
before a claim reaches SQLite. They also verify exact claim/effect and retained
operation-digest reconciliation binding.

Mutable invalidation cases run both transaction orderings:
invalidation-first produces no effect; effect-transaction-first commits the
original effect and later invalidation preserves it. Grant/evidence expiry-first
cases deny, and unchanged authority succeeds.

No sleeps are used as correctness oracles.

## Compatibility and coordination

Execution Runtime PR #14 (refund intent ownership) is merged at
`89eca565a4f3a6a12e18fa9811c43f75a965dff7`. The tested Worker 21
proposal head does not consume it. Its intent ownership semantics must later be
composed with the authority/effect transaction without releasing or migrating
held intent claims.

Control Plane Worker 20 PR #11 is now merged at
`29337fe900d3b2da5656c77d56d70f18feb190b8`. Its Decision Input
Commitment Record remains non-authorizing. Worker 21 does not silently adopt it
into runtime authority and continues to use only optional opaque linkage fields
pending an explicit integration decision.

## Adoption gate

This branch does **not** edit `component-lock.json` or shared release claims.
Hub adoption is deferred until the upstream Worker 21 PRs are reviewed and
accepted, followed by a qualification rerun at the accepted merge SHAs.

## Limits

The tested guarantee is bounded to cooperating same-host processes using one
participating SQLite database and trusted host writer APIs. It does not establish
production identity, distributed authorization, distributed exactly-once
execution, remote revocation, external destination atomicity, OpenShell
confinement, complete mediation, EBL-Core conformance or production readiness.


## Governor hardening

The corrected profile closes three review defects:

1. Claim issuance no longer performs uncoordinated rereads after a successful
   final resolve. Final resolve, coherent snapshot validation and destination
   provisioning occur inside the trusted source handoff. Revoked approvals,
   superseded policies and other non-active/current projections cannot be
   normalized back to active by provisioning.
2. Recovery requires the requested effect to equal the claim's retained effect
   identity and requires the durable effect operation digest to equal the digest
   transactionally retained when that claim was consumed.
3. Expiry-while-waiting qualification now waits for child destination
   initialization and a deterministic pre-`BEGIN IMMEDIATE` execution signal
   before advancing the trusted clock and releasing the competing transaction.

The original successful transaction, separate-process concurrency, shared-budget
and crash-boundary tests remain in the executor suite.


## Hardened proposed-revision evidence

Hardened qualification run `37640502400` completed successfully at hub head
`b437c6e444706676c5a30b6630568ac06995f064`.

Executed totals:

- Control Plane focused: **7 passed**
- Moltbot Safe focused: **19 passed**
- Cross-repository integration repetition 1: **14 passed**
- Cross-repository integration repetition 2: **14 passed**
- Qualification exit: **0**
- No skips in the Worker 21 qualification.

Retained artifact:

- name: `worker21-authority-effect-qualification`
- artifact id: `11492535461`
- digest:
  `sha256:6a44f53d95b86441aa5274618d14561852b993ab7ba7b221df05ada7d56ba3bd`

This run exercised exact proposed Control Plane
`6c7b49138134eeb0d6e37e1b99a36a49cc42218e` and Moltbot Safe
`1e84d01c3861a94f6d512a651e95b3606ffefe66` without changing accepted
hub pins. The final documentation/evidence head is rerun separately and its
result is recorded in the PR handoff.


## Recovery-envelope substitution hardening

The integration qualification now routes recovery through the actual
`AtomicLocalControlPlaneExecutor.reconcile()` after a claim is materialized by
Control Plane and provisioned into the executor store.

Negative vectors keep the original effect ID but substitute, independently:

- decision ID;
- target;
- amount; and
- payload plus its payload commitment.

Each must return a held observation with `observed_state=unknown` and the
specific decision/operation binding reason. A positive control supplies the
exact original envelope and must recover the historical applied effect.

The executor additionally verifies the destination operation digest against the
digest retained transactionally when the claim was consumed. Original Worker 21
evidence remains retained; this is a new qualification generation.


The final recovery-hardening qualification pins executor PR #17 head `9d5285cf3938409f0c2ec5b4f344bde15edbc527`. Because connector-authored PR commits did not emit a fresh PR workflow event on the executor repository, the hub runner is the explicit exact-SHA focused-suite rerun: it checks out this revision and executes `tests/test_local_authority_effect.py` before running the two integration repetitions.


## Verified recovery-hardening result

Run [37643807886](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37643807886)
passed for PR head `ea21f6d476754a319e4c15f314b51bbb759677a2` via
GitHub's test merge `05dcfb43f51661e151f8f57489716d1903041f3e`.
It checked out the exact current proposed upstream revisions listed above:
Control Plane 7 passed; executor 24 passed; integration 19 passed in each of
two repetitions. Total: 69 passed, zero failures, errors or skips.

Artifact ID: `11493730287`; SHA-256:
`3bd7203185c31189220f328b85c389499b37f23946084e94ed01cec37cd5a581`.

This evidence precedes integration with the subsequently updated main branches.
It does not establish compatibility with the merged refund-intent implementation.
The executor PR currently requires conflict resolution and qualification against
current main before acceptance. Accepted hub dependency revisions remain unchanged.


## Current-main compatibility blocker

Read-only merge analysis against executor main
`e0c127178247fbe33ec2c80997c464575738be1e` finds one content conflict:
`engine/safe_executor.py` at the transaction-entry profile checks. Main calls
`_check_commit_profile()` for refund-intent ownership; the Worker 21 branch
adds an authority/effect marker rejection at that same location. Both guards
must remain effective after resolution.

Source inspection also finds that neither profile's activation path rejects the
other profile's marker on an otherwise empty database. Therefore resolving the
text conflict alone is insufficient evidence of safe coexistence. Before
acceptance, reject mixed-profile activation in both orders (preserving existing
claims), or implement and qualify an explicitly combined contract. This is a
source-review finding; no mixed-profile execution reproduction is claimed.
