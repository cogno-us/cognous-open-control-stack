# Start here: Cognous Open Control Stack

Choose a path. **The hub [component lock](../component-lock.json) is the sole source for selected release revisions.** A newer accepted component commit or a green synthetic orchestration test does not replace its pins.

| Your role | First page | Then |
|---|---|---|
| Developer reproducing the reference | [Developer quickstart](quickstart.md) | [Evidence index](evidence-index.md), [architecture](architecture.md) |
| Security or governance reviewer | [Governance quickstart](governance-quickstart.md) | [Release status](release-status.md), [residual risks](../residual-risks.json) |
| Reviewer of optional runtime modes | [Optional execution profiles](optional-execution-profiles.md) | [Recovery semantics](recovery-semantics.md) |
| Evaluator of newer O5/O6 synthetic integration | [Orchestrator overview](https://github.com/cogno-us/cognous-stack-orchestrator/blob/main/README.md) | [O6-Q4 synthetic handoff](https://github.com/cogno-us/cognous-stack-orchestrator/blob/main/development/acceptance/o6-q4/README.md) |
| Operator assessing real deployment | [Release status](release-status.md) | [Operational trust issue #30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30): **HOLD / NOT ESTABLISHED** |

## What you can reproduce

The selected hub is a **bounded synthetic local reference**. It separates declaring a proposed effect, evaluating independently supplied Authority Context, executing under the supported local boundary, observing or reconciling the destination, and packaging the retained record. It is not a real payment integration, institutional adoption or production deployment.

**Example — uncertain synthetic refund:**

1. A Manifest declares refund intent for a synthetic account and amount. The declaration itself grants no permission.
2. The Control Plane evaluates a resolver-supplied context, current grant/policy and the exact proposal. C0 revalidates critical inputs before dispatch; it is **not atomic with the destination commit**.
3. The Runtime attempts one identified effect `E1`. The caller times out: delivery is `unknown`, not failed.
4. Reconciliation checks the original effect `E1`. Neither timeout nor absent observation authorizes a new `E2` or safe retry. Effect-ID dedupe is not the same as dedupe of equivalent business intent.
5. Replay and Evidence Pack preserve related decision, attempt and observation records. Evidence packaging does not independently certify settlement.

See [recovery semantics](recovery-semantics.md) for the exact supported recovery behavior. Optional C1 is same-host and not selected by default; **C2/C3 are not qualified**.

## Selected, accepted, historical and operational are different

- **Selected:** revisions and interfaces in [`component-lock.json`](../component-lock.json), interpreted with [release status](release-status.md).
- **Accepted component source:** a reviewed merge in its owning repository; not necessarily selected by the hub.
- **Historical evidence:** test counts, pins, examples or shell instructions from an earlier checkpoint. Their evidence remains valid for their original revision, not for a later one.
- **Operationally qualified:** would require independently reviewed deployment, trust roots, key custody and environment evidence. That has not been established; see [#30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30).

**When reproducing an old checkpoint**, use its exact checkout and report its historical status. Do not present an archived command as a test of current main. No quickstart grants authority or enables live payment effects.
