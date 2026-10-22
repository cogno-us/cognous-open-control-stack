# S02 proposed architecture dispositions (ADR-P01 to ADR-P09)

**Proposed, not accepted.** Nothing here is an operator decision, an adopted ADR, a repository setting change or an implementation. Each entry is a recommendation from an independent critical review of the S01 packet (received 2026-10-22, relayed by the operator), recorded so the S02 contract drafts have a stated starting point. Activation needs the review named in the Authority column and a separately recorded successor; a technical merge is not adoption.

Evidence references point to [s01/defects.md](../s01/defects.md) (PD ids) and [s01/inventory.md](../s01/inventory.md). The review's reasoning is summarised, not quoted as source evidence: where a statement is a design judgement rather than a source observation, it is written as one.

| ADR | Subject | Proposed disposition | Authority before activation | Register row |
|---|---|---|---|---|
| P01 | Canonical JSON | RFC 8785 (JCS) for newly introduced commitments; legacy canonicalization retained as a named historical profile | Operator approves migration semantics | Step 1.3 |
| P02 | Scanner behavior | Reconcile the three scanners first; then define one normative behavior; keep prior versions | Architecture review; operator if behavior changes | Step 2.2 (reconcile deliverable) |
| P03 | Registry location | Hub-owned, immutable, digest-pinned rule artifact; no new repository yet | Bounded design recommendation | Step 1.3 |
| P04 | Pin-overlay objective | Reduce sequential refreeze depth, not only PR count | Engineering design choice | Step 1.7 |
| P05 | Refund chain and ownership | Orchestrator is engineering integration owner; Qualification owns independent expectations and verdicts; reuse, do not copy | Contract decision | Step 1.2 |
| P06 | Repository protections | Targeted source-ownership proposals; no change to repository settings | Operator / GitHub administration | Step 1.2 |
| P07 | Crash continuation | Reconcile-only under existing contracts; no blind retry or implicit dispatch | Preserves existing boundary | Step 3.5 |
| P08 | Enforcement minimum | Coverage declaration and closure of reachable in-scope bypasses mandatory for the declared minimum profile | Architecture/security requirement | Steps 1.7, 3.3, 4.2 |
| P09 | OpenAPPA | Optional adapter behind an OCS information-flow contract; not exclusive | Architecture recommendation | Step 1.6 |

P01 to P06 involve canonical semantics or trust boundaries and are treated as proposed ADRs requiring review before activation. P07 to P09 follow existing boundaries or scope statements; they are still proposals here.

## ADR-P01 Canonical JSON profile

- **Context.** Four canonical-JSON families exist across the stack and ODES names `rfc8785-jcs` ([s01/defects.md](../s01/defects.md) PD-B02; owner decision 1). Registry digests (1.3) and handoff digests (1.4) need one profile and one owner.
- **Proposal.** New commitments use JCS with a distinct profile identifier. Existing records keep their original bytes and algorithm; a hash computed under one profile is never reinterpreted under another.
- **Reason.** Replacing a serializer can change a digest although the content is semantically identical. A named profile keeps old and new commitments distinguishable.
- **Consequences.** Step 1.3 owns the profile and publishes a profile-identity table; each consumer states which profile each stored digest uses. Whether any locked component must change to emit the new identifier is not established here; if one must, F3 requalification and refreeze apply and are priced separately ([estimates](estimates-m0-m1-m2.md)).
- **Open.** The migration rule for records that carry only a bare digest string.

## ADR-P02 Scanner behavior

- **Context.** Hub, verifier and ergonomics scanners differ: lookalike tables of 67, 76 and 77 keys, differing rule bodies, and a false ergonomics comment that the verifier shares the table (PD-B03). Hub and ergonomics are not locked components; the verifier is.
- **Proposal.** Do not select the largest table. For each difference, classify it as a deliberate source-backed requirement, a defect, or an accidental omission. Define one normative behavior, test the unified scanner independently against all three predecessor behaviors, and keep the predecessor versions as history.
- **Consequences.** The reconcile deliverable is on the critical path of any registry family that includes scanner rules (see [registry-and-effects.md](registry-and-effects.md)). A behavior change needs operator approval.
- **Open.** Whether unlocked scanners are in scope for the minimum profile.

## ADR-P03 Registry location

- **Context.** Options: hub-owned directory consumed by hash, a new data repository, or embedded in Control Plane (owner decision 3). Each added repository adds a pin carrier, a versioning surface and a distribution problem.
- **Proposal.** A hub-owned, immutable, digest-pinned rule artifact, consumed through existing component interfaces. The Hub is not a runtime authorization service: the Control Plane validates and enforces the authenticated, pinned snapshot inside its existing authority boundary. A separate registry repository can follow if requirements justify it.
- **Consequences.** The ADR is a step 1.3 deliverable. The hub gains no new pin carrier. Activation and freshness remain the Control Plane's existing authority (steps 2.4, 3.3).

## ADR-P04 Pin-overlay objective

- **Context.** Each refreeze has been observed to cost seven PRs in seven repositories for g7-r10 and g8-r10 (PD-C01). Qualification already has an overlay engine (`suites/_pins.py`).
- **Proposal.** Optimise for fewer sequential refreeze layers, not only fewer PRs. Automating seven sequential PRs without reducing dependency depth only makes the cascade faster. Analyse how a qualified component tuple can be frozen once and reused by consumers, without transferring a qualification to a different source revision.
- **Consequences.** S01 found that reducing depth needs lock-supplied tuples or content identity, a gate-semantics change on four locked components. That is a locked-component change with its own F3 requalification, so step 1.7 decides the target and step 4.1 builds mechanics only after that decision.

## ADR-P05 Refund chain, ownership and migration order

- **Context.** The refund chain exists three times (orchestrator, qualification matched-refund plus v1-scenarios, hub reference profiles; PD-A08). Assembly sits in Qualification and acceptance-like modules sit in the orchestrator, the reverse of the intended direction; Qualification does not execute or consume the orchestrator (PD-A02, PD-A09).
- **Proposal.** One canonical engineering integration scenario, owned by the Orchestrator. Qualification keeps independent matched-refund expectations and its verdict logic; the producer cannot overwrite an acceptance oracle. Reuse the current implementations; assign one source of truth for executable behavior rather than deleting every similar fixture.
- **Sequencing.** Three changes, kept apart ([ownership-and-sequencing.md](ownership-and-sequencing.md)): migrate engineering integration responsibility; retain frozen independent oracles in Qualification; add operational coordination. Handoff first, coordination second.
- **Open.** How much of the 15.9k-line qualification scenario harness and 1.3k lines of orchestrator acceptance modules move in v0.2. The S01 estimate assumed only the direction is fixed; this ADR may enlarge that scope (see estimate uncertainties).

## ADR-P06 Repository protections

- **Context.** No CODEOWNERS in the orchestrator or qualification repositories; rulesets show 0 required approvals with admin bypass (PD-A05).
- **Proposal.** Propose path-based ownership only where it enforces a real trust boundary: independent qualification specifications and verdict logic, constitutional or authority contracts, and release-selection surfaces. A blanket review requirement would conflict with the Engineering Constitution's risk-proportionate review policy. This workstream changes no repository settings.
- **Open.** The exact path list; only the operator can change settings.

## ADR-P07 Crash continuation

- **Context.** Deliberate refusals exist at `bounded.py:1763-1769` and `operation_admission.py:251-277` (PD-L04).
- **Proposal.** Reconcile-only by default. Recovery may inspect durable history and independently observed effect state; it must not treat a timeout as permission to execute again. Resumption or redispatch needs a separately versioned interface, an independently qualified battery and explicit authorization.

## ADR-P08 Enforcement minimum

- **Context.** Five effect surfaces sit outside the Control Plane gate by source reading ([registry-and-effects.md](registry-and-effects.md)); nothing was executed (PD-C03).
- **Proposal.** In the declared minimum profile the coverage declaration is mandatory and part of the S03 frozen profile (step 1.7), not deferred to final testing. Every reachable in-scope effect is mediated by the appropriate gate, or the profile prevents or explicitly excludes the path; the assurance claim is limited accordingly. A declaration that lists an unmediated surface does not repair it.
- **Consequences.** Closing an in-scope bypass can require a locked-component change, which needs separate authorization and F3 requalification.

## ADR-P09 OpenAPPA

- **Context.** OpenAPPA, Microsoft AGT and OPA artifacts already exist in the hub, Manifest, Control Plane and Qualification (PD-C02, PD-C06); the OpenAPPA site, the AGT repository and the paper "From Mainline to Governed Cognition" were not reachable in S01, so claims that depend on them stay REQUIRES INVESTIGATION.
- **Proposal.** No external information-flow framework is constitutionally privileged. Define the wanted semantics in an OCS contract; adapters implement or supply evidence for it. Reuse the existing OpenAPPA work first; do not build a competing native flow engine without a demonstrated gap.
- **Consequences.** Step 1.6 states precisely what is reused, what is incomplete and what new work is justified, and reconciles the OpenAPPA pins.
