# Supplied agent inventory reconciliation

This optional reference checker partially addresses OG01 of the 7 October enterprise lifecycle addendum. It compares supplied inventory records; it neither discovers deployments nor admits work. It is independent of the current release path, deployment packet and accepted component selection. The source addendum is not reproduced here.

Base: `649df22a1392af2c4fa77e4c71749c482f82649c`. The accepted environment prerequisite observer and deployment checklist do not reconcile logical agents with deployment instance populations. This isolated tool adds that comparison, with no change to their behavior. Hub instructions in CONTRIBUTING.md prefer a small public hub; this intentionally bounded reference utility follows the existing `tools/` qualification pattern and introduces no package, runtime service or asset-management subsystem.

## Contract

`tools.lifecycle_inventory.reconcile(packet, now=..., max_age=...)` accepts `agent-inventory-reconciliation/1`. Times are nonnegative integer UTC seconds from the trusted caller; `max_age` is a declared freshness bound. The packet declares tenant, environment, an inclusive observation window, nonempty unique required connector identifiers, connector observations, logical agent records and observed deployment instances. See the executable harmless fixture in `tests/test_lifecycle_inventory.py` for the complete input shape.

Agent records retain separate agent ID, instance/workload bindings with half-open validity periods, owner, backup owner, accepted release and one of six lifecycle states. Observations carry scope, instance, claimed logical agent, workload identity, observed release, connector and observation time. Replica credentials need not be shared. Unknown contract versions and malformed or cross-scope input are rejected. There is no migration from existing inventories: deployment adapters must explicitly map records into this optional contract.

The report distinguishes missing owners, missing accepted releases, invalid binding periods, unregistered agents/replicas, unobserved registrations, mismatched workload/release and duplicated instance bindings. A registration not observed is a discrepancy requiring investigation, not proof the deployment is absent. Duplicate observations are rejected instead of overwritten; multi-connector deduplication needs a separate provenance-preserving adapter. Non-active states, including retired, produce a review hold. This does not enforce a deployment admission hold.

Missing, stale, partial and unavailable connectors remain explicit even with an empty population. `declared_coverage_current` only describes the supplied declarations for the caller-selected connectors. It does not verify those declarations, measure enterprise coverage or imply all platforms were selected. `no_supplied_discrepancies` is deliberately not an approval. `authorizing`, `deployment_qualified` and `discovery_verified` are always false.

## Validation and residual work

Run the standard-library bounded fixture suite:

```bash
python -m unittest discover -s tests -p test_lifecycle_inventory.py -v
```

Sixteen tests passed locally on the implementation branch. They cover replica and owner gaps, binding expiry at the boundary, five inactive states, incomplete and empty discovery, duplicate bindings and observations, scope isolation, release/workload drift, observation freshness and malformed contracts. Dedicated Linux CI has a three-minute limit; its observed result belongs to the PR, not this local result.

OG01 remains partial. Production discovery, attested identity/owner/release sources, owner departure, state transition authorization, queue/in-flight resolution, credential/grant withdrawal, durable immutable retirement tombstones, retention and protected live admission need component/deployment work. This checker cannot prove that a retired deployment stopped or that active metadata supplies action authority. Review outputs themselves are not a trusted control path.

OG02 (exact extension artifacts), OG03 (adapter semantics and generation activation), OG04 (reliability admission) and OG05 (incident handoff) are not implemented by this batch. No production, vendor parity, runtime enforcement or completeness claim follows. No accepted pins or shared release evidence contracts change.
