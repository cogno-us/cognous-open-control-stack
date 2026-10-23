# MVP dependency graph (rebase of the v0.2 register edges)

Status: PROPOSED per architect ruling Q2; non-authorizing; HOLD. The full v0.2 register (`docs/program-v0.2/engineering-register.json`, r4-aoi) is unchanged and remains the historical and future-program authority. Each removed edge carries a justification; mandatory safety dependencies are not removed to shorten the graph. "Justification" is one of: EXISTING (an existing qualified mechanism is used), EXCLUDED (capability outside the MVP profile), BOUNDED (equivalent bounded control).

| Register edge | MVP treatment | Justification |
|---|---|---|
| 1.7 -> 1.3 (registry R0 contract) | removed | EXCLUDED: no registry in the MVP; fixed pinned configuration. The registry does not replace effect-time authorization in Control Plane/Runtime (registry design doc). |
| 1.7 -> 1.4, 1.5, 1.6 | 1.4, 1.5 kept (narrowed); 1.6 removed | 1.4/1.5 define evidence handoff and unknown-outcome vocabulary the MVP uses via Replay/Evidence Pack and the existing ODES lifecycle; 1.6 is comparative only (EXCLUDED). |
| 2.1-2.5 chain (and 4.1/4.3/4.4 -> 2.5) | removed | EXCLUDED: no rule records, activation or equivalence; any existing control from those components that the MVP depends on stays in scope (none identified so far; confirm in the reachability investigation). |
| 3.5 -> 3.2, 3.3 | 3.2 removed; 3.3 kept (narrowed to MVP-reachable effect surfaces) | 3.2 is the Orchestrator durable workflow, EXCLUDED; durable unknown-outcome handling is EXISTING in Runtime + Replay (verify in the harness investigation). 3.3 stays: unmediated paths are a mandatory negative. |
| 4.2 -> 3.5 | kept | Coverage inventory covers the selected route including revocation/unknown-outcome paths. |
| 4.1/4.3/4.4 -> 3.6 | removed | EXCLUDED: 3.6 qualifies the Orchestrator; the Qualification Contract replaces it. |
| 4.5 -> 4.1, 4.3, 4.4 | kept | Acceptance dossier needs exact candidate identity, on-path issue closure and the adversarial battery. |
| 4.6 -> 4.5 | kept | Operator decision follows the dossier. |
| New: 1.7 (MVP) -> exact-candidate vehicle -> Qualification claim freeze | added | Architect Q13/Q14: claim frozen before the battery; direct exact-candidate job preferred. |
| New: 3.3/4.2 -> static effect-reachability inventory | added | Architect Q10: reachable unmediated path is a release blocker. |
| New: ambiguous-effect disposition -> 3.5 | added | Architect Q9. |
