# Operational state engineering addendum

Date: 2026-10-14. Baseline: `bc42e69a2836c8e27ace0fe992ea64736a16cac5` (PR #104).

The seven-paper review identifies one shared engineering requirement: claims,
constraints and evidence must retain their meaning when work crosses a handoff,
policy boundary or evaluation stage. This addendum extends the optional local
reference profile. It does not change selected components or authorize release.

## Source register

These are the supplied manuscript versions; page numbers refer to their PDF
pages. Their experimental results are not Cognous verification results.

| ID | Manuscript and locator | Engineering implication |
| --- | --- | --- |
| S1 | He and Yu, The Situated Identity Test, arXiv:2609.22195v1, pp. 1–3, 8 | Recorded lineage, temporal access and disclosure must be distinguished from persona consistency. |
| S2 | Lin et al., Large Language Models at the Intersection of Software Engineering and Software Security, arXiv:2608.21107v1, pp. 13–14, Table 5 | Functional success alone cannot establish security; disclose harness, budgets, human input, contamination and failures. |
| S3 | Tang et al., Proactive Service Agents, arXiv:2609.03727v1, pp. 1–2, 8–9 | Silence is a decision; account for interruption, privacy and misunderstanding costs. Feedback is not a permission event. |
| S4 | de la Chica Rodríguez et al., Compliant with Local Controls Collectively Discriminatory, arXiv:2609.27994v1, pp. 1–2, 6–7 | Local checks do not establish collective outcomes; compare observed and expected population behavior. |
| S5 | Papantoniou and Hilton, ANASSA From High-Level Framework to Low-Level Architecture for Spatial Agentic AI, arXiv:2610.14382v1, pp. 7–8 | Bind typed execution to spatial reference, resolution, uncertainty, time and provenance. |
| S6 | Raghav et al., A Unified Policy Architecture, arXiv:2609.06543v1, pp. 9–11 | Normalize principal, action, resource and context; preserve denial, approval suspension and obligations. |
| S7 | Sun et al., When Must Becomes Maybe, arXiv:2608.24569v2, pp. 3–4 | Handoffs must preserve stop status, prerequisite, resolving authority and fallback separately from endpoint behavior. |

## Gaps and implemented requirements

### OPS01 Preserve blockers through handoffs

The baseline has proposal challenges and change conditions, but no run-scoped
structured handoff contract. `OperationalStateRuntime` adds immutable blocker
creation, a designated current reviewer for evidence-bound resolution, and
predecessor-linked handoff snapshots. Summaries are digest references and cannot
change canonical status. Every blocker field must match, including resolved
history. Any unresolved run blocker stops queue admission and effect execution.
A blocker introduced and resolved after review still changes the binding and
requires a new proposal. An already committed effect can be reconciled without
performing it again. Source: S7; tests cover omission, softening, stale predecessor,
wrong resolver, wrong evidence, reopen, stale review and zero-effect refusal.

### OPS02 Bind policy decisions and obligations

An operator-installed, monotonically versioned contract names principal, action,
resource and context. Deny takes precedence; approve means suspended. All declared
obligations must be completed before execution. Contract revisions invalidate
reviewed bindings. The representation deliberately does not implement DGPL, plugin
execution, or automatic approval conversion. Completing obligations is a trusted
operator assertion; the inherited independent proposal review still applies.
Source: S6; tests cover deny precedence, pending approval, incomplete obligations,
revision changes, rollback and actor-role enforcement.

### OPS03 Check population observations at the effect boundary

A configured cohort has declared groups, minimum counts, maximum age and a
permitted absolute observed-versus-expected rate gap in parts per million.
Authenticated evaluators supply immutable complete-window samples. Every current
window is checked independently, using integer arithmetic; samples are not summed.
Missing, stale or undersized coverage is indeterminate and blocks execution.
A benign sample cannot replace a live alarm. New evidence invalidates prior review.
Source: S4; tests exercise those cases on the actual synthetic SQLite effect path.

This is a deterministic monitor over asserted evidence, not a fairness metric,
causal discrimination test, statistical confidence procedure or regulatory finding.
Group selection, expected rates and thresholds require independent domain review.
Overlapping windows are not aggregated. Expired alarms age out of this gate; an
incident requiring durable containment must use the existing stop protocol.

### OPS04 Require explicit spatial support

Contracts bind coordinate reference labels, resolution and uncertainty bounds,
observation time, expiry and an evidence digest. Mismatches or expiry stop the
synthetic effect. The profile does not transform coordinates, validate geometry,
prove sensor accuracy or implement the ANASSA task graph and capability registry.
Units and grid semantics are fixed synthetic fixture conventions. Source: S5;
tests cover reference mismatch, resolution, uncertainty and exact expiry.

### OPS05 Separate proactive feedback from permission

Immutable opportunity records include silence, inquiry, assistance or action and
separate benefit, interruption, privacy and misunderstanding estimates. Reviewer
feedback records acceptance and burden without mutating grants, consent or episode
activation. Source: S3; tests check silence and unchanged authority after positive
feedback. Counterfactual utility, calibrated intervention policy, user outcomes and
longitudinal burden remain empirical evaluation work. These records do not choose
an intervention or certify that an estimated benefit is accurate.

### OPS06 Bound lineage claims by acquired evidence

Steward perception records acquisition time. A lineage claim requires current
consent, the same run, a checkpoint at or after acquisition and no later than now,
and an exact content digest. A successful check explicitly reports identity as
not established. Source: S1; tests cover ungrounded content, temporal leakage and
revoked consent. This checks provenance for a supplied item; it does not determine
whether a model response is autobiographical, provide historical state replay,
implement partner-specific clearance, or reproduce SITBench.

### OPS07 Keep assurance dimensions separate

`assess_report` requires all eight S2 reporting dimensions and five distinct claim
axes: functional, security, operational, provenance and authority. A supported
claim needs an evidence digest, but the validator does not independently verify
that evidence. Completeness never enables release or deployment. Tests demonstrate
that a functional pass leaves security not established, reject missing disclosures
and reject an unsupported claim without evidence.

## Validation and reporting protocol

Run `python tools/operational_state_qualification.py --results-dir /tmp/operational-state-results`
after installing `tools/requirements-federated-governance.txt`. The qualification
runs 34 new independent tests plus the existing 92 integrated/federated tests,
counts XML testcase elements separately from unittest subchecks, runs seven
control-removal probes, hashes source and dependency requirements, and records the
exact commit. CI repeats on Python 3.11 and 3.12. Each mutation must cause an
assertion failure, never an import or execution error.

Task and artifact: optional Python/SQLite control profile, local synthetic effects.
Model and adaptation: not applicable to runtime verification; no LLM is evaluated.
Harness and tools: inherited authenticated local runtime, public-key governance,
trusted clock/host/environment observer; no external effect adapter.
Budget and human input: deterministic regression and mutation cases; two CI
repetitions per interpreter. User authorized implementation and merge; no independent
security or institutional reviewer acceptance is inferred. Agent authoring token,
compute cost and wall-time accounting are not established by this test harness.
Data and contamination: synthetic fixtures; no training dataset or benchmark score;
no claim of model generalization or contamination-free model evaluation.
Validation: positive execution, durable refusal, persistence and removed-control
sensitivity. Security assurance remains limited to the tested contract boundaries.
Uncertainty and failures: deterministic fixtures provide no population confidence
intervals; external telemetry accuracy and empirical intervention value are untested.
Reproducibility: exact commit, source hashes, pinned requirements, XML/log outputs
and scoped CI artifacts. Reports retain both release authorization flags as false.

## Acceptance boundaries and remaining work

The host, SQLite store, clock, initial roles and operator/evaluator assertions remain
trusted. Direct database tampering and compromised administrators are outside this
profile. A process not using this opt-in class receives no new guarantees. Existing
base and federated behavior is unchanged. The new profile must be created through
`OperationalStateRuntime.create`; no migration of prior perception timestamps is
inferred. Missing acquisition records fail closed.

Production acceptance still needs independent security review, institutional
appointments, trusted telemetry and source validation, policy/obligation provider
integration, workload-level outcome evaluation, and real deployment containment
and custody evidence. This batch does not close release issues or establish legal
compliance. Operational trust remains HOLD / NOT ESTABLISHED; C0 limitations and
optional same-host C1 remain. No C2/C3 or real settlement is claimed. Component
pins and selected release authorization files are unchanged.
