# Worker C report: mandatory-row coverage crosswalk (OCS-MVP-FINAL)

Read-only. Written only under /tmp/claude-0/final/C/. As-of: BEFORE the results of run 41165743705 (qgate-05/run-1 at fa12c699, dispatched 2026-10-31T03:45:36Z). Branch qgate-05/evidence-run-1 NOT read; no result guessed. Labels: OBSERVED (I read/computed it), ARCHITECT-STATED, INFERENCE, REPORTED (text in a doc, no retained artifact). Same-lineage AI work; no independence, Q7, certification, Tier 1, release or production claim. Standing holds unchanged.

## 1. Bottom line

- OBSERVED: **0 of 47 mandatory rows are PROVEN, 0 FAILED, 0 BLOCKED, 0 NOT APPLICABLE; all 47 are UNTESTED** at the frozen candidate. No Qualification-owned execution of oracle v8 / battery v2 exists for fa12c699 (no results/mvp-* tree on Qualification main b6142518 or in the frozen view; the only acceptance-workflow run, 41165743705, is in flight with no conclusion in the run list). Every earlier per-row result is a builder report or local dry run, at other pins or an older oracle, and is not carried over.
- Consequence: the **smallest genuinely untested mandatory set is the whole set of 47**. There is no subset that can be treated as already proven. All 47 oracle rows live in one workflow group, `mvp-chain` (root pytest, `suites/mvp-chain/test_mvp_chain.py::test_row[<ID>]`); the `d2-route-b` (16 MED + 6 non-mandatory D2C) and `applicability` (AP01-AP05, 6 entries) groups hold no oracle row.
- Denominators recomputed from the JSON equal the accepted 48 / 47 / 36 / 435 (section 2).

## 2. Recomputed denominators (OBSERVED, script /tmp/claude-0/final/C/_build.py over the files in /home/claude/view-e2/qual)

Files: oracle `process/mvp-chain/expectations.proposed.v8.json` sha256 498efc12...f359c, battery `process/mvp-acceptance/mandatory-battery.proposed.v2.json` sha256 61228fad...d262, commitment v5 `process/mvp-acceptance/candidate-commitment.proposed.v5.json` sha256 81443086...ca49 (216 files). The three hashes match the commitment/custody record values.

| quantity | recomputed | accepted | match |
|---|---|---|---|
| oracle rows | 48 | 48 | yes |
| mandatory rows | 47 (only KL-01 non-mandatory) | 47 | yes |
| mandatory NC rows | 36 in 7 groups | 36 | yes |
| battery entries | 435 | 435 | yes |

Mandatory rows by group: ENV 1, CHAIN 6, VER 4, NC1 5, NC2 7, NC3 4, NC4 8, NC5 5, NC6 4, NC7 3 (NC1 5, NC2 7, NC3 4, NC4 8, NC5 5, NC6 4, NC7 3).

Battery entries by kind: oracle_row 47, verdict_engine_self_check 2, ruling_4 6, applicability 6, supplementary_nc4_03_predicate 183, supplementary_nc2_06_negative_control 6, supplementary_route_b_mediation 16, supplementary_nc2_07_process_kill 18, supplementary_nc3_04_ledger_pruning 8, supplementary_nc4_03_mutation_set 135, supplementary_nc4_03_host_subcases 8 (sum 435).
By invocation: mvp-chain 413, d2-route-b 16, applicability 6.
Unique claims (distinct `row` among entries): 47; oracle_row entries 47 cover exactly the 47 mandatory rows; non-mandatory tests 7 (KL-01, D2C-01, D2C-02, D2C-03, D2C-04, D2C-05, D2C-06); pending_rows 0; declared_not_applicable 0; battery ids and (file,test) nodes are each unique (435). The battery's own `counts` block agrees.

## 3. Evidence inventory bound to fa12c699 / commitment v5 (what exists, and why none of it proves a row)

| id | item | status as evidence |
|---|---|---|
| E1 | Commitment v5 (216 files) and custody record on hub branch qgate-05/custody-1 (recorded 2026-10-31T03:36:01Z; qualification_revision fa12c699, commitment sha 81443086...) | OBSERVED. Binds the identity of the candidate. Not a row result. |
| E2 | PR #256 / push checks at fa12c699: Catalog validation success, Cross-component migration integrity success, CodeQL success, dashboard build cancelled (read from /tmp/claude-0/final/A/allruns.tsv, worker A's list; not re-fetched by me) | Green PR check: NOT proof of any acceptance row. |
| E3 | Owner review 2 (APPROVE, fa12c699) and adversarial pre-execution review 2 (no blocking findings): local reruns (354 passed for kill/pruning/mutation/host/kwflow/verdict; gate tests 214-215 passed; mvp_chain+verdict_engine under developer-opt-out 46 passed, 4 failed = NC4-03a..d BLOCKED as expected) | Local dry runs: NOT evidence. Explicitly state the four host rows are exercised only in the hosted run. |
| E4 | Acceptance run 41165743705 (workflow mvp-acceptance.yml) | IN FLIGHT, no conclusion known. Not read. |
| E5 | Builder-reported history (Issue #215 / hub docs): 2026-10-23 unpatched 19 PASS/5 FAIL/10 BLOCKED of 34, patched 31 PASS/3 BLOCKED; 2026-10-24 oracle v3 at final tuple 36 PASS/1 FAIL (NC4-03) of 37 | REPORTED, no retained artifact, older oracle, different rows. Not carried over. |
| E6 | QGATE-02 hosted run 41125818207 (FAIL, filesystem.no_acl_entries on /opt chain) and QGATE-03 hosted run 41153041401 (capture overall=BLOCKED, verdict INCONCLUSIVE) | Different pins/profile; artifacts unreadable (per-check results UNREAD). Not proof for any NC4 row. Never executed by this candidate. |
| E7 | Component-own CI/tests at tuple pins (e.g. Runtime c5e97e87 test_atomic_approval_status_terminality) | Supporting context only; Qualification rows are owned by the chain run. |

`existing_evidence_at_frozen_candidate` is therefore an empty list for every row in crosswalk.json.

## 4. Classification summary

PROVEN 0 / UNTESTED 47 / FAILED 0 / BLOCKED 0 / NOT APPLICABLE UNDER CONTRACT 0. Notes on boundary calls:
- **NC4-03a..d (and NC4-01, NC4-02, NC4-04, NC2-06)** are classified UNTESTED, not BLOCKED, because BLOCKED is a recorded in-run outcome and none exists at fa12c699; each carries a qualifier saying it can only be PROVEN by the hosted run on the ratified bounded 2751 profile and that any non-hosted result is BLOCKED by design. If you prefer the label BLOCKED-until-hosted for the four subcases, that is a presentation choice; the evidence state is identical.
- **NC4-03** (not the a..d subcases) is, per oracle v8, DETERMINISTIC and host-independent (scenario nc4_03_det). It is not in the host-profile set although the brief lists it with NC4-01..04. It depends on the CPython 3.13 minor for ast-digest pins (fail-closed off the recorded interpreter).
- **KL-01** is non-mandatory (excluded from the 47); it shares scenario nc_unmediated with NC4-01/02/04 and cannot change the verdict.
- **NOT APPLICABLE UNDER CONTRACT: none.** battery.declared_not_applicable is empty; the only row with a not_applicable_if is VER-03 (exit_code 0). The pytest node accepts NOT APPLICABLE as green, but the battery rule says any NA not listed under declared_not_applicable is INCOMPLETE at the gate. So an NA on VER-03 is not a pass at the gate (INFERENCE from the rule text, OBSERVED rule text).
- No row can be FAILED today: there is no observation at the frozen candidate that contradicts a predicate.

## 5. Known historical failures preserved (not relabelled, not carried over)

- **NC1-04**: (1) D2-era approval revocation non-terminal FAIL (Issue #215 2026-10-23T15:45Z and 16:29Z, at CP 0a41faa9 and 7a4bcd40; architect-rulings-3 item 1, 'NC1-04 stays a FAIL until independently requalified', changing the expectation REJECTED); (2) Runtime repair PR #144 merged as **c5e97e87**, which is the frozen Runtime pin; local passes at c5e97e87 are REPORTED / dry-run only. By evidence at the frozen candidate: UNTESTED. The row covers the writer API; the raw-SQL reactivation case is Runtime-test-only.
- **NC4-03**: builder-reported FAIL at oracle v3 / final tuple on 2026-10-24 (qgate-04 negative-case-reconciliation), before the v5 predicate, launch.py scan and the v8 mutation set. Not carried over; row is UNTESTED.
- **NC4-01/02/03a..d**: QGATE-02 hosted FAIL (ACL on /opt chain) and QGATE-03 hosted BLOCKED/INCONCLUSIVE are history at other pins and profile; QGATE-05 uses /var/lib/qgate05-ocs, never run on a hosted runner before (F-06).
- ODES: hub status lists 4 historical failures and an export_cognous_stack_package defect on route B recovery bundles (REPORTED, 2026-10-23, at older ODES pins). Watch item only for NC2-05/CHAIN rows that import via Replay; whether it applies at ODES 1a5e1d30 is UNVERIFIED.

## 6. VER rows and the ABSTAIN rule (exact oracle wording)

- **VER-01** (Pinned Verifier on the raw CP record + proposal + manifest does not crash, does not refute (exit 0 accept or 3 abstain only)). Predicates: chain.verifier.A.crashed false; chain.verifier.A.exit_code in [0, 3]; chain.verifier.A.refuted_check_ids empty. A PASS on exit 3 is a PASS of this row only, not Verifier acceptance.
- **VER-02** (No Verifier finding with code journal_check_reused (the documented claim-stage journal refutation)). Predicates: chain.verifier.A.finding_codes not_contains "journal_check_reused". Independent of exit code; PASSes on an exit-3 ABSTAIN run; not Verifier acceptance.
- **VER-03** (Verifier run B (record + proposal + manifest + harness-derived ledger): any abstention is attributable only to v4.ledger.rows-agree-with-attempts (route B has no attempt layer); no check refuted). Predicates: chain.verifier.B.crashed false; chain.verifier.B.exit_code eq 3; chain.verifier.B.could_not_check_check_ids eq ["v4.ledger.rows-agree-with-attempts"]; chain.verifier.B.refuted_check_ids empty. exit_code must be exactly 3 with that single could-not-check id; NOT APPLICABLE if exit 0, which is INCOMPLETE at the gate because declared_not_applicable is empty.
- **VER-04** (Verifier exit code, report bytes (hash) and module path retained for the run). Predicates: chain.verifier.A.report_sha256 nonempty; chain.verifier.A.module_path_under_pin true. Retention row; PASSes on an ABSTAIN run.

So: VER-01, VER-02 and VER-04 can PASS on an exit-3 ABSTAIN; VER-03 can only PASS on an exit-3 ABSTAIN whose sole could-not-check id is v4.ledger.rows-agree-with-attempts. When results arrive, report these four as `PASS (Verifier ABSTAIN, exit 3; not Verifier acceptance)` and keep ABSTAIN distinct from PASS. Gate-expectation figures (run B 27 confirmed / 1 could-not-check / 0 refuted; run A 7 could-not-check, all input_absent) are PROPOSED values in gate-expectations, not observations.

## 7. Mapping the in-flight run to the 47 rows

All rows run in workflow group `mvp-chain` (`sudo -E ... python -m pytest ... suites/mvp-chain/test_mvp_chain.py ...`, junit-mvp-chain.xml, pytest-exit-mvp-chain.txt, collected-mvp-chain.txt). One scenario per observation key; **a harness exception in a scenario records the whole scenario BLOCKED** (run_scenario in _chain.py), so rows sharing a scenario fail or block together. Expected evidence files (from workflow/handoff, not yet seen): results/mvp-acceptance/mvp-chain/{results,observations}.json, gate-verdict.json, gate.rc, summary.json/md, run-identity.json, host-evidence/*, appended under runs/run-<id>-attempt-1/ on qgate-05/evidence-run-1.

| scenario (observation key) | rows | host/ingress dependent | shared-fate / cascade | supplementary entries to read alongside |
|---|---|---|---|---|
| env | ENV-01 | no | ENV-01 independent of scenarios | - |
| chain | CHAIN-01, CHAIN-02, CHAIN-03, CHAIN-04, CHAIN-05, CHAIN-06, VER-01, VER-02, VER-03, VER-04 | no | one scenario: CHAIN-05 blocked if CHAIN-04 fails; CHAIN-06 blocked if replay fails; VER-01..04 read chain.verifier.* | - |
| nc_revocation | NC1-01, NC1-02, NC1-03, NC1-04, NC1-05 | no | - | - |
| nc_ambiguous | NC2-01, NC2-02, NC2-03, NC2-04, NC2-05 | no | - | R4-01..06 (ruling_4, test_ruling4_lost_ack.py) |
| nc_ingress_ambiguity | NC2-06 | yes | blocked_if ingress probe_ran false | AMB-01..06 |
| nc_process_kill | NC2-07 | no | blocked_if any of 3 seams not reached | KILL-01..18 |
| nc_duplicate | NC3-01, NC3-02, NC3-03 | no | - | - |
| nc_ledger_pruning | NC3-04 | no | - | PRUNE-01..08 |
| nc_unmediated | NC4-01, NC4-02, NC4-04 | yes | NC4-02 blocked_if probe_ran false; ingress start failure takes NC4-01/02/04 and KL-01 down together | (NC4-04: KW launcher-isolation tests, INFERENCE) |
| nc4_03_det | NC4-03 | no | - | KW-001..183, NM-001..135 |
| nc4_03_host | NC4-03a, NC4-03b, NC4-03c, NC4-03d | yes | each subcase BLOCKED independently if profile/probe unavailable | NM-136..143 + host-related NM mutation-set tests |
| nc_tamper | NC5-01, NC5-02, NC5-03, NC5-04, NC5-05 | no | differential: blocked_if control not accepted (NC5-01,02,03,05) | - |
| nc_custody | NC6-01, NC6-02, NC6-03, NC6-04 | no | differential: blocked_if control not accepted (NC6-01,04) | - |
| nc_authority_gates | NC7-01, NC7-02, NC7-03 | no | - | - |

Battery-level reading rule (OBSERVED, battery.rule): a listed test that is skipped, not collected, not executed, or whose oracle row is BLOCKED/NOT RUN makes the verdict INCOMPLETE; FAIL is REJECT; precedence INCOMPLETE over REJECT over ACCEPT. Gate environment-record checks (G-11) and anchor/custody checks are separate from the 47 rows and must be reported separately.

Host/ingress-dependent subset of the 47 (the part most likely to move to BLOCKED rather than PASS/FAIL): NC4-01, NC4-02, NC4-03a, NC4-03b, NC4-03c, NC4-03d, NC4-04 (host profile) and NC2-06 (real ingress as distinct uid). NC2-07 (real SIGKILL, needs the sudo VM and writable /var/lib store) is deployment-dependent as well. Everything else is in-process and host-independent by design. This is a risk map, not a prediction.

## 8. Per-row crosswalk (all 47 mandatory rows; full text, predicates and notes in crosswalk.json)

Every row: expected status PASS; classification_before_run UNTESTED; existing evidence at fa12c699: none. Node id = `suites/mvp-chain/test_mvp_chain.py::test_row[<ID>]` (battery entry id = row id). Predicate counts are from the oracle.

| id | grp | what the row requires (oracle title, truncated) | #pred | supplementary battery entries | notes key |
|---|---|---|---|---|---|
| ENV-01 | ENV | Every component HEAD equals its pin, checkouts pristine, modules loaded from the pinned trees, pydantic >= 2.12 | 4 | - | - |
| CHAIN-01 | CHAIN | Control Plane decides authorized and the operation is admitted (operation identity, journal mode) | 4 | - | - |
| CHAIN-02 | CHAIN | Real provision_local_execution_claim (executor.provision_claim) issues a claim | 2 | - | - |
| CHAIN-03 | CHAIN | Route B execute commits exactly one effect and consumes the claim (independent read-only ledger read) | 5 | - | - |
| CHAIN-04 | CHAIN | export_execution_artifacts serialises the executor evidence | 1 | - | - |
| CHAIN-05 | CHAIN | Replay import accepts the raw CP record, proposal and executor export; all import reports complete | 2 | - | blocked_if |
| CHAIN-06 | CHAIN | Evidence Pack imports the Replay bundle and validate_evidence_pack is valid | 2 | - | blocked_if |
| VER-01 | VER | Pinned Verifier on the raw CP record + proposal + manifest does not crash, does not refute (exit 0 accept or 3 abstain only) | 3 | - | ABSTAIN note |
| VER-02 | VER | No Verifier finding with code journal_check_reused (the documented claim-stage journal refutation) | 1 | - | ABSTAIN note |
| VER-03 | VER | Verifier run B (record + proposal + manifest + harness-derived ledger): any abstention is attributable only to v4.ledger.rows-agree-with-attempts (route B has no attempt ... | 4 | - | ABSTAIN note, NA-if |
| VER-04 | VER | Verifier exit code, report bytes (hash) and module path retained for the run | 2 | - | ABSTAIN note |
| NC1-01 | NC1 | Revocation: grant revoked in the authority store after claim issuance and before effect: effect refused, not attempted, zero effects | 3 | - | - |
| NC1-02 | NC1 | Approval withdrawal before effect: effect refused, not attempted, zero effects | 3 | - | - |
| NC1-03 | NC1 | Revocation at the Control Plane resolver before claim issuance: claim refused, zero effects | 2 | - | - |
| NC1-04 | NC1 | Approval revocation is terminal: revoke, then reactivate the approval, then execute the claim issued earlier: refused, zero effects | 2 | - | HISTORY |
| NC1-05 | NC1 | Grant revocation is terminal: revoke, then reactivate the grant, then execute: refused, zero effects | 2 | - | - |
| NC2-01 | NC2 | Ambiguous commit (lost acknowledgement): result is unknown, never acknowledged, retry not eligible | 3 | R4-01..06 (group-level, INFERENCE) | - |
| NC2-02 | NC2 | No blind retry: re-execution of the same claim is refused (status denied, not attempted) and the ledger still holds exactly one effect | 3 | R4-01..06 (group-level, INFERENCE) | - |
| NC2-03 | NC2 | Reconciliation after ambiguous commit establishes the applied effect without a second write | 2 | R4-01..06 (group-level, INFERENCE) | - |
| NC2-04 | NC2 | Reconciliation route unavailable after ambiguous commit: still unknown, never retry-eligible, never executed | 2 | R4-01..06 (group-level, INFERENCE) | - |
| NC2-05 | NC2 | Ambiguous-commit evidence is reconstructable: export and Replay import of the unknown outcome succeed | 2 | R4-01..06 (group-level, INFERENCE) | - |
| NC2-06 | NC2 | SUPPORTED-INGRESS evidence (NOT executor-level; executor-level is NC2-01..05 / ruling 4 with simulate='lost_ack'): one valid proposal from an unprivileged client over ... | 43 | AMB-01..AMB-06 (6) | HOST/INGRESS, blocked_if |
| NC2-07 | NC2 | REAL OS process death (A1): a child process executing the pinned route B atomic executor on a durable on-disk store is killed with SIGKILL by another process at each of ... | 119 | KILL-01..KILL-18 (18) | blocked_if |
| NC3-01 | NC3 | Duplicate effect: replaying the consumed claim is refused; one effect | 2 | - | - |
| NC3-02 | NC3 | Duplicate effect: a second claim for the same decision does not commit a second effect | 2 | - | - |
| NC3-03 | NC3 | Duplicate effect: renewal with cap 2 for the same operation id is refused operation_already_committed; one effect | 2 | - | - |
| NC3-04 | NC3 | Operation-ledger pruning (A2, documented limit): after one committed effect for an operation id on route B, with an unrecorded revision-2 renewal, the Control Plane ... | 20 | PRUNE-01..PRUNE-08 (8) | - |
| NC4-01 | NC4 | Real ingress (hub tools/mvp_ingress, Unix socket) started; the adversarial client ran as a distinct unprivileged uid (65534, no groups); the state tree was owner-only ... | 5 | - | HOST/INGRESS, HISTORY |
| NC4-02 | NC4 | EXECUTION OBSERVATION, independent of ingress self-report: after D1's adversarial inputs plus claim, simulate, authority-writer and SQL attempts as the unprivileged uid, ... | 5 | - | HOST/INGRESS, HISTORY, blocked_if |
| NC4-03 | NC4 | DETERMINISTIC SOURCE-LEVEL assertion (host-independent; not an execution observation): in the whole pinned hub tools/mvp_ingress source no non-literal ** forwarding ... | 22 | KW-001..NM-135 (318) | HISTORY |
| NC4-03a | NC4 | HOST-DEPENDENT subcase of NC4-03 (Yama), executed on the ratified bounded 2751 test profile (D3; not production): kernel.yama.ptrace_scope >= 1 on the execution host ... | 2 | NM-136..NM-134 (37) | HOST/INGRESS, HISTORY, blocked_if |
| NC4-03b | NC4 | HOST-DEPENDENT subcase of NC4-03 (uid separation), executed on the ratified bounded 2751 test profile (D3; not production): dedicated non-root ingress uid, a distinct ... | 13 | NM-136..NM-134 (37) | HOST/INGRESS, HISTORY, blocked_if |
| NC4-03c | NC4 | HOST-DEPENDENT subcase of NC4-03 (IPC 2751 socket profile), executed on the ratified bounded 2751 test profile (D3; not production): IPC directory 2751 / socket 0660 / ... | 18 | NM-136..NM-134 (37) | HOST/INGRESS, HISTORY, blocked_if |
| NC4-03d | NC4 | HOST-DEPENDENT subcase of NC4-03 (peer-UID allowlist), executed on the ratified bounded 2751 test profile (D3; not production): pinned server.serve against a stub core: ... | 9 | NM-136..NM-134 (37) | HOST/INGRESS, HISTORY, blocked_if |
| NC4-04 | NC4 | CODE-LEVEL launch isolation of the real ingress process (hub PR #230 launcher): observed on the LIVE process's own argv, the ingress is started as `python -I -B ... ... | 5 | - | HOST/INGRESS |
| NC5-01 | NC5 | Evidence tampering: Replay import refuses a CP record with a substituted journal commitment (differential against an accepted control) | 1 | - | blocked_if |
| NC5-02 | NC5 | Evidence tampering: Replay import refuses an executor export naming a different effect (differential) | 1 | - | blocked_if |
| NC5-03 | NC5 | Evidence tampering: Evidence Pack validation rejects a relabelled refusal summary / retained source | 1 | - | blocked_if |
| NC5-04 | NC5 | Evidence tampering: the Verifier reports the finding code decision_result_inconsistent, absent from the untampered record, for an altered decision result | 2 | - | - |
| NC5-05 | NC5 | Evidence tampering: Replay import refuses an executor export whose effect row was edited in the destination store after the fact (differential) | 1 | - | blocked_if |
| NC6-01 | NC6 | Custody failure: omission of the journal check events from the CP record is refused by Replay (differential) | 1 | - | blocked_if |
| NC6-02 | NC6 | Custody failure: destination store unavailable at effect time never yields executed and never a retry-eligible result; zero effects | 2 | - | - |
| NC6-03 | NC6 | Custody failure: authority store unreadable at claim issuance refuses the claim; zero effects | 2 | - | - |
| NC6-04 | NC6 | Custody failure: Replay import without the executor export is not reported as a complete reconstruction (differential against an accepted control) | 1 | - | blocked_if |
| NC7-01 | NC7 | Unauthorized execution commits no effect (route B, executor level): a claim id that was never issued is denied and not attempted, and a decision that is not authorized ... | 8 | - | - |
| NC7-02 | NC7 | Stale or mismatched authority prevents an unauthorized effect (route B, executor level): an expired claim, authority advanced to another grant revision after the claim, ... | 16 | - | - |
| NC7-03 | NC7 | Missing, invalid or expired required evidence does not permit execution (route B, executor level): with the required evidence row deleted, in a non-current state, or ... | 13 | - | - |

## 9. Caveats and residual uncertainty

- Supplementary-to-row links other than the explicit ones (NC2-06 AMB, NC2-07 KILL, NC3-04 PRUNE, NC4-03 KW/NM, NC4-03a..d NM-136..143) are my INFERENCE from test names; ruling_4 R4-01..06 are listed group-level for NC2-01..05 rather than guessed per row; MED-01..16 and AP entries map to no oracle row (ruling Q5 / route C exclusion).
- The 'host-related NM tests' list for NC4-03a..d is a name filter (contains 'host') over the mutation-set tests (33 entries incl. the 8 host-subcase ones); some are independence self-tests, so treat it as a reading aid.
- E2 values come from worker A's list, not an independent fetch. The GitHub Actions API, job logs and artifact zips are unreadable from this environment.
- Pre-disclosed run risks (F-06 never-run /var/lib base path on a hosted runner; floating ubuntu-24.04 label; 3.13 patch-level ast pins; custody branch mutable) can produce BLOCKED/INCOMPLETE rather than a false pass; none is a result.
- Mapping artifacts for later use: crosswalk.json (id -> {classification_before_run, battery_entries, test_nodeids, notes} plus predicates, blocked_if, qualifiers, history), crosswalk.meta.json (denominators, hashes, KL-01), denominators.json, _build.py.
