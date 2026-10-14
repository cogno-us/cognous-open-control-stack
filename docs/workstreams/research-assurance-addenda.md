# Research assurance addenda

Review and implementation date: 2026-10-14. Starting hub main:
`45c1aa6f8bef5faa28ce70d38181901a0165c15c` (PR #101 merged).

This batch implements three bounded hardening changes and records all nine
requirements from the six-paper engineering addendum. It reuses the existing
[engineering register](../engineering-register.md), context memory and synthetic
resolver profiles. The October 5 consolidated recommendations are historical
input, not evidence that their original findings still exist. The current register
already records their later dispositions; those entries are not reset here.

## Implemented boundary

1. **Exact payload disclosure restriction.** An optional trusted-host gate on the
   existing context delivery path checks the actual text digest, exact receipt,
   configured sink and exposure, purpose, recipient and policy version against a
   currently resolved disclosure record. This is an additional restriction, never
   an action grant. A permitted recipient alone does not permit arbitrary content.
2. **Persistent resolver revision memory.** An optional SQLite ledger retains the
   highest authenticated, in-scope, fresh source revision for each source/object
   scope. Older revisions fail after reopen. A contradictory record at the same
   revision remains conflicted until a higher valid revision arrives. Key/profile
   rotation does not implicitly reset this floor.
3. **Retained journal coverage.** A context journal exporter and tri-state checker
   compare contiguous event sequence/count and an exact prefix digest with
   caller-held expectations. The checker reports missing journals as unevaluable,
   inconsistent records as violated, and an excessive uncommitted event tail as a
   separate custody-lag failure. These classifications concern record predicates,
   not proof that the agent violated a behavioral obligation.

These remain optional local reference mechanisms. They are not wired into the
default selected executor, production identity, Replay/AGEP/ODES consumers,
automatic review admission or deployment activation. The new tests are separate
from the existing seven-batch extension population and selected-release counts.

## Requirement mapping and acceptance

“Partial” describes bounded implementation, not completion of the whole
requirement. Proposed tests below are distinct from the named executed local
cases. No requirement becomes production-qualified through this table.

| ID | Existing register | This batch | Required remaining acceptance |
| --- | --- | --- | --- |
| EGA01 execution boundary | AGC02, OG02/03, RS02, IF01 | Specification only; existing inventory/environment tools remain bounded | T01: enumerate and mediate actual tool, subprocess, network, provider, log, cache, artifact, memory and child-agent paths; invalidate an environment lease on change; block an unregistered route and cross-run cache channel while preserving a permitted path. |
| EGA02 payload disclosure | IF01–06/08, context memory | Partial: exact binding checked in the actual local delivery route; revoked/mismatched/expired records prevent callback; refusal retains policy binding | T02: trusted labels across transformations and children, actual external sink binding, explicit declassification, error/URL/log channels and encoded disclosures. A canary test alone is not a general secret detector. |
| EGA03 delegation ordering | RS05/06, TCR03–05, AGC06/07, resolver assurance | Partial reuse: existing ancestry restrictions and new replay floor; no new grant tree or commit protocol | T03: child attenuation over actions/resources/sinks/purpose/expiry/depth; shared budgets; all current ancestors; deterministic revocation-before/at/after-commit cases at the actual destination. Preserve C0 where ordering cannot be enforced. |
| EGA04 change admission | OG02–04, ES01/05, DA | Specification only; existing exact-source and review gates retained | T04: approved old/new harness digests; independent current labels; protected holdout and repeated-comparison budget; reject evaluator/label edits and unsafe-clear regressions; rollback cannot restore revoked authority. No autonomous self-evolution is introduced. |
| EGA05 identity and authority | AGC01/03/07, SH04, resolver assurance | Partial: revision memory survives restart and key-profile change; old-key observations fail under new configured key | T05: production issuer/workload binding, key custody/withdrawal, source namespace continuity, compromise and backup rollback; distinct running instances cannot exchange authority because they use the same model. Behavioral drift is not runtime attestation. |
| EGA06 evidence sufficiency | ES01–04, MG04, AGC04 | Partial: actual retained journal export, count/gap/rewrite checks and event-based custody lag | T06: predicate-to-record coverage at each actual dispatch path, crash boundaries and independently retained acknowledgments; time-based outage policy; missing consent and missing terminal observations remain unevaluable. Hashes do not establish truthful capture. |
| EGA07 review capacity | SH02/03, AGC08, ES05, institutional review | Specification only; existing review history is not staffing evidence | T07: authenticate competent reviewers, prevent prohibited self-approval, retain challenge dispositions, bind exact proposal and deadline, overload queue and remove reviewer; consequential effects must pause rather than auto-approve. Measure latency and error rates. |
| EGA08 safe exit and stop | RS05/09, AGC09/10, OG05, TCR06/07 | Specification only; existing unknown-delivery behavior is preserved | T08: independent stop path across related runs, credentials, queues and callbacks; test monitoring loss/stall; reconcile population and late effects; require remediation evidence and fresh authority before restart. |
| EGA09 recourse packet | RS09/10, ES01, AGC09 | Specification only; tri-state record assessment can inform a later packet | T09: distinguish objective violation, evidence unavailability, disputed interpretation and subjective unevaluable obligations; authenticate adjudication; packet replay must not issue permission, payment or retry. Correction requires its own grant. |

Suggested owners: EGA01/03 deployment and destination maintainers; EGA02 data
steward and information-flow maintainer; EGA04 independent evaluation and release
owners; EGA05 identity maintainer; EGA06 evidence maintainer and separate
custodian; EGA07 review lead; EGA08 incident operations; EGA09 evidence/incident
maintainers with an authorized adjudicator. These are proposed responsibilities,
not claims that particular people have accepted them.

## Exact disclosure contract

Configure `PayloadDisclosureGate(sink_id=..., exposure=..., policy_version=...,
resolve=...)` on the trusted host and pass it to
`ContextMemory(..., clock=..., disclosure_gate=gate)`. The resolver receives a
copy of the computed binding. It returns exactly:

```text
binding: {payload_sha256, receipt_sha256, sink_id, exposure,
          policy_version, purpose, recipient}
grant_id: nonempty string
grant_revision: nonnegative integer
status: active | revoked (other values hold)
valid_from: finite numeric host time
expires_at: finite numeric host time, exclusive
```

`payload_sha256` commits to actual UTF-8 text bytes. `receipt_sha256` uses the
existing context canonical JSON encoding. This is not the executor's differently
prefixed receipt commitment format; do not interchange them. Policy resolution
must come from trusted host configuration, not an agent-supplied allow record.
No issuance or declassification API is added. An approved redacted payload needs
its own exact record; existing parent restrictions still apply to derived items.

The clock is read after resolver work, and context/ancestor expiry is checked
again before the durable delivery intent. The disclosure event records binding,
grant ID/revision and a specific reason without raw payload. A rejection commits
that event and the existing recall-denied event, creates no delivery intent and
never invokes the callback. An unavailable resolver, unknown status, malformed
record, revoked record, expired lifetime or mismatched binding cannot pass.
A callback error still leaves unknown delivery, never blind retry authorization.

The host must bind the configured gate to the same actual callback destination
and configure it again after reopen. Omitting the gate preserves the historical
profile, not the new disclosure guarantee. The gate does not authenticate labels,
inspect arbitrary generated summaries, enforce transformation correctness, count
shared disclosure budgets or retract bytes already sent. A policy revocation
after local admission can still race callback delivery: C0 remains. The local
context transaction is not atomic with an external destination or policy store.
Receipt/source metadata and digests may be sensitive even without payload text.

## Persistent revision memory contract

Provision once with `RevisionLedger.create(path)`. Reopen existing storage with
`RevisionLedger(path)` and pass it as `revision_ledger=...` to
`resolve_observations`. The source identity plus exact institution/domain/object/
scope binding forms the ledger key. Profile/key versions deliberately do not:
trusted rotation must preserve the namespace and monotonic revision contract.
The configured static minimum revision remains enforced as well.

Only authenticated, in-scope, fresh, structurally valid records advance the
ledger, including legitimate `UNKNOWN`, revoked and suspended statuses. Malformed
records now retain no observation body. Same-revision semantic facts include
status, facts digest and effective time; refreshed observation/expiry timestamps
may differ without resetting semantic history. Same-revision disagreement stays
conflicted across reopen; only a higher valid revision clears that conflict.
A SQLite immediate transaction serializes cooperating readers/writers updating
the floor. Missing/corrupt/unavailable storage holds as unknown and is never
silently recreated. An existing path cannot be reinitialized by `create`.

A compromised source can still issue false higher revisions. A database owner
can tamper with or roll back storage. Explicit reprovisioning, namespace changes,
trust-root adoption and backups require governed procedures outside this class.
There is no cache, continuous clock reevaluation, live destination binding or
external atomicity. A successful observation can become stale after it returns
and is always `authorizes_execution: false`. The non-ledger API remains available
with its original static-floor limitation. No default component pin changes.

## Journal evidence contract

`export_context_journal(memory)` reads one SQLite snapshot of the existing
`events` stream into `context-journal/1`. It exports sequence, kind, item identity
and retained detail, excluding raw context content by the existing event design.
It is a whole-stream administrative export; it is not a tenant-filtered API or a
redactor for arbitrary host-written event bodies. Restrict access accordingly.

Call `assess_context_journal(package, expected_count=..., checkpoint=...,
max_uncommitted_events=0)` with independently retained caller expectations.
`checkpoint` contains `count` and the SHA-256 of canonical JSON for that exact
prefix. `expected_count` must describe the expected full stream at the chosen
snapshot; deriving either value only from the received package defeats omission
or coherent-rewrite checking. Compare a matching snapshot rather than a moving
head. The configurable lag bound is an event count, not a time guarantee.

Outputs separately classify `record_coverage`, `checkpoint_match` and
`custody_lag` as compliant, violated or unevaluable. A missing package is
unevaluable; count/gap/order errors violate the record contract; a rewritten
prefix violates its checkpoint; excess tail violates the lag bound. A passing
record check does not prove the original events were all captured or true. Every
output keeps authorizing, independent custody, capture completeness and
production-ready flags false. No adjudication or behavioral verdict is inferred.

No existing context-action export schema, event row or historical receipt is
rewritten. Missing historical terminal outcomes stay unknown; the journal does
not manufacture them. Independent custodian authentication and trusted expected
population are external inputs, not mechanisms supplied by this batch.

## Qualification

Run from the repository root:

```sh
python -m pytest -q tests/test_research_assurance.py tests/test_resolver_assurance.py tests/test_context_memory_profile.py
python tools/research_assurance_mutations.py
```

The new suite has 30 independent test methods, plus parameterized subchecks. The
scoped combined suite has 71 collected tests; do not add the 45 unittest subchecks
to that independent-test count. Tests exercise actual local SQLite state and the
context delivery callback, not real external endpoints. Four disposable-copy
control-removal probes must detect removed payload binding, revision-floor,
checkpoint and tail-count protections; import/loader errors do not count as a
successful mutation detection. CI runs the scoped suite on Python 3.11/3.12,
records the exact head and lock digest, and retains JUnit and mutation output.
Existing context-action and extension gates provide regression coverage on the
actual pinned local executor; their population is not inflated by the new suite.

For later T01–T09 qualification retain exact source/adapter/lock versions, declared
boundary, expected and observed effects, grant/policy revisions, failure cases,
coverage exclusions and controlled timing. Pair refused paths with permitted
controls. An audit refusal alone is not proof of zero destination effects.

## Paper evidence and timing correction

The source set is the supplied six-paper review, not a legal or incident-fact
verification. Paper claims do not transfer as Cognous qualification evidence.
Only the following narrow engineering implications are adopted:

- **P1 DelegateGuard: Purpose-Bound Capabilities for Delegated LLM Agent Workflows**,
  Tran-Truong and colleagues, pp. 5, 11–15: content-blind permissions can leak via
  permitted sinks; trusted labels and full mediation are assumptions; prototype
  expiration is omitted. The paper reports residual leakage, not immunity.
- **P2 From Reactive Containment to Proactive Assurance**, Raftari, sections 8–18:
  independently enforceable boundaries, safe exits and measured intervention.
  Its risk model is conceptual, not a calibrated admission score.
- **P3 Holding Agents Accountable with Verifiable Agent Insurance**, Hua and
  colleagues, Table 1 p. 8 and Appendix C.1: 42.2% measured detection versus 83.0%
  potential coverage with added records; faithful instrumentation and verifier
  independence are assumptions. Buffered uncommitted records can be lost.
- **P4 The Harness as the Only Mutable Surface**, Akhtyamov, sections 3–8:
  independent current labels and bounded change admission. The experiment uses
  a synthetic deterministic proposer, not an LLM self-improvement deployment.
- **P5 Who Can Say No**, Rosenbacke and colleagues, sections 5–10 and 14:
  challenge records and effective stop authority. This is an institutional
  proposal, not measured reviewer effectiveness or an assignment of legal liability.
- **P6 Who is the I in AI**, Ramil and colleagues, sections VI–VIII and X–XI:
  distinguish provenance, behavior, key possession and delegation. Corollary 5
  p. 13 does not establish its expanded in-window revocation timing inference.

For P6, let opening time be 0, challenge duration 64 blocks, finality latency
20 blocks and revocation submission 60. Finalization can occur at 80, after
eligibility at 64. `64 > 20` does not imply `60 + 20 < 64`. The narrower
pre-window claim can hold under a hard end-to-end bound and other assumptions;
“maximum expected” latency is not a deterministic bound. The worked example on
p. 14 already acknowledges a late revocation race. Test actual effect ordering;
a delay or cache invalidation does not establish external commit atomicity.

## Release disposition

Operational trust remains **HOLD / NOT ESTABLISHED**. Preserve C0 check-to-commit
limitations, optional same-host C1, no C2/C3 and no real settlement. Selected
component-lock and profile, `reference_release_authorized=false` and
`production_deployment_authorized=false` are unchanged. No release/tag, production
activation, credentials, external test messages or OpenAPPA changes. This batch
closes no security screening, distribution rights, reporting-channel or final
owner publication-acceptance gate.
