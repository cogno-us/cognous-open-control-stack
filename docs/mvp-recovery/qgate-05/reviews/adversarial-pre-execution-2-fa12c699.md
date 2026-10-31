# OCS-MVP-QGATE-05 adversarial evidence review (Reviewer F2): PRE-EXECUTION, FIXED TIP fa12c699

REVIEWER PRE-EXECUTION (FIXED TIP): NO BLOCKING FINDINGS

Non-authorizing. AI-assisted adversarial technical review only. Not external certification, not Q7, not release authority.

## 0. Separation achieved (honest)
- I am a fresh-context subagent spawned by the builder session, NOT a separate top-level session. Same model lineage and host as the builder; no organizational independence.
- I did not read /tmp/claude-0/qgate05/E/ or E2/. I read the predecessor report (F) and handoff/fix.md and treated the fixer's text as claims.
- I wrote only under /tmp/claude-0/qgate05/F2/. No host changes (no useradd, no sysctl). The Yama probe used a stub sudo and a scratch file.
- `diff -rq` of /home/claude/view-f2/qual against `git archive fa12c699` (excluding results/) is empty, so the inspected tree is fa12c699.

## 1. Recomputed counts (scripts, my own runs)
| item | expected | got |
|---|---|---|
| oracle v8 rows / mandatory | 48 / 47 | 48 / 47 |
| mandatory NC rows / groups | 36 / 7 | 36; NC1 5, NC2 7, NC3 4, NC4 8, NC5 5, NC6 4, NC7 3 |
| battery v2 entries | 435 | 435 (oracle_row 47, predicate 183, mutation_set 135, host 8, kill 18, prune 8, routeB 16, nc2_06 6, ruling_4 6, applicability 6, verdict_engine 2) |
| pending_rows | 0 | 0 |
| v7 mandatory NC rows retained | 30 | 30, none missing. Only NC4-03 changed vs v7. NC4-03 keeps all 12 v7 predicates (same op/value, prefix rebased). The 6 new rows are NC2-07, NC3-04, NC4-03a..d |
| commitment v5 sha256, files | 81443086...ca49, 216 | 81443086...ca49, 216. `gate commit` on a copy regenerates it byte-identically |
| `build_oracle_v8_and_battery_v2.py --check` | CHECK OK | CHECK OK |
| historical files vs base 56a618eb | byte-identical | v1..v7 oracles, battery v1, commitments v1..v4, profile v1, tuple-pin unchanged. candidate-identity.inputs.json differs by design (its env-profile sha is now 4ca8f175..., which equals the v2 file) |
| `tools/mvp_acceptance_gate.py` | unchanged in the delta | not in the 7267570a..fa12c699 diff. No check logic changed |
| committed files embedding fa12c699, 7267570a, ff3b40d0, 81443086 or edc53a4a | none | none (grep). No circularity: the workflow and committed files embed neither the commitment nor the custody commit |

## 2. Local re-runs (python3.13, MVP_*_DIR from b1env.sh, scratch copy)
- test_nc4_03_mutation_set.py + test_nc4_03_host_subcases.py: 143 passed.
- tests/test_mvp_acceptance_gate.py: 214 passed, 1 skipped, 212 subtests.
- test_mvp_chain.py + test_verdict_engine.py under developer-optout (world-traversable TMPDIR): 46 passed, 4 failed. The 4 are NC4-03a..d BLOCKED, the expected local result. (An earlier attempt with a non-traversable TMPDIR also failed NC2-06, NC4-01/02/04 and KL-01. That was my TMPDIR, not the candidate.)
- Host rows with status forced to PASS and `ratified_profile` forced true, hub dir supplied: NC4-03b, c and d are PASS, so every new literal predicate holds on the real probe output. NC4-03a fails with Yama absent here, correctly.
- Mutation discrimination experiment (below, F-05).

## 3. Prior findings
| # | Status | Evidence at fa12c699 |
|---|---|---|
| F-01 (HIGH, procedural) | OPEN as a procedural precondition, not a candidate defect | The order (custody branch, then freeze tree on Qualification main, then the single run-branch push) is now written in the workflow header, runbook, profile and hub docs. Nothing can check it before the run. Hub `qgate-05/custody-1` does not exist yet. No `qgate-05/*` branch exists on Qualification (the evidence branch is absent, so the run is unspent). See N-03 and N-04 |
| F-02 Yama | RESOLVED | The `qgate05_host_setup.sh` provision step reads the as-found value, runs `sudo sysctl -w kernel.yama.ptrace_scope=1` only if the file exists and the value is numerically below 1, and writes the as-found value, the effective value and the action to yama-record.json. I ran the logic with a stub sudo over found = 0, 1, 2, 3, absent, empty and "abc". Only 0 calls sysctl (effective 1). 1, 2 and 3 are untouched, so it cannot lower. Absent stays absent and non-numeric is left alone. A failed sysctl is recorded as `raise-to-1-FAILED`. The script has no `set -e`, so nothing aborts. The test requires exactly one sysctl and only the `=1` value, ordered after the as-found read and before the effective read |
| F-03 custody source | RESOLVED, LOW residual (N-01) | The checkout uses `ref: qgate-05/custody-1`. The step asserts the record path and the fields (verified: a missing field fails), records the branch head to custody-hub-branch-head.txt, then runs the unchanged-logic check |
| F-04 NC4-03a..d | RESOLVED | The rows assert raw observed literals (03a ptrace_scope in "1","2","3"; 03b outsider uid 65533 and cap_eff all zero; 03c dir_mode "0o2751", socket_mode "0o660", the outsider stat/EACCES/EACCES residual, group member "ok"; 03d the empty-allowlist refusal and the response contents) plus the facts. The evaluator treats a missing observation as False, so there is no vacuous pass. A status-only record gives FAIL, and the test contradicts every predicate individually. See N-02 |
| F-05 mutation coverage | RESOLVED | See section 4 |
| F-06 base path unproven on a hosted runner | OPEN, PLAUSIBLE residual | Cannot be tested pre-run. It is disclosed in the freeze record limitations and is an INCOMPLETE risk, not a false pass |
| F-07 QG5_DURABLE_DIR | RESOLVED | grep shows no occurrence in the workflow, helper, profile or committed tests (only a negative assertion) |
| F-08 token in URL or artifact | RESOLVED | No `https://x-access-token:...@` anywhere. The token is an `http.extraheader` on the command line only. stderr goes to a separate file and is redacted. I ran the exact guard `ls-remote` form with a real token against the Qualification repo: rc 0, empty output for an absent branch, so the header form is accepted by GitHub. The sed redaction works as intended |
| F-09 artifact digest and ruleset | OPEN, LOW | Disclosed. No server-side enforcement of append-only |
| F-10 ABSTAIN vocabulary | OPEN, LOW | Disclosed only |
| F-11 03b/03c wording | OPEN, LOW | Disclosed only. Not a false pass |
| F-12 action pins, floating runner label | OPEN, LOW | Disclosed only. The lead verified the SHAs exist upstream |
| F-13 hub docs | RESOLVED for candidate scope | Per the fixer, the hub-side docs are rewritten but uncommitted in wt-hub-d (not inspected by me; the lead must commit them) |

## 4. Fresh attack on the delta
- **Mutation set (F-05 control).** The new GENERIC-FORWARD family has 12 mutations (M043..M054) and 2 controls. My independent check of `_kwflow.py` found 18 upper-case rule-like constants. Every one except the sentinel UNRESOLVED is the expected rule of at least one mutation, so the coverage claim is true. Discrimination test: I rewrote every non-ORIGIN_VIOLATION GENERIC mutation to expect ORIGIN_VIOLATION. The run gave FAIL with exactly 10 mutations not rejected (M043..M052; the 2 ORIGIN_VIOLATION ones were unchanged). So each mutation fires its own rule, not just any rule. The NOOP control requires violation_count 0 and pinned_sites_used 3, so a rule firing on a no-op is impossible. BENIGN requires a changed-bytes, AST-neutral edit and `mutation_applied`. 69/69 rejected and 13/13 accepted are recomputed by script and by test.
- **Circularity of rule choice.** The rules for 9 of the 12 are assigned in the derive script after observing the scan. The swap experiment above shows they are not interchangeable, so this is not a false-pass path.
- **Yama.** It cannot lower or fail destructively. The effective value is read after the attempt. The only residual is an unwritable sysctl, which is recorded and produces BLOCKED/INCOMPLETE, not a false pass.
- **Burn paths.**
  - The guard `ls-remote` header form is verified (above). The rc is captured right after the command, and the sed runs on the .err file after it.
  - All `run:` blocks pass `bash -n`. The YAML parses. Permissions are `contents: read` at the top level and `contents: write` only in the evidence job.
  - The hub is public, so the default token can check out the custody branch.
  - If `qgate-05/custody-1` is absent or the record lacks a field, the acceptance job fails before any test, but the evidence job still runs (it only needs the acceptance result not skipped). The run is then spent with no verdict. That is the procedural ordering risk (F-01 and N-03).
  - The custody heredoc and `set -eo pipefail` are sound.
  - The evidence branch tree is an orphan commit containing only runs/, so no workflow-file `workflows` permission is needed. The array expansion `"${GITN[@]}"` is safe with `set -u`.
- **Uncommitted files at run time.** None found. The delta adds no files. The commitment regenerates from the committed set (216 files), and the fixer's freeze-record verify also passes.
- **Harness bug making the run uninterpretable.** The `observed` and `facts` additions are JSON-serialisable (results.json was produced locally). A probe exception still yields BLOCKED for that subcase only. No new path crashes the scenario.
- **Weakened assertions.** The test diff only strengthens (sysctl restored with the raise-only guards, custody ref and fields, no token in URL, counts). Nothing removed besides the durable-dir requirement.

## 5. New findings
| # | Sev | State | Finding |
|---|---|---|---|
| N-01 | LOW | CONFIRMED (design) | The custody branch is mutable. The workflow checks out a branch name, records the head sha afterwards, and cannot pin it (pinning would be circular). A hub write between approval and the run changes what is read. The effect is a mismatch (INCOMPLETE) or a record that matches a different tree, which cannot happen for the pushed sha. Mitigation, no file change: the lead records the custody branch head sha in the Issue #215 comment before the push and compares it with custody-hub-branch-head.txt in the evidence |
| N-02 | LOW | CONFIRMED | `test_every_rule_the_predicate_can_emit_...` (`suites/mvp-chain/test_nc4_03_mutation_set.py`): the regex `[A-Z]+(_[A-Z]+)+` would miss a rule id with digits or no underscore, and `emitted.discard("UNRESOLVED")` is a no-op because the regex never matches it. I checked independently that nothing is missed today. No action needed; changing the file would force commitment v6 |
| N-03 | LOW | CONFIRMED (procedure) | The custody record's `qualification_revision` must equal GITHUB_SHA. The run branch must therefore be pushed at exactly fa12c699. If the freeze tree lands on main as a squash or merge commit, do NOT push the main commit to qgate-05/run-1. Push fa12c699 itself. G-02c compares blob ids to main, so the content match is what matters |
| N-04 | INFO | CONFIRMED | Before the push, re-run the F-01 blob simulation (zero BAD, including process/mvp-chain/expectations.proposed.v8.json) after the freeze tree is on Qualification main. Also check that the hub branch exists. Neither can be checked by the workflow beforehand |

## 6. Must-fix-before-freeze (test, metadata, config only)
None. No change to a committed file is required. Any edit would force commitment v6.

Pre-push checklist (lead, not candidate edits): (1) hub `qgate-05/custody-1` pushed once with the fa12c699 and 81443086 record, and its head sha noted (N-01); (2) fa12c699 content on Qualification main, simulation shows zero BAD (F-01, N-04); (3) qgate-05/run-1 pushed once, at fa12c699 (N-03); (4) hub docs committed (F-13).

REVIEWER PRE-EXECUTION (FIXED TIP): NO BLOCKING FINDINGS
