# S3 — restore-boundary lane C

Characterization completed; **full-destination restore prevention BLOCKED**.
No independently administered monotonic anchor is available or qualified here.
A passing limitation reproduction is not a passing safety invariant. Operational
trust remains **HOLD / NOT ESTABLISHED**; release and production authorizations
remain false. C0 retains its check-to-commit limitation. Optional C1 is cooperating
same-host SQLite only; no C2/C3, real settlement, or deployment acceptance follows.

## Recorded baseline and ownership

Base: `592919dd95396f3f6164cf0ceec1fd15c065691b` (live main inspected
2026-10-15). PR #116 is merged; open PR #117 was documentation only at intake.
No repository AGENTS.md was present. Read component-lock.json, all four existing
profile JSONs, adversarial-review-remediation-2026-10-15.md, ProtectedDestination,
its tests, AssuranceRuntime persistence, optional_execution/optional_execution_profile,
Worker 21 qualification, optional-execution-profiles.md, and the independent
artifact-inspection record (historical optional C1 population: 73).

ProtectedDestination baseline SHA-256:
`e6f024d75783fc806bfbefa251e46f23a6614a78d845e4c91f2ca2f21292b1f9`.
component-lock.json SHA-256:
`dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`.
These tests do not promote or alter any selection. Optional C1 uses the actual
`atomic-authority-effect` implementation at the component-lock pins through the
existing optional runner: Control Plane `d3dadee70bd319812b207389ab1e0f6efe511916`,
executor `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac`. Those optional pins are
separate from the bounded-v1 release selection's newer component population.
All five dependency pins and the lock digest are retained in each C1 case JSON.
The historical 73-test campaign is context, not rerun or added to S3 totals.

S2 owns `reference_profiles/protected_destination.py`. S3 owns only its new test,
workflow and this report. Coordinator must rerun at the integrated source after
S2 merges; the baseline results cannot qualify S2's changes. No central control
panel, runtime, existing tests, component lock or selection profile is modified.

## Method and actual observations

Tests use SQLite's backup API to create and restore complete consistent databases
with callers quiescent and connections closed, then construct fresh runtime
objects and perform admission again. This is process-object restart with database
reopen, not a machine reboot or power-loss qualification. Every case repeats
admission after another reopen to check persistence. Authority-only restore uses
an explicitly written/restored authority-side pending-command JSON fixture, or
serialized resolver contexts for C1; it is not a complete institutional authority
service restore. All actual destination tables are captured before restore,
after restore and after admission. Restored database contents must equal the
snapshot contents. No direct database edits manufacture the unsafe outcomes.

An append-only test JSONL witness sits **outside the destination restore set**.
After every admission, the harness compares committed effect rows before/after
and records each newly observed commit. It never supplies admission decisions.
It is an observer, **not a production anti-rollback control**; it does not attest
external settlement, handle host compromise or detect unobserved crashes. The
single-caller quiescent experiment permits exact cumulative local observations.
Full restore can erase a prior effect row; its current row count is not a count
of all historical commits. Keys/registry and clock remain trusted and unchanged.
A fixed time of 100 intentionally tests replay inside the verifier's valid window.
No clock rollback is needed for these failures.

| Case / snapshot and restore scope | Expected = observed admission after restore | State transition / cumulative observed effects | Audit survival | Interpretation |
| --- | --- | --- | --- | --- |
| Authority pending queue only; destination fence advanced 7→8 | `AUTHORITY_STORE_BEHIND_FENCE` | Fence 8 survives; 0 effects | Fence event survives; denial appended | Conditional protection |
| Authority pending queue only; destination revoked grant | `CREDENTIAL_BINDING_CLOSED` | Revoked/inactive binding survives; 0 effects | Revocation survives; denial appended | Conditional protection |
| Authority pending queue only; destination consumed command/grant | `COMMAND_REPLAY` | Consumption, command and effect survive; 1 historical effect | Original acceptance survives | Conditional protection |
| Full destination snapshot before fence advance | Accepted, `duplicate=false` | Fence 8→7; stale signed generation 7 commits; 1 effect | Advance and denial erased; new acceptance retained | Limitation |
| Full destination snapshot before revocation | Accepted, `duplicate=false` | Revoked true→false; inactive→active; 1 effect | Revocation and denial erased | Limitation |
| Full destination snapshot before consumption/command acceptance; original ACK discarded | Accepted, `duplicate=false` | Consumed 1→0→1; effect rows 1→0→1; **2 historical commits** | First acceptance erased; second retained | Limitation |
| Current destination lost ACK, then full postcommit snapshot restore | Old command `COMMAND_REPLAY`; new exact-effect command accepted `duplicate=true` | Consumed/closed binding and original effect survive; **1** historical commit | Original acceptance survives; post-snapshot refusal erased | Conditional protection, not permission for new effect |
| Full snapshot before accepting signed admin command; later v2 view overwritten | Old admin command accepted inside 60-unit window | Sequence/command memory lost; restored v1 view becomes v0; 0 effects | v0/v2 acceptances and replay denial erased | Limitation; trusted clock at 161 separately rejects unseen old command `COMMAND_STALE` |
| C1 resolver context restore only after destination revocation | Denied, no new effect | Revoked authoritative grant survives; claim issued; 0 effects | Destination tables preserved | Conditional same-host protection |
| Full C1 snapshot before revocation | Executed, new effect | Grant active again; issued claim consumed; 1 effect | Post-snapshot destination records lost | Same-host limitation |
| Full C1 snapshot before consumption, original ACK discarded | Executed, new effect | Claim consumed→issued→consumed; budget use rolls back; **2 historical commits** | Original attempt/effect/consumption lost | Same-host limitation |
| Full C1 postconsumption snapshot | Denied, no new effect | Consumed claim/effect retained; **1** historical commit | Original attempt/effect retained | Conditional same-host protection |

For every row, another runtime reopen preserves the resulting refusal/replay
boundary and adds no effect. C1's postconsumption `denied` is its executor result;
retained reconciliation evidence, rather than a fresh execution, identifies the
original effect. The C1 cases assert observed committed-row changes against
`newly_executed`. No distributed-system conclusion is drawn.

## Concrete external-anchor contract (implementation requirement, not delivered runtime)

The smallest conservative contract trades availability for restore safety. It
requires an authenticated linearizable external ledger for each destination
scope, a cooperative destination adapter, and explicit recovery. A counter stored
in this SQLite database, a companion file restored with it, a local hash chain,
or a test fake cannot satisfy the contract.

1. **Identity and monotonic state.** Anchor key is immutable
   `(institution_id, authority_domain, destination_id, scope_id, anchor_instance_id)`.
   Names cannot be rebound or silently reset after deletion. Store unsigned bounded
   monotonic `authority_generation` and `transition_sequence` (reject overflow),
   authority/revocation digest, committed local-state commitment, and unresolved
   reservation records. A reservation binds predecessor sequence/commitment,
   request digest, command identity/admin sequence, grant/version, effect identity,
   payload digest, new sequence and unique reservation ID. An effect/command
   identity may not be reallocated to a different payload or reservation.
   An independently durable identity registry or retained tombstones must outlive
   every restorable snapshot; expiry cannot recreate replay permission.
2. **Authentication and ownership.** Mutually authenticated workloads use
   scope-specific reserve/read/complete rights; administration, generation advance,
   key rotation and recovery use separate independently owned credentials and
   approved change records. Signed anchor receipts bind identity, complete state,
   caller nonce and key version. Verify independent trust roots and live
   authenticated reads; an old signed receipt is not evidence of current state.
   Destination operators cannot lower, erase or restore the anchor. Administrative
   separation requires evidence, not distinct role names in a local registry.
3. **Restore independence.** Anchor storage, replicas, administrative credentials,
   backups and disaster recovery must not roll back with destination or authority
   snapshots. Anchor recovery must preserve its high-water state and tombstones
   through independently retained evidence. If that cannot be established, block
   activation and effects. Copying an anchor alongside a DB is not independence.
4. **Ordering and concurrency.** Before any new authority mutation or effect,
   authenticate a current read and atomically compare-and-reserve the exact
   predecessor local commitment, scope generation and sequence. A single
   linearizable CAS serializes cooperating writers; only one reservation may be
   outstanding per scope in this minimal design. Anchor durably reserves before
   the local writer transaction applies its bound mutation/effect and receipt.
   Local commit atomically stores the receipt, new state commitment, consumption,
   command memory, effect and audit evidence. Complete externally only after
   durable local commit; block further admission until completion is reconciled.
   Readers cannot authorize from cached anchor state. Authority invalidations use
   the same order. Define reservation as the authorization linearization point:
   a subsequent revocation cannot erase a previously committed effect or silently
   cancel a pending reserved effect. Revocation acknowledgement must disclose
   outstanding reservations and require resolution before claiming a drained stop.
   Stronger revocation-at-local-commit semantics need an additional supported
   fencing/commit protocol; a precommit anchor read alone has a race.
5. **Mismatch and failure.** Unavailable, unauthenticated, wrong-scope, stale,
   lower-generation, conflicting or inconsistent anchor responses mean HOLD with
   no new effect. Local predecessor mismatch, local-ahead or anchor-ahead state,
   missing receipt, and unknown reservation are recovery conditions. Never
   automatically copy either side over the other. A bounded non-authorizing
   observation/reconciliation path may operate while effect admission is closed.
6. **Crash windows and disagreement.** Crash before reserve leaves no allocation;
   crash after reserve but before local commit leaves anchor ahead and may have
   no effect; crash after local commit before complete/lost ACK leaves a committed
   effect with an unresolved anchor reservation. A later full DB restore may look
   identical to the first situation. Anchor completion may survive while all local
   evidence of effect disappears. Therefore absence in the restored DB does not
   justify execution or reservation reuse. Freeze uncertain reservations; no
   automatic retry, timeout release, or new effect ID. For liveness, a separately
   qualified downstream idempotency/reconciliation or atomic commit protocol is
   required. This contract does **not** claim cross-system atomicity or exactly-once
   delivery; conservative unresolved HOLD is acceptable.
7. **Authorized recovery.** Quiesce writers and revoke old admission capability;
   collect authenticated anchor history plus independently retained destination
   and external-effect observations. Designated recovery owners approve exact
   scope, old/new generation, snapshot digest, outstanding reservation disposition
   and evidence. Reconstruct safe local state with spent/uncertain identities
   closed; advance generation by CAS; bind activation to that state commitment.
   A disputed/missing effect remains unresolved until authoritative reconciliation.
   Independently audit all recovery actions; do not turn approval of a restore
   into authority to repeat an uncertain effect. Key compromise or lost anchor
   continuity requires a new reviewed trust enrollment, with old scope blocked.
8. **Clock, keys and operators.** Trusted monotonic anchor ordering is independent
   of wall-clock timestamps. Freshness/expiry still require a trusted clock,
   bounded skew and rollback detection, including after restore. Production key
   custody, rotation/revocation, workload identity and root distribution are
   deployment obligations. Assume cooperative untampered admission code and
   protected receipt verification; hostile-host bypass requires another boundary.
   Backups do not restore revoked keys or operator privileges into current trust.

## Acceptance required before prevention can leave BLOCKED

- Independently administered service endpoint and owner attestations; IAM denial
  proving destination/backup operators cannot reset anchor state; actual backup
  inventories and disaster-recovery evidence. A mock API or second process with
  the same restore/admin domain is insufficient.
- Restore the whole destination **and** its local receipts to before revocation,
  consumption, command acceptance and anchor completion. Restart on a fresh
  client. Current anchor must refuse stale state before any new effect. Keep an
  independently administered cumulative effect witness outside both restore sets.
- Exercise anchor node failover/recovery and attempted snapshot rollback; verify
  high-water continuity, tombstones, key changes and old receipt rejection.
- Race two real clients with identical and conflicting predecessor CAS requests;
  exactly one reserves, no fork or scope crossover. Test revocation versus reserve
  and demonstrate documented pending-effect/drained-stop semantics.
- Inject failures before/after reserve, local begin, effect insert, local commit,
  completion and lost ACK; reconnect/restart each side independently. Every
  uncertain interval must retain HOLD until evidence-backed reconciliation.
- Partition/unavailable anchor, stale replica, replayed response, wrong nonce,
  clock rollback/skew, expired/revoked key, wrong tenant and administrative takeover
  attempts must not authorize effects. Demonstrate authorized recovery with
  independent signoff, retained history and no automatic replay of spent work.
- Inspect exact code/deployment versions, service consistency/durability guarantees,
  receipts, effect observations and evidence hashes. A green unit suite is not
  independent deployment acceptance.

## Validation and coordinator dependencies

Commands (run from repository root):

```sh
python -m pip install -r tools/requirements-federated-governance.txt 'pydantic>=2,<3'
PYTHONDONTWRITEBYTECODE=1 RESTORE_BOUNDARY_RESULTS=results/restore-cases python -m pytest -q tests/test_destination_restore_boundary.py tests/test_protected_destination.py --junitxml=results/tests.xml
find results -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > results/SHA256SUMS
```

New restore suite: **12 cases** (8 ProtectedDestination, 4 optional C1).
Local Python 3.12 combined run: **53 test functions passed, 11 unittest subtests
passed**, zero failures/errors/skips. JUnit represents subtests as additional
case elements; use XML totals when comparing hosted artifacts. Initial exploratory
rerun had four dependency-setup errors because Python regenerated tracked upstream
bytecode; enabling dont-write-bytecode and restoring only those generated files
fixed the setup. No dependency source was changed. Local Python 3.11 is unavailable;
the immutable-action workflow runs both 3.11 and 3.12 and checks out the PR head
rather than the synthetic merge. Per-case JSON, full state, source revision,
source/dependency hashes, JUnit and SHA256SUMS are uploaded at that head.

Runtime dependency proposal for coordinator: ProtectedDestination and optional
C1 need a reviewed anchor admission/recovery adapter covering **all** administrative
and effect entry points, plus local receipt persistence and reconciliation.
ProtectedDestination's `apply`, `op_fence`, `op_revoke`, `op_execute` and schema are
S2-owned paths: do not patch them in S3. The C1 owner must separately update its
provisioning, status writers, atomic claim execution and recovery interfaces.
A local-only counter, freshness timestamp or hash chain will not close this gap.
Anchor provisioning, key custody, trusted time, backup independence and independent
acceptance remain unresolved. Completed characterization does not close prevention.
