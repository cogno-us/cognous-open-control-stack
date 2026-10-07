<!-- cognous-banner:start -->
```text
──────────────────────────────────────────────────
   __________  _______   ______  __  _______
  / ____/ __ \/ ____/ | / / __ \/ / / / ___/
 / /   / / / / / __/  |/ / / / / / / /\__ \
/ /___/ /_/ / /_/ / /|  / /_/ / /_/ /___/ /
\____/\____/\____/_/ |_/\____/\____//____/
       O P E N   C O N T R O L   S T A C K
       g o v e r n e d   b y   d e s i g n
  github.com/cogno-us/cognous-open-control-stack
──────────────────────────────────────────────────
```
<!-- cognous-banner:end -->

# Cognous Open Control Stack

A public, pinned **bounded synthetic reference** for governed agent actions.
The stack connects a declared action to institutional authority, authorization,
a constrained local effect, and traceable reconstruction and review artifacts.
This repository owns integration qualification and documentation; component
repositories own their implementations.

Engineers can evaluate the contracts and failure behavior. Enterprise architects,
security and governance reviewers can inspect the evidence and deployment gaps.
Passing the reference is not production approval, compliance certification or
independent verification of real-world effects.

## Try the supported workflow

The reference delivers a synthetic refund through local durable transport and
GAX recipient assessment. A Manifest-bound proposal is evaluated against a
separately supplied Authority Context; the Control Plane revalidates at effect
time, and Moltbot Safe applies a bounded SQLite destination effect. Retained
Replay, ODES and IMX artifacts connect that operation to a Governance Evidence Pack.

From the repository root, after the [quickstart prerequisites](docs/quickstart.md):

```bash
python tools/reference_release.py run --results-dir results/reference
```

The runner checks out exact [component pins](component-lock.json), executes two
isolated repetitions and required negative/recovery suites, and writes evidence
with hashes. OpenShell coverage in this runner is mocked. No production accounts,
public-chain writes or paid provisioning are involved.

## Evaluate the evidence

- [Developer quickstart](docs/quickstart.md) — setup, command behavior and outputs.
- [Responsibility map](docs/architecture.md) — authority, execution, exchange and evidence owners.
- [Support and release status](docs/release-status.md) — selected integration versus separately accepted component work.
- [Evidence index](docs/evidence-index.md) — exact runs, provenance and historical snapshots.
- [Recovery semantics](docs/recovery-semantics.md) — uncertainty, observation, denial and retained history.
- [Governance quickstart](docs/governance-quickstart.md) — review questions and authority boundaries.
- [Compatibility](docs/compatibility.md), [threat model](docs/security-and-threat-model.md) and [risk register](residual-risks.json).

## Limits that matter

PR #8 proposes the repaired Control Plane persistence generation and requires
spawned-process shared-store qualification in both release repetitions. Worker 16's
prior record-loss evidence remains historical at its original pin. Equivalent
business intent under different valid proposals can produce multiple effects:
effect-ID deduplication is not
business-intent deduplication. Live OpenShell execution/confinement, production
institutional authentication, remote finality and distributed guarantees remain
unqualified. No rollback or exactly-once delivery guarantee is made.

Signatures, chain inclusion, message receipt and behavioral protocols do not
authorize execution. ISS, Navalia and private research are outside this public
integration. See [licensing](LICENSING.md), [LICENSE](LICENSE), [NOTICE](NOTICE)
and the [documentation follow-up register](docs/downstream-readme-corrections.md).
