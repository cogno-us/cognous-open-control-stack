# O6-P0A collateral evidence snapshot checkpoint

Issue: #64. Branch: `worker/o6-p0-collateral-evidence-snapshot`. Accepted source baseline: `f7d03c719b9be3b9c3fe0fe300df642b0f408d98`.

No hub `AGENTS.md` or `development/README.md` exists at this baseline; prior hub checkpoints record the same. `CONTRIBUTING.md` and `GOVERNANCE.md` therefore govern this documentation-only change.

## Scope

This work changes release/collateral provenance, schema, tests and a path-scoped publishing workflow only. It does **not** modify runtime implementation, `component-lock.json`, authority issuance, credentials, payment processing or release selection.

The current component-lock SHA-256 is `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`. Selected Control Plane is `d3dadee70bd319812b207389ab1e0f6efe511916`; selected Execution Runtime is `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac`.

## Claim boundary

- C0 is the selected default: independent authority resolution plus pre-effect revalidation. A check-to-commit race remains.
- C1 is optional, same-host and SQLite-local for cooperating participants. It is not enabled by default.
- C2/C3 are unqualified.
- Effect-ID dedupe is not business-intent dedupe.
- The reference uses synthetic SQLite and does not demonstrate external settlement.

## Evidence populations

Default selected generation: run `37694032916`, tested source `7e43d55c6cc0123a191480a9e6870d6452affa83`, 35 acceptance scenarios, `full-candidate-gate` SHA-256 `5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7`.

Separate C1 profile evidence: run `37682165860`, 73 passed with zero failures/errors/skips, reviewed Control Plane `73e3c65acc47dc43593dcb0420d14032ed410b14` and executor `b1525a7982e52ebb530457f94d5517de032ca4c4`. This is not added to the default release count.

V1 extension contract `v1-reference-extension-evidence/4`: 91 executed profile cases plus 26 synthetic aggregate negative/unit checks. This remains a separate evidence population.

## Drift gate

`collateral/evidence-snapshot.json` is the detached provenance manifest. It records final Markdown SHA-256 values rather than embedding a self-hash. The stdlib validator and CI reject accepted-pin drift, component-lock digest drift, wrong evidence generation/counts, document tampering, historical relabeling and C2/C3 claim inflation.

Historical `docs/release-status-before-merged-adoption.md` remains untouched and explicitly historical.
