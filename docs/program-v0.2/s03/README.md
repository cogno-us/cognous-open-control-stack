# S03 contract drafts (proposed)

**Non-authorizing, documentation only.** Release and production remain on HOLD. These drafts start no implementation, change no locked component, edit no Qualification expectation or verdict logic and record no operator decision. No step was added, removed or renumbered. They are input to the M0 gate described in [../s02/README.md](../s02/README.md).

| Document | Step | Content |
|---|---|---|
| [identity-and-lifecycle.md](identity-and-lifecycle.md) | 1.5 | 18-identifier crosswalk read at the lock revisions, lifecycle term mapping onto existing vocabularies, the six meanings of "unknown", proposed identity decisions SP-01 to SP-05, reconcile-only recovery |
| [minimum-profile-and-coverage.md](minimum-profile-and-coverage.md) | 1.7 | Named deployment profiles, M1 acceptance items A1 to A8, coverage declaration, overlay target, frozen qualification entry |
| [coverage-seed.json](coverage-seed.json) | 1.7 | Machine-readable seed inventory of the five observed effect surfaces |

## Findings that change earlier records

- The public `DurableRefundDestination.commit` surface covers six direct and twelve total subclasses in runtime `ec728da6` by a static scan; S01 recorded four. The S01 record is kept as history.
- ODES `operation-identity` already defines `operation_id` as the stable business identity and states that `effect_id` changes with the grant revision. The proposed answer to the stable-identifier question is to select that existing opt-in profile, not to add an identifier.

## Still open

The Orchestrator reserved state list and the 15-state list are reconciled at step 1.5 delivery against Orchestrator source not re-read here. Whether `correlation_id` and `run_id` enter any commitment is REQUIRES INVESTIGATION. The overlay layer depth is inferred, not measured. Reachability of each effect surface from the profile path is REQUIRES INVESTIGATION.
