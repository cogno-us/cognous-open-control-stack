# Selected compatibility

The lock selects the component revisions it records; the execution-path components are listed below. GAX selects `security-runtime-p2-20261018`; the execution path remains bounded authorization/effect with executor producer profile 2.0.0 and Reconstruction Bundle 0.2.0.

| Component | Selected revision |
| --- | --- |
| control_plane | `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c` |
| moltbot_safe | `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f` |
| replay_bundle | `40012b8c174c6f25685bd5d9bc93ff46cc9a5842` |
| governance_evidence_pack | `7b9511f2c6d56d424f17b078826594abd29f6c96` |
| odes | `1a5e1d300250d832e611633f0bf8f762e398c0ec` |
| gax_imx_transport | `7f7569b02666b99669a9fca61117ca1f4bce5f0d` |

Evidence Pack selects transformation `agep-manifest-reconstruction-import/0.3.8`; ODES selects `odes-cognous-stack-export-0.2.6-security-runtime-p2-candidate`, retaining pder-v0.1. The lock records these as the programme-2 profile candidates, not as a release. Manifest 1.1 and Authority Context 0.1.0 remain unchanged. Original artifacts and evidence-only recovery preserve decision/effect/attempt lineage. Historical producer/consumer combinations remain isolated in compatibility suites; records are not relabeled to newer revisions.

The full candidate run [37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916) passed all four batches and all 35 acceptance scenarios with both required repetitions, for the earlier selected tuple (the combination qualified in hub PR #23). That tuple is superseded by the revisions above, and no release run exists for the current lock. Adoption-head CI for the earlier tuple is separately recorded in the adoption PR.

Selected source contains the opt-in authority/effect and refund-intent implementations. This integration enables neither execution profile; no combined guarantee follows from selecting their source. Equivalent business intent with distinct operation identities remains a characterized limitation of the bounded path. Live OpenShell, production authority/key custody, remote revocation, fleet orchestration and independent external-truth verification remain unqualified.

[Historical compatibility record](compatibility-before-merged-adoption.md) preserves earlier revisions, interface repairs and findings. [Release status](release-status.md) separates selected behavior from historical and optional-profile qualifications.
