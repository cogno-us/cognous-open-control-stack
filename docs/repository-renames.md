# Repository locations after the October 2026 rename

These are repository-location changes. They do not advance accepted component
revisions or introduce runtime guarantees.

| Previous location | Current location |
|---|---|
| `cogno-us/cognous-agent-action-manifest` | [`cogno-us/cognous-action-manifest`](https://github.com/cogno-us/cognous-action-manifest) |
| `cogno-us/bitrep` | [`cogno-us/cognous-evidence-attestation`](https://github.com/cogno-us/cognous-evidence-attestation) |
| `cogno-us/the-index` | [`cogno-us/cognous-evidence-registry`](https://github.com/cogno-us/cognous-evidence-registry) |
| `cogno-us/cognous-agent-control-plane` | [`cogno-us/cognous-control-plane`](https://github.com/cogno-us/cognous-control-plane) |
| `cogno-us/moltbot-safe` | [`cogno-us/cognous-execution-runtime`](https://github.com/cogno-us/cognous-execution-runtime) |
| `cogno-us/cognous-agent-replay-bundle` | [`cogno-us/cognous-replay-bundle`](https://github.com/cogno-us/cognous-replay-bundle) |
| `cogno-us/cognous-agent-governance-evidence-pack` | [`cogno-us/cognous-governance-evidence-pack`](https://github.com/cogno-us/cognous-governance-evidence-pack) |
| `cogno-us/alvorada` | [`cogno-us/cognous-governed-exchange`](https://github.com/cogno-us/cognous-governed-exchange) |
| `cogno-us/constitutional-governance-for-institutions` | [`cogno-us/cognous-institutional-governance`](https://github.com/cogno-us/cognous-institutional-governance) |

## Compatibility boundary

Clone URLs, GitHub Actions checkout repositories, navigation links and the hub
component lock use the new locations. Every selected and historical commit SHA
in the lock remains unchanged. Local checkout directory names explicitly chosen
by scripts and Actions remain unchanged.

Existing producer-profile `repository` and attempt `owner` strings remain their
versioned wire identifiers. Replay, Evidence Pack and ODES compare these values
against accepted revisions. Renaming them in place would break retained records.
JSON Schema `$id` values, protocol/package/import names, signed or hashed exports,
qualification result files and prior license notices also retain their original
identifiers and bytes. Their old repository spelling is intentional, not a new
checkout dependency. Adoption of renamed wire identities requires a separately
versioned compatibility change and qualification.

Current documentation links may use a renamed repository together with an
unchanged historical commit. This relocates the link without changing its evidence.

## Active branches

Workers should incorporate the reference-migration commit from their repository's
main branch before finalizing open PRs and check any newly added checkout URLs.
This migration does not rebase, overwrite or merge another worker's implementation.
Do not advance hub pins merely to adopt repository names.
