# F6 exact-package checks against the F5b review freeze — 2026-10-16

Publication HOLD. Production HOLD / NOT ESTABLISHED. Rights/security acceptance pending. No release or production authorization is granted by this document.

Scope: exact-byte checks of the frozen F5b review packet against the merged hub head.
Target hub head: `0abd9e14` (post-merge re-check of PR #152, merged by PR #153).
Review freeze directory: `docs/releases/security-review-freeze-f5b-20261016/`.
Review ZIP: `cognous-source-review-f7fe1bc.zip`, SHA-256 `37d575d776dc32cd79ecf815edb328038a49f9c314d3aeb7b82bed406d3ee337`, 1,218,856 bytes, 175 members, built from source `f7fe1bc0` (the merged tree before PR #153's own sidecars were added).
Native qualification archive: `cogno-us/cognous-stack-qualification` `main` `af9f5843`, `results/security-runtime-f5b-20261016/native-archive-run.zip`, SHA-256 `a089f9b33edff6521ceb78885b866f9a87280dc4d5584b3be471b15d309f672d`, 4,890,962 bytes, 1,862 members, byte-identical to GH artifact `12056860537`.
Candidate profile: `profiles/security-runtime-f5b-candidate-20261016.json`, SHA-256 `f159158cd9f5504a6e1c0683cbd136532c1c6938300dd17aa45f700ad9278274`.
F3R run: `38925303886`, tested source `7022881e0958543a8b7685031c63132891b5f47c`, 36×2 pass.
Runtime quarantine: tag `upstream-moltbot-quarantine-20261016` at `fd6b76fa0e85feb5b67324114bf790d3a12fdaf1` on `cogno-us/cognous-execution-runtime`.

## Results summary

| Check | Verdict |
|---|---|
| 1. Exclusion verification | PASS |
| 2. Notice completeness | PASS |
| 3. Public claims audit | PASS |
| 4. Live link verification | PASS (with RESIDUAL for egress-policy denials) |
| 5. Deployment-TBD disclosure | PASS |
| 6. Prior-tracker reconciliation (#87, #140) | PASS |
| 7. F3R + native retention line | PASS |

Totals: **7 PASS**, **1 RESIDUAL (environmental, non-defect)**, **0 FAIL**.

## 1. Exclusion verification — PASS

- `docs/releases/security-review-freeze-f5b-20261016/manifest.json:excluded_files` enumerates **500** paths against `source_commit=f7fe1bc03cf67df2ab5afe81ba513580a29fde25`. The brief's "494 or current count" matches the pre-merge-base record (`verification.json:pre_merge_base.excluded_paths = 494`); the merged-head regeneration recorded in the post-merge re-check accounts for the +6 delta (`verification.json:post_merge_recheck`).
- Exclusion reasons collapse to four categories, matching the historical freeze's bounded hub-only allowlist:
  - 488 × "Outside bounded hub review allowlist; external source, installed dependencies, generated archives and audit metadata not redistributed";
  - 6 × "current freeze's own retention sidecars postdate their frozen source";
  - 5 × "prior freeze retention sidecars postdate their own frozen source";
  - 1 × "prior frozen review archive is a historical retention".
- No external component source, selected PRP/TFA source/PDF, dependency/toolchain bundle, workflow or generated evidence archive is included in the review ZIP; `manifest.json:external_components` records all 13 selected externals as `redistributed:false`.
- Reconciled against `docs/open-source-boundary.md` (hub documentation + formats + validators + reference behavior + examples + tests + business-facing docs — the included-scope lane). The historical freeze under `docs/releases/security-review-freeze-20261016/` listed 487 excluded paths at the smaller `c996a41` tree; the increase to 500 at the F5b freeze is accounted for in `verification.json:delta_from_c996a41_freeze` (10 added + 15 changed + 0 removed) and in the post-merge-base delta (+6 at the merged head).
- Owner's prior removal of Moltbot Safe/Reasoning Protocol component sources from the stack remains correct: the external components list and the historical notice folders stay as history; no new redistribution.
- Byte verification: on-disk ZIP SHA-256 and byte-length match the manifest/README/SHA256SUMS bindings exactly.

Evidence:
- `docs/releases/security-review-freeze-f5b-20261016/manifest.json` (lines 1–end; 500 excluded_files, 175 files, 13 external_components).
- `docs/releases/security-review-freeze-f5b-20261016/verification.json:L75` (`"excluded_paths": 500`), `:L240` (pre-merge-base `"excluded_paths": 494`).
- Local recomputation: `sha256(cognous-source-review-f7fe1bc.zip) = 37d575d7…`; size = 1,218,856.
- `docs/open-source-boundary.md:L1–29`.

## 2. Notice completeness — PASS

- `manifest.json:required_notices` lists **30** notice paths. All are present on disk and byte-identical to the files hashed in `manifest.json:files`:
  - hub `LICENSE` and `NOTICE` (2);
  - 28-entry external notice ledger under `docs/releases/selected-notices/<component>/…` covering: `action_manifest`, `bitrep`, `constitutional_authority`, `control_plane`, `gax_imx_transport`, `governance_evidence_pack`, `moltbot_safe` (10 files including Swabble, Apple device identifiers, engine, open-prose, skill-creator, a2ui and the Apache-2.0 variant), `odes`, `replay_bundle`, `research_intelligence`, `the_index`.
- The 11 external notice directories plus `README.md` under `docs/releases/selected-notices/` match the historical freeze's inventory. PRP and TFA remain `licensing_state:"unresolved"`, `redistributed:false`, with no notice folder — consistent with historical rights tracker #87 and the owner's exclusion.
- Historical "Moltbot Safe" notices are retained as historical selection evidence and not re-promoted; this is correct per the "no new mentions of Moltbot Safe / Reasoning Protocol beyond historical" constraint.

Evidence:
- `docs/releases/security-review-freeze-f5b-20261016/manifest.json:required_notices` (30 entries).
- `docs/releases/selected-notices/` directory listing (12 entries: 11 component folders + README).
- `verification.json:L219` (`"notices": "All 30 original notice files byte-identical to prior freeze; accountable rights acceptance pending"`).

## 3. Public claims audit — PASS

Scoped files reviewed: `README.md`, `docs/start-here.md`, `docs/release-status.md`, `docs/public-preview-qualification.md`, `docs/overview.md`, `docs/architecture.md`, `docs/open-source-boundary.md`, `docs/security-and-threat-model.md`, `docs/v1-deployment-responsibilities.md`, `docs/operational-trust-status.md`, `docs/security-reporting-and-triage.md`, `docs/releases/security-review-freeze-f5b-20261016/README.md`, `docs/releases/f3r-qualification-receipt-20261016.md`.

- No claim of release-ready, production-ready, independently security-cleared, independently IP-cleared or mailbox-triage-verified status.
  - `README.md:L27` labels status as "a merged, pinned **bounded synthetic reference**" and explicitly disclaims production, compliance and institutional adoption.
  - `docs/release-status.md:L13` keeps C2/C3 as "**No release claim**" and `:L48` keeps live confinement/custody/revocation/external settlement outside the release.
  - `docs/public-preview-qualification.md:L3` labels the page "qualification in progress, not a published release" and "not a component-selection decision, deployment authorization or production assurance statement".
  - `docs/security-and-threat-model.md:L3` disclaims production security certification.
  - `docs/operational-trust-status.md:L3` holds operational trust **HOLD / NOT ESTABLISHED**.
  - `docs/public-preview-qualification.md:L20` and `docs/security-reporting-and-triage.md:L39` state mailbox delivery/response remain unverified.
- Non-authorizing / "not an authority" wording is present in `docs/architecture.md:L17–28` ("Does not establish" column for every component).
- The runtime-quarantine disclosure is present where runtime is discussed in the freeze packet (`docs/releases/security-review-freeze-f5b-20261016/README.md:L22`) and the F3R receipt (`docs/releases/f3r-qualification-receipt-20261016.md:L19`). The hub-wide `docs/architecture.md` and `docs/security-and-threat-model.md` continue to describe the runtime by role; the F5b-specific quarantine is scoped to the F5b packet where it was introduced, which is correct for a nonselected candidate (the hub's full-reference profile and `component-lock.json` remain unchanged).

No defects found in public claims against the final frozen bytes.

## 4. Live link verification — PASS (with RESIDUAL for egress-policy denials)

Method: extracted every `http(s)://` URL from the scoped docs (38 unique). All GitHub refs were HEAD/GET-checked at the current head and, for action runs/PRs/issues, cross-checked via `gh api`.

- **27 GitHub links verified live (HTTP 200)**: component repos, PRs #148/#149/#150/#152/#153 (closed), #23/#63/#16, Control Plane #12, Execution Runtime #25, Stack Qualification #27, Issues #68 (open), #69/#140 (closed), raw blob/tree refs including the historical pinned tree `a1cbc7b…` and `39f03843…/suites/cognous-open-control-stack`.
- **Action runs verified via `gh api`** (not HEAD-reachable without auth; `gh api` is the brief's permitted path):
  - `cognous-open-control-stack` run `37682165860` — `success`, head `e926bbd7`;
  - `cognous-open-control-stack` run `37694032916` — `success`, head `7e43d55c`;
  - `cognous-stack-qualification` run `38925303886` — `success`, head `7022881e`.
- **Issue #30 referenced by docs** is the private operational-orchestrator issue; `docs/operational-trust-status.md:L10–11` already discloses that "A private repository's anonymous HTTP 404 is not evidence that its tracked work is complete or absent." The public GitHub Issue numbered #30 in this repo (`Enforce context expiry…`, closed) is a distinct, unrelated local issue; the public doc disambiguates by linking to the local `operational-trust-status.md` page, which is correct.
- **RESIDUAL (environment, non-defect)**: 7 non-GitHub links return 403 at the session's egress proxy (policy denial, not link rot): `https://arxiv.org/abs/2610.05840v1`, `https://cogno.us`, `https://doi.org/10.1787/1257a26f-en`, `https://edge.sagepub.com/creswellrd5e`, `https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/`, `https://nachi065.github.io/AI-Security-Wiki/`, `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7210798`, and `https://github.com/xerj-org/xerj`. These are external citations and bibliography entries; the proxy's "connect_rejected" response is not evidence the links are broken. They are flagged for out-of-band verification by the F7 reviewer, not as package defects.
- Historical freeze links (`docs/releases/security-review-freeze-20261016/README.md`) remain reachable via the local-path markdown link from `docs/release-status.md:L58`.

## 5. Deployment-TBD disclosure — PASS

- Operational trust orchestrator **HOLD / NOT ESTABLISHED** is stated in:
  - `docs/operational-trust-status.md:L3`;
  - `docs/start-here.md:L12` (operator path);
  - `docs/public-preview-qualification.md:L32`.
- Production configuration TBD, no release/tag/announcement/activation:
  - `docs/release-status.md:L48` (deployment limits);
  - `docs/public-preview-qualification.md:L34` ("No production authorization, component-lock update, release tag or merge follows from this document");
  - `docs/v1-deployment-responsibilities.md` entire table marks each role Deployment-dependent and `:L20` disclaims any production target or secret store.
- C0 race, optional same-host C1, no C2/C3 or real settlement:
  - `docs/release-status.md:L11–13` (C0/C1/C2/C3 table);
  - `docs/start-here.md:L26` ("C2/C3 are not qualified");
  - `docs/public-preview-qualification.md:L28`.
- Candidate profile `profiles/security-runtime-f5b-candidate-20261016.json` records `selected=false`, `reference_release_authorized=false`, `production_deployment_authorized=false`, and the quarantine limitation.
- F5b freeze README repeats "No release or production authorization is granted" and bounded-synthetic framing.

## 6. Prior-tracker reconciliation (#87 rights, #140 deployment) — PASS

- **#87 (`PV-FINAL-DIST`)** closed as superseded; its carried residuals are:
  - PRP and TFA remain `licensing_state:"unresolved"`, `redistributed:false` and have no notice folder in `docs/releases/selected-notices/`. Correctly carried; no new rights promotion.
  - All other external components keep `rights_accepted:false`, `licensing_state:"notice_evidence_only"`; carried through the freeze's `external_components` list and the 28-entry notice ledger.
- **#140 (deployment boundary)** closed as superseded; its carried residuals are:
  - "Deployment-dependent" in every row of `docs/v1-deployment-responsibilities.md`;
  - Operational trust **HOLD / NOT ESTABLISHED** in `docs/operational-trust-status.md`;
  - C0/C1/C2/C3 bounds and no external settlement in `docs/release-status.md` and `docs/public-preview-qualification.md`.

No prior-tracker guidance is lost. Nothing requires a new owner decision on already-settled matters.

## 7. F3R + native retention line — PASS

The three independent surfaces agree on run / artifact / tested-source / retention path:

| Surface | Run | Artifact | Tested source | Retention path |
|---|---|---|---|---|
| `docs/releases/f3r-qualification-receipt-20261016.md:L26,L31,L33` | 38925303886 | 12056860537 | 7022881e0958543a8b7685031c63132891b5f47c | `results/security-runtime-f5b-20261016/` |
| `docs/releases/security-review-freeze-f5b-20261016/verification.json:L203–218` | 38925303886 | 12056860537 | 7022881e0958543a8b7685031c63132891b5f47c | `results/security-runtime-f5b-20261016/` |
| `docs/release-status.md:L58` | 38925303886 | — | 7022881e0958543a8b7685031c63132891b5f47c | — |
| `profiles/security-runtime-f5b-candidate-20261016.json:qualification_evidence` | 38925303886 | — | 7022881e0958543a8b7685031c63132891b5f47c | — |

`gh api repos/cogno-us/cognous-stack-qualification/actions/runs/38925303886` confirms status `completed`, conclusion `success`, head `7022881e…`.

## Explicit residuals (not claimed by this packet)

The F6 package explicitly does NOT claim any of the following; these must remain outstanding for the F7 reviewer:

1. No independent security review acceptance. Source scans do not prove coverage of excluded binary artifacts, history, semantic PII/IP or independent security clearance. (Freeze README; `docs/public-preview-qualification.md:L18–20`.)
2. No independent IP / rights-acceptance for any external component. All 13 externals carry `rights_accepted:false`; PRP and TFA remain `licensing_state:"unresolved"`.
3. No mailbox delivery / response SLA; policy/HTTP/MX checks only (`docs/security-reporting-and-triage.md`, `docs/public-preview-qualification.md:L20`).
4. No production deployment, release tag, announcement, operational activation, component-lock update, or public W7 re-selection.
5. The native qualification archive is retained at the qualification repo separately; this hub receipt does not substitute for that retention (`docs/releases/f3r-qualification-receipt-20261016.md:L41`).
6. The quarantined upstream Moltbot application tree at tag `upstream-moltbot-quarantine-20261016` is preserved as history only and is not part of the candidate.
7. Non-GitHub bibliography/citation links are egress-blocked in this session and were not re-verified live; the F7 reviewer should check them out of band (see RESIDUAL in check 4).

## F7 acceptance packet — concrete list

The following bytes-exact bindings are complete and ready for the F7 reviewer:

| Item | Binding |
|---|---|
| Hub head | `0abd9e14…` (post-merge re-check PR #153 on `main`) |
| Review freeze dir | `docs/releases/security-review-freeze-f5b-20261016/` |
| Review ZIP | `cognous-source-review-f7fe1bc.zip` / SHA-256 `37d575d776dc32cd79ecf815edb328038a49f9c314d3aeb7b82bed406d3ee337` / 1,218,856 bytes / 175 members |
| Manifest | `manifest.json` / SHA-256 `9c2cc53cfd6e55b50704dd2776bc4a7add224f27e8eb1bfa388df28d7361ad4b` |
| Verification | `verification.json` / SHA-256 `6b2ae025d74aafeb2347cb56b79f6d241d0e80c3da347de2e61278c84a3c577b` |
| Reproducer | `reproduce.py` / SHA-256 `8b925901037a889dee3c60a5012cc06b32d5fb17182751b27a58a484f1e4cbf8` |
| SHA256SUMS | `SHA256SUMS` present and matches on-disk sidecar hashes |
| Candidate profile | `profiles/security-runtime-f5b-candidate-20261016.json` / SHA-256 `f159158cd9f5504a6e1c0683cbd136532c1c6938300dd17aa45f700ad9278274` |
| F3R receipt | `docs/releases/f3r-qualification-receipt-20261016.md` |
| F3R run | `https://github.com/cogno-us/cognous-stack-qualification/actions/runs/38925303886` — success, head `7022881e…` |
| Native archive | `cogno-us/cognous-stack-qualification` `main af9f5843`, `results/security-runtime-f5b-20261016/native-archive-run.zip`, SHA-256 `a089f9b33edff6521ceb78885b866f9a87280dc4d5584b3be471b15d309f672d`, 4,890,962 bytes, 1,862 members |
| Runtime quarantine | tag `upstream-moltbot-quarantine-20261016` at `fd6b76fa…` on `cogno-us/cognous-execution-runtime`; preserved as history only |
| Prior F6 artifact precedent | `docs/releases/security-review-freeze-20261016/` (historical bytes retained unchanged) |
| Prior trackers reconciled | #87 (closed/superseded), #140 (closed/superseded); residuals carried forward |
| Operational trust | #30 **HOLD / NOT ESTABLISHED** |
| Component lock | unchanged (SHA-256 `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc`); public W7 selection unchanged; `issue #68` untouched |

No release or production authorization is granted by this document.
