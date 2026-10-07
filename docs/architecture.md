# Architecture and responsibility map

The supported synthetic workflow is local durable delivery → GAX assessment →
Manifest-bound proposal → Control Plane decision and effect-time revalidation →
Moltbot Safe SQLite destination → retained Replay/ODES/IMX artifacts and Evidence
Pack. The Authority Context comes from a separately configured trusted resolver.
[Selected contracts](compatibility.md) and [support status](release-status.md)
define the boundaries of this reference.

## Component responsibilities

Repository links identify owners; their current default branches are not a
substitute for the hub's exact [dependency lock](../component-lock.json).

| Component / owner | Responsibility | Does not establish |
|---|---|---|
| [Cognous Institutional Governance](https://github.com/cogno-us/cognous-institutional-governance) | Institutional constitution, source hierarchy and Authority Context 0.1.0 implementation profile | Institutional adoption, authenticated deployment or a grant created by an incoming request |
| [Cognous Action Manifest](https://github.com/cogno-us/cognous-action-manifest) | Declares intended action surface and binds the proposed operation | Permission to execute |
| [Cognous Control Plane](https://github.com/cogno-us/cognous-control-plane) | Evaluates the proposal against resolved authority and revalidates decision-critical inputs at effect time; retains decisions/attempts/reconciliation | A completed destination effect merely because authorization passed |
| [Cognous Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) | Constrained executor, exact operation binding and bounded synthetic SQLite destination; optional OpenShell adapter | Live OS/network confinement from mocked or Docker-only qualification |
| [Cognous Governed Exchange](https://github.com/cogno-us/cognous-governed-exchange) | Governed exchange, recipient assessment, retained artifacts and continuity/recovery | Constitutional authority or renewed execution permission from exchange acceptance |
| [LocalDurableTransport and recipient adapter](https://github.com/cogno-us/cognous-governed-exchange/tree/c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df) | Local durable message delivery/redelivery and association with recipient outcome | Authorization, effect completion or exactly-once delivery from receipt |
| [Cognous Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) | Non-effecting reconstruction from retained producer records, preserving identities and provenance | Policy reevaluation, renewed authority or independent verification |
| [Cognous Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | Traceable review/audit packaging of Manifest and reconstructed records | Independent assurance or compliance certification |
| [ODES](https://github.com/cogno-us/open-decision-evidence-standard) | Portable decision-evidence representation, package integrity and recipient validation | Present authority or authentication merely from package validity |
| [Cognous Evidence Attestation](https://github.com/cogno-us/cognous-evidence-attestation), optional evidence path | Issuer-signature verification under an explicitly trusted snapshot | Execution authority from a valid signature |
| [Cognous Evidence Registry](https://github.com/cogno-us/cognous-evidence-registry), optional evidence path | Local-chain claims, commitments and lifecycle evidence | Execution authority or truth from chain inclusion |
| [PRP](https://github.com/cogno-us/portable-reasoning-protocol), [TFA](https://github.com/cogno-us/truth-freedom-agency-protocol), [Research Intelligence](https://github.com/cogno-us/research-intelligence-protocol), optional | Reasoning/research instructions and compatible artifacts | Runtime enforcement, authority or measured behavioral efficacy from static checks |

The **Cognous Institutional Governance** and **Cognous Governed Exchange**
repositories have different responsibilities. The former supplies institutional
governance research and the Authority Context profile; the latter implements
the experimental GAX/IMX workbench. Transport is a delivery mechanism within that
workbench, distinct from GAX exchange semantics. Cognous Evidence Attestation and
Cognous Evidence Registry form a separate evidence path, not authority dependencies
of the representative refund. The [rename map](repository-renames.md) explains
which package and retained evidence identifiers intentionally keep their old names.

## Identity and trust boundaries

`message_id` identifies a delivery object; `proposal_commitment` binds the operation;
`decision_id` identifies a Control Plane decision; `effect_id` identifies the
intended destination effect across delivery/recovery. Control Plane and executor
`attempt_id` namespaces remain distinct. `bundle_id` identifies reconstruction;
Evidence Pack and ODES IDs identify derived artifacts and do not mint an effect.

Authorization, acknowledgement, accepted destination observation and independent
verification are different facts. See [recovery semantics](recovery-semantics.md)
for their treatment after uncertainty or changed authority.
