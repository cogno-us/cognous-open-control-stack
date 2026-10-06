# Reference architecture

```text
Evidence source -> The Index ----> BitRep verification
                         \             /
                          \ evidence refs
                           v
GAX governed delivery -> recipient assessment -> Manifest-bound RuntimeProposal
                                                |
Alvorada constitutional Authority Context ------+--> Control Plane decision
                                                       |
                                                effect-time revalidation
                                                       |
                                                       v
                                              Moltbot Safe executor
                                                       |
                                              synthetic destination
                                                       |
                                                       v
                          Replay reconstruction -> Governance Evidence Pack
                                      \---------> optional ODES recipient validation
                                       \--------> IMX continuity/recovery
```

PRP, TFA and Research Intelligence are optional instruction/research layers. They can improve inputs or emit compatible structures but are not enforcement dependencies.

## Responsibility map

| Concern | Canonical owner |
|---|---|
| claims, evidence relationships, chain reference | The Index |
| signature / attestation verification | BitRep |
| constitutional and institutional authority | Alvorada constitutional repository |
| intended action declaration | Agent Action Manifest |
| pre-effect authorization and revalidation | Agent Control Plane |
| constrained effect boundary | Moltbot Safe |
| governed inter-agent exchange and continuity | Alvorada experimental GAX/IMX workbench |
| technical reconstruction | Agent Replay Bundle |
| review/audit package | Agent Governance Evidence Pack |
| portable decision evidence | ODES |
| reasoning/research behavior | PRP / TFA / Research Intelligence, optional |

## Trust boundaries

Knowledge is not signature verification. A valid signature is not institutional authority. A Manifest declaration is not a grant. Authorization is not execution. An acknowledgement is not destination observation. Replay is reconstruction, not independent verification. ODES carries decision evidence; GAX describes exchange semantics; transport concerns delivery.

## Identifier crosswalk

`message_id` identifies a GAX delivery object. `proposal_commitment` binds the proposed operation. `decision_id` identifies a Control Plane decision. `effect_id` identifies the intended durable side effect and survives retries. `attempt_id` identifies one delivery attempt. `bundle_id` identifies Replay reconstruction. Evidence Pack and ODES IDs identify derived review/interchange artifacts and never mint a new effect identity.

## Naming migration proposal — no renames in this PR

- **Alvorada Constitution**: use this label for `cogno-us/constitutional-governance-for-institutions`, the source of constitutional/institutional authority semantics.
- **Alvorada Exchange Workbench**: use this label for `cogno-us/alvorada`, the experimental GAX/IMX governed-exchange reference.
- **Moltbot Safe**: retain repository/package names for compatibility now; consider a future descriptive product-neutral name such as **Cognous Constrained Executor** only through a separately approved migration with redirects, package aliases and deprecation period.

Repository, package and import names remain unchanged.
