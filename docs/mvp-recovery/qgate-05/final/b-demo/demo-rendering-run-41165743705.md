# Synthetic $10 refund MVP - demonstration walkthrough (rendered from retained artifacts)

> **OCS-MVP-FINAL: frozen run 41165743705 attempt 1 (fa12c699), evidence branch commit ef407ca3**
> This rendering is labelled by the operator. Treat it exactly as labelled.

Read-only rendering. It shows only what the retained artifacts contain; anything absent is marked MISSING. It is not an acceptance, certification, Tier 1, Q7, release or production claim; standing holds are unchanged. Oracle statuses are the suite's; the gate verdict is the gate's; neither is computed here.

## 0. Scope statement (Architect ruling Q14)

Permitted claim, verbatim:

> The frozen pinned classes compose end-to-end in the qualification harness, while the trusted ingress boundary is separately exercised on the real socket under the same frozen candidate.

PROHIBITED claim (do not make it): "A live socket request produced the reconstructed Replay, Evidence Pack and Verifier evidence."

Why: the Replay, Evidence Pack and Verifier evidence below is reconstructed from the in-process composed chain (Control Plane, route-B executor, Replay, Evidence Pack, Verifier) run inside the qualification harness. The real-socket trusted ingress is exercised separately (section 13). No socket request produced the reconstructed evidence.

## 1. Evidence directory and run identity

| item | recorded value |
|---|---|
| evidence directory argument | /home/claude/view-ev |
| run directory resolved | /home/claude/view-ev/runs/run-41165743705-attempt-1 |
| chain results directory resolved | /home/claude/view-ev/runs/run-41165743705-attempt-1/mvp-chain |
| locator note | evidence branch root; using the only run directory run-41165743705-attempt-1 |
| observations.json | present, readable |
| results.json | present, readable |

Run identity (as recorded by the run job and by the evidence job):

| item | recorded value |
|---|---|
| run-identity.json (run job): run_url | https://github.com/cogno-us/cognous-stack-qualification/actions/runs/41165743705 |
| run-identity.json (run job): GITHUB_RUN_ID | 41165743705 |
| run-identity.json (run job): GITHUB_RUN_ATTEMPT | 1 |
| run-identity.json (run job): GITHUB_REF | refs/heads/qgate-05/run-1 |
| run-identity.json (run job): GITHUB_SHA | fa12c699939880149ed3997cbc2b11b264b23acd |
| run-identity.json (run job): GITHUB_EVENT_NAME | push |
| run-identity.json (run job): RUNNER_OS | Linux |
| run-identity.json (run job): ImageVersion | 20261026.354.1 |
| run-identity.json (run job): yama_ptrace_scope | 1 |
| run-identity.json (run job): kernel | 7.0.0-1017-azure |
| RUN-IDENTITY.json (evidence job): run_url | https://github.com/cogno-us/cognous-stack-qualification/actions/runs/41165743705 |
| RUN-IDENTITY.json (evidence job): GITHUB_RUN_ID | 41165743705 |
| RUN-IDENTITY.json (evidence job): GITHUB_RUN_ATTEMPT | 1 |
| RUN-IDENTITY.json (evidence job): GITHUB_REF | refs/heads/qgate-05/run-1 |
| RUN-IDENTITY.json (evidence job): GITHUB_SHA | fa12c699939880149ed3997cbc2b11b264b23acd |
| RUN-IDENTITY.json (evidence job): GITHUB_EVENT_NAME | push |
| RUN-IDENTITY.json (evidence job): RUNNER_OS | Linux |
| RUN-IDENTITY.json (evidence job): ImageVersion | 20261026.354.1 |
| RUN-IDENTITY.json (evidence job): QG5_JOB_STATUS | failure |

Qualification commit recorded by the run: `fa12c699939880149ed3997cbc2b11b264b23acd`; frozen candidate (Architect-stated) `fa12c699939880149ed3997cbc2b11b264b23acd`: **MATCH**.


### Component tuple recorded in results.json versus the frozen tuple

| component | recorded head | frozen (Architect-stated) |
|---|---|---|
| action_manifest | `fa170815ef96a54c233d0dd9da821b60debabf8b` | MATCH |
| control_plane | `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c` | MATCH |
| evidence_pack | `7b9511f2c6d56d424f17b078826594abd29f6c96` | MATCH |
| hub | `c897266b7ce4b921889519087fa8b1863b4302e3` | MATCH |
| odes | `1a5e1d300250d832e611633f0bf8f762e398c0ec` | MATCH |
| replay | `40012b8c174c6f25685bd5d9bc93ff46cc9a5842` | MATCH |
| runtime | `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f` | MATCH |
| verifier | `c0b8ba1f55b75db787a320f3de0f79342c6f6826` | MATCH |

overrides recorded: {}; cp_revision_override: null

oracle expectations file: `expectations.proposed.v8.json`; sha256 `498efc12fc1f608fb6fb53738ef61776cb576a70573f0644eb42a0f3e35f359c`; git blob `198bf9394db37a291891a1917408a746b6b3c205`; acceptance_declared: false


### Oracle row statuses (the suite's computation, reproduced)

suite-reported counts: {"BLOCKED":0,"FAIL":0,"NOT APPLICABLE":0,"NOT RUN":0,"PASS":48}; pytest_exit_status recorded: 1; rows in results.json: 48

Every row in results.json is PASS.

gate verdict (the gate's, as recorded): **REJECT**; authorizes: false; release: HOLD

commitment custody check: result PASS; recomputed commitment sha256 `814430869c63ab57cae091624c512bb119a3291e39e043827ae180ad59d3ca49` (MATCH with the frozen commitment v5)

pytest groups (run-level files; the gate, not this script, judges them):

- mvp-chain: pytest exit 1; junit: tests 414, failed 1, error 0, skipped 0, passed 413
- d2-route-b: pytest exit 0; junit: tests 22, failed 0, error 0, skipped 0, passed 22
- applicability: pytest exit 0; junit: tests 6, failed 0, error 0, skipped 0, passed 6


## 2. Governed synthetic $10 refund proposal and decision

| item | recorded value |
|---|---|
| action_id | urn:cognous:action:refund-issue-routine-v1 |
| actor | urn:cognous:identity:refund-agent-1 |
| principal | urn:cognous:principal:refund-service |
| target (synthetic account) | urn:cognous:synthetic-account:customer-001 |
| amount / unit | 10.0 USD |
| effects requested | 1 |
| requested_permissions | ["refund.issue.routine"] |
| payload | {"customer_id":"customer-001","refund_reason":"duplicate"} |
| manifest_id / version | refund-integration-pilot-v1 / 1.1 |
| payload_commitment (proposal file) | sha256:6b782ebbcc034ede... |
| proposal_commitment (from the executor export's envelope; the proposal file does not carry it) | sha256:b40cfbbd72185a09... |

| item | recorded value |
|---|---|
| decision_id | dcd9b644-5384-4ffc-89c5-ccc69c9dd863 |
| decision result (Control Plane) | **authorized** |
| reasons | [] |
| effect_id | sha256:79930e99498e59c63b616d35c09cf136547f349ade2db61bfe78d93d257be209 |
| decided_at | 2026-10-05T19:00:00+00:00 |
| time_source | test_override |
| decisions in record / refusals / attempts | 1 / 0 / 0 |

Cross-check with the harness observation: decision result authorized, decision_id MATCH with the retained record. Oracle: CHAIN-01: **PASS** - Control Plane decides authorized and the operation is admitted (operation identity, journal mode)

Time note: the record's time_source is as printed above (the harness fixes the clock; it is not wall-clock evidence).


## 3. Valid authority and approval

Resolution inputs the Control Plane consulted at decision time (recorded `observed` state):

| input_type | input_id | expected | observed | missing |
|---|---|---|---|---|
| manifest | refund-integration-pilot-v1 | {} | {} | false |
| authority_context | urn:cognous:alvorada:public-stack-profile:0.1.0 | {} | {"interface_status":"proposed_pending_governor_review","schema_version":"0.1.0"} | false |
| role_mapping | urn:cognous:institution:synthetic-customer-service | {} | {"digest":"sha256:f8a8db156df7087ddf34be1ed77fc86fa20ba7668deb87a9b3a5bd0a6ace496d","version":"roles-v1"} | false |
| identity | urn:cognous:identity:refund-agent-1 | {} | {"observed_at":"2026-10-05T19:00:00+00:00"} | false |
| mandate | urn:cognous:issuance:1 | {} | {"observed_at":"2026-10-05T19:00:00+00:00"} | false |
| grant | urn:cognous:grant:routine-1 | {"revision":"1","status":"active"} | {"observed_at":"2026-10-05T19:00:00+00:00","revision":"1","status":"active","version":"status-v1"} | false |
| conflict | urn:cognous:authority-requirement:refund-routine-v1 | {} | {"observed_at":"2026-10-05T19:00:00+00:00","state":"clear"} | false |
| policy | urn:cognous:policy:refund-policy | {"status":"active","version":"1.0"} | {"observed_at":"2026-10-05T19:00:00+00:00","status":"active","version":"1.0"} | false |
| approval | urn:cognous:approval:t1-1 | {"grant_id":"urn:cognous:grant:routine-1","grant_revision":"1","policies":"sha256:1cb091c265589e9d079a3c814befac072b3ad7f11f6bfbd0968825f3b816dee2","proposal":"sha256:b40cfbbd72185a094bae37d919165b06e | {"grant_id":"urn:cognous:grant:routine-1","grant_revision":"1","observed_at":"2026-10-05T19:00:00+00:00","policies":"sha256:1cb091c265589e9d079a3c814befac072b3ad7f11f6bfbd0968825f3b816dee2","proposal":"sha256:b40cfbbd72185a094bae37d919165b06e00d620377be8e8adef | false |
| evidence | urn:cognous:evidence:refund-entitlement | {"state":"current"} | {"observed_at":"2026-10-05T19:00:00+00:00","state":"current"} | false |
| evidence | urn:cognous:evidence:optional-context | {} | {"observed_at":"2026-10-05T19:00:00+00:00","state":"unknown"} | false |

Authority receipt retained in the executor export: grant urn:cognous:grant:routine-1 revision 1 status active; claim 8b00b95e-aba9-4b3a-aee5-418346b4c359; profile urn:cognous:profiles:local-authority-effect:0.1.0-proposed

Claim provisioning (real `provision_claim`): ok true, state after provision issued, error null. Oracle: CHAIN-02: **PASS** - Real provision_local_execution_claim (executor.provision_claim) issues a claim


## 4. Route-B atomic execution and the single destination effect

| item | recorded value |
|---|---|
| execute status / observed_state | executed / applied |
| attempted / acknowledged / newly_executed | true / true / true |
| execute error | null |
| destination effect_count (independent read-only readback, harness observation) | 1 |
| destination claim_state_after | consumed |
| operation-identity destination | true |
| effect_id equals the decision's expected effect_id | yes |

Effect rows retained in the executor export (chain/executor-export.json): **1**

- effect `sha256:79930e99498e59c63b616d35c09cf136547f349ade2db61bfe78d93d257be209` state applied amount 10.0 USD target urn:cognous:synthetic-account:customer-001 grant urn:cognous:grant:routine-1

Destination database copy (artifacts/chain-destination.sqlite, sha256 `16e7d55af1297006ca0a6a2174f8a1b6bf0f90ea74387600f4b7b9ae56b29f69`), opened read-only on a private temporary copy:

- table `effects`: 0 row(s)

Sidecar files retained beside the copy: wal MISSING, shm MISSING. If the copy shows fewer effect rows than the harness's independent readback above, the copy is not a complete picture of the destination: the harness copies only the main database file (INFERENCE: committed rows may still sit in the write-ahead log); the effect rows retained in the executor export are the authoritative retained record here.

Oracle: CHAIN-03: **PASS** - Route B execute commits exactly one effect and consumes the claim (independent read-only ledger read)


## 5. Operation identity and journal continuity

| item | recorded value |
|---|---|
| operation_id (harness observation) | op-order-100/refund-1 |
| identity profile on / status | true / ok |
| operations in the retained CP record | op-order-100/refund-1 grant urn:cognous:grant:routine-1 first_revision 1 |

Journal continuity recomputed from the retained record's check_events (the recorded events only; no new inference):

| check_id | stage | phases in recorded order | opened and completed |
|---|---|---|---|
| 885d94c9-4927-45a4-89ef-d55c186eaa28 | decision | opened > input > input > input > input > input > input > input > input > input > input > input > completed | yes |
| 08848aba-5f8d-4579-9147-4e15f08b76e3 | claim | opened > input > input > input > input > input > input > input > input > input > input > input > completed | yes |

events: 26; harness-observed n_events 26; completed stages ["decision","claim"]; distinct completed check ids 2

Oracle: CHAIN-01: **PASS** - Control Plane decides authorized and the operation is admitted (operation identity, journal mode); NC3-04 (operation-ledger pruning, section 9).


## 6. Refusal of unauthorized effects

Control case (the chain still works): status executed, attempted true, acknowledged true, newly_executed true, effects 1

| case | outcome | effects | error |
|---|---|---|---|
| unauthorized/forged_claim_id | status denied, attempted false | 0 | execution claim unavailable |
| unauthorized/not_authorized_decision | claim_ok false | 0 | {"code":null,"message":"decision is not authorized","type":"PermissionError"} |
| stale_or_mismatched/authority_advanced_after_claim | status denied, attempted false | 0 | authoritative grant state invalid |
| stale_or_mismatched/claim_expired | status denied, attempted false | 0 | execution claim outside validity interval |
| stale_or_mismatched/envelope_amount_mismatch | status denied, attempted false | 0 | execution claim operation mismatch: amount,operation_commitment,proposal_commitment |
| stale_or_mismatched/envelope_grant_revision_mismatch | status denied, attempted false | 0 | operation_identity_binding_mismatch |
| stale_or_mismatched/resolver_revision_changed_before_claim | claim_ok false | 0 | {"code":null,"message":"authorization-critical inputs changed before claim issuance","type |
| evidence/expired | status denied, attempted false | 0 | authoritative evidence expired |
| evidence/invalid_state | status denied, attempted false | 0 | authoritative evidence state invalid |
| evidence/missing | status denied, attempted false | 0 | authoritative evidence state unavailable |
| evidence/missing_at_claim_issuance | claim_ok false | 0 | {"code":null,"message":"authorization-critical inputs changed before claim issuance","type |

(Cases not listed above were not present as flat records in the observation; see observations.json for the full structure.)

- NC7-01: **PASS** - Unauthorized execution commits no effect (route B, executor level): a claim id that was never issued is denied and not attempted, and a deci
- NC7-02: **PASS** - Stale or mismatched authority prevents an unauthorized effect (route B, executor level): an expired claim, authority advanced to another gra
- NC7-03: **PASS** - Missing, invalid or expired required evidence does not permit execution (route B, executor level): with the required evidence row deleted, i
- NC5-01: **PASS** - Evidence tampering: Replay import refuses a CP record with a substituted journal commitment (differential against an accepted control)
- NC5-02: **PASS** - Evidence tampering: Replay import refuses an executor export naming a different effect (differential)
- NC5-03: **PASS** - Evidence tampering: Evidence Pack validation rejects a relabelled refusal summary / retained source
- NC5-04: **PASS** - Evidence tampering: the Verifier reports the finding code decision_result_inconsistent, absent from the untampered record, for an altered de
- NC5-05: **PASS** - Evidence tampering: Replay import refuses an executor export whose effect row was edited in the destination store after the fact (differenti
- NC6-01: **PASS** - Custody failure: omission of the journal check events from the CP record is refused by Replay (differential)
- NC6-02: **PASS** - Custody failure: destination store unavailable at effect time never yields executed and never a retry-eligible result; zero effects
- NC6-03: **PASS** - Custody failure: authority store unreadable at claim issuance refuses the claim; zero effects
- NC6-04: **PASS** - Custody failure: Replay import without the executor export is not reported as a complete reconstruction (differential against an accepted co

Boundary: these are executor-level controls on the in-process chain. The unmediated-path rows over the real socket are in section 13.


## 7. Revocation handling

| scenario | status | attempted | effects | refusal reason |
|---|---|---|---|---|
| grant_revoked | denied | false | 0 | authoritative grant state invalid |
| approval_withdrawn | denied | false | 0 | authoritative approval state invalid |
| grant_terminality | denied | false | 0 | authoritative grant state invalid |
| approval_terminality | denied | false | 0 | authoritative approval state invalid |
| resolver_revoked (before claim) | claim_ok false | n/a | 0 | authorization-critical inputs changed before claim issuance |

- grant_terminality: reactivation accepted false; reactivation error: grant revision is revoked; a successor revision is required
- approval_terminality: reactivation accepted false; reactivation error: approval is revoked; a new approval is required

- NC1-01: **PASS** - Revocation: grant revoked in the authority store after claim issuance and before effect: effect refused, not attempted, zero effects
- NC1-02: **PASS** - Approval withdrawal before effect: effect refused, not attempted, zero effects
- NC1-03: **PASS** - Revocation at the Control Plane resolver before claim issuance: claim refused, zero effects
- NC1-04: **PASS** - Approval revocation is terminal: revoke, then reactivate the approval, then execute the claim issued earlier: refused, zero effects
- NC1-05: **PASS** - Grant revocation is terminal: revoke, then reactivate the grant, then execute: refused, zero effects


## 8. Duplicate effect and lost-acknowledgement behaviour

Duplicate effect (route B, executor level):

| item | recorded value |
|---|---|
| first execute | status executed, attempted true, acknowledged true, newly_executed true |
| same claim replayed | status denied, attempted false, acknowledged false, newly_executed false, effects 1, error: execution claim is not usable |
| second claim for the same decision | status denied, attempted false, acknowledged false, newly_executed false, effects 1, error: authoritative effect budget exhausted |
| cap-2 renewal, same operation id: r1 / r2 | status executed, attempted true, acknowledged true, newly_executed true // status denied, attempted false, acknowledged false, newly_executed false, error: operation_already_committed |

Lost acknowledgement (`simulate='lost_ack'`, fault injected by the trusted harness at the executor; EXECUTOR-LEVEL evidence):

| item | recorded value |
|---|---|
| first result | status unknown, acknowledged false, attempted true, retry_eligible false; error: synthetic acknowledgement unavailable after atomic commit |
| destination after | claim consumed, effects 1 |
| retry of same claim | status denied, attempted false, acknowledged false, newly_executed false, error: execution claim is not usable |
| reconcile_claim | status applied, effect sha256:79930e99498e59c6..., retry_eligible false; effects after reconcile 1 |
| reconcile route unavailable | status unknown, retry_eligible false |
| export + Replay of the unknown outcome | export ok true; Replay ok true, records 40, all reports complete true |

Ambiguous acknowledgement through the supported ingress (NC2-06; evidence level as recorded below; real socket, so see section 13 for what it does and does not show):

evidence_level supported-ingress; client response {"code":"OUTCOME_UNKNOWN","outcome":"unknown"}; effect_count_after_first 1; blocked/other reason: MISSING

- NC3-01: **PASS** - Duplicate effect: replaying the consumed claim is refused; one effect
- NC3-02: **PASS** - Duplicate effect: a second claim for the same decision does not commit a second effect
- NC3-03: **PASS** - Duplicate effect: renewal with cap 2 for the same operation id is refused operation_already_committed; one effect
- NC2-01: **PASS** - Ambiguous commit (lost acknowledgement): result is unknown, never acknowledged, retry not eligible
- NC2-02: **PASS** - No blind retry: re-execution of the same claim is refused (status denied, not attempted) and the ledger still holds exactly one effect
- NC2-03: **PASS** - Reconciliation after ambiguous commit establishes the applied effect without a second write
- NC2-04: **PASS** - Reconciliation route unavailable after ambiguous commit: still unknown, never retry-eligible, never executed
- NC2-05: **PASS** - Ambiguous-commit evidence is reconstructable: export and Replay import of the unknown outcome succeed
- NC2-06: **PASS** - SUPPORTED-INGRESS evidence (NOT executor-level; executor-level is NC2-01..05 / ruling 4 with simulate='lost_ack'): one valid proposal from a


## 9. Real process kill and operation-ledger pruning observations

Real OS process death (A1): a child process running the pinned route-B atomic executor on a durable on-disk store is killed with SIGKILL by another process; a fresh observer process reopens the store.

observation status: ran; seams recorded: ["after_begin","after_effect_insert_before_commit","after_commit"]

| seam | killed by SIGKILL | victim returncode | on reopen (effects / claim) | reconcile_first | reconcile_second | final (effects / claim) |
|---|---|---|---|---|---|---|
| after_begin | true | -9 | 0 / issued | hold (no_durable_effect_for_claim) | applied | 1 / consumed |
| after_effect_insert_before_commit | true | -9 | 0 / issued | hold (no_durable_effect_for_claim) | applied | 1 / consumed |
| after_commit | true | -9 | 1 / consumed | applied (null) | applied | 1 / consumed |

Retained kill artifacts (nc_process_kill/<seam>/): after_begin: present, after_effect_insert_before_commit: present, after_commit: present

Scope limit as stated by the harness: SIGKILL of a process at three seams on a durable store. Power loss, OS crash and recovery of a lost acknowledgement stay UNQUALIFIED.

- NC2-07: **PASS** - REAL OS process death (A1): a child process executing the pinned route B atomic executor on a durable on-disk store is killed with SIGKILL b

Operation-ledger pruning (A2, documented limit): the Control Plane operation ledger is pruned after one committed effect.

| item | recorded value |
|---|---|
| control (unpruned) second decision | hold; reasons ["operation_renewal_unrecorded"] |
| ledger rows before / after pruning | 1 / 0 |
| Control Plane decision on the pruned record | authorized; reasons [] |
| claim issued for the second decision | true |
| second execute | status denied, attempted false, acknowledged false, newly_executed false, error: operation_already_committed |
| destination effects after (still only the original) | 1; only_original_effect true |
| Verifier on the pruned record (informational) | overall reject; exit 1; finding codes ["decision_revision_unlicensed","first_revision_mismatch","invalid_effect_identity"] |

Reading of the recorded values: pruning the Control Plane ledger lets the Control Plane authorize again (the oracle titles this a documented limit, row NC3-04); the destination's operation identity refuses the second effect. The Verifier's reaction above is informational.

- NC3-04: **PASS** - Operation-ledger pruning (A2, documented limit): after one committed effect for an operation id on route B, with an unrecorded revision-2 re


## 10. Replay reconstruction

| item | recorded value |
|---|---|
| harness observation: ok / n_records / n_reports / all_reports_complete | true / 40 / 1 / true |
| harness observation: error | null |

| item | recorded value |
|---|---|
| bundle status (retained file) | reconstruction_complete |
| bundle_id / run_id | 6dc3b501-29ba-4f6f-9941-eaba9c83506b / run-1 |
| records in bundle | 40 |
| import reports: complete flags | [true] |
| Replay semantics: record_reconstruction | true |
| Replay semantics: external_effect_execution | false |
| Replay semantics: independent_effect_verification | false |
| Replay semantics: destination_observation | producer_reported |
| Replay semantics: notes | Replay reconstructs recorded events only; import never renews permission or creates an effect. |

Reading: Replay reconstructs recorded events only; it re-executes nothing and the destination observation is producer-reported (as the retained semantics above state).

- CHAIN-05: **PASS** - Replay import accepts the raw CP record, proposal and executor export; all import reports complete


## 11. Evidence Pack reconstruction

| item | recorded value |
|---|---|
| harness observation: ok / valid / error | true / true / null |

| item | recorded value |
|---|---|
| pack_id / pack_version | agep-526914889c35d858 / 0.2.0 |
| review_status | draft |
| validation_summary | valid 1, invalid 0, errors 0, warnings 1 |
| retained replay bundle reference | [{"bundle_id":"6dc3b501-29ba-4f6f-9941-eaba9c83506b","signed":false,"status":"validated_complete","validation_status":"semantically_valid"}] |

Pack caveat as the pack itself states: Source artifacts were evaluated by supported semantic import checks; inspect the actual findings. This does not establish deployment approval, compliance, operational effectiveness, or independent audit.

- CHAIN-06: **PASS** - Evidence Pack imports the Replay bundle and validate_evidence_pack is valid


## 12. Verifier disposition

The pinned Verifier ran as a subprocess over the raw Control Plane record. Dispositions below are the Verifier's own words (from the harness observation); **ABSTAIN is reported as ABSTAIN and is never a PASS.** An oracle row PASS (VER-01..04) means the harness's expectation held (for example, that exit code 0 or 3 occurred, no crash, no refutation); it does not mean the Verifier accepted.

| run | inputs | overall (as recorded) | exit code | checks | confirmed | could not check | refuted | crashed | refuting finding codes |
|---|---|---|---|---|---|---|---|---|---|
| A | record + proposal + manifest | **ABSTAIN** | 3 | 29 | 22 | 7 | 0 | false | [] |
| B | A + harness-derived ledger | **ABSTAIN** | 3 | 28 | 27 | 1 | 0 | false | [] |

Run A could-not-check checks: v4.ledger.acknowledged-attempts-have-rows (input_absent); v4.ledger.counts (input_absent); v4.ledger.effects-have-authorized-decisions (input_absent); v4.ledger.keys (input_absent); v4.ledger.observations-agree (input_absent); v4.ledger.row-matches-binding (input_absent); v4.ledger.rows-agree-with-attempts (input_absent)
- retained report verifier/A-report.json (sha256 `195224398e3cef7fe8af7308f77a27d57f2f687963b9ce9e475f69c8b4819d39`): summary {"checks":29,"confirmed":22,"could_not_check":7,"refuted":0} - MATCHES the harness observation; observation's report_sha256 MATCHES
- the report's own does_not_prove list (9 items): relative_to_pinned_controller, semantic_quality_not_certified, receipt_source_bounded, self_consistent_forgery_not_detected, not_an_attestation, parse_strictness_is_refusal_not_repair, no_v1_scope_claim, differential_agreement_is_not_equivalence, profile_sidecar_semantics_only
Run B could-not-check checks: v4.ledger.rows-agree-with-attempts (tier_unavailable)
- retained report verifier/B-report.json (sha256 `7f14aa007955136f24841a4a22f95cc2fcfc32a94582ffa3df11aef011a6bd67`): summary {"checks":28,"confirmed":27,"could_not_check":1,"refuted":0} - MATCHES the harness observation; observation's report_sha256 MATCHES

- Verifier run A input `record` 5fd3d8300c67bec4082a... vs sha256 of retained chain/cp-run-record.json: **MATCH**
- Verifier run A input `proposal` d255532bf763dff1fc2f... vs sha256 of retained chain/proposal.json: **MATCH**

Reading of ABSTAIN here: the Verifier did not refute and could not check the ledger-based items in run A because no ledger input was supplied; run B supplies a harness-derived ledger and narrows the could-not-check set (as recorded above). This is an abstention on part of the checks, not an acceptance of the record.

- VER-01: **PASS** - Pinned Verifier on the raw CP record + proposal + manifest does not crash, does not refute (exit 0 accept or 3 abstain only)
- VER-02: **PASS** - No Verifier finding with code journal_check_reused (the documented claim-stage journal refutation)
- VER-03: **PASS** - Verifier run B (record + proposal + manifest + harness-derived ledger): any abstention is attributable only to v4.ledger.rows-agree-with-att
- VER-04: **PASS** - Verifier exit code, report bytes (hash) and module path retained for the run

- differential Verifier input T0 (untampered control): report present, summary {"checks":29,"confirmed":22,"could_not_check":7,"refuted":0}
- differential Verifier input T1 (decision-altered): report present, summary {"checks":29,"confirmed":18,"could_not_check":10,"refuted":1}
- NC5-04: **PASS** - Evidence tampering: the Verifier reports the finding code decision_result_inconsistent, absent from the untampered record, for an altered de


## 13. The real-socket trusted ingress, kept separate

> The frozen pinned classes compose end-to-end in the qualification harness, while the trusted ingress boundary is separately exercised on the real socket under the same frozen candidate.

PROHIBITED: "A live socket request produced the reconstructed Replay, Evidence Pack and Verifier evidence." The rows below are separate observations of the ingress boundary; they are not the source of sections 2 to 12.

- KL-01: **PASS** (mandatory: false) - every predicate held on the recorded observations
- NC4-01: **PASS** (mandatory: true) - every predicate held on the recorded observations
- NC4-02: **PASS** (mandatory: true) - every predicate held on the recorded observations
- NC4-03: **PASS** (mandatory: true) - every predicate held on the recorded observations
- NC4-03a: **PASS** (mandatory: true) - every predicate held on the recorded observations
- NC4-03b: **PASS** (mandatory: true) - every predicate held on the recorded observations
- NC4-03c: **PASS** (mandatory: true) - every predicate held on the recorded observations
- NC4-03d: **PASS** (mandatory: true) - every predicate held on the recorded observations
- NC4-04: **PASS** (mandatory: true) - every predicate held on the recorded observations

NC4 observation: profile approved, ingress probe ran: true; blocked_reason: MISSING

Any BLOCKED row above means the exact approved host profile was not available on the machine that produced these artifacts; it is reported BLOCKED, never PASS.


## 14. Evidence custody hashes

| item | recorded value |
|---|---|
| observations.json sha256 | 6045d03dbf168db86ab6ca20a69c80d3b791b395640abcf861423c554b6d52b5 |
| results.json observations_sha256 | 6045d03dbf168db86ab6ca20a69c80d3b791b395640abcf861423c554b6d52b5 - MATCH |
| results.json sha256 | 1ae84f3f4f1c616b4540bf0e6b0f543d82251b60d73d9661e74880efd7ccdb33 |

SHA256SUMS (sha256 `158d3a277a672cb8adaaa7d5e99447376efb325228fd9ceca9a21f1f9c75d984`): 256 file(s) verified, 0 MISMATCH, 0 MISSING.

SHA256SUMS.run-job (sha256 `5de97382f8a091304019a2f65719768e13904791650b7572a0cd58d820525ef2`): 252 file(s) verified, 0 MISMATCH, 0 MISSING.

ARTIFACT-SHA256SUMS-VERIFY.txt (recorded by the evidence job; last line): sha256sum -c exit=0

Hashes of the retained chain artifacts (computed now, file bytes):

| file | sha256 | bytes |
|---|---|---|
| artifacts/chain/cp-run-record.json | `5fd3d8300c67bec4082acd8e31c3954fd4ffebd4c9b7085fc918c9c9fb831a84` | 53250 |
| artifacts/chain/evidence-pack.json | `78d44d6d1d8a6f8d5d2af842347fb975d6e8931893e65d229b2edace9b82deb8` | 238718 |
| artifacts/chain/executor-export.json | `b8092dca90b169edf151004e8f4e4a52b310678ab7fded057c0954a3b49a487a` | 7070 |
| artifacts/chain/proposal.json | `d255532bf763dff1fc2f71887f95ee76009db83f84881daafcc8013ea8cf4894` | 1097 |
| artifacts/chain/replay-bundle.json | `a0a809e4699d2131f8c6a0598e0b3f5671516fdaf521ec64af1678b08f794933` | 87451 |
| artifacts/chain-destination.sqlite | `16e7d55af1297006ca0a6a2174f8a1b6bf0f90ea74387600f4b7b9ae56b29f69` | 12288 |
| artifacts/environment-record.envelope.json | `ae9aa3c9bdef1bd64332a48110fdd33b696a39e14120e28587888d2cc876cdb1` | 751 |
| artifacts/environment-record.json | `d40230797eb8030ba859866f108dcd9a4d988579aaaa363640c3511c947daf9a` | 24852 |
| artifacts/ingress-modules-ambiguity-before.json | `d77003ca50f503db471006234b15224421b97bb4d4eecde4be6e4baa46eaa688` | 45149 |
| artifacts/ingress-modules-ambiguity-forced.json | `6131b699156740d0a6c479a1889770402c1e6571785dc8fc300927303ef74f88` | 45149 |
| artifacts/ingress-modules-ambiguity-nohook.json | `6e14dd4832163dc27b8cd99db91224f7fb7d69e34d86286a6a480dfe1ffd4b8e` | 44969 |
| artifacts/ingress-modules-ambiguity-second.json | `96bbcddffa58a55c46e04e088cea2a5d7ed4fad65a782e83daedeee54c4730a4` | 45149 |
| artifacts/ingress-modules-ambiguity-unbound.json | `7e2e1a506cd95b06dd094d209923f7fd2455b1760875c2683de77524b7e0ef71` | 45149 |
| artifacts/ingress-modules-ambiguity.json | `b39782637658f628342e191c3292b24bebe2d5176a34ecfd671e533e11a4e3e0` | 45149 |
| artifacts/ingress-modules.json | `7dbd835a04ae2f486c50bc88df8b8a9b11011b0e39839eae206068819507cf75` | 44969 |
| artifacts/nc_ledger_pruning/cp-run-record.after-second-decision.json | `bb22792eb206846eaf3ea0567b05e438e6a894d2222b34f99c073a00c93ded87` | 133129 |
| artifacts/nc_ledger_pruning/cp-run-record.intact.json | `22312771702b2b895e76fbebc211a3bd8e6f6a733f1bae916f620cfb6a99edf9` | 80986 |
| artifacts/nc_ledger_pruning/cp-run-record.pruned.json | `13c77cbd7f09ae8446cddf6b4daa45b718f8492c90f64d1dbba4041d50e7400b` | 62589 |
| artifacts/nc_ledger_pruning/destination.final.sqlite | `164ec7c03bf6f30a841590f3f7f47588c8aef696c208173c0240f987b7203161` | 118784 |
| artifacts/nc_ledger_pruning/verifier/pruned-manifest.json | `96e02498c1b53f8f536f6727e857441cda30fb7a19220f893071ebea03332a42` | 5108 |
| artifacts/nc_ledger_pruning/verifier/pruned-proposal.json | `e0a6282b690e256c5930fb9e5d93a0d67dfa73824d62d35d5c0ae776d0a2c0a0` | 1097 |
| artifacts/nc_ledger_pruning/verifier/pruned-report.json | `4bc88e3f76d308b20c99ea27fb79764e58f8aeeb3639536a930ffddc8ca9264a` | 18856 |
| artifacts/nc_ledger_pruning/verifier/pruned-run-record.json | `bb22792eb206846eaf3ea0567b05e438e6a894d2222b34f99c073a00c93ded87` | 133129 |
| artifacts/nc_process_kill/after_begin/observations.json | `d21d73986e7a72d2f25a46e9d605af51c753d3d65a39f519bc8f56df92d5724a` | 4795 |
| artifacts/nc_process_kill/after_begin/post-recovery-tables.json | `72540f374677067f1b94e09d1a4fee45c07a445ea327d24064532691cbe730ae` | 9626 |
| artifacts/nc_process_kill/after_begin/pre-recovery/cp-run.json | `d84a0ba42c8e9be50df3c46f014e2a1bf00cc18b986bfd1d321845ae9db9d1f6` | 53250 |
| artifacts/nc_process_kill/after_commit/observations.json | `69f153c25f7a7e1f314bb3a927be5ada4d8f85884ae787b564810b16d72edc06` | 4895 |
| artifacts/nc_process_kill/after_commit/post-recovery-tables.json | `7dab1e40e0b639fe125e9a9fb39eccb5f0f176fadc114104e18eef669377aaf1` | 10359 |
| artifacts/nc_process_kill/after_commit/pre-recovery/cp-run.json | `d95f17edd41061bb80553b0dcfdefb4bac9ff981528f78e26752770bfb2b1f47` | 53250 |
| artifacts/nc_process_kill/after_effect_insert_before_commit/observations.json | `1a859f50cac3e07053e8b2a51c0d4979673dfe16ccbbf6b61146dcc3e4b73039` | 4949 |
| artifacts/nc_process_kill/after_effect_insert_before_commit/post-recovery-tables.json | `7f3eb64d98c18295d857dcfc3ad5f51ff5d2fffd7ab3324ab5ff70e060503518` | 9625 |
| artifacts/nc_process_kill/after_effect_insert_before_commit/pre-recovery/cp-run.json | `e5c4b0950db74e1db6a4174a8d38eee5197f6fa874285f93ffbf71591f670d93` | 53250 |
| artifacts/verifier/A-manifest.json | `2de33f6fd0936ec56013a5eddb99c8c4a2943ab463f8ee9c3898780a8da20e58` | 5108 |
| artifacts/verifier/A-proposal.json | `d255532bf763dff1fc2f71887f95ee76009db83f84881daafcc8013ea8cf4894` | 1097 |
| artifacts/verifier/A-report.json | `195224398e3cef7fe8af7308f77a27d57f2f687963b9ce9e475f69c8b4819d39` | 18093 |
| artifacts/verifier/A-run-record.json | `5fd3d8300c67bec4082acd8e31c3954fd4ffebd4c9b7085fc918c9c9fb831a84` | 53250 |
| artifacts/verifier/B-ledger.json | `3a6adb48fafca6b8b3bbe8f18e42ba04695b1a6ffe5620f847c4114d92ad8d0f` | 513 |
| artifacts/verifier/B-manifest.json | `2de33f6fd0936ec56013a5eddb99c8c4a2943ab463f8ee9c3898780a8da20e58` | 5108 |
| artifacts/verifier/B-proposal.json | `d255532bf763dff1fc2f71887f95ee76009db83f84881daafcc8013ea8cf4894` | 1097 |
| artifacts/verifier/B-report.json | `7f14aa007955136f24841a4a22f95cc2fcfc32a94582ffa3df11aef011a6bd67` | 18371 |
| artifacts/verifier/B-run-record.json | `5fd3d8300c67bec4082acd8e31c3954fd4ffebd4c9b7085fc918c9c9fb831a84` | 53250 |
| artifacts/verifier/T0-untampered-manifest.json | `2de33f6fd0936ec56013a5eddb99c8c4a2943ab463f8ee9c3898780a8da20e58` | 5108 |
| artifacts/verifier/T0-untampered-proposal.json | `d255532bf763dff1fc2f71887f95ee76009db83f84881daafcc8013ea8cf4894` | 1097 |
| artifacts/verifier/T0-untampered-report.json | `3aa372856df9ef9554197cb793b8c7b55c71480368b969495258d95d6f089845` | 18129 |
| artifacts/verifier/T0-untampered-run-record.json | `e7e54cdbe35cd92fd46bafb6616665563551b22d3544a0f63a9d7f27be9430b5` | 53250 |
| artifacts/verifier/T1-decision-altered-manifest.json | `2de33f6fd0936ec56013a5eddb99c8c4a2943ab463f8ee9c3898780a8da20e58` | 5108 |
| artifacts/verifier/T1-decision-altered-proposal.json | `d255532bf763dff1fc2f71887f95ee76009db83f84881daafcc8013ea8cf4894` | 1097 |
| artifacts/verifier/T1-decision-altered-report.json | `703bc611c39c9f8261e4d722dd2a92e76efb35a0ffa69ec959cc3f58399bba5c` | 18555 |
| artifacts/verifier/T1-decision-altered-run-record.json | `d37af2356301c5deea6a1aa8ca0988c6f4c06cf94138959c94cf898bb8d1b1df` | 41600 |
| artifacts/verifier/pruned-report.json | `4bc88e3f76d308b20c99ea27fb79764e58f8aeeb3639536a930ffddc8ca9264a` | 18856 |

tuple-resolved.json: present, qualification_sha fa12c699939880149ed3997cbc2b11b264b23acd


## 15. Artifact inventory (expected files)

| file under the chain results directory | state |
|---|---|
| observations.json | present |
| results.json | present |
| artifacts/chain/cp-run-record.json | present |
| artifacts/chain/proposal.json | present |
| artifacts/chain/executor-export.json | present |
| artifacts/chain/replay-bundle.json | present |
| artifacts/chain/evidence-pack.json | present |
| artifacts/chain-destination.sqlite | present |
| artifacts/verifier/A-report.json | present |
| artifacts/verifier/B-report.json | present |
| artifacts/nc_process_kill/after_begin/observations.json | present |
| artifacts/nc_process_kill/after_effect_insert_before_commit/observations.json | present |
| artifacts/nc_process_kill/after_commit/observations.json | present |
| artifacts/nc_ledger_pruning/cp-run-record.pruned.json | present |
| artifacts/verifier/pruned-report.json | present |

| run-level file | state |
|---|---|
| run-identity.json | present |
| RUN-IDENTITY.json | present |
| gate-verdict.json | present |
| custody-evidence.json | present |
| tuple-resolved.json | present |
| SHA256SUMS | present |
| ARTIFACT-SHA256SUMS-VERIFY.txt | present |
| environment-record (mvp-chain/artifacts/environment-record.json) | present |

---
Standing holds unchanged: no acceptance, certification, Tier 1, Q7, release or production claim is made or implied by this rendering.

**OCS-MVP-FINAL: frozen run 41165743705 attempt 1 (fa12c699), evidence branch commit ef407ca3**
