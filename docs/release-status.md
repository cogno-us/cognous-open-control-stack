# Support and release status

> **Evidence snapshot:** `document_id=cognous-release-status`; `version=1.1.3`; `generated_at=2026-10-22T00:00:00+00:00`; accepted hub source `f7d03c719b9be3b9c3fe0fe300df642b0f408d98`; component-lock SHA-256 `dcd3ab9e4e737c7e50f4bc38c2439438f156da64c9eb1e46725f477973da59ff`; evidence generation `merged-producers-v1 / full-candidate-gate`. Scope: bounded synthetic local release status. Detached final-file SHA-256 is recorded in [../collateral/evidence-snapshot.json](../collateral/evidence-snapshot.json).

The [component lock](../component-lock.json) lists the selected component revisions. The earlier selected tuple, the merged consumer generation qualified by [hub PR #23](https://github.com/cogno-us/cognous-open-control-stack/pull/23) and accepted at `f801546d5272104b02a240e1126b3f92f26486f2`, is superseded, and no new release run exists for the current lock. A separate bounded qualification run of the current component tuple, candidate `g8-r10` ([run 39690459403](https://github.com/cogno-us/cognous-stack-qualification/actions/runs/39690459403), validation `v1-2026-10-16-a`, profile `r13`, workflow revision `4a57a309`, results retained on the qualification repository main at `27e3deb1`), is retained in the qualification repository. It probed the registry at `b2485998`, the attestation component at `981036c3` and the constitutional authority component at `9b5ab721`, the revisions the component lock lists, together with the seven components of the programme-2 r13 profile at the revisions the lock lists: 34 jobs passed, 2 failed and 2 were not run. The two failed jobs are the ODES suite on the two Python versions, and the four failing tests in each are declared in the pre-registration. The run's selected verdict is PASS and its freeze check is PASS, with all 39 mandatory requirement rows PASS. That verdict is computed over the reduced mandatory claim: 36 rows were moved out of it by a recorded scope reduction with their statuses unchanged, and the verdict rule applied to the rows that were mandatory before the reduction is INCOMPLETE. Four Control Plane declared tests did not fail as declared and are recorded as reportable conditions. The verifier entry of the lock (`c0b8ba1f`) is not probed by this run and is not claimed by it. The earlier runs `g2-r10`, `g3-r10`, `g4-r10b`, `g5-r10`, `g6-r10` and `g7-r10` probed older revisions of one or more of those components and are not claimed for the current lock. It is not a release run of this repository and does not change the claims below. This remains a bounded synthetic reference, not a production deployment.

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
3. C0 revalidates the exact tenant/action/target/payload and current grant/policy/evidence immediately before dispatch. Tenant equality is compared for grant, approval and policy status; evidence status is bound to institution/domain, obligation and source, not to tenant, so tenants sharing those identifiers are not separated by the evidence check unless the optional runtime-authority evidence profile (digest-committed; the signer is an asserted name, not authenticated) is enabled.
4. The executor attempts local effect `E1`.
5. The caller times out before acknowledgement, so delivery is `unknown`.
6. Reconciliation observes the SQLite destination independently using `E1`; it does not treat timeout or observed absence as retry permission.
7. An applied `E1` remains historical even if current authority later denies a new request.
8. A distinct `E2` with equivalent refund intent remains a separate negative control: effect-ID deduplication does not equal business-intent deduplication. The optional refund-intent profile is separate from C1 and no combined guarantee is claimed.

## Evidence for the earlier selected default generation (superseded)

[Full candidate CI 37694032916](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916) tested source `7e43d55c6cc0123a191480a9e6870d6452affa83`. The aggregate resolved all **35 acceptance scenarios**, with required suites executed twice. Artifact `full-candidate-gate` has digest `sha256:5728b8bbdf71dc7a045196eaebaf5f1fa8154485d728c39921eaa882f9a84ed7`.

These counts belong to the earlier evidence generation named above; they are not a result for the current lock. Earlier 915-test persistence collateral is retained as historical evidence and is not added to, substituted for or relabeled as this generation.

## Separate profile CI evidence

Optional C1 authority/effect qualification [run 37682165860](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860) passed **73 tests** with no failures, errors or skips against reviewed-source Control Plane `73e3c65acc47dc43593dcb0420d14032ed410b14` and executor `b1525a7982e52ebb530457f94d5517de032ca4c4`. The eventual selected source contains the profile, but the default bounded workflow does not enable it. The run is separate profile evidence, not a 35-scenario release count and not a merge-SHA/external-destination atomicity claim.

The V1 extension evidence contract `v1-reference-extension-evidence/5` separately requires 111 executed profile cases plus 30 synthetic aggregate negative/unit checks. Those populations are not added to the default 35-scenario release count and do not make C1, C2 or C3 default release guarantees.

## Declared known limit at the programme-2 profile

The representative reference run is not exercised at the programme-2 profile (`security-runtime-p2-20261018`). The governed-exchange recipient adapter requires a runtime authority profile under the security-runtime profiles and does not yet forward one. The `reference-release` workflow (its `cross-component / reference` job, step "Run pinned reference candidate twice") is consequently expected to fail at this profile, and it failed on hub main `2223a8dc` ([run 39477528301](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/39477528301)). This is a declared known limit, not a pass. No result of this workflow is claimed for the current lock.

The authority batch of the `full-candidate-release` matrix and its aggregate passed on hub main `2223a8dc` ([run 39513719580](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/39513719580): authority, exchange, consumers, registry and aggregate). The earlier statement that they are expected to fail at this profile is withdrawn. Their passing is recorded as observed on that revision and is not a claim about the representative reference run.

## Selected behavior and recovery semantics

The selected GAX `security-runtime-p2-20261018` compatibility profile uses the ordinary bounded executor path. Source revisions include non-authorizing Decision Input Commitment sidecars and opt-in authority/effect and refund-intent implementations, but this lock does not activate them as a composed default profile.

Unknown delivery is not permission to retry. Accepted record reconstruction is not policy reevaluation, external truth or independent settlement verification. Equivalent business intent across distinct operation identities remains a characterized limitation of the default path. Effect-ID dedupe and business-intent dedupe are deliberately separate claims.

## Deployment limits

Live OpenShell production confinement, production institutional resolver authentication, credential/key custody, remote revocation propagation, arbitrary-agent confinement, external payment settlement, distributed budgets and independent operational review remain outside this release claim.

Human review burden and enterprise benefit remain unmeasured. Governed Exchange PR #2 remains deferred.

[Prior release status](release-status-before-merged-adoption.md) is explicitly **historical**. It retains its original 915-test persistence campaign and protected-worker evidence for that earlier generation; it must not be used as the current snapshot count.

Explicit optional hub commands remain documented in [optional execution profiles](optional-execution-profiles.md). Each activates only its own fresh synthetic local profile. The default release and its consumer-chain scope are unchanged.

## Nonselected F5b-repaired candidate

The nonselected F5b-repaired seven-component merged-source candidate is recorded in [`profiles/security-runtime-f5b-candidate-20261016.json`](../profiles/security-runtime-f5b-candidate-20261016.json) and its hub-side F3R qualification receipt in [`docs/releases/f3r-qualification-receipt-20261016.md`](releases/f3r-qualification-receipt-20261016.md). Hosted qualification [run 38925303886](https://github.com/cogno-us/cognous-stack-qualification/actions/runs/38925303886) at tested qualification source `7022881e0958543a8b7685031c63132891b5f47c` passed 36 raw cases per repetition across two repetitions with zero failures/errors/skips, under the strict Exchange compatibility profile `security-runtime-f5b-20261016`. The historical c996a41 source-review freeze packet in [`docs/releases/security-review-freeze-20261016/`](releases/security-review-freeze-20261016/README.md) is superseded for fresh review by the new F5b packet retained in [`docs/releases/security-review-freeze-f5b-20261016/`](releases/security-review-freeze-f5b-20261016/README.md); historical freeze bytes are retained as-is. The earlier nonselected profile [`profiles/security-runtime-candidate-20261016.json`](../profiles/security-runtime-candidate-20261016.json) is unchanged. `component-lock.json`, the public W7 selection, every full-reference profile, publication HOLD and production HOLD are unchanged by this receipt. This candidate requires a final review-and-refreeze cycle; no release or production authorization.

## F8 — public-reference tags

The owner approved public reference publication of the F5b-repaired bounded synthetic reference on 2026-10-16 (acceptance packet in [`docs/releases/f7-acceptance-packet-20261016.md`](releases/f7-acceptance-packet-20261016.md); owner decision on [issue #68](https://github.com/cogno-us/cognous-open-control-stack/issues/68)). Three annotated tags named `public-reference-f5b-20261016` were pushed by the owner against the exact-byte heads bound in the acceptance packet:

- Hub [cogno-us/cognous-open-control-stack @ `public-reference-f5b-20261016`](https://github.com/cogno-us/cognous-open-control-stack/tree/public-reference-f5b-20261016), pointing at `a2d3a509856e1621105664c5f11195f6f6b100ce`.
- Qualification [cogno-us/cognous-stack-qualification @ `public-reference-f5b-20261016`](https://github.com/cogno-us/cognous-stack-qualification/tree/public-reference-f5b-20261016), pointing at `af9f5843b9188ee5c6dc0648206d1e92e41a73ef`.
- Runtime [cogno-us/cognous-execution-runtime @ `public-reference-f5b-20261016`](https://github.com/cogno-us/cognous-execution-runtime/tree/public-reference-f5b-20261016), pointing at `e20f92e104aba2ba6ad06120d8549c6170eaf63f`. The retained upstream Moltbot application is preserved at the separate historical tag [`upstream-moltbot-quarantine-20261016`](https://github.com/cogno-us/cognous-execution-runtime/tree/upstream-moltbot-quarantine-20261016); it is not part of this reference.

These tags are a public reference to the bounded synthetic reference bytes. They are not a stack release tag, not a component-lock update, not a W7 re-selection, not operational-trust change, not production authorization, and not an announcement. `component-lock.json`, the public W7 selection, every full-reference profile, publication HOLD and production HOLD / NOT ESTABLISHED are unchanged by these tags. C0 race, optional same-host C1, and no C2/C3 or real settlement are preserved. Residuals carried from the F7 packet remain outstanding; see [`docs/releases/f7-acceptance-packet-20261016.md`](releases/f7-acceptance-packet-20261016.md).


## Review marker tags (2026-10-22)

The owner created one annotated tag, `review-v0.1-g8-r10-20261022`, with the same name in the 14 repositories listed below, each pointing at the commit shown. It is a **review marker** that lets a reviewer recover the exact revisions read together for candidate `g8-r10` from the tag name alone.

What it is not: not a version, not a release and not a released action reference; not a contract freeze (the contracts remain `0.1.0-draft`); not a component-lock change; not a certification, security clearance, readiness or enterprise claim; not production authorization and not a publication authorization. Publication HOLD and production HOLD / NOT ESTABLISHED are unchanged, and `publication_authorized` and `production_authorized` stay `false` wherever a release-state file records them. The tags are non-authorizing and carry the same limits as the F8 reference tags above; they are a second, separate tag family and replace none of them. The known issues are in [the v0.1 known issues register](releases/v0.1-known-issues.md).

| Repository | Commit the tag points at |
|---|---|
| `cognous-action-manifest` | `fa170815ef96a54c233d0dd9da821b60debabf8b` |
| `cognous-control-plane` | `0a41faa972699f7ec3063967a14cd9bdd3e67d27` |
| `cognous-execution-runtime` | `ec728da6dc301a664b331ac8986afd6e850a1273` |
| `cognous-governed-exchange` | `7f7569b02666b99669a9fca61117ca1f4bce5f0d` |
| `cognous-replay-bundle` | `028f63d1c001f99580583888fa4b4e46d77a267b` |
| `cognous-governance-evidence-pack` | `a3ebbb90559a44a88855139a182649d3792bb1ca` |
| `open-decision-evidence-standard` | `e86a25a1d660e74533337d38744e2934200a50ae` |
| `cognous-evidence-attestation` | `981036c315856c71207984797b0c4e48d3b3921d` |
| `cognous-evidence-registry` | `b2485998b88256c2b322493800d1fba076814cbd` |
| `cognous-institutional-governance` | `9b5ab721ae0684150e466c01e9d0d59ec61c3e00` |
| `cognous-open-control-stack-verifier` | `c0b8ba1f55b75db787a320f3de0f79342c6f6826` |
| `cognous-stack-qualification` | `195c728fa292e7f20f6ccca0f625a744c5bf5aec` |
| `cognous-open-control-stack-ergonomics` | `54807212f002bf20d9eba4c0037cb61214aa045f` |
| `cognous-open-control-stack` (this hub) | `a2d9396c1e2022ac36ae4db58dcc2f2e14161b7c` |

The portable-reasoning, research-intelligence and truth-freedom-agency repositories and the orchestrator are not tagged. The verifier entry of the lock is tagged but is still not probed or claimed by run `g8-r10`.
