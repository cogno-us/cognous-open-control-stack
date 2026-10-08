# Cognous W0 C1-C8 baseline index

Status: **candidate / not frozen** until all owning PRs receive required review and applicable CI.

## Inspection record
Inspected 8 October 2026 UTC:
- hub main `30532e261b8fe6f48952387f033b59b7831d6dae`
- Action Manifest main `a56a15efd3d9524698b204dc43f5f874dcc4cd96`; selected `46c950bed37fe3812000895430bc0312d29e37ce`
- Control Plane main/selected `d3dadee70bd319812b207389ab1e0f6efe511916`
- Execution Runtime main `489875c98a3592c0ebe0f939b6466cbd2447acd1`; selected `c3c3ee7188b9367cf70b08074b9c40a5c70c94ac`
- Replay main/selected `459e4ba62fca49364aebb0050cd5fb2dd5a71bfa`
- Evidence Pack main/selected `b4baccd823d2a73be276c1de745b19cf7c56a0d6`

Current selected lock remains `merged-producers-v1`; W0 does not change `component-lock.json`.

Open proposal state checked directly:
- hub #44 open draft, head `eb86fb2d38fdd5fdc88ac9386755e8c776247a06`
- Manifest #10 open draft, head `0c8da50f80557eb7ecc654c7e734f2c55e559346`
- Runtime #29 open draft, head `a7b8a8325671629593d4da84c6f071c85297829e`
None is an accepted dependency.

## Contract inventory and W0 disposition
| Contract | Owning components | W0 disposition | Downstream owner |
|---|---|---|---|
| C1 exact action | Manifest + Control Plane | New tenant-aware generation; preserve 1.1 historical contract | W1 |
| C2 current authority | Control Plane + Runtime | New tenant-aware authority binding generation; preserve ordinary bounded race | W1 |
| C3 capability/profile | Runtime + hub | Freeze profile identity/capability admission semantics; no mandatory adapter | W4-W6 |
| C4 failure record | Control Plane + Runtime | Freeze typed classification; implementation only if W2 proves missing retained path | W2/W3 |
| C5 observation/recovery | Runtime + destination | Reuse effect/attempt identities; freeze uncertainty/freshness/no-blind-retry semantics | W2/W3 |
| C6 flow/result admission | Manifest + Control Plane + Runtime | Freeze exact-operation conjunction and separate result admission; optional path only | W4 |
| C7 stop/intervention | Runtime + profile owner | Freeze request/ack/closure/quiescence/reconciliation distinctions | W2/W6 |
| C8 evidence compatibility | Replay + Evidence Pack | Freeze explicit loss states and no-assurance-upgrade rule | W3/W7 |

## Candidate contract generations
- `runtime-action-proposal/1.2`: requires bounded opaque `tenant_id`.
- `bounded-authorization-effect/0.2`: tenant-aware binding and current-authority join.
- C3/C4/C5/C6/C7 are semantic contract locators over existing owning record/profile surfaces; W0 does not invent schema numbers before owning implementation review.
- Replay remains `Reconstruction Bundle 0.2.0` for existing accepted producer pairs.
- Evidence remains imported schema `0.2.0` / transformation `agep-manifest-reconstruction-import/0.3.2` for its exact accepted producer set. W3 chooses any new consumer generation only after producer schemas are accepted.

## Fixture bundle
Candidate shared fixture: `fixtures/w0/c1-c8-refund-v1.json`.

The positive C1 fixture and tenant-only substitution have different canonical commitments:
- tenant-alpha: `sha256:14e63aece6e26ee985d969e24fab537d583b21d8b8a7a6f475535b3e1246a9c0`
- tenant-beta: `sha256:6ec8c4e73c02d50da0b7080d3970d30872ae124b90151df0dace9afdf5cf70aa`

These hashes were generated using the existing accepted compact sorted-key UTF-8 SHA-256 canonicalization profile. Placeholder manifest/payload digests inside the synthetic fixture are deliberately non-authoritative test values; downstream executable fixtures must replace them from pinned producer code.

## Migration rules
1. Historical artifacts remain decodable at their original assurance.
2. Tenant is mandatory for the new execution profile; no null/default/backfill makes an old artifact executable.
3. Changed tenant/action/profile bytes require fresh authorization and new commitment/effect derivation where applicable.
4. Old effect IDs, attempts, consumed claims and destination deduplication state are preserved.
5. Optional profile extensions cannot weaken core required fields.
6. Atomic authority/effect and refund-intent profiles remain separate.
7. A contract amendment must name affected streams, new fixtures and requalification impact.

## Freeze gate
This index becomes a freeze record only after:
- all owning PRs are accepted or explicitly reviewed as no-change;
- applicable CI/schema/fixture checks pass;
- each accepted PR head/base is rechecked against current main;
- unresolved boundaries are recorded below.

## Handoffs
- W1: C1/C2/C8 and canonical tenant substitution fixtures.
- W2: C4/C5/C7 and failure/uncertainty/stop fixtures.
- W3: C8 plus C1/C4/C6/C7 producer mappings and historical loss cases.
- W4: C1-C3/C6/C8; optional OpenAPPA proposals remain separate until accepted.
- W5: C1-C4/C8; no Microsoft AGT runtime dependency.
- W6: C3/C5/C7/C8; live environment remains profile-specific.
- W7: accepted baseline index plus final composed qualification obligations.

## Unresolved boundaries
- Owning-component review is required for tenant field bounds/location and generation names.
- W2 must verify outer refusal retention before any new failure schema is implemented.
- W2/W6 must name and qualify the actual local stop lever.
- W3 must select consumer schema/transformation generation after accepted producer bytes exist.
- Optional profile route/configuration pins remain profile-specific and are not core freeze blockers unless their shared semantics change.
