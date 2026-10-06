# Cognous Open Control Stack

A pinned public reference integration for governed agent actions. This repository is the architecture, compatibility, scenario and evidence hub; runtime implementations remain in their owning repositories.

## One command

```bash
python tools/reference_release.py run --results-dir results/reference
```

The runner checks out exact component SHAs from [component-lock.json](component-lock.json), executes the synthetic bounded workflow twice, runs negative/recovery suites, qualifies the mocked optional OpenShell adapter separately, and writes one evidence directory with hashes.

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
