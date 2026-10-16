# F7 acceptance packet — F5b-repaired bounded synthetic reference, 16 October 2026

Publication HOLD. Production HOLD / NOT ESTABLISHED. Rights/security acceptance pending. **No release, tag, announcement, publication or production authorization is granted by this document.** This packet exists only to assemble the exact byte bindings, qualification evidence, rights/notice state, safety state and explicit residuals in one reviewable place so the owner, André de Lima, can make the F8 decision described in section 7.

## 1. Scope and bounds

The subject of this packet is the **seven-component F5b-repaired merged-source synthetic bounded reference** at the refrozen bytes identified in section 2. It is not:

- a release selection (`component-lock.json` is unchanged; the public W7 selection is unchanged; issue #68 is untouched),
- a production authorization (operational trust orchestrator remains **HOLD / NOT ESTABLISHED**),
- an authority or settlement (the C0 check-to-commit race remains, optional same-host cooperative C1 only; no C2/C3; no real external settlement),
- an independent security clearance, IP clearance or mailbox delivery/response assurance.

Carried forward verbatim from the F6 package checks (`docs/releases/f6-package-checks-20261016.md`): "No release or production authorization is granted by this document."

## 2. Exact byte bindings

All hashes recomputed locally against the current `main` head of `cogno-us/cognous-open-control-stack` immediately prior to opening the F7 PR. The native-archive hash and size are the values reported by `cogno-us/cognous-stack-qualification` and the F3R receipt; this hub packet does not substitute for the retention at the qualification repo.

| Item | Binding |
|---|---|
| Hub head (post-F6) | `cogno-us/cognous-open-control-stack` `main` `30638e78` (merge of PR #154, which merged `finalization/f6-package-checks-20261016`) |
| Review freeze directory | `docs/releases/security-review-freeze-f5b-20261016/` |
| Review ZIP | `cognous-source-review-f7fe1bc.zip` — SHA-256 `37d575d776dc32cd79ecf815edb328038a49f9c314d3aeb7b82bed406d3ee337` — 1,218,856 bytes — 175 members — built from source `f7fe1bc03cf67df2ab5afe81ba513580a29fde25` |
| Manifest | `docs/releases/security-review-freeze-f5b-20261016/manifest.json` — SHA-256 `9c2cc53cfd6e55b50704dd2776bc4a7add224f27e8eb1bfa388df28d7361ad4b` |
| Verification | `docs/releases/security-review-freeze-f5b-20261016/verification.json` — SHA-256 `6b2ae025d74aafeb2347cb56b79f6d241d0e80c3da347de2e61278c84a3c577b` |
| Reproducer | `docs/releases/security-review-freeze-f5b-20261016/reproduce.py` — SHA-256 `8b925901037a889dee3c60a5012cc06b32d5fb17182751b27a58a484f1e4cbf8` |
| SHA256SUMS sidecar | `docs/releases/security-review-freeze-f5b-20261016/SHA256SUMS` — present; sidecar hashes match on-disk recomputation |
| Candidate profile | `profiles/security-runtime-f5b-candidate-20261016.json` — SHA-256 `f159158cd9f5504a6e1c0683cbd136532c1c6938300dd17aa45f700ad9278274` — `selected=false`, `reference_release_authorized=false`, `production_deployment_authorized=false` |
| F3R qualification receipt | `docs/releases/f3r-qualification-receipt-20261016.md` |
| F6 package checklist | `docs/releases/f6-package-checks-20261016.md` (7 PASS, 1 environmental RESIDUAL, 0 FAIL) |
| Native qualification archive | `cogno-us/cognous-stack-qualification` `main` `af9f5843`, path `results/security-runtime-f5b-20261016/native-archive-run.zip` — SHA-256 `a089f9b33edff6521ceb78885b866f9a87280dc4d5584b3be471b15d309f672d` — 4,890,962 bytes — 1,862 members — byte-identical to GitHub artifact `12056860537` |
| Runtime quarantine tag | `cogno-us/cognous-execution-runtime` tag `upstream-moltbot-quarantine-20261016` at `fd6b76fa0e85feb5b67324114bf790d3a12fdaf1` — preserved as history only, not part of the candidate |
| Prior freeze (historical) | `docs/releases/security-review-freeze-20261016/` — retained unchanged; the F5b freeze does not supersede the historical bytes, it adds a sibling |
| Prior trackers reconciled | #87 (`PV-FINAL-DIST` rights, closed/superseded, residuals carried); #140 (deployment boundary, closed/superseded, residuals carried) |
| Component lock | `component-lock.json` — SHA-256 `dc66aafeb15eb2d5695b2217019775a1a2e517b3a6ab55b07c1b37349d8ee5cc` — unchanged |

Local recomputation confirms every hash in this table against the current hub head.

## 3. Qualification evidence

Verbatim bindings carried from `docs/releases/f3r-qualification-receipt-20261016.md`:

- **Qualification run URL**: https://github.com/cogno-us/cognous-stack-qualification/actions/runs/38925303886 (status `completed`, conclusion `success`).
- **Tested qualification source**: `7022881e0958543a8b7685031c63132891b5f47c` (merge commit `7b29c2a3222492d29e58480284d40acc05c8c149`).
- **Workflow / suite / runner**: `.github/workflows/security-runtime-qualification.yml`, `suites/security-runtime`, `tools/run_security_runtime.py`.
- **Hosted job**: `117055196162`.
- **Compatibility profile**: `security-runtime-f5b-20261016` (new strict Exchange profile; nonselected).
- **Source-identity invariants** (from the receipt verbatim):
  - `source_revisions_equal_profile_pins = true` (yes),
  - `source_hashes_equal_tested_head_bytes = true` (yes),
  - qualification worktree clean,
  - no SQLite `-wal`/`-shm`/`-journal` sidecars present.
- **Raw outcome**: 36 raw JUnit cases per repetition, **two repetitions** on the same tested source, **0 failures / 0 errors / 0 skips** per repetition (36 × 2 pass). The two repetitions are fresh-store repetitions of the same scenario matrix on the same tested source; they are **not** 72 independent scenarios.
- **In-job verification**: 668 original hashed members verified per repetition.
- **Native audit summary** (from the receipt and verification.json): `revoked=0 effects`; no SQLite journal/wal/shm sidecars; `source_revisions_equal_profile_pins=true`; `source_hashes_equal_tested_head_bytes=true`; worktree clean. No independent-security or independent-IP conclusion is implied.
- **Native archive byte identity**: the `results/security-runtime-f5b-20261016/native-archive-run.zip` SHA-256 `a089f9b33edff6521ceb78885b866f9a87280dc4d5584b3be471b15d309f672d` (4,890,962 bytes, 1,862 members) is byte-identical to GH artifact `12056860537` named `f5b-requalification-7022881e0958543a8b7685031c63132891b5f47c`, expires `2027-01-14T15:36:24Z`. The ZIP was not downloaded in-job (session egress proxy refuses the azure blob redirect); member hashes were revalidated in the workflow run through `tools/summarize_security_runtime.py` notice annotations on check run `117055196162`, read via REST; decoded `junit.xml`/`stdout.log` SHA-256 equal the in-job hashes.

The F3R run and the native-archive copy both continue to exist as public artifacts; their continuing existence is not independent assurance (see section 6).

## 4. Rights and notices

- **13 external components** are tracked in `docs/releases/security-review-freeze-f5b-20261016/manifest.json:external_components`. All 13 carry `rights_accepted:false` and `redistributed:false`.
- **PRP** and **TFA** remain `licensing_state:"unresolved"` with no notice folder under `docs/releases/selected-notices/`; this is correct per owner's prior exclusion and tracker #87's reconciled residuals.
- The 11 other externals carry `licensing_state:"notice_evidence_only"`.
- **Notice ledger**: 28-entry external notice ledger under `docs/releases/selected-notices/<component>/…` (11 component folders + README), plus hub `LICENSE` and hub `NOTICE`, equals **30 required notices**. All 30 are byte-identical to the files hashed in `manifest.json:files` and byte-identical to the prior freeze's notice set.
- **No new rights claim is advanced by this packet.** No component's `rights_accepted` is flipped; no notice is added, removed or re-promoted; no PRP/TFA rights state change.

## 5. Safety

- **F5a inventory**: 116 findings, split 7 high / 54 medium / 55 low (as reported on the triage tables posted to https://github.com/cogno-us/cognous-open-control-stack/issues/68).
- **F5b dispositions** across the candidate: 41 REPAIRS merged, 18 upstream-runtime residuals quarantined to the tag `upstream-moltbot-quarantine-20261016`, 33 DOC corrections merged, 22 DEFER, 2 already disclosed.
- **Candidate repair breadth**: all **21 candidate-component repairs** were merged in one requalification round against the single F3R run.
- No independent security clearance is claimed. Source scans do not prove coverage of excluded binary artifacts, history, semantic PII/IP or independent IP clearance.

## 6. Explicit residuals

Verbatim from the F6 checklist (`docs/releases/f6-package-checks-20261016.md`, section "Explicit residuals"):

1. No independent security review acceptance. Source scans do not prove coverage of excluded binary artifacts, history, semantic PII/IP or independent security clearance.
2. No independent IP / rights-acceptance for any external component. All 13 externals carry `rights_accepted:false`; PRP and TFA remain `licensing_state:"unresolved"`.
3. No mailbox delivery / response SLA; policy/HTTP/MX checks only.
4. No production deployment, release tag, announcement, operational activation, component-lock update, or public W7 re-selection.
5. The native qualification archive is retained at the qualification repo separately; this hub receipt does not substitute for that retention.
6. The quarantined upstream Moltbot application tree at tag `upstream-moltbot-quarantine-20261016` is preserved as history only and is not part of the candidate.
7. Non-GitHub bibliography/citation links are egress-blocked in this session and were not re-verified live; the F7 reviewer should check them out of band.

Additionally for F7:

8. No independent security or IP acceptance is granted by this packet; it only assembles bindings.
9. No mailbox delivery / response SLA is claimed.
10. **No** production deployment, reference release, public release, tag, announcement, operational activation, component-lock update or public W7 re-selection follows from this packet.
11. The quarantined upstream Moltbot application tree remains preserved **only** at the quarantine tag; the quarantine disclosure in the F5b freeze README and F3R receipt is the only in-scope mention retained in this packet, and no new mentions of Moltbot Safe / Reasoning Protocol are introduced here.
12. Non-GitHub bibliography links listed in the F6 RESIDUAL remain egress-blocked at this session and require out-of-band verification.
13. The F3R hosted run and the native-archive copy both continue to exist as public artifacts and are **not** independent assurance.

## 7. Owner decisions required at F8

Only the following decisions are open; already-settled matters (component selection, production authorization, PRP/TFA rights, mailbox SLA, C2/C3, Moltbot application retention) are **not** re-asked.

- **a. Accept this bounded synthetic reference as evidence of the F5b repair chain's qualification?** This is an acceptance of the evidence packet described in sections 2–5 against the residuals in section 6. It is **not** a release selection and **not** a production authorization.
- **b. Approve public reference publication of the exact-bytes packet above?** This would authorize the F8 execution scope in section 8 (and only that scope). It is **not** a production authorization. It does **not** create a release tag of the stack, change `component-lock.json`, change the public W7 selection, or trigger any announcement.
- **c. Any specific residual to escalate or defer?** The owner may list specific residuals from section 6 for escalation or deferral. Default is to leave the residual as recorded.

**Default on silence**: HOLD stays; nothing publishes; no tag is created; no component-lock change; no W7 re-selection; no announcement.

## 8. F8 execution scope if (b) is YES

If and only if the owner answers YES to decision (b), F8 performs exactly these four steps and nothing else:

1. **Tag the hub head.** Create annotated tag `public-reference-f5b-20261016` on `cogno-us/cognous-open-control-stack` at `30638e78` (or at `main` if `main` has not advanced; verify equality before tagging).
2. **Tag the qualification head.** Create annotated tag `public-reference-f5b-20261016` on `cogno-us/cognous-stack-qualification` at the current `main` head (`af9f5843` at the time of this packet, or a later `main` head that still carries the retained `results/security-runtime-f5b-20261016/` directory; verify presence before tagging).
3. **Tag the native-archive commit.** Create annotated tag `public-reference-f5b-20261016` on the qualification commit that produced `results/security-runtime-f5b-20261016/native-archive-run.zip`.
4. **Append-only link from release-status.** Append both tag URLs to `docs/release-status.md` under the existing F5b retention line, as an append-only reference. **No** component-lock change. **No** W7 re-selection. **No** change to any selected / release / production field. **No** announcement draft and **no** external messaging — those would belong to a separate gate that does not exist in this plan.

The proposed tag name is identical across all three refs so the three-way binding is machine-recoverable from the tag name alone.

Nothing beyond the four steps above is in F8 scope.

---

**No release or production authorization is granted by this document. No publication, tag or announcement is performed by this document.**
