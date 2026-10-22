# S01 comparative assessment: CA-01 to CA-06

Rows V2-H-01 to V2-H-06. This replaces the "preliminary" status of [comparative-review.md](../comparative-review.md) with source-grounded dispositions; the owner brief and the original rows are unchanged. Vocabulary is "observed". No competing policy engine, canonical gate or evidence authority is proposed, and release and production remain on HOLD.

## What was and was not read

| Source | Result |
|---|---|
| OpenAPPA repository README | read; self-reported results are the project's own |
| OpenAPPA paper (arXiv 2607.24625) | secondary summary only (an AI-generated summary page), not the PDF |
| openappa.com how-it-works | unreachable; REQUIRES INVESTIGATION |
| Cedar documentation (authorization, validation, security pages) | read via search-result URLs; the root page and policy-store separation not read |
| Open Policy Agent (bundles, management; one older version page) | read; field names from the older page may have changed |
| Microsoft Agent Governance Toolkit | repository unreachable; Microsoft blog and a third-party documentation page only; REQUIRES INVESTIGATION for repository claims |
| "From Mainline to Governed Cognition" (Aug 2026) | not found in the hub, project documents or any cloned repository; CA-06 uses the owner's stated principles only |

## Prior work the plan did not name

OCS already holds optional, partly qualified artifacts for several of these items: the hub OpenAPPA interoperability profile and optional-compatibility document; Action Manifest `openappa_binding.py` (140 lines, in the locked revision, `authority_effect: "none"`); twelve runtime workstream documents on OpenAPPA; qualification probe tooling with reported reply (60) and conjunction (125) case runs, not re-run here; Control Plane `microsoft_agt.py` (483 lines, conjunctive only); the comparative governance battery (OPA 1.21.2 and LangGraph, 24 scenarios, 1,440 trials, not independently preregistered); and register rows IF01-08, PI01-12, OG01-05, EGA01-09. The CA dispositions below are therefore deltas on these artifacts, not new tracks (defect PD-C02).

## Summary

| Item | Disposition | Priority | New authority needed? | Step homes |
|---|---|---|---|---|
| CA-01 trajectory information flow | ADAPT; enforcement deferred | design and boundary statement mandatory in P1; implementation post-v0.2 | Yes if built natively, so keep it an external conjunctive route | 1.6 |
| CA-02 typed validation | ADOPT requirements already in the registry direction; REJECT Cedar as internal engine; DEFER a Cedar source-policy adapter | v0.2 mandatory (inside WS-B) | No | 1.3, 2.3, 2.4 |
| CA-03 distribution and convergence | ADAPT local identify-and-detect; DEFER distribution service | local subset v0.2 mandatory | No (extends `rule_identity`) | 2.4, 1.3 |
| CA-04 enforcement coverage | ADOPT as a declaration-only manifest; REJECT any OS-confinement claim | declaration v0.2 mandatory (needs owner confirmation) | No (non-authorizing record) | 1.7, 4.2 |
| CA-05 governed remediation | ADAPT vocabulary only; DEFER execution and metrics | no-blind-retry subset mandatory; vocabulary optional | No for the subset | 1.6, 3.1, 3.5 |
| CA-06 promotion and no-regressions | ADOPT as ADR table plus compatibility gate | v0.2 mandatory | No (records and checks) | 1.2, 4.1, 4.5 |

## CA-01 Trajectory-level information-flow governance

1. External pattern. OpenAPPA tracks a label of reader set and trust level combined by meet, checked before dispatch and at return admission, with child contexts inheriting the parent label. The sources read do not define summarization or paraphrase handling and do not separate evidence reliability from the trust order.
2. Existing OCS. Optional conjunction with an external OpenAPPA runtime (persisted trajectory, host enrolment, reply admission gate); hub `reference_profiles/payload_disclosure.py` (exact-payload check at one sink, `authorizing_execution: False`); Authority Context delegation that cannot exceed the parent. `risk_metadata` is committed in the Control Plane proposal commitment (`bounded.py:1323`) but is absent from the GAX operation commitment and read by no evaluator.
3. Missing. No label model or evaluator in any locked component; no inheritance rule for transformations; the only trajectory state is inside the external engine. The exchange transport cannot currently run under the `security-runtime-*` profiles.
4. Reuse. Interfaces can carry a label reference (carriage yes, enforcement no). Owners: Manifest (declarations), Control Plane (join), runtime and qualification (admission, probes), hub (compatibility record).
5. Implications. A proposer-asserted label can be omitted or lowered unless host-derived and bound. Confidentiality, reliability and authority must stay separate fields. A native evaluator would be a second decision gate.
6. Minimum for v0.2. Written boundary statement (flow permission is not authority); mapping of IF01-08, PI and EGA02 to the conjunction route; a `trajectory_binding` reference as an optional input that holds when a flow-protected class is declared and the reference is missing; one frozen negative case (valid grant plus restricted label gives no dispatch). No new store.
7. Independent criteria. Valid grant plus external deny gives zero destination rows; restriction survives restart and a fresh database allows; child return without a declared contract is refused; missing or mismatched binding holds. The summarization case is BLOCKED until an owner-stated host rule exists.
8. Priority. Design and boundary v0.2 mandatory (already P1); implementation post-v0.2.
9. Disposition. ADAPT, defer enforcement. The acceptance target as worded cannot be established by OCS alone today.

## CA-02 Typed authorization schemas and policy validation

1. External pattern. Cedar: default deny, forbid overrides permit, an erroring policy is skipped and reported in diagnostics, validation against a schema is expected before use but optional, validation does not cover entity existence or integer overflow.
2. Existing OCS. Manifest models, JSON Schema and validator E001-E025 (417 lines); an in-tree port in Control Plane (`manifest_validation.py`, 171 lines) pinned to upstream `46c950be` while the lock selects `fa170815`; Control Plane profiles with `extra="forbid"` and composition checks; `rule_revision.py` (188 lines). Gate errors map to `E999` and hold (fail closed), the opposite of skip-on-error.
3. Missing. No registry in code; no total mandatory-check manifest; no evaluator-identifier registry; no activation refusal on conflicting rule-sets; two validator copies.
4. Reuse. Verifier `NOT_APPLICABLE_REASONS` (two closed reasons) and `MANDATORY_KINDS` as fixtures; reason registry plus vendoring with provenance; owners per the registry-location decision.
5. Implications. Skip-on-error is incompatible with "no allow without all necessary check evidence". A Cedar adapter would be acceptable only if it validates before activation, treats any diagnostics error as hold for the whole request, and never turns "no policy matched" into a skipped mandatory check.
6. Minimum. Closed registry record schema; activation refused unless the schema is valid, every mandatory check has a qualified evaluator, no duplicate or shadowing rule exists, and the epoch is monotone. No Cedar code in v0.2.
7. Independent criteria. Malformed, incomplete, conflicting, unknown-evaluator, null or non-boolean input, unqualified evaluator version, invalid signature and non-monotone epoch each leave no active rule-set and preserve old behavior; old-versus-registry equivalence; agreement of the two validator copies on the locked pair.
8. Priority. v0.2 mandatory, within WS-B.
9. Disposition. ADOPT the validation and refusal requirements; REJECT Cedar as an internal engine; DEFER a Cedar adapter.

## CA-03 Policy distribution and activation convergence

1. External pattern. OPA bundles carry a revision, optional signature verification, activation only after verification, retention of the previous bundle on failure with failure reported through a status interface, and decision logs carrying revision and decision identifier. There is no defined maximum staleness; unsigned bundles activate unless signing is configured.
2. Existing OCS. Decisions carry `rule_identity` and `reason_vocabulary_version` (`bounded.py:343-360`); opt-in profile fields are omitted when unset so default hashes stay identical; freshness clocks (`freshness.py`); the exchange generation fence; runtime in-transaction policy comparison; BitRep custody with epoch.
3. Missing. No acknowledgement of an active rule-set and evaluator digest by any component; no cross-component staleness or conflict detection; no rollback rule; `rule_identity` covers rule kinds, not the evaluator set or an epoch.
4. Reuse. Control Plane `rule_identity`; the three commit-bound mechanisms; Replay and Evidence Pack to carry the identity.
5. Implications. A distribution service would be a new trust root and availability dependency; keep it local. Publication is not activation. Keeping the old bundle on failure must not be copied without an epoch or age bound.
6. Minimum. Each decision records the rule-set digest, evaluator identifiers and versions, and activation epoch obtained by the component itself; a pure comparator reports mismatch, stale or unknown between two components; non-monotone epochs refused. No service.
7. Independent criteria. A decision identifies its rule-set from raw records alone; stale epoch holds; conflicting activation is detected, not merged; downgrade refused; offline restart uses the last activated rule-set only within a declared age bound, otherwise holds; publication without acknowledgement reads UNKNOWN, not ACTIVE.
8. Priority. Local subset v0.2 mandatory; distribution post-v0.2.
9. Disposition. ADAPT local subset; DEFER distribution service.

## CA-04 Enforcement coverage and bypass resistance

1. External pattern. The toolkit documents middleware-layer interception in Python and states it is not kernel-level; container separation is the isolation route. OpenAPPA also gates only calls routed through its hook. Repository-level claims unread.
2. Existing OCS. Hub OpenAPPA profile section 4 (every declared sink needs a hook or an explicit exclusion); runtime host-contract per-surface table (for the quarantined application, not the supported `engine/`); hub `tools/verify_embedding_exposure.py` (always `deployment_verified=false`); `tools/lifecycle_inventory.py`; Control Plane `holder_inventory.py`; runtime threat model statement that a separate host process can bypass the package.
3. Missing. No machine-readable per-effect-path declaration binding path, mediation point, enforcing component and revision, a test that detects a removed gate, and a status. No negative test that detects a missing gate on the supported `engine/` routes.
4. Observed. The supported path is `BoundedAuthorizationWorkflow.execute()` to a destination adapter to synthetic SQLite, with no outbound network client in any locked repository. Five surfaces accept direct calls or sit outside the gate (see [defects.md](defects.md)); none was executed.
5. Implications. Honesty value high, size small if declaration-only. A self-declared manifest is an assertion; independent enumeration is required before "all in-scope paths mediated" can be said.
6. Minimum. One JSON declaration per profile listing each in-scope effect path with an explicit unmediated and excluded list, validated by a hub tool in the style of `verify_embedding_exposure.py` (always non-authorizing). Seed rows from routes A, B and C, the OpenShell worker, the exchange transport, the OpenAPPA reply gate and the AGT adapter.
7. Independent criteria. Independent enumeration of effect-capable code paths in the frozen source; a removal-detection negative for each declared-mediated path; each undeclared effect-capable path fails; mocks and container-only tests never raise a status above application-level.
8. Priority. Declaration v0.2 mandatory; the plan row said optional while the minimum profile requires it, so this needs owner confirmation.
9. Disposition. ADOPT as declaration-only; REJECT any OS-confinement claim; DEFER enforcement beyond declaration.

## CA-05 Governed remediation and safe continuation

1. External pattern. The paper summary describes enumerated recovery routes, an authority ruling for the exact call that does not change the label, and an ablation showing utility depends on recovery. It reports no false-block rate or intervention count, so there is no source baseline for the measured comparison the brief asks for.
2. Existing OCS. `reopen_conditions()` (two kinds only, never permission to dispatch); 164-code reason vocabulary; Authority Context unknown behaviors; runtime unknown handling and recovery resolution; the proposed `AppaRemedyBridge`. The orchestrator holds no remediation code (183 non-adapter lines).
3. Missing. A closed remedy vocabulary across missing authority, incomplete evidence, restricted disclosure, unsupported capability and unknown effect; a remedy object bound to the denied operation with expiry and single use; any measurement harness for remedies.
4. Reuse. Control Plane reopen conditions and reasons; institutional-governance for competence; the comparative battery runner for later metrics.
5. Implications. Remedy objects are an authority-laundering surface. They must carry `authority_effect: none`, bind the exact denied operation, expire, be single-use, and enter the gate only through a newly issued grant.
6. Minimum. Extend the reopen-condition vocabulary by documented, non-executing kinds (design and schema); reuse the no-blind-retry and unknown-reconcile tests of step 3.5; no remedy executor.
7. Independent criteria. Forged, expired or replayed remedy has no effect; an orchestrator proposal never changes a grant, label or retry count (compare destination rows); each remedy kind lists its authorizing party; an unknown effect is never retried.
8. Priority. No-blind-retry and no orchestrator-minted grants v0.2 mandatory (already steps 3.1, 3.5); typed vocabulary optional; execution and metrics post-v0.2.
9. Disposition. ADAPT vocabulary; DEFER execution and metrics.

## CA-06 Canonical-state promotion and no-regressions

1. External pattern. The paper was not retrievable; only the owner's stated principles are used.
2. Existing OCS. `component-lock.json` with a preserved `previous_acceptance` chain; per-component requalification rules; `tools/check_contract_surfaces.py` and `contracts/qualification-surfaces-v1.json`; opt-in profile fields omitted when unset so default hashes stay identical; exact profile dispatch with no fallback; per-action `reversibility.py` (230 lines) and the ODES effect-reversibility contract.
3. Missing. A single declared promotion-boundary table (artifact class, promoting authority, required evidence, reversible or not); a machine-checkable compatibility gate for registry schema, rule-set digest, evaluator identifiers and decision-context fields; a reversible-internal versus irreversible-external classification for workflow and registry transitions. Live example of the regression class: the runtime pins Control Plane `2ea9528e` while the lock selects `0a41faa9`.
4. Reuse. Hub lock and contract-surfaces tool; qualification frozen oracles; Control Plane omit-when-unset pattern.
5. Implications. Low code, high process. The table must record, not decide, so it does not become a new authority.
6. Minimum. Promotion-boundary ADR table; extend the surface comparison to the new objects; rule that a change to a committed field is opt-in or declares a new profile identifier; classify v0.2 effects.
7. Independent criteria. A change to a committed field without a version bump fails; old records re-verify byte-identically under new code; promotion without a named authority and evidence is refused; internal rollback cannot restore revoked authority or undo a committed external effect; a lock-tuple change requires a requalification marker.
8. Priority. v0.2 mandatory.
9. Disposition. ADOPT as ADR table plus compatibility gate; paper-specific content REQUIRES INVESTIGATION before it is cited as a source.
