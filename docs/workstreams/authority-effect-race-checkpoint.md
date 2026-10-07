# Worker 19 - authority/effect race qualification checkpoint

## Scope and selected baseline

This workstream qualifies the boundary between execution-time authorization and
the protected destination effect. It is qualification first, not a runtime repair.

Selected hub baseline:

`5a9ae5de4d445febe1105087a8b650e33f00eee3`

The branch was created from that exact `main` after the Worker 18 documentation
merge, so the concurrent public README work is preserved.

Selected accepted dependency pins from `component-lock.json`:

- Action Manifest: `46c950bed37fe3812000895430bc0312d29e37ce`
- Control Plane: `248d899634d9db3518e831bc7ab568a48733f825`
- Moltbot Safe / executor: `177354e959cc78c59c1a776f018cfbfbf28c927b`
- GAX/IMX transport: `9984d9011568ccdf3d562fa9760ad41368947b34`
- Replay: `043830b56595cecddfa65c064afd1c0b95e64792`

No dependency pin is changed by this branch.

Moltbot Safe PR #14 is not consumed. At baseline selection it remained outside
accepted `main`; this batch therefore keeps the selected executor revision
`177354e9...` even if PR #14 changes or merges later.

## Repository instructions and prior evidence reviewed

The hub `CONTRIBUTING.md` and `GOVERNANCE.md` were reviewed. This batch owns
new qualification files only and makes no runtime, lock, shared acceptance,
release-runner, or existing-evidence edits.

Prior checkpoints reviewed:

- `docs/workstreams/process-boundary-checkpoint.md`
- `docs/workstreams/recovery-authority-checkpoint.md`

The process-boundary work explicitly did not qualify recovery under changed
authority. The recovery-authority work qualifies authority changes after an
unknown original outcome and before recovery/resume. Neither establishes the
ordering when authority changes after execution-time validation but before the
original destination commits.

## Research input and claim boundary

Research input:

*From Intent to Execution Grant: An Execution-Boundary Conformance Profile for
High-Risk AI Actions*, especially sections 3.3.7, 3.3.8, 4.7 and 6.4.

The paper is treated as a proposed external conformance profile, not an adopted
Cognous requirement.

Its relevant proposed rule is stronger than an ordinary last-moment recheck:
validation, single-use lifecycle consumption and the protected effect share one
logical linearization point with respect to decision-relevant state. The paper
also states that a separate recheck followed by an interleavable effect is not an
equivalent realization.

This workstream therefore distinguishes:

1. behavior supported by the current accepted Cognous contract;
2. behavior not yet qualified by that contract;
3. any reproduced violation of an existing Cognous guarantee; and
4. a stronger external property proposed by the paper.

A later effect timestamp alone is not treated as proof of a linearizability
violation. The harness records invocation/completion order using barriers and
events.

## Verified implementation boundary

At accepted Control Plane `248d899...`,
`BoundedAuthorizationWorkflow.execute()`:

1. reloads and validates the persisted decision;
2. resolves current authorization inputs again;
3. rejects changed authorization-critical inputs;
4. reconciles current destination state;
5. persists an attempted Control Plane effect record;
6. invokes `destination.apply()`.

The implementation then explicitly performs no additional authority-context or
grant reread after validation.

At accepted Moltbot Safe `177354e...`, the destination adapter:

1. checks exact operation/envelope binding;
2. creates a durable destination attempt;
3. observes the bound effect identity;
4. invokes the real SQLite `DurableRefundDestination.commit()`.

The SQLite commit serializes effect-ID and cumulative grant-effect checks with
`BEGIN IMMEDIATE`, but it does not include current Control Plane
authority/policy/evidence state in the same transaction.

## Deterministic qualification design

The test pauses the real Moltbot Safe destination immediately before its real
SQLite effect commit. No timing sleeps are used.

For every scenario:

1. create a valid synthetic authorization and exact execution envelope;
2. invoke the accepted `PinnedControlPlaneExecutor`;
3. wait until the destination's real `commit()` is entered;
4. confirm no effect row exists yet;
5. change exactly one decision-relevant condition, or leave it unchanged for the
   positive control;
6. perform a separate, effect-free Control Plane assessment to prove what current
   authorization says after the change;
7. record the resolver-call count while the original execution remains blocked;
8. release the original destination commit;
9. record the execution result, destination attempts, authoritative effect rows,
   and ordered event log;
10. confirm whether the original in-flight execution reread authority after the
    mutation.

The mutation matrix is:

- grant revocation;
- approval revocation;
- policy-version change;
- required authorization evidence becoming non-current;
- grant expiry using controlled evaluation time;
- required-evidence expiry using controlled evaluation time;
- unchanged-authority positive control.

Expiry scenarios refresh unrelated synthetic status timestamps where needed so
the assessment isolates the intended temporal predicate.

## Qualification oracle

For the six changed-condition scenarios, the current accepted contract does not
state an atomic authority/effect linearization guarantee. Therefore the expected
classification is:

`unqualified boundary characterized`

If the already validated in-flight dispatch still commits after the mutation,
the evidence also records:

`stronger_proposed_guarantee.status = not_met`

It does **not** record:

`existing_contract_violation_reproduced = true`

unless a separate adopted Cognous guarantee is identified and actually violated.

For the unchanged-authority control, expected classification is:

`existing contract supported`

The test gate requires truthful retained evidence. It does not force the stronger
external property green.

## Files owned by Worker 19

- `tests/test_authority_effect_race_qualification.py`
- `tools/authority_effect_race_qualification.py`
- `scenarios/authority-effect-race-matrix.json`
- `.github/workflows/authority-effect-race-qualification.yml`
- `examples/authority-effect-race/`
- `docs/workstreams/authority-effect-race-checkpoint.md`

No runtime code, dependency pins, PR #14 files, existing evidence, or shared
release gates are modified.

## Exact command

```bash
python tools/authority_effect_race_qualification.py run \
  --results-dir results/authority-effect-race
```

The runner:

- clones the exact accepted pins above;
- verifies every checked-out HEAD;
- runs the seven scenarios twice;
- retains JUnit, pytest logs, per-scenario JSON, per-run matrix gates and a
  summary;
- exits nonzero for missing/malformed evidence, failed deterministic assertions,
  wrong pins, or a failed pytest run.

The dedicated GitHub Actions workflow uploads the complete
`authority-effect-race-qualification` artifact even on failure.

## Executed results

Local exact-pin execution remained unavailable because the local execution
container could not resolve `github.com`. The dedicated PR workflow therefore
provided the executed qualification evidence.

GitHub Actions run `37634121102` completed successfully at branch head
`d152be494580e625be01d91f22f36c3d25c0a291`.

Both isolated repetitions reported:

- 7 tests;
- 7 passed;
- 0 failures;
- 0 errors;
- 0 skipped;
- all matrix gates passed.

Across the two repetitions, the retained evidence classified:

- 2 unchanged-authority controls as `existing contract supported`;
- 12 changed-condition observations as `unqualified boundary characterized`;
- 12/12 changed-condition observations as `stronger_proposed_guarantee.status = not_met`;
- 0 existing Cognous contract violations reproduced.

For every changed-condition observation, the sequence was deterministic: the
accepted execution reached the real Moltbot Safe destination commit boundary
with no effect row yet present; a separate current Control Plane assessment then
returned `hold` for the intended revocation, approval, policy, evidence, or
validity change; the original in-flight execution performed no additional
authority resolver read after that mutation; and the original bound SQLite
effect committed as `applied`.

The uploaded `authority-effect-race-qualification` artifact is 97,476 bytes
with digest
`sha256:9c5f24455f396ed39a1830e7f8ae3beb2b27b4be62e1a73542d7f68806fe6ced`.
It retains both JUnit files, pytest logs, matrix-gate records and all 14
per-scenario evidence records.

This result establishes the tested gap at the selected synthetic single-host
pins. It does not retroactively make the paper's proposed atomic ordering rule an
adopted Cognous requirement, and it does not establish EBL-Core conformance.

## Bounded repair recommendation

Do not add another uncoordinated authority recheck and call the race solved.

First define the desired ordering contract and authoritative state. If Cognous
adopts a guarantee equivalent to the paper's check-effect linearization rule, the
smallest sound repair class is to couple current-condition validation to protected
effect commitment using one mechanism with equivalent atomic semantics, for
example:

- a transactional authority/effect state transition;
- a version-conditional destination commit against an authoritative authority
  epoch/version;
- or a consumable execution claim/lease whose acquisition and protected effect
  share the required ordering.

The exact mechanism should be chosen only after the owner of the authoritative
lifecycle state and the intended linearization point are defined.

## Limits

This workstream does not establish:

- EBL-Core conformance;
- distributed or cross-host linearizability;
- production revocation enforcement;
- production institutional authentication;
- live OpenShell confinement;
- complete mediation or non-bypassability;
- external-world effect finality;
- cancellation or rollback semantics.
