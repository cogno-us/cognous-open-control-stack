# W7 final merged C1–C8 qualification — pre-acceptance record

Status: **CI REQUIRED / NOT RELEASED**. This checkpoint establishes exact merged component inputs for bounded local synthetic SQLite refund; it is not a final accepted lock.

| Component | SHA |
|---|---|
| Manifest | `8d1572d4f926c968a8704cb912a6e9d49166f74a` |
| Control Plane | `e66e5f163c5d5c112ff345a2f332b4c3893ee183` |
| Runtime | `da9f52900ee2596dab087ec6c249ba84915d2b13` |
| Replay | `2069a0ba1398812c3a8669331a7d8b87c80c4a48` |
| Evidence | `87293cfcbe8dfa2368d5bf77019945ba8ef1ae71` |

The W7 CI calls the *accepted* Evidence source capture scripts against the exact Runtime, Control Plane, Replay and Evidence commits, retaining source SQLite-row authority exports, controller-authored local stop journal, Replay reconstruction and Evidence projection. Positive and mutation negative cases cover tenant mismatch, approval proposal-commitment absence, stale grant/policy, reordered/omitted/cross-effect stop events and expected partial rather than inferred complete reconstruction. Separate W2 actual source refusal/lost-ack tests and W1/W2 source suites preserve effect/attempt identities and no unauthorized retry.

**Scope:** controller-observed local stop only. No generalized stop-path instrumentation or fleet stop. Proposal evidence is its retained approval-row proposal commitment; no full original payload or independent proposal verification. Replay/Evidence are derived and non-authorizing. W4/W5 optional; W6 OpenShell live deferred, not qualified. Universal exactly-once, rollback, generalized IAM and prompt-injection resistance excluded.

Lock `component-lock.json` remains untouched pending green exact-head qualification and Governor approval; no deployment release authorized here. Historical profiles remain decodable and must not be silently upgraded.
