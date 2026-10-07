# Support and release status

Documentation baseline: accepted hub
[`5737267d94d2b445735c95e8480a31de73a2abe8`](https://github.com/cogno-us/cognous-open-control-stack/commit/5737267d94d2b445735c95e8480a31de73a2abe8).
This is a bounded synthetic reference. Its supported integration is determined by
[component-lock.json](../component-lock.json), not by newer component default branches.
The [compatibility table](compatibility.md) gives the selected contracts.

## Accepted qualification

[CI run 37616662337](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37616662337) tested head `7c7eaa0a72401a789c0a5adac59f68d59b94ff19`, accepted through PR #8 at merge `41c2eec80556cadbe27e313f504bc027e0823c39`.
Each of two isolated repetitions passed **915 Python tests**, with zero failures,
errors or skips. All **35 matrix entries** satisfied their gates; the equivalent-intent
case remains a characterized limitation. Transported repeatability passed, as did
120 separate mocked OpenShell tests. Archive and indexed-file hashes were verified.
See the [machine-readable summary](../examples/control-plane-store-adoption/qualification-summary.json).

## Separate accepted protected-worker profile

Hub PR #11 accepted the [completed compatible-host review](workstreams/protected-qualification-checkpoint.md#completed-compatible-host-review): twelve isolated cases and 17 verifier tests passed on Ubuntu 22.04.5, Linux 6.8.0-1064-azure, bubblewrap 0.6.1 and Python 3.11.16. [Campaign](../examples/protected-qualification/ci-37621009389/campaign/summary.json) and [provenance](../examples/protected-qualification/ci-37621009389/provenance.json) retain actual results and distinguish source head from Actions merge ref. The reference gate also passed at that reviewed source.

This is a separate fixed worker fixture with a trusted host, private-path/loopback probes and direct destination checks. It does not qualify live OpenShell, arbitrary agents, production credentials or deployment-wide non-bypassability. Earlier blocked Ubuntu 24.04 evidence remains unchanged.

**Pending:** [executor PR #14](https://github.com/cogno-us/cognous-execution-runtime/pull/14) has not been accepted at this snapshot. Logical-intent prevention is not selected or qualified by the hub; equivalent-intent duplication remains a characterized limitation.

## Mechanism, qualification and adoption

“Implemented” means a mechanism exists. “Tested locally” and “tested in pinned CI”
identify executed evidence at specific sources. “Selected” means the hub lock uses
that source; it is not itself a test result. “Live-qualified” requires separately
executed live evidence. “Unexecuted”, “blocked” and “deferred” are not passes.

| Mechanism | Executed qualification | Selected hub integration | Still unsupported or unexecuted |
|---|---|---|---|
| Transported refund, authorization, constrained effect and retained evidence chain | [Accepted persistence summary](../examples/control-plane-store-adoption/qualification-summary.json): 915 Python tests per repetition; 35 matrix entries satisfied; repeatability and mock OpenShell pass | Yes, selected GAX `9984d90…` | Production authority authentication and independent real-world verification |
| Original-effect reconciliation and changed-authority denial | Current matrix retains passing changed-authority and late-commit cases in both repetitions | Yes; historical effects and current denied recovery remain separately attributed | Rollback, cancellation/termination finality or permission to retry after observed absence |
| Same-host destination concurrency and process-death recovery | [Worker 16](workstreams/process-boundary-checkpoint.md), [evidence directory](../examples/process-boundary/); independent Control Plane stores for concurrent destination cases | Separate accepted hub qualification at its recorded baseline; not an extra pass of the shared release runner | Cross-host/distributed guarantees; shared-store repair is qualified separately below |
| Control Plane record persistence repair | [Accepted component contract/checkpoint](https://github.com/cogno-us/cognous-control-plane/blob/248d899634d9db3518e831bc7ab568a48733f825/docs/workstreams/store-concurrency-checkpoint.md); 20 upstream persistence tests passed in each repetition | **Accepted and qualified** at `248d899…` | Cooperating same-host record transactions on supported local Linux filesystems only; not whole-workflow atomicity or distributed persistence |
| Repaired-generation consumer compatibility | Accepted Replay `043830b…`, ODES `0486b64…`, Evidence Pack `de6b9e0…` and Alvorada/GAX `9984d90…` explicitly support the repaired Control Plane generation | **Accepted and qualified** in both hub repetitions | Evidence Pack 0.3.1 persistence compatibility is mandatory under the selected generation, including unchanged producer-store assertions; previous 0.3.0 and historical 0.2.6 suites remain isolated; 26 Evidence Pack persistence cases and 18 Replay persistence cases passed in each repetition |
| Optional OpenShell adapter and packaged worker | Hub tests mocked adapter. Separately accepted image merge [`ff4eab5…`](https://github.com/cogno-us/cognous-execution-runtime/commit/ff4eab5228c19f73aeb2a61d48046dd29111c6a9); actual Docker worker evidence is recorded in the [accepted readiness checkpoint](https://github.com/cogno-us/cognous-execution-runtime/blob/12b9c55637e2472a1a5ce3036c787e9427c6abd8/docs/workstreams/live-openshell-qualification-checkpoint.md#accepted-packaged-image-evidence-reused) | Hub selects executor `177354e…`; neither image qualification nor readiness revision `12b9c55…` is adopted | Live OpenShell execution/confinement remains unqualified; readiness work was blocked on unavailable prerequisites |
| BitRep and Index local reference | Separate evidence path in the [current summary](../examples/control-plane-store-adoption/qualification-summary.json) | Selected for bounded evidence scenarios | Signature or chain inclusion does not confer institutional authority; no public-chain deployment |
| PRP, TFA, Research Intelligence | Static/schema checks only | Optional, not enforcement dependencies | Model-behavior efficacy remains unexecuted |

## Adoption and release gates

PR #8 now selects the accepted persistence-compatible dependency generation after the owning consumers cleared their exact-revision compatibility gates. The two-repetition release matrix and final-head push CI passed; Governor review accepted the merge. This qualifies the bounded reference, not production deployment.

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
deduplication. Historical Worker 16 evidence at the former selected Control Plane pin observed shared-store record loss and remains unchanged. PR #8 does not relabel that evidence; the repaired generation passed its separately attributed required persistence matrix. Equivalent-intent duplication remains unchanged.

Production institutional resolvers, credential custody/separation, revocation
propagation, live confinement, fleet orchestration, distributed budgets,
cancellation/finality and independent verification need deployment-specific
qualification. Human-review effort and enterprise benefit remain unmeasured.
Alvorada PR #2 remains deferred and excluded. See the [risk register](../residual-risks.json)
and its [documentation follow-ups](downstream-readme-corrections.md).
