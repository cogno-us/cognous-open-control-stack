# Shared synthetic governance comparison

This battery tests whether three configured applications satisfy the same bounded
policy and fault schedules. It measures destination state, decision conformance
and durable refusal coverage. It is designed to permit a tie: proper conventional
controls are a meaningful baseline. It does not assert that Cognous is superior.

## Configurations under test

| Configuration | Actual implementation | Application controls supplied by this repository |
| --- | --- | --- |
| Cognous protected destination | Existing optional `ProtectedDestination` | Synthetic signing clients, trusted bootstrap and clock; existing destination implementation unchanged. |
| OPA transactional application | OPA 1.21.2 binary evaluates `policy.rego` | SQLite writer transaction, current state, signature verification, effect-ID idempotency and durable audit. Those are application responsibilities, not native OPA guarantees. |
| LangGraph plus OPA application | LangGraph 1.2.15 with SQLite checkpoint persistence and a real interrupt/resume | Same OPA application behind the effect node. Harness automatically resumes approval; no human participant or approval-quality claim. |

The Cognous subject is an **optional hub profile**, not the historical selected
component chain. This battery does not move `component-lock.json` or select a new
release profile. OPA and LangGraph are actual dependencies, not simulations of
those products. Shared Cognous wire/signature helpers give all three configurations
identical signed inputs; this is not an independent cryptographic implementation
comparison. The conventional adapter implements only the declared benchmark policy,
not every validation or feature of the Cognous implementation.

## Fixed plan and independent observations

`benchmarks/governance/plan.json` declares 24 scenarios, expected decisions, effect
counts, allowed effect identifiers and exact payloads. Each GitHub job executes ten
repetitions per scenario per configuration, in seeded randomized order. Two separate
jobs use seeds 1701 and 1702. This produces 720 case trials per job, 1,440 overall;
repetitions are not additional independent scenarios or evidence of field efficacy.

Cases cover a permitted effect; missing/revoked/expired grants; stale and unissued
generations; changed policy/target; absent/stale verifier; forged signatures and
direct agent calls; hard-pin rotation; lost acknowledgement and reopened storage;
conflicting redelivery; budget exhaustion; historical receipt reads after revocation;
a new effect after revocation; audit failure; barrier-synchronized last-budget
contention; a retained signed request after time/authority changes; and real child
process exits immediately before audit/commit and after destination commit.

A separate read-only SQLite connection inspects actual effects and events. Success
requires exact effect cardinality, permitted identifiers/payloads, expected decisions
and a durable reason/digest/time record for every returned denial. An expected audit
outage is recorded as unavailable, never as a durable denial. Any other database
error propagates as a harness failure. Crash exit codes and immediate destination
counts are retained; the next fresh command tests retry reconciliation. This tests
same-host destination recovery, not native LangGraph resumption of a crashed graph,
cross-host recovery or power-loss/storage hardware behavior.

The scoring oracle has negative tests for fabricated success receipts, missing or
extra effects, incorrect identity/payload, false allows/blocks, missing or unrelated
denial evidence and truncated outcomes. Four ablations deliberately remove revocation,
target, verifier and budget checks from the conventional configuration. Every ablation
must be detected. These demonstrate sensitivity to those specific faults; they do
not measure every Cognous control's marginal contribution.

## Measurement and fairness

The plan and source are committed before qualified GitHub runs, and each report
records their commit and SHA-256. Exploratory local adapter checks precede that
freeze. This is **not independently preregistered, independently reviewed, or a
hidden held-out benchmark**. Benchmark authors also implemented the baseline.

Primary outcomes are conformance and actual destination state. Unexpected-effect
counts are cardinality excesses against the fixture; wrong identities or payloads
also fail conformance but are not silently folded into that count. False allows
and blocks compare the predefined decision sequence; they are not population-rate
estimates. Minimal durable-refusal coverage does not score institutional adequacy,
complete authority-input reconstruction, external custody or independent review.

Execution wall times are retained, with median and nearest-rank p95 for permitted
calls. They exclude fixture provisioning and request signing, but include OPA CLI
process startup and LangGraph's checkpoint and interrupt round trips. They must
**not** be presented as intrinsic engine speed, cloud latency, human review latency
or a normalized performance ranking. Concurrent calls use one host and SQLite.
No model inference, tool selection quality, token cost or protocol efficacy is measured.

## Reproduction and GitHub evidence

Use Python 3.12 on Linux. Install the exact packages in
`benchmarks/governance/requirements.txt`. Obtain the OPA binary from the URL in
`dependencies.json` and verify its pinned SHA-256 before execution. From a clean,
committed checkout:

```sh
python -m unittest discover -s tests -p test_comparative_governance.py -v
python tools/run_comparative_governance.py \
  --opa /absolute/path/to/opa --seed 1701 --output /new/output/directory
```

The workflow `Shared synthetic governance comparison` checks out the exact PR
head, runs seeds 1701/1702 independently and uploads JSON observations, readable
summaries, plan and dependency pins. Raw databases stay on the disposable runner;
no private signing key is serialized in the reports. The full dependency environment,
Python/SQLite versions, source revision and plan hash are retained. Any mismatch
fails the job while preserving the completed result report. An interrupted or
infrastructure-failed run is incomplete, not a pass.

## Comparisons and evidence still missing

- **AgentCore:** NOT RUN. No configured authorized AWS test environment or account
  resources. A real adapter must use equivalent tool policies and actual destination
  observations, including session reset and revocation/commit boundary cases.
- **Temporal:** NOT RUN. A server/worker recovery adapter is not implemented here.
  A future comparison must include actual worker termination, workflow replay and
  destination idempotency, with authorization supplied explicitly by the application.
- **Historical selected Cognous chain:** not a shared-scenario adapter in this battery.
  Existing pinned-chain qualification remains separately reported by its own workflow.
- **Deployment and research outcomes:** no independent security review, real provider
  IAM, external monotonic authority, human effort measurement or live model study.

Passing all three configurations supports parity on this bounded policy. It does
not establish product-wide parity or superiority, comprehensive safety, legal
clearance or operational trust. Release and production authorizations remain false;
operational trust remains **HOLD / NOT ESTABLISHED**.

## Adversarial corner-case extension

`benchmarks/governance/corner-plan.json` freezes 19 scenarios, five repetitions
per seed, two seeds. It includes five baseline controls, verifier command/digest/
generation/activity/time substitutions, payload substitution with and without
re-signing, strict schema/identifier cases, and exact-command replay. The same expected
statuses, destination contents, and durable-denial oracle apply to all profiles.
No comparator control is removed for this measurement.

This is an exploratory plan informed by adapter code inspection, not a blinded
benchmark. Six cases exercise the strict Cognous wire/single-use-command contract;
failing these demonstrates missing checks in our comparator application, not an
inherent OPA or LangGraph limitation. Accepting an identical duplicate receipt
is not an additional destination effect. Shared authorization-binding cases must
be reported separately from these integration differences.

The original baseline still gates CI. The corner step uses explicit observation
mode: all mismatches remain in raw results and `benchmark_pass=false`; completing
the observation is not passing conformance. Exceptions still fail the job and
all four control-removal probes must be detected. No runtime or comparator
implementation is changed to manufacture a favorable result. Evidence artifacts
contain synthetic records only; private signing keys and databases stay local.
