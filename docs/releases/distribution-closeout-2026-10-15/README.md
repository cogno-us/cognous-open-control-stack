# S4 — distribution lane D technical closeout

**Technical inventory and evidence coverage only. Rights acceptance and publication remain pending.**
Operational trust remains **HOLD / NOT ESTABLISHED**. No release/tag, announcement or production action.

## Frozen source and proposed scope

Base/source: `592919dd95396f3f6164cf0ceec1fd15c065691b` (live main independently checked through Git and GitHub branch metadata on 2026-10-15).
No repository `AGENTS.md` was found. CONTRIBUTING.md and GOVERNANCE.md were read. Issues #70/#87 and their follow-up comments, open PRs (initially #117), lock, selection profiles and the named acceptance/remediation records were inspected. Moved repository names are taken from the live lock; historical reports retain their original revision scope.

[manifest.json](manifest.json) is the explicit allowlist, not a wildcard packaging rule.
Its SHA-256 is:

`18c5f78c0f22d75da87995f8a96cb02bef106434f2cebcbf26f359ec37a2465a`

The locally built **202-file hub-only documentation and qualification-source review kit** includes root public documents, LICENSE/NOTICE, unchanged lock and profiles, hub qualification source/tests/fixtures, selected hub documentation and all original selected notice copies. Each file has a repository-relative path, exact source commit, SHA-256, applicable license/notice evidence references and inclusion rationale. No new notice text was synthesized.

This is deliberately narrower than the October 13 hub/evidence candidate: **all generated examples, including the previously disclosed October 13 evidence archive, are excluded**. This preserves earlier disclosure approvals; it does not revoke them. The kit is a source review package, not a complete offline runnable reproduction environment. Some retained documentation/tests reference excluded examples or external components. Links verified below refer to the public source tree, not a claim that every reference resolves inside this smaller directory package.

The manifest separately records all **441 excluded tracked files**, each with base commit, hash and rationale. Thus all **643 tracked base files** are accounted for. Excluded groups include all examples, collateral, benchmarks, workflow/scanner configuration, private-evaluator documentation, workstream/verification history and `.gitignore`. New S4 checker/tests/workflow and these audit sidecars are review infrastructure; they are **not silently added** to the frozen base package. A future package that includes them requires a new manifest and delta review.

A normal full Git source archive from a future tag has different contents: custom allowlist exclusions do not remove tracked files. This PR itself adds public review metadata to the source tree. There was no tag, release asset, package upload or publishing action.

## Selected license and notice provenance

[selected-provenance.json](selected-provenance.json) re-enumerates all **13 complete selected Git trees** and compares **28 original notice/license files** against both selected Git object bytes/blob IDs and the existing retained copies. All match; the selected lock SHA-256 remains `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`.

- Action Manifest, Control Plane, Governed Exchange, Replay, Evidence Pack, ODES and Research Intelligence: selected Apache-2.0 license/notice evidence.
- Institutional Governance: selected CC BY 4.0 and attribution/external-rights carveout; a later Apache licensing head is not applied backward.
- BitRep and Index: selected MIT licenses, rather than later licensing policy.
- Execution Runtime: upstream MIT, Apache-2.0 Cognous layer and ten retained root/nested license/notice files. Nested Swabble, device mappings, open-prose, skill-creator and vendor/a2ui terms are enumerated. Swabble, device mappings and open-prose carry MIT text; the safety layer, skill-creator and vendor/a2ui carry Apache-2.0 text. The root NOTICE separates the Cognous layer from retained upstream and third-party content. This evidence is not a file-by-file clearance of the runtime's 4,578 tracked files.
- PRP selected `cb137f028e92448a56e785e3d4ea074b444fa225`: nine tracked files; no tracked license/notice instrument. Selected textual files inspected for license indicators, without inventing an applicable grant.
- TFA selected `442d07b4891870abb1756fcb11c24ccf187706f4`: seven tracked files, including `S43_Cryptographic_Protocol.pdf` and `TFA_Whitepaper.pdf`; no tracked license/notice instrument. The selected README expressly distinguishes historical CC0-style intent from authoritative licensing evidence. PDFs are inventoried by exact selected bytes/hash, not republished or treated as cleared. All external component source is excluded.

The older report's 12/11-entry PRP/TFA counts included tree entries; the current nine/seven counts are **tracked files**. These observations are consistent. Later PRP/TFA `licensing_head` values remain descriptive references, not substituted source or proof of a retroactive grant. No component pins or selection profiles change. The whole stack is not Apache-2.0.

All 28 retained notices are required package files alongside hub LICENSE/NOTICE. Their provenance stays in the unchanged original selected-notices.json and the reverified ledger. Copying them does not redistribute the corresponding runtime source or establish a new grant.

## Dependencies and historical artifacts

[dependencies.json](dependencies.json) distinguishes requirement/lock text from redistributed package bytes. The selected-source ledger inventories **65 dependency manifest/lock surfaces** and **300 direct declaration records** where parseable package.json, pyproject.toml and requirements files apply. Lock surfaces include JavaScript, Python and native manifests; their full resolved transitive package obligations are not accepted by this inventory. No complete transitive SBOM or platform-specific dependency clearance is claimed.

S4's checker/tests require only the Python standard library. No pip/npm dependency was installed for S4 testing. Other hub runners can separately fetch components and install qualification dependencies; those execution environments are outside the proposed package. The package includes requirements text, not wheels, node_modules, wallets, toolchains or external checkouts.

[excluded-artifacts.json](excluded-artifacts.json) inventories **342** example, collateral and benchmark file records. All three tracked `.tar.xz` archives were opened without extraction: **227**, **231** and **260** members respectively; every regular member's bytes were hashed. They contain regular files/directories, no nested archive/PDF/source-code member paths were found, and no member had a PDF header. The October 13 archive remains 189,636 bytes with SHA-256 `6f7baf4413b8c8293ff318457bae5ac68a2dba0226c8452903527ce805b8083a`. No standalone tracked hub PDF/DOCX/ZIP was found at this source; the two selected TFA PDFs are external, not hub files. This inspection is structural and byte-level, not semantic PII/IP acceptance. Tracked databases, generated JSON/log/XML and examples remain subject to S5 review if a full source archive or any expanded package is proposed.

## Public entry and notice-reference observations

[link-responses.json](link-responses.json) records **161 distinct targets** from nine named public entry surfaces, their rendered local-source references, all exact notice URLs, outbound/source-relative notice references and the issue chooser. Each records GET method, observation time, response status, final URL and redirects where observed. **All 161 final responses were HTTP 200**; twelve initial HTTP 504 gateway observations are preserved alongside the successful retries. These were inaccessible observations on the first attempt, not evidence of missing files. All **three tested rendered fragments** were found in HTML IDs. All **28 exact notice responses** hash-match the retained originals.

The anonymous chooser returned HTTP 302 to GitHub login and final HTTP 200. No issue template form was reached anonymously, no form was submitted and no private-report/mailbox delivery was tested. Successful source-tree URLs do not repair links to excluded files inside the smaller directory package. Other historical Markdown URLs and every possible rendered anchor remain outside this bounded crawl; no universal all-links acceptance is claimed. The two upstream device-mapping license responses are separately recorded in [upstream-notice-responses.json](upstream-notice-responses.json): both returned HTTP 200. Their original LICENSE is 1,073 bytes; the selected runtime retained copy adds exactly one terminal LF (1,074 bytes). The preceding bytes match. Original selected copies remain unchanged; exact upstream byte equality is not claimed.

## Checker, negative controls and reproduction

The checker rejects extra/missing package files, digest mismatches, missing required notice/evidence, excluded inclusions, duplicate/case-colliding or unsafe paths, symlinks/nonregular entries, incomplete source partitions, changed source revisions, and unresolved entries represented as accepted. It also refuses affirmative legal/release/production status. `evidence_verified` means the referenced licensing evidence is present and byte-bound; it does not mean accountable rights acceptance.

The manifest is the trusted review input: changing that input creates a new proposal and hash. This is an offline directory verifier, not a signature service, hostile concurrent-filesystem sandbox or legal decision engine. Build into a fresh directory under a trusted local workspace. It refuses an existing output directory rather than overlaying previous contents.

From the repository root (the relocated `check_release_integrity.py` is run by the [source-bound wrapper](../../../.github/workflows/release-integrity.yml), not as a hub-local file):

```sh
python -m unittest discover -s tests -p test_publication_inventory.py -v
python tools/verify_publication_inventory.py --manifest docs/releases/distribution-closeout-2026-10-15/manifest.json --package /tmp/s4-review-package --build
python tools/verify_publication_inventory.py --manifest docs/releases/distribution-closeout-2026-10-15/manifest.json --package /tmp/s4-review-package
```

Use a fresh output path. Recorded checker outcomes and negative-control commentary are maintained in the [central test hub](https://github.com/cogno-us/cognous-stack-qualification/blob/main/results/readme-commentary/index.md). Workflow configuration alone is not evidence of execution.

To reproduce provenance, clone each component-lock repository into `<components-root>/<component-key>` with the selected commit available, then run:

```sh
python docs/releases/distribution-closeout-2026-10-15/reproduce_inventory.py --components-root <components-root>
python docs/releases/distribution-closeout-2026-10-15/verify_links.py
python docs/releases/distribution-closeout-2026-10-15/verify_upstream_notices.py
```

The first command uses local exact Git objects, does not fetch/publish, and regenerates the fixed manifest/provenance/dependency/artifact records. The latter two perform bounded public GET requests; responses are time-dependent observations. None sends forms, email or security reports.

## Decisions and S5/coordinator handoff

[rights-exceptions.json](rights-exceptions.json) is the actionable exception register. It identifies exact selected revisions/files, missing evidence, exclusions/remediation and accountable decision roles. Remaining decisions are selected PRP/TFA rights if ever bundled, mixed runtime/dependency obligations for a component bundle, any full-source historical payload inclusion, and accountable review of this exact package. Counsel/rights acceptance, S5 semantic publication-safety review and the release owner's final decision remain pending.

**S5 and coordinator review target:** exact `manifest.json`, SHA-256 `18c5f78c0f22d75da87995f8a96cb02bef106434f2cebcbf26f359ec37a2465a`, source `592919dd95396f3f6164cf0ceec1fd15c065691b`. Review infrastructure and sidecars in this PR are additional source-tree surfaces, separate from that package. Any package change, including adoption of S1/S2/S3/S5 changes, requires a regenerated inventory and delta review. This handoff is made available in the reviewable PR; independent S5 receipt/acceptance is not claimed.

PV-1 and #87 remain partial; nothing here closes them through inventory success alone. `reference_release_authorized=false` and `production_deployment_authorized=false` remain unchanged. C0's check-to-commit limitation, optional cooperating same-host C1, no C2/C3 and no real settlement remain the acceptance boundaries.
