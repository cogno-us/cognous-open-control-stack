# Cognous consolidated engineering register

Review date: 7 October 2026. Prepared for André de Lima and Cognous maintainers. Status: documentation proposal, not adoption of the source requirements.

The completed repair batch remains complete. This register consolidates the October 5 recommendations and nine October 7 addenda into five workstreams. It replaces overlapping planning instructions for this review, while preserving the original documents and their requirement identifiers. Only a named profile with matching implementation and qualification evidence can be described as supported.

## Implementation update after initial reconciliation

The evidence entries B1–B7 below preserve the original review baseline. Subsequent accepted work qualified and adopted the merged consumer chain in hub PRs #23 and #24; default adoption merged at `14696c231e00433161396cfa3093e3e007372fc1`. Hub PR #25 then added explicit optional synthetic execution commands, merged at `e78c0f5766b0e3cd493c59bed488e98a4cd36513` after all 17 final-head checks passed. Its dedicated Linux run `37698280880` passed both profiles. See [current release status](release-status.md) and [optional profiles](optional-execution-profiles.md). Source selection, ordinary execution and optional-profile activation remain distinct.

The next bounded implementation adds [optional record consistency](optional-evidence-contract.md), covering parts of ES01, ES02, ES04, RS08 and RS12. Its local tests include missing artifacts, failed cases, pin mismatch, unexpected effects, changed retained operations and false producer flags. CI acceptance is recorded in its PR. Broader evidence contracts, environment assurance, useful task completion and human effort remain open; no general requirement is closed by this narrow verifier.

## Evidence and scope

This is a document reconciliation with targeted GitHub verification, not a repository-wide implementation audit or a new test run. Proposed and deployment-dependent mean adoption or coverage is not established here; they do not assert that no equivalent code exists. Needs verification is used for historical defect allegations that require fresh source inspection. Partly covered never closes the complete requirement. Source papers were not independently reread or verified in this pass. Their assertions remain attributed to the supplied addenda.

B1 — Hub main `643a1425060a4e50567e0d7789ae1652194ad00c`. Its component lock selects Control Plane `248d899634d9db3518e831bc7ab568a48733f825` and Execution Runtime `177354e959cc78c59c1a776f018cfbfbf28c927b`. [Selected lock](https://github.com/cogno-us/cognous-open-control-stack/blob/643a1425060a4e50567e0d7789ae1652194ad00c/component-lock.json).

B2 — [Control Plane PR 11](https://github.com/cogno-us/cognous-control-plane/pull/11), merged `29337fe900d3b2da5656c77d56d70f18feb190b8`. Decision Input Commitment remains a non-authorizing sidecar. Its PR records 25 focused passing tests; this review did not rerun them.

B3 — [Control Plane PR 12](https://github.com/cogno-us/cognous-control-plane/pull/12), merged `d3dadee70bd319812b207389ab1e0f6efe511916`, and [Execution Runtime PR 25](https://github.com/cogno-us/cognous-execution-runtime/pull/25), merged `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac`. The profile requires cooperating authority writers, a trusted same-host handoff and one authoritative SQLite store.

B4 — [Hub qualification run 37682165860](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860) is verified successful at `e926bbd70126ae9664bb4189bfe12eec4c18336b`. It exercises reviewed source revisions Control Plane `73e3c65acc47dc43593dcb0420d14032ed410b14` and executor `b1525a7982e52ebb530457f94d5517de032ca4c4`. The fetched job log records 7 Control Plane, 4 compatibility, 24 executor and 19 integration tests in each of two repetitions: 73 passed. This is not a rerun at the eventual upstream merge SHAs.

B5 — [Execution Runtime PR 14](https://github.com/cogno-us/cognous-execution-runtime/pull/14), merged `89eca565a4f3a6a12e18fa9811c43f75a965dff7`, supplies refund-intent ownership. Refund-intent and authority/effect profiles remain mutually exclusive per database; no combined guarantee is adopted.

B6 — [Worker 22 checkpoint](https://github.com/cogno-us/cognous-open-control-stack/blob/643a1425060a4e50567e0d7789ae1652194ad00c/docs/workstreams/paired-request-enforcement-checkpoint.md) preserves paired request observations against the older selected pins. Twelve cases were scheduled and eleven evaluable; malformed input is not an enforcement success. Disclosure and final task completion are unmeasured in that profile.

B7 — [Hub PR 14](https://github.com/cogno-us/cognous-open-control-stack/pull/14), Worker 19 race characterization, remains open at review time. Its evidence can inform this register without describing the PR as merged. Its disposition is separate from executor PR 14.

## Consolidated sequence

1. Close documentation drift. Keep one register, refresh the hub README and append current acceptance evidence to the Worker 21 checkpoint. Preserve old results as history.
2. Decide default profile adoption. If desired, qualify exact accepted merge revisions in bounded batches, including consumer compatibility, before changing component-lock.json. Existing separate profiles do not imply a combined refund-intent and atomic-authority contract.
3. Consolidate evaluation records. Combine ES01–ES05 with RS01, RS02, RS07, RS08, RS11 and RS12 around existing qualification evidence. Add only uncovered claim and completeness fields.
4. Select one deployment-driven extension. For protected information use, combine IF, GC and MG. For multi-step workflows, begin with the two-step TCR refund/notification scenario. Do not start both merely because each source labels its work P0.
5. Develop institutional autonomy records after the evidence vocabulary is stable. No runtime maturity scoring or automatic authority expansion.

Priorities in each source are local recommendations, not a global release gate. Steps 3–5 are proposed backlog, not prerequisites for describing the completed bounded reference accurately.

## Shared implementation rules

Keep one authority path and reuse existing identity namespaces. Preserve current producer compatibility through explicit versioned adapters. Record source and resulting revisions, tested operating system, selected profile and remaining limitations. Run small deterministic component batches first, then the affected integration cases. Separate OS jobs where OS behavior is relevant; do not launch unrelated TypeScript or mobile suites for documentation changes. Required missing cases block only the claims they support and remain visible.

Requirements touching refusals, context or memory must use purpose-limited retention and protected references. Evidence completeness does not justify indiscriminate payload logging. Delivery records establish observable presentation, not hidden cognition. Research comparisons and partner discussions supply proposals, not transferred assurance.

## Execution release and redemption

| Source ID and requirement | Disposition and owner | Evidence and next action |
|---|---|---|
| ER01 — Bind the final action | Partly covered; Manifest and Control Plane | B1, B2: operation binding and standalone input commitments exist. Map the complete requested candidate and adapter commitments to live authorization before adopting the exact-action profile. |
| ER02 — Preserve intent constraints and policy hierarchy | Partly covered; Institutional Governance and Control Plane | B2: sidecar includes institutional requirements; runtime adoption is separate. Keep institutional obligations separately committed; review runtime adoption without permitting operational policy to weaken them. |
| ER03 — Bind obligations and evidence resolution | Partly covered; Control Plane | B2: non-authorizing commitment verifier. Reuse the sidecar classifier and negative vectors; require an explicit runtime integration decision. |
| ER04 — Define exact reuse and invalidation | Partly covered; Control Plane | B2 and B3: scoped input and authority binding. Specify which profile requires fresh evaluation for every changed committed input; do not infer grandfathering from stricter policy. |
| ER05 — Separate derivation verification from replay | Partly covered; Control Plane and Replay | B2 verifies its declared profile; B1 reconstruction is narrower. Define verification levels; keep external truth and policy reevaluation outside reconstruction claims. |
| ER06 — Enforce the protected commitment boundary | Partly covered; Execution Runtime and hub | B3 and B4: trusted handoff and authoritative SQLite ordering. Retain the merged same-host profile; qualify accepted merge revisions before default pin adoption. Remote destinations need their own mechanism. |
| ER07 — Preserve lifecycle and recovery semantics | Partly covered; Execution Runtime and Control Plane | B3 and B5: merged profiles, not a combined contract. Preserve consumed claims and historical effects; keep refund-intent and authority/effect profiles mutually exclusive until composition is designed. |
| ER08 — Export full release and effect lineage | Partly covered; Replay and Evidence Pack | B1 supports the selected older evidence chain. Map new release and commitment fields through versioned consumers; do not silently extend existing producer schemas. |

## Evaluation and deployment evidence

| Source ID and requirement | Disposition and owner | Evidence and next action |
|---|---|---|
| ES01 — Define evidence contracts for claims | Proposed; Qualification and Evidence Pack | Source proposal; not established as implemented. Version predicates, mappings, eligibility and sufficiency; do not trust producer witness flags. |
| ES02 — Account for faults and missing coverage | Partly covered; Hub | B1 and B6 provide bounded reporting foundations; broader source requirement remains unqualified. Extend existing scheduled and evaluable counts to required claim groups, faults and exclusions. |
| ES03 — Bound recurrence and proof labels | Proposed; Evidence Pack | Source proposal; not established as implemented. Keep occurrences visible; require an explicit justified bridge before promoting proxies into stronger claims. |
| ES04 — Make evaluation records derivable | Partly covered; Replay and qualification | B1 and B6 provide bounded reporting foundations; broader source requirement remains unqualified. Bind input packages, resolver versions and verification levels; distinguish hash checking from reevaluation. |
| ES05 — Govern release recommendations | Proposed; Institutional Governance | Source proposal; not established as implemented. A recommendation may support an adopted release decision; it cannot authorize execution. |
| RS01 — Record what each check exercised | Partly covered; Hub | B1 and B6 provide bounded reporting foundations; broader source requirement remains unqualified. Reuse Worker 22 fields; extend only missing stimulus, disclosure and completion evidence for supported profiles. |
| RS02 — Bind qualifications to environments | Partly covered; Hub and deployment owner | B1 and B6 provide bounded reporting foundations; broader source requirement remains unqualified. Retain exact versions and environment scope; require requalification when relevant deployment conditions change. |
| RS03 — Preserve argument justification | Proposed; Manifest and Control Plane | Source proposal; not established as implemented. Bind consequential argument provenance and transformation lineage, with access controls for retained evidence. |
| RS04 — Govern recipient reliance and changes | Partly covered; Control Plane and recipient | B1 and B6 provide bounded reporting foundations; broader source requirement remains unqualified. Keep reliance decisions and dependencies explicit; preserve exact-input invalidation where selected. |
| RS05 — Enforce finite workflow restrictions | Proposed; Control Plane | Source proposal; not established as implemented. Define bounds on steps, delegation and cumulative exposure before enabling composition. |
| RS06 — Bind delegation to receiving environment | Deployment-dependent; Institutional Governance and executor | Source proposal; not established as implemented. Require a named receiving environment and bounded authority; do not inherit parent permission implicitly. |
| RS07 — Separate observation from impact | Partly covered; Observer and Evidence Pack | B1 and B6 provide bounded reporting foundations; broader source requirement remains unqualified. Add visibility and typed-absence contracts before claiming that missing events establish no impact. |
| RS08 — Reconcile destination populations | Partly covered; Destination adapter | B1 and B6 provide bounded reporting foundations; broader source requirement remains unqualified. Go beyond one effect lookup only where needed; define expected population, coverage, freshness and unexplained effects. |
| RS09 — Complete correction and containment | Deployment-dependent; Operational owner | Source proposal; not established as implemented. Define correction, deletion, exceptions, cessation and competent restart evidence for the deployment. |
| RS10 — Govern publication and remedy | Deployment-dependent; Institutional Governance and adapter | Source proposal; not established as implemented. Treat consequential publication and corrective actions as separately governed effects. |
| RS11 — Measure useful outcomes and effort | Proposed; Qualification and product owner | Source proposal; not established as implemented. Measure accepted task completion and full effort separately from denied unsafe requests. |
| RS12 — Publish applicable assurance only | Partly covered; Hub and Evidence Pack | B1 and B6 provide bounded reporting foundations; broader source requirement remains unqualified. Bind every assurance claim to selected profile, environment and evidence; never promote component merges automatically. |

## Information flow context and memory

| Source ID and requirement | Disposition and owner | Evidence and next action |
|---|---|---|
| IF01 — Complete sink and parameter contracts | Deployment-dependent; Manifest | Source proposal; enable only for a named protected flow or governed-memory deployment. Declare readers, recipients, argument flows and integrity semantics for canonical adapter values. |
| IF02 — Persist restrictions beyond transcripts | Deployment-dependent; Control Plane and context adapter | Source proposal; enable only for a named protected flow or governed-memory deployment. Keep restrictions in durable governed state; compaction and summarization must preserve obligations. |
| IF03 — Gate dispatch and context admission | Deployment-dependent; Control Plane and executor | Source proposal; enable only for a named protected flow or governed-memory deployment. Require both flow permission and current action authority; neither substitutes for the other. |
| IF04 — Provide governed recovery from blocks | Deployment-dependent; Control Plane | Source proposal; enable only for a named protected flow or governed-memory deployment. Return bounded recovery options with competent authorization for any release or relaxation. |
| IF05 — Isolate child context | Deployment-dependent; Context adapter and executor | Source proposal; enable only for a named protected flow or governed-memory deployment. Inherit restrictions, constrain returns and preserve effects after abandonment. |
| IF06 — Preserve restrictions through reuse | Deployment-dependent; Memory adapter | Source proposal; enable only for a named protected flow or governed-memory deployment. Keep purpose, retention, transformations and current-use checks across sessions. |
| IF07 — Separate history from current permission | Partly covered; Control Plane | B3 addresses local authority continuity; information-flow adoption remains proposed. Reuse Worker 21 only within its local profile; do not claim remote atomicity from a fresh check. |
| IF08 — Export flow decisions accurately | Deployment-dependent; Replay and Evidence Pack | Source proposal; enable only for a named protected flow or governed-memory deployment. Carry denials and unresolved restrictions without inflating assurance. |
| MG01 — Govern durable admission | Deployment-dependent; Memory adapter | Source proposal; enable only for a named protected flow or governed-memory deployment. Publish admitted content only after matching receipt and version are durably committed. |
| MG02 — Record recall before reliance | Deployment-dependent; Memory adapter and executor | Source proposal; enable only for a named protected flow or governed-memory deployment. Persist disclosure intent before delivery and retain delivery outcome or uncertainty; bind receipts to decision context. |
| MG03 — Bind jurisdictional reliance rules | Deployment-dependent; Institutional policy owner | Source proposal; enable only for a named protected flow or governed-memory deployment. Resolve item and receiving-context restrictions for each use; metadata alone does not establish compliance. |
| MG04 — Separate evidence custody | Deployment-dependent; Evidence custodian | Source proposal; enable only for a named protected flow or governed-memory deployment. Declare custody independence, continuity and deletion boundaries; no universal tamper-proof claim. |
| GC 3 and 4 — Separate context permissions and records | Deployment-dependent; Context adapter, Control Plane and hub | Source proposal; implementation coverage not established in this review. Keep access, admission, delivered context, permitted reliance and retention separate; reuse shared artifact identities. |
| GC 5 — Bind decisions to context generations | Deployment-dependent; Context adapter, Control Plane and hub | Source proposal; implementation coverage not established in this review. Require current commitments when policy demands them; a receipt cannot prove hidden model influence. |
| GC 6 and 7 — Carry context lineage through consumers | Deployment-dependent; Context adapter, Control Plane and hub | Source proposal; implementation coverage not established in this review. Extend versioned public interfaces without exposing private AoM or ISS mechanisms. |
| GC 8 to 10 — Qualify governed context | Deployment-dependent; Context adapter, Control Plane and hub | Source proposal; implementation coverage not established in this review. Use the proposed synthetic prohibited-context matrix before claiming selected enforcement. |

## Temporal authority and developmental autonomy

| Source ID and requirement | Disposition and owner | Evidence and next action |
|---|---|---|
| TCR-1 — No implicit authority inheritance | Proposed; Institutional Governance, Control Plane and hub | B1 and B3 establish single-effect foundations; multi-transition profile not qualified. Authorize each later consequential effect or explicitly bounded continuation. |
| TCR-2 — Preserve historical effects | Proposed; Institutional Governance, Control Plane and hub | B1 and B3 establish single-effect foundations; multi-transition profile not qualified. Later invalidation must not erase earlier committed facts. |
| TCR-3 — Revalidate at consequence boundaries | Proposed; Institutional Governance, Control Plane and hub | B1 and B3 establish single-effect foundations; multi-transition profile not qualified. State the real commit ordering for each transition; rechecking alone is not atomicity. |
| TCR-4 — Declare continuation | Proposed; Institutional Governance, Control Plane and hub | B1 and B3 establish single-effect foundations; multi-transition profile not qualified. Separate preparation, dispatch, delegation and independent effects. |
| TCR-5 — Bound revocation claims | Proposed; Institutional Governance, Control Plane and hub | B1 and B3 establish single-effect foundations; multi-transition profile not qualified. Stop future preventable work; do not imply rollback of completed effects. |
| TCR-6 — Distinguish cancellation states | Proposed; Institutional Governance, Control Plane and hub | B1 and B3 establish single-effect foundations; multi-transition profile not qualified. Request, acknowledgement, observed cessation and terminal verification remain separate. |
| TCR-7 — Authorize correction | Proposed; Institutional Governance, Control Plane and hub | B1 and B3 establish single-effect foundations; multi-transition profile not qualified. Require a valid corrective grant for compensation, replacement or reversal. |
| TCR-8 — Keep observation non-authorizing | Proposed; Institutional Governance, Control Plane and hub | B1 and B3 establish single-effect foundations; multi-transition profile not qualified. Observed success or absence cannot authorize continuation. |
| DA R1 — No automatic authority expansion | Proposed; Institutional Governance | Developmental Autonomy section 9; new lifecycle artifacts remain proposals. Competence or maturity evidence may produce a proposal only. |
| DA R2 — Authorize contraction too | Proposed; Institutional Governance | Developmental Autonomy section 9; new lifecycle artifacts remain proposals. Automatic contraction requires an already valid institutional rule. |
| DA R3 — Keep failure dimensions independent | Proposed; Institutional Governance | Developmental Autonomy section 9; new lifecycle artifacts remain proposals. Do not infer incompetence from invalid authority, or erase competence because of a boundary failure. |
| DA R4 — Retain critical incident triggers | Proposed; Institutional Governance | Developmental Autonomy section 9; new lifecycle artifacts remain proposals. Aggregate scores cannot average away configured mandatory-review events. |
| DA R5 — Require explicit restoration | Proposed; Institutional Governance | Developmental Autonomy section 9; new lifecycle artifacts remain proposals. Passing requalification cannot restore authority without a competent decision. |
| DA R6 — Preserve meaningful history | Proposed; Institutional Governance | Developmental Autonomy section 9; new lifecycle artifacts remain proposals. Retain incidents, dissent, authority revisions and prior assessments. |
| DA R7 — Scope every assessment | Proposed; Institutional Governance | Developmental Autonomy section 9; new lifecycle artifacts remain proposals. Bind task, envelope, evaluator, criteria and evaluation period. |
| DA R8 — Keep observations separate from permission | Proposed; Institutional Governance | Developmental Autonomy section 9; new lifecycle artifacts remain proposals. Observed outcomes may inform governance but never issue grants. |

## Historical feedback dispositions

| Source ID and requirement | Disposition and owner | Evidence and next action |
|---|---|---|
| E1 — Prevent replanned business-intent duplicates | Partly covered; Owning component and hub | B5; B6 still characterizes older selected behavior. Reuse merged refund-intent ownership; qualify selected integration and trusted upstream identity. Do not add a competing purpose-key registry without a mapping. |
| E2 — Persist refusals and exchange rejections | Needs verification; Owning component and hub | Historical Moltbook source only; no fresh reproduction. Inspect current denial persistence at exact revisions before reopening the historical finding. Retain protected references or minimized payloads, not unrestricted full proposals. |
| E3 — Bound revocation freshness | Superseded recommendation; Owning component and hub | B3 addresses local ordering; remote mechanism is deployment-dependent. Zero allowed age and human approval do not close check-to-commit races. Use the declared local atomic profile or state remote residual limits. |
| E4 — Use trusted effect-path time | Partly covered; Owning component and hub | B3 scoped implementation. Worker 21 reads trusted time after acquiring its transaction; verify other entry points separately. Do not use monotonic time as an unqualified substitute for wall-clock expiry. |
| E5 — Declare observation consistency | Deployment-dependent; Owning component and hub | Historical feedback and RS07/RS08. Specify finality, visibility and dedupe retention before absent can support retry. A guessed waiting window is insufficient. |
| E6 — Bind adapter implementation | Needs verification; Owning component and hub | Historical feedback asks for verification; ER01 is related. Inspect live binding and declared deployment identity; an adapter name alone does not establish code equivalence. |
| E7 — Avoid automatic partition merge | Deployment-dependent; Owning component and hub | Deferred multi-store design. Retain divergent histories and competent adjudication; do not treat highest sequence number as legitimacy. |
| E8 — Narrow claims and retain falsifier provenance | Proposed; Owning component and hub | Evidence contract consolidation. Fold into ES01, ES03 and RS12; distinguish confirmed falsification from an unconfirmed concern. |
| D1 — Correct public documentation | Partly covered; Owning component and hub | B1 plus this documentation proposal. Use current repository names and profile-specific claims; retain historical names inside historical evidence. |

## Original consolidated recommendations

The October 5 document is a historical architectural review. Its 21 project sections remain traceable below; none of its historical defect descriptions is reasserted as a current defect without fresh inspection. Section numbers are preserved as CR01–CR21 register locators, not claimed as original requirement IDs.

| Locator and original topic | Current disposition |
|---|---|
| CR01 — BitRep | Evidence Attestation is selected in B1; signature-only scope remains. Full original recommendations need component review. |
| CR02 — The Index | Evidence Registry is selected in B1; local chain scope is not fleet consensus or factual truth. |
| CR03 — Alvorada constitutional governance | Institutional Governance remains the authority-semantics owner; repository acceptance is not institutional ratification. |
| CR04 — Agent Action Manifest | Manifest 1.1 is selected. ER01 and IF01 define additional profile proposals. |
| CR05 — Agent Control Plane | Selected persistence baseline and merged optional profiles differ; use B1–B3. |
| CR06 — Moltbot Safe | Execution Runtime selected baseline differs from merged refund-intent and authority/effect profiles; use B1, B3 and B5. |
| CR07 — Agent Replay Bundle | Selected reconstruction is not policy reevaluation, independent verification or full new-profile export. |
| CR08 — Agent Governance Evidence Pack | Selected transformations exist; ES and RS add proposed claim contracts. |
| CR09 — Open Decision Evidence Standard | Selected implementation profile is in B1. New mappings require explicit compatibility review, not silent schema drift. |
| CR10 — Alvorada archive and ODEX IMX | Governed Exchange carries the selected local transport path. Distributed lineage merge remains deferred. |
| CR11 — Portable Reasoning Protocol | Optional behavioral package. Separate client and PRP work are outside this reconciliation; no current-version claim is refreshed. |
| CR12 — Research Intelligence Protocol | Optional research workflow, not a truth or authority source. |
| CR13 — Truth Freedom Agency Protocol | Optional behavioral guidance, not runtime enforcement. |
| CR14 — Comprehension Scope | Conceptual scope guidance; no implementation or validation claim established here. |
| CR15 — Architecture of Mind | Private mechanisms remain outside public contract publication and this audit. |
| CR16 — IGPG Practice System | Practice offering; no runtime dependency is introduced. |
| CR17 — Cognous version one placeholder | Navigation and archival disposition require project review; no runtime dependency. |
| CR18 — Alvorada placeholder | Navigation and archival disposition require project review; no institutional adoption implied. |
| CR19 — Comprehension Stack | Conceptual organization; no new mandatory runtime component. |
| CR20 — Cognous site | Public claims and navigation require alignment with accepted evidence; no deployment claim inferred. |
| CR21 — Open Control Stack consolidation | Original baseline B1 is historical; the implementation update above records later adoption and optional execution. |

The original CR17/CR18 register mapping omitted three source sections. The mapping above corrects those locators to the attached document’s actual 21-section order; earlier register revisions remain in Git history.

## Source mapping and preservation

ER, ES, IF, RS and MG retain the source requirement IDs. E1–E8 and D1 retain the Moltbook identifiers. TCR-1–TCR-8 retain the temporal invariants; TCR-01–TCR-15 are separately named scenario IDs, not interchangeable with those invariants. DA R1–R8 refer to Developmental Autonomy section 9. GC locators refer to sections of Governed Context, which supplies no equivalent numbered requirement series.

The proposed TCR scenario matrix remains the acceptance specification for that future profile: valid continuation, revocation, policy change, expiry, unknown external delivery, cancellation request, late commit after acknowledgement, delegation, callbacks, partial completion, corrective authority, unavailable observation, duplicate replay, equivalent intent and concurrent invalidation. No scenario is marked executed by this register. Developmental Autonomy sections 6 and 10 retain the artifact definitions and qualification matrix; GC sections 4 and 8 retain the context artifacts and matrix.

Original addenda remain unchanged. This register is the current planning overlay; edits to the source documents should reference it rather than rewrite their historical evidence. Retain a per-requirement evidence link before promoting a disposition to covered.

- 01-Cognous_Consolidated_Engineering_Recommendations.docx — SHA-256 `e25292bd6a4ced89040901e50e8470f728a6d8b3425b1baf41a003bab918c08f`.
- Cognous_Engineering_Addendum_Developmental_Autonomy(1).docx — SHA-256 `bc7b30ef418dac418932f54d06a615c29eef308c42937008549493fae362edf8`.
- Cognous_Engineering_Addendum_Evaluation_Semantics_and_Evidence_Contracts(1).docx — SHA-256 `7d3af405947ec4afca9dda99ff9c15206ccf4f7728f1c08d50de8fab9631ceb9`.
- Cognous_Engineering_Addendum_Execution_Release_and_Redemption(1).docx — SHA-256 `6c73f17a247ab6b6dcb4c45960f4ff511b84dbe118657680288f264c9660a5c8`.
- Cognous_Engineering_Addendum_Governed_Context_and_Epistemic_Provenance(1).docx — SHA-256 `33ddc98c30671971820e1db79815fd09b984f8e469dcb4da4adf18185db59bf2`.
- Cognous_Engineering_Addendum_Memory_Admission_and_Evidentiary_Custody(1).docx — SHA-256 `faa44c4c0e26777f2dcf91f381d9e378cf8b29dbbc874159de3ec5f85372021a`.
- Cognous_Engineering_Addendum_Moltbook_Feedback_Recommendations.txt — SHA-256 `44df9d3f7f27656b934671998aa9a8151550d94ee2c5fe66d729b4885c976572`.
- Cognous_Engineering_Addendum_OpenAPPA.docx — SHA-256 `97fdfbf92b70f7217f1f3be009d4bbafb38dbc3d4d19a12c9888ac78f88d91c6`.
- Cognous_Engineering_Addendum_Research_Synthesis_and_Deployment_Assurance(1).docx — SHA-256 `d885e5f12ce2bb2927a12bb6cb359f17e47ed2ad390b53cd921d9a7207f72f50`.
- Cognous_Engineering_Addendum_Temporal_Consequential_Reach(1).docx — SHA-256 `bfbf7ead0b6b9bd5f22ea8fcd829a3e5a891028a620a80c0e9eac64a35122e3f`.

## Release language

The Cognous Open Control Stack is a pinned bounded synthetic reference. Newer merged component profiles are tracked separately from the default selected integration. The optional authority/effect profile qualifies cooperating same-host authority mutation and synthetic SQLite effects under its declared handoff and transaction model. It does not establish distributed authorization, external-destination atomicity, universal mediation, production identity or key custody, independent external truth, production readiness or EBL-Core conformance. Governed context, persistent-memory admission, continued-authority trajectories and developmental-autonomy records remain proposed or deployment-dependent unless separately implemented, selected and qualified.

## V1 reference extension implementation

A subsequent isolated batch adds environment prerequisite observations, a local context/memory adapter, a two-step refund trajectory using the accepted atomic executor, and non-authorizing institutional review records. See the [profile coverage ledger](v1-reference-profiles.md#coverage-and-open-requirements) for exact partial mappings and remaining work. These additions do not close complete IF/MG/GC/TCR/DA requirements or establish production deployment. The existing default runtime, source pins and producer schemas remain unchanged. Local tests and final-head CI belong to the implementation PR; historical B1–B7 remain preserved.

## Context binding, notification and staging recovery follow-up

After PR #27 merged at `ec6a89c0f27073c94d29ae3ae4b9a836733c3b85` with all 19 final-head checks successful, a separate integration batch adds an explicit context-to-action wrapper, independent notification authority/local outbox, and verified per-database staging snapshots. See [the detailed contract and remaining limits](context-notification-recovery.md). These changes advance the partial mappings; they do not imply default-path adoption, production identity/custody, remote effects, cross-store atomicity or deployment restoration authority.

## Unified v1 extension evidence

PR #28 merged at `05fe3ce547b8387f466b23c22b6b2d6481ea780e` after all 22 final-head checks passed. The following evidence-consolidation batch gathers all seven extension profiles under one exact-source/lock gate, advancing the bounded ES01/ES02/ES04/RS12 mappings. All 58 profile tests remain; the overlapping automatic workflow is consolidated rather than dropping tests. See [gate predicates and limits](v1-extension-release-gate.md). The existing default release and production-dependent requirements remain separate.

## Context deadline enforcement follow-up

PR #29 merged at `dcc7ef2ea6bf9049fefce86206e79015d76f728b` after all 23 final-head checks passed. A subsequent bounded repair caps context-bound claims at the context deadline and rechecks persisted claim caps on bind/dispatch. The destination's existing post-lock trusted-time check now prevents an effect when context expiry wins while execution waits. `context-action/2` and extension evidence contract version 2 require four additional tests (62 profile tests total); version 1 evidence remains historical. See [issuance and migration](context-notification-recovery.md#version-2-issuance-and-migration) for clock assumptions, conservative local grant lifetime and fail-closed handling of uncapped old claims.

## Standalone recovery package integrity

PR #30 merged at `9f70b7726f6b23a65cc700f56494a1e73b3ccf5c` with all 23 final-head checks successful. A subsequent recovery repair makes backup packages standalone SQLite files and verifies the exact staged restore bytes, preventing unlisted WAL/SHM inputs or a source-path reread from changing the restored image outside its digest. Snapshot contract version 2 rejects prior packages rather than silently migrating them. Five additional recovery checks raise the extension evidence contract to version 3 and 67 required profile tests. Freshness, activation authority, coordinated restore, authenticated custody and production readiness remain unqualified.

## Deployment evidence intake follow-up

A separate optional [deployment review packet](deployment-review-packet.md) implements structural intake for the ten [deployment responsibilities](v1-deployment-responsibilities.md). It binds declared deployment/environment/profile/source/configuration scope and current lock bytes, requires named owner references and retained current evidence, and reports missing or changed input. This is partial support for RS02, ES05 and RS12, not completion of production qualification or an adopted release decision. The checker always denies authorizing/production-ready claims in its output. Earlier register entries retain their historical review scope.

## October 8 addenda intake and parallel ownership

The [October 8 intake register](workstreams/addenda-intake-2026-10-08.md) adds OG01–OG05, SH01–SH04, Production Authority Context / Resolver Assurance, and Moltbook Addendum B. It preserves source identifiers, distinguishes new standalone reference work from runtime integration, and records existing PR dependencies. No complete new requirement is closed by intake or by launching a worker. The merged deployment-review work in PR #32 remains separately scoped; its register section is preserved above.
