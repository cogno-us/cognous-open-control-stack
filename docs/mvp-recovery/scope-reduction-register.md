# Artifact 2 - Scope Reduction Register

Status: PROPOSED, non-authorizing; HOLD. Classes: A MVP blocker, B MVP hardening, C post-MVP, D stop/remove. Step IDs and names are those of `docs/program-v0.2/engineering-register.json` (rev r4-aoi) and are preserved; that record is not edited. Test: does the MVP workflow fail a mandatory safety invariant or an independently approved acceptance requirement without the item? The register's own dependency edges (e.g. 1.7 -> 1.3, 3.5 -> 3.2/3.3, 4.x -> 2.5/3.6) would pull the registry and Orchestrator in; the MVP re-bases those edges (see critical-path.md) without editing the register. "Merged" means a candidate on main, not qualified.

## The 24 steps
| Step | Status (evidence) | Class | Reason |
|---|---|---|---|
| 1.1 Inventory and 49-row crosswalk | merged docs (#195/#196) | C | Superseded by this register; no invariant depends on it. |
| 1.2 Authority and separation contract | merged docs (#197/#199); M0 approved (R, builder transcription of the operator decision) | B | "Producer cannot self-certify; authority not carried by the message" is already encoded; needs only a short frozen statement in the MVP claim. Refund-chain migration to the Orchestrator (ADR-P05): C. |
| 1.3 Registry R0 contract | merged docs (#199) | C | Fixed pinned configuration suffices; the registry does not replace effect-time authorization (registry design doc). |
| 1.4 Independent evidence handoff | merged docs; producer side merged (orch #124/#125/#127, (R) not re-checked) | B | Invariant 6 is met by the existing Replay + Evidence Pack path; the Orchestrator handoff is not needed unless D3 chooses it (then A). |
| 1.5 Identity, state and recovery model | merged docs (#198) | B | Already mapped onto the existing ODES lifecycle; residual is review and freeze. |
| 1.6 Comparative CA-01..CA-06 | merged docs | C | Comparisons only. |
| 1.7 Minimum profile and frozen qualification entry | designed, not frozen | A (re-scoped) | Qualification needs one frozen claim and entry. Re-scope to this MVP definition; drop registry L1/L2, coverage-manifest and overlay-depth text. |
| 2.1 Versioned rule records and bounded store | merged candidate (#204); `/1` successor docs-only | C | No invariant needs a registry store; floor stays in code. No `/1` code. |
| 2.2 Source-backed policy/scanner extraction | analysis merged (#205-#208) | C (extraction work D) | Scanners guard claim wording, not the effect path. Analysis kept as history. |
| 2.3 Mandatory check manifest/evaluators | merged `/0` + evaluator binding (#209/#211); #213 open | C | Nothing shows the refund path calls it. Caveat: if the MVP verdict relies on verifier checks, "crash = error" is a fail-closed property and Qualification should say so (then B). |
| 2.4 Activation, rollback and freshness | designed only; not authorized (Q13) | C (dynamic registry: D) | Needed only for dynamic rules; a fixed qualified configuration needs none. Largest refreeze driver. |
| 2.5 Independent registry equivalence | not started | C | Meaningful only with a registry and migration. |
| 3.1 Orchestrator runtime powers contract | merged (orch #124, (R)) | B | Lock-driven pins support exact candidate identity; done as candidate; A only under D3 = Orchestrator. |
| 3.2 Durable single-host workflow | merged #126/#128; #132 open | C | Durable unknown-outcome handling already lives in Runtime + Replay; #132 expands lifecycle. Park. |
| 3.3 Control Plane/Runtime integration | not started; locked | A (narrowed) | Unmediated paths within the declared profile is a mandatory negative. Scope: only effect surfaces reachable from the MVP route, after a static-reachability pass (U). Any locked change needs approval and F3. |
| 3.4 Qualification handoff integration | merged #125/#127; #130 open | B | Producer side done; independent verification can use Replay/Evidence Pack. |
| 3.5 Crash/revocation/reconciliation | not started; locked items | A (re-scoped) | This is MVP behaviour 7. Do it on the existing Control Plane/Runtime stack, not the Orchestrator. |
| 3.6 Independent orchestration qualification | not started | C | Qualifies the Orchestrator, which the MVP excludes; replaced by the MVP Qualification Contract. |
| 4.1 Lock/tuple compatibility | not started | A (one fixed tuple) / B (generalized manifest) | Exact candidate identity is what prevents self-certification. No overlay build. |
| 4.2 Enforcement coverage and security | not started | A (closed inventory for the declared profile) | Independent enumeration and removal-detection for the effect paths. Coverage Manifest part: C. Operator documents conflict on whether this is a minimum (D5). |
| 4.3 D/R/M known issue and controller closure | audit done (s01) | Split | A only for items shown on the refund path (candidates R03, R04, R08, R10, M02, M04, M05, D07, D10, R14; on-path status U); the rest C or documented as limits. |
| 4.4 Combined adversarial battery | not started | A (cut) | Reuse the adversarial matrix; keep the mandatory negative controls; drop registry and Orchestrator cases. |
| 4.5 Independent v0.2 acceptance dossier | not started | A (renamed MVP acceptance dossier) | Must show the labelled results and the original-scope denominator (D15 reduction INCOMPLETE state surfaced honestly). |
| 4.6 Operator candidate decision packet | not started | A | The operator decision; release stays HOLD. |

## Other open work and named items
| Item | Class | Reason |
|---|---|---|
| Q1/Q5/Q9 lifecycle and store limits; 3.2-B | C (head cache: D) | Orchestrator not in MVP. PRs #131/#132 parked. |
| #130 `execution_standing` rename | C (cheap) | Do before any freeze of that wire; otherwise not needed. |
| Q6 external checkpoint (#131) | C | Claim limit instead: tail loss not detectable. Custody adoption needs operator commitment and possibly a locked change. |
| 2.3 `/1` manifest and dispositions (#213) | C | See 2.3. |
| 2.1 `/1` successor; 2.4 activation; scanner registry migration (M1 family) | C | Registry not in MVP. |
| Q11 reference-release repair | B, A if reference-release is the chosen qualification vehicle | Qualification's runner; Hub states requirements only. Alternative vehicle: Qualification's own exact-candidate run (see critical-path). |
| Q15 restricted ancestor profile | C | Only if the MVP uses the source-preserving handoff (D3). |
| Observability Coverage Manifest; drift monitoring; agent-identity interop; OTel projection; ISS V6; additional adapters | C (ISS V6, new adapters, drift: D) | No MVP invariant; agent identity stated as a claim limit. |
| Fleet management (ER-05-7 NOT APPLICABLE in Qualification) | C | Fleet orchestration is outside the MVP and already NOT APPLICABLE. |
| `docs/program-v0.2/minimum-profile.md` (proposed minimum acceptance: complete mandatory registry check coverage and a migrated rule family) | Superseded for the MVP | This proposal bundles registry items the MVP classifies C; the operator supersedes it for the MVP (to be confirmed, D5 related). The original file is unchanged. |
| Refreeze cascades (F3) | A only for a cascade forced by an A item | 7 PRs in 7 repos per refreeze observed; avoid cascades without on-path justification. |
| ODES failures (4, 3 declared; lost_ack, prior_absence and end-to-end export cases; one error class) | A or exclude from chain | Ambiguous-commit evidence path; fix, or remove the ODES export from the MVP evidence chain (D4). Exclusion does not remove the Replay ER-07-2 ambiguous-dispatch xfails. |
| Exchange (GAX) `runtime_authority_profile` forwarding | A only if GAX is in the ingress path (D1) | Otherwise declared limit F5b stands (owner decision 2026-10-19). |
| Verifier c0b8ba1f not probed at the lock | A if verification claims use it | Otherwise exclude the verifier from the claim. |

## Per-item questions the operator should confirm
D1-D6 in critical-path.md.
