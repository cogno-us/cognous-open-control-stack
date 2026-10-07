# Batch 4C — bounded late-commit qualification

Starting accepted hub merge: `8a591d5e61627a85c948d39e59c870526aab2639`.
Work branch: `worker14c/late-commit-qualification`. All dependency pins unchanged.
Repository instructions and the existing checkpoint/scenario plan were inspected.

## Executed scope

Two actual transported cases retain the original frozen destination request in a
same-process worker after a synthetic caller timeout. An event barrier prevents
its real SQLite commit until after two public `resume_original` calls observe
fresh absence. No timing sleeps, replacement authorizer or reconciliation algorithm
is introduced. The hub imports public transport/runtime interfaces and synthetic
fixtures; no executor test helper is imported into supported runtime code.

Both absence recoveries deny dispatch and preserve the original pending effect,
unresolved delivery and false retry eligibility. Exactly one destination commit
call occurs. Releasing the barrier commits that original effect, with the original
target, amount, unit, grant and payload. Applied recovery resolves delivery; partial
recovery preserves pending delivery. The earlier unknown acknowledgement remains
visible. Redelivery preserves the original retained artifacts before and after
completion, and Replay commitments are recomputed.

Cancellation is not requested, termination is not confirmed, and rollback is not
performed. The test demonstrates that an original request *can* commit after
observed absence; it does not establish absence finality or cancellation safety.
The worker thread is not separate-process or distributed qualification.

## Actual local validation

- Existing research suite plus two new cases: **9 passed per repetition**, two
  isolated temporary-store executions; zero failures/errors/skips.
- Existing hub release regressions: **74 passed**, zero failures/errors/skips.
- New required matrix reference resolves to both parameterized cases in both runs.
- Normalized late-commit outcomes match across repetitions.
- All component checkout SHAs match the unchanged accepted lock.

[Summary](../../examples/batch4c-late-commit/qualification-summary.json) ·
[Artifact hashes](../../examples/batch4c-late-commit/artifact-index.json) ·
[Source hashes](../../examples/batch4c-late-commit/source-hashes.json).
Per-run raw logs, JUnit and scenario evidence include effect/decision identities,
original/recovery artifacts, destination rows and dispatch counts. Evidence is
written before lifecycle assertions; failures remain failures, never xfail.

Reproduce focused qualification with:
`python tools/research_qualification.py --out results/late-commit-new-run`.
Use an empty output directory and the accepted `.reference-work` checkouts.
The existing full release runner automatically executes the added tests in both
repetitions. It now has 25 required matrix entries. To keep this pass bounded,
full local release qualification was not repeated; its accepted baseline remains
historical evidence. New-head full CI is checked once after PR publication and
recorded in the PR handoff; no CI pass is inferred from the focused local run.

## Next bounded task

Governor review of this proposed qualification, then recovery under changed/revoked
authority as a separate batch. Keep separate-process boundaries, cancellation and
termination/finality, live OpenShell/image review, production authentication,
distributed guarantees and independent real-world verification pending.
Equivalent-intent deduplication remains a characterized limitation. No adjacent
repository edits, dependency updates, self-merge, deployment or private material.
