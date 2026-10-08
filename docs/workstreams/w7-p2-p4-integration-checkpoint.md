# W7-P2/P3/P4 bounded release integration checkpoint

Date: 2026-10-08. Source: Governor C directive in hub issue #53.

## Accepted producer revisions (not yet selected in component-lock)

| Component | Accepted SHA | Scope |
|---|---|---|
| Action Manifest | `8d1572d4f926c968a8704cb912a6e9d49166f74a` | `runtime-action-proposal/1.2`, required exact tenant |
| Control Plane | `e66e5f163c5d5c112ff345a2f332b4c3893ee183` | `bounded-authorization-effect/0.2`; W5 optional commit is separate |
| Execution Runtime | `bd398f16c4cee329d2d0213afc3236ca9232d29e` | W1 tenant-bound SQLite refund, W2 typed `failure_records_v1` and local stop/restart |

Hub W0: `6ad8f6a409d3140aa65af19d5c850dd8e58f8a7d`.
Current accepted hub main at P2 start: `777593cdfa42bd78689490b5e1dd45d060ca1859`.
W7-P1 accepted: `6a055aa4dd31476273e01f60a1ed076eb28c9fd6`.
Current core lock blob SHA: `b3bf15918ec7eaccd10c486b61926351d392dd04`; `runtime_profile=merged-producers-v1`. Preserve until fully qualified.

## Existing test reuse and material new boundaries

Continue to use `scenarios/acceptance-matrix.json`, `full-candidate-release.yml`, `reference-release.yml`, the Control Plane and local SQLite Runtime tenant/refusal/stop suites. Historical candidate success at historical lock pins is **not** proof for the accepted W1/W2 revision combination.

- C1/C2: valid tenant-bound refund and missing/substituted tenant, wrong-tenant grant/approval/policy, current revocation/expiry/actor/conflict, payload/adapter substitution.
- C4: durable typed `failure_records_v1` after actual pre-dispatch refusals and evaluation errors; absence of attempt on pre-dispatch denial is intentional.
- C5/C7: local stop request, worker acknowledgement, dispatch closure, bounded destination observation, reconciliation; accepted precommit rollback and postcommit retained effect; lost ACK never grants retry.
- C8: **BLOCKED** until W3 supplies accepted Replay importer and Evidence transformation for the actual W1/W2 producer bytes; missing/incomplete/unknown lineage cannot be silently promoted to verified.

## P3 composed test gate

At final proposed exact pins, run the finite positive/negative synthetic SQLite refund matrix and require collected tests to pass with no required skips. Require independent destination reads, source-specific refusal/stop records, unchanged effect IDs, and exact Replay/Evidence compatibility. The existing `full-candidate-release.yml` is historical until its profile is changed *after* qualifying the proposed combination. Do not equate a passing historical suite with P3 completion.

## P4 release evidence gate

Publish: final component SHA ledger, lock digest, environment and installation steps, exact test commands and workflow URLs, matrix case statuses (PASS/FAIL/BLOCKED/SKIP/NOT_APPLICABLE), stored destination evidence and derived consumer artifacts; declare known limits. Only advance the lock after qualification of that exact proposed combination. Until then, `release_qualified=false`.

W4 OpenAPPA optional accepted at hub `777593cdfa42bd78689490b5e1dd45d060ca1859`. W5 Microsoft AGT optional accepted in Control Plane `99bb62fff879a8d4e87d7badb0d7d8a17501e4c1`. Neither is a mandatory core dependency. W6 OpenShell live qualification **DEFERRED / NOT QUALIFIED**, no confinement claim.

Excluded: universal exactly-once, general rollback, fleet-wide stop, enterprise IAM completeness, LLM prompt-injection resistance and live OpenShell confinement.

## Coordination

W7 requested W3 actual merge SHAs, producer/consumer schema generations, fixture byte digests and import/validate/render commands in issue #49. P3/P4 remain gated until accepted W3 consumer implementation and exact combination qualification; no speculative claims or pin promotion.
