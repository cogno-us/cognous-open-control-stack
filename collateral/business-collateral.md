# Business Collateral

## 1. Executive Summary

Cognous Open Control Stack is open-source reference infrastructure for governable AI agents. It gives enterprises a public, inspectable artifact chain for declaring what an agent may propose, recording what it proposed at runtime, packaging a run for replay, and translating those records into business-facing governance evidence.

## 2. The Business Problem

AI agents are moving into workflows that touch enterprise data, customer interactions, approvals, exports, and operational decisions. In these settings, organizations need more than model quality and application telemetry. They need records that explain what an agent was expected to do, what it attempted to do, what policy decided, what authority context mattered, what was blocked, and how a reviewer can understand the deployment afterward.

Prompts do not declare an action surface. Tool lists do not explain the difference between reading, drafting, sending, approving, exporting, deleting, or purchasing. Logs and traces may capture activity, but they do not automatically create the records needed for replay and review. Dashboards display information, but they are not the underlying evidence chain.

## 3. The Stack in One View

Cognous Open Control Stack is organized around a four-step lifecycle: Declare → Control → Replay → Evidence.

| Layer | Repository | Core question | Output |
|---|---|---|---|
| Declare | Agent Action Manifest | What may this agent propose? | Declared action surface |
| Control | Agent Control Plane | What did the agent propose, and what did policy decide? | Runtime control records |
| Replay | Agent Replay Bundle | Can we reconstruct this run? | Portable replay record |
| Evidence | Agent Governance Evidence Pack | What evidence supports deployment review? | Business-facing evidence package |

## 4. Layer 1 - Declare

The declaration layer defines the expected action surface before runtime. Agent Action Manifest describes the kinds of actions an agent may propose in a governed deployment. That includes actions such as reads, searches, drafts, sends, approvals, exports, and other categories that matter to policy review.

This matters because an enterprise cannot meaningfully control agent behavior if it has not first declared what behavior is in scope.

## 5. Layer 2 - Control

The control layer records runtime proposals and policy decisions. Agent Control Plane captures what the agent proposed, what was permitted, what was blocked, and what supporting context mattered, including authority records and reliance records.

This creates the runtime governance record. It turns policy from an aspiration into a reviewable event trail tied to actual agent proposals.

## 6. Layer 3 - Replay

The replay layer packages the run so it can be reconstructed outside the original execution environment. Agent Replay Bundle preserves the records needed to understand the run as a coherent whole, not just as disconnected events.

A log records events. A replay bundle reconstructs the agent run.

## 7. Layer 4 - Evidence

The evidence layer translates run records into business-facing governance evidence. Agent Governance Evidence Pack helps reviewers understand the deployment, the kinds of actions involved, the decisions applied, the authority context, the reliance context, and the resulting governance posture.

This layer is about usable review material, not only technical trace data.

## 8. How the Four Layers Work Together

The four layers are meant to reinforce one another:
- Declare defines the action surface.
- Control records runtime proposals and policy decisions against that surface.
- Replay packages a complete run for reconstruction, validation, redaction, and signed export handling.
- Evidence summarizes the deployment for governance review.

A customer-service example makes the flow concrete. An agent reads CRM records, searches account notes, drafts customer emails, and attempts outbound email sends. The manifest declares those actions and marks email send as requiring authority and review. The control plane records the reads as allowed and the outbound send as blocked because the required authority is missing. The replay bundle packages the run. The evidence pack summarizes the governed deployment for review.

## 9. What Makes the Connected Stack Valuable

The value is not just in the individual layers. It is in the connected artifact chain.

The stack helps enterprises:
- declare what an agent may propose before deployment;
- control agent proposals at runtime;
- preserve replayable run records;
- produce business-facing evidence for review;
- keep public reference artifacts separate from higher-level commercial offerings.

## 10. How It Differs from Adjacent Categories

The stack is adjacent to, but distinct from:
- agent frameworks, which focus on building agent behavior;
- model runtimes, which focus on execution;
- dashboards, which focus on visualization;
- authorization systems, which focus on application permissions;
- compliance tooling, which focuses on control mapping and reporting.

Cognous Open Control Stack focuses on the governance artifact chain for governed AI-agent workflows.

## 11. What the Stack Is Not

Cognous Open Control Stack is not:
- an agent framework;
- a model runtime;
- a hosted dashboard;
- a complete enterprise AI governance platform;
- a compliance certification product;
- a security boundary by itself;
- a substitute for application authorization;
- a guarantee that model outputs are correct;
- a guarantee that regulatory obligations have been satisfied;
- the ODES standard;
- a proprietary trust network.

## 12. Why Open Source Matters

The public repositories are intentionally narrow. They expose the formats, schemas, validators, reference behavior, examples, tests, and business-facing documentation that define the artifact chain. This makes the records inspectable and reusable while leaving room for differentiated offerings above the public layer.

Open the record formats. Compete on implementation, governance, and operations.

## 13. Why This Matters Now

Organizations are moving from assistant-style experimentation to agent-driven workflows that can influence real business outcomes. As that shift happens, the gap between what an agent can do and what an enterprise can review becomes more important. A connected artifact chain helps close that gap with public, inspectable reference infrastructure.

## 14. Strategic Summary

Cognous Open Control Stack provides an open-source reference implementation family for governed AI-agent workflows. It links declaration, runtime control, replay packaging, and governance evidence into one public story. For teams adopting governed deployments, the practical first step is simple: take one bounded workflow through the full lifecycle of Declare → Control → Replay → Evidence.
