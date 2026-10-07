# Cognous Open Control Stack — Business Collateral

## 1. Executive Summary

Cognous Open Control Stack is open reference infrastructure for evaluating governed agent actions. It connects an action declaration, independently supplied institutional authority, bounded runtime execution and retained review evidence. The accepted implementation is synthetic and pinned; it is not a production platform, institutional adoption or certification.

## 2. The Business Problem

An organization needs to explain more than what a model said or which tool it called. It needs to know what was proposed, who could authorize it, whether that authority was current when the effect was attempted and what was actually observed at the destination. Timeouts, duplicate messages and later authority changes make these different questions.

The reference supplies a connected artifact chain for examining those questions. It does not quantify cost savings, review efficiency or deployment outcomes.

## 3. The Stack in One View

| Component | Responsibility |
|---|---|
| [Agent Action Manifest](https://github.com/cogno-us/cognous-agent-action-manifest) | Declare the action before evaluating permission. |
| [Agent Control Plane](https://github.com/cogno-us/cognous-agent-control-plane) | Evaluate proposals against authority and preserve the decision record. |
| [Agent Replay Bundle](https://github.com/cogno-us/cognous-agent-replay-bundle) | Reconstruct what the retained records support. |
| [Agent Governance Evidence Pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack) | Turn traceable runtime records into reviewable governance evidence. |
| [Open Decision Evidence Standard](https://github.com/cogno-us/open-decision-evidence-standard) | Portable decision evidence across system and organizational boundaries. |
| [Alvorada Experimental Workbench](https://github.com/cogno-us/alvorada) | Governed exchange and continuity for a bounded synthetic workflow. |
| [Moltbot Safe](https://github.com/cogno-us/moltbot-safe) | Constrained execution beneath independent current authorization. |
| [BitRep](https://github.com/cogno-us/bitrep) | Verify issuer signatures under explicit trust assumptions. |
| [The Index](https://github.com/cogno-us/the-index) | A local blockchain reference for claims, evidence commitments and lifecycle history. |
| [Portable Reasoning Protocol v1.0](https://github.com/cogno-us/portable-reasoning-protocol) | Portable instructions for evidence-bounded reasoning. |
| [Research Intelligence Protocol v1.0](https://github.com/cogno-us/research-intelligence-protocol) | Disciplined discovery and cross-domain abstraction, kept separate. |
| [TFA Protocol (S43)](https://github.com/cogno-us/truth-freedom-agency-protocol) | Truth · Freedom · Agency. |
| [Constitutional Governance for Institutions](https://github.com/cogno-us/constitutional-governance-for-institutions) | Alvorada: authority, challenge and correction for institutions. |

## 4. Declare and Establish Authority

Action Manifest describes the action surface and its binding requirements. Alvorada's constitutional repository supplies an institutional design and Authority Context profile. The trusted runtime resolver must supply actual bounded authority independently of incoming requests. Declaration, signature verification and evidence inclusion cannot create a grant.

## 5. Control and Execute

The Control Plane records proposals and decisions and revalidates critical authority/evidence before execution. Moltbot Safe constrains a local synthetic SQLite refund destination. Its effect identity and content binding suppress supported same-effect duplicates; the selected reference does not prevent all equivalent business intent across different valid proposals.

## 6. Exchange and Recover

GAX defines governed exchange semantics, local durable transport handles delivery/redelivery and IMX carries continuity. Unknown acknowledgement remains distinct from destination observation. Fresh absence cannot authorize retry; an original request can commit later. A current denied recovery and a historical applied effect can coexist without contradiction when recorded separately.

## 7. Reconstruct and Review

Replay reconstructs retained producer records without rerunning execution. Governance Evidence Pack produces traceable review material. ODES carries portable decision evidence for a recipient's own validation and reliance decisions. Original artifacts, recovery derivatives and source assertions remain distinguishable.

## 8. A Supported Workflow

Run one synthetic refund through transport, recipient assessment, Manifest binding, independent authority resolution, effect-time revalidation and constrained execution. Inspect the retained artifacts associated with that exact operation. The reference checks content, counts, identities, commitments and unresolved outcomes in two isolated repetitions.

## 9. What Accepted Evidence Establishes

The [persistence-generation summary](../examples/control-plane-store-adoption/qualification-summary.json) records 915 Python tests per repetition, 35 matrix entries satisfying their gates and 120 separately mocked OpenShell tests. The selected store repair supports cooperating record writers on documented local Linux filesystems, not a transaction across an entire workflow or distributed infrastructure.

The [protected campaign](../examples/protected-qualification/ci-37621009389/campaign/summary.json) adds twelve isolated cases and 17 verifier tests on Ubuntu 22.04.5, Linux 6.8.0-1064-azure, bubblewrap 0.6.1 and Python 3.11.16. That fixed worker fixture checks denied private-path access, a controlled host sink, namespace separation and exact destination outcomes. Earlier Ubuntu 24.04 failure remains preserved. This is not OpenShell qualification, model prompt-injection testing or arbitrary-agent containment.

## 10. Remaining Limits

[Executor PR #14](https://github.com/cogno-us/moltbot-safe/pull/14) remains pending acceptance; logical-intent prevention is not hub-supported. Live OpenShell, production resolver authentication, real credential isolation, deployment-wide non-bypassability, remote finality, distributed budgets and independent real-world verification remain unqualified. No rollback or exactly-once guarantee is made.

## 11. Why Open Source Matters

Public contracts, implementation, tests and retained failures allow an evaluator to inspect and reproduce the bounded claim. They expose compatibility and deployment assumptions that a summary alone could obscure. Openness enables review; it does not replace operational responsibility or independent assurance.

## 12. Practical Next Step

Use the [developer quickstart](../docs/quickstart.md), then review the actual outputs with the [governance quickstart](../docs/governance-quickstart.md). Choose one intended deployment and identify which authority, destination, credential and enforcement assumptions differ from the reference. Those differences require their own acceptance evidence.

## 13. Status and Attribution

This document describes merged evidence at hub `5737267d94d2b445735c95e8480a31de73a2abe8`. [Selected pins](../component-lock.json), [support status](../docs/release-status.md) and [evidence index](../docs/evidence-index.md) control the interpretation. It includes no private source text or proprietary implementation detail.

[Cognous](https://cogno.us) · [README](../README.md) · [One-page overview](one-page-overview.md). Existing licenses and notices apply.
