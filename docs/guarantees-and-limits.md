# What the stack guarantees and what it does not

This is the one stack-level statement of scope. Other pages in this repository and in the component repositories link here instead of restating it. If another page reads more strongly than this one, this page governs and the other page should be corrected.

The stack is a **bounded synthetic local reference**. Nothing here is a production certification, a release declaration or an authorization to connect a real destination. The contract label on every ODES contract stays `0.1.0-draft`.

## 1. Supported platform

**Linux only.** No Windows, macOS or Android support, testing or CI is claimed. See [platform support](platform-support.md) for the reasons and the retained unsupported-platform evidence.

## 2. Certification is not truth

A qualification result, a certification record or a verifier pass states that named checks ran against named bytes in a named scope and had a named outcome. It does not state that:

- the recorded decision was the correct one (a verification pass establishes integrity and internal consistency of a record, not the merits of what it records);
- the destination holds what the record says it holds;
- the host, the key custody or the deployment around the reference is sound;
- anything outside the stated scope behaves as inside it.

Results are kept with their scope, including failed and inconclusive ones. The V1 validation outcome (reduced-scope pass, full-catalog fail, no release declared) is recorded in the [release closeout control panel](workstreams/release-closeout-control-panel.md). At the time of writing no review by a party outside the authoring organisation has been recorded; one party authored, inspected and certifies. Review is invited.

## 3. The prevention claim and its four assumptions

The claim for the bounded reference is conditional: **an effect that completes satisfied the authority check, provided four assumptions hold.** Each assumption below is mapped to the evidence that exists and to the scope in which it holds. The mapping was read against the component code at current main; the D09 cases are in the qualification repository and were not re-run for this page.

| Assumption | Evidence | Scope limit |
|---|---|---|
| **(i) Every effect passes an installed boundary** | Scenario D09 (`suites/v1-scenarios/test_scn_d09.py` in [cognous-stack-qualification](https://github.com/cogno-us/cognous-stack-qualification/tree/main/suites/v1-scenarios)) declares eleven routes, exercises eight, and discovers the call sites that can mutate a destination statically; an undeclared call site fails the case. Direct commit, direct executor and direct adapter calls on a profile-activated destination are refused and leave it unchanged. | Supported routes of the bounded reference only. Not exercised: the OpenShell destination, the legacy CLI (checked statically to reference no route), and direct SQL by a holder of the database file (out of model). A destination database with no profile activated has no gate: a direct commit on it writes the effect. A process that holds a credential for the destination is outside the boundary (section 4). |
| **(ii) Check and release are serialised** | On the effective-grant destination (route A with the runtime-authority profile) the grant check runs inside the destination's `BEGIN IMMEDIATE` transaction (`engine/effective_grant.py`, called from `DurableRefundDestination.commit`). On the atomic claim destination (route B) claim, grant, budget and effect are checked and written in one `BEGIN IMMEDIATE` transaction with trusted time taken after the lock (`execute_claim_atomic`). Revocation placed before execution, at the commit boundary and inside the transaction is covered by D09. | A local SQLite store on one host. Holds only where one of those two profiles is in use. The selected default (C0) revalidates before dispatch and is **not** atomic with the destination commit; its check-to-commit race is documented in [release status](release-status.md). No distributed or external destination is covered (no C2/C3 claim). |
| **(iii) A mandatory synchronous gate rejects violating candidates** | The Control Plane decides before dispatch. On a profile-activated destination a commit without the matching precondition is refused (`effective_grant_precondition_required`; atomic profile: legacy write refused; intent profile: unbound dispatch refused). The exchange ingress without a trusted resolver and runtime-authority profile refuses (`trusted_resolver_required`). | The gate sits at the destination only for profile-activated databases (see (i)). The control plane has no producer for the bounded-deferral draft; freshness clocks are an opt-in profile. The decision is only as current as the inputs the host supplies. |
| **(iv) Failure blocks release** | Unreadable, missing or unknown state refuses or holds rather than authorizes (for example an unavailable effective-grant row, permission set or effect budget refuses). An error after a durable commit is reported as `unknown`, never as denied or failed, and the committed effect is left in place. | Only the failure paths exercised by the tests are covered. A failure after commit cannot reverse the effect; no reversal is offered or claimed. Contract drafts for deferral and freshness have partial producer coverage. |

## 4. Credentials and routes the check does not see

The check only governs effects routed through it. A process that holds a credential for the destination, directly or by inheritance (environment, open handles, ambient cloud or payment roles), can act without the check, and the stack does not detect that. The holder inventory records what the host declares, not what exists; for a holder with no witnessed refusal it reports `coverage_unknown`, and an unlisted holder is invisible. Deployments are responsible for credential separation; see [deployment responsibilities](v1-deployment-responsibilities.md).

## 5. What a check or a signature does and does not show

- **The journal-only validator does not confirm destination content.** The control-plane journal validator and Replay's journal import check the shape and internal consistency of a run record. Neither compares an observation's target, amount, unit or payload to anything outside the record, so neither confirms what happened at the destination.
- **A signature proves authorship, not completeness.** A valid signature shows that the configured key signed those bytes. It does not show that no rows were omitted, that the signer is who the name says (the signer is an asserted name, reported as `issuer_signature_only`), or that the content is true. Single-row deletions that leave the rest of a record consistent are a documented limit of the verifier (see its tiers page); a journal completeness member is deferred to the first contract freeze.
- **An approval record proves the approver's identity and commitment.** It does not prove what the approver was shown. A step-up profile binding a digest of the displayed content to the dispatched operation is deferred.
- **The payload policy checks field names, not values.** A payload field that selects a recipient, resource or amount must be expressed as the target or the amount, or declared constrained; an in-scope-by-name payload with a wrong value is not caught by manifest validation.
- **A shared-key MAC is not a signature by a distinct signer.** Where the assurance runtime holds every principal's key, separation of duties rests on host key custody.
- **A blocked count is not a denial count.** The runtime-authority reason registry classifies reasons only as typed or recomputable. It does not separate an unavailable input from a withheld permission, and some codes cover both.

## 6. Known limits

Each limit is stated as it is, pinned by a test or a document where one exists, and not hidden behind a pass. Limits marked *deferred* are left to the first contract freeze, which has not happened.

| Area | Limit | Where it is pinned |
|---|---|---|
| Delegation | A grant that names a parent is refused (`delegation_profile_unsupported`). No ancestor walk or shared ancestor budget exists. Child caps are counted per grant id with no parent total. | Control Plane `tests/test_known_limits.py`; runtime budget known-limit tests |
| Decision age | The age of an authorized decision is not consulted; a decision whose inputs still match executes. Claim issue time is not consulted at execution. | Control Plane and runtime known-limit tests |
| Holds | A hold has no binding, and a later decision carries no link to it. Deferred. | Control Plane known-limit test |
| Operation identity | A second effect under the same operation id gets one refusal whether it is a replay or different content. | Control Plane and runtime known-limit tests |
| Operation ledger retention | The ledger has no retention rule. If its rows are removed from a run record, a revision-2 decision authorizes where it should hold; the destination still refuses the second effect and the verifier rejects the pruned record. A retention rule is deferred. | Stated here; no test pins it yet |
| Amounts | `10` and `10.0` inside a payload are different canonical bytes. A `minimum_count` of 0 is vacuous. | Control Plane known-limit tests |
| Tenants | Evidence status is bound to institution, domain, obligation and source, not tenant. Use one engine database per tenant, or tenant-unique obligation ids. Scoping the key by tenant is deferred. | [release status](release-status.md), step 3; runtime `tests/test_evidence_tenant_known_limit.py` |
| Records | Single-row deletions that leave the record consistent are not always detected; witness digests cover run-record lists only. | Verifier tiers page and `tests/test_deletion_limits.py`; ODES decision 30 |
| Contracts | One `0.1.0-draft` label can name more than one content; vendored copies are reconciled at the first freeze. Some manifest schema rules differ from the Python validator and are listed. | ODES decision 36; Action Manifest parity test |
| Time | Deadlines are inclusive and windows half-open, with three conformance mismatches remaining. | ODES time semantics, decision 35 |
| Process | Hash-pinned dependencies, pinned workflow actions, image digests and a software bill of materials are deferred to the first freeze. No release, tag or contract freeze has been declared. | [release status](release-status.md) |

## 6a. Merged after the selected revisions

The changes below are merged in the owning repositories after the revisions pinned in the [component lock](../component-lock.json). They are labelled **merged**, not **selected**: the lock decides what is selected, and none of these changes is part of the selected set until the lock moves. Each row states the change and, as a **known limit**, what it does not cover. The wording follows the decisions register and the tests merged with each change.

<!-- pin-round: rows move from merged to selected only when the lock moves to a revision that contains them; recheck each row then -->

| Area | Label | What is merged | Known limit that stays visible |
|---|---|---|---|
| Declared action binding (Control Plane) | merged | A manifest that declares one tool name more than once is refused at decision time with the existing reason `adapter_mismatch` (checked across the whole manifest). A manifest that declares one action id more than once binds no action, and the decision is refused with the existing reason `unknown_action`. | The manifest validator is not run at decision time. No new reason code was added; a distinct code is a contract change left to the first freeze. |
| Lifecycle results (ODES) | merged | The execution-attempt-lifecycle validator refuses a result with status `failed`, `partial`, `unknown`, `executed` or `reconciled` whose `attempt_id` is null or names no registered attempt, with the typed code `result_attempt_unresolved` (the same code the verifier uses). | The rule applies when an `attempts` member is present. A result with no `attempts` member is covered neither by this rule nor by the verifier's. |
| Captured-input binding (Verifier) | merged | A decision binding's `requirement_id` must equal the `input_id` of every successful conflict read, with the existing code `binding_member_mismatch`. Decisions with no successful conflict read are not compared. | `effective_max_effects` is not checked against captured inputs: no captured input states the ceiling, and the retained inputs do not hold requirement or permission bodies. A producer change would be needed. |
| Inbound endpoint binding (Governed Exchange) | merged | Inbound resolution requires the full configured endpoint and identity binding and rejects a route that is not local. An unreferenced twin check was removed and regression tests were added. | The transport has no setting for its own endpoint: any route marked local is accepted. This matches the documented trusted-configuration scope of the reference. |

## 7. Retained evidence is untouched

Retained evidence, result files, migration records and historical packets are kept byte for byte, because later records commit to their bytes. Corrections appear as new notes beside them, for example [the note on the 20261015 freeze directory](releases/NOTE-security-review-freeze-20261015.md). A newer statement here supersedes an older one in retained material only for the purpose of reading it; it does not rewrite it.
