# S01 known-issues ownership and disposition (38 items)

Source: [v0.1 known issues register](../../releases/v0.1-known-issues.md). Each item was checked against its cited source at the revisions in [inventory.md](inventory.md). Verification: VERIFIED means the cited evidence was read at source; PARTIAL means part could not be located; UNVERIFIED means not checked. For M01-M05 "verified" means the test and cited message exist; the recorded failing results were not re-run. No item was contradicted. Critical path: Y on the v0.2 critical path, P partly, N no. Disposition candidate: fix (phase), document as a limit, or defer. Disambiguation: known-issues D15 is "Qualification vs lock"; qualification decision D15 is the post-results scope reduction (known-issues D01).

| Id | Owner | Path | Candidate | Verification and evidence |
|---|---|---|---|---|
| D01 | qualification | Y (4.5) | fix P4 (three indicators) and document | VERIFIED qualification `docs/v1-known-limits.md:348-355` |
| D02 | ODES, Replay | Y (4.1, 4.3) | fix before 4.1 | VERIFIED ODES `tests/test_restriction_semantics.py:221,228`; skip marker `:210` |
| D03 | Control Plane, qualification | N | document | PARTIAL rows ER-05-1 and ER-05-5 exist; four test ids not individually matched |
| D04 | exchange, hub | P | fix P4 or document | PARTIAL heading exists (`release-status.md:40`); cause not located in exchange source |
| D05 | qualification | N | document | VERIFIED prp 0 tests, tfa 0 tests, research-intelligence 13 tests |
| D06 | qualification, runtime, registry | N | document | VERIFIED `v1-known-limits.md:17-19,61,73` |
| D07 | Replay, evidence pack, runtime | Y (3.5) | verify in 3.6 | VERIFIED `v1-known-limits.md:100-121` |
| D08 | Control Plane, hub | P | document; budget in P3 | VERIFIED `guarantees-and-limits.md:46-57` |
| D09 | hub | Y (4.2 wording) | document | VERIFIED headings; content not line-checked |
| D10 | Control Plane, runtime | Y (3.5) | document | VERIFIED `release-status.md:11-13` |
| D11 | ODES | Y (4.1) | document | VERIFIED `ODES-INTERCOMPONENT-CONTRACTS.md:341` |
| D12 | Control Plane | N | document | VERIFIED `bounded.py:56` upstream commit `46c950be` |
| D13 | ODES, verifier | P (4.1) | defer (needs ODES revision and re-vendor cascade) | VERIFIED test asserts 42, Control Plane has 43 added |
| D14 | qualification | N | document | VERIFIED text; "138 skip" not recounted |
| D15 | hub, qualification | Y (4.1) | fix via 4.1 manifest | VERIFIED lock digest `dcd3ab9e...`; hub main has moved |
| R01 | hub, verifier, ergonomics | P (2.2) | fix P2 or document | VERIFIED; scanners differ (see defects PD-B03) |
| R02 | hub | N | document | VERIFIED |
| R03 | ODES | Y | fix P1 | VERIFIED by reading `validate.py:322-338`; not executed |
| R04 | runtime | Y (3.3, 3.5) | fix P3 | PARTIAL `docs/executor-producer-profile.md:46`; "RT-1" not in repository |
| R05 | Control Plane | P | fix P1/P4 | VERIFIED and wider: no model in `bounded.py` forbids extra members |
| R06 | institutional-governance | N | defer | VERIFIED |
| R07 | verifier | N | document | VERIFIED `docs/tiers.md:150` |
| R08 | runtime | Y (3.3) | fix P3 | VERIFIED no reaper reference in the route B executor |
| R09 | Control Plane, runtime | Y (3.5) | document | VERIFIED `freshness.py:75` |
| R10 | runtime (carrier in Control Plane) | Y (3.3) | fix P3 (touches a locked component) | VERIFIED `control_plane_adapter.py:349-351` |
| R11 | Replay | N | defer | VERIFIED changelog; rows not re-checked |
| R12 | registry | N | document | VERIFIED |
| R13 | hub | Y (4.1) | fix in 4.1 | VERIFIED `collateral/evidence-snapshot.json:7` |
| R14 | qualification | Y (4.3) | fix P4 | CONFIRMED by controller source `tools/v1_validation.py:678-681` (register said unverified) |
| R15 | verifier | N | document | VERIFIED `rules_lifecycle.py:516-521` |
| R16 | various | N | document (open list) | PARTIAL |
| M01 | exchange or qualification | N | fix P4 or reclassify | VERIFIED test and reason code exist |
| M02 | runtime | P (3.5) | fix P3 | VERIFIED `engine/c8_source_evidence.py:74` |
| M03 | qualification | N | document | VERIFIED |
| M04 | runtime, Control Plane | Y (3.5) | fix P3 or reclassify | VERIFIED |
| M05 | runtime, Control Plane | Y (4.2) | fix P4 or reclassify | VERIFIED |
| M06 | qualification | N | document | VERIFIED `process/adversarial/components.json` |
| M07 | qualification | N | document | UNVERIFIED (count only in the limits document) |

Totals: 38 items; critical path Y 16, P 6, N 16; 33 verified or confirmed, 4 partial (D03, D04, R04, R16), 1 unverified (M07). R14 moved from partial to confirmed after the qualification controller source was read. Qualification-owned items (D01, D05, D06, D14, R14, M03, M06, M07 and part of M01) are expectations or controller logic that engineering does not edit; they are listed for the independent controller (#218) to decide. Items that change a locked component (R10, R04, R08, M02, M04, M05) need separate authorization and F3 requalification before acceptance.
