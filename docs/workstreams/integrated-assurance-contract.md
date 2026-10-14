# Integrated local assurance contract

Implementation date: 2026-10-14. Starting main:
`cdbd4ded73c6ecffda78942e4fbf4e62e0414893`.
Contract: `integrated-local-assurance/1`.

## Scope and relationship to earlier work

This implements an executable local reference for **all nine EGA addenda** in
one coordinated path. It extends the [six-paper requirement mapping](research-assurance-addenda.md)
beyond PR #102's three isolated checks. It does not describe the remaining six
requirements as completed merely because they were documented.

The profile has its own synthetic destination: a SQLite effect row. Identity,
current grants, ancestor budgets, data restrictions, exact review binding,
environment policy, custody limits and the effect are checked in one cooperating
writer transaction. This is an optional reference, not a replacement or silent
upgrade of the selected Control Plane/Execution Runtime or their component pins.
The existing context, resolver and evidence profiles remain independently usable.

The profile deliberately supports no external adapter callbacks, shell commands,
network requests or shared cache. It mediates all synthetic effects exposed by
its signed request interface. That is not a sandbox around arbitrary Python,
a claim about every process on the host, or proof of production-wide mediation.

## Executable coverage

| Addendum | Implemented mechanism | Required named acceptance evidence |
| --- | --- | --- |
| EGA01 execution boundary | Exact registered local-sink manifest, trusted observation comparison, expiring lease, refused unsupported routes/network/subprocess/cache surfaces, configuration-bound approval | Unknown route and unsupported surface refuse; observation drift and lease expiry prevent effects; changing environment policy invalidates prior review. |
| EGA02 payload disclosure | Steward-authenticated ingress, immutable payload/labels, parent restriction propagation, exact sink/payload declassification, execution-time expiry | Public sink cannot receive secret-labelled content without the separate exact record; label dropping and post-review payload replacement fail; an explicitly declassified exact payload succeeds. |
| EGA03 delegation and ordering | Run/holder/purpose binding; attenuated child sink/label/budget/depth/expiry; live ancestry; shared ancestor consumption; revocation and effect in one transaction | Parent revocation names revision 2 on refusal; two processes cannot spend the last ancestor unit twice; both revocation-before-effect and effect-before-revocation outcomes are retained. |
| EGA04 change admission | Bounded routing harness, immutable independently registered oracle, explicit operator oracle selection, changed-route coverage, improvement/regression limits, evaluation budget, separate proposer/evaluator/reviewer/activator | Unsafe routing regressions, missing oracle cases, stale oracle/base and edits outside the mutable surface fail; activation invalidates prior proposals; rollback follows the same current-oracle process without restoring grants or approvals. |
| EGA05 identity versus authority | Exact-request synthetic HMAC authentication, audience, nonce, expiry, persistent key version/enabled state, distinct logical principals and running instances; separately declared model provenance | Signature tampering produces no effect; old keys fail after restart/rotation; identical model declarations do not transfer grants; disabling a parent identity blocks child authority. |
| EGA06 evidence and custody | Transactional event/effect recording, chained journal, separate durable witness prefix, authenticated checkpoint intake, monotonic checkpoint count/time, event/time lag gate | Missing/stale custody prevents effects; gaps, forks and truncation fail witness acceptance; crashes before commit roll back, crashes after commit reconcile one effect without reapplication. |
| EGA07 review capacity | Configured reviewer availability/capacity/expiry, exact proposal commitment, distinct reviewer/actor, durable challenge dispositions, deadlines, review debt gate | Overload and absent reviewer block; even a dual-role principal cannot review its own request; unresolved or late challenges block approval/effect; retired reviewer key invalidates review. |
| EGA08 safe exit and correlated stop | Finite steps and stall deadline, incident-role stop independent of environment/custody availability, declared cohort closure, generation fencing, grant revocation, queue cancellation, separately reviewed restart | Stop wins against a waiting executor at the actual writer boundary; child runs stop together; new members cannot evade stopped cohort; stale restart reviews cannot override later stops; fresh grants required after restart. |
| EGA09 recourse | Immutable pre-effect obligations and recourse packets; compliant/violated/unevaluable record predicates; distinct evidence-availability result; authenticated adjudication and independent appeal decision; separately granted correction | Not-due/subjective/missing evidence stays unevaluable; packet or decision creates no payment/effect; appeal preserves history and blocks existing corrective grants until resolved; correction executes only through the normal controls. |

These are implemented mechanisms and local tests, not nine completed production
assurance cases. See the explicit deployment dependencies below.

## Trust model and initialization

`AssuranceRuntime.create(path, stream=..., principals=..., keys=..., clock=...,
observe_environment=...)` exclusively creates new storage. Reopen with
`AssuranceRuntime(path, ...)`; missing storage is an error, never fresh authority.
The host supplies a unique stream identity, trusted clock, observation adapter,
initial role/key assignments and fixture HMAC verification keys. Runtime keys are
not stored in ordinary events or request results; the database stores key digests
and current versions. Key custody and institutional adoption are not inferred.

The initial principal configuration is trusted bootstrap input. It is not an
agent-writable registration endpoint. Identity, declared model provenance,
reviewer qualification and institutional authority remain separate concepts.
Model provenance in this version must say `assurance: declared`; asserting
`verified` is rejected. No hidden-weight attestation or behavioral tamper detector
is claimed. Role grants in this API govern the isolated synthetic profile only.

The supported manifest is exact:

```json
{
  "adapter": "sqlite-local/1",
  "network": false,
  "subprocess": false,
  "shared_cache": false,
  "sinks": {"public": ["public"], "private": ["public", "secret"]}
}
```

The trusted observation adapter must produce the actual deployment observation,
not echo an agent request. Tests supply synthetic observations and deliberately
change them. This implementation does not discover host egress routes, enforce
OS firewall policy or attest an external model provider. Such adapters require
separate deployment qualification; do not represent a copied manifest as a
measurement of the host.

## Request and role contract

`apply` accepts exactly `{body, mac}`. The body contains `contract`, `stream`,
`actor`, `key_version`, `nonce`, `expires_at`, `operation` and `arguments`.
The MAC covers canonical JSON of the complete body, including all arguments and
the intended stream. `sign_request` is a synthetic test helper, not a credential
issuance service. Use the admitted current key version; repeated nonces fail.
Signed input is detached from caller-owned objects before evaluation.

| Role | Operations |
| --- | --- |
| operator | environment, run, grant, revoke, rotate, reviewer, select_oracle, activate_change, restart, obligation, appeal |
| steward | ingest, declassify |
| agent | delegate, queue, execute, observe, progress |
| reviewer | review, challenge, resolve_challenge, admit_change, restart_review |
| evaluator | oracle, evaluate_change |
| builder | propose_change |
| custodian | checkpoint |
| incident | stop |
| adjudicator | recourse, adjudicate, decide_appeal |

Separate configured identities are checked at consequential joins, not merely
separate role names. An agent cannot approve its own proposal even if bootstrap
assigns both roles. Change proposal, evaluation, review and activation require
distinct identities at their respective joins. Appeal review must differ from
the previous decision maker. Signing possession is not proof of human identity,
competence, institutional legitimacy or staffing independence.

Every operation accepts only its declared fields. Requests are limited to 1 MiB,
context text to 64 KiB, label sets to 64 entries, direct provenance parents to
eight, provenance depth to 32 and root delegation depth to 16. These are reference
bounds, not tested production throughput or protection against disk exhaustion.

## Delivery and authority path

1. An operator registers the environment and a named run/instance, purpose,
   declared cohort, finite step/stall bounds and declared model/configuration.
2. A steward admits immutable text, labels and parent identities. Derived content
   cannot weaken parent restrictions or extend parent expiry. The steward is a
   trusted source of classification; semantic transformation correctness is not
   inferred from a signature.
3. An operator issues the local run grant. A holder may delegate only to a named
   child run in the same cohort and exact purpose, with narrower sinks/labels,
   no greater budget or expiry, and strictly smaller depth. Every descendant
   consumes every ancestor budget at commit; grants cannot be redefined in place.
4. The agent queues an exact effect/run/grant/item/route/harness request. The
   binding also commits to the payload, sink, run generation and environment
   policy. Reviewer capacity is reserved by pending/approved unexpired entries.
5. A current admitted reviewer accepts or rejects that exact binding. Challenges
   must receive an explicit accept/override disposition; accepted challenges
   reject the proposal. A new unresolved challenge blocks a previously approved
   effect. Review timestamps allow local latency calculation.
6. Execution repeats current identity, run, environment, provenance, authority,
   ancestry, budget, disclosure, reviewer, challenge, deadline and custody checks.
   It consumes review and budgets with the synthetic effect in one transaction.

Ordinary audit events retain operation/actor, authenticated key version, object
references, request/result digests, time, status/reason and effect-time grant
chain snapshots. They do not copy raw payloads, signing keys or arbitrary
exception bodies. A revoked-parent refusal names the exact parent revision it
read. Effects retain their payload and decision evidence in the protected local
destination; exports and access control must account for that sensitive content.

The only effect type is a local row insertion. A duplicate effect ID with the
same reviewed commitment returns the retained observation and creates no second
effect; a conflicting commitment fails. Observation after revocation does not
renew permission. There is no external-delivery timeout in this adapter. An
interrupted caller can observe the destination after restart; no conclusion about
an external unknown effect is transferred from this local behavior.

## Change admission and rollback

The mutable harness has only `instruction_digest` and a route-to-sink map.
Instruction/model declarations are recorded metadata; no LLM is executed and no
natural-language instruction efficacy is evaluated here. The executable harness
behavior under test is deterministic routing. Security policy, keys, evaluators,
labels and grant rules are not mutable harness fields.

An evaluator registers immutable oracle cases and a finite comparison budget.
The operator explicitly selects the current oracle. Each case specifies the
expected sink or `null` for a refused route. Every changed route must be covered.
The evaluator measures improvement and regressions against that current oracle;
a rejected evaluated candidate consumes its comparison budget and remains
recorded. The builder cannot modify that oracle through the request interface.

Only a separately admitted exact candidate can activate, against its unchanged
base and still-current oracle. Open challenge debt blocks admission/activation.
Activation supersedes pending/approved effect proposals so reverting to an older
harness digest cannot resurrect them. Rollback is another proposal evaluated
against the current rule set, not a privileged bypass. It never restores revoked
grants. Provider/model drift evaluation and statistical holdout calibration for
an actual LLM remain a deployment-specific evaluation task.

## Evidence custody and failure semantics

Local event append and effect commit share the transaction. An operation denial
rolls back operation writes but retains its consumed authenticated nonce and
minimal refusal event. A process crash before commit rolls back nonce, effect,
budget and event; after commit, the effect and event survive together. This
assumes cooperating SQLite writers, durable storage semantics and an intact
host; hostile direct database modification and snapshot rollback are excluded.

`LocalWitness` uses a separate explicitly provisioned database. It verifies the
complete received hash chain and rejects gaps, forks and shortening below its
retained prefix, including after reopen. The custodian submits an authenticated
checkpoint with stream/count/head/observation time. Runtime admission checks
monotonic acknowledgment and configured maximum event/time lag. The pending
effect event counts against the event lag bound; the minimum configured bound is
two because acknowledgment itself is audited. Custody outage blocks new effects
once the bound is exceeded; it does not block the incident stop path.

A separate file/process operated on the same host is not independent custody.
The witness does not prove events were truthful, externally timestamped, or
immune to an administrator controlling both stores. Production deployment needs
a separately administered authenticated receiver and an explicitly measured
outage policy. The local test does establish capture consistency for the exposed
synthetic effect transaction under the stated host assumptions.

## Stop and restart

Cohort membership is declared, not discovered. Children must share the parent
cohort. Stop closes that cohort to new runs, stops all registered members,
advances generation, revokes their grants and cancels pending/approved proposals.
The incident control requires its own role and does not depend on working
observation or custody adapters. A barrier test exercises a stop holding the
writer lock while an executor waits. A prior committed effect remains observable.
`quiescent-local` describes this sole local destination, never remote cessation.

Finite step exhaustion or stall causes safe refusal without scope expansion.
Restart needs a separate current reviewer, exact remediation commitment and
operator action. A newer incident generation invalidates an older restart review,
including incidents at the same timestamp. Reopening runs does not revive grants,
keys or proposals. Remediation evidence is a trusted supplied commitment, not an
automated causal diagnosis or proof that human responders can intervene in time.

## Recourse and correction

An operator commits an obligation before the effect and before its deadline.
Supported predicates are effect presence, exact payload digest, evidence
availability and a subjective obligation marker. Before the deadline, or when
required evidence is missing or the obligation is subjective, the result remains
unevaluable. A failed evidence-availability obligation is explicitly labelled
`EVIDENCE_AVAILABILITY_ONLY`, not a behavioral misconduct finding.

Recourse packets and adjudication records are immutable. An owner can lodge an
appeal, and a different adjudicator records its disposition without rewriting the
prior decision. An open appeal blocks existing corrective grants; current remedy
approval is checked again at execution. A remedy decision alone performs no
payment, dispatch, authority restoration or retry. A separate operator-issued
grant plus ordinary review and all execution controls are still required.
No insurance funding, reserve sufficiency, external legal entitlement or real
settlement is implemented or claimed.

## Reproduction and retained evidence

From a clean checkout with Python 3.11 or 3.12 and pytest 8 or 9:

```sh
python tools/integrated_assurance_qualification.py --results-dir /tmp/integrated-assurance-first
python tools/integrated_assurance_qualification.py --results-dir /tmp/integrated-assurance-second
```

The runner requires 51 passing independent testcase elements, named cases for
every EGA group, all nine detected control removals and clean qualification source
paths. Five additional unittest subchecks are not added to the independent count.
It records exact source revision, source/lock digests, environment and outcomes.
A dirty checkout can run the tests but cannot report local qualification.

Each repetition retains JUnit, test output, mutation output, `qualification.json`
and `scenario.json`. The latter contains an actual permitted local effect and a
later refused effect after grant revision 2 revocation, destination observations,
minimal journal and witness receipt. It excludes keys and raw destination text.
The evidence runner asserts one destination effect and the exact refusal revision.
The report always preserves false release/production/independent-custody fields.
CI performs both repetitions on both Python versions at the exact PR head.

Nine disposable-copy mutation probes remove one control per EGA group and must
produce an assertion failure in the named test; a crash or import error is not a
successful detection. The existing PR #102, context-action and evidence-gate suites
remain separate regression populations and are not counted as new integrated cases.

## Migration and remaining deployment work

This adds new optional files. It does not rewrite old memory/events, change
`context-action-evidence/1`, select a new component generation, add a dependency
on an external chain, or activate a production path. Use separate paths for this
runtime and witness; it is not a migration reader for prior context databases.
Keep signing configuration, snapshots and witness continuity under host-owner
control. Never replace a lost authoritative database with an empty one and call
that restoration. An explicit new bootstrap is a new authority domain.

All nine reference mechanisms now have executable implementations. Production
acceptance still requires actual institution/workload identity and key custody;
trusted data classification and model/provider provenance; measured host/adapter
coverage; destination-specific commit guarantees; an independently operated
custodian; competent staffed reviewers and measured intervention deadlines;
incident drills across the real run population; and authorized adjudication.
Those depend on selected infrastructure and people, not merely additional unit
tests. This batch does not manufacture any of those acceptances.

Operational trust remains **HOLD / NOT ESTABLISHED**. Existing selected C0
check-to-commit limitations and optional same-host C1 remain unchanged. No C2/C3,
real settlement, public release/tag, production activation, live credentials,
external test messages or OpenAPPA work. `reference_release_authorized=false`
and `production_deployment_authorized=false` remain unchanged. Screening,
distribution rights, reporting delivery and final owner release acceptance are
separate open gates.
