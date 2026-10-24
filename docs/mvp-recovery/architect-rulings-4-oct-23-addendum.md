# Architect rulings #2 of 2026-10-23 (hub record "rulings 4")

Status: non-authorizing record. Release, publication and production remain on HOLD. Nothing here is a Qualification verdict, an independent acceptance, a security clearance, a certification or a production-readiness claim. The builder cannot self-certify. Qualification owns oracles and verdicts.

This file is a record and summary of the architect's document "OCS MVP — Architect rulings #2" (October 23, 2026). The architect's original text controls over this summary. Relation to the earlier file: [architect-rulings-3-and-known-limitations.md](architect-rulings-3-and-known-limitations.md) (merged via #220) records the earlier, same-date rulings set (items 1-8); this file records the later "rulings #2" document of the same date. The numbers 3 and 4 are hub file numbering only.

Related: [architect-rulings.md](architect-rulings.md), [architect-rulings-2.md](architect-rulings-2.md), [implementation-status-2026-10-23.md](implementation-status-2026-10-23.md).

## 0. Disposition

Date: October 23, 2026. Target: implementation complete October 31. Status: Bounded engineering authorization; independent acceptance pending. Release, publication and production: HOLD.

Proceed toward October 31 without reopening the broader OCS v0.2 program. No mandatory acceptance criterion is removed.

Principal decisions, as stated:
- Approve Runtime F3 #144 within the reported scope, including terminal `revoked -> unknown` treatment.
- Do not adopt NC4-03 v4 unchanged. Its AST pins are useful, but the unguarded origin of `claim_id` and other authority-bearing fields needs correction.
- Freeze a dedicated-group Unix socket profile, with a non-root ingress and verifiable ptrace restrictions.
- Accept direct executor tests as component evidence, but require one supported-ingress ambiguity test for the complete MVP behavior claim.
- Require independent Qualification ownership and freezing of the mandatory battery before its results count as acceptance.
- Keep route C and ODES recovery-export repairs outside the October 31 critical path.

## 1. NC4-03 adoption: conditional, not as currently written

The v4 predicate is more precise than v3's blanket prohibition on non-literal `**` forwarding. The blanket rule is not itself the security invariant; preventing untrusted inputs from reaching protected executor parameters is. Changing the detection mechanism is therefore an implementation-level correction, provided the protected guarantee is unchanged.

v4 has two limitations:
1. The three exact-hash pinned sites are acceptable only if Qualification has independently established their data provenance and call-boundary behavior.
2. The generic comprehension exception for arbitrary `obj` is too broad. A literal list of field names does not establish that the values are trusted.

Ruling: retain AST-normalized pins for the three specifically reviewed sites, but restrict the comprehension exception to a verified trusted source or remove that exception. Do not require wholesale refactoring merely to eliminate `**`.

Every pinned exception must record its source revision, expected AST digest, trusted input origin and protected destination. A changed semantic AST invalidates the exception.

Mandatory acceptance: NC4-03 remains mandatory. Qualification must independently approve the corrected predicate before freezing it.

Schedule: target the correction and review by October 25. No new architectural workstream.

## 2. NC4-03 residual R1: fix before freeze

Ruling: an origin rule is required. The six fields `claim_id`, `grant_id`, `grant_revision`, `effective_max_effects`, `authority_context_id` and `requested_permissions` are sufficiently authority-sensitive that arbitrary client substitution would undermine the trusted-ingress claim.

Source-bound provenance is required at protected calls:
- `claim_id` must originate from the governed claim selected by the trusted execution path.
- Grant identifiers and revisions must originate from the applicable authoritative decision or grant snapshot.
- Effect limits and requested permissions must be derived from the authorized operation, not replaced by client inputs.
- `authority_context_id` must be bound to the selected trusted authority context.

Use the smallest reliable implementation: explicit assignments or a bounded source-aware test, whichever yields a reviewable guarantee. Do not require a general-purpose taint-analysis framework.

The unpinned `claim_id` in `core._run` is the immediate regression target. Add a negative mutation where a client-provided claim identifier reaches execution; the frozen criterion must reject it.

Mandatory acceptance: no change to the protected guarantee. This closes a gap in the proposed test rather than introducing an optional requirement.

Schedule: parallelize with Q1; target completion by October 25-26.

## 3. Runtime F3 #144: approve

Ruling (a): terminal handling of `revoked -> unknown` is within Option A. It enforces the same terminal-revocation invariant and is compatible with the approved grant-parity objective.

Ruling (b): accept the reported owner-level removal/reprovisioning limitation for the restricted trusted-host MVP, subject to independent boundary verification.

The guarantee must be scoped accurately:

> An approval revoked through the governed Runtime lifecycle cannot be reactivated under the same approval reference to authorize an effect.

Do not claim resistance to an authorized database owner deleting or rewriting state through `remove_authoritative_state`, raw SQL or equivalent administrative operations.

Record policy-writer and evidence-writer reversibility separately. A one-time migration is not required for this synthetic MVP unless qualification demonstrates an applicable same-profile bypass.

Operator authorization (architect text): "The exact behavioral package is approved for the reported candidate PR #144, head `d291eda7`, based on the review evidence supplied. Any materially different implementation requires renewed scope review. Merge remains subject to required CI, independent review and applicable repository protections."

Mandatory acceptance: NC1-04 remains mandatory. A component-local PASS is not the independent MVP verdict.

Schedule: proceed with merge and cascade promptly; no further routine approval checkpoint for the exact approved package.

Head facts (verified with the GitHub API, 2026-10-24). The approved head named in the architect's authorization is `d291eda7`. Runtime #144 was merged at head `ee1ff55c250455a3bb14939ca0ce10aeeac70ccb` (merge commit `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f`, 2026-10-23). The compare `d291eda7...ee1ff55c` shows one commit changing one test file, `tests/test_atomic_approval_status_terminality.py` (+3 lines, a `pytest.importorskip("agent_control_plane.bounded", ...)` guard). `engine/local_authority_effect.py` has git blob `6b1319448a8d51dc865c7e3613f83cfb4bd87a58` at both heads. The merge proceeded under the ruling "Proceed with merge and cascade promptly; no further routine approval checkpoint for the exact approved package." #144 is cited as merged, not as qualified.

## 4. Environment profile: approve restricted Linux configuration

4(a) Socket ownership: choose `0660` with a dedicated group containing only the ingress and designated client identities. The socket must reside in a separate IPC directory that the client can traverse, not the ingress-owned `0700` state directory. The parent directory must prevent unauthorized replacement of the socket. Verify effective permissions, group membership and peer credentials rather than relying solely on the declared mode. Do not use client ownership of the socket as the default; it would unnecessarily grant the client control over a security-relevant filesystem entry.

4(b) ptrace: require `kernel.yama.ptrace_scope >= 1` for the proposed Linux qualification profile, alongside verification of effective capabilities, dumpability and process identity. This setting alone does not establish complete process isolation. If Yama is unavailable, the exact profile is unsupported and the boundary test is BLOCKED. Do not silently substitute a weaker environment.

4(c) non-root ingress: mandatory. The ingress must run under a dedicated non-root UID without unnecessary privileged capabilities. The qualification environment must capture the actual ingress and client identities, not stand-in values.

Mandatory acceptance: NC4 boundary controls remain mandatory; the environment constraints are preconditions for the selected profile.

Schedule: update hub PR #219 and conduct the actual-host capture by October 26. Environment evidence must be refreshed if the execution host or relevant settings change.

## 5. Lost-acknowledgment evidence: require a supported-path test

Ruling: direct executor tests are valid component evidence, but insufficient alone for the complete ingress-to-effect claim.

The test harness may use `simulate="lost_ack"` to demonstrate executor UNKNOWN and no-blind-retry behavior. The supported ingress, however, fixes `simulate=None`, so that test does not establish end-to-end ambiguity handling through the advertised interface.

Require one controlled owner-side fault-injection test through the real ingress that produces an ambiguous acknowledgment without allowing the unprivileged client to choose `simulate`. The test must demonstrate:
1. A supported proposal reaches the actual execution boundary.
2. An acknowledgment becomes unavailable after an effect attempt.
3. The system retains UNKNOWN rather than assuming no effect.
4. Reuse cannot cause a second effect.
5. Reconciliation establishes the destination-owned outcome where possible.

Keep fault injection in the trusted qualification harness, not the production-facing request schema.

Mandatory acceptance: preserve the UNKNOWN/no-blind-retry criterion. Distinguish executor-level evidence from supported-ingress evidence in the result.

Schedule: target October 27-29. Use the existing harness and smallest deterministic interception point; do not build a general fault-injection subsystem.

## 6. Qualification job governance: confirm

Ruling: Qualification must independently own, review, freeze and anchor the mandatory battery, the applicability mapping, the gate expectations, and the exact candidate tuple and supported environment.

The existing anchors to expectations v1-v3 and `test_scn_d09.py` do not establish immutability of the new three files. Add those files to the qualification-controlled source commitment before an acceptance run. A later change must produce a new versioned qualification candidate, not silently replace the original expectations.

Python 3.12: the workflow must use Python 3.13 for the frozen environment. A 3.12 result is supplementary and cannot qualify the 3.13 profile.

The builder may submit the proposed files and assist with failures, but independent Qualification must accept the test design and own the resulting verdict. Reviewer approval of builder code does not, by itself, establish oracle independence.

Mandatory acceptance: no relaxation. The exact-candidate gate must refuse uncommitted mandatory tests, unexplained skips and environment mismatches.

Schedule: target Qualification freeze by October 27, then run the final candidate after the Runtime cascade.

## 7. Post-MVP defects: defer

7(a) Route C / Exchange: prefer a new versioned P2 profile if the revision change alters committed behavior, compatibility requirements or existing profile identity semantics. An in-place pin update is acceptable only if independent compatibility evidence shows that it preserves the existing profile contract. Route C remains excluded from the MVP. Assign the Exchange/Replay/ODES owners a post-MVP compatibility investigation; do not start another refreeze now.

7(b) ODES recovery exporter: keep `recovery_observations` as a documented post-MVP defect owned by ODES, with Replay and Evidence Pack participating only where their respective records require it. Do not imply complete recovery-bundle export support in MVP claims.

Mandatory acceptance: no change. Qualification must verify these features are excluded from the selected MVP path.

Schedule: zero additional MVP-critical work.

## 8. Schedule: confirm, with a HARD SCOPE CUTOFF

Retain October 31 for implementation completion, but prioritize the actual security and qualification dependencies over documentation and deferred compatibility work.

| Deadline | Critical deliverable |
|---|---|
| Oct 24-25 | Runtime #144 reviewed/merged; NC4-03 predicate and origin corrections completed |
| Oct 26-27 | Runtime pin cascade, actual Linux environment capture, frozen independent Qualification criteria |
| Oct 28-29 | Supported-ingress ambiguity test and complete exact-tuple mandatory battery |
| Oct 30 | Repair candidate-specific failures; reconcile final pins and evidence |
| Oct 31 | Implementation cutoff, frozen candidate and independent qualification status |

If the cascade slips, reduce work in this order:
1. Stop all route-C and ODES recovery-export investigation.
2. Park nonessential documentation and dashboard enhancements.
3. Defer supplementary portability, Python 3.11 and unrelated profile testing.
4. Defer performance optimization and optional observability enrichment.
5. Reduce redundant developer test executions where exact-head required CI already supplies equivalent evidence, without removing independent mandatory tests.

Do not cut NC1-04, NC4-03, supported-path mediation, duplicate-effect prevention, UNKNOWN/reconciliation behavior or the exact-candidate acceptance battery.

The additional cascade estimate of 1.5-2 person-days is plausible as a working estimate, not verified elapsed time.

### Standing execution instruction

The workers are authorized to continue the approved Runtime F3 and dependent compatibility cascade autonomously. They should review, repair, rerun and merge eligible changes without repeatedly seeking operator permission, provided they preserve independent review, required checks and repository protections.

Qualification retains its independent authority. Changes to mandatory criteria require its own review and freeze, with operator escalation if the underlying safety guarantee changes.

Next priority: merge the exact Runtime repair, correct the NC4-03 provenance gap, freeze the actual Linux/Python 3.13 profile and execute the complete mandatory battery.

The October 31 deadline remains an engineering target. A failed mandatory control remains a failure regardless of schedule. Release, publication and production HOLD remain unchanged.

## 9. Implementation state as of this PR

Checked with the GitHub API on 2026-10-24.

- Runtime #144: merged, `c5e97e87dd239c821b1b4a406a55dcd03c5bc61f`, head `ee1ff55c250455a3bb14939ca0ce10aeeac70ccb`; approved head `d291eda7` (see the head facts in section 3). Merged under the ruling; not qualified.
- Hub #219: open, not a draft. Current head `b35957d0` is only a sync of `main` into `0e2b52a0` (compare `0e2b52a0...b35957d0` shows the merged #220 commit and a merge commit). There are no GitHub reviews on it; the independent review approving `0e2b52a0` was reported by worker agents and is not independently confirmed here.
- Qualification #222, #223 and #224 (repo `cogno-us/cognous-stack-qualification`; the hub has its own, different PR #222, which is the PR carrying this file): open drafts, Qualification-owned, with builder-side reviews reported. They are not frozen and not accepted. Qualification #224 is stacked on the branch of Qualification #223.
