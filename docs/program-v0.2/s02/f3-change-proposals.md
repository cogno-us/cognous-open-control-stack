# Proposed F3 change packages for locked components (documentation only)

**Proposals, not changes.** No locked-component code is modified or authorized by this record. Each package describes a change that would need F3 requalification, refreeze and re-review before acceptance, and each code change needs its own separate authorization. Release and production remain on HOLD. ADR-P01 to P09 are used as labeled proposed assumptions; the M0 gate has not approved any of them. Static reading only; nothing was executed, so every reachability or behavior statement is a reading, not a result.

The cost of each cascade is the refreeze contingency in [estimates-m0-m1-m2.md](estimates-m0-m1-m2.md), which is not in the milestone totals. Observed cost of a refreeze is seven PRs in seven repositories (PD-C01); S01 and [../s03/minimum-profile-and-coverage.md](../s03/minimum-profile-and-coverage.md) section 4 give the evidence.

## Common template

Each package states: purpose; components touched; the change; why a locked change is needed; what stays unchanged; compatibility rule; evidence required; F3 steps; entry conditions; what it does not authorize.

Compatibility rule common to all (boundary commitment, [1.2](contracts/1.2-authority-and-separation.md) section 4): a committed field changes only opt-in or under a new profile identifier; with the opt-in unset, stored and hashed bytes are identical to today; old records re-verify byte-identically under new code.

## FP-01 Effect-surface closure (ADR-P08)

- **Purpose.** Make every reachable in-scope effect path mediated by the Control Plane gate, or prevented or excluded with a stated claim limit.
- **Components touched (candidate).** Execution Runtime (`engine/safe_executor.py`: `DurableRefundDestination` and its subclasses, `LocalDestinationExecutor.execute_snapshot`; `engine/openshell_environment.py`), Control Plane (`bounded.py` `LocalRefundDestination`; `tools.py` `execute_with_control`). A static scan at runtime `ec728da6` finds 6 direct and 12 total subclasses of the public commit surface ([coverage-seed.json](../s03/coverage-seed.json)).
- **Entry conditions.** A static reachability analysis from the profile path for each surface (class M or X). A surface classed X or U needs no code change, only profile text and a negative.
- **The change, by class.** M: route through the gate or make direct construction and calls refuse outside the gate. U (legacy `execute_with_control`, OpenShell commit mode): keep disabled by profile and add a negative that proves it. Whether a surface needs a code change at all is decided per surface after reachability.
- **Unchanged.** The gate's decision semantics, the constitutional floor, existing default behavior.
- **Evidence.** Independent enumeration of effect-capable paths in the frozen source; a removal-detection negative per mediated path; skipped live tests are not evidence.
- **F3 steps.** Requalification of the Execution Runtime and, if touched, the Control Plane; refreeze cascade; re-review.
- **Does not authorize.** Any effect, any real destination, any release.

## FP-02 Canonical JSON emission (ADR-P01)

- **Purpose.** Let new commitments use a named RFC 8785 profile without changing existing digests.
- **Finding that reduces scope (reading).** The registry digest ([1.3](contracts/1.3-registry-r0.md)) and the handoff envelope digest ([1.4](contracts/1.4-evidence-handoff.md)) are produced by the hub and the Orchestrator, not by a locked component, so they need no locked change. A deciding component only needs to carry an opaque `{profile, digest}` pair inside the decision context. The Control Plane already uses omit-when-unset optional members (`exclude_if` on `rule_identity` and `reason_vocabulary_version`, `bounded.py:343-346`), so an additional opt-in member holding two strings does not require re-canonicalizing anything.
- **Minimum.** No locked change for canonicalization itself. The contingent change is the opt-in context member (shared with FP-04).
- **When a real locked change would arise.** Only if a locked component must itself emit a JCS-canonicalized commitment. That is not currently required by any step and is not proposed.
- **Evidence.** A profile-identity table (step 1.3); a demonstration that default hashes are byte-identical with the member unset.
- **Does not authorize.** Reinterpreting any historical hash under a new profile.

## FP-03 Lock-driven overlay and reduced refreeze depth (ADR-P04)

- **Purpose.** Reduce sequential refreeze layers while never transferring a qualification to a different source revision.
- **Entry conditions.** Step 1.7 measures the layer depth of the last two refreezes from PR merge records (currently inferred at about four layers) and fixes a numeric target.
- **Options (analysis, not selected).** (a) Components read the tuple from a lock supplied at run time. (b) Qualification keys on content identity instead of commit identity, so merge identity changes do not invalidate a result. S01 found either needs a gate-semantics change on four locked components; the four are confirmed at step 1.7.
- **Constraint.** Qualification's pin engine is authored by human-authorized refreeze entries (see [1.4](contracts/1.4-evidence-handoff.md) section 3); the proposal does not replace that authorship.
- **F3 steps.** Requalification of each touched component, refreeze cascade, independent review of the gate-semantics change.
- **Does not authorize.** Automatic pin advancement.

## FP-04 Rule-set identity and rule kinds (registry R2)

- **Purpose.** Bind the active rule-set digest, evaluator ids and versions, and epoch into each covered decision, and extend rule revisions beyond the four existing kinds.
- **Components touched (candidate).** Control Plane (`RuleKind` literal in `rule_revision.py`; decision context; resolver), ODES `rule-revision` contract, Execution Runtime policy row (`authority_policies_v1`), exchange generation fence and BitRep digest custody if epochs are shared.
- **Contingent on the M1 family.** With the recommended scanner family scoped to the two unlocked consumers ([1.3 section 8](contracts/1.3-registry-r0.md)), no locked change is needed for M1 except the opt-in context member. A mandatory-check family needs the resolver and rule-kind change.
- **Unchanged.** The floor in code; the one gate per component.
- **Evidence.** Old-versus-new equivalence on frozen inputs; refusal tests per [1.3 section 5](contracts/1.3-registry-r0.md); rollback by a higher epoch.
- **F3 steps.** Requalification of the Control Plane and any other touched component; refreeze cascade; re-review.

## FP-05 Authority-to-observation fields in locked components (contingent; AOI)

- **Purpose.** Only if a locked component must itself emit a field the AOI envelope ([../aoi/aoi-c01-envelope.md](../aoi/aoi-c01-envelope.md)) needs and no existing record carries: for example agent attestation state, observer clock provenance, an observation id, or a recheck outcome field.
- **Finding that reduces scope (reading).** The recommended minimum assembles the envelope from existing records by reference (Orchestrator and the step 1.4 handoff), so no locked change is required for it. Fields with no source carry the state UNSUPPORTED.
- **Components touched (candidate).** Control Plane (`EffectObservation` has no id of its own; no clock-provenance field found), Execution Runtime (attempt namespaces), ODES contracts if a field becomes a shared contract. Not itemized: the field lists in the earlier readings are incomplete (REQUIRES INVESTIGATION).
- **Entry conditions.** An M0 decision that a specific field is mandatory in M1 and has no source; otherwise no package.
- **Compatibility rule.** The common rule above: opt-in or a new profile identifier, byte-identical default behavior.
- **Evidence and F3 steps.** As FP-01; requalification of each touched component, refreeze cascade, re-review.
- **Does not authorize.** Any code change, any effect, any OTel implementation or ISS linkage.

## Not proposed here

Locked changes for the known-issue items that need them (the R, M and D items in [../s01/issues-disposition.md](../s01/issues-disposition.md)) are dispositioned at step 4.3, each as fix, explicit claim-scope exclusion or deferral; a security or functional blocker is not closed by documentation alone. The OpenShell live mode and any destination beyond synthetic SQLite stay out of scope.
