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
| Transported refund, authorization, constrained effect and retained evidence chain | [Worker 14d full/research summary](../examples/worker14d-recovery/qualification-summary.json): 843 Python tests per full repetition; 30 required matrix entries pass in each; repeatability and mock OpenShell pass | Yes, with PR #8 selected GAX `9984d90…`; see [execution checkpoint](workstreams/recovery-authority-checkpoint.md#worker-14d--completed-local-qualification-pending-review) | Production authority authentication and independent real-world verification |
| Original-effect reconciliation and changed-authority denial | Same summary: 10 focused changed-authority cases pass; 19 research tests pass in each of two runs | Yes; historical effects and current denied recovery remain separately attributed | Rollback, cancellation/termination finality or permission to retry after observed absence |
| Same-host destination concurrency and process-death recovery | [Worker 16](workstreams/process-boundary-checkpoint.md), [evidence directory](../examples/process-boundary/); independent Control Plane stores for concurrent destination cases | Separate accepted hub qualification at its recorded baseline; not an extra pass of the shared release runner | Cross-host/distributed guarantees; concurrent shared Control Plane store at selected pin |
| Control Plane record persistence repair | [Accepted component contract/checkpoint](https://github.com/cogno-us/cognous-agent-control-plane/blob/248d899634d9db3518e831bc7ab568a48733f825/docs/workstreams/store-concurrency-checkpoint.md); PR #8 release gate executes the upstream concurrency suite in both repetitions | **Selected for PR #8 qualification** at `248d899…`; stack support remains contingent on this PR's matrix/CI | Cooperating same-host record transactions on supported local Linux filesystems only; not whole-workflow atomicity or distributed persistence |
| Repaired-generation consumer compatibility | Accepted Replay `043830b…`, ODES `0486b64…`, Evidence Pack `de6b9e0…` and Alvorada/GAX `9984d90…` explicitly support the repaired Control Plane generation | **Selected for PR #8 qualification**; component acceptance remains distinct from hub qualification | Evidence Pack 0.3.1 persistence compatibility is mandatory under the selected generation, including unchanged producer-store assertions; previous 0.3.0 and historical 0.2.6 suites remain isolated; PR #8 must pass both repetitions and final-head CI |
| Optional OpenShell adapter and packaged worker | Hub tests mocked adapter. Separately accepted image merge [`ff4eab5…`](https://github.com/cogno-us/moltbot-safe/commit/ff4eab5228c19f73aeb2a61d48046dd29111c6a9); actual Docker worker evidence is recorded in the [accepted readiness checkpoint](https://github.com/cogno-us/moltbot-safe/blob/12b9c55637e2472a1a5ce3036c787e9427c6abd8/docs/workstreams/live-openshell-qualification-checkpoint.md#accepted-packaged-image-evidence-reused) | Hub selects executor `177354e…`; neither image qualification nor readiness revision `12b9c55…` is adopted | Live OpenShell execution/confinement remains unqualified; readiness work was blocked on unavailable prerequisites |
| BitRep and Index local reference | Separate evidence path in the [full summary](../examples/worker14d-recovery/qualification-summary.json) | Selected for bounded evidence scenarios | Signature or chain inclusion does not confer institutional authority; no public-chain deployment |
| PRP, TFA, Research Intelligence | Static/schema checks only | Optional, not enforcement dependencies | Model-behavior efficacy remains unexecuted |

## Adoption and release gates

PR #8 now selects the accepted persistence-compatible dependency generation after the owning consumers cleared their exact-revision compatibility gates. This is a proposed hub adoption until the required two-repetition release matrix and final-head CI pass; component acceptance alone is not stack qualification.

The runner requires both transported representative runs, normalized repeatability,
the selected-generation Evidence Pack persistence suite with its four explicit producer inputs,
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
deduplication. Historical Worker 16 evidence at the former selected Control Plane pin observed shared-store record loss and remains unchanged. PR #8 does not relabel that evidence; the repaired generation must instead pass its new required persistence matrix. Equivalent-intent duplication remains unchanged.

Production institutional resolvers, credential custody/separation, revocation
propagation, live confinement, fleet orchestration, distributed budgets,
cancellation/finality and independent verification need deployment-specific
qualification. Human-review effort and enterprise benefit remain unmeasured.
Alvorada PR #2 remains deferred and excluded. See the [risk register](../residual-risks.json)
and its [documentation follow-ups](downstream-readme-corrections.md).
