# Public release blocker verification — 2026-10-13

Verified source: `9a3772783e4f08d206268bd9650b16395adb546a`.
Selected profile: `merged-producers-v1`; original lock SHA-256
`dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`.
This is newly executed evidence, not a relabeling of the October 10 reports.
It does not authorize release, select newer components or lift operational HOLD.

## Result

| Blocker | New evidence and disposition |
| --- | --- |
| PV-3 clean selected reproduction (#69/#85) | **Executed and passed** in a fresh GitHub clone with Python 3.11.17 / Node 20.20.2; raw results and additional retained negative destinations are now disclosed with explicit owner approval; formal acceptance remains open |
| PV-2 exact evidence | Original lock and actual selected pins verified; both repetitions, matrix, JUnit, skip accounting, repeatability and destination rows inspected; separate from final publication acceptance |
| PV-5 publication screening (#73/#86) | **Partial, materially advanced**: actual versioned secret scans of hub history, reachable blobs, frozen tree and two evidence populations; no confirmed credentials in the examined findings; semantic PII/IP and full external distribution coverage remain open |
| PV-1/PV-6 distribution and navigation (#70/#87) | 35 entrypoint HTTP targets checked; 32 returned 200, three required a private repository. Public entry links now use a public HOLD-status page. Selected license exceptions and actual reporting-route delivery remain open |
| Final publication | **Not authorized by this report.** Owner acceptance must name exact artifacts and resolve or explicitly disposition remaining gates; no production approval |

## Fresh local reproduction and retained evidence

The previous missing-toolchain/DNS block no longer applied. A new clone from
GitHub was detached at the source above. The run used an isolated Python venv
and Node 20 on Linux x86-64, without reusing the older `.reference-work` or
results. Python 3.11.17 was installed through uv; the official Node 20.20.2
archive was checked against its published SHA-256. No repository dependency
pins were changed. All tracked source files remained clean after execution.

```sh
git checkout --detach 9a3772783e4f08d206268bd9650b16395adb546a
python --version  # Python 3.11.17 in isolated venv
node --version    # v20.20.2
python tools/reference_release.py run --results-dir results/independent-20261013
```

The command completed with exit 0, `release_gate_passed=true`,
`release_qualified=true` for the existing selected synthetic profile, and
`representative_repeatability=true`. These runner fields are bounded technical
results, not public-preview or production authorization.

- Each repetition contains **1,009 passing Python testcase elements**, no
  failures/errors/skips. The runner reports **1,014** from JUnit suite attributes:
  `index_bitrep_binding.xml` declares 17 tests but contains 12 testcase elements,
  reflecting five `unittest.subTest` increments. Its terminal log says 12 passed.
  Do not describe the difference as five additional independent test functions.
- The separately logged Node local-chain suite reports **20 passing TAP tests**
  per repetition, no failures/skips. Do not fold it into the Python XML count.
- The matrix resolves **35 scenarios: 34 passed safety invariants and one
  characterized business-intent deduplication limitation**. That limitation is
  `not_established`, not a prevented duplicate. Skip accounting is empty.
- Both representative destinations were opened with SQLite `mode=ro`: each
  contains one applied synthetic USD 50 effect, one attempt and two attempt
  events. Expected/observed JSON reports no mismatches and retains the original
  source-to-consumer artifact relationship.
- Three additional existing pinned GAX tests were run with a fresh retained
  `--basetemp`, all passed. Read-only inspection found zero effects/attempts/
  events for missing resolver and revoked authority; lost-Ack redelivery retained
  one applied effect, one attempt and `attempted`/`unknown` events. The tests and
  databases are preserved separately, not added to the full-run totals.

The raw reproduction archive (189,636 bytes), SHA-256
`6f7baf4413b8c8293ff318457bae5ac68a2dba0226c8452903527ce805b8083a`,
and [detailed verification record](../../examples/public-release-verification-20261013/verification.json)
are now available in the [approved evidence package](../../examples/public-release-verification-20261013/README.md).
The owner explicitly approved disclosure on 2026-10-13; the original bytes are preserved. The archive contains result trees, JUnit/logs/JSON,
representative SQLite files, retained negative destinations, toolchain metadata
and Python package versions. Execution passed, but public evidence acceptance
remains open pending formal review; disclosure approval alone is not acceptance.

The separately downloaded [hosted reference run 38419632422](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38419632422)
belongs to PR #95 head `1ab222f6d8bbbe37d6f4fae170e85a6cd4304da1`.
Artifact `11826920684` ZIP digest
`0101855a4ce4d615afc2ead1cde94d1b950c487875fd4bf592a52954caa03caf`
was independently recomputed. Its two repetitions, scenario resolution and
representative destinations were inspected separately; they were not used as
the fresh local execution. Neither run is a new W7 candidate selection.

## Actual secret screening

Gitleaks **8.30.1**, official Linux x64 distribution SHA-256
`551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`,
was checked against the release checksum before use. The explicit configuration
extends default rules, uses an empty ignore file, ignores repository allow
comments, redacts findings 100%, enables archive depth 3 and decode depth 5,
and does not validate candidate credentials against live providers.

| Surface | Executed coverage | Findings |
| --- | --- | --- |
| Available hub Git history | 77 local/remote refs, 373 reachable commits; Gitleaks diff scan reports 308 non-merge commits | 0 candidates |
| All reachable hub blobs | 882 unique blobs, 21,911,589 stored bytes exported by object ID with filename extensions preserved; separate scan covers merge-only content not established by a diff scan alone | 0 candidates |
| Frozen hub source tree | 538 tracked files, including existing archives and SQLite samples; nested archive traversal enabled | 0 candidates |
| Downloaded selected CI evidence | Verified archive above, extracted then scanned | 32 generic-key candidates, all classified as synthetic test identifiers |
| New local evidence | Newly generated results scanned before archival | Same class of 32 synthetic candidates; no confirmed credentials |

Every artifact candidate was checked against the pinned Control Plane
`tests/test_record_store_concurrency.py`: the field named `token` is a generated
observation identifier, equals the synthetic effect ID, and belongs to an
`absent` test observation. This is a specific false-positive disposition, not a
blanket ignore rule. No credential values or raw candidate reports are published.

Coverage limits remain material: Gitleaks is not a general customer-PII or
proprietary-IP classifier. Binary/SQLite pattern scanning is not semantic review
of every field, and archive depth is bounded. Unreachable Git objects, other
component histories, all prior Actions artifacts/logs, external mirrors and
private-IP comparison were not comprehensively reviewed. No tags were present
in the clone; the release API returned no published releases at inspection.
There is no independent human publication-security signoff. Preserve PV-5 as
PARTIAL rather than substituting a zero secret count for complete clearance.

The [security policy](../../SECURITY.md) now describes the actual qualification-tooling
scope without a categorical absence claim. The owner approved this correction
and preservation of the existing private reporting address on 2026-10-13.
The bounded scans do not establish categorical absence or mailbox delivery.

## Distribution and public navigation

All 13 selected component trees were inventoried locally at their exact SHAs.
The approved machine-readable record includes license/notice and security-policy
paths. The previously reported exceptions remain: selected PRP and TFA have no
tracked license/notice-named files; four components have no tracked security
policy, and Index has an alternate `docs/SECURITY.md`. Later licensing commits
were not silently substituted for the selected source. Runtime remains mixed
MIT/Apache with nested third-party notices. This is a technical inventory, not
legal clearance or a transitive dependency bill of materials.

For a near-term **hub-and-evidence-only** publication, the concrete artifact
scope proposed here is hub-owned documentation/qualification tooling plus the
synthetic output archive, with owner-approved evidence disclosure. The archive does not bundle cloned component
source, Python/Node installations, `node_modules`, wallets or credentials.
Optional PRP/TFA source must not be included in a distribution until its rights
exception is resolved. Reproduction still references their selected commits;
excluding a component from an archive does not change the lock or grant rights.
Any broader component bundle still requires its own license/notice review.

Direct HTTP GET checks covered Markdown links in the eight preview entry pages,
plus the issue chooser: **35 distinct targets**. Thirty-two returned 200. An
initial 503 and two 404s became three 404s on recheck, all in the orchestrator
repository. Authenticated metadata confirmed that repository is private; its
issue #30 and named report exist for authorized users. These were inaccessible
public routes, not deleted evidence. No restricted report content is copied here.

The current entry pages and issue chooser configuration now point to the
[public operational trust status](../operational-trust-status.md), preserving
#30 HOLD. The newer O5/O6 route is explicitly outside selected public scope.
The original HTTP results and redirect destinations remain in the verification
record. Local links/anchors in the revised pages are separately checked by CI;
new public URLs must also be checked after merge. This is not a crawl of every
historical report or external mirror. The chooser returned HTML successfully;
no issue was submitted and no test email was sent. Mailbox delivery, maintainer
response and private vulnerability triage therefore remain unverified.

## Remaining release decision

The clean execution requirement passed for the exact selected profile and
source above; disclosure is owner-approved, while formal evidence acceptance remains open. Keep publication safety and distribution/reporting open for their
explicit residuals. A maintainer must approve the concrete artifact scope,
resolve rights/notice exceptions for anything shipped, confirm the reporting
route, and accept the final claims and any recorded exceptions. This report
does not manufacture that approval.

C0 retains its check-to-commit limit; optional same-host C1 is not remote
atomicity. C2/C3, real settlement and production deployment remain unqualified.
Operational trust #30 stays **HOLD / NOT ESTABLISHED**. No release/tag,
announcement, invitation, credential, grant or real effect was issued.

## Subsequent technical review

The [publication acceptance checkpoint](../releases/publication-acceptance-2026-10-13.md)
accepts the bounded PV-2/PV-3 technical verification after reviewing the approved
raw archive, pins, counts and destinations. Earlier statements above about formal
review being pending describe this report’s original disclosure checkpoint. Final
release-owner acceptance, security and distribution/reporting residuals remain open.
