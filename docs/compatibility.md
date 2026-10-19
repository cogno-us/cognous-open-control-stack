# Selected compatibility

The lock selects the component revisions listed below. GAX selects `security-runtime-p2-20261018`; the execution path remains bounded authorization/effect with executor producer profile 2.0.0 and Reconstruction Bundle 0.2.0.

| Component | Selected revision |
| --- | --- |
| control_plane | `2bac7875391cad0a431fa0d75208b7ade39743e3` |
| moltbot_safe | `6b16962db140590b808f02b5c2cb11a217aec46f` |
| replay_bundle | `6a6a477495ac24e813f12bb0fe314acfe8bac9cf` |
| governance_evidence_pack | `fd030615a782a064b89c57e8e40d7f220f99ff9e` |
| odes | `2893d935f1cb60d1854a3802cc32d739ddfd4efb` |
| gax_imx_transport | `fdc2a410383396553254a39ae641c88b78ee13f1` |

Evidence Pack selects transformation `agep-manifest-reconstruction-import/0.3.2`; ODES selects `odes-cognous-stack-export-0.2.1`, retaining pder-v0.1. Manifest 1.1 and Authority Context 0.1.0 remain unchanged. Original artifacts and evidence-only recovery preserve decision/effect/attempt lineage. Historical producer/consumer combinations remain isolated in compatibility suites; records are not relabeled to newer revisions.

The full candidate run [37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916) passed all four batches and all 35 acceptance scenarios with both required repetitions, for the earlier selected tuple (the combination qualified in hub PR #23). That tuple is superseded by the revisions above, and no release run exists for the current lock. Adoption-head CI for the earlier tuple is separately recorded in the adoption PR.

Selected source contains the opt-in authority/effect and refund-intent implementations. This integration enables neither execution profile; no combined guarantee follows from selecting their source. Equivalent business intent with distinct operation identities remains a characterized limitation of the bounded path. Live OpenShell, production authority/key custody, remote revocation, fleet orchestration and independent external-truth verification remain unqualified.

[Historical compatibility record](compatibility-before-merged-adoption.md) preserves earlier revisions, interface repairs and findings. [Release status](release-status.md) separates selected behavior from historical and optional-profile qualifications.
