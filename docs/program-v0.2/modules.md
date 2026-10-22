# Workstream and component ownership

| Workstream | Existing scope | Proposed step mapping |
|---|---|---|
| WS-A | Orchestrator/Qualification separation and evidence handoff | 1.2,1.4,3.1–3.6 |
| WS-B | Rules, evaluator registry and activation (includes CA-02 and CA-03 local subset) | 1.3,2.1–2.5,4.1 (R4),4.4 |
| WS-C | Pin overlay and compatibility | 1.7 (target decision),4.1 |
| WS-D | D/R/M known-issue disposition | 1.1,4.3 |
| WS-E | Reporting truth and scope reduction | 4.5 |
| WS-F | Qualification hygiene and probes (Qualification-owned decisions; engineering supplies evidence) | 1.7,4.3–4.5 |
| WS-G | Reserved release choice | 4.6, deferred |
| WS-H | Comparative architecture | 1.6,1.7 (CA-04 schema),4.2; CA-02/03 through WS-B; CA-06 through 1.2,4.1,4.5; deferred extensions |

Local components own their implementations and developer tests; Orchestrator owns bounded cross-component coordination and engineering integration; Qualification owns independent frozen expectations and verdicts; Hub retains component selection and operator decision presentation. The S01 [crosswalk](s01/crosswalk.md) maps each original row, including the phase design rows (V2-P1, V2-P3, V2-P4), to steps; steps 2.1, 3.3 and 4.2 are thinly sourced (PD-S01).
