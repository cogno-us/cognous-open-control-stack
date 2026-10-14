# Ascended Intelligence comparison addenda

Implementation date: 2026-10-14. Base: `1e1b0b6b011fde82aad00a75bb74f8e563914611`.
External review source: [Ascended Intelligence Core at 28e2dd0](https://github.com/jjlogic2011-maker/ascended-intelligence-core/tree/28e2dd04f17b8e3e4181b3d8a91326664012c1b1).
The external review was static, without executing that project's tests. Its findings motivate Cognous checks; they do not establish equivalent Cognous defects or transfer assurance.

## Bounded implementation

The existing optional context-action wrapper now retains attempted, acknowledged and observed-state fields in its terminal event and exports `context-action-evidence/1`. Export reads one consistent context-store transaction and binds the delivery, generation, immutable content receipt, envelope commitment, claim and effect identity. It excludes raw memory content and does not modify grants, approval consumption or the destination.

`ContextBoundExecutor.export_evidence(binding_id=..., envelope=..., claim_id=...)` validates retained lineage before returning a package. The verifier requires caller-held binding/envelope/claim/effect identities; it rejects receipt and delivery substitution, missing or duplicate results, premature completion and inflated scope. A finished binding may contain a denial. A started binding with no terminal event remains unknown, including after a crash or after destination commit followed by evidence-write failure. Reconciliation remains a separate observation of the original destination, not permission to dispatch again.

The context-action demonstration writes `context-evidence.json` beside `result.json`. The seven-batch gate version 5 requires the export, its matching demonstration identifiers and digest, 36 context-action cases including named claim cases, and 111 runtime cases overall. Its 30 gate-unit cases use synthetic report fixtures, not runtime evidence. Recomputed artifact hashes cannot hide a missing export or substitute unrelated passing test names for the required claim cases.

## Addendum disposition

| ID | Existing requirements | Implemented in this batch | Remaining boundary |
| --- | --- | --- | --- |
| AIC01 | AGC08, ER07 | Two separate Linux processes compete through the actual context-bound execution wrapper; only one commits an effect. Abrupt exit after the durable started marker leaves restart dispatch blocked. | Cognous's hub is not the external project's approval API. Authenticated human reviewer lifecycle and API approval-versus-denial qualification remain deployment/component work. |
| AIC02 | RS07, RS11, ER08 | Terminal records distinguish attempted, acknowledged and observed state. Finished denial and postcommit recording failure are tested without false success. | This records the selected local executor's result, not external settlement, fresh destination observation or useful task completion. |
| AIC03 | MG02, GC 5–7 | Versioned export binds content receipt, generation, delivery and exact action identifiers. Reopen and logical expiry preserve historical evidence; rehashed substitutions fail. | This is a standalone optional export, not default-path adoption or Replay/AGEP/ODES conformance. Hidden model reliance remains unverified. |
| AIC04 | MG01, IF06, AGC08 | Export preserves non-authorizing receipt semantics; negative controls reject authority and model-reliance inflation. | No heuristic promotion engine is introduced. Authenticated, revision-bound promotion decisions remain a separate extension. Repeated use never grants authority. |
| AIC05 | IF06, MG04, RS09 | Logical expiry retains receipt/history while raw content is absent from exports. Physical-erasure claims are explicitly false and mutation-tested. | Legal holds, remote recipient deletion, index/backup erasure and jurisdictional obligations are not implemented or certified here. |
| AIC06 | MG04, ES04 | A separately retained expected digest detects coherent replacement of the exported snapshot. The test also shows why self-consistency alone cannot detect that replacement. | No independent custodian, signature, append-only external journal, freshness guarantee or whole-history completeness claim. |
| AIC07 | ES01–ES03, RS01, RS12 | Semantic negative controls rehash mutations to isolate contract checks. The gate requires named context cases and inspects the actual export. | A trusted runner's reports are not independently authenticated proof that every semantic predicate ran. |

## Qualification and limits

Scoped local checks use Python 3.11.17, pytest 9.1.1 and pydantic 2.14.1: 36 context-action, 21 context-memory and 30 gate-unit cases. The synthetic context-action demonstration also executes the accepted pinned executor and emits a validated export. Exact-head hosted results belong to the integrating PR, not to this base revision. Do not infer a complete seven-batch pass from the scoped local checks.

The exported checksum is not a signature or an independently trusted checkpoint. Supplying the checksum from the same untrusted package adds no independent protection. Caller-held identities must come from the intended operation; deriving them only from a received package defeats substitution checking. Historical receipt verification does not grant current use, establish truth, or verify hidden model influence. Source references and identity metadata can be sensitive; protect exports even though raw context content is omitted.

Old terminal events without attempted/acknowledged/observed-state fields are not silently upgraded. Preserve those records and reconcile against the original destination separately; the new exporter refuses to manufacture complete evidence. Existing started bindings remain non-retryable. No schema mutation or rewrite of historical events is required.

Component locks, selected profile, producer contracts, release authorization and production authorization are unchanged. Operational trust remains HOLD / NOT ESTABLISHED. C0 check-to-commit limits, optional same-host C1, no C2/C3 and no real settlement remain in force. OpenAPPA is unchanged. This batch does not close public-release security, rights, reporting or final owner-acceptance gates.
