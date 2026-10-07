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
  `b670dd471eb7793ff796fd627d3c60628ed679f6`
- Moltbot Safe Worker 21 PR #17:
  `24f85c36fe8e3e832ac2493362e132a6cc5ecea5`

Supporting accepted pins remain the existing hub revisions for Manifest, Alvorada
and Replay.

## Contract under test

The opt-in profile declares one local SQLite database authoritative for mutable
grant, approval, policy and evidence state, execution claims, shared effect
budgets and protected synthetic effects.

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
through the real proposed Moltbot Safe atomic destination. Mutable invalidation
cases run both transaction orderings: invalidation-first produces no effect;
effect-transaction-first commits the original effect and later invalidation
preserves it. Grant/evidence expiry-first cases deny, and unchanged authority
succeeds.

No sleeps are used as correctness oracles.

## Compatibility and coordination

Moltbot Safe PR #14 (refund intent ownership) remains separate and unaccepted.
Worker 21 does not consume it. Its intent ownership semantics must later be
composed with the authority/effect transaction without releasing or migrating
held intent claims.

Control Plane Worker 20 PR #11 also remains unaccepted and non-authorizing.
Worker 21 does not duplicate its Decision Input Commitment Record.

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
