# Cognous Open Control Stack

**Open-source reference infrastructure for governable AI agents.**

**Declare → Control → Replay → Evidence**

Cognous Open Control Stack is a set of open-source reference artifacts for governable AI agents. It helps teams declare what agents may propose, control what agents actually propose at runtime, package runs for replay, and translate runtime records into business-facing governance evidence.

The stack is designed for enterprise teams moving from AI-agent demos to governed deployment.

This repository is the public hub for the Cognous Open Control Stack. Implementation details live in the four component repositories.

---

## Why this exists

AI agents are moving beyond chat. They can call tools, access enterprise systems, draft communications, prepare exports, propose changes, escalate workflows, and influence business decisions.

Existing tools are not enough by themselves:

- prompts do not declare an agent’s action surface;
- tool lists do not distinguish read, write, send, export, approve, delete, or purchase behavior;
- logs do not preserve action proposals, blocked actions, authority, and reliance as governance records;
- traces do not necessarily reconstruct the agent run;
- dashboards visualize data but do not create the underlying evidence;
- policy documents state intent but do not produce runtime records.

The Open Control Stack supplies the artifact chain between agent behavior and enterprise review.

```text
Declare → Control → Replay → Evidence
```

---

## Stack overview

| Layer | Repository | Question answered | Output |
|---|---|---|---|
| Declare | [Agent Action Manifest](https://github.com/cogno-us/cognous-agent-action-manifest) | What may this agent propose? | Declared action surface |
| Control | [Agent Control Plane](https://github.com/cogno-us/cognous-agent-control-plane) | What did the agent propose, and what did policy decide? | Runtime control records |
| Replay | [Agent Replay Bundle](https://github.com/cogno-us/cognous-agent-replay-bundle) | Can we reconstruct this run? | Portable replay record |
| Evidence | [Agent Governance Evidence Pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack) | What evidence supports deployment review? | Business-facing evidence package |

Each layer answers a question the next layer depends on.

Declaration gives runtime control a baseline. Runtime control generates records. Replay bundles package those records. Evidence packs translate them into business-facing review material.

---

## 1. Agent Action Manifest — Declare

[Agent Action Manifest](https://github.com/cogno-us/cognous-agent-action-manifest) is the pre-runtime declaration layer.

It declares what actions an AI agent may propose before runtime.

**One-line summary:**

> Before an enterprise can control what an AI agent does, it must declare what that agent may propose.

Agent Action Manifest can declare:

- tools;
- actions;
- action types;
- authority requirements;
- review requirements;
- reliance requirements;
- payload policies;
- redaction hints;
- validation results.

A manifest separates tool access from action semantics. A tool list may show that an agent can access a CRM or email system. It does not distinguish reading a CRM record from updating one, or drafting an email from sending one. The manifest makes those distinctions explicit before deployment.

**What it is not:**  
Agent Action Manifest does not run the agent, enforce policy, grant authority, or guarantee review. It gives downstream control and review systems a declared baseline.

Repository:  
<https://github.com/cogno-us/cognous-agent-action-manifest>

---

## 2. Agent Control Plane — Control

[Agent Control Plane](https://github.com/cogno-us/cognous-agent-control-plane) is the runtime control and record layer.

It sits beside the agent and records or governs proposed actions before those actions are treated as executable.

**One-line summary:**

> Before an enterprise delegates meaningful work to AI agents, it must be able to reconstruct what those agents proposed, what they were permitted to do, what was blocked, and what they relied on.

Agent Control Plane can record:

- action proposals;
- policy decisions;
- blocked actions;
- authority context;
- reliance records;
- policy evaluation traces;
- run records;
- redacted exports;
- signed replay bundles.

The control layer makes proposed agent behavior visible. It records what the agent tried to do, what was allowed, what was blocked, why policy decided that way, what authority existed, and what sources were relied on.

Blocked actions are treated as evidence, not silent non-events.

**What it is not:**  
Agent Control Plane is not an agent framework, model runtime, dashboard, full governance platform, or substitute for application authorization.

Repository:  
<https://github.com/cogno-us/cognous-agent-control-plane>

---

## 3. Agent Replay Bundle — Replay

[Agent Replay Bundle](https://github.com/cogno-us/cognous-agent-replay-bundle) packages technical run evidence into portable replay records.

**One-line summary:**

> A log records events. A replay bundle reconstructs the agent run.

Agent Replay Bundle can preserve:

- run frame;
- action proposals;
- policy decisions;
- policy evaluation traces;
- blocked actions;
- authority records;
- reliance records;
- final output;
- validation report;
- redaction metadata;
- signature metadata.

A replay bundle is organized around the run. It helps reviewers reconstruct what happened without piecing together scattered logs, traces, tool-call records, policy decisions, and manual notes.

It supports validation, redaction, and export-integrity metadata so run records can be reviewed and shared more safely.

**What it is not:**  
Agent Replay Bundle does not run the agent, enforce policy, certify compliance, prove correctness, or provide production key management. It packages run evidence for reconstruction and review.

Repository:  
<https://github.com/cogno-us/cognous-agent-replay-bundle>

---

## 4. Agent Governance Evidence Pack — Evidence

[Agent Governance Evidence Pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack) translates runtime and replay records into business-facing evidence packages for deployment review.

**One-line summary:**

> A replay bundle can reconstruct a run. An evidence pack helps a business reviewer understand the deployment.

Agent Governance Evidence Pack can summarize:

- agent overview;
- deployment context;
- tool inventory;
- action inventory;
- authority model;
- policy controls;
- blocked-action summaries;
- reliance summaries;
- replay bundle inventory;
- validation summary;
- redaction/export summary;
- risk register;
- review records.

The evidence pack is designed for governance review, audit preparation, risk review, security signoff, legal review, customer assurance, and executive oversight. It connects technical records to business-facing evidence.

**What it is not:**  
Agent Governance Evidence Pack does not run agents, enforce policy, certify compliance, or replace governance processes. It creates a structured artifact those processes can inspect.

Repository:  
<https://github.com/cogno-us/cognous-agent-governance-evidence-pack>

---

## How the layers work together

A governed agent workflow can move through the stack as follows:

1. **Declare** the agent’s expected action surface with Agent Action Manifest.
2. **Control** runtime proposals with Agent Control Plane.
3. **Replay** run-level evidence with Agent Replay Bundle.
4. **Evidence** the deployment with Agent Governance Evidence Pack.

Each layer produces records that the next layer can use.

```text
Agent Action Manifest
        ↓
Agent Control Plane
        ↓
Agent Replay Bundle
        ↓
Agent Governance Evidence Pack
```

---

## Example workflow

Consider a customer-service agent that can:

- read CRM records;
- search account notes;
- draft customer emails;
- attempt outbound email sends.

The stack would handle that workflow as follows:

1. **Agent Action Manifest** declares four actions: CRM read, account-note search, email draft, and email send. The email send is marked as requiring authority and review.

2. **Agent Control Plane** records the CRM read and account-note search as allowed. It records the attempted email send as blocked because outbound-send authority is missing.

3. **Agent Replay Bundle** packages the run: task frame, action proposals, policy decisions, blocked action, authority context, reliance sources, final output, validation results, redaction metadata, and signature metadata.

4. **Agent Governance Evidence Pack** summarizes the deployment for governance review: business purpose, systems touched, actions, controls, blocked-send evidence, reliance sources, replay bundles, validation status, redacted exports, risks, and review decisions.

The result is a record chain. The enterprise can explain what the agent was allowed to propose, what it actually proposed, what was blocked, why it was blocked, what sources were relied on, how the run can be reconstructed, and what evidence supports deployment review.

---

## Relationship to ODES

ODES, the **Open Decision Evidence Standard**, is a separate proposed open, vendor-neutral public standard for portable decision evidence in AI-mediated and cross-boundary decisions.

Cognous Open Control Stack is not ODES and does not define ODES conformance. The stack may produce, package, or reference evidence that could support ODES-style records in future profiles, but the relationship is optional mapping/supporting evidence — not identity and not conformance.

The distinction:

- **ODES** = proposed public standard for portable decision evidence.
- **Cognous Open Control Stack** = open-source reference implementation family for governed AI-agent workflows.
- **Relationship** = optional mapping and supporting evidence, not identity and not conformance.

---

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

The stack supplies structured artifacts for declaration, runtime control, replay, and evidence. The quality of those records depends on upstream systems, policy design, authorization, monitoring, security controls, governance processes, and implementation discipline.

---

## Open-source boundary

The public repositories are intentionally narrow.

They provide:

- formats;
- schemas;
- validators;
- reference behavior;
- examples;
- tests.

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

**Open the record formats. Compete on implementation, governance, and operations.**

---

## Documentation

- [Stack overview](docs/overview.md)
- [Relationship to ODES](docs/relationship-to-odes.md)
- [Open-source boundary](docs/open-source-boundary.md)
- [Roadmap](docs/roadmap.md)
- [Customer-service end-to-end example](examples/customer-service-end-to-end/README.md)
- [One-page overview](collateral/one-page-overview.md)
- [Business collateral](collateral/business-collateral.md)

---

## Repository list

- [Agent Action Manifest](https://github.com/cogno-us/cognous-agent-action-manifest) — declare what agents may propose.
- [Agent Control Plane](https://github.com/cogno-us/cognous-agent-control-plane) — record and govern runtime proposals.
- [Agent Replay Bundle](https://github.com/cogno-us/cognous-agent-replay-bundle) — package runs for replay.
- [Agent Governance Evidence Pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack) — summarize evidence for business review.

---

## Getting started

Start with one bounded agent workflow.

1. Identify one agent and one workflow.
2. Declare its action surface.
3. Record proposed actions and policy decisions.
4. Package one run as a replay bundle.
5. Produce one governance evidence pack.

The goal is not to govern every agent at once. The goal is to prove that one agent workflow can move through the full artifact chain:

```text
Declare → Control → Replay → Evidence
```

---

## License

The public reference repositories are released under Apache-2.0.

See each repository for its `LICENSE` and `NOTICE` files.
