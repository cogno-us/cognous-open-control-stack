# Proposed logical-intent prevention contract

Status: design for the next bounded engineering batch; not implemented, adopted,
or qualified. This proposal preserves the selected component revisions and the
current 35-entry release matrix. Protected-worker qualification is a separate
boundary claim and does not establish logical-intent prevention.

## Problem and evidence

`tests/test_research_qualification.py::test_replanned_equivalent_intent_multi_use_grant`
demonstrates that separately approved proposals with equivalent business payloads
can create two effects. Replaying the same effect creates no third effect. Thus
effect-ID idempotency does not prevent a new proposal for the same business intent.
The current routine refund payload requires customer identity and reason; it does
not establish a trusted refund-request identity. Equality of customer, amount or
reason cannot distinguish two legitimate refunds from a duplicate.

## Proposed bounded profile

Introduce a versioned, opt-in synthetic refund profile before considering a
general platform claim. A trusted domain service supplies a stable refund-request
identifier and validates its institution, domain, customer and effect-class scope.
The agent cannot mint an accepted identity by changing correlation or run IDs.
The identifier is not an authorization credential: current authority and all
existing scope, approval and committed-operation checks remain necessary.

The claim key is the canonical tuple of profile version, institution, domain,
customer, effect class and domain-issued refund-request ID. Encoding must be
unambiguous and tested. The trusted service binds that key to an immutable
operation commitment covering target, adapter, amount, unit and business payload.
Invalid or unverifiable domain identity fails closed. Changed operation under an
existing key is a conflict, not a new intent; a genuine amendment requires a
separate, explicitly designed domain transition outside this first profile.

## Reservation and dispatch invariant

Before any dispatch, an atomic, durable compare-and-create binds the claim key
to the original effect ID and committed operation. Concurrent proposals cannot
both become owners. Every supported dispatch path must enforce that ownership;
an alternate effect ID or fresh approval cannot replace it. Storage failure or
an ambiguous reservation result holds dispatch until the original ownership is
resolved. A destination uniqueness constraint on final applied rows alone is
insufficient: it could allow a new effect to win while the original is in flight.

Control Plane admission and executor/destination enforcement must share a
verifiable ownership binding. The first implementation must name the authoritative
store and transaction boundary, prove that dispatch cannot precede commit, and
account for any gap between stores. Do not imply atomicity across independent
databases. A single-destination transaction is the initial bounded target;
distributed reservations and external payment processors remain out of scope.

| Observed condition | Required behavior |
| --- | --- |
| New trusted intent, authorized operation | Reserve ownership durably, then dispatch original effect |
| Same key, same operation, new proposal/effect | Return original linkage; no new dispatch |
| Same key, changed operation | Reject conflict; preserve original linkage |
| Different valid intent, identical parameters | Allow independent authorization and effect |
| Original unresolved, absent observation or partial outcome | Retain ownership, pending original effect and `retry_eligible=false` |
| Original applied | Preserve ownership and original evidence; no second effect |
| Restart, storage outage or unverifiable identity | Hold until verified state is available |

Reservation ownership alone never grants retry permission. Point-in-time absence
and fresh authority cannot prove that an interrupted original will not commit.
This batch adds no automatic release, expiry, replacement effect, replay dispatch,
compensation or retry transition. Safe cancellation/release requires a separately
qualified proof that the original can no longer commit.

## Required qualification evidence

Each case must inspect independently persisted destination rows and durable
ownership, correlate original identities, and retain machine-readable artifacts.
Concurrency cases use synchronized competing attempts, not sequential substitutes.

| Case | Acceptance condition |
| --- | --- |
| Authorized new intent | One owner, one exact destination effect |
| Replan with changed run/correlation and fresh approval | Original linkage, no second effect |
| Concurrent same-intent admission | Exactly one owner; at most one dispatch/effect |
| Same intent with changed payload, target or adapter | Conflict and zero alternate effects |
| Distinct trusted intents with matching refund values | Two separately authorized effects |
| Forged or wrong-scope domain ID | No ownership claim or dispatch |
| Crash before reservation commit | No dispatch; deterministic ownership resolution |
| Crash after reservation, before dispatch | Ownership survives; no automatic redispatch |
| Timeout, observed absence, then late original commit | Original identity retained; zero replacement effects; final total one |
| Partial result or unavailable/stale observation | Hold and retain ownership; retry remains false |
| Restart after applied effect | Original evidence and linkage restored; no duplicate |
| Changed/revoked authority | No new effect and no reassignment of ownership |
| Store unavailable or corrupt | Fail closed without an alternate dispatch path |
| Legacy profile and selected reference suite | Existing behavior and characterization remain explicit |

## Implementation and adoption sequence

1. Specify domain-ID validation, canonical encoding, immutable operation binding,
   authoritative store, transaction boundaries and recovery states in the owning
   runtime repository. Review its applicable contributor instructions first.
2. Add the opt-in admission and executor/destination enforcement with durable
   ownership. No hub-only assertion can substitute for destination enforcement.
3. Exercise the cases above, including actual process restart and late commit.
   Demonstrate the negative control without prevention as well as the new profile.
4. Record version/schema compatibility. Existing effects cannot be retroactively
   assigned trusted intent IDs by guessing from payload equality. Keep legacy and
   new-profile coverage distinct; any backfill needs verified domain mappings.
5. Adopt exact reviewed component commits into the hub only after upstream evidence
   passes. Add profile-specific matrix entries and run the full reference gate.
   Never relabel the existing duplicate characterization as a prevention pass.

The first implementation must not claim global semantic equivalence, fleet-wide
exactly-once execution, safe automatic retry, or production destination coverage.
This contract is the reviewable engineering consequence of the research finding;
private research source material is not reproduced here.
