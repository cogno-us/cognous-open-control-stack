# Artifact 1 - MVP Definition

Status: PROPOSED, non-authorizing; release and production HOLD; operator decisions D1-D6 in [critical-path.md](critical-path.md) are open.

## Capability
A single-host, synthetic-effect demonstration that a governed refund action is proposed, evaluated against bounded authority held by a trusted resolver, authorized / refused / held, enforced at the execution boundary with pre-effect revalidation, recorded with decision, attempt, outcome and negative evidence, and reconstructed and verified independently of the producer. Scenario: the existing matched synthetic refund (USD 10, `effect:synthetic-refund-001`).

## Supported workflow and configuration (proposed fixed configuration)
- Components at the existing g8-r10 tuple, unchanged on main: Control Plane 0a41faa9, Runtime ec728da6, Replay 028f63d1, Evidence Pack a3ebbb90, Action Manifest fa170815 (ODES e86a25a1 and Verifier c0b8ba1f only if D4/D3 keep them in the evidence path).
- Native execution route (route B, `AtomicLocalControlPlaneExecutor`, operation identity enabled) against a synthetic SQLite destination; ingress by control-plane proposal (`acp run`-style), not the GAX exchange route. Route A vs B is operator decision D2.
- Linux, single host, same-host custody.
- The Orchestrator, the declarative registry, the mandatory-check catalogue and the external checkpoint are not part of the MVP configuration.

## Included (the seven required behaviours)
1 proposal; 2 authority evaluation by trusted resolver; 3 authorize/refuse/hold; 4 boundary enforcement with pre-effect revalidation; 5 decision/attempt/outcome/negative-evidence record; 6 independent reconstruction and verification; 7 safe behaviour on revocation, failed custody and unknown outcome (`unknown`, retry not eligible, reconcile).

## Explicit limitations (carried, not removed)
- Synthetic effects only; no claim of production effect safety or deployment-environment safety.
- Pre-effect revalidation is not atomic with the destination commit on the default C0 profile (check-to-commit race, D10); in-transaction checking holds only on the opt-in profile fixed by D2.
- The resolver is a test-owned synthetic fixture; it is not institutional authentication. External agent identity is not verified.
- Same-host custody, no external anchor: local chain consistency with limited truncation detection. A holder of the destination credential is outside the boundary.
- Qualification so far is by the project's own separate Qualification repo; it has not been externally audited.
- Known limits F-16, F-18, F-19, D01-D15 and the six unimplemented scenarios stay as published.

## Exclusions
Registry activation and `/1` migration; 58-entry mandatory-check catalogue; scanner normalization; Orchestrator workflow lifecycle, event-store limits, archival and checkpoints; Observability Coverage Manifest; drift monitoring; agent-identity interoperability; OpenTelemetry projection; ISS V6; additional adapters; broad refreeze cascades. See the register for reasons.
