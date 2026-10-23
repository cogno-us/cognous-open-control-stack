# MVP claim text: Verifier section (DRAFT)

Status: DRAFT, non-authorizing. Release, publication and production stay on HOLD; no production use or effect is claimed. This is not a Qualification verdict, a security clearance, a certification or a production-readiness claim. Qualification owns the oracle and every verdict; nothing here is accepted until Qualification says so.
Basis: architect ruling 3 (narrow Verifier claims; evidence for exit criteria 2, 4, 5 and 7 comes from destination-owned observations, Replay and Evidence Pack, and Qualification, not from the Verifier).

## 1. Tuple and fixtures cited

| Item | Pin |
|---|---|
| Control Plane | `7a4bcd40b3b49e61ff3c294dcca53b52f460b22c` |
| Runtime | `ec728da6dc301a664b331ac8986afd6e850a1273` |
| Action Manifest | `fa170815` |
| Verifier (locked, unmodified) | `c0b8ba1f55b75db787a320f3de0f79342c6f6826` |
| Ingress | hub `tools/mvp_ingress` at hub main `7b38ae62` (identical to the `43c526eb` ingress tree; `simulate=None` fixed in `core.py`) |

Fixtures are the matched `$10` USD synthetic refund (request `case-1`, `customer-001`, reason `duplicate`). They replace the earlier fixtures, which used a `$50` amount and the harness-only `simulate="lost_ack"`; those earlier records are not cited by this text.

How each fixture was produced. The executed, held and refused-at-effect records came from `IngressCore.handle` called in process, not through the Unix socket. The lost-ack record is harness-only (`simulate=lost_ack`, called directly on the executor, not through the ingress). Raw observations are retained only locally at `/tmp/wk/o31/R/out/<scenario>/observed.json`; they are not part of this repository and are not published with this draft.

| Scenario | Production path | Ingress response / executor observation |
|---|---|---|
| executed | `IngressCore.handle` (the frozen ingress core, in process) | `executed` / `EXECUTED` |
| held | `IngressCore.handle`, a proposal the synthetic approval does not bind (`customer-002`) | `held` / `DECISION_HELD`; no claim, no effect |
| refused-at-effect | `IngressCore.handle` unchanged, plus an owner-side hook that revokes the destination grant after real claim provisioning | `refused` / `EXECUTION_DENIED`; claim left `issued` |
| lost-ack | HARNESS-ONLY, not through the ingress: `executor.execute(simulate="lost_ack")` then `reconcile` | execute `unknown`, not acknowledged, observed_state `applied`; reconcile `observed`; claim `consumed` |

Limit on provenance: a lost acknowledgement is unreachable through the ingress by design (`simulate=None` is fixed), so the lost-ack record is not an ingress-path record. The refused-at-effect record needs an owner-side authority write that no client can issue. Neither is evidence that a client can reach those states.

## 2. What the Verifier run observed

Pinned Verifier CLI, real exit codes, fixed `--generated-at`, both ledger variants (base; with operation digest and operations) gave identical results.

| Scenario | Exit | Disposition | Tally (of checks) |
|---|---|---|---|
| executed | 3 | ABSTAIN | 27 confirmed, 1 could-not-check, 0 refuted (of 28) |
| lost-ack (harness-only) | 3 | ABSTAIN | 27 confirmed, 1 could-not-check, 0 refuted (of 28) |
| refused-at-effect | 0 | ACCEPT | 23 confirmed, 0 could-not-check, 0 refuted (of 23) |
| held | 0 | ACCEPT | 20 confirmed, 0 could-not-check, 0 refuted (of 20) |

The one abstention in both exit 3 runs is `v4.ledger.rows-agree-with-attempts`, reason `attempt_rows_not_in_record`. The route does not emit the attempt layer into the Control Plane run record, so the Verifier has nothing to compare ledger rows against.

## 3. Claim text

> For the matched $10 synthetic refund on the executed route at the pinned tuple, the Verifier evaluated 28 checks: 27 confirmed, 1 abstained, 0 refuted. The overall result is exit 3, ABSTAIN. ABSTAIN is not a PASS and is not converted into one.
>
> Of the seven V4 ledger checks, 4 were confirmed, 1 abstained (`v4.ledger.rows-agree-with-attempts`, attempt rows not in the record) and 2 were not applicable (`v4.ledger.acknowledged-attempts-have-rows`, `v4.ledger.observations-agree`; zero items). Complete V4 ledger conformance is not claimed.
>
> The Verifier does not establish the destination effect outcome. It checks structure, identity and agreement between supplied records. Its exit 0 or 3 does not attest that an effect committed or was refused, and its exit 0 on the refused and held records attests nothing about the refusal: for those runs the V4 checks had no items to examine. The ledger is a supplied snapshot, trusted by deployment.

Wording that must not be used: "all other V4 checks pass" (two V4 checks were not applicable, not passed); "the Verifier accepted the run"; "the Verifier confirmed the effect"; any statement that ABSTAIN equals PASS.

The Verifier's own `does_not_prove` list (relative to the pinned controller, no semantic-quality claim, ledger completeness not established, self-consistent forgery not detected, not an attestation, no V1 scope claim) applies in full.

## 4. Exit criteria 2, 4, 5, 7: evidence source (not the Verifier)

Criteria as numbered in `docs/mvp-recovery/implementation-status-2026-10-23.md`, Q5(d).

| Exit criterion | Evidence source | Where it comes from |
|---|---|---|
| 2: grant changes and duplicate protection | Destination-owned observations (effect, claim and operation rows read through an independent read-only SQLite connection; grant status in the authority store) and Qualification mvp-chain rows | NC1-01..05 (revocation, terminal), NC3-01..03 (duplicate effect). Fixture observation here: refused-at-effect left the claim `issued` with no effect row. |
| 4: UNKNOWN and no blind retry | Destination-owned observations (execute `unknown`, attempt and claim rows, effect count after retry), Replay import of the unknown outcome, ingress ledger (no re-execution of a reserved `request_id`) and Qualification rows | NC2-01..05, NC6-02. The Verifier cannot see this: its run record is the same shape for executed, lost-ack and refused-at-effect. |
| 5: Replay and Evidence Pack reconstruction | Replay import and Evidence Pack `validate_evidence_pack`, as run and judged by Qualification | CHAIN-04..06, NC2-05, NC5-01..03, NC5-05, NC6-01, NC6-04. Replay and Pack are separate from the Verifier path and are not downstream of it. |
| 7: negative controls on the exact candidate | Qualification (suite `mvp-chain`, exact tuple, six controls, verdict engine and frozen expectations) | NC1..NC6 plus ENV-01 (pin and pristine-checkout check). NC4-01..02 are execution observations; NC4-03 is a source-level assertion and is labelled so. KL-01 is a recorded limitation. |

A passing reconstruction path does not erase a separate Verifier failure, and a Verifier ABSTAIN does not weaken or substitute for these sources.

## 5. Governance statements to carry unchanged

- Non-authorizing. Release, publication and production remain on HOLD until independent Qualification and explicit operator approval.
- Destination is synthetic SQLite only; the resolver is a fixed synthetic trusted source, not institutional authentication.
- Trusted-host boundary: no claim of isolation from code running with the ingress uid or root; not a general-purpose sandbox.
- No claim of security clearance, certification or production readiness.
