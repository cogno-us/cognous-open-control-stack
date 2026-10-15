# U1 security correction verification

## Disposition

Seven scoped corrections are implemented and locally verified as review candidates.
Source integration remains pending: merge [qualification PR 10](https://github.com/cogno-us/cognous-stack-qualification/pull/10)
before [hub PR 141](https://github.com/cogno-us/cognous-open-control-stack/pull/141).
Neither PR is merged by U1. Component selection, release permissions and operational
trust remain unchanged. Operational trust is **HOLD / NOT ESTABLISHED**.

The original scan examined hub `5715f791f9f127506416e9a19bea8eff9231f701` under scan
`8a85574c-2aa7-46f0-b4b7-fada217d573a`. All seven findings retain the scanner's
**low severity, high confidence** classification under its trusted-host assumptions.
Engineering order reflects dependencies, not a severity reclassification.

## Exact source identities

- Starting hub main: `80046e78e9b83e1ea06cbdfb8cda78acd2339e4e`.
- Published, clean, locally tested hub code: `c3b919d1053442e992d499b1766ee0bf8acc768b`.
- Qualification main incorporated: `bcbbd5ae85e49cf9adc8c379ba7a2664eef04c9e`.
- Published, clean, locally tested suite: `78b3f42c93fa3aef64e2fd2216bbdf545db5b0af`.
- Hub CI setup correction: `b404ebcfcd9f008096d95b668d2bd699603fb9cd` changes only
  `.github/workflows/security-corrections.yml` to fetch full Git history.
- This report is a later evidence-only addition; it does not replace those tested
  source identities with a claim that every descendant was re-executed locally.

The connector-published code trees were checked against the corresponding local
Git trees. Final local tests used fresh worktrees of the published commits.
Cross-component execution used a disposable hub checkout plus the exact suite's
76-file overlay. The assembly receipt records both commits, overlay hashes and
changed workflow stubs; assembled source is intentionally distinct from a clean
unoverlaid hub checkout. The canonical suite itself was clean.

## Finding closure matrix

| Work | Stable finding ID | Correction and verification | Candidate disposition |
|---|---|---|---|
| SEC01 | `csf_704a0db129e128b21291679d` | Shared exact-commit and pristine-input checks reject staged, unstaged, untracked and ignored files plus escaping tracked symlinks. Python environment is controlled. Applied to optional, merged, protected, remediation, reference-release and Worker 21 runners in their current qualification owner. Four real-Git regression tests; clean optional and merged runs pass. | Corrected and locally verified; owning PR 10 and hub consumer PR 141 pending. |
| SEC02 | `csf_abc379804b44d3622ef34086` | Bounded detached JSON snapshots precede resolver/context hashing; journals reject count mismatch before visiting details. Boundary tests and instrumentation prove early rejection; valid fixtures preserve canonical bytes. | Corrected and locally verified. |
| SEC03 | `csf_9e04a13b6aa33a8ec0411322` | Identity-bearing envelope, policy, disclosure, parent, evidence and registry keys require exact bounded strings before container use and signatures. Boolean/numeric/null/empty/oversized/unhashable cases reject. | Corrected and locally verified. |
| SEC04 | `csf_07d0823a169258954007c0a0` | Duplicate identities leave the envelope invalid and skip repeated signature and commitment work. Instrumented conflicting and repeated duplicates exercise this invariant. Existing outer wire limits remain. | Corrected and locally verified. |
| SEC05 | `csf_2ec36c89c1fd4ca82b5cb6a6` | Persistent global/anonymous/principal/source budgets, event size and database page ceilings. Anonymous source churn cannot grow tracking rows; counters saturate. Restart, concurrency, actual SQLite page exhaustion and injected audit failures preserve zero effects and rollback. | Corrected and locally verified for the HMAC reference profile. |
| SEC06 | `csf_6ddf5468faba05833d8cede9` | Primary trust evidence uses the public status page. Current relative navigation checks and deliberately private-link regression pass. Anonymous HTTP status-page check returned 200. | Corrected and locally verified for the named entry surface. |
| SEC07 | `csf_16da46683c091829a28e0f39` | Selected transport link matches current lock. Validator rejects deliberate selected-link drift while retaining historical revisions. Anonymous selected-transport check returned 200. | Corrected and locally verified for the selected architecture table. |

## Executed validation

Local environment: Linux x86_64, Python 3.12.14, SQLite 3.53.1. Package versions,
JUnit, scenario receipts and assembly metadata are retained in the
[qualification evidence directory](https://github.com/cogno-us/cognous-stack-qualification/tree/fix/u1-qualification-source-integrity/results/u1-security-20261015).
Counts below are separate populations and must not be summed into release coverage.

| Command or program | Actual result |
|---|---|
| `python -m pytest -q` on published clean hub code | 627 passed; 122 separate subtests passed; zero failed/errors/skips. |
| `python -m unittest discover -s tests -v` on published clean qualification code | 44 passed. Test fixtures intentionally emitting FAIL/INCONCLUSIVE sample manifests are negative controls, not suite failures. |
| `python tools/validate_migrations.py` | 194 original files and 50 workflow mappings validated; original attribution and licenses retained. |
| `python tools/integrated_assurance_qualification.py --results-dir OUT` | 51 testcase elements pass, nine control-removal groups detected, `local_qualified=true`, no tracked source changes. |
| `python tools/resolver_assurance_qualification.py` | 20 tests pass, `qualified=true`, no tracked source changes. |
| Integrated, research, federated, operational and destination mutation programs | All five batteries complete successfully; 9, 4, 8, 7 and 13 controls respectively detected. |
| Optional atomic-authority-effect profile | Allowed and revoked cases pass using pristine exact component checkouts. Separate SQLite reads show 1 and 0 effects. |
| Optional refund-intent profile | Allowed, revoked, same-intent and distinct-intent cases pass. Separate SQLite reads show 1, 0, 1 and 2 effects. |
| Merged-chain recovery | Two repetitions; each 26 tests pass with no failures/errors/skips. |
| Merged-chain transport | Both repetitions pass; normalized outputs match. |
| Qualification gate tests | 92 pass on identical executable source before the published-identity rerun. |
| Current documentation validator | Selected revision link and local navigation checks pass; explicit stale and private-link negative cases pass. |

Reproduction commands for cross-component tests follow the current install-suite
contract. Supply explicit external `WORK` and `OUT` directories. Component pins
remain the existing `merged-producers-v1` set and are recorded in retained summaries.
The local environment used an isolated dependency environment rather than claiming
an exact reproduction of every hosted dependency lock.

One optional sizing probe admitted an already allocated object whose ASCII JSON
encoding is exactly 1 MiB. With tracemalloc enabled it took approximately 0.378 s
and reported 832 additional traced bytes. Existing strings were reused; input
allocation and subsequent serialization are excluded. This is one scoped
measurement, not a throughput, full-process memory or worst-deployment guarantee.

## CI observations and corrected setup failure

At hub source `c3b919d`, hosted integrated assurance, resolver, research assurance,
wire bounds, operational state, federated governance, destination ingress/restore,
optional execution, accepted authority-effect, Worker 21, merged-chain and other
completed workflows were successful when inspected. Workflow conclusions alone do
not establish complete artifact inspection.

The new [security regression run 38807231160](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38807231160)
failed on both Python versions: three publication-inventory tests required frozen
commit `592919dd95396f3f6164cf0ceec1fd15c065691b`, which the shallow checkout omitted.
On Python 3.12, its log reports 624 passed and 3 failed, plus 122 subtests. The
workflow was corrected at `b404ebc` to fetch full history; that correction does not
weaken or skip those tests. Consult the PR's current exact-head checks for rerun
status rather than treating this historical failure or a pending job as a pass.

The initial local gate command also lacked explicit component roots and produced
68 setup errors. Supplying the documented roots resolved that environment error;
the corrected run passed all 92 tests. Initial full-suite testing detected shared
helper reuse by the protected destination; the final correction scopes new audit
limits to the HMAC runtime and the complete hub suite passes.

## Compatibility and remaining limits

See [the correction contract](../workstreams/security-correction-contract-2026-10-15.md)
for exact numeric defaults, identity rules, failure responses and migration notes.
HMAC audit retention is append-only with lifetime limits; counters do not refill
on restart or time rollover. Full capacity blocks further effects. Existing stores
without the audit schema are refused. There is no automatic operational migration,
authority reset or destructive cleanup. The separate protected destination keeps
its existing admission contract.

Preflight cannot defeat a concurrent writer with the same host privileges. Input
budgets cannot undo input allocation and require upstream predecode byte limits.
Refusal budgets bound durable storage, not adversarial CPU, I/O or lock contention.
WAL mode is rejected by the new HMAC admission connection; default rollback-journal
overhead is additional to the capped main database. Database fault injection and
SQLite page exhaustion do not establish power-loss or filesystem durability.

This work performs source tracing on changed paths, regression and synthetic
integration execution. It does not constitute a new repository-wide security scan,
secret/PII/IP clearance, production test or independent external review. Same-host
SQLite observations establish retained destination state only for these synthetic runs.

## Coverage gaps remain open

- [Issue 138](https://github.com/cogno-us/cognous-open-control-stack/issues/138):
  recover path-level receipts and review the original 559 deferred hub paths.
  Empty receipt reference arrays do not identify the original 113 reviewed paths.
- [Issue 139](https://github.com/cogno-us/cognous-open-control-stack/issues/139):
  review exact pinned downstream source. Executing component tests is not that review.
- [Issue 140](https://github.com/cogno-us/cognous-open-control-stack/issues/140):
  wider anonymous link inventory and actual deployed API exposure/configuration.
  Two HTTP 200 observations do not clear that wider scope.

These follow-up issues preserve proof gaps and do not close them. C0 retains its
check-to-commit race, optional C1 remains cooperative same-host SQLite, and C2/C3,
real settlement and production deployment remain unqualified.
