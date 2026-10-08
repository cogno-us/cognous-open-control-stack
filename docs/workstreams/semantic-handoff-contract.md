# Semantic handoff reference contract

This opt-in checker partially addresses SH01 from the semantic handoff and viable
oversight addendum. It checks structural agreement on an exact bounded contract.
It does not verify semantic truth, authenticate parties, observe an effect,
issue authority, or qualify deployed oversight.

## Contract and use

`tools/semantic_handoff_contract.py` exposes `commitment(contract)` and
`check_acceptance(proposal, response, *, current_commitment,
current_context_generation, now)`. The caller supplies the current authoritative
contract commitment, context generation and timezone-aware trusted clock. These
inputs are trust assumptions, not assertions proven by this checker.

The `semantic-handoff/1` contract requires sender, receiver, tenant, task, parent,
operation, goal, versioned domain dictionary reference, positive revision, context
generation, UTC deadline, read/write scopes, preconditions, completion criteria,
evidence requirements and restrictions. A root task uses an explicit root marker.
Each domain term has a unique name, finite number or nonempty text value, unit,
namespace, time basis and uncertainty description. Use explicit `not-applicable`
descriptions where appropriate; omitted interpretation metadata is invalid.
Domain validators remain necessary: a string that says `USD` does not establish
that the currency is correct, and text dates inside domain terms require their
own typed domain validation.

The receiver response identifies the proposing parties in reverse, the exact
proposal commitment, response kind, interpretation and mapping. Only identity
normalization is supported. The mapping records a version, both dictionary
references and explicit lost/unresolved meaning lists. Meaning loss remains
pending; a changed interpretation requires a new proposal. No automatic unit
conversion, ontology translation or model inference is performed.

Canonical SHA-256 includes every contract field and list in order. Reordering
object keys preserves the commitment; changing a revision, restriction, context,
term or scope changes it. A stale response is blocked. Caller-reported supersession
or changed context blocks acceptance. The deadline is exclusive: equality defers.
Rejected, pending, deferred, blocked and accepted are distinct states. Transport
acknowledgement, clarification, progress and completion assertions cannot become
acceptance. Even `accepted` returns `authorizing: false` and `observed_effect: false`.

## Integration and migration limits

This is a new optional reference contract with no migration of existing runtime
records and no accepted pin change. It does not dispatch or replace Manifest,
Control Plane, exchange, Replay or Evidence Pack contracts. A host adopting it must
first adopt a domain schema and mapping through the existing competent authority.

The checker is pure and has no persistent clarification state, attempt budget,
queue ownership, delivery deduplication, durable audit log, authentication,
revocation feed or dispatch transaction. Repeated clarification remains pending;
that fixture does not establish durable duplicate handling. Protected dispatch
must still revalidate the current contract, context and ordinary execution
authority at its own boundary. Acceptance cannot close a time-of-check/time-of-use
gap. Required completion evidence must be evaluated independently.

SH02 durable capacity admission and timely review, SH03 intervention/control
assignment evidence and SH04 deployment-specific agent dimensions are **not
implemented** here. They require separate owned contracts and acceptance evidence.
An assigned reviewer does not establish available capacity; a named intervention
owner does not establish effective control; a capability profile grants no rights.

## Qualification checkpoint

Starting main: `649df22a1392af2c4fa77e4c71749c482f82649c`.
Inspected open hub PRs #32–#36; this batch adds only new checker, test, workflow
and documentation files, leaving their ownership and shared gate counts intact.
No executor PR, accepted lock, shared workflow, README or engineering register is
changed. CONTRIBUTING's public-safe hub scope is preserved by keeping this an
opt-in checking tool rather than a new runtime service.

Run the bounded standard-library suite:

```bash
python -m unittest discover -s tests -p test_semantic_handoff_contract.py -v
```

Local result: 18 tests passed. The tests cover unit/namespace/time/uncertainty
mismatches, dropped restrictions, changed context/scope, ambiguous deadline,
stale/superseded acceptance, duplicate clarification, response-kind separation,
meaning loss, unsupported mapping, deadline expiry and malformed contract values.
The dedicated Linux workflow has a three-minute limit. Local results do not
establish a final-head CI pass or whole-stack qualification.
