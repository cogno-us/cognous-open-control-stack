# F3R qualification receipt — F5b-repaired candidate, 16 October 2026

[Single control plane](https://github.com/cogno-us/cognous-open-control-stack/issues/68), F3/F4. Nonselected and nonauthorizing.

The seven-component F5b-repaired merged-source candidate was requalified at the central test hub under the strict Exchange compatibility profile `security-runtime-f5b-20261016`. The receipt below records that bounded synthetic result; it does not grant release or production authorization and does not transfer qualification to any other profile.

## Candidate pins

| Component | Repository | Revision |
|---|---|---|
| Control Plane | `cogno-us/cognous-control-plane` | `a34c3dc26f84a767a55f9d5c89dc0b53e63fefa5` |
| Execution Runtime | `cogno-us/cognous-execution-runtime` | `e20f92e104aba2ba6ad06120d8549c6170eaf63f` |
| Replay Bundle | `cogno-us/cognous-replay-bundle` | `79ba16d48b9be1e059b3045989c7df960c3df1c2` |
| Governance Evidence Pack | `cogno-us/cognous-governance-evidence-pack` | `893aca8dfb27ba5c5f3e833f2d29210ca7fc92e3` |
| ODES | `cogno-us/open-decision-evidence-standard` | `eb83220c82f942e429a5e3ef5f677fdd5057ef84` |
| Governed Exchange | `cogno-us/cognous-governed-exchange` | `8be6c6b80da8c5038d66419f84c10cc529f78137` |
| Action Manifest | `cogno-us/cognous-action-manifest` | `2c36bcd0b620dbfe7ad924bc7196a3f0c04c5c5e` |

The runtime pin is the quarantined F5b line; the upstream Moltbot application tree it originally carried has been moved under the git tag `upstream-moltbot-quarantine-20261016` on `cogno-us/cognous-execution-runtime`, preserving the prior pin `fd6b76fa0e85feb5b67324114bf790d3a12fdaf1` as historical evidence only. The quarantined tree is not part of this candidate.

## Hosted qualification evidence

- Repository: [`cogno-us/cognous-stack-qualification`](https://github.com/cogno-us/cognous-stack-qualification)
- Qualification PR: [#27](https://github.com/cogno-us/cognous-stack-qualification/pull/27) — `F3R: requalify the F5b-repaired seven-component candidate`
- Tested qualification source: `7022881e0958543a8b7685031c63132891b5f47c` (merge commit `7b29c2a3222492d29e58480284d40acc05c8c149`)
- Workflow: `.github/workflows/security-runtime-qualification.yml`, test suite `suites/security-runtime`, runner `tools/run_security_runtime.py`
- Hosted run: [38925303886](https://github.com/cogno-us/cognous-stack-qualification/actions/runs/38925303886), job `117055196162`
- Compatibility profile: `security-runtime-f5b-20261016` (new strict Exchange profile)
- Raw outcome per repetition: 36 raw JUnit cases; two repetitions; 0 failures / 0 errors / 0 skips; 668 original hashed members verified in-job per repetition
- `source_revisions_equal_profile_pins = true`; `source_hashes_equal_tested_head_bytes = true`; qualification worktree clean; no SQLite `-wal`/`-shm`/`-journal` sidecars present
- Retained record at the qualification repo: `results/security-runtime-f5b-20261016/verification.json`

## Native artifact

| Binding | Value |
|---|---|
| Artifact ID | `12056860537` |
| Artifact name | `f5b-requalification-7022881e0958543a8b7685031c63132891b5f47c` |
| Bytes (reported) | `4,890,962` |
| ZIP SHA-256 (reported) | `a089f9b33edff6521ceb78885b866f9a87280dc4d5584b3be471b15d309f672d` |
| Expires at | `2027-01-14T15:36:24Z` |
| Local ZIP download | Not performed in-job; REST zip redirect to `productionresultssa*.blob.core.windows.net` is refused by session egress proxy. Member hashes were revalidated inside the workflow run through `tools/summarize_security_runtime.py` notice annotations on check run `117055196162`, read via REST; decoded `junit.xml`/`stdout.log` SHA-256 equal the in-job hashes. |

Full native archive retention (download, hash, durable storage of every original file) runs in parallel as an F4 owner-authorized step at `cogno-us/cognous-stack-qualification` before the artifact expiry above. This hub receipt does not substitute for that retention.

## Scope and limits

- The 36-cases-twice outcome does not qualify all 13 selected components and does not transfer to the historical full-reference or any other profile.
- The historical C0 check-to-commit race remains, as do optional same-host cooperative controls; no C2/C3 or real settlement is established.
- Public ODES issuer/status/use authority remains limited; independent-review and operational-deployment limitations remain.
- `component-lock.json` and all existing selected/public W7/full-reference profiles are unchanged by this receipt.
- No paid model trials, external messages, publication, or production authorization were performed. Reference release and production remain unauthorized.

The next gate is the fresh source-review freeze at the post-reconciliation hub source and the final security review; that packet is retained separately in `docs/releases/security-review-freeze-f5b-20261016/`.
