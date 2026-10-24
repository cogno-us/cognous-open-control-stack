# Source inventory (final candidate tuple, as read 2026-10-24)

Status: DRAFT, non-authorizing; every revision is PROVISIONAL / UNQUALIFIED and the tuple is not frozen. Label: VERIFIED (GitHub REST `commits/main`, `pulls` and `check-runs` metadata, and local runs, 2026-10-24) unless marked. The machine-readable form is [candidate-manifest-draft-2026-10-24.json](candidate-manifest-draft.json).

| Component | Final tuple revision (a `main` merge) | CI on that revision | Previous tuple | Hub lock on `main` | Open PRs that change it |
|---|---|---|---|---|---|
| Control Plane | `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c` (F3 #83) | 5/5 success | same | `0a41faa9` | none |
| Runtime | `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f` (F3 #144, terminal approval revocation) | 7/7 success | `ec728da6` | `ec728da6` | #126 (not in the tuple; base older than `main`) |
| Replay | `40012b8c174c6f25685bd5d9bc93ff46cc9a5842` (merge of #79, executor pairing re-tied to `c5e97e87`) | 8/8 success | `ab421ad0` | `028f63d1` | none |
| Evidence Pack | `7b9511f2c6d56d424f17b078826594abd29f6c96` (merge of #64) | 8/8 success | `79ae34d9` | `a3ebbb90` | none |
| ODES | `1a5e1d300250d832e611633f0bf8f762e398c0ec` (merge of #141) | 7/7 success | `eae95dd3` | `e86a25a1` | none |
| Verifier | `c0b8ba1f55b75db787a320f3de0f79342c6f6826` (kept; see below) | 5/5 success | same | `c0b8ba1f` | none |
| Action Manifest | `fa170815ef96a54c233d0dd9da821b60debabf8b` | 6/6 success | same | `fa170815` | none |
| Hub | `5b76c58a8bacb9efe6ed6c08e51ab7db7d03bc12` (#219; has `tools/mvp_env_record/capture_env_record.py`) | 7 of 8 success; `cross-component / reference` fails (see below) | `43c526eb` | n/a | draft #223 (lock bump), #224 (this package), #221, #222 (not touched) |

Notes
- Hub lock: draft #223 moves the lock to the tuple above (Control Plane, Runtime, Replay, Evidence Pack, ODES). Verifier, Action Manifest and `gax_imx_transport` entries are unchanged. See [dependency-manifest.md](dependency-manifest.md) for the blocking qualification-side pins.
- Verifier: `main` is `39d46b49` (#42), one commit after `c0b8ba1f`. The diff was read: two `README.md` lines and the `note` string of `release-state.json` change (they now name the review-marker tag); no code and no boolean change. At the tuple, the `mvp-chain` suite gives the same result at both revisions (36 PASS, 1 FAIL: NC4-03). `c0b8ba1f` is kept so the lock, the review-marker tag and the Qualification files name one Verifier; `39d46b49` is an acceptable one-line substitution.
- Hub `cross-component / reference` has failed on every hub `main` push read (eight listed runs, 2026-10-23 to 2026-10-24), before this tuple. It is not among the ruleset's required checks.
- Qualification `main` is `4298247e`; its drafts #223 and #226 name the same tuple and Verifier `c0b8ba1f` (#226 head `94f4942f`, #223 head `df4c6b76`; not frozen, Qualification owns every verdict).
- The Exchange (route C) is excluded and is not a member of the tuple.
