# Public developer preview qualification (candidate 0.1)

> **Status: qualification in progress, not a published release.** Canonical [control board #68](https://github.com/cogno-us/cognous-open-control-stack/issues/68). This page is a public-facing audit checklist; it is **not** a component-selection decision, deployment authorization or production assurance statement.

## Start with the selected evidence, not the newest component main

Read the [component lock](../component-lock.json), [release status](release-status.md), [evidence snapshot](../collateral/evidence-snapshot.json) and [evidence index](evidence-index.md). Preserve each artifact's source SHA, version, digest, generation and test scope. Component acceptance, selected release, historical CI and operational deployment are different statuses.

**Important:** The [developer quickstart](quickstart.md) explicitly reproduces the historical documentation checkout `5737267d94d2b445735c95e8480a31de73a2abe8`. Running that path does not independently qualify current `main` or the candidate W7 release-selection [PR #63](https://github.com/cogno-us/cognous-open-control-stack/pull/63). The release-selection proposal is not selected merely because its PR exists. A fresh current-selected execution is now recorded in the [October 13 verification](verification/public-release-verification-2026-10-13.md), tracked at [#69](https://github.com/cogno-us/cognous-open-control-stack/issues/69).

## Six gates

| Gate | Acceptance requirement | Current disposition |
| --- | --- | --- |
| PV-1 navigation and documentation | Entry paths, complete applicable local references, external links, license paths and scoped exact-head documentation checks | **Partial**: [October 13 checkpoint](releases/publication-acceptance-2026-10-13.md) records 14 authored pages / 168 local links and 28 retained selected notices; full distribution and final artifact rights review remain open. |
| PV-2 frozen snapshot | Exact hub and selected component SHAs, file digests, compatibility matrix, evidence generation, scenario provenance and no historical count substitution | **Technical PASS for named selected evidence**: [October 13 root verification](releases/publication-acceptance-2026-10-13.md) checks ancestry, pins and digests; final publication acceptance remains separate. |
| PV-3 reproducible example | Clean disposable environment, selected SHAs, independently executed command and output, valid and denied synthetic refund, SQLite destination assertion and recovery/negative controls | **Technical PASS for named synthetic execution**: [October 13 acceptance checkpoint](releases/publication-acceptance-2026-10-13.md) reviews the published raw evidence; final release-owner acceptance remains open. |
| PV-4 risk and trust disclosure | C0/C1/C2/C3 bounds, unknown delivery, no external settlement or production identity, independent observation and explicit operational trust HOLD | **Partial**: documented in [release status](release-status.md); publication surfaces need review. |
| PV-5 publication safety | No credentials, customer data, protected IP, production payment effects, live grants or unapproved operational authority in distributable samples | **Partial**: [October 13 executed screening](verification/public-release-verification-2026-10-13.md) covers hub history/tree and selected evidence; semantic PII/IP and broader distribution signoff remain open. |
| PV-6 security/feedback | Working private vulnerability report path and non-sensitive public issue triage, with maintainership and scope stated | **Partial**: [reporting and triage](security-reporting-and-triage.md) records policy/HTTP/MX checks and maintainer responsibilities; mailbox delivery and response remain unverified. |

Only evidence-linked verification can upgrade a gate to **PASS**. An unexecuted example, a passing shell syntax check or an open PR is not proof of behavior. Record **BLOCKED** explicitly where prerequisites are inaccessible.

## Exact selected reference vs historical evidence

The current [release-status page](release-status.md) reports **35** selected synthetic acceptance scenarios across two repetitions and a separate optional same-host C1 campaign of **73** tests. Those populations must remain separate. It also references an earlier **915-test** persistence campaign as historical. Never aggregate these counts or infer production coverage.

The default **C0** revalidates decision-critical authority shortly before dispatch but remains subject to a check-to-destination-commit race. **C1** is optional, same-host, cooperating SQLite ordering; it is not external destination atomicity. **C2/C3 are unqualified.** Timeout or absence of observation alone is not permission to retry; effect-ID dedupe is not dedupe of equivalent business intents. The synthetic SQLite refund is **not** real processor settlement.

## Release disposition

The operator/deployment trust [issue #30](operational-trust-status.md) remains **HOLD / NOT ESTABLISHED**. A public developer preview, if approved separately, would invite technical reproduction and security feedback—not grant permission for real-world effects.

Before an announcement, the [control board #68](https://github.com/cogno-us/cognous-open-control-stack/issues/68) must link a source revision and result to each PASS and record any explicit risk-accepted exception. No production authorization, component-lock update, release tag or merge follows from this document.

Current gate reconciliation: [publication acceptance checkpoint](releases/publication-acceptance-2026-10-13.md). Two bounded technical gates pass; no final publication GO is implied.
