# Qualification initiation path

Status: DRAFT, non-authorizing description of an existing, unmodified proposal. Source: `.github/workflows/mvp-acceptance.yml`, `tools/mvp_acceptance_gate.py` and `process/mvp-acceptance/` in Qualification draft PR #223 (branch `mvp-acceptance-job`, head `df4c6b76aca93051e0123f56a82062a98c5b5192`). Qualification owns the oracle and every verdict; the workflow's own comment says it "authorizes nothing". Label: VERIFIED (files read at that head; REST workflow list read 2026-10-24).

## The one command

`workflow_dispatch` of `mvp-acceptance.yml` in `cogno-us/cognous-stack-qualification` (dispatch only; never on push):

`gh workflow run mvp-acceptance.yml -R cogno-us/cognous-stack-qualification -f candidate_commitment_sha256=<sha256>`

At head `df4c6b76` the identity file `process/mvp-acceptance/candidate-identity.inputs.json` already names the final tuple of [candidate-manifest-draft-2026-10-24.json](candidate-manifest-draft-2026-10-24.json) (Runtime `c5e97e87`, Replay `40012b8c`, Evidence Pack `7b9511f2`, ODES `1a5e1d30`, hub `5b76c58a`, Verifier `c0b8ba1f`), so no revision input is needed. Optional inputs override one component for that run only (40-hex only; recorded in `tuple-resolved.json`): `control_plane_revision`, `runtime_revision`, `replay_revision`, `evidence_pack_revision`, `odes_revision`, `verifier_revision`, `manifest_revision`, `hub_revision`, `qualification_revision` (blank or equal to the workflow commit). A blank `candidate_commitment_sha256` gives an INCOMPLETE verdict. Verdicts: INCOMPLETE over REJECT over ACCEPT; the job fails unless the gate says ACCEPT. Python 3.13 and the hash lock in [dependency-manifest.md](dependency-manifest.md) are used.

## What blocks it today

1. Not dispatchable: the workflow exists only on the #223 branch; the REST workflow list of the repository shows `mvp-chain` but no `mvp-acceptance`. GitHub dispatches a workflow only once its file is on the default branch (general behaviour, not tested here). Qualification must merge #223, or an equivalent. This record merges nothing.
2. `candidate_commitment_sha256` must come from Qualification, recorded outside the checkout. The commitment file at `df4c6b76` was recomputed for the final tuple; any change to a hashed file (identity, battery, mapping, gate, workflow, mandatory tests, a tuple edit, including a Verifier change) needs a new commitment. Qualification targets its freeze for 2026-10-27 (ruling 6, REPORTED).
3. Yama: the run sets `kernel.yama.ptrace_scope=1` with `sudo sysctl` on the hosted runner. If it is absent or unsettable the boundary test is BLOCKED and the verdict is INCOMPLETE (ruling 4b); no weaker profile is substituted. Whether the hosted runner allows it is UNVERIFIED (never dispatched).
4. Pending criteria: the NC4-03 origin-rule negative mutations are not battery rows; rows are added only after Qualification freezes the corrected predicate (proposals Qualification #222, #225). At the final tuple the `mvp-chain` suite fails exactly this row (below).
5. Hub exact-pin checks: the hub's required `cross-component / aggregate` check and the process-boundary, protected and paired-request wrappers pin the previous tuple (profile `r13`) exactly, so the hub lock bump in draft hub PR #223 fails them until Qualification moves its expectations; `suites/mvp-d09` reads the `r13` profile and cannot run at Runtime `c5e97e87` until an owner-authorized next profile exists (Qualification #226 body, REPORTED).
6. Qualification `main` has no branch protection (REST 404), so the workflow's anchor of expectations v1 to v3 to `main` proves identity with current `main`, not an owner approval.
7. The matched USD 10 refund fixtures are outside this record.

## Integration checks run at the final tuple (VERIFIED locally, 2026-10-24; not a Qualification run)

Pristine checkouts at the exact shas, CPython 3.13.16, the hash lock above, Qualification `main` `4298247e` suites; none needs Yama or a dedicated user.
- `suites/mvp-chain` (expectations v3): 36 PASS, 1 FAIL (NC4-03), 0 BLOCKED. The same result at Verifier `39d46b49`.
- `suites/mvp-d2-route-b` (Qualification #226 head `94f4942f`, Runtime `c5e97e87`): 34 passed, including the terminal-revocation test.
- Route B executed bundle and two denied bundles (approval withdrawn, grant revoked) through the real Replay import (all reports complete), then through `odes.exporter.export_cognous_stack_package` with that real Replay: all three export. These use the chain's own harness objects, not the live ingress.
- Component test suites at their shas: Control Plane 1117 passed, 91 skipped; Runtime 556 passed; Replay 1297 passed, 12 skipped, 8 xfailed; Evidence Pack 376 passed; Action Manifest 298 passed; ODES 3089 passed, 4 failed (the declared retained-example tests, ODES #131).

A run at an unfrozen tuple is a developer run: even with every input set it is not an acceptance.
