# Cognous Open Control Stack

Open-source reference infrastructure for governable AI agents.

**Lifecycle:** Declare → Control → Replay → Evidence

## Opening

Cognous Open Control Stack is a set of open-source reference artifacts for governable AI agents. It helps teams declare what agents may propose, control what agents actually propose at runtime, package runs for replay, and translate runtime records into business-facing governance evidence.

## Why this exists

AI agents are moving beyond chat. They can call tools, access enterprise systems, draft communications, prepare exports, propose changes, escalate workflows, and influence business decisions.

Existing tools are not enough by themselves:
- prompts do not declare an agent's action surface;
- tool lists do not distinguish read, write, send, export, approve, delete, or purchase behavior;
- logs do not preserve action proposals, blocked actions, authority, and reliance as governance records;
- traces do not necessarily reconstruct the agent run;
- dashboards visualize data but do not create the underlying evidence;
- policy documents state intent but do not produce runtime records.

The Open Control Stack supplies the artifact chain between agent behavior and enterprise review.

## Stack overview

| Layer | Repository | Question answered | Output |
|---|---|---|---|
| Declare | [Agent Action Manifest](https://github.com/cogno-us/cognous-agent-action-manifest) | What may this agent propose? | Declared action surface |
| Control | [Agent Control Plane](https://github.com/cogno-us/cognous-agent-control-plane) | What did the agent propose, and what did policy decide? | Runtime control records |
| Replay | [Agent Replay Bundle](https://github.com/cogno-us/cognous-agent-replay-bundle) | Can we reconstruct this run? | Portable replay record |
| Evidence | [Agent Governance Evidence Pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack) | What evidence supports deployment review? | Business-facing evidence package |

## 1. Agent Action Manifest - Declare

Agent Action Manifest is the declaration layer for agent action governance. It describes the action surface an agent may propose before runtime.

"Before an enterprise can control what an AI agent does, it must declare what that agent may propose."

It declares expected actions such as reads, searches, drafts, sends, approvals, and other proposal categories that matter to governance review.

It is not a runtime controller, policy engine, or full application authorization system.

Repository: [cognous-agent-action-manifest](https://github.com/cogno-us/cognous-agent-action-manifest)

## 2. Agent Control Plane - Control

Agent Control Plane is the runtime control layer. It records what the agent proposed, what policy decided, what was allowed, what was blocked, and what authority or reliance context was present.

"Before an enterprise delegates meaningful work to AI agents, it must be able to reconstruct what those agents proposed, what they were permitted to do, what was blocked, and what they relied on."

It records runtime control records, including action proposals, policy decisions, blocked actions, authority records, and reliance records.

It is not a general agent framework, model runtime, or substitute for application authorization.

Repository: [cognous-agent-control-plane](https://github.com/cogno-us/cognous-agent-control-plane)

## 3. Agent Replay Bundle - Replay

Agent Replay Bundle is the replay layer. It preserves the run package needed to reconstruct a governed agent run outside the original runtime environment.

"A log records events. A replay bundle reconstructs the agent run."

It preserves run-level records, validation outputs, redacted export material, signed export metadata, and related replay context.

It is not just a log sink, monitoring dashboard, or long-term storage platform by itself.

Repository: [cognous-agent-replay-bundle](https://github.com/cogno-us/cognous-agent-replay-bundle)

## 4. Agent Governance Evidence Pack - Evidence

Agent Governance Evidence Pack is the evidence layer. It summarizes a governed deployment in business-facing terms for review and oversight.

"A replay bundle can reconstruct a run. An evidence pack helps a business reviewer understand the deployment."

It summarizes the deployment using governance evidence such as validation report outputs, authority context, reliance context, and business-facing evidence.

It is not a compliance certification product, legal opinion, or guarantee that regulatory obligations have been satisfied.

Repository: [cognous-agent-governance-evidence-pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack)

## How the layers work together

1. Declare the agent's expected action surface with Agent Action Manifest.
2. Control runtime proposals with Agent Control Plane.
3. Replay run-level evidence with Agent Replay Bundle.
4. Evidence the deployment with Agent Governance Evidence Pack.

Agent Action Manifest  
        ↓  
Agent Control Plane  
        ↓  
Agent Replay Bundle  
        ↓  
Agent Governance Evidence Pack

## Example workflow

Consider a customer-service agent that reads CRM records, searches account notes, drafts customer emails, and attempts outbound email sends.

- The manifest declares four actions and marks email send as requiring authority and review.
- The control plane records CRM read and account-note search as allowed.
- The control plane records attempted email send as blocked because outbound-send authority is missing.
- The replay bundle packages the run.
- The evidence pack summarizes deployment for governance review.

## Relationship to ODES

ODES, the Open Decision Evidence Standard, is a separate proposed open, vendor-neutral public standard for portable decision evidence in AI-mediated and cross-boundary decisions.

Cognous Open Control Stack is not ODES and does not define ODES conformance. The stack may produce, package, or reference evidence that could support ODES-style records in future profiles, but the relationship is optional mapping/supporting evidence - not identity and not conformance.

- ODES = proposed public standard for portable decision evidence.
- Cognous Open Control Stack = open-source reference implementation family for governed AI-agent workflows.
- Relationship = optional mapping and supporting evidence, not identity and not conformance.

## What this is not

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

## Open-source boundary

The public repositories are intentionally narrow. They provide formats, schemas, validators, reference behavior, examples, and tests.

Commercial systems can compete above that layer on:
- hosted services;
- integrations;
- user interfaces;
- approval workflows;
- compliance mappings;
- enterprise storage;
- identity integration;
- analytics;
- support;
- operational depth.

Open the record formats. Compete on implementation, governance, and operations.

## Repository list

- [Agent Action Manifest](https://github.com/cogno-us/cognous-agent-action-manifest)
- [Agent Control Plane](https://github.com/cogno-us/cognous-agent-control-plane)
- [Agent Replay Bundle](https://github.com/cogno-us/cognous-agent-replay-bundle)
- [Agent Governance Evidence Pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack)

## Getting started

Start with one bounded agent workflow.

1. Identify one agent and one workflow.
2. Declare its action surface.
3. Record proposed actions and policy decisions.
4. Package one run as a replay bundle.
5. Produce one governance evidence pack.

The goal is not to govern every agent at once. The goal is to prove that one agent workflow can move through the full artifact chain: Declare → Control → Replay → Evidence.

## License

The public reference repositories are released under Apache-2.0. See each repository for its LICENSE and NOTICE files.
