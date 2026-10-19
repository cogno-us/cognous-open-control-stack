# Naming

The stack uses several names for the same repository: a display name, a repository name, a package name, an import module, a command and, for some, a former name. This page collects them in one place. Retained identifiers are not renamed: a name that looks old can be a versioned wire identifier that retained records depend on.

See the [stack map](stack-map.md) for what each repository is for and [profiles and tools](profiles-and-tools.md) for its commands.

## Names by repository

| Display name | Repository (under `cogno-us/`) | Package (distribution) | Import module | Command | Former names |
|---|---|---|---|---|---|
| Action Manifest | `cognous-action-manifest` | `agent-action-manifest` | `agent_action_manifest` | `aam` | `cognous-agent-action-manifest` |
| Control Plane | `cognous-control-plane` | `agent-control-plane` | `agent_control_plane` | `acp` | `cognous-agent-control-plane` |
| Institutional Governance (Alvorada) | `cognous-institutional-governance` | not packaged | not applicable | none | `constitutional-governance-for-institutions` |
| Governed Exchange (GAX/IMX) | `cognous-governed-exchange` | `alvorada-gax-imx-reference` | `experiments` package (see the repository) | none | `alvorada` |
| Execution Runtime | `cognous-execution-runtime` | not packaged | `engine` | `cli/moltbot_safe_cli.py` | `moltbot-safe` (Moltbot Safe); lock key `moltbot_safe` |
| Replay Bundle | `cognous-replay-bundle` | `agent-replay-bundle` | `agent_replay_bundle` | `arb` | `cognous-agent-replay-bundle` |
| Governance Evidence Pack | `cognous-governance-evidence-pack` | `agent-governance-evidence-pack` | `agent_governance_evidence_pack` | `agep` | `cognous-agent-governance-evidence-pack` |
| ODES | `open-decision-evidence-standard` | `open-decision-evidence-standard` | `odes` | `odes` | none recorded |
| Evidence Attestation (BitRep) | `cognous-evidence-attestation` | not packaged | not applicable | none | `bitrep`; lock key `bitrep` |
| Evidence Registry (The Index) | `cognous-evidence-registry` | `the-index` | see the repository | none | `the-index`; lock key `the_index` |
| Portable Reasoning Protocol (PRP) | `portable-reasoning-protocol` | not packaged | not applicable | none | none recorded |
| Research Intelligence Protocol | `research-intelligence-protocol` | not packaged | not applicable | none | none recorded |
| TFA Protocol (S43) | `truth-freedom-agency-protocol` | not packaged | not applicable | none | none recorded |
| Ergonomics | `cognous-open-control-stack-ergonomics` | `cognous-ocs` | `cognous_ocs` | `cognous-ocs` | none recorded |
| Verifier | `cognous-open-control-stack-verifier` | `cognous-open-control-stack-verifier` | `cognous_verify` | `cognous-verify` | none recorded |
| Orchestrator | `cognous-stack-orchestrator` | not packaged | not applicable | none | none recorded |
| Qualification | `cognous-stack-qualification` | not packaged | not applicable | none | none recorded |
| Hub | `cognous-open-control-stack` | not packaged | not applicable | none | none recorded |

"Not packaged" means the repository carries no installable package metadata at the time of writing. The ergonomics distribution `cognous-ocs` installs one command, `cognous-ocs`; there is no `ocs` script.

## Legacy lock keys

[`component-lock.json`](../component-lock.json) keys are identifiers that retained records and checks refer to. They keep their original spelling even where the repository was renamed.

| Lock key | Repository today | Note |
|---|---|---|
| `action_manifest` | `cognous-action-manifest` | |
| `control_plane` | `cognous-control-plane` | |
| `constitutional_authority` | `cognous-institutional-governance` | Shown as Institutional Governance (Alvorada). |
| `gax_imx_transport` | `cognous-governed-exchange` | The key names the transport; the entry covers the exchange repository. |
| `moltbot_safe` | `cognous-execution-runtime` | Legacy key from the former `moltbot-safe` repository. It is a retained identifier, not the current display name. The repository is now Execution Runtime. |
| `replay_bundle` | `cognous-replay-bundle` | |
| `governance_evidence_pack` | `cognous-governance-evidence-pack` | Also called Evidence Pack in prose. |
| `odes` | `open-decision-evidence-standard` | |
| `bitrep` | `cognous-evidence-attestation` | Shown as Evidence Attestation (BitRep). |
| `the_index` | `cognous-evidence-registry` | Shown as Evidence Registry (The Index). |
| `prp`, `research_intelligence`, `tfa` | the three optional protocol repositories | Entries carry `optional: true`. |

## Name pairs that are easy to confuse

- **Alvorada.** In current documentation, Alvorada is the display name of `cognous-institutional-governance`. The former `cogno-us/alvorada` repository is now `cognous-governed-exchange`, and the exchange package is still called `alvorada-gax-imx-reference`. These are two different repositories with different responsibilities.
- **Evidence Pack and Governance Evidence Pack.** The same repository. "Evidence Pack" is the short prose form.
- **Replay Bundle and paired replay.** Replay Bundle is the reconstruction format. In this repository, paired replay means the experimental comparison of an identical frozen request across enforcement conditions. It is not Replay Bundle reconstruction.
- **Execution Runtime and Moltbot Safe.** The same repository under its current and former name. Wire identifiers inside retained producer records keep the old spelling.
- **Hub and qualification.** The hub holds the lock and selection decisions. The qualification repository holds relocated suites and records and does not select revisions.

## Retained identifiers

Producer-profile `repository` and attempt `owner` strings, JSON Schema `$id` values, protocol, package and import names, signed or hashed exports, qualification result files and earlier licence notices keep their original identifiers and bytes. Adopting renamed wire identities would need a separately versioned compatibility change and qualification. See the [rename map](repository-renames.md) for repository location changes.

The rename map covers the October 2026 location changes. The ergonomics, verifier, orchestrator and qualification repositories are listed on the [stack map](stack-map.md) and in the table above; they were not part of that rename.

## Terms

| Term | Meaning here |
|---|---|
| Selected | A revision and interface pinned in the component lock, interpreted with release status. |
| Accepted component source | A reviewed merge in the owning repository; not necessarily selected by the hub. |
| Historical evidence | Counts, pins, examples or instructions from an earlier checkpoint. Valid for their original revision, not a later one. |
| Operationally qualified | Would need independently reviewed deployment, trust roots, key custody and environment evidence. Not established; see [operational trust status](operational-trust-status.md). |
| Authority Context | The institutional context supplied by a separately configured resolver, outside the incoming message. |
| `message_id`, `proposal_commitment`, `decision_id`, `effect_id`, `attempt_id`, `bundle_id` | Distinct identity namespaces. See [architecture](architecture.md#identity-and-trust-boundaries). |
| Status labels | merged, selected, known limit, proposed. Defined on the [stack map](stack-map.md#status-labels). |
| Contract label | Contract labels stay `0.1.0-draft` where a page says so. |

## Status label legend

The same four labels are used in every table that carries a status column:

- **merged**: merged in the owning repository; not by itself selected.
- **selected**: pinned in the hub component lock as a selected component.
- **known limit**: a limitation that existing documentation already states.
- **proposed**: draft or planned work that is not a supported interface.

Labels only describe what existing text already states. They do not add claims.
