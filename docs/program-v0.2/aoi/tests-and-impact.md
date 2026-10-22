# AOI test inventory and privacy and integrity impact (proposed)

**Proposed, documentation only.** These are candidate developer-test cases for a later producer implementation, not independent acceptance cases. Independent cases, expectations and verdicts are Qualification's ([qualification-request.md](qualification-request.md)); a producer-written test never qualifies itself. Nothing here runs or authorizes anything. Release and production remain on HOLD.

## 1. Candidate developer tests for the envelope (steps 3.4, 3.5; contingent on M0)

Positive:

| Id | Case | Expected |
|---|---|---|
| P1 | Envelope for one refund decision, attempt and observation built from existing records only | Every referenced record resolves; no field outside the C01 vocabulary |
| P2 | Field with no source (for example agent attestation) | State UNSUPPORTED, not omitted and not defaulted |
| P3 | Two attempt namespaces for one dispatch | Both references present; join named |
| P4 | Renewed grant (revision 2) for the same `operation_id` | Two effects, one operation; both references present |
| P5 | Reconciliation after `attempt.unknown` | New envelope references the reconciliation record; original unchanged |
| P6 | Envelope with the profile identifier of C01 | Digest stable under the step 1.3 canonical profile |

Negative:

| Id | Case | Expected refusal or outcome |
|---|---|---|
| N1 | Envelope with a verdict, pin or expectation member | Refused as an unknown member |
| N2 | Referenced decision id or digest not found | Refused; reference reported invalid |
| N3 | Digest altered after issue | Refused at intake |
| N4 | `unknown` presented as success, absence or retry | Refused (F-06) |
| N5 | Missing telemetry read as no effect | Outcome is UNOBSERVED, not absence |
| N6 | Asserted identity recorded as verified | Refused; stays "asserted" |
| N7 | Superseded envelope presented as current | Reported as superseded |
| N8 | Trace or span reference present but exporter dropped it | Authoritative record unchanged; classification of the drop recorded |
| N9 | Tuple differs from the supplied lock | Refused (as 1.4) |
| N10 | Hidden reasoning or confidence field supplied | Refused as an unknown member |

## 2. Privacy impact

| Concern | Impact | Proposed control (design level) |
|---|---|---|
| Identity references (principal, agent, session) carried in a second place | Widens exposure of identifiers | Envelope holds references, not profile data; redaction and retention declared per field in C02 |
| Human review records (reviewer identity, evidence shown) | Personal data about the reviewer; may include data shown to them | Include only where the profile has an approval-bearing path; store references to the evidence, not the evidence |
| OTel export of the envelope | Moves fields to an external collector | Selective disclosure: export only declared fields; no hidden reasoning or confidence signal exported; export is optional |
| Synthetic scope | v0.2 uses synthetic SQLite and no real credentials | No real personal data in the default path (repository rule); this is a limit, not a guarantee for later profiles |

Redaction and retention decisions are REQUIRES DECISION (M0 packet row 18); this record states no policy.

## 3. Integrity impact

| Concern | Impact | Proposed control |
|---|---|---|
| A correlation record read as authority | Could be mistaken for a grant or verdict | Fixed `authority_effect: none`; no verdict member; F-02, F-07, F-09 |
| Digest mistaken for authorization | A digest proves byte identity only | Documented in C01 section 6; issuer authorization stays with the deciding component |
| Cross-store inconsistency | Stores can disagree; no atomic transaction exists | Join by reference; mismatch is classified, not repaired; no atomicity claim |
| Clock disagreement | Order cannot be inferred | Per-domain clock provenance; order uncertainty stated |
| Exporter failure | Could lose evidence if export were the custody path | Custody stays in the existing stores; export failure never alters them |
| New field in a committed record | Could change historical digests | Opt-in or new profile only; old records re-verify byte-identically (1.2 section 4) |
| Added attack surface in the handoff | New fields to forge | Intake refuses unknown members and digest mismatch |

## 4. Not covered

Performance, storage and latency measurements (Q07 asks for the trade-off analysis; none exists), the OTel round-trip, and any independent verification are not provided here.
