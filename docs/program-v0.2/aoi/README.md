# Authority-to-Observation Integrity (AOI) addendum (proposed)

**Non-authorizing, documentation only.** Profile identifier: `OCS-AOI/0.2-PROPOSED`. This record folds the OCS v0.2 Builder Observability Engineering Addendum (22 October 2026, supplied by the operator) into the v0.2 plan. It starts no implementation, changes no locked component, edits no Qualification expectation, oracle or verdict logic, touches no Qualification controller, defines no ISS V6 contract, and records no operator decision. Release and production remain on HOLD. The 24 step identifiers and the 49-row [original register](../original-register.md) are unchanged; no step was added, removed or renumbered. Static reading only; nothing was executed, so nothing here claims an authoritative observation already exists.

## 1. What the addendum asks, and what this record does

The addendum adopts a cross-stack "Authority-to-Observation Integrity" concept: every observed event should be joinable to the authority that governed it and to the evidence that records it, with unsupported, inferred and unknown fields kept as first-class states. It narrows the builder's job to contracts and source mappings for OCS v0.2, not a second telemetry authority.

| Deliverable asked (addendum section 9) | Where it is |
|---|---|
| Source-to-field matrix | [aoi-c01-envelope.md](aoi-c01-envelope.md) section 3 |
| Two proposed contracts | AOI-C01 [aoi-c01-envelope.md](aoi-c01-envelope.md); AOI-C02 [aoi-c02-paired-coverage.md](aoi-c02-paired-coverage.md) |
| Positive and negative test inventory; privacy and integrity impact | [tests-and-impact.md](tests-and-impact.md) |
| Independently reviewable M0 packet | Section 6 below (additions to the [M0 decision packet](../s02/m0-decision-packet.md)) |
| Qualification request mapping Q01 to Q07 | [qualification-request.md](qualification-request.md) (an input to Qualification, not posted to its controller) |
| Exact source and profile | Section 7 below |

## 2. Reconciliation with the earlier paired-coverage proposal

The addendum asks that the AOI concept be reconciled with the earlier Enforcement Coverage and Observability Coverage proposal. Disposition for each issue, with the existing record it extends:

| Issue | Disposition | Extends |
|---|---|---|
| Core abstraction | Keep AOI as a non-authorizing correlation profile: `authority_effect: none`, no verdict, no pin | [1.2](../s02/contracts/1.2-authority-and-separation.md) forbidden transitions F-02, F-07, F-09 |
| Coverage | Add a distinct Observability Coverage Manifest paired by profile with the Enforcement Coverage declaration; neither is a verdict | [1.7 section 3](../s03/minimum-profile-and-coverage.md) |
| Identity | Reuse the 18-identifier crosswalk; distinguish principal, agent identity, runtime instance, session, operation, decision, attempt, effect | [1.5](../s03/identity-and-lifecycle.md) SP-01 to SP-05 |
| ISS | Linkage optional, separately gated, owned by ISS; no ISS V6 R0 to R4 rescope | out of v0.2 scope by default |
| Signals | OTel projection optional for M1; source records first; export failure never erases custody | design only (AOI-4) |
| Human oversight | Keep the five intervention fields; qualify scope and effectiveness separately | [1.2](../s02/contracts/1.2-authority-and-separation.md) F-04 |
| Reasoning | Hidden reasoning and confidence signals excluded from mandatory evidence and authority tests | new constraint, below |
| Execution | AOI-0 to AOI-5 mapped into existing steps without opening an implementation sprint | section 4 |

## 3. Binding boundaries (restated from the addendum, checked against the existing contracts)

- **No second authority.** Control Plane owns grant and policy authority and canonical decision admission; the Execution Runtime owns effect-time revalidation and effect-boundary observations; the Orchestrator coordinates and emits source-bound observations but grants nothing and certifies nothing. This matches the exclusive-powers table in [1.2 section 2](../s02/contracts/1.2-authority-and-separation.md) except one wording point: the addendum gives effect-time revalidation to the Runtime, while the 1.2 table gives "effective authorization at effect time" to the Control Plane gate and "constrained execution under an authorized envelope" to the Runtime. This record keeps the 1.2 wording (the gate decides; the Runtime executes and records) and flags the difference for the M0 gate as a clarification, not a new power. AOI adds no power.
- **No common atomic transaction.** Replay, Evidence Pack, registry and attestation keep their own custody. No cross-store atomicity or instantaneous revocation guarantee is implied without proof.
- **Qualification stays independent.** Builder traces, spans, manifests and locally passing tests do not qualify themselves; expected cases, negatives and verdicts are Qualification's.
- **ISS keeps its own authority.** OCS may consume a separately accepted reference or projection and never creates or infers an ISS state transition.
- **OTel is informational.** A span, digest or signed event is not a certified decision, a valid grant, a reliable effect receipt or proof of semantic correctness. A digest establishes byte identity, not issuer authorization.
- **No hidden reasoning in mandatory tests.** Chain-of-thought and log-probability signals are not mandatory evidence and not inputs to any authority test.
- **Absence of telemetry is not evidence of absence of an effect or a violation.**

## 4. Mapping of AOI work items to the existing steps

No new step. Each AOI item is proposed as a clause on the steps the addendum names. Exits in [engineering-register.md](../engineering-register.md) remain as they are until the M0 gate decides; the proposed additions are recorded there as a separate table (r4-aoi) and in the JSON mirror under `aoi_addendum`.

| AOI item | Steps | Builder deliverable | Reviewer | State |
|---|---|---|---|---|
| AOI-0 | 1.2, 1.5 | Source-to-field and identity matrix | Source-backed review packet; no invented schema ownership | Drafted: [aoi-c01-envelope.md](aoi-c01-envelope.md) section 3 |
| AOI-1 | 1.2, 1.4 | AOI-C01 envelope and human-intervention record | Architecture owners; authority owner adopts changes separately | Drafted: [aoi-c01-envelope.md](aoi-c01-envelope.md) |
| AOI-2 | 1.7, 4.2 | Paired enforcement and observability coverage; M1 field applicability and claim restrictions | Security and architecture; Qualification specifies proof independently | Drafted: [aoi-c02-paired-coverage.md](aoi-c02-paired-coverage.md) |
| AOI-3 | 1.5, 3.5 | Authority, configuration and memory-transition provenance with effect and attempt distinctions; reconcile-only recovery | No new ISS or OCS memory authority; no blind retry | Contract text in C01 sections 5 to 6; memory-transition provenance deferred (section 5) |
| AOI-4 | 3.4, 4.4 | Informational OTel projection design: negative and outage behavior, security and privacy | No authorization-path effect or custody loss on exporter failure; implementation deferred pending M0 | Design constraints only: C01 section 7; no design beyond constraints in this pass |
| AOI-5 | 4.4, 4.5 | Qualification request mapping Q01 to Q07 | Qualification accepts, rejects or reshapes its own contract | Drafted: [qualification-request.md](qualification-request.md) |

## 5. Recommended minimum for v0.2 (proposed, not decided)

Following the addendum: the AOI envelope and paired coverage contracts; truthful identity, authority, effect and custody correlation on the one bounded customer-refund scenario already proposed for migration (ADR-P05); human intervention only where an approval-bearing path applies; no new memory service; no mandatory hidden reasoning; OTel as an export contract only unless separately approved.

Optional or deferred until separately demonstrated: multi-agent drift analytics, the OpenTelemetry implementation, the ISS bridge, enterprise-wide coverage, and memory-transition provenance (AOI-3 second half). These stay outside M1 and M2 totals.

Key feasibility reading (static): the correlation record can be assembled by the Orchestrator and the step 1.4 handoff as a joinable index that references existing records by identifier and commitment, so M1 does not by itself require a locked component to emit a new field. Fields with no source today (see C01 section 3) carry the state UNSUPPORTED rather than a fabricated value. A change that makes a locked component emit a new field is a separate F3 package, FP-05 in [../s02/f3-change-proposals.md](../s02/f3-change-proposals.md), contingent and unauthorized.

## 6. Additions to the M0 decision packet

The addendum lists eight mandatory M0 decisions. They are recorded as rows 13 to 20 of the [M0 decision packet](../s02/m0-decision-packet.md) and as rows in [operator-decisions.md](../operator-decisions.md), all PROPOSED:

| # | Addendum decision | Recommendation in this record |
|---|---|---|
| 13 | Exact compatibility profile for the envelope and canonical JSON | The step 1.3 profile (ADR-P01: JCS for new commitments); the envelope reuses it, defines no second one |
| 14 | Allowed identity references and proof-of-binding source | Reuse existing identifiers (1.5 crosswalk); agent attestation has no source in the four locked sources read, so `agent_identity_ref` carries an attestation state, default UNSUPPORTED |
| 15 | Required event classes and missing-field semantics | Event classes and the field-state vocabulary in C02; a missing required field is a typed outcome, never silent |
| 16 | Which approval-bearing and governance-state-changing paths apply to M1 | Only paths the one bounded refund scenario exercises; others NOT_APPLICABLE with predicate |
| 17 | Enforcement versus observation minimum across the five surfaces | Enforcement per ADR-P08 stays the gate; observation is reported separately and never raises a gate status |
| 18 | Integrity, custody and redaction boundaries | Custody stays with each existing store; redaction and retention are declared per field in C02; selective disclosure design is Q07 input |
| 19 | Which parts need locked-component F3 changes and renewed Qualification | FP-05 (contingent) names candidate carriers; none is needed for the recommended M1 minimum by static reading |
| 20 | Whether and when optional OTel and ISS linkage enter the qualified profile | Not in M1; contract-only for OTel; ISS only after an ISS-owned accepted export exists |

## 7. Exact source and profile (the M0 packet pin the addendum requires)

Pinned from the hub lock read in the earlier passes, not re-read in this pass: Control Plane `0a41faa9`, Execution Runtime `ec728da6`, ODES `e86a25a1`, Orchestrator `a745e131`, hub `main` at `26424c16` (merge of #199), plus the unmerged #201 head `999bd074`. The adopted Engineering Constitution revision is not pinned here: no exact revision has been adopted (see [../README.md](../README.md)), and the addendum requires the actual adopted revision to be pinned in the M0 packet; that stays open until the operator records it.

## 8. Not read, not claimed

- The primary external source cited by the addendum, "The Observability Gap in AI Agents" (Partnership on AI, September 2026), was not read in this pass. No claim here depends on it, and the addendum itself notes that it analyzes four agent frameworks and does not qualify Cognous.
- The earlier attached addendum file named in the addendum's provenance section (`Cognous_Agent_Observability_Engineering_Addendum.docx`) was not supplied; only the builder revision was. The reconciliation in section 2 follows the issues as that revision states them.
- Trace and span identifiers, observer clock provenance and agent attestation were not searched for in the locked sources in this pass (see C01 section 3, state REQUIRES INVESTIGATION).

## 9. Stop-condition check (addendum section 9)

| Stop condition | Result |
|---|---|
| Conflict with accepted source authority | None found; the addendum restates the existing exclusive powers |
| Non-reconcilable identifier semantics | None; open items are marked (for example `correlation_id` and `run_id` commitment status, [1.5](../s03/identity-and-lifecycle.md)) |
| Mandatory observation inaccessible in M1 | Trace and span references, observer clock provenance and agent attestation have no verified source; proposed as optional or typed-absent in M1 rather than mandatory |
| Unowned new pin carrier | The AOI profile digest needs a carrier; proposed to reuse the hub-owned registry artifact and the single opt-in context member of FP-04. Not yet owned; flagged as an operator decision (row 13) |
| Cross-store atomicity claim | None made |
| Locked-component implementation need | None for the recommended minimum by static reading; FP-05 records the contingent case |

## 10. Estimates

A separately labeled additive delta is in [estimate-delta.md](estimate-delta.md). It is not included in the M0, M1 and M2 totals of [../s02/estimates-m0-m1-m2.md](../s02/estimates-m0-m1-m2.md) until the operator decides row 16 of the packet, because the delta depends on how many approval-bearing paths the M1 profile contains.
