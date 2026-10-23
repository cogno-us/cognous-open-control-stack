# Architect disposition Q1-Q17: decision record and implementation status

**Non-authorizing record. Release, publication and production remain on HOLD.** Nothing here claims clearance, certification, qualification or readiness for any use. Source of the rulings: the architect disposition Q1-Q17 (binding for this programme). The Hub coordinates; component owners own components; independent Qualification owns oracles and verdicts; the operator owns authority decisions.

Controlling position (verbatim in substance): preserve the separation of Hub coordination, component ownership, independent Qualification and operator authority. The reported merges establish candidate engineering progress, not independent qualification or production readiness.

Related: [Q11 requirements](q11-reference-release-remediation-requirements.md), [Q15 profile](restricted-ancestor-profile-q15.md), [Q16/Q17 freeze boundaries](freeze-boundaries-q16-q17.md), [2.4 successor note](2.4-architect-defaults-successor-note.md).

## 1. Rulings

| Q | Subject | Ruling | Ownership / escalation |
|---|---|---|---|
| 1 | Qualification runner ownership | Approve with ownership correction. Fix lands in the Qualification repository, which owns the runner. The Hub may coordinate integration behavior, source tuple and priority; it may not direct or modify independent oracles and verdicts. Qualification reviews the runner change independently. After the repaired runner passes, requalify the exact candidate and update the Hub pin through a separate reviewed PR. Preserve historical failing runs. | Qualification repo owner (runner); Hub (coordination only) |
| 2 | Default vs profile mode | Profile-first: explicit, versioned profile mode is the supported release-evidence path. Default mode retired from normative use, historical invocations stay reproducible, no silent reinterpretation. Deprecate before removal if consumers break; version the interface. | Qualification repo owner (inferred from Q1; not stated in Q2) |
| 3 | Synthetic clock vs fixtures | Regenerate freshness fixtures whose assumptions are invalid, preserving predecessors and hashes. Declared deterministic synthetic-clock profile allowed for reproducible synthetic tests, never to establish real-time freshness. Any real freshness assertion needs an independently justified clock and source timestamp. | Qualification owns acceptance of replacements |
| 4 | Replay/ODES isolated tests | Optional hardening. Owners may propose installation-independent `-I` tests separately. Not a prerequisite: install the exact pinned distributions properly. Do not weaken Python isolation to conceal a packaging error. | Replay and ODES owners |
| 5 | Lifecycle, rename, event store | Partially authorized, unlocked Orchestrator repository only, separate reviewed PRs. 3.2-A: coordination states, terminal retention, archival, active-slot release (restart recovery, cancellation semantics, unresolved-effect preservation). 3.4-A: rename unmerged observation member to `execution_standing` before first schema freeze. 3.2-B: configurable store bounds, capacity accounting, load characterization; verified-head cache only with restart verification and preserved chain-integrity checks. Archival is not evidence deletion; cancellation cannot reverse an effect; a workflow awaiting authority stays durably recoverable without permanently consuming an active slot. Local, synthetic, non-effecting only. | Orchestrator owner |
| 6 | External checkpoint | Interface design and local synthetic implementation only. Evidence Attestation proposed as independent operational custodian, subject to its owner's acceptance. Orchestrator produces per-workflow head/count checkpoints; custodian retains them; Qualification verifies histories against retained checkpoints. Until adopted and qualified, the claim stays: local chain consistency with limited truncation detection. | Operator: final custody commitment, any locked Evidence Attestation change and its F3 package |
| 7 | Abstaining checks | Typed dispositions: `not_applicable` (frozen, source-backed predicate), `abstained` (applicable, executed, no substantive result; not a pass), `error` (failed, crashed, timed out, invalid result). If the contract cannot distinguish, return UNKNOWN or the existing fail-closed disposition. Every applicable mandatory check needs an accountable outcome. | Hub/2.3 contract; Qualification evaluates |
| 8 | Failure-path surrogates | Explicit surrogates only. Keep `v1.structure.run-record` and `v2.coverage.items-examined` as named failure-path identifiers if confirmed in pinned source; not ordinary successes or independent substitutes; preserve original failure identity, trigger, provenance. Qualification verifies the mapping neither invents coverage nor masks an error. | Qualification verifies |
| 9 | `input_read.*` and refuted-V1 | Distinct semantics. `input_read.<kind>` means the kind was actually read and accounted for. Refuted-V1 wording: "The required input was not read because the governing V1 premise was explicitly refuted under the applicable supported profile; the refutation and its evidence are retained." Justified inapplicability only where an independently accepted applicability rule establishes it; otherwise report missing input or unresolved condition. | Hub/2.3; Qualification |
| 10 | `verify_document` crash | Confirmed: a crash is `error`, not `not_applicable`. Preserve failure record and cause; no fabricated inapplicability code; not counted as success. | Hub/2.3 |
| 11 | Registry `/1` successor | Approve with version isolation: `ocs-registry-record/1`, closed `required_when_applicable` predicate identities, unconditional code-side floor kept, free-text `predicate` only for nonmandatory advisory rules. `/0` records stay valid under original validator and digest semantics, never silently reinterpreted. `/1` may reference a `/0` predecessor only via an explicit versioned migration transition with independent compatibility evidence. Syntax validated in 2.1, membership/meaning in 2.3; both required. | Hub (2.1/2.3); Qualification |
| 12 | 2.3 sequence | Confirmed: (1) finalize `/1` contracts, evaluator identity binding, closed applicability; (2) freeze exact candidate schemas and source commitments; (3) Qualification evaluates applicability, refusal paths, negative controls, evaluator equivalence; (4) reconcile F3 changes, pins, ordering, refreeze costs; (5) return for explicit 2.4 activation authorization. An engineering schema freeze is not a Qualification PASS; a PASS on reference code is not production authorization. | Hub then Qualification, then operator |
| 13 | Independent 2.3 qualification | Owner is `cogno-us/cognous-stack-qualification` through its own review. Hub supplies exact revisions, interfaces, raw evidence, proposed requirements; cannot author verdicts or modify frozen oracles. | Qualification repo owner |
| 14 | 2.4 design questions | Architectural defaults, operator gates retained. See [2.4 successor note](2.4-architect-defaults-successor-note.md). No 2.4 activation code authorized. | Operator |
| 15 | Restricted ancestor-symlink profile | Strict first profile. See [Q15 profile](restricted-ancestor-profile-q15.md). | Env owner declares boundary; Qualification evaluates; operator for expansion |
| 16 | Bounds and observation wording | Provisional. Retain `execution_standing` with exact closed values distinguishing workflow coordination, authority disposition and externally observed effect. Numeric bounds are configurable safety ceilings, not performance-safe defaults; defaults only after measurement; archival retention separate from active capacity; unresolved-effect evidence never discarded to reclaim slots. | Orchestrator owner; operator for production limits |
| 17 | Provisional wire names | Profile-specific freeze boundaries; freezing one does not freeze others. See [freeze boundaries](freeze-boundaries-q16-q17.md). | Per profile owner; Qualification |

The reported 58-check candidate, 18 predicates and manifest digest remain candidate evidence, not an adopted or qualified control profile.

## 2. Operator escalations (retained)

Locked-component F3 changes; external custody commitments; 2.4 activation authorization; release-scope expansion; production limits; new spending; any change to independent Qualification authority. Also: expansion of the Q15 restricted profile to new custody environments or trust boundaries; numeric thresholds and production acceptance in 2.4 defaults 8 and 10; M1 scope expansion (2.4 default 11).

## 3. Implementation status

Status words describe authorization to proceed only. None of them is a qualification result.

| Item | Status | Limits |
|---|---|---|
| 3.2-A coordination states, retention, archival, slot release | Authorized (bounded) | Unlocked Orchestrator repo, separate reviewed PRs, local synthetic non-effecting; tests with negative controls |
| 3.4-A rename to `execution_standing` | Authorized (bounded) | Before first schema freeze; same limits |
| 3.2-B store bounds, capacity accounting, load characterization | Authorized (Q5 lists it as a later bounded item; any ordering after 3.2-A is a Hub sequencing suggestion, not an architect ruling) | Ceilings configurable, not safe defaults; verified-head cache only with restart verification |
| Q6 external checkpoint interface and local synthetic implementation | Authorized (interface design, local synthetic only) | Custodian acceptance pending; claim stays "local chain consistency with limited truncation detection"; no locked Evidence Attestation change |
| `/1` registry/manifest contract and qualification preparation (Q7-Q13) | Authorized (preparation) | Docs, contracts, synthetic tests; no freeze counted as PASS |
| Q11 runner fix | Not a Hub action | Lands in Qualification repo under its own review; Hub requests only |
| Hub pin update | Not authorized yet | Separate reviewed PR after repaired runner passes and exact candidate is requalified |
| 2.4 activation code | Not authorized | Operator authorization required after 2.3 sequence |
| Locked-component changes (verifier, scanner, Evidence Attestation, Control Plane) | Not authorized | F3 package and operator approval |
| External custody commitment | Not authorized | Operator |
| Deployment, external effects, self-qualification | Not authorized | None permitted |
| Release, publication, production | HOLD | Unchanged |
