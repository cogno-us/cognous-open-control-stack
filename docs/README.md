# Documentation index

Every documentation page of the Open Control Stack hub, grouped by purpose. Historical and closeout pages are labelled historical rather than hidden: they remain valid for the revision they describe and do not describe the current selection.

The hub [component lock](../component-lock.json) is the sole source for selected revisions; [release status](release-status.md) interprets it. Shared scope and limits are stated once in [guarantees and limits](guarantees-and-limits.md).

## Start by role

| Your role | First page | Then |
|---|---|---|
| New reader | [Start here](start-here.md) | [Stack map](stack-map.md), [overview](overview.md) |
| Looking for a component, name or command | [Stack map](stack-map.md) | [Naming](naming.md), [profiles and tools](profiles-and-tools.md) |
| Developer reproducing the reference | [Developer quickstart](quickstart.md) | [Evidence index](evidence-index.md), [architecture](architecture.md) |
| Security or governance reviewer | [Governance quickstart](governance-quickstart.md) | [Release status](release-status.md), [security and threat model](security-and-threat-model.md), [residual risks](../residual-risks.json) |
| Reviewer of optional runtime modes | [Optional execution profiles](optional-execution-profiles.md) | [Recovery semantics](recovery-semantics.md) |
| Operator assessing a real deployment | [Release status](release-status.md) | [Deployment responsibilities](v1-deployment-responsibilities.md), [operational trust status](operational-trust-status.md) (HOLD, not established) |
| Private technical evaluator | [Private evaluator package](private-evaluator/README.md) | [Observation worksheet](private-evaluator/evaluation-worksheet.md) |
| Contributor | [CONTRIBUTING](../CONTRIBUTING.md) | [GOVERNANCE](../GOVERNANCE.md), [SECURITY](../SECURITY.md) |

## Current pages

### Orientation and map

- [Start here](start-here.md)
- [Stack overview](overview.md)
- [Stack map](stack-map.md): every repository, group, label and selected revision.
- [Documentation index of each repository](stack-map.md#documentation-index-of-each-repository): the index page of every component and tooling repository.
- [Naming](naming.md): display names, repositories, packages, commands, former names and status labels.
- [Profiles and tools](profiles-and-tools.md): commands, profiles and tools per repository.
- [Architecture and responsibility map](architecture.md)
- [Selected compatibility](compatibility.md)
- [Repository locations after the rename](repository-renames.md)
- [Relationship to ODES](relationship-to-odes.md)
- [Open-source boundary](open-source-boundary.md)
- [Platform support](platform-support.md)
- [Roadmap](roadmap.md)

### Status, scope and limits

- [What the stack guarantees and what it does not](guarantees-and-limits.md)
- [Support and release status](release-status.md)
- [Operational trust status](operational-trust-status.md)
- [Known issues register for the v0.1 private review release](releases/v0.1-known-issues.md): declared limits, issues observed in review and results measured outside the controller (non-authorizing; HOLD unchanged).
- [Recovery and evidence semantics](recovery-semantics.md)
- [Security and threat model](security-and-threat-model.md)
- [Security reporting and triage](security-reporting-and-triage.md)
- [Security coverage corrections](security-coverage-addendum.md)
- [Residual risks](../residual-risks.json)

### Reproduce and qualify

- [Developer quickstart](quickstart.md)
- [Governance reviewer quickstart](governance-quickstart.md)
- [Evidence index](evidence-index.md)
- [Cross-component test migration map](../CROSS_COMPONENT_TESTS.md)
- [Protected local worker qualification](protected-qualification.md)
- [Public developer preview qualification](public-preview-qualification.md)
- [Preview entry points audit](preview-entry-audit.md)
- [Cognous W0 C1-C8 baseline index](w0-c1-c8-baseline-index.md)
- [Batch 4C qualification index](qualification/batch4c.md)

### Profiles and extensions

- [Optional execution profiles](optional-execution-profiles.md)
- [Optional execution record consistency contract](optional-evidence-contract.md)
- [V1 reference extension profiles](v1-reference-profiles.md)
- [Context binding, notification and staging recovery](context-notification-recovery.md)
- [V1 extension evidence gate](v1-extension-release-gate.md)
- [V1 deployment responsibilities](v1-deployment-responsibilities.md)
- [Deployment review packet](deployment-review-packet.md)
- [OpenAPPA interoperability profile 0.1 (proposed)](integrations/openappa-interoperability-profile.md)
- [Optional OpenAPPA compatibility profile 0.1](integrations/openappa-optional-compatibility.md)

### Registers and bibliography

- [Consolidated engineering register](engineering-register.md)
- [Engineering constitution](engineering-constitution.md): adopted engineering articles EP01–EP18, review tiers and documentation rule DOC-01 (non-authorizing).
- [Declarative governance registry](declarative-governance-registry.md): adopted design direction for moving policy and check rules into versioned registry data (not implemented; non-authorizing).
- [Documentation reconciliation register](downstream-readme-corrections.md)
- [Research bibliography](research-bibliography.md)
- [Changelog](../CHANGELOG.md)
- [Licensing inventory](../LICENSING.md)

### Collateral

Collateral pages carry a pinned evidence digest and are not edited by documentation rework.

- [Business collateral](../collateral/business-collateral.md)
- [One-page overview](../collateral/one-page-overview.md)

### Private evaluator package

- [Cognous Open Control Stack — Private Technical Evaluation Package 0.1](private-evaluator/README.md)
- [Private technical evaluator — observation worksheet](private-evaluator/evaluation-worksheet.md)
- [Private evaluation feedback register](private-evaluator/feedback-register.md)
- [Private technical evaluation — invitation template](private-evaluator/invitation-template.md)
- [Private evaluator pilot — facilitator protocol](private-evaluator/pilot-protocol.md)
- [Synthetic evaluator pilot — enterprise runtime/security reviewer](private-evaluator/synthetic-pilot-2026-10-10.md)

## Historical pages

These pages record earlier checkpoints, candidates and closeouts. Their statements are scoped to the revision they name.

- [Compatibility and interface-gap matrix (before merged adoption)](compatibility-before-merged-adoption.md)
- [Support and release status (before merged adoption)](release-status-before-merged-adoption.md)
- [Targeted release-gate correction](release-gate-correction.md)
- [Security Cloud remediation proposal](security-cloud-remediation-20261016.md)

### Release and closeout records (historical)

- [Note on security-review-freeze-20261015](releases/NOTE-security-review-freeze-20261015.md)
- [Bounded V1 candidate release record — Governor C decision pending](releases/bounded-v1-governor-candidate.md)
- [Cognous bounded V1 — selected reference release (Governor acceptance pending)](releases/bounded-v1-reference-release.md)
- [Stack implementation closeout and remaining release gates](releases/closeout-2026-10-13.md)
- [S4 — distribution lane D technical closeout](releases/distribution-closeout-2026-10-15/README.md)
- [S0 engineering closeout and publication acceptance follow-up](releases/engineering-closeout-followup-20261015.md)
- [F3R qualification receipt — F5b-repaired candidate, 16 October 2026](releases/f3r-qualification-receipt-20261016.md)
- [F6 exact-package checks against the F5b review freeze — 2026-10-16](releases/f6-package-checks-20261016.md)
- [F7 acceptance packet — F5b-repaired bounded synthetic reference, 16 October 2026](releases/f7-acceptance-packet-20261016.md)
- [S0 exact-source closeout packet — 2026-10-15](releases/final-closeout-20261015/README.md)
- [Publication acceptance checkpoint — 2026-10-13](releases/publication-acceptance-2026-10-13.md)
- [Frozen source-review handoff — 2026-10-15](releases/security-review-freeze-20261015/README.md)
- [Repaired source-review freeze — 2026-10-16](releases/security-review-freeze-20261016/README.md)
- [F5b-repaired source-review freeze — 2026-10-16](releases/security-review-freeze-f5b-20261016/README.md)
- [Selected-revision license and notice inventory](releases/selected-notices/README.md)
- [W7 final integration gate — exact accepted W1/W2/W3 candidate](releases/w7-final-gate-disposition.md)
- [W7 final merged C1–C8 qualification — pre-acceptance record](releases/w7-final-merged-c8-qualification.md)


### Verification records (historical)

- [Adversarial review remediation](verification/adversarial-review-remediation-2026-10-15.md)
- [S6 — Final operational acceptance form, lane F](verification/operational-acceptance-checklist-2026-10-15.md)
- [S6 — Operational closeout, lane F](verification/operational-closeout-2026-10-15.md)
- [Public release blocker verification — 2026-10-13](verification/public-release-verification-2026-10-13.md)
- [PV-FINAL-DIST — independent selected-pin distribution and navigation verification](verification/pv-final-distribution-2026-10-10.md)
- [PV-FINAL-RUN — independent selected-lock clean-room reproduction](verification/pv-final-run-2026-10-10.md)
- [PV-FINAL-SEC: independent public-distribution security verification — 2026-10-10](verification/pv-final-security-2026-10-10.md)
- [PV-LINK external verification ledger — 2026-10-10](verification/pv-link-2026-10-10.md)
- [Public preview — resource-constrained qualification disposition](verification/pv-resource-constrained-disposition-2026-10-10.md)
- [S1 / candidate-integration lane A: nonselected hardening candidate](verification/remediation-candidate-2026-10-15.md)
- [Nonselected remediation full-reference qualification](verification/remediation-full-reference-2026-10-15.md)
- [S0 serial component repair and diagnostic checkpoint](verification/s0-component-repair-2026-10-15.md)
- [S5 — publication-safety lane E closeout, 2026-10-15](verification/safety-closeout-2026-10-15.md)
- [U1 security correction verification](verification/u1-security-corrections-2026-10-15.md)


### Workstream checkpoints (historical)

- [Accepted authority effect qualification](workstreams/accepted-authority-effect-checkpoint.md)
- [Engineering addenda intake — 8 October 2026](workstreams/addenda-intake-2026-10-08.md)
- [Agent governance engineering controls](workstreams/agent-governance-controls.md)
- [Ascended Intelligence comparison addenda](workstreams/ascended-intelligence-addenda.md)
- [Batch 4C — accepted-pin qualification checkpoint](workstreams/batch4c-integration-checkpoint.md)
- [Shared synthetic governance comparison](workstreams/comparative-governance-battery.md)
- [Context admission deadline follow-up](workstreams/context-memory-addenda-followup.md)
- [Contract and candidate artifact verification](workstreams/contract-artifact-verification.md)
- [Control Plane store-adoption qualification checkpoint](workstreams/control-plane-store-adoption-checkpoint.md)
- [Deployment review packet checkpoint](workstreams/deployment-review-checkpoint.md)
- [Destination admission engineering addendum](workstreams/destination-admission-addendum.md)
- [S2 — ingress-hardening lane B](workstreams/destination-ingress-hardening.md)
- [S3 — restore-boundary lane C](workstreams/destination-restore-boundary.md)
- [Documentation evidence alignment](workstreams/documentation-alignment-checkpoint.md)
- [Engineering addendum for federated governance and state continuity](workstreams/federated-governance-addendum.md)
- [Feedback B: declared provenance groups](workstreams/feedback-provenance-groups.md)
- [F2 repaired-source reconciliation — 16 October 2026](workstreams/final-source-reconciliation-20261016.md)
- [Full merged-chain candidate checkpoint (historical)](workstreams/full-candidate-release-checkpoint.md)
- [Institutional review addenda follow-up](workstreams/institutional-review-addenda-followup.md)
- [Integrated local assurance contract](workstreams/integrated-assurance-contract.md)
- [Interface-cleanup workstream checkpoint](workstreams/interface-cleanup-checkpoint.md)
- [Batch 4C — bounded late-commit qualification](workstreams/late-commit-checkpoint.md)
- [Supplied agent inventory reconciliation](workstreams/lifecycle-inventory-reconciliation.md)
- [Proposed logical-intent prevention contract](workstreams/logical-intent-prevention-contract.md)
- [Merged consumer chain candidate checkpoint](workstreams/merged-consumer-chain-checkpoint.md)
- [Merged-generation pin adoption](workstreams/merged-pin-adoption-checkpoint.md)
- [O6-P0A collateral evidence snapshot checkpoint](workstreams/o6-p0a-collateral-evidence-snapshot.md)
- [Operational state engineering addendum](workstreams/operational-state-addendum.md)
- [Optional execution selection checkpoint](workstreams/optional-execution-checkpoint.md)
- [Paired-request enforcement qualification checkpoint](workstreams/paired-request-enforcement-checkpoint.md)
- [Same-host process-boundary qualification checkpoint](workstreams/process-boundary-checkpoint.md)
- [Profile repair and evidence population integration](workstreams/profile-population-integration.md)
- [Protected qualification checkpoint](workstreams/protected-qualification-checkpoint.md)
- [Public README and collateral alignment](workstreams/public-readmes-collateral-checkpoint.md)
- [PV-ARTIFACT: selected release evidence payload inspection](workstreams/pv-artifact-evidence-inspection-2026-10-10.md)
- [PV-SAFETY: public-preview publication and claims audit (issue #73)](workstreams/pv-safety-publication-audit.md)
- [PV-SEC: bounded public distribution screening (issue #73)](workstreams/pv-sec-public-distribution-screening.md)
- [Batch 4C — recovery-authority qualification](workstreams/recovery-authority-checkpoint.md)
- [Release closeout control panel](workstreams/release-closeout-control-panel.md)
- [Research assurance addenda](workstreams/research-assurance-addenda.md)
- [RA-01: synthetic authority observation assurance](workstreams/resolver-observation-assurance.md)
- [Security correction contracts](workstreams/security-correction-contract-2026-10-15.md)
- [Repaired runtime source migration — 16 October 2026](workstreams/security-runtime-migration-20261016.md)
- [Semantic handoff reference contract](workstreams/semantic-handoff-contract.md)
- [Remaining engineering register work and serial estimates](workstreams/serial-engineering-plan.md)
- [SQLite staging recovery addenda follow-up](workstreams/sqlite-recovery-addenda-followup.md)
- [Temporal authority qualification follow-up](workstreams/temporal-authority-addenda-followup.md)
- [W7-P2/P3/P4 bounded release integration checkpoint](workstreams/w7-p2-p4-integration-checkpoint.md)
- [W7 bounded V1 integration baseline](workstreams/w7-release-integration-baseline.md)
- [Proposed atomic authority/effect integration qualification](workstreams/worker21-authority-effect-checkpoint.md)


## Keeping this index current

New hub pages should be added here in the group that fits them. Component repositories carry their own documentation indexes, linked from the [stack map](stack-map.md#documentation-index-of-each-repository). The hub [README](../README.md) links this index, and every page listed here is reachable from it.
