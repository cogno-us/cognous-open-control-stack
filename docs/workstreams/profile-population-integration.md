# Profile repair and evidence population integration

Integration base: `0fa461eb7f15dfeed8bae12c97a32a571b2a42e5`, including
accepted deployment review, recovery sidecar refusal and standalone handoff,
lifecycle, provenance and resolver observation checkers. This candidate includes three reviewed heads
without rewriting or replacing their history:

| PR | Preserved parent | Contribution |
| --- | --- | --- |
| #33 | `8a1ed4a96d5100854e3aeaec494c9d6317e78072` | Exact reviewer configuration and retained review history |
| #35 | `fab4f1856fb70ddbec5dfeb882df930971d2642f` | Context admission expiry rechecked after writer lock |
| #36 | `0615d77a30c36b206cb9e5d6b39e4c7abc83ef03` | Exact temporal result and effect qualification |

The combined commit parents preserve those reviewed contributions. Original PRs
remain available; this candidate is their combined acceptance boundary, not a
claim that their earlier independent evidence gates passed.

Evidence contract `v1-reference-extension-evidence/4` requires 91 profile cases:
6 environment, 21 context, 16 institutional review, 15 temporal, 16 bound action,
8 notification and 9 recovery. It retains exact same-revision, lock, artifact and
execution-status requirements. Four additional gate cases reject contract /3
and each old population even when relabeled as /4. Historical reports remain
historical; updating their labels does not qualify them.

## Local evidence

After incorporating accepted recovery #34, all seven profile batches and all
26 gate tests passed (117 tests). Seven actual demonstrations/batches were also
recorded with retained JUnit, environment and component provenance; the aggregate
returned `valid=true`, 91 scheduled tests, seven verified batches and no errors.
That artifact set belongs to its recorded local integration revision, not a
subsequent published commit. Final-head CI must produce its own evidence.

After incorporating main through #39, a combined run passed **184 tests**:
91 profile tests, 26 gate tests and 67 tests for the four accepted standalone
checkers (deployment review, handoff, lifecycle and provenance grouping). No
skipped case is counted as a pass. The existing bounded CI workflow collects the
91 profile population and all gate negatives without changing workflow policy.

No accepted component pin, engineering register, runtime grant, default-path
selection or production qualification changes. Existing parent-checkpoint local
counts are preserved as historical evidence, while this integration document
records the combined population and resolves their shared-gate dependency.

After additive resolver PR #40 was merged, its 20 isolated checks passed on the composed candidate. No shared profile files changed in that merge, so the 91-profile campaign was not repeated. The final CI head remains the release acceptance source.
