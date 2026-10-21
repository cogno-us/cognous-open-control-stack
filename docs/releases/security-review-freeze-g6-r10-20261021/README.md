# G6 hub review freeze — 2026-10-21

Publication HOLD. Production HOLD / NOT ESTABLISHED. Rights/security acceptance pending.

Frozen source: `97ed5364dd962b61fac520f93c462c623ce87ddb` (tree `7619d2a290ed3b1a89e9993ffcf7c8e6107a175c`), the merged `main` head after hub PR #175. This packet supersedes the G5 packet (source `64d89d6`) for fresh review; the G5 packet's bytes under `docs/releases/security-review-freeze-g5-r10-20261021/` remain unchanged. No release or production authorization is granted.

| Binding | Value |
|---|---|
| Review ZIP | `cognous-source-review-97ed536.zip` |
| ZIP SHA-256 | `69a636f0f80785648f811bfe020409f7cf5e918de9b9a0eff2a0642dfd31ff21` |
| ZIP bytes / members | 1316335 / 181 |
| Manifest SHA-256 | `926ef8faaefd003a46321ddffdd7253ee2b1fe922b5460dca6dcd381c9b4e6f5` |
| Hub component lock SHA-256 (`component-lock.json`) | `0de22fb41eb9b5e2df47e655e72f6a07583812d19b5ba321dbeece831483386f` |
| Qualified candidate profile SHA-256 (`process/security-runtime-f5b-20261016-r11.json` in the qualification repository) | `49ca5745d786d97abba316864a7577dc8eb21600198a138d290982d35a2f1cc6` |
| Candidate | `g6-r10`, manifest digest `84a8a647beb7fddef3c91f71044dbf9b4e26e2272d3a11f0bd8b818904418c68` |
| Inventory | 696 tracked paths partitioned; 181 included, 515 excluded |
| Original notices | All 30 included, byte-identical to the R10, G5 and F5b freezes |

## What the packet binds, and what it does not

The hub component lock and the candidate that the controller run g6-r10 (run 39563114678, results retained in `cogno-us/cognous-stack-qualification` at merge commit `b6b67cc9`) qualified name the same revisions for the seven r11-profile components, the registry (`d25afe60`), the attestation component (`981036c3`) and the constitutional authority component (`d4462697`, the authority-lineage validator fixes of governance #60). The run ended with 40 of 40 workflow jobs succeeded and 33 jobs passed, 3 failed and 2 not run; the failing tests are declared by id in the qualification pre-registration (ODES, four tests; SCN-C04, three copy cases).

The earlier runs g2-r10 to g5-r10 probed older revisions of one or more of those components and are not claimed for the current lock. Components of the lock outside the profile and the three refrozen ones are not claimed by this packet.

`reference-release` is a declared known limit at the programme-2 profile; see `docs/release-status.md`. This packet is bounded synthetic scope, not independent certification and not production readiness.

## What changed since the G5 packet

0 hub pages were added to the review archive; 4 included files changed bytes (`component-lock.json`, `docs/release-status.md`, `docs/stack-map.md`, `tools/collateral_evidence_snapshot.py`); 6 paths became newly tracked and are excluded (the G5 packet files, as prior freeze retention). `verification.json` lists every path.

Reconstruct the exact ZIP with the frozen-source checkout and the sidecar script:

```sh
python /path/to/sidecars/reproduce.py --repository /path/to/hub-at-97ed536 --output /new/path/cognous-source-review-97ed536.zip
```

The script refuses overwrite, checks source, inventory and member hashes and the final ZIP digest. Both builds must have identical bytes. The sidecars postdate their frozen source and are excluded from their own archive.

## Retention checkpoint

The owner asked on 2026-10-21 for the full refreeze chain through this packet. The ZIP was built from the committed source via the same inclusion rules as the R10 and G5 packets and checked against the manifest. After this packet merges, main moves; a post-merge record (the ZIP rebuilt from `97ed536` and its digest compared) is added in a small follow-up change, as for the G5 packet. No new scans, paid trials, release or production activation were performed.
