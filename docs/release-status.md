# Reference candidate status

This branch is a bounded **public reference candidate**, not a production deployment.

## Evidence-state ledger

- Component contracts and pins are advanced to the observation-validation revisions (including accepted Alvorada PR #7 recovery-export merge) in `component-lock.json`.
- The runner performs two isolated transported representative workflows. Each uses a separate LocalDurableTransport sender store, recipient store, GAX exchange store and Moltbot synthetic destination.
- The representative operation is executed only through `LocalDurableTransport -> AcceptedGaxRecipientAdapter`. The hub does not execute a second direct GAX operation and reuse it as evidence.
- The hub consumes the **original retained** Reconstruction Bundle, ODES package/recipient validation and IMX successor from Alvorada's versioned retained-artifact API. It no longer regenerates Replay as a workaround.
- Expected-versus-observed validation gates destination effect count/content/state, decision/effect/attempt identity, retained artifact identity/content commitments, Evidence Pack continuity and ODES integrity/assurance boundaries.
- The acceptance matrix contains **30 required entries** (including five changed-authority entries, each covering applied and absent effects). Missing, failed or skipped required references block release in either isolated repetition.
- Qualification includes original-artifact continuity, post-effect evidence-only recovery, lost acknowledgement/timeouts and retry exhaustion.
- `test_gax_public_runtime_artifacts.py` and `test_governed_message_transport_integration.py` are part of the pinned acceptance suites.
- A hub regression test proves a nonexistent required test reference cannot produce a green release gate.
- OpenShell mocked adapter is tested separately; live OpenShell remains **unexecuted** unless explicitly enabled against already-authorized infrastructure.
- Model-behavior evaluation for PRP, TFA and Research Intelligence remains **unexecuted**. Static JSON/artifact checks do not imply behavioral efficacy.
- Alvorada PR #2 remains **deferred** and excluded.

## Batch 4C integration checkpoint

The dependency chain now selects the accepted Alvorada PR #7 recovery-export merge.
The accepted-pin execution is separate from the preserved historical candidate run.
Current executions and exact totals are recorded in the [durable checkpoint](workstreams/batch4c-integration-checkpoint.md).
Checkpoint 1's three failed absence assertions are historical. Two equivalent-intent
effects remain a characterized limitation, not business-intent deduplication.
Two bounded same-process late-commit cases have focused local evidence; see the
[late-commit checkpoint](workstreams/late-commit-checkpoint.md). Recovery-authority
results are in the [current checkpoint](workstreams/recovery-authority-checkpoint.md).
Worker 16 separately qualified bounded same-host destination/process-death behavior.
Shared Control Plane JSON-store concurrency is unsupported with observed record loss.
Cancellation/finality and distributed guarantees remain unexecuted.

## Release blockers

A reference candidate is **blocked** if final-head pinned CI fails; either transported representative run fails; normalized expected outcomes differ across the two isolated runs; a required matrix reference is missing, failed, skipped or unexecuted; a required original retained artifact is unavailable on a successful path; post-effect recovery mints a replacement effect; or cross-artifact effect/decision/attempt identity is contradictory.

The accepted integration now has a public executor entrypoint, versioned producer compatibility and original-artifact retention. Those former interface debts are no longer release blockers.

Recovery qualification is deliberately asymmetric:

- if the original artifact set was durably retained, duplicate/redelivery must return that original set and its identities;
- if an effect completed but the original artifact set was never retained, the operation remains recoverable/unresolved until evidence recovery succeeds;
- regenerated evidence is explicitly derivative and must not be labeled original;
- timeout, lost acknowledgement and retry exhaustion do not authorize a replacement effect.

## Deferred production work

Passing this bounded reference candidate does **not** implement authenticated institutional resolvers, production credential separation, live OpenShell/network/OS confinement, fleet orchestration, distributed budgets, production revocation propagation or independent real-world verification.

Each deferred item requires an owning component and deployment-specific acceptance condition. Human review effort and enterprise benefit remain unmeasured unless separately studied.

## Naming and scope

No repository rename, deployment, public-chain transaction, paid infrastructure or adjacent-repository mutation is part of this hub integration. ISS, Navalia and private research remain outside the public integration.
