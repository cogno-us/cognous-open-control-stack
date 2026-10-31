# QGATE-04: gate decisions and Architect decision list

Non-authorizing. Same-lineage AI work by the lead builder and short-lived workers; **not independent certification** (Q7 NOT ESTABLISHED). The separate top-level Qualification Owner and Adversarial Evidence Reviewer sessions required by D1 could **not** be instantiated from this environment (the only reachable agents are builder-spawned subagents; no other session exists), so both roles remain **NOT YET INSTANTIATED**; the strongest separation available was fresh-context read-only workers with their own file ownership, which D1 says does not satisfy the requirement. Candidate: PROVISIONAL, UNFROZEN, UNQUALIFIED. No production change; no protected path touched.

Basis: `ipc-2751-security-review.md` (A), `freeze-reconciliation.md` + `freeze-record.proposed.json` (B), `qualification-vehicle-assessment.md` (C), `negative-case-reconciliation.md` (D), `adversarial-review.md` (F: 0 HIGH, 5 MED, 7 LOW; every re-checked fact reproduced). The QGATE-03 artifact (13023553992) was never readable by this session; its numbers are **Architect-stated**.

## Gate results

| Gate | Result | Basis |
|---|---|---|
| 1 Host | **CONDITIONALLY ACCEPTED for the bounded synthetic test**: 2751 test configuration, socket 0660, peer-UID allowlist, no production use, original profile and 2750 history unchanged. Pending (a) Architect ratification that an outsider's stat of a known socket name is acceptable metadata exposure, (b) Reviewer verification against artifact 13023553992. Fallback: retain 2750, `outsider_denied_socket` BLOCKED | A + F; connect/state/listing/proc denied, only socket stat exposed (reproduced twice) |
| 2 Freeze | **BLOCKED, candidate NOT frozen** (specific inconsistencies below) | B + D + F |
| 3 Vehicle | **READY for the unambiguous portion** (existing in-process chain harness + NC rows + `mvp-acceptance.yml`); the **continuous live chain is BLOCKED by one missing interface**: the live ingress neither persists nor returns the executor result and envelope that `export_execution_artifacts` needs (`core.py:27-28`, `:111-120`; `producer_contract.py:253-289`), and no Runtime code emits the Verifier-shaped route-B ledger. A Qualification-owned capture seam could bridge it without production edits but is untested | C + F |
| 4 Battery | **NOT EXECUTED**: Gate 2 unmet; no freeze; no activated Qualification Owner; the workflows say `ubuntu-latest` (not `ubuntu-24.04`); log/artifact blobs are unreadable to this builder. Local dry runs (37 PASS / 5 BLOCKED of the in-process suite; revocation tests pass) are **not evidence** and give no verdict | C + D |
| 5 Review | Same-lineage review done (F). Separate reviewer session **NOT INSTANTIATED**; no certification | F |

## Why the freeze is blocked (exact items)

1. **Source-backed metadata staleness (repairable under D4, deliberately deferred until the rulings below land to avoid shifting pins twice):** manifest identity-inputs/tuple-pin digests `0ef8f3fd…`/`bde38aa8…` vs recomputed `e7484a0a…`/`efe9be3e…`; stale Qualification reference (`4298247e` vs `56a618eb`); stale registry digest (`d6c768c9` vs `22f49fd1`); oracle v7 status text ("v6 byte-identical plus NC7") vs the real diff (NC4-03 changed, NC4-04 added, NC7-01..03 added); workflows on `ubuntu-latest`; the suite hard-codes 2751 without a label.
2. **Contract vs oracle disagreement (acceptance-rule matters, not mine to settle):** (A1) true OS-level process kill is mandatory in the hub contract but UNQUALIFIED in oracle v7 (the cited "Q2" text is in no hub document read); (A2) operation-ledger pruning has no oracle row; (A3/A4) the NC4-03 mutation set is an empty placeholder and its verdict depends on a host-dependent part.
3. **No technical Qualification Owner approval exists**, and the immutable commitment is not stored outside the checkout. Commitment v4 `c26db0edec0a0e17ed816bc1ca519bb9c07badfd49ce4fc93c64e77dfb721160` recomputes (192/192 per-file hashes); a v5 would be forced by changing 2751 handling or any committed file.
4. Pins themselves are consistent: all 8 are full 40-hex commits, none substituted, ODES now verified.

## Mandatory negative cases (recomputed from the JSON)

42 rows, 41 mandatory (30 NC across 7 groups + 6 CHAIN + 4 VER + 1 ENV), 260 battery entries, 41 unique claims, 7 non-mandatory tests outside the 260. **No mandatory row deleted, downgraded or deferred.** Runnable once frozen with no ruling: **25 of 30 NC rows**; NC4-01..04 need the host profile (NC4-03 also a ruling); NC2-06 needs a topology answer. Results: **none executed**; no PASS/FAIL/BLOCKED verdict exists for any row. VER rows PASS on a V4 ABSTAIN (disclosed; ABSTAIN is not a PASS of the Verifier).

## Architect decision list (one packet; nothing else blocks)

1. **D3 ratification:** is an outsider's stat of a known socket name acceptable under "no unauthorized metadata"? Yes: 2751 stands for the test. No: retain 2750 and the socket-level negative test stays BLOCKED (the suite hard-codes 2751, so this would force a v5 and a suite change).
2. **A1 OS-level kill:** mandatory row with a real kill vehicle, or accepted synthetic fault injection with claim wording that does not promise recovery after real process death.
3. **A2 ledger pruning:** confirm reuse of NC3-03 or add a mandatory row (proposed row text is in `negative-case-reconciliation.md`).
4. **A3/A4 NC4-03:** fix the frozen mutation set and whether the verdict may depend on the host-dependent part.
5. **Q14 live chain:** is in-process harness + real-socket NC4/NC2-06 + Qualification-accepted equivalence sufficient, or must at least one $10 request go through the real ingress into Replay, Evidence Pack and the Verifier (which needs the Qualification-owned capture seam or a production interface, the latter needing separate authorization)?
6. **Activation:** launch two NEW top-level sessions (Qualification Owner, Adversarial Evidence Reviewer) from the existing QGATE-02 packets, each with its own worktree, and record them in a dated instrument merged by a non-builder. Attach artifact 13023553992 to the Reviewer.
7. After 1-6: authorize the lead to apply the source-backed metadata repair (a superseding dated manifest and, if needed, commitment v5), have the Owner approve the freeze, store the commitment outside the checkout, and run the battery once.

## Standing holds (unchanged)

F3 CLOSED (Q2/Q3 UNRESOLVED); Q7 NOT ESTABLISHED; final Tier 1 DEFERRED, NOT WAIVED; publication/release/production HOLD; Registry #58/#59, Control Plane #87, Ed25519 #26/#34 HELD; constructor tolerance NOT AUTHORIZED; V09 SEPARATE; DEF-OBS-TOL-OVERFLOW-1 OPEN, SEPARATE; R1 DEFERRED.
