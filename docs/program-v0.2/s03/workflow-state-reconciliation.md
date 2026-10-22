# Workflow state reconciliation (step 1.5 addendum)

**Proposed, documentation only.** Closes the item [identity-and-lifecycle.md](identity-and-lifecycle.md) left open: reconcile the 15-state list of V2-P1-03 with the Orchestrator's reserved list. No state machine is added, no locked component is changed, no decision is recorded, and release and production remain on HOLD.

Static reading. Orchestrator `a745e131`, `orchestration/state-transitions/README.md`: "Reserved for explicitly named orchestration statuses (proposed, awaiting_authority, authorized, dispatched, observed, unresolved, reconciled) and transition evidence. Not an alternate Control Plane." Orchestrator `ARCHITECTURE.md` and `CONTRACTS.md` set the boundaries used below. The directory holds a README only; no implementation exists (S01).

## 1. The two lists

| Source | States |
|---|---|
| V2-P1-03 (15) | PROPOSED, VALIDATING, WAITING_AUTHORITY, READY, DISPATCHING, RUNNING, RECONCILING, COMPLETED, HELD, DENIED, FAILED, CANCEL_REQUESTED, CANCELLED, UNKNOWN, SUSPENDED |
| Orchestrator reserved (7) | proposed, awaiting_authority, authorized, dispatched, observed, unresolved, reconciled |

## 2. Reconciliation

The test for each name: does it describe the orchestrator's own coordination, or does it restate a record that another component owns? A workflow must not set or alias a state another component owns (a decision result, an attempt status, an observation, an effect verification).

| Name (either list) | Closest existing vocabulary | Collision risk | Proposed treatment |
|---|---|---|---|
| proposed / PROPOSED | The proposal record before any decision | None | `workflow.proposed` (orchestrator-owned) |
| awaiting_authority / WAITING_AUTHORITY | No component state; waiting for a decision to exist | None | `workflow.awaiting_authority` |
| authorized | Control Plane decision result `authorized` | Aliases a decision outcome the orchestrator does not own | Not a workflow state. Record a reference to the decision (`decision_id`); the workflow may read it, never set it |
| DENIED, HELD / `deny`, `hold` | Control Plane decision results | Alias | Not workflow states. References to the decision record |
| dispatched / DISPATCHING | No state exists (S01 PD-L01) | Tense differs between the lists | `workflow.dispatched`: the orchestrator handed a proposal to the gate. It does not mean an attempt exists |
| RUNNING | Attempt `attempted` in the Control Plane and ODES executor lifecycle | Alias | Not a workflow state; read the attempt record |
| observed | `observation.*` states (`applied`, `partial`, `absent`, `unknown`) | Alias; an observation is independent evidence, not a workflow claim | Not a workflow state; reference the observation. A workflow never writes an observation |
| reconciled / RECONCILING | ODES executor status `reconciled`; attempt `unknown` leaves only through reconciliation | Alias with `attempt.reconciled` | `workflow.reconciling` for the orchestrator's act of inspecting; the result is the attempt or observation record, not a workflow-set status |
| unresolved / UNKNOWN | Six distinct `unknown` enumerations | Collision with any of them | `workflow.unresolved` only; never named `unknown` (see [identity-and-lifecycle.md](identity-and-lifecycle.md) section 5) |
| FAILED | Attempt `failed`; also a workflow failure | Alias if used for an effect | `workflow.failed` only for orchestration failure (task not run, timeout waiting). An effect failure is the attempt record |
| COMPLETED | No state; `verified` has none either | Would imply an effect verification | `workflow.completed` means all workflow tasks finished and records references; it never states that an effect was verified |
| VALIDATING, READY | Internal to coordination | None | `workflow.validating`, `workflow.ready` if needed by the coordinator |
| CANCEL_REQUESTED, CANCELLED | No state exists (PD-L05); no terminal cancelled in locked source | Cancelling is not reversal | `workflow.cancel_requested`, `workflow.cancelled`: coordination only; cancellation never reverses a committed effect and compensation needs new authority |
| SUSPENDED | None | None | `workflow.suspended` |

## 3. Result

- Workflow vocabulary is small and orchestrator-owned: `proposed`, `validating`, `awaiting_authority`, `ready`, `dispatched`, `reconciling`, `unresolved`, `completed`, `failed`, `cancel_requested`, `cancelled`, `suspended`, each written `workflow.<name>`.
- The two lists name 17 distinct concepts (22 names; five pairs describe the same state). Five of the 17 are not workflow states because they restate records another component owns: `authorized`, `DENIED`, `HELD`, `RUNNING` and `observed`. The workflow carries references to those records. Three more (`failed`, `completed`, `reconciling`) stay as workflow states only in their orchestration meaning and never as a claim about an effect. That leaves 12 workflow states.
- No workflow state may be an input to an authorization decision, a grant, a rule selection or a verdict (SP-03).
- The proposal is a vocabulary, not a new machine: transition rules are the Orchestrator's own and are added at step 3.2 under the existing "no alternate Control Plane" rule.

## 4. Remaining checks (not done here)

Whether the transition evidence the reserved list mentions maps to existing ODES journal records, and which identifiers each workflow state record carries, is for step 3.2 once the identity decisions at the M0 gate settle.
