# Artifact 1 - MVP Definition

Status: PROPOSED controlling MVP scope after operator adoption (architect ruling Q3); non-authorizing; release and production HOLD. The architect has selected Decision 1 control-plane ingress, Decision 2 route B, Decision 3 Replay + Evidence Pack with a bounded verifier, Decision 6 trusted synthetic resolver (see [architect-rulings.md](architect-rulings.md)); the operator must adopt the exact bounded profile. `docs/program-v0.2/minimum-profile.md` stays the broader v0.2 proposal and is not a release prerequisite for this MVP.

## Capability
A single-host, synthetic-effect demonstration that a governed refund action is proposed, evaluated against bounded authority held by a trusted resolver, authorized / refused / held, enforced at the execution boundary with pre-effect revalidation, recorded with decision, attempt, outcome and negative evidence, and reconstructed and verified independently of the producer. Scenario: the existing matched synthetic refund (USD 10, `effect:synthetic-refund-001`).

## Supported workflow and configuration (proposed fixed configuration)
- Components at the existing g8-r10 tuple, unchanged on main (pre-F3 text, superseded in part: the Control Plane pin 0a41faa9 changes if the bounded F3 repair is authorized and refrozen; the tuple is re-pinned at refreeze, see critical-path.md and the limitations below): Control Plane 0a41faa9, Runtime ec728da6, Replay 028f63d1, Evidence Pack a3ebbb90, Action Manifest fa170815 (Verifier c0b8ba1f as the bounded verifier, tested at its exact pin; ODES e86a25a1 only as an evidence-format dependency to the extent the selected records require it, architect Q7).
- Authority is evaluated against a fixed, synthetic, trusted authority source under controlled test conditions: this demonstrates enforcement logic, not production IAM integration or institutional authority delegation, and must not be advertised as production-grade enterprise authority (Alvorada Authority Context deferred).
- Native execution route (route B, `AtomicLocalControlPlaneExecutor`, operation identity enabled) against a synthetic SQLite destination; ingress by control-plane proposal (`acp run`-style), not the GAX exchange route. Route B is the architect's selection (Decision 2); Qualification must verify its in-transaction grant check and duplicate protection at the exact pinned revisions, selection itself does not qualify them. GAX is excluded.
- Linux, single host, same-host custody.
- The Orchestrator, the declarative registry, the mandatory-check catalogue and the external checkpoint are not part of the MVP configuration.

## Included (the seven required behaviours)
1 proposal; 2 authority evaluation by trusted resolver; 3 authorize/refuse/hold; 4 boundary enforcement with pre-effect revalidation; 5 decision/attempt/outcome/negative-evidence record; 6 independent reconstruction and verification; 7 safe behaviour on revocation, failed custody and unknown outcome (`unknown`, retry not eligible, reconcile).

## Explicit limitations (carried, not removed)
- Synthetic effects only; no claim of production effect safety or deployment-environment safety.
- Pre-effect revalidation is not atomic with the destination commit on the default C0 profile (check-to-commit race, D10); in-transaction checking holds only on the opt-in profile fixed by Decision 2.
- The resolver is a fixed, synthetic, trusted authority source under controlled test conditions; it is not institutional authentication. External agent identity is not verified.
- Same-host custody, no external anchor: local chain consistency with limited truncation detection. A holder of the destination credential is outside the boundary.
- Qualification so far is by the project's own separate Qualification repo; it has not been externally audited.
- Known limits F-16, F-18, F-19, D01-D15 and the six unimplemented scenarios stay as published.

## Two distinct outcomes
A functioning MVP demonstration (engineering readiness) can be reached with the fixed configuration and narrow scenario. A qualified MVP release needs the safety and evidence gaps relevant to exactly this scenario resolved and independently accepted. The two are tracked separately. If the ambiguous-effect path (architect Q9) cannot be established, the MVP remains a demonstration and cannot pass the safe-retry / ambiguous-effect release claim.

## Exclusions
Registry activation and `/1` migration; 58-entry mandatory-check catalogue; scanner normalization; Orchestrator workflow lifecycle, event-store limits, archival and checkpoints; Observability Coverage Manifest; drift monitoring; agent-identity interoperability; OpenTelemetry projection; ISS V6; additional adapters; broad refreeze cascades. See the register for reasons.

## Trusted-host profile conditions (architect MVP2 Q9; conditional, subject to Qualification)
- One designated ingress process.
- Only that process holds destination write access and the relevant authority-writer capabilities.
- The ingress fixes operation identity and `simulate=None`.
- Claim provisioning and execution APIs are not exposed to untrusted clients.
- The supported interaction is a governed proposal, not arbitrary invocation of internal effect APIs.
- File ownership and permissions are captured as part of the exact Linux qualification environment.
- No claim of isolation from malicious code already executing with the process's privileges.
Qualification must show the declared ordinary client interface cannot reach the excluded surfaces; assuming well-behaved clients is insufficient. A wrapper alone is not sufficient (Q11). If these conditions cannot be enforced, the profile does not hold and that is a stop condition.

## Narrow evidence claim (architect MVP2 Q6, text verbatim; Qualification must establish each affirmative statement before publication)
> The selected synthetic route produces decision, journal and effect evidence that Replay and Evidence Pack can reconstruct and verify within the declared profile. The separate Verifier evaluates applicable Control Plane run-record checks but abstains on V4 attempt-ledger agreement because this route does not emit that attempt layer. Complete V4 ledger conformance is not claimed.

An ABSTAIN is not a PASS and is never converted into one.

## Two verification paths (architect MVP2 Q7)
| Path | Scope | Permissible claim |
|---|---|---|
| Replay + Evidence Pack | Reconstruction, consistency and integrity of supported evidence | Verified within the exact supported evidence profile |
| Verifier | Control Plane run-record checks and applicable ledger semantics | Partial conformance assessment, with explicit ABSTAIN |
The Verifier is not the final stage of Replay/Evidence Pack unless it consumes their output. A passing reconstruction path cannot erase a separate Verifier failure.

## Added explicit limitations (architect MVP2 Q8, Q9, Q11)
- Callers with in-process execution access, and holders of the destination database file or credentials, are outside the guarantee; claim authenticity is an unkeyed hash (no keyed claim MAC in the MVP; MAC is post-MVP, conditional).
- This is a trust-based boundary, not a general-purpose sandbox; no multi-process or adversarial-host claim.
- The claim-journal defect (`journal_check_reused`) requires the bounded Control Plane F3 repair and refreeze before any claim needing valid claim-stage journal evidence; see [investigation-findings.md](investigation-findings.md).
