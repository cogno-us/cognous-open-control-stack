# Cognous Open Control Stack — Business Collateral

> **Evidence snapshot:** `document_id=cognous-business-collateral`; `version=2.0.0`; `generated_at=2026-10-09T16:16:00-07:00`; accepted hub source `f7d03c719b9be3b9c3fe0fe300df642b0f408d98`; component-lock SHA-256 `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`; evidence generation `merged-producers-v1 / full-candidate-gate`. Scope: bounded synthetic local reference only. Detached final-file SHA-256 is recorded in [evidence-snapshot.json](evidence-snapshot.json).

## 1. Executive Summary

Cognous Open Control Stack is open reference infrastructure for evaluating governed agent actions. It connects an action declaration, **independently resolved** institutional authority, bounded runtime execution and retained review evidence. The selected implementation is synthetic, local and pinned. It is not a production payment system, institutional adoption, compliance certification or evidence of external settlement.

## 2. Release Boundary — Read Before the Component Inventory

The default selected path is **C0**: the Control Plane resolves authority independently of the incoming message, then revalidates decision-critical state immediately before dispatch. That reduces stale-authority exposure, but it does **not** make authorization and destination commit atomic. A grant, approval, policy or evidence state can change after the final check and before the effect commits.

**C1 is optional and local only.** The separately qualified authority/effect profile orders cooperating writers and the synthetic effect through one same-host SQLite transaction boundary. It is not enabled by the default release, does not cover external processors, and does not establish distributed atomicity.

**No C2 or C3 claim is made.** Remote destination commit protocols, distributed coordinators, external settlement finality and production exactly-once semantics remain outside the release.

The reference destination is a **synthetic SQLite refund table**. Application-level checks and local database ordering are not bank, card-network, merchant-acquirer or payment-processor controls. Authority, credentials, external settlement and production bypass resistance must be qualified separately in any deployment.

## 3. Worked Refund Timeout and Reconciliation Example

1. A synthetic refund request arrives as a proposal. Message content, a signature or a prior approval record is not execution authority.
2. A trusted resolver supplies the current Authority Context independently of the request.
3. On the default C0 path, the Control Plane checks the exact tenant, action, target, payload, grant, policy and required evidence immediately before dispatch. A check-to-commit race still remains.
4. The executor attempts local effect `effect_id=E1` against the synthetic SQLite destination.
5. The caller times out before receiving an acknowledgement. The outcome is **unknown**; timeout is not failure and does not authorize retry.
6. Reconciliation reads the destination independently of the executor acknowledgement, using `E1`. If `E1` is present and applied, the historical effect is retained even if current authority is later denied.
7. If `E1` is absent at one observation, that is point-in-time evidence only. The system does not infer safe retry or external settlement; it preserves uncertainty and re-observes/re-evaluates according to the bounded recovery contract.
8. A second valid proposal with `effect_id=E2` but the same business refund intent is a separate risk. Default effect-ID deduplication can suppress repeat delivery of `E1`, but it does **not** deduplicate equivalent business intent across `E1` and `E2`. The separate refund-intent profile addresses that local case and is not composed with C1 by this release.

## 4. The Business Problem

An organization needs to explain more than what a model said or which tool it called. It needs to know what was proposed, who could authorize it, whether that authority was current when the effect was attempted, what the executor reported and what the destination was independently observed to contain. Timeouts, duplicate messages and later authority changes make these different questions.

The reference supplies a connected artifact chain for examining those questions. It does not quantify cost savings, review efficiency, payment settlement or deployment outcomes.

## 5. The Stack in One View

| Component | Responsibility |
|---|---|
| [Cognous Action Manifest](https://github.com/cogno-us/cognous-action-manifest) | Declare the action before evaluating permission. |
| [Cognous Control Plane](https://github.com/cogno-us/cognous-control-plane) | Evaluate proposals against independently resolved authority, revalidate current inputs and preserve the decision record. |
| [Cognous Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) | Constrain the local synthetic SQLite effect beneath current authorization. |
| [Cognous Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) | Reconstruct what retained records support. |
| [Cognous Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | Turn traceable runtime records into reviewable governance evidence. |
| [Open Decision Evidence Standard](https://github.com/cogno-us/open-decision-evidence-standard) | Carry portable decision evidence without deciding recipient reliance. |
| [Cognous Governed Exchange](https://github.com/cogno-us/cognous-governed-exchange) | Governed exchange and continuity for the bounded synthetic workflow. |
| [Cognous Institutional Governance](https://github.com/cogno-us/cognous-institutional-governance) | Supply proposed institutional governance and Authority Context semantics; repository acceptance is not institutional ratification. |
| [Cognous Evidence Attestation](https://github.com/cogno-us/cognous-evidence-attestation) | Verify issuer signatures under an explicit trust snapshot; verification is not factual truth or authority. |
| [Cognous Evidence Registry](https://github.com/cogno-us/cognous-evidence-registry) | Record claims/evidence commitments on a separate local reference path. |

PRP, Research Intelligence and TFA remain optional behavioral instruction layers, not enforcement dependencies.

## 6. Current Quantitative Evidence — Do Not Combine Generations

The selected lock's default release evidence is [CI run 37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916), which tested source `7e43d55c6cc0123a191480a9e6870d6452affa83` and resolved **35 acceptance scenarios**. The retained `full-candidate-gate` artifact digest is `sha256:5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7`. This is the evidence generation selected by the current `component-lock.json`; older 915-test collateral belongs to an earlier persistence generation and is historical.

Separate C1 profile evidence is [run 37682165860](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860): **73 passed**, no failures/errors/skips, against reviewed Control Plane `73e3c65acc47dc43593dcb0420d14032ed410b14` and executor `b1525a7982e52ebb530457f94d5517de032ca4c4`. It is separate profile CI evidence, not a default-release count and not a claim of external-destination atomicity.

The historical protected-worker campaign remains separately scoped to its recorded Ubuntu/bubblewrap fixture. It is not transferred to the current selected pins.

## 7. Recovery, Deduplication and Review

Unknown acknowledgement does not imply absence. Destination observation, executor receipt, policy decision and historical effect are retained as separate facts. A current denial can coexist with an earlier valid local effect.

Effect identity answers “is this the same technical effect?” Business-intent identity answers “is this a second attempt to accomplish the same underlying refund?” The default release qualifies the first boundary, not the second across distinct valid operation identities.

Replay reconstructs retained producer records without rerunning execution. Governance Evidence Pack prepares traceable review material. ODES carries decision evidence for a recipient's own validation and reliance decision. None of these artifacts independently proves external settlement.

## 8. Practical Next Step

Use the [developer quickstart](../docs/quickstart.md), then review outputs with the [governance quickstart](../docs/governance-quickstart.md). For a real pilot, separately qualify identity and credential custody, independent authority resolution, destination semantics, revocation propagation, recovery and operational observation.

## 9. Status and Attribution

This is the current collateral snapshot for accepted hub source `f7d03c719b9be3b9c3fe0fe300df642b0f408d98` and lock digest `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`. The detached [snapshot manifest](evidence-snapshot.json), [selected pins](../component-lock.json), [support status](../docs/release-status.md) and [evidence index](../docs/evidence-index.md) control interpretation. Earlier collateral versions and pre-adoption release documents are historical snapshots and must not be relabeled as current evidence.

[Cognous](https://cogno.us) · [README](../README.md) · [One-page overview](one-page-overview.md). Existing licenses and notices apply.
