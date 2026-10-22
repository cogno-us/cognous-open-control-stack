# Workstream and component ownership

| Workstream | Existing scope | Proposed step mapping |
|---|---|---|
| WS-A | Orchestrator/Qualification separation and evidence handoff | 1.2,1.4,3.1–3.6 |
| WS-B | Rules, evaluator registry and activation | 1.3,2.1–2.5 |
| WS-C | Pin overlay and compatibility | 4.1 |
| WS-D | D/R/M known-issue disposition | 1.1,4.3 |
| WS-E | Reporting truth and scope reduction | 4.5 |
| WS-F | Qualification hygiene and probes | 1.7,4.3–4.5 |
| WS-G | Reserved release choice | 4.6, deferred |
| WS-H | Comparative architecture | 1.6,4.2, deferred extensions |

Local components own their implementations and developer tests; Orchestrator owns bounded cross-component coordination and engineering integration; Qualification owns independent frozen expectations and verdicts; Hub retains component selection and operator decision presentation. This map is proposed pending S01 source reconciliation.
