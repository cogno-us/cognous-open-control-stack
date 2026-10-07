# Accepted authority effect qualification

## Objective

Qualify the accepted Control Plane and Execution Runtime merge revisions without advancing the default hub component lock. This is the first integration closeout from the consolidated engineering register, separate from documentation PR #20.

Hub starting revision: `643a1425060a4e50567e0d7789ae1652194ad00c`.

- Control Plane: `d3dadee70bd319812b207389ab1e0f6efe511916` (merged PR #12).
- Execution Runtime: `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` (merged PR #25).
- Supporting Manifest, GAX and Replay fixture revisions remain those in the existing Worker 21 runner.

## Bounded batches

The dedicated Linux workflow separates Control Plane (7), profile compatibility (4), executor (24), integration repetition 1 (19) and integration repetition 2 (19) into five independently visible jobs. Each test subprocess has a two-minute timeout; dependency and checkout operations have five-minute limits, and each job has a twelve-minute outer limit. On POSIX timeout the subprocess group is terminated and output retained.

No macOS or Windows qualification is claimed. No Swift, TypeScript or mobile application test is introduced. Existing test assertions and historical source revisions remain available; `--accepted-merges` selects the new merge revisions explicitly. `--batch` allows one bounded batch, and the default runs all five sequentially.

Missing JUnit, unexpected counts, skipped required tests and nonzero commands cannot satisfy a batch gate. Summary schema 2.0 records the selected revisions, batch and executing hub revision rather than labeling accepted merges as proposed revisions.

## Default adoption boundary

The selected Replay persistence tests assert Control Plane `248d899634d9db3518e831bc7ab568a48733f825` and executor `177354e959cc78c59c1a776f018cfbfbf28c927b`. Consequently this atomic-profile run cannot establish downstream consumer compatibility or justify a default lock bump. Replay, Evidence Pack, ODES and GAX producer acceptance need a separately reviewed compatibility generation before default adoption.

Refund-intent ownership and authority/effect profiles remain mutually exclusive per database. Qualification does not compose them or silently adopt the non-authorizing Decision Input Commitment sidecar into execution authority.

## Validation

Local qualification-gate tests: 4 passed. Workflow YAML parsed. Accepted-merge runtime qualification is pending execution at this checkpoint.

## Limits

Cooperating same-host authority writers, trusted source handoff and authoritative SQLite destination only. No distributed authorization, external-destination atomicity, hostile-host protection, universal mediation, production identity or key custody, production readiness or EBL-Core conformance claim.
