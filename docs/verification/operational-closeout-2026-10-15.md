# S6 — Operational closeout, lane F

**Disposition: PARTIAL / HOLD. This report grants no publication or production authority.**

Observed 2026-10-15 UTC. Reviewed hub `main` and isolated branch base:
`592919dd95396f3f6164cf0ceec1fd15c065691b`. Only this report and the
[acceptance form](operational-acceptance-checklist-2026-10-15.md) are proposed.
No tracked AGENTS.md was found. SECURITY.md, GOVERNANCE.md, CONTRIBUTING.md,
issue templates, all 35 tracked workflow YAML files, component-lock.json and
all four existing profile JSON files were read. Issues [68][board] and
[70][navigation], including the latter's comments, were read live. The initial
open-PR listing contained only [117][pr117], head
`d557112d2b3b6ccff75421e8276066c53422dcd8`; it was not selected or merged here.
The October 13 [acceptance checkpoint](../releases/publication-acceptance-2026-10-13.md)
and October 15 [remediation record](adversarial-review-remediation-2026-10-15.md)
are historical scoped evidence, not current-head clearance.

## Source identity and boundaries

The selected runtime remains `merged-producers-v1` in component-lock.json,
SHA-256 `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`.
The separate bounded reference selection file
`profiles/bounded-v1-reference-release-selection.json` hashes to
`b3666dc24d20f2a85377ff509446b4124b5deb60510691b6263615dc55ef7535`;
its candidate lock hashes to
`4ed11127adc0a05edde6ae3596ac552e0edb0f318b1177bac0c473ccfd1fca12`.
It retains pending governor acceptance and false reference-release/production
authorization fields. Do not promote it or S1's prospective nonselected candidate
by completing this form. S4 package inventory and S5 screening evidence were not
available in the reviewed tree or initial open-PR list; their exact report heads,
manifests and hashes remain pending coordinator intake.

Operational trust #30 remains **HOLD / NOT ESTABLISHED**. C0 checks are not atomic
with destination commit; C1 is optional, same-host and cooperative. No C2/C3
qualification, real settlement, production activation, release/tag or announcement
is authorized. Neither workflow success nor this report changes those boundaries.

## Reporting observations

Canonical policy: [SECURITY.md](../../SECURITY.md). The issue chooser's private
security contact links to that policy, not to a public vulnerability form.
The bounded feedback form requires revision and sanitized reproduction and warns
against sensitive reports. Blank public issues remain enabled. The
[triage guide](../security-reporting-and-triage.md) assigns Cognous repository
maintainers responsibility under GOVERNANCE.md; it requires a case maintainer
and private handling, but establishes no named primary/backup, confirmed coverage,
response SLA, escalation contact or evidence-retention period. A published policy
contact is not confirmation of staffed intake.

Fresh unauthenticated Python urllib HTTPS GETs completed at
`2026-10-15T14:26:29Z`; repeated parallel GETs returned matching observations.
No form, report or communication was submitted; no authenticated form was tested.

| Target | HTTP observation | What remains unverified |
| --- | --- | --- |
| [Public policy](https://github.com/cogno-us/cognous-open-control-stack/blob/main/SECURITY.md) | 200, same final URL | Mail delivery and recipient availability |
| [Security overview](https://github.com/cogno-us/cognous-open-control-stack/security) | 200, same final URL; retrieved HTML lacked `Report a vulnerability` text | Administrative private-advisory configuration; absence of text is not a settings audit |
| [Issue chooser](https://github.com/cogno-us/cognous-open-control-stack/issues/new/choose) | Final 200 at GitHub login, return-to points to chooser | Signed-in rendering and submission; final 200 is not anonymous access to the form |
| [MX lookup](https://dns.google/resolve?name=cogno.us&type=MX) | 200; answer `1 smtp.google.com.` (TTL 1800) | Individual mailbox acceptance, delivery, receipt, acknowledgement and private triage |

The dated [route JSON](../releases/reporting-route-verification.json) was read for
comparison, not used as a substitute for these fresh observations. No SMTP session,
mailbox probe, message, invitation or private-advisory submission was performed.

### Owner-run reporting exercise — proposed, not sent

1. Owner names and confirms a primary intake maintainer, backup and private
   escalation route. Confirm the mailbox currently advertised in SECURITY.md and
   approved sender; do not copy contact details into public evidence unnecessarily.
2. Obtain **explicit authorization before sending**, naming sender, recipient,
   time window, harmless payload, authorized observers, escalation interval and
   retention/deletion rule. This assignment does not authorize that communication.
3. Send through the canonical policy mailbox. Proposed subject:
   `Authorized synthetic intake exercise — S6 — <unique token>`.
   Proposed body: `This is an authorized synthetic reporting-route exercise, not
   a vulnerability report. Token: <token>. Repository: cogno-us/cognous-open-control-stack.
   Source: <final SHA>. No secrets, customer data or exploit content are included.
   Please acknowledge privately and record private triage ownership.`
4. Retain authorized sender delivery metadata, timestamp, message identifier and
   any bounce privately; obtain recipient-side arrival evidence and an explicit
   acknowledgement from the confirmed maintainer. A sender success or no bounce
   alone does not prove receipt. Record source-bound private case ID, classification,
   accountable triager and closure; do not post raw headers or message content publicly.
5. If acknowledgement is absent at the owner-approved interval, the sender/owner
   uses the agreed private escalation route and backup. No interval or SLA is
   asserted by this report. Agree retention duration and access permissions before
   sending, retain through acceptance/closure, then follow the agreed deletion rule.
6. Publish only a sanitized attestation identifying tested route, date, final SHA,
   evidence reference, receipt/acknowledgement/triage result and accountable reviewer.
   Missing evidence stays PENDING; update the policy separately if the route fails.

## Actual repository enforcement

Read-only connector GETs returned:

| Endpoint | Observed result | Interpretation |
| --- | --- | --- |
| [Rulesets collection][rulesets] | `[]` | No rulesets returned in this view; not proof that legacy protection is absent |
| [Main branch][branch] | `protected=false`; protection `enabled=false`; required status enforcement `off`, `contexts=[]`, `checks=[]` | Positive API evidence that main was reported unprotected, with checks off at observation time |
| [Legacy protection][protection] | 403, `Resource not accessible by integration` | Detailed legacy review, bypass and restriction settings could not be audited with this connection |
| `/repos/cogno-us/cognous-open-control-stack/rules/branches/main` | Connector 400 `INVALID_ARGUMENT`: endpoint not allowed | Effective branch-rules read unavailable through this connector; not a GitHub no-rules response |

A final branch refresh observed main advanced to
`0347d541939d1cc9a8dd3f2f07f7f3c7b029ee56`; it still reported protection disabled
and required checks off. This report remains scoped to its named S6 base; the
coordinator must reconcile intervening changes before final integration acceptance.

No settings were modified. Admin must inspect effective organization/repository
rules and legacy protection with administrative access, record export/time and
confirm applicability to main. Current workflow existence is not enforced policy.

Live [base check-runs][basechecks] returned 19 successful runs, including
`integrity`, `verify (3.11)`, `verify (3.12)`, `reference`, and several repeated
`qualify` matrix contexts. [PR 117 check-runs][prchecks] also demonstrated the
exact all-PR matrix names listed below, plus `aggregate` and `preview-audit`.
These are observations of other heads, not tests of S6's final head or inspection
of their artifacts. `Analyze (python)`, `Analyze (actions)` and PR `CodeQL` also
appear in API results; no tracked CodeQL workflow explains that configuration.
Admin must export the default/external scanning setup before making it a gate.

### Complete tracked workflow/job inventory at the reviewed base

Names below expand YAML matrices; live contexts were cross-checked for the
proposed required set using base and PR 117 check-runs. Other names are source-derived,
not a claim of executed jobs. `PR (paths)` / `push (paths)` means filtered:
the immutable workflow link is the authoritative exact path list. `manual`
means workflow_dispatch. No tracked job uses continue-on-error. All PR workflows
have no branch filter. Unless noted below, jobs have the default success condition.
`aggregate` in full-candidate and `V1 complete evidence gate` use `always()` with
matrix dependencies; manual-only diagnostic jobs are not automatic PR checks.

| Workflow source | Trigger conditions | Emitted job/check names |
| --- | --- | --- |
| [accepted-authority-effect.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/accepted-authority-effect.yml) | PR (paths), manual | `Linux / control-plane-focused`, `Linux / profile-compatibility`, `Linux / moltbot-focused`, `Linux / integration-1`, `Linux / integration-2` |
| [collateral-evidence-snapshot.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/collateral-evidence-snapshot.yml) | PR (paths), manual | `collateral-drift` |
| [comparative-governance.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/comparative-governance.yml) | PR (paths), push (paths) main, manual | `compare (1701)`, `compare (1702)` |
| [context-notification-recovery.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/context-notification-recovery.yml) | manual | `Linux / context-action`, `Linux / notification`, `Linux / recovery` |
| [contract-artifact-verification.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/contract-artifact-verification.yml) | PR, push main, manual | `verify (3.11)`, `verify (3.12)` |
| [deployment-review.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/deployment-review.yml) | PR (paths), manual | `packet-contract` |
| [destination-admission.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/destination-admission.yml) | PR (paths), push (paths) main, manual | `qualify (3.11)`, `qualify (3.12)` |
| [federated-governance.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/federated-governance.yml) | PR (paths), push (paths) main, manual | `qualify (3.11)`, `qualify (3.12)` |
| [feedback-provenance.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/feedback-provenance.yml) | PR (paths), manual | `provenance-contract` |
| [full-candidate-release.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/full-candidate-release.yml) | PR, manual | `qualify-linux (authority)`, `qualify-linux (exchange)`, `qualify-linux (consumers)`, `qualify-linux (registry)`, `aggregate` |
| [integrated-assurance.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/integrated-assurance.yml) | PR (paths), push (paths) main, manual | `qualify (3.11)`, `qualify (3.12)` |
| [lifecycle-inventory.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/lifecycle-inventory.yml) | PR (paths), manual | `inventory` |
| [merged-chain-candidate.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/merged-chain-candidate.yml) | PR, manual | `qualify-linux (3.11, recovery)`, `qualify-linux (3.11, transport)`, `qualify-linux (3.12, recovery)`, `qualify-linux (3.12, transport)` |
| [openappa-optional-compat.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/openappa-optional-compat.yml) | PR (paths), manual | `qualify` |
| [operational-state.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/operational-state.yml) | PR (paths), push (paths) main, manual | `qualify (3.11)`, `qualify (3.12)` |
| [optional-execution-profiles.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/optional-execution-profiles.yml) | manual, PR (paths) | `Linux / atomic-authority-effect`, `Linux / refund-intent` |
| [oss-scanner-readiness.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/oss-scanner-readiness.yml) | PR (paths), manual | `offline-build` |
| [paired-request-enforcement.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/paired-request-enforcement.yml) | PR (paths), manual | `qualify` |
| [preview-entry-audit.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/preview-entry-audit.yml) | PR (paths), manual | `preview-audit` |
| [process-boundary-qualification.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/process-boundary-qualification.yml) | PR (paths), manual | `qualify` |
| [protected-qualification.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/protected-qualification.yml) | PR (paths), manual | `qualify` |
| [reference-release.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/reference-release.yml) | PR, push, manual | `reference` |
| [release-integrity.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/release-integrity.yml) | PR, push main, manual | `integrity` |
| [research-assurance.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/research-assurance.yml) | PR (paths), push (paths) main, manual | `local-contracts (3.11)`, `local-contracts (3.12)` |
| [resolver-observation-assurance.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/resolver-observation-assurance.yml) | PR (paths), push (paths) main, manual | `observation-contract (3.11)`, `observation-contract (3.12)` |
| [semantic-handoff-contract.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/semantic-handoff-contract.yml) | PR (paths), push (paths) main | `contract` |
| [v1-reference-profiles.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/v1-reference-profiles.yml) | PR (paths), manual | `Linux / environment`, `Linux / governed-context`, `Linux / institutional-review`, `Linux / temporal-refund`, `Linux / context-action`, `Linux / notification`, `Linux / recovery`, `V1 complete evidence gate` |
| [w0-contract-fixture.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/w0-contract-fixture.yml) | PR (paths), manual | `golden-fixture` |
| [w7-final-composed.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/w7-final-composed.yml) | PR (paths), manual | `composed` |
| [w7-final-merged-c8.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/w7-final-merged-c8.yml) | PR (paths), manual | `exact-final` |
| [w7-p3-core-qualification.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/w7-p3-core-qualification.yml) | PR (paths), manual | `core-producers` |
| [w7-reference-release.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/w7-reference-release.yml) | PR (paths), manual | `exact-final` |
| [w7-release-preflight.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/w7-release-preflight.yml) | PR (paths), manual | `release-preflight` |
| [wire-budget.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/wire-budget.yml) | PR (paths), push (paths) main, manual | `test (3.11)`, `test (3.12)` |
| [worker21-authority-effect.yml](https://github.com/cogno-us/cognous-open-control-stack/blob/592919dd95396f3f6164cf0ceec1fd15c065691b/.github/workflows/worker21-authority-effect.yml) | PR (paths), manual | `qualify` |

### Gate weaknesses and coordinator patch proposal

- `preview-entry-audit.yml` filters PR paths; it omits the triage guide, releases
  directory and these verification documents. Its checker explicitly scans only
  eight entry pages and skips HTTP/mailto validation. This S6-only PR will not
  trigger that workflow. A required filtered workflow can leave a pending check;
  a green check cannot establish unexamined documentation coverage.
- Many workflows reuse `qualify` (including overlapping Python matrices),
  `Linux / <profile>` and `exact-final`. Requiring an ambiguous context is unsafe.
  Select unique contexts below; give any additional required job a unique name
  and verify the emitted check-run name on a fresh PR before configuring settings.
- `full-candidate-release.yml` aggregate uses `if: always()` and its verifier
  requires all four passing batches, suite repetitions and profile digest. It
  downloads artifacts within the run; success does not independently establish
  artifact security/rights. Cancelled or skipped prerequisite jobs must block
  acceptance. The proposed gate requires batch checks as well as aggregate.
- Several workflows check out GitHub's PR merge ref by default; the contract
  verifier explicitly checks out the PR head. Record both head SHA and tested
  merge SHA/base, run attempt and workflow revision. On any head/base update,
  rerun affected integration checks and renew source-bound review. A previous
  green run or stale approval cannot approve a moving head.
- No tracked workflow declares `merge_group`. Do not enable a merge queue that
  depends on these contexts until its workflows support and pass that event.

Smallest proposed coordinator patch (not applied by S6):

```diff
--- a/.github/workflows/preview-entry-audit.yml
+++ b/.github/workflows/preview-entry-audit.yml
@@ -1,17 +1,4 @@
 name: Preview entrypoint audit
 on:
   pull_request:
-    paths:
-      - 'README.md'
-      - 'docs/start-here.md'
-      - 'docs/quickstart.md'
-      - 'docs/governance-quickstart.md'
-      - 'docs/release-status.md'
-      - 'docs/preview-entry-audit.md'
-      - 'CONTRIBUTING.md'
-      - 'SECURITY.md'
-      - '.github/ISSUE_TEMPLATE/**'
-      - 'tools/check_preview_entries.py'
-      - 'tests/test_preview_negative_controls.py'
-      - '.github/workflows/preview-entry-audit.yml'
   workflow_dispatch:

```

This makes `preview-audit` available on every PR; it does not expand the
checker's coverage. Proposed companion patch to its explicit page list:

```diff
--- a/tools/check_preview_entries.py
+++ b/tools/check_preview_entries.py
@@ -10,3 +10,7 @@
          "docs/governance-quickstart.md", "docs/release-status.md",
-         "docs/preview-entry-audit.md", "CONTRIBUTING.md", "SECURITY.md"]
+         "docs/preview-entry-audit.md", "CONTRIBUTING.md", "SECURITY.md",
+         "docs/security-reporting-and-triage.md",
+         "docs/releases/publication-acceptance-2026-10-13.md",
+         "docs/verification/operational-closeout-2026-10-15.md",
+         "docs/verification/operational-acceptance-checklist-2026-10-15.md"]
 LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
```

Coordinator should apply the companion only after integrating these two documents,
then validate the positive audit and existing seven negative controls. If dynamic
S4/S5 pages are later included, integrate only once present. A stronger future
aggregate must fail on missing/cancelled/skipped required jobs and bind immutable
workflow, source, lock and artifact identities. Coordinator owns these shared edits.

### Proposed enforcement — admin action, not configured

Apply main protection to all changes, including administrators, after verifying
these check names and their GitHub Actions app provenance at the current head:

| Workflow | Proposed required check contexts |
| --- | --- |
| Release source integrity | `integrity` |
| Contract and candidate artifact verification | `verify (3.11)`, `verify (3.12)` |
| Reference release evidence | `reference` |
| Full candidate release matrix | `qualify-linux (authority)`, `qualify-linux (exchange)`, `qualify-linux (consumers)`, `qualify-linux (registry)`, `aggregate` |
| Merged chain candidate | `qualify-linux (3.11, recovery)`, `qualify-linux (3.11, transport)`, `qualify-linux (3.12, recovery)`, `qualify-linux (3.12, transport)` |
| Preview entrypoint audit | `preview-audit` **only after** removing the path filter and validating its actual scope |

Require PRs, two accountable approvals with at least one independent of the
change author, resolved review conversations, dismissal of stale approvals and
approval of the most recent reviewable push by someone other than its pusher.
Require up-to-date branches and the checks above; block force pushes/deletions and
direct pushes. Staffing and availability are not established by proposing this.
Protect workflows/checker changes with designated qualified reviewers; establish
CODEOWNERS or equivalent review routing separately (none is claimed here).
Default bypass list: empty, including routine admin merges. Any unavoidable
emergency exception needs named owner authorization, reason, exact SHA, omitted
check, bounded scope, expiry and compensating review in a sanitized exception
record; restore controls and rerun before normal publication acceptance. Never
allow that exception to confer production authority. Admin validates blocking
with a deliberately failing harmless PR in an authorized test branch/repository;
S6 performed no such mutation or settings change.

S1/S2/S3/S4 new workflows remain proposals until integrated and observed. Their
candidate qualification, ingress, restore and package checks must be linked at
final source and required by the acceptance decision where applicable. Do not
invent check contexts for workflows absent from this base.

## External OSS Scanner status

Live [PR 640][scanner] head `b24d0849189b9ed5f0db63dc998114e80c177af0`:
`state=closed`, `merged=false`, `merged_at=null`, closed
`2026-10-15T06:00:34Z`. The [maintainer comment][scannerclose] asks for evidence
of wider use, closes the request for now, and permits reopening if criteria fit.
No response or reopening was performed by S6. Its [reviews][scannerreviews]
collection was empty. [Checks at the enrollment head][scannerchecks] show
CLA, terms and gather/comment automation; these are not a code-security scan.

| Stage | Evidence-based disposition |
| --- | --- |
| Enrollment submitted | VERIFIED: PR 640 exists |
| Enrollment accepted/merged | NOT ACCEPTED: closed unmerged |
| Scan actually executed | NOT ESTABLISHED by inspected PR, comments or checks |
| Findings available | No scan finding report obtained from inspected public evidence; private provider/mailbox evidence inaccessible in this assignment |
| Findings reviewed/remediated | NOT ESTABLISHED; no finding set to reconcile |

Project Docker/offline validation and local `oss-scanner-readiness` workflow
test build readiness only. Neither they, enrollment triage, CodeQL success nor
a badge constitute a completed independent security assessment. If owner pursues
enrollment, substantiate actual usage against provider criteria and decide whether
to reopen; otherwise record its unavailable assessment without claiming coverage.

## S1 evidence intake follow-up — 2026-10-15

Follow-up base: `e335e5512fe8dd0a73637dcd8fd9c21ec235e43e`.
Live [draft PR 122](https://github.com/cogno-us/cognous-open-control-stack/pull/122)
was open/unmerged at head `d577b11a9ee4258fd097dc0abcc37a7deae218aa`.
S6 read the [exact-head S1 report](https://github.com/cogno-us/cognous-open-control-stack/blob/d577b11a9ee4258fd097dc0abcc37a7deae218aa/docs/verification/remediation-candidate-2026-10-15.md)
and verified that [run 38752535267](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38752535267)
concluded **failure** at that same head. Candidate integration is **BLOCKED**;
report availability does not establish qualification. Historical S1-pending
statements above describe initial intake, superseded for this candidate by this section.

S1 reports two local and two hosted repetitions, each with 23 testcase elements:
13 passed, 10 failed, no errors/skips/subtests. S6 did not rerun that integration
or independently download/recompute its 399-file artifact manifest. The worker's
reported ZIP SHA-256 is
`07cb521bd54e60fa0684f21f2b78050bb809506d28805808d9df7f0bdaf556bf`;
independent artifact-content/checksum review remains pending. The exact report
lists all seven pins, interface versions and minimal reproductions.

Required owning-repository actions, coordinated outside S6:

1. Executor: preserve each call's actual durable refusal, typed reasons and bindings.
2. Replay: qualify the actual new CP/executor revisions and preserve refusal,
   resolution-check, time-floor and closeout fields; an allowlist-only change is insufficient.
3. ODES/Evidence Pack: migrate exact source extraction and revalidation without
   suppressing reconstruction disagreement or unknown-data warnings.
4. Governed Exchange: add truthful opt-in candidate provenance and exact consumer
   pins; preserve historical merged-producers-v1 semantics and store ownership.
5. Rerun the same S1 candidate against the resulting merged revisions; retain raw
   failures and exact source/artifact hashes for a new selection decision.

Zero-effect refusals and store-local ownership checks do not repair downstream
lineage gaps or the unsafe C0 check-to-commit race. The candidate remains
nonselected, does not replace the publication profile, and grants no authority.
This follow-up changes no central control panel, shared release record or component.
Current follow-up base already includes coordinator changes to the preview audit;
its local run now checks 13 pages / 127 local references, including these S6 files.
The original eight-page coverage and patch proposal above remain historical.

## Validation and remaining actions

Local baseline validation passed: eight preview entry pages / 113 local links,
seven preview negative controls, source integrity check, two W7 selection tests
and six collateral tests. Final-head commands/results and hosted run identity
are recorded in the PR handoff, avoiding a self-referential commit hash here.
The existing preview checker does not include these new files; their relative
paths/anchors and cited source identities were separately checked. No runtime,
full selected-chain execution, scanner execution or repository-settings test is
claimed by this documentation lane.

1. **Owner:** confirm primary, backup, private escalation and retention; authorize
   and run the harmless exercise, or supply actual authorized delivery/response
   evidence. Confirm independent reviewer availability without implying an SLA.
2. **Admin:** export effective enforcement/default scanning settings, apply
   approved protection and verify fail-closed behavior after coordinator fixes.
3. **Coordinator:** integrate S1–S5 evidence serially, freeze final source and
   actual distribution, complete exact-head checks and link S4/S5 hashes in the form.
4. **Rights and safety reviewers:** review that exact distribution and unresolved
   findings; record dispositions and explicit exclusions without invented clearance.
5. **Accountable publication owner:** complete and sign the source-bound form
   with explicit exceptions or retain HOLD. Production remains separately gated.

[board]: https://github.com/cogno-us/cognous-open-control-stack/issues/68
[navigation]: https://github.com/cogno-us/cognous-open-control-stack/issues/70
[pr117]: https://github.com/cogno-us/cognous-open-control-stack/pull/117
[rulesets]: https://api.github.com/repos/cogno-us/cognous-open-control-stack/rulesets
[branch]: https://api.github.com/repos/cogno-us/cognous-open-control-stack/branches/main
[protection]: https://api.github.com/repos/cogno-us/cognous-open-control-stack/branches/main/protection
[basechecks]: https://api.github.com/repos/cogno-us/cognous-open-control-stack/commits/592919dd95396f3f6164cf0ceec1fd15c065691b/check-runs
[prchecks]: https://api.github.com/repos/cogno-us/cognous-open-control-stack/commits/d557112d2b3b6ccff75421e8276066c53422dcd8/check-runs
[scanner]: https://github.com/anthropics/oss-scanner/pull/640
[scannerclose]: https://github.com/anthropics/oss-scanner/pull/640#issuecomment-6185592346
[scannerreviews]: https://api.github.com/repos/anthropics/oss-scanner/pulls/640/reviews
[scannerchecks]: https://api.github.com/repos/anthropics/oss-scanner/commits/b24d0849189b9ed5f0db63dc998114e80c177af0/check-runs
