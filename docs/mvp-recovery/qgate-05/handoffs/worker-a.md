# Worker A handoff (OCS-MVP-QGATE-05): source-backed qualification-metadata reconciler

Worktrees (uncommitted): hub /home/claude/wt-hub-a (2583b32), Qualification /home/claude/wt-qa (56a618eb). No oracle/battery/gate/workflow/suite code/lock/pin/identity/commitment/profile file changed (OBSERVED: `git status` in wt-qa lists only 3 text files).

## Files (sha256)
Hub, new:
- docs/mvp-recovery/qgate-05/build_successor_manifest.py a4ea2cd6b1c366edfc4817b9d9c443d71349b05f1912f5272906dba916973940
- docs/mvp-recovery/qgate-05/metadata-repair-record.md 7a814721bf33116ec1fa1320d8c15c975099481e4b1ace836be02433fff1af5b
- docs/mvp-recovery/qgate-05/errata-r10-ipc-directory-mode.md 643e2607b7711571d52af125da6c2292517ae04e3ac100935fbf188688350118
- docs/mvp-recovery/qgate-05/issue-215-correction-draft.md (NOT posted) b0c8d43dafb455694a539d2c9024519c7dd819d069f98bbcfdb318bae20316e5
- docs/mvp-package/candidate-manifest.successor-2026-10-31.json 44744cac3410ed30d10a4722fe0fff96ea6772a1718e1553283c9410a6de0eeb (PROVISIONAL output from today's 56a618eb tree: REGENERATE after assembly)
Hub, appended dated errata only (text above unchanged):
- docs/mvp-package/INDEX.md 0a3a78a0f1fa0fab35125c61e43cc2b4b3277bc5747a06c83621cb2bc49245e4
- docs/mvp-package/dependency-manifest.md 648bca52e933546bd8ec392515c3e2657e388e68939995151ef6358346c56139
- docs/mvp-package/source-inventory.md 8cfa21e19785b6ce7c56cb7e20b351b9843cadc3b70776f959b1de494d3929fc
- docs/mvp-recovery/critical-path.md 303b3d0c601b0e268d5f47583ece45e9a5b4fde12dce87dbcd947749c739c3ce
- docs/mvp-recovery/delivery-estimate.md 6c9c85191220746428971176cb0c42980e2c620660937dd2122c78daf35697be
- docs/mvp-recovery/implementation-status-2026-10-23.md 4dc921a0051f354a5e2283a97acbe7d0909eff12f0a45aec8988ee2ef9695a61
- docs/mvp-recovery/mvp-definition.md bcb2a729ac199af8ef8dd8da3dbd20ab57e3f1c8364ae124f6e23c114459eed0
Qualification, text-only edits:
- suites/mvp-chain/README.md 1f5957e7df7f61bf05a470cc2cd4b19e37341845dc207b6e313838512adcd5d6
- process/mvp-acceptance/README.md 3476eda1d54d55c1f200333f59bad47ce65cefc6775987c7cce820179abaec8d
- process/mvp-acceptance/mandatory-battery.ingress-ambiguity.placeholder.md (appended dated note) a765439d9ef49a32ce3ad35ccc7529ecd08f6aaaec51235e3670b96e7c833ba0

IMPORTANT for the lead: these three Qualification files are in the committed set (process/mvp-acceptance, suites/mvp-chain), so they must be final BEFORE commitment v5 is generated; the sha256s above change when you fill the placeholders.

## @@FINAL_COUNTS@@ sites (10 occurrences)
- suites/mvp-chain/README.md:48 (oracle paragraph, final v8 counts)
- suites/mvp-chain/README.md:60 (negative controls heading note: mandatory NC rows / groups)
- suites/mvp-chain/README.md:67 (NC4 row, amended NC4 rows)
- suites/mvp-chain/README.md:70 (new NC7 row, rows added by v8)
- suites/mvp-chain/README.md:97 (3 occurrences: NC7 section v7/v8 counts; battery v2 entries; final mandatory claims)
- process/mvp-acceptance/README.md:10 (2 occurrences: battery v2 counts; final mandatory oracle rows)
- process/mvp-acceptance/mandatory-battery.ingress-ambiguity.placeholder.md:34 (appended note)
Find: `grep -n @@FINAL_COUNTS@@ -r suites process`. Also, if v8 adds rows for real OS-kill, ledger pruning and the NC4-03 mutation set, the README row lists (lines 67/70) may want names; I did not invent them.

## Commands run (OBSERVED)
Wrapper /tmp/claude-0/qgate05-a-run.sh (python3.13 -B build_successor_manifest.py --qa-root /home/claude/wt-qa --tuple-pin .../tuple-pin.proposed.json --oracle-v7 ... --battery-v1 ... --profile ... --commitment ...v4.json [extra]).
- Generate twice: identical bytes (cmp IDENTICAL), sha256 44744cac...; `--check`: CHECK OK, rc 0.
- Tamper test: edited digest in a copy -> `--check` prints diff, "CHECK FAIL", non-zero exit. Wrong `--external-commitment-sha` -> FAIL (exit 2).
- Recomputed at 56a618eb (reproduce QGATE-04): candidate_identity_inputs e7484a0afa1758b3925801ae6cf70a718f676eaa593addb9c20d739b9654c7fb; tuple_pin efe9be3eb3a2c68121f9dc1203a5af2d194b24989c617a9029d09b1ccf25844b; registry sha256:22f49fd1341cfaa6e46727db9b6153c2073b82a3125fd725173494f3ebb37650; oracle v7 0dc17a1984e1c3c153f3cb6e3f7fdd4dad87cdc4414728a20df0f8174e402f6b; oracle v6 fe6ecf87...; battery v1 a520e9e92534f196a48d4229d984231abbb71c23dfe63b573d919d2285bcdb16; profile 78518a9fa49e372203bb902e5ff59ec9dd5296234930c68d2cc6b5a42f4f9207; commitment v4 c26db0edec0a0e17ed816bc1ca519bb9c07badfd49ce4fc93c64e77dfb721160; component-lock dcd3ab9e4e737c7e50f4bc38c2439438f156da64c9eb1e46725f477973da59ff; requirements lock (hub = Qualification lock) 84caee9ea5fcc297270d1b0a8c68f279e849c814b8052b2a54bb618bd9ef9ff5; ingress *.py tree 0c0e2cf6a69f4ce69d4ca39ac7a443890a05b50ba420902e2d346912d369f591. Qualification reference = git HEAD of the tree (or `--qa-sha`).

## Final-assembly use
`python3.13 -B docs/mvp-recovery/qgate-05/build_successor_manifest.py --qa-root <final tree> --tuple-pin F --identity-inputs F(optional; default <qa>/process/mvp-acceptance/candidate-identity.inputs.json) --oracle-v7 F --oracle-v8 F --battery-v1 F --battery-v2 F --profile F --commitment F(v5) --require-final [--external-commitment-sha HEX] [--qa-sha SHA]`, then rerun with `--check`. The tool refuses (exit 2) if: tuple pin/identity inputs/historical manifest disagree on any SHA, component-lock moved, hub vs Qualification requirements lock differ, identity-inputs composite profile sha or registry digest or capture-script sha differ from recomputation, ingress *.py file set differs. Only stdlib; no network; uses `git rev-parse` locally for tree ids/Qualification sha. If the final tree is a git commit, run it from a clean checkout of that commit so HEAD is the final reference. Note: the script's file path arguments are recorded relative to --qa-root; it does not assume file names except the v6 oracle, Qualification lock and identity inputs defaults.

## Not done / residuals
- Hub profile doc `ingress-qualification-environment-profile.md` deliberately NOT appended (hash-pinned original profile; R-10 erratum lives in qgate-05/errata-r10-ipc-directory-mode.md). Lead may add a one-line pointer.
- `qualification-initiation.md` (R-02 cite) not edited; superseded by the successor manifest.
- Info heads (CP b19c47dd, Runtime f7a55e2a, Verifier 39d46b49, hub main c40bfcd) are constants taken from freeze-reconciliation.md section 1, not re-observed (no network); labelled so in the manifest.
- Successor `created` is fixed 2026-10-31 (override `--created`).
- R-07 lock unmoved, PR #223 unmerged, disposition unrecorded; R-09/R-13/R-14/R-15 open per register. Commitment external anchor is not set.
- Observed hub issue #215 body and disposition comment 6537418060 via gh api (read-only).

## Paths for the commit
Hub: all 5 new files and the 7 appended docs above. Qualification: the 3 README/note files (after placeholders are filled).
