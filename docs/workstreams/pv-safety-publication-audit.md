# PV-SAFETY: public-preview publication and claims audit (issue #73)

**Audit status:** PARTIAL / HOLD. **Source inspected:** hub `3efe456d10a37dcdd2277b4a37d9034403380f09` (2026-10-10). **Selected generation:** `component-lock.json` `merged-producers-v1` (blob `b3bf15918ec7eaccd10c486b61926351d392dd04`; file not edited). This is a public, findings-only review; it does not constitute a repository-wide secret scan, release approval or deployment assessment. Operational trust [orchestrator #30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30) remains **HOLD / NOT ESTABLISHED**.

## Sources actually inspected

Read `README.md`, `docs/start-here.md`, `docs/quickstart.md`, `docs/release-status.md`, `collateral/business-collateral.md`, `collateral/one-page-overview.md`, `docs/security-and-threat-model.md`, `docs/architecture.md`, `SECURITY.md`, `CONTRIBUTING.md`, `component-lock.json`, issues #68/#70/#73 and the current main commit. `AGENTS.md` at repository root returned 404 (absence at that path only). Individual linked fixtures, archived artifacts, images, historical commits, subdirectories not named above, and component repositories have **not** been exhaustively inspected. Therefore a negative secret-exposure finding cannot be asserted.

## Public claims: path/line observations and level

| Observation | Current evidence at audited SHA | Risk and treatment |
|---|---|---|
| C0 is pre-effect revalidation, not destination commit atomicity | `docs/release-status.md:11`; `docs/start-here.md:20`; `collateral/business-collateral.md:11` | Low for inspected text; preserve explicit check-to-commit race in every promotion |
| C1 is optional cooperating same-host SQLite only; C2/C3 not qualified | `docs/release-status.md:12-13`; `collateral/one-page-overview.md:11` | Low for inspected text; do not translate optional source presence into selected activation |
| Timeout/absent observation never permits retry | `docs/start-here.md:22`; `docs/release-status.md:24,44`; `collateral/one-page-overview.md:41` | Low for inspected text; require original-effect reconciliation |
| Effect-ID dedupe differs from business-intent dedupe | `README.md:107`; `docs/release-status.md:26,44`; `collateral/business-collateral.md:28,65` | Medium residual technical risk; duplicate business intent possible under selected default |
| No real payment settlement or production credentials qualified | `docs/release-status.md:15,48`; `collateral/business-collateral.md:7,17`; `docs/start-here.md:15` | Low for wording; high if externally advertised as operational payment safety |
| Operational trust HOLD on canonical entry path | `docs/start-here.md:11` links operational trust #30; issue #68 prohibits a preview GO being treated as operational GO | Medium publication risk: `README.md` and two collateral summaries do not independently display the explicit #30 HOLD marker. Add prominent status in owner-coordinated publication edits (#70), without changing historical snapshot files or their detached hashes |
| Broad assertion of absent credentials | `SECURITY.md:3` says the repository contains no credentials; a full distributed-file and Git-history inspection has not occurred in this audit | Medium epistemic/publication risk, **not evidence of actual exposure**. Prefer: “This hub is intended for documentation and bounded synthetic examples; do not place credentials or sensitive data here. Repository-wide disclosure screening must be performed before public release.” Coordinate edit with #70 |
| Historical vs selected execution example | `docs/quickstart.md:3,23` explicitly pins an earlier documentation baseline, rather than current main; `README.md:73-87` describes the default runner | Medium usability risk: do not imply the historical pinned quickstart is an independently reproduced exact-current-head flow; PV-RUN #69 owns reproduction |
| Public private-IP boundary | `README.md:138`, `CONTRIBUTING.md:7-9` prohibit private material | No actual private ISS/IGPG exposure identified **in inspected text**; full evidence/artifact/history scan remains OPEN |

## Publication safety: actual vs possible exposure

**Confirmed:** No live credentials, customer PII, real settlement receipt or private implementation detail was identified in the *specific passages and files read* above. This is not proof of their absence elsewhere. An email address in `SECURITY.md` is an intentionally published security contact, not a secret. Repository-wide credential/PII/IP checks, committed binary/ZIP/artifact inspection, complete Git history, generated output files and upstream linked repositories are **not executed** in this pass. No raw suspected secret or personally identifying record is reproduced here.

**Required private escalation if a suspected actual disclosure is identified:** Do not paste content into an issue/PR, comment or public CI output. Communicate only a redacted path, commit, category and verification instructions through the private contact in `SECURITY.md`; follow incident response for revocation/removal as independently authorized.

## Recommended publication wording (for #70 documentation owner)

> **Developer preview candidate — not yet released.** The selected `merged-producers-v1` chain is a pinned bounded synthetic SQLite reference. C0 revalidates immediately before dispatch but is not atomic with destination commit. C1 is optional and same-host SQLite only; C2/C3 are not qualified. Timeout or absent observation is not retry permission. Effect-ID deduplication does not deduplicate equivalent business intent across distinct effects. No real payment settlement, production credential custody or institutional deployment has been established. Operational trust #30 remains **HOLD / NOT ESTABLISHED**.

The above text is a **recommendation**, not adopted external collateral. Coordinate with #70 and #72 before editing signed/digested release and collateral snapshots.

## Exit gate and unresolved work

- **PV-4:** PARTIAL. Inspected core public claims are suitably bounded; review every publication, externally served marketing page, downloadable artifact and announcement before PASS. Explicit HOLD should be visible where a reader may bypass `docs/start-here.md`.
- **PV-5:** OPEN / BLOCKED FOR GO. No demonstrated leak from the sampled file contents, but no exhaustive selected-tree plus history, archive, attachments, examples, artifact and generated-output screening; no operational credentials or production effects were accessed.
- **Decision:** **HOLD** on public-preview publication pending remaining board gates and sign-off. **HOLD** on operational trust #30 regardless of a later preview decision.
- **Validation:** This prose-only audit makes no runtime, institutional authority, release lock, deployment, credential or permission change. A successful GitHub workflow by itself would not validate the unexecuted disclosure inventory or security claims.

Ownership: this file is PV-SAFETY's audit evidence only. PV-DOCS #70 owns navigation, templates, external links and coordinated wording changes; PV-SNAPSHOT #72 owns hash/snapshot work; PV-RUN #69 owns reproduction.
