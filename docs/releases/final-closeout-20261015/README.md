# S0 exact-source closeout packet — 2026-10-15

**Publication HOLD. Operational trust HOLD / NOT ESTABLISHED.**
`reference_release_authorized=false`; `production_deployment_authorized=false`.
No release/tag, asset upload, announcement, production activation, settings change
or reporting exercise was performed. All accountable acceptance remains unsigned.

## Source and proposed package

| Binding | Exact identity |
| --- | --- |
| Integrated qualification/package source | `e335e5512fe8dd0a73637dcd8fd9c21ec235e43e` |
| Integrated source tree | `a437349d83ce3d83de4697afdf154800258c1483` |
| Selected lock SHA-256 | `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc` |
| Selection | `merged-producers-v1`; lock and all four existing profiles unchanged |
| Separate S1 candidate | [PR #122](https://github.com/cogno-us/cognous-open-control-stack/pull/122), head `d577b11a9ee4258fd097dc0abcc37a7deae218aa`; BLOCKED, unmerged, nonselected |
| S1 manifest SHA-256 | `c381cfa44ef93aee27f0bf4e4789d216369652a904c353efe6d36c899e6d21ea` |
| Final manifest | [manifest.json](manifest.json), SHA-256 `b1805bac8990676c17222d10e18810dbcd346a1003b3e4d67936efb997318d99` |
| Actual locally constructed ZIP | `cognous-source-review-e335e551.zip`, 1,549,446 bytes, 206 regular files / 1,518,114 file bytes |
| ZIP SHA-256 | `1c9ae8af9d313cfde478c6e1bb46f58e563845f9ae22b6c56c86670b57b33faf` |

The manifest partitions all 669 tracked files at the frozen source: **206 included,
463 excluded**. It refreshes S4's 202-file baseline kit with current included
bytes and four new ingress/restore/inventory qualification files. All 30 required
original license/notice files remain. Every ZIP member/path and its digest were
checked against the manifest. The ZIP exists locally as a review construction;
it has not been distributed or committed as a release asset.

Excluded: generated examples and historical payloads, collateral, workflows,
closeout audit metadata, external component source, optional protocol source/PDFs,
installed dependencies/toolchains and production material. This is a source
review kit with references to excluded/external material, not an offline runnable
environment. Do not replace it with a normal Git source/tag archive: that would
include a different, unaccepted population. Root hub terms do not relicense all
selected components. Rights acceptance is still `pending_accountable_review`.

These packet files, the refreshed control panel and S5/S6 report-only follow-ups
postdate the frozen source and are excluded from this package. Earlier scans do
not cover them, all new commit objects or future full-source archives. This
explicit exclusion avoids circular claims that a report screened itself.

## Source integration and qualification

| Work | Source disposition | Evidence and remaining boundary |
| --- | --- | --- |
| S2 ingress, #118 | MERGED `0347d54` | 39 new ingress/wire testcase elements; 179 affected existing elements and 22 separate subtests; 13 existing mutation probes plus two new negative controls. Ten exact-head workflows passed. Shared admission budget can deny legitimate callers; total wire/lock/write work is unbounded. |
| S3 restore, #119 | MERGED `963de0b` | 12 new restore cases; combined 53 testcase elements plus 11 subtests. Six exact-head workflows passed and S0 reran after S2. Full preconsumption restore permits two historical synthetic commits while one current row remains. Prevention is BLOCKED. |
| S4 inventory, #123 | MERGED `7ec2476` | 27 unittest methods plus 10 unsafe-path subtests. Six exact-head workflows passed. S0 regenerated baseline manifest/provenance/dependencies/excluded artifacts with no diff and built its 202-file kit. Final 206-file refresh is separately bound above. |
| S5 safety, #124 | MERGED `7655d23` | Public-safe bounded screening report; five exact-head workflows and 17 check runs passed. Source integration is not independent security acceptance. S0 final replay counts below correct the interpretation of the original smaller-kit zero result. |
| S6 operations, #121 | MERGED `a234fd1` | Two reports; five exact-head workflows passed. Reporting receipt/acknowledgement/triage and administrative enforcement remain unestablished. |
| S0 shared repairs, #125 | MERGED `e335e55` | Preview audit now runs on every PR and covers 13 pages/127 local links. Both collateral summaries print HOLD; detached hashes refreshed. S3 testcase/subtest wording corrected. Eight exact-head workflows and all 21 check runs passed. |
| S1 integration, #122 | BLOCKED / UNMERGED | Rerun on an exact candidate overlay over `e335e55`: two repetitions of 23 testcase elements, each 13 passed / 10 failed, zero errors/skips/subtests. No compatible candidate or selection approval is claimed. |

At the frozen integrated source, S0 ran the combined affected suites:
**134 raw JUnit testcase elements, 21 separately reported subtests, zero
failures/errors/skips**. The suite attribute is `tests=155`; it is not 155
independent testcases. Raw XML SHA-256 is
`efdbe9cf168acbbea0bea0f8b4911242e9d49c607a2c1097883cfb9c1140dd8c`.
Exact commands and artifact/source identities are in [verification.json](verification.json)
and the [control panel](../../workstreams/release-closeout-control-panel.md).
Historical selected PV-2/PV-3 passes retain their original 2026-10-13 scope;
these current scoped checks do not rerun or broaden the historical whole matrix.

S2 migration is additive: deploy every writer together, retain existing history,
handle `INGRESS_SATURATED`, and keep signed/fresh/sequenced ingress recovery
trusted-local. Saturated requests still acquire a writer lock and commit an
aggregate update. Authenticated evidence and effect/consumption/audit persistence
remain required and atomic in the local transaction. Trusted clock, host custody,
authenticated growth and complete-destination restore are outside that bound.

S3 delivers characterization and an external-anchor contract, not the anchor.
An independently administered monotonic service, receipt/reconciliation semantics,
backup independence and deployment acceptance remain necessary for prevention.
C0 check-to-commit limitations, optional cooperative same-host C1, no C2/C3 and
no real settlement remain unchanged.

## S1 selection proposal — do not apply

The concrete proposed replacements are recorded in the control-panel JSON under
`final_packet.selection_proposal`: CP `d3dadee7…` → `c7f122ba…`; GAX `a1cbc7b2…`
→ `6ea048e7…` for its `sha` and `accepted_sha`. Other five core candidate pins
remain unchanged. **Recommendation: defer selection.** These values are a
reviewable blocked proposal, not accepted replacements or a patch to the lock.

The actual candidate loses durable effect-time refusal fields in the executor,
Replay rejects the exact CP revision, GAX claims historical producer provenance,
and ODES/Evidence Pack reconstruction fails. Owning-component contracts must be
repaired and qualified with new exact pins; an allowlist-only adjustment or
suppressed status comparison is insufficient. No historical acceptance metadata
or existing selection profile may be relabeled to imply acceptance of this pair.

## Rights, safety, reporting and enforcement

| Gate | Current disposition |
| --- | --- |
| PV-1 navigation/rights | Precise package and original notice provenance verified; accountable package rights acceptance PENDING. External PRP/TFA, runtime mixed terms and dependency bundles remain excluded/unaccepted for redistribution. |
| PV-2 source/pins/provenance | Technical identity VERIFIED for the frozen source and 206-file ZIP; no candidate promotion or release permission follows. |
| PV-3 bounded execution | Historical scoped PASS preserved; current closeout suites pass; S1 compatibility BLOCKED. Restore/race characterizations are not safety guarantees. |
| PV-4 disclosure | Scoped entry/claims review and collateral HOLD correction complete; accountable final publication claims acceptance PENDING. |
| PV-5 safety | PARTIAL / HOLD. Exact final kit and current source delta screened; full semantic PII/IP and independent human acceptance remain unavailable. |
| PV-6 reporting | PARTIAL. HTTP/MX observations do not establish mailbox receipt, acknowledgement, private handling or staffing. Owner exercise/evidence PENDING. |

S0's Gitleaks 8.30.1 scan returned zero alerts for the final kit and the 32-file
current source delta (1,085,736 bytes). Explicit default-rule config was used;
repository ignore/inline suppression was disabled and reports were redacted.
Detect-secrets 1.5.0 used 27 default plugins, ten default filters and disabled
network verification. It returned **258 kit observations and 1,939 delta
observations**, all hex entropy. Exact matched 40/64-character tokens were traced
to public source/hash fields or constants; remaining contexts were read manually.
These are contextual agent dispositions, not an absence proof or independent
security acceptance. Raw outputs and per-observation records remain private.

Replaying S4's original 202-file kit also returned 258 detect-secrets observations.
The S5 report's zero-observation coverage was not independently reproduced; use
these replay counts for final acceptance. Broader component screening still has
21 unresolved Gitleaks candidates and incompletely reconciled detector/semantic
observations, outside the kit. Runtime history, over-bound archives, binary/media
semantics, full hosted artifacts/logs and external collateral remain unexamined
as documented. Nothing here clears an expanded/full-source distribution.

Main's observed API state was protection disabled/check enforcement off;
rulesets returned empty and detailed administrative protection was inaccessible.
The always-run preview fix changes source only. No enforcement settings were
changed. OSS Scanner enrollment #640 is closed unmerged; no executed independent
scan is established by its enrollment/build checks.

## Proposed action and remaining work

After all applicable accountable gate dispositions and explicit owner
authorization, the proposed publication action is to upload **only the custom
ZIP named and hashed above** as a bounded source review kit. Do not create a
source tag/archive substitution, announce production readiness or select S1.
No such action is executed by this packet.

Remaining engineering:

- Repair and requalify S1's owning executor/consumer/provenance contracts before
  considering its proposed selection changes.
- Implement/qualify the external restore anchor if restore prevention is a
  required deployment property; characterization itself is complete.
- Regenerate inventory and screen deltas for any content/profile/package expansion.

External acceptance dependencies:

- Accountable rights and independent security/data/IP reviewers accept the exact
  kit or record explicit bounded exceptions and exclusions.
- Reporting owner confirms primary/backup, private escalation and retention, and
  supplies authorized delivery/acknowledgement/triage evidence. No exercise sent.
- Administrator exports effective rules, configures approved required checks and
  reviews, and demonstrates enforcement without bypass. No settings changed.
- Publication owner signs the exact source/manifest/package decision or retains
  HOLD. Production acceptance remains separate and unauthorized.

See the [unsigned operational acceptance form](../../verification/operational-acceptance-checklist-2026-10-15.md).

## Reconstruct the proposed bytes

Check out the frozen source, use the reviewed S4 inventory verifier with the
final manifest from this packet, and build into a new directory:

```sh
python tools/verify_publication_inventory.py --manifest /path/to/final-manifest.json --package /tmp/cognous-review-kit --build
```

Archive only those verified files using Python `zipfile`: sorted relative paths,
`ZIP_STORED`, fixed `(1980,1,1,0,0,0)` timestamps, `create_system=3`, and
`external_attr=0o100644 << 16`, without directory entries. The manifest and
verification record are sidecars, not ZIP members. Verify all member digests,
file count, archive size and SHA-256 against this packet before any later action.
