<!-- cognous-banner:start -->
```text
──────────────────────────────────────────────────
   __________  _______   ______  __  _______
  / ____/ __ \/ ____/ | / / __ \/ / / / ___/
 / /   / / / / / __/  |/ / / / / / / /\__ \
/ /___/ /_/ / /_/ / /|  / /_/ / /_/ /___/ /
\____/\____/\____/_/ |_/\____/\____//____/
       O P E N   C O N T R O L   S T A C K
       g o v e r n e d   b y   d e s i g n
  github.com/cogno-us/cognous-open-control-stack
──────────────────────────────────────────────────
```
<!-- cognous-banner:end -->

# Cognous Open Control Stack

**Open reference infrastructure for governed agent actions and traceable decision evidence.**

## Overview

The stack connects a declared action to independently supplied institutional authority, runtime authorization, a constrained destination effect and reviewable evidence. It helps an evaluator follow what was proposed, what was permitted at effect time, what was attempted and what the destination was observed to do.

**Status:** a merged, pinned **bounded synthetic reference**, with accepted persistence and a separately accepted protected-worker campaign. It is not a production deployment, compliance certification or proof of institutional adoption. The [component lock](component-lock.json) defines the supported integration; newer component releases are not selected automatically.

## Purpose and intended users

Agent workflows create a practical accountability problem: a model response, tool receipt or event log may not identify the authority for an action or whether the intended effect actually occurred. A timeout can conceal a committed effect; a later denial can coexist with earlier valid execution. Review needs those facts kept separate and connected.

Engineers can evaluate the public contracts and failure behavior. Enterprise architects, security teams, risk owners and governance reviewers can inspect the authority boundaries, retained artifacts and deployment gaps. The reference gives them a concrete synthetic workflow and reproducible evidence, without requiring commercial components or private research.

## Key capabilities

- **Explicit declarations:** bind an operation to a Manifest rather than interpreting a tool name as permission.
- **Independent authority:** resolve the institutional context outside the incoming message and revalidate critical inputs at effect time.
- **Bounded execution:** constrain the local synthetic refund destination and bind effects to exact operation content.
- **Durable history:** retain decisions, attempts, observations and evidence lineage through supported interruption and recovery cases.
- **Traceable review:** reconstruct producer records and derive Evidence Pack and ODES artifacts without treating a summary as independent verification.
- **Executable qualification:** resolve required scenarios to actual test evidence, compare two isolated repetitions and preserve characterized limitations.

## Components and responsibilities

| Component | Function and boundary |
|---|---|
| [Cognous Action Manifest](https://github.com/cogno-us/cognous-action-manifest) | A lightweight format, Python validator and CLI for describing the actions an AI agent may propose. Manifest 1.1 adds deterministic runtime bindings so a downstream controller can compare a proposal with a specific declared action. |
| [Cognous Control Plane](https://github.com/cogno-us/cognous-control-plane) | A Python reference implementation for bounded agent authorization, effect-time revalidation and persistent runtime records. It connects declared actions, independently resolved authority, execution attempts and reconciliation without treating an earlier decision as a permanent credential. |
| [Cognous Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) | A portable reconstruction format, importer, validator and CLI for agent-run evidence. Reconstruction Bundle 0.2.0 imports exact supported producer revisions while keeping legacy bundle formats and historical provenance distinct. |
| [Cognous Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | A reference format, validator, traceable importer and Markdown renderer for business-facing review of agent governance records. It preserves the relationship between a declared action surface and reconstructed runtime evidence instead of treating a summary as independent assurance. |
| [Open Decision Evidence Standard](https://github.com/cogno-us/open-decision-evidence-standard) | ODES is an open, vendor-neutral discussion draft and reference tooling for portable decision evidence. The v0.2 narrative and implementation profile retain the pder-v0.1 record schema. It carries coordinates for recipient evaluation, rather than deciding whether a recipient should rely on the underlying decision. |
| [Cognous Governed Exchange](https://github.com/cogno-us/cognous-governed-exchange) | An experimental GAX/IMX reference that connects governed messages, recipient assessment, bounded execution and retained evidence. It is separate from the constitutional authority repository: this workbench implements exchange behavior and local transport, not an institution or a constitution. |
| [Cognous Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) | The Python execution layer under engine/ provides the stack's bounded synthetic destination and adapter boundary. The repository also retains the upstream TypeScript Moltbot application; that application is outside the reviewed Cognous Python execution boundary. |
| [Cognous Evidence Attestation](https://github.com/cogno-us/cognous-evidence-attestation) | A binary-attestation protocol and reference verifier. The accepted v1 interface checks Ed25519 signatures against an operator-configured issuer-key trust snapshot and evaluation time. A successful result means issuer_signature_only under those conditions, not factual truth or institutional authority. |
| [Cognous Evidence Registry](https://github.com/cogno-us/cognous-evidence-registry) | A protocol and reference implementation for registering scientific claims, linking evidence commitments and preserving revision/lifecycle history. The accepted bounded slice makes the local blockchain contract authoritative for those records and uses Cognous Evidence Attestation verification independently off-chain. |
| [Portable Reasoning Protocol v1.0](https://github.com/cogno-us/portable-reasoning-protocol) | PRP is a reusable SKILL.md-based instruction package for general-purpose AI work. It asks a model to calibrate rigor to consequence, distinguish evidence from inference, state material uncertainty and preserve the user's agency. These are behavioral instructions, not runtime enforcement. |
| [Research Intelligence Protocol v1.0](https://github.com/cogno-us/research-intelligence-protocol) | A modular SKILL.md-based research workflow with two distinct components: Discovery structures observations, hypotheses and discriminating experiments; Abstractor of Abstractors (AoA) compares structure and proposes transferable invariants with explicit limits. |
| [TFA Protocol (S43)](https://github.com/cogno-us/truth-freedom-agency-protocol) | A lightweight optional behavioral protocol for AI interaction. Its identity remains three rules: Say what is true. Ask for nothing. Protect their next move. Implementation and evaluation guidance explain those rules without making them an authority system. |
| [Cognous Institutional Governance](https://github.com/cogno-us/cognous-institutional-governance) | An open research framework for businesses, public bodies and communities, with or without AI. It combines proposed constitutional designs, proportional governance, domain guidance, decision templates and a public-stack implementation profile. Repository acceptance does not ratify a constitution. |

The constitutional authority repository and Cognous Governed Exchange workbench are separate. Within the workbench, **GAX** supplies exchange semantics, **LocalDurableTransport** supplies local delivery/redelivery, and **IMX** supplies continuity records. Receipt, understanding, acceptance, authorization, execution, observation and verification are distinct states.

Cognous Evidence Attestation and Cognous Evidence Registry form a separate evidence path. PRP, Research Intelligence and TFA are optional instruction layers, not enforcement dependencies. A signature, chain inclusion, message receipt or reasoning protocol does not authorize execution. See the [responsibility map](docs/architecture.md) for trust boundaries and identity namespaces.

## One supported workflow

The representative operation is a synthetic refund, delivered through local durable transport to the GAX recipient adapter. The adapter assesses the message and produces a Manifest-bound proposal. A separately configured resolver supplies Authority Context; the Control Plane decides and revalidates before the constrained executor reaches the SQLite destination.

The hub consumes the original retained Replay, ODES and IMX artifacts associated with that transported operation and produces a Governance Evidence Pack. It checks effect content and count, decision/effect/attempt continuity, original artifact commitments and recipient assurance limits. It does not substitute an unrelated direct execution for evidence of the delivered message.

## Getting started

Use a disposable Linux checkout, Git, an activated Python environment and the Node/npm prerequisites in the [developer quickstart](docs/quickstart.md). Reference CI uses Python 3.11 and Node 20. Dependency setup requires GitHub and package-registry access; no production credentials, Docker or OpenShell installation is needed for the standard mocked-adapter run.

```bash
git clone https://github.com/cogno-us/cognous-open-control-stack.git
cd cognous-open-control-stack
python3.11 -m venv .venv
source .venv/bin/activate
python tools/reference_release.py --help
python tools/reference_release.py run --results-dir results/reference
```

The runner checks out the exact lock, installs dependencies into the active environment and runs two isolated repetitions. It replaces the named results directory and, by default, `.reference-work/`; keep personal changes out of runner-owned paths and use a new results path when preserving an earlier run. See the quickstart for exact-baseline reproduction and checkout-reuse rules.

Start review with `results/reference/scenario-results.json`, then inspect the resolved scenario matrix, repeatability, skip accounting and artifact index. A required missing, skipped, failed or unexecuted scenario blocks the release gate. A passing characterization of a known limitation does not mean the limitation was prevented.

## Tested guarantees and their boundaries

| Accepted evidence | What was demonstrated | Scope that remains outside the claim |
|---|---|---|
| [Historical persistence-generation qualification](examples/control-plane-store-adoption/qualification-summary.json) | Two repetitions of 915 Python tests, 35 matrix entries satisfying their gates, repeatable representative outcomes and 120 separate mocked OpenShell tests | Production authentication, independent real-world verification and live OpenShell |
| [Shared-store persistence](https://github.com/cogno-us/cognous-control-plane/blob/248d899634d9db3518e831bc7ab568a48733f825/docs/record-store-persistence.md) | Cooperating same-host record transactions preserve supported concurrent writes and process-interruption behavior on documented local Linux filesystems | Whole-workflow atomicity, cross-host persistence and remote exactly-once delivery |
| [Recovery qualification](docs/recovery-semantics.md) | Same-effect continuity, original-effect reconciliation, accepted/rejected observations and changed-authority denial separated from historical execution | Retry permission from absence, rollback, cancellation or remote finality |
| [Protected-worker campaign](docs/workstreams/protected-qualification-checkpoint.md#completed-compatible-host-review) | Twelve isolated cases and 17 verifier tests passed on the recorded Ubuntu 22.04/bubblewrap environment | OpenShell, arbitrary agents, production credentials or general production non-bypassability |

### Protected-worker qualification

The historical qualified profile uses a fixed synthetic worker under separate mount, PID and network namespaces. A trusted host owns authority, execution and the destination; direct destination reads, canary hashes and a controlled host-loopback sink check the worker's claims and attempted alternate paths. One authorized control must produce exactly one expected effect; payload, target and adapter substitutions, missing authority and forged success produce none.

Qualification applies to **Ubuntu 22.04.5, Linux 6.8.0-1064-azure, bubblewrap 0.6.1 and Python 3.11.16**, six scenarios repeated twice. It does not demonstrate model prompt-injection resistance or arbitrary-program confinement. The earlier Ubuntu 24.04 campaign remains blocked, with its evidence preserved. See the [profile and prerequisites](docs/protected-qualification.md), [actual campaign](examples/protected-qualification/ci-37621009389/campaign/summary.json) and [source/CI provenance](examples/protected-qualification/ci-37621009389/provenance.json).

## Recovery and remaining limitations

Unknown acknowledgement does not imply absence. Accepted `observed_absent` is point-in-time evidence, not retry permission: an original in-flight effect can still commit. Reconciliation concerns that original effect and preserves acknowledgement history. A newly denied recovery request does not erase a historical applied effect. Retained originals and recovery derivatives keep separate identities and lineage.

**Logical-intent prevention is present in the selected executor source but is not enabled by the bounded integration path.** Different valid proposals for equivalent business intent can still create multiple effects in the selected reference. Effect-ID deduplication is not business-intent deduplication.

Live OpenShell execution/confinement, production institutional authentication, credential custody, deployment-wide bypass resistance, distributed budgets, remote finality and independent real-world verification remain unqualified. No rollback or exactly-once delivery guarantee is made. Human-review efficiency, model-behavior improvements and enterprise outcomes have not been measured by the reference tests.

## Paired-request enforcement qualification

A dedicated Worker 22 qualification compares the **same frozen shared request fields** under an isolated permissive synthetic baseline and the accepted Cognous Control Plane/executor path. The deterministic required batch uses constructed unsafe requests; it does **not** claim observed model compromise, prompt-injection resistance or population attack rates. The pairing gate compares the action, target, payload, actor, principal, amount, unit and requested permissions actually supplied to each condition. Institution/domain are trusted resolver context on the accepted path and are excluded from the paired caller fields; operation identity is a scenario label. Selection, authorization, dispatch, tool outcome, direct destination observation and recovery are recorded separately, and invalid/skipped cases remain visible in scheduled denominators.

The experiment is intentionally narrower than an end-to-end agent benchmark. Disclosure coverage is unavailable in the accepted refund adapter, and task completion is not measured. Same-business-intent behavior is reported exactly as selected today; the refund-intent execution profile is not enabled by the selected path. See the [matrix](scenarios/paired-request-enforcement-matrix.v2.json) and [checkpoint](docs/workstreams/paired-request-enforcement-checkpoint.md).

In this repository, **paired replay** means the experimental comparison of an identical frozen request across enforcement conditions. It is not Cognous Replay Bundle reconstruction.

## Merged profiles and engineering roadmap

The optional same-host authority/effect profile has merged through [Control Plane PR #12](https://github.com/cogno-us/cognous-control-plane/pull/12), [Execution Runtime PR #25](https://github.com/cogno-us/cognous-execution-runtime/pull/25) and [hub PR #16](https://github.com/cogno-us/cognous-open-control-stack/pull/16). [Qualification run 37682165860](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860) passed 73 tests against its exact reviewed source revisions. It orders cooperating authority mutations, claim and budget consumption, and the protected synthetic effect through the declared trusted handoff and authoritative SQLite transaction.

The lock selects source containing this profile, but the bounded workflow **does not enable it**. Its qualification does not establish external-destination atomicity, distributed authorization or production readiness. Refund-intent ownership and authority/effect profiles remain mutually exclusive per database; no combined guarantee is implied. The [current checkpoint](docs/workstreams/worker21-authority-effect-checkpoint.md#acceptance-update-7-october-2026) distinguishes tested source revisions from subsequent merge revisions.

The [consolidated engineering register](docs/engineering-register.md) reconciles the research addenda with current evidence. Information-flow/context, governed memory, continued-authority trajectories and developmental-autonomy proposals are tracked as scoped future work, not automatically adopted requirements.

## Documentation and collateral

- [Developer quickstart](docs/quickstart.md) and [governance reviewer quickstart](docs/governance-quickstart.md).
- [Architecture](docs/architecture.md), [compatibility](docs/compatibility.md) and [support status](docs/release-status.md).
- [Evidence index](docs/evidence-index.md), [recovery semantics](docs/recovery-semantics.md), [threat model](docs/security-and-threat-model.md) and [risk register](residual-risks.json).
- [Business collateral](collateral/business-collateral.md) and [one-page overview](collateral/one-page-overview.md).

## Contributing and attribution

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md). Keep changes bounded, preserve historical evidence and qualify new behavior before extending support claims. Runtime implementations remain in their owning repositories.

Developed by [Cognous](https://cogno.us). See [LICENSE](LICENSE), [NOTICE](NOTICE) and [licensing inventory](LICENSING.md). ISS, Navalia and private research remain outside this public integration.

---

## Bibliography

Selected external sources from the October 2026 research review. These inform evaluation questions; they do not establish Cognous implementation, adoption, conformance or production qualification.

- [OECD. *Agentic AI in organisations: Early insights from practitioner interviews*. OECD Artificial Intelligence Papers, No. 65 (2026)](https://doi.org/10.1787/1257a26f-en). Qualitative practitioner research on bounded autonomy, oversight and organizational deployment.
- [OWASP GenAI Security Project. *State of Agentic AI Security and Governance*, version 2.01 (June 2026)](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/). Security synthesis covering agent identity, delegated permissions, tool access and containment.
- Jonathan Chadbourne / JCEE Labs. *When a Timeout Is Not a Failure: Authority, Evidence, and Recovery in Consequential AI Execution*. Technical Note 001, public release v0.1.1 (6 October 2026). Technical note on uncertain outcomes and recovery. An original public URL has not been verified; no substitute or private copy is linked.
- [Alexander Barrett. *Boundary Blindness Under Artificial Intelligence: Early Cross-Industry Findings on the Missing Decision-Evidence Layer* (2026)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7210798). Working paper on carrying the basis for reliance across organizational boundaries; proposed architecture, not a validated interoperability guarantee.
- [John W. Creswell and J. David Creswell. *Research Design: Qualitative, Quantitative, and Mixed Methods Approaches*, fifth edition. SAGE (2018)](https://edge.sagepub.com/creswellrd5e). Research-methods reference for explicit questions, comparison designs and interpretation limits.

- [Tural Hagverdiyev. *Compromise Is Not Consequence: Evaluating Task-Scoped Authorization in LLM Agents with Paired Replay*. arXiv:2610.05840v1 (5 October 2026)](https://arxiv.org/abs/2610.05840v1). External research on fixed-request enforcement comparisons; its reported results are not Cognous qualification evidence.

See the [research bibliography](docs/research-bibliography.md) for review scope and source-verification limits.

## Component cross-links

| Component | Responsibility |
|---|---|
| [Cognous Action Manifest](https://github.com/cogno-us/cognous-action-manifest) | Declare the action before evaluating permission. |
| [Cognous Control Plane](https://github.com/cogno-us/cognous-control-plane) | Evaluate proposals against authority and preserve the decision record. |
| [Cognous Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) | Reconstruct what the retained records support. |
| [Cognous Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | Turn traceable runtime records into reviewable governance evidence. |
| [Open Decision Evidence Standard](https://github.com/cogno-us/open-decision-evidence-standard) | Portable decision evidence across system and organizational boundaries. |
| [Cognous Governed Exchange](https://github.com/cogno-us/cognous-governed-exchange) | Governed exchange and continuity for a bounded synthetic workflow. |
| [Cognous Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) | Constrained execution beneath independent current authorization. |
| [Cognous Evidence Attestation](https://github.com/cogno-us/cognous-evidence-attestation) | Verify issuer signatures under explicit trust assumptions. |
| [Cognous Evidence Registry](https://github.com/cogno-us/cognous-evidence-registry) | A local blockchain reference for claims, evidence commitments and lifecycle history. |
| [Portable Reasoning Protocol v1.0](https://github.com/cogno-us/portable-reasoning-protocol) | Portable instructions for evidence-bounded reasoning. |
| [Research Intelligence Protocol v1.0](https://github.com/cogno-us/research-intelligence-protocol) | Disciplined discovery and cross-domain abstraction, kept separate. |
| [TFA Protocol (S43)](https://github.com/cogno-us/truth-freedom-agency-protocol) | Truth · Freedom · Agency. |
| [Cognous Institutional Governance](https://github.com/cogno-us/cognous-institutional-governance) | Alvorada: authority, challenge and correction for institutions. |

## Repository locations

See the [repository rename map and compatibility notes](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/repository-renames.md) for current component URLs. Existing package names, schema identifiers and retained producer identities are unchanged.

### Merged consumer chain candidate

The [merged-chain checkpoint](docs/workstreams/merged-consumer-chain-checkpoint.md) records bounded hub recovery and transported-workflow qualification against the newly accepted consumers. Its [candidate profile](profiles/merged-consumer-chain.json) is separate from the accepted release lock; passing it does not claim the full release matrix has passed.

The [full candidate release checkpoint](docs/workstreams/full-candidate-release-checkpoint.md) describes the four bounded batches and aggregate acceptance gate for the newer revision set. Candidate evidence remains separate from the accepted component lock until explicit adoption.

### Merged-generation adoption

The hub selects the exact revisions that passed the full 35-scenario candidate matrix. [Compatibility](docs/compatibility.md) lists the selected versions; the [adoption checkpoint](docs/workstreams/merged-pin-adoption-checkpoint.md) records the separate adoption-head checks. Source selection does not enable optional atomic-claim or refund-intent execution profiles.

### Optional execution profiles

Explicit hub commands now activate the accepted atomic authority/effect or refund-intent implementation for synthetic local execution. They use separate databases and separate evidence; the ordinary release path remains the default. See [optional execution profiles](docs/optional-execution-profiles.md) for commands, Linux batches, and boundaries.

### V1 reference extensions

[Environment preflight, governed context/memory, two-step temporal authority, and institutional review](docs/v1-reference-profiles.md) now have explicit synthetic reference entry points and separate bounded Linux checks. Their coverage ledger distinguishes executable local controls from remaining runtime integrations and deployment prerequisites. See [deployment responsibilities](docs/v1-deployment-responsibilities.md) before planning a real pilot.

### Bound context, notification and recovery

[Context-to-action binding, independently authorized notification, and SQLite staging recovery](docs/context-notification-recovery.md) extend the explicit reference profiles. They retain exact operation/claim binding, separate notification authority, and restored consumption history. Their scope excludes production activation, remote delivery and cross-database atomicity.

### V1 extension release evidence

The [v1 extension evidence gate](docs/v1-extension-release-gate.md) requires all seven Linux batches and 91 profile tests against the same source revision and component lock. It rejects missing, changed, skipped or mixed-revision evidence. This complements the existing reference release gates; it does not authorize execution or establish production readiness.

### Deployment review evidence

The optional [deployment review packet](docs/deployment-review-packet.md) checks named responsibility coverage, declared environment/configuration scope, retained file digests and freshness. Its template remains incomplete by design. A complete packet prepares human review; it grants no authority and establishes no production readiness.
