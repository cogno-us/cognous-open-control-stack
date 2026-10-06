# Reference candidate status

This branch is a bounded **public reference candidate**, not a production deployment.

## Evidence-state ledger

- Component contracts and pins: **implemented** and unchanged by the targeted release-gate correction.
- The runner performs two isolated transported representative workflows. Each uses a separate LocalDurableTransport sender store, recipient store, GAX exchange store and Moltbot synthetic destination.
- The representative operation is executed only through `LocalDurableTransport -> AcceptedGaxRecipientAdapter`. The hub does not execute a second direct GAX operation and reuse it as evidence for transport.
- After transport, the runner reconstructs Replay, Governance Evidence Pack, ODES and IMX successor artifacts from the retained records for that transported operation.
- Expected-versus-observed validation is an enforced gate: destination effect count/content/state, execution semantics and cross-artifact identities must agree or the command exits non-zero.
- The acceptance matrix is resolved from collected JUnit cases in both repetitions. Missing, failed or skipped **required** references block release.
- `test_governed_message_transport_integration.py` is part of the pinned acceptance suite.
- A hub regression test proves a nonexistent required test reference cannot produce a green release gate.
- OpenShell mocked adapter: tested separately; exact result and JUnit output are in the evidence artifact.
- OpenShell live qualification: **unexecuted** unless explicitly enabled against already-authorized infrastructure with `MOLTBOT_SAFE_OPENSHELL_CONFIG`, `MOLTBOT_SAFE_OPENSHELL_BINARY`, and `MOLTBOT_SAFE_OPENSHELL_HOME`.
- Model-behavior evaluation for PRP, TFA and Research Intelligence: **unexecuted**. Static JSON/artifact checks do not imply behavioral efficacy.
- Alvorada PR #2: **deferred** and excluded.

## Release blockers

A reference candidate is **blocked** if final-head pinned CI fails; either transported representative run fails; normalized expected outcomes differ across the two isolated runs; a required matrix reference is missing, failed, skipped or unexecuted; the representative evidence chain lacks a required artifact; or cross-artifact effect/decision/attempt identity is contradictory.

One known interface debt remains visible: accepted GAX currently loads Moltbot integration helpers from `tests/test_safe_executor.py` even though Moltbot exports `engine.control_plane_adapter.PinnedControlPlaneExecutor`. The hub does not hide or patch that adjacent-repository issue.

The accepted Moltbot head `e8a4f8c...` is qualified separately because Replay/GAX/Evidence Pack still declare `6b0ba118...` as their supported producer revision. Moving the core evidence chain to `e8a4f8c...` requires a versioned upstream producer-profile update, not a hub-side relabel.

## Deferred production work

These items do not become implemented merely because a bounded reference candidate passes: authenticated institutional resolvers, production credential separation, live OpenShell/network/OS confinement, fleet orchestration, distributed budgets, production revocation propagation and independent real-world verification.

Each item requires an owning component and deployment-specific acceptance condition. Human review effort and enterprise benefit remain unmeasured unless separately studied.

## Naming and scope

No repository rename, deployment, public-chain transaction, paid infrastructure or adjacent-repository mutation is part of this reference candidate. ISS, Navalia and private research remain outside the public integration.
