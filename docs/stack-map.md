# Stack map

One row per repository in the Open Control Stack: its name, repository, purpose, group, status label and link. This page is the canonical component map. The names used here are defined in [naming](naming.md); commands and profiles per repository are in [profiles and tools](profiles-and-tools.md).

The map is a navigation and responsibility map. It is not an execution sequence and it does not change any selected interface. Selected revisions come only from the [component lock](../component-lock.json), interpreted with [release status](release-status.md). Scope and limits are stated once in [guarantees and limits](guarantees-and-limits.md).

## Status labels

| Label | Meaning on this page |
|---|---|
| merged | Reviewed and merged in the owning repository. Not by itself part of the selected set. |
| selected | Pinned in the hub component lock as a selected component. |
| known limit | A limitation that existing documentation already states; it is kept visible, not removed. |
| proposed | Draft or planned work that is not implemented as a supported interface. |

A repository can carry more than one label across its parts. The component rows below carry one label for the repository as a whole; limits and proposals are listed per row. Contract labels remain `0.1.0-draft` wherever a page says so.

## Groups

The hub keeps its five responsibility groups and adds two named side groups. The side groups do not change the five-group map.

| Group | Members |
|---|---|
| 01 Knowledge & Provenance | Evidence Registry (The Index), Evidence Attestation (BitRep) |
| 02 Institutional Governance | Institutional Governance (Alvorada) |
| 03 Declaration & Policy Control | Action Manifest, Control Plane |
| 04 Constrained Execution | Execution Runtime |
| 05 Replay & Evidence | Replay Bundle, Governance Evidence Pack, ODES |
| Cross-cutting exchange | Governed Exchange (GAX/IMX) |
| Optional reasoning protocols (side group) | PRP, Research Intelligence Protocol, TFA Protocol |
| Tooling and qualification (side group) | Ergonomics (cognous-ocs), Verifier, Orchestrator, Qualification |

## 01 Knowledge & Provenance

| Component | Repository | Purpose | Label | Known limits and notes |
|---|---|---|---|---|
| [Evidence Registry (The Index)](https://github.com/cogno-us/cognous-evidence-registry) | `cognous-evidence-registry` | Protocol and reference implementation for registering claims, linking evidence commitments and preserving revision and lifecycle history. | selected | Chain inclusion does not establish execution authority or truth. |
| [Evidence Attestation (BitRep)](https://github.com/cogno-us/cognous-evidence-attestation) | `cognous-evidence-attestation` | Binary-attestation protocol and reference verifier; the selected interface checks issuer signatures against an operator-configured trust snapshot. | selected | A valid signature is `issuer_signature_only`, not factual truth or institutional authority. |

## 02 Institutional Governance

| Component | Repository | Purpose | Label | Known limits and notes |
|---|---|---|---|---|
| [Institutional Governance (Alvorada)](https://github.com/cogno-us/cognous-institutional-governance) | `cognous-institutional-governance` | Open research framework for institutional governance, with proposed constitutional designs and the Authority Context 0.1.0 implementation profile. | selected | Repository acceptance does not ratify a constitution; proposed authority is distinct from operative authority. |

## 03 Declaration & Policy Control

| Component | Repository | Purpose | Label | Known limits and notes |
|---|---|---|---|---|
| [Action Manifest](https://github.com/cogno-us/cognous-action-manifest) | `cognous-action-manifest` | Format, Python validator and CLI (`aam`) for declaring the actions an agent may propose; Manifest 1.1 adds deterministic runtime bindings. | selected | A declaration is not permission to execute. |
| [Control Plane](https://github.com/cogno-us/cognous-control-plane) | `cognous-control-plane` | Reference implementation of bounded authorization, effect-time revalidation and persistent runtime records; CLI `acp`. | selected | Authorization passing does not by itself establish a completed destination effect. |

## 04 Constrained Execution

| Component | Repository | Purpose | Label | Known limits and notes |
|---|---|---|---|---|
| [Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) | `cognous-execution-runtime` | Bounded synthetic destination and adapter boundary (Python execution layer under `engine/`), with an optional OpenShell adapter. | selected | Live OS or network confinement is a known limit: mocked or Docker-only qualification does not establish it. |

## 05 Replay & Evidence

| Component | Repository | Purpose | Label | Known limits and notes |
|---|---|---|---|---|
| [Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) | `cognous-replay-bundle` | Portable reconstruction format, importer, validator and CLI (`arb`); Reconstruction Bundle 0.2.0. | selected | Reconstruction does not re-evaluate policy or provide independent verification. |
| [Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | `cognous-governance-evidence-pack` | Format, validator, traceable importer and Markdown renderer for review packaging; CLI `agep`. | selected | Packaging is not independent assurance or compliance certification. |
| [ODES](https://github.com/cogno-us/open-decision-evidence-standard) | `open-decision-evidence-standard` | Open discussion draft and reference tooling for portable decision evidence; CLI `odes`; record schema `pder-v0.1`. | selected | Package validity does not establish present authority or authentication. The specification is a draft. |

## Cross-cutting exchange

| Component | Repository | Purpose | Label | Known limits and notes |
|---|---|---|---|---|
| [Governed Exchange (GAX/IMX)](https://github.com/cogno-us/cognous-governed-exchange) | `cognous-governed-exchange` | Experimental GAX/IMX reference for governed messages, recipient assessment, local durable transport and retained artifacts. | selected | Experimental. Exchange acceptance does not grant authority or renew execution permission. |

## Optional reasoning protocols (side group)

These three repositories are in the lock with `optional: true`. They are not part of the refund workflow and do not change selected interfaces.

| Component | Repository | Purpose | Label | Known limits and notes |
|---|---|---|---|---|
| [Portable Reasoning Protocol (PRP)](https://github.com/cogno-us/portable-reasoning-protocol) | `portable-reasoning-protocol` | Reusable reasoning protocol packaged as a `SKILL.md` skill. | merged | Optional; no runtime authority. |
| [Research Intelligence Protocol](https://github.com/cogno-us/research-intelligence-protocol) | `research-intelligence-protocol` | Research workflow packaging a discovery protocol and a cross-domain abstraction protocol. | merged | Optional; no runtime authority. |
| [TFA Protocol (S43)](https://github.com/cogno-us/truth-freedom-agency-protocol) | `truth-freedom-agency-protocol` | Optional behavioral protocol (Truth, Freedom, Agency) with evaluation guidance. | merged | Optional; a behavioral protocol, not an authority system. |

## Tooling and qualification (side group)

These repositories sit beside the lock. They are not lock entries and do not select component revisions.

| Component | Repository | Purpose | Label | Known limits and notes |
|---|---|---|---|---|
| [Ergonomics (`cognous-ocs`)](https://github.com/cogno-us/cognous-open-control-stack-ergonomics) | `cognous-open-control-stack-ergonomics` | Front-door CLI: offline demo, evidence render, validation, checks and CI entry; relays component verdicts and decides nothing. | merged | Contract `0.1.0-draft`. Its control-plane pin is ahead of the hub lock (see its docs). Publication is not authorized. |
| [Verifier](https://github.com/cogno-us/cognous-open-control-stack-verifier) | `cognous-open-control-stack-verifier` | Independent verifier for run records: own parser and canonical form, standard library only; a verification report, not an attestation. | merged | Pre-release and on hold; detection rates are measured by the qualification repository. |
| [Orchestrator](https://github.com/cogno-us/cognous-stack-orchestrator) | `cognous-stack-orchestrator` | Engineering integration and evidence coordination in bounded synthetic qualification tests. | merged | Not an authority issuer or release selector. Operational deployment assurance is not established (issue #30, HOLD). |
| [Qualification](https://github.com/cogno-us/cognous-stack-qualification) | `cognous-stack-qualification` | Cross-component scenarios, relocated executable suites and qualification records. | merged | Does not select revisions or authorize production; scenario specifications are recorded with their run state. |

## Hub

| Component | Repository | Purpose | Label |
|---|---|---|---|
| [Open Control Stack hub](https://github.com/cogno-us/cognous-open-control-stack) | `cognous-open-control-stack` | Canonical architecture, the component lock, selection profiles, reference profiles and tools, and evidence links. | merged |

The hub is the authority for selected revisions. Operational trust remains HOLD (see [operational trust status](operational-trust-status.md)).

## Selected revisions

<!-- lock-table:start -->
<!-- Generated from component-lock.json. Refresh at the pin round: regenerate this table from the lock and update the line below. -->

Last checked against `component-lock.json` at hub commit `dcc9bd7533ef`.

| Lock key | Repository | Pinned revision | Lock status | Interfaces recorded in the lock |
|---|---|---|---|---|
| `action_manifest` | [cogno-us/cognous-action-manifest](https://github.com/cogno-us/cognous-action-manifest) | `46c950bed37fe3812000895430bc0312d29e37ce` | selected | Manifest 1.1 |
| `control_plane` | [cogno-us/cognous-control-plane](https://github.com/cogno-us/cognous-control-plane) | `d3dadee70bd319812b207389ab1e0f6efe511916` | selected | bounded authorization/effect 0.1 |
| `constitutional_authority` | [cogno-us/cognous-institutional-governance](https://github.com/cogno-us/cognous-institutional-governance) | `fb3d97938969a89e149e8ff8db2756091d1233fc` | selected | Authority Context 0.1.0 |
| `gax_imx_transport` | [cogno-us/cognous-governed-exchange](https://github.com/cogno-us/cognous-governed-exchange) | `a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf` | selected | GAX retained artifacts 1.1.0; merged-producers-v1 opt-in compatibility |
| `moltbot_safe` | [cogno-us/cognous-execution-runtime](https://github.com/cogno-us/cognous-execution-runtime) | `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` | selected | Execution Envelope 0.2.0; executor producer profile 2.0.0; OpenShell adapter 0.1.0 |
| `replay_bundle` | [cogno-us/cognous-replay-bundle](https://github.com/cogno-us/cognous-replay-bundle) | `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa` | selected | Reconstruction Bundle 0.2.0 |
| `governance_evidence_pack` | [cogno-us/cognous-governance-evidence-pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | `b4baccd823d2a73be276c1de745b19cf7c56a0d6` | selected | imported Evidence Pack schema 0.2.0; manifest/reconstruction transformation 0.3.2 (merged producer pair); historical transformations retained |
| `odes` | [cogno-us/open-decision-evidence-standard](https://github.com/cogno-us/open-decision-evidence-standard) | `c5e9a0f3695ae836b803be06c46d2c669642ee03` | selected | ODES implementation profile 0.2.1 (merged producer pair); pder-v0.1 |
| `bitrep` | [cogno-us/cognous-evidence-attestation](https://github.com/cogno-us/cognous-evidence-attestation) | `5b5077dafde232a7801cb425c4efddcffb468723` | selected | verification contract v1 |
| `the_index` | [cogno-us/cognous-evidence-registry](https://github.com/cogno-us/cognous-evidence-registry) | `d5e45d275cb301d9684b543e93b05997991d1cf2` | selected | local blockchain reference 0.1.0 |
| `prp` | [cogno-us/portable-reasoning-protocol](https://github.com/cogno-us/portable-reasoning-protocol) | `cb137f028e92448a56e785e3d4ea074b444fa225` | optional | none recorded in the lock |
| `research_intelligence` | [cogno-us/research-intelligence-protocol](https://github.com/cogno-us/research-intelligence-protocol) | `30c7274b49c07a0df4c8ca7b281f2e3f8ae68dee` | optional | none recorded in the lock |
| `tfa` | [cogno-us/truth-freedom-agency-protocol](https://github.com/cogno-us/truth-freedom-agency-protocol) | `442d07b4891870abb1756fcb11c24ccf187706f4` | optional | none recorded in the lock |

<!-- lock-table:end -->

The lock also records previous acceptances and historical test dependencies; those are evidence of earlier checkpoints and are not selected. A newer commit in a component repository is not selected until the lock changes. Component sections above describe what each repository is for, not its latest revision.

## Where to go next

- [Documentation index](README.md) for every hub page by role.
- [Naming](naming.md) for display names, repository names, packages, CLIs and former names.
- [Profiles and tools](profiles-and-tools.md) for commands, profiles and tools per repository.
- [Repository locations after the rename](repository-renames.md).
- [Architecture](architecture.md) for trust boundaries and identity namespaces.
