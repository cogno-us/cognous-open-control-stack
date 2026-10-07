# Merged-generation pin adoption

Starting hub: `f801546d5272104b02a240e1126b3f92f26486f2`, accepted PR #23. The full candidate was qualified in run `37694032916`; all four batches and 35 acceptance scenarios passed. This change adopts that exact component set and explicitly selects GAX `merged-producers-v1`.

Historical compatibility inputs remain in the lock. Previous GAX acceptance history is preserved. Tests compare selected pins with the qualified full candidate rather than stale pre-adoption constants. The paired-request harness receives a versioned v2 baseline matrix; v1 and prior campaign evidence remain unchanged. Process-boundary and protected-worker runners receive the selected GAX profile explicitly, so their future evidence cannot silently report an older pairing.

README, current release status and compatibility pages distinguish code availability from execution-profile activation. Earlier release/compatibility pages are retained as historical records. Protected-worker results are not transferred automatically to new pins.

Adoption-head CI results are recorded in the PR. No success is inferred merely from the lock edit. Runtime semantics, matrix assertions and component implementation code are unchanged. The ordinary bounded path still does not compose authority/effect atomicity with refund-intent ownership or establish production readiness.
