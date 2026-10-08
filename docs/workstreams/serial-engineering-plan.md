# Remaining engineering register work and serial estimates

Prepared for André de Lima and Cognous maintainers. Review date: 8 October 2026 UTC. Baseline: hub main `61010c69a8d836d63bd85727f8c4aa9542e98d95`. This is a planning estimate, not a runtime change or a completion claim.

## Serial decision and estimate basis

Implement the native Microsoft-derived OG01–OG05 and OpenAPPA-derived PI01–PI12 changes first. The Microsoft and OpenAPPA interoperability adapters follow serially, owned by the other worker. Hub PR #44 is an open documentation/contract proposal; this plan does not merge it or start its implementation. Existing accepted repairs and evidence remain accepted.

Estimates are focused engineer-days of eight hours with AI assistance, including targeted source inspection, implementation, tests, documentation and one review cycle. They estimate the next bounded reference/staging increment, not full enterprise closure. They are judgment ranges, not measured throughput or promises about the duration of a Codex session. Confidence is low to moderate until the first implementation batches establish actual velocity.

One existing local profile, one staging environment and one named destination/identity backend are assumed. CI queue delays, customer approvals, unavailable IAM/destination access, independent review, field observation periods and production rollout are additional elapsed time. Additional destinations, hostile-host guarantees, distributed atomicity or multiple tenants require separate estimates. No legislative mapping is included.

Each identifier is preserved for traceability. Overlap means reuse the same implementation and charge it once; row estimates must not be summed. Completed bounded checks do not close broader requirements. The current extension contract covers 91 profile cases and 26 gate cases; it does not establish these future acceptance cases. Historical register dispositions are reconciled with later profile updates here rather than treated as evidence that already-built foundations are missing.

## First native phase

Planning envelope: approximately 30–50 focused engineer-days, or 6–10 working weeks for one serial engineer, for the combined bounded native phase. This discounted envelope reflects shared capability, policy version, flow, review, replay and incident infrastructure across OG/PI requirements; it is not the sum of all rows. Production completion remains dependent on real institutional/IAM/destination/operations evidence. Re-estimate after the capability and flow batches.

Use four consecutive batches: capability/plugin/policy contracts; protected flow/result/child/recovery paths; friction/proposal/replay/adoption/permission-delta lifecycle; operational quotas/telemetry/incidents/post-deployment review. Complete and qualify each batch before the next. Passing replay or an accepted proposal never grants an action permission. Remote effect ordering and authenticated ownership remain explicit deployment boundaries.

## Full item inventory

The tables include every canonical requirement row, every October 8 intake group, all twelve PI additions, and release/adapter follow-up. Original CR locators are listed separately: they are historical component-review topics, not twenty-one additional rebuild projects. E3 is superseded and INT-01 is complete. Verification-first estimates cover investigation only; any confirmed repair is estimated after reproduction.

## Native Microsoft and OpenAPPA changes

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| OG01 | Real inventory adapters, controlled admission/retirement and persistent tombstones | Partial | 3–5 | AGC01/03/05 |
| OG02 | Approved exact artifact binding, replacement/withdrawal and loading checks | Open | 2–4 | AGC02/07; PI01 |
| OG03 | Supported semantic subset, reproducible resolution and activation generations | Open | 2–4 | PI08/09; ER04 |
| OG04 | Durable quota reservations, circuit state and bounded recovery probes | Open | 3–5 | RS05; SH02 |
| OG05 | Correlated delivery, acknowledgement, containment and closure records | Open | 2–4 | AGC09; RS09/10 |
| PI01 | Versioned capability contract and fail-closed protected-profile loading | Open | 1–2 | OG02/03; SH04 |
| PI02 | Persistent flow state, exact sink contracts and conjunction with current authority | Partial | 3–5 | IF01–03/06/07; MG/GC |
| PI03 | Decision-bound remedies with expiry, scope and single-use handling | Open | 2–4 | IF04; F1/2 |
| PI04 | Inherited restrictions, fixed return contract and enforced admission boundary | Open | 3–6 | IF05; RS06 |
| PI05 | Idempotent minimized reports with exact references and no authority effect | Open | 1–2 | F1; AGC04 |
| PI06 | Typed diagnoses, exact diffs, falsifiers, risk, tests and rollback proposals | Open | 1–2 | DA; ES05 |
| PI07 | Pinned policy-change fixtures, utility/protection cases and CI gate | Open | 2–4 | ES/RS01/11/12 |
| PI08 | Competent decision, immutable revisions, transition rules and deployment receipts | Partial | 3–5 | OG03; DA/AGC08 |
| PI09 | Formal protected-parent constraints, conflict handling and delegated choice | Open | 2–4 | ER02; OG03 |
| PI10 | Low-cardinality metrics, privacy controls and enforcement-independent collector | Open | 1–2 | AGC04; RS11 |
| PI11 | New allows/denials, unresolved paths and coverage deltas over exact corpus | Open | 2–3 | PI07; ES01/04 |
| PI12 | Baseline comparisons, explicit trigger records and authorized rollback/suspension | Open | 2–4 | OG05; DA/RS09/AGC09 |

## Execution release and redemption

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| ER01 | Bind canonical final arguments and adapter implementation to live authorization | Partial | 2–3 | PI02; E6 |
| ER02 | Integrate protected institutional constraints without weaker operational overrides | Partial | 1–2 | PI09 |
| ER03 | Connect commitment verification and required obligations to selected runtime path | Partial | 2–3 | PI02/03 |
| ER04 | Define and test invalidation for every changed committed input | Partial | 1–2 | OG03; PI08 |
| ER05 | Version verification levels and explicit reevaluation/reconstruction boundaries | Partial | 1–2 | ES04 |
| ER06 | Qualify one additional real effect boundary; local atomic foundation already exists | Partial | 3–6 | AGC06; RA-03 |
| ER07 | Design and test combined intent/authority lifecycle without database-profile collision | Partial | 3–5 | E1/A-E1 |
| ER08 | Carry new release/claim/effect fields through versioned consumers | Partial | 2–4 | IF08; GC 6 and 7 |

## Evidence and deployment assurance

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| ES01 | Extend exact evidence contracts to remaining supported claims | Partial | 1–2 | PI07/11; E8 |
| ES02 | Add applicable claim-group completeness, exclusions and fault accounting | Partial | 0.5–1 | PI07 |
| ES03 | Retain recurrence and falsifier lineage without stronger proof labels | Open | 1–2 | F4; E8 |
| ES04 | Bind resolver/input versions and derivation verification beyond record consistency | Partial | 1–2 | ER05; PI11 |
| ES05 | Bind release recommendation to competent acceptance without execution authority | Partial | 1–2 | PI08; DA |
| RS01 | Complete per-check stimulus, disclosure and task-outcome fields | Partial | 1–2 | ES02; PI07 |
| RS02 | Qualify one named environment and configuration beyond structural packet intake | Partial | 2–4 | SH04; AGC |
| RS03 | Retain protected argument provenance and transformation lineage | Open | 2–3 | SH01; IF/GC |
| RS04 | Bind recipient reliance and changed dependencies to current commitments | Partial | 2–3 | IF03/07; ER04 |
| RS05 | Add durable step/delegation and cumulative exposure bounds | Open | 2–4 | OG04; TCR-4 |
| RS06 | Bind delegated authority and restrictions to receiving environment | Partial | 3–5 | PI04; RA-02 |
| RS07 | Define visibility, finality and typed absence for a named destination | Partial | 2–3 | E5/A-E5; F3 |
| RS08 | Reconcile complete declared destination population with freshness/coverage | Partial | 2–4 | AGC04; RS07 |
| RS09 | Execute containment/correction/cessation and authorized restart in staging | Partial | 3–6 | OG05; AGC05/09/10 |
| RS10 | Govern consequential publication/remedy as separate effects | Partial | 2–4 | TCR-7; OG05 |
| RS11 | Build task completion and full human-effort measures with baseline cases | Partial | 2–3 | PI07/10/12 |
| RS12 | Extend scoped release claims to all newly selected profiles and environments | Partial | 0.5–1 | ES01; PI07 |

## Information flow context and memory

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| IF01 | Add full sink, recipient, parameter and integrity contracts | Partial | 1–2 | PI02 |
| IF02 | Extend persistent obligations through compaction, restart and derived state | Partial | 2–3 | PI02; MG/GC |
| IF03 | Integrate protected dispatch/result/context gates with current action authority | Partial | 2–4 | PI02/04 |
| IF04 | Implement bounded typed remedies without implicit permission | Open | 2–4 | PI03 |
| IF05 | Qualify real child isolation and controlled return admission | Open | 3–6 | PI04 |
| IF06 | Qualify restriction-preserving reuse across sessions and memory transforms | Partial | 1–2 | PI02; MG01/02 |
| IF07 | Bind current flow state independently from retained historical evidence | Partial | 1–2 | PI02; ER04 |
| IF08 | Export denials, unresolved restrictions and admission lineage through consumers | Partial | 2–3 | ER08; GC 6 and 7 |
| MG01 | Integrate admission receipts with protected deployment/default path | Partial | 1–2 | PI02; IF03 |
| MG02 | Integrate recall/delivery receipts with current permitted reliance and recovery | Partial | 1–2 | PI02; GC 5 |
| MG03 | Implement configured receiving-context restrictions; legislative mapping deferred | Partial | 1–2 | IF01/06 |
| MG04 | Qualify authenticated evidence custody, access and deletion boundaries | Partial | 3–5 | AGC04; F5 |
| GC 3 and 4 | Integrate separate access/admission/delivery/reliance/retention records | Partial | 1–2 | PI02/04; MG |
| GC 5 | Extend exact context-generation binding beyond the existing refund wrapper | Partial | 1–2 | ER01; PI02 |
| GC 6 and 7 | Version context lineage export through Replay/Evidence Pack/ODES | Partial | 2–3 | ER08; IF08 |
| GC 8 to 10 | Run the remaining protected-context scenarios at selected revisions | Partial | 2–4 | PI02/04/07 |

## Temporal authority and institutional review

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| TCR-1 | Generalize no implicit authority inheritance beyond two-step fixture | Partial | 1–2 | RS06; PI04 |
| TCR-2 | Qualify historical-effect preservation across longer trajectories and recovery | Partial | 0.5–1 | ER07; RS09 |
| TCR-3 | Apply current authority at additional consequential transitions | Partial | 2–3 | ER06; RA-02 |
| TCR-4 | Add durable continuation/dispatch/delegation contracts and coordinator state | Partial | 2–4 | RS05 |
| TCR-5 | Qualify future-work stop bounds for real queued/in-flight work | Partial | 2–3 | AGC10 |
| TCR-6 | Implement requested/acknowledged/observed/verified cancellation states | Partial | 3–5 | AGC10 |
| TCR-7 | Execute separately authorized compensation/replacement/reversal | Partial | 2–4 | RS09/10 |
| TCR-8 | Extend tests that observation never authorizes continuation or retry | Partial | 0.5–1 | RS07; F2/3 |
| DA R1 | Connect institutional proposals to grant lifecycle without automatic expansion | Partial | 1–2 | PI06/08 |
| DA R2 | Bind contraction to explicit competent decisions or previously adopted rules | Partial | 1–2 | PI08/12 |
| DA R3 | Carry separate competence/authority/boundary assessments into live workflow | Partial | 0.5–1 | PI06; AGC08 |
| DA R4 | Connect critical incidents to mandatory review triggers | Partial | 1–2 | OG05; PI12 |
| DA R5 | Integrate explicit restoration decision and fresh runtime grant issuance | Partial | 1–2 | AGC08/10 |
| DA R6 | Integrate retained dissent/incident/revision history through consumers | Partial | 1–2 | ER08; PI08 |
| DA R7 | Bind assessments to exact operational envelope/evaluator/criteria/period | Partial | 1–2 | RS02; AGC08 |
| DA R8 | Qualify non-authorizing observations throughout adoption/grant integration | Partial | 0.5–1 | PI05–08/12 |

## Historical feedback and verification

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| E1 | Qualify stable business intent across replanning and configuration/grant changes | Open | 1–2 | A-E1; ER07 |
| E2 | Revalidate current durable refusal recording before any repair | Verify first | 0.5–1 | A-E2; F1 |
| E3 | Superseded freshness remedy; use local atomic ordering or explicit remote limits | Superseded | 0 | ER06; RA-03 |
| E4 | Verify trusted post-lock time semantics at other selected entry points | Open | 0.5–1 | ER06; AGC06 |
| E5 | Establish actual destination observation/absence contract | Open | 2–3 | A-E5; RS07 |
| E6 | Revalidate live adapter implementation binding before any repair | Verify first | 0.5–1 | ER01; OG02 |
| E7 | Design governed partition reconciliation only if multi-store deployment selected | Open | 3–6 | RA-03; ER07 |
| E8 | Integrate narrow assurance claims and falsifier provenance | Open | 1–2 | ES01/03; F4 |
| D1 | Refresh public documentation after each accepted profile change | Open | 0.5–1 | CR20/21; RS12 |

## Operational completion controls

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| AGC01 | Authenticate owners, accepted responsibility, transfers and actual intervention | Partial | 2–3 | OG01; SH03 |
| AGC02 | Qualify IAM/action/destination scope and prevent alternate-route bypass | Partial | 3–5 | OG02/03; ER06 |
| AGC03 | Extend inventory with purpose/tasks/connections/data flows and real discovery | Partial | 2–4 | OG01; SH04; PI02 |
| AGC04 | Integrate production execution/outcome joins, visibility and useful metrics | Partial | 2–4 | ER08; ES/RS; PI10 |
| AGC05 | Implement retirement workflow and verify withdrawal/cessation/tombstones | Partial | 3–5 | OG01; AGC07/10 |
| AGC06 | Qualify current authorization at named deployed effect boundaries | Partial | 3–6 | ER06; RA-02/03 |
| AGC07 | Integrate workload IAM/secret manager and test rotation/revocation/caching | Partial | 3–5 | OG02; RA-03 |
| AGC08 | Integrate competent authenticated reviewers, capacity and grant lifecycle | Partial | 2–4 | SH02/03; DA; PI08 |
| AGC09 | Qualify live incident delivery, containment and evidenced closure | Partial | 2–4 | OG05; RS09/10 |
| AGC10 | Qualify shutdown population, queues, replicas, late effects and restart | Partial | 3–6 | TCR-5/6/7; RS09 |

## Handoffs resolver and feedback addenda

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| SH01 | Durable clarification and actual dispatch binding beyond standalone checker | Partial | 2–3 | PI02/03; RS03 |
| SH02 | Atomic review-capacity admission, deadline-safe fallback and restart | Open | 2–4 | OG04; AGC08 |
| SH03 | Verify owner visibility, intervention lever and competent authority | Open | 1–2 | AGC01/09/10 |
| SH04 | Version deployment capability/obligation profiles and drift invalidation | Open | 1–2 | PI01; RS02 |
| RA-01 | Durable authenticated source trust/high-water storage beyond synthetic observations | Partial | 2–3 | RA-03; PI08 |
| RA-02 | Integrate source resolution with grant/policy/approval/ancestor validity at effect | Open | 3–5 | ER06; AGC06/08 |
| RA-03 | Qualify one real authority source, rotation/compromise and destination race | Deployment | 4–8 | AGC07; ER06 |
| A-E1 | Test stable purpose key across config/grant changes and lost acknowledgement | Partial | 1–2 | E1; ER07 |
| A-E2 | Revalidate both current refusal paths with protected input/version references | Verify first | 0.5–1 | E2; F1 |
| A-E5 | Declare and test dedupe/deadline/authoritative-read/hold-only retry mode | Verify first | 2–3 | E5; RS07 |
| F1 | Revalidate hold-input history and causal reconsideration conditions | Verify first | 0.5–1 | E2/A-E2; PI03/05 |
| F2 | Implement bounded reread schedule and one named escalation without new effect | Open | 1–2 | PI03; RS07 |
| F3 | Integrate typed observation coverage/consistency and rendered recovery choices | Open | 2–3 | RS07; F2 |
| F4 | Integrate existing dependency-lineage grouping into Evidence Pack consumers | Partial | 1–2 | ES03; E8 |
| F5 | Bind refusal order to earlier criteria using authenticated external anchor | Open | 3–5 | MG04; CR01/02 |

## Release and adapter follow-up

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| INT-01 | PR #42 is merged; no remaining implementation for this integration batch | Complete | 0 |  |
| EXEC-29 | Inspect exact final head/checks, fix only reviewed blockers, qualify applicable merge interaction | Pending acceptance | 0.5–2 | Separate executor work; no automatic hub-pin advance |
| EXEC-30 | Inspect exact final head/checks, fix only reviewed blockers, qualify applicable merge interaction | Pending acceptance | 0.25–1 | Separate executor work; no automatic hub-pin advance |
| EXEC-31 | Inspect exact final head/checks, fix only reviewed blockers, qualify applicable merge interaction | Pending acceptance | 0.25–1 | Separate executor work; no automatic hub-pin advance |
| OA01–OA10 | Delegated optional compatibility work after native interfaces stabilize | Deferred | 3–6 | Other worker; PR #44 is a proposal |
| MSFT adapter | Delegated compatibility/translation work after native interfaces stabilize | Deferred | 3–6 | Other worker; separate specification |

## Original component review locators

| ID | Remaining scoped work | Status | Engineer-days | Reuse or boundary |
| --- | --- | --- | --- | --- |
| CR01 | Evidence Attestation is selected in B1; signature-only scope remains. Full original recommendations need component review. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR02 | Evidence Registry is selected in B1; local chain scope is not fleet consensus or factual truth. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR03 | Institutional Governance remains the authority-semantics owner; repository acceptance is not institutional ratification. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR04 | Manifest 1.1 is selected. ER01 and IF01 define additional profile proposals. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR05 | Selected persistence baseline and merged optional profiles differ; use B1–B3. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR06 | Execution Runtime selected baseline differs from merged refund-intent and authority/effect profiles; use B1, B3 and B5. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR07 | Selected reconstruction is not policy reevaluation, independent verification or full new-profile export. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR08 | Selected transformations exist; ES and RS add proposed claim contracts. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR09 | Selected implementation profile is in B1. New mappings require explicit compatibility review, not silent schema drift. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR10 | Governed Exchange carries the selected local transport path. Distributed lineage merge remains deferred. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR11 | Optional behavioral package. Separate client and PRP work are outside this reconciliation; no current-version claim is refreshed. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR12 | Optional research workflow, not a truth or authority source. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR13 | Optional behavioral guidance, not runtime enforcement. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR14 | Conceptual scope guidance; no implementation or validation claim established here. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR15 | Private mechanisms remain outside public contract publication and this audit. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR16 | Practice offering; no runtime dependency is introduced. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR17 | Navigation and archival disposition require project review; no runtime dependency. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR18 | Navigation and archival disposition require project review; no institutional adoption implied. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR19 | Conceptual organization; no new mandatory runtime component. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR20 | Public claims and navigation require alignment with accepted evidence; no deployment claim inferred. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |
| CR21 | Original baseline B1 is historical; the implementation update above records later adoption and optional execution. | Review/optional | 0.5–1 review only | Historical locator; feature scope must be revalidated |

## Completion and source boundaries

For native work, the definition of done is a reviewed implementation at exact component revisions, applicable positive/negative tests, versioned public contracts, migration notes and a register update identifying remaining deployment limits. Real identity, custody, source authenticity, intervention, remote observation and institutional competence are not supplied by a synthetic fixture.

The individual estimate ranges are for remaining scoped increments. Original CR estimates cover a component review and disposition only; optional behavioral, conceptual, private and practice projects require their own separately selected scope before feature estimates. Private mechanisms are not part of this public platform work. The superseded E3 remedy is not scheduled. No reliable whole-program completion date can be derived until overlaps and the chosen production deployment are resolved.

Sources: canonical engineering register and linked accepted profile contracts at the baseline above; October 8 intake register; current executor PR metadata; the supplied consolidated recommendations; and Cognous Engineering Addendum OpenAPPA Derived Improvements, read in full on 8 October 2026. PI identifiers are addendum intake, not previously implemented register closure. These estimates import no OpenAPPA dependency or Microsoft adapter.
