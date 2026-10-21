# G5 hub review freeze — 2026-10-21

Publication HOLD. Production HOLD / NOT ESTABLISHED. Rights/security acceptance pending.

Frozen source: `64d89d6f130673b641eb50e322241b7316e884cd` (tree `244abc3be6321835d8063a18a360d63d0e4ac2b3`), the merged `main` head after hub PR #172. This packet supersedes the R10 packet (source `ac1a596`) for fresh review; the R10 packet's bytes under `docs/releases/security-review-freeze-r10-20261020/` remain unchanged. No release or production authorization is granted.

| Binding | Value |
|---|---|
| Review ZIP | `cognous-source-review-64d89d6.zip` |
| ZIP SHA-256 | `788102a687cbf85d0222b7e659cc734780a23bc526ec23988fa0f70ed3081376` |
| ZIP bytes / members | 1316250 / 181 |
| Manifest SHA-256 | `156d081aa0b348093729b9673dcedc05878f814bf7c8becda036be924966d211` |
| Hub component lock SHA-256 (`component-lock.json`) | `e86b1a42067345cc44857bd99368b3bec8102a2e1d8c616c0f6e53215cbdb07b` |
| Qualified candidate profile SHA-256 (`process/security-runtime-f5b-20261016-r10.json` in the qualification repository) | `33a35d1bbafcdde6d8bc3f9edbd97aa5704d627d2f8cad49cd8fcc6463e7304e` |
| Candidate | `g5-r10`, manifest digest `46cdf96f25c542b951bba4b1f76a921bef7e689ea8504b387d72868653af170d` |
| Inventory | 690 tracked paths partitioned; 181 included, 509 excluded |
| Original notices | All 30 included, byte-identical to the R10 and F5b freezes |

## What the packet binds, and what it does not

The hub component lock and the candidate that the controller run g5-r10 (run 39531760987, results retained in `cogno-us/cognous-stack-qualification` at merge commit `0e4a29ac`) qualified name the same revisions for the seven r10-profile components, the registry (`d25afe60`) and the attestation component (`981036c3`). The run ended with 40 of 40 workflow jobs succeeded and 33 jobs passed, 3 failed and 2 not run; the failing tests are declared by id in the qualification pre-registration (ODES, four tests; SCN-C04, three copy cases). The 14 SCN-C03 cases that were inconclusive in g4-r10b ran and passed.

The earlier runs g2-r10 and g3-r10 probed older registry and attestation revisions and are not claimed for the current lock. Components of the lock outside the profile and the two refrozen ones are not claimed by this packet.

`reference-release` is a declared known limit at the programme-2 profile; see `docs/release-status.md`. This packet is bounded synthetic scope, not independent certification and not production readiness.

## What changed since the R10 packet

0 hub pages were added to the review archive; 4 included files changed bytes (`component-lock.json`, `docs/release-status.md`, `docs/stack-map.md`, `tools/collateral_evidence_snapshot.py`); 6 paths became newly tracked and are excluded (the R10 packet files, as prior freeze retention). `verification.json` lists every path.

Reconstruct the exact ZIP with the frozen-source checkout and the sidecar script:

```sh
python /path/to/sidecars/reproduce.py --repository /path/to/hub-at-64d89d6 --output /new/path/cognous-source-review-64d89d6.zip
```

The script refuses overwrite, checks source, inventory and member hashes and the final ZIP digest. Both builds must have identical bytes. The sidecars postdate their frozen source and are excluded from their own archive.

## Retention checkpoint

Owner explicitly asked for this review freeze on 2026-10-21. The ZIP was built from the committed source via the same inclusion rules as the R10 packet and checked against the manifest. After this packet merges, main moves; a post-merge record (the ZIP rebuilt from `64d89d6` and its digest compared) is added in a small follow-up change, as for the R10 packet. No new scans, paid trials, release or production activation were performed.
