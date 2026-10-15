# S2 — ingress-hardening lane B

Base inspected: `592919dd95396f3f6164cf0ceec1fd15c065691b` (live main,
2026-10-15). PR #116 is merged at that base; its preallocation wire-size fix is
retained without modification. The only observed open PR at initial inspection
was documentation PR #117. No AGENTS.md was present in the checkout.

This is the optional ProtectedDestination synthetic SQLite profile, not selected
component integration. Operational trust remains **HOLD / NOT ESTABLISHED**.
Release and production authorization remain false. Preserve selected C0
check-to-commit limitations, optional cooperative same-host C1, no C2/C3 and no
real settlement. Local SQLite tests do not establish Internet-facing readiness.

## Policy and boundary

Every regular `apply` call with encodable trust/1 input takes the destination
writer transaction and a shared budget slot **before** command schema/signature
work. All identities share 128 attempts per 60 integer clock units. Claims of
issuer, command ID, operation or digest cannot obtain a separate budget.
An admitted attempt is not an authorized or accepted operation.

After 128 slots, return `INGRESS_SATURATED` without signature verification,
request digest computation, command dispatch or per-request event creation.
Persist a limited/unclassified request count and dropped-detail count instead.
These requests have not been authenticated; the counter does not establish that
they were malicious, nor reconstruct their IDs, payloads, signatures or reasons.
The first 64 unauthenticated refusals over the database lifetime retain the
existing payload-free correlated event detail. Later unauthenticated refusals
increment aggregate counts only. Claimed IDs remain `claimed_command`; `command`
is populated only after the existing schema and signature admission checks.
Admitted authenticated refusals always receive full durable existing audit
records, including replays. Their retention is not capped by the unauthenticated
budget. Trusted key compromise can therefore still cause authenticated growth.

The class now imports only the SQLite primitives it needs from AssuranceRuntime
instead of inheriting unrelated HMAC operation entrypoints. Its five direct
`op_*` methods require the authenticated dispatch's connection-scoped ContextVar.
Calling an operation directly fails `DESTINATION_ADMISSION_REQUIRED`; context
is reset even on exceptions. This is application routing protection, not a
sandbox against Python code that already controls the process or database.

Unencodable/oversized wire input keeps PR #116 behavior: `INVALID_REQUEST`, no
database access, no durable per-request telemetry. Its failures are excluded
from the aggregate counts; an enclosing service needs bounded telemetry for
that surface. Wire validation/decoding still occurs before the regular budget.

## Persistence, clocks and migration

One `destination_ingress` singleton row stores version, lifetime aggregation
origin, current interval `[start,end)`, used slots, current interval limited
count, and cumulative requests/admitted/limited/unauthenticated/details/
dropped-detail/recovery counts. There are no attacker-keyed or time-bucket rows.
`requests = admitted + limited` for committed regular attempts since migration;
`dropped_detail = limited + unauthenticated - new_details` since migration.
`details` includes historical retained detail, so subtract the migration baseline
when using that equation for an upgraded database. Authenticated acceptance is
separately established by existing command/event/effect records.

State and required events, consumption and effects share `BEGIN IMMEDIATE` and
one commit. Process competition and restart cannot create extra slots. Counters
never wrap: increment beyond signed 64-bit maximum fails closed. Storage errors
propagate and close the connection without committing any effect. Required
audit/counter persistence is never best-effort.

Trusted clock units are seconds for this policy. Nonnegative integer time is
required; clock range must leave room for the 60-unit end boundary. Fixed or
regressing time cannot refill a bucket. At or past end, replace the current
interval with `[now,now+60)`; jumps do not accumulate credits. A fast or
attacker-controlled clock defeats the intended temporal rate. At an interval
boundary two adjacent budgets can run close together; this is a fixed-window
work cap, not a uniform sliding-window rate guarantee.

First admission performs an additive, writer-serialized migration, counting all
legacy events not explicitly marked authenticated toward the lifetime detail
cap. Existing history is neither deleted nor rechained; an already oversized
history stays oversized, with no new unauthenticated detail. No historical
request totals are invented. New counters start at migration. Unknown state
versions fail closed. Operators must upgrade every writer together; an old
binary can bypass this new policy. No configurable request-supplied defaults,
retention resets, automatic pruning, or silently renewed lifetime capacity.

## Saturation and trusted recovery

Attackers **can exhaust the shared regular budget needed by legitimate callers**.
Authentication is deliberately after that gate, so claimed trusted identity
cannot bypass it. Legitimate operations then wait for the next interval or
trusted recovery; fairness or protected capacity is not established.

A separately invoked local `recover_ingress` accepts only a signed admin
`destination-command` with operation `ingress_recover`, empty arguments, fresh
`at`, unique `id` and monotonic `sequence`. It shares the existing 60-unit admin
freshness rule, sequence store, writer transaction and required full audit.
It resets used slots only; it never clears evidence, counters, retained-detail
usage, grants or effects. Replays cannot replenish capacity. Ordinary `apply`
cannot invoke recovery. This route must remain available only to trusted local
administration, never an unauthenticated network endpoint. Its signature work
is intentionally outside the regular budget; repeated use requires host access
controls. An attacker can immediately consume reopened regular slots. Recovery
cannot repair full disk, counter exhaustion, missing database or an untrusted
clock; trusted offline remediation/upgrade is required without deleting evidence.

## Measured fixed schedule and limits

Local Python 3.12.14 / SQLite, three accepted setup commands at t=100 followed
by 400 distinct forged requests, then 400 more at the same t=100:

| Measurement | After first 400 | After all 800 |
| --- | ---: | ---: |
| Flood accepted / denied | 0 / 400 | 0 / 800 |
| Total regular attempts including setup | 403 | 803 |
| Admitted attempts including setup | 128 | 128 |
| Limited, not authenticated | 275 | 675 |
| Admitted unauthenticated refusals | 125 | 125 |
| Retained unauthenticated detail | 64 | 64 |
| Dropped-detail count | 336 | 736 |
| Events / objects / ingress rows / effects | 67 / 8 / 1 / 0 | 67 / 8 / 1 / 0 |
| Database bytes (initial 28,672) | 57,344 | 57,344 |

The final file uses 14 pages of 4,096 bytes. These are measured bytes for this
schedule, not a universal file-size ceiling. The established unauthenticated
storage bound is one fixed-field counter row plus at most 64 bounded detail
events beyond the retained legacy baseline. Counts and clock values have fixed
numeric ranges. Advancing-clock tests confirm that new intervals add no detail
or bucket rows after the lifetime cap. Authenticated events/effects and legacy
history are outside this storage bound. SQLite journal/transient I/O, allocator
behavior, existing free pages and filesystem overhead are not globally bounded.

At most 128 committed regular command admissions occur per declared interval
(fresh local recovery explicitly renews this budget). Aborted transactions do
not consume durable slots: repeated storage failures can repeat signature work,
while every such transaction fails closed before any committed effect. This
is another reason no total CPU/work bound is established. Saturated calls
still do wire validation, connection setup, writer-lock acquisition and one
aggregate update/commit. There is **no bound on total CPU, aggregate disk writes,
lock contention, incoming request rate, process count or network traffic**.
Five-second SQLite lock timeout is inherited; lock failure propagates without
effect. A service still needs connection/concurrency limits, bounded queues,
transport body limits/timeouts, rate enforcement and protected administration.
Full-destination restore rollback remains outside the guarantee.

## Validation and artifacts

The scoped workflow `destination-ingress.yml` uses immutable checkout,
setup-python and upload-artifact revisions and the hash-locked release dependency
file. It tests Python 3.11 and 3.12 at the PR head. Artifact names are
`destination-ingress-3.11` and `destination-ingress-3.12`; each contains
`ingress.xml`, `ingress.log`, and `existing/{tests.xml,tests.log,mutations.log,
qualification.json}`. The latter records exact source revision and source hashes.
The ingress log records the schedule measurements and negative-control outcome.

Local scope: 25 new ingress testcase elements plus 14 existing wire testcase
elements, without subtests. The affected existing destination/assurance
qualification has 179 testcase elements and 22 separately reported unittest
subtests. Thirteen existing control-removal probes are detected by assertions.
New controls remove the pre-signature gate in an isolated copied module and
raise the detail cap in a patched module; both must produce assertion failures.
Tests cover distinct forgeries, malformed normal/direct/recovery routes, fixed /
advancing / regressing clocks, restart, four competing processes, legitimate
effect and admin recovery after saturation, durable authenticated refusal after
retention saturation, legacy migration, counter exhaustion, audit failure,
counter-persistence failure and actual SQLite `SQLITE_FULL` during required audit
insertion, with zero committed effects or consumption on storage failure.

No changes to shared trust helpers, existing tests, benchmark adapters,
qualification-count files, component locks, profiles or the central control panel
are required. Coordinator action: callers must handle `INGRESS_SATURATED`; deploy
all writers together and keep recovery local. Any inherited AssuranceRuntime
operations previously called on this destination were outside its signed
command contract and are now unavailable. Existing qualification/benchmark
scoped tests remain the compatibility check, not a new selected acceptance.
