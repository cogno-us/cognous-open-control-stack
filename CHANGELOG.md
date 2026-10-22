# Changelog

## 2026-10-22 hub docs aligned to the published engineering constitution (documentation only; non-authorizing, HOLD unchanged)

- The constitution repository now publishes the principles (EP1 to EP7), 23 constitutional articles (CA01 to CA23), orchestration practice and adoption rules. The hub's references were updated: the retired EP01 to EP18 range and the DOC-01 label are replaced by the constitution's own terms, and the orchestration and adoption documents are linked from `docs/README.md` and `docs/program-v0.2/`.
- The v0.2 register's Tier column is unchanged (Tier 1 routine, Tier 3 critical); the constitution's tier numbering is being reconciled by the owner.
- No exact constitution revision is adopted by this change; that remains a recorded act of the owner. No pin, lock, profile, contract or evidence record changed.
## 2026-10-22 engineering constitution links point at its document (documentation only; non-authorizing, HOLD unchanged)

- The hub links to the engineering constitution now go to the document in its own repository ([ENGINEERING_CONSTITUTION.md](https://github.com/cogno-us/cognous-engineering-constitution/blob/main/ENGINEERING_CONSTITUTION.md)) instead of the repository root, in `docs/README.md`, `docs/declarative-governance-registry.md` and `docs/program-v0.2/`. The constitution is repository-agnostic and is being updated there; the declarative governance registry design stays in the hub because it is specific to this stack. No pin, lock, profile or contract changed.

## 2026-10-22 program v0.2 planning placeholders (documentation only; non-authorizing, HOLD unchanged)

- Added [docs/program-v0.2/](docs/program-v0.2/README.md): a README, an engineering register (workstreams WS-A to WS-G: separation of orchestrator and qualification, registry instead of hard-coding, pin-round cost, known-issue burn-down, reporting, qualification hygiene, review release deferred) and a status page, all with placeholder owner, acceptance and evidence cells. Linked from the documentation index. Organized into four phases (P1 contract reconciliation and ownership freeze, P2 registry-backed governance, P3 orchestrator operational integration, P4 integrated qualification and v0.2 candidate) with a scope boundary: v0.2 is not multi-agent fleet deployment. Added workstream WS-H (six comparative-requirement rows, all P1, with proposed priorities for the P1 RFC to decide). Register source ids disambiguated against the known issues register. No release is planned; no pin, lock, profile, vendored contract or refreeze file changed; no tooling or tests added.

## 2026-10-22 review marker tags recorded in the release status (documentation only; non-authorizing, HOLD unchanged)

- [docs/release-status.md](docs/release-status.md) (version 1.1.3) gained a "Review marker tags" section recording the annotated tag `review-v0.1-g8-r10-20261022` in 14 repositories with the commit each points at. It states that the tag is a review marker, not a version or release, declares no contract freeze (contracts stay `0.1.0-draft`) and leaves publication and production on HOLD. [docs/guarantees-and-limits.md](docs/guarantees-and-limits.md) Process row no longer says that no tag exists.
- Snapshot bookkeeping: `collateral/evidence-snapshot.json` version 1.0.3 to 1.0.4 (`EXPECTED_SNAPSHOT_VERSION` in `tools/collateral_evidence_snapshot.py` moved with it), release-status row version 1.1.3 and `document_sha256` re-hashed. The component-lock digest, accepted hub pin, evidence generation and every other field are unchanged. `docs/releases/f7-acceptance-packet-20261016.md` is not edited (its bytes are pinned by retained freeze manifests).

## 2026-10-22 known issues register for the v0.1 public review release (documentation only; non-authorizing, HOLD unchanged)

- Added [docs/releases/v0.1-known-issues.md](docs/releases/v0.1-known-issues.md), linked from the documentation index. It lists, by how each became known (declared, observed in review, measured outside the controller), the limits and issues recorded in the repositories for candidate `g8-r10`, without ranking them. No code, pin, lock, profile, vendored contract, hashed collateral document or release status text changed, and nothing is claimed as qualified, certified or ready for production.

## 2026-10-22 fix wave 7 (tools and tests only; non-authorizing, HOLD unchanged)

- Candidate archive verifier: the raw header pass now refuses a nonzero size on any member that is not a regular file (links, devices, directories, fifos, and `\0` entries whose name ends in `/`), so a PAX or GNU header can no longer be hidden in a directory's "data" where tarfile would still parse it; unknown typeflags are refused; and the member start offsets seen by the raw pass must equal those yielded by tarfile (count included).
- Candidate archive verifier: gzip is decoded as exactly one member with nothing after it (a second member, a trailing zero run or an empty extra member is refused), consistent with bz2 and xz. No existing test relied on the old gzip behaviour.
- Selected documentation check: link text is normalised before matching (NFKC, backslash to slash, collapsed slashes, ideographic full stops, empty port, trailing dots, whitespace after a keyword segment, HTML/percent decoding to a fixpoint). Encoding deeper than 32 rounds is refused (`link_problems`; `verify` raises) rather than passed. Added the `/git/trees/`, `/statuses/`, `/find/` and `/pull/N/files/` revision forms.
- New tests: `tests/test_wave7_archive_hidden_headers.py`, `tests/test_wave7_selected_documentation_forms.py`. No pin, lock, profile, vendored contract or refreeze file changed.

## 2026-10-22 engineering constitution moved out of the hub (documentation only; non-authorizing, HOLD unchanged)

- Per owner instruction, the engineering constitution is now housed in its own repository, [cognous-engineering-constitution](https://github.com/cogno-us/cognous-engineering-constitution). The file `docs/engineering-constitution.md` is removed from the hub and every hub link to it now points to that repository; the hub keeps pointers and continues to cite its rules (EP01–EP18, DOC-01, review tiers). The new repository was empty when this change was made and the owner is seeding it. The full text as it stood before removal remains in hub git history at the #183 merge commit (`0df98ecfb064107f2eb72f44e3c80f2d89c061b0`). The declarative governance registry stays in the hub; only its links changed. The entry below that records the constitution being added is history and is unchanged. No code, pin, lock, profile, vendored contract or release status changed.

## 2026-10-22 engineering constitution and declarative governance registry direction (documentation only; non-authorizing, HOLD unchanged)

- Added [engineering constitution](docs/engineering-constitution.md) (EP01–EP18, review tiers, DOC-01, technical cautions) and [declarative governance registry](docs/declarative-governance-registry.md) (versioned rule data, constitutional floor in code, registered evaluators, R0–R4 sequence). Both are design and process documents: no code, pin, lock, profile, vendored contract or release status changed, and nothing is claimed as implemented or qualified.

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
