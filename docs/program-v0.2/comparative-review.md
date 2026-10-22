# Comparative architecture disposition (preliminary; superseded in detail by S01)

These six requirements originate in the prior comparative analysis, not independently revalidated acceptance facts. S01 must check exact third-party sources and current OCS paths before final adoption.

| Item | Learning | Preliminary disposition | Boundary |
|---|---|---|---|
| CA-01 | Trajectory-aware information flow | Post-v0.2 implementation; P1 design analysis | Sensitivity not the same as reliability or grant |
| CA-02 | Typed policy validation | Candidate mandatory registry feature | No skip-on-error bypass |
| CA-03 | Rule distribution and convergence | Local digest/activation identity mandatory; network service deferred | Publication not proof of active load |
| CA-04 | Enforcement coverage declaration | Candidate bounded v0.2 control | Declaration not proof of OS confinement |
| CA-05 | Governed remediation | Design and optional later profile | No fabricated grant or blind retry |
| CA-06 | Canonical state and no-regressions | Use in compatibility/acceptance | Internal changes cannot silently break commitments |

For each: source URL/commit or version, existing implementation, gap, owner, impact, tests, and adopt/adapt/reject/defer decision remain S01 deliverables. This is a source review queue, not a conclusion.

**S01 update:** source-grounded dispositions, existing OCS artifacts that this table omitted, and the nine requested deliverables per item are in [s01/comparative.md](s01/comparative.md). In short: CA-01 adapt with enforcement deferred (an external conjunctive route already exists); CA-02 adopt the validation requirements already in the registry direction and reject Cedar as an internal engine; CA-03 adapt as a local subset; CA-04 adopt as a declaration-only manifest; CA-05 adapt vocabulary only, with the no-blind-retry subset already mandatory; CA-06 adopt as a promotion-boundary ADR plus compatibility gate. The table above is kept for traceability.
