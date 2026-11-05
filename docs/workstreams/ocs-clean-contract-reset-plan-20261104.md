# OCS clean contract reset — static project plan

**Architect decision:** 2026-11-04. **Program intent:** abandon the accumulated historical-qualification remediation path; establish a clean *development* baseline from selected current component sources, reconcile every supported inter-component behavioral boundary, and qualify the candidate with a new, small, independent contract-first battery.

**Supersession:** This plan **supersedes the execution strategy** in draft Hub PR [#264](https://github.com/cogno-us/cognous-open-control-stack/pull/264) (`current-contract-qualification-transition-plan-20261104.md`), and supersedes the dependent incremental P1 merge sequence as the *controlling future-work direction*. Historical decisions, evidence, vulnerabilities, and existing competent reservations of authority are **not** rescinded by plan supersession. Earlier plans and PRs remain readable as predecessor records. This file is itself a proposal until integrated by competent authority; its creation does not modify CI, a lock, a contract, a test, or branch protection.

**Non-negotiable:** A fresh development candidate is **UNQUALIFIED, NON-RELEASE, NON-PRODUCTION** until separately qualified and accepted. Closing PRs and archiving tests are not demonstrations of corrected security behavior. Preserve original adverse findings and source lineage.

## A. Current facts and entry gates

At plan authoring, Hub `main` is `985dfe461241db18a318b921d4a7d52ffb47491a`. This is an **initial observation**, not a permanent freeze or proof of qualification; refresh before execution.

Existing Hub assets to reuse:
- [component-lock.json](../../component-lock.json), [contracts/qualification-surfaces-v1.json](../../contracts/qualification-surfaces-v1.json), [CROSS_COMPONENT_TESTS.md](../../CROSS_COMPONENT_TESTS.md), [existing closeout control panel](release-closeout-control-panel.md), [security runtime migration record](security-runtime-migration-20261016.md), and [engineering register](../engineering-register.md).
- Cross-repository [Qualification](https://github.com/cogno-us/cognous-stack-qualification), [GAX](https://github.com/cogno-us/cognous-governed-exchange), [ODES](https://github.com/cogno-us/open-decision-evidence-standard), and each component actually selected from the lock. Inventory the complete active component universe before declaring the selection.
- [Engineering Constitution](https://github.com/cogno-us/cognous-engineering-constitution), including `ENGINEERING_CONSTITUTION.md`, `ADOPTION.md`, `TESTING_POLICY.md`, `ORCHESTRATION.md` and any independently adopted addendum. Determine the exact controlling adoption revision *in each repository*. Conflicting or missing adoption records mean **UNVERIFIED**, not implicit authority.
- Prior verified integration facts: Qualification #269 merged as `8e5e4ac31cae3300694bcaa3bfa67205e204813c`; GAX #67 merged as `e78a7be3cb4ea622d2a0eec430c209449ec4c86c`. These are implementation source facts, not transfer of release qualification.

Observed open Hub work at plan authoring (re-fetch exact heads and open state): [#265](https://github.com/cogno-us/cognous-open-control-stack/pull/265) crosswalk; [#264](https://github.com/cogno-us/cognous-open-control-stack/pull/264) superseded draft plan; [#263](https://github.com/cogno-us/cognous-open-control-stack/pull/263) qualification repin; [#262](https://github.com/cogno-us/cognous-open-control-stack/pull/262) trusted freeze-record verifier; [#261](https://github.com/cogno-us/cognous-open-control-stack/pull/261) vulnerability reporting; [#260](https://github.com/cogno-us/cognous-open-control-stack/pull/260) workflow credential hardening; and independent MVP/draft work [#247](https://github.com/cogno-us/cognous-open-control-stack/pull/247), [#244](https://github.com/cogno-us/cognous-open-control-stack/pull/244), [#223](https://github.com/cogno-us/cognous-open-control-stack/pull/223), [#222](https://github.com/cogno-us/cognous-open-control-stack/pull/222), [#221](https://github.com/cogno-us/cognous-open-control-stack/pull/221), [#213](https://github.com/cogno-us/cognous-open-control-stack/pull/213). Qualification [#270](https://github.com/cogno-us/cognous-stack-qualification/pull/270) is an old-runner remediation candidate. No merge or closure is implied by inclusion here.

## B. Reset rules

1. **Preserve, do not execute, old history by default.** Freeze evidence references and exact original failure status; cease historical-tuple requalification as a routine development goal. Do not delete Git history, tamper with historical results, rescore old failures, or create an artificial PASS.
2. **Retire old pending work explicitly.** Close *superseded* unmerged PRs with short, source-pinned reasons and a pointer to this reset; a closed PR is an archived proposal, not an accepted implementation. A security remediation PR is not silently discarded: retain the finding, invariant, severity, owner, test and candidate fix in a canonical residual-risk/issue record before closure. An unrelated MVP project remains under its existing owner/authority; do not unilaterally cancel it.
3. **No bulk merges.** Only choose the source components intentionally for the clean candidate. Do not import incomplete or unsafe changes simply to empty the PR queue.
4. **Contracts are behavioral**, not mere JSON shapes: inputs, outputs, trust and authorization, refusal, evidence/provenance, expiry/revocation, state/durability, retries/recovery, idempotency, effects, failure/partial failure, version/profile semantics and supported producer-consumer identities.
5. **Reconcile before code.** Document all selected component boundaries first, assign one canonical contract writer, and freeze the cross-component compatibility contract before parallel migrations. Internal implementation freedom is allowed only where relied-upon semantics remain protected.
6. **Qualify the current candidate**, not an obsolete matrix. Design a fresh minimal independent suite with current component-local tests, pairwise contract checks, and a small explicit end-to-end security/effects flow. Reuse useful negative fixtures from history; current acceptance must be reproducible from the new source/configuration pins.
7. **No premature CI waiver.** Current required checks and branch protection remain effective until competent authority reviews and explicitly adopts a replacement current-contract acceptance rule. Develop and shadow-run the new battery in parallel; change the required gate only through a separately authorized policy migration, never by hiding failures.
8. **Zero drift.** No architecture expansion, new generic testing platform, duplicate dashboard, speculative compatibility with unsupported old tuples, paid calls, cloud deployment or production effects. A real interface conflict triggers one concise source-backed decision, while independent work proceeds.

## C. Bounded execution program

### R0 — Freeze, classify, and stop stale work

**Owner:** lead orchestrator; read-only investigators in parallel.

- Capture current source identities and selection: each component, repository, commit/tree, version/profile, lock hash, mandatory CI, active ownership and adoption documents. Capture outstanding current security findings (including Hub freeze verification, credentials and private reporting) in an existing control panel or residual-risk register.
- Capture predecessor qualification records and original failed results as immutable references; archive by *reference*, not bulk-copying or rerunning historical suites.
- Inventory all open Hub and active related Qualification PRs and classify individually: **SUPERSEDED_CLOSE**, **SECURITY_OBLIGATION_TRANSFER**, **SEPARATE_ACTIVE_PROGRAM**, or **KEEP_FOR_CURRENT_CANDIDATE**. A PR may have multiple obligations; preserve them all before closure.
- Suggested *review candidates*, not automatic dispositions: #263/#264/#265 and Qualification #270 are likely superseded by this reset; #262/#260/#261 contain security obligations requiring preservation before any closure; #247/#244/#223/#222/#221/#213 may belong to separate MVP governance and cannot be closed merely to achieve a zero-open-PR metric.
- Close approved superseded PRs using GitHub's ordinary close path with explicit successor record. Never delete branches or destroy audit context as part of closeout. Do not close unowned/scope-external PRs without authority.

**Exit R0:** one exact-source reset manifest, per-PR disposition with authority and security crosswalk, predecessor evidence index, developer baseline frozen; all superseded active *work* stopped. No current PASS implied.

### R1 — Select a single supported current tuple

**Owner:** architect/competent selection authority; one canonical lock writer.

- Inventory eligible components and current implementations; verify actual merged revisions rather than PR heads. Select **one** intended current set of component commits and one execution compatibility profile. Document consumers, configuration, build environments, optional components and unsupported/retired generations.
- Read current inter-component contract sources and identify conflicts or absent adopted contracts. No assumption that a draft ODES contract is already normative.
- Produce a reviewable candidate manifest; no automatic upgrade to unrelated branches or package versions.
- Address compatibility/selection decisions explicitly, including whether new GAX `e78a7be3...` is selected and which current security-runtime profile governs. Do not confuse profile string reuse across different tuple revisions.
- Keep baseline `UNQUALIFIED` until independent qualification.

**Exit R1:** versioned exact current component tuple with identified selection/contract authority; one current development target.

### R2 — Boundary and contract crosswalk

**Owner:** one canonical contract writer, parallel read-only component boundary inspectors.

For **each selected component** record:
`component | source SHA | supported profile | exposed entrypoints | inputs (schemas/version/provenance) | outputs/status/error | state and durability | authority/issuer/trust | negative/refusal behavior | retries/recovery/idempotency | effects | producers | consumers | contract owner/version | open mismatch | required tests`.

- Draw the actual dependency graph; assess both individual producer-consumer edges and transitive authority/effect paths.
- Reconcile conflicts by the smallest complete change at the contract boundary. No invented authorization defaults or silent reinterpretation of ambiguous fields, including nested `decision_id`/`effect_id`.
- Preserve currently relied-upon semantics and security floors; classify unsupported obsolete generation behavior as historical without requiring current compatibility.
- Independently inspect the final contract matrix and version/freeze the adopted candidate. Any new binding normative contract needs the competent contract authority.

**Exit R2:** one approved, versioned current-contract matrix with explicit positive/negative invariants and unresolved-risk register. No implementation before the controlling boundary is defined.

### R3 — Smallest implementation repairs

**Owner:** single writer per affected repository, disjoint paths; independent inspectors.

- Implement only discovered mismatches against the R2 frozen contracts. Prefer boundary adapters rather than broad refactors. Restore correct producer-consumer communication, refusal and provenance fields, state transitions, and effects guarantees.
- No new support for obsolete tuples without actual present reliance. Reuse accepted components. Make PRs small, test changed paths, and record rollback and exact source identities.
- Do not change contracts to conform to broken implementation output without competent review.

**Exit R3:** reviewable exact-head implementation candidates with tests and independently inspected changes.

### R4 — Fresh minimal current qualification

**Owner:** independent qualification owner, separate from implementation writers.

Build one new frozen current-contract qualification battery (not a repaired copy of the prior historical release matrix), with three layers:
1. **Component:** currently supported input/output, authority, refusal, error and state tests; negative/boundary/adversarial cases.
2. **Boundary:** each current producer-consumer pair's round trip, provenance/identity, error, mismatch, recovery and duplicate-effect behavior.
3. **End-to-end:** bounded representative governance-sensitive flow(s) with independently checked final effects, including missing/forged/revoked authority, replay/redelivery and partial-failure recovery where reachable.

- Source every test to a frozen R2 contract invariant and exact R1/R3 pins. Independently own the acceptance oracle; preserve all adverse outcomes. Make test selection transitive-impact aware rather than file path only.
- Keep legacy tests accessible for *on-demand forensic reproduction*, not current release qualification after the governed cutover.
- Shadow-run the new battery alongside existing enforced checks and independently review negative coverage and residual risks.

**Exit R4:** exact pinned independent qualification verdict on the new candidate; no production/release claim.

### R5 — Governed CI cutover, integration and security closeout

**Owner:** qualification governance authority and Hub integrator; independent security reviewer.

- Obtain distinct competent approval to replace mandatory qualification applicability/checks. Document old-to-new control coverage, failures, retained negatives, and rollback. Only after approval and successful protected-rule transition may old historical-only workflows cease routine gating.
- Integrate accepted candidate pins and implementation fixes using expected-head merge guards and applicable reviews. Do not turn unresolved current contract failures into N/A or green by waiver.
- Verify security controls captured at R0, including trusted freeze-record verification, `persist-credentials:false` policy and security-reporting mechanisms. Implement/adopt these requirements if their prior PRs were closed rather than merged; preserve residual findings until checked.
- Freeze the actual Hub main SHA, prepare/run authorized Hub-only Security Cloud review, compare findings against predecessor evidence, and keep production/publication HOLD unless separately lifted.
- Update the existing control panel; avoid a new dashboard or blanket claim of qualification.

**Exit R5:** independently accepted current-contract baseline, governed CI transition, integrated Hub candidate, security finding disposition, and one concise closeout report.

## D. Speed, parallelism and scope rules

- R0 inventories are parallel; R1 selection and R2 contract freeze have a single architect/contract decision path; R3 disjoint component repairs parallel after the freeze; R4 independent design may prepare fixtures early but must assess the actual frozen subject; R5 integration and protected policy mutations are serialized.
- **Do not** chase the old reference matrix, re-run historical producer combinations to satisfy an obsolete gate, rewrite old synthetic dates or reconstruct discarded historical run environments as a prerequisite to current development. Preserve failures and obtain a governed CI replacement rather than bypassing branch protection.
- Work in short, bounded sprints with one fresh lead-builder session per sprint. Preserve continuity in this plan, exact GitHub PRs, owner decisions and existing closeout-status record. Do not depend on chat history.
- Every worker assignment must name one work package, current source pin, owner, writable paths, acceptance tests and escalation boundary. Avoid concurrent canonical contract or lock mutations.
- Do not count open PRs, agent count, or green partial shards as independent acceptance. Optimize for elapsed authorization-to-qualified integration and measured CI cost, using actual run metrics.
- No general re-architecture or speculative contract registry. Extend existing contract/qualification structures.

## E. Decision table

| Matter | Status | Rule |
| --- | --- | --- |
| Start clean current-contract baseline and abandon historical runner rehabilitation | **ARCHITECT-APPROVED DIRECTION** | This plan; execution requires controlling authority reconciliation |
| Supersede incremental plan #264 | **ARCHITECT DIRECTED** | Retain PR #264 as predecessor; close after successor recorded |
| Retire historical-only suites from routine execution | **APPROVED DIRECTION; NOT YET ADOPTED CI RULE** | Independent replacement coverage and competent CI policy approval |
| Close superseded unmerged PRs | **APPROVED RESET METHOD, CASE BY CASE** | Preserve security obligations; do not close other owners' separate programs |
| Blindly merge all open PRs | **REJECTED** | Select only qualified intended candidate |
| Delete historical evidence, failures or source ancestry | **NOT AUTHORIZED** | Archive for traceability |
| Change/disable still-required GitHub checks now | **NOT AUTHORIZED** | R5 governed cutover |
| Assert current candidate qualified/released/production-ready | **NOT AUTHORIZED** | Separate evidence and approval |
| Security and constitutional adoption ambiguities | **UNVERIFIED; AUTHORITY DECISION REQUIRED WHERE RELEVANT** | No guessed adoption or self-certification |

## F. Completion criteria

The reset succeeds when the entire intended current component tuple is exactly pinned; all selected interfaces and security/effect obligations are documented and reconciled; necessary code changes have independent review; current-contract qualification has independently accepted positive and negative results; the protected CI selector is validly adopted; obsolete open work is explicitly closed or assigned to a separate owner; unresolved security findings are tracked and assessed; and Hub source/integration status is verified.

**Not a goal:** make every historical test pass, eliminate old evidence, close unrelated MVP projects, or declare production qualification by assertion.
