# Compatibility and interface-gap matrix

Evidence states: **implemented**, **tested locally**, **tested in pinned CI**, **live-qualified**, **unexecuted**, **blocked**, **deferred**.

| Producer / consumer | Selected contract | Selected pin (GAX candidate) | Integration rule |
|---|---|---|---|
| Action Manifest -> Control Plane | Manifest 1.1 | `46c950b...` -> `2ea9528...` | exact manifest/payload/adapter/target binding |
| Constitutional authority -> Control Plane | Authority Context 0.1.0 | `fb3d979...` | authority comes from trusted resolver, never request content |
| Control Plane -> Moltbot Safe | bounded effect + Execution Envelope 0.2.0 | `2ea9528...` + `177354e...` | effect-time revalidation before constrained destination |
| Moltbot Safe producer -> Replay | executor producer profile 2.0.0 + Reconstruction Bundle 0.2.0 | `177354e...` -> `274543f...` | preserves frozen operation, effect, observation and separate attempt namespaces |
| Replay + Manifest -> Evidence Pack | import 0.2.6 | `812194b...` | summaries remain traceable; source assertions are not independent verification |
| Replay + Manifest -> ODES | ODES implementation profile 0.2; pder-v0.1 unchanged | `226adb0...` | package integrity, authentication and current authority remain separate |
| GAX/IMX exchange | refund exchange 0.1.0 + retained artifacts 1.1.0 | `8836136...` | explicit resolver, execution/observation policy and trusted clock, original-artifact retention and evidence-only recovery |
| BitRep -> evidence scenario | verification contract v1 | `5b5077d...` | valid signature establishes attributable verification only |
| Index local chain -> evidence scenario | local blockchain reference | `d5e45d2...` | chain inclusion establishes inclusion only, never action permission |

## Resolved interface debt

1. **Versioned Moltbot producer compatibility — resolved for the candidate path.** Moltbot `177354e...`, Replay `274543f...`, ODES `226adb0...`, Evidence Pack `812194b...` and Alvorada `8836136...` now share the candidate executor producer profile `urn:cognous:profiles:moltbot-safe-executor-producer` / `2.0.0`. Legacy unversioned Moltbot artifacts remain revision-pinned in the consumer path and are not relabeled.
2. **GAX public executor entrypoint — resolved.** The supported Alvorada runtime imports public Moltbot producer/executor modules and requires caller-supplied resolver and execution policy. The hub qualifies the supported path with upstream test directories unavailable.
3. **Original Replay artifact retention — resolved.** The versioned Alvorada retained-artifact interface exposes the original Reconstruction Bundle, ODES package/recipient validation and successor packet with identities and content commitments. Duplicate/redelivery returns the retained original when available. When an original was never retained after a post-effect interruption, regenerated evidence has distinct derivative lineage and does not trigger a replacement effect.

## Remaining bounded gaps

1. **Alvorada PR #2 remains deferred.** It is unaccepted and excluded from the reference integration.
2. **Live OpenShell remains unexecuted unless authorized infrastructure already exists and is explicitly enabled.** Mock tests do not establish live sandbox/network/OS confinement.
3. **Production institutional authority is out of scope.** The public integration uses synthetic/bounded resolver fixtures; it does not establish authenticated institutional resolver deployment, credential custody or production revocation propagation.
4. **Fleet orchestration and distributed budgets remain out of scope.**

## Batch 4C observation boundary

The proposed lock advances accepted CP/executor/Replay/ODES/Evidence Pack pins,
but Alvorada `8836136c8b17a5eeda65467d06976d2164927515` is an **unmerged candidate**
from PR #6. Its Tests run 37551082772 passed at the single dependency check.
The accepted Alvorada revision remains `6bcde026a804c7377f5e39f57ca6dd00b3c3292d`.
No release acceptance is inferred from candidate test success.

Explicit ObservationPolicy and timezone-aware evaluation time govern observation
acceptance. A rejected or null observation is retained separately from attempt and
acknowledgement history. `observed_absent` is point-in-time evidence and never
retry permission. An original interrupted attempt remains pending and unresolved
after fresh absence. Applied recovery can resolve delivery while preserving unknown
acknowledgement and earlier rejection. Reconstruction completeness is separate from
delivery resolution and independent verification remains unavailable.

Historical producer/profile generations retain their original attribution; no old
artifact is relabeled 2.0.0 or 1.1.0. Remaining in-flight/late-commit, recovery-authority
and unproven separate-process boundaries remain pending; see [checkpoint](workstreams/batch4c-integration-checkpoint.md).

Historical compatibility suites use separate CP/Moltbot/Replay/ODES/GAX checkouts
listed under `historical_test_dependencies` in the lock. These are test-only inputs,
not selected runtime pins. Replay/ODES v2 qualification is enabled explicitly;
Evidence Pack historical and v2 suites execute in separate processes/environments.
No suite is dropped: the v2 Evidence Pack file has its own mandatory suite.
