# Changelog

## 2026-10-22 review scan 4 hardening (tools and tests only; non-authorizing, HOLD unchanged)

- Collateral evidence snapshot checker and schema: `additionalProperties: false`, required members, types and patterns now apply to every nested object (component lock, evidence generation, documents, historical snapshots, separate profile evidence, assurance levels). The C1 reviewed-source shas, the snapshot version, document scopes and document versions (against each document's inline identity) are pinned, `generated_at` must be a UTC timestamp inside the plausible window, the separate profile inventory is exact, and a conservative boundary-wording check refuses any production, certification, readiness, authorization, settlement or guarantee term that is not inside a negated clause. The current snapshot and `component-lock.json` are unchanged.
- Candidate archive verifier: the selection file is read through the strict bounded loader; duplicate members, NaN/Infinity and non-object roots are refused with typed failures.
- Selected documentation check: revision-specific links on the three current entry pages are matched in the http, www, archive, raw, codeload, pull-commits, compare and `.git` forms and under the previous repository names listed in `docs/repository-renames.md`. Scope is unchanged: only those three pages.
- Preview entry check: its docstring now states that it verifies disclaimer presence, not overclaim absence.

## 2026-10-22 review scan 3 hardening (tools and tests only; non-authorizing, HOLD unchanged)

- Collateral evidence snapshot checker: loads through the bounded loader (duplicate members refused), applies the snapshot schema (declared members only), requires exact integer counts, and cross-checks lock-derived claims against `component-lock.json`.
- Publication inventory verifier: refuses any package directory that is not an ancestor of a listed file, and an unreadable directory fails closed.
- SQLite staging restore: reads the snapshot manifest through the bounded loader, so duplicate members and non-object manifests are refused instead of last-wins.
- Selected documentation check: every revision-specific link to a locked component on the three current entry surfaces (any hex case, full or abbreviated) must match the lock; the docs agreed with the lock before the change.

## Reference candidate workstream

- Added exact component lock and accepted/deferred revision ledger.
- Added reproducible two-run acceptance harness and GitHub Actions evidence upload.
- Added governed transport, GAX/IMX, Control Plane, Moltbot Safe, Replay, Governance Evidence Pack, ODES, BitRep and Index checks.
- Added representative GAX-to-Replay-to-Evidence-Pack/ODES/IMX artifact generation.
- Added separate mocked OpenShell qualification and explicit unexecuted live gate.
- Added machine-readable acceptance and residual-risk registers.
- Replaced the four-component hub presentation with the current responsibility map, trust boundaries, compatibility matrix and adoption guidance.
- Recorded the Moltbot producer-revision gap and GAX test-helper dependency without altering adjacent repositories.
- Excluded unaccepted cogno-us/alvorada PR #2.
