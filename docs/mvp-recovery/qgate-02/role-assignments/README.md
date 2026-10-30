# Q-GATE-02 D1 role assignments

Non-authorizing. Work package OCS-MVP-QGATE-02-D1, base `dff727a9d039bac6b4e111aa14650deb08fef8be`. These are assignment packets in the existing `cognous-orchestrator-assignment-v1` convention (model: `../../assignments/A-mvp-readiness-OCS-MVP-READINESS-20261030.json`), governed by Constitution revision `dcdbe3b76843d672ca3cfb1f000124ecd78ed03c` (prospective orchestration convention) with adopted technical baseline `1c2e920f4e58e07a52e8e2408a506cf7dbc1292b`. Plan: issue #215 and the linked `docs/mvp-recovery/` documents. Writing these files does not create either role.

## Role designations (Architect decision D1)

| Role | Packet | Archetype | Tier |
|---|---|---|---|
| Qualification Owner (`independent_qualification_owner`) | `QUALIFICATION-OWNER-OCS-MVP-QGATE-02-D1.json` | D (qualification specification; no execution authorized now) | T3 |
| Adversarial Evidence Reviewer | `ADVERSARIAL-EVIDENCE-REVIEWER-OCS-MVP-QGATE-02-D1.json` | D slice, closest fit; no verdict authority | T2 |

## Exact boundaries

- Qualification Owner: fresh independent session from the builder; separate assignment and worktree; no authority to change production implementation; owns technical qualification protocol preparation, evidence review and later technical verdicts; may not self-certify organizational independence. No qualification execution is authorized.
- Adversarial Evidence Reviewer: separate fresh session from the builder and the Qualification Owner; read-only access to source and evidence; independently challenges assumptions, controls, observations and claimed technical conclusions; cannot modify evidence or production source.
- Both remain separate from implementation. AI technical review is authorized. Formal independent certification is NOT established; AI session lineage under the builder's environment is not organizational independence; per ADOPTION.md independence cannot be inferred from a second automated process alone and may not be waived through role renaming. D3/D4 remain UNAPPROVED.
- Protected (read-only) in both packets: Control Plane, Execution Runtime, Replay, Evidence Pack, ODES, Action Manifest, Verifier, qualification oracle, MVP battery, `component-lock.json`, accepted host-profile contract, capture script and gate (exact accepted paths to be bound by the Architect at activation: UNVERIFIED here), recorded evidence, production source and tests.
- Escalation: Architect, through the Cognous operator.

## Activation status

| Role | Status | Session identity | Worktree |
|---|---|---|---|
| Qualification Owner | NOT YET INSTANTIATED | PLACEHOLDER (none assigned) | not created |
| Adversarial Evidence Reviewer | NOT YET INSTANTIATED | PLACEHOLDER (none assigned) | not created |

## Activation step (operator/Architect action)

1. The Cognous operator or Architect launches a new top-level session for each role. A subagent or continuation of the builder does not satisfy "fresh independent session from the builder".
2. Each session gets only its own packet and its own separate worktree (distinct directory and branch; reviewer read-only).
3. Each session's identity is recorded in a dated instrument merged by a non-builder. Until then the status above stays NOT YET INSTANTIATED.

## Remains unestablished

Both roles' existence; organizational independence; Q7 formal independent certification; any qualification or verdict. Standing holds are unchanged: F3 engineering CLOSED; F3 Q2/Q3 UNRESOLVED; Q7 NOT ESTABLISHED; MVP candidate PROVISIONAL, UNFROZEN, UNQUALIFIED; final Tier 1 DEFERRED, NOT WAIVED; publication/release/production HOLD; Registry #58/#59 HELD; Control Plane #87 HELD; constructor tolerance NOT AUTHORIZED; Ed25519 #26/#34 HELD; V09 SEPARATE; DEF-OBS-TOL-OVERFLOW-1 OPEN, SEPARATE; R1 DEFERRED.
