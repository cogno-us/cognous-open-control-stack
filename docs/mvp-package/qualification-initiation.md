# Qualification initiation path

Status: DRAFT, non-authorizing description of an existing, unmodified proposal. Source: `.github/workflows/mvp-acceptance.yml`, `tools/mvp_acceptance_gate.py` and `process/mvp-acceptance/` in Qualification draft PR #223 (branch `mvp-acceptance-job`, head `5690f7b8c83335d62ec24e992227f96797ab0591`). Qualification owns the oracle and every verdict; the workflow's own comment says it "authorizes nothing". Label: VERIFIED (files read at that head; REST workflow list read 2026-10-24).

## The one command

`workflow_dispatch` of `mvp-acceptance.yml` in `cogno-us/cognous-stack-qualification` (dispatch only; never on push). Example shape, with every sha a full 40-hex string:

`gh workflow run mvp-acceptance.yml -R cogno-us/cognous-stack-qualification -f runtime_revision=<sha> -f hub_revision=<sha> -f candidate_commitment_sha256=<sha256> [-f <component>_revision=<sha> ...]`

Inputs (all optional strings): `control_plane_revision`, `runtime_revision`, `replay_revision`, `evidence_pack_revision`, `odes_revision`, `verifier_revision`, `manifest_revision`, `hub_revision`, each an override of one component in `process/mvp-acceptance/candidate-identity.inputs.json` for that run only (40-hex only; branches, tags and short shas are refused; overrides are recorded in `tuple-resolved.json`); `candidate_commitment_sha256` (blank gives an INCOMPLETE verdict); `qualification_revision` (blank or equal to the workflow commit, else refused). Verdicts: INCOMPLETE over REJECT over ACCEPT; the job fails unless the gate says ACCEPT. Python 3.13 and the hash lock in [dependency-manifest.md](dependency-manifest.md) are used.

## What blocks it today

1. Not dispatchable yet: the workflow exists only on the #223 branch. The REST workflow list of the repository shows no `mvp-acceptance` workflow, and GitHub dispatches a workflow only once its file is on the default branch (general GitHub behaviour, not tested here). Qualification must merge #223, or an equivalent, first. This record does not merge anything.
2. `hub_revision` must be set. The identity file's hub sha `43c526eb` predates `tools/mvp_env_record/capture_env_record.py`; the run exits 1 right after the hub checkout. A sha containing the script with sha256 `5ae7beca645bf9cf6676c77996656ba7cdaaf4e5413c8c69741e1c7f269f1a51` is required; hub `main` `5b76c58a` has it (VERIFIED, computed).
3. `runtime_revision` must be set to the post-F3 sha `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f`; the identity file still names `ec728da6`.
4. `candidate_commitment_sha256` must come from Qualification, recorded outside the checkout. The commitment hashes the identity file, battery, mapping, gate, workflow and mandatory test sources, so any change (for example #224 and #225 on the #223 branch, #226's change to `process/mvp-chain/tuple-pin.proposed.json`, or a tuple edit in the identity file) needs a new commitment file and hash. Qualification targets its freeze for 2026-10-27 (ruling 6, REPORTED).
5. Yama: the run sets `kernel.yama.ptrace_scope=1` with `sudo sysctl` on the hosted runner. If Yama is absent or unsettable the boundary test is BLOCKED and the verdict is INCOMPLETE (ruling 4b); no weaker profile is substituted. Whether the hosted runner allows it is UNVERIFIED (the workflow has not been dispatched).
6. Pending criteria: per the #223 README the NC4-03 origin-rule negative mutations are not battery rows; `pending_rows` is a placeholder and rows are added only after Qualification freezes the corrected predicate (proposals #222, #225). The supported-ingress ambiguity test (ruling 5) is draft #224, on the #223 branch and not in #223's head.
7. Pins pending in components: Replay draft #79 (Programme 2 executor pairing at Runtime `c5e97e87`), and Evidence Pack and ODES re-ties, are in progress; their Programme 2 profiles still name Runtime `ec728da6` (REPORTED by #226).
8. Qualification `main` has no branch protection (REST 404), so the workflow's anchor of expectations v1 to v3 to `main` proves identity with current `main`, not an owner approval (the #223 README states this limit).
9. The scenario fixtures for the matched USD 10 refund are outside this record; a later prompt defines them.

A run at an unfrozen tuple is a developer run: even with every input set it is not an acceptance. At the pre-F3 tuple the oracle itself records NC1-04 as a failure and expects non-ACCEPT (README of #223).
