# Step 1.5 draft: identity, state and recovery model

**Proposed contract draft, documentation only.** Nothing here changes a locked component, adds a state machine, creates an identity service or records an operator decision. It answers [s01/defects.md](../s01/defects.md) PD-L01, PD-L03, PD-L04, PD-L05 and PD-L06 for review at the M0 gate.

Source reading for this draft (VERIFIED means read at the stated revision; nothing was executed): Control Plane `0a41faa9` (`src/agent_control_plane/bounded.py`, `models.py`), Execution Runtime `ec728da6` (`engine/control_plane_adapter.py`), ODES `e86a25a1` (`contracts/execution-attempt-lifecycle`, `contracts/operation-identity`). Not re-read: the orchestrator reserved state list, Replay `importers.py`, verifier `rules_lifecycle.py` (their findings stay as recorded in S01).

## 1. Principle

OCS already has an attempt lifecycle, an observation vocabulary and an operation-identity contract. Step 1.5 delivers a mapping and a crosswalk onto them. It adds no global state machine and no universal identity service. Workflow coordination vocabulary lives in the Orchestrator and is namespaced apart from attempt and observation vocabulary.

## 2. Identity crosswalk (the 18 identifiers of V2-P1-06)

| # | Identifier | Where it exists today | Observation | Gap or conflict |
|---|---|---|---|---|
| 1 | tenant | `tenant_id` on `TenantRuntimeProposal` and tenant bindings (`bounded.py:154,167,184`); omitted when unset so tenantless evidence serialises as before (`bounded.py:195`) | VERIFIED | Optional; the minimum profile must state whether it is single-tenant |
| 2 | principal | `RuntimeProposal.principal` (`bounded.py:127-128`, actor and principal); `principal_id` in the operation-identity code (`bounded.py:739,1545,1557`, passed from `binding.principal`) | VERIFIED | Same value, two names |
| 3 | agent | `RuntimeProposal.actor`; runtime `agent_id` in `engine/audit.py`, `engine.py`, `permissions.py` | VERIFIED | Two names in two components; relation not declared |
| 4 | worker | No field in the four sources read | VERIFIED (absence by search) | Gap: Orchestrator-owned if introduced |
| 5 | workflow | No field in the four sources read | VERIFIED (absence by search) | Gap: Orchestrator-owned |
| 6 | task | No field in the four sources read | VERIFIED (absence by search) | Gap: Orchestrator-owned |
| 7 | proposal | No `proposal_id`; identified by `payload_commitment` on the proposal and `proposal_commitment` in the authorization binding | VERIFIED | Identified by commitment, not by id |
| 8 | action | `action_id` is "Unique identifier for this action proposal" (`models.py:66`); also on `RuntimeProposal.action_id`; a manifest action type is identified by `action_id` in manifest validation (`manifest_validation.py:94-107`) | VERIFIED | Overloaded: one name for a proposal instance and for a manifest action type (PD-L03) |
| 9 | policy | `RefusalInputVersion.input_type` includes `policy` with an `input_id` (`bounded.py`); no `policy_id` field | VERIFIED | Referenced only as a refusal input |
| 10 | rule-set | `RuntimeDecision.rule_identity` (a dict, optional, `bounded.py:343-346`); ODES `rule-revision` contract | VERIFIED | Covers rule kinds, not the evaluator set or an activation epoch (S01 CA-03) |
| 11 | grant | `grant_id` and `grant_revision` in the authorization binding | VERIFIED | `grant_revision` changes on renewal |
| 12 | approval | `approval_ref` (`bounded.py:173`) | VERIFIED | S01 recorded `approval_id` elsewhere; not in the four sources read; relation REQUIRES INVESTIGATION |
| 13 | decision | `RuntimeDecision.decision_id` (`bounded.py:347`) | VERIFIED | None |
| 14 | effect | `effect_id` = commitment of `{proposal, grant_id, grant_revision}` (`bounded.py:2010-2015`); ODES `operation_id` is the stable business identity supplied by the grant issuer (`contracts/operation-identity/README.md`) | VERIFIED | `effect_id` changes when a grant is renewed, so a stalled attempt on revision 1 and a fresh attempt on revision 2 are two effects of one operation. The operation-identity profile is opt-in and is selected only by the host setting `RuntimeAuthorityProfile.operation_identity`; with it unset nothing applies |
| 15 | attempt | `EffectAttempt.attempt_id` in the Control Plane (`bounded.py:361-363`); the runtime adapter returns the local attempt id when a local attempt exists and the Control Plane's otherwise (`control_plane_adapter.py:~414`) | VERIFIED | Two attempt-id namespaces per dispatch |
| 16 | observation | `EffectObservation` holds `effect_id`, `observed_at`, `state`, `destination_state` (`bounded.py:404-409`) | VERIFIED | No observation id of its own |
| 17 | evidence artifact | `evidence_refs: list[str]` on the proposal; `evidence_id` in `decision_input_profile.py` | VERIFIED | Free-form references, no registry of artifact ids |
| 18 | qualification execution | Not in the locked sources read; owned by Qualification (job and run records) | INFERRED from S01 | Out of the Control Plane identity chain by design; the handoff (step 1.4) must carry a reference |

The proposal model does not forbid extra members (S01 PD-L03). Orchestrator identifiers (rows 4 to 6) must therefore not be added to proposal payloads on the assumption they will be refused or ignored. Whether the optional `correlation_id` and `run_id` on `RuntimeProposal` enter any commitment is REQUIRES INVESTIGATION and decides whether they can carry workflow correlation.

## 3. Proposed identity decisions

| Id | Proposal | Reason |
|---|---|---|
| SP-01 | The stable identity of a business effect is the ODES `operation_id`, selected for the minimum profile through the existing `operation_identity` host setting; no new identifier is introduced | The contract already exists and states the renewal problem. Choosing it in a profile is configuration of an existing opt-in, though its effect on default behavior and hashes must be shown unchanged when unset |
| SP-02 | `effect_id` stays as it is (per grant revision); documents say "effect" for the revision-specific commitment and "operation" for the stable identity | Removes the ambiguity without changing a committed field |
| SP-03 | Worker, workflow and task identifiers are created, owned and recorded only by the Orchestrator; they are correlation, never inputs to an authorization decision, grant, rule selection or verdict | Prevents the Orchestrator acquiring authority by identity |
| SP-04 | The two attempt namespaces are documented as local (runtime) and control-plane attempts joined by the adapter result; the crosswalk names the join field | Documentation of an existing join; no change |
| SP-05 | `action_id` use is disambiguated in documents as `action-proposal id` versus `action type id`; no field rename | A rename would change committed bytes |

SP-01 is the answer this draft proposes to owner decision 6 ("stable effect identifier: `operation_id` versus a new identifier"). It is a proposal; making the profile mandatory for the minimum profile is for review.

## 4. Lifecycle term mapping (V2-P1-05)

| Term | Existing vocabulary | Where |
|---|---|---|
| requested | None; the proposal exists as a record before any decision | `RuntimeProposal` |
| authorized | Decision result `authorized` (not an attempt state) | `RuntimeDecision.result` (`authorized`, `hold`, `deny`) |
| denied | Decision result `deny`; attempt status `denied` in the executor lifecycle | `bounded.py:343-352`; ODES `execution-attempt-lifecycle` schema |
| attempted | Attempt status `attempted` | Control Plane `EffectAttempt.status`; ODES executor lifecycle |
| dispatched | None | Gap |
| acknowledged | Control Plane attempt status `acknowledged`; in the executor lifecycle acknowledgement is a flag on a result, not a status | `EffectAttempt.status`; ODES result matrix |
| observed | Observation state (`applied`, `partial`, `absent`, `unknown`); an effect-free result status `observed` | `EffectObservation.state`; ODES schema |
| verified | None | Gap |
| unknown | Six distinct enumerations (section 5) | See below |
| reconciled | Executor lifecycle status `reconciled` | ODES transitions |
| cancelled | None; no terminal cancelled state, delegation unsupported | S01 PD-L05 |

Allowed attempt transitions are defined by the ODES contract (executor: `attempted` to `executed`, `partial`, `failed`, `unknown`, `denied`, `reconciled`; `unknown` to `executed`, `partial`, `failed`, `reconciled`; `executed` and `partial` to `unknown` or `reconciled`; `failed`, `denied`, `reconciled` terminal. Control Plane: `attempted` to `acknowledged`, `unknown`, `failed`, `partial`; `acknowledged`, `partial`, `failed` terminal). A closed attempt is never reopened. These are cited, not redefined.

Gaps `requested`, `dispatched`, `verified` and `cancelled` become Orchestrator workflow states, written `workflow.requested`, `workflow.dispatched`, `workflow.verified`, `workflow.cancelled`. They never replace or alias an attempt or observation state. The 15-state list in V2-P1-03 and the Orchestrator reserved list of seven names (PD-L01) are reconciled at step 1.5 delivery against the Orchestrator source, which this draft did not re-read. Cancellation does not reverse a committed effect; compensation needs new authority.

## 5. The word "unknown"

Six enumerations carry it. Records and documents qualify it by enumeration.

| Qualified name | Enumeration | Source |
|---|---|---|
| `observation.unknown` | `EffectObservation.state` and ODES observation state | `bounded.py:404-409`; ODES schema |
| `attempt.unknown` | Control Plane `EffectAttempt.status` | `bounded.py:361-375` |
| `executor-attempt.unknown` | ODES executor lifecycle status | ODES schema |
| `result.unknown` | `observed_state` of an execution result | ODES result matrix |
| `provider.unknown` | Provider acceptance (`accepted`, `rejected`, `unknown`) | runtime `operation_admission.py:16` |
| `recovery.unknown` | Recovery status (`applied`, `partial`, `hold`, `unknown`) | ODES schema |

Rule (preserves [ADR-P07](../s02/adr-proposals.md#adr-p07-crash-continuation)): no `unknown` of any kind is converted to success, absence or a retry. It leaves only through reconciliation against independently observed state.

## 6. Recovery model

- Reconcile-only. Recovery inspects durable history and independently observed effect state; a timeout is not permission to execute again.
- Any resumption or redispatch needs a separately versioned interface, an independently qualified battery and explicit authorization. That interface is not in the minimum profile.
- Evidence for recovery is re-pinned to the selected tuple before it is cited: Q6 evidence is pinned to runtime `1b0a9e32`, 169 commits behind the lock (PD-L07).
- The two adapter-conformance schemas (`operation_admission.py:124-165`; Orchestrator `reconciliation.py:19-34`, PD-L06) are reconciled in step 3.5. Neither grants authority.

## 7. Exit check for step 1.5

An independent reader can take any identifier of the 18 and find its owner, its field and its stability; can map each lifecycle term to one existing vocabulary or to a namespaced workflow state; and finds no new state machine, identity service or authority.
