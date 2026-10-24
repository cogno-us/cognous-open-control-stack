# OCS MVP: supported capabilities and limitations

Status: DRAFT, non-authorizing. Built only from the sources linked here; it makes no certification, readiness or security-clearance claim and no scenario claim beyond what is already recorded. Every revision is UNQUALIFIED and the candidate is not frozen. Release, publication and production remain on HOLD. A component-local PASS is not the independent MVP verdict; Qualification owns verdicts. Sources: operator directive of 2026-10-23 section 2 (REPORTED, attachment), architect rulings #2 of 2026-10-23 (text read, VERIFIED), [mvp-definition.md](../mvp-recovery/mvp-definition.md), [architect-rulings-3-and-known-limitations.md](../mvp-recovery/architect-rulings-3-and-known-limitations.md), [BOUNDARY.md](../../tools/mvp_ingress/BOUNDARY.md).

## Intended scope (what the MVP is configured to exercise)
- Linux, CPython 3.13, single host, exact dependency set in [dependency-manifest.md](dependency-manifest.md).
- Restricted trusted-host Control Plane proposal ingress: a dedicated non-root ingress uid, a separate unprivileged client uid, one Unix socket (`0660`, dedicated group, in a separate IPC directory), one closed JSON operation, `simulate=None` fixed, operation identity derived by the Runtime.
- Route B, `AtomicLocalControlPlaneExecutor`, operation identity enabled, existing local atomic enforcement; fixed trusted synthetic authority resolver; synthetic SQLite destination only.
- Evidence reconstructed by Replay and Evidence Pack; a separate, bounded Verifier assessment; independent Qualification.
- Guarantee wording for revocation ([rulings-3](../mvp-recovery/architect-rulings-3-and-known-limitations.md) item 1): an approval revoked through the governed Runtime lifecycle cannot be reactivated under the same approval reference to authorize an effect (Runtime F3 #144, merged `c5e97e87`, UNQUALIFIED; NC1-04 remains a mandatory control).
- Ambiguous acknowledgement: `UNKNOWN` is retained, no blind retry, reuse cannot cause a second effect, reconciliation reads the destination-owned outcome ([rulings-3](../mvp-recovery/architect-rulings-3-and-known-limitations.md) item 4). Direct executor tests are component evidence only; the supported-ingress ambiguity test is a separate Qualification proposal (Qualification draft #224; not hub #224, which is this package) and is not established here.

## Explicitly not supported
- Exchange route C and GAX (excluded and not invoked; its defects stay in the broader register); the Orchestrator as a runtime dependency; Registry `/1` activation and dynamic rule evaluation; scanner harmonization; ISS V6 and Alvorada integration; general OpenTelemetry observability; external event checkpoints; additional adapters; generalized production deployment.
- Real payment, network, subprocess or production-credential effects; production IAM or institutional authority (the resolver is a fixed synthetic fixture; external agent identity is not verified).
- Complete recovery-bundle export: the ODES exporter drops `recovery_observations` for Replay bundles carrying a route B recovery report (ODES issue #140, REPORTED; post-MVP, owned by ODES). Four historical ODES failures are unchanged and not relabelled. No MVP claim implies complete recovery-export support.
- Python 3.11 and 3.12 (unqualified: [rulings-3](../mvp-recovery/architect-rulings-3-and-known-limitations.md) item 8 and the environment profile; 3.12 results are supplementary per operator directive 2026-10-23, not in a hub doc); other operating systems.

## Trusted-host boundary: what it does not cover
- The boundary is conditional on a distinct unprivileged uid that reaches only the socket, observed in one configuration. Outside it: root, the ingress uid, same-uid clients, shared-uid containers, in-process callers, anything holding `ptrace` or `DAC_OVERRIDE`, and any holder of the destination database or authority store.
- Not claimed: resistance to an authorized database owner deleting or rewriting state through `remove_authoritative_state`, raw SQL or equivalent administrative operations (owner-level removal or reprovisioning is outside the MVP; [rulings-3](../mvp-recovery/architect-rulings-3-and-known-limitations.md) section 2 register row, REPORTED, not a numbered ruling). Policy-writer and evidence-writer reversibility are recorded separately as residual trust-boundary limitations.
- Required environment preconditions: non-root ingress, dedicated `0660` socket group, `kernel.yama.ptrace_scope >= 1` (effective capabilities, dumpability and identities are verified, and Yama alone is not complete isolation). If Yama is unavailable the profile is unsupported and the boundary test is BLOCKED; no weaker substitute.
- Claim authenticity is an unkeyed hash; there is no client authentication beyond socket permissions, no channel confidentiality and limited denial-of-service protection; the `simulate` check is a static AST scan with stated blind spots; same-host custody has no external anchor.
- A request row left `inflight` is permanently refused until the owner reconciles it out of band.

## Verifier
- Overall result on the assessed route is `ABSTAIN` (exit 3), not ACCEPT. The V4 check `v4.ledger.rows-agree-with-attempts` abstains because the route B run record does not carry the attempt layer; V4 abstention is preserved and the Verifier is not modified to force ACCEPT. Do not say "all other V4 checks pass". The reported 27 of 28 confirmed came from an assessment that used a USD 50 fixture, a harness-only `lost_ack` and a pre-merge commit, so it is superseded for claim use until regenerated at the exact tuple.
- The Verifier does not independently establish the destination effect outcome; an exit 0 or 3 does not attest that an effect committed or was refused.

## Not yet established (UNVERIFIED)
- Replay, Evidence Pack and ODES reconstruction of the route B chain through the live ingress on the merged tuple; any independent acceptance; the corrected NC4-03 provenance predicate (proposals Qualification #222, #225); the actual-host environment capture.
