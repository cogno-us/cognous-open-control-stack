# Recovery and evidence semantics

These rules describe the selected synthetic implementation. Evidence comes from
[Worker 14d's accepted-pin qualification](../examples/worker14d-recovery/qualification-summary.json),
the [recovery-authority checkpoint](workstreams/recovery-authority-checkpoint.md),
[late-commit qualification](workstreams/late-commit-checkpoint.md) and the separate
[same-host process qualification](workstreams/process-boundary-checkpoint.md).
Their source pins and scopes remain distinct.

| Fact or operation | Meaning at this boundary |
|---|---|
| Effect-time revalidation | The Control Plane checks decision-critical authority/evidence against a trusted resolver and evaluation time before constrained execution. An earlier grant or decision is not permanent permission. |
| Unknown acknowledgement | The caller lacks a conclusive acknowledgement. The original effect may already have committed; timeout/lost acknowledgement does not prove absence or authorize a replacement. |
| Accepted observation | ObservationPolicy and trusted timezone-aware evaluation time validate freshness, completeness and exact operation/effect binding. This is bounded acceptance of destination evidence, not authentication of a production source. |
| Rejected or unavailable observation | Retained separately from accepted observations and acknowledgement/attempt history. Stale, incomplete, contradictory or wrong-effect evidence cannot be promoted to accepted fact; null evidence is not invented. |
| `observed_absent` | Point-in-time evidence only. After an interrupted original attempt, the original effect remains pending/unresolved and `retry_eligible=false`. An in-flight original can still commit later. |
| Original-effect reconciliation | Queries/reconciles the original effect under the supported recovery path. Accepted applied evidence can resolve delivery without a replacement dispatch; it does not rewrite the original unknown acknowledgement. |
| Newly denied recovery | Changed authority can deny the current request before destination observation. Historical execution/effect evidence remains historical; denial neither erases it nor renews permission. |

In the ten changed-authority cases, grant revocation, expiry, policy version,
evidence freshness and approval status were each changed against applied and absent
prior effects. Denied recovery made no observation or replacement dispatch and left
the owning Control Plane records unchanged. `recovery_denied_derivative` preserves
historical Replay/ODES/successor content and producer references, while separately
attributing the current denial, reason, evaluation time and source commitments.
A historical observation is not a fresh observation performed by the denied request.

With valid current authority, `reconciled_derivative` can report fresh absence or
applied recovery. Fresh absence still cannot authorize retry. The late-commit cases
show an original request committing after two absence observations; they establish
neither cancellation safety nor remote finality.

## Original artifacts and derivatives

If the original Replay/ODES/successor artifact set was durably retained,
duplicate/redelivery returns that original set with its identities and commitments.
If an effect completed but evidence was never retained, the workflow stays
recoverable/unresolved until evidence-only recovery succeeds. Regenerated artifacts
carry derivative lineage; they are not relabeled as originals and do not create a
replacement effect. Current-denial derivatives likewise remain distinguishable from
the historical artifacts they reference.

Reconstruction completeness, delivery resolution and independent verification are
separate dimensions. Replay reconstructs records; it does not rerun execution,
reauthorize a request or independently verify the destination. ODES integrity and
Evidence Pack validation do not change that assurance boundary.

No rollback, exactly-once delivery, business-intent deduplication, termination
confirmation or remote finality is claimed. Cancellation request, stop
acknowledgement, process termination and destination observation are distinct facts.
