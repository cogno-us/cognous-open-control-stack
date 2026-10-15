> Historical draft-pin diagnostic evidence below is preserved. The current manifest now contains actual serially merged predecessor pins; final exact-head qualification is recorded separately in the [S0 control panel](../workstreams/release-closeout-control-panel.md). No final result is asserted by this historical diagnostic record.

# S0 serial component repair and diagnostic checkpoint

Publication/production HOLD; operational trust HOLD / NOT ESTABLISHED. Both
release/deployment authorizations remain false. Candidate nonselected. This
checkpoint is excluded from the frozen e335e551 206-file review kit; that package
and its rights/security/independent acceptance exceptions are unchanged. An
expanded source package requires refreshed inventory and S5 delta review.

The original S1 PR #122 head d577b11a had 13 passes/10 failures of 23 in each
repetition. Its branch, report and artifacts are preserved. This follow-on reuses
the S1 harness on an isolated S0 branch without overwriting worker branches.

## Owning-repository changes

| Repair | Draft/current PR | Required dependency action |
| --- | --- | --- |
| Per-call durable refusal capture | runtime #86, 63bd4d8d | Finish current checks, review and merge |
| Strict typed refusal/closeout reconstruction | Replay #25, 24fa9571 | Replace runtime head by actual merge SHA; rerun |
| Retained fields and recipient semantic consistency | ODES #33, da4f1976 | Replace runtime/Replay pins by actual merge SHAs; rerun |
| Retained fields and pack semantic consistency | Evidence Pack #25, 74cd70aa | Replace runtime/Replay pins by actual merge SHAs; rerun |
| Separate truthful opt-in provenance | GAX #23, f43b0492 | Replace all four dependency pins by actual merge SHAs; rerun |

CP remains c7f122ba and Manifest 46c950be. Full SHAs and exact interface versions
are in the separate candidate manifest. The existing selected lock and four
profiles are unchanged. No selected profile or existing default was promoted.

Executor captures the actual refusal after the authoritative store returns and
keeps concurrent requests isolated. Existing producer export deep-copies it.
Replay retains refusals, resolution checks, input time floors and attempt
closeouts as committed records and rejects missing/substituted typed evidence.
Consumers reconstruct all four fields before full Replay comparisons; those
comparisons are retained. GAX checks actual imported source Git heads, tracked
membership/cleanliness and exact Manifest identity before using its new labels.
Neither source consistency nor matching commits establish independent trust.

Runtime local scoped: seven new cases passed; historical Python 359 passed,
57 existing skips and nine separate subtests. Local pnpm lint/build/test were
attempted but bootstrap fails under the installed pnpm exotic-subdependency
policy for upstream libsignal. No dependency policy was weakened and no local
Node gate pass is claimed. Hosted Linux Node/Bun lint/build/test checks pass;
Windows and Swift checks are still pending at this checkpoint. No runtime merge
is claimed. Other local scopes: Replay 16; ODES 10; Evidence Pack 10; GAX eight
stage cases, each passing without failures/errors/skips/subtests. Hosted new and
historical consumer matrices also pass at their current draft heads; those draft
pins are not final merged-chain evidence. CI URLs/counts belong in the S0 panel.

The initial GAX candidate CI rejected tracked Replay egg-info rewritten by
editable dependency installation (eight setup errors, companion cancelled).
Corrected workflow imports clean source directly and pins external test packages;
the source gate remains intact and the corrected head's checks pass.

## Diagnostic S1 run

`PYTHONDONTWRITEBYTECODE=1 python tools/remediation_candidate.py --work
../candidate-probe --out ../evidence/s0-draft-pin-diagnostic-3` executed twice
against the seven exact clean draft-pin component checkouts. The runner records
all source hashes and installed packages. Hub HEAD was 5715f791 with the three
recorded harness/test/manifest working-tree hashes; this is not a tested committed
hub head. Each repetition: **23 passed, zero failures/errors/skips/subtests**.
`qualification_input_status=draft_pr_heads_diagnostic`; the manifest and summary
do not claim final candidate integration acceptance. The runner requires exactly
23 testcase elements. The runtime profile now comes from the separate candidate
manifest. The handoff's envelope builder now lets the actual constructor supply
new optional dataclass defaults (tenant_id=None); mandatory missing fields still
raise constructor errors. No component adapter is patched in the S1 suite.

S0 inspected all 22 destination SQLite stores in each repetition: 19 zero-effect
and three one-effect stores (direct lost-ack recovery, exchange checkpoint
recovery, and unsafe C0 race characterization). Four refusal records exactly
match executor export, Replay committed records, ODES facts, and Evidence Pack
lifecycle records and both retained reconstruction bundles. Lost-ack before/after
rows are identical. The second-message claim refusal retains the original owner
and zero effects. Truthful exchange provenance matches the new exact profile.
C0 still records safety_success=false: revocation after revalidation commits.
These are synthetic local SQLite outcomes, not settlement or operational safety.
Restart injection recreates workflows/reopens stores; no power-loss/SIGKILL claim.

Final merged-pin S1 qualification still requires serial merges, an exact manifest
refresh and two fresh repetitions. Passing draft diagnostics cannot select the
candidate, accept PV gates, authorize publication/production or supply independent
human/legal/security/reporting/enforcement signoff. The final packet must identify
source/package populations and exclusions separately; do not reuse an earlier
scan as clearance of these later report/code objects.

Local diagnostic artifact SHA-256 (not hosted artifact attestations):

- `summary.json`: `cc37f4dfb94328feac429332c099f3f73743df9078dc0ba590ccf1f47d2b1a52`.
- `sha256.json`: `94153dd81be3d1991e2ceb4381600ea1dd682cf589b805c2dc04d1fe182e4e67`.
- `material-audit.json`: `ebe5e43ac9769c4c1afd9c4593b4f5064610ed563bb266326f968bd5aa6c9cb2`.
- `run-1/junit.xml`: `e0f68e473d38fe17df625a3bad2342b463318437e43c6b12b474a0c2de27d289`.
- `run-2/junit.xml`: `09b8c49be7cea0d524b3160b0634f999f2b67ad8026ccd9a8863ed25e27cebea`.
