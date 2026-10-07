# Batch 4C — qualification index

New bounded late-commit extension: [checkpoint](../workstreams/late-commit-checkpoint.md).
Two same-process cases passed locally; recovery-authority, process boundaries and
cancellation/finality remain unqualified.

Current bounded integration: [Worker 14c checkpoint](../workstreams/batch4c-integration-checkpoint.md)
and [executed evidence](../../examples/batch4c-accepted/scenario-results.json).
Alvorada is now pinned to its accepted merge; remaining research scenarios are pending.

## Historical checkpoint 1

The following preserves the original failures and source mapping. It is not current qualification.

**BLOCKED: 3 required safety invariants fail. Draft for Governor review.**
Starting main: `5df06d5fb4710bafa36e49569efc7bb32f40ac6d`.
All dependency pins remain unchanged. This pass executes Part A cases 1–2;
cases 3–5 remain unexecuted. No claim that Batch 4C is complete.

## Evidence and reproduction

One entry point: this page. [Machine-readable executed evidence](../../examples/batch4c/results.json)
contains exact pins, setup/fault points, original proposals, approvals, decisions,
envelopes, effect/attempt identities, observations, SQLite destination rows before
and after, classifications and limitations for all seven scenarios.
[JUnit](../../examples/batch4c/research_qualification.xml) and
[raw output](../../examples/batch4c/pytest.log) preserve the failing assertions.

With the unchanged locked component checkouts in `.reference-work/` and Python
requirements installed (as established by `tools/reference_release.py`):

```sh
python tools/research_qualification.py --out results/batch4c-new-run
```

Use an empty output directory. The command returns **1**, with **4 passed,
3 failed, 0 errors, 0 skipped**. It writes evidence before asserting. No xfail,
skip, mock execution success, alternate authorizer or local recovery algorithm
is used. The exact public `BoundedAuthorizationWorkflow.reconcile` consumes the
injected observation. Real effects use `PinnedControlPlaneExecutor` and
`DurableRefundDestination`. This does not exercise transport or remote authority.

The release runner now includes `research_qualification` in each repetition and
retains detailed JSON under `run-N/research-qualification/`. The acceptance matrix
has 23 required entries: the existing 21 plus one required characterization
reproduction and one required safety scenario covering six evidence cases.
Characterizations render as `characterized`, with `safety_outcome=not_established`.
A failed required invariant or characterization reproduction still blocks release.

## Executed outcomes

| Scenario ID suffix | Classification | Actual result | Destination effects before → after |
|---|---|---|---|
| `replanned-equivalent-intent` | Characterization confirmed; not a safety pass | Two separately approved proposals create distinct effects; same-ID replay creates no third effect | 0 → 2 |
| `absence-unavailable` | Required invariant passed | Observation raises OSError; no reconciliation permission produced | 1 → 1 |
| `absence-unknown` | Required invariant passed | `hold` | 1 → 1 |
| `absence-stale` | **Required invariant failed** | Absence dated 2000 is promoted to `safe_to_retry` | 1 → 1 |
| `absence-incomplete` | **Required invariant failed** | Absence with empty observation time is promoted to `safe_to_retry` | 1 → 1 |
| `absence-wrong_operation` | **Required invariant failed** | Observation naming a different effect is promoted to `safe_to_retry` | 1 → 1 |
| `absence-authoritative_absence` | Required local observation invariant passed | Actual SQLite lookup yields absence and `safe_to_retry`; no execution follows | 0 → 0 |

All IDs above begin `4c-`. A retry conclusion is not itself a new dispatch.
The three failures prove an unsafe reconciliation conclusion at the trusted
adapter-result boundary; they do **not** demonstrate three duplicate payments
or a bypass of effect-time authorization. The actual local adapter checks bound
operation content before returning its genuine applied observation. Faults are
injected only into its observation return, not its execution implementation.
Injected objects also pass the accepted `EffectObservation` model validation.

Case 1 raises the synthetic manifest, requirement, grant and local policy limits
to 3, preserves required human-review declarations, and supplies a fresh approval
bound to each proposal's commitment. Both decisions are authorized. Correlation
and run IDs differ; actor, target, amount, unit and refund payload are identical.
A third permitted slot remains unused, so budget exhaustion cannot conceal the
same-ID replay result. The stated equivalence is fixture-defined business intent,
not a claim that the system inferred semantic equivalence.

Case 2 fixes the observation/reconciliation clock to 2026-08-08T01:00:00Z.
Except for actual absence, a real effect already exists before the observation
fault. Source, time and scope of each injected/genuine observation are retained.
The observation model lacks authenticated source, coverage and in-flight finality
fields. Empty time is one concrete incomplete-evidence reproduction; exhaustive
missing-field, coverage and source-competence qualification is not claimed.
Actual local absence means no matching effect row at the SQLite read boundary.
It does not exclude an earlier in-flight request committing later. No cancellation,
termination or rollback guarantee follows from this result.

## Source register and derived requirements

The supplied files were read locally. Original documents are not republished.
[Source hashes and locators](../../scenarios/research-sources.json) identify them.

- **JCEE Labs / Jonathan Chadbourne, _When a Timeout Is Not a Failure: Authority,
  Evidence, and Recovery in Consequential AI Execution_, Technical Note 001,
  Public Release v0.1.1, 6 October 2026.** Sections 2–5, pp. 1–2 separate occurrence,
  retry admissibility and authority; section 5 limits idempotency to its key and
  scope; section 6, p. 3 requires competent, current premises. These motivate cases
  1–2. Sections 3–5 motivate pending late-commit and recovery-authority cases.
  Sections 6–9, pp. 3–4 report bounded internal campaigns; their numerical results
  are **source-reported, not independently reproduced by Cognous**. This work
  neither implements JCEE's private mechanisms nor reproduces its cross-host tests.
- **_Cognous Consolidated Engineering Recommendations_, prepared 5 October 2026,
  no explicit version identifier.** “Shared implementation requirements”, sections
  05 (Agent Control Plane), 06 (Moltbot Safe), and 21 (stack consolidation), including
  “Bounded workflow acceptance” and “Integration test program”, motivate actual
  destination assertions and explicit unknown-delivery/recovery limits. Its old
  repository observations are historical review findings, not assertions about
  the current accepted baseline. Proprietary or unrelated recommendations are
  not carried into this public qualification.
- **OECD, _Agentic AI in organisations: Early insights from practitioner interviews_,
  OECD Artificial Intelligence Papers No. 65, ©2026.** Page citations below use
  printed page numbers (PDF page = printed page + 1). Sections 2.1–2.2, pp. 8–10:
  25 organisational interviews; qualitative, nonrepresentative perspectives,
  without quantitative performance validation or independently evaluated impacts.
  No more precise publication date is asserted from this attachment.

## OECD finding → mechanism → evidence → gap

This is a source-grounded engineering mapping, not OECD endorsement or evidence
of operational effectiveness. Inherited Batch 4B evidence means the executed
results recorded in the accepted [checkpoint](../workstreams/interface-cleanup-checkpoint.md),
not a new 4C execution of those suites.

| Report finding / locator | Enterprise problem and responsible component | Implemented mechanism and exact executed evidence | Remaining gap and action |
|---|---|---|---|
| Extended workflows need visibility and checkpoints; §4.1 pp. 19–20; §4.2 p. 20 | Oversight across multi-step/multi-agent activity; Manifest, Control Plane, transport | Bounded declarations and current authorization; inherited 4B `test_real_transported_gate_passes`; new `4c-replanned-equivalent-intent` proves identity-level limits | No fleet oversight efficacy demonstrated. Add workflow/business-operation identity and delegation scope qualification; evaluate checkpoint placement with humans. |
| Cross-boundary traceability and responsibility remain difficult; §4.1 p. 19; §4.2 p. 23 | Accountability; Replay, Evidence Pack, ODES, Alvorada | Inherited 4B `test_substituted_identities_fail` and `test_actual_artifact_commitment_required`; new records retain proposal/approval/effect/attempt chains | Imported records are producer evidence, not accountable ownership or independent verification. Preserve successor `relevant_decisions: [null]`; require a separately reviewed producer attribution contract. |
| Calibrated review, clarification and escalation; §4.2 p. 20 | Intervention; Control Plane and institutional procedures | New `4c-absence-unknown` holds without an effect; unavailable observation raises rather than fabricating permission | Stale/incomplete/wrong-effect reconciliation fails. Repair upstream evidence acceptance first; then evaluate notification receipt, response time, reviewer comprehension and actual intervention success. An error/hold is not proof a human intervened. |
| Model metrics omit long action sequences; §4.1 p. 19; §4.2 pp. 20–21 | System-level evaluation; hub qualification | Seven new scenarios: four test passes and three safety failures; characterization explicitly separated from safety | Cases 3–5 and conventional-control comparisons remain unexecuted. Measure false allows/blocks, duplicate effects, unresolved duration, latency and corrective efficacy. |
| Prompt injection, compromised tools, identity/permission risks; §4.1 pp. 18–19; §4.2 pp. 21–22 | Operational security; executor, Control Plane, BitRep, deployment operator | Inherited 4B OpenShell mock suite: 120 passed; new actual SQLite effects are operation-bound | No new prompt-injection, production identity or live confinement qualification. Keep authenticated resolvers, scoped credentials, live sandbox and bypass testing in a separate deployment workstream. |
| Oversight/efficiency tension, automation bias and domain expertise; §4.1 p. 19; §4.2 pp. 20–21 | Adoption and human-review burden; institutional owners and Evidence Pack review process | Synthetic approvals are correctly proposal-bound in case 1; **no human study executed** | Measure workload, missed interventions, over-reliance, task completion and retained expertise against conventional controls. Do not infer oversight efficacy from approval records or synthetic success. |

## Prioritized follow-up

1. **Reference prerequisite / Control Plane:** reject stale, incomplete and mismatched
   observation scope before any retry-safe conclusion; define source competence,
   evaluation time, coverage and finality. Preserve the three failing reproductions.
   Repair requires a separate upstream review and Governor-accepted pin; this PR
   changes no component implementation or dependency pin.
2. **Reference contract / Manifest + Control Plane + destination owners:** propose an
   explicit business-operation key, scoped to institution, principal, action and
   destination, with issuer, equivalence policy, payload-conflict rules, retention
   and recovery lifecycle. Carry it across replans without silently replacing
   current effect IDs. Destination atomic enforcement must be separately specified;
   such a key never creates authority. Test both equivalent and legitimately distinct
   repeated intents before accepting the contract.
3. **Next bounded 4C pass:** deterministic late-commit barriers, recovery-time authority
   variants, and separate-process local-store tests. Retain cancellation request,
   confirmed termination and rollback as different claims. Revisit this mapping with
   the newly executed evidence, then run full release qualification once ready.
4. **Production workstream:** authenticated institutional/observation sources, live
   confinement and remote transaction/finality/budget semantics. No same-host SQLite
   result can close these gaps.
5. **Organisational evaluation:** comparative intervention and human-review burden
   study with named roles and representative tasks. This cannot be completed by
   additional synthetic evidence export alone.

Worker 15 findings were not supplied to this pass; work did not wait for them.
