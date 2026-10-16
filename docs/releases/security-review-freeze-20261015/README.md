# Frozen source-review handoff — 2026-10-15

**Historical pre-remediation evidence.** This packet preserves source `7f335099` and its original archive bytes. It excludes subsequent security repairs, including hub #145. Rebuild and review a new package after repair integration; this packet is not the final repaired publication candidate.

**FOR OWNER SECURITY/IP REVIEW. Publication HOLD; operational HOLD / NOT ESTABLISHED.**
No security review, legal clearance, release, tag, announcement or production
activation is performed by this packet. Both release/production authorizations
remain false. This is a bounded hub-only source review kit, with external project
references; it is not a complete installed stack or offline runnable environment.

## Exact frozen bindings

| Item | Frozen identity |
| --- | --- |
| Hub source | `7f335099ca52a68533b6e78c2e35166a9109e35c` |
| Selected runtime | `merged-producers-v1` from the unchanged component lock |
| Lock SHA-256 | `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc` |
| Supporting merged-chain profile | `profiles/merged-consumer-chain.json`, SHA-256 `d6942c417de29dc9dee42b1ee47fb3189b3f816b380c0425ec6461a251db7509` |
| Manifest SHA-256 | `3964250ed7f0dfef74655930a3ffeba3a8813bf8de34549bb04b42f186e41aa3` |
| Actual review ZIP | `cognous-source-review-7f335099.zip`, 1,192,900 bytes |
| ZIP SHA-256 | `2148dbac766f4b8ae24eb6629e73e67f3a983cf665e5511b193487b021f36e06` |
| ZIP members | 170 regular files, 1,166,826 file bytes; every path and digest verified |
| Source inventory | All 646 tracked paths partitioned: 170 included, 476 excluded |

[Manifest](manifest.json) lists every included and excluded path/hash.
[Verification](verification.json) records the source tree, all 13 selected component
pins, hashes of all six profile files, candidate exclusions, test counts/hashes,
package delta and notice evidence. Candidates remain separately named and
nonselected; this freeze does not promote the repaired remediation profile or W7
candidate. [SHA256SUMS](SHA256SUMS) binds the handoff files and review ZIP.

The previous 206-file kit was tied to `e335e551...`. This refresh retains its 161
paths still in current hub source, removes the 45 absent/migrated paths and adds
nine explicitly listed original hub documentation/helper/regression paths. Twenty-five
retained files have changed bytes. These changes require the upcoming security/IP
review; no historical scan is transferred to them. Migrated canonical qualification
code and active PRP trials are external to this package and are not copied back.

## Exclusions and original notices

The allowlist preserves the owner's exclusions: no external component source
checkouts, selected PRP/TFA source or PDFs, installed third-party dependencies or
toolchains, historical/generated archives, databases or collateral. Workflows and
closeout audit metadata are outside the ZIP. Requirements/lock text and component
references do not bundle installed packages. All nonallowlisted source paths are
explicitly excluded in the manifest; a normal Git source/tag archive would be a
different, unaccepted distribution.

All **30 required notice files** are in the actual ZIP: hub LICENSE/NOTICE plus
28 original selected-component notice/license copies. All 28 retained component
files match the committed notice ledger and freshly retrieved upstream bytes and
Git blob IDs at their exact selected revisions. See [notice observations](notice-verification.json).
Nested paths containing `vendor` are original notice copies only, not vendored
source. Root hub terms do not relicense external projects; exact-byte notice
verification is not legal acceptance or proof of all substantive IP provenance.
Included original hub paths rely on their recorded license evidence, with
accountable rights acceptance still pending. Questionable content found during
the owner's security/IP review must be excluded or corrected before publication.

## Integration and actual verification

- Historical [PR #122](https://github.com/cogno-us/cognous-open-control-stack/pull/122)
  closed unmerged as superseded, retaining its failed source and evidence.
  Repaired nonselected compatibility remains separately recorded by #133 and
  canonical qualification #4. Residual publication/security requirements stay
  on [#68](https://github.com/cogno-us/cognous-open-control-stack/issues/68),
  [#86](https://github.com/cogno-us/cognous-open-control-stack/issues/86) and
  [#138](https://github.com/cogno-us/cognous-open-control-stack/issues/138).
- All 19 exact-head checks passed before #117 merged; all six observed checks at
  the frozen merge source also succeeded. Their source identities are distinct.
- Fresh local full hub suite at the frozen source: **636 testcase elements and
  126 separately reported subtests passed; zero failures/errors/skips**.
  JUnit's `tests=762` includes subtests and is not 762 independent testcase elements.
  Python 3.12.14, pytest 9.1.1, cryptography 50.0.0; the full locked dependency
  environment was not reinstalled for this rerun.
- Scoped preview audit: 13 pages / 143 references, zero failures; seven negative
  controls passed. Selected-documentation checker verified one selected-revision
  link with `network_checked=false`, `authorizing=false`. Whitespace check passed.
- Existing source/package verifier built and checked all manifest files; actual
  ZIP membership/digests were checked independently with `zipfile`. Reproduction
  produced the identical ZIP SHA-256 without network fetch or installed bundles.

These checks cover the named hub tests/inventory, not a fresh full selected-stack
integration run, security assessment or operational observer independence. C0
retains its unsafe check-to-commit race; optional C1 is same-host/cooperative.
No C2/C3, real settlement or deployed configuration is established. README's
Deployment configuration: TBD remains applicable. Export mapping limitations
and unreviewed source/security evidence remain for the next review.

## Reconstruct the exact review bytes

Obtain these sidecars from this packet's immutable Git revision. Use a separate
hub checkout at the frozen source; the sidecars themselves postdate that source
and are not included in the ZIP. Run:

```sh
python /path/to/this-packet/reproduce.py \
  --repository /path/to/hub-at-7f335099 \
  --output /path/to/new/cognous-source-review-7f335099.zip
```

The helper invokes the frozen existing inventory verifier, refuses existing output,
constructs the declared deterministic ZIP, rechecks every member and verifies the
archive digest. No release upload or publication is included. The locally built
review ZIP is supplied directly to the owner; no raw unreviewed ZIP is committed
as a public release asset. The generated packet files are metadata sidecars,
excluded from their own frozen source to avoid circular review claims.

## Next owner action

Run the fresh security/IP review on this exact source and ZIP, using the complete
manifest inventory and changed/added path lists. Reconcile #86/#138 and specific
findings; retain approved exclusions and original notices. No blanket risk
acceptance or independent certification is requested. After findings are corrected
and affected checks rerun, reconcile any changed digest and decide publication
only for the resulting exact package. PRP evaluation can continue separately;
its paid trials, credentials and unfinished material are untouched and excluded.
No new source/profile-selection decision is needed to use this existing scope.
