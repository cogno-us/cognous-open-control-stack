# AOI-C01: authority-to-observation envelope (proposed contract draft)

**Proposed, documentation only.** It records no decision, adopts no ADR, changes no locked component and defines no schema owner. It covers AOI-0 (source-to-field matrix) and AOI-1 (envelope and Human Intervention Record) for steps 1.2, 1.4 and 1.5, and the design constraints for AOI-3 and AOI-4. ADR-P01 to P09 are used as labeled proposed assumptions. Release and production remain on HOLD. Status of every normative sentence: PROPOSED until the M0 gate records an outcome in a versioned successor document.

Source reading for the matrix is the reading already recorded in [../s03/identity-and-lifecycle.md](../s03/identity-and-lifecycle.md) (Control Plane `0a41faa9`, Execution Runtime `ec728da6`, ODES `e86a25a1`) and [../s02/contracts/1.4-evidence-handoff.md](../s02/contracts/1.4-evidence-handoff.md) (Orchestrator `a745e131`). It was not re-read for this draft; where a field was not found in those readings the status says so. VERIFIED means found in a recorded reading of the stated revision; INFERRED means concluded from such a reading; REQUIRES INVESTIGATION means not searched.

## 1. Principle

The envelope is a correlation record: it names the existing records that govern and describe one observed event, and says for each field how it was obtained. It does not authorize, certify, qualify, prove an effect, or replace any record it references.

Three rules follow from the existing contracts:

1. **Extend profiles, do not change them.** A committed field changes only opt-in or under a new profile identifier ([1.2 section 4](../s02/contracts/1.2-authority-and-separation.md)). The envelope is a new record with its own profile; historical digest semantics stay as they are.
2. **Reference, do not restate.** The envelope carries identifiers and commitments of decisions, attempts, observations and evidence. It does not carry a decision result, attempt status or observation state of its own (the same rule as the workflow vocabulary in [../s03/workflow-state-reconciliation.md](../s03/workflow-state-reconciliation.md)).
3. **No state is silently filled.** A field with no source carries a typed state, not a default and not a guess.

## 2. Record shape (conceptual; names frozen only at the M0 gate)

| Category | Minimum proposed content | Written by |
|---|---|---|
| Identity | event reference; trace and span references where an exporter exists; principal reference; agent identity reference with an attestation state; runtime instance, session and workflow references; tenant and scope; delegation parent where applicable. A name is never treated as an enterprise identity | Producer of the envelope, copied from source records |
| Authority | decision reference; grant id and revision; rule-set or registry digest and epoch; effective capability and scope; sampled authority time with the observer's clock provenance; recheck and revocation status | Copied from the deciding component's record |
| Action and effect | requested-operation commitment; invocation, attempt and idempotency references; before-effect recheck outcome; committed, refused or unknown; independently observed readback when the destination supports it | Copied from attempt, observation and result records |
| Evidence | ODES decision, negative-record and custody references; source, configuration and evaluator pins; observation producer identity and timestamp; typed absence or invalidity | Copied or referenced |
| Human and state | review trigger; mandatory or discretionary basis; reviewer identity and authority; disposition (see section 4); an ISS governed-state-transition reference only where an ISS-owned accepted export exists | Copied from the review record; ISS reference owned by ISS |
| Completeness | per-field presence, capture mode (source or derived), availability, and the unsupported, unobserved, not-applicable and unknown distinctions; the observer's capability | Producer of the envelope |

The envelope has no member for a verdict, an expectation, a pass, a pin choice or an authorization. A producer cannot write one and a consumer must not read any field as one (same rule as the step 1.4 envelope). An issued envelope is immutable; supersession is by a new envelope with a new digest.

## 3. Source-to-field matrix (AOI-0)

State column: where the field already exists in a record read earlier. "Join" is how the envelope would reference it. No field here is claimed to be emitted for correlation today; the matrix says what exists, not what is joined.

| Envelope field | Existing source record and field | State | Join, and gap |
|---|---|---|---|
| tenant | `tenant_id` (`bounded.py:154,167,184`) | VERIFIED | Optional; omitted when unset. Single-tenant must be stated by the profile |
| principal reference | `RuntimeProposal.principal`; `principal_id` in the operation-identity code | VERIFIED | One value, two names (1.5 row 2) |
| agent identity reference | `RuntimeProposal.actor`; runtime `agent_id` (`audit.py`, `engine.py`, `permissions.py`) | VERIFIED | Two names, relation not declared (1.5 row 3). **Attestation or proof-of-binding: no field found**; state UNSUPPORTED by default |
| runtime instance, session | None found in the readings | REQUIRES INVESTIGATION | Not searched for in this pass |
| workflow, worker, task | No field in the sources read (1.5 rows 4 to 6) | VERIFIED (absence by search) | Orchestrator-owned if introduced; correlation only (SP-03) |
| delegation parent | None found | REQUIRES INVESTIGATION | |
| event reference; trace and span references | `correlation_id` and `run_id` are optional on `RuntimeProposal`; whether they enter any commitment is not known | REQUIRES INVESTIGATION | Optional in M1; no OTel identifier source read |
| decision reference | `RuntimeDecision.decision_id` (`bounded.py:347`) | VERIFIED | Direct reference |
| grant id and revision | `grant_id`, `grant_revision` in the authorization binding | VERIFIED | `grant_revision` changes on renewal (SP-02) |
| rule-set or registry digest and epoch | `RuntimeDecision.rule_identity` (optional dict, `bounded.py:343-346`); ODES `rule-revision` | VERIFIED | Covers rule kinds, not the evaluator set or an activation epoch (S01 CA-03). The registry digest and epoch are proposed at 1.3 and need the FP-04 opt-in member before a decision carries them |
| effective capability and scope | Authorization binding scope fields | INFERRED | Exact field list not itemized in the recorded reading |
| sampled authority time; observer clock provenance | `observed_at` exists on `EffectObservation` (`bounded.py:404-409`); no clock-provenance field found | VERIFIED (time); REQUIRES INVESTIGATION (provenance) | Per-domain clock provenance and order uncertainty must be preserved (section 6) |
| recheck and revocation status | The Control Plane holds "effective authorization at effect time" in the exclusive-powers table ([1.2](../s02/contracts/1.2-authority-and-separation.md) section 2); the addendum assigns effect-time revalidation to the Runtime (see README section 3); no result field name was recorded | INFERRED | Which component's record carries the recheck outcome, and its field list, REQUIRES INVESTIGATION |
| requested-operation commitment | `payload_commitment`; `proposal_commitment` in the binding | VERIFIED | Identified by commitment, not id (1.5 row 7) |
| invocation and attempt references | `EffectAttempt.attempt_id`; local runtime attempt id returned by the adapter when present | VERIFIED | Two namespaces per dispatch (SP-04) |
| idempotency reference | ODES `operation_id` (opt-in `operation_identity`); `effect_id` = commitment of `{proposal, grant_id, grant_revision}` | VERIFIED | Stable identity only when the profile is selected (SP-01) |
| committed, refused, unknown | Attempt status; executor lifecycle status; six `unknown` enumerations (1.5 section 5) | VERIFIED | Referenced by qualified name; never merged |
| independently observed readback | `EffectObservation` (`effect_id`, `observed_at`, `state`, `destination_state`) | VERIFIED | No observation id of its own (1.5 row 16); join by `effect_id` and `observed_at` |
| ODES decision, negative record, custody references | ODES contracts exist; `evidence_refs` free-form list on the proposal; `evidence_id` in `decision_input_profile.py` | VERIFIED (existence) | No registry of artifact ids (1.5 row 17); custody reference format not itemized |
| source, configuration and evaluator pins | Hub `component-lock.json`; 1.4 envelope `tuple` | VERIFIED | Joined through the 1.4 envelope |
| observation producer identity | None found | REQUIRES INVESTIGATION | Needed to state "observation producer" in C02 |
| human review: trigger, basis, reviewer, authority, disposition | `approval_ref` (`bounded.py:173`) only | VERIFIED (one reference) | The other four have no verified source (section 4) |
| ISS governed-state reference | Not an OCS record | n/a | Owned by ISS; only if separately accepted |

Summary: fields with a verified source are the decision, grant, commitment, attempt, effect, observation and rule-identity references. Fields with no verified source are agent attestation, runtime instance and session, delegation parent, trace and span identifiers, clock provenance, observation producer identity, and four of five human-review fields. Those are carried as typed states in M1, not invented.

## 4. Human Intervention Record

The addendum asks the five intervention fields be preserved and that scope and effectiveness claims be qualified separately.

| Field | Content | Existing source |
|---|---|---|
| Review identity | Who reviewed (principal reference) | None verified beyond `approval_ref` |
| Authority | The authority under which the reviewer acted; scope of what they could approve | None verified |
| Trigger | Why review occurred; mandatory (a rule required it) or discretionary (agent or operator asked) | None verified |
| Evidence shown | References to what the reviewer was shown, including any agent recommendation | None verified |
| Outcome | Disposition and the response, including refusal | `approval_ref` only |

Rules:

- A review record is evidence of what happened, never an authorization (F-04, [1.2 section 3](../s02/contracts/1.2-authority-and-separation.md)). A human sign-off is not governance; the validity of the approval context matters (owner paper, section 7). Whether OCS evaluates approval-context validity beyond an approval status is REQUIRES INVESTIGATION and stays open.
- Scope and effectiveness are different claims: "an approval existed" does not say it covered this operation or was informed. The record states which was observed.
- Applies only where an approval-bearing path is in the profile. For the one bounded refund scenario the path classes in scope are decided at the M0 gate (packet row 16); other paths carry NOT_APPLICABLE with the predicate.

## 5. Authority transitions and recovery (AOI-3, first half)

Stated as constraints on the correlation, not new behavior:

- **Effect versus attempt.** Authorization at decision time, authority at effect time and the observed effect are three records. A grant recorded in a trace may have expired before the effect. The envelope records the time each was sampled and the clock domain, not an inferred order.
- **Residual race.** Revocation between recheck and effect is a bounded residual. No instantaneous revocation guarantee is implied; the envelope preserves the exact source and timing of the recheck.
- **Reconcile-only recovery.** After any `unknown`, the envelope may be extended by a new envelope that references the reconciliation record. It never converts the `unknown` to success, absence or retry (F-06, ADR-P07). No blind retry.
- **Configuration provenance.** The registry digest, epoch and evaluator pins at decision time are recorded by reference once 1.3 and FP-04 settle where they live.
- **Memory-transition provenance** (second half of AOI-3) is deferred: OCS has no memory authority and none is added. Where a memory or state transition matters, the envelope carries only an ISS-owned accepted reference.

## 6. Timing and identity caveats (carried from the addendum)

- Per-domain clock provenance is preserved; where clocks are not comparable the record states order uncertainty instead of inferring a sequence.
- A digest establishes byte identity, not issuer authorization.
- Telemetry absence is not evidence of no effect or no violation.
- A name is not an identity: same-name agents and substituted instances are different records unless a binding says otherwise.
- No cross-store atomicity is implied. Each store keeps its own custody and the envelope joins by reference.

## 7. Informational OTel projection: constraints only (AOI-4)

No projection design is drafted in this pass. The constraints any later design must meet:

- Optional for M1. Source records are instrumented first.
- Export failure, drop or delay never affects the authorization path and never erases or alters authoritative custody.
- A projected span is not an authority record. It carries references to the envelope and never the sole copy of a field.
- Version mismatch, tampering and clock mismatch are detectable and classified, not repaired by inference.
- Security and privacy: selective disclosure and redaction declared per field in [aoi-c02-paired-coverage.md](aoi-c02-paired-coverage.md); no hidden reasoning or confidence signal is exported as evidence.
- Round-trip is claimed only within a declared field set.

## 8. Failure and refusal semantics

| Condition | Outcome |
|---|---|
| Required field absent from source | Envelope issued with state UNSUPPORTED or UNOBSERVED for that field, never omitted silently; the profile says whether that state fails the coverage claim |
| Referenced record not found or digest mismatch | Envelope refused at intake; the reference is reported as invalid, not repaired |
| A field that carries a verdict, pin choice or expectation | Refused as an unknown member |
| Tuple differs from the supplied lock | Refused (same as 1.4) |
| Envelope presented after supersession | Reported as superseded |
| Identity asserted but not independently verified | Recorded as asserted; never promoted to verified by the producer |

## 9. Open items

- Whether `correlation_id` and `run_id` enter any commitment (decides whether they can carry workflow correlation).
- Where the AOI profile identifier and digest live (an unowned pin carrier today; proposal: the hub-owned registry artifact and the single opt-in context member, FP-04, F3 package FP-05).
- Source for agent attestation, runtime instance, session, clock provenance and observation producer identity.
- Field list for effect-time recheck and revocation status.
- Whether OCS evaluates approval-context validity.

## 10. Exit check for steps 1.2 and 1.4 (AOI part)

An independent reader can see which envelope fields have a verified source and which carry a typed state; that the envelope only references records and decides nothing; which fields are copied from which component; and which questions are open and who owns them.
