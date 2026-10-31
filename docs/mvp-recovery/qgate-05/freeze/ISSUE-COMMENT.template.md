<!-- Post on cogno-us/cognous-open-control-stack Issue #215 AFTER the custody record is pushed to the hub branch qgate-05/custody-1 and BEFORE the run branch is pushed. Order: (1) custody branch pushed; (2) this comment; (3) the freeze tree is on Qualification main; (4) qgate-05/run-1 is pushed once (the push triggers the run; the workflow has no inputs). Replace every <...>. -->
**OCS-MVP-QGATE-05 candidate custody anchor (PROPOSED; not a certification, verdict, Tier 1, Q7, release or production authorization)**

- Qualification revision: `<40-hex>` (cogno-us/cognous-stack-qualification)
- Candidate: `<mvp-qualification-candidate-v5>`, commitment file `<path>`
- **candidate_commitment_sha256: `<64-hex>`** (`sha256sum <path>`), `<N>` committed files, listing sha256 `<64-hex>`
- Oracle `<v8>` sha256 `<64-hex>`; battery `<v2>` sha256 `<64-hex>`
- Tuple: CP `<sha>`, Runtime `<sha>`, Replay `<sha>`, Evidence Pack `<sha>`, ODES `<sha>`, Verifier `<sha>`, Action Manifest `<sha>`, Hub `<sha>`
- Custody file: hub branch `qgate-05/custody-1` at `<commit sha>`, `docs/mvp-recovery/qgate-05/custody/freeze-commitment.json` (sha256 `<64-hex>`); pushed once, never force-pushed. The workflow reads this branch (not the hub default branch) and records its resolved head sha.
- Freeze record: hub `<path>` sha256 `<64-hex>`; Owner approval: `<role / session / UTC time>`; AI-assisted technical approval, not certification.
- Recorded before the single run; the run branch had not been pushed at this time. Prerequisite for the push: the exact Qualification revision above is on Qualification `main` (anchor gate G-02c compares the frozen files with `main`).
- Standing holds unchanged: F3 CLOSED (Q2/Q3 UNRESOLVED); Q7 NOT ESTABLISHED; Final Tier 1 DEFERRED, NOT WAIVED; publication/release/production HOLD.
