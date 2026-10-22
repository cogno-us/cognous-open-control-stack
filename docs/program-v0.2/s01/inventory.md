# S01 verified source inventory

Method: each repository was cloned over HTTPS and checked out at the stated revision; sizes are from `git ls-files` and `wc -l`; test counts are static counts of `def test_` and understate collected cases (Control Plane: 625 defined, 1,194 collected per the qualification record). Tags: VERIFIED means measured or read at the revision. Read-only; nothing was executed. Role comes from the stack map and the component lock. Release and production remain on HOLD.

## Repositories (18 in scope)

The lock has 14 entries and the verifier is one of them; the earlier phrase "15 locked components plus the verifier" double-counts. Scope is the 14 locked repositories, the hub, the orchestrator, qualification and ergonomics.

| Repository | Revision | Role | Source / test LOC | Tests | Workflows | Licence (top level) |
|---|---|---|---|---:|---:|---|
| cognous-open-control-stack (hub) | `308932f7` main, not locked | selection authority, documents, reference profiles | 6,042 / 4,999 | 540 | 42 | Apache-2.0 |
| cognous-action-manifest | `fa170815` | declaration | 1,487 / 1,952 | 157 | 1 | Apache-2.0 |
| cognous-control-plane | `0a41faa9` | policy control (`bounded.py` 2,756 lines) | 10,442 / 13,311 | 625 | 4 | Apache-2.0 |
| cognous-institutional-governance | `9b5ab721` | authority semantics | 11,283 / 6,945 | 520 | 2 | Apache-2.0 plus CC-BY-4.0 |
| cognous-governed-exchange | `7f7569b0` | exchange transport | 3,802 / 2,189 | 107 | 4 | Apache-2.0 |
| cognous-execution-runtime | `ec728da6` | constrained execution (`engine/` 5,622 lines) | 5,622 / 6,636 | 283 | 15 | MIT; `engine/` Apache-2.0 |
| cognous-replay-bundle | `028f63d1` | replay | 5,668 / 8,553 | 437 | 4 | Apache-2.0 |
| cognous-governance-evidence-pack | `a3ebbb90` | evidence | 3,669 / 3,303 | 229 | 7 | Apache-2.0 |
| open-decision-evidence-standard | `e86a25a1` | decision-evidence standard (18 contracts) | 17,532 / 9,441 | 751 | 3 | Apache-2.0 |
| cognous-evidence-attestation | `981036c3` | attestation (BitRep) | 1,334 / 967 | 58 | 2 | Apache-2.0 plus MIT |
| cognous-evidence-registry | `b2485998` | claims and evidence registry | 4,318 / 2,977 | 200 | 1 | Apache-2.0 plus MIT |
| cognous-open-control-stack-verifier | `c0b8ba1f` | verifier | 9,203 / 12,946 | 467 | 1 | Apache-2.0 |
| portable-reasoning-protocol | `cb137f02` | optional lock entry | 0 / 0 | 0 | 0 | none at top level |
| research-intelligence-protocol | `30c7274b` | optional lock entry | 146 / 139 | 13 | 1 | Apache-2.0 |
| truth-freedom-agency-protocol | `442d07b4` | optional lock entry | 68 / 0 | 0 | 1 | none at top level |
| cognous-stack-orchestrator | `a745e131` main, not locked | integration and evidence coordination | 4,924 / 7,225 | 355 | 36 | Apache-2.0 |
| cognous-stack-qualification | `195c728f` main (tagged) | controller, suites, retained results (27,594 of 28,677 files are results) | 28,064 / 60,893 | 2,403 | 68 | Apache-2.0 |
| cognous-open-control-stack-ergonomics | `bea582b3` main | `cognous-ocs` CLI | 7,822 / 5,794 | 378 | 1 | Apache-2.0 |

Mains ahead of the lock: verifier, institutional-governance, prp, research-intelligence, tfa; the other nine locked repositories have main equal to the lock. The hub tag `review-v0.1-g8-r10-20261022` points at `a2d9396c`, earlier than hub main. Review tags exist on 14 repositories (not the orchestrator, prp, research-intelligence or tfa).

## Revision disagreements between artifacts

| Component | Locked | Other revisions named by other artifacts | Where |
|---|---|---|---|
| Control Plane | `0a41faa9` | `2ea9528e` (runtime pin), `d3dadee7` (hub business-collateral), `2bac7875` (adversarial suite and orchestrator), `46c950be` (manifest port upstream commit, `bounded.py:56`) | runtime `engine/safe_executor.py:17`; hub `collateral/business-collateral.md:39`; qualification `process/adversarial/components.json` |
| Runtime | `ec728da6` | `1b0a9e32` (orchestrator O6-Q6, 169 commits behind), `6b16962d` (orchestrator O5), `c3c3ee71` (collateral) | orchestrator tests and workflows |
| Action manifest | `fa170815` | `ff549082` (orchestrator) | orchestrator pins |
| OpenAPPA | not locked | `10aa0e09`, `v0.31.1`/`4debcfb7`, upstream main `1c52575` | hub integration documents; runtime workstream documents |

The orchestrator contains none of the 14 lock revisions in non-markdown files (45 distinct 40-hex values, 477 occurrences including documents). Its green CI therefore exercises older pins, not the selected tuple.

## Orchestrator and qualification facts used by the crosswalk

- Orchestrator: 209 files, 82 Python files (12,149 LOC), 36 workflows. State store, event history, scheduler and dispatcher do not exist (`orchestration/state-transitions`, `workflow-contracts`, `dependency-registry` are README-only). Only SQLite is the synthetic refund fixture (`development/scenarios/customer_refunds/runtime/refund_runtime.py`, 429 lines) pinned to runtime `6b16962d`. Recovery intake `development/recovery/o6_q6/reconciliation.py` is 144 lines and issues no authority.
- Qualification: controller `v1-validation.yml` (577 lines) with ten jobs; `tools/v1_validation.py` 1,378 lines; 131 requirement rows (39 mandatory in the reduced claim; 75 in the unreduced mandatory set); refreeze log 61 entries; g8-r10 job statuses 34 PASS, 2 FAIL, 2 NOT RUN; pre-reduction mandatory verdict INCOMPLETE. The controller never mentions or runs the orchestrator.
- Refund chain implementations: orchestrator O5 (4,543 LOC plus 14 workflows), qualification `tools/run_matched_refund.py` and `suites/v1-scenarios` (45 files, 15,932 LOC, 303 tests), hub reference profiles.
- Pin literals: orchestrator 18 workflows (94 lines) and 34 source files (101 lines); the only lock reader is `development/acceptance/o6-q5/admission.py:96`. Qualification guards its own literals (`tools/v1_validation.py:381` `cmd_check_workflow_pins`, `suites/_pins.py`).

## Registry-relevant facts

- Canonical JSON: four families across the stack (compact legacy form; ASCII-escaped; default flags; default separators). ODES also holds a tested `rfc8785-jcs` profile (24 tests) that differs from the legacy form on key order for astral characters, floats and large integers. Control Plane documents that it does not claim RFC 8785.
- Scanners: three non-equivalent copies (hub, verifier, ergonomics).
- Required checks: no table in Control Plane; the verifier `MANDATORY_KINDS` and 44 check identifiers are the nearest manifest. Reason-code maps are already versioned data (121 and 164 codes) with a vendoring and provenance precedent.
- Commit-bound mechanisms that exist: runtime `authority_policies_v1` in-transaction comparison, exchange generation fence, BitRep digest custody with epoch. No acknowledgement of an active rule-set exists.
- Pin carriers moved by a refreeze: hub (124 files carry a current lock revision), four component code sites, ergonomics (4 files), qualification (workflow lines, 13 profile files, refreeze log, declared sets). Reproduced cost: seven PRs across seven repositories for g7-r10 and g8-r10; two for single-component refreezes.

## Limits of this inventory

Not deep-read: exchange `gax_ref_runtime.py` (about 1,600 lines), runtime `control_plane_adapter.py`, ODES lifecycle and journal validators line by line, Replay validator and redaction, Evidence Pack validator rule bodies. The OpenAPPA site, the Microsoft AGT repository and the paper "From Mainline to Governed Cognition" could not be read; claims depending on them are marked REQUIRES INVESTIGATION in [comparative.md](comparative.md).
