# Engineering addendum for federated governance and state continuity

Date: 2026-10-14. Reviewed baseline: `e8491eb31e35577693906cab8fedb95f58a75ae3`.

## Decision and scope

The ten papers motivate eight engineering work packages beyond the integrated
local assurance profile. Implement them as an opt-in extension to that profile,
with executable negative cases and an independent evidence-consumer interface.
Preserve selected component pins, C0 limitations, optional same-host C1, no C2/C3,
no real settlement, and operational trust HOLD / NOT ESTABLISHED. Neither this
addendum nor local test success authorizes a public release or production.

These are engineering deductions from the supplied papers. The papers' empirical
results, novelty claims and institutional assumptions are not Cognous validation.
The earlier consolidated recommendations remain background; repository code and
new acceptance tests determine completion.

## Source review

Page numbers below refer to PDF pages, counted from one. Sources were read from
the supplied files; no source PDF or private implementation is distributed here.

| Source | Relevant contribution | Engineering use and limits |
| --- | --- | --- |
| S1 Li and Xia, When Agentic Trust Crosses Organizational Boundaries, sections IV-VII, pp. 6, 8-14; arXiv 2609.22961v1 | Immutable manifests, issuer-attributed attestations, relying-party policy, disclosure gaps, historical status and challenge | Verify evidence under consumer-owned trust configuration; hashes and signatures do not establish truth, completeness or independent administration. |
| S2 Wang and Liu, Software Engineering in the Agent Era, sections 4 and 7, pp. 13-15, 23-27; arXiv 2609.04630v1 | Candidate, eligible and accepted change states; joint residual-risk acceptance; context invalidation | Bind every required acceptance domain to exact change and authoritative fact versions. Distinct keys do not prove institutional independence. |
| S3 Shariff, The Authority Resolution Framework, sections 3.1-3.2, 3.7 and 4, pp. 8-9, 14-19 | Actor/action/object/context/justification relation across social, business, process, machine and real-world domains | Check explicit object identity and context consistency. Leave DNA-coefficient uncalibrated; informal influence never grants authority automatically. |
| S4 Canale, The Last Human Gate, sections 3 and 5, pp. 6-8, 13-14; arXiv 2609.29345v1 | Information, validity and mandate prerequisites; conditional findings survive handoff; total residual work | Carry unresolved conditions through admission and require closure evidence. Count review, exceptions, verification, correction and support separately; no workforce-saving claim from test success. |
| S5 Fernandez, Identity-Bound Governance Under Execution Uncertainty, sections 3 and 5, pp. 4-7, 11; arXiv 2610.00787v1 | System evidence and human decision bound by Ed25519 signatures; freshness, semantic uniqueness, threshold governance | Require distinct configured signers over the same incident decision before restart. Cryptographic attribution is not proof of human identity or truthful evidence. |
| S6 Sarker, A Mathematical Framework for Legacy Governance and Decision Integrity, sections 6-10, pp. 7-10; arXiv 2609.00572v1 | Authority and jurisdiction hard filters before ranking; confidence separated from consequence; decision memory and freshness | Refuse stale, superseded, conflicting or wrong-context authority. Do not adopt uncalibrated aggregate legacy/confidence scores or interpret law. |
| S7 Ferreira, When Intelligence Becomes Agency, sections 4 and 8, pp. 23, 30, 33-35, 60; arXiv 2609.07741v1 | Standing revocable mandate, consent-gated acquisition, inspectable activation and recorded restraint | Record act/ask/monitor/defer/refrain decisions separately from effect authorization. No affect inference, autonomous planner or psychological agency claim. |
| S8 He and Yu, The Cognitive Continuity Test, sections 3-4 and 11, pp. 2-4, 10; arXiv 2610.00132v1 | VALID/INVALID/INDETERMINATE; historical policy binding; candidate persistence separate from activation; current-head fencing | Apply deterministic typed mutations, preserve history, verify evidence, then atomically compare-and-advance head. This tests records, not consciousness, personality or cross-model behavior. |
| S9 Zou et al., AgentKernel, sections 4.3-4.5 and 5, pp. 13-17, 21; arXiv 2609.29647v1 | Item-level provenance, separate integrity/confidentiality labels, explicit sharing, plan/trace comparison, mandatory mediation assumptions | Preserve source integrity through derived items and keep retrieved content non-authorizing. Reuse local-only effect mediation; no eBPF implementation or OS isolation claim. |
| S10 Annapureddy and Thamatani, PRIMUS, sections 2-5 and 13-17, pp. 3-5, 12-13; arXiv 2609.07910v1 | Participation versus contribution truth, epoch fencing, explicit quorum and availability assumptions | Count distinct permitted signers, reject duplicate/key alias quorum inflation, persist fences. Do not import prime identities, BLS/VRF, economic crossover or noise thresholds without a deployment need and calibration. |

## Gap and acceptance register

| ID | Baseline gap | Required change | Acceptance cases |
| --- | --- | --- | --- |
| FGA01 | Same-host witness checks integrity but has no relying-party envelope contract | Public-key signed, immutable manifest and typed attestations; consumer-supplied audience, purpose, accepted issuers, required claims, evidence commitments and status policy; explicit disclosure view | Tamper, wrong audience, issuer substitution, duplicate IDs, missing required record, contradictory evidence, unavailable evidence, over-disclosure and revoked key; historical evaluation distinguished from current reliance. |
| FGA02 | Harness evaluation/admission has one reviewer and no multi-anchor closure | Predeclared responsibility domains sign exact candidate plus dependency snapshot; retain open conditions and separately reviewed closure records; revalidate before activation | One missing anchor stays pending; duplicated signers/keys do not satisfy quorum; stale facts or conditional finding block; passing tests cannot substitute for acceptance. |
| FGA03 | Run/grant purpose lacks cross-domain object and authoritative-source resolution | Versioned source facts and five-domain object bindings; explicit context, source class, effective interval, review deadline and conflicts; bind facts at review and effect | Object mismatch, wrong context, supersession, stale source and conflict block even with high declared confidence; unavailable evidence is distinct from contradiction. |
| FGA04 | Restart is HMAC-authenticated with one reviewer and no portable joint decision | Ed25519 decision bundle over exact stop evidence, stream, generation, remediation, decision, event ID and expiry; distinct configured principals; persistent one-use acceptance | Tamper either block, replay after reopen, expired bundle, wrong incident/stream, duplicate signers, fewer signers, DENY and later incident; none resumes. Normal fresh-grant rules remain. |
| FGA05 | Memory has receipts but no candidate-to-authoritative-head state transition | Persist immutable candidate; deterministic typed state changes, immutable policy/history commitments, ternary verification; atomic head comparison and generation fencing | Missing evidence indeterminate; contradictory evidence invalid even with missing evidence; modified history/norms rejected; concurrent successors cannot both activate; replay and restart recover one head; old grants remain invalid. |
| FGA06 | Confidentiality labels do not distinguish origin integrity or perception consent | Steward-owned source metadata, run/purpose/channel consent, parent integrity propagation and data-only retrieval; no content-derived permission | Signed untrusted content remains untrusted; derived content cannot promote integrity; wrong channel/purpose/run or revoked consent prevents retrieval; attempted injection cannot create grants. |
| FGA07 | Every execution is reactive and has no explicit mandate/activation decision | Operator-owned versioned mandate with allowed modes, channels, risk ceiling and expiry; inspectable episode decision; explicit restraint; current mandate binding at effect | Refrain/defer records zero effects; inferred intent or urgency cannot create authority; revoked/changed mandate invalidates earlier activation; act still needs all existing effect gates. |
| FGA08 | Review latency omits conditional handoff and complete human-work accounting | Immutable gate-work entries with explicit categories and denominator-aware reporting; decision records retain unresolved conditions | Missing work categories yield incomplete report; zero output yields N/A; automation cannot erase exceptions/support; closure requires separate evidence and exact candidate. |

## Implementation contract

Use `FederatedGovernanceRuntime` as an explicit opt-in subclass of
`AssuranceRuntime`; new databases have immutable bootstrap trust configuration.
The original profile retains its existing API and behavior. New profile grants
remain synthetic and local. All new mutations use its authenticated request,
nonce, role, refusal-journal and SQLite transaction boundary. No new external
effect adapter is introduced.

Portable signatures use Ed25519 with public verification keys only on the verifier
side. The signed encoding is a domain-separated, ASCII-key/string, integer-only
canonical JSON profile with sorted keys and no whitespace. It rejects floats,
non-ASCII, oversized/deep values and integers outside the interoperable safe range.
This is explicitly not a full RFC 8785 implementation and not APB wire compatibility.
Private fixture keys remain solely in test clients. Existing HMAC transport remains
a trusted-host simulation, not a production credential boundary.

Evidence consumers receive only disclosed envelope data, independently supplied
trust configuration and evidence resolver results. `INVALID` takes precedence
over `INDETERMINATE`; only `VALID` is evidentially admissible. Every result is
non-authorizing. Producer signatures alone cannot prove completeness; required
claim identities and independently committed evidence must come from the consumer.
External truth, status anchoring and independence remain deployment obligations.

The profile records candidate persistence separately from activation. Activation
must check current predecessor, policy and evidence, advance a monotonic generation,
revoke old run grants and cancel old proposals in the same local transaction.
Past verification never grants a currently active runtime identity.

## Deployment work that remains

Actual organizational signatory appointment, jurisdiction interpretation, source
truth, key custody, independent status/custody services, production host isolation,
real model migration, semantic evaluator accuracy and human staffing calibration
require qualified owners and deployment evidence. The addendum does not manufacture
those facts. All paper-specific performance numbers remain source claims.

## Verification and handoff

Run the new adversarial suite and control-removal probes, then the existing
integrated assurance suite and preview checker. CI must use the exact PR head,
repeat on Python 3.11 and 3.12, retain JUnit and qualification results, and fail when
a required test, control probe or source binding is absent. Report independent
testcase elements separately from unittest subchecks. Keep the selected lock and
authorization files byte-for-byte unchanged.

## Implemented interfaces and bounded acceptance

The implementation is in `reference_profiles/federated_governance.py` and
`reference_profiles/trust_evidence.py`. The base runtime adds only an overridable
role map and a binding-extension hook; its default behavior is preserved.

- FGA01: `assess_envelope` consumes public signatures, explicit disclosure,
  consumer-owned expected claims and independently supplied evidence contents.
  The test consumer reads no runtime database. Historical mode reports an old
  evidence proposition; it never authorizes present execution. Compromise dating
  and registry status must come from a trusted external source in deployment.
- FGA02 and FGA08: `change_context`, `accept_change`, `condition`,
  `close_condition` and `activate_change` retain the earlier oracle/reviewer
  gates and add all configured acceptance domains plus unresolved-condition
  closure. `work` stores immutable category entries; `work_report` requires an
  explicit denominator and every category, including explicit zero entries.
- FGA03: `fact` preserves prior versions; `relation` requires the same object
  in all five declared domains and binds that object to the actual local sink.
  Facts must remain current at queue and effect; review bindings include their
  versions. These are checks of configured representations, not an ontology
  discovery service or a determination of legal authority.
- FGA04: `restart` additionally requires distinct Ed25519 signers over one
  incident decision. Its public registry is immutable bootstrap configuration.
  Event IDs survive reopening. DENY never resumes; RECALIBRATE is unsupported
  and remains refused. Registry changes require separately reviewed provisioning,
  not an agent-operated registration or recalibration endpoint.
- FGA05: `continuity_propose`, `continuity_check` and `continuity_activate`
  implement remember, forget and explicit succession records under fixed
  `continuity/1` policy. Unknown mutations are invalid. Candidate persistence is
  an actual local database write, not a portable signed persistence receipt.
  State history retains operation commitments; policy and norms are immutable.
  Missing evidence requires a new proposal. Activation fences old grants and
  pending proposals. This is a small typed transition policy, not a complete
  implementation of every CCT semantic invariant or behavioral evaluation.
- FGA06 and FGA07: `mandate`, `consent`, `perceive`, `retrieve` and
  `activate_episode` provide run-scoped consent, source-integrity propagation,
  a data-only retrieval result and recorded non-action. Original `ingest` is
  disabled in this opt-in profile. Appraisal and risk values are declared inputs,
  not validated psychological estimates. They cannot enlarge a mandate or grant.

Configuration selects public keys, acceptance domains and restart quorum before
use. Distinct key bytes and distinct configured principals are required; this
prevents duplicate-key counting but cannot establish independent organizations.
The runtime inherits the trusted-host HMAC transport of the local profile and
must not be represented as isolation from a compromised Python process.

Reproduce with:

```sh
python -m pip install -r tools/requirements-federated-governance.txt
python tools/federated_governance_qualification.py --results-dir results/first
python tools/federated_governance_qualification.py --results-dir results/second
```

The qualification requires 92 independent testcase elements (41 new plus 51
existing), all eight control-removal probes, a clean exact-source binding and a
representative replay. Eleven unittest subchecks are reported separately. The
replay contains one permitted synthetic effect, a zero-effect refusal after
consent withdrawal, and an offline public-key evidence-consumer assessment.
Two competing activation processes, abrupt exits before and after commit, and
reopening are exercised. Neither candidate persistence nor a VALID offline
assessment is accepted as current execution authority.
