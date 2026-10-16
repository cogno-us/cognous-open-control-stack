# F5b-repaired source-review freeze — 2026-10-16

Publication HOLD. Production HOLD / NOT ESTABLISHED. Rights/security acceptance pending.

Base frozen source: `0c3ee57ea37cfbe3ee1bab8ba8be4a4d73c42396` (tree `c56adf2a09719d8762eb9cdeef11609f91d4ebf1`), the current branch head of the F4 hub reconciliation PR before merge. This packet supersedes the historical `c996a41` packet for fresh review; historical bytes under `docs/releases/security-review-freeze-20261016/` remain unchanged. A post-merge re-check at the merged hub `main` head is required before acceptance; this freeze is bound to the pre-merge base above.

| Binding | Value |
|---|---|
| Review ZIP | `cognous-source-review-0c3ee57.zip` |
| ZIP SHA-256 | `a554ec78f9a4f143172b48bf8d61b04eaedcb6e498634d50c4c4a4908cc378ef` |
| ZIP bytes / members | 1218744 / 175 |
| Manifest SHA-256 | `47d29cbb5dfe05e0316093dfda576bec7bd490691ba10ed518d111de8135917d` |
| Candidate profile SHA-256 (`profiles/security-runtime-f5b-candidate-20261016.json`) | `f159158cd9f5504a6e1c0683cbd136532c1c6938300dd17aa45f700ad9278274` |
| Historical component-lock SHA-256 (`component-lock.json`) | `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc` |
| Inventory | 669 tracked paths partitioned; 175 included, 494 excluded |
| Original notices | All 30 included, exact historical notice bytes |
| Native qualification archive | `a089f9b33edff6521ceb78885b866f9a87280dc4d5584b3be471b15d309f672d`, 4,890,962 bytes, artifact 12056860537, expires 2027-01-14T15:36:24Z |

The manifest retains the bounded hub-only allowlist and adds only the two hub source files recording the F5b-requalified candidate (its profile and the F3R qualification receipt) plus the F5b regression test added by hub PR #150. The prior freeze's own retained sidecars and ZIP are listed in the inventory but excluded from the new review ZIP: sidecars postdate their own frozen source. No external component source, selected PRP/TFA source/PDF, installed dependency/toolchain, workflow or generated evidence archive is included in the review ZIP. The separately retained synthetic native qualification archive belongs to the central test hub, outside this distribution.

The unchanged historical component lock, public W7 selection and every full-reference profile remain historical selections. The seven F5b-repaired candidate pins and their profile hash are separately frozen in `verification.json`; qualification of 36 raw cases twice does not qualify all 13 selected components. The runtime pin is the quarantined F5b line; its upstream Moltbot application tree has been moved under tag `upstream-moltbot-quarantine-20261016` on `cogno-us/cognous-execution-runtime`, preserving prior pin `fd6b76fa` as history only. Failure IDs remain source-asserted, public ODES authority remains limited, C0 and deployment/custody limits remain. No promotion or release authorization is granted.

Reconstruct the exact ZIP with the frozen-source checkout and sidecar script:

```sh
python /path/to/sidecars/reproduce.py --repository /path/to/hub-at-0c3ee57 --output /new/path/cognous-source-review-0c3ee57.zip
```

The script refuses overwrite, checks source/inventory/member hashes and final ZIP digest. Both builds must have identical bytes. Sidecars postdate their frozen source and are excluded from their own archive. See `verification.json` for source tree, every profile hash, selected pins, F5b-repaired candidate pins and the delta from the superseded `c996a41` freeze.

Fresh Security Cloud source reviews are tracked by run ID and actual resolved commit, separately from this package digest. Source scans do not prove coverage of excluded binary artifacts, history, semantic IP/PII or independent security acceptance. These remain explicit F5/F6/F7 tasks at the [single control plane](https://github.com/cogno-us/cognous-open-control-stack/issues/68).

## Retention checkpoint

Owner explicitly authorized the F4 hub reconciliation and this new review ZIP and sidecars for this repository on 2026-10-16. The review ZIP was built from the committed source via `tools/verify_publication_inventory.py --build` and verified byte-identically on a second independent build; its 175 member hashes and ZIP integrity match the manifest. The native qualification archive is retained separately at `cogno-us/cognous-stack-qualification` under `results/security-runtime-f5b-20261016/`; its full retention (download, hash, durable storage) runs in parallel as an F4 step there and is not substituted by this hub receipt.

All recorded Security Cloud scan runs for the F5b-repaired candidate completed at their recorded source revisions. Findings triage and final exposure/rights/accountable acceptance remain pending. No new scans, paid trials, release or production activation were performed by this retention step. This candidate requires a final review-and-refreeze cycle; no release or production authorization.
