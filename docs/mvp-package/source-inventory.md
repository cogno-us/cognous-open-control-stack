# Source inventory (as read 2026-10-24)

Status: DRAFT, non-authorizing; all revisions PROVISIONAL / UNQUALIFIED. Label: VERIFIED (GitHub REST, `commits/main` and `pulls` metadata read 2026-10-24) unless marked.

"Last tuple" is the tuple on Qualification `main` (`process/mvp-chain/tuple-pin.proposed.json` at `4298247e`; Evidence Pack and ODES were null) and, identically for the Runtime, in `process/mvp-acceptance/candidate-identity.inputs.json` of Qualification draft PR #223. The hub lock column is `component-lock.json` on hub `main`.

| Component | `main` now | Last tuple | Hub lock on `main` | Open PRs that change it | Status |
|---|---|---|---|---|---|
| Control Plane | `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c` (F3 #83) | `7a4bcd40` (same) | `0a41faa9` | none | merged, UNQUALIFIED; hub lock bump in hub draft #223 |
| Runtime | `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f` (F3 #144, terminal revocation) | `ec728da6dc301a664b331ac8986afd6e850a1273` (pre-F3) | `ec728da6` | #126 (open, not draft, head `5f525ddd`, base `c60dded7`, older than `main`): `IntentRefundDestination.observe_bound` ownership validation, 2 files; not in the tuple | merged, UNQUALIFIED; Qualification draft #226 and hub draft #223 move the pin |
| Replay | `ab421ad0fdc6a24999273adf82455968953598ae` (F3 #78) | `ab421ad0` (same) | `028f63d1` | draft #79, head `c58e4ae13f1fe6fcc84f3c1ac14862d07b10270e`: re-ties the Programme 2 executor pairing to Runtime `c5e97e87`; fixtures, `importers.py`, docs, new revoked-approval fixture; titled provisional, UNQUALIFIED | PROVISIONAL |
| Evidence Pack | `79ae34d9dc0ca37cabd67b10793a46a972b986fd` (#63) | null on Qualification `main`; `79ae34d9` in draft #226 and in #223's identity file | `a3ebbb90` | none open at read time; re-tie in progress by another worker (REPORTED) | merged, UNQUALIFIED; its Programme 2 importer tuple still names Runtime `ec728da6` (REPORTED by #226) |
| ODES | `eae95dd3d8aab97b0fa64aa31f7ad830ec75530c` (#139) | null on Qualification `main`; `eae95dd3` in #226 and #223 | `e86a25a1` | none open at read time; re-tie in progress by another worker (REPORTED) | merged, UNQUALIFIED; pin-checked only, never imported by the chain |
| Verifier | `39d46b494558e271439966bec98b26dc4d040cc4` (#42, "docs only", per its commit title) | `c0b8ba1f55b75db787a320f3de0f79342c6f6826` | `c0b8ba1f` | none | tuple revision is the pinned Verifier; `main` is one docs-only commit ahead (title read, diff not read) |
| Action Manifest | `fa170815ef96a54c233d0dd9da821b60debabf8b` | `fa170815` (same) | `fa170815` | none | unchanged |
| Hub ingress | `5b76c58a8bacb9efe6ed6c08e51ab7db7d03bc12` (#219 merged) | `43c526eb1c8df9f07942ac36a6b2d11e14775bd1` (#217, predates the env capture script) | n/a (hub itself) | drafts #221 (claim text, Verifier), #222 (rulings record), #223 (provisional lock bump: Control Plane `7a4bcd40`, Runtime `c5e97e87`; also collateral and doc references; left untouched), #213 (2.3 dispositions, not draft) | merged, UNQUALIFIED; the capture script sha256 at `5b76c58a` is `5ae7beca...f1a51` (VERIFIED, computed) |
| Qualification | `4298247e860126d04d0bc44e1f2aef0fde1c4c97` | n/a | n/a | drafts #223 (head `5690f7b8c83335d62ec24e992227f96797ab0591`, acceptance job and gate, base `main`), #224 (`771f6b6d1a091c315dc08ce976e6535901b36dfb`, ambiguity test, base is the #223 branch), #225 (`c106b8693509290283177176e19c4d9f91ca16ad`, expectations v6, base is the #223 branch), #222 (`8d406eeabbab...`, NC4-03 v4 predicate, "do not merge"), #226 (`715b6b08951723339c6d5f8fd8e7a28867bc1c2e`, Runtime/Pack/ODES pin, base `main`); #198 is an unrelated dependency bump | proposals only, not frozen; Qualification owns every verdict |

Notes
- The Exchange (route C) is excluded and is not a member of the tuple.
- `#223` (acceptance job) names the Runtime `ec728da6` in its identity file; the post-F3 Runtime is a `runtime_revision` dispatch input (or one value in that file). Draft #226 moves only `process/mvp-chain/tuple-pin.proposed.json` (plus three `mvp-d2-route-b` files), which is hashed by the #223 candidate commitment, so landing both requires a recomputed commitment.
- The candidate tuple is not frozen by this record.
