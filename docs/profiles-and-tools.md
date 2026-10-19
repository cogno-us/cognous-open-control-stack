# Profiles and tools

A catalogue of the commands, profiles and tools that the repositories of the Open Control Stack provide. Names and groups are as on the [stack map](stack-map.md); package and command names are explained in [naming](naming.md).

How to read this page:

- **At the lock** means the revision pinned in the [component lock](../component-lock.json). **After the lock** means present on the default branch of the owning repository but not in the pinned revision. After-the-lock items are labelled merged, not selected. The lock decides what is selected; a newer default branch does not change it.
- The command lists below were read from each repository's command-line source at the locked revision and at the default branch when this page was written. Pinned revisions change at the pin round; recheck the "At the lock" columns then (see [Refreshing this page](#refreshing-this-page)).
- Status labels are defined on the [stack map](stack-map.md#status-labels): merged, selected, known limit, proposed.
- No command here grants authority. A passing check means what its owning page says it means, no more; see [guarantees and limits](guarantees-and-limits.md).
- Where a purpose is not documented in existing text, the row says "documentation pending" instead of inventing one.

## Component command-line tools

### Action Manifest: `aam`

Install: `pip install -e ".[dev]"` from a checkout of `cognous-action-manifest`. The CLI has no help flag; running it without a command prints usage.

| Command | Purpose | At the lock | After the lock |
|---|---|---|---|
| `aam validate <manifest.json>` | Validate a manifest and report errors and warnings. | yes | yes |
| `aam summarize <manifest.json>` | Summarize the declared actions and their requirements. | yes | yes |
| `aam list-actions <manifest.json>` | Table of actions with posture, authority and review columns. | yes | yes |
| `aam check-examples` | Validate every `examples/*.manifest.json` file. | yes | yes |

Examples at the lock: five `*.manifest.json` files (customer service, finance workflow, internal research, procurement, refund integration v1.1). After the lock, `examples/runtime_action_proposal_v1_2.json` is also present. Schemas are in the repository `schemas/` directory.

### Control Plane: `acp`

Install: `pip install -e .` from a checkout of `cognous-control-plane`.

| Command | Purpose | At the lock | After the lock |
|---|---|---|---|
| `acp validate-run <path>` | Validate a run record. | yes | yes |
| `acp validate-replay <path>` | Validate a replay bundle. | yes | yes |
| `acp redact-run <path> --out <file>` | Write a redacted copy of a run record (redaction flags per `--help`). | yes | yes |
| `acp redact-replay <path> --out <file>` | Write a redacted copy of a replay bundle. | yes | yes |
| `acp sign-replay <path> --secret <key> --out <file>` | Sign a replay bundle. | yes | yes |
| `acp verify-signed-replay <path> --secret <key>` | Verify a signed replay bundle. | yes | yes |
| `acp run --manifest F --proposal F --authority-context F --resolver-state F --store-dir DIR --out-dir DIR [--now ISO8601] [--format text\|json]` | Execute one declared bounded operation against a local throwaway store. Both directories must be new or empty. The shipped example fixtures are time-sensitive: pass `--now` with a timezone-aware time to evaluate at a declared time; it is recorded as `time_source=test_override`. | no | yes |
| `acp witness digest <path>` | Print the head digest chain of a record store document. | no | yes |
| `acp witness publish <path> --witness <file>` | Verify the record set against a local witness file, then append its head digest (local file witness only). | no | yes |
| `acp witness verify <path> --witness <file>` | Reject a record set whose covered rows were dropped or rewritten. | no | yes |

That is eight top-level commands after the lock (six at the lock, plus `run` and `witness`; `witness` has three subcommands). Repository tools: `tools/verify_decision_input_commitment.py` and `tools/adversarial_mutations.py`; conformance vectors in `conformance/decision-input-commitment-vectors.json`. Examples are under `examples/` (including `acp_run/`).

### Execution Runtime

Command line: `python cli/moltbot_safe_cli.py <command>` from a checkout (no installed script).

| Command | Purpose |
|---|---|
| `validate-permissions` | Validate `permissions.json`. |
| `run-action [--file F]` | Run an action from a JSON file or standard input. |
| `print-audit-log [-n N]` | Print recent entries of `engine/audit.log`. |

Execution modules under `engine/` include the safe executor, the atomic local control-plane executor, the local authority/effect and recovery modules, the refund-intent module and the OpenShell adapter modules. The accepted interfaces at the lock are Execution Envelope 0.2.0, executor producer profile 2.0.0 and OpenShell adapter 0.1.0. Known limit: live OpenShell execution and confinement are not qualified; see [guarantees and limits](guarantees-and-limits.md).

### Replay Bundle: `arb`

Install: `pip install -e .` from a checkout of `cognous-replay-bundle`.

| Command | Purpose | At the lock | After the lock |
|---|---|---|---|
| `arb validate <path>` | Validate a replay bundle. | yes | yes |
| `arb summarize <path>` | Print a summary of a replay bundle. | yes | yes |
| `arb redact <path> --out <file> [--targets] [--final-output] [--reasons] [--replacement S] [--policy NAME]` | Redact selected fields. | yes | yes |
| `arb redact ... [--task] [--scope] [--drop-signature]` | Additional redaction options. | no | yes |
| `arb sign <path> --secret <key> --out <file> [--key-id ID]` | Sign a replay bundle. | yes | yes |
| `arb verify <path> --secret <key>` | Verify a signed bundle. | yes | yes |
| `arb verify ... --require-bound-envelope` | Refuse a signature that covers the inner bundle only. | no | yes |
| `arb check-examples` | Validate all example bundles. | yes | yes |

Examples include `bounded_success_reconstruction_v0_2.json` and `bounded_lost_ack_reconstruction_v0_2.json` (Reconstruction Bundle 0.2.0) and a `producer-v2/` directory.

### Governance Evidence Pack: `agep`

Install: `pip install -e .` from a checkout of `cognous-governance-evidence-pack`. The CLI has no help flag; running it with no arguments prints usage and exits 2.

| Command | Purpose |
|---|---|
| `agep validate <evidence_pack.json>` | Validate an Evidence Pack. |
| `agep summarize <evidence_pack.json>` | Print pack counts and, for traceable imports, derived counts. |
| `agep render <evidence_pack.json> [--out F.md] [--traceable]` | Render Markdown for review. |
| `agep import --manifest F --reconstruction F --out F [--render F.md]` | Build a traceable Evidence Pack from a Manifest and a reconstruction bundle. |
| `agep check-examples` | Validate every example pack and re-render the Markdown. |

These five commands are the same at the lock and after it. Templates are in `templates/`; schemas in `schemas/`; examples in `examples/` (including `import_inputs/`, `producer-v2/` and `rendered/`).

### ODES: `odes`

Install: `pip install -e .` from a checkout of `open-decision-evidence-standard`.

| Command | Purpose | At the lock | After the lock |
|---|---|---|---|
| `odes export-cognous --manifest F --reconstruction F --out F [--relying-party S] [--purpose S] [--expires-at T]` | Export a Cognous-stack decision-evidence package. | yes | yes |
| `odes validate-record <record>` | Validate a record against the `pder-v0.1` schema. | yes | yes |
| `odes recipient-validate <package> --policy F [--out F]` | Evaluate a package against a recipient policy. | yes | yes |

Profiles (documents under `profiles/`): minimal, agentic-ai, regulated-enterprise, cognous-stack-export 0.1, cognous-stack-export 0.2 and, after the lock, generic-recipient 0.1 and cognous-stack-export 0.2 restrictions. RFCs 0001 to 0004 are under `rfcs/`. After the lock the repository also carries `contracts/` (draft contract directories, each with a README, schema, validator and fixtures, listed in the repository) and `conformance/` vectors. Treat the contract directories as draft (`0.1.0-draft` where labelled); the repository's own documentation states their status.

### Evidence Attestation, Evidence Registry, Governed Exchange

These repositories do not install a command-line script.

| Repository | Entry points | Notes |
|---|---|---|
| Evidence Attestation | `main.py` (application), `api/`, `utils/`; run tests with `pytest` after installing `requirements-dev.txt`. | Selected interface: verification contract v1. |
| Evidence Registry | `app/main.py` (application), `chain/` (local blockchain reference, Node tooling and Python), `protocol/`, `schema/`, `examples/`. | Selected interface: local blockchain reference 0.1.0. Chain reproduction runs through the repository's Actions workflow. |
| Governed Exchange | Packages under `experiments/` (`governed_message_transport`, `odex_gax_imx_reference`); `pip install -e ".[dev]"` then `pytest`. | Experimental; selected artifacts are GAX retained artifacts 1.1.0 and the `security-runtime-p2-20261018` opt-in compatibility. |

### Institutional Governance

No installed command. `tools/validate_bootstrap.py` validates the constitutional research bootstrap invariants. Documents are organized under `constitution/`, `constitutional-design/`, `governance-engineering/`, `history/`, `process/`, `research/`, `testing/` and `applications/`; see the repository's own docs index.

## Tooling and qualification repositories

### Ergonomics: `cognous-ocs`

Install: `pip install ".[stack]"` from a checkout (the `stack` extra installs the four component command-line tools through pinned git references; it needs GitHub access). Contract label `0.1.0-draft`.

| Command | Purpose | Writes |
|---|---|---|
| `cognous-ocs --version` | Print CLI, distribution, contract and bundled-component versions. | nothing |
| `cognous-ocs demo customer-service --out DIR [--clean] [--strict]` | Run the bundled offline example; exit 0 only if the blocked email send is evidenced. | `DIR` |
| `cognous-ocs validate PATH --kind KIND` | Check one artifact; kinds: `manifest`, `run-record`, `replay-bundle`, `evidence-pack`. | nothing |
| `cognous-ocs init workflow --out DIR` | Scaffold a manifest, a policy file and a sample run record. | `DIR` |
| `cognous-ocs doctor [--workflow DIR]` | Read-only setup diagnosis. | nothing |
| `cognous-ocs evidence render PATH --out FILE` | One self-contained HTML view of an evidence pack. | `FILE` |
| `cognous-ocs dashboard --out FILE INPUT...` | Read-only static HTML reading of reports, packs and run records; adds no verdict. | `FILE` |
| `cognous-ocs schema export --out DIR` | Export bundled schema snapshots. | `DIR` |
| `cognous-ocs ci` | Entry used by the composite GitHub Action. | declared outputs |
| `cognous-ocs manifest ...`, `cognous-ocs replay ...`, `cognous-ocs evidence ...` | Passthrough to `aam`, `arb` and `agep`. | as the component does |

Global options: `--format text|json`, `--strict`, `--out`, `--no-color`. Exit codes: 0 success, 1 gate or policy failure, 2 invalid input, 3 not applicable, 4 internal error. Its pinned component revisions are recorded in its own source and documentation; its control-plane pin is ahead of the hub lock. See its `docs/cli-contract.md`.

### Verifier: `cognous-verify`

`cognous-verify RUN_RECORD [--proposal F] [--manifest F] [--ledger F] [--witness F] [--holder-inventory F]` plus `--out FILE`, `--json`, `--controller-revision`, `--source-revision`, `--generated-at`, `--version`. Exit codes: 0 accept, 1 refuted, 2 usage or input error, 3 abstain, 4 crash. A report is a verification report, never an attestation. Tiers are described in its `docs/tiers.md`. Additional scripts: `scripts/check_claim_boundaries.py` and capture tools under `tools/`. Status: pre-release and on hold.

### Orchestrator

No installed command. Profiles: `profiles/bounded-v1-reference.yaml` and `profiles/integrated-preview.yaml` (a profile, not a deployment approval). Documents: `ARCHITECTURE.md`, `CONTRACTS.md`, `docs/component-matrix.md`, `docs/trust-boundaries.md`, `docs/qualification-ledger.md` and the `development/` cockpit. Operational deployment assurance is not established (issue #30, HOLD).

### Qualification

No installed command. Tools are run as scripts from `tools/`; suites are under `suites/`.

| Tool | Purpose |
|---|---|
| `build_dashboard.py` | Validate coverage and run commitments and build Markdown plus a static page (the dashboard page is generated; do not edit by hand). |
| `capture_workflow_run.py` | Capture allowlisted public GitHub run metadata as an append-only manifest. |
| `check_public_links.py` | Anonymous bounded public-navigation checks; unavailable is never a pass. |
| `*_agent_pilot.py`, `restore_*_pilot.py`, `prp_*_evaluation.py` | Bounded actual-agent pilots and experiments with synthetic native tools; they call external model APIs and need credentials supplied by the operator. |
| `contract_matrix.py` | Print or check the contract-version compatibility matrix for component checkouts. |
| `export_exchange.py`, `verify_exchange.py` | Package serial trial evidence for review; read-only standard-library verification of an exchange evidence package. |
| `failure_register.py` | Validate the V1 failure register and back-fill closure-evidence labels. |
| `final_source_preflight.py` | Inspect merged-source admission without changing compatibility mappings. |
| `install_suite.py`, `run_suite.py` | Assemble relocated test files into a disposable checkout; run an explicit command in a disposable checkout and retain telemetry. |
| `omit_locks.py`, `pristine_checkout.py`, `safe_paths.py` | Evidence hygiene helpers. |
| `qualification_results.py`, `scenario_report.py`, `trajectory_contract.py` | Execution telemetry, read-only per-scenario reporting and a versioned bounded evidence evaluator. |
| `run_matched_refund.py`, `verify_matched_refund.py` | Matched synthetic refund stimulus; stand-alone verification of its evidence. |
| `run_runtime_authority.py`, `run_security_runtime.py`, `summarize_security_runtime.py` | Exact-source candidate runs and their re-verification. |
| `run_serial_qualification.py`, `serial_orchestration.py` | Serial local-variant runs and state validation. |
| `security_coverage.py` | Revision-bound file screening receipts, never a security clearance. |
| `sync_ai_security_wiki.py` | Import pinned third-party test specifications without executing upstream code. |
| `v1_validation.py` | Frozen-V1 validation controller helpers. |
| `validate_catalog.py`, `validate_migrations.py` | Validate scenario provenance and specifications; check relocation completeness and retained licence bytes. |

Suite directories under `suites/`: `cognous-evidence-registry`, `cognous-execution-runtime`, `cognous-governance-evidence-pack`, `cognous-governed-exchange`, `cognous-open-control-stack`, `cognous-replay-bundle`, `open-decision-evidence-standard`, `fix2-probes`, `operation-identity`, `outside-holder`, `runtime-authority`, `security-runtime`, `v1-probes`, `v1-scenarios`, `verifier-mutation` and `wiki-derived`. Scenario specifications are recorded with their run state; a specification is not evidence of a run.

## Hub: selection profiles

Files under `profiles/`. They are evidence of candidate and diagnostic selections. The selected set is the lock itself.

| File | What the file records | Label |
|---|---|---|
| `bounded-v1-reference-release-selection.json` | Scoped reference-only selection; publication state "governor final acceptance pending"; reference release and production deployment recorded as not authorized. | proposed |
| `full-release-candidate.json` | Full merged-chain candidate lock; qualification status "candidate". | merged |
| `merged-consumer-chain.json` | Profile `merged-consumer-chain-v1`; qualification status "candidate". | merged |
| `remediation-candidate-20261015.json` | Remediation candidate; merged-only inputs; release and production not authorized. | merged |
| `remediation-full-reference-20261015.json` | Non-selected full-reference diagnostic qualification; candidate. | merged |
| `security-remediation-source-probe-20261016.json` | Source probe profile; qualification status NOT_RUN; merged-only inputs. | merged |
| `security-runtime-candidate-20261016.json` | Security runtime candidate; merged-only inputs; release and production not authorized. | merged |
| `security-runtime-f5b-candidate-20261016.json` | Variant of the security runtime candidate; same authorization statements. | merged |
| `w7-bounded-v1-component-lock.candidate.json` | W7 scoped bounded V1 candidate lock; governor acceptance pending; not the selected core lock. | proposed |

## Hub: reference profile modules

Modules under `reference_profiles/`. They are opt-in synthetic references for a trusted host and grant no authority. The owning document is linked where one names the module; otherwise it says documentation pending.

| Module | Purpose (from the module's own description) | Owning document |
|---|---|---|
| `assurance_runtime.py` | Integrated optional assurance reference with one local SQLite effect boundary. | documentation pending |
| `bounded_json.py` | Bounded detached JSON inputs for synthetic reference verifiers. | documentation pending |
| `context_evidence.py` | Non-authorizing context lineage export; no raw content or external custody claim. | [context, notification and recovery](context-notification-recovery.md) |
| `context_journal.py` | Context journal coverage against caller-held commitments, never authority. | documentation pending |
| `context_memory.py` | Trusted-host memory admission and delivery; no execution authority. | [V1 reference profiles](v1-reference-profiles.md) |
| `federated_governance.py` | Opt-in trusted-host governance extension; synthetic SQLite effects only. | documentation pending |
| `institutional_review.py` | Trusted-host institutional review records; never issues or changes a runtime grant. | [V1 reference profiles](v1-reference-profiles.md) |
| `operational_state.py` | Optional structured-state gates; trusted host; synthetic SQLite effects only. | [V1 reference profiles](v1-reference-profiles.md) |
| `payload_disclosure.py` | Exact-payload disclosure checks for one trusted configured local sink. | documentation pending |
| `protected_destination.py` | Synthetic destination outside a declared authority restore set. | [V1 reference profiles](v1-reference-profiles.md) |
| `protocol_evaluation.py` | Preregistered paired-outcome scoring utilities; no model effectiveness claim. | [V1 reference profiles](v1-reference-profiles.md) |
| `provenance_groups.py` | Conservative grouping of declared dependencies; never an independence proof. | documentation pending |
| `resolver_assurance.py` | Synthetic observation assurance; no authority issuance or execution permission. | documentation pending |
| `resolver_revision_ledger.py` | Trusted-host rollback memory for synthetic resolver observations, not permission. | documentation pending |
| `sqlite_recovery.py` | Verified per-database snapshots and staging restore; never activates a deployment. | documentation pending |
| `trust_evidence.py` | Consumer-owned evidence acceptance; signatures establish attribution, not truth. | documentation pending |

The temporal-authority example named in [V1 reference profiles](v1-reference-profiles.md) lives in the qualification suite directory, not in this repository. Run instructions for the governed-context, institutional-review and temporal profiles are on that page.

## Hub: tools

Scripts under `tools/`. Each script's purpose is the first line of its own description. Arguments are documented in the script; run it from a checkout of the hub with Python 3.11 or 3.12.

| Tool | Purpose (from the tool's own description) | Owning document |
|---|---|---|
| `bounded_input.py` | Byte and syntax budgets for local artifact admission; never grants authority. | documentation pending |
| `check_contract_surfaces.py` | Compare published structural contracts with definitions used by validators. | documentation pending |
| `check_preview_entries.py` | Offline, non-authorizing preview entrypoint link and anchor smoke check. | [preview entry audit](preview-entry-audit.md) |
| `check_w0_fixture.py` | documentation pending | documentation pending |
| `collateral_evidence_snapshot.py` | Validate the detached collateral evidence snapshot. | documentation pending |
| `deployment_review.py` | Validate a local deployment review packet; never authorize deployment. | [deployment review packet](deployment-review-packet.md) |
| `destination_admission_qualification.py`, `destination_admission_mutations.py` | Exact-source qualification of the destination-admission controls and removed-control probes. | documentation pending |
| `federated_governance_qualification.py`, `federated_governance_mutations.py` | Exact-source qualification of the optional federated governance profile and removed-control probes. | documentation pending |
| `import_paired_requests.py` | Import recorded model-selected requests for later paired qualification. | documentation pending |
| `integrated_assurance_qualification.py`, `integrated_assurance_mutations.py` | Qualify the nine local assurance groups; isolated control-removal probes. | documentation pending |
| `lifecycle_inventory.py` | Reconcile a supplied inventory; never discovers or authorizes work. | documentation pending |
| `operational_state_qualification.py`, `operational_state_mutations.py` | Exact-source qualification of the structured-state gates and removed-control probes. | documentation pending |
| `research_assurance_mutations.py` | Control-removal probes in disposable copies. | documentation pending |
| `resolver_assurance_qualification.py` | Run the bounded synthetic observation suite and retain exact evidence. | documentation pending |
| `semantic_handoff_contract.py` | Opt-in structural reference checker; never an execution authority. | documentation pending |
| `sqlite_staging_recovery.py` | Snapshot or restore a trusted local SQLite store without authorizing activation. | [context, notification and recovery](context-notification-recovery.md) |
| `verify_candidate_archive.py` | Verify an unpublished hub source archive against a trusted exact Git revision. | [security remediation record](security-cloud-remediation-20261016.md) |
| `verify_embedding_exposure.py` | Bind embedding admission declarations to retained configuration evidence. | [security coverage addendum](security-coverage-addendum.md) |
| `verify_publication_inventory.py` | Fail-closed verifier for a frozen hub-only review package; never authorizes release. | documentation pending |
| `verify_selected_documentation.py` | Check current architecture links against the selected lock. | tested by `tests/test_selected_documentation.py` |
| `requirements-federated-governance.txt`, `requirements-release.lock` | Pinned requirement inputs for the profiles above. | documentation pending |

Optional execution profiles (atomic authority/effect, refund intent) and their Linux batches are documented in [optional execution profiles](optional-execution-profiles.md). The v1 extension evidence gate is in [V1 extension release gate](v1-extension-release-gate.md).

## Refreshing this page

The "At the lock" columns and the lock table on the [stack map](stack-map.md#selected-revisions) depend on `component-lock.json`. At the pin round, regenerate the lock table from the lock file, then re-read each repository's command-line source at the new pinned revision and update the yes/no cells. Rows marked "documentation pending" are open documentation items, not claims.
