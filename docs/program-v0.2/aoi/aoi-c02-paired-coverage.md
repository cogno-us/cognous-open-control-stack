# AOI-C02: paired Enforcement and Observability Coverage (proposed contract draft)

**Proposed, documentation only (AOI-2, steps 1.7 and 4.2).** It records no decision, authorizes no work, changes no component or Qualification expectation, and adds no step. Release and production remain on HOLD. Machine-readable seed: [observability-coverage-seed.json](observability-coverage-seed.json). It extends the single coverage declaration of [../s03/minimum-profile-and-coverage.md](../s03/minimum-profile-and-coverage.md) section 3, which is kept unchanged.

## 1. Two declarations, one profile identity

| Declaration | Question it answers | Status vocabulary | Seed |
|---|---|---|---|
| A. Enforcement Coverage (already proposed, ADR-P08) | Which declared effect paths are actually gated, and tested? | classes M, X, U, B; status DECLARED, ENUMERATED, OBSERVED | [../s03/coverage-seed.json](../s03/coverage-seed.json) |
| B. Observability Coverage (new here) | Which event classes and fields can be emitted, joined to authority, retained and independently verified? | field states below; status DECLARED, ENUMERATED, OBSERVED | [observability-coverage-seed.json](observability-coverage-seed.json) |

Both bind the same exact profile and configuration identity (profile name, hub lock digest, exact component revisions), and each has its own test outcome. Neither is an enforcement verdict, neither authorizes anything (`authority_effect: none`), and neither can be derived from the other:

- Do not promote partial telemetry to complete monitoring.
- Do not promote observation to gate coverage: an observed event on a path does not make the path mediated.
- Do not claim wider coverage than the frozen tested path.
- Telemetry absence on a path is not evidence that no effect occurred there.

## 2. Effect-path dimension (shared with declaration A)

For each in-scope path the declaration states: in scope, mediated or unmediated, disabled, or explicitly excluded; whether it is a reachable supported path; and negative bypass evidence. The original five unmediated surfaces (EP-01 to EP-05 in the seed) are each dispositioned individually in both declarations. In the Observability declaration each surface additionally states whether events on it are observable at all (an excluded or disabled surface can be NOT_APPLICABLE with its source predicate). Reachability of each surface from the profile path is still REQUIRES INVESTIGATION (static pass not done); designation stays with the security review.

## 3. Observed-field dimension

Each field of the [AOI-C01 envelope](aoi-c01-envelope.md) in each event class carries one state in the declaration:

| State | Meaning |
|---|---|
| EMITTED | The source component writes the field into its own record |
| DERIVED | Computed from source records by a named derivation; the derivation is part of the declaration |
| JOINABLE | Present in different stores and joinable by a named key, but not carried in one record |
| PARTIAL | Present for some paths, versions or outcomes only; the restriction is stated |
| NOT_EMITTED | Applicable but not written by any component |
| NOT_APPLICABLE | Not applicable, with the source predicate that makes it so |
| UNKNOWN | Not yet determined. Qualified as `field.unknown`; it is none of the six lifecycle `unknown` enumerations of [1.5](../s03/identity-and-lifecycle.md) section 5 and is never converted to EMITTED or NOT_EMITTED without reading source |

Each entry also names the observation producer and the authority of source (which component owns the record). The declaration state and the per-record state of C01 (present, derived, inferred, unsupported, unobserved, not applicable, unknown) are related but distinct: the declaration says what the profile can do; the record says what happened for one event.

## 4. Completeness dimension

For each required field the declaration states: required or optional; the outcome when the field is missing (which per C01 section 8 is a typed state, never silent); redaction and retention policy; exact producer and configuration; custody identity; and the independent evidence that checks it. A field cannot be both required and UNKNOWN in a frozen profile.

## 5. Event classes in the seed

The seed lists event classes by the records that exist today: decision (admission and refusal), grant use, effect attempt, effect observation, human review, rule-set activation (proposed at 1.3), workflow state (proposed at 3.2), evidence handoff (proposed at 1.4), and negative or refusal record. Each field state is taken from the C01 matrix: where C01 says VERIFIED the state is EMITTED or JOINABLE as recorded; where C01 says REQUIRES INVESTIGATION the state is UNKNOWN. Nothing in the seed is an observation of a running system.

## 6. M1 applicability and claim restrictions (proposed)

- Required in M1: decision, grant, commitment, attempt, effect and observation references for the one bounded refund scenario, plus the evidence and pin references handled by the 1.4 envelope.
- Optional in M1: trace and span references, runtime instance and session, clock provenance, observation producer identity, agent attestation.
- NOT_APPLICABLE with predicate unless the profile includes an approval-bearing or governance-state-changing path: human review fields and ISS reference.
- The profile claim carries the wording: "observability coverage as declared for the frozen path; partial telemetry is not complete monitoring; observation does not establish enforcement."
- Hidden reasoning and confidence signals are not fields.

## 7. Validation (later, not part of this documentation)

A hub check in the style of the coverage-declaration check proposed at 1.7 would validate the two declarations against their schemas and against each other (same profile identity; no state above what independent evidence supports). That is a later code change and needs its own authorization. Independent enumeration of events and fields is Qualification's; this draft supplies none of it.

## 8. Exit check for step 1.7 and 4.2 (AOI part)

An independent reader can read the Enforcement and Observability declarations for one profile, see that they bind the same identity but state separate outcomes, find a state and evidence requirement for each field, and see which claims the profile may not make.
