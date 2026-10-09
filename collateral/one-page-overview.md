# Cognous Open Control Stack — One-Page Overview

> **Evidence snapshot:** `document_id=cognous-one-page-overview`; `version=2.0.0`; `generated_at=2026-10-09T16:16:00-07:00`; accepted hub source `f7d03c719b9be3b9c3fe0fe300df642b0f408d98`; component-lock SHA-256 `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`; evidence generation `merged-producers-v1 / full-candidate-gate`. Scope: bounded synthetic local reference only. Detached final-file SHA-256 is recorded in [evidence-snapshot.json](evidence-snapshot.json).

## Purpose

An open, pinned synthetic reference connecting declared agent actions, **independently resolved** institutional authority, constrained local execution and traceable governance evidence.

## Release Boundary First

The reference destination is a synthetic SQLite refund table. **C0**, the default selected path, revalidates current authority/evidence immediately before dispatch but retains a check-to-commit race; it is not destination commit atomicity. **C1** is an optional same-host SQLite authority/effect profile for cooperating participants and is not enabled by the default release. **C2/C3 are not claimed.** External processor atomicity, distributed coordination, settlement finality, production credentials and deployment-wide bypass resistance remain unqualified.

## Worked Refund Timeout

1. A refund message proposes an action; it does not carry authority.
2. A trusted resolver supplies current Authority Context independently.
3. C0 checks the exact operation and current decision-critical inputs immediately before dispatch.
4. Local effect `E1` is attempted in the synthetic SQLite destination.
5. The caller times out; delivery is **unknown**, not failed.
6. Reconciliation observes SQLite independently of the acknowledgement.
7. If `E1` is applied, retain the historical effect; if absent at one observation, do not infer retry permission or settlement.
8. A new `E2` for the same business refund intent can still duplicate intent under the default path. Effect-ID dedupe is not business-intent dedupe; the optional intent profile is separate and not composed with C1 here.

## Current Evidence Snapshot

The selected lock points to the merged-producer generation qualified by [run 37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916): source `7e43d55c6cc0123a191480a9e6870d6452affa83`, **35 acceptance scenarios**, `full-candidate-gate` digest `sha256:5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7`. Older 915-test collateral is a historical persistence-generation snapshot and is not copied forward as a current count.

Separate optional C1 profile CI [run 37682165860](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860) records **73 passed** against reviewed Control Plane `73e3c65acc47dc43593dcb0420d14032ed410b14` and executor `b1525a7982e52ebb530457f94d5517de032ca4c4`. That result is not default release evidence and does not establish external atomicity.

## How the Components Fit

- **Action Manifest** declares the exact action surface.
- **Institutional Governance / Authority Context** describes authority semantics; the runtime resolver must independently supply current bounded authority.
- **Control Plane** decides and revalidates; **Execution Runtime** constrains the synthetic local destination.
- **Governed Exchange** supplies GAX/IMX continuity for the bounded workflow.
- **Replay** reconstructs retained records; **Governance Evidence Pack** prepares traceable review material; **ODES** carries portable decision evidence.
- Evidence Attestation/Registry and PRP/Research Intelligence/TFA remain separate paths/layers with narrower claims.

## Limits

Unknown acknowledgement and observed absence do not authorize retry. A later denial does not erase a historical effect. No rollback, exactly-once delivery, real refund settlement, compliance certification, production authority or measured enterprise benefit is claimed.

The current [detached evidence snapshot](evidence-snapshot.json) binds this file to the accepted hub source and lock digest. Historical documents retain their own dates, pins and counts and are not evidence for this snapshot.

[Cognous](https://cogno.us) · [Component lock](../component-lock.json) · [Support status](../docs/release-status.md) · [Business collateral](business-collateral.md).
