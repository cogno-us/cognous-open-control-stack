# Changelog

## 2026-10-22 review scan 3 hardening (tools and tests only; non-authorizing, HOLD unchanged)

- Collateral evidence snapshot checker: loads through the bounded loader (duplicate members refused), applies the snapshot schema (declared members only), requires exact integer counts, and cross-checks lock-derived claims against `component-lock.json`.

## Reference candidate workstream

- Added exact component lock and accepted/deferred revision ledger.
- Added reproducible two-run acceptance harness and GitHub Actions evidence upload.
- Added governed transport, GAX/IMX, Control Plane, Moltbot Safe, Replay, Governance Evidence Pack, ODES, BitRep and Index checks.
- Added representative GAX-to-Replay-to-Evidence-Pack/ODES/IMX artifact generation.
- Added separate mocked OpenShell qualification and explicit unexecuted live gate.
- Added machine-readable acceptance and residual-risk registers.
- Replaced the four-component hub presentation with the current responsibility map, trust boundaries, compatibility matrix and adoption guidance.
- Recorded the Moltbot producer-revision gap and GAX test-helper dependency without altering adjacent repositories.
- Excluded unaccepted cogno-us/alvorada PR #2.
