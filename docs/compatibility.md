# Selected compatibility

The lock adopts the exact merged component combination qualified in hub PR #23. GAX selects `merged-producers-v1`; the execution path remains bounded authorization/effect with executor producer profile 2.0.0 and Reconstruction Bundle 0.2.0.

| Component | Selected revision |
| --- | --- |
| control_plane | `d3dadee70bd319812b207389ab1e0f6efe511916` |
| moltbot_safe | `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` |
| replay_bundle | `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa` |
| governance_evidence_pack | `b4baccd823d2a73be276c1de745b19cf7c56a0d6` |
| odes | `c5e9a0f3695ae836b803be06c46d2c669642ee03` |
| gax_imx_transport | `a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf` |

Evidence Pack selects transformation `agep-manifest-reconstruction-import/0.3.2`; ODES selects `odes-cognous-stack-export-0.2.1`, retaining pder-v0.1. Manifest 1.1 and Authority Context 0.1.0 remain unchanged. Original artifacts and evidence-only recovery preserve decision/effect/attempt lineage. Historical producer/consumer combinations remain isolated in compatibility suites; records are not relabeled to newer revisions.

The full candidate run [37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916) passed all four batches and all 35 acceptance scenarios with both required repetitions. Adoption-head CI is separately recorded in the adoption PR.

Selected source contains the opt-in authority/effect and refund-intent implementations. This integration enables neither execution profile; no combined guarantee follows from selecting their source. Equivalent business intent with distinct operation identities remains a characterized limitation of the bounded path. Live OpenShell, production authority/key custody, remote revocation, fleet orchestration and independent external-truth verification remain unqualified.

[Historical compatibility record](compatibility-before-merged-adoption.md) preserves earlier revisions, interface repairs and findings. [Release status](release-status.md) separates selected behavior from historical and optional-profile qualifications.
