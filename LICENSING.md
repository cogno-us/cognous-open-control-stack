# Public stack licensing

Updated 2026-10-06 at the maintainer's direction.

Apache License 2.0 is the standard for Cognous-owned original material in the public stack. Existing third-party licenses, attribution notices, and prior license grants remain valid. A repository's LICENSE and scope notices control its distribution; this inventory does not relicense dependencies or external works.

## Applied updates

| Repository | Licensing commit |
| --- | --- |
| [cogno-us/cognous-governed-exchange](https://github.com/cogno-us/cognous-governed-exchange) | [11208008d597](https://github.com/cogno-us/cognous-governed-exchange/commit/11208008d597bc1eec45edacda7ec4a06deed0ce) |
| [cogno-us/cognous-evidence-attestation](https://github.com/cogno-us/cognous-evidence-attestation) | [b947baaed78f](https://github.com/cogno-us/cognous-evidence-attestation/commit/b947baaed78fb854861f5a916bd36214acaa269b) |
| [cogno-us/cognous-evidence-registry](https://github.com/cogno-us/cognous-evidence-registry) | [b1571ac0f77b](https://github.com/cogno-us/cognous-evidence-registry/commit/b1571ac0f77b6232e0a143a4ce1728bc1db3f76a) |
| [cogno-us/truth-freedom-agency-protocol](https://github.com/cogno-us/truth-freedom-agency-protocol) | [a1dc16794527](https://github.com/cogno-us/truth-freedom-agency-protocol/commit/a1dc16794527fd39a21f0e89cef71d50c2cbef02) |
| [cogno-us/comprehension-scope](https://github.com/cogno-us/comprehension-scope) | [17138cb1c372](https://github.com/cogno-us/comprehension-scope/commit/17138cb1c3720b18b1bae42a1d6c20492a15623f) |
| [cogno-us/comprehension-stack](https://github.com/cogno-us/comprehension-stack) | [cbb35efe6a7a](https://github.com/cogno-us/comprehension-stack/commit/cbb35efe6a7a6c36cf1041bfda276d06540c45ab) |
| [cogno-us/portable-reasoning-protocol](https://github.com/cogno-us/portable-reasoning-protocol) | [67c36e87c191](https://github.com/cogno-us/portable-reasoning-protocol/commit/67c36e87c191a6a42b0acb775f500a58fc2fa7d9) |
| [cogno-us/research-intelligence-protocol](https://github.com/cogno-us/research-intelligence-protocol) | [bf0ac11299d8](https://github.com/cogno-us/research-intelligence-protocol/commit/bf0ac11299d8058e4bde15808d6c38307759caf9) |
| [cogno-us/cognous-institutional-governance](https://github.com/cogno-us/cognous-institutional-governance) | [412fbbdcd57d](https://github.com/cogno-us/cognous-institutional-governance/commit/412fbbdcd57d8390e140efd27f5e95ddc574bda6) |
| [cogno-us/cognous-execution-runtime](https://github.com/cogno-us/cognous-execution-runtime) | [4ed7c9b9fbc8](https://github.com/cogno-us/cognous-execution-runtime/commit/4ed7c9b9fbc8159be70d68f2ca9bd8a8ddc012e3) |

## Already Apache 2.0

- cognous-agent-action-manifest
- cognous-agent-control-plane
- cognous-agent-replay-bundle
- cognous-agent-governance-evidence-pack
- open-decision-evidence-standard
- cognous-open-control-stack

## Scope and retained licenses

- Moltbot Safe: the Cognous Python safety layer, corresponding tests and Cognous safety documentation use Apache 2.0. The retained upstream application remains MIT; bundled third-party components retain their licenses. See LICENSE-APACHE-2.0, engine/LICENSE, LICENSE and NOTICE in that repository.
- BitRep and The Index retain the previous MIT notices in LICENSES/MIT.txt.
- Constitutional Governance for Institutions retains its earlier CC BY 4.0 license and attribution in LICENSES/. Other rights holders' contributions retain their existing terms unless separately authorized. Apache 2.0 includes its Section 3 patent grant; no trademark rights or institutional authority are conferred.
- TFA now has an explicit Apache 2.0 license, replacing the unresolved current-distribution description of CC0-style intent. Historical PDFs are unchanged.
- ISS, Navalia and private repositories are outside this public-stack change. The separate company website repository is outside this module inventory.

## Maintenance

Use Apache-2.0 in new Cognous-owned module license files and applicable package metadata. Preserve all third-party notices. Existing worker branches must retain these licensing updates when merged. Previously pinned commits retain the licensing files present at those revisions; use a later licensing commit when distributing the updated tree. No runtime version or dependency pin was changed by this licensing pass.
