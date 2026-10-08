# W7 bounded V1 release record — unqualified draft

Status: **NOT RELEASED; NO LOCK UPDATE AUTHORIZED**.

## Exact candidate source revisions

- Hub base: `d556aad559560e8d7b51e5ea2276068ab7097b8e`
- Action Manifest: `8d1572d4f926c968a8704cb912a6e9d49166f74a`
- Control Plane W1: `e66e5f163c5d5c112ff345a2f332b4c3893ee183`
- Execution Runtime W1+W2: `bd398f16c4cee329d2d0213afc3236ca9232d29e`
- Replay supplementary W2 importer: `4299e1b16cb5b80a32930ef7659a216b6baabc45`; not complete combined W1/W2 C8 coverage
- Evidence Pack: **UNSELECTED**, W3 actual producer-export acceptance pending

## Qualification ledger

| Gate | Evidence | State |
|---|---|---|
| P2 accepted producer ledger | Hub #57 / `d556aad559560e8d7b51e5ea2276068ab7097b8e` | ACCEPTED |
| P3 independent producer candidate | Hub #58 and its current-head CI / retained JUnit | IN PROGRESS |
| Exact tenant and current authority path | Accepted W1 producer tests; composed release gate not yet recorded | PENDING FINAL QUALIFICATION |
| W2 refusal/stop/recovery | Runtime #33–35 accepted; W7 producer-only CI | PENDING FINAL QUALIFICATION |
| W3 Replay accepted W1/W2 producer-export import | W3 issue #49 | BLOCKED |
| W3 Evidence Pack exact producer compatibility | W3 issue #49 | BLOCKED |
| Final exact combination and negative matrix | No final component profile selected | NOT RUN |
| Component lock digest and final workflow provenance | Historical `merged-producers-v1` lock retained | NOT ADVANCED |

## Release packaging obligations before acceptance

1. Record accepted complete Replay and Evidence consumer revisions, exact format/generation identifiers and fixture SHA-256 bytes from actually executed W1/W2 source.
2. Qualify the exact proposed component combination with positive and negative SQLite refund, tenant mismatch, grant/approval/policy mismatch, refusal, stop, lost acknowledgement/restart, evidence loss, lineage substitution, incomplete observation and no-blind-retry cases.
3. Store JUnit, workflow run URLs, environment, fixture hashes, source revision evidence, expected/actual destination records and per-case PASS/FAIL/BLOCKED/SKIP/NOT_APPLICABLE.
4. On success only, advance `component-lock.json`, record its new exact digest and repeat all applicable gates against the final locked combination.
5. Only then replace this draft with a bounded V1 release-qualified record.

Optional OpenAPPA W4 and Microsoft AGT W5 are independently accepted adapters and do not grant execution authority or block core. OpenShell W6 **DEFERRED / NOT LIVE QUALIFIED** and excluded from the core.

Excluded claims: universal exactly-once effects, rollback/compensation, fleet stop, enterprise IAM, general LLM prompt-injection resistance and live confinement.

Atomic-authority and refund-intent remain separate profiles, not a composite guarantee. Derived Replay/Evidence summaries never establish permission or independent destination truth.

## Exact W7 five-repository integration result (2026-10-08)

W7 final candidate PR #60 head `921c1dcbabacbd92a17cae4d76494f59a77cf72b`, [workflow 37842638176](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37842638176): **PASS**.

- Accepted Manifest: `8d1572d4f926c968a8704cb912a6e9d49166f74a`.
- Accepted Control Plane: `e66e5f163c5d5c112ff345a2f332b4c3893ee183`.
- Accepted Runtime: `bd398f16c4cee329d2d0213afc3236ca9232d29e`.
- Accepted Replay: `4299e1b16cb5b80a32930ef7659a216b6baabc45`.
- Accepted Evidence: `9c0098d216b788d29af46508b738eef884e5a68a`.

Results: actual accepted producer `refusal,lost_ack` records → Replay → Evidence projection PASS; source 42 passed; Replay 15 passed; Evidence 9 passed. Workflow retains output `w7-final-scoped-cross-repo-evidence` with original producer JSON and JUnit case outputs.

**Disposition:** C4 refusal and lost-ack supplementary projection covered by actual producer. Independent full C1/C2 tenant grant/approval/policy lineage and C7 stop request/ack/quiescence/reconciliation lifecycle are NOT reconstructed end to end. Thus this is **not full C1–C8 release qualification** and does not authorize lock advancement. The needed narrow W3 + producer/export follow-up is recorded in #49. W4/W5 optional; W6 not live qualified.
