# S01 source packet (review draft, 2026-10-22)

Non-authorizing. Release and production remain on HOLD. This is a reviewable documentation packet that reconciles the v0.2 program ([README](../README.md), merged by hub PR 194) with what the repositories contain. It is a dated record against exact revisions, not live status; assignments, check results and acceptance are kept in the engineering controller ([#193](https://github.com/cogno-us/cognous-open-control-stack/issues/193)) and the independent qualification controller ([#218](https://github.com/cogno-us/cognous-stack-qualification/issues/218)). It implements nothing, spends nothing and authorizes nothing.

## Contents

| File | Content |
|---|---|
| [inventory.md](inventory.md) | Verified inventory of 18 repositories at exact revisions; revision disagreements between artifacts; registry-, orchestrator- and qualification-relevant facts |
| [crosswalk.md](crosswalk.md) | All 49 original rows mapped to the 24 steps, with disposition and source finding |
| [defects.md](defects.md) | Planning-defect register with evidence, correction and lane; owner decisions raised |
| [issues-disposition.md](issues-disposition.md) | The 38 known issues with owner, critical-path flag and candidate disposition |
| [comparative.md](comparative.md) | CA-01 to CA-06 assessed with the nine requested deliverables each; what could not be read |
| [estimates.md](estimates.md) | Source-grounded low/central/high estimates per step, minimum profile separated from the full plan |

## Method and limits

Four read-only source reviews were run (orchestrator and qualification; registry and pin overlay; comparative requirements; identity, lifecycle, enforcement and known issues). Each repository was inspected at the locked revision where one exists. Findings carry the evidence tags VERIFIED, INFERRED or REQUIRES INVESTIGATION. Nothing was executed apart from reading source and calling read-only interfaces; no component test suite was run, and the counts of tests are static. Not read: the OpenAPPA site, the Microsoft agent governance repository and the paper "From Mainline to Governed Cognition"; claims that depend on them are marked. The Engineering Constitution was reviewed at commit `1c2e920f` and later; no exact revision is adopted by this packet.

## Separation of controllers

Findings about the orchestrator, registry and other components are engineering inputs. Findings about qualification expectations, controller logic and verdict reporting (the probe status rule, scope-reduction disclosure, hash-freezing of requirements, the digest rule, prp/tfa and wiki-derived applicability) are listed in [defects.md](defects.md) with lane QUAL: Qualification decides them independently through its own controller, and engineering neither edits expectations nor presents these items as accepted. Historical failures and retained results are preserved; the g8-r10 outcome and the pre-reduction INCOMPLETE verdict are unchanged.

## What this packet changes and does not change

It adds this directory only. Corrections to the program files (register steps, dependencies, mapping, decisions, estimates) follow as a separate bounded pull request that cites defect identifiers from [defects.md](defects.md). The original 49-row register is not edited.
