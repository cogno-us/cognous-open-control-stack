# Worker D handoff: candidate-freeze package and evidence custody (OCS-MVP-QGATE-05)

Worktree: /home/claude/wt-hub-d (detached at 2583b32b, uncommitted). Only `docs/mvp-recovery/qgate-05/freeze/` is new; `git status` shows only `?? docs/mvp-recovery/qgate-05/`. Qualification checkout untouched (verified clean, no __pycache__ afterwards).

## Files (sha256), paths wanted in the commit (all five)
| path (under docs/mvp-recovery/qgate-05/freeze/) | sha256 |
|---|---|
| build_freeze_record.py | 9d595ee58e3fc15b4b79426e0c5ead846ed2bbde822bbcdb7894971b94de8d79 |
| verify_freeze_record.py | 2487d1027d5fa698b3be6e0136ecf0bfa151f6acbc0d2825f13ebb4f010d7961 |
| freeze-commitment.template.json | e248cc8aa1d86d3205099a451500ba8b082426b1f8ada7c06c8dc2d89b8570cd |
| ISSUE-COMMENT.template.md | 7a8177a7de0820ece11fd579bdc7f093e0317eeff1b8620711ebff20074612b9 |
| CUSTODY.md | d9a1752f3c626c5bb1bf745375e70914b3f283ead60c81a9c050372a256e5173 |
Not for commit (scratch): /tmp/claude-0/qgate05/d/ (run_build.sh, sample record freeze-record.current-56a618eb.json sha256 862a5734...50ce, tamper outputs out-*.txt).

## CLI for the lead (final tree)
```
python3.13 build_freeze_record.py --qualification-tree <Q> --qualification-revision <40hex> --prepared-utc <text> \
  --control-plane <sha> --runtime <sha> --replay <sha> --evidence-pack <sha> --odes <sha> --verifier <sha> --action-manifest <sha> --hub <sha> --out freeze-record.json
   (optional --commitment REL / --battery REL; default = highest vN in process/mvp-acceptance; --prepared-by)
python3.13 verify_freeze_record.py --qualification-tree <Q> --record freeze-record.json --qualification-revision <40hex> \
  --expect-commitment-sha256 <hex64> [--require-final-tree] [--require-approved] [--skip-gate]
```
Exit 0 pass, 1 mismatch, 2 unreadable. Reproduction of my run: /tmp/claude-0/qgate05/d/run_build.sh OUT.json.

## Results (OBSERVED, against Qualification 56a618eb)
- Determinism: two builds gave byte-identical files, sha256 862a57346191a93c1be5a6fbd440a33aade628f4989286b04b188e06326d50ce.
- Record values: commitment `candidate-commitment.proposed.v4.json` sha256 c26db0edec0a0e17ed816bc1ca519bb9c07badfd49ce4fc93c64e77dfb721160, 192 files, listing hash 8cf718d1ddabede46b1ff1c4411ae9e5e87368394f68eaaba426c242bec46b0a; oracle v7 0dc17a19...; battery v1 a520e9e9...; 8 tuple SHAs equal tuple-pin and identity inputs. Denominators recomputed: 42 rows, 41 mandatory, 30 mandatory NC rows in 7 groups (5,6,3,4,5,4,3), battery 260 (oracle_row 41, nc4_03_predicate 183, route_b_mediation 16, nc2_06 6, ruling_4 6, applicability 6, verdict_engine 2), claims 41, non-mandatory tests 7, pending_rows 1 (the NC4-03 placeholder; expected to be 0 in the final tree).
- Verify on untampered tree and record: PASS, 63 checks OK, exit 0 (incl. gate `commit_files()` == 192 committed, gate COMMITMENT_FILE == v4, no pycache created). With `--require-final-tree`: FAIL on pending_rows=1 (correct for the current tree).
- Tamper cases, all exit 1 (on a copy of the tree without .git/results, 31 MB): flip/append byte in committed test file; new uncommitted file in suites/mvp-chain; planted tools/yaml.py; oracle v7 bytes changed; commitment bytes changed; committed file removed; __pycache__ planted; committed file replaced by symlink. Record tamper, all exit 1: one tuple SHA off by a digit; hub=`main`; short ODES sha; oracle sha; file_count 191; mandatory rows 40; Q14 prohibited claim altered; host mode 2750; first limitation removed; standing hold removed; frozen=true without approval; wrong external commitment hash; wrong revision (caught by `--qualification-revision` and by git HEAD check against the real clone). Positive control: synthetic fully-approved record passes `--require-approved`.

## Not executed / limits
- Real final tree (oracle v8, battery v2, commitment v5) does not exist; tools are parameterised and were only exercised on 56a618eb. Local runs are not evidence.
- verify's gate check imports the tree's own gate (in a `python -B` subprocess), so a malicious gate could lie; that is the inherent limit already stated in the commitment and CUSTODY.md. The independent anchor is the externally held hash.
- Owner approval fields are empty; `frozen` false. Approved records must use status `FROZEN-TECHNICAL` (verify enforces).

## Assumptions / items for the lead and Worker C
- Gate constant `COMMITMENT_FILE` must be bumped to v5 in the same change set as the v5 commitment (verify fails otherwise).
- Workflow (Worker C) should assert GITHUB_SHA == custody qualification_revision and compare the recomputed commitment hash with the hub custody value at a pinned hub commit; CUSTODY.md states this as a requirement, not as implemented. The existing workflow already refuses qualification_revision != GITHUB_SHA (mvp-acceptance.yml:100).
- Sample record shows `prepared_by` default as Worker D same-lineage text; override with `--prepared-by`.
- No genuine authority/safety blockers.
