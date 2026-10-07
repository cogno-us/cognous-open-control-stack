# V1 deployment responsibilities

This is an operational adoption checklist, not a report of completed production deployment. Each role below requires a named deployment owner and retained evidence before a real pilot. The reference environment preflight cannot complete these responsibilities.

| Responsibility | Accountable role | Required evidence | Current status |
| --- | --- | --- | --- |
| Institutional authority | Customer authority owner | Adopted action scope, grant issuance/revocation rules, competent approvers, review and remedy route | Deployment-dependent |
| Identity and key custody | Security owner | Authenticated principal mapping, key storage/rotation/revocation, service credential scopes | Deployment-dependent |
| Host and writer boundary | Platform owner | Inventory of trusted writers/admins, mediation/isolation design, filesystem and SQLite configuration | Deployment-dependent |
| Profile selection | Integration owner | Ordinary, atomic or intent profile selected explicitly; separate database ownership; no unqualified composition | Reference options available |
| Data and context | Data owner | Permitted sources/recipients/purposes, retention/deletion rules, custody, protected references and privacy review | Reference controls partial |
| Destination contract | Adapter owner | Target binding, observation consistency/finality, duplicate retention, remote uncertainty and current authority semantics | Synthetic refund qualified; real destination pending |
| Backup and restoration | Operations owner | Executed crash/recovery and backup/restore evidence, retained identity continuity, fail-closed response to loss | Deployment-dependent |
| Incident response | Operations and authority owners | Alert routes, suspension authority, investigation records, corrective grants and competent restoration decision | Reference records available; operational process pending |
| Useful outcomes | Pilot owner | Conventional-control baseline, task completion, false allows/blocks, unresolved delivery, latency and human review burden | Unmeasured in a field pilot |
| Release acceptance | Release owner | Exact source/configuration/environment, passing applicable checks, acknowledged limitations and explicit acceptance | Reference PR checks only |

Start with a bounded synthetic staging environment and one destination owner. An optional example or successful preflight does not authorize connecting production credentials or exposing a destination to an agent. Restore procedures must preserve consumed claims and intent ownership; an empty recreated database is not proof that an effect never happened.

There is no production deployment target, secret store or institutional adoption record configured by this change. No public service, cloud infrastructure or customer data is created or modified.
