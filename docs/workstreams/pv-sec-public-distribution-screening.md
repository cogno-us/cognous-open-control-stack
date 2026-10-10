# PV-SEC: bounded public distribution screening (issue #73)

**Result: PARTIAL / PUBLICATION HOLD.** Audited selected hub main `3efe456d10a37dcdd2277b4a37d9034403380f09` on 2026-10-10. Companion PV-SAFETY PR #75 head as reported by that PR: `cd720e63d0d289a91f6f24302d2cc0d966aabddb`. This assessment extends, but does not supersede, PR #75. No disclosure clearance or operational GO is implied.

## Method and inspection boundary

GitHub connector reads of individual text files at selected main, plus GitHub issue #73, PR #75 metadata and its report at the PR head, and a recent-commit search. Files read: `README.md`, `component-lock.json`, `docs/start-here.md`, `docs/quickstart.md`, `docs/release-status.md`, `docs/architecture.md`, `docs/security-and-threat-model.md`, `collateral/business-collateral.md`, `collateral/one-page-overview.md`, `collateral/evidence-snapshot.json`, `SECURITY.md`, `CONTRIBUTING.md`, and PR #75 `docs/workstreams/pv-safety-publication-audit.md`. Root `AGENTS.md` was queried and returned 404; other repository instruction paths were not enumerated.

Read-only lexical screening of the six fetched collateral/security/architecture files was performed for credential vocabulary (`password`, `secret`, `token`, `api_key`, `private_key`), private-method identifiers (`ISS`, `IGPG`), and production/settlement assurances. This is NOT a credential or PII detector: those words are not secrets, while actual secrets may match none of them. No private source payload was copied into this report. Existing public security-contact information is intentionally public, not PII exposure evidence.

**Unscanned:** the complete Git tree and all nonlisted paths; Git object history, branches, tags, reflogs, deleted blobs; images, binaries and archive members; workflow artifact bytes and generated outputs; published websites, downloads, package or release attachments; upstream component repository histories; commit diffs beyond the current sampled text. Git clone was unavailable from the execution environment (GitHub DNS resolution failure), and the GitHub connector does not provide a complete recursive blob/history scan within this run. Accordingly, no negative whole-repository leakage claim is justified.

## Actual observations versus false positives

| Surface | Observation | Disposition |
|---|---|---|
| `SECURITY.md:3` | Categorically asserts that the repository contains no credentials despite no demonstrated full-distribution and full-history scan | **Medium: unsupported assurance**, not evidence of exposed credentials. PV-DOCS #70 should qualify wording. |
| `README.md`, `docs/start-here.md`, `docs/release-status.md` | Synthetic-local limitations and separate authority/effect/observation states are explicit | **No claim defect identified in sampled passages**; not a repository-wide assurance. |
| `collateral/business-collateral.md`, `collateral/one-page-overview.md` | C0 race, optional same-host C1, no C2/C3, no real settlement and refund deduplication limits are described | **No exposure identified in sampled text**; external re-use must retain qualifiers. |
| `docs/security-and-threat-model.md` | Correctly disclaims production security certification, custody, live confinement and operational response | **No unsupported production certification found in sampled text.** |
| `CONTRIBUTING.md` | Prohibits proprietary implementation and private terminology | Policy statement, not technical prevention. |
| `collateral/evidence-snapshot.json` | Contains public provenance IDs, digests and recorded test counts | Hashes/commit IDs are not credential findings; digest and artifact content were not independently revalidated here. |
| `SECURITY.md` public contact | Published security-reporting destination | Expected contact information, **not a customer-PII incident**. |
| Private ISS/IGPG | No private mechanism detected in inspected text; term-count absence in several sampled documents is not sufficient IP clearance | **Unknown beyond sample**. |

No confirmed credential, customer PII or proprietary implementation exposure was established by this inspection. This finding is **limited to sampled contents**, and should never be converted into “the repository is clean.”

## Unsafe command and assurance review

The public README and developer quickstart show network clone, Python virtualenv, and a synthetic reference runner. The runner is documented as deleting/recreating `--results-dir` and, absent checkout reuse, `.reference-work/`; it also installs dependencies, requiring disposable checkout and path precautions. These are **bounded destructive/environment-mutating behaviors**, not evidence of malicious commands. The quickstart's checkout `5737267d94d2b445735c95e8480a31de73a2abe8` is explicitly historical, not a current-head qualification. Script implementation was not executed or audited here.

Selected `component-lock.json` uses `merged-producers-v1`. Its current evidence metadata records 35 selected synthetic scenarios at reviewed source `7e43d55c6cc0123a191480a9e6870d6452affa83`, workflow run 37694032916 and artifact digest `5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7`. Separately, docs record 73 optional same-host C1 tests in run 37682165860; 915 earlier persistence tests are historical. Counts and digests are **read from selected metadata, not independent artifact inspections or tests**.

**Non-negotiable claim boundaries:** C0 revalidates immediately before dispatch and retains check-to-commit race; C1 is optional cooperating same-host SQLite only, not selected by default; C2/C3 are not qualified. Timeout, missing acknowledgement or point-in-time observed absence never grants retry permission; reconcile the original effect. Effect-ID dedupe is not equivalent business-intent dedupe. Synthetic SQLite effects are not bank/card/processor settlement. Orchestrator operational trust #30 is **HOLD / NOT ESTABLISHED**.

## Coordination and follow-up gates

PV-DOCS #70 should own any update to `SECURITY.md`, README or published collateral, especially replacing unconditional “contains no credentials” with a scoped intent and screening statement, and making #30 HOLD prominent. PV-SNAPSHOT #72 owns collateral snapshot/digest regeneration where required. Neither artifact is modified here.

A complete publication security gate requires an authorized clean checkout or export of all public refs and Git objects, an inventory of releases/CI attachments and generated/binary formats, secret/PII scanning with private output, targeted private-IP comparison against authorized exclusion criteria, manual review of positives, and a second-person verification of remediation. Preserve scan-tool versions, exact source SHA, refs, artifact identities and excluded/unreachable objects in a **private** evidence record. Suspected actual exposure must be privately escalated through the repository's existing security contact with **redacted metadata only**; do not post secret values, personal records, or proprietary excerpts to PRs/issues/CI. No positive exposure was identified that justified an escalation during this pass.

## Execution and decision

Checks executed: GitHub main-head/revision lookup; individual file reads; bounded term-presence checks on six sampled files; cross-document consistency review against PR #75 and issue #73. No local source checkout, full Git-history scan, third-party secret scanner, binary inspection, full scoped CI, or actual Actions artifact verification occurred. The sandbox Git clone failed because `github.com` DNS could not resolve. **Do not report these missing checks as passed.**

**Publication recommendation: HOLD pending comprehensive evidence. Operational trust #30: HOLD independently.** This is a findings-only report; no runtime, component lock, authority, credentials, effects, release permissions or other worker-owned paths are changed.