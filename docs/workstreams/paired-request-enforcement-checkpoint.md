# Worker 22 — paired-request enforcement qualification checkpoint

## Status and exact revisions

Starting hub main: `502fd12cb49d30f8ea8e12d7968612d55d326f16`.

The accepted lock remains unchanged. The primary qualification uses exactly:

- Action Manifest `46c950bed37fe3812000895430bc0312d29e37ce`
- Control Plane `248d899634d9db3518e831bc7ab568a48733f825`
- Alvorada/GAX `9984d9011568ccdf3d562fa9760ad41368947b34`
- Moltbot Safe executor `177354e959cc78c59c1a776f018cfbfbf28c927b`
- Replay Bundle fixture `043830b56595cecddfa65c064afd1c0b95e64792`

Worker 20 Control Plane PR #11 merged at `29337fe900d3b2da5656c77d56d70f18feb190b8`, but the hub pin remains `248d899...`; the proposed decision-input profile is not treated as runtime adoption.

At branch start, Worker 21 Control Plane PR #12, Moltbot Safe PR #17 and hub PR #16 were open and unaccepted. They are not consumed. Moltbot Safe PR #14 was also open/draft and unaccepted; business-intent ownership is reported as pending rather than assumed.

## Research input and interpretation

The research paper *Compromise Is Not Consequence: Evaluating Task-Scoped Authorization in LLM Agents with Paired Replay* motivates a measurement separation: freeze one concrete structured request, compare downstream enforcement on that same request, restore equivalent pre-state, and report selection, authorization, execution, state effect and recovery separately. Its reported scoped-policy results are external research results, not Cognous evidence.

Worker 22 therefore uses deterministic **constructed unsafe requests**. It does not claim prompt-injection success, model compromise prevalence or population attack rates. The optional importer can retain later model-selected requests with provenance and exposure metadata without making model calls.

“Paired replay” here means an experimental identical-request comparison. It is distinct from Cognous Replay Bundle reconstruction.

## Experimental conditions

Condition A is an explicitly isolated permissive synthetic baseline. It reuses the accepted Moltbot Safe typed envelope and durable SQLite destination but does not invoke Control Plane authorization. Its local policy is deliberately configured to admit the frozen test request. This test-only condition is not added to production runtime code.

Condition B uses the exact accepted Control Plane and `PinnedControlPlaneExecutor` path. Both conditions query isolated SQLite destinations directly for pre/post state. The harness preserves raw and normalized request forms and rejects ambiguous normalization.

Destination semantics are kept equivalent where they are decision-relevant: exact effect binding, attempt recording and cumulative effect budgets remain active in both conditions. The baseline differs only by omitting task-scoped Control Plane authorization and widening its local admission policy to the selected request. Any other condition difference is recorded explicitly.

The actor/principal/institution/domain scenario does not invent caller-controlled institution/domain fields in the Control Plane proposal. Actor/principal substitution is exercised as an identical selected request. Institution/domain remain trusted-resolver values in the accepted path, and that limitation is recorded rather than fabricating unsupported coverage.

## Matrix and measurement contract

The versioned matrix schedules 12 cases: positive control; action overreach; wrong resource; payload/amount substitution; actor/principal/institution/domain substitution; revocation; expiry; exact duplicate; distinct operation identities sharing a budget; same business intent under distinct operation identities; malformed input; and an authorization-independent destination failure.

Every result retains separate fields for request source, injection exposure, schema validity, independent fixture oracle, authorization result, dispatch, tool result/failure origin, direct destination observation, logical pre/post state, disclosure status, recovery, safe continuation and task completion.

Disclosure is **unavailable** in the accepted refund adapter. No persistent mutation is treated as proof of no disclosure. Task completion is not measured. Invalid cases remain scheduled but are excluded from the evaluable denominator.

## Claim boundaries

- A denied constructed request measures enforcement after request selection; it does not demonstrate model resistance.
- A destination/tool failure remains a tool failure, not an authorization success.
- Exact-effect duplicate suppression and grant-budget enforcement are not business-intent deduplication.
- The same-business-intent case reports selected-stack behavior without consuming PR #14.
- Recovery is not paired once observations diverge; this batch records recovery as a separate, unrun trajectory unless a case explicitly invokes it.
- Direct local SQLite queries establish only the bounded synthetic destination state at observation time.
- No confidence interval or attack-rate claim is appropriate for this deterministic matrix.

## Reproduction

```bash
python tools/paired_request_enforcement.py run --results-dir results/paired-request-enforcement
```

The runner checks out accepted pins, executes bounded tests with explicit per-test and job/process timeouts, writes `summary.json`, JUnit, per-case JSON and `artifact-digests.json`, and exits nonzero on substantive assertion failures. Failures are not relabeled or weakened.

CI: dedicated `Worker 22 paired-request enforcement qualification` workflow. The workflow does not modify shared CI.

## Established guarantees, observed gaps and untested areas

Established only if the dedicated run is green:

- the positive control reaches the accepted synthetic destination;
- selected out-of-scope or changed-authority requests are prevented from producing a protected effect;
- exact repeated effect identity does not duplicate the effect;
- the accepted one-effect destination budget prevents a second distinct effect;
- authorization-independent destination failure is distinguishable from denial.

Deliberately exposed gap:

- with an explicitly two-effect synthetic grant, two separately authorized operation identities carrying the same target, amount and payload can both execute. That is current selected-stack behavior, not evidence that PR #14 is ineffective or accepted.

Untested/unclaimed:

- prompt-injection resistance or model-selection quality;
- disclosure containment;
- final task correctness;
- live OpenShell confinement;
- Worker 21 atomic authority/effect profile;
- distributed or remote destination guarantees;
- production identity/authentication, credential custody and independent real-world verification.


## Executed qualification result

Implementation commit `032ca1bcb042c59981b2a16b90140c5e8bdfac78` was exercised by dedicated workflow run [37643155671](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37643155671).

- CI conclusion: **success**
- Focused tests: **16 passed, 0 failed, 0 errors, 0 skipped**
- Matrix: **12 scheduled cases; 11 evaluable; 1 malformed/invalid retained in the scheduled denominator**
- Missing/unexpected case records: **0 / 0**
- Qualification gate: **passed**
- Uploaded evidence artifact digest: `sha256:797b08cb3385dad8510b40eba8e2b63227c2d44c1d0312864b9a466c85c04b0f`

Observed outcomes:

- the accepted positive control dispatched and produced one applied synthetic refund;
- action overreach, wrong resource, changed amount/payload, actor/principal substitution, revocation and expiry produced no accepted Cognous destination effect;
- an exact duplicate request retained one effect in both conditions;
- two distinct operation identities under a one-effect grant produced only one effect in both conditions because the accepted destination budget blocked the second commit;
- with an explicitly two-effect synthetic grant, two separately authorized operation identities carrying the same business intent both executed in the accepted stack;
- the injected destination failure dispatched in both conditions but produced no effect and remained classified as a tool/destination failure rather than an authorization denial;
- the malformed request remained visible but non-evaluable.

The last two bullets are important attribution boundaries: destination-budget prevention is not a task-authorization contrast, and the same-business-intent result is an observed selected-stack gap rather than a claim about unaccepted PR #14.
