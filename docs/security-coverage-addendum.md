# Security coverage corrections — 2026-10-15

This addendum records bounded work for hub issues #138–#140. It grants no security clearance, deployment authorization, or component selection change. Operational HOLD remains in force.

## Scope and receipts

The original scan revision is `5715f791f9f127506416e9a19bea8eff9231f701`: all 672 tracked paths now have revision-bound byte commitments and screening dispositions. The historical scan's 113 reviewed-path identities and receipts remain unavailable. The other 559 identities cannot be inferred. This new screen does not reconstruct historical review.

The separately frozen current hub revision is `52fdbcda70c77e9781cc082e316e1ffc8261287f`, with 641 paths. Its delta is 22 added, 53 removed, 45 changed, and 574 unchanged. Subsequent implementation files belong to the delivery commits, not that frozen screen.

All 13 selected component revisions have per-path receipts (5,561 paths), plus 27 targeted source traces across the hub and components. Each trace records repository, exact revision, path, SHA-256, method, scope and disposition. Automated Python AST/JSON parsing, text rules and Bandit 1.9.4 are structural checks; they do not establish full semantic review. Binary/compiled files, large inputs, optional legacy code, TypeScript semantics and paths outside targeted traces retain explicit deferrals. This is an agent source review, not an independent auditor sign-off. No existing exact-revision component clearance was established.

## Source boundary conclusions

The targeted traces inspect decision/effect bindings, executor local permissions and budgets, manifest targets, transport configuration, replay integrity, evidence loading, attestation and registry adapters. Core adapters and loaders still require trusted-host admission. Selected source also contains standalone listeners and legacy/demo surfaces; their existence does not establish deployed reachability. Route labels, attestor names, evidence commitments and replay integrity are not authorization or cryptographic identity by themselves. These limitations remain recorded in the qualification repository’s `results/security-coverage-20261015/manual-review.json`; selected pins are unchanged.

Static signals retain rule IDs and locations, with matched secrets and source snippets omitted. Test TLS key markers and documentation placeholders were distinguished from deployment credentials; no deployment key inventory is claimed. Git blob SHA-1 compatibility and internally fixed SQL identifiers were inspected in context. Remaining automated signals are not silently converted into confirmed vulnerabilities or clearance.

## Public navigation and embedding admission

Anonymous checks covered 48 URLs referenced by 12 public pages: 44 reachable, one intentional GitHub authentication wall, and three unverified (DOI, OWASP and the action-manifest landing page). The initial DNS failure and subsequent retries are retained separately. Unverified network/HTTP 502 responses are not proof that a source is broken; fragments were not verified. No links were deleted to manufacture a passing result. These receipts support the navigation follow-up to #70/#87 only at the recorded observation time.

Actual deployment configuration is unavailable. All nine exposure surfaces remain unverified. The new `embedding-exposure/1` checker binds source revision, lock digest, environment and bounded configuration/evidence bytes, and requires per-surface authentication, predecode and traversal limits, request/time budgets, storage bounds and host permissions. Remote declarations cannot use trusted-local-host authentication. Even a complete declaration packet always returns `deployment_verified=false`, `production_authorized=false` and `authorizing=false`; an operator still must establish actual deployment truth.

The existing deployment-review validator now bounds packet structure before traversal and returns an incomplete assessment for malformed/oversized structures rather than crashing. No production endpoint was probed, deployment activated, or component pin/profile changed.

## Remaining work

* #138: missing historical receipts and unreviewed semantic scope remain unresolved; this ledger makes their absence explicit.
* #139: the bounded exact-pin source review and independent deferrals are delivered; broader audits remain separate work.
* #140: wider navigation receipts and fail-closed admission tooling are delivered. Actual deployed configuration and the three unverified URLs remain open evidence gaps. Obtain configuration through the established private security channel; do not commit secrets or probe production under this addendum.

## Using the exposure checker

```sh
python tools/verify_embedding_exposure.py examples/embedding-exposure-unverified.json --lock component-lock.json --expected-revision 52fdbcda70c77e9781cc082e316e1ffc8261287f
```

The retained example intentionally exits 2. Configuration references are relative to the packet directory and contain `path` and `sha256`; escapes, symlinks, mismatched hashes and excessive packet structure fail closed. Replace the example only with actual retained, secret-free evidence. Surface IDs and exact field names are defined in the checker and covered by synthetic regression tests.
