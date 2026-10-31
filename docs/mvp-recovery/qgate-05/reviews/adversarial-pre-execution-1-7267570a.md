# OCS-MVP-QGATE-05 adversarial evidence review (Reviewer F): PRE-EXECUTION

REVIEWER PRE-EXECUTION: BLOCKING FINDINGS (1 HIGH)

Non-authorizing. AI-assisted adversarial technical review only. Not external certification, not Q7, not release authority.

## 0. Separation actually achieved

- I am a fresh-context subagent spawned by the builder session. I am NOT a separate top-level session.
- I did not read /tmp/claude-0/qgate05/E/. I did read /tmp/claude-0/qgate05/handoff/*.md, which are builder claims, and treated them as claims.
- I wrote only under /tmp/claude-0/qgate05/F/.
- I made no host changes (no useradd, no sysctl). Probes ran with numeric uids in a scratch TMPDIR.
- Same model lineage and same host as the builder. No organizational independence.

Inspected tree: /home/claude/view-f/qual. `diff -rq -x results` against `git archive 7267570a` is empty, so it equals commit 7267570a. All eight pinned checkouts under /tmp/claude-0 are at the identity-input shas and clean.

## 1. Findings

| # | Sev | State | Finding |
|---|---|---|---|
| F-01 | HIGH | CONFIRMED (local blob simulation of G-02c; workflow not run) | The anchor gate G-02c can never be PASS if the tree is only pushed to `qgate-05/run-1`. Details in 1.1. |
| F-02 | MED | CONFIRMED (code) | Yama is no longer set (`sysctl` removed) and the original profile v1 says the workflow sets it. If the runner's `ptrace_scope` is 0 or Yama is absent, NC4-03a, NC4-01/02/04, KL-01 and G-11 are BLOCKED and the verdict is INCOMPLETE. That is not a false pass, but it wastes the single run. "QGATE-03 passed" does not show the as-found value, because QGATE-03 set it. |
| F-03 | MED | CONFIRMED | Custody is read from the hub DEFAULT branch at run time (workflow line 93), not from a pinned hub commit. Worker D's CUSTODY.md requires "a pinned hub commit (input, not a branch)". The resolved hub head is recorded only after the fact (custody-evidence.json). Ordering is also unforgiving. If the custody file is not already merged to hub `main` when `qgate-05/run-1` is pushed, the custody step fails, no test runs, the evidence branch gets created, and the run is spent. |
| F-04 | MED | CONFIRMED | NC4-03a..d predicates are `status == PASS` on a string the harness writes (`_nc4_03_host.py`, `scenario_observation`). The facts (`dir_mode_is_2751`, `outsider_cannot_connect`, ...) live only in `observed` and are not in the oracle row. The oracle is frozen and Qualification-owned, so the expected observations should be in it. The code is committed, so this is not an escape, but it is the "assertion on harness-written data" pattern. |
| F-05 | MED | CONFIRMED (from the set file and the `_kwflow.py` rule list) | The frozen NC4-03 mutation set has no mutation whose expected rule is SIMULATE_NOT_CONSTANT_NONE, NONLITERAL_KWARGS, MODEL_COPY_KWARGS_FORBIDDEN, MODEL_COPY_UPDATE_NOT_FIXED, COMPREHENSION_NOT_FIXED, OPAQUE_POSITIONAL_UNPACK or UNRESOLVED. The set file says "The 24 remaining MUTANTS (generic `**` forwarding ...) stay supplementary only". The row title is about client `simulate` and arbitrary keywords. Those mutants do run in the 183 mandatory `test_kwflow.py` tests, so coverage exists in the battery but not in the frozen NC4-03 set. Architect A3/A4 asked for an explicit versioned set. |
| F-06 | MED | PLAUSIBLE | The base path /var/lib/qgate05-ocs/tmp has never run on a hosted runner. The ACL and ancestor-writability checks in G-11 are unproven there. The old FAIL was under /opt. Residual risk in the single run. |
| F-07 | LOW | CONFIRMED | `QG5_DURABLE_DIR` is exported and passed through sudo but no code reads it (grep: only the workflow, helper, runbook and a test). The workflow, profile v2 and helper describe it as "the durable writable store for the real-kill test". The kill harness uses `tempfile.mkdtemp` under TMPDIR, which is also under /var/lib, so there is no false pass, only false documentation. |
| F-08 | LOW | CONFIRMED (code) | Workflow line 81 sends `git ls-remote` stdout and stderr (`2>&1`) of a URL containing `x-access-token:${GH_TOKEN}` into `evidence-branch-lsremote-before.txt`. That file is uploaded and committed. On the failure path git can echo the URL. Masking applies to logs only, not artifacts. The job token expires at job end, so impact is small. |
| F-09 | LOW | CONFIRMED | The `upload-artifact` digest and id are not captured, only SHA256SUMS inside the artifact. The evidence branch is append-only by script (no force, fast-forward only) but not enforced server-side. If the push is rejected by a ruleset, the "evidence branch exists" guard is not set and a second push could be run. |
| F-10 | LOW | CONFIRMED | VER-01 and VER-03 are oracle PASS while the Verifier disposition is exit 3 ABSTAIN (VER-03 requires it). The oracle status vocabulary has no ABSTAIN. It is disclosed in VER-01's title, G-07's message and process/mvp-acceptance/README.md:46. The row-level reader sees PASS without ABSTAIN. `qgate05_summarize.py` reports Verifier dispositions separately, so the categories are kept apart. |
| F-11 | LOW | CONFIRMED | NC4-03b's title says "no capabilities", but the probe drops the client and outsider to CapEff 0. The ingress's own CapEff is not probed there (it is in the NC4-01 / G-11 environment record). NC4-03c needs the outsider to be able to stat the socket (a residual) for PASS, so a stricter host would FAIL. Neither is a false pass. |
| F-12 | LOW | CONFIRMED | Other workflows trigger on the same push (catalog-validation on any push; migration-integrity on suites paths). They are noise and do not touch the run. Action pins cannot be verified from here (403). `actions/checkout@11d5960a...` is used in 157 other workflows, and the old mvp-acceptance used `11bd7190` (v4.2.2). The runner image is a floating `ubuntu-24.04` label. ImageOS and ImageVersion are recorded in run-identity.json and the host snapshot. |
| F-13 | LOW | CONFIRMED | Worker D's CUSTODY.md and ISSUE-COMMENT template still describe "dispatch with `candidate_commitment_sha256` input" and "pinned hub commit". The push-trigger workflow has no inputs. Stale hub-side docs. |

### 1.1 F-01 detail (HIGH)

- Gate `frozen_files()` is `battery.oracle.unchanged_files_sha256` union the applicability historical files. For battery v2 that includes `process/mvp-chain/expectations.proposed.v8.json`. The tests assert this: `test_v8_is_in_force...`.
- The workflow step "Anchor the frozen files to the main branch" (line 223) records `gh api repos/<repo>/contents/<rel>?ref=main`.
- `check_anchor` (gate, about line 525) makes a missing main blob G-02c INCOMPLETE.
- `Gate.verdict()` makes any INCOMPLETE an overall INCOMPLETE.
- Qualification `origin/main` is 56a618eb, which has no v8. The simulation below prints BAD / ABSENT-on-main for v8 only. The other six frozen files match.
- The handoffs never mention this. Result as designed: the one authorized run ends INCOMPLETE regardless of how every row behaves.
- Minimal safe fix, without editing any committed file: land the freeze tree 7267570a on Qualification `main` (PR or fast-forward) BEFORE pushing `qgate-05/run-1`, and re-run the simulation below to show zero BAD. Alternatives all change committed files and force commitment v6: drop v8 from battery v2 `oracle.unchanged_files_sha256`, or anchor against another ref.

## 2. Task checklist outcomes

**Freeze identity and commitment**
- The 8 pins equal the identity inputs and the local pinned checkouts, which are clean.
- Commitment v5 regenerates byte-identically with `tools/mvp_acceptance_gate.py commit` (sha edc53a4a..., 216 files). Reproduction below.
- Committed set: suites/mvp-chain, mvp-applicability, mvp-d2-route-b; the sys.path directories (root, suites, suites/operation-identity, tools); process/mvp-chain and process/mvp-acceptance (except the commitment); the lock files; pytest.ini; the workflow; plus a static import closure.
- tools/qgate05_*.py and .sh, the workflow, pytest.ini and conftest are all in the set. The `must_remain_absent` files are absent.
- I found no mvp-chain, applicability or d2 code that reads an uncommitted repo file. Reads are under process/ or suites/. `tests/` is not run by the workflow, so test edits (the COMMITMENT_VERSION line) are outside the commitment. That is correct.
- Residual: static import analysis does not see dynamic loads (importlib, runpy, exec). I saw them only on committed or pinned-checkout paths.
- No circularity: the workflow embeds neither sha. The custody check requires GITHUB_SHA == custody `qualification_revision` == checkout HEAD, and the recomputed commitment sha256 == the custody record. A different tree would need a different pushed sha, which the custody record rejects. The gate's `--expect-qualification-sha "$(git rev-parse HEAD)"` is self-derived, but the custody check covers it.
- The weakness is F-03: the custody source is mutable.

**Oracle and false-pass mechanisms**
- NC2-07 (real kill). I read `_killharness.py` and `test_process_kill_a1.py` and ran them: 26 passed in 14 s here, as root, with no `simulate=` used.
  - The victim blocks inside the pinned `_transaction_stage` hook (hooks verified at Runtime engine/local_authority_effect.py:797/799/920/923).
  - The parent SIGKILLs it. The row needs waitpid returncode -9, `proc_gone_after`, `completed_without_kill == false`, and a fresh observer pid.
  - Predicates are literals, not copied from observations. Controls: SIGTERM, no kill, and three store mutations each FAIL the row.
  - The `after_commit` kill happens after the real COMMIT. The hot-journal presence is recorded but not asserted, which is acceptable.
- No NC wording promises recovery after process death. `limitations.os_level_process_kill` says "must not promise recovery of the lost acknowledgement or automatic retry". The word "QUALIFIED" there is strong but scoped to SIGKILL at three seams.
- NC3-04 (pruning). The destination refusal (`operation_already_committed`, attempted false, acknowledged false) and the independent read-only SQLite counts are real. `rows_removed` and `rows_after` are harness-written, but the destination refusal is the real behaviour. `claim_issued == true` implies the Control Plane decision was `authorized`. Negative controls: nothing pruned, and destination ledger also lost (2 effects, row FAILs). 8 tests passed.
- NC4-03 deterministic.
  - Literals bind the ingress tree sha 0c0e2cf6..., the set-file sha and the 57 / 11 counts.
  - Each mutation is applied to a copy and counts only if the tree bytes changed. A control satisfying a rejection predicate fails the guard.
  - Gap: F-05.
- NC4-03a..d. I executed the probes with numeric ids and `ratified=True` (no host change). 03b, 03c and 03d returned PASS; 03a was BLOCKED because Yama is absent here. Under the developer opt-out they cap at BLOCKED. Gap: F-04.
- Diff against the base:
  - v7 and v8 differ only in NC4-03 plus the 6 added rows (computed).
  - All 30 v7 mandatory NC rows are present. 29 are byte-identical; NC4-03 keeps all 12 predicates with identical op and value, plus additions.
  - Battery v1 and v2: all 260 v1 entries are unchanged in v2 (+154 new).
  - Gate diff: only constants (v5, battery v2, profile v2) and BASELINE_ITEMS. No check logic changed.
- The 13 modified tests in tests/ are not weakened in substance except:
  - the Yama sysctl requirement was replaced by a "no sysctl -w anywhere" assertion (F-02);
  - runbook command-line parity went from at least 8 lines to exactly 2 (the provisioning moved into the committed helper);
  - hub_revision input assertions were replaced by identity and tuple assertions;
  - the blank-revision check became stricter.

**Host profile**
- Env profile v2 vs v1: required check ids, capture-script pin, identities, socket 0660 and journal mode are unchanged. v2 adds the 2751 annotation, the as-found Yama record, ubuntu-24.04 and the /var/lib base. See F-02 and F-06.
- ptrace_scope 0 gives BLOCKED, never PASS. This holds through `_ingress.yama_block_reason`, the NC4-03a probe and gate G-11 (`isolation.ptrace_scope` BLOCKED becomes INCOMPLETE; scope not in 1/2/3 becomes fail/incomplete).
- The 2751 claims in profile v2 match the preserved QGATE-04 review: an outsider can stat a known name; no listing, connect or state access. The review also recorded that stat of a nonexistent name is ENOENT (existence is distinguishable), which v2 does not repeat. The review's Section 5 items were reportedly satisfied via the D3 ratification; I did not re-verify them.

**Q14.** No overclaim found. The permitted wording is in `limitations.composed_chain_claim_wording_q14` and the workflow header. The prohibited form is stated.

**Custody and evidence.** Covered in F-03, F-08, F-09.
- Triggers: only `push` on branch `qgate-05/run-1`, with both jobs guarded by `run_attempt == 1`, repository, ref and event.
- The workflow-level concurrency group queues rather than cancels.
- `contents: write` is granted to the evidence job only. Checkout uses `persist-credentials: false`. `GH_TOKEN` appears only in the guard, anchor and evidence steps.
- SHA256SUMS is created before upload and again at commit, with a verify.
- Evidence is produced on failure: the key steps use `if: always()` and the shell has no errexit.
- Supply chain: dependencies are `--require-hashes`; there are no other downloads.

## 3. Must-fix-before-freeze (test / metadata / config only)

1. **F-01 (blocking).** Land the exact freeze tree on Qualification `main` before the run branch push, then show zero BAD in the simulation. Alternatively remove v8 from battery v2 `oracle.unchanged_files_sha256` and regenerate (tests/test_mvp_acceptance_gate.py `test_v8_is_in_force...` would need an edit; commitment v6).
2. **F-02.** Either (a) restore `sudo sysctl -w kernel.yama.ptrace_scope=1` only when the as-found value is below 1, recording both values, in tools/qgate05_host_setup.sh provision and the workflow lines 199-203; or (b) have the Owner accept in writing that a BLOCKED Yama row is an acceptable outcome of the single run. (a) is preferred because it restores the v1 profile. Either needs a commitment v6.
3. **F-03.** Make the custody-file commit and its time precede the run-branch push, and require that the hub custody record is on the hub default branch at that point. Better still, read it at a pinned hub commit (needs a workflow edit).
4. **F-04 / F-05.** Disclose them in the Owner's freeze record at minimum. To fix: add the facts to the NC4-03a..d rows, and add mutations for the uncovered rules to the set (v1 set file and oracle v9, so a new commitment).
5. **F-07 / F-08.** Correct the `QG5_DURABLE_DIR` wording, and redact or avoid the token URL in lines 81-83 (use `git -c http.extraheader` or sed). These are optional and low risk but need commitment v6.

If items 2, 4 and 5 are not taken, record them as known residuals in the freeze record.

## 4. Reproduction commands

```
# F-01: frozen files vs origin/main blobs
cd /home/claude/view-f/qual && python3 - <<'E'
import sys,subprocess; sys.path.insert(0,'tools'); sys.dont_write_bytecode=True
import mvp_acceptance_gate as G; from pathlib import Path
for rel in G.frozen_files(Path('.')):
    p=subprocess.run(['git','-C','/home/claude/cognous-stack-qualification','rev-parse',f'origin/main:{rel}'],capture_output=True,text=True)
    print('OK ' if p.returncode==0 and p.stdout.strip()==G.blob_id(Path(rel)) else 'BAD',rel)
E
# commitment regenerates byte-identically
mkdir -p /tmp/claude-0/qgate05/F/cp1 && cd /home/claude/view-f/qual && tar --exclude=./results --exclude=./docs -cf - . | tar -xf - -C /tmp/claude-0/qgate05/F/cp1
cd /tmp/claude-0/qgate05/F/cp1 && python3.13 -B tools/mvp_acceptance_gate.py commit --repo-root . --out /tmp/regen.json && cmp /tmp/regen.json process/mvp-acceptance/candidate-commitment.proposed.v5.json
# NC2-07 / NC3-04
cd /home/claude/view-f/qual/suites/mvp-chain && source /tmp/claude-0/qgate05/b1env.sh && MVP_RESULTS_DIR=/tmp/claude-0/qgate05/F/res-kill TMPDIR=/tmp/qgF MVP_INGRESS_PROFILE=developer-optout python3.13 -B -m pytest -q -p no:cacheprovider test_process_kill_a1.py test_ledger_pruning_a2.py
# v7 vs v8 rows: Python dict comparison of rows (only NC4-03 differs; 6 rows added)
# Host probes with numeric ids and ratified=True: monkeypatch _nc4_03_host.identities, call run_host_subcases
```

Scratch files: /tmp/claude-0/qgate05/F/{disposition.md, committed.txt, regen.v5.json, cp1, chk, res-host, res-kill}. `/tmp/qgF` is a scratch TMPDIR outside F/ that I created; it can be removed.

## 5. Not reproduced

I did not run the workflow, the runner, Yama, the real useradd identities, or the ACL checks. I did not verify action SHAs, evidence-branch permissions or rulesets (403 from here). I did not read Worker E's scratch space.

REVIEWER PRE-EXECUTION: BLOCKING FINDINGS (1 HIGH)
