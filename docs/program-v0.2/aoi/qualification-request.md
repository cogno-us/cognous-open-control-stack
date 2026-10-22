# Qualification request for AOI (input to Qualification; not builder verdicts)

**A request, not a contract.** This file proposes independent acceptance objectives that mirror the addendum's Q01 to Q07. It is engineering's input. Qualification decides on its own whether to accept, reject or reshape them, freezes any expectation itself, and owns every oracle and verdict. The builder does not amend the Qualification controller (#218), its expectations or its oracles, and this record is not posted there. Release and production remain on HOLD. No case below has been run; nothing here claims a result.

Frozen prerequisites that already bind this request are in [../s03/minimum-profile-and-coverage.md](../s03/minimum-profile-and-coverage.md) section 5: expectations are written before any candidate exists; the freeze-boundary assessment and the Qualification-owned items stay Qualification's.

## Proposed cases (acceptance objectives)

| Case | Independent acceptance objective | Envelope fields exercised (C01) | Addendum steps |
|---|---|---|---|
| Q01 Identity and delegation | Same-name agents, substituted instances, expired or absent credentials, parent-child scope. Distinguish asserted from independently verified identity | principal, agent identity reference and attestation state, instance, delegation parent | 1.5, 4.4 |
| Q02 Authority transition | Epoch, grant expiry, revocation or approval withdrawal, in-flight stale authority. Preserve the bounded residual race and the exact source | grant id and revision, rule-set digest and epoch, sampled authority time, recheck status | 3.5, 4.4 |
| Q03 Effect correlation | Attempt, refusal, readback, committed effect, lost acknowledgement and unknown are distinguishable; no inference from missing telemetry to no effect | attempt, effect, observation, idempotency references | 3.5, 4.4 |
| Q04 Human intervention | Mandatory and discretionary triggers, reviewer scope, agent recommendation, evidence, response; an invalid approval claim is refused | the five review fields | 4.4 |
| Q05 Governed memory and state | Only when an ISS-owned accepted export exists: source, mutation, before and after commitment, reliance and negative history reconstructable. Independently gated, with its own ISS-side work | ISS reference only | out of M1; deferred |
| Q06 Integrity and outage | Dropped export, tampering, custody failure, clock mismatch and version mismatch detectable and classified, without inventing causal order | completeness states, digests, clock provenance | 4.4 |
| Q07 Interoperability and economy | OTel mapping round-trip within a declared field set; selective disclosure, storage, latency and privacy trade-offs; a span is not an authority record | declared exported field set | 4.4, 4.5 |

## Notes for Qualification

- Cases Q05 and Q07 depend on things that do not exist in the minimum profile (an ISS export; an OTel projection). Proposed: Qualification marks them deferred rather than specifying proof against nothing.
- Qualification's usual practice of recording the independent result in its own records applies; the handoff envelope carries no Qualification result and no verdict ([1.4](../s02/contracts/1.4-evidence-handoff.md) section 4).
- The reporting split in step 4.5 (mandatory verdict, raw suite health, original-scope coverage) is unchanged. Observability coverage is reported as a separate line and does not raise the mandatory verdict.
- If Qualification rejects a case, the proposed engineering response is to narrow the profile claim, not to weaken the criterion.
