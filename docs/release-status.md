# Reference candidate status

This branch is a bounded **public reference candidate**, not a production deployment.

## Evidence-state ledger

- Component contracts and pins: **implemented**.
- The runner performs two isolated executions of the pinned acceptance suites. A local invocation is **tested locally** only if it passes; the GitHub Actions invocation is **tested in pinned CI** only if the final-head workflow passes.
- OpenShell mocked adapter: tested separately; exact result and JUnit output are in the evidence artifact.
- OpenShell live qualification: **unexecuted** unless explicitly enabled against already-authorized infrastructure with `MOLTBOT_SAFE_OPENSHELL_CONFIG`, `MOLTBOT_SAFE_OPENSHELL_BINARY`, and `MOLTBOT_SAFE_OPENSHELL_HOME`.
- Model-behavior evaluation for PRP, TFA and Research Intelligence: **unexecuted**. Static JSON/artifact checks do not imply behavioral efficacy.
- Alvorada PR #2: **deferred** and excluded.

## Release blockers

A reference candidate is **blocked** if pinned CI fails, if either clean run fails an expected suite, if the accepted GAX path cannot retain/recover evidence through its declared interfaces, or if evidence provenance claims a producer revision different from the compatibility profile.

One known interface debt remains visible: accepted GAX currently loads Moltbot integration helpers from `tests/test_safe_executor.py` even though Moltbot exports `engine.control_plane_adapter.PinnedControlPlaneExecutor`. The hub does not hide or patch that adjacent-repository issue.

The accepted Moltbot head `e8a4f8c...` is qualified separately because Replay/GAX/Evidence Pack still declare `6b0ba118...` as their supported producer revision. Moving the core evidence chain to `e8a4f8c...` requires a versioned upstream producer-profile update, not a hub-side relabel.

## Deferred production work

These items do not become implemented merely because a bounded reference candidate passes: authenticated institutional resolvers, production credential separation, live OpenShell/network/OS confinement, fleet orchestration, distributed budgets, production revocation propagation and independent real-world verification.

Each item requires an owning component and deployment-specific acceptance condition. Human review effort and enterprise benefit remain unmeasured unless separately studied.

## Naming and scope

No repository rename, deployment, public-chain transaction, paid infrastructure or adjacent-repository mutation is part of this reference candidate. ISS, Navalia and private research remain outside the public integration.
