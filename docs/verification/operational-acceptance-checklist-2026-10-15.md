# S6 — Final operational acceptance form, lane F

**UNSIGNED / PENDING. Publication HOLD. Operational trust HOLD / NOT ESTABLISHED.**

Prepared by S6 as an evidence intake form, not an approval. Blank, proposed,
unchecked or unsigned fields grant no authority. Complete for one frozen preview
distribution; this form cannot authorize production. Change of source, profile,
package bytes, findings or relevant settings invalidates the corresponding review
until reconciled and signed again. See [S6 observations](operational-closeout-2026-10-15.md).

## Decision identity — coordinator must complete

| Required binding | Current entry / acceptance state |
| --- | --- |
| Final integrated hub source SHA | PENDING — S6 reviewed base `592919dd95396f3f6164cf0ceec1fd15c065691b`, not a final release source |
| Reviewed/tested PR head and merge/base SHA | PENDING — copy exact final head, tested merge ref, base, workflow revision and run attempt from final CI |
| Selected runtime profile | Observed `merged-producers-v1`; final-source confirmation PENDING |
| component-lock.json SHA-256 | Observed `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`; final-source match PENDING |
| Scoped bounded reference selection | Observed `profiles/bounded-v1-reference-release-selection.json`, SHA-256 `b3666dc24d20f2a85377ff509446b4124b5deb60510691b6263615dc55ef7535`; governor acceptance pending; not substituted for selected lock |
| W7 candidate lock | Observed SHA-256 `4ed11127adc0a05edde6ae3596ac552e0edb0f318b1177bac0c473ccfd1fca12`; separately scoped, not silently selected |
| Separately tested S1 nonselected candidate | BLOCKED / nonselected — draft [PR 122](https://github.com/cogno-us/cognous-open-control-stack/pull/122), head `d577b11a9ee4258fd097dc0abcc37a7deae218aa`; [exact report](https://github.com/cogno-us/cognous-open-control-stack/blob/d577b11a9ee4258fd097dc0abcc37a7deae218aa/docs/verification/remediation-candidate-2026-10-15.md) lists seven pins/interfaces; [run 38752535267](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38752535267) verified failed. S1 reports 13 pass/10 fail per repetition; artifact ZIP hash `07cb521bd54e60fa0684f21f2b78050bb809506d28805808d9df7f0bdaf556bf` is worker-reported, not independently rehashed by S6. Candidate profile hash: `c381cfa44ef93aee27f0bf4e4789d216369652a904c353efe6d36c899e6d21ea` (computed by S6 from exact Git blob). Owning-repository migrations and new qualification remain required; excluded from selected profile |
| S4 exact distribution manifest | PENDING — report path/head, manifest path/schema and SHA-256, package filename/size/SHA-256, inclusion/exclusion policy and verifier result |
| S5 safety screening | PENDING — report path/head/hash, screened source/package/manifest hash, methods, inspected and unexamined surfaces, unresolved finding IDs/severity and private evidence references |
| Reproduction evidence | PENDING — final-source runs, toolchain/dependency lock hashes, raw artifact SHA-256, test counts with skips/subtests separated, destination observations and limitations; historic October 13 acceptance alone is insufficient |
| Rights/notice review | PENDING — exact S4 manifest and notice ledger/hash, applicable grants, bundled dependencies, exclusions and accountable reviewer; no blanket Apache-2.0 characterization |
| Final claims and preview entry surfaces | PENDING — match packaged docs/announcement draft to actual verified scope; no announcement authorized here |

## Gate evidence — leave unchecked until reviewed

| Gate | Evidence to attach | Status |
| --- | --- | --- |
| PV-1 distribution/navigation/rights | S4 package inventory and rights disposition; final links/anchors and notice provenance | PENDING |
| PV-2 frozen source | Exact source/profile/lock/component pins, manifest and artifact hashes reconciled | PENDING for final source |
| PV-3 reproducibility | Final qualified runs and raw artifacts; historical versus current/optional evidence separated | PENDING for final source |
| PV-4 truthful boundaries | C0 check-to-commit limitation; optional same-host C1; no C2/C3 or real settlement; production HOLD visible | PENDING for final package |
| PV-5 screening | S5 scope, findings and unexamined surfaces; named safety reviewer disposition | PENDING |
| PV-6 reporting | Named primary/backup and private escalation, actual receipt/acknowledgement/triage attestation | PENDING — HTTP/MX alone insufficient |
| Repository enforcement | Admin export with timestamp, effective main rules/protection, required contexts and app, approvals, bypass restrictions, fail-closed verification | PENDING — observed main protection off; detailed protection API 403 |
| Optional remediation coverage | S1 candidate: exact failed run/report linked above; S2 ingress and S3 restore require separate exact integrated evidence | S1 BLOCKED; remaining acceptance PENDING; do not transfer proof to selected profile |
| Independent assessment | Scanner or other reviewer scope/results/limits, or explicit decision on unavailable evidence | PENDING — OSS Scanner #640 closed unmerged; scan not established |

## Reporting acceptance record — owner-run only

- Confirmed accountable primary (name/role/confirmation date): **PENDING**.
- Confirmed backup and private escalation route (restricted reference): **PENDING**.
- Authorization before exercise: approver, sender/recipient scope, time window,
  permitted observers and evidence reference: **PENDING**.
- Tested policy revision and route, synthetic token, send timestamp: **PENDING**.
- Delivery evidence including recipient arrival (private reference/hash): **PENDING**.
- Maintainer acknowledgement and timestamp (private reference/hash): **PENDING**.
- Private case classification, triager, closure and sanitized attestation: **PENDING**.
- Agreed escalation interval, retention/deletion duration and access scope: **PENDING**.
- Reporting review conclusion and limitations: **PENDING**.

No exercise was sent by S6. Never put raw mail headers, private contacts, secrets
or sensitive findings into this public form. Record restricted evidence identifiers
and sanitized attestations instead.

## Enforcement acceptance record — administrator only

- Settings observer, role, timestamp and effective organization/repository export: **PENDING**.
- Main branch scope and legacy protection/rules reconciliation: **PENDING**.
- Actual required check contexts, GitHub App identity and workflow revision: **PENDING**.
- Always-run coverage, uniqueness of names and fail-closed skip/cancellation test: **PENDING**.
- Latest push approval, stale-review dismissal, required independent reviews,
  conversation resolution and branch freshness: **PENDING**.
- Direct/force push/deletion restrictions, administrator applicability and bypass list: **PENDING**.
- Authorized harmless enforcement test evidence at exact head: **PENDING**.
- Merge queue, if any: **PENDING**; workflows at S6 base do not declare merge_group.
- Exceptions, expiry and restoration evidence: **PENDING**, not implicitly none.

## Technical limitations and exceptions

C0 retains a check-to-commit interval; optional C1 is same-host/cooperative.
No C2/C3, universal exactly-once external effects, business-intent deduplication,
external restore anchor, trusted institutional resolver/clock/custody or real
settlement acceptance follows from this form. Record S1–S5's additional limits.
Operational trust #30 remains HOLD / NOT ESTABLISHED.

Each proposed exception requires the following complete record before review:

| Field | Entry |
| --- | --- |
| Exception ID, affected gate/finding and exact source/package hash | PENDING |
| Missing evidence or violated requirement | PENDING |
| Risk, affected users/surfaces and bounded publication scope | PENDING |
| Compensating controls, exclusions and remediation owner/date | PENDING |
| Expiry/recheck trigger and withdrawal procedure | PENDING |
| Named accountable risk reviewer and explicit decision/signature/date | PENDING |

Duplicate this record for each exception. An empty record accepts no risk.
If no exceptions are proposed, a named reviewer must explicitly attest that
conclusion after reviewing all pending gates and findings.

## Accountable review and final decision — do not prefill approvals

| Responsibility | Named person and role | Exact evidence reviewed | Decision / signature / UTC date |
| --- | --- | --- | --- |
| Engineering/source qualification | PENDING | PENDING | UNSIGNED |
| Distribution and applicable rights | PENDING | PENDING | UNSIGNED |
| Safety/security screening | PENDING | PENDING | UNSIGNED |
| Reporting owner | PENDING | PENDING | UNSIGNED |
| Repository administrator | PENDING | PENDING | UNSIGNED |
| Independent reviewer | PENDING | PENDING | UNSIGNED |
| Accountable publication owner | PENDING | PENDING | UNSIGNED |

Final preview publication decision: **PENDING — no decision recorded**.
Approved scope, exact source/profile/manifest/package hashes, exclusions,
exceptions and publication mechanism: **PENDING**.
Decision expiry/revalidation triggers and accountable signature: **PENDING**.

Until completed and explicitly authorized through the governing process,
`reference_release_authorized=false` and
`production_deployment_authorized=false` remain unchanged. This form does not
edit selection files or grant credentials, runtime authority or production
permissions. Production authorization requires a separate deployment-specific
acceptance; even a later signed preview decision cannot clear that boundary.
