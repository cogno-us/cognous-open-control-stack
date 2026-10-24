# Architect rulings, fourth record (2026-10-23, addendum rulings 1-8)

Status: non-authorizing record. Release, publication and production remain on HOLD. Nothing here is a Qualification verdict, an independent acceptance, a security clearance, a certification or a production-readiness claim. The builder cannot self-certify. Qualification owns oracles and verdicts.

This record sits next to [architect-rulings-3-and-known-limitations.md](architect-rulings-3-and-known-limitations.md) (merged via #220). It records the architect's rulings #2 of 2026-10-23 as supplied to the author. It adds no claims beyond those rulings and the PR states listed in section 9.

Related: [architect-rulings.md](architect-rulings.md), [architect-rulings-2.md](architect-rulings-2.md), [implementation-status-2026-10-23.md](implementation-status-2026-10-23.md).

## 1. NC4-03 v4 predicate

- NC4-03 v4 is not adopted as written.
- Keep AST-normalized pins for the three reviewed sites. Each pin records the source revision, the AST digest, the trusted input origin and the protected destination.
- Restrict or remove the generic comprehension exception.
- Qualification independently approves the corrected predicate before freeze.
- Target: Oct 25.

## 2. Residual R1: origin rule

- Define an origin rule for `claim_id`, `grant_id`, `grant_revision`, `effective_max_effects`, `authority_context_id` and `requested_permissions`.
- A negative mutation in which a client-supplied `claim_id` reaches execution must be rejected.
- No general taint framework.
- Target: Oct 25-26.

## 3. Runtime F3 #144

- Runtime F3 #144 is approved, including terminal `revoked -> unknown`.
- Guarantee, as scoped: "An approval revoked through the governed Runtime lifecycle cannot be reactivated under the same approval reference to authorize an effect".
- No claim is made of resistance to an authorized DB owner using `remove_authoritative_state`, raw SQL or admin operations.
- Policy-writer and evidence-writer reversibility are recorded separately.
- No one-time migration is needed.
- Status: #144 merged into Runtime `main` as `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f` on 2026-10-23 (head `ee1ff55c`). Cite as merged, not as qualified.

## 4. Environment profile

- Socket mode 0660 with a dedicated group containing only the ingress and the designated client identities.
- The socket lives in a separate IPC directory the client can traverse, not in the ingress-owned 0700 state directory. The parent directory prevents replacement.
- Verify effective permissions, group membership and peer credentials.
- `kernel.yama.ptrace_scope >= 1` is required. If Yama is absent the result is UNSUPPORTED/BLOCKED; there is no weaker substitute.
- A non-root, dedicated-UID ingress is mandatory, with no unnecessary capabilities.
- Capture the actual identities.
- Hub PR #219 update and actual-host capture by Oct 26.

## 5. Lost-ack

- One supported-ingress owner-side fault-injection test is required, covering: (1) a supported proposal reaches the execution boundary; (2) the ack is unavailable after the effect attempt; (3) UNKNOWN is retained; (4) reuse cannot cause a second effect; (5) reconciliation establishes the destination-owned outcome where possible.
- Fault injection lives in the trusted qualification harness, not in the request schema.
- Distinguish executor-level evidence from supported-ingress evidence.
- Target: Oct 27-29.

## 6. Qualification governance

- Qualification independently owns, reviews, freezes and anchors the mandatory battery, the applicability mapping, the gate expectations, the exact tuple and the supported environment.
- New files must be added to the Qualification-controlled commitment.
- Python 3.13 is required; Python 3.12 is supplementary only.
- Target freeze: Oct 27.

## 7. Post-MVP

- Route C/Exchange: prefer a new versioned P2 profile if committed behavior or profile identity changes.
- ODES `recovery_observations` remains a documented post-MVP defect.
- Zero MVP-critical work.

## 8. Schedule and cut order

| Window | Item |
|---|---|
| Oct 24-25 | Rulings 1 (target Oct 25) and 2 (target Oct 25-26) |
| Oct 26-27 | Ruling 4 (hub #219 update and host capture by Oct 26); ruling 6 freeze (Oct 27) |
| Oct 28-29 | Ruling 5 (target Oct 27-29) |
| Oct 30 | As set by the architect's rulings |
| Oct 31 | Engineering target |

Oct 31 is an engineering target. A failed mandatory control remains a failure. The cut order is as set in the architect's rulings and is not restated or altered here.

## 9. Implementation state as of this PR

Checked with the GitHub API on 2026-10-24.

- Runtime #144: merged, `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f`, head `ee1ff55c`. Merged, not qualified.
- Hub #219: open (not merged), current head `b35957d0`. A builder-side independent review approval was reported at `0e2b52a0`; that commit is in the PR, but it is not the current head, and the author could not confirm the review through the GitHub reviews API.
- Qualification #222, #223 and #224: open drafts, Qualification-owned, with builder-side reviews reported. They are not frozen and not accepted.
