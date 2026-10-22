# Step 1.7 draft: minimum profile, coverage declaration, overlay target, qualification entry

**Proposed contract draft, documentation only.** It records no decision, authorizes no work and changes no component, Qualification expectation or repository setting. Release and production remain on HOLD. Machine-readable seed: [coverage-seed.json](coverage-seed.json). It builds on [../minimum-profile.md](../minimum-profile.md), [../s02/registry-and-effects.md](../s02/registry-and-effects.md) and [../s02/adr-proposals.md](../s02/adr-proposals.md).

## 1. Named deployment profiles (V2-P4-03)

No source defines named deployment profiles (PD-L09); hub and Orchestrator profiles are release and qualification profiles. These names are proposals so that acceptance can name its target.

| Proposed profile | Status in v0.2 | Meaning |
|---|---|---|
| `bounded-synthetic-reference` | In scope | The existing reference path: synthetic SQLite destination, no network, subprocess or production credential effect |
| `single-host-governed-candidate` | In scope; the M1 target | One synthetic Linux host: registry-backed governance, durable Orchestrator coordination, existing Control Plane and Runtime effect gates, independent Qualification |
| `multi-agent-coordinated` | Out of scope | Marked out of v0.2 |
| `external-destination` | Out of scope | Marked out of v0.2; no remote settlement or distributed atomicity claim |

## 2. M1 acceptance specification

Every item is observed independently of the producer, against frozen expectations, and keeps raw negatives. None transfers from historical v0.1 results.

| # | Acceptance item | Step | Independent observer |
|---|---|---|---|
| A1 | Registry mechanism: authenticated immutable rules, typed evaluation, deterministic selection, refusal of invalid, stale, conflicting or non-monotone rules, historical identity | 2.1, 2.3, 2.4, 2.5 | Qualification |
| A2 | At least one real rule family migrated, with source-to-rule reconciliation and old-versus-new equivalence or authorized semantic differences | 2.2, 2.5 | Qualification |
| A3 | Each decision identifies the rule set and evaluator versions governing it, obtained by the component itself | 2.4 | Qualification |
| A4 | Durable single-host workflow; reconcile-only recovery; no blind retry; truthful unknown | 3.2, 3.5, 3.6 | Qualification |
| A5 | Source-preserving producer handoff; no producer write to acceptance expectations or verdict logic | 3.4 | Qualification |
| A6 | Closed effect-surface inventory: every reachable in-scope effect mediated, prevented or excluded; unmediated surfaces not merely listed | 3.3, 4.2 | Qualification enumerates independently |
| A7 | Exact selected tuple closed over pinned sources; no transferred historical pass | 4.1 | Qualification |
| A8 | Separate reporting of mandatory verdict, raw suite health and original-scope coverage | 4.5 | Qualification |

The final decision stays reserved to the operator; no result here grants release.

## 3. Coverage declaration

One declaration per profile lists every in-scope effect path with a class (M mediated, X excluded, U unsupported, B demonstrated bypass; see [registry and effects](../s02/registry-and-effects.md)), a reachability statement, the mediation point, the enforcing component and revision, a removal-detection negative, a reference to an independent enumeration, a status (DECLARED, ENUMERATED, OBSERVED) and the claim limit the profile must carry. The declaration is a non-authorizing record (`authority_effect: none`); it is validated by a hub check in the style of `tools/verify_embedding_exposure.py`, which is a later code change and is not part of this documentation. The field list is in the seed file.

A declared path is a claim by the producer. It reaches ENUMERATED only when a party other than the producer enumerates effect-capable paths in the frozen source, and OBSERVED only when its negative has run. Mocks and container-only tests never raise a status above application level.

### Correction to the S01 observation of surface 1

S01 recorded the public `DurableRefundDestination.commit` and "four subclasses". A static scan of `engine/*.py` at runtime `ec728da6` (syntax tree of class bases; nothing executed) finds six direct subclasses and twelve in total:

`AtomicAuthorityEffectDestination`, `DelayedCommitDestination`, `EffectiveGrantDestination`, `IntentRefundDestination`, `OpenShellRefundDestination`, `OperationIdentityDestination`, and the derived `DedupeTtlOperationDestination`, `DelayedEffectiveGrantDestination`, `DelayedOperationIdentityDestination`, `DelayedOperationIdentityEffectiveGrantDestination`, `OperationIdentityAtomicAuthorityEffectDestination`, `OperationIdentityEffectiveGrantDestination`.

The S01 count understated the surface. It is a static count of classes that inherit a public `commit`; whether any is reachable from the profile path is REQUIRES INVESTIGATION. This is why designation of surface 1 needs independent enumeration before it can be classed M or X. The seed carries the full list. The S01 record is not edited.

## 4. Pin-overlay target (proposed ADR-P04 detail)

Observed cost of a refreeze: seven PRs in seven repositories for g7-r10 and g8-r10 (four component re-ties, hub, ergonomics, qualification) and two for single-component refreezes (S01 inventory and PD-C01). Qualification already has an overlay engine (`suites/_pins.py`, 61 refreeze-log entries).

- Candidate measure: sequential layers, meaning the longest chain of PRs in which each merge identity feeds the next. INFERRED from the observed order: component re-ties (which may run in parallel), then hub, then ergonomics, then qualification, about four layers; not confirmed from merge timestamps.
- Step 1.7 deliverable: measure the layer depth of the last two refreezes from PR merge records and fix a target as a number of layers.
- Constraint: no qualification transfers to a different source revision. Lock-supplied tuples or content identity reduce depth but change gate semantics on four locked components, which needs separate authorization, F3 requalification and refreeze (not priced in the milestone totals; see the contingency in [../s02/estimates-m0-m1-m2.md](../s02/estimates-m0-m1-m2.md)).
- Step 4.1 builds mechanics only after the target is decided.

## 5. Frozen qualification entry

Before any M1 candidate exists, these are frozen and independently reviewed. Qualification owns each decision; engineering does not edit expectations, oracles or verdict logic.

| Prerequisite | Owner | State |
|---|---|---|
| Independent expectations for A1 to A8, written before the candidate | Qualification | Open |
| Freeze-boundary assessment, including the requirements file (131 rows) that is outside the freeze hashes (PD-A05) | Qualification | Open; Qualification's decision |
| Applicability of prp, tfa and the wiki-derived suite (PD-F01, PD-F02) | Qualification, with operator input | Open |
| Probe verdict rule (R14, `tools/v1_validation.py:678-681`) and impact assessment of affected claims | Qualification | Open; confirmed defect (PD-F03) |
| Scope-reduction disclosure semantics (PD-E02) | Qualification | Open |
| Comparator digest test wiring (PD-F04) | Qualification | Open |
| Orchestrator pins driven by the lock for the selected tuple (PD-A04) | Engineering (step 3.1) | Open |
| M0 gate review of ADR-P01 to P06 and these drafts | Reviewer named by the operator | Open |

## 6. Exit check for step 1.7

An independent reader can name the target profile and what is out of scope; read the acceptance items and the observer for each; read the coverage declaration fields and see every known effect path with a class and an evidence requirement; and find the overlay target stated as a measured number once the layer depth is measured, with the locked-component cost stated.
