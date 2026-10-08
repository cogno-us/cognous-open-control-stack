# W7 bounded V1 integration baseline

Status: **W7-P1 baseline only; release pins unchanged**.

## Frozen start

- Hub main: `6ad8f6a409d3140aa65af19d5c850dd8e58f8a7d`.
- W7 branch started at the same SHA.
- Contracts C1-C8 are frozen at W0.
- `component-lock.json` remains the accepted `merged-producers-v1` lock and MUST NOT advance until the selected exact producer/consumer combination is qualified.
- W1-W6 were inspected at W7 start and were PREPARED only; no implementation PRs were found.

## Selected revisions at W7 start

| Component | Selected revision | Selected interface/profile |
|---|---|---|
| Action Manifest | `46c950bed37fe3812000895430bc0312d29e37ce` | Manifest 1.1 |
| Control Plane | `d3dadee70bd319812b207389ab1e0f6efe511916` | bounded authorization/effect 0.1 |
| Execution Runtime | `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` | Execution Envelope 0.2.0; producer 2.0.0 |
| Replay Bundle | `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa` | Reconstruction Bundle 0.2.0 |
| Governance Evidence Pack | `b4baccd823d2a73be276c1de745b19cf7c56a0d6` | imported schema 0.2.0; transformation 0.3.2 |
| Governed Exchange | `a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf` | merged-producers-v1 compatibility |
| Constitutional Authority | `fb3d97938969a89e149e8ff8db2756091d1233fc` | Authority Context 0.1.0 |
| Evidence Attestation | `5b5077dafde232a7801cb425c4efddcffb468723` | verification contract v1 |
| Evidence Registry | `d5e45d275cb301d9684b543e93b05997991d1cf2` | local blockchain reference 0.1.0 |

These are the accepted starting pins, not the final bounded V1 release pins.

## Claim-to-test disposition

The existing `scenarios/acceptance-matrix.json` already provides substantial positive and negative coverage for: exact effect binding, authority expiry/revocation, payload/adapter/identity substitution, required evidence freshness, lost acknowledgement, restart, partial/unknown observation, no-blind-retry recovery, replay integrity, Evidence Pack provenance and historical producer compatibility.

The W7 delta is intentionally small. New release cases are needed only where W0 explicitly left semantic assertions unexecuted or where W1/W2 create new producer generations:

1. **Tenant authority:** cross-tenant substitution, missing tenant on the tenant-aware generation, and wrong tenant across grant/approval/current-policy joins.
2. **Durable refusal:** evaluation-error and authority-refusal records retained through the actual outer failure callers.
3. **Bounded stop:** request, acknowledgement, dispatch closure, observed quiescence and destination reconciliation kept distinct; committed effects are never rewritten as undone.
4. **Consumer compatibility:** W3 must import accepted tenant/refusal/stop records without fabricating missing lineage or upgrading assurance.

All other final release cases should reuse existing accepted tests and gates unless an accepted producer change invalidates their applicability.

## Dependency ledger

| Stream | Start state | Release dependency | W7 disposition |
|---|---|---|---|
| W1 | PREPARED | accepted tenant-aware producer generation and exact bytes | CORE BLOCKER |
| W2 | PREPARED | accepted refusal/stop/recovery producer records | CORE BLOCKER |
| W3 | PREPARED | accepted consumer mapping for W1/W2 generations | CORE BLOCKER |
| W4 | PREPARED | optional OpenAPPA qualification | OPTIONAL; never automatic core blocker |
| W5 | PREPARED | optional Microsoft AGT qualification | OPTIONAL; never automatic core blocker |
| W6 | PREPARED | optional OpenShell live qualification | OPTIONAL; BLOCKED is valid if no authorized live environment |

## Final qualification rule

After W1-W3 are accepted, W7 will select their exact accepted SHAs, qualify the material combination at those revisions, then and only then update `component-lock.json`. The final core run must exercise valid refund, tenant mismatch, refusal, stop, observation/recovery, replay and evidence lineage at the selected pins.

No release statement may claim universal exactly-once behavior, general rollback, fleet-wide stop, enterprise IAM completeness, prompt-injection resistance or live confinement without corresponding evidence.
