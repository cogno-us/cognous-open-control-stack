# R10 hub review freeze — 2026-10-20

Publication HOLD. Production HOLD / NOT ESTABLISHED. Rights/security acceptance pending.

Frozen source: `ac1a596032714baa9ddb32c351b3fa7ddf8696c8` (tree `70f22fea56b6cea46734e2df8487c87a9b32fc13`), the merged `main` head after hub PR #169. This packet supersedes the F5b packet (source `f7fe1bc`) for fresh review; the F5b packet's bytes under `docs/releases/security-review-freeze-f5b-20261016/` remain unchanged. No release or production authorization is granted.

| Binding | Value |
|---|---|
| Review ZIP | `cognous-source-review-ac1a596.zip` |
| ZIP SHA-256 | `7feced749b1b8fc44075398ca2139d4c183b480e544a820be93b996e9708997f` |
| ZIP bytes / members | 1315932 / 181 |
| Manifest SHA-256 | `0108be0fee9f833bb423337b41a4d354ced37fe482f9ec42094c2f6d91e4572c` |
| Hub component lock SHA-256 (`component-lock.json`) | `ea657b36b930f591af4cf310b0943e8de18b4f6ca15f9b67ed2dc63a280379a0` |
| Qualified candidate profile SHA-256 (`process/security-runtime-f5b-20261016-r10.json` in the qualification repository) | `33a35d1bbafcdde6d8bc3f9edbd97aa5704d627d2f8cad49cd8fcc6463e7304e` |
| Inventory | 684 tracked paths partitioned; 181 included, 503 excluded |
| Original notices | All 30 included, byte-identical to the F5b freeze |

## What the packet binds, and what it does not

The seven components of the r10 profile have the same revisions in the hub lock and in the candidate that the controller runs g2-r10 (run 39349033320) and g3-r10 (run 39481839420) qualified. Both runs ended with 33 jobs passed, 3 failed and 2 not run; the failing tests are the same in both runs and are declared by id in the qualification pre-registration. The results are retained in `cogno-us/cognous-stack-qualification` (merge commits `5027aff9` and `2db591b9`).

**Known difference.** Two components differ between the hub lock and the revisions the runs probed: the registry (`the_index`: lock `704f55ea`, probed `d17b8ac2`, lock 5 commits ahead) and attestation (`bitrep`: lock `981036c3`, probed `5b5077da`, lock 27 commits ahead). No qualification result is claimed for those two at the lock revisions.

`reference-release` is a declared known limit at the programme-2 profile; see `docs/release-status.md`. This packet is bounded synthetic scope, not independent certification and not production readiness.

## What changed since the F5b packet

6 hub pages were added to the review archive (`docs/README.md`, `docs/guarantees-and-limits.md`, `docs/naming.md`, `docs/platform-support.md`, `docs/profiles-and-tools.md`, `docs/stack-map.md`); 21 included files changed bytes; 4 paths became newly tracked and are excluded (prior-freeze retention files, and three retention or acceptance records of earlier freezes, excluded under the same rule as the earlier sidecars). `verification.json` lists every path.

Reconstruct the exact ZIP with the frozen-source checkout and the sidecar script:

```sh
python /path/to/sidecars/reproduce.py --repository /path/to/hub-at-ac1a596 --output /new/path/cognous-source-review-ac1a596.zip
```

The script refuses overwrite, checks source, inventory and member hashes and the final ZIP digest. Both builds must have identical bytes. The sidecars postdate their frozen source and are excluded from their own archive.

## Retention checkpoint

Owner explicitly authorized this review freeze on 2026-10-20. The ZIP was built from the committed source via `tools/verify_publication_inventory.py --build` and checked against the manifest; the process was first validated by rebuilding the F5b ZIP byte-identically. The packet merged as hub PR #170 at `29bc8d11` (tree `d68fde7a`), which added only the six packet files. The post-merge check ran `reproduce.py` against the merged head with the frozen source `ac1a596` available: the rebuilt ZIP is byte-identical to the committed ZIP (`7feced74...`) and `SHA256SUMS` verifies; `verification.json` records it. No new scans, paid trials, release or production activation were performed.
