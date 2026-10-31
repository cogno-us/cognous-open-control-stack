# OCS-MVP-QGATE-05 Owner freeze review (E2) - candidate fa12c699939880149ed3997cbc2b11b264b23acd

Role: fresh-context AI Qualification Owner, separate immutable view, no write authority. AI-assisted technical review only. Not independence, not Q7, not certification, not release authority.
Scratch: /tmp/claude-0/qgate05/E2/ (env.sh, tree/ and tree2/ = clean checkouts of fa12c699, freeze-record.scratch.json, verify.out).

OWNER DECISION: APPROVE TECHNICAL FREEZE AND AUTHORIZE ONE BATTERY DISPATCH

## Per item

(a) D-1 Yama and host profile - VERIFIED
- tools/qgate05_host_setup.sh: reads kernel.yama.ptrace_scope as found; only if the file exists and the value is numerically < 1 runs `sudo sysctl -w kernel.yama.ptrace_scope=1`; 1/2/3 untouched; absent stays absent (rows BLOCK); failure recorded (`raise-to-1-FAILED`); yama-record.json {as_found, effective, action}. Only one executable sysctl, only value 1.
- The base 56a618eb workflow had `sudo sysctl -w kernel.yama.ptrace_scope=1` (line 201); restored in effect, raise-only. Workflow calls the helper and prints yama-record.json; run-identity.json embeds it.
- tests/test_mvp_acceptance_gate.py again requires the sysctl string, `[ "$YAMA_FOUND" -lt 1 ]`, ordering as-found < sysctl < effective, both record keys, and no sysctl in the workflow body. Ran: 215 passed, 212 subtests (clean clone fa12c699).
- Profile v2 diffed field-by-field against v1 (script): only host.*, ipc annotation, base_path, yama wording, supersedes/status differ; yama.ptrace_scope_min 1, identities, 0660 socket, 0700 state, no-ACL, non-root ingress, peer-UID allowlist unchanged. v2 wording is honest (no claim about runner default; establishment stated). IPC 2751 appears only as the bounded synthetic test (D3), NC4-03c asserts it.
- Environment record (hub capture, G-11 ptrace >= 1) still independently decides.

(b) Diff 7267570a..fa12c699 - VERIFIED
- 21 files modified, 0 added. Read the workflow, helper, custody check, evidence script, profile, runbook/README, tests, _nc4_03_host, derive scripts, oracle builder diffs line by line. No weakened assertion or changed expectation found.
- Oracle v8 vs v7 (script): rows 42 -> 48; added NC2-07, NC3-04, NC4-03a..d; only NC4-03 changed (12 v7 predicates retained, identical op/value, prefix nc_unmediated -> nc4_03_det; 10+ added); no removal.
- Oracle v8 vs previous v8: only NC4-03 (count/hash values 57/11 -> 69/13, set sha) and NC4-03a..d (predicates added, none removed) changed.
- Byte-identical to base 56a618eb (sha256 compare of git show vs tree): oracle v1-v7 incl. v5-ingress-ambiguity, battery v1, commitments v1-v4, profile v1, tuple-pin.
- 8 pins in candidate-identity.inputs.json == tuple-pin file == the 8 task pins; each of /tmp/claude-0/{cp,rt,qgc-*} HEAD equals its pin and is clean.

(c) Counts (own script) - VERIFIED
oracle rows 48; mandatory 47 (KL-01 the only non-mandatory); mandatory NC 36 in 7 groups (NC1 5, NC2 7, NC3 4, NC4 8, NC5 5, NC6 4, NC7 3); battery tests 435 (oracle_row 47, nc4_03_predicate 183, mutation_set 135, host_subcases 8, nc2_07 18, nc3_04 8, route_b 16, nc2_06 6, ruling_4 6, applicability 6, verdict_engine 2); unique claims 47 (distinct `row` values); non-mandatory tests 7 (KL-01 + D2C-01..06); pending_rows 0. Match the stated numbers.

(d) NC2-07 / NC3-04 / NC4-03 / NC4-03a..d - VERIFIED (no false-pass mechanism found)
- Ran under /usr/bin/python3.13.18 with MVP_*_DIR on pinned checkouts: kill, pruning, mutation_set, host_subcases, kwflow, verdict_engine = 354 passed.
- NC2-07: _killharness.py: victim blocks at the pinned `_transaction_stage` seam, parent `os.kill(pid, SIGKILL)`, waitpid returncode -9, /proc gone, disk hashed before any open, fresh observer PID; oracle asserts kill_signal 9, term_signal 9, completed_without_kill false, per-seam row/claim/reconcile facts. Real kill, not synthetic.
- NC3-04: control (ledger intact -> hold operation_renewal_unrecorded), pruned (rows 0, claim issued, destination refuses operation_already_committed, effect count 1); limitation preserved.
- NC4-03: 69 mutations, 7 families, 13 controls, all six fields present on every item (checked), structure validator clean, 69/69 rejected, 13/13 accepted, control-guard empty, pinned input matches target. My tamper probes: wrong expected rule -> FAIL (set structure); non-matching anchor -> FAIL (mutation not applied counts as not rejected). Unapplied or no-change mutation cannot count as rejected. New test asserts every _kwflow rule id is expected by some mutation.
- NC4-03a..d: rows now assert literal observed facts (ptrace in 1/2/3; dir 0o2751; socket 0o660; outsider stat ok / listdir EACCES / connect EACCES; member connect ok; empty allowlist refused; PEER_NOT_ALLOWED and not stub-core-reached; cap_eff zero; outsider uid 65533) plus the facts booleans; status-only record -> FAIL (tested per predicate). Operators in/contains/not_contains exist in the oracle. developer-optout caps status at BLOCKED. Missing observation = FAIL/NOT RUN, never PASS.
- NOT VERIFIABLE HERE: the four host rows on a real ratified profile (this container has no Yama and no dedicated identities); they are exercised only in the single hosted run. Deterministic AST pins are honoured on CPython 3.13 minor only (runner patch version differs from 3.13.18; ast.dump stability across 3.13 patches assumed, fail-closed to BLOCKED/FAIL, disclosed in the code).

(e) Q14 - VERIFIED
grep over workflow, process/, tools/, suites, tests, README: every mention of live socket / end-to-end is the permitted claim or the PROHIBITED statement; oracle limitation `composed_chain_claim_wording_q14` carries both; no row or text claims a live socket request produced Replay, Evidence Pack or Verifier evidence.

(f) Workflow - VERIFIED (static read; not executable here)
- ubuntu-24.04 both jobs; setup-python 3.13 and sys.version assertion; trigger is push to qgate-05/run-1 only (no pull_request/workflow_dispatch/schedule/tag); `github.run_attempt == 1` and repository/ref guards on both jobs; no retry or continue-on-error; guard step also refuses if qgate-05/evidence-run-1 exists (ls-remote rc checked).
- Custody: hub checkout `ref: qgate-05/custody-1`, sparse, persist-credentials false; record path and fields asserted; hub branch head recorded; custody_check asserts GITHUB_SHA == qualification_revision == checkout HEAD and recomputed commitment sha256 == record, output written only when no problems; runs before any test; gate step uses the custody value as --expect-commitment-sha256.
- Evidence: upload-artifact `if: always()`, SHA256SUMS, evidence job `always()` after acceptance, append-only fast-forward, explicit refspec, no force; gate failure keeps evidence and fails the job honestly.
- Token: passed as http.extraheader on the command line only, stderr redacted via sed, no token URL anywhere (test asserts). 
- Action SHAs: I re-ran `git ls-remote`: 11d5960a (v4), a26af69b (v5), ea165f8d (v4.6.2), d3f86a10 (v4.3.0) all exist upstream.

(g) Commitment v5 - VERIFIED
- sha256 of process/mvp-acceptance/candidate-commitment.proposed.v5.json == 814430869c63ab57cae091624c512bb119a3291e39e043827ae180ad59d3ca49 (clean git archive of fa12c699); 216 files; every listed file hash recomputes; gate.commit_files() on the clean tree equals the committed list exactly; commitment does not list itself; no __pycache__.
- Worker D: build_freeze_record.py then verify_freeze_record.py --require-final-tree on a clone of fa12c699 -> `verify_freeze_record: PASS (0 failing checks)`, rc 0, 72 OK lines. Record is unapproved/scratch.
- Own recomputation (inline python importing nothing of Worker D): per-file sha256 of all 216, list equality, commitment sha256 - all agree.

(h) Disclosed residuals - VERIFIED
Scratch freeze record limitations (14) contain: same-lineage AI roles / no formal independence; F-01 and F-03 prerequisites (G-02c needs the freeze tree on Qualification main; custody branch pushed first); F-06 (/var/lib base path never run on a hosted runner); F-09; F-10 (VER-01/03 PASS on exit 3 ABSTAIN); F-11; F-12 (floating ubuntu-24.04 label; action pins). Also Q14 scope, ODES pin-only, KL-01, synthetic fault supplementary, local runs are not evidence.

## Defects
None blocking. Observations (non-blocking, already disclosed or inherent): hosted run is the first execution of the provisioning + 4 host rows (F-06); AST-digest pins fail closed off CPython 3.13; GITHUB_TOKEN reading the hub repo's custody branch relies on the same cross-repo access the pin checkouts already use (a failure spends the run without verdict, see precondition 1).

## Approval statement text for the freeze record
"Technical freeze of Qualification candidate fa12c699939880149ed3997cbc2b11b264b23acd (candidate commitment v5, sha256 814430869c63ab57cae091624c512bb119a3291e39e043827ae180ad59d3ca49, 216 files; oracle v8 sha256 498efc12fc1f608fb6fb53738ef61776cb576a70573f0644eb42a0f3e35f359c; battery v2 sha256 61228fad3d28aa9188e528ec8dbea3952308bdc8ad750d7d1628755f46e4d262, 435 entries; tuple pins as in candidate-identity.inputs.json) is APPROVED AS AI-ASSISTED TECHNICAL APPROVAL ONLY, and ONE battery dispatch (push of qgate-05/run-1, run_attempt 1) is authorized, subject to the listed preconditions. Role instantiation: fresh-context builder-spawned subagent, separate immutable view, no implementation-write authority. This does NOT satisfy the separate top-level session requirement and makes no claim of organizational independence, Q7, certification, Final Tier 1, release or production readiness. Production-code change, pin substitution, weaker oracle or a second run require separate Architect authority. Standing holds unchanged: F3 CLOSED, Q2/Q3 UNRESOLVED; Q7 NOT ESTABLISHED; Final Tier 1 DEFERRED, NOT WAIVED; publication/release/production HOLD; Registry #58/#59, Control Plane #87, Ed25519 #26/#34 HELD; constructor tolerance NOT AUTHORIZED; V09 SEPARATE; DEF-OBS-TOL-OVERFLOW-1 OPEN, SEPARATE; R1 DEFERRED."

## Preconditions before qgate-05/run-1 is pushed (in order; each a single-use irreversible step)
1. Custody record `{"schema":"cognous.qgate05-freeze-commitment/1","qualification_revision":"fa12c699939880149ed3997cbc2b11b264b23acd","candidate_commitment_sha256":"814430869c63ab57cae091624c512bb119a3291e39e043827ae180ad59d3ca49"}` pushed ONCE (no force, no amend) to hub branch qgate-05/custody-1 at docs/mvp-recovery/qgate-05/custody/freeze-commitment.json; confirm it is readable by the Qualification workflow token. Old custody values (edc53a4a..., 7267570a) are void.
2. The exact tree fa12c699 (oracle v8, battery v2, all 216 committed files) is on Qualification `main` (G-02c compares each frozen file with its blob on main; absent -> INCOMPLETE).
3. Freeze record built with Worker D tools from fa12c699 and verified (`--require-final-tree`, then `--require-approved` with this statement); record carries the 14 limitations.
4. qgate-05/run-1 and qgate-05/evidence-run-1 do not exist; qgate-05/run-1 is pushed once at exactly fa12c699 and never again; no re-run, no second dispatch.
5. Pinned checkouts/ hub capture script preflight remain as in the workflow (no substitution).
