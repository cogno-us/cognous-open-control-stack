# S0 engineering closeout and publication acceptance follow-up

**Publication HOLD. Operational trust HOLD / NOT ESTABLISHED.**
`reference_release_authorized=false`; `production_deployment_authorized=false`.
Candidate nonselected. No release/tag, announcement, production activation,
settings change, institutional grant/credential or reporting submission occurred.
Agent review does not supply independent accountable human acceptance.

## Exact source and proposed populations

| Binding | Exact identity |
| --- | --- |
| Integrated engineering/candidate source | `0e6ab2435438dd1edcdc5a00789afa6f0f5f4ccf` |
| Qualified PR #129 head | `d42bcde719c4307b2141954e3c8d30bb0e59c9cc` |
| Identical qualified/integrated Git tree | `4f4c9bdf7f287aed2d4dcda9adf361e139e276ec` |
| Selected lock SHA-256, unchanged | `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc` |
| Separate candidate source manifest SHA-256 | `7b0788c8a7624393bfeb91104fb58bd9f96ab1a6d09b30e7d9e5c0c05190f4f5` |
| Candidate | `profiles/remediation-candidate-20261015.json`; selected=false; all seven pins actual merged commits |
| Publication package source, still frozen | `e335e5512fe8dd0a73637dcd8fd9c21ec235e43e` |
| [Actual package inventory](final-closeout-20261015/manifest.json) SHA-256 | `b1805bac8990676c17222d10e18810dbcd346a1003b3e4d67936efb997318d99` |
| Proposed custom source-review ZIP | 206 files; 1549446 bytes; SHA-256 `1c9ae8af9d313cfde478c6e1bb46f58e563845f9ae22b6c56c86670b57b33faf` |
| [Unapplied selection diff](../workstreams/remediation-selection-proposal.diff) SHA-256 | `fe51cd8b4b42fddb6f1ada8c10c8602d1adddfc7622aa21774fb84b5c1c4964f` |
| Proposed lock bytes SHA-256, not applied | `ae2d3fec2f9291a1cde57a51870f3dd235da14881b36ca69e830591dd6d9622a` |

The original inventory partitions 669 files at e335e551: 206 included, 463
excluded, 30 required original notices. ZIP bytes and every member digest were
reverified unchanged. This is the same bounded source review kit, not a package
of the new external component source or an offline runnable environment. Root
terms do not relicense all components. A normal Git source/tag archive would
include a different, unaccepted population and is not a permitted substitution.

The closing metadata/proposal in PR #128 postdate qualification at d42bcde7 and
are excluded from that earlier source/package/scan population. They are report
follow-ups, not evidence that a report scanned itself. Current selected lock and
all four pre-existing profiles are unchanged; the new candidate is separate.
Normalized artifact candidate.json bytes have SHA-256
`599ab78cfee44acc987a2ba2dad398e4dfbce561af65bb509cecec11a3dc4b0f`; source manifest bytes have
the different hash above. [Machine evidence](../verification/s0-component-repair-integration-2026-10-15.json)
records full source/tested/merge pins, commands, CI URLs and artifact hash bases.

## Verified bounded fixes and interfaces

| Component / PR | Actual merged source | Scoped cases per Python version |
| --- | --- | --- |
| [runtime #86](https://github.com/cogno-us/cognous-execution-runtime/pull/86) | `309e194c1b0a3de23e11e20133e6eaf88875e48a` | 7 |
| [replay #25](https://github.com/cogno-us/cognous-replay-bundle/pull/25) | `83fbaf2a0f6f071aca1ea0af859eb8fc6385c26a` | 18 |
| [odes #33](https://github.com/cogno-us/open-decision-evidence-standard/pull/33) | `25c7ad608c2e6fd9f450e075db6bbf3ee4091a49` | 10 |
| [pack #25](https://github.com/cogno-us/cognous-governance-evidence-pack/pull/25) | `1e789c7d67a897097445faef1813fb0cd22d55e5` | 10 |
| [gax #23](https://github.com/cogno-us/cognous-governed-exchange/pull/23) | `9de2d438ed03531bb960c896f541a6a2da1b2315` | 8 |

Manifest remains 46c950bed37fe3812000895430bc0312d29e37ce; CP remains
c7f122ba3a6e39f9268a7163c99be3ee514cd97e. Scoped Python 3.11/3.12 tests and
historical consumer checks passed at each reviewed head; exact jobs/artifacts
are in machine evidence. Post-merge local scoped cases also pass. All executed runtime PR-head jobs, including broader macOS app jobs,
completed without failure (46 successful check runs, one skipped iOS job).
The skipped scope is retained in evidence and is not implied qualified. Local Node
lint/build/test could not pass dependency bootstrap under installed pnpm's
libsignal exotic-subdependency policy; no policy was weakened. Hosted Linux/Bun
and Windows Node gates passed. Source merging is not full platform acceptance.

- Executor captures the current call's actual typed refusal only after durable
  write success, keeps concurrent requests isolated and preserves its deep copy
  through producer 2.0.0 export. Write failures never manufacture durable evidence.
- Replay retains all four new evidence collections, validates strict typed
  fields/original horizon and authorization bindings, and rejects unsupported
  horizon source or substituted refusal/executor/read lineage. Unknown top-level
  data stays explicit loss. Historical pairings remain unchanged.
- ODES transformation 0.2.2-refusal-candidate and Evidence Pack transformation
  0.3.3-refusal-candidate reconstruct all four fields before full records/links/
  commitments/profile/status comparisons. No comparison is suppressed. The new
  pack emits singleton compatibility sets; historical sets retain original values.
- GAX's explicit typed-refusal-candidate-20261015 profile verifies actual loaded
  Git source heads, tracked membership/cleanliness and exact Manifest identity.
  Historical defaults and original effect ownership/retry logic are preserved.

Migration is explicit revision/profile selection. Preserve ownership stores,
unresolved checkpoints and immutable source bindings. Historical unresolved work
needs its original revision-pinned recovery path; no generic cross-generation
production-store migration is qualified. Do not reset ownership state to make a
new profile accept old work. Synthetic fresh test stores are not migration advice.

## Final execution and material evidence

Two local and two [hosted](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38768226238)
repetitions at exact head d42bcde7 each pass **23 testcase elements**, zero
failures/errors/skips/subtests. All 21 hosted checks at the head passed. S0
independently downloaded [artifact 11990585468](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/38768226238/artifacts/11990585468),
verified ZIP SHA-256 `f65af840bc4f3456bb31c7597f3d250cb7946f440a1ce181081f14c9cca0670b` and all 399 original hashed
members, counted both raw JUnit files and inspected actual material records.
Each repetition has 22 actual destination SQLite stores: 19 zero-effect, three
one-effect (lost-ack recovery, exchange checkpoint recovery, unsafe C0 race).
Four actual refusals match executor, Replay and both downstream consumers, with
identical retained reconstruction bundles. Lost-ack effect rows remain identical;
a second message is refused ownership of unresolved work. Actual GAX provenance
matches exact loaded source. UUID-bearing bytes are not claimed repeatable.

C0 still commits when revocation occurs after revalidation: its passing
characterization records safety_success=false. Optional C1 remains cooperative
same-host scope; no C2/C3 or real settlement. Restart tests recreate workflows and
reopen stores, not SIGKILL or power-loss tests. Fresh integrated-source ingress
and restore subsets also pass 25 + 12 cases (37 total, no failures/errors/skips/
subtests). Restore failure characterization is not a prevention guarantee or
deployed external anchor. Original d577b11a S1 failures and intermediate draft
proof remain preserved, not relabeled as passes. Historical e335e551/2026-10-13
technical passes retain their original source, pins and scope.

## Separate preview-gate dispositions

| Gate | Disposition and remaining acceptance |
| --- | --- |
| PV-1 navigation/distribution rights | PARTIAL / HOLD. Exact kit/notice bytes verified; applicable distribution rights, transitive/optional-source exceptions and accountable rights review remain pending. Generated notices do not establish rights. |
| PV-2 source/pins/provenance | Technical identity established for the exact historical package and separate named candidate. Selected lock unchanged; candidate owner selection pending. No transfer to a different package/profile/full-reference claim. |
| PV-3 reproducible bounded execution | Named bounded passes retained; new 23-case twice proof is seven-component synthetic C0 only. Unsafe race/restore characterization remains unsafe; broader platform/full-reference/anchor deployment claims are not established. |
| PV-4 truthful disclosure | PARTIAL / HOLD. C0, optional same-host C1, no C2/C3/settlement and operational HOLD preserved. Any final publication/expanded package claims must be reviewed against actual content. No general platform superiority is inferred. |
| PV-5 publication safety | PARTIAL / HOLD. Prior bounded kit scans are not complete PII/IP clearance or independent security acceptance. Broader residual findings/exclusions remain. Later candidate/source/report objects are not retroactively cleared; scanner enrollment alone is not an executed reviewed scan. |
| PV-6 reporting/enforcement | PARTIAL / HOLD. Reporting owner/backup/escalation/retention and authorized delivered/acknowledged/triaged handling remain unproven. MX/HTTP availability is not delivery. Effective admin enforcement evidence/actions remain external; no settings were changed. |

The [original exact-package packet](final-closeout-20261015/README.md) retains
rights/security dispositions, the contextual scan observations and unsigned
acceptance forms. No new legal/security approval, institutional grant or
independent human signoff is manufactured by these merges. S6 distinguishes
completed repository observations from still-required owner/admin actions.

## Explicit owner decisions and proposed publication action

The [selection proposal](../workstreams/remediation-selection-proposal.json)
contains an exact unapplied component-lock diff, all actual merged candidate
pins, compatibility evidence and scope limits. Dry-run application succeeds;
the patch was not applied. Owner must explicitly decide selection. Its proposed
thirteen-component lock does not inherit a full-reference pass from the bounded
seven-component gate; historical qualification is retained separately.

After accountable acceptance of all applicable PV gates and explicit publication
authorization, the proposed action remains upload **only the original custom
206-file source review ZIP** named and hashed above. No release/tag, normal Git
archive substitution, public announcement or production activation is proposed
as an executed action. If the owner instead wants new candidate source/proposal
included, first define and hash that expanded population, refresh S4 inventory
and rights/notices, then execute/review S5 delta coverage and obtain independent
acceptance. All current authorizations remain false; publication stays HOLD.

Remaining engineering/verification:

- Requalify the broader full-reference scope if selection is expanded to it;
  rebuild inventory and screen deltas if shipped source/package content changes.
- Implement and independently qualify/deploy an external restore anchor only if
  rollback prevention is a required deployment property; characterization is done.

External acceptance dependencies:

- Explicit owner selection and exact publication-source/package decision.
- Accountable rights and independent security/data/IP dispositions, with explicit
  bounded exceptions/exclusions rather than universal clearance claims.
- Reporting primary/backup, private escalation/retention and authorized evidence
  of delivery, acknowledgement and triage; no exercise was sent.
- Admin exports/configuration/demonstration of effective required reviews/checks
  and enforcement without bypass; no settings were changed.
- Independent publication-owner signature. Production acceptance is separate,
  unauthorized and not established by a bounded preview or engineering merge.
