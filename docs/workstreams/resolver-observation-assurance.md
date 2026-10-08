# RA-01: synthetic authority observation assurance

Base: `649df22a1392af2c4fa77e4c71749c482f82649c`.
Contract: `synthetic-authority-observation/1`.
Status: bounded reference checker, not a production authority resolver.

The checker makes the trust boundary around one authority object explicit. Trusted host configuration supplies source identities, profile versions, institution/domain/object/scope bindings, synthetic HMAC keys, revision floors, maximum ages, clock tolerance and the adapter function. These inputs must never be taken from the incoming agent request. Each adapter response is checked against its configured source, exact object binding, authentication fixture, revision floor and time limits. Source errors hold as unknown; no cache or continuity fallback is provided.

This is an additional isolated reference profile. It is not wired into RuntimeDecision, the default reference release or any execution adapter. It issues no grants and performs no effects. `CURRENT_VALID` means only that this particular source observation passed the local configured checks. It cannot establish full actor, mandate, delegation, policy, approval or effect authority. Every result includes `authorizes_execution: false` and `production_qualified: false`.

## Evidence and classifications

The report retains detached copies of authenticated observations, each consumed profile's public time/revision constraints, failures and a digest of the report. Unauthenticated bodies are not retained. The digest is a content commitment, not a signature, trusted timestamp or bearer permission. The caller is responsible for durable evidence storage; outputs are ordinary mutable Python dictionaries. A previously returned report is not altered when a later call sees revocation.

Observations bind a source identity and profile version to institution, domain, object class, object ID and exact scope digest. `facts_digest` commits to the source's semantic authority facts; adapters must use an agreed fact representation across sources. The checker cannot verify those facts' truth or completeness. Source-local revisions may differ, but divergent current fact digests or classifications produce `CONFLICT`. Both observations are preserved; there is no majority vote. `HISTORICAL_VALID`, `REVOKED`, `SUSPENDED`, `SUPERSEDED`, `UNKNOWN`, `STALE`, `UNAUTHENTICATED` and `OUT_OF_SCOPE` hold. Contradictory classifications also hold as conflict.

Time uses trusted host numeric seconds. The valid-until boundary is exclusive; the configured age boundary is inclusive. Future effective times hold even within observation-clock tolerance. The revision floor is trusted configuration, not a persisted high-water mark. An earlier response at or above that floor within the freshness window may still pass. Replay resistance, revocation latency and check-to-commit atomicity are **not** established by this fixture.

## Qualification

```sh
python tools/resolver_assurance_qualification.py > resolver-run.json
```

Twenty standard-library unit tests exercise accepted observations, historical/current separation, exact bindings, source/profile pins, freshness/expiry/future times, revision floors, authentication tampering, request self-assertion, outages, conflict preservation and prior-report preservation. The dedicated Linux workflow repeats the bounded suite twice on Python 3.11 and 3.12, each process limited to 30 seconds, with a three-minute job limit. Each machine-readable result records source revision, component-lock digest, Python/platform and exact test/failure/error/skip counts. A skipped test cannot qualify. No dependency installation is needed. This profile does not change the existing seven-batch evidence population or accepted component pins.

This is partial coverage of the resolver addendum's P0/P1 boundary requirements and scenarios A3, A8–A11, A16 and A18. It does not complete any end-to-end A1–A18 campaign. In particular, the tests are not evidence for a real past effect, runtime authority revalidation or production source authentication.

## Remaining requirements and threats

- A production adapter must authenticate actual institution-owned endpoints and responses, protect credentials, qualify clocks and measure propagation. Synthetic shared-key HMAC does not establish institutional legitimacy or independence. Any holder of the fixture key can forge a response. Resolver/source/key compromise remains unqualified; no A15 resistance is claimed.
- Persisted anti-rollback state, authorized trust-root rotation, real source precedence, cache/continuity semantics, delegation ancestry and explicit succession require separate contracts and qualifications. No automatic succession or key rollover occurs here.
- The Control Plane must bind a future AuthorityResolutionCommitment to each decision and exact effect, then re-resolve before execution. This checker does not implement that integration or the source-to-external-commit race.
- Replay, evidence packages and registry outputs remain evidence. They must not turn a retained observation or checker result into renewed authority.

Only new checker, test, qualification-runner, workflow and checkpoint files are introduced. Concurrent context, temporal, review, recovery and deployment-review changes remain independent.
