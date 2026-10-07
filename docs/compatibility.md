# Compatibility and interface-gap matrix

Evidence states: **implemented**, **tested locally**, **tested in pinned CI**, **live-qualified**, **unexecuted**, **blocked**, **deferred**.

| Producer / consumer | Selected contract | Accepted selected pin | Integration rule |
|---|---|---|---|
| Action Manifest -> Control Plane | Manifest 1.1 | `46c950b...` -> `248d899...` | exact manifest/payload/adapter/target binding |
| Constitutional authority -> Control Plane | Authority Context 0.1.0 | `fb3d979...` | authority comes from trusted resolver, never request content |
| Control Plane -> Moltbot Safe | bounded effect + Execution Envelope 0.2.0 | `248d899...` + `177354e...` | effect-time revalidation before constrained destination; repaired same-host record transactions qualified separately |
| Moltbot Safe producer -> Replay | executor producer profile 2.0.0 + Reconstruction Bundle 0.2.0 | `177354e...` -> `043830b...` | preserves frozen operation, effect, observation and separate attempt namespaces |
| Replay + Manifest -> Evidence Pack | persistence transformation 0.3.1; previous producer-2.0.0 transformation 0.3.0; historical transformation 0.2.6; pack schema 0.2.0 | selected `de6b9e0...` | 0.3.1 is mandatory under selected Replay `043830b...` + Control Plane `248d899...`; prior suites remain isolated |
| Replay + Manifest -> ODES | ODES implementation profile 0.2; pder-v0.1 unchanged | `0486b64...` | package integrity, authentication and current authority remain separate |
| GAX/IMX exchange | refund exchange 0.1.0 + retained artifacts 1.1.0 | `9984d90...` | accepted merge; reviewed source `ee2dde3...`, PR #8; evidence-only recovery remains non-authorizing |
| BitRep -> evidence scenario | verification contract v1 | `5b5077d...` | valid signature establishes attributable verification only |
| Index local chain -> evidence scenario | local blockchain reference | `d5e45d2...` | chain inclusion establishes inclusion only, never action permission |

## Resolved interface debt

1. **Versioned Moltbot producer compatibility — resolved for the accepted dependency path.** Moltbot `177354e...`, Replay `043830b...`, ODES `0486b64...`, Evidence Pack `de6b9e0...` and Alvorada `9984d90...` share the accepted executor producer profile `urn:cognous:profiles:moltbot-safe-executor-producer` / `2.0.0`. Legacy unversioned Moltbot artifacts remain revision-pinned in the consumer path and are not relabeled.
2. **GAX public executor entrypoint — resolved.** The supported Alvorada runtime imports public Moltbot producer/executor modules and requires caller-supplied resolver and execution policy. The hub qualifies the supported path with upstream test directories unavailable.
3. **Original Replay artifact retention — resolved.** The versioned Alvorada retained-artifact interface exposes the original Reconstruction Bundle, ODES package/recipient validation and successor packet with identities and content commitments. Duplicate/redelivery returns the retained original when available. When an original was never retained after a post-effect interruption, regenerated evidence has distinct derivative lineage and does not trigger a replacement effect.

For separately accepted but unselected component revisions, see the
[support/adoption table](release-status.md#mechanism-qualification-and-adoption).
Recovery terminology is explained in [recovery semantics](recovery-semantics.md).

## Remaining bounded gaps

1. **Alvorada PR #2 remains deferred.** It is unaccepted and excluded from the reference integration.
2. **Live OpenShell execution/confinement remains unqualified.** Separately accepted packaged-image tests and a blocked readiness package do not establish live enforcement. Mock tests do not establish live sandbox/network/OS confinement.
3. **Production institutional authority is out of scope.** The public integration uses synthetic/bounded resolver fixtures; it does not establish authenticated institutional resolver deployment, credential custody or production revocation propagation.
4. **Fleet orchestration and distributed budgets remain out of scope.**

## Batch 4C observation boundary

The lock selects accepted Alvorada/GAX persistence-compatible merge
`9984d9011568ccdf3d562fa9760ad41368947b34`, reviewed source
`ee2dde3062468b07723d92a040bc1f0bafafd50e`, merged PR #8.
The previous `c52f9f0...` acceptance and earlier acceptance remain historical metadata.

Explicit ObservationPolicy and timezone-aware evaluation time govern observation
acceptance. A rejected or null observation is retained separately from attempt and
acknowledgement history. `observed_absent` is point-in-time evidence and never
retry permission. An original interrupted attempt remains pending and unresolved
after fresh absence. Applied recovery can resolve delivery while preserving unknown
acknowledgement and earlier rejection. Reconstruction completeness is separate from
delivery resolution and independent verification remains unavailable.

Historical producer/profile generations retain their original attribution.
Late-commit, recovery-authority and bounded same-host process tests have separate
evidence; none establishes cancellation/finality or shared JSON-store concurrency.

Historical compatibility suites use separate CP/Moltbot/Replay/ODES/GAX checkouts
listed under `historical_test_dependencies` in the lock. These are test-only inputs,
not selected runtime pins. Replay/ODES v2 qualification is enabled explicitly;
Evidence Pack historical and v2 suites execute in separate processes/environments.
No suite is dropped: the v2 Evidence Pack file has its own mandatory suite.

## Recovery under changed authority

The accepted repair exports `recovery_denied_derivative` when current authority
denies before observation. Historical Replay, ODES, successor artifacts and producer
references remain unchanged. Current denial/result/reason/evaluation time and source
commitments are separately attributed in lineage; no authorization is renewed.
Ten cases cover five authority changes against applied and absent prior effects.
Valid-authority absence continues through `reconciled_derivative`, preserving
`observed_absent`, `retry_eligible=false` and the pending original effect.
See the [qualification checkpoint](workstreams/recovery-authority-checkpoint.md).
Historical failure evidence remains preserved. Replay contradiction validation is unchanged.

Equivalent-intent duplicate effects remain a characterized limitation. Merged PR #8 adopted the repaired Control Plane `248d899...` with Replay `043830b...`, ODES `0486b64...`, Evidence Pack `de6b9e0...` and Alvorada/GAX `9984d90...` after successful pinned CI. Its release matrix passed the repaired shared-store concurrency/interruption/fail-closed suite in both repetitions; see [accepted evidence](../examples/control-plane-store-adoption/qualification-summary.json). Worker 16's prior record-loss evidence remains historical at its original pin. The repaired boundary is cooperating same-host record transactions on supported local Linux filesystems; it does not imply whole-workflow atomicity or distributed guarantees.
