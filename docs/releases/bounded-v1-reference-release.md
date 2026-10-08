# Cognous bounded V1 — selected reference release (Governor acceptance pending)

**Release class:** qualified reference implementation; trusted-host synthetic local SQLite refund only. **Not production deployment approval.**

Founder and Governor C approved the *scope in principle* in issues [#53](https://github.com/cogno-us/cognous-open-control-stack/issues/53) and [#54](https://github.com/cogno-us/cognous-open-control-stack/issues/54). This PR proposes explicit publication and selection, pending current-head regression evidence and Governor final acceptance. Do not interpret a pull request, successful CI or this document as Governor's final merge decision.

The machine-readable selection is `profiles/bounded-v1-reference-release-selection.json`. It references the immutable accepted candidate `profiles/w7-bounded-v1-component-lock.candidate.json` at hub merge `f7d03c719b9be3b9c3fe0fe300df642b0f408d98` and Git blob `096b2ac91ac799a875b696beb92b70b5bf11fdca`. The selected historical `component-lock.json`, blob `b3bf15918ec7eaccd10c486b61926351d392dd04`, remains untouched.

## Exact bounded core

| Component | Accepted revision |
|---|---|
| Manifest | `8d1572d4f926c968a8704cb912a6e9d49166f74a` |
| Control Plane | `e66e5f163c5d5c112ff345a2f332b4c3893ee183` |
| Execution Runtime | `da9f52900ee2596dab087ec6c249ba84915d2b13` |
| Replay Bundle | `2069a0ba1398812c3a8669331a7d8b87c80c4a48` |
| Governance Evidence Pack | `87293cfcbe8dfa2368d5bf77019945ba8ef1ae71` |

## Accepted objective evidence

- Hub #61 merged `76075158713f77ef9fbfe59de8538bfad30d5697`, exact merged C1–C8 run [37852016588](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37852016588): 42 Runtime, 18 Replay, 11 Evidence tests, zero fail/error/skip.
- Hub #62 merged `f7d03c719b9be3b9c3fe0fe300df642b0f408d98`: nine historical and candidate gates green, including authority-inclusive matrix [37854430854](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37854430854).
- Current selection PR must rerun actual source-to-Replay-to-Evidence and appropriate legacy qualification at its exact head. Retain `w7-final-merged-c8-evidence` and regression artifacts, record run links in #53.

Supported claim: a bounded source-derived SQLite tenant/grant/approval/policy lineage and retained approval-row proposal commitment, typed refusal/lost-ACK evidence, exact effect/attempt correlation, non-authorizing Replay/Evidence reconstruction, and **controller-observed local** stop request, acknowledgment, dispatch closure, quiescence and destination reconciliation for the tested synthetic workflow.

## Exclusions / not supported

No general production deployment or production hardening, generalized all-path stop, fleet-wide cancellation, remote quiescence, independently verified original proposal payload, independently verified destination effect, generalized rollback, universal exactly-once, enterprise IAM completeness, general model prompt-injection resistance or live OpenShell confinement. W4 OpenAPPA and W5 Microsoft AGT remain separate optional profiles; W6 OpenShell is **DEFERRED / NOT LIVE QUALIFIED**. Historical artifact profiles remain separately attributable, backward-decodable and are not elevated to C8 by inference.

**Release status before Governor final acceptance: NOT PUBLISHED.** The record authorizes only a narrowly qualified reference profile when explicit final CI and Governor acceptance are recorded; never production deployment.
