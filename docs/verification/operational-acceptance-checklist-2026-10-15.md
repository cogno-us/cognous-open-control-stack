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
| Final integrated hub source SHA | Current reviewed engineering source `d516d73fbe579a81a3805c2f2df9dfa2ce594b38`; historical package remains frozen to `e335e5512fe8dd0a73637dcd8fd9c21ec235e43e`. Final publication source selection and delta acceptance PENDING |
| Reviewed/tested PR head and merge/base SHA | PENDING — copy exact final head, tested merge ref, base, workflow revision and run attempt from final CI |
| Selected runtime profile | Verified `merged-producers-v1` at current reviewed engineering source; publication-source confirmation PENDING |
| component-lock.json SHA-256 | Observed `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`; verified equal at current reviewed engineering source; final publication-source match PENDING |
| Scoped bounded reference selection | Observed `profiles/bounded-v1-reference-release-selection.json`, SHA-256 `b3666dc24d20f2a85377ff509446b4124b5deb60510691b6263615dc55ef7535`; governor acceptance pending; not substituted for selected lock |
| W7 candidate lock | Observed SHA-256 `4ed11127adc0a05edde6ae3596ac552e0edb0f318b1177bac0c473ccfd1fca12`; separately scoped, not silently selected |
| Historical S1 nonselected candidate (failed original generation) | BLOCKED / nonselected — draft [PR 122](https://github.com/cogno-us/cognous-open-control-stack/pull/122), head `d577b11a9ee4258fd097dc0abcc37a7deae218aa`; [exact report](https://github.com/cogno-us/cognous-open-control-stack/blob/d577b11a9ee4258fd097dc0abcc37a7deae218aa/docs/verification/remediation-candidate-2026-10-15.md) lists seven pins/interfaces; [run 38752535267](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38752535267) verified failed. S1 reports 13 pass/10 fail per repetition; artifact ZIP hash `07cb521bd54e60fa0684f21f2b78050bb809506d28805808d9df7f0bdaf556bf` is worker-reported, not independently rehashed by S6. Candidate profile hash: `c381cfa44ef93aee27f0bf4e4789d216369652a904c353efe6d36c899e6d21ea` (computed by S6 from exact Git blob). Superseded for current compatibility by repaired nonselected full-reference evidence below; this original head remains failed and excluded from selected profile |
| Repaired nonselected full-reference candidate | Profile `profiles/remediation-full-reference-20261015.json`, SHA-256 `a4baef7134fb84fd2a753522c99caca63ab4e2cd735d5386ade37301d6d2f4bc`; hub tested head `ee51dbed785dd393d2639f0ab52e373b9e930393`; suite `5eebdc16ef3248a19df58ff27b9d8e9056026eb3`; [run 38781363275](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38781363275), aggregate ZIP SHA-256 `37aa95d308141307512b9e1f0d232f81a0cc7d8a2c3ca818b632893c44c75d02`: 34 pass + one characterized unsafe C0 limitation; not selected, no release authority |
| S4 exact distribution manifest | S0 final refresh: [manifest](../releases/final-closeout-20261015/manifest.json), SHA-256 `b1805bac8990676c17222d10e18810dbcd346a1003b3e4d67936efb997318d99`; 206 included / 463 excluded; ZIP SHA-256 `1c9ae8af9d313cfde478c6e1bb46f58e563845f9ae22b6c56c86670b57b33faf`; technical verification passed, accountable acceptance PENDING |
| S5 safety screening | [S5 report](safety-closeout-2026-10-15.md) at current engineering source, SHA-256 `78f30c6c05885f11b44c81d4bd134e07387b9e3c0ce21203e2438d1612fc2a4f`; S0 replay supersedes original zero-count interpretation: kit 258 entropy observations contextually traced to public hashes; 21 broader Gitleaks candidates and semantic/excluded surfaces unresolved. New package/source delta and independent acceptance PENDING |
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
| Optional remediation coverage | S1 candidate: exact failed run/report linked above; S2 ingress and S3 restore require separate exact integrated evidence | Historical S1 head failed; repaired full-reference qualification passes its defined gate; selection and remaining acceptance PENDING; no proof transfer to selected profile |
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

## S0 source-bound technical intake

See [final packet](../releases/final-closeout-20261015/README.md) and its
[verification record](../releases/final-closeout-20261015/verification.json) for
exact integrated source, package bytes, S1 failure evidence and scoped gate
dispositions. Technical bindings above do not complete any unsigned owner,
independent reviewer, rights, security, reporting or administration decision.
All signatures and final publication authority remain PENDING.

## Final engineering closeout intake

See [final S6 checkpoint](operational-closeout-2026-10-15.md#final-s6-checkpoint--2026-10-15-1815-utc)
for merged compatibility fixes, exact tested heads/artifacts, post-merge workflows,
fresh reporting/settings observations and the current proposed required contexts.
The historical unprefixed contexts must not be copied into settings. Resolve
colliding reusable-workflow names before enforcing the proposed set. The original
206-file S4/S0 manifest and ZIP hashes above are historical exact-byte evidence;
they do not cover current main or the canonical qualification repository by default.
All approvals, risk acceptance and final publication decision remain UNSIGNED.
