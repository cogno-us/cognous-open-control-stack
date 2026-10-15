> Historical S1 evidence at d577b11a, preserved unchanged below. For the S0 follow-on diagnostic scope see [S0 checkpoint](s0-component-repair-2026-10-15.md). No current qualification is inferred from this historical record.

# S1 / candidate-integration lane A: nonselected hardening candidate

**Disposition: BLOCKED. This candidate is not qualified for selection.**
`reference_release_authorized=false`; `production_deployment_authorized=false`.
Operational trust remains **HOLD / NOT ESTABLISHED**. This work prepares evidence
for a separate selection decision and grants no release permission.

## Live-source verification and smallest candidate

Hub main was fetched and rechecked as
`592919dd95396f3f6164cf0ceec1fd15c065691b`. This is the branch base. Repository
contribution/security instructions, existing profiles, component-lock, remediation
and publication-acceptance reports were read. No root AGENTS.md was present.
At initial inspection the only open hub PR was #117 (external-reference docs).
No existing profile, component-lock or reference-release runner was edited.

GitHub reported [Control Plane #31](https://github.com/cogno-us/cognous-control-plane/pull/31)
merged at `c7f122ba3a6e39f9268a7163c99be3ee514cd97e` and
[Governed Exchange #22](https://github.com/cogno-us/cognous-governed-exchange/pull/22)
merged at `6ea048e7189724e1f7563954db50838e1ce83d62`. Actual merged trees were
read and executed; PR-body test counts are not reused as S1 execution evidence.

| Component | Candidate commit | Interface exercised |
| --- | --- | --- |
| Manifest | `46c950bed37fe3812000895430bc0312d29e37ce` | Manifest 1.1 fixture |
| Control Plane | `c7f122ba3a6e39f9268a7163c99be3ee514cd97e` | bounded-authorization-effect/0.1; durable resolution inputs/refusals/checks, closeouts and service clock |
| Executor | `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac` | Execution Envelope 0.2.0; producer 2.0.0; PinnedControlPlaneExecutor; DurableRefundDestination |
| Governed Exchange | `6ea048e7189724e1f7563954db50838e1ce83d62` | retained artifacts 1.1.0; merged-producers-v1; persistent store-local effect ownership |
| Replay | `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa` | Reconstruction Bundle 0.2.0; import_bounded_workflow |
| ODES | `c5e9a0f3695ae836b803be06c46d2c669642ee03` | implementation profile 0.2.1; export_cognous_stack_package |
| Evidence Pack | `b4baccd823d2a73be276c1de745b19cf7c56a0d6` | imported schema 0.2.0; transformation 0.3.2; build_evidence_pack_from_artifacts |

Only Control Plane and Exchange differ from the selected core chain. A compatible
set incorporating the fixes was **not** found: keeping other pins exposes the
smallest migration surface, rather than claiming compatibility.

Before choosing these pins, current executor main
`392db8c88de6e05f2d5410510049c1eea15bc3fe`, Replay main
`1d0abca3a0c62220a5cf509c4eddaeb3a7cf73c6`, Evidence Pack main
`1304a91b373aab6ea566a923167bff124bc495b3`, and ODES main
`ff029fd1ec6f6e06b9e2d1d111e8acaab65dd14d` were inspected. The newer optional
atomic/C8/recovery interfaces do not add the required bounded refusal integration;
the current executor still has the same generic bounded refusal path. These newer
heads were inspected, not integration-tested or selected. No unrelated optional
feature was added. This is the historical C0 interface, not tenant 0.2 or C1 adoption.

## Method and actual results

The opt-in harness verifies clean exact checkouts, imported module file locations,
and the non-authorizing manifest before executing. It invokes actual component
classes, stores, importers and exporters. Synthetic resolver inputs and fault/clock
injections are declared. The service `_now` clock is fixed to the dated public
fixture at 2026-08-08T01:00:00Z; this does not qualify trusted time.

Two local repetitions each produced **23 raw JUnit testcase elements: 13 passed,
10 failed, 0 errors, 0 skips**. There are **0 unittest subtests**. Parametrized
cases each have their own testcase. Both commands exit 1, and
`candidate_integration_passed=false`. No failures are xfailed or converted into
successful qualification. Named assertion outcomes repeat across runs; random
record identifiers and artifact bytes are not claimed byte-repeatable.

| Case | Actual outcome |
| --- | --- |
| Denied destination; schema mismatch | Decision holds with target_out_of_scope / missing_required_payload_field; zero effects and zero attempts; actual policy/grant/evidence projections retained by CP |
| Stale required context | Context evidence state stale with hold_effect; context_unknown_requires_hold; zero effects |
| Principal self-approval | approval_independence_violation; zero effects |
| Unsupported delegation | delegation_profile_unsupported; zero effects |
| Approve then revoke before dispatch | Executor denies, zero effects; CP durable refusal includes grant_not_active, original decision/effect lineage and actual resolution inputs; executor evidence is empty |
| Approval withdrawal; policy change; evidence stale after approval | Zero effects; CP retains approval_not_active / policy_version_changed / required_evidence_not_current; same executor/consumer propagation blockers |
| Positive infinity; negative infinity; NaN | Three separate schema rejections with finite_number; no decision, attempt or effect; no fabricated policy/grant evidence from inputs never read |
| Unsupported human override | Claimed metadata does not authorize; unsupported keyword rejected; ordinary execution of held decision denied; zero effects. No supported attributable override transition demonstrated |
| Lost acknowledgement and reopened-store redelivery | First result unknown with acknowledgement false; actual SQLite already has one effect. New workflow/store/destination instances reconcile the same effect without a new effect; authoritative destination rows unchanged |
| Second message claiming unresolved effect | First checkpoint unknown and destination empty; second message not attempted, effect_owned_by_another_message, original owner retained, one durable claim refusal; zero effects |
| Exchange post-dispatch crash checkpoint and redelivery | One committed effect remains one. Redelivery export raises ODES status-reconstruction mismatch; no completed exchange consumer response. This is an integration failure |
| C0 revoke inside revalidation-to-commit interval | Revoked authority still produces one effect. Characterization confirmed; safety_success=false. This is a remaining unsafe race, never a safety success |

Restart tests recreate workflows and reopen durable stores after injected faults.
They do not kill an OS process or simulate host power failure. No distributed
fence, business-intent deduplication, real settlement or operational acceptance is
established. Optional same-host cooperative C1 limitations remain; no C2/C3.

## Concrete compatibility gaps and field disposition

1. **Executor drops the durable effect-time refusal.**
   `PinnedControlPlaneExecutor.execute` catches the CP PermissionError and returns
   `error="authorization-critical inputs changed before effect"` with
   `control_plane_evidence={}`. Decision/effect IDs remain in the result, but typed
   reasons and their actual bindings are absent. The producer exports that empty
   evidence without repairing it. The four refusal tests fail explicitly here.
2. **Replay rejects actual CP revision.** Calling `import_bounded_workflow` with
   the exact new commit yields `unsupported Control Plane revision`. All five
   decision-refusal consumer tests and four effect-refusal tests retain that
   actual exception. ODES/Evidence Pack are then marked **not invoked: no
   exact-revision Replay record**; they are not passed dummy artifacts.
3. **GAX assigns historical provenance to new source.** The supported
   `merged-producers-v1` branch still declares CP `d3dadee7...`. Actual exported
   Replay profiles consequently claim that historical revision while executing
   `c7f122ba...`. No hub constant/allowlist is patched to conceal this mismatch.
4. **New top-level CP data is discarded by the historical importer.** Under
   GAX's own declared labels (diagnostic evidence only; provenance_valid=false),
   Replay emits B001 unmapped_field findings for `refusals`, `resolution_checks`,
   `input_time_floors`, `closeouts`, and returns reconstruction_partial.
   Decision records retain their raw reasons/resolution_inputs, but the
   effect-time refusal is a different record and is not retained this way.
5. **Actual downstream consumers reject the diagnostic Replay.** ODES raises
   `retained Replay status differs from accepted validator reconstruction`;
   Evidence Pack raises `pinned Replay semantic validation failed unexpectedly:
   retained Replay status differs from accepted reconstruction`. Their extraction
   reconstructs older inputs without the new top-level data that caused Replay's
   partial status. No downstream assurance record is produced. Diagnostics retain
   raw Replay, both actual exceptions and original checkpoints separately.

The full missing refusal field set is `refusal_id`, `decision_id`, `effect_id`,
`recorded_at`, `time_source`, `original_operation_horizon`, `operation_horizon`,
`stage`, `reasons`, `changed_inputs`, `resolution_inputs`. Each horizon has
`source`, `proposal_commitment`, `not_before`, `expires_at`. Each changed input has
`input_type`, `input_id`, `expected_version`, `observed_version`. Each resolution
input has `input_type`, `input_id`, `expected`, `observed`, `record_commitment`,
`missing`, `previous_observed_at`. All these refusal-specific values are missing
from the executor evidence; duplicated top-level decision/effect IDs are not a
replacement for the refusal record. Each consumer diagnostic includes a
runtime-derived interface_inventory of these fields.

The discarded resolution-check fields are `check_id`, `stage`, `evaluated_at`,
`time_source`, `inputs`, `reasons`; input projections have the fields above.
Discarded closeouts have `attempt_id`, `effect_id`, `original_status`,
`observed_state`, `observed_at`, `reconciled_at`. `input_time_floors` is the actual
input-to-observed-time mapping. Absence/null remains absence/null. Nonfinite
schema rejections and held decisions have no authorized envelope; none is invented.

## Minimal reproductions and proposed owning-repository patches

Run from the hub with Python 3.12 and Git:

```bash
python -m pip install --require-hashes -r tools/requirements-release.lock
python tools/remediation_candidate.py --prepare-work --work /tmp/s1-components --out /tmp/s1-evidence
```

The second command must currently exit 1. `/tmp/s1-evidence/summary.json` names
individual testcase failures; each scenario saves checks before asserting.
`run-1/effect-revoke/` is the minimal executor refusal reproducer;
`run-1/consumer-decision-denied-destination/` reproduces exact-revision rejection;
`run-1/exchange-crash-provenance/` reproduces misleading provenance and downstream
export failure. `run-1/second-message-unresolved/` shows ownership still prevents
replacement dispatch even when first export failed.

Proposed patches for the coordinator, **not applied in S1**:

- **cognous-execution-runtime / engine/control_plane_adapter.py**: extend the
  existing per-call `_ReconciliationCapture` to capture `append_refusal` after
  successful durable write, exactly like append_reconciliation. In the
  PermissionError branch copy that call's actual refusal into
  `result.control_plane_evidence['refusal']`. Do not re-resolve or scan unrelated
  concurrent refusals, synthesize a reason, or issue an authorization binding.
  Minimal shape:

  ```python
  # _ReconciliationCapture.__init__
  self.refusals = []

  def append_refusal(self, value):
      self.records.append_refusal(value)
      self.refusals.append(value)

  # execute's PermissionError branch, after constructing denied result
  if records.refusals:
      result.control_plane_evidence['refusal'] = records.refusals[-1].model_dump(
          mode='json', exclude_none=False)
  ```

  Producer export tests must require unchanged reason/binding lineage through the
  actual public interface, including storage-write failure and concurrent calls.
- **cognous-replay-bundle / importers.py**: add an explicitly qualified revision
  profile for CP c7f122ba and the resulting executor commit. Import typed refusals,
  resolution checks, time floors and closeouts as non-authorizing source evidence,
  preserving all fields above and their actual decision/effect/input namespaces.
  Reject inconsistent bindings and future unknown fields with explicit loss.
  An allowlist-only change is insufficient.
- **open-decision-evidence-standard / exporter.py** and
  **cognous-governance-evidence-pack / importer.py**: extend exact compatibility
  and source extraction/revalidation for that same profile. Reconstruct actual
  new fields so partial/complete status and source commitments agree. Retain typed
  refusal reasons and actual read bindings, without promoting evidence to authority.
  Do not fix by suppressing status comparison or dropping unknown-data warnings.
- **cognous-governed-exchange / gax_ref_runtime.py**: introduce an explicit opt-in
  candidate compatibility profile with exact qualified CP/executor/Replay/ODES/
  Evidence Pack pins. Export truthful producer provenance; retain failure/export
  state and original ownership across retries. Do not redefine merged-producers-v1.
  Re-run unresolved-owner and post-dispatch recovery cases after consumer migration.

The next action is coordinator-owned upstream executor/consumer contract repair,
followed by new merged pins and this same candidate qualification. S1 does not
modify any owning component or another worker's path.

## Evidence and hosted CI handoff

The workflow `S1 nonselected remediation candidate` checks out the PR's actual
head (not its synthetic merge), runs two repetitions, and uploads
`s1-candidate-<exact-head>` even when the integration gate fails. The PR handoff
records the exact final head, hosted run URL, outcome and artifact digest after
inspection; this document does not preclaim a hosted result.

Artifacts contain `candidate.json`, `environment.json` (actual pins, imported
source hashes, Python/dependency versions, hub HEAD, dependency-lock hash),
`summary.json`, `sha256.json`, and per-run `junit.xml`, raw execution logs,
`junit-inspection.json`, expected/observed `checks.json`, CP sources, real SQLite
state/checkpoint stores, executor records and actual consumer diagnostics.
`sha256.json` hashes every other retained artifact; it cannot hash itself.
All published data is generated from public synthetic fixtures; no live grants,
credentials, external messages, private method internals or customer data are used.

Only the five assigned new paths are owned. Selection, release/tag, announcement,
production effects and OpenAPPA/reasoning-protocol functionality remain outside S1.

Local precommit working-tree evidence (source file hashes identify the tested inputs;
base HEAD alone does not identify uncommitted changes):

| Retained file | SHA-256 |
| --- | --- |
| `s1-evidence-precommit/run-1/junit.xml` | `82fd3d158d00b2ecb26554dda2b608a9e03773e7e8cb72a1809f3d07e9873e76` |
| `s1-evidence-precommit/run-2/junit.xml` | `32a5606ae390843fe4cd13e801d26861a43f26342949b11504d872ec14baebf5` |
| `s1-evidence-precommit/summary.json` | `348e1c770f47a22cd9f6e55d58033e4c449f882fb4ae6cd47301535647199485` |
| `s1-evidence-precommit/sha256.json` | `fd013406bfc02b3f9c7cff77677eba3a9c8787543eabf79ea28f06e64e364f8d` |

Final-head local/hosted evidence is recorded in the PR handoff, with its own hashes.
