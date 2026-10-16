# F5b-repaired source-review freeze — 2026-10-16

Publication HOLD. Production HOLD / NOT ESTABLISHED. Rights/security acceptance pending.

Base frozen source: `f7fe1bc03cf67df2ab5afe81ba513580a29fde25` (tree `2fa2dc30f2225c8ac64c92317a067883ccfda985`), the merged `main` head after PR #152. The post-merge re-check regenerated this packet at the merged head; see the pre-merge-base record below. This packet supersedes the historical `c996a41` packet for fresh review; historical bytes under `docs/releases/security-review-freeze-20261016/` remain unchanged. No release or production authorization is granted.

| Binding | Value |
|---|---|
| Review ZIP | `cognous-source-review-f7fe1bc.zip` |
| ZIP SHA-256 | `37d575d776dc32cd79ecf815edb328038a49f9c314d3aeb7b82bed406d3ee337` |
| ZIP bytes / members | 1218856 / 175 |
| Manifest SHA-256 | `9c2cc53cfd6e55b50704dd2776bc4a7add224f27e8eb1bfa388df28d7361ad4b` |
| Candidate profile SHA-256 (`profiles/security-runtime-f5b-candidate-20261016.json`) | `f159158cd9f5504a6e1c0683cbd136532c1c6938300dd17aa45f700ad9278274` |
| Historical component-lock SHA-256 (`component-lock.json`) | `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc` |
| Inventory | 675 tracked paths partitioned; 175 included, 500 excluded |
| Pre-merge base | source `0c3ee57ea37cfbe3ee1bab8ba8be4a4d73c42396`, ZIP SHA-256 `a554ec78f9a4f143172b48bf8d61b04eaedcb6e498634d50c4c4a4908cc378ef`, 1218744 bytes, 175 members; both base and merged-head ZIPs are legitimate for their respective trees |
| Original notices | All 30 included, exact historical notice bytes |
| Native qualification archive | `a089f9b33edff6521ceb78885b866f9a87280dc4d5584b3be471b15d309f672d`, 4,890,962 bytes, artifact 12056860537, expires 2027-01-14T15:36:24Z |

The manifest retains the bounded hub-only allowlist and adds only the two hub source files recording the F5b-requalified candidate (its profile and the F3R qualification receipt) plus the F5b regression test added by hub PR #150. The prior freeze's own retained sidecars and ZIP are listed in the inventory but excluded from the new review ZIP: sidecars postdate their own frozen source. No external component source, selected PRP/TFA source/PDF, installed dependency/toolchain, workflow or generated evidence archive is included in the review ZIP. The separately retained synthetic native qualification archive belongs to the central test hub, outside this distribution.

The unchanged historical component lock, public W7 selection and every full-reference profile remain historical selections. The seven F5b-repaired candidate pins and their profile hash are separately frozen in `verification.json`; qualification of 36 raw cases twice does not qualify all 13 selected components. The runtime pin is the quarantined F5b line; its upstream Moltbot application tree has been moved under tag `upstream-moltbot-quarantine-20261016` on `cogno-us/cognous-execution-runtime`, preserving prior pin `fd6b76fa` as history only. Failure IDs remain source-asserted, public ODES authority remains limited, C0 and deployment/custody limits remain. No promotion or release authorization is granted.

Reconstruct the exact ZIP with the frozen-source checkout and sidecar script:

```sh
python /path/to/sidecars/reproduce.py --repository /path/to/hub-at-f7fe1bc --output /new/path/cognous-source-review-f7fe1bc.zip
```

The script refuses overwrite, checks source/inventory/member hashes and final ZIP digest. Both builds must have identical bytes. Sidecars postdate their frozen source and are excluded from their own archive. See `verification.json` for source tree, every profile hash, selected pins, F5b-repaired candidate pins, the delta from the superseded `c996a41` freeze and the post-merge re-check record (including the pre-merge-base ZIP SHA-256).

Fresh Security Cloud source reviews are tracked by run ID and actual resolved commit, separately from this package digest. Source scans do not prove coverage of excluded binary artifacts, history, semantic IP/PII or independent security acceptance. These remain explicit F5/F6/F7 tasks at the [single control plane](https://github.com/cogno-us/cognous-open-control-stack/issues/68).

## Retention checkpoint

Owner explicitly authorized the F4 hub reconciliation and this new review ZIP and sidecars for this repository on 2026-10-16. The review ZIP was built from the committed source via `tools/verify_publication_inventory.py --build` and verified byte-identically on a second independent build; its 175 member hashes and ZIP integrity match the manifest. The native qualification archive is retained separately at `cogno-us/cognous-stack-qualification` under `results/security-runtime-f5b-20261016/`; its full retention (download, hash, durable storage) runs in parallel as an F4 step there and is not substituted by this hub receipt.

All recorded Security Cloud scan runs for the F5b-repaired candidate completed at their recorded source revisions. Findings triage and final exposure/rights/accountable acceptance remain pending. No new scans, paid trials, release or production activation were performed by this retention step. This candidate requires a final review-and-refreeze cycle; no release or production authorization.

## Post-merge re-check

PR #152 merged at `f7fe1bc03cf67df2ab5afe81ba513580a29fde25`. The merge introduced bytes-level changes within the review scope at the merged head: `docs/release-status.md` was updated to add markdown links to the superseded and new freeze READMEs (included scope); six retention sidecars under `docs/releases/security-review-freeze-f5b-20261016/` and the pre-merge review ZIP became newly tracked and are excluded as prior-freeze retention under the bounded hub review allowlist; `collateral/evidence-snapshot.json` was updated to reflect the merged packet state (excluded scope). The ZIP was therefore regenerated at the merged head. Both the pre-merge-base ZIP (`a554ec78…`, 1,218,744 bytes, 175 members at `0c3ee57`) and the merged-head ZIP (`37d575d7…`, 1,218,856 bytes, 175 members at `f7fe1bc`) are legitimate for their respective trees. No release or production authorization is granted; `component-lock.json`, the public W7 selection and every full-reference profile remain unchanged.
