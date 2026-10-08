# Bounded V1 candidate release record — Governor C decision pending

**Disposition:** exact merged C1–C8 qualification PASSED for the scoped synthetic local SQLite refund path; **NOT RELEASED**, lock proposal not accepted on hub main.

## Final accepted candidate revisions

| Component | Exact merge |
|---|---|
| Action Manifest | `8d1572d4f926c968a8704cb912a6e9d49166f74a` |
| Control Plane | `e66e5f163c5d5c112ff345a2f332b4c3893ee183` |
| Execution Runtime | `da9f52900ee2596dab087ec6c249ba84915d2b13` |
| Replay Bundle | `2069a0ba1398812c3a8669331a7d8b87c80c4a48` |
| Governance Evidence Pack | `87293cfcbe8dfa2368d5bf77019945ba8ef1ae71` |

## Current-head qualification evidence

- Hub final merged qualification PR #61, head `0598168ca96f2290a092f70bb34d18c63177dc9a`.
- [W7 merged five-repository CI 37852016588](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37852016588): **SUCCESS**, exactly verified accepted source/consumer revisions.
- Synthetic SQLite source execution: Runtime tests **42 passed**, Replay tests **18 passed**, Evidence tests **11 passed**, with **zero failures, errors or skips**.
- Source-derived bounded C8 authority export → Replay → Evidence: **PASS**, including tenant and grant/approval/policy linkage, approval-row proposal commitment, negative tenant/stale revision/commitment mutations.
- Local controller-authored C7 stop journal → Replay → Evidence: **PASS**, including observed stop request, acknowledgement, local dispatch closure, quiescence, destination reconciliation and negative duplicate/cross-effect/sequence/omitted-event mutations. Missing event yields partial, not invented completeness.
- Actual durable refusal and lost-ACK source records → Replay → Evidence: **PASS**, including exact attempt/effect correlation and non-retry observation.
- Retained GitHub Actions artifact: `w7-final-merged-c8-evidence`, containing source `authority.json`, `stop.json`, `reconstruction.json`, `projection.json`, refusal/lost-ACK `producer-cases.json`, and 3 JUnit files.

## Supported release claim

A bounded, synthetic, trusted-host, local SQLite refund implementation demonstrates exact tenant-aware authority enforcement and revalidation, durable typed failure records, immutable effect/attempt correlations, no-blind-retry handling, local controller-observed stop boundaries, and non-authorizing evidence reconstruction for these specifically exported source records. Historical artifact generations remain separately attributable.

## Explicit limits

- Stop instrumentation is **local controller authored**; not generalized stop-path coverage, fleet-wide cancellation or remote quiescence.
- Authority export contains trusted local SQLite rows and retained approval **proposal commitment**, not the full original proposal payload nor independent proposal verification.
- Replay and Evidence are derived reconstructions; no independent destination effect verification or authority acquisition.
- Local commit, lost acknowledgement and reconciliation do not establish universal exactly-once external effects, compensation or general rollback.
- OpenAPPA W4 and Microsoft AGT W5 are optional independent integrations, not core prerequisites or authority grants.
- OpenShell W6 **DEFERRED / NOT LIVE QUALIFIED**; no live confinement, egress or credential isolation claim.
- No broad enterprise IAM completeness or model-level prompt-injection resistance.

## Governor acceptance requirements

This PR proposes a separate scoped `component-lock.json` profile only after passing the exact source combination. It does **not** self-authorize release. Governor C must inspect final PR-head CI and exact lock diff, accept/merge the candidate only if compatible gates pass, then issue an explicit release acceptance decision. Historical release workflows that validate old `merged-producers-v1` must not be substituted for new lock qualification.

Release authorization: **PENDING**.
