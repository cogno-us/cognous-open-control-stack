# Support and release status

Documentation baseline: accepted hub
[`f8afac8fae9ebcedb207c46cdaba51728a918d5b`](https://github.com/cogno-us/cognous-open-control-stack/commit/f8afac8fae9ebcedb207c46cdaba51728a918d5b).
This is a bounded synthetic reference. Its supported integration is determined by
[component-lock.json](../component-lock.json), not by newer component default branches.
The [compatibility table](compatibility.md) gives the selected contracts.

## Mechanism, qualification and adoption

“Implemented” means a mechanism exists. “Tested locally” and “tested in pinned CI”
identify executed evidence at specific sources. “Selected” means the hub lock uses
that source; it is not itself a test result. “Live-qualified” requires separately
executed live evidence. “Unexecuted”, “blocked” and “deferred” are not passes.

| Mechanism | Executed qualification | Selected hub integration | Still unsupported or unexecuted |
|---|---|---|---|
| Transported refund, authorization, constrained effect and retained evidence chain | [Worker 14d full/research summary](../examples/worker14d-recovery/qualification-summary.json): 843 Python tests per full repetition; 30 required matrix entries pass in each; repeatability and mock OpenShell pass | Yes, including GAX `c52f9f0…`; see [execution checkpoint](workstreams/recovery-authority-checkpoint.md#worker-14d--completed-local-qualification-pending-review) | Production authority authentication and independent real-world verification |
| Original-effect reconciliation and changed-authority denial | Same summary: 10 focused changed-authority cases pass; 19 research tests pass in each of two runs | Yes; historical effects and current denied recovery remain separately attributed | Rollback, cancellation/termination finality or permission to retry after observed absence |
| Same-host destination concurrency and process-death recovery | [Worker 16](workstreams/process-boundary-checkpoint.md), [evidence directory](../examples/process-boundary/); independent Control Plane stores for concurrent destination cases | Separate accepted hub qualification at its recorded baseline; not an extra pass of the shared release runner | Cross-host/distributed guarantees; concurrent shared Control Plane store at selected pin |
| Control Plane record persistence repair | [Accepted component contract/checkpoint](https://github.com/cogno-us/cognous-agent-control-plane/blob/248d899634d9db3518e831bc7ab568a48733f825/docs/workstreams/store-concurrency-checkpoint.md) | **No**: hub selects `2ea9528…`, not accepted repair `248d899…` | Selected store remains unsupported for concurrent writers, with observed record loss; repaired component scope is cooperating writers on supported local Linux filesystems, not whole-workflow atomicity |
| Replay compatibility with repaired Control Plane | [Accepted component checkpoint](https://github.com/cogno-us/cognous-agent-replay-bundle/blob/043830b56595cecddfa65c064afd1c0b95e64792/docs/workstreams/replay-control-plane-persistence-checkpoint.md): 18 focused and 231 full tests on Python 3.11/3.12 | **No**: hub selects `274543f…`, not `043830b…` | ODES/Evidence Pack/GAX compatibility and separately qualified hub adoption are required |
| Optional OpenShell adapter and packaged worker | Hub tests mocked adapter. Separately accepted image merge [`ff4eab5…`](https://github.com/cogno-us/moltbot-safe/commit/ff4eab5228c19f73aeb2a61d48046dd29111c6a9); actual Docker worker evidence is recorded in the [accepted readiness checkpoint](https://github.com/cogno-us/moltbot-safe/blob/12b9c55637e2472a1a5ce3036c787e9427c6abd8/docs/workstreams/live-openshell-qualification-checkpoint.md#accepted-packaged-image-evidence-reused) | Hub selects executor `177354e…`; neither image qualification nor readiness revision `12b9c55…` is adopted | Live OpenShell execution/confinement remains unqualified; readiness work was blocked on unavailable prerequisites |
| BitRep and Index local reference | Separate evidence path in the [full summary](../examples/worker14d-recovery/qualification-summary.json) | Selected for bounded evidence scenarios | Signature or chain inclusion does not confer institutional authority; no public-chain deployment |
| PRP, TFA, Research Intelligence | Static/schema checks only | Optional, not enforcement dependencies | Model-behavior efficacy remains unexecuted |

## Adoption and release gates

At inspection, [hub PR #8](https://github.com/cogno-us/cognous-open-control-stack/pull/8)
was an **open draft**, recording blocked persistence adoption with no pin change.
Its blocker statement describes the consumers inspected at that time. Replay has
since accepted compatibility at the exact revision above, but the hub still selects
the old consumer set. Component acceptance does not advance the lock or establish
stack qualification. ODES/Evidence Pack and later GAX work must be accepted and
then separately adopted; this documentation batch anticipates no merges.

The runner requires both transported representative runs, normalized repeatability,
all required matrix references and pinned suites to pass. Missing, failed, skipped
or unexecuted required coverage fails the gate. Successful paths must expose the
required original artifacts, consistent decision/effect/attempt identities and
expected destination content; evidence recovery must not create a replacement effect.
Final-head CI and review remain separate from earlier local evidence.

[Evidence navigation](evidence-index.md) distinguishes the latest selected-pin
recovery run from earlier accepted runs and historical failures. Historical
checkpoints retain their original “pending” or “blocked” wording and are not
rewritten as current status.

## Limits for an evaluator

Equivalent-intent proposals under a multi-use grant produced two effects; replay
of the same effect produced no third. Effect-ID deduplication is not business-intent
deduplication. The selected Control Plane shared JSON store has observed record loss.
Neither is erased by a newer component acceptance.

Production institutional resolvers, credential custody/separation, revocation
propagation, live confinement, fleet orchestration, distributed budgets,
cancellation/finality and independent verification need deployment-specific
qualification. Human-review effort and enterprise benefit remain unmeasured.
Alvorada PR #2 remains deferred and excluded. See the [risk register](../residual-risks.json)
and its [documentation follow-ups](downstream-readme-corrections.md).
