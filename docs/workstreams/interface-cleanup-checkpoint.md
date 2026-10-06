# Interface-cleanup workstream checkpoint

Checkpoint scope: recovery of interrupted Worker 14 cross-repository interface-cleanup work before bounded Batch 1 executor-only completion.

## Recovery method and uncommitted state

This workstream has been performed through the GitHub connector, not through a persistent local Git worktree. The connector exposes committed remote branch state but no separate local working tree or Git index. Therefore:

- no uncommitted local changes are observable in this environment;
- every change listed below is already committed and pushed to its named remote branch;
- no branch was reset, recreated, force-moved or discarded during recovery;
- no existing work was duplicated.

No open pull request existed for any recovered work branch at checkpoint time.

## Dependency state

The accepted hub release lock remains unchanged at `8d1155d337f2b572ed829a9945d6b7ccae11b8be`. No proposed dependency pin has been written into the hub lock.

Proposed work branches currently reference these dependency heads where noted:

- Moltbot Safe proposed executor producer head: `054e92d12ccb0bc756ca6652f39fc13b51e05d9b`.
- Replay proposed producer-profile head: `710ceb5667762a5e8f3a7b02e14c40eb8e1a9379`.
- ODES proposed consumer head: `aa7c53d3ad8c1d0b9c42620e9c8e2b99cd203873`.
- Evidence Pack still checks out accepted GAX/IMX revision `9ad378145d326799e3209136e47e82d66c6f69af`; it does not yet consume the interrupted Alvorada branch.
- Alvorada's interrupted branch CI currently pins Moltbot `054e92d...`, Replay `710ceb56...`, accepted Evidence Pack `c699c1fb...`, and ODES `a501f12f...`. Those pins are preserved for a later batch.

## cogno-us/moltbot-safe

- Branch: `worker14/executor-producer-profile`
- PR: none at checkpoint time.
- Starting commit: `bd61f03fd0784fcc34fcd05b77be109214180e0c`
- Current commit: `054e92d12ccb0bc756ca6652f39fc13b51e05d9b`
- Uncommitted changes: none observable; all recovered edits are pushed.
- Completed work:
  - added `engine/producer_contract.py`;
  - defined executor producer profile ID `urn:cognous:profiles:moltbot-safe-executor-producer`, version `1.0.0`;
  - separated interface/profile version from repository revision and source-asserted versus independently-established provenance;
  - exported execution envelope/result, effects, attempts, append-only attempt events and observations;
  - producer export does not construct authority, approvals, grants, resolver or execution policy;
  - documented legacy unversioned consumer behavior as historical/revision-pinned rather than relabeled;
  - added focused producer-contract tests and README/docs references.
- Tests actually executed:
  - Python safety boundary run `37485510869` at exact head `054e92d...`: **success**.
  - Workflow Sanity run `37485510912` at exact head `054e92d...`: **success**.
  - General CI run `37485511133` at exact head was **queued** at checkpoint recovery.
  - Earlier Python safety run `37484384306` on intermediate head failed because the new test called `LocalDestinationExecutor.execute` instead of `execute_snapshot`; corrected in `054e92d...`.
  - No separate local pytest execution was performed in this connector-only recovery.
- Outstanding blocker:
  - Batch 1 still needs focused proof that supported runtime imports require no upstream test directories and that authority remains explicit caller-supplied; exact-head Python safety should be rechecked after those tests.
- Next required action:
  - finish only the public executor/runtime producer surface and focused tests on this same branch; open/reuse a review PR for this branch; do not advance downstream pins in Batch 1.

## cogno-us/alvorada

- Branch: `worker14/gax-public-runtime-artifacts`
- PR: none.
- Starting commit: `e0b2495fea66fe5d7446745b3387b473625c55de`
- Current commit: `b03b8ae535c7558c3eea0b4c3c5f8fb67822f492`
- Uncommitted changes: none observable; all recovered edits are pushed.
- Completed work:
  - began replacing GAX test-helper loading with the Moltbot public producer/runtime surface and public Control Plane runtime modules;
  - moved synthetic resolver/policy construction into an explicitly named synthetic fixture module;
  - began versioned retained-artifact export and governed-transport result retention;
  - added public-runtime/artifact regressions;
  - removed a legacy import-time recovery monkeypatch;
  - preserved explicit caller-supplied resolver/policy requirements.
- Tests actually executed:
  - Tests run `37488220150` at exact head `b03b8ae...`: **failure**.
  - Python 3.12 result: **66 passed, 3 failed**.
  - Failing tests:
    - `test_checkpoint_after_destination_commit_recovers_original_effect_without_replacement`;
    - `test_checkpoint_recovery_with_changed_policy_does_not_issue_replacement_refund`;
    - `test_replay_odes_failure_after_commit_retries_evidence_without_repeating_effect`.
  - All three currently report checkpoint recovery status `dispatched` where existing tests expect `reconciled`.
  - Python 3.11 matrix job was cancelled after the failure.
- Outstanding blocker:
  - checkpoint recovery/result-status compatibility remains incomplete; later batch must reconcile retained original/derivative artifact semantics without effect re-execution.
- Next required action:
  - resume only in a later Alvorada batch from `b03b8ae...`; do not modify in Batch 1.

## cogno-us/cognous-agent-replay-bundle

- Branch: `worker14/executor-profile-v1`
- PR: none.
- Starting commit: `548523e587ec32c87ea079618e042ecfbe6de637`
- Current commit: `710ceb5667762a5e8f3a7b02e14c40eb8e1a9379`
- Uncommitted changes: none observable; all recovered edits are pushed.
- Completed work:
  - added versioned executor producer-profile handling;
  - retained explicit legacy unversioned compatibility pinned to Moltbot `6b0ba118...`;
  - versioned path validates profile ID/version, repository revision, source-asserted provenance, envelope/result/effect/attempt bindings and observations;
  - historical unversioned records are not relabeled;
  - pinned integration test now exports through the public producer contract;
  - added migration documentation.
- Tests actually executed:
  - Tests run `37487369699` at exact head `710ceb56...`: **success**.
  - Workflow runs `pytest -ra`, pinned integration checks, example generation on Python 3.12, and `arb check-examples` across Python 3.11/3.12.
- Outstanding blocker:
  - none within Replay itself at checkpoint; downstream dependency chain remains unaccepted/proposed.
- Next required action:
  - preserve branch unchanged in Batch 1; later batch should review and open its dependency-ordered PR after executor acceptance.

## cogno-us/cognous-agent-governance-evidence-pack

- Branch: `worker14/executor-profile-v1`
- PR: none.
- Starting commit: `a9aca055e18e5b35cee356c224a146138ebbd948`
- Current commit: `ddbabedd8bde4359a4eb6ad5123746800b3f262c`
- Uncommitted changes: none observable; all recovered edits are pushed.
- Completed work:
  - began consuming Replay's versioned executor producer-contract metadata;
  - preserves legacy Moltbot `6b0ba118...` compatibility separately;
  - proposed new Moltbot revision requires producer-profile `1.0.0`;
  - advanced proposed Replay/Moltbot/ODES CI pins while deliberately leaving GAX on accepted revision `9ad378145...`;
  - added migration documentation and compatibility tests.
- Tests actually executed:
  - Tests run `37488340425` at exact head `ddbabedd...`: **failure**.
  - Python 3.12 result: **152 passed, 1 failed**.
  - Failing test: `test_traceability_preserves_producer_revision_and_provenance_status`; Control Plane revision is currently marked `declared_revision_conflicts_with_accepted_pin` where the test expects `declared_revision_matches_accepted_pin`.
  - Python 3.11 matrix job was cancelled after the failure.
- Outstanding blocker:
  - accepted-pin comparison representation needs correction/reconciliation in a later Evidence Pack batch; GAX proposed head is intentionally not yet pinned.
- Next required action:
  - preserve branch unchanged in Batch 1.

## cogno-us/open-decision-evidence-standard

- Branch: `worker14/executor-profile-v1`
- PR: none.
- Starting commit: `7a6b4108369c07dbf9c1144087c92ce8e8540873`
- Current commit: `aa7c53d3ad8c1d0b9c42620e9c8e2b99cd203873`
- Uncommitted changes: none observable; all recovered edits are pushed.
- Completed work:
  - updated proposed Replay/Moltbot compatibility pins;
  - ODES exporter preserves versioned executor producer provenance when reconstructing Replay validation input;
  - documented legacy-versus-versioned migration.
- Tests actually executed:
  - Tests run `37487445723` at exact head `aa7c53d3...`: **success** across Python 3.11/3.12.
- Outstanding blocker:
  - no ODES-local blocker recorded; dependency chain is still proposed/unmerged.
- Next required action:
  - preserve branch unchanged in Batch 1; review in later dependency-order batch.

## cogno-us/cognous-open-control-stack

- Branch: `worker14/interface-debt-closure`
- PR: none.
- Starting commit: `8d1155d337f2b572ed829a9945d6b7ccae11b8be`
- Current commit before this checkpoint: `8d1155d337f2b572ed829a9945d6b7ccae11b8be`
- Uncommitted changes: none observable.
- Completed work before checkpoint:
  - no proposed lock change or hub integration change had been committed on this branch.
  - accepted release lock remains the merged reference-candidate lock.
- Tests actually executed:
  - accepted head reference-release workflow run `37483856363`: **success**.
  - no new interface-cleanup hub gate has been run because proposed dependency pins have not been written.
- Outstanding blocker:
  - hub update must wait for dependency-order batches; accepted lock must remain unchanged.
- Next required action:
  - after this checkpoint commit, make no further hub changes in Batch 1.

## Batch 1 boundary

After this checkpoint is committed, Batch 1 work is restricted to `cogno-us/moltbot-safe`.

Do not modify Alvorada, Replay, Evidence Pack, ODES or hub dependency pins until a later bounded batch.


## Batch 1 final producer-export correction

Scope remained limited to `cogno-us/moltbot-safe` plus this checkpoint update.

### Moltbot Safe PR #9 final producer-export state

- PR: https://github.com/cogno-us/moltbot-safe/pull/9
- Previous Batch 1 head: `452736994f4b68d23c3912a530567e1022e82653`
- Revised head: `2ab64e1a9d4e77530903ce73a2b362f81390f184`
- Producer profile remains:
  - ID: `urn:cognous:profiles:moltbot-safe-executor-producer`
  - version: `1.0.0`

Correction completed:

- `export_execution_artifacts()` now snapshots the caller envelope first and serializes that validated frozen snapshot rather than rereading mutable caller-owned envelope data later.
- The supplied frozen operation is bound to retained destination evidence through the durable `operation_digest`.
- Retained effect evidence is additionally checked for grant, target, amount, unit and payload consistency.
- Retained attempt evidence is checked for decision, effect and operation-digest consistency.
- A result `attempt_id` must resolve to a retained bound attempt when one is claimed.
- Observation destination state is checked against the frozen effect/operation binding where fields are present.
- Contradictory changed amount, target or payload under unchanged decision/effect IDs is rejected.
- Payload substitution remains rejected even when the caller recomputes a matching payload commitment for the substituted payload.
- Caller-owned nested mutation occurring during export does not alter the serialized execution envelope because the exporter serializes the pre-mutation validated snapshot.
- Legitimate success, unknown/lost-ack, partial, restart/historical-observation and denied exports remain supported.
- Denied exports do not fabricate effects, attempts, events or observations that do not exist.
- Historical observation exports retain pre-existing attempt/effect evidence without fabricating a new observation attempt.
- Producer-side checking supplements rather than replaces Replay/consumer semantic validation.

Focused regressions added for:

- changed amount under unchanged decision/effect identity;
- changed target under unchanged decision/effect identity;
- changed payload with recomputed payload commitment;
- nested caller-data mutation during export;
- valid success export;
- lost-ack/unknown export;
- partial export;
- restart/historical-observation export;
- denied export without fabricated destination evidence.

Exact-head execution evidence:

- Python safety boundary run `37490177663` at `2ab64e1a9d4e77530903ce73a2b362f81390f184`: **SUCCESS**.
- Result: **180 passed, 2 skipped in 4.57s**.
- `python -m compileall -q engine examples/openshell`: **SUCCESS**.
- The two existing skips remain outside this producer-export correction; no required producer-export regression was skipped.

No downstream consumer pin, Alvorada, Replay, Evidence Pack, ODES or accepted hub lock change was made in this correction.


## Batch 1 observation/reconciliation producer-export correction

Scope remained limited to `cogno-us/moltbot-safe` plus this checkpoint update.

### Moltbot Safe PR #9 revised state

- PR: https://github.com/cogno-us/moltbot-safe/pull/9
- Previous head: `2ab64e1a9d4e77530903ce73a2b362f81390f184`
- Revised head: `5eb90c0be32c1f6246220f5f7f83881c6c9fc1bd`

Corrections completed:

- Preserved the frozen-operation and retained destination-content validation added in the prior correction.
- Historical observation exports now allow authoritative `observed_state="absent"` with no effect row and no fabricated destination state.
- Historical `observed_state="unknown"` is likewise exportable when no effect evidence exists and the observation does not fabricate destination state.
- Applied/partial observations continue to require retained effect evidence.
- Control Plane reconciliation attempt IDs are no longer interpreted as executor/destination attempt IDs.
- `PinnedControlPlaneExecutor` now includes the actual Control Plane attempt record in reconciliation observation metadata as explicitly attributed Control Plane evidence.
- Producer export validates that Control Plane attempt evidence matches the result attempt ID, decision ID and effect ID.
- Export emits an explicit `attempt_identity` namespace:
  - `executor` for retained destination attempts;
  - `control_plane` for reconciliation attempts owned by the pinned Control Plane.
- Export emits `control_plane_attempts` separately from destination `attempts`.
- Dangling/unattributed attempt references remain rejected.
- Fabricated Control Plane attempt references remain rejected.
- No attempt namespace is collapsed or relabeled.

Focused regressions added:

- historical absence observation with empty destination;
- historical unknown observation without fabricated effect;
- actual pinned `BoundedAuthorizationWorkflow` + `PinnedControlPlaneExecutor` successful execution followed by duplicate/reconciliation;
- distinct Control Plane versus executor attempt namespaces;
- exactly one durable destination effect after reconciliation;
- fabricated Control Plane attempt identity rejection;
- dangling unattributed attempt rejection.

Execution status:

- Exact-head Python safety workflow run `37491115286` for `5eb90c0be32c1f6246220f5f7f83881c6c9fc1bd` was created successfully.
- At checkpoint time its `safety-tests` job `112363839103` is **QUEUED**.
- No pass is claimed yet for this head.
- The focused regressions are included in the Python safety test selection; no separate local execution result is claimed in this connector-only environment.

No Alvorada, Replay, Evidence Pack, ODES, downstream dependency pin, accepted hub lock, deployment or production infrastructure change was made.


## Batch 1 CI import repair

Scope remained limited to `cogno-us/moltbot-safe` plus this checkpoint update.

### Moltbot Safe PR #9 final CI repair

- PR: https://github.com/cogno-us/moltbot-safe/pull/9
- Previous head: `5eb90c0be32c1f6246220f5f7f83881c6c9fc1bd`
- Revised head: `c0a904508bc987639ec1e1640e00c82ed32d4ac3`

Correction completed:

- Added missing `copy` import in `tests/test_safe_executor.py`.
- Added missing `ExecutionResult` import in `tests/test_safe_executor.py`.
- No runtime code changed in this repair.
- Operation-binding, authoritative absence/unknown observation handling, and Control Plane/executor attempt-namespace corrections remain unchanged.

Previously blocked tests now execute:

- `test_export_historical_unknown_observation_without_fabricated_effect`;
- `test_export_rejects_fabricated_control_plane_attempt_reference`;
- `test_export_rejects_dangling_unattributed_attempt_reference`.

Exact-head execution evidence:

- Python safety boundary run `37492075608` at `c0a904508bc987639ec1e1640e00c82ed32d4ac3`: **SUCCESS**.
- Result: **185 passed, 2 skipped in 4.83s**.
- `python -m compileall -q engine examples/openshell`: **SUCCESS**.
- Pinned Control Plane revision verified by CI: `283500652d47a692fb0b99a1172a6d5faffbd9a7`.
- Pinned Action Manifest revision verified by CI: `46c950bed37fe3812000895430bc0312d29e37ce`.

No downstream consumer, dependency pin, Alvorada, Replay, Evidence Pack, ODES or accepted hub lock change was made.
