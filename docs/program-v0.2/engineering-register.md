# Program v0.2 engineering register (placeholder)

Non-authorizing. HOLD unchanged. No production use. Every row is a proposal with placeholder acceptance; no row is completed work, and nothing here claims certification, security clearance or readiness. See the [README](README.md) for how to read this file. Current status is in [status.md](status.md) only (DOC-01).

## Conventions

- **Id:** `V2-<workstream>-<nn>`, stable once assigned; never reused or renumbered.
- **Status** is the declared planning disposition, from a fixed vocabulary: `PROPOSED` (default), `ACCEPTED` (owner accepted the row for v0.2), `DEFERRED` (owner deferred it), `SUPERSEDED` (replaced by a named row). Execution state (started, blocked, done) is never recorded here.
- **Owner:** role placeholder `TBD-role`.
- **Acceptance** and **Evidence:** `TBD` placeholders. Evidence is later a pointer to an exact commit or record, never a status claim.
- **Tier:** constitution review tier (1, 2 or 3). Tiers here are initial proposals and are confirmed at acceptance.
- **Source** names the learning that motivates the row: a known-issue id from the [v0.1 known issues register](../releases/v0.1-known-issues.md), the hub issue, or `planning`.

## Register

| Id | Title | Workstream | Source / learning | Owner | Status | Acceptance | Evidence | Tier |
|---|---|---|---|---|---|---|---|---|
| V2-A-01 | Orchestrator back in the fold, separated from qualification | WS-A separation of powers | planning; D15, D14 | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-A-02 | Orchestrator assembles pinned components and demonstrates behavior using observed vocabulary only; qualification owns criteria, oracles, verdicts and evidence | WS-A | planning | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-A-03 | One-way flow from orchestrator to qualification, via a versioned evidence handoff manifest with a canonical digest | WS-A | planning | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-A-04 | Orchestrator is lock-driven, with no hard-coded component pins | WS-A | planning; D14 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-A-05 | Path-ownership guard: evidence producers cannot edit qualification expectations | WS-A | planning | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-A-06 | Correct the wrong "private" wording about the orchestrator in qualification and hub docs | WS-A | planning | TBD-role | PROPOSED | TBD | TBD | 1 |
| V2-A-07 | Orchestrator README line 22 is stale; refresh | WS-A | planning | TBD-role | PROPOSED | TBD | TBD | 1 |
| V2-A-08 | Keep orchestrator O4e/Q5/Q6 content; resolve the refund-chain duplication | WS-A | planning | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-B-01 | R0: inventory and contract freeze, including the authority-to-effect consistency contract and the canonical JSON algorithm freeze | WS-B registry instead of hard-coding | hub issue #184; [registry direction](../declarative-governance-registry.md) | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-B-02 | R1: scanner extraction into registry data | WS-B | hub issue #184 | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-B-03 | Required-check extraction into registry data | WS-B | hub issue #184 | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-B-04 | R2: resolution and epoch | WS-B | hub issue #184 | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-B-05 | R3: independent equivalence tests | WS-B | hub issue #184 | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-B-06 | R4: integration | WS-B | hub issue #184 | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-B-07 | Decide whether the registry lives in a separate repository (suggested) | WS-B | hub issue #184 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-C-01 | Data-driven pin overlay to reduce refreeze layers | WS-C pin-round cost | known issue: every refreeze needed 7 repository PRs | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-D-01 | Burn down declared limits D01-D15 (one row per class) | WS-D known-issue burn-down | D01-D15 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-D-02 | Burn down issues observed in review R01-R16 (one row per class) | WS-D | R01-R16 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-D-03 | Burn down results measured outside the controller M01-M07 (one row per class) | WS-D | M01-M07 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-E-01 | Three indicators on release-facing summaries: mandatory verdict, raw suite health, original-scope coverage | WS-E reporting | D15 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-E-02 | Explicit disclosure rule for any post-hoc scope reduction (D15) | WS-E | D15 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-F-01 | Controller covers the `prp` and `tfa` jobs, now NOT RUN | WS-F qualification hygiene | D05 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-F-02 | Wiki-derived suite collected by the controller | WS-F | M01-M05 | TBD-role | PROPOSED | TBD | TBD | 2 |
| V2-F-03 | `probes-*` jobs judged by the job gate | WS-F | M06 | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-F-04 | Comparator digests refreshed in the same change as any `run_core.py` edit | WS-F | planning | TBD-role | PROPOSED | TBD | TBD | 3 |
| V2-G-01 | Review release deferred: v0.1 review marker tags exist (`review-v0.1-g8-r10-20261022`); no release or publication is planned until the owner decides | WS-G review release | [release status](../release-status.md) | Owner | DEFERRED | Owner decision | TBD | 1 |
