# Cognous Open Control Stack — Private Technical Evaluation Package 0.1

**Status:** Invitation-only, **read-only evaluation material**. Not a released software distribution, deployment authorization, security certification, legal approval, or public developer preview. This package is a proposal for bounded private review, not evidence of formal release-gate acceptance. See the [current decision record](../verification/pv-resource-constrained-disposition-2026-10-10.md) and [six-gate board #68](https://github.com/cogno-us/cognous-open-control-stack/issues/68). **All six public-preview gates remain unaccepted.** Operational trust [orchestrator #30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30) is **HOLD / NOT ESTABLISHED**.

## Facilitator materials

- [Invitation template](invitation-template.md) — unsent draft, subject to owner approval
- [Pilot protocol](pilot-protocol.md) — one-reviewer rehearsal and stop criteria
- [Feedback register](feedback-register.md) — sanitized intake; no real observations recorded

## Intended evaluators and access

For individually invited enterprise architects, platform engineers, security/governance reviewers and prospective technical partners. The permitted evaluation is a *guided, read-only walkthrough* of already public-safe descriptive material and **archived synthetic evidence**. It does not authorize copying, redistributing, cloning, deploying, executing against external services, probing security boundaries, or sharing privileged private materials. Repository visibility is not an assurance of redistribution rights. Evaluators must obtain specific approval before obtaining any software bundle or nonpublic information. No NDA, access agreement, confidentiality obligation or commercial terms are created by this document; any required agreement must be handled separately.

**Recommended access:** share a link to this document or a narrowly selected PDF/printout of approved public-safe pages. Do not grant broad repository/organization access just to conduct a preview. If an existing GitHub page is publicly reachable, calling the review “private” limits participation and presentation, **not** the public visibility of that page.

## One-hour facilitator agenda

| Time | Exercise | Expected evaluator output |
| --- | --- | --- |
| 0–10 min | State purpose, scope, exclusions and HOLD | Written acknowledgement of what is not qualified |
| 10–20 min | Walk selected pins, authority separation and action declaration | Identify which component establishes each input and which does not |
| 20–35 min | Examine archived synthetic refund/timeout and destination-state evidence | Distinguish decision, dispatch, destination effect and observation |
| 35–45 min | Evaluate C0 race, optional C1, duplicate intent and retry restrictions | List residual risks and evidence needed for a real destination |
| 45–55 min | Inspect Replay, Evidence Pack, ODES and provenance | Explain why presentation of evidence is not independent truth/settlement |
| 55–60 min | Capture feedback and next action | Complete [evaluation worksheet](evaluation-worksheet.md) |

The agenda uses retained evidence rather than requiring a live environment, credentials, additional compute or fresh checkout.

## Evaluation materials, in recommended order

1. [Start here](../start-here.md), [architecture](../architecture.md), [selected component lock](../../component-lock.json) and [release status](../release-status.md). Selection follows the lock; newer component main branches and W7 [PR #63](https://github.com/cogno-us/cognous-open-control-stack/pull/63) are separate.
2. [Evidence index](../evidence-index.md) and [selected artifact inspection](../workstreams/pv-artifact-evidence-inspection-2026-10-10.md), based on downloaded GitHub Actions archives and read-only synthetic SQLite. This is **inspected existing evidence**, not a fresh evaluation execution.
3. [Public-preview qualification](../public-preview-qualification.md) and [resource-constrained disposition](../verification/pv-resource-constrained-disposition-2026-10-10.md); for unavailable independent clean execution see [PV-FINAL-RUN](../verification/pv-final-run-2026-10-10.md).
4. [Publication safety](../verification/pv-final-security-2026-10-10.md) and [distribution verification](../verification/pv-final-distribution-2026-10-10.md). These are **HOLD reports**, not attestations of safety or licensing clearance.
5. [Worksheet](evaluation-worksheet.md), for evaluator observations rather than release signoff.

## Worked synthetic refund case

In the selected archived evidence, **35 required scenarios** comprise **34 passed** and **one characterized** `research_replanned_equivalent_intent` case. The characterized outcome is not prevention of equivalent-business-intent duplicates. Two inspected archived SQLite destinations each contain a **single USD 50 synthetic applied effect**, one attempt and two attempt events. This demonstrates bounded local state in those archived runs only. The original selected run's candidate-time `release_qualified=false` does not turn into `true` retroactively; later hub acceptance and newer preview evidence are separately attributed.

Walk through these questions: Which action was declared? Where did independent Authority Context enter? What did C0 revalidate? Was an effect committed, or merely acknowledged? What is knowable after timeout? Why must an absent observation **not** permit retry? How do Replay, Evidence Pack and ODES preserve provenance without independently establishing real-world settlement?

**Trust boundaries:** C0 revalidates before effect dispatch but retains a check-to-destination-commit race. Optional C1 orders within a cooperating same-host SQLite context and is **not** selected by default. No C2/C3, external processor settlement, business-intent exactly-once, production identity, institutional adoption, regulatory/compliance approval or operational trust qualification is established. A synthetic event record is not a payment-processor receipt.

## Safety and distribution rules

- **Read-only and synthetic only.** No real customer records, credentials, access tokens, grant issuance, production connectors, real payments, independent settlement claims or adversarial testing of live services.
- **No software distribution by default.** Two optional selected component trees (PRP and TFA) have no license-/notice-named tracked files at their selected commits. Runtime has mixed upstream MIT, Cognous Apache and nested third-party notices. Any code/package distribution needs separately authorized rights review and explicit scope; invitation status does not repair licensing.
- **No confidential attachments by default.** Do not share private ISS/IGPG implementations, unpublished research, customer materials, internal security reports or raw suspected secrets. Screen any exported handout for sensitive content; repository-wide/history/binary screening has **not** been completed.
- **No production or legal claims.** Do not say “certified”, “production ready”, “exactly once”, “payment safe”, “settled”, “fully audited”, or that public release gates passed.
- **Vulnerabilities:** use the private [SECURITY.md](../../SECURITY.md) reporting route. Do not put exploitation details, secrets or PII into public worksheets, forms, GitHub issues or PR comments.
- **Feedback:** request non-sensitive, evidence-linked observations using the [worksheet](evaluation-worksheet.md). A private evaluator can return the worksheet through an individually approved channel; do not assume the public issue form is private.

## Private-evaluation completion criteria

The facilitator has recorded: evaluator role and date (without exposing personal contact publicly); exact evidence source; three boundary distinctions that the evaluator understood; at least one falsifiable technical question; limitations and explicit no-deployment/no-distribution acknowledgement. **Completion is feedback collection only**: it does not turn any public-preview gate into PASS, approve a merge or upgrade operational #30.

**Next permitted decision:** incorporate sanitized feedback into a scoped issue or follow-up documentation PR. Further access, independent running, redistribution or live deployment requires separate explicit authority and review.
