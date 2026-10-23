# Architect rulings, third set (2026-10-23, items 1-8), known limitations and the Oct 24-31 critical path

Status: non-authorizing record. Nothing here is a Qualification verdict, an independent acceptance, a security clearance, a certification or a production-readiness claim. The author did not self-certify and re-ran no test. Qualification owns oracles and verdicts.

Labels:
- VERIFIED: text the author of this record actually read. Files read: the architect's full rulings of 2026-10-23 (attachment text, the primary source for section 1), and hub `docs/mvp-recovery/` `mvp-definition.md`, `implementation-status-2026-10-23.md` and `architect-rulings-2.md` at hub `main` `7b38ae62`. VERIFIED means the ruling text was read; it does not mean the underlying facts were reproduced.
- REPORTED: stated by an operator message, PR description, worker or reviewer report; not re-run or re-read here. All PR numbers, heads and test counts not found in the files above are REPORTED.
- UNVERIFIED: not established by anyone.

Related: [architect-rulings.md](architect-rulings.md), [architect-rulings-2.md](architect-rulings-2.md), [implementation-status-2026-10-23.md](implementation-status-2026-10-23.md), [mvp-definition.md](mvp-definition.md).

## 0. Overall disposition (VERIFIED, ruling text)

Preserve the October 31 implementation target. Approve a narrowly scoped Runtime repair for terminal approval revocation, correct the overbroad ingress test through independent Qualification review, and exclude Exchange/route C and the unrelated ODES recovery export from the MVP. The controlling principle: distinguish an actual security-invariant failure from an incorrect test predicate; repair the former, amend the latter without weakening its intended control.

The reported results (35/37 `mvp-chain`, 34/35 `mvp-d2-route-b`, 12/12 `mvp-d09`) show substantial progress and do not establish MVP acceptance. Two mandatory failures remain and exact-tuple integration coverage is incomplete. (Results REPORTED; the sentence is the architect's.)

## 1. Rulings 1-8 and dispositions

### 1. NC1-04, approval revocation is not terminal (VERIFIED ruling text)

Ruling A: authorize preparation and execution of the bounded Runtime F3, subject to exact-head review, applicable locked-component gates and the operator gate. Wording discipline: this is "authorize preparation and execution subject to operator gate", not an approval of the patch.
- Revoke, then reactivate, then a committed effect is incompatible with a mandatory terminal-revocation invariant. It is a genuine safety defect for that invariant, not a documentation discrepancy.
- Revocation becomes terminal for the same `approval_ref` within the governed lifecycle. A genuinely new approval, issued through a separately authorized lifecycle, stays distinct from reactivating a revoked reference.
- All nine reported new regressions are retained, including revoke, reactivate, execute.
- Tests cover persistence across process restart, concurrent mutation, effect-time checks and existing grant behavior. Historical evidence is preserved; unchanged profiles must be shown compatible where required.
- Option B (change the mandatory expectation) is rejected: it would change the intended release guarantee after a failure was observed.
- Policy-writer and evidence-writer reversibility are recorded as explicit residual trust-boundary limitations regardless of this repair. Their existence alone does not establish that the supported unprivileged socket client can reach them.
- Mandatory-criteria impact: none. NC1-04 remains mandatory.
- Added effort: an estimated 1.5-2 engineering person-days plus affected requalification and refreeze work, in parallel with the qualification repairs (ruling 2). The Oct 31 target remains; passing independent acceptance by then is not guaranteed.

Disposition: operator approval of the exact Runtime patch and its requalification and refreeze is required before merge; the earlier Replay F3 authorization does not cover it (architect, VERIFIED). Candidate: PR #144 in `cogno-us/cognous-execution-runtime`, head `d291eda7`, REPORTED. No approval is recorded here. NC1-04 stays a FAIL until independently requalified.

### 2. NC4-03, ingress `**` forwarding predicate (VERIFIED ruling text)

Ruling: approve a targeted Qualification predicate correction. The failure concerns a syntactic prohibition broader than the intended property: a fixed-name dictionary comprehension, and a lambda forwarding no client-controlled argument, are not equivalent to an uncontrolled executor parameter.
- Prefer a data-flow and call-boundary predicate over the proposed general exception for dictionary comprehensions.
- The revised test must reject any client-controlled `simulate`, authority-writer capability, operation-identity override or arbitrary keyword reaching a protected executor or claim API, and may permit demonstrably fixed, trusted keyword forwarding.
- Add negative fixtures where `**kwargs` is assembled indirectly (comprehension or proxy) and actually carries prohibited client input.
- Qualification must independently review and freeze the new predicate before its result is used for acceptance.
- Mandatory-criteria impact: NC4-03 remains mandatory; only its implementation-level predicate may change, not the protected property. If the frozen criterion's underlying guarantee would change, explicit operator adoption is required; the expectation is not silently replaced.
- Schedule: target Oct 24-25. No Runtime or ingress architecture change is justified by the reported finding.

Current state (REPORTED): Qualification PR #222 head `72b35623` was independently reviewed CHANGES REQUIRED because the v4 predicate is weaker than v3; it is being revised. The review outcome of the revision is not known here. A predicate that weakens the guarantee is not acceptable under this ruling.

### 3. Verifier limitations and MVP claims (VERIFIED ruling text)

Ruling: confirm narrow claims. Do not state that all remaining V4 checks pass. Pinned Verifier, REPORTED results: 27 of 28 checks confirmed overall, 1 abstention, 0 refutations; V4 subset 4 confirmed, 1 abstained, 2 not applicable; overall exit code 3 (ABSTAIN). An ABSTAIN is not a PASS.
- The Verifier does not independently establish the destination effect outcome merely by confirming Control Plane run-record fields.
- For exit criteria 2 (grant changes and duplicate protection), 4 (UNKNOWN and no blind retry), 5 (Replay and Evidence Pack reconstruction) and 7 (negative controls on the exact candidate), the evidence sources are destination-owned observations, Replay/Evidence Pack reconstruction and independent Qualification controls, as applicable.
- Mandatory-criteria impact: no relaxation; only claim language that overstates Verifier coverage is corrected. Schedule: none beyond the exact-tuple verification.
- Caveat (REPORTED, status record): these numbers came from an assessment that used the $50 fixture, a harness-only `lost_ack` and a local pre-merge commit; it must be regenerated at the exact tuple before any claim cites it.

### 4. Second execute after lost acknowledgement (VERIFIED ruling text)

Ruling: acceptable if UNKNOWN and no-retry semantics remain provable. The second result may be `denied` because the claim is no longer usable; it need not itself be `unknown`, provided the distinct meanings are preserved:
- First attempt: outcome uncertain, `UNKNOWN`, `retry_eligible: false`.
- Second invocation: refused or denied because reuse is prohibited.
- Destination: one committed effect, established by authoritative readback.
- Reconciliation: resolves the original uncertainty without authorizing a duplicate effect.

The second result's default `observed_state: unknown` must not be represented as an authoritative observation of the effect. Qualification should confirm a caller cannot read the second denial as permission to issue a fresh operation identity and retry the same business effect without new authority. No requirement is added that every later response inherit the first attempt's status. Schedule: a focused assertion in the existing battery; no new F3 indicated.

### 5. Exchange / route C and SCN-D09 (VERIFIED ruling text)

Ruling: exclude route C from the MVP execution and qualification profile. The MVP uses Control Plane ingress and route B; route C is not an alternative supported route.
- The five reported failures and the intermittent determinism issue stay in the broader program's defect register; their results are not transferred into the MVP route-B verdict.
- A component in the Hub's broader lock is distinct from one activated or reachable in the frozen MVP profile. Exchange may remain in historical lock metadata, but the MVP's exact candidate manifest must state that it is excluded and not invoked.
- Qualification must verify the exclusion rather than omit the tests.
- Historical SCN-D09 expectations are not modified; a separately frozen MVP applicability mapping is used.
- Route C remediation is off the Oct 31 critical path; the investigation continues post-MVP.

### 6. ODES recovery-bundle export (VERIFIED ruling text)

Ruling: defer. The dropped `recovery_observations` export and four historical ODES failures may remain documented findings if the MVP does not consume that exporter. The selected route must nevertheless preserve correct UNKNOWN, lost-acknowledgment and reconciliation behavior through the actual evidence path. Mandatory-criteria impact: none if the exporter is demonstrably excluded; any applicable ODES schema validation remains required. No MVP implementation work.

### 7. Exact-tuple claim-journal and route-B CI (VERIFIED ruling text)

Ruling: required before independent MVP acceptance. An independently owned Qualification job exercises the complete selected route at the exact candidate tuple, including the new Runtime revision after the F3. The job must execute:
- real claim provisioning in journal mode with operation identity;
- actual route-B synthetic execution;
- grant and approval revocation negatives;
- duplicate-operation and lost-acknowledgment negatives;
- Replay/Evidence Pack reconstruction;
- pinned Verifier execution with exact disposition capture;
- mandatory custody and trusted-host boundary checks.

A mandatory selected test that is skipped, not discovered or not executed prevents a complete acceptance verdict. A declared, justified NOT APPLICABLE result is different from a skipped test. Zero skips is not required across unrelated historical suites; zero unexplained skips is enforced within the frozen mandatory MVP battery. No security requirement is removed. Targets: harness readiness Oct 27, exact-tuple execution Oct 29-30.

### 8. Trusted-host boundary and environment (VERIFIED ruling text)

Ruling: conditionally sufficient for the bounded MVP. The distinct unprivileged UID and socket-only client interface give a defensible restricted profile, not a general hostile-host boundary. The supported environment is frozen as Linux with the exact tested Python 3.13 interpreter and dependency revisions; Python 3.11 is unqualified until separately tested. No platform expansion.

The Qualification environment record must cover nine areas: platform (distribution, kernel, architecture, filesystem type); Python (exact interpreter and dependency versions); process identity (ingress and client UID/GID, ownership); IPC (socket path, owner, group, mode, connection policy); filesystem (database and authority-store paths, ownership, permissions, mounts); invocation (exact supported client entry point, fixed `simulate=None`); isolation limits (effective capabilities, ptrace restrictions, namespace and security settings); configuration (source pins, manifest digests, operation-identity and journal-mode settings); qualification (positive and negative results against the exact configuration).

Non-claims: no resistance to root, the ingress UID, arbitrary same-privilege code or direct database modification by an authorized file holder. If untested ACL or ptrace conditions can invalidate the isolation of the unprivileged socket client, either constrain the profile with enforceable, verified requirements or treat the boundary as unqualified. Target Oct 25-27, in parallel with the Runtime repair.

Current state (REPORTED): hub PR #219 holds the environment record; it is under revision after a CHANGES REQUIRED review. Socket-policy and ptrace decisions remain open.

## 2. Known limitations and defect register

Nothing below is resolved by this record; a failed mandatory control is a failure and is not relabelled.

| Item | Record | Label |
|---|---|---|
| Route C identity mismatch | 5 of 32 cases at Control Plane `7a4bcd40`; raw, unchanged; cause UNVERIFIED. Excluded from the MVP (ruling 5), stays in the broader defect register. | REPORTED |
| Route C determinism flake | Earlier reported at about 1 run in 5; raw, unchanged. A later investigation did not reproduce it in 53 runs, with one unexplained setup failure; this does not close it. | REPORTED |
| Route C re-pin investigation | Exchange branch `repin-cp-7a4bcd40` is local and unpushed; it needs Replay, Evidence Pack and ODES re-ties. Post-MVP; off the critical path. | REPORTED |
| ODES exporter `recovery_observations` drop | `export_cognous_stack_package` fails on Replay bundles with a route B recovery report; pre-existing, reproduced, not fixed. Deferred (ruling 6). | REPORTED |
| ODES historical failures | 4, the same before and after re-pin; not relabelled. | REPORTED |
| Python 3.11 | Unqualified; integration not run. Only Python 3.13 in scope. | REPORTED |
| Runtime CI skips | Runtime CI skips 33 route B tests at pinned Control Plane `2ea9528e`, so the claim-journal fix is not exercised by Runtime CI without a separate pin decision. The exact-tuple job (ruling 7) must cover it. | REPORTED |
| Ingress boundary scope | Holds only for a distinct unprivileged uid reaching only the socket, observed in one configuration. Same-uid, root, shared-uid containers, in-process use, `ptrace`, `DAC_OVERRIDE` are outside it. | REPORTED |
| V4 abstention | Verifier abstains on `v4.ledger.rows-agree-with-attempts`; complete V4 conformance is not claimed. | REPORTED |
| Policy-writer reversibility | Residual trust-boundary limitation. Existence alone does not establish that the unprivileged client can reach it. | VERIFIED (ruling text) |
| Evidence-writer reversibility | Residual trust-boundary limitation (a consistent rewrite of ledger rows and counts moved a Verifier exit 3 to 0 in a probe, REPORTED). Existence alone does not establish that the unprivileged client can reach it. | VERIFIED (ruling text) / REPORTED (probe) |
| `remove_authoritative_state` | Out of scope for the MVP. | REPORTED |
| Superseded fixtures | The $50 fixture and harness-only `simulate="lost_ack"` are superseded for claim purposes; regenerate at the $10 fixture, frozen ingress and merged revision. | REPORTED |
| Pydantic | 2.12 or later required; 2.11.9 gives false Verifier refusals. | REPORTED |
| Replay / Evidence Pack / ODES reconstruction through the live ingress on the merged tuple | Not established. | UNVERIFIED |

## 3. Critical path, Oct 24-31 (VERIFIED, architect's phases)

These dates are execution targets, not verified completion dates. They depend on successful Runtime F3 review and refreeze. The Oct 31 implementation target is viable but at risk, and passing independent acceptance by then is not guaranteed.

| Phase | Targets |
|---|---|
| Oct 24-25, parallel repairs | Runtime F3 preparation and operator authorization; Qualification NC4-03 predicate correction (Oct 24-25); trusted-host environment freeze (Oct 25-27). |
| Oct 26-27, integration | Runtime exact-head review, CI and merge if authorized; dependent pin reconciliation; mandatory exact-tuple job operational (harness readiness Oct 27). |
| Oct 28-29, qualification execution | Full selected battery: NC1-04, NC4-03, actual claim issuance, negative controls, Replay/Evidence Pack reconstruction (exact-tuple execution Oct 29-30). |
| Oct 30, candidate reconciliation | Address candidate-specific failures, finalize revision pins, preserve historical results, produce the implementation evidence inventory. |
| Oct 31, implementation cutoff | Report separately: code completeness, exact candidate identity, independent qualification status, remaining blockers. |

Off the critical path: route C remediation, the ODES exporter, Python 3.11. On it: items 1, 2, 7, 8 (item 4 uses existing tests; item 3 needs no extra implementation). Ruling 1 adds an estimated 1.5-2 person-days plus requalification and refreeze.

Do not attempt to recover schedule by changing NC1-04 from FAIL to a known limitation after observing the result. The fastest defensible path is one bounded Runtime repair, one independently approved test-predicate correction and one exact-candidate qualification run.

## 4. What this record does not do

It does not approve PR #144, accept PR #222 or #219, change the component lock, a locked component or an acceptance criterion, or declare a Qualification outcome.

Release, publication and production remain on HOLD.
