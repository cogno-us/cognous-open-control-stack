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
