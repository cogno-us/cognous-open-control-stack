# Traceable Agent Governance Evidence Pack

| Field | Value |
|---|---|
| Pack ID | agep-659510302f5893cb |
| Version | 0.2.0 |
| Generated At | 2026-10-07T01:36:40.769466+00:00 |
| Review Status | draft |
| Agent | Synthetic Refund Agent |
| Environment | other |
| Owner | cognous-integration-pilot |
| Business Unit | — |

## 1. Executive Summary

**Synthetic Refund Agent** is represented in this evidence pack for the **other** environment. Business purpose: Imported from Manifest and Reconstruction Bundle; business purpose unavailable.

The pack records **1** tool(s), **2** action(s), **2** privileged/review-sensitive action(s), and **1** replay/reconstruction bundle reference(s).

Validation summary: 1 valid bundle(s), 0 invalid bundle(s), 0 error(s), 2 warning(s).
Source artifacts passed supported semantic import checks. This does not establish deployment approval, compliance, operational effectiveness, or independent audit.

No open risks recorded. Absence of incident records does not prove absence of incidents.

## 2. Agent Overview

**Agent Name:** Synthetic Refund Agent

**Description:** Synthetic bounded integration fixture; not deployed and not an institutional grant.

**Business Purpose:** Imported from Manifest and Reconstruction Bundle; business purpose unavailable.

**Owner:** cognous-integration-pilot

**Business Unit:** —

**User Population:** —

**Lifecycle Stage:** —


## 3. Deployment Context

**Environment:** other

**Deployment Name:** synthetic

**Deployment Date:** —

**Systems Touched:** synthetic-refund-ledger

**Data Domains:** —

**Geographic Scope:** —

**Notes:** Generated from retained producer artifacts; does not establish deployment approval or operational effectiveness.


## 4. Tool Inventory

| Tool Name | Description | External System | Data Classification | Access Mode | Control Status |
|---|---|---|---|---|---|
| refund_adapter | Synthetic refund destination adapter. | synthetic-refund-ledger | synthetic | — | planned |

## 5. Action Inventory

| Action Name | Tool | Type | Authority Required | Review Required | Reliance Required | Default Posture | Control Status |
|---|---|---|---|---|---|---|---|
| refund_issue_routine | refund_adapter | write | Yes | Yes | Yes | escalate | planned |
| refund_issue_high_consequence | refund_adapter | write | Yes | Yes | Yes | escalate | planned |

## 6. Authority Model

**Summary:** Authority evidence imported from retained runtime records. This is not a grant or approval.

**Authority Scopes:** —

**Privileged Action Types:** write

**Expiration Required:** Yes

**Human Approval Required:** Yes

**Notes:** Authority Context profile references remain distinct from context-instance identifiers.


## 7. Policy Controls

| Control Name | Description | Status | Evidence Reference |
|---|---|---|---|
| Manifest declaration | Actions and requirements imported from Manifest v1.1. Declaration alone does not establish implementation. | planned | metadata.traceable_import.input_artifacts&#91;manifest&#93; |
| Review and approval declaration | Manifest review_requirement and approval-related declarations are preserved for review support; declaration alone does not create human approval. | planned | manifest.actions&#91;*&#93;.review_requirement |
| Replay semantic import validation | The importer executed the accepted Replay semantic validator over retained producer records. This is import-time evidence checking, not evidence that runtime controls were operationally effective. | implemented | metadata.traceable_import.replay_semantic_validation |
| Independent operational verification | No independent real-world effect verification supplied. | planned | metadata.traceable_import.lifecycle_summary.independent_verification |

## 8. Blocked-Action Summary

No blocked actions recorded.

## 9. Reliance Summary

No reliance records recorded.

## 10. Replay Bundle Inventory

| Bundle ID | Run ID | Status | Generated At | Signed | Redacted | Validation Status | Evidence Reference |
|---|---|---|---|---|---|---|---|
| 0709b026-253e-4c35-8a01-7efdfe0d02e1 | run-1 | reconstruction_complete | 2026-10-07T01:36:40.769466+00:00 | No | No | semantically_valid | metadata.traceable_import.source_record_refs |

## 11. Validation Summary

**Valid Bundles:** 1 | **Invalid Bundles:** 0 | **Errors:** 0 | **Warnings:** 2

Source artifacts passed supported semantic import checks. This does not establish deployment approval, compliance, operational effectiveness, or independent audit.


## 12. Redaction and Export Summary

No redaction or export records recorded.

## 13. Risk Register

No risks recorded. Missing incident records do not prove that no incidents occurred.

## 14. Review Records

No review records recorded. Default review status remains unreviewed/draft unless supplied by an attributable human reviewer.

## 15. Known Limitations

This evidence pack summarizes available runtime and governance records. It does not prove that model outputs are correct, policy controls are sufficient, compliance obligations are satisfied, deployment is approved, controls are operationally effective, or independent audit has occurred. Schema validity and successful reconstruction are review aids only.

## 16. Traceability and Import Provenance

This section is generated from `metadata.traceable_import`. It is review support only. It does not certify deployment approval, compliance, operational effectiveness, or independent audit.

### Input artifacts

| Role | Artifact ID | Version | Hash | Trusted Revision | Verification Status |
|---|---|---|---|---|---|
| manifest | refund-integration-pilot-v1 | 1.1 | sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac | 46c950bed37fe3812000895430bc0312d29e37ce | digest_and_cross_artifact_binding_checked_when_runtime_proposal_present |
| reconstruction_bundle | 0709b026-253e-4c35-8a01-7efdfe0d02e1 | 0.2.0 | sha256:7dfb3c72045a8fc82e6221caba6099a8ec6589bdfd47a8412026486e54194b27 | 274543f1cd7171784a923a8e37015017a0d8bc9d | validated_complete |

### Transformation

| Field | Value |
|---|---|
| Transformation Version | agep-manifest-reconstruction-import/0.3.0 |
| Canonicalization Profile | json-sort-keys-compact-utf8-no-nan |

### Derived counts

| Count | Value |
|---|---|
| proposal_count | 1 |
| decision_count | 1 |
| distinct_effect_count | 1 |
| control_plane_attempt_count | 1 |
| executor_attempt_count | 1 |
| attempt_transition_record_count | 4 |
| authorization_granted_count | 1 |
| authorization_held_count | 0 |
| authorization_denied_count | 0 |
| destination_observation.absent | 1 |
| destination_observation.applied | 1 |
| acknowledgement.control_plane_received | 1 |
| acknowledgement.execution_result_received | 1 |

Counting rules:
- Repeated lifecycle records do not inflate attempt counts.
- Duplicate submissions do not inflate distinct effect counts when effect_id is unchanged.
- Control Plane and executor attempt IDs are separate namespaces unless explicit correlation exists.
- Destination effects, effect observations and reconciliations are counted separately.
- Missing observations are unavailable, not success or failure.
- Latest supported state uses Replay producer sequence and exact effect lineage; earlier rejection remains visible. Independent clocks do not establish ordering.

### Lifecycle and effect status

| Dimension | Value |
|---|---|
| authorization | authorized |
| current_permission | not_evaluated_from_historical_records |
| execution_attempted | yes |
| acknowledgement | received |
| destination_observed | applied |
| destination_observation_scope | latest supplied Control Plane reconciliation per exact effect; not a fresh query |
| reconstruction_status | reconstruction_complete |
| retry_permission | not_established |
| independent_verification | unavailable |

- Historical authorization is retained evidence and does not establish current permission.
- Control Plane transition status is preserved separately from acknowledgement receipt.
- Executor acknowledgement is distinct from independently verified delivery.
- A lost or unknown acknowledgement followed by an applied observation retains both facts.
- Observed local destination state does not establish independently verified institutional outcome.
- Reconstruction completeness does not mean effect completion.
- HMAC/shared-secret integrity is not public issuer identity or independent review.
- A software-generated pack cannot create human approval.

### Control evidence levels

| Level | Status | Evidence | Meaning |
|---|---|---|---|
| semantic_validation_performed_during_import | validated_complete | metadata.traceable_import.replay_semantic_validation | the importer executed the accepted Replay semantic validator; this is not a test-run or runtime-control-effectiveness claim |
| source_asserted_runtime_evidence | unavailable | — | no source runtime or fixture provenance was supplied |
| attributable_test_run_evidence | unavailable | — | no complete attributable test-run provenance was supplied |
| declared | present | manifest | control or requirement is declared only |
| implemented | not_established_by_import | — | implementation requires producer-specific evidence; manifest declarations and import success do not suffice |
| tested | unavailable | — | semantic import validation and source runtime records do not by themselves establish that a test occurred |
| tested_in_this_repository | not_evaluated_during_import | — | this import does not execute or imply execution of the Evidence Pack repository test suite |
| operationally_observed | unavailable | — | no production operational observation supplied |
| independently_audited | unavailable | — | no independent audit or certification supplied |

### Import findings and unresolved limitations

| Code | Severity | Path/Source | Message |
|---|---|---|---|
| REPLAY_B003 | warning | proposal.authority_context_ref | Profile reference equals a context-instance identifier; semantics remain distinct. |
| REPLAY_M003 | info | moltbot.execution_envelope.operation.institution_id | Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding. |
| REPLAY_M004 | info | moltbot.execution_envelope.operation.authority_context_id | At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID. |
| REPLAY_SEMANTIC_LIMITATION | info | semantics.notes | Replay reconstructs recorded events only; import never renews permission or creates an effect. |
| R_REDACTION_STATE_UNKNOWN | warning | reconstruction_bundle.derivation\|metadata.redaction | Source did not declare redaction state; EvidencePack boolean defaults to false for schema compatibility. |

### Unresolved issues

| Code | Severity | Message |
|---|---|---|
| U_INDEPENDENT_VERIFICATION_UNAVAILABLE | warning | Destination observation is producer-retained unless independent verifier evidence is supplied. |
| U_OPERATIONAL_EFFECTIVENESS_NOT_MEASURED | warning | Synthetic import success cannot support operational effectiveness or deployment approval. |
| U_HISTORICAL_AUTHORIZATION_NOT_CURRENT_PERMISSION | info | Retained authorization is historical evidence only; current permission must be re-evaluated by the runtime authority/control boundary. |
| U_EXCHANGE_METADATA_SUPPLEMENTARY | info | Accepted GAX/IMX exchange metadata remains supplementary unless represented by a supported Replay mapping; the Evidence Pack does not invent exchange fields. |

### Producer profiles

| Profile | Repository | Revision | Format Version | Revision Check | Independent Provenance Verification |
|---|---|---|---|---|---|
| control-plane-bounded-run@2ea9528e | cogno-us/cognous-agent-control-plane | 2ea9528eeb87e14ff10f05de06473122b9df540f | — | declared_revision_matches_accepted_pin | not_performed |
| moltbot-safe-executor-producer-2.0.0@177354e9 | cogno-us/moltbot-safe | 177354e959cc78c59c1a776f018cfbfbf28c927b | 2.0.0 | declared_revision_matches_accepted_pin | not_performed |

### Executor producer contract

| Field | Value |
|---|---|
| interface_profile_id | urn:cognous:profiles:moltbot-safe-executor-producer |
| interface_profile_version | 2.0.0 |
| repository_revision | 177354e959cc78c59c1a776f018cfbfbf28c927b |
| legacy | False |
| source_asserted_repository_revision | 177354e959cc78c59c1a776f018cfbfbf28c927b |
| source_asserted_profile_id | urn:cognous:profiles:moltbot-safe-executor-producer |
| source_asserted_profile_version | 2.0.0 |
| independently_established_count | 0 |

Executor producer metadata and repository revision are source assertions unless separately established. A locally computed commitment or successful semantic import does not authenticate the producer or independently verify the outcome.

### Conversion losses and source findings

| Code | Category | Severity | Path | Value State | Message |
|---|---|---|---|---|---|
| B003 | conversion_warning | warning | proposal.authority_context_ref | — | Profile reference equals a context-instance identifier; semantics remain distinct. |
| M003 | conversion_warning | info | moltbot.execution_envelope.operation.institution_id | — | Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding. |
| M004 | conversion_warning | info | moltbot.execution_envelope.operation.authority_context_id | — | At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID. |

### Supporting source-record references

| Record ID | Type | Producer Profile | Evidence Class (source assertion) | Producer Revision | Revision Check | Source Path |
|---|---|---|---|---|---|---|
| control-plane-bounded-run@2ea9528e:runtime_proposal:0 | runtime_proposal | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | proposal |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | runtime_decision | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | decisions&#91;0&#93; |
| control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:2 | control_plane_attempt_transition | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | attempts&#91;0&#93; |
| control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3 | control_plane_attempt_transition | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | attempts&#91;1&#93; |
| control-plane-bounded-run@2ea9528e:effect_observation:4 | effect_observation | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | observations&#91;0&#93; |
| control-plane-bounded-run@2ea9528e:effect_observation:5 | effect_observation | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | observations&#91;1&#93; |
| control-plane-bounded-run@2ea9528e:reconciliation:6 | reconciliation | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | reconciliations&#91;0&#93; |
| control-plane-bounded-run@2ea9528e:reconciliation:7 | reconciliation | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | reconciliations&#91;1&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:8 | execution_envelope | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.execution_envelope |
| moltbot-safe-executor-producer-2.0.0@177354e9:executor_control_plane_evidence:9 | executor_control_plane_evidence | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.control_plane_evidence |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10 | execution_result | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.execution_result |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11 | destination_attempt | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.attempts&#91;0&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:12 | destination_attempt_event | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.attempt_events&#91;0&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:13 | destination_attempt_event | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.attempt_events&#91;1&#93; |
| control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14 | moltbot_attributed_control_plane_attempt | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | moltbot.control_plane_attempts&#91;0&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15 | destination_effect | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.effects&#91;0&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:executor_observation:16 | executor_observation | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.observations&#91;0&#93; |

### Source-supplied commitments

| Record ID | Label | Commitment | Algorithm | Canonicalization | Source Verification Status | Source Path |
|---|---|---|---|---|---|---|
| control-plane-bounded-run@2ea9528e:runtime_proposal:0 | payload_commitment | sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e | SHA-256 | json-sort-keys-compact-utf8-no-nan | checked_match | proposal.payload_commitment |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | effect_id | sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829 | SHA-256 | json-sort-keys-compact-utf8-no-nan | checked_match | decisions&#91;0&#93;.effect_id |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | proposal_commitment | sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.proposal_commitment |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | manifest_digest | sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.manifest_digest |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | payload_commitment | sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.payload_commitment |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | requirement_commitment | sha256:f6f5f1915b8ad4dd3d65992b5faceb5e3c3a3dde67570759b44b0c56ec936617 | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.requirement_commitment |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | role_mapping_digest | sha256:b6efb6a8d89e81f980d649015ac6e04e9126659c28ff4606972041c8c99beb8b | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.role_mapping_digest |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:8 | payload_commitment | sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e | SHA-256 | json-sort-keys-compact-utf8-no-nan | checked_match | moltbot.execution_envelope.operation.payload_commitment |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15 | operation_digest | sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175 | SHA-256 | json-sort-keys-compact-utf8-no-nan | checked_match | moltbot.effects&#91;0&#93;.operation_digest |

### Locally computed record commitments

| Record ID | Local Commitment | Compatibility Hash Alias | Canonicalization | Verification Status |
|---|---|---|---|---|
| control-plane-bounded-run@2ea9528e:runtime_proposal:0 | sha256:e72961e2b5814723f665fcb1335516c1541c158862087867def4116864893ba4 | sha256:e72961e2b5814723f665fcb1335516c1541c158862087867def4116864893ba4 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | sha256:d52c63fee092ed4327fc1d14c6d7abd9fc21825ca60ad6eabfdf37f4a8c4f5b5 | sha256:d52c63fee092ed4327fc1d14c6d7abd9fc21825ca60ad6eabfdf37f4a8c4f5b5 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:2 | sha256:e4c74a9ab03a47bb7eed06939261fd8428338517f65786c0d5aab392d967d5a0 | sha256:e4c74a9ab03a47bb7eed06939261fd8428338517f65786c0d5aab392d967d5a0 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3 | sha256:0964bde5823083c4619d7b698c9428bd2570df6917562cc0218a1f34883b3e70 | sha256:0964bde5823083c4619d7b698c9428bd2570df6917562cc0218a1f34883b3e70 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:effect_observation:4 | sha256:738c5ee26007e37a315d66bddc97ae18b2e29f3298c3492effd9bb76d8a1f2a2 | sha256:738c5ee26007e37a315d66bddc97ae18b2e29f3298c3492effd9bb76d8a1f2a2 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:effect_observation:5 | sha256:3e711f00a7697ecf6c7b4c50fa7f1e5f1df9b97909c331876bb7b1ab3876e7e6 | sha256:3e711f00a7697ecf6c7b4c50fa7f1e5f1df9b97909c331876bb7b1ab3876e7e6 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:reconciliation:6 | sha256:5372268fece9cbfa8a3f2c1e18383973581ece9fe4be0d8bd142b9213e3138e1 | sha256:5372268fece9cbfa8a3f2c1e18383973581ece9fe4be0d8bd142b9213e3138e1 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:reconciliation:7 | sha256:e5f2362a29e2c74078a73164f0c9ce91653f80ebef5b36214fadee16d44b567b | sha256:e5f2362a29e2c74078a73164f0c9ce91653f80ebef5b36214fadee16d44b567b | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:8 | sha256:a3cf2beae25540c5d0ab4f27fddec7ea20f9ca3c1e0fa04b5e557a283745d092 | sha256:a3cf2beae25540c5d0ab4f27fddec7ea20f9ca3c1e0fa04b5e557a283745d092 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:executor_control_plane_evidence:9 | sha256:a54023b3708da457cca39a79ceab3241d5331509cd70278a79cb6fedd3c809ce | sha256:a54023b3708da457cca39a79ceab3241d5331509cd70278a79cb6fedd3c809ce | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10 | sha256:0b98f1b2c739a95c3099fa6cbea42bf2ca006ac4eab364bc8fc825c25e00cf4e | sha256:0b98f1b2c739a95c3099fa6cbea42bf2ca006ac4eab364bc8fc825c25e00cf4e | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11 | sha256:07ed9ca98a1873db334e220f03ed1b63f7e768a89e2d94cb1c0d8cab2d980111 | sha256:07ed9ca98a1873db334e220f03ed1b63f7e768a89e2d94cb1c0d8cab2d980111 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:12 | sha256:5f8601b74590c97b9288338b6bb311b4deb190f80c588e88155f147553db07a1 | sha256:5f8601b74590c97b9288338b6bb311b4deb190f80c588e88155f147553db07a1 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:13 | sha256:51c50372be33d4e2602a9fa0609d0dd8ab07ce5281fb3c9847b5c36f20f2bafa | sha256:51c50372be33d4e2602a9fa0609d0dd8ab07ce5281fb3c9847b5c36f20f2bafa | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14 | sha256:9f3f884cfe1e325be2ea66ba2b2dbe1660852a0a5a14eb1e6644f8ada7f01e73 | sha256:9f3f884cfe1e325be2ea66ba2b2dbe1660852a0a5a14eb1e6644f8ada7f01e73 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15 | sha256:edcff53d4d8a61c48841d9256e7f7bca01d45dc62466b4bfef1c3544b1880ebc | sha256:edcff53d4d8a61c48841d9256e7f7bca01d45dc62466b4bfef1c3544b1880ebc | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:executor_observation:16 | sha256:f58a25d889a8f3a046686c553df3e61140da644c801db839454b7773f6c08b61 | sha256:f58a25d889a8f3a046686c553df3e61140da644c801db839454b7773f6c08b61 | json-sort-keys-compact-utf8-no-nan | computed_during_import |

Source evidence classes and source verification statuses are retained as producer/source assertions. They are not the importer’s independent assurance or verification.

### Complete material trace (escaped JSON)

The following is the complete trace metadata without truncation. Null observations, rejected content, historical states, policy/evaluation metadata and original sources remain distinct. Rejected evidence is not accepted lineage. No retry or current authority is established.

<pre>{
  "transformation_version": "agep-manifest-reconstruction-import/0.3.0",
  "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
  "supported_revisions": {
    "manifest": "46c950bed37fe3812000895430bc0312d29e37ce",
    "replay": "274543f1cd7171784a923a8e37015017a0d8bc9d",
    "control_plane": "2ea9528eeb87e14ff10f05de06473122b9df540f",
    "moltbot_safe": "177354e959cc78c59c1a776f018cfbfbf28c927b",
    "odes": "226adb0e3cde5377ac9db6f7e5857bfa7e65e30a",
    "gax_imx_experimental_reference": "6bcde026a804c7377f5e39f57ca6dd00b3c3292d",
    "gax_imx_acceptance_status": "provisional_experimental_dependency",
    "alvorada": "fb3d97938969a89e149e8ff8db2756091d1233fc"
  },
  "replay_semantic_validation": {
    "validator": "agent_replay_bundle.importers.import_bounded_workflow",
    "required_revision": "274543f1cd7171784a923a8e37015017a0d8bc9d",
    "status": "validated_complete"
  },
  "replay_import_reports": [
    {
      "adapter_profile": "control-plane-bounded-run@2ea9528e",
      "complete": true,
      "field_mappings": {
        "attempts": "records[control_plane_attempt_transition]",
        "decisions": "records[runtime_decision]",
        "observations": "records[effect_observation]",
        "reconciliations": "records[reconciliation]"
      },
      "findings": [
        {
          "category": "conversion_warning",
          "code": "B003",
          "message": "Profile reference equals a context-instance identifier; semantics remain distinct.",
          "path": "proposal.authority_context_ref",
          "severity": "warning",
          "value_state": null
        },
        {
          "category": "conversion_warning",
          "code": "M003",
          "message": "Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding.",
          "path": "moltbot.execution_envelope.operation.institution_id",
          "severity": "info",
          "value_state": null
        },
        {
          "category": "conversion_warning",
          "code": "M004",
          "message": "At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID.",
          "path": "moltbot.execution_envelope.operation.authority_context_id",
          "severity": "info",
          "value_state": null
        }
      ],
      "source_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f"
    }
  ],
  "replay_semantics": {
    "destination_observation": "producer_reported",
    "external_effect_execution": false,
    "independent_effect_verification": false,
    "model_reexecution": false,
    "notes": "Replay reconstructs recorded events only; import never renews permission or creates an effect.",
    "policy_reevaluation": false,
    "record_reconstruction": true
  },
  "input_artifacts": [
    {
      "artifact_role": "manifest",
      "artifact_id": "refund-integration-pilot-v1",
      "version": "1.1",
      "hash": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
      "trusted_revision": "46c950bed37fe3812000895430bc0312d29e37ce",
      "verification_status": "digest_and_cross_artifact_binding_checked_when_runtime_proposal_present",
      "commitment_source": "locally_computed",
      "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan"
    },
    {
      "artifact_role": "reconstruction_bundle",
      "artifact_id": "0709b026-253e-4c35-8a01-7efdfe0d02e1",
      "version": "0.2.0",
      "hash": "sha256:7dfb3c72045a8fc82e6221caba6099a8ec6589bdfd47a8412026486e54194b27",
      "trusted_revision": "274543f1cd7171784a923a8e37015017a0d8bc9d",
      "verification_status": "validated_complete",
      "commitment_source": "locally_computed",
      "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan"
    }
  ],
  "producer_profiles": [
    {
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "producer": "Cognous Agent Control Plane",
      "repository": "cogno-us/cognous-agent-control-plane",
      "revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "format_version": null,
      "revision_check": "declared_revision_matches_accepted_pin",
      "provenance_status": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "format_name": "BoundedRunRecord",
      "schema_ref": null,
      "notes": "No embedded format version; adapter is revision-pinned."
    },
    {
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "producer": "Moltbot Safe",
      "repository": "cogno-us/moltbot-safe",
      "revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "format_version": "2.0.0",
      "revision_check": "declared_revision_matches_accepted_pin",
      "provenance_status": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "format_name": "Executor producer export",
      "schema_ref": null,
      "notes": "Versioned producer profile; repository provenance remains source-asserted unless separately established."
    }
  ],
  "executor_producer_contract": {
    "control_plane_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
    "interface_profile_id": "urn:cognous:profiles:moltbot-safe-executor-producer",
    "interface_profile_version": "2.0.0",
    "legacy": false,
    "profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
    "provenance": {
      "independently_established": [],
      "mode": "versioned_profile",
      "source_asserted": {
        "consumer": "cogno-us/alvorada:gax_ref_runtime",
        "producer": "cogno-us/moltbot-safe",
        "producer_profile_id": "urn:cognous:profiles:moltbot-safe-executor-producer",
        "producer_profile_version": "2.0.0",
        "repository_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b"
      }
    },
    "repository_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b"
  },
  "source_record_refs": [
    {
      "record_id": "control-plane-bounded-run@2ea9528e:runtime_proposal:0",
      "record_type": "runtime_proposal",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "proposal",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "checked_match",
          "source_path": "proposal.payload_commitment",
          "notes": null
        }
      ],
      "source_content_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
      "source_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "source_commitment_verification_status": "checked_match",
      "local_content_commitment": "sha256:e72961e2b5814723f665fcb1335516c1541c158862087867def4116864893ba4",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:e72961e2b5814723f665fcb1335516c1541c158862087867def4116864893ba4"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
      "record_type": "runtime_decision",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "decisions[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [
        {
          "label": "effect_id",
          "value": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "checked_match",
          "source_path": "decisions[0].effect_id",
          "notes": "Checked under pinned Control Plane effect-id contract."
        },
        {
          "label": "proposal_commitment",
          "value": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.proposal_commitment",
          "notes": null
        },
        {
          "label": "manifest_digest",
          "value": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.manifest_digest",
          "notes": null
        },
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.payload_commitment",
          "notes": null
        },
        {
          "label": "requirement_commitment",
          "value": "sha256:f6f5f1915b8ad4dd3d65992b5faceb5e3c3a3dde67570759b44b0c56ec936617",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.requirement_commitment",
          "notes": null
        },
        {
          "label": "role_mapping_digest",
          "value": "sha256:b6efb6a8d89e81f980d649015ac6e04e9126659c28ff4606972041c8c99beb8b",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.role_mapping_digest",
          "notes": null
        }
      ],
      "source_content_commitment": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
      "source_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "source_commitment_verification_status": "checked_match",
      "local_content_commitment": "sha256:d52c63fee092ed4327fc1d14c6d7abd9fc21825ca60ad6eabfdf37f4a8c4f5b5",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:d52c63fee092ed4327fc1d14c6d7abd9fc21825ca60ad6eabfdf37f4a8c4f5b5"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:2",
      "record_type": "control_plane_attempt_transition",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "attempts[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:e4c74a9ab03a47bb7eed06939261fd8428338517f65786c0d5aab392d967d5a0",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:e4c74a9ab03a47bb7eed06939261fd8428338517f65786c0d5aab392d967d5a0"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
      "record_type": "control_plane_attempt_transition",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "attempts[1]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:0964bde5823083c4619d7b698c9428bd2570df6917562cc0218a1f34883b3e70",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:0964bde5823083c4619d7b698c9428bd2570df6917562cc0218a1f34883b3e70"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:effect_observation:4",
      "record_type": "effect_observation",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "observations[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:738c5ee26007e37a315d66bddc97ae18b2e29f3298c3492effd9bb76d8a1f2a2",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:738c5ee26007e37a315d66bddc97ae18b2e29f3298c3492effd9bb76d8a1f2a2"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:effect_observation:5",
      "record_type": "effect_observation",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "observations[1]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:3e711f00a7697ecf6c7b4c50fa7f1e5f1df9b97909c331876bb7b1ab3876e7e6",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:3e711f00a7697ecf6c7b4c50fa7f1e5f1df9b97909c331876bb7b1ab3876e7e6"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:reconciliation:6",
      "record_type": "reconciliation",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "reconciliations[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:5372268fece9cbfa8a3f2c1e18383973581ece9fe4be0d8bd142b9213e3138e1",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:5372268fece9cbfa8a3f2c1e18383973581ece9fe4be0d8bd142b9213e3138e1"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:reconciliation:7",
      "record_type": "reconciliation",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "reconciliations[1]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:e5f2362a29e2c74078a73164f0c9ce91653f80ebef5b36214fadee16d44b567b",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:e5f2362a29e2c74078a73164f0c9ce91653f80ebef5b36214fadee16d44b567b"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:8",
      "record_type": "execution_envelope",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.execution_envelope",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "checked_match",
          "source_path": "moltbot.execution_envelope.operation.payload_commitment",
          "notes": null
        }
      ],
      "source_content_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
      "source_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "source_commitment_verification_status": "checked_match",
      "local_content_commitment": "sha256:a3cf2beae25540c5d0ab4f27fddec7ea20f9ca3c1e0fa04b5e557a283745d092",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:a3cf2beae25540c5d0ab4f27fddec7ea20f9ca3c1e0fa04b5e557a283745d092"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:executor_control_plane_evidence:9",
      "record_type": "executor_control_plane_evidence",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.control_plane_evidence",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:a54023b3708da457cca39a79ceab3241d5331509cd70278a79cb6fedd3c809ce",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:a54023b3708da457cca39a79ceab3241d5331509cd70278a79cb6fedd3c809ce"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10",
      "record_type": "execution_result",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.execution_result",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:0b98f1b2c739a95c3099fa6cbea42bf2ca006ac4eab364bc8fc825c25e00cf4e",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:0b98f1b2c739a95c3099fa6cbea42bf2ca006ac4eab364bc8fc825c25e00cf4e"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11",
      "record_type": "destination_attempt",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.attempts[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:07ed9ca98a1873db334e220f03ed1b63f7e768a89e2d94cb1c0d8cab2d980111",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:07ed9ca98a1873db334e220f03ed1b63f7e768a89e2d94cb1c0d8cab2d980111"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:12",
      "record_type": "destination_attempt_event",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.attempt_events[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:5f8601b74590c97b9288338b6bb311b4deb190f80c588e88155f147553db07a1",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:5f8601b74590c97b9288338b6bb311b4deb190f80c588e88155f147553db07a1"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:13",
      "record_type": "destination_attempt_event",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.attempt_events[1]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:51c50372be33d4e2602a9fa0609d0dd8ab07ce5281fb3c9847b5c36f20f2bafa",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:51c50372be33d4e2602a9fa0609d0dd8ab07ce5281fb3c9847b5c36f20f2bafa"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14",
      "record_type": "moltbot_attributed_control_plane_attempt",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "moltbot.control_plane_attempts[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:9f3f884cfe1e325be2ea66ba2b2dbe1660852a0a5a14eb1e6644f8ada7f01e73",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:9f3f884cfe1e325be2ea66ba2b2dbe1660852a0a5a14eb1e6644f8ada7f01e73"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15",
      "record_type": "destination_effect",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.effects[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [
        {
          "label": "operation_digest",
          "value": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "checked_match",
          "source_path": "moltbot.effects[0].operation_digest",
          "notes": "Checked against the exact retained Execution Envelope operation under the pinned canonicalization profile."
        }
      ],
      "source_content_commitment": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
      "source_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "source_commitment_verification_status": "checked_match",
      "local_content_commitment": "sha256:edcff53d4d8a61c48841d9256e7f7bca01d45dc62466b4bfef1c3544b1880ebc",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:edcff53d4d8a61c48841d9256e7f7bca01d45dc62466b4bfef1c3544b1880ebc"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:executor_observation:16",
      "record_type": "executor_observation",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.observations[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:f58a25d889a8f3a046686c553df3e61140da644c801db839454b7773f6c08b61",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:f58a25d889a8f3a046686c553df3e61140da644c801db839454b7773f6c08b61"
    }
  ],
  "conversion_losses": [
    {
      "source": "replay_import_report",
      "report_index": 0,
      "finding_index": 0,
      "adapter_profile": "control-plane-bounded-run@2ea9528e",
      "code": "B003",
      "category": "conversion_warning",
      "severity": "warning",
      "path": "proposal.authority_context_ref",
      "value_state": null,
      "message": "Profile reference equals a context-instance identifier; semantics remain distinct."
    },
    {
      "source": "replay_import_report",
      "report_index": 0,
      "finding_index": 1,
      "adapter_profile": "control-plane-bounded-run@2ea9528e",
      "code": "M003",
      "category": "conversion_warning",
      "severity": "info",
      "path": "moltbot.execution_envelope.operation.institution_id",
      "value_state": null,
      "message": "Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding."
    },
    {
      "source": "replay_import_report",
      "report_index": 0,
      "finding_index": 2,
      "adapter_profile": "control-plane-bounded-run@2ea9528e",
      "code": "M004",
      "category": "conversion_warning",
      "severity": "info",
      "path": "moltbot.execution_envelope.operation.authority_context_id",
      "value_state": null,
      "message": "At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID."
    }
  ],
  "derived_counts": {
    "proposal_count": 1,
    "decision_count": 1,
    "distinct_effect_count": 1,
    "control_plane_attempt_count": 1,
    "executor_attempt_count": 1,
    "attempt_transition_record_count": 4,
    "destination_effect_count": 1,
    "effect_observation_count": 2,
    "reconciliation_count": 2,
    "destination_observation_counts": {
      "absent": 1,
      "applied": 1
    },
    "destination_effect_state_counts": {
      "applied": 1
    },
    "effect_observation_state_counts": {
      "absent": 1,
      "applied": 1
    },
    "reconciliation_state_counts": {
      "applied": 1,
      "observed_absent": 1
    },
    "execution_result_state_counts": {
      "applied": 1
    },
    "acknowledgement_counts": {
      "control_plane_received": 1,
      "execution_result_received": 1
    },
    "acknowledgement_sources": [
      {
        "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
        "source": "control_plane_transition",
        "state": "received",
        "status": "acknowledged",
        "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395"
      },
      {
        "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10",
        "source": "execution_result",
        "state": "received",
        "status": "executed",
        "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519"
      }
    ],
    "coverage_denominators": {
      "effect_denominator": "distinct authorized effect_id values",
      "control_plane_attempt_denominator": "unique Control Plane attempt IDs",
      "executor_attempt_denominator": "unique destination_attempt IDs",
      "destination_effect_denominator": "destination_effect records",
      "effect_observation_denominator": "effect_observation records",
      "reconciliation_denominator": "reconciliation records",
      "missing_observation": "unavailable, not zero/success/failure",
      "destination_observation_denominator": "accepted Control Plane effect_observation records only; destination rows and reconciliations counted separately"
    },
    "counting_rules": [
      "Repeated lifecycle records do not inflate attempt counts.",
      "Duplicate submissions do not inflate distinct effect counts when effect_id is unchanged.",
      "Control Plane and executor attempt IDs are separate namespaces unless explicit correlation exists.",
      "Destination effects, effect observations and reconciliations are counted separately.",
      "Missing observations are unavailable, not success or failure.",
      "Latest supported state uses Replay producer sequence and exact effect lineage; earlier rejection remains visible. Independent clocks do not establish ordering."
    ],
    "authorization_granted_count": 1,
    "authorization_held_count": 0,
    "authorization_denied_count": 0
  },
  "lifecycle_summary": {
    "authorization": "authorized",
    "current_permission": "not_evaluated_from_historical_records",
    "execution_attempted": "yes",
    "acknowledgement": "received",
    "acknowledgement_sources": [
      {
        "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
        "source": "control_plane_transition",
        "state": "received",
        "status": "acknowledged",
        "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395"
      },
      {
        "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10",
        "source": "execution_result",
        "state": "received",
        "status": "executed",
        "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519"
      }
    ],
    "control_plane_transition_statuses": {
      "acknowledged": 1,
      "attempted": 1
    },
    "destination_observed": "applied",
    "independent_verification": "unavailable",
    "notes": [
      "Historical authorization is retained evidence and does not establish current permission.",
      "Control Plane transition status is preserved separately from acknowledgement receipt.",
      "Executor acknowledgement is distinct from independently verified delivery.",
      "A lost or unknown acknowledgement followed by an applied observation retains both facts.",
      "Observed local destination state does not establish independently verified institutional outcome.",
      "Reconstruction completeness does not mean effect completion.",
      "HMAC/shared-secret integrity is not public issuer identity or independent review.",
      "A software-generated pack cannot create human approval."
    ],
    "reconstruction_status": "reconstruction_complete",
    "effect_observation_history": {
      "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829": {
        "acknowledgement_history": [
          {
            "acknowledgement": {},
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "source_index": 0,
            "status": "attempted"
          },
          {
            "acknowledgement": {
              "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
              "moltbot_safe_status": "executed",
              "newly_executed": true,
              "observation": {
                "destination_state": {
                  "amount": 50.0,
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "state": "applied",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "unit": "USD"
                },
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied"
              }
            },
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "source_index": 1,
            "status": "acknowledged"
          }
        ],
        "basis": "Control Plane reconciliation array order, filtered by exact effect_id",
        "cross_sequence_order": "not_established",
        "freshness_at_import": "not_evaluated",
        "latest_accepted_observation": {
          "observation": {
            "destination_state": {
              "amount": 50.0,
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "grant_id": "urn:cognous:grant:routine-1",
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "state": "applied",
              "target": "urn:cognous:synthetic-account:customer-001",
              "unit": "USD"
            },
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "observed_at": "2026-08-08T01:00:00+00:00",
            "state": "applied"
          },
          "source_index": 1
        },
        "latest_reconciliation": {
          "observation_accepted": true,
          "result": "applied",
          "source_index": 1
        },
        "latest_supported_destination_state": "applied",
        "rejected_reconciliation_indices": [],
        "retry_eligible": false
      }
    },
    "destination_observation_scope": "latest supplied Control Plane reconciliation per exact effect; not a fresh query",
    "retry_permission": "not_established",
    "historical_local_observation": false
  },
  "control_evidence_levels": {
    "semantic_validation_performed_during_import": {
      "status": "validated_complete",
      "evidence": [
        "metadata.traceable_import.replay_semantic_validation"
      ],
      "meaning": "the importer executed the accepted Replay semantic validator; this is not a test-run or runtime-control-effectiveness claim"
    },
    "source_asserted_runtime_evidence": {
      "status": "unavailable",
      "evidence": [],
      "scope": "unavailable",
      "meaning": "no source runtime or fixture provenance was supplied"
    },
    "attributable_test_run_evidence": {
      "status": "unavailable",
      "evidence": [],
      "scope": "unavailable",
      "meaning": "no complete attributable test-run provenance was supplied"
    },
    "declared": {
      "status": "present",
      "evidence": [
        "manifest"
      ],
      "meaning": "control or requirement is declared only"
    },
    "implemented": {
      "status": "not_established_by_import",
      "evidence": [],
      "meaning": "implementation requires producer-specific evidence; manifest declarations and import success do not suffice"
    },
    "tested": {
      "status": "unavailable",
      "evidence": [],
      "scope": "unavailable",
      "meaning": "semantic import validation and source runtime records do not by themselves establish that a test occurred"
    },
    "tested_in_this_repository": {
      "status": "not_evaluated_during_import",
      "evidence": [],
      "meaning": "this import does not execute or imply execution of the Evidence Pack repository test suite"
    },
    "operationally_observed": {
      "status": "unavailable",
      "evidence": [],
      "meaning": "no production operational observation supplied"
    },
    "independently_audited": {
      "status": "unavailable",
      "evidence": [],
      "meaning": "no independent audit or certification supplied"
    }
  },
  "redaction_state": {
    "redacted": false,
    "source": "unknown_schema_default_false",
    "derivation": null
  },
  "import_findings": [
    {
      "code": "REPLAY_B003",
      "severity": "warning",
      "path": "proposal.authority_context_ref",
      "message": "Profile reference equals a context-instance identifier; semantics remain distinct.",
      "category": "conversion_warning",
      "value_state": null
    },
    {
      "code": "REPLAY_M003",
      "severity": "info",
      "path": "moltbot.execution_envelope.operation.institution_id",
      "message": "Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding.",
      "category": "conversion_warning",
      "value_state": null
    },
    {
      "code": "REPLAY_M004",
      "severity": "info",
      "path": "moltbot.execution_envelope.operation.authority_context_id",
      "message": "At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID.",
      "category": "conversion_warning",
      "value_state": null
    },
    {
      "code": "REPLAY_SEMANTIC_LIMITATION",
      "severity": "info",
      "path": "semantics.notes",
      "message": "Replay reconstructs recorded events only; import never renews permission or creates an effect."
    },
    {
      "code": "R_REDACTION_STATE_UNKNOWN",
      "severity": "warning",
      "path": "reconstruction_bundle.derivation|metadata.redaction",
      "message": "Source did not declare redaction state; EvidencePack boolean defaults to false for schema compatibility."
    }
  ],
  "manual_assessments": [],
  "unresolved_issues": [
    {
      "code": "U_INDEPENDENT_VERIFICATION_UNAVAILABLE",
      "severity": "warning",
      "message": "Destination observation is producer-retained unless independent verifier evidence is supplied."
    },
    {
      "code": "U_OPERATIONAL_EFFECTIVENESS_NOT_MEASURED",
      "severity": "warning",
      "message": "Synthetic import success cannot support operational effectiveness or deployment approval."
    },
    {
      "code": "U_HISTORICAL_AUTHORIZATION_NOT_CURRENT_PERMISSION",
      "severity": "info",
      "message": "Retained authorization is historical evidence only; current permission must be re-evaluated by the runtime authority/control boundary."
    },
    {
      "code": "U_EXCHANGE_METADATA_SUPPLEMENTARY",
      "severity": "info",
      "message": "Accepted GAX/IMX exchange metadata remains supplementary unless represented by a supported Replay mapping; the Evidence Pack does not invent exchange fields."
    }
  ],
  "outcomes_and_burden": {
    "unresolved_delivery": "see lifecycle_summary.destination_observed",
    "incidents": "unavailable_not_zero",
    "remedies": "unavailable",
    "measured_latency": "not_measured",
    "human_review_effort": "not_measured",
    "error_prevention": "not_measured",
    "error_correction": "not_measured",
    "comparison_baseline_reference": "unavailable"
  },
  "retained_sources": {
    "manifest": {
      "manifest_version": "1.1",
      "manifest_id": "refund-integration-pilot-v1",
      "agent_name": "Synthetic Refund Agent",
      "agent_description": "Synthetic bounded integration fixture; not deployed and not an institutional grant.",
      "owner": "cognous-integration-pilot",
      "environment": "synthetic",
      "default_action": "escalate",
      "tools": [
        {
          "tool_name": "refund_adapter",
          "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
          "description": "Synthetic refund destination adapter.",
          "allowed": true,
          "external_system": "synthetic-refund-ledger",
          "data_classification": "synthetic"
        }
      ],
      "actions": [
        {
          "action_name": "refund_issue_routine",
          "action_id": "urn:cognous:action:refund-issue-routine-v1",
          "tool_name": "refund_adapter",
          "action_type": "write",
          "description": "Issue one bounded routine synthetic refund.",
          "default_action": "escalate",
          "authority_required": [
            {
              "scope": "refund.issue.routine",
              "description": "Declaration only; downstream resolver must establish a current institutional grant.",
              "required": true,
              "source": "alvorada-authority-context-0.1.0"
            }
          ],
          "review_requirement": {
            "mode": "human_review",
            "reviewer_role": "customer-service-supervisor",
            "reason": "Synthetic routine case retains human review for the integration pilot."
          },
          "reliance_requirement": {
            "required": true,
            "allowed_source_types": [
              "database",
              "user_input"
            ],
            "description": "Record entitlement and customer request evidence."
          },
          "payload_policy": {
            "required_fields": [
              "customer_id",
              "refund_reason"
            ],
            "optional_fields": [],
            "sensitive_fields": [
              "customer_id"
            ],
            "forbidden_fields": []
          },
          "target_policy": {
            "allowed_targets": [
              "urn:cognous:synthetic-account:customer-001"
            ],
            "allow_any_target": false
          },
          "effect_limits": {
            "max_amount": 100.0,
            "unit": "USD",
            "max_effects": 1
          },
          "authority_context": {
            "schema_version": "0.1.0",
            "profile_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
            "institution_id": "urn:cognous:institution:synthetic-customer-service",
            "authority_domain": "customer-refunds",
            "consequence_tier": "T1",
            "evidence_obligation_ids": [
              "urn:cognous:evidence:refund-entitlement"
            ]
          },
          "redaction_hints": [
            {
              "field_path": "customer_id",
              "reason": "Synthetic identifier is treated as sensitive in exported evidence.",
              "replacement": "[REDACTED]"
            }
          ],
          "tags": [
            "synthetic",
            "refund",
            "routine"
          ],
          "metadata": {}
        },
        {
          "action_name": "refund_issue_high_consequence",
          "action_id": "urn:cognous:action:refund-issue-high-v1",
          "tool_name": "refund_adapter",
          "action_type": "write",
          "description": "Issue one higher-consequence synthetic refund requiring explicit approval downstream.",
          "default_action": "escalate",
          "authority_required": [
            {
              "scope": "refund.issue.high",
              "description": "Declaration only; downstream resolver must establish a current institutional grant.",
              "required": true,
              "source": "alvorada-authority-context-0.1.0"
            }
          ],
          "review_requirement": {
            "mode": "approval_required",
            "reviewer_role": "refund-authorizer",
            "reason": "Higher-consequence synthetic case requires explicit approval."
          },
          "reliance_requirement": {
            "required": true,
            "allowed_source_types": [
              "database",
              "user_input"
            ],
            "description": "Record entitlement, amount basis and approval evidence."
          },
          "payload_policy": {
            "required_fields": [
              "customer_id",
              "refund_reason",
              "case_reference"
            ],
            "optional_fields": [],
            "sensitive_fields": [
              "customer_id"
            ],
            "forbidden_fields": []
          },
          "target_policy": {
            "allowed_targets": [
              "urn:cognous:synthetic-account:customer-002"
            ],
            "allow_any_target": false
          },
          "effect_limits": {
            "max_amount": 1000.0,
            "unit": "USD",
            "max_effects": 1
          },
          "authority_context": {
            "schema_version": "0.1.0",
            "profile_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "requirement_id": "urn:cognous:authority-requirement:refund-high-v1",
            "institution_id": "urn:cognous:institution:synthetic-customer-service",
            "authority_domain": "customer-refunds",
            "consequence_tier": "T2",
            "evidence_obligation_ids": [
              "urn:cognous:evidence:refund-entitlement",
              "urn:cognous:evidence:refund-approval"
            ]
          },
          "redaction_hints": [
            {
              "field_path": "customer_id",
              "reason": "Synthetic identifier is treated as sensitive in exported evidence.",
              "replacement": "[REDACTED]"
            }
          ],
          "tags": [
            "synthetic",
            "refund",
            "higher-consequence"
          ],
          "metadata": {}
        }
      ],
      "metadata": {
        "upstream_alvorada_commit": "fb3d97938969a89e149e8ff8db2756091d1233fc",
        "authority_context_version": "0.1.0",
        "deployment_status": "not_deployed"
      }
    },
    "reconstruction_bundle": {
      "bundle_id": "0709b026-253e-4c35-8a01-7efdfe0d02e1",
      "bundle_version": "0.2.0",
      "commitments": [
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "payload_commitment",
          "notes": null,
          "source_path": "proposal.payload_commitment",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_proposal:0",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "verification_status": "checked_match"
        },
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "effect_id",
          "notes": "Checked under pinned Control Plane effect-id contract.",
          "source_path": "decisions[0].effect_id",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "value": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "verification_status": "checked_match"
        },
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "proposal_commitment",
          "notes": null,
          "source_path": "decisions[0].binding.proposal_commitment",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "value": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
          "verification_status": "attributed_claim"
        },
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "manifest_digest",
          "notes": null,
          "source_path": "decisions[0].binding.manifest_digest",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "value": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
          "verification_status": "attributed_claim"
        },
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "payload_commitment",
          "notes": null,
          "source_path": "decisions[0].binding.payload_commitment",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "verification_status": "attributed_claim"
        },
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "requirement_commitment",
          "notes": null,
          "source_path": "decisions[0].binding.requirement_commitment",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "value": "sha256:f6f5f1915b8ad4dd3d65992b5faceb5e3c3a3dde67570759b44b0c56ec936617",
          "verification_status": "attributed_claim"
        },
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "role_mapping_digest",
          "notes": null,
          "source_path": "decisions[0].binding.role_mapping_digest",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "value": "sha256:b6efb6a8d89e81f980d649015ac6e04e9126659c28ff4606972041c8c99beb8b",
          "verification_status": "attributed_claim"
        },
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "payload_commitment",
          "notes": null,
          "source_path": "moltbot.execution_envelope.operation.payload_commitment",
          "source_record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:8",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "verification_status": "checked_match"
        },
        {
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "label": "operation_digest",
          "notes": "Checked against the exact retained Execution Envelope operation under the pinned canonicalization profile.",
          "source_path": "moltbot.effects[0].operation_digest",
          "source_record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15",
          "value": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
          "verification_status": "checked_match"
        }
      ],
      "derivation": null,
      "generated_at": "2026-10-07T01:36:40.769466+00:00",
      "import_reports": [
        {
          "adapter_profile": "control-plane-bounded-run@2ea9528e",
          "complete": true,
          "field_mappings": {
            "attempts": "records[control_plane_attempt_transition]",
            "decisions": "records[runtime_decision]",
            "observations": "records[effect_observation]",
            "reconciliations": "records[reconciliation]"
          },
          "findings": [
            {
              "category": "conversion_warning",
              "code": "B003",
              "message": "Profile reference equals a context-instance identifier; semantics remain distinct.",
              "path": "proposal.authority_context_ref",
              "severity": "warning",
              "value_state": null
            },
            {
              "category": "conversion_warning",
              "code": "M003",
              "message": "Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding.",
              "path": "moltbot.execution_envelope.operation.institution_id",
              "severity": "info",
              "value_state": null
            },
            {
              "category": "conversion_warning",
              "code": "M004",
              "message": "At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID.",
              "path": "moltbot.execution_envelope.operation.authority_context_id",
              "severity": "info",
              "value_state": null
            }
          ],
          "source_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f"
        }
      ],
      "integrity": [],
      "links": [
        {
          "basis": "Producer-supplied Control Plane attempt evidence exactly matches the retained Control Plane run record.",
          "establishes_identity_equivalence": true,
          "from_record_id": "control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14",
          "link_type": "explicit",
          "to_record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3"
        },
        {
          "basis": "Control Plane acknowledgement explicitly supplied executor attempt_id.",
          "establishes_identity_equivalence": false,
          "from_record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
          "link_type": "explicit",
          "to_record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11"
        }
      ],
      "metadata": {
        "alvorada_revision": "fb3d97938969a89e149e8ff8db2756091d1233fc",
        "control_plane_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
        "effect_observation_history": {
          "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829": {
            "acknowledgement_history": [
              {
                "acknowledgement": {},
                "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
                "source_index": 0,
                "status": "attempted"
              },
              {
                "acknowledgement": {
                  "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
                  "moltbot_safe_status": "executed",
                  "newly_executed": true,
                  "observation": {
                    "destination_state": {
                      "amount": 50.0,
                      "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                      "grant_id": "urn:cognous:grant:routine-1",
                      "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                      "payload": {
                        "customer_id": "customer-001",
                        "refund_reason": "duplicate"
                      },
                      "state": "applied",
                      "target": "urn:cognous:synthetic-account:customer-001",
                      "unit": "USD"
                    },
                    "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                    "state": "applied"
                  }
                },
                "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
                "source_index": 1,
                "status": "acknowledged"
              }
            ],
            "basis": "Control Plane reconciliation array order, filtered by exact effect_id",
            "cross_sequence_order": "not_established",
            "freshness_at_import": "not_evaluated",
            "latest_accepted_observation": {
              "observation": {
                "destination_state": {
                  "amount": 50.0,
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "state": "applied",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "unit": "USD"
                },
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "observed_at": "2026-08-08T01:00:00+00:00",
                "state": "applied"
              },
              "source_index": 1
            },
            "latest_reconciliation": {
              "observation_accepted": true,
              "result": "applied",
              "source_index": 1
            },
            "latest_supported_destination_state": "applied",
            "rejected_reconciliation_indices": [],
            "retry_eligible": false
          }
        },
        "manifest_revision": "46c950bed37fe3812000895430bc0312d29e37ce",
        "moltbot_producer_contract": {
          "control_plane_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
          "interface_profile_id": "urn:cognous:profiles:moltbot-safe-executor-producer",
          "interface_profile_version": "2.0.0",
          "legacy": false,
          "profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "provenance": {
            "independently_established": [],
            "mode": "versioned_profile",
            "source_asserted": {
              "consumer": "cogno-us/alvorada:gax_ref_runtime",
              "producer": "cogno-us/moltbot-safe",
              "producer_profile_id": "urn:cognous:profiles:moltbot-safe-executor-producer",
              "producer_profile_version": "2.0.0",
              "repository_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b"
            }
          },
          "repository_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b"
        },
        "moltbot_safe_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b"
      },
      "producer_profiles": [
        {
          "format_name": "BoundedRunRecord",
          "format_version": null,
          "notes": "No embedded format version; adapter is revision-pinned.",
          "producer": "Cognous Agent Control Plane",
          "profile_id": "control-plane-bounded-run@2ea9528e",
          "repository": "cogno-us/cognous-agent-control-plane",
          "revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
          "schema_ref": null
        },
        {
          "format_name": "Executor producer export",
          "format_version": "2.0.0",
          "notes": "Versioned producer profile; repository provenance remains source-asserted unless separately established.",
          "producer": "Moltbot Safe",
          "profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "repository": "cogno-us/moltbot-safe",
          "revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
          "schema_ref": null
        }
      ],
      "records": [
        {
          "data": {
            "action_id": "urn:cognous:action:refund-issue-routine-v1",
            "actor": "urn:cognous:identity:refund-agent-1",
            "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
            "amount": 50.0,
            "authority_context_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "correlation_id": "case-1",
            "effects": 1,
            "evidence_refs": [
              "urn:cognous:evidence:refund-entitlement"
            ],
            "expected_side_effects": [],
            "expires_at": null,
            "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
            "manifest_id": "refund-integration-pilot-v1",
            "manifest_version": "1.1",
            "not_before": null,
            "payload": {
              "customer_id": "customer-001",
              "refund_reason": "duplicate"
            },
            "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
            "principal": "urn:cognous:principal:refund-service",
            "requested_permissions": [
              "refund.issue.routine"
            ],
            "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
            "risk_metadata": {},
            "run_id": "run-1",
            "target": "urn:cognous:synthetic-account:customer-001",
            "unit": "USD"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "action_id": "urn:cognous:action:refund-issue-routine-v1",
            "authority_context_profile_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "correlation_id": "case-1",
            "manifest_id": "refund-integration-pilot-v1",
            "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:runtime_proposal:0",
          "record_type": "runtime_proposal",
          "recorded_at": null,
          "source_path": "proposal",
          "source_sequence": 0
        },
        {
          "data": {
            "binding": {
              "action_id": "urn:cognous:action:refund-issue-routine-v1",
              "actor": "urn:cognous:identity:refund-agent-1",
              "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
              "amount": 50.0,
              "authority_context_id": "urn:cognous:alvorada:public-stack-profile:0.1.0",
              "authority_context_status": "proposed_pending_governor_review",
              "authority_context_version": "0.1.0",
              "effective_max_effects": 1,
              "effects": 1,
              "grant_id": "urn:cognous:grant:routine-1",
              "grant_revision": "1",
              "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
              "manifest_id": "refund-integration-pilot-v1",
              "manifest_version": "1.1",
              "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
              "policy_versions": [
                {
                  "ref": "urn:cognous:policy:refund-policy",
                  "version": "1.0"
                }
              ],
              "principal": "urn:cognous:principal:refund-service",
              "proposal_commitment": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
              "requested_permissions": [
                "refund.issue.routine"
              ],
              "requirement_commitment": "sha256:f6f5f1915b8ad4dd3d65992b5faceb5e3c3a3dde67570759b44b0c56ec936617",
              "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
              "role_mapping_digest": "sha256:b6efb6a8d89e81f980d649015ac6e04e9126659c28ff4606972041c8c99beb8b",
              "role_mapping_version": "roles-v1",
              "target": "urn:cognous:synthetic-account:customer-001",
              "unit": "USD"
            },
            "decided_at": "2026-08-08T01:00:00+00:00",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "reasons": [],
            "result": "authorized"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "action_id": "urn:cognous:action:refund-issue-routine-v1",
            "authority_context_instance_id": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "grant_id": "urn:cognous:grant:routine-1",
            "grant_revision": "1",
            "manifest_id": "refund-integration-pilot-v1",
            "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "record_type": "runtime_decision",
          "recorded_at": "2026-08-08T01:00:00+00:00",
          "source_path": "decisions[0]",
          "source_sequence": 1
        },
        {
          "data": {
            "acknowledgement": {},
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "error": null,
            "started_at": "2026-08-08T01:00:00+00:00",
            "status": "attempted"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:2",
          "record_type": "control_plane_attempt_transition",
          "recorded_at": "2026-08-08T01:00:00+00:00",
          "source_path": "attempts[0]",
          "source_sequence": 2
        },
        {
          "data": {
            "acknowledgement": {
              "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
              "moltbot_safe_status": "executed",
              "newly_executed": true,
              "observation": {
                "destination_state": {
                  "amount": 50.0,
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "state": "applied",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "unit": "USD"
                },
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied"
              }
            },
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "error": null,
            "started_at": "2026-08-08T01:00:00+00:00",
            "status": "acknowledged"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
          "record_type": "control_plane_attempt_transition",
          "recorded_at": "2026-08-08T01:00:00+00:00",
          "source_path": "attempts[1]",
          "source_sequence": 3
        },
        {
          "data": {
            "destination_state": {},
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "observed_at": "2026-08-08T01:00:00+00:00",
            "state": "absent"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:effect_observation:4",
          "record_type": "effect_observation",
          "recorded_at": "2026-08-08T01:00:00+00:00",
          "source_path": "observations[0]",
          "source_sequence": 4
        },
        {
          "data": {
            "destination_state": {
              "amount": 50.0,
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "grant_id": "urn:cognous:grant:routine-1",
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "state": "applied",
              "target": "urn:cognous:synthetic-account:customer-001",
              "unit": "USD"
            },
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "observed_at": "2026-08-08T01:00:00+00:00",
            "state": "applied"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:effect_observation:5",
          "record_type": "effect_observation",
          "recorded_at": "2026-08-08T01:00:00+00:00",
          "source_path": "observations[1]",
          "source_sequence": 5
        },
        {
          "data": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "evaluation_time": "2026-08-08T01:00:00+00:00",
            "observation": {
              "destination_state": {},
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "observed_at": "2026-08-08T01:00:00+00:00",
              "state": "absent"
            },
            "observation_accepted": true,
            "observation_clock_tolerance_seconds": 5,
            "observation_max_age_seconds": 60,
            "reasons": [],
            "reconciled_at": "2026-10-07T01:36:40.747438+00:00",
            "result": "observed_absent",
            "retry_eligible": false
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:reconciliation:6",
          "record_type": "reconciliation",
          "recorded_at": "2026-10-07T01:36:40.747438+00:00",
          "source_path": "reconciliations[0]",
          "source_sequence": 6
        },
        {
          "data": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "evaluation_time": "2026-08-08T01:00:00+00:00",
            "observation": {
              "destination_state": {
                "amount": 50.0,
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "grant_id": "urn:cognous:grant:routine-1",
                "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                "payload": {
                  "customer_id": "customer-001",
                  "refund_reason": "duplicate"
                },
                "state": "applied",
                "target": "urn:cognous:synthetic-account:customer-001",
                "unit": "USD"
              },
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "observed_at": "2026-08-08T01:00:00+00:00",
              "state": "applied"
            },
            "observation_accepted": true,
            "observation_clock_tolerance_seconds": 5,
            "observation_max_age_seconds": 60,
            "reasons": [],
            "reconciled_at": "2026-10-07T01:36:40.749413+00:00",
            "result": "applied",
            "retry_eligible": false
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:reconciliation:7",
          "record_type": "reconciliation",
          "recorded_at": "2026-10-07T01:36:40.749413+00:00",
          "source_path": "reconciliations[1]",
          "source_sequence": 7
        },
        {
          "data": {
            "attempt_id": null,
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "operation": {
              "action_id": "urn:cognous:action:refund-issue-routine-v1",
              "actor": "urn:cognous:identity:refund-agent-1",
              "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
              "amount": 50.0,
              "authority_context_id": "urn:cognous:alvorada:public-stack-profile:0.1.0",
              "authority_domain": "customer-refunds",
              "effective_max_effects": 1,
              "effects": 1,
              "grant_id": "urn:cognous:grant:routine-1",
              "grant_revision": "1",
              "institution_id": "urn:cognous:institution:synthetic-customer-service",
              "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
              "manifest_id": "refund-integration-pilot-v1",
              "manifest_version": "1.1",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
              "principal": "urn:cognous:principal:refund-service",
              "proposal_commitment": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
              "requested_permissions": [
                "refund.issue.routine"
              ],
              "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
              "target": "urn:cognous:synthetic-account:customer-001",
              "unit": "USD"
            },
            "version": "0.2.0"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "action_id": "urn:cognous:action:refund-issue-routine-v1",
            "authority_context_profile_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "authority_domain": "customer-refunds",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "grant_id": "urn:cognous:grant:routine-1",
            "grant_revision": "1",
            "institution_id": "urn:cognous:institution:synthetic-customer-service",
            "manifest_id": "refund-integration-pilot-v1"
          },
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:8",
          "record_type": "execution_envelope",
          "recorded_at": null,
          "source_path": "moltbot.execution_envelope",
          "source_sequence": 8
        },
        {
          "data": {
            "attempt": {
              "acknowledgement": {
                "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
                "moltbot_safe_status": "executed",
                "newly_executed": true,
                "observation": {
                  "destination_state": {
                    "amount": 50.0,
                    "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                    "grant_id": "urn:cognous:grant:routine-1",
                    "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                    "payload": {
                      "customer_id": "customer-001",
                      "refund_reason": "duplicate"
                    },
                    "state": "applied",
                    "target": "urn:cognous:synthetic-account:customer-001",
                    "unit": "USD"
                  },
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "state": "applied"
                }
              },
              "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
              "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "error": null,
              "started_at": "2026-08-08T01:00:00+00:00",
              "status": "acknowledged"
            },
            "reconciliation": {
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "evaluation_time": "2026-08-08T01:00:00+00:00",
              "observation": {
                "destination_state": {
                  "amount": 50.0,
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "state": "applied",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "unit": "USD"
                },
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "observed_at": "2026-08-08T01:00:00+00:00",
                "state": "applied"
              },
              "observation_accepted": true,
              "observation_clock_tolerance_seconds": 5,
              "observation_max_age_seconds": 60,
              "reasons": [],
              "reconciled_at": "2026-10-07T01:36:40.749413+00:00",
              "result": "applied",
              "retry_eligible": false
            }
          },
          "evidence_class": "producer_reported",
          "identifiers": {},
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:executor_control_plane_evidence:9",
          "record_type": "executor_control_plane_evidence",
          "recorded_at": null,
          "source_path": "moltbot.control_plane_evidence",
          "source_sequence": 9
        },
        {
          "data": {
            "acknowledged": true,
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "attempted": true,
            "control_plane_evidence": {
              "attempt": {
                "acknowledgement": {
                  "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
                  "moltbot_safe_status": "executed",
                  "newly_executed": true,
                  "observation": {
                    "destination_state": {
                      "amount": 50.0,
                      "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                      "grant_id": "urn:cognous:grant:routine-1",
                      "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                      "payload": {
                        "customer_id": "customer-001",
                        "refund_reason": "duplicate"
                      },
                      "state": "applied",
                      "target": "urn:cognous:synthetic-account:customer-001",
                      "unit": "USD"
                    },
                    "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                    "state": "applied"
                  }
                },
                "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
                "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "error": null,
                "started_at": "2026-08-08T01:00:00+00:00",
                "status": "acknowledged"
              },
              "reconciliation": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "evaluation_time": "2026-08-08T01:00:00+00:00",
                "observation": {
                  "destination_state": {
                    "amount": 50.0,
                    "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                    "grant_id": "urn:cognous:grant:routine-1",
                    "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                    "payload": {
                      "customer_id": "customer-001",
                      "refund_reason": "duplicate"
                    },
                    "state": "applied",
                    "target": "urn:cognous:synthetic-account:customer-001",
                    "unit": "USD"
                  },
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "observed_at": "2026-08-08T01:00:00+00:00",
                  "state": "applied"
                },
                "observation_accepted": true,
                "observation_clock_tolerance_seconds": 5,
                "observation_max_age_seconds": 60,
                "reasons": [],
                "reconciled_at": "2026-10-07T01:36:40.749413+00:00",
                "result": "applied",
                "retry_eligible": false
              }
            },
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "error": null,
            "newly_executed": true,
            "observation": {
              "destination_state": {
                "amount": 50.0,
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "grant_id": "urn:cognous:grant:routine-1",
                "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                "payload": {
                  "customer_id": "customer-001",
                  "refund_reason": "duplicate"
                },
                "state": "applied",
                "target": "urn:cognous:synthetic-account:customer-001",
                "unit": "USD"
              },
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "observed_at": "2026-08-08T01:00:00+00:00",
              "state": "applied"
            },
            "observed_state": "applied",
            "status": "executed"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829"
          },
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10",
          "record_type": "execution_result",
          "recorded_at": null,
          "source_path": "moltbot.execution_result",
          "source_sequence": 10
        },
        {
          "data": {
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "created_at": 1791337000.7480268,
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829"
          },
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11",
          "record_type": "destination_attempt",
          "recorded_at": null,
          "source_path": "moltbot.attempts[0]",
          "source_sequence": 11
        },
        {
          "data": {
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "created_at": 1791337000.7481256,
            "error": null,
            "event_id": 1,
            "status": "attempted"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "event_id": "1"
          },
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:12",
          "record_type": "destination_attempt_event",
          "recorded_at": null,
          "source_path": "moltbot.attempt_events[0]",
          "source_sequence": 12
        },
        {
          "data": {
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "created_at": 1791337000.7486007,
            "error": null,
            "event_id": 2,
            "status": "executed"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "event_id": "2"
          },
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:13",
          "record_type": "destination_attempt_event",
          "recorded_at": null,
          "source_path": "moltbot.attempt_events[1]",
          "source_sequence": 13
        },
        {
          "data": {
            "acknowledgement": {
              "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
              "moltbot_safe_status": "executed",
              "newly_executed": true,
              "observation": {
                "destination_state": {
                  "amount": 50.0,
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "state": "applied",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "unit": "USD"
                },
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied"
              }
            },
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "error": null,
            "started_at": "2026-08-08T01:00:00+00:00",
            "status": "acknowledged"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "run_id": "run-1"
          },
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_id": "control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14",
          "record_type": "moltbot_attributed_control_plane_attempt",
          "recorded_at": null,
          "source_path": "moltbot.control_plane_attempts[0]",
          "source_sequence": 14
        },
        {
          "data": {
            "amount": 50.0,
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "grant_id": "urn:cognous:grant:routine-1",
            "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
            "payload_json": "{\"customer_id\":\"customer-001\",\"refund_reason\":\"duplicate\"}",
            "state": "applied",
            "target": "urn:cognous:synthetic-account:customer-001",
            "unit": "USD"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "grant_id": "urn:cognous:grant:routine-1"
          },
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15",
          "record_type": "destination_effect",
          "recorded_at": null,
          "source_path": "moltbot.effects[0]",
          "source_sequence": 15
        },
        {
          "data": {
            "destination_state": {
              "amount": 50.0,
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "grant_id": "urn:cognous:grant:routine-1",
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "state": "applied",
              "target": "urn:cognous:synthetic-account:customer-001",
              "unit": "USD"
            },
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "observed_at": "2026-08-08T01:00:00+00:00",
            "state": "applied"
          },
          "evidence_class": "producer_reported",
          "identifiers": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829"
          },
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:executor_observation:16",
          "record_type": "executor_observation",
          "recorded_at": null,
          "source_path": "moltbot.observations[0]",
          "source_sequence": 16
        }
      ],
      "run_id": "run-1",
      "semantics": {
        "destination_observation": "producer_reported",
        "external_effect_execution": false,
        "independent_effect_verification": false,
        "model_reexecution": false,
        "notes": "Replay reconstructs recorded events only; import never renews permission or creates an effect.",
        "policy_reevaluation": false,
        "record_reconstruction": true
      },
      "status": "reconstruction_complete"
    }
  },
  "retained_source_scope": "exact supplied sources, including declared redaction/derivative lineage; no unredaction",
  "lifecycle_records": {
    "runtime_proposal": [
      {
        "action_id": "urn:cognous:action:refund-issue-routine-v1",
        "actor": "urn:cognous:identity:refund-agent-1",
        "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
        "amount": 50.0,
        "authority_context_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
        "correlation_id": "case-1",
        "effects": 1,
        "evidence_refs": [
          "urn:cognous:evidence:refund-entitlement"
        ],
        "expected_side_effects": [],
        "expires_at": null,
        "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
        "manifest_id": "refund-integration-pilot-v1",
        "manifest_version": "1.1",
        "not_before": null,
        "payload": {
          "customer_id": "customer-001",
          "refund_reason": "duplicate"
        },
        "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
        "principal": "urn:cognous:principal:refund-service",
        "requested_permissions": [
          "refund.issue.routine"
        ],
        "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
        "risk_metadata": {},
        "run_id": "run-1",
        "target": "urn:cognous:synthetic-account:customer-001",
        "unit": "USD"
      }
    ],
    "runtime_decision": [
      {
        "binding": {
          "action_id": "urn:cognous:action:refund-issue-routine-v1",
          "actor": "urn:cognous:identity:refund-agent-1",
          "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
          "amount": 50.0,
          "authority_context_id": "urn:cognous:alvorada:public-stack-profile:0.1.0",
          "authority_context_status": "proposed_pending_governor_review",
          "authority_context_version": "0.1.0",
          "effective_max_effects": 1,
          "effects": 1,
          "grant_id": "urn:cognous:grant:routine-1",
          "grant_revision": "1",
          "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
          "manifest_id": "refund-integration-pilot-v1",
          "manifest_version": "1.1",
          "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "policy_versions": [
            {
              "ref": "urn:cognous:policy:refund-policy",
              "version": "1.0"
            }
          ],
          "principal": "urn:cognous:principal:refund-service",
          "proposal_commitment": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
          "requested_permissions": [
            "refund.issue.routine"
          ],
          "requirement_commitment": "sha256:f6f5f1915b8ad4dd3d65992b5faceb5e3c3a3dde67570759b44b0c56ec936617",
          "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
          "role_mapping_digest": "sha256:b6efb6a8d89e81f980d649015ac6e04e9126659c28ff4606972041c8c99beb8b",
          "role_mapping_version": "roles-v1",
          "target": "urn:cognous:synthetic-account:customer-001",
          "unit": "USD"
        },
        "decided_at": "2026-08-08T01:00:00+00:00",
        "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "reasons": [],
        "result": "authorized"
      }
    ],
    "control_plane_attempt_transition": [
      {
        "acknowledgement": {},
        "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
        "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "error": null,
        "started_at": "2026-08-08T01:00:00+00:00",
        "status": "attempted"
      },
      {
        "acknowledgement": {
          "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
          "moltbot_safe_status": "executed",
          "newly_executed": true,
          "observation": {
            "destination_state": {
              "amount": 50.0,
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "grant_id": "urn:cognous:grant:routine-1",
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "state": "applied",
              "target": "urn:cognous:synthetic-account:customer-001",
              "unit": "USD"
            },
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "state": "applied"
          }
        },
        "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
        "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "error": null,
        "started_at": "2026-08-08T01:00:00+00:00",
        "status": "acknowledged"
      }
    ],
    "effect_observation": [
      {
        "destination_state": {},
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "observed_at": "2026-08-08T01:00:00+00:00",
        "state": "absent"
      },
      {
        "destination_state": {
          "amount": 50.0,
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "grant_id": "urn:cognous:grant:routine-1",
          "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
          "payload": {
            "customer_id": "customer-001",
            "refund_reason": "duplicate"
          },
          "state": "applied",
          "target": "urn:cognous:synthetic-account:customer-001",
          "unit": "USD"
        },
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "observed_at": "2026-08-08T01:00:00+00:00",
        "state": "applied"
      }
    ],
    "reconciliation": [
      {
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "evaluation_time": "2026-08-08T01:00:00+00:00",
        "observation": {
          "destination_state": {},
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "observed_at": "2026-08-08T01:00:00+00:00",
          "state": "absent"
        },
        "observation_accepted": true,
        "observation_clock_tolerance_seconds": 5,
        "observation_max_age_seconds": 60,
        "reasons": [],
        "reconciled_at": "2026-10-07T01:36:40.747438+00:00",
        "result": "observed_absent",
        "retry_eligible": false
      },
      {
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "evaluation_time": "2026-08-08T01:00:00+00:00",
        "observation": {
          "destination_state": {
            "amount": 50.0,
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "grant_id": "urn:cognous:grant:routine-1",
            "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
            "payload": {
              "customer_id": "customer-001",
              "refund_reason": "duplicate"
            },
            "state": "applied",
            "target": "urn:cognous:synthetic-account:customer-001",
            "unit": "USD"
          },
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "observed_at": "2026-08-08T01:00:00+00:00",
          "state": "applied"
        },
        "observation_accepted": true,
        "observation_clock_tolerance_seconds": 5,
        "observation_max_age_seconds": 60,
        "reasons": [],
        "reconciled_at": "2026-10-07T01:36:40.749413+00:00",
        "result": "applied",
        "retry_eligible": false
      }
    ],
    "execution_envelope": [
      {
        "attempt_id": null,
        "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "operation": {
          "action_id": "urn:cognous:action:refund-issue-routine-v1",
          "actor": "urn:cognous:identity:refund-agent-1",
          "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
          "amount": 50.0,
          "authority_context_id": "urn:cognous:alvorada:public-stack-profile:0.1.0",
          "authority_domain": "customer-refunds",
          "effective_max_effects": 1,
          "effects": 1,
          "grant_id": "urn:cognous:grant:routine-1",
          "grant_revision": "1",
          "institution_id": "urn:cognous:institution:synthetic-customer-service",
          "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
          "manifest_id": "refund-integration-pilot-v1",
          "manifest_version": "1.1",
          "payload": {
            "customer_id": "customer-001",
            "refund_reason": "duplicate"
          },
          "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "principal": "urn:cognous:principal:refund-service",
          "proposal_commitment": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
          "requested_permissions": [
            "refund.issue.routine"
          ],
          "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
          "target": "urn:cognous:synthetic-account:customer-001",
          "unit": "USD"
        },
        "version": "0.2.0"
      }
    ],
    "executor_control_plane_evidence": [
      {
        "attempt": {
          "acknowledgement": {
            "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
            "moltbot_safe_status": "executed",
            "newly_executed": true,
            "observation": {
              "destination_state": {
                "amount": 50.0,
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "grant_id": "urn:cognous:grant:routine-1",
                "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                "payload": {
                  "customer_id": "customer-001",
                  "refund_reason": "duplicate"
                },
                "state": "applied",
                "target": "urn:cognous:synthetic-account:customer-001",
                "unit": "USD"
              },
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "state": "applied"
            }
          },
          "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
          "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "error": null,
          "started_at": "2026-08-08T01:00:00+00:00",
          "status": "acknowledged"
        },
        "reconciliation": {
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "evaluation_time": "2026-08-08T01:00:00+00:00",
          "observation": {
            "destination_state": {
              "amount": 50.0,
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "grant_id": "urn:cognous:grant:routine-1",
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "state": "applied",
              "target": "urn:cognous:synthetic-account:customer-001",
              "unit": "USD"
            },
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "observed_at": "2026-08-08T01:00:00+00:00",
            "state": "applied"
          },
          "observation_accepted": true,
          "observation_clock_tolerance_seconds": 5,
          "observation_max_age_seconds": 60,
          "reasons": [],
          "reconciled_at": "2026-10-07T01:36:40.749413+00:00",
          "result": "applied",
          "retry_eligible": false
        }
      }
    ],
    "execution_result": [
      {
        "acknowledged": true,
        "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
        "attempted": true,
        "control_plane_evidence": {
          "attempt": {
            "acknowledgement": {
              "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
              "moltbot_safe_status": "executed",
              "newly_executed": true,
              "observation": {
                "destination_state": {
                  "amount": 50.0,
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "state": "applied",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "unit": "USD"
                },
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied"
              }
            },
            "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
            "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "error": null,
            "started_at": "2026-08-08T01:00:00+00:00",
            "status": "acknowledged"
          },
          "reconciliation": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "evaluation_time": "2026-08-08T01:00:00+00:00",
            "observation": {
              "destination_state": {
                "amount": 50.0,
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "grant_id": "urn:cognous:grant:routine-1",
                "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
                "payload": {
                  "customer_id": "customer-001",
                  "refund_reason": "duplicate"
                },
                "state": "applied",
                "target": "urn:cognous:synthetic-account:customer-001",
                "unit": "USD"
              },
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "observed_at": "2026-08-08T01:00:00+00:00",
              "state": "applied"
            },
            "observation_accepted": true,
            "observation_clock_tolerance_seconds": 5,
            "observation_max_age_seconds": 60,
            "reasons": [],
            "reconciled_at": "2026-10-07T01:36:40.749413+00:00",
            "result": "applied",
            "retry_eligible": false
          }
        },
        "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "error": null,
        "newly_executed": true,
        "observation": {
          "destination_state": {
            "amount": 50.0,
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "grant_id": "urn:cognous:grant:routine-1",
            "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
            "payload": {
              "customer_id": "customer-001",
              "refund_reason": "duplicate"
            },
            "state": "applied",
            "target": "urn:cognous:synthetic-account:customer-001",
            "unit": "USD"
          },
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "observed_at": "2026-08-08T01:00:00+00:00",
          "state": "applied"
        },
        "observed_state": "applied",
        "status": "executed"
      }
    ],
    "destination_attempt": [
      {
        "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
        "created_at": 1791337000.7480268,
        "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
      }
    ],
    "destination_attempt_event": [
      {
        "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
        "created_at": 1791337000.7481256,
        "error": null,
        "event_id": 1,
        "status": "attempted"
      },
      {
        "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
        "created_at": 1791337000.7486007,
        "error": null,
        "event_id": 2,
        "status": "executed"
      }
    ],
    "moltbot_attributed_control_plane_attempt": [
      {
        "acknowledgement": {
          "attempt_id": "8e9a73e2-27cd-4aa4-9b08-1988b8d2b519",
          "moltbot_safe_status": "executed",
          "newly_executed": true,
          "observation": {
            "destination_state": {
              "amount": 50.0,
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "grant_id": "urn:cognous:grant:routine-1",
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "state": "applied",
              "target": "urn:cognous:synthetic-account:customer-001",
              "unit": "USD"
            },
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "state": "applied"
          }
        },
        "attempt_id": "9201baaa-2040-4293-9594-581e04ad5395",
        "decision_id": "31cede33-11b3-4027-ab62-3071b5642ace",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "error": null,
        "started_at": "2026-08-08T01:00:00+00:00",
        "status": "acknowledged"
      }
    ],
    "destination_effect": [
      {
        "amount": 50.0,
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "grant_id": "urn:cognous:grant:routine-1",
        "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
        "payload_json": "{\"customer_id\":\"customer-001\",\"refund_reason\":\"duplicate\"}",
        "state": "applied",
        "target": "urn:cognous:synthetic-account:customer-001",
        "unit": "USD"
      }
    ],
    "executor_observation": [
      {
        "destination_state": {
          "amount": 50.0,
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "grant_id": "urn:cognous:grant:routine-1",
          "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
          "payload": {
            "customer_id": "customer-001",
            "refund_reason": "duplicate"
          },
          "state": "applied",
          "target": "urn:cognous:synthetic-account:customer-001",
          "unit": "USD"
        },
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "observed_at": "2026-08-08T01:00:00+00:00",
        "state": "applied"
      }
    ]
  },
  "explicit_links": [
    {
      "basis": "Producer-supplied Control Plane attempt evidence exactly matches the retained Control Plane run record.",
      "establishes_identity_equivalence": true,
      "from_record_id": "control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14",
      "link_type": "explicit",
      "to_record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3"
    },
    {
      "basis": "Control Plane acknowledgement explicitly supplied executor attempt_id.",
      "establishes_identity_equivalence": false,
      "from_record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
      "link_type": "explicit",
      "to_record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11"
    }
  ],
  "reconstruction_completeness": "reconstruction_complete"
}</pre>
