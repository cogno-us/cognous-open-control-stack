# Program v0.2 (placeholders)

Status: planning placeholder, documentation only. Non-authorizing. HOLD unchanged. No production use, and no certification, security-clearance or readiness claim is made or implied. No release is planned until the owner decides.

## Purpose

This directory is the minimal planning and reporting structure for v0.2 development. It reuses the shape of an adopted structure from other Cognous programmes (one register, one status page, fixed vocabularies, review tiers, evidence pointers) and none of their content. The cells below are placeholders: owner roles, acceptance criteria and evidence pointers are filled in by later reviewed changes.

## Files

| File | Role | Mutable? |
|---|---|---|
| [README.md](README.md) | Purpose and reading guide (this file) | No |
| [engineering-register.md](engineering-register.md) | The register: workstreams WS-A to WS-G, one row per work item, stable ids | Only by reviewed revision |
| [status.md](status.md) | Dated reporting: status counts and links | Yes; the only place for mutable status |

## How to read

1. Start with the register. Each row has a stable id (`V2-<workstream>-<nn>`), a source or learning, a status from a small fixed vocabulary, an acceptance placeholder, an evidence pointer placeholder and a review tier.
2. Tiers are the review tiers of the [engineering constitution](../engineering-constitution.md#review-and-allocation-policy): Tier 1 routine, Tier 2 bounded ordinary engineering, Tier 3 critical. A row takes the highest tier that applies.
3. Rules come from the [engineering constitution](../engineering-constitution.md) and the [declarative governance registry](../declarative-governance-registry.md). Known issue classes (D, R, M) are defined in the [v0.1 known issues register](../releases/v0.1-known-issues.md); this program refers to them by id and does not copy them.
4. Read [status.md](status.md) for the current counts. Nothing else in this directory states current status.

## DOC-01

DOC-01 applies: no mutable execution state in canonical docs. The register and this file define scope, dependencies and acceptance. Current authorization, assignments, pull-request and CI state, blockers and progress appear only in [status.md](status.md) or in the linked hub issue. Dated evidence stays as historical records and is never rewritten.

## Out of scope for this placeholder

No tooling, no tests and no generated files. No pin, lock, profile, vendored contract or refreeze file is touched by it.
