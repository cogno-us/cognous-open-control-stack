# Worker B2 handoff: NC4-03 frozen mutation set (A3/A4)  [OCS-MVP-QGATE-05]

Worktree: /home/claude/wt-b2 (detached 56a618eb, nothing committed). All files NEW under suites/mvp-chain/. No existing file, pinned checkout, oracle, battery, workflow or commitment was edited. Nothing written outside wt-b2 and /tmp/claude-0/qgate05 (pytest ran with MVP_RESULTS_DIR=/tmp/claude-0/qgate05/b2scratch/results, PYTHONDONTWRITEBYTECODE=1).
All local results are OBSERVED local dry runs, NOT evidence.

## Files (sha256)
- 28a97c8dcc0de724f68ce5dc6571225d77185342a27ed3ee9d2fed4b4a23c245  _nc4_03_host.py (host probes NC4-03a..d)
- e9eca747649a69f9e6e37408ac0c382629cac9c65bfc3f9f922d1dba3b421c7c  _nc4_03_mutations.py (loader, runner, deterministic verdict, compose, scenario_observation)
- ea30ba2bee7d1bc213bfd7e6cbcb7009c963addbb7f0fb81b92e465885951f37  _nc4_03_mutation_set_derive.py (authoring record; used by anti-drift test)
- 5e59e3ba4f058b16855a44d96cd5a7a5976e1b78d7b9ba690ee58b07a69fc1db  _nc4_03_v8_fragment_derive.py (authoring record of the two fragments)
- 1da3c7c8fef98ccecce1b2f6dc3dc3c2f890a8b7eab8258c7b74fda8789a5bd8  nc4_03_mutation_set.v1.json (FROZEN-candidate deterministic set)
- 69aa57d00a96874a3116845025359352b0be25b83f363689fbf29f383bcf071d  nc4_03_host_subcases.v1.json (host subcases, separate file)
- 7b7440eec5c62432031754de163c10e6856c578398c0003444fca58669482050  nc4_03_oracle_v8_fragment.proposed.json
- 4363caa7609cf4041f8d387a1f28e9c60de85ad66da4ae748745c0f47f024558  nc4_03_battery_v2_fragment.proposed.json
- 89818e988ad8ce24b57753f254a1c47b84f960753b371236eccbe2bb55bfec59  test_nc4_03_mutation_set.py (114 tests)
- 5c106c821e6aaec9373cfebb4426f1b06d5c8458f4040475a01a50b7db17e679  test_nc4_03_host_subcases.py (8 tests)

## Design
**Set (nc4_03_mutation_set.v1.json, version v1, deterministic:true, host_dependent:false).** 57 mutations in 6 families + 11 negative controls. Each mutation AND control carries the six required fields: `input` (tree, per-file sha256, anchor text with exact occurrence count), `operation` (ordered steps: replace/append/create_file/create_dir/symlink/delete on a COPY), `expected` (REJECTED + rules_all_of, or ACCEPTED), `environment` (CPython 3.13, host_dependent:false, no privileges/socket/network, scan_mode), `evidence_source` (`_kwflow.scan_dir` via `observe_tree`, observation names), `predicate` (list of {obs, op, value}, evaluated by the existing `verdict._check` operators; reused, not new machinery).
Families: OR-FIELD 9 (the six authority fields + display + reassigned claim + envelope caller; R1), OR-BINDING 13 (F1 scope, F2 producer shadowing, F3 envelope escape, N5 host binding, import/match/except rebinding), OR-LITERAL 8 (v5 literal-only keywords), OR-OBJECT 8 (authority-object mutation, model_validate, __class__), OR-FIXEDFORM 4 (fixed-form keys, positional values), PIN 15 (pinned mode, fail closed: comment-only edit of each of 7 files, semantic AST change, changed pinned site, vanished required site, 5 recursive-tree tamper cases).
Rebased families run with pins/tree digest re-based on the mutated copy so ONLY the source-aware rule decides (same technique as test_kwflow `_rebased_scan`; otherwise any edit is rejected merely by un-pinning, which would be a false-pass risk). Predicate for those: mutation_applied (operation applied AND tree bytes changed) AND the expected rule in violation_rules AND pins_unmatched_count == 0 (dropped, with reason, for the 5 `host: client ...` mutants and E15/E15b which edit INSIDE a pinned function; the origin/positional rule must still fire).
**Negative controls (11, >=1 per family).** Per rebased family: C-<fam>-NOOP (identity replace of the family's first anchor) and C-<fam>-BENIGN (AST-neutral trailing comment on the family's file); PIN: C-PIN-NOOP (byte-identical copy under pinned mode). Predicate: applied, 0 violations, 0 unmatched pins, no missing sites, 3 pinned sites used. Additional guard: no control may satisfy any rejection predicate of its family (computed per run, recorded as `control_satisfies_rejection_predicate`), plus tests that a lenient scanner (accept-all) yields FAIL with >=50 mutations not rejected and a strict scanner (reject-all) yields FAIL with controls falsely rejected. An unapplied or no-op "mutation" can never count as rejected.
**Relation to the 183 supplementary entries.** KW-001..183 (every test of test_kwflow.py) are NOT replaced, edited or duplicated: they remain the predicate's self-tests (71 neg + 7 pos fixtures, baseline, pin records, 43 `MUTANTS`, 23 `V5_MUTANTS`, tree/interpreter tests). The new set selects, by provenance field per mutation (`test_kwflow.MUTANTS[...]` / `V5_MUTANTS[...]` / test names), a frozen mandatory subset of the origin-rule mutants and tree/pin tamper cases, restated as data with the six fields, run through its own runner on a copy of the PINNED hub tree (MVP_HUB_DIR, not the kwflow_fixtures/baseline copy; OBSERVED identical bytes at c897266b), and adds the per-family negative controls the supplementary tables lack. Selected: 19 of 43 `MUTANTS` and 23 of 23 `V5_MUTANTS` (plus 15 PIN cases mirrored from named test_kwflow tests); the other 24 `MUTANTS` (generic `**` forwarding, pinned-site un-pin etc.) and the fixture-level negatives stay supplementary-only. `test_frozen_set_matches_its_derivation` is an anti-drift check (data == rebuilt from those tables).
**Deterministic vs host (A4).** `run_deterministic(hub)` is a pure function of (set file, hub tools/mvp_ingress bytes, _kwflow code, CPython 3.13). It never imports `_nc4_03_host` (test asserts via AST and bans host/clock API names in the module), is computed first, and carries its own `record_sha256` over canonical JSON. Non-3.13 or missing hub = BLOCKED; a hub tree that is not the frozen bytes = FAIL; never PASS. Test: a subprocess with scrambled env/cwd/TZ/hash seed/junk MVP_INGRESS_PROFILE reproduces the identical sha. `compose(det, host)` is the only meeting point: it copies the deterministic block verbatim (sha-asserted), sets `nc4_03_row_verdict` = deterministic verdict, and lists host statuses beside it; parametrized test over {PASS,FAIL} x {all PASS, all BLOCKED, all FAIL, mixed}.
**Host subcases (nc4_03_host_subcases.v1.json; separate rows).** NC4-03a Yama (ptrace_scope>=1), NC4-03b uid separation (dedicated non-root ingress, distinct unprivileged client, outsider 65533, distinct primary groups, CapEff 0, via forked drop), NC4-03c IPC 2751 profile (dir 2751/group/setgid, socket 0660 + group, outsider can stat known name = accepted residual D3, cannot list/connect EACCES, group member connects), NC4-03d peer-UID allowlist (PINNED hub `server.serve` on a COPY of hub tools with a stub core: allowlisted uid served, non-allowlisted group member gets PEER_NOT_ALLOWED, empty allowlist refused). Status PASS/FAIL/BLOCKED; profile `approved` (MVP_INGRESS_USER, MVP_CLIENT_USER, MVP_IPC_GROUP) is the ratified one; `developer-optout` records facts but is capped at BLOCKED (never PASS); a probe exception = BLOCKED for that subcase only. Scenario `nc4_03_host` is never "blocked" as a whole, so one blocked subcase cannot block the others or anything else.

## Oracle v8 fragment (nc4_03_oracle_v8_fragment.proposed.json; apply on v7, v7 untouched)
- NC4-03 CHANGED: scenario `nc_unmediated` -> `nc4_03_det` (the A4 decoupling: a blocked host scenario no longer blocks it). All 12 v7 predicates kept with identical op/value, only prefix `nc_unmediated.source_level.` -> `nc4_03_det.source_level.` (test asserts none lost/weakened; no blocked_if / not_applicable_if). ADDED 10 predicates: set_version, set_file_sha256 (= file sha above), verdict PASS, mutations_total/rejected = 57, mutations_not_rejected empty, controls_total/accepted = 11, controls_falsely_rejected empty, mutation_set_control_guard empty. mandatory:true.
- NEW mandatory rows NC4-03a, NC4-03b, NC4-03c, NC4-03d, scenario `nc4_03_host`, `blocked_if status==BLOCKED`, `all status==PASS`. Test: each host status maps to the same oracle status (PASS/BLOCKED/FAIL) and a missing scenario is NOT RUN; NC4-03's verdict is identical whatever the host scenario holds.
- Row delta from this fragment alone: v7 42 rows/41 mandatory -> 46/45 (+4 rows, +4 mandatory, 1 changed). Mandatory NC rows 30 -> 34, negative groups unchanged (7) (before the A1/A2 rows of other workers; recompute at integration).
- NC4-01/02/04 untouched (no expected outcome weakened). NC4-04 and KL-01 stay in `nc_unmediated`.

## Battery v2 fragment (nc4_03_battery_v2_fragment.proposed.json)
- `pending_rows`: v1's single placeholder removed -> `[]` (G-14 passes with an empty list; OBSERVED gate code at tools/mvp_acceptance_gate.py:838).
- +4 `oracle_row` entries NC4-03a..d (test_row[...] in test_mvp_chain.py); NC4-03 keeps its entry.
- +122 supplementary entries: 114 `supplementary_nc4_03_mutation_set` (test_nc4_03_mutation_set.py) + 8 `supplementary_nc4_03_host_subcases`; invocation paths of `mvp-chain` must add both new test files (G-13).
- Delta from this fragment alone: 260 -> 386 entries (+126); oracle_row entries 41 -> 45; the 183 KW entries unchanged.

## REQUIRED harness wiring (not mine to edit; owner: lead / whoever owns _chain.py, conftest, test_mvp_chain)
1. `_chain.py`: register two scenarios, e.g.
```
@scenario("nc4_03_det")
def nc4_03_det(work):
    import _nc4_03_mutations as M
    return M.scenario_observation(_state.ENV["dirs"].get("hub"), _state.ENV["heads"].get("hub"))
@scenario("nc4_03_host")
def nc4_03_host(work):
    import _nc4_03_host as H
    return H.scenario_observation(_state.ENV["dirs"].get("hub"))
```
(`scenario_observation` returns `status:"blocked"` for the det scenario only when the interpreter is not 3.13 or the hub is absent.)
2. The v7 NC4-03 observation `nc_unmediated.source_level.*` is still produced by `_ingress.run`; leaving it is harmless (v8 reads `nc4_03_det`).
3. Add the two test files to the `mvp-chain` invocation paths in battery v2, the collection step and run step of mvp-acceptance.yml (must stay identical), and mvp-chain.yml if it should collect them. On Python 3.12 (mvp-chain.yml) the pin-dependent tests SKIP with explicit reason (suite convention); the authoritative 3.13 run must show no skip (else INCOMPLETE).
4. Host rows need the `approved` env (MVP_INGRESS_USER/MVP_CLIENT_USER/MVP_IPC_GROUP) and root, same as NC4-01; the authoritative run is the GitHub-hosted ubuntu-24.04 job.

## Commands and OBSERVED local results (container: root, /usr/bin/python3.13 = 3.13.18, pydantic 2.13.5, no Yama)
- Env: MVP_HUB_DIR=/tmp/claude-0/qgc-hub (c897266b, pristine; `git status --porcelain` = 0 lines after all runs), MVP_RESULTS_DIR=/tmp/claude-0/qgate05/b2scratch/results.
- `cd /home/claude/wt-b2 && /usr/bin/python3.13 -m pytest -q -p no:cacheprovider suites/mvp-chain/test_nc4_03_mutation_set.py suites/mvp-chain/test_nc4_03_host_subcases.py` x3 consecutive: 122 passed (21.0 s, 21.0 s, 20.5 s; final regenerated set; an earlier set revision with one prose difference in the set file passed 3x as well). Deterministic record after each run: verdict PASS, 57/57 mutations rejected, 11/11 controls accepted, record_sha256 f5d4c199a4abb5d89dccba9abff45fc8c73e5f0f5ddfb04caf31e5a82faca3ca (identical x3; also identical from the scrambled-env subprocess).
- `suites/mvp-chain/test_kwflow.py` unchanged: 183 passed (5.4 s).
- Host subcases, MVP_INGRESS_PROFILE=approved (default) in this container: NC4-03a BLOCKED (/proc/sys/kernel/yama/ptrace_scope absent), NC4-03b/c/d BLOCKED (approved identities not named). => "could not execute locally" on the ratified profile.
- Host subcases, MVP_INGRESS_PROFILE=developer-optout (LOCAL DRY RUN only, root ingress, uid 65534 client, gid 65532 IPC group): probes executed; observed facts all true (uid 65534/65533 CapEff 0; dir 0o2751; socket 0o660, group via setgid; outsider stat ok, listdir EACCES, connect EACCES; group member connect ok; hub serve: empty allowlist refused, allowlisted -> stub core, uid 65531 group member -> PEER_NOT_ALLOWED); statuses capped BLOCKED by design. These dry-run facts are not evidence of the ratified profile.
- NOT run: Python 3.12 behaviour (skips are by `requires_313`; not exercised); GitHub-hosted run.

## Assumptions / things the lead should know
- Expected rule names for the selected mutations are taken from the existing `MUTANTS`/`V5_MUTANTS` tables (the ones that name a rule); nothing was re-derived from my run. Pinned-mode (PIN family) predicates use rule INGRESS_TREE_DIGEST / INGRESS_TREE_FILE_LIST and pins_unmatched_count==3, which I read from a dry run of the existing predicate (INFERENCE: authored after seeing the predicate's output for those 15 cases; they mirror assertions already in test_kwflow).
- The set freezes 57 items (42 from the 66 MUTANTS/V5_MUTANTS plus 15 PIN cases); choosing the subset is a Qualification decision (A3 sub-option "separate rows"): the generic `**` mutants are left supplementary.
- The three pinned-site provenance records still need independent establishment (NC4-03-PROPOSAL "Pins"); unchanged by this work.
- Sandbox note: running the hub D1 AST tests (`d1_ast_test_exit_code`) is done on a COPY of hub tools/tests.
- The conftest session hook prints a one-line "mvp-chain results ... FAIL 1 / NOT RUN 41" when only these files run (ENV row unwired); ignore, it is the suite's end-of-session summary with no component env.
- Genuine blockers: none for this work item. Residual (not mine): A5 (non-allowlisted group member as a separate mandatory row) is partially covered by NC4-03d; whether that satisfies A5 is the Qualification Owner's call. D3 2750-vs-2751 semantics is as ratified; the set/host file assert 2751.

## Paths wanted in the commit
suites/mvp-chain/_nc4_03_host.py
suites/mvp-chain/_nc4_03_mutations.py
suites/mvp-chain/_nc4_03_mutation_set_derive.py
suites/mvp-chain/_nc4_03_v8_fragment_derive.py
suites/mvp-chain/nc4_03_mutation_set.v1.json
suites/mvp-chain/nc4_03_host_subcases.v1.json
suites/mvp-chain/nc4_03_oracle_v8_fragment.proposed.json
suites/mvp-chain/nc4_03_battery_v2_fragment.proposed.json
suites/mvp-chain/test_nc4_03_mutation_set.py
suites/mvp-chain/test_nc4_03_host_subcases.py
