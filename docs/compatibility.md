# Compatibility and interface-gap matrix

Evidence states: **implemented**, **tested locally**, **tested in pinned CI**, **live-qualified**, **unexecuted**, **blocked**, **deferred**.

| Producer / consumer | Selected contract | Pin | State before this PR | Integration rule |
|---|---|---|---|---|
| Action Manifest -> Control Plane | Manifest 1.1 | `46c950b...` -> `2835006...` | implemented | exact manifest/payload/adapter/target binding |
| Constitutional authority -> Control Plane | Authority Context 0.1.0 | `fb3d979...` | implemented | authority comes from trusted resolver, never request content |
| Control Plane -> Moltbot Safe | bounded effect + Execution Envelope 0.2.0 | `2835006...` + `6b0ba11...` | implemented | effect-time revalidation before constrained destination |
| Moltbot Safe accepted head | Execution Envelope 0.2.0 + OpenShell 0.1.0 | `e8a4f8c...` | implemented, separately qualified | not substituted into core provenance until Replay/Evidence Pack pins advance |
| Control/Moltbot -> Replay | Reconstruction Bundle 0.2.0 | `f126483...` | implemented | preserves effect/attempt/observation identity |
| Replay + Manifest -> Evidence Pack | import 0.2.6 | `cb06d8a...` | implemented | summaries remain traceable; draft review is not approval |
| Replay + Manifest -> ODES | ODES tooling 0.2.0 | `b3a2f1e...` | implemented | optional recipient evidence; not GAX or transport |
| GAX/IMX exchange | refund exchange 0.1.0 | `10113bc...` | implemented | receipt/assessment/continuity; authority resolved independently |
| BitRep -> evidence scenario | verification contract v1 | `5b5077d...` | implemented | valid signature establishes attributable verification only |
| Index local chain -> evidence scenario | local blockchain reference | `d5e45d2...` | implemented | chain inclusion establishes inclusion only, never action permission |

## Known interface gaps

1. **Moltbot producer revision gap — release-scoped.** Replay `f126483...`, GAX `10113bc...`, and Evidence Pack `cb06d8a...` still declare Moltbot `6b0ba118...`. The accepted Moltbot head `e8a4f8c...` adds optional OpenShell but has not been adopted as the producer revision by those consumers. The reference workflow therefore pins `6b0ba118...` for the core evidence chain and qualifies `e8a4f8c...` separately. A future upstream change must version the producer profile and update all three consumers before the core pin moves.
2. **Accepted GAX implementation loads some integration fixture helpers from a Moltbot test module.** Moltbot itself exposes the supported executor in `engine.control_plane_adapter.PinnedControlPlaneExecutor`; downstream GAX should remove the test-module loader and import the public executor directly. This hub does not patch the adjacent repository.
3. **GAX PR #2 is deferred.** It is open/unaccepted and contains known semantic concerns. None of its changes are incorporated here.
4. **Live OpenShell is unexecuted unless infrastructure already exists and is explicitly enabled.** Mock tests do not establish sandbox/network/production confinement.
