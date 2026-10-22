# Operator decisions and reserved choices

This is a stable decision-substance register, not live task telemetry. Existing owner directions are recorded as such; proposed solutions are not treated as adopted decisions.

| Subject | Authority state | Contractual consequence |
|---|---|---|
| v0.2 bounded single host, not fleet deployment | Operator scope direction | Nonproduction local target |
| Restore operational Orchestrator independent of Qualification | Operator architecture direction | Separate coordination and independent evaluation |
| Keep Control Plane/Runtime effect authority | Existing architectural boundary | No alternate authorization point |
| Governed registry rather than scattered hard-coded configurable rules | Adopted architectural direction; see ../declarative-governance-registry.md | Floor enforced in code; registered data/evaluators separately |
| Qualification owns frozen expectations and verdicts | Existing independent-qualification obligation | Producer cannot edit oracle or certify itself |
| Hub owns selected component-lock identity | Existing release-selection rule | No auto pin advancement |
| Shared Engineering Constitution | Operator decision | Exact revision adoption to be recorded separately |
| Release/deployment | HOLD and separately reserved | No candidate or document grants release |
| Rule storage location and owner | PROPOSED, not decided: hub-owned immutable digest-pinned artifact (ADR-P03); options in [s01/defects.md](s01/defects.md) | Step 1.3 ADR; each extra repository adds a pin carrier |
| Activation/freshness semantics | OPEN contract detail | S02 then gated P2 |
| Enforcement coverage minimum | PROPOSED, not decided: declaration mandatory and every reachable in-scope effect mediated, prevented or excluded (ADR-P08); five unmediated surfaces observed ([s01/comparative.md](s01/comparative.md), [s02/registry-and-effects.md](s02/registry-and-effects.md)) | Schema and inventory at 1.7, closure at 3.3, observation at 4.2 |
| Information-flow trajectory and non-authorizing remediation | S01 disposition: adapt and defer enforcement; OpenAPPA conjunction is the existing route. PROPOSED (ADR-P09): optional adapter behind an OCS contract, not exclusive | No native flow evaluator in v0.2 unless separately decided |
| Canonical JSON profile | PROPOSED, not decided (ADR-P01): JCS for new commitments; legacy form retained as a named historical profile | One owner at step 1.3; digests differ between the two; operator approves migration semantics |
| Scanner behavior to preserve | PROPOSED, not decided (ADR-P02): reconcile all three, define one normative behavior, keep predecessors | Reconcile at 2.2 before extraction; operator approves any behavior change |
| Pin-overlay target | PROPOSED, not decided (ADR-P04): fewer sequential layers (needs lock-supplied tuples or content identity, a gate-semantics change on four locked components) | Decision at 1.7 |
| Canonical refund chain; handoff versus refreeze authorship; repository settings (CODEOWNERS, required reviews, path rules) | PROPOSED, not decided: Orchestrator is engineering integration owner, Qualification keeps independent expectations (ADR-P05); targeted ownership proposals, no settings change (ADR-P06). Handoff versus refreeze authorship remains OPEN | Steps 1.2 and 1.4; settings need the owner |
| Meaning of continuation after a crash; stable effect identifier | Continuation PROPOSED reconcile-only (ADR-P07); stable effect identifier PROPOSED, not decided: select the existing ODES `operation_id` profile (SP-01 in [s03/identity-and-lifecycle.md](s03/identity-and-lifecycle.md)) | Step 3.5; any locked-contract change needs separate authorization |
| OpenAPPA as sole information-flow route; revision to cite; summarization host rule | Exclusivity PROPOSED against (ADR-P09); revision to cite and summarization host rule OPEN | Step 1.6 |
| prp and tfa (no tests, no top-level licence) and wiki-derived applicability | OPEN; Qualification decides independently | Controller #218 |

The proposals above are recorded in [s02/adr-proposals.md](s02/adr-proposals.md) as review input only. A sprint number is not authorization; a technical merge is not adoption. Record any new decision as a separately reviewed successor with source, exact identity and rationale.
