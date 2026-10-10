# PV-FINAL-DIST — independent selected-pin distribution and navigation verification

Date: **2026-10-10**. Issue [#87](https://github.com/cogno-us/cognous-open-control-stack/issues/87); parent [#83](https://github.com/cogno-us/cognous-open-control-stack/issues/83). Independent input: integrated draft [PR #84](https://github.com/cogno-us/cognous-open-control-stack/pull/84) exact **head `62c93784f34f6ad0a3f63a5efac04a948e826ae1`**, accepted main base `3efe456d10a37dcdd2277b4a37d9034403380f09`. Source of selection: `component-lock.json` at frozen head, Git blob **`b3bf15918ec7eaccd10c486b61926351d392dd04`**, profile `merged-producers-v1`. This is a **report-only, non-authorizing independent follow-up**, not a replacement for the partial [PV-LINK ledger](pv-link-2026-10-10.md).

## Method, evidentiary meaning and checks

1. Read issue #87, integrated PR #84 metadata/diff, the selected lock, hub `LICENSING.md`, `SECURITY.md`, existing `docs/verification/pv-link-2026-10-10.md`, and exact-head Git tree. Queried all **13** selected component Git trees by full pinned commit SHA via authenticated GitHub Git-tree API with `recursive=1`, recording `truncated=false` for all 13. The only selected component using `accepted_sha` instead of `sha` for its canonical core implementation is Execution Runtime; use the lock's `accepted_sha`. Trees enumerate tracked files, **not bundled dependency transitive license clearance**.
2. Compared root LICENSE / SECURITY path probes already documented in PV-LINK against complete selected-revision tree path listings. For selected exceptions, fetched Index `docs/SECURITY.md`, PRP/TFA README, GAX README, Execution Runtime `NOTICE`, and Institutional Governance `NOTICE.md` via authenticated exact-ref file-content API, retaining blob SHAs below. Successful content returns expose file blob SHA but not an HTTP status code. Missing paths are *path-specific* 404, not legal determinations.
3. Retrieved three GitHub Actions runs and orchestrator issue #30 by GitHub authenticated REST GET URL; exact run metadata and source SHA appear below. Separate public web/browser fetches of the selected run and issue-form chooser yielded **cache misses**; GitHub connector fetch of issue-form chooser yielded 404 from an unsupported/non-resource navigation endpoint. Neither response proves that public browser navigation fails. No redirects, final browser URL or live form-submission outcome were observed.
4. No checkouts, shell checks, browser DOM/fragment clicks, package installations, test suites, rendered documentation HTTP crawls, or third-party dependency scanner executions occurred. **This is not a complete advertised-external-link or rendered-anchor audit**. Earlier local docs checker results are source claims, not reproduced by this worker.

## Exact selected SHA, license and reporting-path ledger

Legend: `root` = actual root file present at selected SHA; `absent root` = not in complete selected Git tree / earlier API path 404; `alternate` = verified alternate selected-revision path. Tree enumerations are full (`truncated=false`). All repositories below are under `cogno-us/`; each row target is `https://github.com/cogno-us/<repo>/tree/<SHA>`. License name is descriptive from selected file-text checks previously recorded in PV-LINK, not legal clearance.

| Selected component repository | Exact selected SHA | Root license / notice findings from complete tree | Security reporting artifact at selected SHA |
| --- | --- | --- | --- |
| `cognous-action-manifest` | `46c950bed37fe3812000895430bc0312d29e37ce` | `LICENSE` Apache-2.0; `NOTICE` | root `SECURITY.md` |
| `cognous-control-plane` | `d3dadee70bd319812b207389ab1e0f6efe511916` | `LICENSE` Apache-2.0; `NOTICE` | root `SECURITY.md` |
| `cognous-institutional-governance` | `fb3d97938969a89e149e8ff8db2756091d1233fc` | `LICENSE` CC BY 4.0; `NOTICE.md` blob `36fbb002225820e78328c71d198e1415f179bbef` specifies attribution and external-rights carveout | root `SECURITY.md` |
| `cognous-governed-exchange` | `a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf` | `LICENSE` Apache-2.0; `NOTICE` | **No tracked SECURITY-named file** at selected tree; maintainership reporting may use hub policy but per-component private route not verified |
| `cognous-execution-runtime` | `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` | root `LICENSE` MIT upstream; `LICENSE-APACHE-2.0`, `engine/LICENSE` Apache-2.0, `NOTICE` blob `9cae5fd07d87266c6b71cf4cf6f5018b1e8cb90e`; **nested third-party notice/license paths exist** (e.g. `Swabble/LICENSE`, `apps/macos/Sources/Moltbot/Resources/DeviceModels/LICENSE.apple-device-identifiers.txt`, `extensions/open-prose/skills/prose/LICENSE`, `skills/skill-creator/license.txt`) | root `SECURITY.md` |
| `cognous-replay-bundle` | `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa` | `LICENSE` Apache-2.0; `NOTICE` | root `SECURITY.md` |
| `cognous-governance-evidence-pack` | `b4baccd823d2a73be276c1de745b19cf7c56a0d6` | `LICENSE` Apache-2.0; `NOTICE` | root `SECURITY.md` |
| `open-decision-evidence-standard` | `c5e9a0f3695ae836b803be06c46d2c669642ee03` | `LICENSE` Apache-2.0; `NOTICE` | root `SECURITY.md` |
| `cognous-evidence-attestation` (BitRep) | `5b5077dafde232a7801cb425c4efddcffb468723` | root `LICENSE` MIT; selected tree has **no `LICENSES/MIT.txt`**; later licensing guidance differs | root `SECURITY.md` |
| `cognous-evidence-registry` (Index) | `d5e45d275cb301d9684b543e93b05997991d1cf2` | root `LICENSE` MIT; selected tree has **no `LICENSES/MIT.txt`** | root `SECURITY.md` **absent**, but **`docs/SECURITY.md` present and fetched**, blob `f1c62176e59d58907d61fa75a5824faf9ea9e5bd` (older security assertions and future integrations, not independent assurance); inspect its reporting section before calling its route operational |
| `portable-reasoning-protocol` (optional PRP) | `cb137f028e92448a56e785e3d4ea074b444fa225` | **No license- or notice-named tracked file anywhere in this 12-entry selected tree**; no license inferred from README; later license commit not selected | **No SECURITY-named tracked file**; README present blob `34b61bfd1ff6b15fe1ed9994d2d3714afc3d90b4` |
| `research-intelligence-protocol` (optional) | `30c7274b49c07a0df4c8ca7b281f2e3f8ae68dee` | root `LICENSE` Apache-2.0; `NOTICE` | **No SECURITY-named tracked file** |
| `truth-freedom-agency-protocol` (optional TFA) | `442d07b4891870abb1756fcb11c24ccf187706f4` | **No license- or notice-named tracked file anywhere in this 11-entry selected tree**; historical PDF rights and later licensing are not substituted | **No SECURITY-named tracked file**; README present blob `ffed16e75a103e5dd6ef6180c63a6bd2e4103fdf` |

**Resolution of the #81 four missing root SECURITY.md:** Index has a documented **alternate** at `docs/SECURITY.md`; the other three (Governed Exchange, Research Intelligence and optional PRP/TFA? Clarification: earlier ledger's four root SECURITY 404 listed **Governed Exchange, Index, PRP, Research Intelligence, TFA**, which is **five**, despite its claimed four. Tree results show **five** missing root SECURITY paths and **four with no SECURITY-named tracked file** after Index's alternate; 8 root SECURITY files present. Prior #81 totals `9 SECURITY present / 4 missing` appear arithmetically inconsistent with its own 13-row table. This report corrects by full-tree enumeration: **8 root SECURITY, 5 missing root; 1 alternate, 4 no security-named file**. The two missing root LICENSE paths (PRP and TFA) are confirmed as no license-named files anywhere in those two selected tracked trees. This does **not** establish that no copyright license or disclosure channel exists outside the tracked tree; it creates a distribution-signoff exception.

The hub `SECURITY.md` supplies an identified private maintainer contact for hub and related components; no sensitive contact or vulnerability detail is reproduced here. Structural text presence is not a tested mailbox, private advisory workflow, or secure submission exercise. Hub root `LICENSE`, `NOTICE`, `LICENSING.md`, `SECURITY.md` are present at frozen head.

### Mixed rights and later guidance

`LICENSING.md` explicitly says Apache-2.0 is the policy for new Cognous-owned original content but that third-party and prior grants remain. Mixed original Cognous Apache / upstream MIT under Execution Runtime must be handled by file provenance, **not** by treating the entire repository as Apache. Institutional Governance at the selected pin is CC BY 4.0; BitRep and Index are MIT at selected pins. Licensing updates in the hub inventory and `licensing_head` entries apply to **later trees**, not retroactively to selected revisions:

- Institutional Governance later `412fbbdcd57d8390e140efd27f5e95ddc574bda6`
- BitRep later `b947baaed78fb854861f5a916bd36214acaa269b`
- Index later `b1571ac0f77b6232e0a143a4ce1728bc1db3f76a`
- PRP later `67c36e87c191a6a42b0acb775f500a58fc2fa7d9`
- TFA later `a1dc16794527fd39a21f0e89cef71d50c2cbef02`.

Third-party dependencies are **identified as surfaces**, not fully enumerated or cleared. Examples of exact selected manifest surfaces: runtime `package.json`, `pnpm-lock.yaml`, many `extensions/*/package.json`; Index `chain/package-lock.json` and Python requirements; Python `pyproject.toml` in Manifest, Control Plane, GAX, Replay, Evidence Pack and ODES; BitRep `requirements.txt`; Research Intelligence `requirements-dev.txt`. An SPDX or dependency license bill of materials was not generated; complete nested copyright/attribution obligations remain unverified, particularly the 5,073-entry runtime Git tree.

## External URL and rendered-navigation verification ledger

These URLs are **targets actually tested**; broad link extraction from all public Markdown, browser redirects and fragment-anchor clicking were not performed. A successful authenticated GitHub API request verifies resource existence/metadata, **not** browser HTTP status/redirect or rendered heading resolution.

| Target URL | Method, exact observation | Disposition |
| --- | --- | --- |
| https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916 | REST `GET /repos/.../actions/runs/37694032916` returned `completed/success`, `head_sha=7e43d55c6cc0123a191480a9e6870d6452affa83`, `html_url` equal to target. Public web fetch yielded cache miss, not HTTP 404 | **API verified / browser inaccessible**; no artifact content inspection |
| https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860 | REST metadata: `completed/success`, `head_sha=e926bbd70126ae9664bb4189bfe12eec4c18336b` | **API verified**; optional same-host C1 run, **not selected default** |
| https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37616662337 | REST metadata: `completed/success`, `head_sha=7c7eaa0a72401a789c0a5adac59f68d59b94ff19` | **API verified**; historical, not additive to selected generation |
| https://github.com/cogno-us/cognous-stack-orchestrator/issues/30 | REST `GET` returned issue #30 `state=open`, title `[O4e] Operator trust environment and deployment evidence` | **API verified**; operational trust remains **HOLD / NOT ESTABLISHED** |
| https://github.com/cogno-us/cognous-open-control-stack/issues/new/choose | Public web fetch cache miss. GitHub connector generic fetch returned 404 for non-REST issue chooser route; two YAML issue templates + `config.yml` exist in exact hub tree | **Rendered form navigation and submission not verified**, not proved broken |
| https://github.com/cogno-us/cognous-open-control-stack/pull/84 | Authenticated PR API returned open draft, exact head `62c93784f34f6ad0a3f63a5efac04a948e826ae1` | **API verified**; no merge or release approval |
| https://github.com/cogno-us/cognous-open-control-stack/issues/87 | Authenticated issue API returned open scope and exact report path | **API verified** |
| Exact SHA component tree URLs in table above | Git tree GET at all 13 SHA targets returned complete tree metadata | **Git object verified**, not rendered HTML, redirects or anchors |

**Unverified:** every other outbound link, the full rendered-anchor corpus, GitHub Actions run page browser rendering, redirect destinations/status codes for HTML, chooser/form interaction, security-reporting delivery, vendor/third-party outbound URLs, artifact zip contents, dependency-license notices. This is a **PARTIAL / not full distribution GO** finding, not an all-links pass. If the release gate requires real HTTP status and final redirects for **every** advertised URL, this worker cannot substantiate that gate.

## Exceptions, corrective handoff and scope

- **High-priority distribution exception:** PRP and TFA exact *selected* trees contain no discoverable tracked license or notice file. Resolve with qualified licensing review, properly selected replacement revisions if formally authorized, or exclusion from distributable package. Do not silently use later licensing heads. Optional status does not erase copyright constraints.
- **Security-navigation exception:** five selected root SECURITY paths absent by complete-tree evidence; Index has alternate `docs/SECURITY.md`, four have none. Hub reporting contact exists, but independently verify an authorized private response route and distinguish its scope from individual repository policies.
- **Third-party exception:** runtime MIT/Apache segmentation plus nested licenses and lockfiles requires distributable bill-of-materials and notice review; no legal clearance represented.
- **External link exception:** REST verifies three CI run resources and source SHA, but broad HTTP 200/301/302 + final-location crawl, GitHub-rendered fragment checking, and issue-form submission are **not evidenced**. Do not convert a web cache miss into a broken-link result.
- **Scope limit:** no files other than this new report, no component selection, PR #84 edit, checker edit, CI configuration, execution, credential, constitutional authority, release-permission or production-effect change. No new CI tests run; this is a bounded API/tree/content inspection with 13 complete-tree checks, 3 workflow-run metadata checks and issue/PR reads. No legal clearance or independent deployment security evaluation.

**Trust boundary preserved:** C0 checks immediately before dispatch but does **not** close the check-to-destination-commit race; C1 is optional cooperating same-host SQLite, not default; C2/C3 remain unqualified; no real refund settlement, remote atomicity, or production exactly-once guarantee. Evidence, issue forms, and licensing are not authorization. Operational trust issue #30 remains **HOLD / NOT ESTABLISHED**.
