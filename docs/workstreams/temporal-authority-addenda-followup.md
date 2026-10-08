# Temporal authority qualification follow-up

Base: hub main `649df22a1392af2c4fa77e4c71749c482f82649c`. Scope: the existing
`two-step-synthetic-refund/1` reference profile and its qualification predicate.
The engineering register and published profile contracts supply the requirement
mapping; unavailable addendum contents are not inferred.

## Correctness gap and repair

The trajectory previously accepted the expected number of rows plus the first
effect's identity and amount. It did not require the second row to represent the
expected installment, or either row to remain applied. Held branches also did not
qualify their first result status, and result identities were not compared to the
decisions and effects the fixture actually requested.

Qualification now requires the exact projected set of effect IDs, amounts and
applied states: the historical first installment in every case, plus the exact
second installment only in the allowed case. Each returned decision/effect ID
must match its requested operation. Continuation must use separate decisions,
claims and effect identities. Held uncertainty requires an unknown,
unacknowledged first result; cancellation-request holding requires the expected
executed first result. These predicates inspect observed local results; they do
not issue authority or repair an inconsistent destination.

Eight regression cases inject inconsistent observations after the real local
executor returns: incorrect second amount, identity or state; changed first
state; incorrect first status for cancellation holding; acknowledged unknown;
and substituted result effect/decision identities. All eight fail against the
base implementation and pass with the repair. These injected records are test
stimuli, not examples of supported executor behavior.

## Validation and release integration

On Linux with Python 3.12.14, pytest 9.1.1 and Pydantic 2.13.5:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_temporal_refund_profile.py
```

All 15 tests pass (seven existing scenarios and eight regression cases). The
fixture checks clean component checkouts against the unchanged accepted lock:

| Component | Accepted revision |
| --- | --- |
| Control Plane | `d3dadee70bd319812b207389ab1e0f6efe511916` |
| Execution Runtime | `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` |
| Action Manifest | `46c950bed37fe3812000895430bc0312d29e37ce` |
| Governed Exchange | `a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf` |
| Replay Bundle | `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa` |

The shared extension evidence gate still declares seven temporal tests on this
branch. Its owner must update the versioned batch contract and aggregate counts
before release qualification. This component PR alone does not claim the shared
gate passes. Prior evidence remains historical; no historical report is rewritten.

## Remaining boundaries

This advances local qualification for the partial TCR-1–5/TCR-8 mapping. Each
consequence still obtains its own authority. Earlier effects remain historical,
an unknown acknowledgement holds continuation without retry permission, and a
cancellation request remains distinct from acknowledged or verified cessation.
No compensation, cancellation acknowledgement, remote delivery, distributed
guarantee, general scheduler or production-readiness claim is added. The report
remains a final local observation, not a crash-resumable coordinator journal or
authenticated evidence against a hostile host. Full operation integrity remains
the accepted executor's responsibility; this repair validates the profile's
declared effect projection rather than introducing an independent replay verifier.
