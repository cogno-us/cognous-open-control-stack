# Optional execution record consistency contract

Contract: `optional-execution-record-consistency/1`.

This verifier derives a narrow result from retained optional-profile records and SQLite destination state. It does not use the producer's `qualified` flags as premises. It does not re-run policy, verify external truth, establish that authority was legitimate, or grant permission. Coherently fabricated records remain outside this verifier's detection claim.

```sh
python tools/verify_optional_evidence.py results/atomic-example-1
python tools/verify_optional_evidence.py results/intent-example-1
```

Run against a completed, quiescent local package. Verification reads SQLite with `mode=ro` and a transaction, including committed WAL state. Retain the destination database and its WAL sidecars together. Input digests bind the parsed record and logical effect rows, rather than claiming a standalone database-file hash captures WAL contents. These digests identify the observed inputs; they are not signatures or evidence of trustworthy custody. Snapshot consistency is per database, not across an actively changing package.

| Contract predicate | Required evidence |
| --- | --- |
| Profile and revision applicability | Supported summary/profile version, exact accepted component revisions, matching lock digest |
| Case completeness | Exact scheduled case list and directories; no missing, duplicate, unexpected, failed or interrupted cases |
| Retained population | All destination effect IDs match the scenario's expected IDs, including zero for the revoked case |
| Successful effect consistency | Applied state, digest, grant, target, amount, unit and payload agree between the retained outcome and destination |
| Replan distinction | Two distinct operation identities are visible; same intent retains one effect and distinct intents retain two |
| Scope discipline | Synthetic records cannot claim consumer-chain qualification or production readiness |

The output retains every scheduled case inspected, its consistency result, eligibility, errors and input digest. An unreadable or inconsistent case cannot qualify the package. `scheduled`, `evaluable` and `consistent` are distinct counts; a reduced denominator never turns a failed package into success. Summary-level applicability failures stop case evaluation and remain explicit errors.

An absent row establishes absence only in the inspected synthetic SQLite snapshot. It does not establish no external impact, future absence, cancellation, permission to retry, or successful task completion. This contract does not validate all authority-claim or intent-sidecar semantics; those remain covered by their profile tests. Runtime identity, OS suitability and broader environment assurance are not established by matching source hashes.

This is partial implementation of engineering-register ES01, ES02, ES04, RS08 and RS12 for these two optional profiles only. It does not close those general requirements, adopt source-paper conformance, or create a release recommendation authority.
