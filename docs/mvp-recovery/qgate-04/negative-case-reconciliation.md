# QGATE-04 Workstream D: mandatory negative-case reconciliation (OCS-MVP-QGATE-04)

Status: NON-AUTHORIZING reconciliation by a Workstream D worker (short-lived reconciler). AI, same-lineage work: NOT independent certification (Q7 NOT ESTABLISHED; D1 roles NOT YET INSTANTIATED). It changes no oracle, battery, gate, pin, component or workflow, authorizes nothing, and removes, downgrades or defers no mandatory row. Qualification owns every row and verdict. Candidate PROVISIONAL, UNFROZEN, UNQUALIFIED. Release, publication and production HOLD. Standing holds unchanged (F3 CLOSED, Q2/Q3 UNRESOLVED; Q7 NOT ESTABLISHED; final Tier 1 DEFERRED, NOT WAIVED; Registry #58/#59, Control Plane #87, Ed25519 #26/#34 HELD; constructor tolerance NOT AUTHORIZED; V09 SEPARATE; DEF-OBS-TOL-OVERFLOW-1 OPEN, SEPARATE; R1 DEFERRED).

Labels used: SOURCE (text read, with file:line), OBSERVATION (a local DRY RUN by this worker: not evidence, no retained artifact, not a Qualification run), INFERENCE (reasoning from the above), ARCHITECT-STATED (supplied in the assignment or in an Issue #215 comment; not read from the artifact), UNVERIFIED.

Sources read: Qualification repo `cogno-us/cognous-stack-qualification` at `56a618eb2c235993526cf8423e00efa5703fec55` (shallow clone `/tmp/claude-0/qual`), oracle `process/mvp-chain/expectations.proposed.v7.json`, battery `process/mvp-acceptance/mandatory-battery.proposed.v1.json`, `gate-expectations.proposed.v1.json`, `environment-profile.proposed.v1.json`, `process/mvp-chain/NC4-03-PROPOSAL.md`, `process/mvp-acceptance/mandatory-battery.ingress-ambiguity.placeholder.md`, `suites/mvp-chain/*`, `tools/mvp_acceptance_gate.py`, both workflows; hub docs `qualification-contract.md`, `architect-rulings.md`, `architect-rulings-2.md`, `architect-rulings-3-and-known-limitations.md`, `critical-path.md`, `scope-reduction-register.md`, `mvp-readiness-reconciliation-2026-10-30.md`, `mvp-definition.md`, `docs/mvp-package/*`; Issue #215 (11 comments, REST); Control Plane `7a4bcd40` and Runtime `c5e97e87` source and tests; hub `c897266b` `tools/mvp_ingress` and `tools/mvp_env_record`.

## 0. Conclusions in one screen

1. The oracle has SEVEN negative groups (NC1..NC7) and exactly 30 mandatory NC rows; the battery lists 260 entries; 41 unique oracle claims; 7 non-mandatory tests sit outside the 260. All recomputed from the JSON (section 1). Nothing was found missing from the denominators. The documentation around the denominators is stale in six places (section 1.3).
2. No Qualification-owned run of any NC row exists (readiness report section E: 0 of 41 rows; `mvp-chain.yml` and `mvp-acceptance.yml` have 0 recorded runs). Builder-reported results have no retained artifact. No run of oracle v6 or v7 exists in the sources.
3. Single most important blocker for this workstream: three of the seven treatments have a contract-versus-oracle disagreement that only the Architect or the Qualification Owner can settle, and none of them blocks the 25 in-process rows: (a) OS-level process kill (the hub contract lists it as part of the mandatory ambiguous-commit control; the oracle declares it UNQUALIFIED; the cited Architect "Q2" text is not in any hub document read), (b) operation-ledger pruning (named missing in `critical-path.md:59`, a disclosed Control Plane limit, no oracle row), (c) NC4-03 mutations (zero-row placeholder by design).
4. Runnable once the candidate is frozen WITHOUT any owner ruling: 25 of the 30 rows (all in-process rows). NC2-06 runs but its topology needs a Qualification Owner answer (A6). NC4-01..04 are blocked by the host profile (Yama, dedicated identities) and the D3 IPC-mode outcome. Every row additionally depends on the vehicle chosen by Workstream C and on the freeze.
5. Approval revocation: NC1-04 FAILED in the D2/builder history because approval revocation was not terminal; the repair (Runtime PR #144, merged `c5e97e87`) is present at the pinned Runtime and its tests pass in a local dry run. The Control Plane pin `7a4bcd40` needed no change. Not independently requalified.
6. A dry run of `existing` code shows two missing negative cases are cheap to express on the existing harness (pruned ledger; hard process exit at three route B seams). This is information for the owner, not a recommendation to change the oracle in this workstream.

## 1. Denominators recomputed from the JSON

### 1.1 Recomputation (OBSERVATION, python over the committed JSON)

| Quantity | Claimed | Recomputed | Source of the recomputation |
|---|---|---|---|
| Oracle rows (v7) | 42 | 42 | `expectations.proposed.v7.json` `rows` (ENV 1, CHAIN 6, VER 4, NC 30, KL 1) |
| Mandatory oracle rows | 41 | 41 (KL-01 `mandatory:false`) | same |
| Negative groups | seven (readiness F), "six" (builder grouping) | seven: NC1 5, NC2 6, NC3 3, NC4 4, NC5 5, NC6 4, NC7 3 | row id prefixes |
| Mandatory NC rows | 30 | 30 (5+6+3+4+5+4+3) | same |
| Mandatory total | 41 | 41 = 30 NC + 6 CHAIN + 4 VER + 1 ENV | same |
| Battery inventory entries | 260 | 260 (`tests`) | `mandatory-battery.proposed.v1.json` `tests` |
| Battery composition | 41 oracle rows, 6 ruling 4, 6 applicability, 2 verdict-engine, 183 kwflow, 6 AMB, 16 MED | 41 `oracle_row`, 6 `ruling_4`, 6 `applicability`, 2 `verdict_engine_self_check`, 183 `supplementary_nc4_03_predicate`, 6 `supplementary_nc2_06_negative_control`, 16 `supplementary_route_b_mediation` = 260 | `kind` counts |
| Unique oracle claims in the battery | 41 | 41 distinct `row` values among 41 `oracle_row` entries | same |
| Non-mandatory tests outside the 260 | 7 | 7 (`non_mandatory_tests`: KL-01 plus D2C-01..06) | same |
| `pending_rows` | placeholder, no rows | 1 placeholder `NC4-03-origin-rule-negative-mutations`, `rows: []` | same |
| v7 file hash | `0dc17a19...f6b` | matches `sha256sum` of the clone (`0dc17a1984e1c3c153f3cb6e3f7fdd4dad87cdc4414728a20df0f8174e402f6b`) | battery `oracle.unchanged_files_sha256` |
| KW entries vs tests | 183 | 183 collected and passed in a dry run of `test_kwflow.py` (OBSERVATION) | pytest |

### 1.2 Diff v6 to v7 (OBSERVATION, JSON diff)

v6 has 38 rows, 37 mandatory. v7 adds NC4-04, NC7-01, NC7-02, NC7-03 (four rows) and CHANGES one existing row, NC4-03 (adds `launch.py` to `files_scanned`; `ingress_tree_sha256` `ea37100d...` becomes `0c0e2cf6a69f4ce69d4ca39ac7a443890a05b50ba420902e2d346912d369f591`). 37 + 4 = 41 mandatory. Every other v6 row is byte-identical (including NC2-06).

### 1.3 Mismatches to flag (all documentation or label defects; none changes a denominator)

| # | Mismatch | Where | Note |
|---|---|---|---|
| M1 | v7 `status` says "v7 = v6 ... byte-identical in every row, plus the three required negative controls NC7-01..03" and `supersedes.unchanged_rows` says "all 38 rows of v6 are byte-identical in v7"; the actual diff is NC4-03 changed and NC4-04 added in addition to NC7-01..03. `supersedes.composition.row_count` (v7.json:40) does mention NC4-04, so the file contradicts itself. | `expectations.proposed.v7.json` status, `:45`, `:40` | The correction lives only in the battery `oracle.note` (battery.json:15, "Wording correction") and `process/mvp-acceptance/README.md:150`; v7 itself is hash-pinned and must not be edited. |
| M2 | `limitations.nc4_03_source_predicate_v5` (v7.json:1301) says "The *.py tree digest ea37100d... that the pins bind is unchanged" and "exact list of 7 regular files incl. BOUNDARY.md". The v7 NC4-03 row pins `0c0e2cf6...` and 7 `.py` files; `_kwflow.py:102` `EXPECTED_TREE_FILES` has 8 entries (BOUNDARY.md plus 7 `.py`); `NC4-03-PROPOSAL.md` and `suites/mvp-chain/README.md:146` say "exactly 8". | v7.json:1301, `_kwflow.py:98-102` | "7" should read 8 (or 7 `.py` plus BOUNDARY.md). The `ea37100d` digest is the pre-launcher tree (`history/` records it). |
| M3 | `suites/mvp-chain/README.md:58-67` table is titled "Six negative controls", lists NC4 as "NC4-01..03, KL-01", and has no NC4-04 or NC7 row. `README.md:72` still says the ingress is started with `python -m tools.mvp_ingress.server` (superseded; the old entry point is refused, exit 2). `README.md:48` and `:94` are current (42 rows, 41 mandatory). | Qualification `suites/mvp-chain/README.md` | This is the stale Qualification README table. |
| M4 | "Six" versus "seven": hub `critical-path.md:32` ("six mandatory negative controls") and `architect-rulings-2.md` Q12 ("six controls") and Issue #215 WS B use six; the oracle has seven groups. The sixth/seventh gap is NC7 (architect "Q2", unlocated, see A1). Readiness report F already records this. | hub docs | The hub counts are the earlier builder grouping, not a different denominator. |
| M5 | `mandatory-battery.ingress-ambiguity.placeholder.md` says "143 collected tests ... KW-001 to KW-143" and "expectations_in_force is expectations.proposed.v6.json"; the battery has KW-001..183 and names v7. The same note's addendum then updates to v7 and 260. | placeholder note | History is appended, not rewritten; the 143 is stale. |
| M6 | The AMB tests (`test_ingress_ambiguity.py:23,38,...`) read the NC2-06 row from the v6 file (`V6 = ... expectations.proposed.v6.json`), while the battery names v7 in force. NC2-06 is byte-identical in v6 and v7 (OBSERVATION), so no effect today. | `test_ingress_ambiguity.py` | An oracle-version coupling to note if v8 is ever created. |
| M7 | Hub registry record `catalogue-v0.1/scenarios/NC4-0001.json` still embeds the old ingress digest `ea37100d...` (`architect-rulings-3...md` section 6(c)). | hub | Follow-up already recorded by the hub. |
| M8 | NC5-03 title says "rejects a relabelled refusal summary / retained source"; the implemented tamper (`_chain.py:722-737`) drops the last retained reconstruction record from the pack's retained source. The title is broader than the test. | oracle v7.json:965, `_chain.py:728-735` | Row text unchanged here; flagged for the owner. |
| M9 | IPC directory mode: hub text says 2750; Qualification `_ingress.py` (`ipc_dir` ... `0o2751`) and `environment-profile.proposed.v1.json` say 2751. | hub vs Qualification | Governed by Architect decision D3 (2751 approved as a narrowly scoped TEST configuration only if confinement is confirmed; else retain 2750 and report the socket-level negative test BLOCKED). See section 2.6. |

Vehicle-related, for Workstream C (not decided here): `mvp-chain.yml` runs Python 3.12 with `MVP_INGRESS_PROFILE: developer-optout` (supplementary, never acceptance); `mvp-acceptance.yml` runs Python 3.13 with the approved profile on `ubuntu-latest`, whereas decision D2 names GitHub-hosted `ubuntu-24.04`. `ast_digest` pins in NC4-03 are honoured on CPython 3.13 only (`_kwflow.py:105-107`), so NC4-03 cannot PASS on 3.12.

## 2. The thirty mandatory NC rows

### 2.1 Legend

Interface: IP = in-process harness `_chain.Ctx` (Control Plane `BoundedAuthorizationWorkflow`, Runtime `AtomicLocalControlPlaneExecutor` with operation identity on the operation-identity atomic SQLite destination, owner-side raw SQLite for authority rows; no socket) (`_chain.py:94-120`); RS = real Unix-socket ingress (hub `tools/mvp_ingress/launch.py`, `python -I`, client uid 65534); SRC = static source scan, no execution; LIVE = observation on the live ingress process argv.

Needs host = needs the Yama / dedicated-identity / peer-UID host profile. Oracle line = `expectations.proposed.v7.json` line of the row; Battery line = `mandatory-battery.proposed.v1.json` line of the `oracle_row` entry. Harness test for every row: `suites/mvp-chain/test_mvp_chain.py:21-27` `test_row[<ID>]` (parametrised; runs the scenario once, then `verdict.evaluate_row`).

Run class (section 5): R1 runnable once frozen, no owner ruling; R2 runnable, but the result cannot be interpreted without a ruling; BH blocked by the host profile; every row also depends on the vehicle (Workstream C) and the freeze.

Status in the sources for EVERY row: no Qualification-owned run; no recorded verdict; builder-reported results exist only as text in Issue #215 / hub docs without a retained artifact (2026-10-23 unpatched 19 PASS / 5 FAIL / 10 BLOCKED of 34 and patched 31 PASS / 3 BLOCKED; 2026-10-24 oracle v3 at the final tuple 36 PASS / 1 FAIL (NC4-03) of 37; "NC1-04 passed locally at Runtime c5e97e87"). No v6 or v7 run exists. My dry run (section 2.4) is OBSERVATION only.

### 2.2 Table

| Row | Grp | Asserts (oracle v7) | Harness scenario / observation source (file:line) | Battery entries (line) | Interface | Needs host | Run class |
|---|---|---|---|---|---|---|---|
| NC1-01 (v7:293, bat:148) | NC1 | Grant revoked in the authority store after claim issuance and before effect: effect refused, not attempted, zero effects | `nc_revocation` (a) `_chain.py:347-356` | `NC1-01` | IP | no | R1 |
| NC1-02 (v7:315, bat:156) | NC1 | Approval withdrawn before effect: refused, not attempted, zero effects | `nc_revocation` (b) `_chain.py:357-366` | `NC1-02` | IP | no | R1 |
| NC1-03 (v7:337, bat:164) | NC1 | Revocation visible at the CP resolver before claim issuance: claim refused, zero effects | `nc_revocation` (c) `_chain.py:367-374` | `NC1-03` | IP | no | R1 |
| NC1-04 (v7:354, bat:172) | NC1 | Approval revocation is terminal: revoke, attempt reactivation, execute the earlier claim: refused, zero effects | `nc_revocation` (d) `_chain.py:375-385` | `NC1-04` | IP (writer API path only; raw-SQL rewrite is Runtime-test-only, see 3.1) | no | R1 |
| NC1-05 (v7:372, bat:180) | NC1 | Grant revocation is terminal (same shape, grant) | `nc_revocation` (e) `_chain.py:386-396` | `NC1-05` | IP | no | R1 |
| NC2-01 (v7:390, bat:188) | NC2 | `simulate='lost_ack'`: result unknown, never acknowledged, retry not eligible | `nc_ambiguous` (a) `_chain.py:403-416` | `NC2-01`; `R4-01` (`test_ruling4_lost_ack.py:95`) | IP; fault is harness-injected, not a process kill | no | R1 (group-level completeness: A1) |
| NC2-02 (v7:411, bat:196) | NC2 | No blind retry: re-execute same claim denied, not attempted; ledger holds one effect | `_chain.py:417-419` | `NC2-02`; `R4-02` (`:102`), `R4-03` (`:112`) | IP | no | R1 |
| NC2-03 (v7:433, bat:204) | NC2 | `reconcile_claim` establishes the applied effect without a second write | `_chain.py:420-426` | `NC2-03`; `R4-04` (`:120`) | IP | no | R1 |
| NC2-04 (v7:454, bat:212) | NC2 | Reconcile route unavailable (injected `TimeoutError`): still unknown, never retry-eligible, never executed | `nc_ambiguous` second block `_chain.py:436-446` | `NC2-04`; `R4-05` (`:132`) and `R4-06` (`:142`) cover adjacent meaning only | IP | no | R1 |
| NC2-05 (v7:471, bat:220) | NC2 | Unknown outcome is reconstructable: `export_execution_artifacts` and Replay import succeed | `_chain.py:427-434` | `NC2-05` | IP (in-process export/Replay; no restart, no ingress) | no | R1 (continuity scope: 3.7) |
| NC2-06 (v7:487, bat:228) | NC2 | Supported-ingress ambiguity: valid proposal from an unprivileged client over the real ingress (`simulate=None`), owner-side post-commit hook makes ack unavailable, client sees UNKNOWN, a bound fresh request reaches the executor again and is denied, one effect, owner-side reconcile applied | `nc_ingress_ambiguity` `_chain.py:628`, `_ingress_ambiguity.py:96` | `NC2-06`; `AMB-01..06` (bat:1767; `test_ingress_ambiguity.py:23,38,44,56,63,71`; five must-fail negative controls) | RS, but the harness starts a ROOT ingress with `--socket-mode 666` and client uid 65534 (`_ingress_ambiguity.py:100,115-116`); no dedicated identities, no Yama | no | R2 (topology: A6) |
| NC3-01 (v7:699, bat:236) | NC3 | Replaying the consumed claim is refused; one effect | `nc_duplicate` `_chain.py:452-461` | `NC3-01` | IP | no | R1 |
| NC3-02 (v7:717, bat:244) | NC3 | A second claim for the same decision commits no second effect | `_chain.py:462-470` | `NC3-02` | IP | no | R1 |
| NC3-03 (v7:734, bat:252) | NC3 | Renewal with cap 2 for the same operation id refused `operation_already_committed`; one effect | `_chain.py:472-501` | `NC3-03` | IP | no | R1 (group-level completeness: A2) |
| NC4-01 (v7:752, bat:260) | NC4 | Real ingress started; adversarial client is a distinct unprivileged uid (65534, no groups); state tree owner-only before and after | `nc_unmediated` `_chain.py:614-624` -> `_ingress.py:332` (`run`) | `NC4-01` | RS | YES (approved profile: dedicated `mvp-ingress`/`mvp-client`/`mvp-ipc`, Yama >= 1; else the scenario is BLOCKED, `_ingress.py:171-174,366-367`) | BH |
| NC4-02 (v7:780, bat:268) | NC4 | After D1's adversarial inputs (232 bodies), claim/simulate/authority-writer/SQL attempts as the unprivileged uid, no table, ledger or state-tree entry changed; direct file/sqlite/proc access denied by the OS; one legitimate proposal then yields one effect and one consumed claim | same scenario | `NC4-02` | RS | YES | BH |
| NC4-03 (v7:824, bat:276) | NC4 | SOURCE-LEVEL only: no non-literal `**` forwarding in `tools/mvp_ingress` except three pinned sites; six authority fields have a trusted origin at every protected call; every `simulate` keyword is constant None; D1's AST tests pass; tree digest `0c0e2cf6...` | `_kwflow.scan_dir` (`_kwflow.py:543`) called at `_ingress.py:345`; `d1_ast_test_exit_code` runs hub `tests/test_mvp_ingress_boundary.py -k simulate` (`_ingress.py:349`) | `NC4-03`; `KW-001..183` (bat:486-1760; `test_kwflow.py`, 23 test functions) | SRC | Not intrinsically, but COUPLED: it lives in scenario `nc_unmediated`, and a blocked scenario blocks all its rows (`verdict.py:70-72`); see A4 | BH (coupling) and R2 (A3) |
| NC4-04 (v7:897, bat:284) | NC4 | Live ingress argv is `python -I -B ... launch.py` with mandatory `--allow-uid` equal to the one client uid; the old `-m tools.mvp_ingress.server` entry is refused (exit 2) | `_ingress.py:212-232` (`launch_evidence`), `:383` | `NC4-04` | LIVE | coupled as NC4-03 | BH |
| NC5-01 (v7:929, bat:292) | NC5 | Replay refuses a CP record with a substituted journal commitment (differential against an accepted control) | `nc_tamper` `_chain.py:698-715` | `NC5-01` | IP | no | R1 |
| NC5-02 (v7:947, bat:300) | NC5 | Replay refuses an export naming a different effect | `_chain.py:716-721` | `NC5-02` | IP | no | R1 |
| NC5-03 (v7:965, bat:308) | NC5 | Evidence Pack validation rejects a tampered retained source (title says "relabelled refusal summary"; see M8) | `_chain.py:722-737` | `NC5-03` | IP | no | R1 |
| NC5-04 (v7:983, bat:316) | NC5 | Pinned Verifier reports `decision_result_inconsistent`, absent from the untampered record, for an altered decision | `_chain.py:738-746` | `NC5-04` | IP + Verifier subprocess | no | R1 |
| NC5-05 (v7:1000, bat:324) | NC5 | Replay refuses an export whose effect row was edited in the destination after the fact | `_chain.py:747-763` | `NC5-05` | IP | no | R1 |
| NC6-01 (v7:1018, bat:332) | NC6 | Omitting the journal `input` check events from the CP record is refused by Replay (differential) | `nc_custody` `_chain.py:769-783` | `NC6-01` | IP | no | R1 |
| NC6-02 (v7:1036, bat:340) | NC6 | Destination store directory renamed away at effect time: never `executed`, never retry-eligible, zero effects | `_chain.py:788-806` | `NC6-02` | IP | no | R1 |
| NC6-03 (v7:1054, bat:348) | NC6 | Authority store unreadable at claim issuance: claim refused, zero effects | `_chain.py:808-816` | `NC6-03` | IP | no | R1 |
| NC6-04 (v7:1071, bat:356) | NC6 | Replay import without the executor export is not reported complete (differential) | `_chain.py:784-786` | `NC6-04` | IP | no | R1 |
| NC7-01 (v7:1089, bat:364) | NC7 | Unauthorized execution commits no effect (forged claim id; not-authorized decision cannot be provisioned); control commits exactly one | `nc_authority_gates` `_chain.py:507-611` | `NC7-01` | IP | no | R1 |
| NC7-02 (v7:1135, bat:372) | NC7 | Stale or mismatched authority (expired claim; authority advanced after claim; resolver revision change; envelope amount / grant-revision mismatch): refused, zero effects | same | `NC7-02` | IP | no | R1 |
| NC7-03 (v7:1218, bat:380) | NC7 | Missing / invalid-state / expired evidence, and evidence missing at claim issuance, do not permit execution; zero effects | same | `NC7-03` | IP | no | R1 |

Battery entries that attach to the NC groups without being NC rows: `R4-01..06` (`test_ruling4_lost_ack.py`, kind `ruling_4`), `AMB-01..06`, `KW-001..183`, `MED-01..16` (bat:1809; `suites/mvp-d2-route-b/test_inventory_negatives.py`, Runtime `c5e97e87`, invocation `d2-route-b`, route B effect-path mediation; they support the NC4 "unmediated path" claim at executor level, not at the ingress), `VE-1,2` (verdict engine self-checks). The 7 outside the 260 (KL-01, D2C-01..06) are characterisations: `test_REACHABLE_*` tests PASS WHEN A HOLE EXISTS and must never be counted as controls.

Interface summary: 25 rows are in-process only (NC1 x5, NC2-01..05, NC3 x3, NC5 x5, NC6 x4, NC7 x3); NC2-06 and NC4-01/02/04 touch the real socket ingress; NC4-03 is static. INFERENCE: therefore no NC1/NC3/NC5/NC6/NC7 result says anything about the live ingress path, and the ingress persists only an id/digest/outcome ledger, so the chain rows are an in-process equivalent of the supported path (readiness report section D, "INTEGRATION GAP"; Workstream C owns the vehicle consequence).

### 2.3 Row-level status words that must not be over-read

- Oracle semantics (v7 `semantics`): PASS "says nothing beyond the named row". Differential rows (NC5-01/02/03/05, NC6-01/04) are BLOCKED, never PASS, when the untampered control is not accepted (`blocked_if`).
- VER-01/VER-03 read "PASS" for Verifier exit 3 (ABSTAIN) with no refutation; VER-03 requires exit 3 exactly and `v4.ledger.rows-agree-with-attempts` as the only could-not-check id. A VER "PASS" is not Verifier acceptance (readiness report K; architect MVP2 Q5: ABSTAIN is never a PASS).

### 2.4 Dry run performed (OBSERVATION; NOT evidence; no retained artifact; clones cleaned of bytecode)

Environment: this sandbox, root, CPython 3.13.18, pydantic 2.13.5, `kernel.yama.ptrace_scope` ABSENT, component clones at the pins (CP `7a4bcd40`, Runtime `c5e97e87`, Replay `40012b8c`, Pack `7b9511f2`, ODES `1a5e1d30`, Verifier `c0b8ba1f`, Action Manifest `fa170815`, hub `c897266b`), `MVP_RESULTS_DIR` in the scratchpad.

| Dry run | Result |
|---|---|
| `test_mvp_chain.py` + `test_ruling4_lost_ack.py` for ENV, NC1, NC2-01..06, NC3, NC5, NC6, NC7, R4-01..06 | 33 passed (every row PASS, including NC2-06 on a root ingress / socket 666) |
| NC4-01..04 and KL-01, `MVP_INGRESS_PROFILE` unset (approved) | all five BLOCKED: "approved ingress profile ... not named (MVP_INGRESS_USER, MVP_CLIENT_USER, MVP_IPC_GROUP)" |
| NC4-01..04 and KL-01 with `MVP_INGRESS_PROFILE=developer-optout` | all five row-level PASS (the gate classifies opt-out as INCOMPLETE, `mvp_acceptance_gate.py:867-875`: never an acceptance) |
| `test_kwflow.py` (KW-001..183) | 183 passed; `scan_dir` on hub `c897266b`: tree digest `0c0e2cf6...`, 7 files, no violations, 10 real protected calls (>= 8), 3 pinned sites used |
| Runtime `test_crashed_holder.py`, `test_atomic_post_commit_fault_injection.py`, `test_atomic_approval_status_terminality.py`, `test_atomic_approval_terminality_flow.py` (PYTHONPATH with CP) | 44 passed |
| CP `tests/test_known_limits.py`, `tests/test_claim_journal_stage.py` (Verifier on path) | 23 passed, 1 skipped (`test_claim_journal_stage.py:154`, check-id linkage only recorded with operation identity) |
| Scratch probe: prune CP `operations` rows, renew, decide, provision, execute through `_chain.Ctx` | CP decision `authorized` with no reasons; route B execute `denied`, error `operation_already_committed`; effect count 1 |
| Scratch probe: forked child `os._exit(17)` at `after_begin`, `after_effect_insert_before_commit`, `after_commit` through `_chain.Ctx` | pre-commit seams: 0 effects, claim `issued`, reconcile `hold` / `no_durable_effect_for_claim`, re-execute `executed`, 1 effect; `after_commit`: 1 effect, claim `consumed`, reconcile `applied`, `retry_eligible` False, re-execute `denied` ("claim is not usable"), 1 effect |

Side effects disclosed: running the Runtime tests left a `engine/__pycache__` directory in the shared Runtime clone `/tmp/claude-0/rt` (which would make it non-pristine); this worker removed it and re-checked `git status --ignored` clean for `rt` and `cp`. Nine temporary directories `/tmp/mvp-replay-dist-*` and `/tmp/mvp-ruling4-*` created by the suite's own helpers remain because a wildcard delete was refused by the permission classifier; they are harmless scratch and may be removed by the owner.

## 3. The seven named treatments

### 3.1 Approval revocation (NC1-01..05)

History (SOURCE): Issue #215 comment 2026-10-23T15:45Z: "new e2e 33 passed / 1 failed (approval revocation not terminal)"; comment 16:29Z: "approval revocation is non-terminal (D2, FAILS at CP 0a41faa9 and 7a4bcd40)". `architect-rulings-3-and-known-limitations.md` section 1 item 1: a revoke-reactivate-effect sequence "is a genuine safety defect", Option A (repair) authorized subject to the operator gate, Option B (change the mandatory expectation) REJECTED, "NC1-04 remains mandatory", "NC1-04 stays a FAIL until independently requalified".

Is it fixed at the pinned CP/Runtime? The defect was in the Runtime destination, so the fix is at Runtime, not at CP:
- SOURCE: Runtime PR #144 merged as `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f` (addendum 5 of the rulings record): approval revocation terminal per `approval_ref` on `AtomicAuthorityEffectDestination`, production change confined to `engine/local_authority_effect.py`, retained table `authority_approval_revocations_v1` (`local_authority_effect.py:39`), retention at `:506-520`, reactivation refused with `PermissionError("approval is revoked; a new approval is required")` (`:523-544`), effect-time check consults the retained record.
- SOURCE: Runtime tests at the pin: `tests/test_atomic_approval_status_terminality.py` (19 tests, including persistence across a new process `:155`, concurrent connections `:167`, concurrent processes `:212`, `:250` revoke-reactivate-effect-time check still refuses, `:104,:262` a row rewritten to active outside the writer is still refused) and `tests/test_atomic_approval_terminality_flow.py:24` (revoke, reactivate, execute is refused and no effect is committed). OBSERVATION: 44 passed in the dry run (2.4).
- OBSERVATION: Qualification row NC1-04 PASSED in the dry run at the pins. Builder-reported earlier: "NC1-04 passed locally at Runtime c5e97e87" (Issue #215, 2026-10-24).
- INFERENCE: Control Plane `7a4bcd40` needed and received no change for this defect (the F3 PR #83 is the separate claim-journal repair).
- NOT ESTABLISHED: independent requalification; operator-gate approval of the exact patch before merge (addendum 5: "not established from the hub or from PR #144, which has no comments or reviews"); whether the architect reviewed the delta `d291eda7`..`ee1ff55c` (test-only).

What the Qualification row does and does not cover: NC1-04 drives the writer API (`set_approval_status`). The raw-SQL "row rewritten to active outside the writer" case is covered by Runtime's own tests (`:104`, `:262`), not by a Qualification row. Residual, recorded limitations (rulings-3 section 1): policy-writer and evidence-writer reversibility; D2C-05 `test_REACHABLE_authority_writers_can_reactivate_suspended_grant_and_delete_authority_rows` PASSES WHEN A HOLE EXISTS and is non-mandatory. NC1 runs on the in-transaction route B profile, so the C0 check-to-commit race that the contract says to "state plainly or run on the in-transaction profile" is avoided by profile, and the claim wording must still say so. Isolated question: A7.

### 3.2 Ledger pruning (no row)

Facts (SOURCE): Control Plane `7a4bcd40` `tests/test_known_limits.py:170` `test_removed_operation_rows_let_a_revision_2_decision_authorize_but_the_destination_refuses_known_limit`, and `docs/bounded_authorization_effect.md:114-116`: "The operation-identity ledger has no retention rule. If its rows are removed from a run record, a revision-2 decision that would hold as `operation_renewal_unrecorded` is `authorized`; the destination still refuses the second effect (`operation_already_committed`), and the independent verifier rejects the pruned record. A retention rule is a freeze item." `critical-path.md:59` (step 4d) names "operation-ledger pruning" among the missing negative tests owned by "component owners"; `mvp-readiness-reconciliation-2026-10-30.md` F: "has no row". `rg` over the oracle and battery finds no row, no scenario and no entry that removes `operations` rows.

Important scoping fact (SOURCE plus OBSERVATION): the Control Plane known-limit test exercises the CP's own bounded workflow destination (`f.execute`, `f.destination.snapshot()`), not Runtime route B. NC3-03 exercises route B with an INTACT, correctly renewed ledger (`_chain.py:472-501`). Therefore neither the disclosed test nor NC3-03 shows that route B refuses the second effect when the CP ledger is pruned. The scratch probe in 2.4 shows it does (CP `authorized`, route B `denied` / `operation_already_committed`, one effect), using only the existing `_chain.Ctx`.

Does the oracle need a row, or does reuse suffice? INFERENCE: reuse of the disclosed CP test is NOT sufficient for the route B claim because it does not touch the selected route; reuse of NC3-03 is not sufficient because it does not prune. Contract text (hub `qualification-contract.md:13`: "replay and duplicate effect with operation identity") plus Architect Q1 ("deferring an implementation does not waive a safety invariant") point to a row. The decision belongs to the Qualification Owner and the Architect (A2). A CP retention rule is a production change: not authorized (a freeze item) and not proposed.

PROPOSED minimal row text (a proposal to the owner; the oracle is NOT edited here; a new oracle file would be required, "never edit after seeing results"):

> NC3-04 (proposed), scenario `nc_ledger_pruning` (new, executor level, route B, built from the existing `Ctx`): "Operation-ledger pruning cannot yield a second effect: after one committed effect for an operation id, with the operation-identity ledger rows removed from the Control Plane run record and a revision-2 renewal for the same operation id, a claim obtained for the new decision and executed through route B is not `executed` (denied, `operation_already_committed`) and the independent read-only effect count stays 1; the control case with the intact ledger and an unrecorded renewal holds as `operation_renewal_unrecorded`, so a refusal cannot be an artefact of a harness that cannot distinguish the states; the Control Plane decision on the pruned record may be `authorized` (disclosed known limit, recorded and not judged)."

Suggested predicates: `control.status eq executed`, `control.effect_count eq 1`, `unpruned.decision_result eq hold`, `unpruned.reasons contains operation_renewal_unrecorded`, `pruned.rows_removed gte 1`, `pruned.second_execute.status ne executed`, `pruned.second_execute.error eq operation_already_committed`, `pruned.effect_count eq 1`. UNVERIFIED: the unpruned-control behaviour inside the route B `Ctx` (the CP-level behaviour is verified by `test_known_limits.py:170` passing), and whether the pinned Verifier rejects the pruned record as the CP document states (not run).

### 3.3 True OS-level process kill (NC2 group)

Contract text versus oracle (SOURCE):
- Hub `qualification-contract.md:13`: the mandatory negative controls include "ambiguous commit and lost acknowledgment (including an OS-level process kill)".
- Hub `critical-path.md:59` and `delivery-estimate.md:11` carry "OS-kill recovery" as missing-negative-test work (3 / 5 / 8 person-days, "Reproduction at Runtime ec728da6").
- Oracle v7 `limitations.os_level_process_kill` (v7.json:1300): "UNQUALIFIED. True OS-level process kill and crash recovery are not exercised by any row ... Accepted for the 2026-10-31 target under architect ruling Q2 unless the MVP claim promises OS-kill recovery; if it does, this stays UNQUALIFIED/INCOMPLETE." Repeated in the battery placeholder addendum and `suites/mvp-chain/README.md:94`.
- Hub `docs/mvp-package/final-report-template.md:65` lists "True OS-kill recovery qualification" under post-MVP and deferred items.
- The "Q2" cited is NOT located: `architect-rulings.md` Q2 (dependency graph), `architect-rulings-2.md` Q2 (narrow F3 package) and `architect-rulings-3...md` item 2 (NC4-03 predicate) are about other matters; the oracle's own reason text for NC7 also says "Architect ruling Q2". UNVERIFIED: the text of that ruling. The contract says one thing, the oracle and the hub template say another, and the only authority cited for the acceptance cannot be read.

What exists, by seam (SOURCE; all on the pinned tuple unless stated):

| Case | Existing test | Real process death? | In the mandatory battery? |
|---|---|---|---|
| Hard exit before COMMIT on route B (after `BEGIN IMMEDIATE`; after effect insert before COMMIT) | Runtime `tests/test_crashed_holder.py:107` `test_atomic_holder_dying_before_commit_leaves_no_effect_and_no_success`, `_atomic` `:90-103` (`os.fork`, `os._exit(17)`); control `:122` | yes (forked child, no cleanup code runs) | NO. Skipped in Runtime CI at its pinned CP (readiness: Runtime CI skips 33 route B tests; the `needs_cp` guard, `:28`) |
| Death AFTER COMMIT before acknowledgement on route B | Runtime stage `after_commit` exists (`local_authority_effect.py:923`) but `test_crashed_holder.py` parametrises only `after_begin` and `after_effect_insert_before_commit` (`:106`); post-commit is tested by hooks and connection faults only (`test_atomic_post_commit_fault_injection.py`) | no | NO |
| Same post-commit death, real child `os._exit(77)` at `after_commit` and `before_failure_record`, restart, reconcile | Qualification `suites/v1-scenarios/test_scn_c08.py` `test_scn_c08_route_b_real_process_kill_then_restart_reconciles_without_duplicate`, `B_SEAMS` | yes | NO: it runs against the FROZEN F5b bounded reference (`FROZEN_RUNTIME` / `FROZEN_CONTROL_PLANE`), a different tuple, and is a historical scenario (INCONCLUSIVE in the original 75-row result) |
| Journal check events interrupted by a hard exit mid-resolve at decide time | Control Plane `tests/test_runtime_authority.py:79-87` `test_process_dies_mid_resolve_reads_interrupted` (`os._exit(71)`, `recover_interrupted_checks`) | yes | NO |
| Lost acknowledgement | NC2-01..05, `R4-01..06`, NC2-06 | NO: `simulate='lost_ack'`, owner-side post-commit wrapper, an unavailable or unreadable store (v7.json:1300) | yes |

OBSERVATION (2.4 probe): a forked child with `os._exit(17)` at all three seams through the existing `Ctx` reproduces the expected behaviour at the pinned tuple, so a row is expressible without any component change. INFERENCE: `os._exit` skips Python cleanup but the kernel still holds written pages, so it approximates SIGKILL for SQLite durability; an external SIGKILL, a kill during the Verifier or Replay steps, and power loss are not exercised (`_asw_helpers.py:81` already disclaims power loss for the historical route B tests).

Status: the contract-level "including an OS-level process kill" stays MANDATORY and UNQUALIFIED until the owner decides (this worker does not downgrade it). PROPOSED row text for the owner, if the answer to A1 is "mandatory":

> NC2-07 (proposed), scenario `nc_process_kill` (new, executor level, route B): "True process death: a child process executing route B is terminated at each of three seams (after BEGIN, after the effect insert before COMMIT, after COMMIT before acknowledgement); after restart on a fresh destination object, the pre-COMMIT seams leave zero effects, the claim `issued`, reconcile `hold` / `no_durable_effect_for_claim`, never an applied or partial observation, and the claim then executes exactly once; the post-COMMIT seam leaves one effect, the claim `consumed`, reconcile `applied` with `retry_eligible` false, and re-execution is denied with no second effect; effect count never exceeds 1."

### 3.4 NC4-03 mutations

Facts (SOURCE): battery `pending_rows` holds one placeholder, `NC4-03-origin-rule-negative-mutations`, `rows: []`, "become battery rows ONLY after Qualification freezes the corrected NC4-03 predicate. No row is invented here; the gate refuses a placeholder that carries rows" (gate G-14, `mvp_acceptance_gate.py:840`). Rulings-3 item 2: NC4-03 remains mandatory, only the implementation-level predicate may change; "Qualification must independently review and freeze the new predicate before its result is used for acceptance"; a predicate that weakens the guarantee is not acceptable; PR #222 v4 was reviewed CHANGES REQUIRED because it was weaker than v3 (REPORTED). `NC4-03-PROPOSAL.md`: v4 origin rule, v5 additions, "Qualification must independently establish the stated provenance of these three sites" (the pinned sites); builder-stated evidence: 71 negative fixtures, 7 positive, 43 mutants plus v5 evading mutants.

Frozen predicate: v7 NC4-03 is the predicate in force, v5 of `_kwflow.py`, BUILDER-PREPARED, not frozen. OBSERVATION: at hub `c897266b` the scan passes with tree digest `0c0e2cf6...`, 7 files, 3 pinned sites, 10 protected calls; 183 KW tests pass; the D1 AST test exit code needs the hub tests and was not isolated in the dry run beyond the scenario-level run under opt-out (PASS).

What must exist before the battery runs (the NC4-03 mutations may be run only after these; none is performed here):
1. A designated Qualification Owner and independent reviewer (D1: NOT YET INSTANTIATED), who decide whether predicate v5 in `_kwflow.py` at the pinned Qualification commit is the frozen predicate. The v7 hash, `_kwflow.py` and the three pin records (`ast_digest`, `reviewed_ingress_tree_sha256`, provenance) are frozen together; the commitment hash is currently null.
2. A ruling on what "the mutations" are (A3): the existing supplementary KW entries (negative fixtures, 43 ingress mutants, v5 evading mutants) stay supplementary and "do not freeze the predicate" per the battery note; separate mutation ROWS would need a new battery version and a populated `pending_rows` entry, which G-14 refuses today.
3. Correction of the stale documentation (M2, M5, M7) so the frozen text matches the digest in force.
4. An environment on CPython 3.13 (pins fail closed elsewhere) with the hub checkout at the tuple `c897266b` (tree `656b506d...`, `*.py` digest `0c0e2cf6...`); a hub byte change, even a comment, un-pins by design.
5. The NC4 scenario coupling (A4) understood: NC4-03 cannot report PASS if the host-dependent part of `nc_unmediated` is BLOCKED.

### 3.5 Peer authorization (NC4 and the host profile)

SOURCE, ingress behaviour: `tools/mvp_ingress/server.py:31` `_peer_uid` via `SO_PEERCRED`; `serve` checks the peer uid against an explicit non-empty `--allow-uid` allowlist before reading any byte; unreadable credentials or a uid outside the list return `refused` / `PEER_NOT_ALLOWED` (`:160-176`); no default, no implicit ingress uid, no wildcard (`:148-155`). The oracle's known limit lists "IPC peer authentication default allowed_uids=None" as NOT fixable here (v7.json:1302); the launcher now mandates `--allow-uid`.

The three classes on the real ingress, and where each is covered:

| Class | Expected | Qualification oracle row | Other coverage |
|---|---|---|---|
| Allowlisted client (uid 65534 = `--allow-uid`) | served | NC4-02 (legitimate proposal after the attack: one effect), NC4-04 (`allow_uid_equals_client`), NC2-06 | `qualification.client_socket_reachable` in the environment record |
| Group member that is NOT on the allowlist | `PEER_NOT_ALLOWED` | NONE | hub `tests/test_mvp_ingress_peer_allowlist.py` (injected credentials, unit level, builder-owned); ARCHITECT-STATED: the supplementary 2751 capture reports a non-allowlisted group member returned `PEER_NOT_ALLOWED` and the original synthetic ingress positive client reached an application decision (`DECISION_HELD`, `approval_operation_binding_mismatch`, which is not an effect). The profile itself makes the dedicated group exactly ingress plus client, so this class does not exist in the approved topology |
| Outsider (neither ingress, client nor group member, uid 65533) | OS refusal at connect (`EACCES`) | NONE (an oracle row); it is a required check of the environment record, `qualification.outsider_denied_socket` (`environment-profile.proposed.v1.json:49`), gated by G-11 | ARCHITECT-STATED: 2750 capture 31 PASS / 1 BLOCKED / 0 FAIL, the sole block being `qualification.outsider_denied_socket` because mode 2750 removes outsider search permission, so the denial is not socket-specific; 2751 supplementary capture 31 PASS / 0 BLOCKED / 0 FAIL; both `profile_supported=true`. The harness already provisions 2751 (`_ingress.py:377-384`, mode `0o2751`) |

Relation to the host profile (INFERENCE): NC4-01/02/04 only run, and only count, on a host that satisfies the approved profile (dedicated non-root ingress uid, dedicated group, separate IPC directory, Yama `ptrace_scope >= 1`, Python 3.13); otherwise they are BLOCKED (never a weaker substitute, `_ingress.py:185-190`) and the gate returns INCOMPLETE. Developer opt-out produces row-level PASS that the gate refuses to count (`mvp_acceptance_gate.py:867-875`). Peer authorization beyond the allowlisted client is host-level evidence (G-11) plus hub unit tests; no Qualification-owned NC row asserts the group-member refusal (A5). D3 (ARCHITECT-STATED): 2751 is approved as a narrowly scoped TEST configuration only if confinement shows no socket access, state contents or unauthorized metadata through the extra other-traverse bit; socket stays 0660 with peer-UID allowlisting; if confinement cannot be established, retain 2750 and report the socket-level negative test BLOCKED. Workstream C/ipc-2751-security-review.md owns that confirmation; this worker does not decide it.

### 3.6 Journal recovery

Journal mode here is the Control Plane claim and check journal in `runtime_authority_profile` mode with operation identity (route B configuration). SOURCE: F3 (Control Plane PR #83, pin `7a4bcd40`) records a distinct, bound claim-stage `stage` / `check_ref` at claim provisioning (`tests/test_claim_journal_stage.py:1-5,71,93,112-152`: distinct and bound, no journal reuse and no refutation with the pinned Verifier, the pre-patch call pattern refuted as `journal_check_reused`, reused check reference refuted, missing stage refused, incorrect linkage detected; the file is `importorskip("cognous_verify.engine")` so it is skipped in CP CI without the Verifier, readiness E). `journal_check_reused` was "a confirmed (per reported reproduction) evidence-integrity and release-assurance defect; not by itself unauthorized execution" (MVP2 Q1). OBSERVATION: the CP journal tests pass in the dry run with the Verifier on the path (23 passed, 1 skipped).

Qualification coverage of the journal: VER-02 (no `journal_check_reused` finding), NC6-01 (omitting the `input` check events from the CP record is refused by Replay), CHAIN-01/02 (decide, claim in journal mode with operation identity). Recovery after a crash:
- CP: `tests/test_runtime_authority.py:79-87` (hard exit during resolve; `recover_interrupted_checks`; check event becomes `interrupted`, `check_interrupted`, no decision or attempt) is the only test of journal recovery after a real process death; it is CP-owned and is not in the Qualification battery.
- Runtime destination: pre-COMMIT hard exit leaves no effect and an `issued` claim (`test_crashed_holder.py:107`), reconcile reports `hold` / `no_durable_effect_for_claim`; not in the battery.
- No Qualification row restarts the CP record store after a crash or imports the post-crash record into Replay / Evidence Pack. INFERENCE: journal recovery after crash is covered at component level only and is part of the A1 question; with the Replay F3 state "closed" and the standing holds, this worker proposes nothing at the component level.

### 3.7 Evidence continuity (NC2-05, NC5, NC6 versus the chain)

The chain is: CP record, executor export (`export_execution_artifacts`), Replay import (`import_bounded_workflow`), Evidence Pack (`import_manifest_reconstruction` plus `validate_evidence_pack`), and the pinned Verifier on the raw record in two runs (A without a ledger; B with a harness-derived ledger from the SQLite `effects` table) (`suites/mvp-chain/README.md`, "What runs"; `_chain.py:276-341`). SOURCE and OBSERVATION: the tamper and custody rows (NC5-01..05, NC6-01, NC6-04) are differential against an accepted control; if Replay does not accept the untampered chain the rows are BLOCKED, never PASS. NC2-05 shows the unknown outcome exports and imports in-process.

Verifier ABSTAIN is not a PASS. SOURCE: gate expectations v1 assert run B exit 3, `overall: abstain`, 27 confirmed / 1 could-not-check / 0 refuted, V4 could-not-check id `v4.ledger.rows-agree-with-attempts`, run A exit 3 with 7 could-not-check ids all `input_absent` (these figures are proposed, bind to the $10 fixture and must be regenerated at the exact tuple; the earlier 27/28 numbers were superseded for the $50 fixture). Rulings MVP2 Q5 conditionally accepts ABSTAIN under four conditions (missing attempt layer is an inherent declared route property; remaining applicable checks pass; the abstention is attributable to that comparison; no mandatory condition depends on the missing layer); ABSTAIN "is never a PASS". Oracle VER-01 accepts exit 0 or 3 without refutation; VER-03 is eq exit 3 with the single could-not-check id. OBSERVATION: `chain.verifier.A` exit 3 with seven `input_absent` ids reproduces in the dry run.

Gaps (SOURCE): (i) `critical-path.md:59` names "missing-custody through the verifier" as a missing negative test; the NC6 rows exercise custody loss through Replay and the destination, and NC5-04 exercises the Verifier on a tampered decision, but no row feeds the Verifier a record with missing custody (for example journal events omitted) and requires a non-ACCEPT, non-crash disposition (A8). (ii) The chain rows run in-process; the live ingress persists only id, digest and outcome, so Replay / Pack / Verifier inputs are not produced by the live ingress path (readiness D, "INTEGRATION GAP", UNVERIFIED end to end on the merged tuple). (iii) NC5-03 title versus implementation (M8). (iv) A pass of the reconstruction path cannot erase a Verifier failure (MVP2 Q7); the report must keep the two paths separate.

## 4. Contractual ambiguities (each isolated as one question)

For every item: Question; Consequences of each answer; Deciding authority; Unrelated rows that proceed regardless. In all items no mandatory row is deleted, downgraded or deferred by this document; the default until the authority answers is that the row or claim stays MANDATORY and any uncovered part stays UNQUALIFIED / INCOMPLETE.

### A1. Is a true OS-level process kill part of the mandatory ambiguous-commit claim?
Question: Does the Qualification Contract's "ambiguous commit and lost acknowledgment (including an OS-level process kill)" (`qualification-contract.md:13`) bind the MVP claim, or is OS-kill recovery an accepted limitation as the oracle (v7.json:1300) and the hub final-report template (`final-report-template.md:65`) state, and what exactly is the Architect "Q2" text that the oracle cites?
- Answer YES (mandatory): the NC2 group is incomplete (INCOMPLETE) until a new oracle version carries a kill row (proposed text in 3.3), a new battery version and a new commitment are produced and frozen; the harness cost is small (OBSERVATION: existing `Ctx` plus `os.fork`); no component change; the Oct 31 candidate freeze is unaffected, acceptance timing is. The claim wording may then say OS-process-death recovery was exercised at the three route B seams (not power loss).
- Answer NO (accepted limitation): the oracle limitation stays; the claim wording must state in terms "true OS-level process kill and crash recovery are not qualified; synthetic fault injection only"; the hub contract text at `:13` must be amended by the Architect, not silently reinterpreted; the row set stays 30 and the NC2 group verdict is labelled with the limitation.
- Sub-question A1b: if YES, must it include restart-and-reconstruct (journal recovery, 3.6) or only destination behaviour after restart?
Deciding authority: Architect (author of "Q2"; contract owner) with the operator for claim wording; the Qualification Owner freezes the resulting oracle. Unrelated rows that proceed: all 30 rows run and report; only the NC2 group-level conclusion waits.

### A2. Is the operation-ledger pruning limit covered by NC3-03, or does it need its own mandatory row?
Question: With the Control Plane operation-identity ledger rows removed (a disclosed Control Plane limit, `bounded_authorization_effect.md:114`, `test_known_limits.py:170`), must the Qualification oracle assert on route B that the second effect is still refused?
- YES: add a row (proposed text 3.2) in a new oracle version; NC3 becomes four rows (the mandatory NC count would then be 31 in that version; denominators must be restated, never silently changed); small harness addition; the CP retention rule remains an unauthorized production change and stays out of scope.
- NO (reuse): the owner must record why a CP-workflow test and an intact-ledger route B test are accepted for the route B claim; the pruning limit then appears only as a disclosed known limit with the destination refusal described as route B behaviour that was not independently exercised.
Deciding authority: Qualification Owner (oracle) with the Architect (Q1: deferral does not waive an invariant). Unrelated rows proceed: all 30.

### A3. What counts as the "NC4-03 mutations", and is predicate v5 the frozen predicate?
Question: Do the existing supplementary KW-001..183 entries (negative fixtures and mutants) satisfy the Architect's requirement of origin-rule negative mutations, or are separate battery rows required, and does the Qualification Owner freeze predicate v5 (`_kwflow.py`, v7 NC4-03, three pinned sites) as written?
- KW entries suffice: the placeholder is closed by an explicit statement; no new rows; the three pinned-site provenance records still need independent establishment (NC4-03-PROPOSAL "Pins").
- Separate rows: a new battery version populates `pending_rows`; G-14 must be satisfied in the same freeze; frozen text must be reconciled first (M2, M5).
- Predicate not accepted as written: NC4-03 stays FAIL / unfrozen at v7; a new file with a recorded reason is required (no edit of v7).
Deciding authority: Qualification Owner and independent reviewer (D1 roles not instantiated); the Architect where the protected guarantee would change (rulings-3 item 2). Unrelated rows proceed: the 25 in-process rows and NC2-06.

### A4. Should the source-level NC4-03 verdict depend on the host-dependent part of `nc_unmediated`?
Question: As coded, NC4-03 and NC4-04 (and non-mandatory KL-01) share the scenario `nc_unmediated`; if the scenario is blocked (no approved identities, Yama absent, not root), `verdict.py:70-72` marks every row of the scenario BLOCKED even though the source-level observations were recorded first (`_ingress.py:345-349`). Is that coupling intended?
- Intended: NC4-03 PASS exists only with a qualifying host; consistent with "NC4 cannot exceed INCOMPLETE without a Yama-capable host or an approved successor profile" (readiness F). No action.
- Not intended: a Qualification-owned harness change (not an oracle edit) could record the source rows separately; the verdict of NC4-03 would then be independent of the host.
Deciding authority: Qualification Owner. Unrelated rows proceed: all.

### A5. Is peer authorization beyond the allowlisted client a mandatory negative case?
Question: Is the refusal of a non-allowlisted socket-group member (`PEER_NOT_ALLOWED`) and of an outsider (OS refusal) required as mandatory NC4-level oracle evidence, or is it satisfied by the host environment record (G-11 `qualification.outsider_denied_socket`, `ipc.peer_credentials`) plus hub unit tests?
- Mandatory in the oracle: a new NC4 row and a harness addition (a second group-member uid that is not on the allowlist; in the approved profile the group is exactly ingress plus client, so the profile text must also say how the group-member case is staged); more host dependence.
- Covered by G-11: record this explicitly, because today the group-member case appears in no required check id (`environment-profile.proposed.v1.json:30-50`) and exists only as an ARCHITECT-STATED supplementary capture and hub unit tests.
- Sub-question A5b (Architect, D3): 2750 versus 2751 as the governing semantics; hub documents say 2750, Qualification provisions 2751; the supplementary PASS is not automatic normative acceptance.
Deciding authority: Architect (D3, profile semantics); Qualification Owner (row). Unrelated rows proceed: the 25 in-process rows and NC2-06.

### A6. Must NC2-06 run under the approved ingress identities?
Question: NC2-06 starts a ROOT ingress with `--socket-mode 666` and client uid 65534 (`_ingress_ambiguity.py:100,115-116`), not the dedicated-identity topology of NC4; is that acceptable for a mandatory "supported ingress" row?
- Acceptable: the row is labelled SUPPORTED INGRESS with non-approved topology; it runs now on any root Linux host and does not need Yama.
- Not acceptable: a Qualification-owned harness change to use the NC4 identities, making NC2-06 host-dependent (and BLOCKED without the profile).
Deciding authority: Qualification Owner. Unrelated rows proceed: all others.

### A7. Is Runtime-owned evidence for the raw-SQL reactivation case sufficient for NC1-04?
Question: NC1-04 uses the writer API only; the "row rewritten to active outside the writer" case is tested in Runtime (`test_atomic_approval_status_terminality.py:104,:262`). Does the mandatory claim need a Qualification-owned row for it?
- Yes: new row or sub-assertion; in tension with the recorded residual trust-boundary limitation (a holder of the destination credential is outside the boundary, `mvp-definition.md`), so the row would have to be scoped to the retained-revocation record, not to the credential holder.
- No: cite the Runtime tests as component evidence reusable only if Qualification confirms the identity applies (`qualification-contract.md`, "Pre-existing coverage").
Deciding authority: Qualification Owner; Architect for the scope. Unrelated rows proceed: all.

### A8. Does "missing custody through the verifier" require a Verifier-based custody row?
Question: Must a mandatory NC6 row show the pinned Verifier handling a record with missing custody (named as a missing negative test, `critical-path.md:59`), in addition to the Replay-based NC6-01/04 and the destination-based NC6-02/03?
- Yes: new row (Verifier on a record with the journal events omitted: no crash, no ACCEPT, a named could-not-check or refutation); result must keep ABSTAIN distinct from PASS.
- No: record that custody loss is evidenced through Replay and the destination only, and that the Verifier's behaviour on missing custody is exercised only by run A (`input_absent`).
Deciding authority: Qualification Owner. Unrelated rows proceed: all 30.

### A9. How are VER rows worded in reports?
Question: VER-01/VER-03 return the status "PASS" for a Verifier ABSTAIN; which wording does the acceptance report use so that no reader takes it as Verifier acceptance (readiness K)?
- Wording change only; no row change. Deciding authority: Qualification Owner and the report template owner. Unrelated: everything. (Listed for completeness; it is not an NC row.)

## 5. Runnable now versus ruling versus vehicle

"Runnable" means: a row can produce a row-level verdict on the frozen candidate with the existing, unchanged suite, once (1) the candidate is frozen (tuple, oracle v7, battery, commitment hash supplied outside the checkout, G-12), (2) CPython 3.13 and pydantic >= 2.12 are present, and (3) a Qualification-owned vehicle executes the suite (Workstream C decides; this document only states the dependency).

### 5.1 Runnable once frozen with NO owner ruling needed (25 of 30 rows)
NC1-01, NC1-02, NC1-03, NC1-04, NC1-05; NC2-01, NC2-02, NC2-03, NC2-04, NC2-05; NC3-01, NC3-02, NC3-03; NC5-01, NC5-02, NC5-03, NC5-04, NC5-05; NC6-01, NC6-02, NC6-03, NC6-04; NC7-01, NC7-02, NC7-03.
Battery entries (all runnable without a ruling; no root and no Yama needed for the in-process ones): the 25 oracle_row entries above, `R4-01..06`, `VE-pass_fail_and_missing_is_fail`, `VE-not_run_blocked_not_applicable`, and `MED-01..16` (invocation `d2-route-b`, needs `D2_CONTROL_PLANE_DIR`, `D2_RUNTIME_DIR`, `D2_CONTROL_PLANE_PIN`). The group-level meaning of NC2 and NC3 still depends on A1 and A2, but these rows themselves need no ruling to run and report.

### 5.2 Runnable, but the result cannot be relied on without a ruling
- NC2-06 and `AMB-01..06`: runnable on any root Linux host (no Yama, no dedicated identities); topology question A6 (6 battery entries plus the row).
- NC4-03 and `KW-001..183`: the 183 KW entries and the row's predicates run on any CPython 3.13 host with the hub checkout; their meaning depends on A3 (what freezes) and A4 (coupling). KW entries are runnable without a ruling in the sense of executing; their weight as "mutation" evidence needs A3.

### 5.3 Blocked by the host profile (the vehicle must provide it)
NC4-01, NC4-02, NC4-04, and NC4-03 through the scenario coupling: need the approved profile on the vehicle (dedicated non-root `mvp-ingress` and `mvp-client`, group `mvp-ipc`, separate IPC directory, Yama `ptrace_scope >= 1`, root to drop privileges, Python 3.13) and the D3 outcome for 2750 versus 2751 (ARCHITECT-STATED captures: 2750 31 PASS / 1 BLOCKED / 0 FAIL, 2751 31 PASS / 0 BLOCKED / 0 FAIL, both `profile_supported=true`; the harness provisions 2751). Without it these rows are BLOCKED and the gate returns INCOMPLETE; they are never replaced by the developer opt-out.

### 5.4 Needs a ruling and possibly a new oracle / battery version before the group can be called complete
- OS-level process kill (A1): new row family; blocks nothing else.
- Ledger pruning (A2): new row; blocks nothing else.
- NC4-03 mutation rows (A3) and the peer-authorization row (A5): decisions first; any row addition is a new file, never an edit of v7, and G-14/G-03 must be re-satisfied.
- Verifier-based custody (A8) and raw-SQL revocation (A7).

### 5.5 Vehicle dependency (Workstream C decides)
Every row depends on a Qualification-owned execution that does not exist (0 runs of `mvp-chain.yml` and `mvp-acceptance.yml`). Facts that C must carry: `mvp-chain.yml` is Python 3.12 + developer opt-out and is supplementary only; `mvp-acceptance.yml` is Python 3.13 with the approved profile but `ubuntu-latest` (decision D2 names ubuntu-24.04); the in-process chain is an equivalent of, not the live, supported path (readiness D); a hub change to make the live ingress emit Replay / Pack / Verifier inputs would change the tree `656b506d` and the candidate identity and needs separate authorization (not proposed). Independence: a same-lineage run, including this worker's dry run, is not certification (D1).

## 6. Not claimed / UNVERIFIED

- The text of the Architect "Q2" ruling (oracle and battery citations) was not located in any document read.
- No Qualification verdict exists for any row; all statuses in section 2 are source statements or OBSERVATIONS from an uncontrolled dry run.
- QGATE-03 artifact `13023553992` and its 366/366 checksums, the 31/1/0 and 31/0/0 numbers, the `DECISION_HELD` / `PEER_NOT_ALLOWED` / `EACCES` outcomes were not read by this worker (ARCHITECT-STATED).
- Whether the pinned Verifier rejects a pruned ledger record (CP document statement) was not run.
- Behaviour of the pruned-ledger control (intact ledger, unrecorded renewal, `operation_renewal_unrecorded`) inside the route B `Ctx` was not run.
- NC4 rows were not run under the approved profile (no Yama in this sandbox); the opt-out PASS is not a result.
- Whether an external SIGKILL, rather than `os._exit`, yields identical SQLite durability behaviour is INFERENCE.
- Independent organizational review of the three pinned NC4-03 sites; independent requalification of NC1-04; operator-gate approval of the Runtime PR #144 patch.
- Python 3.12 and 3.11 are unqualified; the ODES exporter defect and Exchange / route C are excluded from the MVP and are not part of any NC row.

Nothing here claims qualification, security clearance, certification or production readiness. Release, publication and production remain on HOLD.
