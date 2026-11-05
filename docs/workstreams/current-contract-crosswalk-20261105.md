# OCS mandatory-test and current-contract crosswalk (PR A: S1 + S2 proposal)

**Status: PROPOSED. NOT ADOPTED. NOT A GATE.** Builder output for independent review (no self-certification, CA04/CA23). This document and its data file change no gate, workflow, ruleset, lock, oracle, test selection or behavior. Nothing here makes any check non-gating; UNRESOLVED keeps gating status. Historical PASS is never a current PASS. Original failing evidence is preserved.

Data (all per-record fields): `docs/workstreams/current-contract-crosswalk-20261105.json` (format `cognous.contract-crosswalk/1`, proposal schema, not an adopted schema).

Controlling plan (read, not modified): Hub PR #264, `docs/workstreams/current-contract-qualification-transition-plan-20261104.md` @ `0e47581506914147225779afe6fff97cce93258a`. Work packages: S1 crosswalk and S2 baseline proposal (plan section 5 PR (a)). Constitution pin `1c2e920f4e58e07a52e8e2408a506cf7dbc1292b`: publication is not adoption; adoption for the OCS active configuration is UNVERIFIED (no `ADOPTION.md` found in Hub; AD-08). No compliance claim is made beyond what is verified below.

Provenance labels: **WRITER_VERIFIED_LIVE** = read by the PR writer from the cited source on 2026-11-05 UTC. **CARRIED_FROM_WORKER_AUDIT** = finding from read-only static audits dated 2026-11-04 (inventory, historical audit, coverage audit, CI analysis) that the writer did not re-derive. Test-id presence was checked against a sparse test index of the lock-pinned checkouts; presence is not a pass result.

## 1. Sources and identity

### 1.1 Revisions verified live (WRITER_VERIFIED_LIVE)

| Item | Revision |
|---|---|
| Hub main | `985dfe461241db18a318b921d4a7d52ffb47491a` |
| Hub PR #263 head (component-lock identical to main; only 3 workflow files differ) | `a00a02aca3ed22a0667a45d729b5e5c08b430822` |
| Hub PR #264 head (plan) | `0e47581506914147225779afe6fff97cce93258a` |
| Qualification main | `8e5e4ac31cae3300694bcaa3bfa67205e204813c` |
| Qualification PR #270 head (live; earlier worker read recorded bb1bdc97) | `6ac2f1a9d6c97c27a76630590025557f1ae0a482` |
| GAX main | `e78a7be3cb4ea622d2a0eec430c209449ec4c86c` |
| Hub lock runtime_profile | `security-runtime-p2-20261018` |
| Hub ruleset 25195893 required contexts (no bypass actors) | `cross-component / integrity; verify (3.11); verify (3.12); cross-component / aggregate; preview-audit` |
| acceptance-matrix.json sha256 | `7c4325cdf311e4acc6633cc08d5fd54c0d967bceda32ae25e30e4957975cb7ea` |
| component-lock.json sha256 | `dcd3ab9e4e737c7e50f4bc38c2439438f156da64c9eb1e46725f477973da59ff` |

Lock pins (Hub `component-lock.json` @ 985dfe46): action_manifest `fa170815`; control_plane `0a41faa9`; constitutional_authority `9b5ab721`; gax_imx_transport `7f7569b0`; moltbot_safe `ec728da6`; replay_bundle `028f63d1`; governance_evidence_pack `a3ebbb90`; odes `e86a25a1`; bitrep `981036c3`; the_index `b2485998`; verifier `c0b8ba1f`.

### 1.2 Which matrix is meant by '35 scenarios'

Hub scenarios/acceptance-matrix.json matrix_version 1.6 @985dfe46: 35 scenarios, 115 test refs (108 unique), 15 suites. Resolved by release_gate.resolve_matrix over JUnit.

Not meant: Qualification scenarios/catalog.json (40 scenarios, all NOT RUN, specification only) and scenarios/coverage-map.json (proposed coverage); and the 40 SCN-* rows of the g8 v1 validation run (0 PASS, 27 INCONCLUSIVE, 13 NOT RUN). Lock qualification_evidence.matrix_scenarios=35 is for run 37694032916 on an earlier tuple (Hub PR #23); whether it applies to the p2 pins is AD-07 (mapping to the Hub matrix is UNVERIFIED).

Correction carried forward: one worker audit states 109 test refs; the matrix file contains 115 refs (108 unique) over 15 suites (WRITER_VERIFIED_LIVE).

## 2. Crosswalk (S1)

Records: 35 scenarios, 25 stage groups, 10 other test groups/fixtures, 7 CI gate records. Classifications are PROPOSED only. LEGACY_SUPPORTED: none qualifies today (no owner-stated consumers plus duration found).

### 2.1 Acceptance-matrix scenarios (matrix 1.6)

Columns: contract = lock-declared interface name or source-native id (no adopted contract revision exists; ODES drafts are 0.1.0-draft). Replacement = current replacement status (full ids in the data file). AN = authority needed flag.

| # | Scenario | Refs | Contract (id) | Owner | Stages (generation) | Class | AN | Current replacement |
|---|---|---|---|---|---|---|---|---|
| 1 | `valid_t1_refund` | 3 | bounded authorization/effect 0.1; ODEX-GAX/IMX refund exchange 0.1.0 (urn:cognous:profiles:odex-gax-imx-refund-exchange:0.1.0) | cognous-control-plane, cognous-governed-exchange | control_plane (current); gax_reference (current); governed_transport_integration (current) | CURRENT_REQUIRED | no | self_current_pins; gax refs blocked by A |
| 2 | `t2_approval` | 1 | bounded authorization/effect 0.1 | cognous-control-plane | control_plane (current) | CURRENT_REQUIRED | no | self_current_pins |
| 3 | `authority_missing_revoked_expired_stale` | 6 | bounded authorization/effect 0.1; ODEX-GAX/IMX refund exchange 0.1.0 (urn:cognous:profiles:odex-gax-imx-refund-exchange:0.1.0) | cognous-control-plane, cognous-governed-exchange | control_plane (current); gax_reference (current); governed_transport_integration (current); research_qualification (current) | CURRENT_REQUIRED | no | self_current_pins; research refs blocked by A and need a synthetic clock |
| 4 | `binding_substitution` | 5 | bounded authorization/effect 0.1; governed-message-transport 0.1.0 (urn:cognous:profiles:governed-message-transport:0.1.0) | cognous-control-plane, cognous-governed-exchange | control_plane (current); gax_reference (current); governed_transport (current) | CURRENT_REQUIRED | no | self_current_pins |
| 5 | `policy_changed_after_decision` | 2 | bounded authorization/effect 0.1 | cognous-control-plane | control_plane (current); gax_reference (current) | CURRENT_REQUIRED | no | self_current_pins |
| 6 | `bad_evidence` | 6 | bounded authorization/effect 0.1; verification contract v1; Reconstruction Bundle 0.2.0 | cognous-control-plane, cognous-evidence-attestation, cognous-replay-bundle | control_plane (current); bitrep_verification (current); replay (current) | CURRENT_REQUIRED | no | self_current_pins |
| 7 | `required_stale_vs_optional_unknown` | 1 | bounded authorization/effect 0.1 | cognous-control-plane | control_plane (current) | CURRENT_REQUIRED | no | self_current_pins |
| 8 | `non_action_messages` | 2 | governed-message-transport 0.1.0 (urn:cognous:profiles:governed-message-transport:0.1.0) | cognous-governed-exchange | gax_reference (current); governed_transport (current) | CURRENT_REQUIRED | no | self_current_pins |
| 9 | `multi_sender_shared_recipient` | 1 | governed-message-transport 0.1.0 (urn:cognous:profiles:governed-message-transport:0.1.0) | cognous-governed-exchange | governed_transport (current) | CURRENT_REQUIRED | no | self_current_pins |
| 10 | `message_id_and_replay` | 2 | governed-message-transport 0.1.0 (urn:cognous:profiles:governed-message-transport:0.1.0) | cognous-governed-exchange | governed_transport (current) | CURRENT_REQUIRED | no | self_current_pins |
| 11 | `duplicate_lost_ack_restart` | 5 | bounded authorization/effect 0.1; governed-message-transport 0.1.0 (urn:cognous:profiles:governed-message-transport:0.1.0) | cognous-control-plane, cognous-governed-exchange | control_plane (current); gax_reference (current); governed_transport (current); governed_transport_integration (current) | CURRENT_REQUIRED | no | self_current_pins |
| 12 | `interruption_after_inbox` | 1 | governed-message-transport 0.1.0 (urn:cognous:profiles:governed-message-transport:0.1.0) | cognous-governed-exchange | governed_transport (current) | CURRENT_REQUIRED | no | self_current_pins |
| 13 | `interruption_after_commit` | 3 | governed-message-transport 0.1.0 (urn:cognous:profiles:governed-message-transport:0.1.0); ODEX-GAX/IMX refund exchange 0.1.0 (urn:cognous:profiles:odex-gax-imx-refund-exchange:0.1.0) | cognous-governed-exchange | gax_reference (current); governed_transport (current) | CURRENT_REQUIRED | no | self_current_pins; gax_reference blocked by A |
| 14 | `partial_and_unavailable_observation` | 3 | bounded authorization/effect 0.1 | cognous-control-plane | control_plane (current); gax_reference (current) | CURRENT_REQUIRED | no | self_current_pins |
| 15 | `continuity_tamper` | 3 | ODEX-GAX/IMX refund exchange 0.1.0 (urn:cognous:profiles:odex-gax-imx-refund-exchange:0.1.0) | cognous-governed-exchange | gax_reference (current) | CURRENT_REQUIRED | no | self_current_pins (blocked by A) |
| 16 | `replay_import_redaction_no_effect` | 3 | Reconstruction Bundle 0.2.0; imported Evidence Pack schema 0.2.0 | cognous-governance-evidence-pack, cognous-replay-bundle | replay (current); evidence_pack (current (labelled); executes with historical-root env agep_historical_env) | CURRENT_REQUIRED | no | Replay refs at lock; EP ref in relocated test_importer.py |
| 17 | `test_provenance` | 2 | imported Evidence Pack schema 0.2.0 | cognous-governance-evidence-pack | evidence_pack (current (labelled); historical-root env) | CURRENT_REQUIRED | no | relocated test_importer.py only; no equivalent found in EP tests at lock |
| 18 | `bitrep_index_non_authorizing` | 4 | verification contract v1; local blockchain reference 0.1.0 | cognous-evidence-attestation, cognous-evidence-registry | bitrep_verification (current); index_bitrep_binding (current) | CURRENT_REQUIRED | no | index refs in relocated test_bitrep.py (rc 0, 17 tests in PR #270 local reproduction) |
| 19 | `original_artifact_continuity` | 3 | GAX retained artifacts 1.1.0 (urn:cognous:profiles:gax-retained-artifacts) | cognous-governed-exchange | gax_public_runtime_artifacts (historical (3/3 refs run under merged-producers-v1)) | UNRESOLVED (invariant CURRENT_REQUIRED) | yes | PARTIAL: hub_release_gate refs exist at lock (blocked by A, 68 setup errors); durable redelivery retrieval has no current-pin test |
| 20 | `post_effect_evidence_recovery` | 4 | GAX retained artifacts 1.1.0 (urn:cognous:profiles:gax-retained-artifacts); ODEX-GAX/IMX refund exchange 0.1.0 (urn:cognous:profiles:odex-gax-imx-refund-exchange:0.1.0) | cognous-governed-exchange | gax_public_runtime_artifacts (historical (2/4 refs)); gax_reference (current (2/4 refs)) | UNRESOLVED (invariant CURRENT_REQUIRED) | yes | PARTIAL: gax_reference refs at lock (blocked by A); research_qualification recovery tests (blocked by A) |
| 21 | `timeout_retry_qualification` | 4 | bounded authorization/effect 0.1; governed-message-transport 0.1.0 (urn:cognous:profiles:governed-message-transport:0.1.0) | cognous-control-plane, cognous-governed-exchange | control_plane (current); gax_reference (current); governed_transport (current) | CURRENT_REQUIRED | no | self_current_pins |
| 22 | `research_replanned_equivalent_intent` | 1 | none identified (source is a research note, not an adopted contract) | cognous-stack-qualification | research_qualification (current (needs synthetic clock; blocked by A)) | CURRENT_REQUIRED | yes | self; blocked by A |
| 23 | `research_absence_evidence` | 1 | none identified (source is a research note, not an adopted contract) | cognous-stack-qualification | research_qualification (current) | CURRENT_REQUIRED | no | self; blocked by A |
| 24 | `observation_repair_lifecycle` | 7 | bounded authorization/effect 0.1; executor producer profile 2.0.0; execution-attempt-lifecycle 0.1.0-draft | cognous-control-plane, cognous-execution-runtime, open-decision-evidence-standard | gax_observation_repair (current (3 refs)); replay/odes/evidence_pack_v2 producer-v2 (historical (4 refs; manifest 46c950be, CP 2ea9528e)) | UNRESOLVED (invariant CURRENT_REQUIRED) | yes | PARTIAL: GAX refs at lock (blocked by A); consumer lifecycle tests at lock; no gated live-producer round trip at p2 in reference_release |
| 25 | `original_late_commit` | 1 | bounded authorization/effect 0.1 | cognous-control-plane | research_qualification (current) | CURRENT_REQUIRED | no | self; blocked by A |
| 26 | `recovery_authority_revocation` | 2 | bounded authorization/effect 0.1 | cognous-control-plane | research_qualification (current (2 parametrized refs)) | CURRENT_REQUIRED | no | self; blocked by A |
| 27 | `recovery_authority_expiry` | 2 | bounded authorization/effect 0.1 | cognous-control-plane | research_qualification (current (2 parametrized refs)) | CURRENT_REQUIRED | no | self; blocked by A; needs synthetic clock |
| 28 | `recovery_authority_policy` | 2 | bounded authorization/effect 0.1 | cognous-control-plane | research_qualification (current (2 parametrized refs)) | CURRENT_REQUIRED | no | self; blocked by A |
| 29 | `recovery_authority_evidence` | 2 | bounded authorization/effect 0.1 | cognous-control-plane | research_qualification (current (2 parametrized refs)) | CURRENT_REQUIRED | no | self; blocked by A |
| 30 | `recovery_authority_approval` | 2 | bounded authorization/effect 0.1 | cognous-control-plane | research_qualification (current (2 parametrized refs)) | CURRENT_REQUIRED | no | self; blocked by A |
| 31 | `control_plane_shared_store_concurrency` | 6 | bounded authorization/effect 0.1 | cognous-control-plane | control_plane_store (current) | CURRENT_REQUIRED | no | self (rc 0, 20 tests in PR #270 local reproduction) |
| 32 | `control_plane_store_restart_and_interruption` | 3 | bounded authorization/effect 0.1 | cognous-control-plane | control_plane_store (current) | CURRENT_REQUIRED | no | self (rc 0, 20 tests in PR #270 local reproduction) |
| 33 | `control_plane_store_fail_closed` | 6 | bounded authorization/effect 0.1 | cognous-control-plane | control_plane_store (current) | CURRENT_REQUIRED | no | self (rc 0, 20 tests in PR #270 local reproduction) |
| 34 | `evidence_pack_persistence_compatibility` | 8 | Evidence Pack import path of a superseded CP persistence-repair generation (version string per worker audit: 0.3.1; not verified by writer) | cognous-governance-evidence-pack | evidence_pack_persistence (historical (8/8)) | UNRESOLVED (invariant CURRENT_REQUIRED (negatives and provenance non-promotion)) | yes | PARTIAL analogs; CP store invariants covered at p2 by control_plane_store scenarios |
| 35 | `replay_persistence_producer_compatibility` | 8 | Reconstruction Bundle 0.2.0 (historical persistence producer generation) | cognous-replay-bundle | replay: test_producer_v2_persistence.py (historical (8/8 under PR #270 labelling; main labelling is 'current' stage replay)) | UNRESOLVED (invariant CURRENT_REQUIRED (invariant) / HISTORICAL_ONLY (pin parts)) | yes | PARTIAL analogs |

Per-scenario invariants (positive/negative), consumer relationship, continuing relevance, evidence and rationale, caveats and the verbatim matrix test refs are in the data file. Detail for the five UNRESOLVED scenarios:

- **original_artifact_continuity**: Invariant CURRENT_REQUIRED; as-run evidence is historical-generation. Only 1 of 13 tests in qualification/test_merged_artifacts.py asserts HT revisions. Required before reclassification: p2-pinned variant of the 3 refs passing at exact pins, independently reviewed. Profile as run: security-runtime-p2-20261018. Replacement: PARTIAL: hub_release_gate refs exist at lock (blocked by A, 68 setup errors); durable redelivery retrieval has no current-pin test. Caveats: not covered at current pins: durable retrieval of original export on forced redelivery; EP/ODES integrity-without-inflation round trip against p2 producers.
- **post_effect_evidence_recovery**: Invariant CURRENT_REQUIRED. Gap: 'derivative evidence is distinct and original stays unavailable' has current coverage only in historical-env refs and orphaned test_recovery_export_separation.py. Profile as run: security-runtime-p2-20261018. Replacement: PARTIAL: gax_reference refs at lock (blocked by A); research_qualification recovery tests (blocked by A). Caveats: none.
- **observation_repair_lifecycle**: Invariant CURRENT_REQUIRED. The 4 producer-v2 refs lean HISTORICAL_ONLY only if the S2 baseline names the p2 consumer lifecycle tests plus a p2 live round trip as replacement. Profile as run: security-runtime-p2-20261018. Replacement: PARTIAL: GAX refs at lock (blocked by A); consumer lifecycle tests at lock; no gated live-producer round trip at p2 in reference_release. Caveats: producer generation script asserts manifest 46c950be (lock pins fa170815): 'wrong pinned producer revision'; ODES lifecycle contract 0.1.0-draft is not adopted.
- **evidence_pack_persistence_compatibility**: Strong HISTORICAL_ONLY lean for the pin parts only; as-written tests stay UNRESOLVED. Would allow HISTORICAL_ONLY: S2 baseline states CP persistence repair is superseded by 0a41faa9, accepts p2 consumer tests as replacement for the import-side negatives, and EP/Replay owners confirm in writing no consumer relies on the generation. No p2 import-side non-mutation test confirmed. Profile as run: as run: Replay 043830b5 + CP 248d8996 + runtime 177354e9 + manifest 46c950be (not selected by lock). Replacement: PARTIAL analogs; CP store invariants covered at p2 by control_plane_store scenarios. Caveats: none.
- **replay_persistence_producer_compatibility**: Not on the builder's list of four; arises because PR #270 moves test_producer_v2_persistence.py into the historical-extras invocation. Verify against real scenario-results.json (not retrievable by workers). Profile as run: as run: CP 248d8996, executor 177354e9 (not selected by lock). Replacement: PARTIAL analogs. Caveats: none.

Caveats on CURRENT_REQUIRED rows: `bad_evidence` and `bitrep_index_non_authorizing` (bitrep source not inspected); `replay_import_redaction_no_effect` and `test_provenance` (fixtures are Replay f63ce914 bundles, re-fixture on p2 recommended; test_provenance skips when UPSTREAM_* unset and a skip blocks the gate); `research_replanned_equivalent_intent` (characterization only, JCEE note source, AD-10). Many CURRENT_REQUIRED rows depend on GAX or research stages that PR #270 reports as blocked by failure class A (blocked is not obsolete).

### 2.2 Stage groups (Qualification runner stages)

| ID | Stages | Contract | Owner | Matrix-ref'd | Class | AN | Replacement |
|---|---|---|---|---|---|---|---|
| SG-01 | control_plane, control_plane_store | bounded authorization/effect 0.1 | cognous-control-plane | yes | CURRENT_REQUIRED | no | self |
| SG-02 | governed_transport | governed-message-transport 0.1.0 | cognous-governed-exchange | yes | CURRENT_REQUIRED | no | self |
| SG-03 | gax_observation_repair, gax_reference, governed_transport_integration | ODEX-GAX/IMX 0.1.0; governed-message-transport 0.1.0 | cognous-governed-exchange | yes | CURRENT_REQUIRED | no | self (blocked by failure class A) |
| SG-04 | gax_public_runtime_artifacts | GAX retained artifacts 1.1.0 | cognous-governed-exchange | yes | UNRESOLVED | yes | partial: hub_release_gate refs at lock; no p2-pinned variant |
| SG-05 | research_qualification | none adopted (JCEE TN001 source) | cognous-stack-qualification | yes | CURRENT_REQUIRED | no | self (blocked by A; synthetic clock needed) |
| SG-06 | hub_release_gate | GAX retained artifacts 1.1.0 (commitment negatives); gate integrity | cognous-stack-qualification | no | CURRENT_REQUIRED | no | self (68 setup errors, class A) |
| SG-07 | replay (lock tests) | Reconstruction Bundle 0.2.0 | cognous-replay-bundle | yes | CURRENT_REQUIRED | no | self |
| SG-08 | replay: relocated test_pinned_integration.py | Reconstruction Bundle 0.2.0 (historical pairing) | cognous-replay-bundle | yes | UNRESOLVED | yes | exists elsewhere: Replay test_programme2_n4_and_pairing, test_programme2_profiles |
| SG-09 | replay-producer-v2, replay-published-results | executor producer profile 2.0.0; Reconstruction Bundle 0.2.0 | cognous-replay-bundle | yes | UNRESOLVED | yes | Replay lifecycle tests at lock (see scenario 24) |
| SG-10 | evidence_pack (lock tests + relocated test_importer.py) | imported Evidence Pack schema 0.2.0 | cognous-governance-evidence-pack | yes | CURRENT_REQUIRED | no | self; fixtures from Replay f63ce914 |
| SG-11 | evidence_pack: relocated test_accepted_executor_profile.py | Evidence Pack legacy executor evidence (consumer-managed, revision-pinned per runner summary) | cognous-governance-evidence-pack | yes | UNRESOLVED | yes | none located |
| SG-12 | evidence_pack_v2 | executor producer profile 2.0.0 (earlier generation) | cognous-governance-evidence-pack | yes | UNRESOLVED | yes | consumer lifecycle tests at lock |
| SG-13 | evidence_pack_persistence | Evidence Pack import path of superseded CP persistence repair | cognous-governance-evidence-pack | yes | UNRESOLVED | yes | see scenario 34 |
| SG-14 | odes (lock tests + test_odes_stack_export.py) | ODES implementation profile 0.2.6 (security-runtime P2 candidate) | open-decision-evidence-standard | yes | CURRENT_REQUIRED | yes | self |
| SG-15 | odes: relocated test_accepted_replay_profile.py | ODES accepted Replay profile (earlier generation) | open-decision-evidence-standard | yes | UNRESOLVED | yes | none located |
| SG-16 | odes-producer-v2 | executor producer profile 2.0.0 (earlier generation) | open-decision-evidence-standard | yes | UNRESOLVED | yes | ODES test_lifecycle_* at lock |
| SG-17 | replay_merged | historical tuple merged-producers-v1 | cognous-replay-bundle | no | HISTORICAL_ONLY | yes | Replay test_refusal_journal f5b/p4 cross-generation; test_programme2_n4_and_pairing; test_programme2_profiles |
| SG-18 | evidence_pack_merged | historical tuple merged-producers-v1 | cognous-governance-evidence-pack | no | HISTORICAL_ONLY | yes | EP test_p2_generation |
| SG-19 | odes_merged | historical tuple merged-producers-v1 | open-decision-evidence-standard | no | HISTORICAL_ONLY | yes | ODES test_security_cloud_regressions cross-generation tests |
| SG-20 | bitrep_verification | verification contract v1 | cognous-evidence-attestation | yes | CURRENT_REQUIRED | yes | self |
| SG-21 | index_bitrep_binding, index_local_chain | local blockchain reference 0.1.0 | cognous-evidence-registry | yes | CURRENT_REQUIRED | no | self (green in PR #270 local reproduction) |
| SG-22 | representative x2 (transported reference) | p2 chain end-to-end | cognous-open-control-stack | no | CURRENT_REQUIRED | no | self (blocked by A) |
| SG-23 | preflight replay, preflight odes | n/a | cognous-stack-qualification | no | CURRENT_REQUIRED | no | self |
| SG-24 | openshell_mock | OpenShell adapter 0.1.0 (mocked) | cognous-execution-runtime | no | CURRENT_REQUIRED | no | self |
| SG-25 | gax_historical_artifacts, executor_refusal, replay_refusal, odes_refusal, evidence_pack_refusal, gax_refusal | typed-refusal tuple (CP c7f122ba, runtime 309e194c, Replay 83fbaf2a) | multiple | no | HISTORICAL_ONLY | yes | p2 refusal tests (native suite) |

Source/version, invariant and rationale per stage are in the data file. Stage-to-file mapping verified live at Qualification 8e5e4ac3 `reference_release.py`; the runner revision pinned by the Hub aggregate is 4a57a309 (a65c0a30 in PR #263) and was not diffed (UNVERIFIED).

### 2.3 Other test groups and fixtures

| ID | Item | Contract | Owner | Class | AN | Rationale |
|---|---|---|---|---|---|---|
| OT-01 | GAX test_profile_under_a_historical_profile_raises_and_cannot_elevate; test_historical_profiles_reject_runtime_authority_options | runtime authority profile 0.1 (GAX side) | cognous-governed-exchange | CURRENT_REQUIRED | no | Authority-absence/substitution refusal; component-local in GAX CI; no Qualification/Hub run at e78a7be3. |
| OT-02 | GAX test_historical_profiles_are_unchanged_no_new_keyword_is_passed | GAX historical profiles (persistence-v1, merged-producers-v1, typed-refusal) | cognous-governed-exchange | UNRESOLVED | yes | Lean LEGACY_SUPPORTED: README says 'historical, opt-in'; no consumers or duration named. |
| OT-03 | Older duplicate GAX tests/test_gax_public_runtime_artifacts.py (pins 043830b5/248d8996) | GAX retained artifacts 1.1.0 (older generation) | cognous-governed-exchange | HISTORICAL_ONLY | yes | PROPOSED only after the pin-free tests are re-homed (scenario 19). |
| OT-04 | test_recovery_export_separation.py (3 fn, 20 parametrized cases) | GAX retained artifacts 1.1.0; recovery | cognous-governed-exchange | UNRESOLVED | yes | Orphaned: in no reference_release stage; only test of this property at export level; CURRENT_REQUIRED candidate; do not drop with the HT. |
| OT-05 | test_merged_store.py; tests/test_control_plane_store_adoption.py | HT store adoption | cognous-governed-exchange | HISTORICAL_ONLY | yes | PROPOSED; orphaned (no stage); CP store invariants covered at p2 by scenarios 31-33. |
| OT-06 | GAX tests/test_real_pinned_stack.py | authenticated source loader (GAX main only) | cognous-governed-exchange | UNRESOLVED | yes | Opt-in (GAX_REAL_STACK_ROOT); defaults to provisional r2 profile (NOT ADOPTED); skipped when unset; not run by Qualification. |
| OT-07 | Replay f63ce914 example bundles supplied as UPSTREAM_* fixtures | pinned fixture generation | cognous-replay-bundle | HISTORICAL_ONLY | yes | As a pinned fixture generation only; consuming behaviour tests are CURRENT_REQUIRED and need p2 re-fixturing. |
| OT-08 | Manifest fixture refund_integration_v1_1.manifest.json at 46c950be vs lock fa170815 | historical manifest pin | cognous-action-manifest | HISTORICAL_ONLY | yes | Pin only. Do not repin from the runner (PR #270 item B: declaring the tuple needs a decision). |
| OT-09 | Synthetic fixture timestamps (EVAL 2026-08-08T01:00:00Z; NOW 2026-10-05T19:00Z; 2026-10-06T12:00Z) | n/a | multiple | CURRENT_REQUIRED | no | Time-bomb risk, not a historical marker. Explicit synthetic clock is the PR #270 fix; it does not qualify freshness/expiry/revocation behaviour. |
| OT-10 | Historical-profile constants inside current Replay importers (CONTROL_PLANE_SUPPORTED_V2_REVISIONS, etc.) | Replay legacy generations | cognous-replay-bundle | UNRESOLVED | yes | Explicit but duration-less, consumer-less backward-compat statement. |

### 2.4 CI workflows and required checks

| ID | Item | Facts | Class | AN | Rationale |
|---|---|---|---|---|---|
| GW-01 | cross-component / aggregate (ruleset-required) | FAILS on Hub main-derived PRs (e.g. #264 head 0e475815) at Qualification pin 4a57a309: unauthenticated clone of retired PRP/RI repos; passes at #263 head a00a02ac (Qualification a65c0a30) | UNRESOLVED | yes | Retirement/relabel needs S4 accepted policy; a failing required check cannot be relabelled non-applicable (plan s2). |
| GW-02 | merged-chain-candidate.yml | scope 'bounded workflow integration; not the complete matrix'; not in ruleset | HISTORICAL_ONLY | yes | PROPOSED only. |
| GW-03 | remediation-candidate.yml; remediation-full-reference.yml | path-filtered PR trigger; not in ruleset (ruleset 'aggregate' matches full-candidate-release job id; remediation's job is remediation-aggregate) | HISTORICAL_ONLY | yes | PROPOSED only. |
| GW-04 | w7-* workflows (5) and profiles/w7-bounded-v1-component-lock.candidate.json | 'governor_acceptance_pending'; 'not selected historical core lock'; not in ruleset | UNRESOLVED | yes | Authority is the Governor. |
| GW-05 | reference-release.yml ('Reference release evidence') | not a required context; fails on Hub main pushes (e.g. 985dfe46) and on #263 head | CURRENT_REQUIRED | yes | PROPOSED: the check Qualification #269/#270 target; applicability decided by S4. |
| GW-06 | release-integrity (cross-component / integrity), contract-artifact-verification (verify 3.11/3.12), preview-entry-audit (preview-audit) | ruleset-required; green at #263 head | CURRENT_REQUIRED | no | Outside this crosswalk's historical scope; recorded for completeness. |
| GW-07 | GAX 'Merged consumer chain' workflow | GAX ruleset lists no required status contexts (advisory by rules); only place the 7-component HT pins are declared besides tests (PR #270 item B) | UNRESOLVED | yes | Declared CI gate on every GAX PR. |

Hub ruleset 25195893 requires exactly the five contexts listed in 1.1; only `cross-component / aggregate` runs the historical-tuple profile. Qualification and GAX rulesets list no required status contexts (worker read; org-level rulesets not enumerated).

### 2.5 Counts

| Group | CURRENT_REQUIRED | LEGACY_SUPPORTED | HISTORICAL_ONLY | UNRESOLVED | Authority needed |
|---|---|---|---|---|---|
| scenarios | 30 | 0 | 0 | 5 | 6 |
| stage_groups | 13 | 0 | 4 | 8 | 14 |
| other_test_groups | 2 | 0 | 4 | 4 | 8 |
| ci_gate_records | 2 | 0 | 2 | 3 | 6 |
| all_records | 47 | 0 | 10 | 20 | 34 |

## 3. Current-contract baseline (S2 proposal)

Status: PROPOSED S2 baseline; contract identifiers are lock-declared interface names or source-native ids; none is an adopted contract revision.

**Supported profile:** `security-runtime-p2-20261018` (selected by Hub component-lock.json runtime_profile @985dfe46 (identical in PR #263 head)). p2 treated as current because it is the lock profile and the plan names it; r2/r3 (security-runtime-current-20261031 r2/r3; Hub profiles/current-stack-integration-candidate-20261102-r3.json) are labelled PROVISIONAL, NOT ADOPTED. AD-02.

**Tuple (lock pins):** control_plane `0a41faa9`; runtime (moltbot_safe) `ec728da6`; replay_bundle `028f63d1`; evidence_pack `a3ebbb90`; odes `e86a25a1`; gax_imx_transport `7f7569b0`; action_manifest `fa170815`; constitutional_authority `9b5ab721`; bitrep `981036c3`; the_index `b2485998`; verifier `c0b8ba1f`.

**What GAX main `e78a7be3` adds (carried from worker audit; AD-13):** (1) #63/#65 r2/r3 current-stack profiles (provisional, NOT ADOPTED) (2) #64/#66 authenticated in-process git object reader and immutable authoritative manifest for all strict profiles including p2 (pins and profile semantics unchanged) (3) #67 AcceptedGaxRecipientAdapter carries trusted runtime_authority_profile under security-runtime-* profiles p2 constants: still equal the lock tuple at e78a7be3 (gax_ref_runtime.py). Qualification evidence: none: no Qualification run references e78a7be3 (worker grep of Qualification main 8e5e4ac3). Tests: component-local only: tests/test_adapter_runtime_authority_profile.py (19), test_authenticated_source.py (26), test_authenticated_manifest.py (21).

**Evidence basis:** Retained exact-lock-tuple run: Qualification results/v1-validation/v1-2026-10-16-a/g8-r10-39690459403 (Qualification 8e5e4ac3; harness 4a57a309). Job-level PASS verified by workers; per-test junit only for native p2 suite and ODES. Evidence at other tuples is labelled and NOT counted as COVERED.

**Contract structures:** Existing structures reused, no second registry: lock interfaces strings, Qualification contract-matrix.json (cognous.contract-matrix/1: 1 contract, 2 boundaries), Hub qualification-surfaces-v1.json (2 optional structural contracts). ODES draft contracts (17, all 0.1.0-draft, not frozen) exist; ODES-INTERCOMPONENT-CONTRACTS.md is rev 0.2 draft and says none of it applies until V1 closes. Whether they form the S2 baseline is AD-05.

### 3.1 Guarantees by obligation category

Status key: COVERED = test exists at the pin and a retained exact-pin PASS exists with positive and negative cases; PARTIAL = some cases, characterisation of a known limit, or a different tuple; GAP = no test, or tests assert the obligation is NOT met. Roll-up is the lowest sub-status; the audit's own headline is kept alongside. Statuses are builder-proposed from worker audits and are not independently reviewed.

#### 1. Trusted runtime authority profiles: roll-up PARTIAL (audit headline: COVERED at lock tuple; PARTIAL at GAX main)

- **1a COVERED**: Trusted profile semantics across CP/runtime/Replay/Pack/ODES at lock tuple
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_runtime_authority.py::test_required_profile_cannot_be_downgraded_at_execute`; `cognous-control-plane@0a41faa97269::tests/test_runtime_authority.py::test_holder_cannot_reclassify_action`; `cognous-control-plane@0a41faa97269::tests/test_runtime_authority.py::test_known_denial_overrides_cache`; `cognous-control-plane@0a41faa97269::tests/test_runtime_authority.py::test_journal_write_failure_never_dispatches`; `cognous-control-plane@0a41faa97269::tests/test_authority_context_versions.py::test_other_versions_are_refused`; `cognous-execution-runtime@ec728da6dc30::tests/test_effective_grant.py::*`; `cognous-governed-exchange@7f7569b02666::tests/test_exchange_input_and_source_repairs.py::*`
  - Note: Qualification native p2 suite suites/security-runtime/test_security_runtime_chain.py: 36/36 PASS x2 at lock pins in retained run g8-r10-39690459403 (Qualification 8e5e4ac3 results dir; harness 4a57a309); it is not a Hub-required check.
- **1b PARTIAL**: GAX transport adapter carries trusted runtime_authority_profile under p2
  - Current tests: `cognous-governed-exchange@e78a7be3cb4e::tests/test_adapter_runtime_authority_profile.py::*`
  - Gap: At lock pin 7f7569b0 the transport path under p2 has no test (Qualification's own p2 profile limitation)
  - Gap: GAX main e78a7be3 tests are component-local; no Qualification or Hub run at e78a7be3
  - Gap: runner-side supply of runtime_authority_profile absent (PR #270 class A)
- **1c PARTIAL**: Authority-source observation contract (synthetic-authority-observation/1)
  - Current tests: `cognous-open-control-stack@985dfe461241::tests/test_resolver_assurance.py::*`
  - Gap: Run status at Hub 985dfe46 not retained; verify (3.11/3.12) green on main runs Hub tests

#### 2. Authentication / identity: roll-up GAP (audit headline: PARTIAL)

- **2a COVERED**: Resolver authentication, attestation verification negatives
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_resolver_authentication_and_destination_binding.py::*`; `cognous-evidence-attestation@981036c31585::tests/test_verification.py::*`; `cognous-evidence-attestation@981036c31585::tests/test_authority_digest_custody_profile.py::*`
  - Note: matrix rows ER-01-1..5 PASS in g8 (retained run); bitrep tests job-level PASS.
- **2b GAP**: Adapter identity, sender-to-actor binding, forged-consistent exchange message, HMAC-only attestation, asserted rule-revision signer, registry issuer/key admission
  - Note: Thin: mostly known-limit characterisations
  - Gap: adapter identity is an id string (test_add_molt_verify_e6_adapter_binding_is_id_string_not_code_digest characterises)
  - Gap: SCN-C13: HMAC and content digest only
  - Gap: rule_revision signer is an asserted, unauthenticated name
  - Gap: migrated OCS Registry (cognous-ocs-registry 6b96a9a6) issuer/key admission tested by no Qualification test
  - Gap: wiki S3-tuple known limits (sender label not bound to actor; forged consistent message accepted) are at another tuple

#### 3. Scoped authorization: roll-up GAP (audit headline: PARTIAL)

- **3a COVERED**: Exact finite scope, tenant binding, substitution, delegation-cannot-widen
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_bounded_authorization.py::test_tenant_only_substitution_cannot_reuse_authorization`; `cognous-control-plane@0a41faa97269::tests/test_bounded_authorization.py::test_delegation_cannot_widen_or_survive_invalid_parent`; `cognous-control-plane@0a41faa97269::tests/test_bounded_authorization.py::test_substitution_prevents_effect`; `cognous-execution-runtime@ec728da6dc30::tests/test_permissions.py::*`
  - Note: job-level PASS at exact pins; per-test junit not inspected by workers
- **3b GAP**: Known limits asserted as limits (evidence tenant column, cumulative counters per grant id, sub-delegation unsupported, exchange route has no tenant concept)
  - Current tests: `cognous-execution-runtime@ec728da6dc30::tests/test_evidence_tenant_known_limit.py::*`; `cognous-control-plane@0a41faa97269::tests/test_known_limits.py::*`
  - Gap: tests assert the limit, not the obligation
  - Gap: matrix SCN-D02, C01, C02, C09, C18, C17 INCONCLUSIVE at exact tuple

#### 4. Expiry / revocation: roll-up GAP (audit headline: COVERED for grant/evidence; PARTIAL for decision age and identity/mandate status)

- **4a COVERED**: Grant and evidence expiry and revocation hold before effect
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_bounded_authorization.py::test_revocation_expiry_stale_status_and_policy_change_hold`; `cognous-control-plane@0a41faa97269::tests/test_time_instant.py::test_policy_gate_authority_expiry_is_strict_and_exclusive`; `cognous-execution-runtime@ec728da6dc30::tests/test_atomic_grant_status_and_envelope_binding.py::*`
  - Note: matrix ER-05-2 and SR-1 PASS in g8; terminal revocation is an opt-in profile (default path characterised permissive)
- **4b GAP**: Decision age, identity/mandate status change at claim consumption, freshness-before-criterion ordering
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_known_limits.py::*`
  - Gap: decision age not consulted at execution (known-limit tests)
  - Gap: 6 strict xfail probes: suites/v1-probes/test_authority_ra_probes.py (freshness ordering)
  - Gap: these known-limit tests count as PASS in component jobs
- **4c PARTIAL**: C0 check-to-commit race
  - Gap: residual by design (matrix SCN-C07 INCONCLUSIVE; RT c0_post_check_pre_commit_race_is_in_doubt_not_atomicity_claim)

#### 5. Fail-closed refusal: roll-up GAP (audit headline: COVERED (negative-heavy))

- **5a COVERED**: Typed refusal, journaled denial, no dispatch on resolver/journal failure
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_runtime_authority.py::test_journal_write_failure_never_dispatches`; `cognous-control-plane@0a41faa97269::tests/test_policy_gate.py::*`; `cognous-control-plane@0a41faa97269::tests/test_refusal_does_not_poison.py::*`; `cognous-execution-runtime@ec728da6dc30::tests/test_security_admission.py::*`
  - Note: native p2 test_denial_preserves_actual_journal_refusal_and_destination[6 reasons] PASS at lock pins in g8
- **5b GAP**: Human override; refusals before acceptance stored; selector fail-closed on unknown reachability
  - Gap: Qualification coverage map H01 DEFERRED, H02 unmapped
  - Gap: wiki known limit: refusals before acceptance returned not stored (other tuple)
  - Gap: 'unknown reachability fails closed to broader testing' (plan S3) is not enforced by any selector today

#### 6. Evidence provenance / integrity: roll-up GAP (audit headline: PARTIAL)

- **6a COVERED**: Digest/pin/relabel/tamper negatives across Replay, Pack, ODES, GAX
  - Current tests: `cognous-replay-bundle@028f63d1c001::tests/test_programme2_profiles.py::*`; `cognous-replay-bundle@028f63d1c001::tests/test_programme2_n4_and_pairing.py::*`; `cognous-governance-evidence-pack@a3ebbb90559a::tests/test_security_review_hardening.py::*`; `cognous-governance-evidence-pack@a3ebbb90559a::tests/test_p2_generation.py::*`; `open-decision-evidence-standard@e86a25a1d660::tests/test_security_cloud_regressions.py::*`
- **6b GAP**: ODES vs Replay lost-ack and prior-absence export at exact lock tuple
  - Note: Failing evidence preserved; not waived by this document
  - Gap: g8: ODES FAIL 4 of 3094: tests/test_restriction_semantics.py::test_control_legacy_export_is_digest_identical_to_the_retained_example, ::test_explicit_export_end_to_end; tests/test_result_classification.py::test_control_producer_v2_examples_pass_the_semantic_layer[lost_ack.package.json | prior_absence.package.json]
  - Gap: error: pinned Replay semantic validation failed: an unknown result cannot carry a validated applied/partial observation
  - Gap: test_explicit_export_end_to_end matches no mandatory selector so freeze verdict stayed PASS (regex-selected matrix)
  - Gap: three are declared limits under ER-09-1
  - Gap: ODES main 9d6f9edc effect on these: UNKNOWN
- **6c PARTIAL**: Provenance authenticity (source-asserted failure references, HMAC/digest only)
  - Gap: native test_failure_reference_is_not_durability_proof characterises source_asserted_not_independently_verified
- **6d GAP**: Migrated OCS Registry (cognous-ocs-registry 6b96a9a6)
  - Gap: in no lock and no harness; no Qualification test

#### 7. Durable state: roll-up GAP (audit headline: PARTIAL)

- **7a COVERED**: CP record store concurrency, termination, corruption, unsupported platform
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_record_store_concurrency.py::*`; `cognous-execution-runtime@ec728da6dc30::tests/test_recovery_resolution.py::*`
  - Note: in Hub remediation authority batch
- **7b GAP**: Attempt state-machine enforcement, external anchor, OS-level kill routes A/C, ingress limiter
  - Current tests: `cognous-execution-runtime@ec728da6dc30::tests/test_attempt_transition_characterisation.py::*`
  - Gap: known-limit tests assert no state machine
  - Gap: matrix SCN-C08, D06, D07 INCONCLUSIVE
  - Gap: Hub protected-destination/sqlite tests cover the Hub reference profile, not the p2 chain

#### 8. Recovery / redelivery: roll-up GAP (audit headline: COVERED for lost-ack/crash/redelivery; PARTIAL for partial delivery and observer independence)

- **8a COVERED**: Lost-ack, crash, redelivery on routes A/B/C; no replacement effect
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_bounded_authorization.py::test_lost_ack_restart_reconciles_without_duplicate`; `cognous-control-plane@0a41faa97269::tests/test_bounded_authorization.py::test_partial_delivery_holds_instead_of_blind_retry`; `cognous-replay-bundle@028f63d1c001::tests/test_route_b_recovery_import.py::*`
  - Note: native p2 [lost_ack|crash|ownership|revoked] PASS at lock pins; matrix ER-05-3 and ER-07-4 PASS
- **8b PARTIAL**: Partial delivery, observer independence
  - Gap: matrix SCN-D05 INCONCLUSIVE (no native multi-part operation); SCN-C06; coverage map D04, D05 PARTIAL
- **8c GAP**: ODES lost-ack package export; transport adapter recovery under p2
  - Gap: see 6b and 1b

#### 9. Idempotency / duplicate-effect prevention: roll-up GAP (audit headline: COVERED for same effect-id; GAP for same business intent (by documented design))

- **9a COVERED**: Same effect-id duplicate prevention
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_bounded_authorization.py::test_duplicate_submission_does_not_duplicate_effect`; `cognous-governed-exchange@7f7569b02666::tests/test_governed_message_transport.py::*`
- **9b GAP**: Same-business-intent duplicate on default routes
  - Note: documented design limit; AD-11
  - Gap: suites/v1-scenarios/test_add_c2c_bi.py asserts the second same-intent effect is NOT deduplicated (residual_exposed=true)
  - Gap: refund_intent_profile opt-in; not composable with route A
- **9c PARTIAL**: Operation identity / dedupe-ttl (opt-in profiles)
  - Current tests: `cognous-control-plane@0a41faa97269::tests/test_dedupe.py::*`; `cognous-control-plane@0a41faa97269::tests/test_operation_identity.py::*`
  - Gap: off by default; whether part of the current contract set is AD-14

#### 10. Permitted-effects boundaries: roll-up GAP (audit headline: PARTIAL)

- **10a COVERED**: Exact target/amount/effect-limit matching
  - Current tests: `cognous-execution-runtime@ec728da6dc30::tests/test_permissions.py::*`; `cognous-execution-runtime@ec728da6dc30::tests/test_exact_target_matching.py::*`; `cognous-control-plane@0a41faa97269::tests/test_amount_substitution.py::*`; `cognous-action-manifest@fa170815ef96::tests/test_exact_identifiers.py::*`
  - Note: matrix ER-04-1/-2 PASS in g8
- **10b GAP**: Bypass: raw SQL by database holder, OpenShell isolation, credential broker, prohibited access seeding
  - Gap: matrix SCN-D09, C10, C11, C23 INCONCLUSIVE at exact tuple
  - Gap: live OpenShell suites environment-gated

#### 11. Input / output conformance: roll-up GAP (audit headline: COVERED for schemas and examples; PARTIAL for p2 boundary contracts)

- **11a COVERED**: Schema, example, input-bound conformance
  - Current tests: `cognous-replay-bundle@028f63d1c001::tests/test_importers.py::*`; `open-decision-evidence-standard@e86a25a1d660::tests/test_validator_input_hardening.py::*`; `cognous-governance-evidence-pack@a3ebbb90559a::tests/test_input_admission.py::*`
  - Note: matrix ER-04-*, ER-07-1/-2 PASS in g8
- **11b PARTIAL**: p2 boundary contracts machine-versioned
  - Gap: Hub contracts/qualification-surfaces-v1.json covers only semantic-handoff/1 and synthetic-authority-observation/1
  - Gap: Qualification contract-matrix.json: 1 contract (execution-attempt-lifecycle 0.1.0-draft), 2 boundaries
- **11c GAP**: Unknown member silently dropped by executor export (SCN-C12); old-producer/new-reader matrix (inventory row X-13 PLAN)
  - Gap: SCN-C12 INCONCLUSIVE
  - Gap: no test found for X-13 at Qualification 8e5e4ac3 (inventory dated 2026-10-19)

#### 12. Cross-component compatibility: roll-up GAP (audit headline: PARTIAL)

- **12a COVERED**: Pin/generation checks and p2 native chain at lock pins
  - Current tests: `cognous-replay-bundle@028f63d1c001::tests/test_programme2_n4_and_pairing.py::*`; `cognous-governance-evidence-pack@a3ebbb90559a::tests/test_p2_generation.py::*`; `open-decision-evidence-standard@e86a25a1d660::tests/test_security_cloud_regressions.py::*`
  - Note: native p2 suite 36/36 PASS at lock pins in g8 (suite_generation p2 inferred from profile; job env not read)
- **12b GAP**: GAX main e78a7be3 and the current-stack tuple exercised on the Qualification harness
  - Gap: grep of Qualification main finds no reference to e78a7be3
  - Gap: r2/r3 profile is selected:false / NOT ADOPTED
- **12c GAP**: p2 native suite as a required check; inventory X-12 (vendored-contract drift), X-14 (exact-chain consistency)
  - Gap: native suite runs in the Qualification v1 validation controller, not a Hub-required context
  - Gap: X-12 PARTIAL, X-13 PLAN, X-14 PLAN, X-11 FAIL (inventory 2026-10-19)

#### 13. Security-negative / adversarial: roll-up GAP (audit headline: PARTIAL)

- **13a COVERED**: Retained lock-tuple negatives (native p2 about 20 of 36 cases; probes-* jobs; v1-scenarios negatives)
  - Note: job-level PASS at exact pins in g8; 6 control-plane probes xfail
- **13b GAP**: Adversarial batch T01-T20 and verifier mutation at the lock tuple
  - Note: coverage audit status was UNKNOWN; recorded here as GAP because no evidence exists at the lock tuple
  - Gap: T01-T20 last run at r10 pins (CP 2bac7875); feed no gate; UNKNOWN whether they pass at 0a41faa9/ec728da6
  - Gap: verifier mutation X-08 NOT_RUN_HERE; R1B/R1C mutations bound to current-stack tuple
- **13c GAP**: Known-limit negatives (sender-to-actor, forged consistent message, decision age, business-intent duplicate)
  - Gap: all are known-limit characterisations

### 3.2 Top gaps carried forward (ranked)

1. ODES vs Replay boundary fails at the exact lock tuple on lost-ack and prior-absence exports; test_explicit_export_end_to_end matches no mandatory selector (regex-selected matrix) and the verdict stayed PASS.
2. Mandatory evidence is name/regex-selected (rows like 'min N tests matching revok|expir'), not contract-mapped; Hub qualification-surfaces-v1.json has 2 structural contracts only.
3. No evidence at the tuple actually in use: GAX main e78a7be3 has component-local tests only; newer security evidence (R1B/R1C/S3 wiki) is at the current-stack tuple (CP b19c47dd) and is non-transferable; the lock's qualification_evidence (run 37694032916) predates the p2 pins; migrated registry untested and unlocked.
4. Authentication/identity is thinly negative-covered (id-string adapter identity, asserted signer names, HMAC-only, sender label unbound).
5. Duplicate-effect prevention is effect-id only on default routes; same-intent duplicates are a documented residual; operation-identity/dedupe/refund-intent/terminal-revocation are opt-in and off by default.
6. Temporal/status limits are asserted rather than enforced (decision age, claim consumption vs identity/mandate status, C0 race, freshness ordering xfail).
7. Adversarial batch T01-T20 and verifier mutation have no run at the lock tuple and feed no gate (stale; ran at r10 tuple).
8. Restore/durability limits at exact tuple: no external anchor (D07), no OS-level kill routes A/C (C08), no ingress limiter (D06).
9. Required GitHub checks do not include the p2 native suite; cross-component / reference is red on Hub main and on #263 head; the four qualify-linux batches are named file lists.
10. Matrix identity: at the lock tuple (g8) the 40 Qualification SCN-* rows are 0 PASS, 27 INCONCLUSIVE, 13 NOT RUN; that is a different artifact from the Hub 35-scenario acceptance matrix.

One further fact on selection: the Hub aggregate resolves the 35-scenario matrix by `suite::test` name; a stage result under a historical generation can satisfy a scenario that reads as a current claim (PR #270 item D). This crosswalk labels it and does not edit the matrix.

## 4. Frozen candidate mapping (FOR INDEPENDENT REVIEW)

**Rule: Historical PASS is never a current PASS. Do not promote. Do not weaken. Original failing evidence is preserved.** Candidates below are proposals; none is effective; every item remains gating until a competent authority acts.

Preconditions before any gate change: S2 names a current replacement for each continuing invariant, passing at exact pins, independently reviewed; owners confirm in writing absence of reliance (AD-01); S4 shadow comparison against a frozen tuple; competent authority accepts the policy change (AD-15); a reviewer verdict is not adoption.

| Record | Proposed | Mapping | Decisions | Status |
|---|---|---|---|---|
| observation_repair_lifecycle | UNRESOLVED | UNRESOLVED with stated lean; as-written test stays gating | AD-01, AD-02, AD-05 | FOR_INDEPENDENT_REVIEW |
| evidence_pack_persistence_compatibility | UNRESOLVED | UNRESOLVED with stated lean; as-written test stays gating | AD-01, AD-02, AD-05 | FOR_INDEPENDENT_REVIEW |
| SG-08 | UNRESOLVED | UNRESOLVED with stated lean; as-written test stays gating | AD-01, AD-03 | FOR_INDEPENDENT_REVIEW |
| SG-11 | UNRESOLVED | UNRESOLVED with stated lean; as-written test stays gating | AD-01, AD-06 | FOR_INDEPENDENT_REVIEW |
| SG-13 | UNRESOLVED | UNRESOLVED with stated lean; as-written test stays gating | AD-01, AD-03 | FOR_INDEPENDENT_REVIEW |
| SG-15 | UNRESOLVED | UNRESOLVED with stated lean; as-written test stays gating | AD-01, AD-06 | FOR_INDEPENDENT_REVIEW |
| SG-17 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-01, AD-03, AD-04 | FOR_INDEPENDENT_REVIEW |
| SG-18 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-01, AD-03, AD-04 | FOR_INDEPENDENT_REVIEW |
| SG-19 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-01, AD-03, AD-04 | FOR_INDEPENDENT_REVIEW |
| SG-25 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-01, AD-03, AD-04 | FOR_INDEPENDENT_REVIEW |
| OT-02 | UNRESOLVED | UNRESOLVED with stated lean; as-written test stays gating | AD-01 | FOR_INDEPENDENT_REVIEW |
| OT-03 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-01 | FOR_INDEPENDENT_REVIEW |
| OT-05 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-01, AD-03 | FOR_INDEPENDENT_REVIEW |
| OT-07 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-03 | FOR_INDEPENDENT_REVIEW |
| OT-08 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-03 | FOR_INDEPENDENT_REVIEW |
| GW-02 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-01, AD-12 | FOR_INDEPENDENT_REVIEW |
| GW-03 | HISTORICAL_ONLY | candidate for HISTORICAL_ONLY | AD-01, AD-12 | FOR_INDEPENDENT_REVIEW |

## 5. Open authority decisions (no decisions taken)

| ID | Question | Candidate authority | Affects |
|---|---|---|---|
| AD-01 | Is merged-producers-v1 / producer-v2 / persistence generation a continuing backward-compatibility commitment (identified consumers, duration)? | GAX, Replay, Evidence Pack, ODES owners; Architect | scenarios 19, 20, 24, 34, 35; SG-04, 08, 09, 11-13, 15-19, 25; OT-02..05, 10; GW-02, 03, 07 |
| AD-02 | Is security-runtime-p2-20261018 (Hub lock) or the provisional, NOT ADOPTED security-runtime-current-20261031 r2/r3 the 'current supported profile' for S2? | Architect | all rows; baseline in section 3 |
| AD-03 | Where is the frozen historical tuple (merged-producers-v1) declared: Hub profiles, Qualification workflow, or lock? (PR #270 item B) | Architect / Qualification owner | historical-tuple stages; GW-01 |
| AD-04 | Is the ruleset-required 'cross-component / aggregate' (full-release-candidate, historical tuple) still the intended gate? Are org-level rulesets present (not enumerated)? Is 'cross-component / reference' intended as gate of record? | Repository admin / gate-policy authority | GW-01, GW-05; SG-17..19 |
| AD-05 | Are the ODES 0.1.0-draft contracts (esp. execution-attempt-lifecycle) to be frozen/adopted as the S2 baseline? | ODES owner / Architect | scenario 24; contract identifiers; SG-09, 12, 14, 16 |
| AD-06 | Legacy unversioned Moltbot exports, bundle 0.1, Manifest 1.0, legacy executor evidence: consumers and duration. | Replay / Evidence Pack owners | SG-11, SG-15; OT-10 |
| AD-07 | Which matrix is the '35 scenarios' of record, and does the Hub lock qualification_evidence (run 37694032916, earlier tuple) apply to the p2 pins? | Lock owner / Architect | section 1.2 |
| AD-08 | Constitution adoption record for the Hub/OCS active configuration (pin 1c2e920f; publication is not adoption; no ADOPTION.md found in Hub). | Adopting authority | whole transition (plan s1) |
| AD-09 | Authority Context 0.1.0 (lock) vs 0.2.0 (document at pin); Governor acceptance of Authority Context and BitRep verification contract v1 ('proposed pending Governor review'). | Governor | authority contracts; SG-20 |
| AD-10 | May characterization scenarios whose source is a research note (JCEE TN001 v0.1.1) be promoted to requirements? | Architect / Qualification owner | scenarios 22, 23 |
| AD-11 | Do known-limit characterisation tests (decision age, same-intent duplicate, tenant evidence, attempt state machine) count as accepted limits or open obligations? | Architect / contract owners | baseline sub-obligations flagged GAP |
| AD-12 | Disposition of non-required failing 'cross-component / reference', W7 workflows (Governor acceptance pending), remediation and merged-chain workflows. | Gate-policy authority / Governor | GW-02..05 |
| AD-13 | Is GAX main e78a7be3 (authenticated loader #66, adapter profile forwarding #67) the S2 baseline GAX pin, or lock pin 7f7569b0? (pin transitions are plan S5) | Architect / lock writer | baseline; OT-06 |
| AD-14 | Are the opt-in Control Plane programme-2 profiles (operation-identity, rule-revision, freshness, terminal-revocation, dedupe-ttl, ...) part of the current supported contract set? | Control Plane owner / Architect | baseline idempotency/expiry sub-obligations |
| AD-15 | Identity of the S4 acceptance authority and CA18/CA21/CA23 reviewer/approver separation (plan S4 'acceptance authority' is undefined). | Architect | S4 |

## 6. Measured baseline (carried from the CI analysis worker; not re-measured)

Source: Qualification-side analysis worker (cc-ci-analysis), REST queries on 2026-11-04 against cogno-us/cognous-open-control-stack Actions; table values carried, not re-measured by the writer.

| Passing head | Date | aggregate | Required wall (s) | Required job-s |
|---|---|---|---|---|
| b2639fc0 | 2026-11-02 | success | 115 | 89 |
| 5d056743 | 2026-11-04 | success | 130 | 101 |
| a00a02ac (PR #263) | 2026-11-04 | success | 165 | 105 |

Median required critical path of passing runs: 130 s. 7 failing runs (aggregate failure at Qualification pin 4a57a309: unauthenticated clone of retired private repos) die after 50-317 s and run no tests; they are not a cost baseline. Other required workflows (median): integrity job 16 s, verify slowest job 37 s, preview-audit 14.5 s. Static work per run: 4 batch jobs, 19 suites x 2 repetitions = 38 suite runs, 35 scenarios, 115 refs (108 unique), 23 repos cloned per batch job (11 historical or previous roots).

**Executed test counts: NOT MEASURED.** per-suite JUnit exists only inside run artifacts; artifact blob host blocked by the sandbox proxy (CONNECT 403); job logs do not print per-suite counts; no figure estimated. Not estimated. To complete: REST artifact query in cc-ci-analysis section 6.1 on runs 41436591797, 41862618099, 41869689161 by someone with unrestricted egress; count <testcase> in run-{1,2}/*.xml and read full-candidate-gate/full-candidate-results.json. Also not measured: executed test counts per class (CURRENT_REQUIRED/LEGACY_SUPPORTED/HISTORICAL_ONLY/UNRESOLVED); flaky/error rates; coverage per active obligation after change. No savings are claimed. This PR changes no gate; before/after comparison is for plan S3/S4.

## 7. Unverified statements

- Constitution adoption for Hub/OCS (AD-08).
- cognous-evidence-attestation source (bitrep) not inspected; its rows are from matrix and lock only.
- Per-scenario pass/fail under PR #270: inferred from #270 body and runner labelling; scenario-results.json not retrievable.
- Per-test junit for cited component test ids (job-level PASS only, except native p2 suite and ODES).
- Qualification runner revisions 4a57a309 and a65c0a30 (used by Hub aggregate) were not diffed against 8e5e4ac3 beyond a differing file hash; stage-file mapping verified at 8e5e4ac3 only.
- Org-level rulesets were not enumerated.
- Statements marked CARRIED_FROM_WORKER_AUDIT are worker findings that the writer did not re-derive.
