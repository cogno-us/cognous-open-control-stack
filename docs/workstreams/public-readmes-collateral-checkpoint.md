# Public README and collateral alignment

## Scope and provenance

Starting accepted hub: `5737267d94d2b445735c95e8480a31de73a2abe8`.
Branch in each repository: `worker18/public-readmes-collateral`.
Scope is the public root README and two component-specific collateral files in
the hub and all 13 repositories selected in its lock. Nested reference READMEs,
protocol instructions, runtime, dependency pins, workflows, tests, risk-register
JSON and qualification evidence are unchanged. Current hub navigation and support
explanations are updated. No private SharePoint text, uploaded DOCX content or
proprietary ISS mechanism is used. No self-merge or deployment.

The Index README supplied the overview/features/getting-started/evidence/navigation
style reference. Its aspirational claims were not copied as implemented guarantees.
Each component receives a tailored business overview and one-page overview; the
root README ends with stack component cross-links. Constitutional text and source
hierarchy, TFA's three rules, and separate Discovery/AoA responsibilities remain intact.

GitHub PRs are repository-scoped, so the hub PR coordinates companion documentation
PRs rather than pretending that one PR can change several repositories.

## Accepted evidence and corrected claims

- The lock now selects the accepted persistence generation: Control Plane
  `248d899…`, Replay `043830b…`, ODES `0486b64…`, Evidence Pack `de6b9e0…`,
  GAX `9984d90…`; executor remains `177354e…`.
- [Persistence qualification](../../examples/control-plane-store-adoption/qualification-summary.json)
  supports the selected bounded reference, with 915 tests per repetition and 35
  matrix gates. Equivalent-intent duplication remains characterized, not prevented.
- [Protected campaign](../../examples/protected-qualification/ci-37621009389/campaign/summary.json)
  and [provenance](../../examples/protected-qualification/ci-37621009389/provenance.json)
  support twelve isolated cases and 17 verifier tests on Ubuntu 22.04.5, Linux
  6.8.0-1064-azure, bubblewrap 0.6.1, Python 3.11.16. This is a fixed worker fixture,
  not OpenShell, arbitrary-agent confinement, model injection resistance or real
  credential isolation. Earlier failed local/Ubuntu 24.04 evidence is untouched.
- Moltbot's current producer profile is 2.0.0; its own CI pin remains distinct
  from the hub's selected Control Plane generation. Replay and Evidence Pack
  current versus historical compatibility are explicit; current Evidence Pack
  transformation is 0.3.1, not the old legacy-only README baseline.
- BitRep v1 means Ed25519 issuer-signature assurance under configured trust, not
  RSA prototype identity, ZK, platform verification or authority. Index local-chain
  registration/lifecycle is separate from legacy scoring ambitions and truth.
- ODES points to its current organization and retains discussion-draft status.
  Optional reasoning protocols provide instructions and static artifacts, not
  measured behavioral efficacy or execution permission.
- Executor PR #14 was rechecked before publication: open draft, unmerged at
  `70b9f7d73e48eb98289678b3e2ae6da35fc793df`. Logical-intent prevention is pending
  acceptance and not hub-supported. Its finalization check is recorded in the PR.

## Documentation and available checks

Link audit resolves local file/heading targets and GitHub blob targets against
actual local objects at named accepted SHAs; external non-repository HTTP status
and GitHub rendered visual QA are not claimed. Fenced shell blocks pass `bash -n`.
`git diff --check` passes. Exact final counts are recorded in the PR handoff.

Executed in an isolated Python 3.12 environment:

| Check | Observed result |
|---|---|
| Manifest package tests and `aam check-examples` | 111 passed; five examples valid |
| Control Plane package tests | 145 passed |
| Replay tests in locally installed environment | 154 passed, 77 skipped; full pinned producer coverage not executed |
| Evidence Pack tests in locally installed environment | 120 passed, 74 skipped, 42 missing-producer-configuration errors, one retained legacy-contract mismatch failure; not a passing suite |
| Evidence Pack `check-examples` | Four valid example packs; existing warnings retained |
| ODES tests without pinned fixture inputs | 2 passed, 112 skipped; not an integration pass |
| Research Intelligence proposal checks | Five fixtures validated; 13 unit tests passed |
| Constitutional structure validator and tests | Validator passed; 424 tests ran successfully with one skipped |
| TFA case validator | 19 cases validated; no model execution |
| Hub runner, Control Plane, Replay and ODES CLI help; example validations | Executed; sample run/bundle/pack validation passed with existing warnings |

Initial CLI test attempts lacked the activated environment on PATH and failed to
find the installed entrypoints; reruns above used activation. Evidence Pack
`--help` is not a supported command and is not advertised by its new quickstart.
The Evidence Pack suite requires separately configured historical/current producer
environments; they were not recreated for this prose-only batch. No test assertion,
skip rule or fixture was changed. Install-generated tracked metadata/bytecode was
restored before publication, leaving documentation-only changes.

No new full-stack or protected isolation run is claimed. New prose references
accepted source-attributed evidence without relabeling it as this worker's test run.
Repository mains were rechecked before publication and matched the inspected
starting commits. Final PR heads and one-time CI observations belong in the PR
handoff, since a document cannot embed its own final commit SHA.

## Repository review index

Companion PR links are recorded below after publication. Their changes remain proposals
until independently reviewed and merged. This hub PR does not assert their adoption.

| Repository | Inspected main |
|---|---|
| [cognous-open-control-stack](https://github.com/cogno-us/cognous-open-control-stack) | `5737267d94d2b445735c95e8480a31de73a2abe8` |
| [cognous-agent-action-manifest](https://github.com/cogno-us/cognous-agent-action-manifest) | `b24ac11d5d63bccc7281cf22ba0f0b31a0510f27` |
| [cognous-agent-control-plane](https://github.com/cogno-us/cognous-agent-control-plane) | `248d899634d9db3518e831bc7ab568a48733f825` |
| [constitutional-governance-for-institutions](https://github.com/cogno-us/constitutional-governance-for-institutions) | `6ed0b34b6ef6a5732457b556c74cddbeb94922a1` |
| [alvorada](https://github.com/cogno-us/alvorada) | `9984d9011568ccdf3d562fa9760ad41368947b34` |
| [moltbot-safe](https://github.com/cogno-us/moltbot-safe) | `31cd5dc5bc5cc4bf8d3c62e69737ec7a74e1f28d` |
| [cognous-agent-replay-bundle](https://github.com/cogno-us/cognous-agent-replay-bundle) | `043830b56595cecddfa65c064afd1c0b95e64792` |
| [cognous-agent-governance-evidence-pack](https://github.com/cogno-us/cognous-agent-governance-evidence-pack) | `de6b9e071df49fc3e0c1254d39b5c94cced554f0` |
| [open-decision-evidence-standard](https://github.com/cogno-us/open-decision-evidence-standard) | `0486b645e99c46d9cd16ca34b1ba7c653a6b3024` |
| [bitrep](https://github.com/cogno-us/bitrep) | `b820e6cf5a4be4c0cede5a6e80b20b6ef4aaf1e7` |
| [the-index](https://github.com/cogno-us/the-index) | `bbde8a598c7502ca08a7126c093e1cdfaa28bca1` |
| [portable-reasoning-protocol](https://github.com/cogno-us/portable-reasoning-protocol) | `44bbd1ee9d9feba1e73c3fa54862b690c571daa2` |
| [research-intelligence-protocol](https://github.com/cogno-us/research-intelligence-protocol) | `958eeebbcf5a3b591f8c3e733acad4b9642bb87a` |
| [truth-freedom-agency-protocol](https://github.com/cogno-us/truth-freedom-agency-protocol) | `4cb91ec3dccd3228ab48246b4efd2447a2dcf5b2` |

## Companion documentation PRs

These PRs contain documentation only and remain separately reviewable; none is merged by this batch.

| Repository | Review | Final documentation head |
|---|---|---|
| cognous-agent-action-manifest | [PR #5](https://github.com/cogno-us/cognous-agent-action-manifest/pull/5) | `d1dda5bfba2fe8ff07641e50fc91aec0e624fec8` |
| cognous-agent-control-plane | [PR #9](https://github.com/cogno-us/cognous-agent-control-plane/pull/9) | `b537dc91b1bf5a40e41f4b8c06871248924725d1` |
| constitutional-governance-for-institutions | [PR #36](https://github.com/cogno-us/constitutional-governance-for-institutions/pull/36) | `7f1ebab18187fc93311702277c7435eaa125512a` |
| alvorada | [PR #9](https://github.com/cogno-us/alvorada/pull/9) | `8a63b48e7aac885b6b3a18abe51ad23b12e44616` |
| moltbot-safe | [PR #16](https://github.com/cogno-us/moltbot-safe/pull/16) | `c306176c22494ad427554c82b362a8d9ec08bd1f` |
| cognous-agent-replay-bundle | [PR #10](https://github.com/cogno-us/cognous-agent-replay-bundle/pull/10) | `1f7ca8ed6919908644f388d6b7e117d13b1a3c87` |
| cognous-agent-governance-evidence-pack | [PR #11](https://github.com/cogno-us/cognous-agent-governance-evidence-pack/pull/11) | `f489ee956e84ecf00a77438a2433043176454abb` |
| open-decision-evidence-standard | [PR #27](https://github.com/cogno-us/open-decision-evidence-standard/pull/27) | `2d38f0cd513d9e11dc6d0e6afc4ff03e66fe6753` |
| bitrep | [PR #4](https://github.com/cogno-us/bitrep/pull/4) | `32920741011a30a56992c05e8bb04d1531569d23` |
| the-index | [PR #12](https://github.com/cogno-us/the-index/pull/12) | `91f094364670130abf30b1fbbd28b995770b2a76` |
| portable-reasoning-protocol | [PR #2](https://github.com/cogno-us/portable-reasoning-protocol/pull/2) | `72c7adb577b41f42118b0620869ab26bf724a32f` |
| research-intelligence-protocol | [PR #2](https://github.com/cogno-us/research-intelligence-protocol/pull/2) | `2d22f291e10639ab1a9af524eaf89283bd847b5f` |
| truth-freedom-agency-protocol | [PR #2](https://github.com/cogno-us/truth-freedom-agency-protocol/pull/2) | `87c09ca1fdb3a4ca93c423d6caee746fdae6acb5` |

## One-time companion CI observation

Checked each published documentation head once. Workflow status is observed; raw test totals were not re-audited here. Absence of runs is not a pass. No polling.

| Repository | Observed workflows |
|---|---|
| cognous-agent-action-manifest | [Tests](https://github.com/cogno-us/cognous-agent-action-manifest/actions/runs/37628867476): completed / success |
| cognous-agent-control-plane | [Tests](https://github.com/cogno-us/cognous-agent-control-plane/actions/runs/37628927036): completed / success |
| constitutional-governance-for-institutions | No workflow runs returned |
| alvorada | [Tests](https://github.com/cogno-us/alvorada/actions/runs/37629057279): completed / success |
| moltbot-safe | [CI](https://github.com/cogno-us/moltbot-safe/actions/runs/37629125530): queued / no conclusion; [Install Smoke](https://github.com/cogno-us/moltbot-safe/actions/runs/37629125493): in_progress / no conclusion; [Workflow Sanity](https://github.com/cogno-us/moltbot-safe/actions/runs/37629125588): completed / success |
| cognous-agent-replay-bundle | [Tests](https://github.com/cogno-us/cognous-agent-replay-bundle/actions/runs/37629190745): completed / success |
| cognous-agent-governance-evidence-pack | [Tests](https://github.com/cogno-us/cognous-agent-governance-evidence-pack/actions/runs/37629261311): completed / success |
| open-decision-evidence-standard | [Tests](https://github.com/cogno-us/open-decision-evidence-standard/actions/runs/37629328913): completed / success |
| bitrep | No workflow runs returned |
| the-index | No workflow runs returned |
| portable-reasoning-protocol | No workflow runs returned |
| research-intelligence-protocol | [proposal-validation](https://github.com/cogno-us/research-intelligence-protocol/actions/runs/37629588595): completed / success |
| truth-freedom-agency-protocol | [Validate TFA evaluation files](https://github.com/cogno-us/truth-freedom-agency-protocol/actions/runs/37629659487): completed / success |

Evidence Pack's configured CI passed at its published head; the earlier local missing-fixture/mixed-generation result remains recorded separately and is not relabeled as a local pass.
