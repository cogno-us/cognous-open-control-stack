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

**Status:** a merged, pinned **bounded synthetic reference** (label: **selected** for the components pinned in the [component lock](component-lock.json); see the labels below). It is not a production deployment, compliance certification or proof of institutional adoption. Linux only. Operational trust remains HOLD ([#30](docs/operational-trust-status.md)). Contract drafts keep the label `0.1.0-draft`. The lock defines the supported integration; newer component releases are not selected automatically.

**New reader?** Run the [five-minute offline path](#try-it-in-five-minutes), then use [Start here](docs/start-here.md) for developer and reviewer paths, the worked refund example and the difference between selected revisions, source acceptance and deployment trust. The [documentation index](docs/README.md) lists every hub page. The hub [component lock](component-lock.json) and [release status](docs/release-status.md) govern selected-release claims; historical evidence remains labeled by its original revision.

<a id="overview"></a>
<a id="purpose-and-intended-users"></a>
<a id="key-capabilities"></a>

## What it is, who it is for, what it does not do

The stack connects a declared action to independently supplied institutional authority, runtime authorization, a constrained destination effect and reviewable evidence. It helps an evaluator follow what was proposed, what was permitted at effect time, what was attempted and what the destination was observed to do.

Agent workflows create a practical accountability problem: a model response, tool receipt or event log may not identify the authority for an action or whether the intended effect actually occurred. A timeout can conceal a committed effect; a later denial can coexist with earlier valid execution. Review needs those facts kept separate and connected.

Engineers can evaluate the public contracts and failure behavior. Enterprise architects, security teams, risk owners and governance reviewers can inspect the authority boundaries, retained artifacts and deployment gaps. The reference gives them a concrete synthetic workflow and reproducible evidence, without requiring commercial components or private research.

**What it does not do.** It is not a production service, a compliance certification or an authorization to connect a real destination; a signature, registry entry, message receipt or evidence summary does not grant execution authority. The stack-level statement of scope and limits (Linux only; certification is not truth; the prevention claim and its assumptions; known limits) is made once in [what the stack guarantees and what it does not](docs/guarantees-and-limits.md) and is linked from other pages rather than repeated.

**Key capabilities** (bounded synthetic reference):

- **Explicit declarations:** bind an operation to a Manifest rather than interpreting a tool name as permission.
- **Independent authority:** resolve the institutional context outside the incoming message and revalidate critical inputs at effect time.
- **Bounded execution:** constrain the local synthetic refund destination and bind effects to exact operation content.
- **Durable history:** retain decisions, attempts, observations and evidence lineage through supported interruption and recovery cases.
- **Traceable review:** reconstruct producer records and derive Evidence Pack and ODES artifacts without treating a summary as independent verification.
- **Executable qualification:** resolve required scenarios to actual test evidence, compare two isolated repetitions and preserve characterized limitations.

## Try it in five minutes

An offline path that needs no qualification checkout and no Node. It uses the ergonomics front door, which runs the real pinned component command-line tools on a bundled synthetic example.

Prerequisites: Linux, Python 3.11 or newer, Git, and network access to GitHub once (the `stack` extra installs the four component tools through pinned git references; after that the demo runs offline).

```bash
git clone https://github.com/cogno-us/cognous-open-control-stack-ergonomics
cd cognous-open-control-stack-ergonomics
python3 -m venv .venv && . .venv/bin/activate
pip install ".[stack]"
cognous-ocs --version
cognous-ocs demo customer-service --out demo-out
cognous-ocs evidence render demo-out/outputs/evidence-pack.json --out view.html
```

Expected output (exit code 0 for each command). `--version` prints the CLI, contract, example and bundled-component lines; the bundled-component revisions are the ergonomics pins; the hub lock records the selected revisions:

```text
cognous-ocs 0.1.0
cli-contract 0.1.0
bundled-example customer-service 0.2.0
bundled-component aam cogno-us/cognous-action-manifest@ff5490828b2b
bundled-component acp cogno-us/cognous-control-plane@2bac7875391c
bundled-component arb cogno-us/cognous-replay-bundle@6a6a477495ac
bundled-component agep cogno-us/cognous-governance-evidence-pack@fd030615a782
```

The demo then prints (first lines):

```text
demo: pass (exit 0)
  the blocked email_send is evidenced in all four layers (19 component commands run offline, every exit code as expected); acp run held it: grant_scope_mismatch; view: evidence.html
  verdict source: control-plane (bounded-authorization-effect 0.1.0)
```

followed by a long `does not prove` line. `evidence render` prints `evidence render: pass (exit 0)` and writes one self-contained HTML file of about 5 KB. Run time: the whole sequence, including the clone and install, took about 15 seconds on one Linux host with Python 3.13 (the demo itself about 5 seconds); a loaded host or slower network can take longer. Verified by running exactly the commands above in a fresh virtual environment against ergonomics `main` at commit `6fea3f5` on 2026-10-19. <!-- pin-round: re-verify this section after the ergonomics pins refresh -->

What this does not prove: a passing demo shows that the pinned components, run on synthetic inputs, block the email send and evidence it in every layer. It does not show that any real action was blocked, that a grant came from an institution, or anything about deployment. `evidence render` does not validate the pack it draws. See [guarantees and limits](docs/guarantees-and-limits.md) and the ergonomics [README](https://github.com/cogno-us/cognous-open-control-stack-ergonomics/blob/main/README.md). If you install without the `stack` extra, `demo` fails closed with exit code 2 and reason code `OCS_VERSION`; that is intended behaviour, not a bug.

<a id="components-and-responsibilities"></a>
<a id="component-cross-links"></a>
<a id="repository-locations"></a>

## Where it fits: the stack map

<!-- stack-map:start -->
<!-- Canonical block: identical text in every component README. Source: docs/stack-map.md in the hub. Refresh at the pin round. -->
The Open Control Stack groups its repositories by responsibility. The groups are a navigation map, not an execution sequence and not a requirement to install every component. The hub [component lock](https://github.com/cogno-us/cognous-open-control-stack/blob/main/component-lock.json) is the only source of selected revisions; [release status](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) states their evidence and limits. The component revisions selected for the stack are listed in the hub's `component-lock.json`; this repository does not record which hub commit it was last checked against.

| Group | Members |
| --- | --- |
| **01 Knowledge & Provenance** | [Evidence Registry (The Index)](https://github.com/cogno-us/cognous-evidence-registry) · [Evidence Attestation (BitRep)](https://github.com/cogno-us/cognous-evidence-attestation) |
| **02 Institutional Governance** | [Institutional Governance (Alvorada)](https://github.com/cogno-us/cognous-institutional-governance) |
| **03 Declaration & Policy Control** | [Action Manifest](https://github.com/cogno-us/cognous-action-manifest) · [Control Plane](https://github.com/cogno-us/cognous-control-plane) |
| **04 Constrained Execution** | [Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) |
| **05 Replay & Evidence** | [Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) · [Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) · [ODES](https://github.com/cogno-us/open-decision-evidence-standard) |
| **Cross-cutting exchange** | [Governed Exchange (GAX/IMX)](https://github.com/cogno-us/cognous-governed-exchange) |
| **Tooling and qualification** (side group) | [Ergonomics (`cognous-ocs`)](https://github.com/cogno-us/cognous-open-control-stack-ergonomics) · [Verifier](https://github.com/cogno-us/cognous-open-control-stack-verifier) · [Orchestrator](https://github.com/cogno-us/cognous-stack-orchestrator) · [Qualification](https://github.com/cogno-us/cognous-stack-qualification) |

Status labels used in this README: **merged** (reviewed and merged in the owning repository; not by itself selected), **selected** (pinned in the hub lock), **known limit** (a limitation that is stated and kept visible) and **proposed** (draft or planned work, not a supported interface). Full map, names and commands: [stack map](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/stack-map.md), [naming](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/naming.md), [profiles and tools](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/profiles-and-tools.md). A signature, registry entry, message receipt or evidence summary does not grant execution authority.
<!-- stack-map:end -->

One row per repository, with purpose, label and the page that indexes its documentation: [stack map](docs/stack-map.md). Display names, repository names, packages, commands and former names are collected in [naming](docs/naming.md); commands, profiles and tools per repository are in [profiles and tools](docs/profiles-and-tools.md). Repository location changes are in the [repository rename map](docs/repository-renames.md). Existing package names, schema identifiers and retained producer identities are unchanged. The five groups are a navigation and responsibility map, not an execution sequence or a change to selected interfaces.

### Components at a glance

| Component | Purpose | Label | Documentation index |
| --- | --- | --- | --- |
| [Evidence Registry (The Index)](https://github.com/cogno-us/cognous-evidence-registry) | Protocol and reference implementation for registering claims, linking evidence commitments and keeping revision and lifecycle history. | selected | [docs](https://github.com/cogno-us/cognous-evidence-registry/blob/main/docs/README.md) |
| [Evidence Attestation (BitRep)](https://github.com/cogno-us/cognous-evidence-attestation) | Binary-attestation protocol and reference verifier; a successful result means `issuer_signature_only`, not truth or institutional authority. | selected | [docs](https://github.com/cogno-us/cognous-evidence-attestation/blob/main/docs/README.md) |
| [Institutional Governance (Alvorada)](https://github.com/cogno-us/cognous-institutional-governance) | Open research framework for institutional governance; repository acceptance does not ratify a constitution. | selected | [docs](https://github.com/cogno-us/cognous-institutional-governance/blob/main/docs/README.md) |
| [Action Manifest](https://github.com/cogno-us/cognous-action-manifest) | Format, validator and CLI (`aam`) for declaring actions an agent may propose; a declaration is not permission. | selected | [docs](https://github.com/cogno-us/cognous-action-manifest/blob/main/docs/README.md) |
| [Control Plane](https://github.com/cogno-us/cognous-control-plane) | Bounded authorization, effect-time revalidation and persistent runtime records (`acp`). | selected | [docs](https://github.com/cogno-us/cognous-control-plane/blob/main/docs/README.md) |
| [Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) | Bounded synthetic destination and adapter boundary; live confinement is a known limit. | selected | [docs](https://github.com/cogno-us/cognous-execution-runtime/blob/main/docs/README.md) |
| [Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) | Portable reconstruction format, importer, validator and CLI (`arb`). | selected | [docs](https://github.com/cogno-us/cognous-replay-bundle/blob/main/docs/README.md) |
| [Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | Format, validator, importer and Markdown renderer for review packaging (`agep`); not independent assurance. | selected | [docs](https://github.com/cogno-us/cognous-governance-evidence-pack/blob/main/docs/README.md) |
| [ODES](https://github.com/cogno-us/open-decision-evidence-standard) | Open, vendor-neutral discussion draft and reference tooling for portable decision evidence (`odes`); record schema `pder-v0.1`. | selected | [docs](https://github.com/cogno-us/open-decision-evidence-standard/blob/main/docs/README.md) |
| [Governed Exchange (GAX/IMX)](https://github.com/cogno-us/cognous-governed-exchange) | Experimental reference connecting governed messages, recipient assessment, bounded execution and retained evidence. | selected | [README section](https://github.com/cogno-us/cognous-governed-exchange/blob/main/README.md#documentation-index) |
| [Ergonomics (`cognous-ocs`)](https://github.com/cogno-us/cognous-open-control-stack-ergonomics) | Front-door CLI: offline demo, evidence render, validation and CI entry; relays component verdicts, decides nothing. | merged | [README section](https://github.com/cogno-us/cognous-open-control-stack-ergonomics/blob/main/README.md#documentation-index) |
| [Verifier](https://github.com/cogno-us/cognous-open-control-stack-verifier) | Independent verifier for run records; produces a verification report, not an attestation. | selected | [docs](https://github.com/cogno-us/cognous-open-control-stack-verifier/blob/main/docs/README.md) |
| [Orchestrator](https://github.com/cogno-us/cognous-stack-orchestrator) | Engineering integration and evidence coordination in bounded synthetic qualification tests. | merged | [docs](https://github.com/cogno-us/cognous-stack-orchestrator/blob/main/docs/README.md) |
| [Qualification](https://github.com/cogno-us/cognous-stack-qualification) | Cross-component scenarios, relocated suites and qualification records. | merged | [docs](https://github.com/cogno-us/cognous-stack-qualification/blob/main/docs/README.md) |

Ergonomics, orchestrator and qualification sit beside the lock and do not select component revisions; the verifier is a lock entry. Full per-row limits are on the [stack map](docs/stack-map.md).

## One supported workflow

The representative operation is a synthetic refund, delivered through local durable transport to the GAX recipient adapter. The adapter assesses the message and produces a Manifest-bound proposal. A separately configured resolver supplies Authority Context; the Control Plane decides and revalidates before the constrained executor reaches the SQLite destination.

The hub consumes the original retained Replay, ODES and IMX artifacts associated with that transported operation and produces a Governance Evidence Pack. It checks effect content and count, decision/effect/attempt continuity, original artifact commitments and recipient assurance limits. It does not substitute an unrelated direct execution for evidence of the delivered message.

<a id="source-selection"></a>
<a id="optional-execution-profiles"></a>
<a id="v1-reference-extensions"></a>
<a id="bound-context-notification-and-recovery"></a>
<a id="v1-extension-release-evidence"></a>
<a id="deployment-review-evidence"></a>

## What ships in this repository

This repository holds the component lock, selection profiles, opt-in reference profile modules, tools, scenario matrices, retained evidence and documentation. Runtime implementations remain in their owning repositories. The complete catalogue (name, purpose, entry point, label, owning page) is [profiles and tools](docs/profiles-and-tools.md).

| What | Where | Label | Notes and page |
| --- | --- | --- | --- |
| Component lock | [`component-lock.json`](component-lock.json) | selected | The only source of selected revisions. [Compatibility](docs/compatibility.md) describes selected interfaces. Source selection does not enable optional atomic-claim or refund-intent execution profiles. |
| Selection and candidate profiles | `profiles/` (9 files) | merged | Candidate and diagnostic profiles; two are proposed (reference-only selection, W7 candidate lock). [Profiles](docs/profiles-and-tools.md#hub-selection-profiles). |
| Reference profile modules | `reference_profiles/` (16 modules) | merged | Opt-in synthetic references for a trusted host; they grant no authority. [Modules](docs/profiles-and-tools.md#hub-reference-profile-modules). |
| Optional execution profiles | [optional execution profiles](docs/optional-execution-profiles.md) | merged | Explicit hub commands activate the accepted atomic authority/effect or refund-intent implementation for synthetic local execution, with separate databases and separate evidence; the ordinary release path remains the default. Known limit: the bounded workflow does not enable them. |
| V1 reference extensions | [V1 reference profiles](docs/v1-reference-profiles.md) | merged | Environment preflight, governed context/memory, two-step temporal authority and institutional review have explicit synthetic reference entry points and separate bounded Linux checks. The coverage ledger distinguishes executable local controls from remaining runtime integrations and deployment prerequisites; see [deployment responsibilities](docs/v1-deployment-responsibilities.md) before planning a real pilot. |
| Bound context, notification and recovery | [context, notification and recovery](docs/context-notification-recovery.md) | merged | Context-to-action binding, independently authorized notification and SQLite staging recovery extend the explicit reference profiles. They retain exact operation/claim binding, separate notification authority and restored consumption history. Known limit: scope excludes production activation, remote delivery and cross-database atomicity. |
| V1 extension evidence gate | [extension release gate](docs/v1-extension-release-gate.md) | merged | Requires all seven Linux batches and 111 profile tests (contract `v1-reference-extension-evidence/5`) against the same source revision and component lock; rejects missing, changed, skipped or mixed-revision evidence. It does not authorize execution or establish production readiness. |
| Deployment review packet | [deployment review packet](docs/deployment-review-packet.md) | merged | Checks named responsibility coverage, declared environment/configuration scope, retained file digests and freshness. The template is incomplete by design; a complete packet prepares human review, grants no authority and establishes no production readiness. |
| Tools | `tools/` (26 files) | merged | Verifiers, qualification and mutation scripts. [Tools](docs/profiles-and-tools.md#hub-tools). |
| Contracts and schemas | `contracts/qualification-surfaces-v1.json`, `schemas/collateral-evidence-snapshot-v1.schema.json` | merged | Checked by `tools/check_contract_surfaces.py` and the collateral snapshot test. |
| Scenario matrices, examples, risks | `scenarios/`, `examples/`, [`residual-risks.json`](residual-risks.json) | merged | Retained evidence is kept byte for byte; examples carry their own scope notes. |

Status labels are defined on the [stack map](docs/stack-map.md#status-labels): **merged**, **selected**, **known limit**, **proposed**.

<a id="getting-started"></a>
<a id="qualification-evidence"></a>
<a id="cross-component-qualification"></a>

## Reproduce the qualification

This is a separate audience from the five-minute path: it reproduces the reference run for review and needs the qualification repository, GitHub and Node 20.

Use a disposable Linux checkout, Git, an activated Python environment and the Node/npm prerequisites in the [developer quickstart](docs/quickstart.md). Reference CI uses Python 3.11 and Node 20. Dependency setup requires GitHub and package-registry access; no production credentials, Docker or OpenShell installation is needed for the standard mocked-adapter run.

```bash
git clone https://github.com/cogno-us/cognous-open-control-stack.git
cd cognous-open-control-stack
python3.11 -m venv .venv
source .venv/bin/activate
```

The reference runner is not part of this repository. It is maintained in the qualification repository as `suites/cognous-open-control-stack/tools/reference_release.py` (see [CROSS_COMPONENT_TESTS.md](CROSS_COMPONENT_TESTS.md) for the current location and source identity rules); it runs against a hub checkout with that suite's files in place, as the qualification workflows assemble it. The runner checks out the exact lock, installs dependencies into the active environment and runs two isolated repetitions. It refuses a nonempty results directory and, by default, replaces `.reference-work/`; keep personal changes out of runner-owned paths and use a new results path when preserving an earlier run. See the quickstart for exact-baseline reproduction and checkout-reuse rules.

Start review with `results/reference/scenario-results.json`, then inspect the resolved scenario matrix, repeatability, skip accounting and artifact index. A required missing, skipped, failed or unexecuted scenario blocks the release gate. A passing characterization of a known limitation does not mean the limitation was prevented.

Test results, environment-specific observations and historical campaign commentary are maintained in the [central test hub](https://github.com/cogno-us/cognous-stack-qualification/blob/main/results/readme-commentary/index.md). The [component lock](component-lock.json) defines source selection. Review the [persistence contract](https://github.com/cogno-us/cognous-control-plane/blob/main/docs/record-store-persistence.md), [recovery semantics](docs/recovery-semantics.md) and [protected-worker profile](docs/protected-qualification.md) for implementation boundaries; none grants deployment approval.

Executable integration suites and harnesses moved to the [qualification repository](https://github.com/cogno-us/cognous-stack-qualification/tree/main/suites/cognous-open-control-stack). See [the path migration map](CROSS_COMPONENT_TESTS.md) for current commands, source identity rules and the pinned revision of record. Component-local tests remain in their owning repositories; historical qualification results retain their original scope.

<a id="documentation-and-collateral"></a>

## Documentation index

The [documentation index](docs/README.md) lists every page in this repository by role and by topic; historical pages are labelled historical rather than hidden. Reading paths by role are on [Start here](docs/start-here.md). Component documentation indexes are linked from the [stack map](docs/stack-map.md#documentation-index-of-each-repository).

- [Developer quickstart](docs/quickstart.md) and [governance reviewer quickstart](docs/governance-quickstart.md).
- [Architecture](docs/architecture.md), [compatibility](docs/compatibility.md) and [support status](docs/release-status.md).
- [Evidence index](docs/evidence-index.md), [recovery semantics](docs/recovery-semantics.md), [threat model](docs/security-and-threat-model.md) and [risk register](residual-risks.json).
- [Guarantees and limits](docs/guarantees-and-limits.md), [platform support](docs/platform-support.md) and [roadmap](docs/roadmap.md).
- [Business collateral](collateral/business-collateral.md) and [one-page overview](collateral/one-page-overview.md).

## Status, known limits and recovery

**Deployment configuration: TBD.** No actual runtime deployment configuration or environment has been identified in the reviewed repository evidence. Committed deployment examples are synthetic or unconfigured; deployed API exposure, authentication, admission limits, storage bounds and host permissions remain unverified. See [deployment responsibilities](docs/v1-deployment-responsibilities.md) and the [exposure evidence checker](docs/security-coverage-addendum.md#using-the-exposure-checker) before selecting an environment. Operational trust remains HOLD. [Issue #140](https://github.com/cogno-us/cognous-open-control-stack/issues/140) records the completed public URL verification and this explicit deployment deferral.

**Release closeout:** the selected component profile remains frozen. Subsequent optional
profiles and qualification tools have been added; their results do not update the
selected release evidence or authorize deployment. Current work addresses verified
defects and evidence gaps rather than opening another feature intake round.
See the [completion record and remaining launch gates](docs/releases/closeout-2026-10-13.md)
for accepted work, deferred optional profiles and the finite public-preview checklist.
Public-preview approval remains pending; operational trust #30 remains HOLD.
The [contract and candidate artifact checks](docs/workstreams/contract-artifact-verification.md)
verify scoped structural interfaces and unpublished hub source archives without
granting release or production authority.

### Recovery and remaining limitations

Unknown acknowledgement does not imply absence. Accepted `observed_absent` is point-in-time evidence, not retry permission: an original in-flight effect can still commit. Reconciliation concerns that original effect and preserves acknowledgement history. A newly denied recovery request does not erase a historical applied effect. Retained originals and recovery derivatives keep separate identities and lineage.

**Logical-intent prevention is present in the selected executor source but is not enabled by the bounded integration path.** Different valid proposals for equivalent business intent can still create multiple effects in the selected reference. Effect-ID deduplication is not business-intent deduplication.

Live OpenShell execution/confinement, production institutional authentication, credential custody, deployment-wide bypass resistance, distributed budgets, remote finality and independent real-world verification remain unqualified. No rollback or exactly-once delivery guarantee is made. Human-review efficiency, model-behavior improvements and enterprise outcomes have not been measured by the reference tests.

Recently merged changes and whether the component lock selects them, each with the limit that stays visible, are listed in [guarantees and limits, section 6a](docs/guarantees-and-limits.md#6a-merged-after-the-selected-revisions).

### Paired-request enforcement qualification

A dedicated paired-request qualification compares the **same frozen shared request fields** under an isolated permissive synthetic baseline and the accepted Cognous Control Plane/executor path. The deterministic required batch uses constructed unsafe requests; it does **not** claim observed model compromise, prompt-injection resistance or population attack rates. The pairing gate compares the action, target, payload, actor, principal, amount, unit and requested permissions actually supplied to each condition. Institution/domain are trusted resolver context on the accepted path and are excluded from the paired caller fields; operation identity is a scenario label. Selection, authorization, dispatch, tool outcome, direct destination observation and recovery are recorded separately, and invalid/skipped cases remain visible in scheduled denominators.

The experiment is intentionally narrower than an end-to-end agent benchmark. Disclosure coverage is unavailable in the accepted refund adapter, and task completion is not measured. Same-business-intent behavior is reported exactly as selected today; the refund-intent execution profile is not enabled by the selected path. See the [matrix](scenarios/paired-request-enforcement-matrix.v2.json) and [checkpoint](docs/workstreams/paired-request-enforcement-checkpoint.md).

In this repository, **paired replay** means the experimental comparison of an identical frozen request across enforcement conditions. It is not Cognous Replay Bundle reconstruction.

### Merged profiles and engineering roadmap

The optional same-host authority/effect profile has merged through [Control Plane PR #12](https://github.com/cogno-us/cognous-control-plane/pull/12), [Execution Runtime PR #25](https://github.com/cogno-us/cognous-execution-runtime/pull/25) and [hub PR #16](https://github.com/cogno-us/cognous-open-control-stack/pull/16). It orders cooperating authority mutations, claim and budget consumption, and the protected synthetic effect through the declared trusted handoff and authoritative SQLite transaction.

The lock selects source containing this profile, but the bounded workflow **does not enable it**. Its qualification does not establish external-destination atomicity, distributed authorization or production readiness. Refund-intent ownership and authority/effect profiles remain mutually exclusive per database; no combined guarantee is implied. The [current checkpoint](docs/workstreams/worker21-authority-effect-checkpoint.md#acceptance-update-7-october-2026) distinguishes tested source revisions from subsequent merge revisions.

The [consolidated engineering register](docs/engineering-register.md) reconciles the research addenda with current evidence. Information-flow/context, governed memory, continued-authority trajectories and developmental-autonomy proposals are tracked as scoped future work, not automatically adopted requirements.

## Contributing, licence and attribution

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md). Keep changes bounded, preserve historical evidence and qualify new behavior before extending support claims. Runtime implementations remain in their owning repositories. Security reporting: [SECURITY.md](SECURITY.md).

Developed by [Cognous](https://cogno.us). See [LICENSE](LICENSE), [NOTICE](NOTICE) and [licensing inventory](LICENSING.md). Private and unrelated Cognous work is outside this public integration.

---

## Bibliography

Selected external sources from the October 2026 research review. These inform evaluation questions; they do not establish Cognous implementation, adoption, conformance or production qualification.

- [OECD. *Agentic AI in organisations: Early insights from practitioner interviews*. OECD Artificial Intelligence Papers, No. 65 (2026)](https://doi.org/10.1787/1257a26f-en). Qualitative practitioner research on bounded autonomy, oversight and organizational deployment.
- [OWASP GenAI Security Project. *State of Agentic AI Security and Governance*, version 2.01 (June 2026)](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/). Security synthesis covering agent identity, delegated permissions, tool access and containment.
- Jonathan Chadbourne / JCEE Labs. *When a Timeout Is Not a Failure: Authority, Evidence, and Recovery in Consequential AI Execution*. Technical Note 001, public release v0.1.1 (6 October 2026). Technical note on uncertain outcomes and recovery. An original public URL has not been verified; no substitute or private copy is linked.
- [Alexander Barrett. *Boundary Blindness Under Artificial Intelligence: Early Cross-Industry Findings on the Missing Decision-Evidence Layer* (2026)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7210798). Working paper on carrying the basis for reliance across organizational boundaries; proposed architecture, not a validated interoperability guarantee.
- [John W. Creswell and J. David Creswell. *Research Design: Qualitative, Quantitative, and Mixed Methods Approaches*, fifth edition. SAGE (2018)](https://edge.sagepub.com/creswellrd5e). Research-methods reference for explicit questions, comparison designs and interpretation limits.

- [Nachiket Sathaye. *AI Security Wiki*](https://nachi065.github.io/AI-Security-Wiki/). Vendor-neutral practitioner reference spanning AI security governance, controls, threat modeling, testing and assurance. It is an external knowledge resource, not a Cognous authority source, runtime dependency or qualification artifact. The live project currently publishes its content under CC BY-SA 4.0.

- [XERJ](https://github.com/xerj-org/xerj). Open-source reference-coding and corpus-search tooling for retrieving exact code/documentation passages for coding agents. It may be useful when inspecting public reference implementations, but it is not required by the Cognous runtime and retrieval output does not establish correctness, authority or qualification.

- [Tural Hagverdiyev. *Compromise Is Not Consequence: Evaluating Task-Scoped Authorization in LLM Agents with Paired Replay*. arXiv:2610.05840v1 (5 October 2026)](https://arxiv.org/abs/2610.05840v1). External research on fixed-request enforcement comparisons; its reported results are not Cognous qualification evidence.

See the [research bibliography](docs/research-bibliography.md) for review scope and source-verification limits.

<!-- Retained anchors for existing documentation links. -->
<a id="tested-guarantees-and-their-boundaries"></a>
<a id="protected-worker-qualification"></a>
<a id="merged-consumer-chain-candidate"></a>
<a id="merged-generation-adoption"></a>
