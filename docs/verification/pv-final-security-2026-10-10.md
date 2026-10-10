# PV-FINAL-SEC: independent public-distribution security verification — 2026-10-10

**Issue:** [#86](https://github.com/cogno-us/cognous-open-control-stack/issues/86); parent [#83](https://github.com/cogno-us/cognous-open-control-stack/issues/83). **Decision: BLOCKED / PUBLICATION HOLD.** This is a limited, independently authored verification record, **not** a full-history security clearance, a clean-repository assertion, or authorization to publish.

## Exact source boundary

- Integrated preview candidate: [PR #84](https://github.com/cogno-us/cognous-open-control-stack/pull/84), independently observed draft/unmerged at exact head `62c93784f34f6ad0a3f63a5efac04a948e826ae1`. Its reported base `main` SHA is `3efe456d10a37dcdd2277b4a37d9034403380f09`; these are not interchangeable.
- This report's isolated branch was created directly from that exact integrated-head SHA. Only this new report file is proposed; no changes to integrated preview, component lock, runtime, authority, credentials, production effects or release permissions.
- Selected `component-lock.json` read at the integrated head, blob SHA `b3bf15918ec7eaccd10c486b61926351d392dd04`; selected runtime profile `merged-producers-v1`. The lock lists Control Plane `d3dadee70bd319812b207389ab1e0f6efe511916`, Execution Runtime `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac`, and accepted hub merge `f801546d5272104b02a240e1126b3f92f26486f2`. These SHA values were read as contract metadata, **not** independent code inspections of component repositories.
- Inspected governing public instructions: `CONTRIBUTING.md` (small public-safe hub-only changes, no proprietary implementation or unsupported guarantees), `SECURITY.md` (private reporting channel), and the integrated `docs/release-status.md` / `docs/preview-entry-audit.md`. Root `AGENTS.md` fetch at the exact head returned HTTP 404; other nested instructions were not exhaustively enumerated.

## Actual methods, coverage and outcomes

1. Via the authenticated GitHub repository connector, fetched at exact preview SHA: `SECURITY.md` (blob `5851c28c6f158ae7063312f6850f383da6f350ed`), `CONTRIBUTING.md`, `README.md`, `docs/release-status.md` (blob `1a1c04228db1cf7468a65e701bd05c19a89a4068`), `docs/preview-entry-audit.md`, `component-lock.json`, `docs/workstreams/pv-sec-public-distribution-screening.md`, and `.github/workflows/preview-entry-audit.yml`. Compared visible text semantically for explicit production guarantees, governance boundaries, sensitive-data publication rules and the earlier PV-SEC review. This was manual inspection of named text files; it was not byte-complete scanning or a tested absence of hidden credentials, PII, or proprietary implementation.
2. Read issue #86, metadata/body for PR #84, and separate earlier PR #75 head `cd720e63d0d289a91f6f24302d2cc0d966aabddb` and PR #80 head `febc463e804966da3c667779b6a43e3978de3a87`. Previous reviews explicitly left complete history, binaries and published distributions unscanned. Their observations do not become independent source coverage in this run.
3. Attempted to clone the GitHub repository into a disposable local path using Git over HTTPS. **Failed before cloning:** DNS could not resolve `github.com`. No local tree, history or blob corpus was obtained; there was no opportunity to execute a secret-scanner or Git-history audit.
4. In inspected `SECURITY.md`, the categorical statement that the hub “does not contain ... credentials” is **not supportable as a verified assurance** without the comprehensive screening required by #86. This is a disclosure/claim-quality finding, **not** evidence that credentials were actually exposed. Change ownership is with the existing documentation/security owners, not this report-only worker.
5. Reviewed the selected release-status prose: C0 is expressly pre-dispatch revalidation with a check-to-destination-commit race; C1 is optional same-host cooperating SQLite; C2/C3 and external settlement are expressly unqualified. The preview audit separately labels operational trust #30 HOLD. This is positive **wording evidence on sampled surfaces only**, not proof that every external copy retains disclaimers.
6. The `preview-entry-audit.yml` workflow runs documentation entrypoint checks and negative controls against specified paths. It is **not** an exhaustive publication security scanner, history scanner, archive scanner or PII/IP clearance gate. No CI execution was triggered by this verification before report creation; a future green check must not be read as whole-distribution clearance.

## Surface-by-surface coverage ledger

| Distribution surface required by #86 | Verified coverage in this run | Disposition |
| --- | --- | --- |
| Integrated head and selected contracts | Exact PR SHA and listed text files fetched at that SHA; lock contents and named release claims inspected | **Partial**, not complete tracked-tree enumeration |
| All tracked files and nested instructions | Eight named text files only, root `AGENTS.md` queried and absent | **NOT SCANNED** exhaustively |
| All Git commits, parent histories, deleted blobs, all public refs | Clone DNS failure; no historical object walk | **BLOCKED** |
| All branches and tags | No complete ref/tag inventory or reachable-object analysis | **NOT SCANNED** |
| GitHub releases and attached download bytes | No release inventory or attachment extraction | **NOT SCANNED** |
| GitHub Actions artifact bytes and logs | Workflow YAML inspected; no complete artifact/log retrieval or byte scan | **NOT SCANNED** |
| Generated archives, examples, packaged downloads | No systematic generation, extraction or nested archive scan | **NOT SCANNED** |
| Images, media, PDFs, binary/encoded payloads | No byte retrieval or decoder/metadata review | **NOT SCANNED** |
| Published website, public collateral copies and third-party mirrors | Sampled repository README and preview docs only; no public distribution crawl | **NOT SCANNED** |
| Component repository histories | Lock metadata only; no upstream source corpus | **NOT SCANNED** |
| Credentials, keys, tokens and secrets | Public reporting policy and wording inspected; no credential detectors run on complete corpus | **UNKNOWN — no clearance** |
| Customer PII | No complete PII detection and protected manual triage | **UNKNOWN — no clearance** |
| Proprietary ISS/IGPG implementation disclosure | No complete public/private exclusion comparison; no private reference corpus accessed | **UNKNOWN — no clearance** |
| Unsafe executable instructions | Sampled documentation and workflow YAML reviewed; scripts or scripts embedded in artifacts not comprehensively audited/executed | **PARTIAL** |
| Unsupported production assurance claims | Inspected sample release-status/entrypoint text and prior review; all external distribution variants not checked | **PARTIAL** |

## Scanner inventory, positives, false positives and private escalation

- **Automated scanners executed: none.** No version can honestly be reported for Gitleaks, TruffleHog, detect-secrets, Semgrep, PII detectors, archive scanners, binary extractors, or proprietary-IP comparison tools. Manual semantic review used the GitHub file connector; its responses are *individual fetched paths*, not a directory-wide attestation.
- **Confirmed disclosures:** none established in the named inspected material. This is **not** a finding of no exposures in uninspected surfaces.
- **Candidate findings:** unsupported categorical cleanliness assertion in `SECURITY.md`, noted above. This is not a secret-value pattern hit.
- **False positives:** public Git commit SHA values, workflow IDs, evidence digests and intentionally public vulnerability-reporting contact are provenance/contact data, not by themselves secret or customer-PII disclosures. No scanner alert inventory was produced, so no count of scanner false positives can be asserted.
- **Sensitive triage:** no suspected *actual* credential, customer-data or private implementation exposure was identified that warrants a private disclosure from the examined material. If a future authorized scan identifies a candidate, do not publish its raw contents, path embedding secrets, samples or vulnerable reproduction in public artifacts. Escalate privately using `SECURITY.md` with redacted metadata and privately retain severity, detector/class, scope and remediation evidence.

## Missing evidence and completion criteria

An authorized security-capable environment must freeze exact preview source and **all** public repository refs, enumerate the full reachable/unreachable object scope with explicit limits, collect release/tag assets and GitHub Actions artifact/log inventory, inspect all tracked and historical bytes (including encoded binary/media/archive members), check published copies, execute and record versioned secret/PII detectors and manual ISS/IGPG exclusion review, privately adjudicate matches, and have a separate reviewer verify remediation and publication decisions. Preserve exact scan date, tool versions/configuration, object/ref counts, selected SHAs, external artifact IDs/digests, scanned vs inaccessible surfaces, and findings **only in authorized private evidence storage**. A public report should contain sanitized classifications and coverage metrics without exposing sensitive materials.

Existing PV-SEC reports at issue #73 and PRs #75/#80 are **partial earlier checks**, not substitutes for this independent exhaustive assessment. The absence of a full clone, complete Git history, scanner executions and artifact-byte checks independently blocks an affirmative PV-FINAL-SEC result.

## Trust and release disposition

**PV-FINAL-SEC #86: BLOCKED / HOLD; public-distribution security signoff not justified. Operational trust [orchestrator #30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30): HOLD / NOT ESTABLISHED, independently.** C0 retains check-to-commit races; optional same-host C1 does not eliminate remote commit races; C2/C3 are not qualified. Synthetic SQLite destination observation is not real settlement. Effect-ID deduplication is not business-intent deduplication. Unknown/absent observation alone is not retry permission. No release, production grant or merge is requested by this report.
