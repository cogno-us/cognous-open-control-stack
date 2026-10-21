# Selected compatibility

The lock selects the component revisions it records; the execution-path components are listed below. GAX selects `security-runtime-p2-20261018`; the execution path remains bounded authorization/effect with executor producer profile 2.0.0 and Reconstruction Bundle 0.2.0.

| Component | Selected revision |
| --- | --- |
| control_plane | `e77fe0ee8714617899592528e660a80fbb2e864a` |
| moltbot_safe | `cab4d9abc651c7efbafb429798d2c908f048bf5c` |
| replay_bundle | `53c0cd60d565ea1797ed0be87a2310c5b68b24f6` |
| governance_evidence_pack | `99ba3211450b25a18007b4b62907b072fe05c964` |
| odes | `dc5cf19d405ce885b287cde2f78519d3109b9ae6` |
| gax_imx_transport | `81b0877e1a9a82c2a61b1bafe631a4691556355f` |

Evidence Pack selects transformation `agep-manifest-reconstruction-import/0.3.8`; ODES selects `odes-cognous-stack-export-0.2.6-security-runtime-p2-candidate`, retaining pder-v0.1. The lock records these as the programme-2 profile candidates, not as a release. Manifest 1.1 and Authority Context 0.1.0 remain unchanged. Original artifacts and evidence-only recovery preserve decision/effect/attempt lineage. Historical producer/consumer combinations remain isolated in compatibility suites; records are not relabeled to newer revisions.

The full candidate run [37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916) passed all four batches and all 35 acceptance scenarios with both required repetitions, for the earlier selected tuple (the combination qualified in hub PR #23). That tuple is superseded by the revisions above, and no release run exists for the current lock. Adoption-head CI for the earlier tuple is separately recorded in the adoption PR.

Selected source contains the opt-in authority/effect and refund-intent implementations. This integration enables neither execution profile; no combined guarantee follows from selecting their source. Equivalent business intent with distinct operation identities remains a characterized limitation of the bounded path. Live OpenShell, production authority/key custody, remote revocation, fleet orchestration and independent external-truth verification remain unqualified.

[Historical compatibility record](compatibility-before-merged-adoption.md) preserves earlier revisions, interface repairs and findings. [Release status](release-status.md) separates selected behavior from historical and optional-profile qualifications.
