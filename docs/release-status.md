# Support and release status

> **Evidence snapshot:** `document_id=cognous-release-status`; `version=1.1.0`; `generated_at=2026-10-09T16:16:00-07:00`; accepted hub source `f7d03c719b9be3b9c3fe0fe300df642b0f408d98`; component-lock SHA-256 `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`; evidence generation `merged-producers-v1 / full-candidate-gate`. Scope: bounded synthetic local release status. Detached final-file SHA-256 is recorded in [../collateral/evidence-snapshot.json](../collateral/evidence-snapshot.json).

The [component lock](../component-lock.json) selects the merged consumer generation qualified by [hub PR #23](https://github.com/cogno-us/cognous-open-control-stack/pull/23), accepted at `f801546d5272104b02a240e1126b3f92f26486f2`. This remains a bounded synthetic reference, not a production deployment.

## Release boundary

| Level | Current claim |
|---|---|
| **C0 — selected default** | Independently resolve Authority Context and revalidate decision-critical inputs immediately before dispatch. This is **pre-effect revalidation, not destination commit atomicity**; a check-to-commit race remains. |
| **C1 — optional** | Same-host cooperating authority/effect ordering through one participating SQLite transaction boundary. Not enabled by the default release and not an external destination guarantee. |
| **C2/C3** | **No release claim.** No remote commit protocol, distributed transaction coordinator, external settlement finality or production exactly-once guarantee is established. |

The reference destination is synthetic SQLite. Application enforcement, local process coordination and retained receipts must not be presented as card-network, bank, merchant-processor or other external settlement evidence. The incoming message does not carry authority; current bounded authority is supplied by a trusted resolver independently of that message.

## Worked refund timeout and reconciliation

1. A synthetic refund request is received as a proposal.
2. A trusted resolver supplies current Authority Context independently.
3. C0 revalidates the exact tenant/action/target/payload and current grant/policy/evidence immediately before dispatch.
4. The executor attempts local effect `E1`.
5. The caller times out before acknowledgement, so delivery is `unknown`.
6. Reconciliation observes the SQLite destination independently using `E1`; it does not treat timeout or observed absence as retry permission.
7. An applied `E1` remains historical even if current authority later denies a new request.
8. A distinct `E2` with equivalent refund intent remains a separate negative control: effect-ID deduplication does not equal business-intent deduplication. The optional refund-intent profile is separate from C1 and no combined guarantee is claimed.

## Evidence supporting the selected default generation

[Full candidate CI 37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916) tested source `7e43d55c6cc0123a191480a9e6870d6452affa83`. The aggregate resolved all **35 acceptance scenarios**, with required suites executed twice. Artifact `full-candidate-gate` has digest `sha256:5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7`.

These are the current release counts for this evidence generation. Earlier 915-test persistence collateral is retained as historical evidence and is not added to, substituted for or relabeled as this generation.

## Separate profile CI evidence

Optional C1 authority/effect qualification [run 37682165860](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860) passed **73 tests** with no failures, errors or skips against reviewed-source Control Plane `73e3c65acc47dc43593dcb0420d14032ed410b14` and executor `b1525a7982e52ebb530457f94d5517de032ca4c4`. The eventual selected source contains the profile, but the default bounded workflow does not enable it. The run is separate profile evidence, not a 35-scenario release count and not a merge-SHA/external-destination atomicity claim.

The V1 extension evidence contract `v1-reference-extension-evidence/4` separately requires 91 executed profile cases plus 26 synthetic aggregate negative/unit checks. Those populations are not added to the default 35-scenario release count and do not make C1, C2 or C3 default release guarantees.

## Selected behavior and recovery semantics

The selected GAX `merged-producers-v1` compatibility profile uses the ordinary bounded executor path. Source revisions include non-authorizing Decision Input Commitment sidecars and opt-in authority/effect and refund-intent implementations, but this lock does not activate them as a composed default profile.

Unknown delivery is not permission to retry. Accepted record reconstruction is not policy reevaluation, external truth or independent settlement verification. Equivalent business intent across distinct operation identities remains a characterized limitation of the default path. Effect-ID dedupe and business-intent dedupe are deliberately separate claims.

## Deployment limits

Live OpenShell production confinement, production institutional resolver authentication, credential/key custody, remote revocation propagation, arbitrary-agent confinement, external payment settlement, distributed budgets and independent operational review remain outside this release claim.

PRP, TFA and Research Intelligence checks are instruction/schema evidence, not model-behavior efficacy or runtime authority. Human review burden and enterprise benefit remain unmeasured. Governed Exchange PR #2 remains deferred.

[Prior release status](release-status-before-merged-adoption.md) is explicitly **historical**. It retains its original 915-test persistence campaign and protected-worker evidence for that earlier generation; it must not be used as the current snapshot count.

Explicit optional hub commands remain documented in [optional execution profiles](optional-execution-profiles.md). Each activates only its own fresh synthetic local profile. The default release and its consumer-chain scope are unchanged.
