# Agent governance engineering controls

Review date: 8 October 2026 UTC. Engineering planning update for André de Lima and Cognous maintainers. Inspected hub main: `13817b1c5a2ddff08c9302f47051ee4df21f054f`. This is the detailed extension of the [canonical engineering register](../engineering-register.md#agent-governance-controls-and-operational-completion).

The stack has implemented bounded reference foundations for these controls. Operational completion still requires authenticated identities, deployment adapters and demonstrated intervention. The ten AGC identifiers below are new Cognous planning identifiers; they do not replace earlier requirement IDs. Accountable roles are proposed responsibility allocations, not assertions that a person has accepted an assignment. Acceptance cases are required future evidence, not tests executed by this documentation update.

## Evidence baseline and status rules

Inspection covered the current register, lock, profile contracts, inventory checker, institutional review and temporal reference implementations, and their test definitions. It was a targeted inspection, not a fleet audit, credential audit or new runtime qualification campaign. “Needs to be built” means the capability is not established by this accepted reference evidence; deployment discovery may identify reusable implementation elsewhere.

The selected Control Plane is `d3dadee70bd319812b207389ab1e0f6efe511916`; Execution Runtime is `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac`. [Hub PR #42](https://github.com/cogno-us/cognous-open-control-stack/pull/42) merged the integrated profile repairs at the inspected hub revision. The accepted extension contract requires 91 profile cases and 26 gate cases; these populations do not prove the new AGC acceptance cases. Existing inventory, resolver, handoff and provenance checkers have separate scopes and evidence.

Built reference means executable accepted behavior within its named synthetic profile. Partial means only a subset of the operational control is established. Production completion remains deployment-dependent. A structural record check, retained digest or favorable review does not establish live enforcement, source authenticity, independent truth or institutional authority.

## AGC01 Accountable agent ownership

**Status:** Partial reference; operational ownership and intervention open.

**Built:** The [inventory checker](lifecycle-inventory-reconciliation.md) retains owner and backup-owner references, logical agents, instances, lifecycle state and accepted release; missing owners produce findings. The [deployment packet](../deployment-review-packet.md) requires responsibility owner references. These are supplied declarations, not authenticated people or proof they can intervene.

**Needs to be built:** Bind owner and deputy to authenticated institutional identities, current organizational membership, precise tenant/environment scope and a documented intervention route. Require accepted responsibility, controlled ownership transfer and departure handling. Join execution evidence to the inventory identity and accountable owner without replacing existing operation/instance IDs. Verify visibility, authority and the actual intervention lever independently.

**Owner and dependencies:** Institutional and deployment owners; OG01, SH03, DA R5/R6 and AGC03/09/10. Reuse inventory rather than create a second owner registry.

**Acceptance:** Missing/departed owner holds admission; deputy works only within adopted authority; cross-tenant owner cannot intervene; ownership changes preserve history; a named owner without a working lever cannot satisfy the control.

## AGC02 Enforced access and action scope

**Status:** Partial reference; real identity and universal mediation open.

**Built:** Manifest and selected Control Plane describe and validate bounded actions; explicit execution profiles enforce operation/claim binding and scoped synthetic budgets. [Atomic execution](../optional-execution-profiles.md) orders participating local authority state, consumption and the synthetic effect. This does not enforce every external credential or prevent direct destination access.

**Needs to be built:** Join authenticated workload identities, grant permissions, credential scopes, adapter actions and destination permissions. Inventory direct and delegated routes; enforce least privilege and deny unknown/unmediated routes. Publish the supported policy semantics and current activation generation per adapter. Qualify actual read/write permissions at each production destination.

**Owner and dependencies:** Security, Control Plane, Runtime and adapter owners; OG02/03, ER01/04/06, IF03, AGC03/06/07. Credential possession must not become action authority.

**Acceptance:** Wrong tenant, resource, actor, action, argument or current generation prevents the effect; stronger credentials cannot bypass the governed route; direct/alternate-route tests either demonstrate prevention or remain an explicit deployment blocker.

## AGC03 Registered purpose and deployment behavior

**Status:** Partial reference; authoritative discovery and behavioral inventory open.

**Built:** OG01 reconciles supplied agents with workload/instance bindings, owner/release, freshness and connector coverage. It detects unregistered replicas and mismatches. Manifests and examples describe named actions; there is no accepted fleet-wide purpose/connection/data-flow register or live discovery guarantee.

**Needs to be built:** Extend the existing inventory through a versioned contract with purpose, permitted tasks, connected systems, data recipients/flows, autonomy bounds, delegated relationships, approved configuration and review dates. Collect real deployment observations, retain coverage gaps, and use governed admission for unauthorized or changed deployments. Keep logical identity, instance identity and business intent distinct.

**Owner and dependencies:** Deployment/integration and data owners; OG01, SH04, RS02/06, IF01/02. Review purpose/configuration changes without silently inheriting old acceptance.

**Acceptance:** Undeclared replica/connection, changed purpose, missing data-flow declaration and stale discovery hold the relevant deployment; unavailable connectors remain unknown; an empty supplied inventory never proves no agents exist.

## AGC04 Execution and outcome evidence

**Status:** Partial reference; complete production telemetry and useful-outcome measures open.

**Built:** Selected execution/recovery paths retain bounded decisions, attempts and effect observations; Replay/Evidence Pack support their declared consumer profiles. Optional record consistency checks compare exact operations and retained local effects. Extension evidence requires exact source/lock and complete case populations. Unknown acknowledgement holds temporal continuation. Optional extension artifacts are not automatically qualified consumer-chain exports.

**Needs to be built:** Define a versioned production event contract joining agent/instance, owner binding, task, operation, grant/policy/approval references, attempt, acknowledgement, observed effect and recovery state. Preserve denied, held, failed, cancelled, unknown and missing observations separately. Declare destination visibility/finality and coverage. Measure useful completion, latency, errors, unresolved outcomes and review effort separately from successful blocking. Add purpose-limited reporting and protected evidence references.

**Owner and dependencies:** Runtime, Replay, Evidence Pack, adapter and qualification owners; ER08, ES01–04, RS01/07/08/11/12, A-E2/A-E5, F1–F4 and AGC09. Do not create unbounded payload logging.

**Acceptance:** Missing/duplicate/out-of-order events, substituted operation, unavailable observer, partial population and unknown delivery remain explicit; denied execution is not useful task completion; retained digests alone cannot establish truthful observations.

## AGC05 Verified retirement and offboarding

**Status:** Partial inventory/recovery foundations; end-to-end retirement open.

**Built:** Inventory recognizes inactive/retiring/retired states and reports lifecycle holds, without enforcing admission. Local grant invalidation and retained consumption support bounded enforcement. Staging restore preserves tested revocation and consumption state. None establishes fleet cessation or secret removal.

**Needs to be built:** Implement an authorized retirement workflow: close new admission, invalidate grants and credentials, resolve or hold queued/in-flight work, reconcile committed/unknown effects, remove integrations, and retain immutable identity/tombstone and evidence references. Distinguish disabled, unreachable, ceased and retired. Apply approved retention and restoration rules without erasing consumed claims or unresolved effects.

**Owner and dependencies:** Operations, security and authority owners; OG01, RS09, TCR-5/6, AGC07/09/10. Retirement uses shutdown verification; it is not satisfied by deleting a register row.

**Acceptance:** Queued work, late callbacks, orphan replica, restart and stale restored state cannot reactivate retired work; unknown external outcomes remain unresolved; tombstones and historical effects survive offboarding; completed retirement requires evidence for the declared population.

## AGC06 Current runtime authorization

**Status:** Built bounded local profile; production effect-boundary coverage open.

**Built:** The explicit atomic-authority-effect profile uses a trusted Control Plane handoff and authoritative same-host SQLite ordering for current grant/policy state, expiry, claim consumption, budget and synthetic effect. Context-action adds bounded receipt/generation/envelope/claim binding and expiry enforcement. Default source selection does not automatically activate these profiles. Refund-intent ownership remains a separate, mutually exclusive database profile.

**Needs to be built:** Select the profile per deployment and qualify exact deployed source/configuration, authenticated authority inputs, trusted clocks and every participating writer. Bind final consequential inputs and adapter identity through declared interfaces. For external destinations, implement or explicitly bound validation/consumption/effect ordering; a fresh check alone cannot eliminate the race. Apply current authority at delegation, continuation and correction boundaries.

**Owner and dependencies:** Control Plane, Runtime, authority source and destination owners; ER01–08, TCR-1/3/7, RA-02/03 and AGC02/08. Reuse the existing authority path; do not add a parallel authorizer.

**Acceptance:** Revocation, expiry, policy/approval change, substituted operation, replayed claim and budget contention prevent effects within the declared ordering. Preserve earlier committed effects. Characterize external races and nonparticipating writers explicitly; no distributed or notification atomicity follows from the local refund profile.

## AGC07 Credential lifecycle and custody

**Status:** Deployment responsibility recorded; operational lifecycle not established.

**Built:** Deployment responsibilities and packet intake request identity/key-custody evidence. Inventory separates logical agent, workload and instance identities. Synthetic actor/reviewer/resolver identities are fixtures. Grant validity and credential validity are different controls; this reference does not establish production issuance, custody, rotation or revocation propagation.

**Needs to be built:** Integrate the deployment's workload identity and secret manager. Record non-secret credential IDs, issuer, subject, scope, validity, version, custodian and rotation/revocation evidence. Use dedicated least-privilege identities, protected custody and bounded credential caching. Define overlap during rotation, compromise response, owner departure and retirement. Invalidate runtime grants where adopted policy requires it; verify both access revocation and authority withdrawal independently.

**Owner and dependencies:** Security/IAM and platform owners; OG01/02, RA-03, AGC02/05/06/09. Reuse existing IAM rather than build a competing secret store.

**Acceptance:** Expired/revoked/wrong-scope/wrong-tenant credentials fail at the destination; cached credentials obey measured withdrawal bounds; authorized rotation preserves continuity without widening scope; compromised identity cannot restore itself; logs contain no secret values.

## AGC08 Approval and human intervention boundaries

**Status:** Partial exact-proposal and review reference; live institutional workflow open.

**Built:** Temporal fixtures obtain separate proposal-bound approvals, decisions and consumable claims for independent consequences. Institutional review admits exact configured reviewer identities, preserves dispositions/history and requires explicit critical-incident dispositions for acceptance. Review outputs remain non-authorizing and do not mutate runtime grants. Reviewer configuration is trusted-host membership, not production authentication or capacity scheduling.

**Needs to be built:** Define which actions require approval, the competent reviewer role and separation rules, and exact binding to candidate, scope, policy generation, deadline and evidence. Integrate authenticated review, withdrawal, timeout/reassignment and bounded capacity admission. Convert an adopted approval through the existing grant lifecycle; approval or favorable competence evidence must never itself dispatch an effect. Qualify the actual reviewer lever and current approval at the protected boundary.

**Owner and dependencies:** Institutional/review owner and Control Plane; SH02/03, DA R1–8, ES05, RA-02 and AGC06. No automatic approval on timeout or automatic authority expansion.

**Acceptance:** Wrong reviewer, changed candidate, expired/withdrawn approval, duplicate use, changed policy and unavailable reviewer hold/deny the action; contention for the last review slot is atomic; no timeout bypass; restoration requires a competent new decision and applicable current runtime authority.

## AGC09 Incident response and evidenced closure

**Status:** Partial retained assessment/history; operational response open.

**Built:** Institutional review retains critical-incident flags, references and explicit dispositions; deployment packet intake requires incident-response evidence. Denial/unknown records and recovery foundations can supply inputs. OG05 and RS09/10 remain operational proposals; no live incident route, acknowledgement or containment completion is established.

**Needs to be built:** Define incident triggers/severity, correlate protected event references to deployment/agent/operation/authority versions, and deliver through an authenticated operations adapter. Retain delivery, acknowledgement, investigation, authorized containment, observed intervention and closure evidence. Handle retries/outages without losing events. Keep corrective effects and restart separately authorized; alert clearance or successful requalification cannot restore authority.

**Owner and dependencies:** Security operations, operational and authority owners; OG05, RS09/10, DA R4/5/6, F1/F2, AGC04/07/08/10. Minimize sensitive incident payloads.

**Acceptance:** Duplicate, delayed and reordered events preserve one correlated history; unavailable endpoint escalates visibly; unknown suspension cannot be labeled contained; closure rejects missing intervention evidence; corrective action uses its own valid grant; unresolved effects survive alert clearance.

## AGC10 Shutdown and cessation verification

**Status:** Built undispatched-continuation hold; acknowledged and verified cessation open.

**Built:** The temporal cancellation scenario holds a second undispatched consequence and preserves the first effect. It explicitly reports cessation as unverified. Local revocation can prevent subsequent participating effects; inventory inactivity is a finding, not proof of stoppage. Neither cancellation-request recording nor a process exit proves fleet or destination cessation.

**Needs to be built:** Define separate durable states for stop requested, delivery acknowledged, admission closed, execution quiesced, destination reconciled and cessation verified. Bind a stop epoch to the scoped inventory, replicas, queues, delegation and callback population; record observer coverage and deadline. Demonstrate no further preventable effects within the declared destination contract, retain late/unknown effects, and require separately authorized restoration using current state and high-water marks. Add deployment adapters for real cancellation and observation.

**Owner and dependencies:** Runtime/orchestration, platform and destination owners; TCR-5/6/7, RS09, OG01/05, AGC03/05/06/09. Shutdown does not roll back historical effects; compensation needs separate authority.

**Acceptance:** In-flight work, late commit after acknowledgement, disconnected replica, queued callback, network partition, crash/restart and stale restore are tested. Request or acknowledgement alone cannot pass; incomplete observation remains unknown; verified cessation names its exact population/window and residual reach; restart cannot reset consumed claims or inherit old approval.

## Sequencing and completion rule

1. Extend the accepted inventory and owner bindings (AGC01/03), using a named staging deployment and IAM owner. Discover the real effect/credential routes before selecting enforcement claims.
2. Qualify access, credential lifecycle, current authorization and approval on one bounded destination (AGC02/06/07/08). Address deployment blockers before allowing production effects.
3. Connect execution evidence to incident handling and verify shutdown/retirement (AGC04/09/10/05). Preserve historical and unknown effects through recovery and restoration.

The ten controls are required design topics for the proposed agent deployment profile, not new gates retroactively imposed on the completed synthetic release. They remain open until the relevant implementation, selected configuration and required acceptance evidence agree at exact revisions. Discovery of reusable code changes the implementation plan; it does not remove the need to qualify its deployment behavior.

## Source and publication boundary

The initial five topics follow the prior discussion of [AI BCF](https://aibcf.org/controls/) version 1.0 and its inventory, access, accountability, tracking and offboarding themes. The runtime authorization, credential lifecycle, approval, incident and shutdown requirements are the user's requested engineering extensions. The requirements and acceptance cases above are Cognous engineering proposals in original wording; no external conformance or endorsement is asserted. No legislative mapping is included.

This update changes documentation only. Accepted component pins, runtime implementations, workflow protections and historical evidence are preserved. Executor dependency PRs #29–#31 have no acceptance or pin change through this register. The attached consolidated recommendations remain unchanged; prior CR, ER, ES, RS, IF, MG, GC, TCR, DA, OG, SH, RA and F identifiers remain traceable.
