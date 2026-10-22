# AOI estimate delta (proposed planning figures)

**Not a budget, commitment or authorization.** Unit: conventional-equivalent person-days, split I (design and implementation), T (developer tests), Q (separately owned independent qualification), low/central/high, as in [../s02/estimates-m0-m1-m2.md](../s02/estimates-m0-m1-m2.md). The values are ASSUMED with confidence LOW: no AOI source records a measured rate, and no productivity measurement exists. Machine-readable mirror: [estimate-delta.json](estimate-delta.json). The delta is **not included** in the M0, M1 and M2 totals of the estimates page, which is kept unchanged. Whether to include it depends on the operator's M0 decisions, chiefly packet row 16 (which approval-bearing and state-changing paths the M1 profile contains).

## Items

| Scope | Item (steps) | I L/C/H | T L/C/H | Q L/C/H | Total L/C/H |
|---|---|---|---|---|---|
| M0 | AOI-0 source-to-field matrix finalization (1.2, 1.5) | 2/3/5 | 0/0/0 | 0.5/1/1.5 | 2.5/4/6.5 |
| M0 | AOI-1 envelope and human-intervention record (1.2, 1.4) | 2/3/5 | 0/0/0 | 0.5/1/2 | 2.5/4/7 |
| M0 | AOI-2 paired coverage declarations (1.7) | 1.5/2.5/4 | 0/0/0 | 1/1.5/2.5 | 2.5/4/6.5 |
| M0 | AOI-4 informational OTel projection design (3.4, 4.4) | 1.5/2.5/4 | 0/0/0 | 0.5/0.5/1 | 2/3/5 |
| M0 | AOI-5 Qualification request (4.4, 4.5) | 1/1.5/2.5 | 0/0/0 | 0/0/0 | 1/1.5/2.5 |
| **M0 delta** | | 8/12.5/20.5 | 0/0/0 | 2.5/4/7 | **10.5/16.5/27.5** |
| M1 | Correlation record assembly on the one bounded scenario (3.4, 3.5) | 4/7/12 | 2/4/7 | 3/6/10 | 9/17/29 |
| M1 | Observability coverage declaration validation and observation (4.2) | 2/3/5 | 1/2/3 | 2/3/5 | 5/8/13 |
| M1 | AOI adverse cases in the combined battery (4.4) | 0/0/0 | 1/2/3 | 2/4/6 | 3/6/9 |
| **M1 delta** | | 6/10/17 | 4/8/13 | 7/13/21 | **17/31/51** |

M2 delta: none priced.

## If the delta is included (central)

| Scope | Current central | With delta |
|---|---|---|
| M0 | 51 | 67.5 |
| M1 | 164.1 | 195.1 |
| Through M1, no contingency | 215.1 | 262.6 |
| Adjusted full plan | 290 | 337.5 |

## What is not priced

OpenTelemetry implementation, the ISS bridge and memory-transition provenance, multi-agent drift analytics, enterprise-wide coverage, and the refreeze and F3 requalification cost of [FP-05](../s02/f3-change-proposals.md), which stays in the separate contingency and applies only if a locked component must emit a new field.

## Caveats

1. Overlap: AOI-0 to AOI-2 partly repeat work already drafted in S02 and S03 (the identity crosswalk and the coverage declaration); the M0 items are priced as finalization and review, so the central values may be high if the M0 reviewer accepts the drafts with few changes, and low if the matrix reveals sources that need further reading (several fields are REQUIRES INVESTIGATION).
2. The M1 items assume the recommended minimum in [README.md](README.md) section 5: a correlation index assembled by the Orchestrator and the 1.4 handoff over existing records, with no locked component emitting a new field. If any required field needs a locked change, add the contingency.
3. Q values assume Qualification accepts a reduced Q01 to Q04 and Q06 set and defers Q05 and Q07; if Qualification specifies all seven, Q rises.
4. Recalibration with measured throughput remains at S03, as stated in the estimates page.
