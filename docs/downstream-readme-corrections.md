# Documentation follow-up register

Audit baseline: hub `f8afac8fae9ebcedb207c46cdaba51728a918d5b`.
This register records follow-ups, not changes or approvals in adjacent repositories.
Current selected contracts are in [compatibility](compatibility.md); newer accepted
component revisions and their adoption status are in [release status](release-status.md).

| Owner / inspected source | Finding | Bounded follow-up |
|---|---|---|
| [Moltbot Safe README at `12b9c55…`](https://github.com/cogno-us/moltbot-safe/blob/12b9c55637e2472a1a5ce3036c787e9427c6abd8/README.md#executor-producer-profile-100) | Heading still says executor producer profile 1.0.0, while the accepted observation/image/readiness work uses 2.0.0 | Distinguish historical 1.0.0 support from current 2.0.0 and link the current contract; preserve legacy evidence |
| [Replay README at `043830b…`](https://github.com/cogno-us/cognous-agent-replay-bundle/blob/043830b56595cecddfa65c064afd1c0b95e64792/README.md#reconstruction-import-020) | “Supported profiles are pinned to” lists only older Control Plane/Moltbot revisions; current v2 support and accepted persistence compatibility are not explained there | Label the legacy list and link the current exact compatibility sets and qualification checkpoint |
| [Alvorada workbench README at `c52f9f0…`](https://github.com/cogno-us/alvorada/blob/c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df/README.md) | Experimental scope is accurate but entry point has no navigation to current GAX runtime, retained-artifact/recovery contracts or the distinct constitutional repository | Add descriptive cross-repository links and bounded workflow navigation without changing the repository name |
| [Moltbot image checkpoint at accepted readiness revision](https://github.com/cogno-us/moltbot-safe/blob/12b9c55637e2472a1a5ce3036c787e9427c6abd8/docs/workstreams/openshell-image-qualification-checkpoint.md) | Historical checkpoint still says image CI is pending; later accepted readiness checkpoint records successful packaged-image evidence | Link later evidence from current navigation; preserve the historical checkpoint and distinguish Docker execution from live OpenShell |
| Hub integration risk-register owner | R-002/R-008 retain older profile wording; R-011 mixes completed bounded qualifications and unresolved work under one state | Reconcile current machine-readable status in a separately owned integration batch; retain original evidence attribution. This batch leaves the register unchanged |
| Hub collateral owners | Older “four layers” framing is an artifact-chain summary, not the complete current responsibility map | Use the current architecture link when refreshing collateral; no renames or collateral expansion here |

## Link and naming audit boundary

Alvorada, Moltbot Safe and Replay READMEs at the revisions above, plus Control
Plane at `248d899634d9db3518e831bc7ab568a48733f825`, were inspected read-only.
No missing relative file target was found in those four repositories' READMEs
(Alvorada, Moltbot Safe, Replay and Control Plane). Their repository URLs were
reachable by Git clone. This is not an HTTP-status or anchor audit of every
cross-repository URL; no confirmed broken cross-repository link is claimed.
Any unverified external targets should be checked by their owners before a
broader documentation release.

The confirmed hub navigation defect was attribution: the evidence index called
`examples/batch4c-accepted/` current even though the selected GAX recovery-export
repair's full evidence is in `examples/worker14d-recovery/`. Current navigation now
separates them. This register's former current Replay profile-1.0.0 claim is also
replaced by the current compatibility link.

Use **Alvorada Constitution** for the institutional authority repository and
**Alvorada experimental workbench** for the GAX/IMX repository. Keep **Moltbot Safe**
repository/package/interface names unchanged. No signature, chain inclusion,
message receipt or reasoning protocol confers execution authority.
