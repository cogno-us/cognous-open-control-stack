# Cognous Open Control Stack engineering constitution

Status: adopted for this stack by instruction of the operator, André de Lima, on 2026-10-21. Articles EP01–EP18 and the document rule DOC-01 are binding engineering rules for work on the stack's repositories. Adoption changes how engineering work is done. It does not change what the stack guarantees, what any release status says, or any recorded qualification result. It is non-authorizing: it grants no access, spending, deployment, release or production authority, and it makes no claim of certification or security clearance. Operational trust remains HOLD (see [operational trust status](operational-trust-status.md)).

The constitution is adapted from a governed engineering text the operator maintains for a separate programme. Only the generic engineering articles, the review policy, the documentation rule and the technical cautions are carried over. Domain-specific principle tables and repository crosswalks of that programme are not part of this document.

## Authority, source and roles

Authority order: system and organizational security rules; explicit operator authority; the recorded decisions and contracts of the stack (the [component lock](../component-lock.json), [guarantees and limits](guarantees-and-limits.md), component contracts); the articles below; repository cautions. A repository document cannot grant missing access, spending, deployment, release or architectural authority.

Component repositories own implementation of their contracts. The [qualification repository](https://github.com/cogno-us/cognous-stack-qualification) owns independent expectations, fixtures, oracles and verdicts. Qualification is not an alternative implementation or an authority service and must not fit an oracle to implementation behavior. A component cannot certify its own independent qualification. The effect-authorization components (control plane and execution runtime) keep their own execution, replay and effect-time authorization responsibilities; no document, registry entry or terminology mapping transfers that authority.

## Engineering articles

| ID | Required behavior | Prohibited shortcut | Validation |
|---|---|---|---|
| EP01 Reuse before build | Inspect and reuse qualified versioned components | Duplicate an owned capability for convenience | Reuse and source crosswalk |
| EP02 Minimum sufficient implementation | Deliver the smallest complete authorized capability | Speculative architecture, infrastructure, dependency or scope expansion | Authorization-to-diff review |
| EP03 Contract before code | Identify source, boundary, obligations and acceptance before implementation | Start against an unnamed or mutable contract | Entry checklist |
| EP04 Qualification designed before acceptance | Independent expectations precede candidate acceptance; implementation and qualification stay separate | Fit an oracle to the implementation or substitute developer tests | Independent pre-acceptance source and pin record |
| EP05 Fail closed without inventing policy | Apply the specified conservative treatment and expose missing semantics | Invent a cause, grant, floor, deadline, mapping or default | Negative controls and source audit |
| EP06 Preserve original evidence | Supplement history with corrections and distinct identities | Delete, relabel, overwrite or silently rescore a failure | Immutable predecessor evidence |
| EP07 Exact-source reproducibility | Bind claims to exact source, configuration and head | Transfer a pass across revisions | Exact-head manifest and review |
| EP08 Independently qualified delivery | Distinguish lifecycle evidence; report honest PASS, FAIL and BLOCKED | Treat PR count, green CI or documents as delivery or a pass | Stage record; active effort is unknown unless measured |
| EP09 Safe parallelism | Parallelize independent work against pins; serialize conflicting contract, state, schema, gate and integration changes | Concurrent conflicting authority mutations | Ownership, pin and dependency review |
| EP10 Autonomous within authority | Finish routine authorized work and eligible corrections and merges | Delegate new architecture, financial, security or release authority | Authorization and merge audit |
| EP11 Proactive blocker management | Check dependencies, resolve routine issues, redirect useful work and isolate one decision package | Repeat planning loops or wait for routine continuation | Blocker and next-action record |
| EP12 No unqualified degradation | Preserve mandatory governance, quality and reliability floors | Treat lower cost or a fallback as equivalent | Floor and negative-control evidence |
| EP13 Observability before optimization | Measure baseline cost, latency, refusal, failure, retry, resource use and acceptance | Claim improvement from a projection | Reproducible measurement protocol |
| EP14 Secure by construction | Least privilege, bounded environments, risk-proportionate assurance | Treat CI or speculative counts as security qualification | Enabled-path security review |
| EP15 Bounded changes and reversible integration | Keep changes reviewable, with migration and rollback and recorded irreversible authority | Bundle unrelated architecture or erase history | Scope and migration review |
| EP16 No silent claim promotion | Separate proposed, documented, implemented, developer-tested, independently qualified, deployed and production-qualified | Promote a lifecycle label or replace the stack's claim statuses | Claim and evidence review |
| EP17 Decision finality and controlled reopening | Implement a scoped authorized decision unless valid reopening grounds arise | Reopen from preference, or use finality to suppress a defect | Decision record and reopening assessment |
| EP18 Declarative governance rules, constitutional floor | Move policy and check metadata into a versioned, authenticated registry; constitutional floors and typed evaluator logic stay code | Mutable unchecked data files, policy bypass, arbitrary scripting, a second decision point, invented conformance | Registry and evaluator pins, negative and equivalence tests, independent qualification |

EP17 overlaps EP03, EP06, EP07, EP11 and EP15. It prevents repetitive debate, but an overbroad finality rule could suppress a source, constitutional or security correction. Reopening requires authority, source, rationale, scope, version and qualification implications. It is allowed for new material evidence, a demonstrated inconsistency, a constitutional or security defect, or explicit operator instruction. A correction supplements history and never rewrites it.

### EP18 — declarative governance rules, constitutional floor

**Doctrine.** Rules that define check membership, conditional applicability, reason codes, disposition mappings, required evidence and remediation are governed, versioned **registry data**. Trusted typed evaluators remain code. The immutable constitutional floor remains enforced by the **one** canonical gate of the component that owns the decision. The full design is in [declarative governance registry](declarative-governance-registry.md).

- Derive the complete mandatory check manifest deterministically from authenticated policy, class, profile and assurance inputs. Version and hash the selected registry, the evaluator versions and the policy commitment into the decision context.
- No rule file, feature flag, external caller, model output, selected configuration or privileged operator setting can waive the mandatory floor. Unknown, conflicting, unqualified, downgraded or missing rules or evaluators fail closed.
- Registry activation is a governed policy mutation with authority, epoch, audit and negative-history semantics. Immutable pinned startup rules are a bounded reference profile only, not a policy-change backdoor.
- Keep pure evaluators as registered, versioned, typed code. Do not implement interpreted scripts, a second rules engine or a second decision point.
- Preserve old registry versions and original inputs so historical replay stays deterministic. New policy evaluation is a distinct event and never rewrites an old decision.
- Acceptance needs a closed source-to-rule inventory, a pinned valid registry, no missing mandatory checks, invariant precedence, fail-closed bad-registry cases, replay and version binding, a focused trust review, and independent behavioral equivalence plus refusal evidence. Green CI, a text-only compatibility claim or a historical pass cannot substitute for it.

## Review and allocation policy

Classify a change by its highest applicable risk.

| Tier | Scope | Required review and integration |
|---|---|---|
| Tier 1, routine | Documentation, metadata and minor non-semantic CI | Worker self-validation and required automated checks; coordinator merge. No independent agent review. |
| Tier 2, bounded ordinary engineering | Ordinary bounded implementation that does not touch a Tier 3 boundary | Developer regressions, CI and applicable independent qualification. Add code review only for a concrete identified risk. |
| Tier 3, critical | Admission or decision gates, authority, atomic state, trust, authentication, negative custody, oracle or acceptance logic, security | One focused independent verifier for the identified risk. No blanket multiple reviewers. All applicable Tier 2 gates stay. |

Parallelize nonconflicting work against exact pins and serialize shared contract or gate mutations. Assign concrete, disjoint deliverables. Avoid duplicate manifests, duplicate reviews and unchanged reruns. Enforce the articles through task instructions, scope review and evidence-stage reporting. Add an automated blocker only where a requirement has an objective, repository-local test and a reviewed enforcement design, not merely to police prose.

## DOC-01 — program and status separation

Canonical engineering documents define scope, architecture, dependencies, deliverables, acceptance criteria and completion conditions. They must not encode mutable execution state: current authorization, worker assignments, pull-request status, CI results, qualification outcomes, blockers or progress. That information belongs to the decision record, release status pages and linked evidence records.

- **Class A, canonical architecture and engineering program:** stable definitions, profiles and qualification requirements. These stay stateless.
- **Class B, execution telemetry:** active PR and CI state, assignments, blockers and status. These change as work proceeds.
- **Class C, immutable historical evidence:** dated decisions, reports, logs, manifests, freezes and source records. They may preserve execution facts but are clearly historical and never presented as current status.

DOC-01 never suppresses, deletes, rewrites or invalidates historical evidence. A source-pinned requirement, dependency or immutable provenance reference may name a PR, commit or authorization. The prohibited content is a mutable status assertion presented as part of the canonical program. No automated statelessness check exists in this repository yet; adding one needs an objective, reviewed design under the review policy above.

## Technical cautions

| Trigger | Required response |
|---|---|
| A legacy status or reason resembles a canonical result | Keep a labeled one-way projection; do not rename it into canonical semantics. |
| A mandatory check is missing, disabled, unavailable, unsupported or not evaluated | Treat the result as incomplete and fail closed; do not report a pass or a not-applicable without a source predicate. |
| Freshness evidence is absent | Treat freshness as unestablished. |
| A historical failure or negative record becomes inconvenient | Preserve the original bytes and identity and add a linked successor; no silent rescore. |
| A commit acknowledgment is ambiguous | Keep custody unknown until authenticated, bound readback or reconciliation. |
| A receipt exists | Treat it as post-commit evidence only; it manufactures no authority. |
| Model output proposes an action | Treat it as content or evidence, never a grant or execution authority. |
| An earlier release's evidence passes | Limit the claim to the exact source and profile; requalify. |
| An emulator or local run passes | Claim local behavior only. |
| Source inspection succeeds | Record a read or review, not an executed test. |
| A developer suite or static analysis passes | Record developer and static validation, not independent qualification. |
| A PR merges | Record source integration, not deployment, release or production qualification. |
| Planning is complete | Check executable interfaces, entry decisions and authorization; planning is not readiness. |
| More workers are available during normative ambiguity | Assign only disjoint source or review work; concurrency cannot create authority. |
| A cheaper or faster fallback is proposed | Prove the governance, quality and reliability floors first. |
| Canonical wording is unavailable | Record the exact source gap; never replace it with plausible prose. |
| A conditional check implementation is disabled | Distinguish unavailability from an absent source predicate; only the latter supports not-applicable. |
| An oracle differs from candidate behavior | Preserve the independent expectation. A mismatch against resolved, applicable, frozen expectations is FAIL. An unresolved mapping or unavailable required evidence is BLOCKED. Never fit the oracle to the candidate. |
| A producer supplies its expected output | Treat it as an interface proposal, not independent certification. |
| Real payment, network, subprocess or production-credential effects look useful | Keep them out of the default path until compatible contracts, ownership and authority exist. |

## Worker delivery and adoption

Workers receive this file through repository discovery or an explicit task reference. Pull requests name the affected articles and cautions and the exact evidence. Formatting-only changes need no full matrix. Substantive architectural conflicts remain operator decision points. No worker may self-certify independent qualification or alter a recorded contract.
