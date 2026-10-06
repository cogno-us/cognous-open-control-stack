# Reference candidate status

This branch is a bounded **public reference candidate**, not a production deployment.

## Evidence-state ledger

- Component contracts and pins: **implemented**.
- Two isolated local synthetic executions: performed by `tools/reference_release.py`; status is recorded in generated evidence.
- Pinned CI: **tested in pinned CI** only after the PR workflow succeeds at final head.
- OpenShell mocked adapter: tested separately; exact result is in the evidence artifact.
- OpenShell live qualification: **unexecuted** unless explicitly enabled against already-authorized infrastructure.
- Model-behavior evaluation for PRP, TFA and Research Intelligence: **unexecuted**. Static JSON/artifact checks do not imply behavioral efficacy.
- Alvorada PR #2: **deferred** and excluded.

## Release blocker versus production backlog

A reference candidate is blocked if pinned CI fails, if the two clean runs disagree on expected pass/fail outcomes, or if evidence provenance claims a producer revision different from the compatibility profile.

Production-only backlog does not block this bounded reference candidate: real institutional identity/resolver authentication, production credential separation, network/OS confinement, live OpenShell qualification, fleet orchestration, distributed budgets, production revocation propagation and independent real-world verification. Each requires an owning component and deployment-specific acceptance test before any production claim.

## Naming and scope

No repository rename, deployment, public-chain transaction, paid infrastructure or adjacent-repository mutation is part of this release candidate. ISS, Navalia and private research remain outside the public integration.
