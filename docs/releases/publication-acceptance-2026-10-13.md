# Publication acceptance checkpoint — 2026-10-13

**Final publication: HOLD. No release/tag or production authorization.**
Reviewed main: `f076f5f0cf085546dfa6c1d70f34b22c278c5fd0`.
Execution source: `9a3772783e4f08d206268bd9650b16395adb546a`.
Selected profile remains `merged-producers-v1`; OpenAPPA remains closed for now.

This checkpoint accepts the bounded technical verification tasks below. It does
not supply independent human security/legal signoff or the final owner release
decision. Earlier environment and disclosure blockers are resolved; do not keep
reporting them as missing prerequisites. Remaining uncertainties are explicit.

## Technical gate disposition

| Gate | Technical disposition | Evidence / remaining condition |
| --- | --- | --- |
| PV-1 navigation/licensing | PARTIAL | Local entry checks and public policy routes verified; 28 original notice/license files retained from all 13 selected trees. Selected PRP/TFA source and transitive dependency distribution remain unaccepted. |
| PV-2 frozen snapshot | PASS for the named selected evidence | Source ancestry, unchanged qualification paths, selected lock, all 13 actual pins, archive and verification-record hashes match. This does not select W7 or newer components. |
| PV-3 reproducible example | PASS for the named synthetic execution | Original fresh run and published raw bytes reviewed; two repetitions of 1,009 Python testcase elements, separate 20 Node TAP tests, 34 passed invariants plus one characterized limitation, representative and negative destination states retained. No new execution is claimed by this checkpoint. |
| PV-4 truthful disclosure | PARTIAL | C0 race, optional same-host C1, no C2/C3, no real settlement and operational HOLD retained on reviewed entry paths. Final promotional/package surfaces must match the actual publication scope. |
| PV-5 publication safety | PARTIAL / HOLD | Bounded secret scans and synthetic-candidate dispositions are recorded; full semantic PII/IP, remaining distribution surfaces and independent security acceptance remain incomplete. |
| PV-6 reporting and feedback | PARTIAL | Public policy, sign-in boundary and mail-domain MX verified; maintainer intake documented. Individual mailbox delivery/acknowledgement and private-report handling remain unverified. |

PV-2/PV-3 close bounded verification work in #72/#69/#85. Final release-owner
acceptance remains on [#68](https://github.com/cogno-us/cognous-open-control-stack/issues/68).
No gate is risk-accepted by implication and no six-gate GO is claimed.

## Root, source and evidence verification

The [root-verification record](publication-root-verification.json) captures the
exact comparisons. Root means content/source identity here, not operational
trust-root custody, signer authorization or production environment assurance.

- `git merge-base --is-ancestor` verifies execution source is an ancestor of the reviewed main.
- `git diff --name-only` across that interval reports no changes in `tools`, `tests`,
  `schemas`, `scenarios`, `component-lock.json` or `profiles`.
- SHA-256 of the selected lock is
  `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`.
- All 13 selected SHAs match both archived `component-pins.json` and actual pins
  in `scenario-results.json`; Execution Runtime uses `accepted_sha`.
- The original 189,636-byte archive hash is
  `6f7baf4413b8c8293ff318457bae5ac68a2dba0226c8452903527ce805b8083a`.
  A post-merge unauthenticated download was independently hash-checked in the
  disclosure closeout. The new record also hashes the unchanged verification JSON.
- Raw XML, resolved matrix, empty skip accounting, repeatability and both
  expected-versus-observed files were inspected. Their failures lists are empty.
  Five extra suite-attribute increments are subTests, not independent testcases.
- Read-only SQLite review confirms one synthetic effect per representative and
  lost-ack destination; missing resolver and revoked authority retain zero effects.
- All four exact-head workflows for disclosure PR #97 completed SUCCESS at
  `8320b3179ff4cebdc46ad9c3e93fb80e1323cf90`: preview `38444156372`, merged chain
  `38444156344`, full matrix `38444156460`, reference `38444156313`.

These checks establish identity and bounded behavior, not business-intent
deduplication, remote commit atomicity, production trust or comprehensive safety.

## License and notice disposition

The [selected notice ledger](selected-notices/README.md) and
[hashed source inventory](selected-notices.json) preserve 28 unmodified files.
Full nontruncated selected Git trees were enumerated; copied bytes were checked
against their Git blob IDs and SHA-256. This includes runtime nested notices,
MIT upstream attribution and the selected CC BY 4.0 institutional-governance terms.
It is not a transitive dependency SBOM or an assertion of all third-party rights.

Do not relabel the selected stack as wholly Apache-2.0. The hub's later-license
inventory cannot silently relicense older PRP/TFA revisions. Those selected
source trees/historical PDFs remain excluded from a proposed component bundle
until an applicable grant or separately approved selection resolves the exception.
No source pins change in this disposition.

## Concrete publication scope for final review

Candidate: the named hub source, its documentation/qualification tooling,
root LICENSE/NOTICE, retained selected notices and the already approved evidence
package at `examples/public-release-verification-20261013/`.

Excluded: external component source bundles, optional PRP/TFA source/PDFs,
installed Python/Node dependencies, toolchains, wallets, credentials, production
configurations and any private orchestration/IP material. The normal reproduction
runner fetches external sources separately; this scope does not certify their
redistribution rights or change what the selected runner tests.

The existing hub contains earlier examples/artifacts. The narrow notice inventory
and fresh evidence review do not supply complete rights or semantic safety
clearance for every historical payload. A final release artifact inventory must
list what actually ships; a source tag alone would include all tracked files.
Do not describe this candidate scope as an already approved release package.

## Reporting disposition

The issue chooser now points directly to the canonical SECURITY.md policy.
The [route observations](reporting-route-verification.json) distinguish direct
HTTP 200 from a login redirect. The retrieved security page showed no private
report button; its absence is not an administrative setting audit. Mail-domain
MX resolves, but no mailbox delivery or maintainer acknowledgement was tested.
[Reporting and triage](../security-reporting-and-triage.md) defines private/public
separation and Cognous maintainer responsibility without inventing an SLA.

## Remaining owner/security decisions

1. Complete or explicitly disposition the actual package's semantic PII/IP and
   distribution-safety review with an accountable reviewer and exact scope.
2. Resolve selected PRP/TFA and dependency rights for anything actually bundled;
   preserve the explicit exclusion if publishing a narrower package.
3. Obtain maintainer confirmation of reporting ownership and delivery/response,
   or separately authorize an acknowledgement exercise. No message was sent.
4. Freeze the final source/profile and complete artifact inventory, reconcile all
   six gates (including any explicit exceptions), and obtain final owner signoff.

`reference_release_authorized=false` and `production_deployment_authorized=false`
remain unchanged. Operational trust #30 stays **HOLD / NOT ESTABLISHED**.
