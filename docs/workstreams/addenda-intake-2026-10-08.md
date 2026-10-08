# Engineering addenda intake — 8 October 2026

Baseline: hub main `649df22a1392af2c4fa77e4c71749c482f82649c`, freshly inspected. Scope: four October 7 addenda supplied for this intake. All statuses below are intake/worker snapshots; an open draft or local pass is not accepted release coverage. No whole addendum is complete. Accepted pins and prior evidence remain unchanged.

## Ownership and reconciliation

Four parallel workers own only new standalone reference files: lifecycle OG01, semantic SH01, resolver RA-01 and feedback F4. The register owner owns this page and an additive link in the main register. Shared gates, pins, README and existing runtime files are excluded from these four batches. RA identifiers are local planning groups; A1–A18 remain the resolver source scenario IDs. OG/SH priorities are intake sequencing recommendations; Moltbook priorities are source priorities, not release blockers.

The consolidated October 5 baseline and existing register remain historical context. Current register records accepted bounded authority/effect, refund-intent, context, review, notification and recovery profiles; these are foundations to reuse, not proof that the new operational contracts are covered. Historical Moltbook code allegations refer to older component revisions and require fresh revalidation. Design critiques and source papers are not independent current implementation evidence.

## Concurrent work and integration dependency

| Work | Observed state and integration rule |
|---|---|
| Hub #32 | Deployment packet, merged at `ec0b9a86441369272280895b183d43273445b106`; 21 local tests and dedicated CI reported in PR. Structural evidence only. Its separate register appendix is preserved. |
| Hub #33 | Reviewer configuration, open; PR reports 25 review/recovery local tests. Shared evidence count needs reconciliation. |
| Hub #34 | Restore sidecar repair, merged at `166ccdcbfbff909e0256d58b8450f3ea80aad9a2`; 9 local recovery tests reported; integration tests not rerun. |
| Hub #35 | Context admission expiry, draft; six stdlib cases reported, pytest unavailable. Expected context population changes 16 to 21. |
| Hub #36 | Temporal exact outcomes, draft; 15 local tests reported. Expected temporal population changes 7 to 15. |
| INT-01 (root owner) | Pending integration PR42: reconcile exact test populations and versioned evidence contract for #33/#35/#36, including review-count discovery; qualify integrated exact heads before acceptance. Do not infer final totals from two PRs alone. |
| Executor #29–#31 | Reserved for separate dependency/guard work. This intake makes no executor edits, merges, or hub-pin advancement. |

PR descriptions supply the reported test evidence above; this documentation task did not rerun those suites or establish final-head CI acceptance. Open PRs are proposals. New standalone checks do not enter the seven-profile release gate automatically.

## Requirement register

### OG01 — P1

- Source: Lifecycle addendum, OG01.
- Owner / target: Lifecycle worker / deployment governance; hub.
- Bounded deliverable: Supplied-inventory reconciliation with tenant, environment, window, identity joins and coverage.
- Acceptance: Unregistered replica, expired binding, missing owner, retired identity, incomplete discovery.
- Status / gaps: Partial reference: hub PR38 merged at `931f8c9ab36fe9c6367b9c20ac7828dcfde3aefa`; 16 local tests and accepted checks passed. Retirement workflow, real discovery, admission and tombstones remain open.
- Dependencies / conflicts: RS09; existing inventory and identity systems. No runtime admission authority.

### OG02 — P1

- Source: Lifecycle addendum, OG02.
- Owner / target: Manifest, Runtime, supply-chain owner.
- Bounded deliverable: Exact extension artifact admission and loading/replacement binding.
- Acceptance: Signed but unapproved, changed digest/schema, withdrawn cache, current per-call authority.
- Status / gaps: Proposed; no implementation assigned in this batch.
- Dependencies / conflicts: IF03, ER04, existing loader; real credential/version guarantees deployment-dependent.

### OG03 — P1

- Source: Lifecycle addendum, OG03.
- Owner / target: Control Plane and adapter owners.
- Bounded deliverable: Declared policy semantic subset and immutable activation generations.
- Acceptance: Unknown action, missing fields, conflicting rules, obligations, stale generation, unsupported transform.
- Status / gaps: Proposed; no cross-adapter equivalence qualified.
- Dependencies / conflicts: ER04/ER06; adapters must declare supported semantics.

### OG04 — P1

- Source: Lifecycle addendum, OG04.
- Owner / target: Reliability owner, Control Plane, Runtime.
- Bounded deliverable: Operational admission, durable quotas, circuits and bounded recovery probes.
- Acceptance: Stale telemetry, budget exhaustion, concurrent probes, restart, denial/error separation.
- Status / gaps: Proposed; operational deployment envelope unqualified.
- Dependencies / conflicts: Durable reservation contracts, ER07/RS09; recovery authority remains separate.

### OG05 — P1

- Source: Lifecycle addendum, OG05.
- Owner / target: Security operations, Replay, Evidence Pack.
- Bounded deliverable: Correlated incident delivery, acknowledgement and evidenced closure.
- Acceptance: Delayed/duplicate/out-of-order events, unavailable endpoint, unknown suspension, premature closure.
- Status / gaps: Proposed; external incident adapter unqualified.
- Dependencies / conflicts: RS09/RS10, MG04; alert clearance cannot restore authority.

### SH01 — P1

- Source: Semantic Handoffs addendum, SH01.
- Owner / target: Handoffs worker / Manifest, exchange adapter; hub.
- Bounded deliverable: Exact bounded proposal/interpretation commitment and semantic acceptance checker.
- Acceptance: Unit/namespace/time ambiguity, dropped restriction, changed context, stale acceptance, receipt versus effect.
- Status / gaps: Partial reference: hub PR37 merged at `dd14d3a82a905ad3e366db85d19d40dcf1006baf`; 18 local tests and accepted checks passed. Durable clarification and live dispatch remain open.
- Dependencies / conflicts: OG03, RS03, IF/MG; acceptance does not grant permission.

### SH02 — P1

- Source: Semantic Handoffs addendum, SH02.
- Owner / target: Review service / institutional workflow.
- Bounded deliverable: Atomic review-capacity admission and deadline-safe fallback.
- Acceptance: Last-slot contention, unavailable reviewer, stale capacity, timeout, reassignment, restart; no auto-approval.
- Status / gaps: Proposed; reviewer-record PR33 does not implement capacity scheduling.
- Dependencies / conflicts: ES05/OG04; qualified reviewer identity, exact candidate and decision validity.

### SH03 — P1

- Source: Semantic Handoffs addendum, SH03.
- Owner / target: Institutional/deployment owner, Evidence Pack.
- Bounded deliverable: Intervention register mapping actual visibility, lever, authority and completion evidence.
- Acceptance: Owner lacking lever, operator lacking authority, missing feed/receipt, deployment change.
- Status / gaps: Proposed; named ownership alone is not control evidence.
- Dependencies / conflicts: OG01/OG05; deployment packet PR32 is structural review only.

### SH04 — P2

- Source: Semantic Handoffs addendum, SH04.
- Owner / target: Deployment qualification / Manifest.
- Bounded deliverable: Separate autonomy, causal reach, goal structure and task breadth; versioned obligation mapping.
- Acceptance: Drafting versus transaction profile, unknown breadth, tool/domain changes and invalidation.
- Status / gaps: Proposed; no combined agentic score or automatic authority expansion.
- Dependencies / conflicts: OG01, RS02/RS12; profile selects checks, never permissions.

### RA-01 — P0/P1

- Source: Resolver addendum sections 3–7, 9, 11, 14; partial A3/A8/A9/A10/A11/A16/A18.
- Owner / target: Resolver worker; hub / future Control Plane adapter.
- Bounded deliverable: Synthetic source-observation assurance: source/object scope, current/historical state, freshness, anti-rollback and conflicts.
- Acceptance: Wrong institution/domain/object, replay/staleness, outage/conflict, future timestamps, preserved historical observations.
- Status / gaps: Local reference complete: 20 tests passed twice; head a9df5c6eab2636bd3ca8c72dcb1493a6f2509119. Published PR40, head `8410ff695693e69eca5843776efcd1b921381a7b`; dedicated Linux CI passed 20 tests twice on each Python 3.11/3.12. Broader checks remain pending. No production authentication or effect integration.
- Dependencies / conflicts: Local register ID, not source ID. Synthetic authentication fixture; durable trust/high-water storage remains open.

### RA-02 — P1

- Source: Resolver sections 8, 10, 12, 14; A1/A2/A4/A5/A6/A7/A12/A13.
- Owner / target: Institutional Governance, Control Plane, Runtime.
- Bounded deliverable: Decision/effect authority-resolution binding, revocation/delegation and explicit succession.
- Acceptance: Exact grant/mandate, request self-assertion, revocation before effect, ancestor suspension, succession, stale policy/approval.
- Status / gaps: Proposed integration; existing bounded authority checks must be reused and remapped, not presumed missing.
- Dependencies / conflicts: RA-01; exact consumer versioning; no implicit succession or inherited authority.

### RA-03 — P2

- Source: Resolver sections 5, 9–15; A14/A15/A17 plus full A1–A18.
- Owner / target: Deployment owners, hub, Replay, Evidence Pack, ODES.
- Bounded deliverable: Real source authentication, rotation, compromise containment, propagation/race measurement and exact-revision qualification.
- Acceptance: Full A1–A18 twice, real source/credential/clock tests, external check-to-commit residual risk.
- Status / gaps: Deployment-dependent; no production source or destination qualification in this batch.
- Dependencies / conflicts: RA-01/02, named institutional systems; evidence exports remain non-authorizing.

### A-E2 — P1 (source)

- Source: Moltbook B section 2, amendment A-E2.
- Owner / target: Control Plane and Execution Runtime.
- Bounded deliverable: Revalidate durable refusal recording in both paths; retain protected untrusted payload references.
- Acceptance: Refusal trace exists with effect ID, failed check and input versions; destination absence alone insufficient.
- Status / gaps: Historical allegation needs current-code revalidation; no confirmed present defect imported.
- Dependencies / conflicts: Amends E2; no overlap edits to executor dependency PR29–31.

### A-E5 — P1 (source)

- Source: Moltbook B section 2, amendment A-E5.
- Owner / target: Destination adapter / Runtime.
- Bounded deliverable: Declare dedupe, request-deadline/authoritative-read, or hold-only retry semantics.
- Acceptance: Replica lag, no lag bound, in-flight delay; absent alone cannot establish safe retry.
- Status / gaps: Historical allegation needs current-code revalidation; remote semantics unqualified.
- Dependencies / conflicts: Amends E5; F2/F3; configured bounds are not measured guarantees.

### A-E1 — P1 (source)

- Source: Moltbook B section 2, amendment A-E1.
- Owner / target: Control Plane and Runtime.
- Bounded deliverable: Stable purpose key distinct from policy/manifest/grant provenance.
- Acceptance: Config or grant revision change plus lost acknowledgement yields exactly one terminal effect.
- Status / gaps: Partial existing refund-intent profile; amendment scenario not demonstrated by this intake.
- Dependencies / conflicts: Amends E1; preserve independent atomic-authority and refund-intent profiles.

### F1 — P1 (source)

- Source: Moltbook B section 3, F1.
- Owner / target: Control Plane / refusal-record owner.
- Bounded deliverable: Held-decision observed authority inputs and causal reconsideration conditions.
- Acceptance: Policy v7 hold retains v7 after supersession; reconsideration never auto-authorizes.
- Status / gaps: Historical finding needs current-code revalidation; integration open.
- Dependencies / conflicts: E2/A-E2; hold/deny vocabulary must be explicitly versioned.

### F2 — P2 (source)

- Source: Moltbook B section 3, F2.
- Owner / target: Recovery coordinator / destination adapter.
- Bounded deliverable: Bounded re-read schedule, denominator, capped retries and named escalation.
- Acceptance: Exactly N unsuccessful reads then one escalation, no effect; unknown lag stays explicit.
- Status / gaps: Proposed; scheduling/escalation unimplemented in this batch.
- Dependencies / conflicts: A-E5/F1/F3; assumed worst-case bound must not become authoritative absence.

### F3 — P2 (source)

- Source: Moltbook B section 3, F3.
- Owner / target: Runtime, Replay, Evidence Pack.
- Bounded deliverable: Separate observation coverage and consistency with shape-specific rendering.
- Acceptance: Unbounded observation cannot contain absence verdict; distinguish widen/wait/repair-input.
- Status / gaps: Proposed; full adapter/renderer integration open.
- Dependencies / conflicts: A-E5/F2; transport receipt is not effect observation.

### F4 — P2 (source)

- Source: Moltbook B section 3, F4.
- Owner / target: Feedback worker; hub / future Evidence Pack.
- Bounded deliverable: Structural grouping by failure-relevant dependency lineage.
- Acceptance: 100 same-cache receipts do not inflate support; missing lineage remains unestablished; labels do not prove independence.
- Status / gaps: Partial reference: hub PR39 merged at `0f85b79dbd1a31a8429a484b106281270dd746c1`; 12 local tests and accepted checks passed. Evidence Pack integration remains open.
- Dependencies / conflicts: E8, CR02/CR08; grouping cannot establish truth, independent witnesses or calibrated weights.

### F5 — P3 (source)

- Source: Moltbook B section 3, F5.
- Owner / target: Evidence/log infrastructure owner.
- Bounded deliverable: Ordering and pre-existing criterion references, with external anchor requirements.
- Acceptance: Later-inserted refusal detectable against authenticated append order and earlier criterion record.
- Status / gaps: Design-only; external append-only anchor not established.
- Dependencies / conflicts: Shared-secret HMAC is not independent witnessing; retain F1/E2 links.

## Resolver scenario coverage map

| Source IDs | Bounded mapping / outstanding work |
|---|---|
| A1, A2 | RA-02: complete decision authorization and rejection of request-supplied authority. |
| A3 | RA-01 partial: historical evidence cannot establish current state. |
| A4–A7 | RA-02: effect-time revocation, parent/ancestor invalidation and governed succession. |
| A8–A11 | RA-01 partial: scope binding, old response replay, conflicts and outage/freshness. |
| A12, A13 | RA-02: changed policy and obsolete approval bindings. |
| A14, A15 | RA-03: authorized rotation and compromised resolver/source containment. |
| A16 | RA-01 partial: future source clock tolerance. |
| A17 | RA-03: external revocation/commit race characterization. |
| A18 | RA-01 partial historical classification; full past-effect/current-denial integration remains RA-02/03. |

## Acceptance handoff

Each worker returns base/head, exact changed paths and profile version, local test command/results, final-head CI state, migration rules, remaining limitations and proposed PR. A new reference check is accepted only for its demonstrated scope. Root owns integration sequencing after review. Production authentication, real discovery, remote delivery, competent institutional adoption and actual intervention remain deployment qualification work.

Source documents remain unchanged. This proposed repository register summarizes engineering requirements only; no private implementation corpus is exported. Retain earlier E1–E8/D1 and ER/IF/MG/GC/RS/ES/TCR/DA identifiers and evidence in the main register; amendments refine them rather than silently closing or renumbering them.

## Publication checkpoint

The user subsequently authorized publishing and merging eligible work. This register is a documentation-only proposal; each component PR retains its own acceptance gates. Resolver publication is complete in [PR40](https://github.com/cogno-us/cognous-open-control-stack/pull/40). The earlier publication pause is historical, not a current authorization blocker.

Acceptance checkpoint: hub #32, #34, #37, #38 and #39 are merged. Resolver #40 and the shared evidence integration #42 remain pending acceptance. Requirement closure remains limited to the bounded profiles above; no production qualification is inferred.
