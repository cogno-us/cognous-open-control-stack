# Synthetic evaluator pilot — enterprise runtime/security reviewer

**Simulation only | 2026-10-10 | No human evaluator participated.** This is an adversarial *desk review* generated from existing Cognous public-preview documentation. It is **not independent execution, user research, expert certification, external endorsement, a security penetration test, or a public-preview acceptance decision**. The synthetic reviewer is a role, not a real person.

**Evaluated input:** private evaluator package and facilitator protocol at [PR #93](https://github.com/cogno-us/cognous-open-control-stack/pull/93), exact head `16853c0b39197b554577753e8a24cdf6503e28c9`; original selected artifact-inspection report `docs/workstreams/pv-artifact-evidence-inspection-2026-10-10.md`, incorporated from PR #82; read-only qualification record `docs/verification/pv-resource-constrained-disposition-2026-10-10.md`; selected component lock unchanged. **Method:** textual challenge, evidence attribution and counterexample reasoning. No fresh checkout, tests, file scanner, live service, database execution, external customer or evaluator interview in this pilot.

## Synthetic evaluator persona and review question

Role: skeptical enterprise architect with payment-integration and platform-security experience, **not an actual participant**. Core question: *“Which claims are grounded in independent destination observation, and what remains unproven if an agent's authority changes between a permission check and the destination commit?”*

## Simulated 60-minute review

| Segment | Evaluator challenge | Evidence-based response and judgement |
| --- | --- | --- |
| Scope (0–10) | Is this a pilot of deployable governance? | **No.** Documentation permits read-only synthetic evidence walkthrough only. All six public gates are unaccepted; operational trust [#30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30) remains HOLD. |
| Authority (10–20) | Does an agent-supplied message or Manifest authorize a refund? | **No.** Manifest is a declaration; Control Plane evaluates separately resolved Authority Context. This is a source-described contract, not a live institutional authority audit. |
| Effect (20–35) | Do the two SQLite rows prove a refund reached a processor? | **No.** Archived selected ZIPs contain two synthetic SQLite destinations. Each inspected repetition shows one USD 50 applied effect, one attempt, two attempt events. These establish a bounded local archived state, not settlement, processor receipt or current fresh execution. |
| Concurrency (35–45) | Can revocation after C0 check prevent a commit? Can an equivalent intent be repeated? | **Not guaranteed.** C0 has a check-to-commit race. C1 is optional cooperating same-host SQLite and not default; C2/C3 unqualified. The selected 35-scenario matrix has 34 PASS plus one `research_replanned_equivalent_intent` characterized limitation. Effect-ID dedupe is not business-intent dedupe. |
| Evidence (45–55) | Does Replay / Evidence Pack / ODES independently attest truth? | **No.** They retain, reconstruct, project and present source evidence. A presentation or successor reference cannot turn an unobserved destination outcome into settlement proof. |
| Feedback (55–60) | What should be tested next? | Freeze one synthetic operation; hold its authorized decision valid, change grant/policy generation just before the local destination commit, and independently inspect committed state plus durable refusal. Do not substitute an earlier denial or a newer candidate workflow for selected source evidence. |

## Filled synthetic observation worksheet

| Worksheet question | Simulated response | Class / specific source |
| --- | --- | --- |
| Action declaration vs authorization | Manifest describes proposed work; independent resolver-supplied Authority Context and Control Plane decide supported authorization. | **Source-derived** — `docs/start-here.md` at PR #93 input and selected artifact report |
| C0 race | Validation immediately before dispatch is not an atomic check-plus-destination commit. | **Source-derived** — `docs/release-status.md`, evaluator README |
| Optional C1 | Orders cooperating work within same-host SQLite profile; does not establish external commit, distributed linearizability or payment exactly once. | **Source-derived** — evaluator README and artifact report's separate 73-test run |
| Unknown timeout | Do not infer failure from absent observation; reconcile original effect before considering any next action. | **Source-derived** — `docs/start-here.md` |
| Effect proof | In the inspected archived representative paths, two runs each show one applied synthetic USD 50 effect with one attempt and two attempt events. | **Earlier worker's inspected evidence**, not rechecked by this synthetic reviewer — artifact report, selected run `37694032916` |
| Evidence provenance | Replay, Evidence Pack and ODES may preserve lineage, not independent factual confirmation of settlement. | **Source-derived** — evaluator README |
| Scenario count | 35 required = 34 passed + 1 characterized equivalent-intent case. It is incorrect to call this 35 prevented failures. | **Earlier inspected evidence** — artifact report `full-candidate-results.json` |
| Operational usability | A real institution's grant identity, key custody, production environment, security, rights and settlement are still outside this demonstration. | **Inference from explicitly absent qualification** — #88/#89/#90 and release status |

### Scored simulated assessment

Scale: 0 = no source support, 1 = articulated but not independently reproduced in this pilot, 2 = supporting archived evidence inspected by a prior worker, 3 = newly independently executed by this evaluator. **Scores are a synthetic review aid, not objective product-performance measurements.**

| Dimension | Score | Reason |
| --- | ---: | --- |
| Conceptual separation of proposal, authority and effect | 1/3 | Contracts are clear in sources; no live institution tested |
| Archived synthetic destination provenance | 2/3 | Prior worker inspected ZIP digests and SQLite rows |
| C0/C1/C2/C3 limitation honesty | 2/3 | Explicit and differentiated in reports; not operational qualification |
| Independent reproducibility by evaluator | 0/3 | No fresh selected checkout executed |
| Security/publication clearance | 0/3 | Comprehensive scans unperformed |
| Redistribution/legal clearance | 0/3 | Selected PRP/TFA notice gaps and mixed rights outstanding |

**Do not average these scores into a readiness percentage.**

## Priority findings for owner triage (synthetic, not external feedback)

| ID | Taxonomy | Class | Finding | Consequence | Suggested bounded follow-up |
| --- | --- | --- | --- | --- | --- |
| SIM-001 | ARCH | Inference | Effect-time C0 is distinguishable from atomic commit; a public audience might still read “revalidated” as “revocation safe”. | High if misrepresented in demonstrations | Make the residual race the first limitation in every live walkthrough; ask evaluator to restate it |
| SIM-002 | EVID | Observed in referenced archive report | One required equivalent-business-intent case is *characterized*, not prevented. | High for retry/idempotency claims | Show this case next to successful USD 50 destination evidence; never label 35/35 prevented |
| SIM-003 | EVID | Unavailable | No fresh selected checkout was performed by an independent reviewer. | Medium for reproducibility confidence | Explicitly state an unavailable live run at the session outset; provide only retained archive links |
| SIM-004 | ARCH | Inference | Evidence lineage could be mistaken for independent settlement or third-party attestation. | High for nontechnical audience | Use a two-column “what local SQLite proves / does not prove” explanation |
| SIM-005 | DOC | Inference | The evaluator worksheet names PR #84 even though the working evaluator package descends via #91/#92/#93. | Medium provenance ambiguity | In future evaluator-facing revision, distinguish frozen evidence baseline #84 from evaluator-package version #93 |
| SIM-006 | EVID | Unavailable | Comprehensive secret/IP and selected component rights clearance absent. | High for code distribution | Keep evaluation read-only; do not distribute repository/package bundles |

## One discriminating experiment, not performed

**Hypothesis:** For a single synthetic operation with decision D evaluated against authority generation G1, a subsequent revocation or policy version change to G2 before the destination commit may allow the default C0 path to commit despite the changed authority, whereas a bounded cooperating same-host C1 boundary may reject or serialize that commit under its documented prerequisites.

**Controlled comparison (future only):** freeze exact request, selected component pins and synthetic SQLite destination; independently run unchanged-authority control and changed-authority injection; capture decision/effect IDs, authority generation before and at commit, SQLite rows, durable refusal and two repetitions. Examine failures before interpreting results; no real credentials, third-party settlement, external effects or broader claims. **This test is not authorized or executed by this synthetic exercise**, and optional C1 must not be represented as selected/default.

## Simulation disposition

**Adequate for a facilitator rehearsal of a read-only private evidence walkthrough; not proof of external evaluator acceptance.** Keep broad public preview **HOLD** and operational trust **#30 HOLD**. Nothing here advances the six release gates or confirms independent production adequacy. No real invitations, calendar sessions, interviews, feedback submissions, credentials, access grants or code distribution occurred.
