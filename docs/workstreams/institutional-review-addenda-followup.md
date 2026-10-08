# Institutional review addenda follow-up

## Bounded correction

Reviewed against hub main `649df22a1392af2c4fa77e4c71749c482f82649c`,
the institutional-review profile already separates competence, authority validity
and boundary compliance; records assessment-linked proposals; requires explicit
incident dispositions for accepting reviews; and appends review history without
issuing or mutating runtime grants.

The remaining concrete defect addressed here is the trusted reviewer
configuration boundary. Validation previously iterated the input separately from
construction of the retained reviewer set. A one-shot iterable consequently lost
its identities, while a scalar string was treated as a collection. The constructor
now snapshots an iterable once, rejects scalar strings/bytes, empty collections,
non-string identities and blank identities, and retains exact valid identity
strings. Invalid configuration fails before database creation. This does not
normalize identity strings or authenticate a person.

## Qualification evidence

Focused local command, using an existing Python test environment:

```sh
/tmp/cognous-adoption-venv/bin/python -m pytest -q tests/test_institutional_review_profile.py tests/test_sqlite_recovery_profile.py
```

Result: **25 passed**. The institutional-review regressions cover invalid
configuration without store creation, empty and populated one-shot iterables,
exact reviewer membership, and accepting, rejecting and deferring reviews.
They verify unchanged prior assessment/proposal history, retained incident
dispositions, unchanged history after denied or duplicate review attempts,
reopened history, and non-authorizing review results. The existing SQLite
recovery tests also passed unchanged. This is local reference-profile evidence;
no CI, production identity or filesystem durability qualification is claimed.

## Requirement boundaries and next decision

This correction supports the explicit-review and retained-history boundaries
described in DA R5/R6 and the non-authorizing boundary in DA R8. It does not close
any complete DA requirement. DA R1/R2 still do not permit automatic expansion or
contraction, and DA R3/R4 retain independent dimensions and critical incidents.
DA R7 assessment scope remains the documented synthetic local scope; no new
runtime envelope binding is claimed.

The next deployment decision is to identify the competent reviewing institution,
its adopted review rules, authenticated reviewer identity/custody, and the
separate grant-lifecycle process. Evidence and incident-disposition references
remain unverified local references. This patch supplies none of those deployment
decisions and establishes no production readiness.
