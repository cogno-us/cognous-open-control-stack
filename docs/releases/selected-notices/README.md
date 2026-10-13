# Selected-revision license and notice inventory

Verified 2026-10-13 against hub `f076f5f0cf085546dfa6c1d70f34b22c278c5fd0`.

This directory preserves original tracked license and notice bytes from the 13
selected component revisions. The [machine-readable inventory](../selected-notices.json)
records every source URL, Git blob SHA, SHA-256 and retained path. Full selected
Git trees were enumerated without truncation. These copies are attribution records,
not component source bundles, a new license grant or transitive dependency clearance.

| Component | Selected terms observed | Retained license/notice files |
| --- | --- | --- |
| action_manifest | Apache-2.0 | [LICENSE](action_manifest/LICENSE), [NOTICE](action_manifest/NOTICE) |
| control_plane | Apache-2.0 | [LICENSE](control_plane/LICENSE), [NOTICE](control_plane/NOTICE) |
| constitutional_authority | CC-BY-4.0 | [LICENSE](constitutional_authority/LICENSE), [NOTICE.md](constitutional_authority/NOTICE.md) |
| gax_imx_transport | Apache-2.0 | [LICENSE](gax_imx_transport/LICENSE), [NOTICE](gax_imx_transport/NOTICE) |
| moltbot_safe | MIT upstream; Apache-2.0 Cognous safety layer; nested terms | [LICENSE](moltbot_safe/LICENSE), [LICENSE-APACHE-2.0](moltbot_safe/LICENSE-APACHE-2.0), [NOTICE](moltbot_safe/NOTICE), [Swabble/LICENSE](moltbot_safe/Swabble/LICENSE), [apps/macos/Sources/Moltbot/Resources/DeviceModels/LICENSE.apple-device-identifiers.txt](moltbot_safe/apps/macos/Sources/Moltbot/Resources/DeviceModels/LICENSE.apple-device-identifiers.txt), [apps/macos/Sources/Moltbot/Resources/DeviceModels/NOTICE.md](moltbot_safe/apps/macos/Sources/Moltbot/Resources/DeviceModels/NOTICE.md), [engine/LICENSE](moltbot_safe/engine/LICENSE), [extensions/open-prose/skills/prose/LICENSE](moltbot_safe/extensions/open-prose/skills/prose/LICENSE), [skills/skill-creator/license.txt](moltbot_safe/skills/skill-creator/license.txt), [vendor/a2ui/LICENSE](moltbot_safe/vendor/a2ui/LICENSE) |
| replay_bundle | Apache-2.0 | [LICENSE](replay_bundle/LICENSE), [NOTICE](replay_bundle/NOTICE) |
| governance_evidence_pack | Apache-2.0 | [LICENSE](governance_evidence_pack/LICENSE), [NOTICE](governance_evidence_pack/NOTICE) |
| odes | Apache-2.0 | [LICENSE](odes/LICENSE), [NOTICE](odes/NOTICE) |
| bitrep | MIT | [LICENSE](bitrep/LICENSE) |
| the_index | MIT | [LICENSE](the_index/LICENSE) |
| prp | Unresolved at selected pin | None at selected revision |
| research_intelligence | Apache-2.0 | [LICENSE](research_intelligence/LICENSE), [NOTICE](research_intelligence/NOTICE) |
| tfa | Unresolved at selected pin | None at selected revision |

Original files are unchanged, including their copyright and attribution text.
Relative links inside copied notices belong to the original source tree; use the
exact source URL in the inventory when following those links.

## Distribution disposition

- Keep hub LICENSE and NOTICE with hub-owned material and retain applicable third-party notices.
- The bounded publication candidate is the existing hub documentation/qualification source and the explicitly approved synthetic evidence. It does not bundle external component checkouts, installed dependencies, toolchains, node_modules, or wallets.
- PRP and TFA selected source and historical PDFs are excluded from any proposed component bundle until their selected-revision rights are resolved. Their pins stay unchanged; later licensing heads are not substituted or treated as retroactive proof.
- Reproduction fetches external source separately. This inventory does not turn that fetch into a rights clearance. A complete redistributable/runtime bundle remains unaccepted.
- Preserve selected CC BY 4.0 institutional-governance attribution, MIT notices for BitRep/Index, and mixed runtime terms. Do not describe the whole selected stack as Apache-2.0.
- A later change to artifact scope requires a new inventory and applicable notice review. Third-party dependency lockfiles and downloaded packages are not fully cleared by this file.

Primary background: [Apache licensing FAQ](https://www.apache.org/foundation/license-faq.html).
The actual license texts and provenance of shipped files control; this technical inventory is not legal signoff.
