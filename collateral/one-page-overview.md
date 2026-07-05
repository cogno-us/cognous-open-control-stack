# One-Page Overview

Cognous Open Control Stack is open-source reference infrastructure for governable AI agents. It helps teams declare what agents may propose, control what agents actually propose at runtime, package runs for replay, and turn those runtime records into business-facing governance evidence.

## Problem

AI agents can read data, draft communications, prepare exports, and influence business decisions. Prompts, tool lists, logs, traces, and dashboards each help with part of the story, but they do not automatically create the full artifact chain needed for governance review.

## Declare → Control → Replay → Evidence

| Layer | Repository | Question answered | Output |
|---|---|---|---|
| Declare | Agent Action Manifest | What may this agent propose? | Declared action surface |
| Control | Agent Control Plane | What did the agent propose, and what did policy decide? | Runtime control records |
| Replay | Agent Replay Bundle | Can we reconstruct this run? | Portable replay record |
| Evidence | Agent Governance Evidence Pack | What evidence supports deployment review? | Business-facing evidence package |

## Why it matters

The stack provides a usable chain from declared action surface to runtime policy decision, from run reconstruction to deployment review. That helps teams demonstrate how a governed deployment was expected to behave, what it attempted, what was blocked, what context mattered, and what evidence can be reviewed by business stakeholders.

## What it is not

Cognous Open Control Stack is not an agent framework, a model runtime, a hosted dashboard, a complete enterprise AI governance platform, a compliance certification product, a security boundary by itself, or a substitute for application authorization.

## ODES distinction

ODES, the Open Decision Evidence Standard, is a separate proposed open, vendor-neutral public standard for portable decision evidence in AI-mediated and cross-boundary decisions.

Cognous Open Control Stack is not ODES and does not define ODES conformance. The relationship is optional mapping and supporting evidence, not identity and not conformance.

## Practical next step

Start with one bounded agent workflow. Declare its action surface, record proposed actions and policy decisions, package one run as a replay bundle, and produce one governance evidence pack. The goal is to prove one full artifact chain: Declare → Control → Replay → Evidence.
