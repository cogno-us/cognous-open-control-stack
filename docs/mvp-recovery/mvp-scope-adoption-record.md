# MVP scope and adoption record (successor text, prepared for operator approval)

Status: PREPARED FOR OPERATOR APPROVAL, dated 2026-10-24. NOT adopted. This record is not retrospective, is not backdated, and records no adoption that has not been given. Non-authorizing, builder-side, documentation-only. Release, publication and production remain on HOLD. No qualification, certification, security-clearance or readiness claim is made. Qualification owns its acceptance criteria, oracle, evidence and verdicts; the Hub does not.

Labels: V = verified against hub main by reading it; R = reported (not re-verified here); I = inferred. Basis: hub `main` at `7661983849474784469f029297fd5bbcccd03ffe` (V, read 2026-10-24). Companion: [program-crosswalk.md](program-crosswalk.md). Constitution rev `6f7f2731` is provisional guidance and is not adopted.

## 1. Operator directive (October 24)

> The October 31 MVP remains a bounded subset and extension of the original four-phase, 24-step, S01-S12 program. The original program remains unchanged.

The original program (`docs/program-v0.2/*`, `engineering-register.json` rev r4-aoi, `docs/workstreams/*`, historical evidence) is not edited by this change. The MVP is a bounded subset (steps kept, narrowed or reduced) and an extension (ingress, launcher, F3 repairs, candidate manifest, informational catalogue, successor trusted-host profile).

## 2. Source documents with stale assumptions (exact revisions read from main)

These three documents are PROPOSED, remain unedited, and carry stale assumptions. The corrected successor text is in section 3 of this record. Revision = git blob id at the basis commit above (V); last-touching commit for all three on the shallow clone is the basis commit.

| Document | Blob (V) | Stale assumption |
|---|---|---|
| `docs/mvp-recovery/mvp-definition.md` | `df4a1e142301cdb5408485398110943d1e40ee48` | Tuple pins CP `0a41faa9`, Runtime `ec728da6`, Replay `028f63d1`, Evidence Pack `a3ebbb90`, ODES `e86a25a1` are pre-F3 text; "unchanged on main" no longer holds. Says adoption is pending. Orchestrator excluded without naming the M0 conflict. Line 9: "re-pinned at refreeze". |
| `docs/mvp-recovery/scope-reduction-register.md` | `64d7e6dbced2d83c0efd964315eb9e7e827305c6` | Assumes no locked-component change; omits ingress, launcher, candidate manifest, catalogue and successor host profile; step statuses (e.g. "not started") are pre-delivery; "7 PRs in 7 repos per refreeze" framed as per-refreeze cascade. |
| `docs/mvp-recovery/mvp-dependency-graph.md` | `cdeeae575ef8df224f2234b20fe1218fb2040979` | Orchestrator edges removed as "EXCLUDED" without superseding M0 row 5; reachability inventory listed as added edge only. |

Also read (V, not stale in the sense above): `critical-path.md` blob `6a7e6e071f93a1c1f6c5f60133612ac88950b147`, `qualification-contract.md` blob `5e4383d099cae4f1559c450b47e3db7981a86137`.

## 3. Corrected successor text for the October 31 MVP

### 3.1 Candidate tuple (V: `docs/mvp-package/candidate-manifest.json`, blob `7afef8de62cb0c9ce5ba0ba48cac242e50112f65`; status UNQUALIFIED, provisional, not frozen)
Control Plane `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c` (F3 claim-journal fix); Runtime `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f` (F3 terminal approval revocation); Replay `40012b8c174c6f25685bd5d9bc93ff46cc9a5842`; Evidence Pack `7b9511f2c6d56d424f17b078826594abd29f6c96`; ODES `1a5e1d300250d832e611633f0bf8f762e398c0ec`; Action Manifest `fa170815ef96a54c233d0dd9da821b60debabf8b`; Verifier `c0b8ba1f55b75db787a320f3de0f79342c6f6826` (bounded verifier; later doc revision `39d46b49` is not the pin); hub provenance `c897266b7ce4b921889519087fa8b1863b4302e3` (merge of #232). CPython 3.13, hash-locked dependencies. The historical hub `component-lock.json` is stale and does not describe this tuple (V per manifest; hub draft #223 proposing a lock bump is open, V). The manifest's registry-catalogue digest field still reads `d6c768c9...` superseded-pending while the merged catalogue manifest digest is `22f49fd1...` (V); that is a pending manifest successor, not changed here.

### 3.2 Scope
Capability, seven required behaviours, scenario (matched synthetic USD 10 refund), route B with operation identity, synthetic SQLite, Linux single host, trusted synthetic resolver, narrow evidence claim (architect MVP2 Q6 wording) and the two verification paths are carried verbatim from mvp-definition.md (V) and are not restated here. Explicit limitations are carried, not removed. Verifier V4 ABSTAIN is never converted to PASS. Python 3.11 is unqualified; route C and the ODES exporter are excluded (rulings-3, V).

### 3.3 Supersession of the M0 Orchestrator migration dependency, for the October 31 MVP ONLY
- M0 decision record (V, `docs/program-v0.2/m0-decision-record.md`), row 5: "ADR-P05 ownership: one bounded refund scenario migrates to the Orchestrator; Qualification keeps independent expectations. Approved."
- For the October 31 MVP only, this record proposes that the refund-chain migration to the Orchestrator is NOT a dependency of the MVP. The refund path is exercised on the existing Control Plane / Runtime stack with Replay + Evidence Pack (architect Q1/Q7 exclude the Orchestrator handoff; V in rulings).
- The M0 decision (row 5) is preserved unchanged and the full-program obligation to migrate the refund scenario remains. This is a scoped change to MVP dependencies. It is not completion, reopening, or dismissal of the Orchestrator work. Parked Orchestrator PRs #130-#132 and hub #213 remain parked (V critical-path). The scoped change takes effect only on operator approval of this record.

### 3.4 Develop, Integrate, Test, Final Freeze (operator-directed, architect Rounds 5-7; recorded prospectively)
This is recorded prospectively as of 2026-10-24. No dated earlier source is claimed; none was found in the hub (R: the direction was relayed by the coordinator). Direction:
1. Development and component testing continue.
2. Qualification establishes its acceptance baseline before the final run.
3. Independently controlled expectations are preserved before acceptance.
4. The integrated candidate is frozen once, after final acceptance.
5. A later material change needs appropriate revalidation, not an automatic seven-repository cascade.
Effect: the "7 PRs in 7 repos per refreeze" wording and "refreeze" wording in documents listed in section 7 are historical observations or planning text and are read in light of this direction for the MVP only. No new gate, intermediate freeze or approval step is created. The existing candidate manifest remains UNQUALIFIED and not a freeze.

### 3.5 MVP-specific work accounted for
| Work | Evidence | Label |
|---|---|---|
| Trusted-host ingress, `tools/mvp_ingress` | hub #217 merged (V) | V |
| Isolated launcher, mandatory peer-uid allowlist | hub #230-#232 merged (V); `tools/mvp_ingress/BOUNDARY.md` | V |
| F3 repairs: Runtime #144, Control Plane #83 | named in candidate manifest origins (V); merge facts in component repos | R |
| Fixed candidate manifest and validator | hub #228, #231, #233 merged (V) | V |
| Six-layer informational registry catalogue (`authority: none`) | hub #225, #229 merged (V); `registry/README.md` | V |
| Successor trusted-host (distinct-UID) profile | Qualification #225, open draft (V); not adopted by Qualification | V |

None of these satisfies an original program exit by itself. The catalogue is informational, off the MVP critical path, and satisfies no register exit for steps 2.1-2.5.

### 3.6 Unchanged historical positions
Original restricted-host profile (Yama `ptrace_scope>=1`, dedicated uids): host-isolation properties INCOMPLETE, unchanged. Verifier V4: ABSTAIN retained. g8-r10: reduced 39-row selected verdict is cited only with the 75-row result (40 PASS, 30 INCONCLUSIVE, 5 NOT RUN; INCOMPLETE) and the post-observation selection statement. Qualification issue #218 is closed (not_planned, 2026-10-24T18:07:43Z, administrative, no verdict; V by REST) and historical; it is not reopened, and Qualification retains ownership of its acceptance criteria and evidence. Coordination runs through hub #193 (open), existing Qualification PRs and the final Qualification report. Hub PR #218 (merged status docs) is a different object from Qualification issue #218.

The successor trusted-host profile does not erase the original: its wording is Qualification's (Qualification #225 draft), no same-UID, ingress-UID, root or interpreter isolation claim is made, and properties not independently exercised stay INCOMPLETE.

## 4. Operator approval requested (not given)
Approve or amend: (a) section 3 as the MVP scope for October 31; (b) the scoped M0 row 5 supersession in 3.3; (c) the direction in 3.4. Until recorded by the operator in a dated successor entry, none of these is adopted. `minimum-profile.md` acceptance (registry coverage, migrated rule family, durable workflow) is proposed as superseded for the MVP only, as the register already proposes; the file is unchanged.

## 5. Unresolved items (owner, evidence, MVP applicability, disposition)
Rule: an informational catalogue gap is not an MVP blocker. An unresolved mandatory requirement on the supported execution path remains a blocker. No implementation work is assigned here.

| # | Item | Owner | Evidence | MVP applicability | Disposition |
|---|---|---|---|---|---|
| U1 | 14,176 catalogue entries with unresolved MVP applicability (of 3,190 rules, 2,840 scenarios, 6,648 tests, 2,011 fixtures, 19,860 evidence, 6,030 coverage rows; V) | Hub (catalogue is informational) | `registry/catalogue-v0.1/manifest.json` `unresolved_accounting` (V, digest `22f49fd1...`) | Informational; not on MVP critical path | Recorded, not a blocker. Applicability classification stays open; the nine MVP-linked items were classified by overlay #229. |
| U2 | 17,704 evidence records without source revision (V; plus 45 entries without recorded source revision, 15,384 unresolved placeholders/relationships, 9 crosswalk rows) | Hub | same manifest | Informational | Recorded, not a blocker. Such records are not used as evidence for any MVP claim. |
| U3 | Outdated controller references: program README and operator-decisions name Qualification #218 as live controller; hub #193 body and comments stop before MVP pivot | Hub (references); Qualification (its own controller state) | `docs/program-v0.2/README.md` layer 3, `operator-decisions.md` line 25 (V); #218 closed (V) | Documentation only | Superseded-for-MVP pointer in section 7; originals unchanged. No comment is posted by this change. |
| U4 | Operator adoption of MVP definition / register / this record | Operator | section 4; source docs say adoption pending (V) | Required for MVP scope to be adopted | OPEN, awaiting operator. |
| U5 | Static effect-reachability inventory (critical-path 4e; qualification-contract item 6) | Hub (4e text); Qualification decides whether its contract requires it | section 6 | Required only where the adopted Qualification contract requires it | NOT FOUND as a completed artifact. An unmediated reachable path on the supported path remains a blocker if found. No work assigned here. |
| U6 | Proposed mandatory rows NC7-01..03, NC2-06 and changed NC4-03 predicate | Qualification | Qualification #225 draft (V open); hub #222/#224 | Mandatory criteria are Qualification's | OPEN, Qualification decides. Hub does not adopt. |
| U7 | Yama non-mandatory only in Qualification #225 draft; hub `supported-capabilities-and-limitations.md` line 22 and `qualification-initiation.md` line 17 still require `ptrace_scope>=1` | Qualification (profile); Hub (its docs) | those files (V) | On supported path | OPEN; hub text unchanged; original restricted-host INCOMPLETE preserved. |
| U8 | Verifier V4 attempt-ledger agreement | Qualification | mvp-definition narrow claim (V) | Supported path | ABSTAIN retained; never PASS. |
| U9 | Ambiguous-effect / unknown-outcome path (architect Q9) and ODES 4 failures (3 declared), Replay ER-07-2 xfails | Component owners; Qualification verdict | critical-path, register ODES row (V) | Supported path (mandatory behaviour 7) | OPEN; remains a blocker for the safe-retry / ambiguous-effect claim if neither repaired nor proven. |
| U10 | Candidate manifest catalogue digest field `d6c768c9...` vs merged `22f49fd1...`; hub #244 bundles further change | Hub | candidate-manifest.json, catalogue manifest (V) | Candidate identity bookkeeping | Pending a dated successor manifest by the owning change; not edited here. |
| U11 | Lock/pin reconciliation (hub #223 open draft; stale `component-lock.json`) | Hub / component owners | #223 open (V) | Candidate identity | OPEN. |
| U12 | Python 3.11 integration; route C; ODES exporter | Hub | rulings-3 (V) | Excluded | Documented limits. |
| U13 | Single-final-freeze direction has no dated source in the hub | Operator | section 3.4 | Planning | Recorded prospectively; see section 3.4. |

## 6. Static effect-reachability inventory: found or not found
Searched the repository on main (file names and content). NOT FOUND as a completed, source-backed inventory of reachable effect surfaces for the selected MVP route. Related, non-equivalent artifacts exist: the proposed seed inventory `docs/program-v0.2/s03/coverage-seed.json` ("PROPOSED seed inventory for step 1.7; read-only static observation", status DECLARED/ENUMERATED/OBSERVED rows, V) with `docs/program-v0.2/s02/registry-and-effects.md` surface numbering (FP-01); `tools/mvp_ingress/BOUNDARY.md` (closed client surface: one socket, one operation; V); `.github/workflows/lifecycle-inventory.yml`, `publication-inventory.yml` and `tools/lifecycle_inventory.py`, `tools/verify_publication_inventory.py` (publication and lifecycle inventories, unrelated to effect reachability). Qualification's own repository was not searched for this item (I). It is a required source-backed deliverable only where the adopted MVP qualification contract requires it (`qualification-contract.md` suite item 6, architect Q10: a reachable unmediated path is a release blocker). No implementation work is assigned by this PR.

## 7. Superseded-for-the-MVP pointer notes (new text only; the listed files are not edited)
Superseded for the MVP by sections 3.3 and 3.4 of this record, once approved by the operator, where they concern the M0 Orchestrator dependency or repeated refreeze/seven-repository-cascade wording. Originals stand as written.
- `docs/program-v0.2/s02/f3-change-proposals.md` lines 3 and 5 (each F3 package needs refreeze; seven PRs per refreeze).
- `docs/program-v0.2/s02/adr-proposals.md` lines 44-45 (refreeze cost; P04 fewer layers).
- `docs/program-v0.2/s02/estimates-m0-m1-m2.md` lines 14, 32 (refreeze and requalification contingency).
- `docs/program-v0.2/s05/2.4-activation-design-and-f3-impact-proposal.md` line 65; `s05/2.4-architect-defaults` line 20 ("per refreeze").
- `docs/mvp-recovery/delivery-estimate.md` lines 15, 22; `critical-path.md` lines 26, 37; `mvp-definition.md` line 9; `scope-reduction-register.md` line 46.
- `docs/mvp-package/qualification-initiation.md` line 16 (any hashed-file change needs a new commitment; Qualification owns this rule and it is not altered).
- `docs/program-v0.2/m0-decision-record.md` row 5 (scoped, see 3.3; decision preserved).
- `docs/program-v0.2/README.md` layer 3 and `operator-decisions.md` line 25 (Qualification #218 as live controller; now closed and historical).
- `docs/program-v0.2/minimum-profile.md` acceptance (superseded for the MVP, as already proposed in the register).
Historical evidence is preserved with no pointer added: `docs/program-v0.2/s01/*`, `s03/minimum-profile-and-coverage.md`, `docs/releases/*`, `docs/workstreams/*`, `CHANGELOG`. Line numbers are as read at the basis commit; the reconciliation report's section D is the source (R for lines not re-read).

## 8. Not verified here
Operator adoption of any MVP document; the original wording and date of the Develop/Integrate/Test/Final Freeze direction; architect Round 5-7 texts (not in hub docs); merge and review state of orchestrator #124-#132, Runtime #144, Control Plane #83; verifier test counts; Qualification main and the contents of hub #221-#223; whether Qualification requires NC7-01..03.
