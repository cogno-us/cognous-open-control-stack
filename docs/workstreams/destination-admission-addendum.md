# Destination admission engineering addendum

Date: 2026-10-14. Hub baseline: `ed13c271f6e380bf294943291b7f173c2bfff5e3`.
Source: user-supplied `Cognous_Engineering_Addendum_Moltbook_101426_A.md`,
sections J1–J4. Discussion reports are requirements input, not verified exploit
results. No Moltbook messages or operational automation were changed.

## Repository findings

The selected lock still names control plane
`d3dadee70bd319812b207389ab1e0f6efe511916` and execution runtime
`c3c3ee7188b9367cf70b08074b9c40a5c70c94ac`. Current upstream main was fetched:
control plane `b0208e31c8ade4708e1f2765a8a3b5ab0052aa0c`; runtime
`392db8c88de6e05f2d5410510049c1eea15bc3fe`. The runtime checkout's origin pointed
to a local checkout, so live verification used the explicit GitHub repository URL.

Targeted inspection confirmed that `verify_local_execution_claim` at the control
plane pin and main checks self-computable commitments. These commitments establish
consistency, not issuer authentication. Runtime main retains authority/effect
receipts in its transaction and checks provisioned local authority. The selected
profile therefore depends on its trusted provisioning and database boundary;
this review did not demonstrate a remote bypass of that boundary. The source's
hypothetical accepted direct calls are not treated as reproduced findings.

The hub already has authenticated optional runtime profiles, public-key evidence
checks and staging recovery. Those do not establish independent restore domains,
production secret custody or destination-provider grant equivalence. This batch
adds a separate opt-in destination reference. It neither replaces the selected
runtime nor moves component pins.

## J1 Revocation beyond an authority restore

`ProtectedDestination` owns a monotonically increasing scope generation alongside
its effective-grant view, credential bindings, consumption, resolution records and
synthetic effects. Fence advancement and effect admission take the same SQLite
writer transaction. Commands are signed by the configured administrator; effects
require the separately configured custodian. The generation must equal the current
destination fence: both stale and unissued future generations fail closed.

The authority snapshot is outside this destination's declared backup set. A stale
signed authority request restored from a JSON snapshot and submitted by another
process cannot lower the fence or reuse epoch 7 after advancement to epoch 8.
Refusal is durable as `AUTHORITY_STORE_BEHIND_FENCE`. A matching backup-set
identifier fails provisioning with `FENCE_IN_SAME_BACKUP_SET`.

**Acceptance achieved:** separate-process stale snapshot refusal, monotonicity,
future-epoch refusal, crash rollback and shared-budget concurrency are exercised.
**Boundary:** separate backup-set labels are declarations, not infrastructure
attestation. The test uses one host and two processes, not two hosts. Restoring the
destination database, keys and fence together defeats the assumed boundary. A real
external monotonic service, independent destination administration and cross-host
restore qualification remain required. Neither same-host SQLite nor a second file
alone establishes C2/C3 or durable revocation under total platform rollback.

Discussion source: https://www.moltbook.com/post/1a3e2e31-cd55-472c-a054-96b0309ae56b

## J2 Explicit destination equivalence for rotation

Hard pins remain the default. Only credential and dependency version classes may
opt into a soft pin. Policy and target identity remain exact hard pins. The
destination's administrator-provisioned effective-grant set is captured when a
grant is provisioned and read again inside the effect transaction. Exact equality
is required: widening, including a strict superset, fails with
`SOFT_PIN_SCOPE_WIDENED`; narrowing fails with `SOFT_PIN_SCOPE_CHANGED`.
An unavailable view fails with `SOFT_PIN_DESTINATION_UNREAD`.

An accepted rotation retains the destination authority label, principal, expected
and observed versions, before/after grant digests, predicate and result in a
resolution-input record. Issuer claims contribute only a context digest and cannot
establish equivalence. The receipt, consumption and effect commit together.
Failure to write the resolution record or audit aborts the effect and consumption.

**Acceptance achieved:** equivalent rotation, identical issuer claims with broader
destination grants, superset/narrowing refusal, missing view, hard-pin defaults and
receipt-write failure. **Boundary:** the view is a synthetic, trusted destination
assertion. No provider IAM API is integrated; no semantic equivalence beyond the
explicit grant strings is claimed. Dependency version rotation additionally needs
an adapter-specific behavioral compatibility contract before real deployment.
Unsupported adapters must retain hard pins.

Discussion source: https://www.moltbook.com/post/7e9509c4-680a-44bf-bff8-0d37f4d7cdf4

## J3 Custody and signed destination admission

Administrator, custodian and verifier have distinct identities and public keys.
The runtime receives public verification keys only. Synthetic client fixtures hold
private signing keys outside the runtime object. A destination command must be
signed by its designated role; an agent cannot substitute a self-computed digest.
Each execution requires a verifier-signed status bound to the exact command,
request digest, generation and current clock tick. Missing status produces
`VERIFIER_UNREACHABLE`; stale, inactive, altered or cross-command attestations hold.
There is no cached-state grace mode.

Each provisioned grant declares the custodian and a per-grant credential binding.
Exhaustion or explicit revocation closes that binding; expiry blocks admission.
A fresh effect cannot use the closed binding even through the custodian. A
credentialless direct agent command is refused. Identical committed effects may
be observed again without consuming or performing another effect; conflicting
reuse of an effect ID is refused.

**Acceptance achieved:** forged claims, direct agent calls, exhausted/revoked/expired
bindings, verifier absence/staleness/replay, audit rollback, concurrent consumption
and restart/lost-ack reconciliation. **Boundary:** these are synthetic signed
admission bindings, not cloud credentials or a secret manager. No live credential
was issued, revoked or tested. Key custody, agent process isolation, actual direct
provider routes and real verifier reachability remain deployment evidence gaps.
The verifier input is supplied to the local admission API; no online RPC is
implemented. All participating revocations must advance destination state. A
remote authority change that never reaches that state is not linearized by this
reference, even with a fresh signature.

Discussion sources:
https://www.moltbook.com/post/0617e6ab-10db-4fe1-9cef-b9a4e8114b97
and https://www.moltbook.com/post/7390910c-be98-4253-bafa-ad6dc63a6fd5

## J4 Protocol evaluation machinery

`protocol_evaluation.py` prepares paired on/off assignments with fixed model,
tool configuration, budget, seed and error costs. The registration has a content
commitment. Outcome records contain case, observations and actions, with curated
truth, relevance, confidence and holdout annotations; transcript and condition
fields are rejected. Scoring is committed before unblinding.

Reports separate action change after relevant evidence, stability after irrelevant
evidence, asymmetric false-positive/negative costs, Brier calibration and held-out
accuracy. The blinding diagnostic uses an exact paired permutation distribution,
not an independent-trial binomial assumption. A perfect condition guess across six
pairs detects leakage at the preregistered 0.05 threshold; a constant guess across
balanced pairs does not.

**Acceptance achieved:** scoring, paired completeness, duplicate rejection, plan and
score tamper detection, transcript/condition exclusion and blinding diagnostics.
**Not achieved:** model behavior evaluation or effectiveness evidence. No model
trials, human grading, sample-size justification or curated real task study ran.
The hashes detect accidental changes under an honest coordinator; they are not
independent timestamping or custody. The allocation and seed must be withheld from
graders, and semantic leakage through actions/observations still needs the blinding
check. Labels and ground truth require independent curation. A passing fixture
is not a protocol efficacy result. Protocols remain **instructions, not measured**.

Discussion source: https://www.moltbook.com/post/3fc82d48-f2e4-44aa-9db9-1a80071572a3

## Qualification and release implications

Run `python tools/destination_admission_qualification.py --results-dir /tmp/destination-results`
after installing `tools/requirements-federated-governance.txt`. The runner records
exact commit, source hashes, independent XML testcase counts and control-removal
results. CI repeats on Python 3.11 and 3.12. New tests cover 29 destination cases
and 12 evaluation cases; the inherited 126-case suite is also included. Subchecks
are reported separately from independent testcase elements.

No selected component, release profile, real destination, external message,
production authority or OpenAPPA feature changed. Operational trust remains
HOLD / NOT ESTABLISHED. C0 limitations and optional same-host C1 remain; C2/C3,
real settlement, production custody and independent security acceptance are not
established. Both release and deployment authorization flags remain false.

Remaining acceptance work is concrete: independently enforce and attest the
restore boundary; integrate destination IAM and credential revocation; qualify
remote verifier/fence failure and revocation propagation; execute real cross-host
recovery tests; curate and preregister a powered, independently graded protocol
study. Do not close those items based on these synthetic fixtures.
