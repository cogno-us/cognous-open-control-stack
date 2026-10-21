# Changelog

## 2026-10-22 review scan 6 structural fixes (tools and tests only; non-authorizing, HOLD unchanged)

- Selected documentation check: links are decoded (HTML entities and percent-encoding, repeatedly and bounded) and a port or trailing dot after a GitHub host is dropped before revisions are compared with the lock, so `github.com:443`, `github.com.`, `&#x2F;`, `%2F`, `&amp;ref=` and percent-encoded revisions are judged like plain links. Revisions longer than 40 hex characters are now recognised and, never equal to a selected sha, refused.
- Candidate archive verifier: bz2 and xz archives are decoded as exactly one stream; any byte after the stream end (garbage, padding, a second stream) and truncation are refused. A raw pass over the tar headers refuses PAX keys other than `comment` (which must name the trusted revision) and `path`, GNU long-name/long-link/sparse and other vendor extensions, and non-zero padding after any data area; directory members are bound like file members (no setuid/setgid/sticky bits, owner rwx, not world-writable).
- Lifecycle inventory: an agent `state` that is not a string (list, dict, set, number, null) is refused with `ValueError('invalid/duplicate logical identity or lifecycle state')` instead of raising `TypeError`.
- New tests: `tests/test_scan6_selected_documentation_forms.py`, `tests/test_scan6_archive_structure.py`, `tests/test_scan6_lifecycle_state_types.py`. No pin, lock, profile, vendored contract or refreeze file changed.

## 2026-10-22 review scan 5 hardening (tools and tests only; non-authorizing, HOLD unchanged)

- Collateral evidence snapshot checker: boundary wording is folded before matching (NFKC, casefold, zero-width/format characters, variation selectors and combining marks dropped, common Cyrillic/Greek/small-capital lookalikes mapped to Latin, dash variants unified). A negation now has to scope the term (same comma/"or" piece with no finite verb between, an earlier verbless piece of the same noun list, or a trailing "remain unqualified/outside"); "but", "however", "yet", "and" and similar words end the scope, and "not only" and "no-op" are not negations. The term list gained approved for production/live/customers, secure, safe, audited, enterprise-grade, deployable, production-grade, certified, compliant, attested and ready for prod. The affirmative-claim subset is also scanned over the bodies of the three hashed collateral documents.
- Collateral evidence snapshot checker: the inline document identity must be exactly one `> **Evidence snapshot:**` line whose `document_id` and `version` fields equal the manifest row exactly (`version=2.0.10` no longer satisfies `2.0.1`) and which carries the accepted hub pin and lock digest as whole tokens.
- Candidate archive verifier: gzip archives open with `fileobj=` (they raised TypeError before), and any non-zero byte after the tar end-of-archive marker (for example a second appended tar) is refused.
- Selected documentation check: revision links abbreviated to 4-6 hex characters (when they mix digits and letters) and `?ref=<revision>` links are now compared with the lock. Not covered: `github.com:443`, percent-encoded paths, `pull/N/files/<sha>`, all-digit or all-letter 4-6 character abbreviations.

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
