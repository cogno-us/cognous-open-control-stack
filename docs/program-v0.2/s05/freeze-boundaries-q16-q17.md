# Freeze boundaries and provisional ceilings (Q16, Q17)

**Non-authorizing record. Release, publication and production remain on HOLD.** Nothing here claims clearance, certification, qualification or readiness for any use. Source of the rulings: the architect disposition Q1-Q17 (binding for this programme). The Hub coordinates; component owners own components; independent Qualification owns oracles and verdicts; the operator owns authority decisions.

A freeze here is an engineering freeze of a wire profile. It is not a Qualification PASS and not a production authorization. Related: [disposition record](architect-disposition-q1-q17.md).

## 1. Provisional single-host event-store ceilings (Q16)

These are configurable safety ceilings. They are not established performance-safe defaults. Default operational limits are chosen only after measured memory, disk, append-latency and recovery behavior. Archival retention is kept separate from active capacity. Unresolved-effect evidence is never discarded to reclaim slots.

| Parameter | Provisional ceiling |
|---|---|
| Events per workflow | 10,000 |
| Event payload | 64 KiB |
| Workflows per store | 1,000 |
| Recovery reserve | 64 events |
| Coordination events per workflow | 16 |
| Concurrent active workflow slots | 64 |

Observation records keep the distinct member `execution_standing` with exact closed values, separating workflow coordination, authority disposition and externally observed effect.

## 2. The five provisional wire profiles (Q17)

| Profile | Freeze boundary |
|---|---|
| `ocs-mandatory-manifest/0` | Historical `/0` contract stays separately identified; `/1` freezes only after its own independent applicability/evaluator review. |
| `cognous-producer-observation/0` | After `execution_standing` and exact observation semantics are reviewed, before independent 3.4 qualification. |
| `cognous-source-preserving-handoff/0` | After custody, path, disclosure and portability semantics are reviewed, before independent 3.4 qualification. |
| `ocs-workflow-event/0` | After lifecycle, capacity, integrity and recovery contracts are reviewed, before independent 3.2 qualification. |
| `ocs-workflow-lock/0` | After lock ownership, expiry, contention and recovery semantics are reviewed, before independent 3.2 qualification. |

## 3. Freeze identity requirements

Each freeze record must identify: exact revision; schema digest; producer; consumer; supported environment; associated qualification scope.

## 4. Independence rule

Freezing one profile does not freeze any other. A freeze of one profile makes no statement about the others, about their ceilings, or about components that consume them.
