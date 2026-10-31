# QGATE-05 candidate custody (design, PROPOSED)

Status: design and templates only. Labels: ARCHITECT-STATED = binding rulings D3/D4/Q14 in the QGATE-05 brief; OBSERVED = read in the Qualification tree at 56a618eb (file cited); INFERENCE = Worker D design reasoning. Nothing here is a freeze, certification, Q7, Tier 1, release or production authorization.

## Why the anchor lives in the hub, outside the candidate checkout
1. OBSERVED (`process/mvp-acceptance/candidate-commitment.proposed.v4.json`, fields `independence` and `inherent_limit`; gate `check_commitment` G-12): the commitment lists the bytes of the gate, workflow and tests, but the gate and the commitment come from the same checkout. A changed checkout could carry a changed gate and a changed commitment that agree with each other. The commitment hash is only meaningful against a value held outside that checkout. Without an external value G-12 is INCOMPLETE.
2. INFERENCE: a record inside the candidate tree would either be part of the committed set (changing it changes the commitment: circular) or be uncommitted (the gate refuses uncommitted files in committed directories). It therefore cannot live there.
3. INFERENCE: the hub repository is a different repository with its own history. A commit there that predates the run branch push fixes the declared candidate before any result exists, so the candidate cannot be adjusted after seeing results (rule: expectations are never edited after a result is seen). The Issue #215 comment is a second channel with GitHub-assigned timestamps.
4. Limit (state it, do not hide it): the same AI lineage operates the hub commit and the candidate, so this is tamper-evidence and ordering evidence, not independence. A human or separately-roled reviewer is what upgrades it; none is claimed.

## What the workflow asserts (OBSERVED in `.github/workflows/mvp-acceptance.yml` and `tools/qgate05_custody_check.py` of the Qualification candidate; push-triggered, NO workflow inputs)
- The workflow is triggered only by a push to `qgate-05/run-1` (no `workflow_dispatch`, no inputs; `run_attempt == 1`). Nothing is supplied by hand at run time.
- It checks out the hub repository at the DEDICATED branch `qgate-05/custody-1` (checkout `ref` = that branch; NOT the hub default branch and NOT a floating pin), records the resolved head sha of that branch (`host-evidence/custody-hub-branch-head.txt`, `custody-evidence.json`), asserts that `docs/mvp-recovery/qgate-05/custody/freeze-commitment.json` exists and carries `schema`, `qualification_revision` and `candidate_commitment_sha256`, and then asserts `GITHUB_SHA == qualification_revision == checkout HEAD` and `sha256(process/mvp-acceptance/candidate-commitment.proposed.v5.json)` recomputed in the job `== candidate_commitment_sha256`. The value is handed to the gate as the independent `--expect-commitment-sha256`. All of this runs before any test.
- The gate, workflow, tuple files and helpers are covered transitively: they are in the commitment, so a different tree gives a different commitment. The custody record is pushed ONCE to `qgate-05/custody-1` and never force-pushed or amended; nothing else may change `freeze-commitment.json` after that commit (a changed candidate is a new commitment, a new record and a new custody branch/file).
- The gate's `COMMITMENT_FILE` constant names the same commitment version as `commitment_file` (verify_freeze_record.py checks this by calling the gate read-only).
- Limits (state them): the branch head is mutable in principle until it is protected; the resolved head sha is recorded after the fact. A ruleset forbidding force-push and deletion on `qgate-05/custody-1` (not checked from here) would make the anchor stronger.

## Exact order of events (the three ORDERING PREREQUISITES are not checked by the workflow before it runs; missing one spends the single run)
1. Repairs of qualification metadata/test configuration only (D4); no production component change, no oracle weakening.
2. Assemble oracle v8 and battery v2 as NEW versioned files (v7 and battery v1 untouched).
3. Generate commitment v5 (`python3 tools/mvp_acceptance_gate.py commit --out process/mvp-acceptance/candidate-commitment.proposed.v5.json`, with `COMMITMENT_FILE` bumped to v5 in the same change set). Generated LAST; the commitment excludes itself.
4. Commit that set in the Qualification repository; fix `qualification_revision`. The tree must be clean.
5. Build the freeze record (`build_freeze_record.py`) then verify it with the independent `verify_freeze_record.py` (add `--require-final-tree` to refuse leftover placeholder rows). Exit 0 required.
6. Qualification Owner reviews and approves: fills `owner_approval` (role, session, UTC time, `approved` true, `statement_acknowledged` true), sets `frozen` true and `status` `FROZEN-TECHNICAL`. Re-run verify with `--require-approved`. (Approval is AI-assisted technical approval, not certification.)
7. PREREQUISITE A (custody before the run branch): push the custody record ONCE to the hub branch `qgate-05/custody-1` (the approved freeze record plus `custody/freeze-commitment.json` from `freeze-commitment.template.json`); record the hub commit sha. Never force-push.
8. Post the Issue #215 comment from `ISSUE-COMMENT.template.md` (second channel, GitHub timestamp).
9. PREREQUISITE B (F-01, Qualification main before the run branch): land the exact freeze tree (`qualification_revision`, including oracle v8 and battery v2) on Qualification `main` by PR or fast-forward. The anchor gate G-02c compares every frozen file with its blob on `main` through the REST API and is INCOMPLETE for any file absent or different there; with oracle v8 absent from `main` the single run ends INCOMPLETE regardless of how the rows behave. Confirm by comparing blob ids of the frozen files with `origin/main` before step 10.
10. Push the run branch `qgate-05/run-1` pointing exactly at `qualification_revision` (once, never again). This push IS the single run (no dispatch, no input).
11. Collect evidence (artifact `qgate05-run1-evidence`, append-only branch `qgate-05/evidence-run-1`, SHA256SUMS, gate verdict, report with four separated layers). No re-run to improve a result.
If any step 1-4 changes the tree after step 5, the record is void: new commitment version, new record, new custody file.

## How a reviewer verifies (all read-only)
```
git clone <hub> && git -C hub show origin/qgate-05/custody-1:docs/mvp-recovery/qgate-05/custody/freeze-commitment.json   # or <custody-commit>:...
git clone <qualification> q && git -C q checkout <qualification_revision> && git -C q status --porcelain   # empty
sha256sum q/<commitment_file>                                   # equals candidate_commitment_sha256 in the hub file AND in the Issue #215 comment
python3.13 verify_freeze_record.py --qualification-tree q --record <approved record> --qualification-revision <rev> --expect-commitment-sha256 <hash> --require-approved --require-final-tree
git log --format='%H %cI' origin/qgate-05/custody-1 -- docs/mvp-recovery/qgate-05/custody/freeze-commitment.json   # hub commit time earlier than the run branch push and workflow run start
```
Also compare the hub commit timestamp and the Issue comment timestamp with the workflow run's `created_at` (run page; Actions API is not readable from the build environment, so this is a reviewer step). The verifier does not trust the build script and re-derives every field; it runs the gate's `commit_files()` with `python -B` so no bytecode is written into the tree.

## What verify checks (OBSERVED from its output on 56a618eb; see handoff)
Tuple SHAs 40-hex and equal to tuple-pin and identity inputs; oracle/battery/commitment paths are the highest versions; their sha256; commitment file count and listing hash; every committed file's bytes; gate `commit_files()` equals committed list; no symlink, no `__pycache__`, `must_remain_absent`; tree git HEAD equals revision and tree is clean; denominators; host profile; Q14 permitted and prohibited text; limitations present; standing holds; unfrozen records carry no approval; frozen records require complete approval.
