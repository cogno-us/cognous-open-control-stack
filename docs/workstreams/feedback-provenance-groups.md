# Feedback B: declared provenance groups

## Baseline and scope

Hub baseline: `649df22a1392af2c4fa77e4c71749c482f82649c`.
Source: Moltbook feedback addendum B (2026-10-07), F4, read with
Addendum A E8. This is design critique, not market-demand or independent
assurance evidence. Full private source text is not included here.

The selected Evidence Pack revision `b4baccd823d2a73be276c1de745b19cf7c56a0d6`
was inspected in `src/agent_governance_evidence_pack/models.py` and `summary.py`.
Its summary counts bundles, actions and review records; that inspected summary
has no failure-relative provenance grouping. This is a new standalone hub
reference contract, not a modification to or qualification of that consumer.
No repository AGENTS.md was present at the hub baseline.

## Contract

`reference_profiles/provenance_groups.py:summarize` accepts
`declared-provenance-groups/1`. Packet fields are exactly `contract`,
`claim_ref`, `scenario_ref`, `failure_axes`, `basis_ref`, and `receipts`.
The basis reference names the review that selected failure-relevant axes; it
is a declaration, not an authenticated or validated review.

Each receipt declares a unique `receipt_id` and `dependencies` containing all
six axes: `data_snapshot`, `model_version`, `policy_version`,
`retrieval_lineage`, `tool`, `provider`. Each value is a nonempty list of exact,
canonical dependency references, or null when unknown. Model seed and receipt
identity are not independence criteria. Version and issuer namespaces must be
included by the producer where needed to identify a dependency exactly.

Grouping is relative to the packet's explicit, nonempty failure axes. Sharing
any selected dependency connects two receipts; transitive overlap joins the
same group. Thus 100 workers reading one cache give one declared dependency
group, not 100 independent witnesses. Two distinct snapshots produce two
additional groups only when no selected dependency connects them. Selecting
a shared provider as relevant can collapse all three groups.

Receipts missing any selected lineage enter `unestablished_receipts` and
contribute no group. Unknown unselected dependencies still preclude an
independence claim. Different labels can disguise the same source; this
contract cannot resolve aliases, authenticate references, verify the choice
of relevant axes, or discover concealed common causes. Choosing fewer axes
can change the result and must not be treated as increasing assurance.

Output always says `independence: not_established` and
`authorizes_action: false`. `declared_group_count` is structural bookkeeping,
not witness weight, probability, corroboration, truth or verification. There
is deliberately no pass, approval or independent-witness-count field.
The function preserves its input and produces deterministic ordered results.
Effect identity and settlement ledgers remain entirely separate.

## Acceptance and integration boundary

Run `python -m unittest discover -s tests -p test_provenance_groups.py -v`.
Twelve focused tests cover the 100-worker example, shared provider collapse,
transitive lineage, missing lineage, invalid/duplicate entries, stable output,
and empty populations. These tests establish the local contract only.

Future Evidence Pack adoption requires versioned schema/importer/renderer
mapping, producer lineage capture and authenticated or independently examined
source dependencies. E8 claim narrowing and falsifier provenance still need
separate review. This module is not included in the shared v1 release evidence
population and does not advance accepted component pins.

## Remaining feedback B acceptance matrix

| Source item | Current disposition | Required next evidence |
|---|---|---|
| A-E1 | Partially addressed by existing separate refund-intent profile; no new closure | Exact-revision config/authority update plus lost-ack qualification with trustworthy upstream intent identity; no competing purpose registry |
| A-E2 | Historical finding requires current component verification | Persisted integrated refusal with reason, effect and observed versions; minimized protected payload references marked as data |
| A-E5 | Adapter integration remains open | Distinguish in-flight request finality from read visibility and declared dedupe retention; unknown bounds cannot become guessed retry authority |
| F1 | Runtime refusal/hold binding remains open | Hold retains observed authority stratum, causal reconsideration inputs and current-authority re-evaluation; reconsideration itself is not authorization |
| F2 | Runtime escalation remains open | Exactly bounded re-reads, named escalation, retained denominator and no effect; a configured guess is not an authoritative lag bound |
| F3 | Observation/renderer contract remains open | Separate coverage from consistency; unbounded observations cannot carry an absence verdict |
| F4 | Standalone structural contract proposed here | Consumer integration and independent lineage assessment remain unqualified |
| F5 | Design-only | External append-only anchor and trust model; local insertion order or shared-secret HMAC is not an independent witness |

The historical source's expected failures were not rerun by this batch and
are not asserted as present defects. Open hub PRs #32–#36 were inspected for
scope: deployment evidence, institutional review, restore, context admission
and temporal qualification. This batch edits none of their files or shared
README/register/workflows. Executor PRs #29–#31 remain untouched.
