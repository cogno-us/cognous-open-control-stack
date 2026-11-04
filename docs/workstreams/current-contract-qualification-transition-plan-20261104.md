# OCS current-contract qualification transition — static execution plan

**Decision:** Architect approval, 2026-11-04, to remove historical-only tests from routine active qualification *through a governed, independently reviewed policy transition*. This document records the plan; **it does not enact a new gate, waive a mandatory check, merge a component, or certify a release.**

**Status:** PROPOSED IMPLEMENTATION PLAN / POLICY TRANSITION NOT YET ADOPTED. **Current mandatory checks remain in force until competent approval and a qualified replacement gate are integrated.**

**Program:** Complete the existing OCS P1 closeout, not a new architecture program. Avoid rebuilding the stack, deleting evidence, or revalidating every obsolete historical tuple on every PR.

## 1. Controlling sources and baseline

- Existing Hub source at plan creation: `985dfe461241db18a318b921d4a7d52ffb47491a` on `main`; refresh heads before execution.
- Existing contract and inventories: [contracts/qualification-surfaces-v1.json](../../contracts/qualification-surfaces-v1.json), [CROSS_COMPONENT_TESTS.md](../../CROSS_COMPONENT_TESTS.md), [component-lock.json](../../component-lock.json), [docs/workstreams/release-closeout-control-panel.md](release-closeout-control-panel.md), [docs/workstreams/security-runtime-migration-20261016.md](security-runtime-migration-20261016.md).
- Existing qualification runner and evidence: [cognous-stack-qualification](https://github.com/cogno-us/cognous-stack-qualification), its existing plans, historical results and known limitations. Existing inter-component contracts must be inventoried from their actual owner repositories; in particular inspect ODES's `docs/engineering/ODES-INTERCOMPONENT-CONTRACTS.md` and verify its current existence, version and adoption before treating it as controlling.
- Engineering Constitution: [cognous-engineering-constitution](https://github.com/cogno-us/cognous-engineering-constitution). Verify each affected repository's `ADOPTION.md`, selected exact constitutional revision, project-specific contracts and applicable companion policies. **A proposed change to qualification policy needs its own competent adoption/acceptance; operator approval of this plan is not a blanket waiver.**
- Related current P1 work: Qualification #269 merged (`8e5e4ac31cae3300694bcaa3bfa67205e204813c` per verified handoff); GAX #67 merged (`e78a7be3cb4ea622d2a0eec430c209449ec4c86c`); Qualification #270 open at plan creation; Hub #263, #262, #260, #261 open. Reconfirm independently before acting.
- Preserve the original failed reference runs, historical 35-scenario matrix, seven-component historical tuple evidence, and all other adverse findings under existing retention rules. **Do not rewrite the original oracle, old test outputs, or historical claims.**

## 2. Policy objective and boundary

**Policy candidate:** Historical tests are retained as reproducible evidence but excluded from *routine current-release gating* unless they implement a presently supported compatibility commitment or continuing security/governance invariant. Qualification of current behavior is based on **versioned inter-component behavioral contracts**, not matching old internal implementations.

**Contract conformance includes:** input/output schemas; identity, authority and trust; evidence/provenance and custody; refusal and fail-closed behavior; state transitions, idempotency, recovery and retry; permitted and prohibited effects; temporal scope; canonical source/configuration/version bindings; and relevant negative/adversarial cases. Schema/output shape alone is insufficient.

Distinguish:
1. **CURRENT_REQUIRED:** active supported contract, current applicable release check; may block.
2. **LEGACY_SUPPORTED:** explicit backward-compatibility contract with identified consumers and duration; run when changed boundary is reachable or at prescribed milestone; may block where applicable.
3. **HISTORICAL_ONLY:** obsolete profile, frozen tuple, old file location or superseded implementation expectation without active reliance; archive/run on demand; not current-release gate *after authorized transition*.
4. **UNRESOLVED:** absent contract, uncertain support, or inadequate current negative coverage; retain existing gate until reconciled and approved.

Historical test failure is **not by itself** evidence of a present contract failure, but a required check cannot be relabeled nonapplicable solely because it fails. An outstanding supported contract cannot be retired via category changes.

## 3. Non-negotiable acceptance invariants

- **No silent weakening:** preserve current security-runtime-p2 authority validation, absence-of-authority refusals, mismatch and substitution refusals, revocation/expiry enforcement, source/evidence integrity and permitted-effects boundaries. Retain end-to-end negative tests where behavior spans components.
- **No self-certification:** independent evaluator/reviewer verifies the replacement active contract-to-test mapping and negative cases before adopting a new CI gate.
- **No automatic pass transfer:** historical tests cannot establish current p2 qualification; changed GAX or Qualification revisions need affected current-contract evidence at exact pins.
- **No erasure:** old matrices and failures remain discoverable, reproducible where feasible, and labeled with the original source, selected profile and environment.
- **No unauthorized CI bypass:** preserve existing branch protection and all currently mandatory checks until the authorized qualification policy migration has passed independent review and the responsible authority has explicitly accepted the new rule.
- **No release claim:** source merges, green CI, qualification, certification, organizational adoption and production deployment remain separate statuses.

## 4. Work packages, ownership and gates

### S0 — Reconcile source, authority and current P1 state

**Owner:** lead orchestrator, read-only inspectors in parallel. **Exit:** exact-head inventory, active adoption documents and decision owners; no guessed pins. Read existing plan and component contracts before editing. Confirm actual status of #270 and Hub #263/#262/#260/#261; mark existing blocked stages unchanged.

### S1 — One-time mandatory-test and contract crosswalk

**Owner:** single qualification-policy writer; independent source inspectors for components. Inventory every active reference stage, scenario matrix entry, CI workflow, required status check and test profile. For each obligation record:

`id | source path/test | original pin/profile | owning contract ID + revision | current producer/consumer | support commitment | behavioral invariant | positive/negative cases | current-profile evidence | classification | disposition rationale | reviewer | approval reference`.

Include all 35 current reference-matrix scenarios and separately identify the four historically sourced cases reported by the builder; **their contractual disposition is not pre-decided**. Compare required behavior rather than filename resemblance. Identify missing current replacements for any continuing invariant.

**Exit:** complete source-backed crosswalk in the existing Qualification evidence location or Hub plan subdirectory, reviewable as a separate PR. Unmapped cases remain UNRESOLVED; do not drop.

### S2 — Freeze minimal active contract baseline

**Owner:** architect/contract authority for choices; one canonical contract writer for approved changes. Reuse [qualification-surfaces-v1](../../contracts/qualification-surfaces-v1.json) or an existing adopted contract manifest; avoid creating a second registry. Define versioned supported profiles (including current security-runtime-p2), contract IDs, exact producer/consumer scope, mandatory behavioral assertions, adverse cases and applicability logic. Preserve explicit `LEGACY_SUPPORTED` only where reliance exists. Record compatibility transitions and supersession without rewriting predecessors.

**Exit:** candidate current-contract baseline with independent review, complete coverage map and competent acceptance for any normative change. No new architecture beyond this qualification boundary.

### S3 — Build and test replacement qualification selection

**Owner:** single Qualification writer; independent qualification reviewer separate. Implement **smallest change** to select current required contract checks and reachable supported compatibility checks; archive historical-only suites outside routine gating with links to original immutable evidence. Maintain an optional historical reproduction workflow, manually invoked/on-demand, clearly non-release-gating. Do **not** delete tests or mutate frozen expectations. No file-path-only heuristic may be the sole impact oracle for authority, trust, persistence or effects changes.

Define impacted-contract selection based on versioned contract dependencies, changed callers, interfaces, state or configuration. Always include contract-negative tests, affected integration and any prescribed security/release acceptance. Unknown reachability fails closed to broader testing, not zero tests.

**Exit:** CI Scope Declaration (selected cases, excluded cases with contract reasons, exact pins), mutation/negative coverage, source reproducibility and independently reviewed qualification PR.

### S4 — Shadow comparison and controlled gate migration

**Owner:** independent qualification owner; acceptance authority for gate policy. Run candidate current-contract gate in **shadow mode** against a frozen current Hub/GAX/Qualification tuple while old required checks remain enforced. Compare failures and omissions to the S1 crosswalk; demonstrate each currently required invariant is tested or explicitly transferred under an approved compatible mechanism. Prove historical-only cases are not accidentally counted as current PASS. If a required scenario has no valid current replacement, remain BLOCKED and repair coverage.

**Exit:** independent result and explicit authority approval for changing mandatory CI applicability; then and only then update protected workflows/rulesets and version the new gate. Record approval and rollback/re-enable steps. A reviewer verdict is not a policy adoption act.

### S5 — Finish existing P1 closeout against the approved baseline

**Owner:** Hub integrator, one canonical lock writer, independent reviewers. Finish #270 fixes and accepted GAX/Qualification pin transitions within established authority. Run the qualified current-contract gate at the resulting exact pins. Merge eligible Hub PRs in dependency order **#263 → #262 → #260 → #261**, verifying current heads, reviews, expected-head guards and all applicable checks immediately before each. No red mandatory check is bypassed merely because it is historic; its replacement must already have been adopted under S4.

**Exit:** exact merged SHAs, current gate PASS, full source/evidence and independence record; otherwise one precise blocker.

### S6 — Security scan handoff and closeout

**Owner:** qualified security reviewer/operator. Freeze exact Hub `main` SHA after prerequisite merges. Prepare Hub-only Security Cloud rescan at that SHA, subject to scan authority/tooling. Preserve the eight baseline Hub findings and compare with the new run only if completed. Do not infer finding closure, production certification or deployment. Update existing closeout control panel rather than creating new telemetry.

**Exit:** one closeout record distinguishing implemented, independently qualified, integrated, security-reviewed and any remaining HOLD.

## 5. Parallelism and scope control

- Parallel **read-only** inspection of contracts, CI selectors and archived cases in S1. One canonical writer owns each shared qualification manifest, runner, contract or component lock; serialize all shared mutations.
- S0/S1 evidence inventory and S5 independent preparation can overlap. S2 contract decisions precede S3 gating; S3 shadow run precedes S4 acceptance; S4 gate adoption precedes removal from mandatory CI.
- Keep PRs bounded: (a) crosswalk/baseline proposal, (b) Qualification selector/archival implementation, (c) governed CI gate migration, (d) dependent P1 integration. No unrelated feature, product or security architecture refactor.
- Stop only on source-backed genuine policy/adoption/authority blocker. Do routine CI packaging and test-path corrections without repeated architect questions. Never invoke paid services or production effects.

## 6. Decision register

| Decision | State | Owner / release condition |
| --- | --- | --- |
| Use current behavioral contracts as primary acceptance basis | **ARCHITECT APPROVED — direction** | This plan |
| Preserve historical tests and negative evidence | **REQUIRED** | Throughout |
| Exclude historical-only tests from routine gate | **AUTHORIZED TO DESIGN/MIGRATE; NOT YET EFFECTIVE** | S1 classification, S2 current coverage, S4 independent review and competent approval |
| Retire any one of 35 scenario checks | **NOT YET APPROVED** | Specific scenario-to-contract evidence and normative decision |
| Keep current p2 authorization/security invariants mandatory | **REQUIRED** | Current applicable contract |
| Change GitHub required checks or protection | **NOT YET AUTHORIZED AS BYPASS** | S4 accepted policy, competent integration, protected checks |
| Merge Hub P1 sequence | **CONDITIONALLY AUTHORIZED** | Exact heads, passing applicable gates, reviews, reserved authority |
| Run Security Cloud rescan | **POST-MERGE HANDOFF; EXECUTION CONDITIONAL** | Actual operator capability and authority |

## 7. Success metric and bounded exit

The transition is complete when **(1)** every current supported contract obligation has a verified test and negative coverage; **(2)** every historical-only exclusion is traceable to approved disposition; **(3)** current contract-only qualification passes on the exact accepted tuple; **(4)** all required GitHub protections still enforce the approved gate; **(5)** original failures remain retained; and **(6)** the existing P1 merge sequence either closes or has a single evidenced blocker.

Measure before/after CI latency, test count, flaky/error rates, and coverage per active obligation on the same candidate where feasible. Do not claim savings without measurement or count archived tests as executed.

**Anti-drift rule:** Each new task must trace to one work package and one accepted contract obligation. No new dashboard, general architecture rewrite, retesting of obsolete producer generations by default, or repeated options already decided.
