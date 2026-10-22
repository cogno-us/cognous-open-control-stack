# Registry acceptance levels and the closed effect-surface inventory

Proposed, documentation only. Applies [ADR-P03](adr-proposals.md#adr-p03-registry-location), [ADR-P02](adr-proposals.md#adr-p02-scanner-behavior) and [ADR-P08](adr-proposals.md#adr-p08-enforcement-minimum).

## 1. Registry: two acceptance levels

The registry exists to replace distributed, diverging hard-coded configurable rules. A rule store that works but leaves the identified rule families scattered demonstrates mechanics, not the motivating refactor. The earlier minimum profile excluded scanner extraction (2.2), which left that gap. Acceptance is therefore split.

| Level | Question | Acceptance (all independently observed) |
|---|---|---|
| L1 Mechanism | Does the registry work as a governed store? | Authenticated immutable rules; typed evaluation; deterministic selection; refusal of invalid, stale, conflicting or non-monotone rules; historical identity (which rule set governed each decision) |
| L2 Migration | Is a real rule family faithfully moved? | Complete source-to-rule reconciliation for the family; equivalence of old and new behavior established independently, or each semantic difference explicitly authorized; predecessor behavior kept as history |

**M1 rule.** The minimum profile includes at least one real rule family that crosses both L1 and L2. Remaining families may be scheduled in M2 only if their exclusions are written down. Claim wording: M1 demonstrates the registry mechanism and one migrated family, not completion of declarative governance.

The constitutional floor stays in code; the registry carries data and registered evaluators, not the floor ([operator-decisions.md](../operator-decisions.md)).

### Selecting the M1 family (step 1.3 ADR; not selected here)

Criteria: exists in current source; bounded enough for exhaustive reconciliation; does not move the code-enforced floor; has an independent oracle that can be frozen before the candidate; needs no locked-component change, or states which one.

| Candidate | S01 evidence | Consideration |
|---|---|---|
| Scanner rule tables and claim-boundary rule bodies | Tables of 67, 76 and 77 keys in hub, verifier, ergonomics (PD-B03) | Real divergence, so reconciliation is demonstrable. It depends on [ADR-P02](adr-proposals.md#adr-p02-scanner-behavior), and the verifier is a locked component |
| Mandatory check catalogue | 369 procedural lines in `bounded.py:2239-2607`; 44 verifier check ids (PD-B04) | Largest consumer value. The floor stays code, so only the data and evaluator-reference part can move; likely the larger family |

Pricing: [estimates](estimates-m0-m1-m2.md) assumes the M1 family needs part of scanner extraction (2.2) and part of the check manifest (2.3), a conservative upper-side assumption until 1.3 picks one.

## 2. Effect surfaces: closed inventory

A coverage manifest that documents an unmediated surface does not repair it. For the minimum profile every reachable in-scope effect is mediated by the appropriate gate, or the profile prevents or excludes the path, and the assurance claim is limited to that.

### Classification

| Class | Meaning | Required evidence |
|---|---|---|
| M Mediated | In scope and reachable; must pass the canonical authorization boundary | Independent enumeration of the path and a negative showing a direct call is refused or routed through the gate |
| X Excluded | Deliberately outside the profile claim | Statement in the frozen profile; claim text names the exclusion |
| U Unsupported | Unqualified; must remain disabled in the profile | Negative showing the path is disabled under the profile configuration |
| B Bypass | A demonstrated bypass of an asserted protection boundary | A recorded execution result; a B finding blocks the affected claim until closed |

No surface is classed B today, because S01 read source and executed nothing. Read-only inspection shows a path may exist; it does not show a bypass succeeds in an operational environment. Reachability from the v0.2 path is REQUIRES INVESTIGATION for each surface.

### Seed inventory (five surfaces, read at the locked revisions)

| # | Surface | Source observation (static) | Proposed designation, for security review | Evidence required |
|---|---|---|---|---|
| 1 | Public `DurableRefundDestination.commit` and four subclasses | Accepts a direct call; the adversarial direct-call matrix does not list `OpenShellRefundDestination` or `IntentRefundDestination` | M if reachable from the profile path, else X with an unreachability negative | Reachability analysis; matrix extended to every subclass |
| 2 | `LocalDestinationExecutor.execute_snapshot` | Accepts a direct call | M if reachable, else X | As above |
| 3 | Control Plane `LocalRefundDestination.apply` | Outside the Control Plane gate by source reading | M if reachable, else X | As above |
| 4 | Legacy `execute_with_control` (`tools.py:22-102`) | Legacy path outside the canonical gate | U: disabled in the minimum profile | Negative under the profile configuration |
| 5 | OpenShell worker commit mode | Live tests are skipped unless `MOLTBOT_SAFE_OPENSHELL_CONFIG` is set, so there is no routine evidence | U: disabled; enabling needs its own qualification | Negative under the profile configuration; skipped tests are not evidence |

Designations are proposals. Where the proposal is M, closure can require a change to a locked component, which needs separate authorization and F3 requalification; where it is X or U, the profile text carries the limit.

### Where the work lands

| Step | Obligation |
|---|---|
| 1.7 | Freeze the coverage declaration schema and this inventory with a designation for each surface; part of the M0 gate |
| 3.3 | Close in-scope surfaces by mediation, or record the exclusion |
| 4.2 | Independently enumerate and observe; removal-detection negatives; every reachable in-scope effect mediated or excluded |
