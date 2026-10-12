# W7 final integration gate — exact accepted W1/W2/W3 candidate

**Release disposition: BLOCKED for complete frozen C1–C8 assurance until missing C8 lineage coverage is resolved.** This record is an executable qualification checkpoint, not a release declaration.

Accepted source combination:

| Role | Revision |
|---|---|
| W1 Manifest | `8d1572d4f926c968a8704cb912a6e9d49166f74a` |
| W1 Control Plane | `e66e5f163c5d5c112ff345a2f332b4c3893ee183` |
| W1+W2 Runtime | `bd398f16c4cee329d2d0213afc3236ca9232d29e` |
| W3 Replay | `4299e1b16cb5b80a32930ef7659a216b6baabc45` |
| W3 Evidence | `9c0098d216b788d29af46508b738eef884e5a68a` |

Independent accepted producer qualification: Hub #58 / run 37841300861, 42 passed with zero failures/errors/skips, covering local SQLite authority, refusal, stop and recovery.

This PR adds a cross-repository workflow reusing W3's **actual accepted producer export** script and real Replay/Evidence importer/tests at exact pinned revisions. The workflow retains actual source outputs and JUnit. Tests may demonstrate only the cases they execute.

## Required claim coverage and boundaries

| Claim | Producer | Replay → Evidence | Final disposition pending run |
|---|---|---|---|
| Tenant exact equality across action/grant/approval/policy | Accepted W1 producer test | No complete tenant-bearing cross-layer exporter/import qualified by W3 | PARTIAL |
| C4 refusal durable and typed | Accepted W2 source tests | W3 supplementary `agep-w3-atomic-failure-trace/0.1.0` | QUALIFIED COMPONENT SCOPE, pending W7 exact run |
| Lost ACK and effect/attempt identity | Accepted W2 source tests | W3 supplementary W2 failure trace; unsupported claims remain explicit | QUALIFIED COMPONENT SCOPE, pending W7 exact run |
| C7 stop request/ack/closure/quiescence/reconciliation | Accepted W2 local process tests | No unified durable sequence exported/reconstructed | PARTIAL |
| Reconciliation/no blind retry | Accepted W2 source tests | W3 W2 source-projection trace only | PARTIAL |
| Historical consumer compatibility | Earlier exact historical pin tests | W3 historical suite validated separately | DO NOT UPGRADE |

### C8 assessment

W0 C8 freezes explicit loss/unknown semantics, truthful reconstruction and no assurance upgrade. The bounded V1 release mission specifically requires evidence lineage for tenant authority and stop intervention. Accordingly, complete consumer lineage for C1/C2/C7 cannot currently be asserted from W3's accepted supplementary refusal/lost-ACK support. The release has two defensible possibilities: (a) hold the full planned C1–C8 release until W3 publishes source-derived tenant and C7 stop lineage, or (b) explicitly reduce release claims to producer-bound tenant/stop plus supplementary W2 refusal/lost-ACK consumer reporting, and obtain Governor acceptance of the reduced scope. This checkpoint does **not** authorize (b) by implication.

**Smallest corrective workstream:** W3 paired with the Runtime/Control Plane owners: export source-authentic (within the bounded trusted-host profile) tenant binding and C7 local stop lifecycle events with stable correlation identities and supported missing/unknown states, then add exact Replay → Evidence consumer tests for positive and mismatched/absent evidence. Do not infer stop acknowledgement from process termination alone outside the defined local test or infer tenant lineage from a textual label.

No `component-lock.json` mutation, release declaration, live OpenShell confinement or general effect-finality proof is authorized by this PR. W6 deferred/unqualified; W4/W5 optional.
