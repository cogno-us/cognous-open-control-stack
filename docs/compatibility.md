# Compatibility and interface-gap matrix

Evidence states: **implemented**, **tested locally**, **tested in pinned CI**, **live-qualified**, **unexecuted**, **blocked**, **deferred**.

| Producer / consumer | Selected contract | Accepted pin | Integration rule |
|---|---|---|---|
| Action Manifest -> Control Plane | Manifest 1.1 | `46c950b...` -> `2835006...` | exact manifest/payload/adapter/target binding |
| Constitutional authority -> Control Plane | Authority Context 0.1.0 | `fb3d979...` | authority comes from trusted resolver, never request content |
| Control Plane -> Moltbot Safe | bounded effect + Execution Envelope 0.2.0 | `2835006...` + `1d308fa...` | effect-time revalidation before constrained destination |
| Moltbot Safe producer -> Replay | executor producer profile 1.0.0 + Reconstruction Bundle 0.2.0 | `1d308fa...` -> `f63ce91...` | preserves frozen operation, effect, observation and separate attempt namespaces |
| Replay + Manifest -> Evidence Pack | import 0.2.6 | `f1a7618...` | summaries remain traceable; source assertions are not independent verification |
| Replay + Manifest -> ODES | ODES tooling 0.2.0 | `cba83a1...` | package integrity, authentication and current authority remain separate |
| GAX/IMX exchange | refund exchange 0.1.0 + retained artifacts 1.0.0 | `6bcde02...` | explicit resolver/policy, original-artifact retention and evidence-only recovery |
| BitRep -> evidence scenario | verification contract v1 | `5b5077d...` | valid signature establishes attributable verification only |
| Index local chain -> evidence scenario | local blockchain reference | `d5e45d2...` | chain inclusion establishes inclusion only, never action permission |

## Resolved interface debt

1. **Versioned Moltbot producer compatibility — resolved for the accepted path.** Moltbot `1d308fa...`, Replay `f63ce91...`, ODES `cba83a1...`, Evidence Pack `f1a7618...` and Alvorada `6bcde02...` now share the accepted executor producer profile `urn:cognous:profiles:moltbot-safe-executor-producer` / `1.0.0`. Legacy unversioned Moltbot artifacts remain revision-pinned in the consumer path and are not relabeled.
2. **GAX public executor entrypoint — resolved.** The supported Alvorada runtime imports public Moltbot producer/executor modules and requires caller-supplied resolver and execution policy. The hub qualifies the supported path with upstream test directories unavailable.
3. **Original Replay artifact retention — resolved.** The versioned Alvorada retained-artifact interface exposes the original Reconstruction Bundle, ODES package/recipient validation and successor packet with identities and content commitments. Duplicate/redelivery returns the retained original when available. When an original was never retained after a post-effect interruption, regenerated evidence has distinct derivative lineage and does not trigger a replacement effect.

## Remaining bounded gaps

1. **Alvorada PR #2 remains deferred.** It is unaccepted and excluded from the reference integration.
2. **Live OpenShell remains unexecuted unless authorized infrastructure already exists and is explicitly enabled.** Mock tests do not establish live sandbox/network/OS confinement.
3. **Production institutional authority is out of scope.** The public integration uses synthetic/bounded resolver fixtures; it does not establish authenticated institutional resolver deployment, credential custody or production revocation propagation.
4. **Fleet orchestration and distributed budgets remain out of scope.**
