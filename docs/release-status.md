# Support and release status

The [component lock](../component-lock.json) selects the merged consumer generation qualified by [hub PR #23](https://github.com/cogno-us/cognous-open-control-stack/pull/23), accepted at `f801546d5272104b02a240e1126b3f92f26486f2`. This remains a bounded synthetic reference, not a production deployment.

## Evidence supporting adoption

[Full candidate CI 37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916) tested source `7e43d55c6cc0123a191480a9e6870d6452affa83`. Authority, exchange, consumer and registry batches passed. The aggregate resolved all **35 acceptance scenarios**, with required suites executed twice. Historical compatibility, mocked OpenShell, Index chain and optional-package static checks were retained. Artifact `full-candidate-gate` has digest `sha256:5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7`.

Adoption-head CI is a separate check: paired-request qualification now uses a new baseline matrix; the old matrix and historical evidence are retained. See the [adoption checkpoint](workstreams/merged-pin-adoption-checkpoint.md) and [selected interfaces](compatibility.md).

## Selected behavior and optional profiles

The selected GAX `merged-producers-v1` compatibility profile uses the ordinary bounded executor path. New source revisions include non-authorizing Decision Input Commitment sidecars and opt-in authority/effect and refund-intent implementations, but this lock does not activate them. Same-host atomic authority/effect qualification and logical-intent ownership remain separately scoped profiles; they are mutually exclusive per database. Their guarantees are not composed here.

Recovery keeps current authorization denial distinct from historical effects. Unknown delivery is not permission to retry; accepted record reconstruction is not policy reevaluation, external truth or independent delivery verification. Equivalent intent across distinct operation identities remains a characterized limitation of the selected path.

## Deployment limits

The earlier protected-worker campaign applies to its recorded revisions and Ubuntu/bubblewrap environment. It is not automatically transferred to these new pins; any rerun is recorded separately. Live OpenShell, production institutional resolvers, credential/key separation, remote revocation propagation, arbitrary-agent confinement, distributed budgets and independent operational review remain outside this release claim.

PRP, TFA and Research Intelligence checks are static/schema checks, not model-behavior efficacy evidence. Human review burden and enterprise benefit remain unmeasured. Governed Exchange PR #2 remains deferred.

[Prior release status](release-status-before-merged-adoption.md) retains the earlier 915-test campaign, protected-worker evidence, source/merge distinctions and historical failures without rewriting their scope.
