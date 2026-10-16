# Security Cloud remediation proposal — cognous-open-control-stack

Scan: https://chatgpt.com/codex/cloud/security/runs/wfr_e020892dd8d0503cdd47f80c629b890ccefd937e35f637af7c47a253057584f9
Scanned/base revision: `7f335099ca52a68533b6e78c2e35166a9109e35c`.

Require exact collateral inventories and contained paths, enforce dependency hashes, correct current contract/location documentation, tighten context lineage and local links, bound artifact parsing/expansion, verify excluded source hashes and actual Git commit identity. Historical evidence stays historical. No component selection or authorization changes.

## Finding coverage

- `csf_cff164fe4c6efeb12907ccf8` (medium): Collateral snapshot validation can pass with no documents or with paths outside the repository. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_fff60e51a5070d065af66d9c` (medium): Qualification workflows execute Python dependencies without cryptographic artifact binding. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_ec3423ded0f0dffb0605624a` (medium): Current release status cites an obsolete V1 extension evidence contract. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_215664c0f2d0d6b27b90e31d` (medium): Current documentation directs readers to qualification tools that are absent from this repository. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_080b03d37a8569d76758bdce` (low): Published collateral evidence schema is internally unsatisfiable. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_1b37a7c4f013f4c6627855b2` (low): Context evidence verifier accepts type-confused and non-exact lineage records. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_6c21511f40f59c2d4bc4165f` (low): Selected-documentation checks accept local links that escape the repository. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_a03db608d0460b31574afda6` (low): Roadmap undercounts the current selected component repositories. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_bf40cba0874795209c8ed489` (low): Offline artifact tools parse attacker-selected inputs without admission budgets. Proposed code correction; final disposition pending review and source-bound checks.
- `csf_6420f99e3539115d23335a9d` (low): Publication inventory does not fully bind excluded-file and commit provenance. Proposed code correction; final disposition pending review and source-bound checks.

## Validation and limits

Final full tests and preview checks recorded in the PR description.

Component changes require integrated qualification before any selected hub pin advances. These are proposed repairs; passing local checks is not independent security certification. The package frozen at hub `7f335099ca52a68533b6e78c2e35166a9109e35c` has not been regenerated or relabeled as containing these edits. No publication or production authorization is granted. No paid model trials, production probes or external communications ran.
