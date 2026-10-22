# Declarative governance registry — adopted engineering direction

Record: `OCS-DGR-ARCH/1.0.0` (identifier assigned for this document; the operator may rename it).
Authority: operator instruction of 2026-10-21 to adopt the declarative-registry architecture and the engineering constitution for the stack ([engineering constitution (housed in its own repository)](https://github.com/cogno-us/cognous-engineering-constitution/blob/main/ENGINEERING_CONSTITUTION.md), CA18 Governed Policy and Protected Invariants in the current text; adoption of an exact revision is a separate recorded act).
Classification: stable design contract. It is not execution telemetry, not a new authorization to execute, not a change to any release status, and not a claim of qualification. It is non-authorizing and changes nothing about the current HOLD position or the V1 candidate under review. No production use is claimed or implied.
Scope: the decision gates of the stack's components and their governed policy and check metadata. It does not create a second decision point, does not replace effect-time authorization in the control plane and execution runtime, and does not change any vendored contract.

## Constitutional principle

**Governance rules are versioned data. Constitutional invariants stay enforced code.**

### Why

Review rounds on the stack repeatedly found the same two problem classes:

1. Wording and claim scanners are denylists written as regular expressions and duplicated across repositories (hub, verifier, ergonomics). Each repair was bypassed by the next encoding or markup variant, and the copies drifted apart.
2. Several decision checks were skipped or under-specified when an input was null, missing or non-boolean, or when a gate did not re-run the validator that defines the mandatory checks.

The first class belongs in governed data with one shared evaluator. The second is a completeness problem: the set of mandatory checks and their conditional applicability must be a closed, versioned table, and a missing or null input must fail closed rather than skip a check.

### Three partitions

1. **Constitutional floor, in code, owned by each component's one gate.** Mandatory applicability floors. Separation of authorization and evidence. Deterministic completeness, including incomplete or stale selection. Fixed precedence among complete adverse results (deny over quarantine over require-authority over require-evidence, where a component uses those dispositions). Preservation of all established adverse causes. No allow without all necessary check evidence. No model-origin authorization. Source and negative-record integrity. No shortcut from a governance result to an external effect. A registry entry cannot disable or weaken any of these.
2. **Versioned, authenticated registry, as data.** Canonical check IDs and versions, applicable classes and profiles, required or advisory classification, explicit conditional applicability predicates, evaluator IDs and versions, typed input contracts, failure dispositions, missing and unavailable treatments, reason-code mappings, remediation and negative-record obligations, scanner term lists, negation scopes and allow-listed excusals, and the rule-set identity. The registry keeps issuer, version, digest, activation epoch, lineage and immutable historical versions. Constitutional precedence is referenced by the registry, never modified by it.
3. **Registered evaluators, as code.** Pure, deterministic, separately qualified checkers (hashing, canonical folding and normalisation, signature validation, typed guards, clock and storage verification) with stable IDs and versions. No arbitrary expressions, downloaded scripts, caller-supplied rules or new general-purpose rule language. Evaluators return typed results and evidence; only the component's gate combines them.

For the claim and wording scanners this means: the registry holds the terms, lookalike tables, negation scopes and excusals; one fixed, versioned evaluator performs normalisation (entities, escapes, invisible and control characters, markup, lookalikes) and matching; all repositories consume the same registry and evaluator by content hash, the way the stack already vendors shared contracts. The scanners remain accident-prevention lint, not a security boundary, and the documentation says so.

## Minimum governed records and activation

- A registry record contains a registry ID, schema version, catalogue and policy versions, profile and assurance identifiers, an effective epoch, a closed rule and check table, approved source references, evaluator IDs and versions, a canonical digest, the authoritative signer or custodian, and a predecessor reference. This is a conceptual field inventory; exact schema and wire names are frozen before any code is written.
- The resolver derives a **total mandatory check manifest** by deterministic lookup from the authenticated policy version, class, profile and assurance level. It refuses ambiguous, unknown, unsupported, unavailable, conflicting or non-monotonic selections and never falls back to a smaller manifest.
- Every required check retains a typed result and version, the result-input digest, the context digest, evidence references and any failure or unknown reasons. Covered decisions bind the selected registry and evaluator versions into their context commitment. Historical re-evaluation uses the original registry bytes. Current-policy re-evaluation is a separately identified event and never relabels an old verdict.
- Registry changes are governed policy mutations with authority, epoch and negative-evidence handling. An authenticated, pinned, immutable registry is permitted only inside an explicitly versioned reference profile. A settings file grants no bootstrap exemption.
- Mandatory safeguards cannot be disabled, removed, marked advisory, marked not-applicable without a proven source predicate, shadowed by a conflicting rule, or paired with an unqualified evaluator version. Registry validation fails closed before activation. Authentication establishes provenance, not constitutional validity, so the gate validates every registry against its floor.

## Implementation sequence

This is an implementation strategy inside the existing programme, not a new governance layer. Scanners come first because they are the smallest and most frequently bypassed rules; required-check manifests for the verifier identity checks and the control-plane gate follow. Algorithmic checks (archive binding, source-key folding, checkout verification) stay code.

| Unit | Bounded change | Exit |
|---|---|---|
| R0, contract freeze and inventory | Extract the source-backed floors and the complete inventory of scanner rules and mandatory checks from the existing repositories. Define the registry, evaluator and floor boundaries. Freeze the schema, canonicalization, activation epoch and invalid-registry refusal rules. No new policy interpretation. | Closed inventory, independently source-checked by qualification |
| R1, registry extraction | Mechanically move existing term lists, lookalike tables, check manifests, applicability, dispositions and reason tables into frozen registry data. Keep one evaluator path and one gate per component. No generalized rules engine. | Schema and digest validation, soundness checks |
| R2, registry-backed resolution | Replace constant-driven selection with deterministic pinned resolution. Prevent caller override, downgrade and unauthenticated activation. Bind registry digest and evaluator versions into the decision context. Keep fail-closed compatibility and rollback with version identity and without rewriting records. | Exact-head developer and negative regressions |
| R3, independent equivalence and adversarial tests | Freeze expectations before evaluating the changed candidate. Compare old and new behavior on the same bound inputs: complete check membership, order, causes and dispositions, stale and incomplete handling, conditional not-applicable, corrupted, unknown or unqualified registry, signature-invalid or expired rule, missing evaluator, replay, cross-tenant, negative history, no external authority. Preserve prior independent failures and BLOCKED results. | Qualification repository: exact-source raw evidence with scoped PASS, FAIL or BLOCKED |
| R4, integration gate | Source compatibility, one focused trust review of the code and data authority boundary, exact-head CI and independent qualification before integration. | Integration only after the applicable gates |

Existing release candidates and qualification runs are pre-registry reference candidates. Their evidence is not rewritten, not silently reclassified as registry conformance, and not fitted to new expectations. Publishing this document does not approve code changes, release, a refreeze, a pin move or any change to a held candidate.

## Acceptance obligations (not blanket waivers)

- Account for every current scanner rule, manifest check and cause, and isolate any residual policy left in code. No silent missing members, fallback rules, suppression or duplicated authoritative policy.
- Demonstrate byte and policy determinism, round-trip registry validation, fail-closed handling of unknown checks, evaluators and manifests, replay of old revisions, and qualified activation. Show the complete required checks and all adverse causes in decisions.
- Before replacement, collect old-versus-registry-backed behavior equivalence for each supported profile. Document any permitted difference with source, authority and an independently frozen expected outcome.
- Keep prior exact-pin qualification history as originally observed. New runs get new identities and independent outcomes. A registry extraction by itself resolves no open finding and qualifies nothing.
- Do not widen scope into real payment, network, subprocess or production-credential effects, or into production claims.

## Document governance

This document is normative and planned material under the constitution's documentation and operational-records separation: it describes obligations, contracts, gates and deliverables, not whether a PR is open, merged or green. Current status and authorization are recorded in the decision record and release status pages. Historical contract and profile evidence is archived with historical version labels and never silently edited.

Related: [engineering constitution (housed in its own repository)](https://github.com/cogno-us/cognous-engineering-constitution/blob/main/ENGINEERING_CONSTITUTION.md), [guarantees and limits](guarantees-and-limits.md), [engineering register](engineering-register.md), [qualification](qualification/).
