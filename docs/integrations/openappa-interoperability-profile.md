# OpenAPPA interoperability profile 0.1 — proposed

**Status:** design contract; not implemented, enabled, or qualified. **Owner:** Cognous Open Control Stack hub (cross-project compatibility only). Component implementations remain in their owning repositories.

**Pinned review inputs:** Cognous hub `61010c69a8d836d63bd85727f8c4aa9542e98d95` and its unchanged [component lock](../../component-lock.json); external OpenAPPA `10aa0e09e32d8c6704bdb030dc3c66140bf81915`. A source SHA is **not** a stable published wire-version guarantee. Reconfirm the OpenAPPA API at build time. Do not edit the accepted lock in this contract batch.

**Source and scope:** [OpenAPPA integration guide](https://github.com/archestra-ai/OpenAPPA/blob/10aa0e09e32d8c6704bdb030dc3c66140bf81915/website/content/docs/add-to-agent.md), [runtime API](https://github.com/archestra-ai/OpenAPPA/tree/10aa0e09e32d8c6704bdb030dc3c66140bf81915/appa-runtime-api), [self-improving policies](https://github.com/archestra-ai/OpenAPPA/blob/10aa0e09e32d8c6704bdb030dc3c66140bf81915/website/content/docs/self-improving-policies.md), and [reporting](https://github.com/archestra-ai/OpenAPPA/blob/10aa0e09e32d8c6704bdb030dc3c66140bf81915/website/content/docs/yell.md). This profile consumes the separate OpenAPPA interoperability addendum OA01–OA10. It is not the native Cognous information-flow implementation (IF01–IF08); common concepts should be reused rather than duplicated.

## 1. Authority and flow invariants

1. **Conjunction:** A protected dispatch can occur only if the exact canonical operation has a current APPA flow allowance **and** independently valid Cognous authorization. Neither decision creates, extends, revives, or substitutes for the other.
2. **Single effect binding:** Both checks refer to identical tenant, action, adapter, target, canonical parameters/payload commitment and destination. Any substitution invalidates the combined eligibility. A tool alias alone is insufficient.
3. **Temporal validity:** Bind decisions to immutable versions and required state generations. Expiry, policy changes, relevant trajectory restrictions, authority changes, or changed operation inputs require re-evaluation under the declared profile. Distinguish OpenAPPA's pinned historical trajectory policy from the authority currently governing a *new* effect.
4. **Boundary:** APPA `allow_call` is not execution; Cognous 'allowed' is not dispatch; dispatch is not an observed effect; admitted tool output is not verified truth. A post-effect output block cannot undo or erase the applied effect.
5. **Competent remedies:** APPA remedy offers are non-authorizing proposals. Any consequential release, amendment or exception must be issued and consumed through Cognous Institutional Governance / existing Authority Context, with exact operation scope and replay-safe lineage. No agent or classifier grants itself authority.
6. **Fail closed for the selected protected profile:** Unavailable, invalid, mismatched, stale, corrupted or uncorrelated APPA responses cannot become implicit allowances. An unqualified hook path cannot be called protected.
7. **Evidence:** A valid log or imported record is neither a current authorization nor independent destination verification. Raw sensitive arguments/results are not copied into telemetry by default.

## 2. Proposed adapter record schema (not current OpenAPPA wire schema)

The following names are **Cognous-side proposed fields**; they must be mapped from inspected upstream wire types, not injected as fictional OpenAPPA fields.

| Record | Required identity/commitment | Status and boundaries |
| --- | --- | --- |
| `AppaDeploymentBinding` | tenant from authenticated host; APPA source SHA/build; deployment and policy digest; trust/store partition; declared supported hooks; binding version | rejects missing hook/tenant isolation; no permission effect |
| `AppaTrajectoryBinding` | Cognous run/workflow ID; APPA root/trajectory and launch family; tenant; parent/child scope; state generation or durable event cursor | session changes, restart and fork cannot silently open unrestricted roots |
| `AppaToolBinding` | Manifest 1.1 version/digest; action key; adapter identity; actual sink/recipient and parameter roles; canonical target/payload hash; APPA tool identifier | no permissive fallback for unmapped composite tools |
| `AppaFlowCheck` | operation/effect ID; attempt ID if dispatched; tool call ID; trajectory generation; APPA policy identity; request and decision commitment; outcome/reason; evaluated time | allowance is information-flow only, requires same-operation join to current authority |
| `AppaResultAdmission` | tool call/result identity; actual delivery status and result commitment; admission outcome; replacement reference if any | blocked/replaced result must not enter model, memory, exports or child context through any declared path |
| `AppaRemedyBridge` | original denial; offered remedy ID/version; exact proposed revision; institutional decision/grant refs; consumption and expiry | a proposed remedy is never authority; stale and replayed offers fail |
| `AppaChildReturn` | parent-child/spawn binding; inherited restrictions; declared return contract; child end and parent admission receipts | child abandonment never erases separate known effects |
| `AppaEvidenceProjection` | record schema/version; source hashes; redaction map; transformation version; import losses/unknowns | reconstructs captured events, not hidden cognition or external effect verification |
| `AppaFrictionReport` | originating policy decision/denial; consent/retention basis; bounded diagnostic refs; report identity and delivery/duplicate state | report/telemetry/maintenance recommendation has `authority_effect: none` |

Unknown, absent, redacted and unsupported must remain distinct values. All identity bindings are scoped to the trusted tenant context, not model-supplied labels. Store raw protected content outside exported records; logs may retain commitments and access-controlled references only. Preserve provenance and applicable deletion/retention obligations.

## 3. Hook mapping and required host behavior

OpenAPPA's documented external path is `POST /hook` (or embedded runtime call) with lifecycle actions. The **real upstream wire contract** must be pinned and fixture-validated before executable work.

| OpenAPPA event or response | Cognous owner / host action | Non-negotiable check |
| --- | --- | --- |
| `session_start`, `prompt`, `turn_end` | Context/Execution host records lifecycle and durable trajectory association | `prompt` is a turn marker, not model-input verification; no reset on restart |
| `tool_call` -> `allow_call` / `deny_call` / `pass_control` | Executor host checks APPA before tool dispatch; Control Plane independently resolves current authority | deny never dispatches; `pass_control` routes a remedy handler, never tool execution |
| `tool_result` -> `ack` / `deliver_value` / `replace_output` / `block` | Context admission gate before model/memory/child access | replacement, withheld result and actual effect/outcome separately recorded |
| `child_start`, `child_end`, `spawn_result` | Optional Governed Exchange/child-context adapter | match `spawn_binding`; prevent unapproved child context and unmediated parent return |
| `appa/execute_remedy_plan` (through approved route) | Institutional Governance/Control Plane bridge | only an existing competent authority path may authorize consequential exception |
| `appa yell` report | Optional evidence/diagnostic ingestion | caller content not trusted, opt-in and retention constrained; report is never a policy change |

OpenAPPA's built-in report receiver describes its public salt/signature as **not authenticating sender identity**. Never map that signature to BitRep issuer attestations. OpenTelemetry is lossy operational telemetry, not the authoritative Cognous replay ledger.

## 4. Deployment and enforcement conditions

Supported profile starts with the *synthetic same-host refund* and a declared local trusted host that owns interception and destination access. An external APPA sidecar needs authenticated local IPC and tenant partitioning; an embedded runtime still requires strict separation of stores and credential lookup. Identify actual endpoints from the pinned upstream API, not this proposal.

Every declared sink (remote query arguments, message, file, memory, telemetry, model context and child return) must have a hook or an explicit exclusion. Enforce **before dispatch** and **before output admission**. If an effect has already committed but output admission blocks, preserve 'applied/observed' separately from 'withheld'. Remote destination commit races require the existing Cognous destination-specific authority/effect and idempotent recovery contract; APPA's pre-call check does not close that race.

Conformant deployment must document hook coverage, operating system and trust boundary, startup health, policy reload semantics, response timeouts, state durability, crash recovery, multiple sessions and concurrency, tenant isolation, telemetry destinations, secret custody and explicit emergency failure mode. No live-agent protection claim follows from mocked hooks.

## 5. Component ownership and implementation order

| Gate | Repository | Scoped owner output |
| --- | --- | --- |
| A | `cognous-action-manifest` | Canonical action-to-APPA tool/sink/parameter binding; validation and negative substitutions (OA02) |
| B | `cognous-institutional-governance` | Remedy issuer competence and approved grant/reference semantics, no auto-policy adoption (OA05) |
| C | `cognous-control-plane` | Conjunctive flow/authority join; current state revalidation; denial, recovery, effort IDs (OA03/OA05) |
| D | `cognous-execution-runtime` | Pre-dispatch and pre-admission hooks, durable correlation and failure behavior (OA04) |
| E | `cognous-governed-exchange` | Optional constrained child lifecycle and return bridge (OA06) |
| F | `cognous-replay-bundle` | Loss-reporting APPA event import, redaction and lineage (OA07) |
| G | `cognous-governance-evidence-pack` | Traceable projection; protected-flow and denied/unknown outcomes; non-authorizing friction report (OA07/OA08) |
| H | `open-decision-evidence-standard` | Optional informative mapping; any new normative field needs a separate RFC/profile (OA10) |
| I | `cognous-open-control-stack` | Exact-pin compatibility manifest, synthetic qualification, residual risk ledger; opt-in activation only after acceptance (OA01/OA09) |

Cognous Evidence Attestation/Registry may carry independently verified provenance, not APPA authorization or the public yell salt as issuer identity. No changes required for initial profile.

**Integration sequencing:** A and B publish contract fixtures; C and D establish enforced same-operation joins; E optional; F/G consumers only after actual producer outputs; H optional; I qualifies a complete pinned candidate. Each upstream PR must report its exact source SHA, tests, interface version and migration impact. Hub pins advance **only** after explicit acceptance.

## 6. Qualification matrix (planned, not run)

Run against a frozen synthetic refund destination, asserting both decision records and destination state, then check actual admitted model/context bytes where supported.

| Case | Expected dispatch / outcome |
| --- | --- |
| APPA flow allow + valid current Cognous grant | Exactly one declared authorized effect, observed separately |
| APPA deny + Cognous allow | No dispatch or effect; clear flow denial |
| APPA allow + Cognous deny | No dispatch or effect; clear institutional denial |
| APPA runtime/store timeout, bad response, stale state | No protected dispatch; unresolved safely preserved |
| Call/payload/recipient/adapter substitution | No effect; binding mismatch |
| Flow or authority changed between approval and effect | Revalidate; refusal under the declared supported boundary; disclose remaining remote race |
| Forged, expired or duplicated remedy | No exception; no effect |
| Effect applied, post-result block | Applied effect retained, restricted result absent from all covered admissions |
| Crash/restart, compaction or child fork | Restrictions and known effects not reset; unsafe missing state blocks |
| Invalid child return / unapproved child spawn | No parent admission and no expanded rights |
| Friction report or telemetry suggests policy relaxation | No policy or authority change |
| Replay/evidence projection with missing source entry | Explicit incomplete/unverified, never silently successful |

Report each case as planned/executed/pass/fail/blocked, environment, source/pin, assertion, observations and coverage. Evaluate safe work continuation and false blocks as distinct metrics. No production non-bypassability, remote exactly-once, external-truth verification or institutional efficacy claim is included.

## 7. Acceptance and non-goals

This document alone is **not acceptance of OA01–OA10**. Next implementation gate requires upstream hook fixtures, a Cognous operation crosswalk, a two-sided denial fixture, and a defined state/tenant trust model.

Non-goals: adding OpenAPPA to the default runtime/lock, substituting APPA for Institutional Governance, permitting automatic policy/authority expansion, making ODES a runtime control, duplicating IF01–IF08, transferring benchmark claims, deploying credentials or exposing proprietary ISS/Navalia methods.

## 8. Handoff checklist

Every owning component must return: starting head, accepted dependency pins used, exact changed files, new/changed wire profile, fixture samples, actual tests and outcomes, unsupported paths, residual races, and PR/merge SHA. Keep work in isolated branches; preserve unrelated merges; no force push.
