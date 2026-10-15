# S5 — publication-safety lane E closeout, 2026-10-15

**Baseline work complete; publication-safety disposition: PARTIAL / HOLD.**
Final-package freeze and accountable acceptance are **PENDING**.
S4’s exact proposed 202-file kit is screened below.
A separately identified interim integration delta is screened below. This is an
agent-performed bounded screening record, not independent human security acceptance,
semantic/IP clearance, legal clearance or release authorization. Issues
[#73](https://github.com/cogno-us/cognous-open-control-stack/issues/73) and
[#86](https://github.com/cogno-us/cognous-open-control-stack/issues/86) remain open.

## Source, instructions and publication boundary

- Hub base and current-tree screening source: `592919dd95396f3f6164cf0ceec1fd15c065691b`.
  Main was rechecked remotely during the pass and still named this SHA.
  Base commit date: 2026-10-14T22:47:15-07:00. Screening executed 2026-10-15 UTC.
- Isolated worktree/branch: `closeout/s5-safety-closeout`. Only this new public
  report is changed. Its eventual PR commit is the report validation head; it
  does not replace the baseline source identity above.
- Entire baseline tree enumerated: **643 tracked files**, no hub symlinks or
  submodules. No tracked `AGENTS.md` was found anywhere in that tree; read
  `CONTRIBUTING.md`, `SECURITY.md`, the remediation record and acceptance checkpoint.
- `component-lock.json` SHA-256:
  `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`.
  Selected runtime remains `merged-producers-v1`. Read the full-release,
  merged-consumer and bounded-v1 selection profiles; their distinct historical,
  candidate and scope-approval states are not interchangeable. False publication
  and production authorization fields are preserved.
- Initial open-PR lookup returned #117. A subsequent complete public API page
  returned #117–#120, including parallel S2/S3/coordinator work. Those later PR
  heads are **not** added to this baseline coverage. No other worker's path is changed.
- Working distribution proposal follows the
  [October 13 acceptance checkpoint](../releases/publication-acceptance-2026-10-13.md):
  named hub source/docs/tooling, root terms, retained notices and approved
  `examples/public-release-verification-20261013/` evidence. External component
  source bundles, installed dependencies/toolchains, optional protocol source/PDFs,
  credentials and private orchestration/IP are excluded from that proposal.
  A source tag nevertheless includes every tracked historical payload; a prose
  exclusion does not remove bytes from a tag or archive.

**S4 proposed manifest received and verified:**
[PR #123](https://github.com/cogno-us/cognous-open-control-stack/pull/123),
head `e7b63da186c9992244e79255cef809860bb53df2`,
`docs/releases/distribution-closeout-2026-10-15/manifest.json`, SHA-256
`18c5f78c0f22d75da87995f8a96cb02bef106434f2cebcbf26f359ec37a2465a`.
It supersedes the broader working proposal above with a **202-file source review
kit**, frozen to `592919dd95396f3f6164cf0ceec1fd15c065691b`; all 441 other baseline
paths are explicitly excluded. All generated examples, collateral and external
component source are excluded. The kit is not an offline reproduction environment.
S5 independently constructed its 202 regular files from exact Git objects and
verified every manifest SHA-256: **1,472,525 package bytes**. Both Gitleaks and
detect-secrets returned **zero alerts** on this exact constructed package.
No supplied compressed/downloadable final package was received or cleared.

Supplemental kit lexical review found **13 matching lines** (three email and ten
IP/PII-vocabulary observations), zero SSN-pattern observations. All 13 were read:
the email cases are the published reporting contact and two test placeholders;
the other lines concern exclusions, notices, public profile scope and governance
work descriptions. No customer record or private implementation was established
in that small sample. Full semantic/IP acceptance remains with accountable owners;
this lexical result does not establish absence beyond the observed patterns.

The private S5 baseline inventory (643 paths, Git blob IDs, sizes and SHA-256)
has SHA-256 `09afb85023dadba3a5010efa56f6e35f097eae84f3b1baf4aad5d51c25510562`;
this is separate from S4's manifest. S4's newly added checker/sidecars and later
integrated files are outside the 202-file proposal and are not automatically
covered by its package screening. The 21 unresolved broader Gitleaks candidates
are outside this frozen hub-only package; they remain unresolved for any expanded
source/component distribution. **Final source/package freeze remains pending.**

## Executed collection and scanner methods

Git 2.51.1; Python 3.12.14; ripgrep 15.2.0; Gitleaks **8.30.1**;
Yelp detect-secrets **1.5.0**; SQLite via Python's read-only API.
`pdftotext` 24.02.0 was available, but no PDF was encountered in the examined
nonoptional corpus and no PDF extraction coverage is claimed.

Hub clone was nonshallow. Frozen local ref snapshot: **97 refs**,
SHA-256 `9f8a15c4bb2842f09554236c30a7b3df0c21ad4b0437d1e020753e64b9254b0c`.
`git rev-list --objects --all` plus `git cat-file` enumerated **414 commits,
1,165 trees and 1,089 blobs** (23,834,452 raw blob bytes); no requested object was
missing. Commit dates across those available refs range from
2026-07-05T10:19:31-07:00 through 2026-10-15T07:18:33-07:00.
This includes available remote-tracking branch history, not just main; it does
not mean all server-side PR refs, deleted branches or unreachable objects.
No annotated tag object was returned in that object population.

Ten nonoptional component repositories were cloned bare; selected commits and
ancestors were enumerated. Histories were byte-screened only when at most
20,000 distinct blobs and 200 MiB of raw blobs. Runtime exceeds both thresholds:
**51,658 ancestor blobs / 1,237,074,403 raw bytes**. Its **4,560 distinct selected-tree
blobs** were processed instead; its remaining historical bytes are unexamined.
The runtime tree has 4,578 path entries, including one symlink; the symlink target
was not followed. Repeated paths can share a blob. Other component refs outside
the selected ancestors were not scanned.

| Selected lock component | Exact selected revision | Selected paths | Ancestor commits | Ancestor blobs / processed blobs | Commit-date bounds |
| --- | --- | ---: | ---: | ---: | --- |
| `action_manifest` | `46c950bed37fe3812000895430bc0312d29e37ce` | 62 | 15 | 123 / 123 | 2026-07-05T06:51:50-07:00 — 2026-10-05T12:07:19-07:00 |
| `control_plane` | `d3dadee70bd319812b207389ab1e0f6efe511916` | 108 | 101 | 262 / 262 | 2026-07-05T04:05:19-07:00 — 2026-10-07T13:30:06-07:00 |
| `constitutional_authority` | `fb3d97938969a89e149e8ff8db2756091d1233fc` | 329 | 90 | 871 / 871 | 2026-08-27T07:21:59-07:00 — 2026-10-05T11:53:49-07:00 |
| `gax_imx_transport` | `a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf` | 39 | 139 | 164 / 164 | 2026-10-05T18:52:08-07:00 — 2026-10-07T14:53:34-07:00 |
| `moltbot_safe` | `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` | 4578 | 8386 | 51658 / 4560 | 2025-11-24T11:16:47+01:00 — 2026-10-07T13:43:05-07:00 |
| `replay_bundle` | `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa` | 100 | 100 | 218 / 218 | 2026-07-05T06:55:46-07:00 — 2026-10-07T14:25:58-07:00 |
| `governance_evidence_pack` | `b4baccd823d2a73be276c1de745b19cf7c56a0d6` | 110 | 82 | 213 / 213 | 2026-07-05T06:57:52-07:00 — 2026-10-07T14:38:45-07:00 |
| `odes` | `c5e9a0f3695ae836b803be06c46d2c669642ee03` | 62 | 72 | 161 / 161 | 2026-07-01T20:05:05-07:00 — 2026-10-07T14:38:51-07:00 |
| `bitrep` | `5b5077dafde232a7801cb425c4efddcffb468723` | 56 | 64 | 143 / 143 | 2026-01-22T08:23:25-08:00 — 2026-10-05T09:43:33-07:00 |
| `the_index` | `d5e45d275cb301d9684b543e93b05997991d1cf2` | 80 | 53 | 156 / 156 | 2026-01-23T06:04:45-08:00 — 2026-10-05T10:07:26-07:00 |

Optional locked repositories were not fetched or scanned: `prp`
`cb137f028e92448a56e785e3d4ea074b444fa225`, `research_intelligence`
`30c7274b49c07a0df4c8ca7b281f2e3f8ae68dee`, and `tfa`
`442d07b4891870abb1756fcb11c24ccf187706f4`. Preserve exclusion of their source/PDFs
from the proposed bundle; separately fetched reproduction inputs remain outside
this safety clearance. Later licensing heads and W7/S1 candidate sources were
not silently substituted for selected revisions.

Across hub/components, **7,960 blob-processing requests** were made (not a
unique-file total across repositories). Text, bounded extracted members and
supplemental binary strings were deduplicated by SHA-256 into **8,194 text
objects**; eleven Git log/metadata exports made **8,205 scanner inputs totaling
94,401,930 bytes** for the final Gitleaks corpus scan.

Executed Gitleaks commands, with private report/log destinations omitted:

```sh
gitleaks dir <baseline-hub> --config <private-config> --gitleaks-ignore-path <nonexistent-path> --ignore-gitleaks-allow --redact=100
gitleaks git <baseline-hub> --log-opts=--all --config <private-config> --gitleaks-ignore-path <nonexistent-path> --ignore-gitleaks-allow --redact=100
gitleaks dir <derived-corpus> --config <private-config> --gitleaks-ignore-path <nonexistent-path> --ignore-gitleaks-allow --redact=100
```

The explicit config contains `[extend]` / `useDefault = true`: embedded default
rules and their built-in allowlists apply. No repository ignore file, baseline
or inline `gitleaks:allow` suppression is accepted by these final commands.
Default recursive decoding applies; Gitleaks archive traversal is disabled and
archive handling below was performed separately. The history command reports
**331 diff-bearing scanned commits**; that is not the 414-commit inventory.
Independent blob export also covers unchanged/merge-reachable file bytes.
Gitleaks does not validate credentials against services.

Detect-secrets ran with **27 default plugins**, default filters and entropy
thresholds (base64 4.5, hex 3.0): `scan -n .` in the baseline worktree, and
`scan -n --all-files <derived-corpus>`. `-n` disables network verification.
The second run covered the 8,194-input corpus before the eleven metadata exports;
Gitleaks subsequently covered those exports. Default heuristic/allowlist filtering
can hide candidates; neither detector is an absence proof.

Supplemental lexical semantic screening identified **1,059 matching lines**:
666 email-pattern observations and 393 private-IP/customer-data vocabulary
observations (603 distinct matching line texts overall), with zero SSN-pattern
observations. These are review prompts, not 1,059 exposure findings. No general
PII model, address/phone/date-of-birth classifier, OCR or private-IP reference
comparison was executed.

## Archive, database and binary handling

Contents were never executed. Archive members were read in memory; no member
path was used as an extraction destination. Traversal/absolute/backslash paths,
encrypted ZIP members and unsupported TAR member types are rejected. Bounds:
16 MiB per blob/member and per XZ decoded stream, depth three, at most 2,000
members and 64 MiB expanded members per archive. No encountered archive bypassed
these limits. Unsupported/encrypted/over-limit material is unexamined.

Successful processing: **two XZ streams, four TAR/ZIP archive objects containing
354 members**, and **33 SQLite blob versions** containing 124 total table rows.
These overlap nested/historical populations and are not counts of independent
qualification runs. SQLite was opened `mode=ro&immutable=1`, extension loading
disabled, ordinary table rows selected (10,000 per-table bound); triggers and
schema statements were not executed. No new qualification artifacts were generated.

**Two current historical recovery archives exceeded the XZ decoded-stream bound**:
`examples/worker14d-recovery/diagnostic-runs.tar.xz` and
`examples/worker14d-recovery/raw-evidence.tar.xz` (370,976 and 434,228 compressed
bytes). Their contents remain unexamined in this pass; this is not evidence of a
malicious archive. Distribution/security owners must inspect them in an
appropriately bounded follow-up or explicitly exclude them from the package.

**249 other binary blob versions** (13,727,406 bytes) received printable-byte-run
screening only. This includes media/compiled content; images were not visually
reviewed, OCR was not run, compiled objects were not decompiled and hidden/
encoded content is not cleared. Optional/historical PDFs outside the examined
corpus remain unexamined.

## Candidate trace and safe findings

Raw scanner results, per-observation neutral IDs, source-object/member mappings,
context and adjudications are retained outside the repository. No suspected
credential value, customer record or proprietary excerpt is included here.
No credential was tested against an external service; no finding was sent to a
mailbox or another person.

| Population | Actual result | Disposition and limitation |
| --- | --- | --- |
| Baseline hub Gitleaks directory + available Git diff history | **0 alerts** in each command | No confirmed credentials found by these rules in examined hub material; not whole-distribution safety |
| Baseline hub detect-secrets | **3,039 observations in 232 paths**: 3,038 hex entropy and one base64 entropy | 2,224 observations had a hash/provenance term on the matched line; this is provisional contextual evidence, not blanket dismissal. The single base64 hit was reviewed as a generated workspace path. Remaining entropy observations need reconciliation |
| Broader Gitleaks derived corpus | **399 alerts**: 387 generic API key, five auth-header, four private-key, three client-ID | Per-alert trace retained; **378 contextually dispositioned, 21 unresolved**. Counts are not unique credentials |
| Broader detect-secrets derived corpus | **8,673 observations in 802 inputs**: 7,148 hex entropy, 1,093 base64 entropy, 415 keyword, nine private-key, seven basic-auth, one provider-key pattern | Each observation has a private neutral ID and source/member trace. Not fully reconciled with Gitleaks or adjudicated; no net unique-finding count is claimed |
| Lexical PII/IP candidates | 1,059 matching lines | Public attribution/contact and boundary-policy language are present. Full semantic review remains open; absence of a matched vocabulary cannot clear IP |

The 378 reviewed Gitleaks dispositions comprise 228 hashed entries in a committed
scanner baseline (not raw secret values), 136 deterministic concurrency-event
identifiers traced to generated bounded-store test evidence, five documentation
token placeholders, three illustrative identity mappings, two public OAuth client
identifiers, two API-documentation key ellipsis placeholders, one redaction-test
fixture and one test idempotency identifier. These are contextual dispositions,
not independent human acceptance. The unresolved population includes test/
example-associated key-like material; test placement alone does not establish
that a value has never been operationally reused.

**Confirmed operational credential, customer-PII or proprietary implementation
exposures: none established by this pass.** This does not resolve the 21 Gitleaks
candidates, unreconciled detector observations or unreviewed semantic surfaces.
Security must adjudicate individual records privately before making a broader
negative finding. Do not publish guessed remediation or rotate/delete anything
based solely on a detector match. If confirmed, return a minimal private fix
proposal to the coordinator and obtain the appropriate incident authorization.

## Manual claim and semantic review

Read current README; start-here; quickstart; governance quickstart; release status;
security/threat model; operational trust status; SECURITY and CONTRIBUTING;
both Markdown collateral summaries and evidence-snapshot JSON; earlier safety
reports; October 13 verification/acceptance/closeout; October 15 remediation;
comparative battery documentation and both comparison plans. This is a bounded
named-file semantic/claims sample, not manual review of every source line,
archive row, binary, email hit or component implementation.

- Current SECURITY.md qualifies sensitive-data absence. The categorical cleanliness
  assertion flagged in October 10 reports is **corrected on this baseline**;
  those reports retain their historical observations. October 13 recovered scans
  also remain evidence only for their recorded revisions and populations.
- README and release-status distinguish frozen selected-chain evidence from newer
  optional implementations. Current entry disclosures retain C0's check-to-commit
  race, optional cooperating same-host C1, no C2/C3, no real settlement, and
  operational **HOLD / NOT ESTABLISHED**. Retained old execution JSON/runner fields
  are historical evidence, not current publication authority.
- Comparison documentation explicitly permits parity and identifies the Cognous
  subject as the optional hub profile. Corner differences reflect checks in
  configured applications, not general OPA/LangGraph limitations. Shared signature
  helpers, automatic LangGraph approval, absent commercial adapters and unnormalized
  timings preclude general superiority or human-effort claims. No comparison was
  rerun for this report.
- Both collateral summaries contain synthetic/C0/C1/settlement limitations but do
  not independently print the explicit operational HOLD/public-preview-pending
  status. **Proposed coordinator fix:** add that status before separately publishing
  either summary, then regenerate their detached collateral hashes through the
  existing owner workflow. This is a presentation gap, not evidence of deployment
  authorization or a confirmed sensitive disclosure. No collateral file is edited.
- Public quickstart/reproduction instructions invoke network fetch/install and
  write result directories. Only their documented trusted-host/disposable-checkout
  scope was reviewed; this is not an audit of every executable path or embedded
  binary instruction.

No authoritative proprietary exclusion corpus was accessed. A Cognous IP owner
must examine implementation substance against authorized exclusion criteria;
private-term searches and an agent's unfamiliarity cannot supply that decision.

## Coverage, exclusions and accountable next actions

| Surface / exact identity | Coverage achieved and confirmed finding status | Exclusions / residual / next action and role |
| --- | --- | --- |
| Hub tracked tree at baseline SHA | 643-path inventory, Gitleaks and detect-secrets; named-file manual sample; no confirmed sensitive exposure | Unreconciled entropy observations and full semantic review: security + data/IP owners |
| Hub reachable history at frozen 97-ref snapshot | 414 commits enumerated, 1,089 blobs processed, metadata exported, Gitleaks diff scan; no confirmed sensitive exposure | Server PR refs not fetched, later refs, deleted/unreachable objects, reflogs and hosting backups excluded: security owner defines required history boundary |
| Ten nonoptional selected trees and ancestor histories in table | Selected bytes processed; nine histories within bounds processed; derived-corpus candidates privately traced | Runtime ancestor bytes beyond selected tree, other component refs, symlink referent and optional protocols unexamined: component maintainers + security |
| Historical examples, archives and databases at their Git blob identities | Four archives/354 members and 33 SQLite versions processed; synthetic-event candidates traced | Two over-limit current archives and binary semantics pending: distribution + security reviewer |
| Generated qualification evidence already tracked/in archives | Existing logs/JSON/XML/SQLite included in processed populations; no fresh execution claim | Not every artifact's entire semantic content manually reviewed; subsequent generated output absent: qualification owner supplies final hashes, security reviews |
| GitHub Releases API | One complete page returned **0 releases**, no pagination | No release asset bytes existed in that response; external/mirrored packages not covered: release owner confirms actual distribution |
| GitHub Actions artifact API | First 100 records retrieved; API reported **1,978 artifacts**, additional pages present | No full artifact pagination, downloads or workflow-log screening. Tracked copies do not clear hosted originals/expired artifacts: CI owner inventories, security selects and scans relevant retained bytes |
| Repository entrypoints/collateral at baseline | Named-file claim review and existing entry/link/integrity checks | External website, social/promotional copies, attachments, screenshots, mirrors, packages and announcements unexamined: communications/release owner supplies exact final surfaces |
| S4 proposed manifest at exact PR #123 head/hash above | 202 exact source files constructed and hashed; zero alerts from both detectors; 13 lexical hits reviewed | Final source/package freeze, S4 review-infrastructure delta and supplied final artifact bytes pending: coordinator + S4 + security |
| Independent security/data/IP acceptance | **NOT PERFORMED** | Named independent human security reviewer, data owner and Cognous IP owner adjudicate scope/candidates/exceptions; release owner records final decision |

OSS-scanner enrollment, an accepted enrollment PR, its readiness workflow and CI
badges are not evidence of a completed vulnerability scan. No vulnerability-scan
clearance is asserted by S5. Mail delivery/response verification remains a separate
maintainer acceptance item; this pass sends no messages.

## Interim integrated-source delta

During this pass main advanced to `963de0bdf71f9dd3cb2aca57a169a413c573b353`
(2026-10-15T07:34:36-07:00). The S5 branch was rebased onto that exact source;
this is the **PR base**, while the larger baseline scan remains identified by
`592919dd95396f3f6164cf0ceec1fd15c065691b`. The interval changes nine paths
(96,008 complete current-file bytes): S2 destination implementation/tests/workflow/
report, S3 tests/workflow/report, and the coordinator's Markdown/JSON control panel.
The hub now has 651 pre-report tracked paths. No lock or selected profile changed.

All nine current file versions were copied to a separate private delta corpus,
manifest SHA-256 `fe5640cc9d9ad9d4e00d46064d7557202643d07a6f2b7784b84f7700076c080c`.
Gitleaks with the same explicit config and detect-secrets with `-n --all-files`
each returned **zero alerts** for that corpus. Read the destination diff and
workflow commands, sampled new test construction and reviewed new report/panel
scope wording. New restore documentation treats rollback reproduction as a
limitation and the external anchor as a requirement, not deployed protection;
new ingress documentation retains local/trusted-clock limitations. No new
confirmed sensitive exposure or unsupported production assurance was identified
in this bounded delta review. This does not independently validate S2/S3 tests.
Intermediate new Git commit objects and hosted artifacts were not comprehensively
rescanned; current changed-file coverage is not full-history coverage for this
new interval. The S5 report itself receives final-head review below and is not
included in either pre-report population. Later source changes, S4 review infrastructure and final downloadable package
bytes remain pending; do not present this interim delta as final-package clearance.

## Validation and integration handoff

Existing documentation/source-integrity checks are run on this report's committed
PR head, alongside local-link/source-identity checks and `git diff --check`.
Exact validation head/results are returned in the PR handoff; no unrelated
integration suite is rerun and no runtime test coverage is claimed.

Private evidence is held in a mode-restricted sibling directory outside every Git
worktree, keyed as **S5-20261015**. Its hash ledger SHA-256 is
`8fba16d4ab40bd6c68a50ae61dae0cb4d09e186079ed2b08971d0d40400a2d75`.
The coordinator receives the local location privately in the handoff. It is
session-local evidence, not an external durable security archive; the evidence
custodian must preserve the minimum necessary records before workspace expiry.
Do not attach the raw ledger/candidate context to a public PR or CI run.

**Final-package delta review: NOT EXECUTED.** The interim delta above is bounded
to its named source; no final source/package freeze was supplied. Required sequence: freeze final
source and final S4 manifest/hash (the proposed identity above is now received);
compare every inclusion against the baseline inventory;
process added/modified package bytes and claim surfaces; reconcile exclusions,
historical payloads and unresolved candidates; have accountable reviewers accept
or explicitly disposition the bounded residuals. Then record exact source,
manifest and artifact hashes with the release-owner decision. Source screening
alone does not establish that a subsequently built package contains only those bytes.

`reference_release_authorized=false`, `production_deployment_authorized=false`,
C0 limitations, optional same-host C1, no C2/C3, no real settlement and operational
**HOLD / NOT ESTABLISHED** remain unchanged. No merge, tag, release, announcement,
production action, credential validation or issue closure is performed by S5.
