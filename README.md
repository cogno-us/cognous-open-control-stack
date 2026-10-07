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

A pinned public reference integration for governed agent actions. This repository is the architecture, compatibility, scenario and evidence hub; runtime implementations remain in their owning repositories.

## One command

```bash
python tools/reference_release.py run --results-dir results/reference
```

The runner checks out exact component SHAs from [component-lock.json](component-lock.json), executes the synthetic bounded workflow twice, runs negative/recovery suites, qualifies the mocked optional OpenShell adapter separately, and writes one evidence directory with hashes.

The Batch 4C dependency lock uses **accepted pins**, including the Alvorada PR #6 merge.
Hub CI and review remain separate acceptance gates. See the
[durable integration checkpoint](docs/workstreams/batch4c-integration-checkpoint.md).

## Reference flow

```text
GAX delivery
  -> recipient assessment
  -> Manifest-bound proposal
  -> independent Alvorada Authority Context
  -> Control Plane authorization + effect-time revalidation
  -> Moltbot Safe constrained synthetic destination
  -> Replay reconstruction
  -> Governance Evidence Pack
  -> optional ODES recipient validation
  -> IMX continuity/recovery
```

BitRep and The Index are exercised as a separate evidence path. Signature verification and chain inclusion do **not** grant execution authority. PRP, TFA and Research Intelligence remain optional.

## Read next

- [Quickstart](docs/quickstart.md)
- [Architecture and responsibility map](docs/architecture.md)
- [Compatibility and interface gaps](docs/compatibility.md)
- [Reference candidate status](docs/release-status.md)
- [Evidence index](docs/evidence-index.md)
- [Security and threat model](docs/security-and-threat-model.md)
- [Governance quickstart](docs/governance-quickstart.md)
- [Downstream documentation corrections](docs/downstream-readme-corrections.md)
- [Residual-risk register](residual-risks.json)
- [Licensing inventory](LICENSING.md)

## Evidence semantics

Use these states exactly: **implemented**, **tested locally**, **tested in pinned CI**, **live-qualified**, **unexecuted**, **blocked**, **deferred**.

A valid signature is not authority. A declaration is not permission. Authorization is not execution. An acknowledgement is not destination observation. Reconstruction is not independent verification. ODES is decision evidence, GAX is exchange semantics, and transport is delivery.

## Scope

This is a synthetic public reference candidate, not a production deployment or fleet orchestrator. It performs no public-chain write, production transaction or paid provisioning. ISS, Navalia and private research are outside this repository. See [LICENSE](LICENSE), [NOTICE](NOTICE) and [LICENSING.md](LICENSING.md).
