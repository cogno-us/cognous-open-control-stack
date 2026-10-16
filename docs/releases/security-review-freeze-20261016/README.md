# Repaired source-review freeze — 2026-10-16

Publication HOLD. Production HOLD / NOT ESTABLISHED. Rights/security acceptance pending.

Hub #148 is merged. Frozen source: `c996a41ee7a4e63617dade5ce61cbed5953a6610`. This packet supersedes the historical #144 packet for fresh review; historical bytes remain unchanged.

| Binding | Value |
|---|---|
| Review ZIP | `cognous-source-review-c996a41.zip` |
| ZIP SHA-256 | `f7d755d7a93df88660535d9b339479737a7c04177a70ffd2141e6dceadbb8e57` |
| ZIP bytes / members | 1206406 / 172 |
| Manifest SHA-256 | `86ff0e346bc983b73c17b96e850b88ee4316955204a1b8ff8d9ea903ce280b9f` |
| Inventory | 659 tracked paths partitioned; 172 included, 487 excluded |
| Original notices | All 30 included, exact historical notice bytes |
| Native qualification archive | `49fb98a3bf5d53b397ea44ff0afedc2d0c3db9dd5e45b57a5e51263d1a78b179`, 4,888,050 bytes |

The manifest retains the bounded hub-only allowlist and adds only the two original hub files recording the nonselected repaired candidate. No external component source, selected PRP/TFA source/PDF, installed dependency/toolchain, workflow or generated evidence archive is included in the review ZIP. The separately retained synthetic native qualification archive belongs to the central test hub, outside this distribution.

The unchanged historical component lock and public selection remain historical selections. The seven repaired candidate pins and their profile hash are separately frozen in verification.json; qualification of 36 raw cases twice does not qualify all 13 selected components. Failure IDs remain source-asserted, public ODES authority remains limited, C0 and deployment/custody limits remain. No promotion or release authorization is granted.

Reconstruct the exact ZIP with the frozen-source checkout and sidecar script:

```sh
python /path/to/sidecars/reproduce.py --repository /path/to/hub-at-c996a41e --output /new/path/cognous-source-review-c996a41.zip
```

The script refuses overwrite, checks source/inventory/member hashes and final ZIP digest. Both builds must have identical bytes. Sidecars postdate their frozen source and are excluded from their own archive. See verification.json for source tree, every profile hash, selected pins, repaired candidate pins and path delta.

Fresh Security Cloud source reviews are tracked by run ID and actual resolved commit, separately from this package digest. Source scans do not prove coverage of excluded binary artifacts, history, semantic IP/PII or independent security acceptance. These remain explicit F5/F6/F7 tasks at the [single control plane](https://github.com/cogno-us/cognous-open-control-stack/issues/68).

## Retention checkpoint

Owner explicitly approved this review ZIP and sidecars for this repository and the original native qualification archive for the central test hub. The review ZIP was recovered and rebuilt byte-identically in this pass; the original native archive also matches its recorded SHA-256 and passes ZIP integrity checks. This commit retains the hub review packet. The separate native archive transfer remains pending; do not infer test-hub retention from this commit.

All sixteen recorded Security Cloud scan runs completed at their recorded source revisions. Findings triage and final exposure/rights/accountable acceptance remain pending. No new scans, paid trials, release or production activation were performed by this retention step.
