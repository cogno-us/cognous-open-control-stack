# Independent qualification and evidence contract

Apply the ISSBench planning distinction, adapted to existing OCS Qualification formats:

1. **TestSpec:** source-backed applicability, original scope, independent frozen expectations and negative controls.
2. **Configuration:** exact component/registry/evaluator/adapter profile with support and enabled state.
3. **FrozenInvocation:** source/fixture/oracle hashes, environment, identity, attempt and immutable inputs.
4. **Observation:** raw output, failures, timeout, state, readback, negative records and custody uncertainty.
5. **IndependentOracle:** separate expected-vs-actual assessment, without producer-controlled changes.
6. **EvidenceRecord:** claim scope, PASS/FAIL/BLOCKED/NOT RUN with limitations, predecessor links and custody.

These are conceptual record roles, **not a new runtime protocol**. Reuse current OCS schemas and record precise gaps in S01. Missing mandatory evidence cannot become PASS or NOT APPLICABLE without a proved source predicate. Setup failures and ambiguous effects retain their own attempts. Report separately: mandatory-requirement verdict, raw executable-suite health and original/pre-reduction coverage. An accepted narrow claim cannot be advertised as full qualification.
