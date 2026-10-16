# F2 repaired-source reconciliation — 16 October 2026

[Single finalization control plane](https://github.com/cogno-us/cognous-open-control-stack/issues/68).

Runtime security PR #90 is merged at `fd6b76fa0e85feb5b67324114bf790d3a12fdaf1`.
Exact premerge head `ca14a9617b990f441872162a5d8963a1fcde3b5f` reports 50 successful checks and one iOS skip. That is component-head evidence, not acceptance of an assembled selected stack.

## Reviewable source proposal

`profiles/security-remediation-source-probe-20261016.json` pins seven actual merged component-main commits for a source-admission probe. It is explicitly **nonselected and nonauthorizing**. It is not an applied selection patch and is not claimed compatible. Component-main may include intervening optional work; this probe does not activate those capabilities.

| Component | Historical selected lock | Earlier refusal candidate | Merged source probe |
|---|---|---|---|
| action_manifest | `46c950bed37fe3812000895430bc0312d29e37ce` | `46c950bed37fe3812000895430bc0312d29e37ce` | `e385f8c19b4444817a8b84b72ed6edbc37deb807` |
| control_plane | `d3dadee70bd319812b207389ab1e0f6efe511916` | `c7f122ba3a6e39f9268a7163c99be3ee514cd97e` | `996baeb476c8745b1a58ddc968b9eecc6a39b76b` |
| moltbot_safe | `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` | `309e194c1b0a3de23e11e20133e6eaf88875e48a` | `fd6b76fa0e85feb5b67324114bf790d3a12fdaf1` |
| replay_bundle | `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa` | `83fbaf2a0f6f071aca1ea0af859eb8fc6385c26a` | `733e282bf5af82787e2f4e146a378b94df15869a` |
| odes | `c5e9a0f3695ae836b803be06c46d2c669642ee03` | `25c7ad608c2e6fd9f450e075db6bbf3ee4091a49` | `42d0893217b82c22dcbdc47a19a3e25d074e7078` |
| governance_evidence_pack | `b4baccd823d2a73be276c1de745b19cf7c56a0d6` | `1e789c7d67a897097445faef1813fb0cd22d55e5` | `3090ef7b715bf109e786632e2be4b2a2008a5a7f` |
| gax_imx_transport | `a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf` | `9de2d438ed03531bb960c896f541a6a2da1b2315` | `71d1a113d43be48da782a57dc8314f317ce7e4cf` |

The historical `component-lock.json`, full-release candidate, W7 candidate and bounded-reference selection remain byte-identical. Their past qualification applies to their recorded pins. The seven-component probe is not a complete 13-component release profile and supplies no proof for excluded components.

## Concrete compatibility blockers

The existing `typed-refusal-candidate-20261015` Exchange profile still verifies the older CP/executor/Replay/ODES/Evidence Pack and Manifest commits. Its verifier deliberately rejects new actual heads. Replay, ODES and Evidence Pack likewise admit only recorded Control Plane generations and do not recognize the new current CP head. Do not bypass these checks, relabel the new source as an older commit, or assume shape compatibility from schema versions.

Executable source-admission evidence belongs in the central qualification repository at `results/final-source-preflight-20261016/`. This reconciliation is not scenario execution. The next integrated campaign remains NOT RUN until the admission prerequisite is repaired.

## Required bounded continuation

1. Scope an explicit repaired compatibility generation in Replay, binding actual CP and executor revisions. Reuse and verify existing refusal/runtime-authority semantic checks; preserve historical mappings, unknown-field reporting and nonauthorizing exports. Identify which optional CP fields are present rather than silently dropping them.
2. Migrate ODES and Evidence Pack to the actual merged Replay revision and the same exact producers, retaining strict reconstruction, restrictions and issuer/status checks. Qualify their actual outputs and all affected negative cases.
3. After those consumer merges, add a separate Exchange profile with the exact resulting producer/consumer pins and Manifest fixture. Keep historical `typed-refusal-candidate-20261015` unchanged.
4. Freeze those merged sources as the next candidate, repeat the existing bounded positive/refusal/lost-ack/restart/ownership cases and relevant complete-reference regressions, inspect retained destination/consumer evidence, and only then prepare an applicable selection delta.

F2 source reconciliation and a concrete nonselected proposal are delivered by this PR. F3 remains blocked on explicit compatibility migration and subsequent exact-source execution. This does not ask the owner to approve unqualified pins.

Final package regeneration, approved exclusions/original notices, fresh final security review, accountable acceptance and final publication decision remain subsequent F4–F8 tasks. Historical #144 archive bytes remain unchanged. No paid trials, external communications, release/tag, new grants, production effects or selection promotion occurred. C0 race, optional same-host C1, no C2/C3 or real settlement, and operational HOLD remain explicit.
