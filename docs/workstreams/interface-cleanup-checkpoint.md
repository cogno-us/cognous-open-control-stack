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


## Batch 2 — Alvorada runtime integration and original-artifact retention

Scope was limited to `cogno-us/alvorada` plus this durable checkpoint update. Replay, Evidence Pack, ODES and the accepted hub lock were inspected but not modified.

### Alvorada PR #5

- PR: https://github.com/cogno-us/alvorada/pull/5
- Preserved Batch 2 starting head: `b03b8ae535c7558c3eea0b4c3c5f8fb67822f492`
- Final Batch 2 head: `62f16348f3127af8d663dd7719d25dddd6f9ac70`
- Base/main observed at Batch 2 start: `e0b2495fea66fe5d7446745b3387b473625c55de`
- Unaccepted Alvorada PR #2 was not incorporated.

### Accepted executor dependency

- Moltbot Safe accepted merge: `1d308faf664c504b6e310db3c7a310153ef7b067`
- Public runtime modules used:
  - `engine.control_plane_adapter.PinnedControlPlaneExecutor`
  - `engine.producer_contract`
- Executor producer profile:
  - ID: `urn:cognous:profiles:moltbot-safe-executor-producer`
  - version: `1.0.0`

Alvorada now source-asserts the accepted merged Moltbot repository revision. It does not relabel the producer as the pre-merge feature revision.

### Supported Alvorada interfaces

GAX retained-artifact export:

- profile: `urn:cognous:profiles:gax-retained-artifacts`
- version: `1.0.0`

Governed transport recipient result:

- profile: `urn:cognous:profiles:governed-message-recipient-result`
- version: `1.0.0`

Existing transport remains:

- profile: `urn:cognous:profiles:governed-message-transport:0.1.0`
- transport version: `0.1.0`

### Completed runtime integration work

- Supported GAX runtime loads public Moltbot producer/executor modules and public Control Plane modules rather than executor test helpers.
- Runtime requires an explicit caller-supplied trusted resolver and explicit execution-policy factory.
- Synthetic resolver/grant/policy construction remains in the explicitly named `synthetic_fixture.py` example/test fixture.
- Incoming proposal content does not create institutional authority.
- Added a runtime regression that blocks the `tests.*` import namespace and executes through public executor modules successfully.
- Runtime dependency constants/CI now point to accepted Moltbot merge `1d308faf...`.

### Original-artifact retention

The versioned GAX export retains, when produced:

- original Reconstruction Bundle;
- ODES package;
- ODES recipient-validation result;
- complete IMX successor packet;
- producer decision/effect/attempt identity references;
- explicit content commitments for Reconstruction, ODES package, recipient validation and successor packet.

Artifact identity is bound to content. Validation rejects reconstruction, ODES, validation or successor digest/commitment substitution.

Successor packet content is complete before its packet digest is calculated and is revalidated when the retained export is loaded.

Transport exposes supported retrieval methods:

- `LocalDurableTransport.retained_result(message_id)`
- `LocalDurableTransport.retained_artifacts(message_id)`

Consumers do not need direct SQLite access for normal retained-artifact retrieval.

### Interruption and recovery semantics

- Workflow association and retained artifact export are persisted atomically in the GAX exchange store.
- Recipient assessment/execution metadata and retained artifact export are persisted atomically in the transport recipient store.
- `original_complete`: original generated artifacts were durably retained.
- `recovery_required`: effect/recipient processing completed but complete retained artifacts are not yet available.
- `regenerated_derivative`: evidence regenerated from retained Control Plane/executor records after an interruption, with distinct identity/lineage and `effect_reexecution=false`.
- `historical_artifacts_unavailable`: legacy transport outcome exists without a retained versioned artifact set.
- Recoverable incomplete artifact retention receives a retryable unresolved transport receipt rather than a false complete acknowledgement.
- Evidence-only checkpoint recovery does not invoke a replacement effect.
- Exact duplicate delivery returns the retained original artifacts when available.
- Dispatch-checkpoint lifecycle state is no longer confused with execution result status; an executed checkpoint recovered for evidence is reported as `reconciled`.
- Control Plane and executor attempt identities are retained in the namespaces declared by the accepted Moltbot producer profile; they are not collapsed.

### Batch 2 regressions added/preserved

Focused tests cover:

- successful delivery and supported original-artifact retrieval;
- exact duplicate returning the same original artifact identities;
- lost acknowledgement/restart path;
- post-effect interruption before artifact persistence;
- evidence-export failure followed by evidence-only recovery;
- regenerated derivative lineage with no replacement effect;
- partial delivery with one durable effect;
- denied outcome with zero effects and retained evidence;
- GAX artifact digest substitution;
- transport retained-artifact substitution;
- legacy transport record lacking retained artifacts;
- runtime import/execution with `tests.*` unavailable;
- explicit producer content commitments;
- producer attempt namespace preservation.

### Exact dependency pins used by Batch 2 CI

Accepted dependencies:

- Action Manifest: `46c950bed37fe3812000895430bc0312d29e37ce`
- Authority Context: `fb3d97938969a89e149e8ff8db2756091d1233fc`
- Control Plane: `283500652d47a692fb0b99a1172a6d5faffbd9a7`
- Moltbot Safe: `1d308faf664c504b6e310db3c7a310153ef7b067`
- Governance Evidence Pack checkout remains accepted `c699c1fb7c4f8057631c4e5909d11a721c2c958d` where present.

Proposed consumer dependencies used only for integration testing:

- Replay: `710ceb5667762a5e8f3a7b02e14c40eb8e1a9379`
- ODES: `aa7c53d3ad8c1d0b9c42620e9c8e2b99cd203873`

### Final-head CI result and explicit blocker

Final-head Tests workflow:

- run: `37494701834`
- Alvorada head: `62f16348f3127af8d663dd7719d25dddd6f9ac70`
- Python 3.12: **45 passed, 32 failed**
- Python 3.11: cancelled after matrix failure.

All 32 failures have the same downstream contract cause:

`agent_replay_bundle.importers.ImportContractError: unsupported Moltbot producer repository revision`

Replay proposed head `710ceb56...` recognizes producer profile 1.0.0 but requires Moltbot repository revision:

`054e92d12ccb0bc756ca6652f39fc13b51e05d9b`

The accepted executor dependency is:

`1d308faf664c504b6e310db3c7a310153ef7b067`

Alvorada intentionally emits the accepted merged revision. Validation was not weakened and the producer was not relabeled to obtain green CI.

The immediately preceding code-head run also exposed a generic transport regression caused by treating all artifact-less generic recipient outcomes as incomplete GAX results. That Alvorada defect was corrected before final head by limiting recovery-required artifact semantics to explicit recipient result states. The final-head failure list contains only the Replay revision incompatibility.

### Outstanding Batch 2 blocker

A compatible Replay consumer revision is required before the complete GAX -> Replay -> ODES artifact pipeline can pass.

Required downstream action for the next consumer batch:

1. update Replay's versioned producer-profile compatibility to accept the merged Moltbot revision `1d308faf...` while preserving legacy revision-pinned handling;
2. keep producer profile/version validation and operation/attempt semantic validation intact;
3. then update ODES compatibility to the accepted Replay/Moltbot revisions as required;
4. rerun Alvorada PR #5 against those exact accepted/proposed consumer heads.

No consumer repository was modified in Batch 2. No accepted hub lock was changed. No deployment, public-chain write, paid infrastructure, rename, DOCX edit or self-merge occurred.


## Batch 3A — Replay consumer compatibility

Scope was limited to `cogno-us/cognous-agent-replay-bundle` plus this durable checkpoint update. Alvorada, ODES, Evidence Pack and the accepted hub lock were not modified.

### Replay PR #7

- PR: https://github.com/cogno-us/cognous-agent-replay-bundle/pull/7
- Preserved starting head: `710ceb5667762a5e8f3a7b02e14c40eb8e1a9379`
- Final head: `3fb6921c3e13be2426074b59431e4bf51250c65e`
- Base/main at PR creation: `548523e587ec32c87ea079618e042ecfbe6de637`

### Accepted producer mapping

Versioned executor consumer contract:

- repository: `cogno-us/moltbot-safe`
- accepted revision: `1d308faf664c504b6e310db3c7a310153ef7b067`
- producer profile ID: `urn:cognous:profiles:moltbot-safe-executor-producer`
- profile version: `1.0.0`
- execution envelope version: `0.2.0`

Legacy unversioned compatibility remains revision-pinned to:

`6b0ba1185bcd390f71df947dda349415e4105f5f`

The pre-merge versioned feature revision `054e92d12ccb0bc756ca6652f39fc13b51e05d9b` is no longer accepted as interchangeable with the merged producer revision. Historical artifacts are not relabeled.

### Replay semantic validation completed

Replay now validates:

- frozen execution envelope against the retained RuntimeProposal and Control Plane authorization binding;
- payload commitment and operation content;
- destination effect identity, operation digest, grant, target, amount, unit and payload;
- executor attempt decision/effect/operation binding;
- append-only attempt events resolving to retained executor attempts;
- executor observations and destination-state binding;
- explicit `attempt_identity`;
- separately attributed `control_plane_attempts`;
- producer profile/version, repository revision and source-asserted provenance consistency.

Attempt namespace behavior:

- `executor` attempts must be owned by `cogno-us/moltbot-safe` and resolve to retained destination attempt records.
- `control_plane` attempts must be owned by `cogno-us/cognous-agent-control-plane`.
- A supplied Control Plane attempt is accepted only when its complete producer-supplied object exactly matches the retained Control Plane run record for that attempt ID, decision and effect.
- Matching attempt labels or IDs alone do not establish lineage.
- Control Plane and executor attempt namespaces remain distinct.

Supported legitimate outcomes include:

- successful execution;
- duplicate/restart reconciliation;
- lost acknowledgement;
- partial delivery;
- historical `absent` observation with no effect row;
- historical `unknown` observation with no fabricated effect;
- denied/no-effect result.

Rejected conditions include:

- unsupported producer profiles or profile versions;
- unsupported repository revisions;
- contradictory repository provenance;
- operation-content substitution;
- payload/amount/target contradictions;
- dangling executor attempt identities;
- fabricated/dangling Control Plane attempts;
- wrong namespace owner;
- Control Plane attempt namespace used as newly executed effect evidence;
- denied result with retained destination effect evidence;
- applied/partial observation without required destination effect evidence.

### Actual accepted-executor integration coverage

Pinned integration now executes against:

- Control Plane: `283500652d47a692fb0b99a1172a6d5faffbd9a7`
- Moltbot Safe: `1d308faf664c504b6e310db3c7a310153ef7b067`
- Action Manifest: `46c950bed37fe3812000895430bc0312d29e37ce`
- Authority Context/Alvorada implementation source: `fb3d97938969a89e149e8ff8db2756091d1233fc`

The pinned tests generate producer exports through the actual accepted Moltbot executor/producer contract and cover:

- success;
- decision hold;
- execution-time denied revalidation;
- lost acknowledgement;
- duplicate/restart reconciliation;
- partial delivery;
- stale required evidence denial;
- historical absence observation.

The reconciliation test verifies:

- exactly one durable destination effect;
- producer `attempt_identity.namespace == "control_plane"`;
- Control Plane reconciliation attempt ID is distinct from retained executor attempt IDs;
- the same Control Plane attempt ID is present in the retained Control Plane run record;
- Replay imports an explicitly attributed Control Plane attempt record with an explicit link to the owning run record.

### Tests and CI

Code head `004469d67730a015228128274c6d7b92596200df`:

- workflow `37495623056`;
- Python 3.11: **161 passed**;
- Python 3.12: **161 passed**;
- generated reconstruction examples: **success**;
- example validation: **success**;
- prior tamper, lineage, redaction, signing and integrity regressions remained in the full suite.

Final documentation head `3fb6921c3e13be2426074b59431e4bf51250c65e`:

- push workflow `37495685193`: **SUCCESS**;
- Python 3.11 job `112379492853`: **SUCCESS**;
- Python 3.12 job `112379492634`: **SUCCESS**.
- PR dynamic workflow `37495773516` was queued when the final-head push workflow had already completed successfully.

### Remaining incompatibilities

No Replay-local incompatibility remains for the accepted Moltbot producer profile/revision.

Downstream work remains intentionally deferred:

1. ODES still needs its compatibility pins/Replay-validation path advanced to the accepted Replay/Moltbot mapping.
2. Evidence Pack still needs the same consumer-chain update and its preserved provenance-status test correction.
3. Alvorada PR #5 must then rerun against the revised Replay/ODES heads.
4. The accepted hub lock remains unchanged until the dependency chain is reviewed/accepted.

No Alvorada, ODES, Evidence Pack or hub dependency pin was modified in Batch 3A. No self-merge occurred.


## Batch 3B — ODES compatibility

Scope was limited to `cogno-us/open-decision-evidence-standard` plus this durable checkpoint update. Evidence Pack, Alvorada and the accepted hub lock were not modified.

### ODES PR #23

- PR: https://github.com/cogno-us/open-decision-evidence-standard/pull/23
- Preserved starting head: `aa7c53d3ad8c1d0b9c42620e9c8e2b99cd203873`
- Final head: `d5b8954f401cb6b7bfcd755b2477a4289c66c9bf`
- Base/main at PR creation: `7a6b4108369c07dbf9c1144087c92ce8e8540873`

### Accepted compatibility mapping

- Replay: `f63ce914504dd06813c4ccd199b0570dbd8dd427`
- Moltbot Safe: `1d308faf664c504b6e310db3c7a310153ef7b067`
- producer profile ID: `urn:cognous:profiles:moltbot-safe-executor-producer`
- producer profile version: `1.0.0`
- execution envelope version: `0.2.0`

Historical unversioned executor evidence remains a Replay-managed legacy path pinned to:

`6b0ba1185bcd390f71df947dda349415e4105f5f`

ODES does not relabel historical artifacts as versioned producer-profile evidence.

### ODES compatibility work completed

- Updated ODES accepted pins for Replay and Moltbot Safe.
- Replay semantic revalidation input reconstruction now preserves:
  - executor destination attempts;
  - separately attributed Control Plane attempts;
  - executor observations;
  - accepted producer profile/repository/source-asserted provenance.
- For versioned Replay output, `execution_result.attempt_id` must resolve to exactly one validated attempt namespace.
- Ambiguous or unresolved attempt namespace lineage fails export.
- Control Plane namespace reconstruction is derived only from Replay's explicit `moltbot_attributed_control_plane_attempt` records; matching labels alone are not accepted as lineage evidence.
- Source-asserted repository/profile provenance remains source-asserted. ODES does not promote it to authentication or independent verification.
- ODES execution provenance now exposes separate `control_plane` and `executor` attempt namespaces.
- Existing package digest construction remains over the final material package content. No content mutation was added after digest construction.
- Existing recipient validation boundaries remain unchanged:
  - package-content digest validation;
  - authentication separate from content integrity;
  - historical authority separate from present authority;
  - exact relying party and purpose;
  - exact recipient evaluation scope;
  - explicit non-negative `status_max_age_seconds`;
  - timezone-aware recipient/status timestamps;
  - future status evidence rejected;
  - stale evidence rejected even if labeled current;
  - unavailable authentication/status evidence remains unavailable rather than inferred.

### Accepted-profile integration tests added

ODES-owned tests now generate actual executor producer output from accepted Moltbot, import that output through accepted Replay, and export/evaluate ODES for:

- successful execution;
- duplicate/restart reconciliation with distinct Control Plane/executor attempt namespaces;
- lost acknowledgement;
- partial delivery;
- historical absent observation;
- historical unknown observation;
- denied/no-effect result;
- unsupported producer revision;
- unsupported producer profile;
- inconsistent/dangling attempt lineage;
- package tampering;
- wrong recipient;
- wrong purpose;
- stale status despite current labels;
- future status timestamp;
- missing status freshness-age policy;
- recipient/status scope mismatch;
- unavailable authentication evidence;
- unavailable status evidence.

Existing ODES tests continue to cover schema/profile versions, redaction, provenance tamper, recipient clocks, expiry, revocation, supersession and canonicalization boundaries.

### CI state

Final-head workflow:

- ODES head: `d5b8954f401cb6b7bfcd755b2477a4289c66c9bf`
- Tests run: `37498490412`
- State at checkpoint/handoff: **QUEUED**
- No passing CI claim is made for this final head yet.

Per Batch 3B instruction, no indefinite polling was performed.

### Remaining work

1. Review final-head ODES CI once available; repair only ODES-local failures if any.
2. Evidence Pack compatibility remains a separate bounded batch.
3. Alvorada PR #5 must be rerun after accepted/compatible Replay and ODES revisions are available.
4. Accepted hub lock remains unchanged.

No Evidence Pack, Alvorada or hub dependency pin was modified. No deployment, rename, DOCX edit or self-merge occurred.


## Batch 3B targeted CI repair — helper clock

Scope remained limited to `cogno-us/open-decision-evidence-standard` plus this durable checkpoint update.

### ODES PR #23 revised state

- PR: https://github.com/cogno-us/open-decision-evidence-standard/pull/23
- Previous head: `d5b8954f401cb6b7bfcd755b2477a4289c66c9bf`
- Revised head: `442d03de207caea05df9804f55befedf8d72a5be`

Correction completed:

- In `tests/test_accepted_replay_profile.py`, all affected accepted-executor integration calls now use the actual clock returned by `_integrated()`: `helper.NOW`.
- No replacement timestamp was introduced.
- Accepted Replay/Moltbot pins, ODES exporter validation, recipient-policy validation and all existing assertions were preserved.
- No runtime ODES code changed in this targeted repair.

Prior failing run evidence:

- Final pre-repair workflow: `37498490412`
- Python 3.11 result: **50 passed, 11 failed**.
- All 11 failures were `AttributeError: module 'odes_accepted_moltbot_fixture' has no attribute 'NOW'`.
- Python 3.12 matrix job was cancelled after the Python 3.11 failure.
- No additional substantive exporter/recipient defect was exposed in that run because each failing accepted-profile test stopped at the same missing-clock reference.

Corrected exact-head workflow state:

- ODES head: `442d03de207caea05df9804f55befedf8d72a5be`
- Push Tests workflow: `37504791560`
- Dynamic PR workflow: `37504793214`
- State at checkpoint/handoff: **QUEUED**
- No green CI claim is made yet.
- The push workflow includes the complete ODES test suite and the existing CLI export / validate-record / recipient-validate checks against pinned Manifest, Authority Context, Control Plane, accepted Moltbot, accepted Replay and Governance Evidence Pack checkouts.

Per instruction, no prolonged polling was performed.

No Evidence Pack, Alvorada or accepted hub-lock change was made. No self-merge occurred.


## Batch 3C — Governance Evidence Pack compatibility

Scope was limited to `cogno-us/cognous-agent-governance-evidence-pack` plus this durable checkpoint update. Alvorada, Replay, ODES and the accepted hub lock were not modified.

### Evidence Pack PR #7

- PR: https://github.com/cogno-us/cognous-agent-governance-evidence-pack/pull/7
- Preserved starting head: `ddbabedd8bde4359a4eb6ad5123746800b3f262c`
- Final Batch 3C head: `59f6b9752715b136b170d5693b675c50ee701193`
- Base/main at PR creation: `a9aca055e18e5b35cee356c224a146138ebbd948`
- No prior open PR existed for the preserved branch.

### Accepted compatibility mapping

- Manifest: `46c950bed37fe3812000895430bc0312d29e37ce`
- Control Plane: `283500652d47a692fb0b99a1172a6d5faffbd9a7`
- Moltbot Safe: `1d308faf664c504b6e310db3c7a310153ef7b067`
- Replay: `f63ce914504dd06813c4ccd199b0570dbd8dd427`
- ODES: `cba83a1c06f718a8afd76178f36e5cc15896347d`
- executor producer profile ID: `urn:cognous:profiles:moltbot-safe-executor-producer`
- executor producer profile version: `1.0.0`
- Execution Envelope version: `0.2.0`

Legacy unversioned Moltbot evidence remains supported only through the explicit Replay-managed revision-pinned path:

`6b0ba1185bcd390f71df947dda349415e4105f5f`

Historical artifacts are not relabeled as versioned producer-profile evidence.

The Alvorada/GAX experimental checkout at
`9ad378145d326799e3209136e47e82d66c6f69af` remains a **provisional experimental dependency** for bounded compatibility testing. Batch 3C does not promote it to an accepted stack dependency.

### Changed paths

- `.github/workflows/tests.yml`
- `src/agent_governance_evidence_pack/importer.py`
- `src/agent_governance_evidence_pack/trace_renderer.py`
- `tests/test_importer.py`
- `tests/test_accepted_executor_profile.py`
- `docs/traceable_imports.md`
- `README.md`

### Compatibility and assurance corrections

- Advanced Replay, Moltbot Safe and ODES compatibility declarations/CI pins to accepted revisions.
- Preserved the legacy Moltbot revision as the only explicit alternate executor revision.
- Versioned accepted Moltbot Replay producer profiles require:
  - accepted Replay producer-profile identity;
  - profile version `1.0.0`;
  - accepted Moltbot repository revision;
  - preserved source-asserted producer provenance.
- Evidence Pack reconstructs Replay semantic-validation input with:
  - executor destination attempts;
  - append-only executor attempt events;
  - executor observations;
  - separately attributed `moltbot_attributed_control_plane_attempt` records;
  - explicit executor versus Control Plane `attempt_identity`.
- Versioned result attempt IDs must resolve to exactly one namespace. Ambiguous or unresolved attempt lineage is rejected by Replay semantic validation.
- The importer preserves the executor producer contract in `metadata.traceable_import.executor_producer_contract`.
- Profile ID/version, repository revision, source-asserted provenance and independently-established provenance remain separate fields.
- Source assertions are not promoted to authentication or independent verification.
- Locally computed record commitments remain distinct from source-supplied commitments.
- Compatibility alias `hash == local_content_commitment` is preserved.
- Fixed producer revision-status reporting for repositories that have an explicit set of accepted/legacy revisions; valid revisions now report `declared_revision_matches_accepted_pin`.
- Traceable Markdown renders the executor producer contract and explicitly states that semantic validation/local commitments do not authenticate the producer or independently verify the outcome.
- Existing conversion findings, redaction lineage, warning accounting and failed/inconclusive source-attributed test-result rendering remain intact.
- Historical authorization remains separate from present permission.
- Importing evidence continues to record `tested_in_this_repository = not_evaluated_during_import`; source-attributed test evidence is not converted into a claim that Evidence Pack tests ran.
- Destination observation remains producer-retained evidence unless independent verification is separately supplied.

### Actual accepted-profile validation added

A new integration suite generates actual accepted Moltbot producer output, imports it through accepted Replay, then exercises the public Evidence Pack importer, validator and traceable renderer for:

- successful execution;
- duplicate/restart reconciliation;
- one durable effect under reconciliation;
- separate Control Plane and executor attempt namespaces;
- lost acknowledgement;
- partial execution;
- historical absent observation with no effect row;
- historical unknown observation with no fabricated effect;
- execution-time denied/no-effect result;
- Control Plane held/no-execution result;
- unsupported producer revision;
- unsupported producer profile;
- dangling/tampered attempt lineage;
- tampered operation content;
- missing test provenance;
- malformed test provenance;
- failed source-attributed test provenance.

The JSON/Markdown assertions verify common material lifecycle facts, producer contract identity/revision, independent-verification limitations and failed-test attribution.

### Preserved validation behavior

The full existing suite continues to include:

- `hash == local_content_commitment` checks;
- source-supplied versus locally computed commitment rendering;
- replay conversion findings;
- redaction derivation lineage;
- warning/error accounting;
- failed attributable test evidence rendering;
- exact source record/revision traceability;
- independent-verification non-inference;
- held/denied no-effect behavior;
- tamper/dangling-attempt rejection.

### Executed validation and CI state

Intermediate code-head workflow `37506019652`:

- Python 3.11: **165 passed, 3 failed**.
- Python 3.12: cancelled after the Python 3.11 matrix failure.
- The three failures were test/fixture assumptions, not relaxed runtime semantics:
  1. partial execution was expected to have acknowledgement `unknown`, but actual accepted producer/Control Plane semantics record acknowledgement `received` while destination remains `partial`;
  2. the held-case fixture attempted to call Control Plane helpers directly on the loaded Moltbot test module rather than through its pinned `_load_pinned_helpers()`;
  3. the old versioned-format test still injected pre-merge Moltbot revision `054e92d...`, causing the intended format-version assertion to be pre-empted by correct unsupported-revision rejection.
- All three test assumptions were corrected:
  - partial acknowledgement now expects the actual `received` state while retaining `partial` destination state;
  - held scenario now uses the actual pinned Control Plane helper;
  - format-version regression now mutates the accepted Moltbot revision rather than a rejected historical feature head.

Final head `59f6b9752715b136b170d5693b675c50ee701193`:

- Tests workflow: `37506264931`
- State at checkpoint/handoff: **QUEUED**
- No final green CI claim is made yet.
- The workflow is configured to run:
  - full package `pytest` on Python 3.11 and 3.12;
  - `agep check-examples`;
  - CLI `agep import`;
  - CLI `agep validate`;
  - CLI traceable `agep render`;
  - all against the exact accepted Manifest, Control Plane, Moltbot Safe, Replay and ODES pins plus the explicitly provisional GAX checkout.

Per Batch 3C instruction, no prolonged polling was performed.

### Remaining blockers / next bounded starting point

- Final-head Evidence Pack CI has not completed at this checkpoint; review `37506264931` before accepting PR #7.
- If final CI is green, no known Evidence Pack-local compatibility blocker remains.
- If final CI exposes a substantive Evidence Pack-local defect, repair it without weakening Replay semantic validation or assurance separation.
- Alvorada PR #5 rerun remains a later bounded batch.
- The accepted hub lock remains unchanged.

No adjacent implementation repository, Alvorada runtime, Replay, ODES, deployment, DOCX, rename or self-merge change occurred in Batch 3C.


## Batch 3C targeted correction — held run identity and compatibility docs

Scope remained limited to `cogno-us/cognous-agent-governance-evidence-pack` plus this durable checkpoint update.

### Evidence Pack PR #7 revised state

- PR: https://github.com/cogno-us/cognous-agent-governance-evidence-pack/pull/7
- Previous head: `59f6b9752715b136b170d5693b675c50ee701193`
- Revised head: `96b4a2bc173695992d8b3783f677de3f6a2a0b38`

Targeted corrections:

1. Held-case fixture run identity
   - `test_actual_control_plane_hold_has_no_execution_or_effect` now constructs a single `run_id = "run-held"` before authorization.
   - The proposal is copied with that run ID before resolver/workflow authorization.
   - The `BoundedRecordStore` uses the same run ID.
   - Replay's proposal/run identity validation remains unchanged.
   - Existing no-execution/no-effect assertions remain unchanged.

2. Compatibility documentation
   - `docs/traceable_imports.md` supported-revision table now lists:
     - Moltbot Safe `1d308faf664c504b6e310db3c7a310153ef7b067`
     - Replay `f63ce914504dd06813c4ccd199b0570dbd8dd427`
     - ODES `cba83a1c06f718a8afd76178f36e5cc15896347d`
   - The accepted-pin list in the same document now uses the same revisions.
   - Legacy unversioned Moltbot compatibility at `6b0ba1185bcd390f71df947dda349415e4105f5f` remains explicit.
   - README and traceable-import docs now consistently describe GAX/IMX `9ad378145d326799e3209136e47e82d66c6f69af` as a **provisional experimental dependency** used for bounded compatibility testing, not an accepted stack dependency.
   - Obsolete wording that called the GAX/IMX reference accepted was removed from the compatibility section.

No runtime importer/validator/renderer logic or dependency pin was weakened or changed in this targeted correction.

### Exact-head CI state

Revised head: `96b4a2bc173695992d8b3783f677de3f6a2a0b38`

Workflows created:

- push Tests: `37508893152` — **QUEUED**
- pull-request Tests: `37508901348` — **QUEUED**
- dynamic PR #7 workflow: `37508894479` — **QUEUED**

The Tests workflow is configured to execute:

- Python 3.11 full package suite;
- Python 3.12 full package suite;
- `agep check-examples`;
- CLI `agep import`;
- CLI `agep validate`;
- CLI traceable `agep render`;
- against exact accepted Manifest, Control Plane, Moltbot Safe, Replay and ODES pins plus the explicitly provisional GAX checkout.

Per instruction, no prolonged polling was performed and no green claim is made for this revised head yet.

No Evidence Pack-adjacent repository, Alvorada, Replay, ODES or accepted hub lock was modified. No deployment or self-merge occurred.


## Alvorada PR #5 rerun against accepted consumers

Scope was limited to `cogno-us/alvorada` plus this durable checkpoint update. No adjacent implementation repository or accepted hub lock was modified.

### PR state

- PR: https://github.com/cogno-us/alvorada/pull/5
- Preserved starting head: `62f16348f3127af8d663dd7719d25dddd6f9ac70`
- Final head: `66c6bcad62735d8349924c34bf114d76e8a2efb6`
- Base/main remained `e0b2495fea66fe5d7446745b3387b473625c55de`
- Deferred/unaccepted Alvorada PR #2 was not consumed.

### Exact accepted pins

Preserved accepted pins:

- Manifest: `46c950bed37fe3812000895430bc0312d29e37ce`
- Authority Context: `fb3d97938969a89e149e8ff8db2756091d1233fc`
- Control Plane: `283500652d47a692fb0b99a1172a6d5faffbd9a7`

Updated accepted consumers:

- Moltbot Safe: `1d308faf664c504b6e310db3c7a310153ef7b067`
- Replay: `f63ce914504dd06813c4ccd199b0570dbd8dd427`
- ODES: `cba83a1c06f718a8afd76178f36e5cc15896347d`
- Governance Evidence Pack: `f1a76187b72d5b7c9fded12580ba081cb9cba338`

The workflow now installs accepted Evidence Pack in addition to Control Plane, Replay and ODES and verifies each exact checkout revision before testing.

### Integration checks preserved/completed in code

The existing Batch 2 public-path coverage remains in place and now runs against the accepted consumers:

1. `LocalDurableTransport -> AcceptedGaxRecipientAdapter -> Control Plane -> accepted Moltbot executor` with explicitly supplied resolver and execution-policy factory.
2. Runtime public-module execution with the upstream `tests.*` namespace blocked.
3. Public `retained_result()` / `retained_artifacts()` retrieval of retained Replay, ODES and successor artifacts with content commitments and producer identities.
4. Duplicate/lost-ack/restart behavior preserving one durable destination effect and original decision/effect identity.
5. Post-effect interruption/evidence-export recovery with no replacement effect, explicit `regenerated_derivative` lineage, and originals remaining unavailable when never retained.
6. Success, revocation/denial, partial delivery, tamper rejection and separate producer attempt namespaces.
7. New accepted-consumer-chain regression:
   - delivers through public transport;
   - retrieves the original retained Reconstruction Bundle, ODES package/recipient result and successor packet;
   - verifies retained artifact IDs and commitments;
   - imports retained Replay through accepted Governance Evidence Pack;
   - validates the Evidence Pack and traceable Markdown;
   - asserts accepted Replay/Moltbot/ODES revisions in Evidence Pack metadata;
   - asserts independent verification remains `unavailable`;
   - asserts historical evidence does not establish current permission;
   - asserts retained ODES package schema/content integrity passes;
   - asserts ODES authentication remains `unavailable`;
   - asserts present authority/status evidence remains `unavailable` under the deliberately empty recipient status inputs;
   - performs an exact duplicate delivery and confirms one durable effect plus byte-equivalent retained original artifacts.

No authentication, present authority, or independent verification is manufactured by this path.

### Documentation reconciliation

Updated:

- `experiments/governed_message_transport/mapping.md`
- `docs/gax-runtime-artifact-interface.md`

These now list the accepted Moltbot, Replay, ODES and Evidence Pack revisions above and remove stale proposed/pre-cleanup consumer SHAs from the branch-local integration guidance.

### Exact-head CI state

Final head: `66c6bcad62735d8349924c34bf114d76e8a2efb6`

Workflows created:

- push Tests: `37516895840` — **QUEUED**
- pull-request Tests: `37516900733` — **QUEUED**
- dynamic PR #5: `37516898770` — **QUEUED**

The Tests workflow is configured to run:

- full `pytest -q tests` on Python 3.11;
- full `pytest -q tests` on Python 3.12;
- the demonstration command `python -m experiments.odex_gax_imx_reference.demo`;
- after verifying the exact accepted pins listed above.

At checkpoint time no exact-head job had started, therefore no test totals, failure totals or skip totals are claimed for `66c6bc...`.

Per instruction, no prolonged polling was performed.

### Remaining blocker

The only current release-gate blocker recorded at this checkpoint is **pending exact-head CI execution**. No upstream defect has yet been exposed by this accepted-consumer rerun because the final-head jobs are queued.

If the exact-head suite exposes a concrete Alvorada-local failure, repair only that failure. If it exposes an accepted-consumer defect, report it without modifying the adjacent repository.

No hub lock update, deployment, DOCX edit, rename or self-merge occurred.
