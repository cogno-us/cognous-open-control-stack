# Context binding, notification and staging recovery

These are explicit extensions of the synthetic v1 reference profiles. They use the accepted component lock without changing upstream producer schemas, default authorization, or deployment selection. They do not compose refund-intent and atomic profiles into one database.

## Commands

Use the same Python/Git prerequisites as the [v1 reference profiles](v1-reference-profiles.md). Result directories must be new.

```sh
python tools/bound_context_notification.py --profile context-action --results-dir results/context-action-1
python tools/bound_context_notification.py --profile notification --results-dir results/notification-1
python tools/sqlite_staging_recovery.py snapshot results/context-action-1/context.sqlite3 results/context-backup-1
python tools/sqlite_staging_recovery.py restore results/context-backup-1 results/restored-context.sqlite3
```

Integration commands retain exact component revisions, lock digest, outcomes and databases. Each child process has a 90-second deadline. CI runs these three independent Linux batches within the [seven-batch extension evidence workflow](v1-extension-release-gate.md), with 120-second test limits. Backup output contains sensitive content if the source database does; operate only on approved local stores and protect the package.

## Context-to-action binding

`ContextBoundExecutor` requires the accepted local atomic executor. It binds an acknowledged context delivery, generation, receipt commitment, exact frozen execution envelope and exact execution claim. The supported action is the routine synthetic refund, with purpose `refund` and a delivery recipient exactly matching the action's actor. Unknown delivery, wrong purpose/actor, changed generation, revoked/expired context, substituted operation and wrong claim fail closed.

Before dispatch, a `started` marker commits durably. The wrapper then obtains the context write transaction, verifies current use again, and holds that lock while the atomic executor performs its independent authority checks and destination commit. Cooperating context admissions and revocations therefore order before or after that call. The destination's original claim and budget enforcement remain in force; a context receipt does not grant authority.

This is **not a cross-database transaction**. Failure after the destination commits may leave the context action marked started without a final outcome. A started binding cannot dispatch again; recovery reconciles only its exact original envelope and claim. This deliberately favors preventing duplicate execution over automatic recovery availability.

The guarantee requires trusted host code to route context-dependent actions through this wrapper and all context mutations through the same SQLite store. Direct calls to the underlying executor do not enforce context binding. The wrapper's context freshness check occurs at locked dispatch admission; it does not establish that a context expiry occurring during destination execution prevents commit. Destination authority/time checks retain their own narrower atomic contract. This is not remote disclosure control, hidden model-reliance verification, universal mediation, or a new Control Plane decision schema.

## Independently authorized notification

The notification fixture first commits a refund through the accepted atomic executor. It then uses a separate notification manifest action, adapter identity, requirement, policy identity, scoped grant, approval and persisted Control Plane decision. Its unit is `message` and budget is one. The refund decision cannot be supplied as notification authority.

The synthetic adapter appends a record to a local SQLite outbox after current Control Plane revalidation. It also requires the referenced refund to remain present as an applied effect for the corresponding synthetic customer. Destination commit enforces operation binding on duplicate IDs and the cumulative notification-grant cap. A lost acknowledgement is reconciled to the original outbox record.

`applied` means **appended to this local outbox**, not sent, received, read or acted upon externally. No email, network delivery or real customer data is involved. The ordinary notification path retains its validation-to-commit race: it does not inherit the refund executor's authority/effect atomicity. It does not establish notification revocation at an external commit boundary, business-intent deduplication across new grants, independent verification of refund truth, or crash-resumable multi-step scheduling.

## Backup and staging restore

The backup utility uses SQLite's backup API to capture a single committed logical database, including committed WAL contents and excluding uncommitted changes. It checks SQLite consistency, records a SHA-256 digest, and publishes a new protected snapshot. Restore verifies the manifest and digest, checks the database, and creates a new staging file without overwriting an existing path. Missing sources cannot silently become empty stores.

The tests verify retained context revocation, consumed atomic claims, consumed context bindings, refund-intent dispatch ownership, WAL visibility, corruption rejection and overwrite refusal. Atomic claims and intent ownership are tested in separate databases.

A backup hash is not a signature, independent custody, freshness proof or authority to activate a restored store. Packages must be protected and quiescent during verification/restore. Each database snapshot is consistent independently; multiple snapshots are not an atomic deployment snapshot. Restoring an older snapshot can omit later invalidations and consumption. This utility never updates a live configuration or grants activation permission. An operator must establish current authority, high-water marks and destination reconciliation before activation under a deployment-specific recovery procedure.

Crash/power-loss durability, hostile-host resistance, authenticated remote backups, encryption, coordinated multi-store restore and production recovery-time/recovery-point objectives remain unqualified.

## Requirement mapping

This batch advances GC 5/IF03 through an explicit local action binding, TCR-1–3 and TCR-8 through independently authorized refund/outbox steps, and recovery requirements through retained-state tests. It does not close complete source requirements. Existing evidence-consistency and Replay/AGEP/ODES profiles are unchanged; these new artifacts are not silently promoted to consumer-chain conformance.
