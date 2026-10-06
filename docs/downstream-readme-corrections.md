# Downstream documentation reconciliation

This document tracks interface-cleanup corrections that were previously listed as downstream work. The accepted integration now incorporates the corresponding reviewed upstream changes.

## Completed

### cogno-us/alvorada

- Supported GAX runtime uses the public Moltbot executor/producer APIs rather than `tests/test_safe_executor.py`.
- Caller-supplied resolver and execution policy remain required; incoming proposals do not create authority.
- Versioned retained-artifact APIs expose original Replay, ODES validation/package and successor artifacts with content commitments.
- Evidence-only recovery after post-effect interruption does not mint a replacement effect.
- PR #2 remains deferred and excluded.

### cogno-us/cognous-agent-replay-bundle

- Accepted versioned Moltbot producer profile:
  `urn:cognous:profiles:moltbot-safe-executor-producer` / `1.0.0`.
- Accepted Moltbot revision: `1d308faf664c504b6e310db3c7a310153ef7b067`.
- Legacy unversioned `6b0ba118...` evidence remains historical/revision-pinned and is not relabeled.
- Executor and Control Plane attempt namespaces remain distinct.

### cogno-us/open-decision-evidence-standard

- Accepted Replay/Moltbot compatibility is versioned and namespace-preserving.
- Package integrity remains separate from authentication and present authority.

### cogno-us/cognous-agent-governance-evidence-pack

- Accepted Replay/Moltbot/ODES revisions are reflected in traceable import metadata.
- Source assertions, semantic validation, attributable test evidence and independent verification remain separate assurance classes.

## Still deferred

### cogno-us/moltbot-safe

- Live OpenShell remains optional/unexecuted until the live qualification gate passes against authorized infrastructure.
- The bounded local executor remains the public reference execution path.

## Naming and scope

No rename occurs here. Documentation uses:

- **Alvorada Constitution** for `cogno-us/constitutional-governance-for-institutions`;
- **Alvorada Exchange Workbench** for `cogno-us/alvorada`;
- **Moltbot Safe** for the executor repository/package unless a future explicit compatibility migration changes the name.
