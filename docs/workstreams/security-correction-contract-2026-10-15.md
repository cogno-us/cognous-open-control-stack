# Security correction contracts

This maintenance profile addresses the seven findings from scan
`8a85574c-2aa7-46f0-b4b7-fada217d573a` at hub
`5715f791f9f127506416e9a19bea8eff9231f701`. Implementation and measured
verification status are recorded separately in the U1 verification report.
Selected component pins, authority semantics and production permissions are unchanged.

## Bounded verifier admission

`reference_profiles/bounded_json.py` admits built-in JSON values into a detached
snapshot before existing encoders, hashes or MACs process them. Trusted defaults
are 1,048,576 conservative ASCII-encoded bytes, depth 20, 16,384 nodes, 4,096 list
entries, 256 fields per object, and 65,536 characters per string. Keys count as
nodes; repeated references count at every expansion. Integers must fit the JSON
safe range and floats must be finite. Cycles, custom types and unpaired Unicode
surrogates fail closed. These bounds support the existing small reference fixtures;
they are not a deployment capacity recommendation.

Existing valid canonical formats remain unchanged. Budgets add rejection conditions
without changing signed bytes. Hosts must separately limit incoming bytes before
JSON decoding; already allocated in-memory input cannot be retroactively bounded.
Object size, byte cost and depth are checked during snapshot construction rather
than serializing a complete untrusted container first. Journal count mismatches
return before visiting event details.

## Evidence identities and duplicate processing

The existing ASCII trust wire format is retained. Every identity must be an exact,
nonempty ASCII string of at most 200 characters. No numeric coercion, case folding
or Unicode normalization occurs. Policies, disclosures, issuer/evidence mapping keys,
manifest and attestation references are checked before lookup or signatures.
A repeated attestation identity leaves the envelope invalid and skips that record's
signature and commitment work. Diagnostics remain bounded by the existing wire limits.

## Assurance runtime audit retention

New HMAC assurance stores persist the following trusted lifetime budgets:

| Limit | Default |
|---|---:|
| Append-only events | 4096 |
| Anonymous detailed refusals across all claimed identities | 64 |
| Recorded calls per authenticated principal across key rotations | 1024 |
| Source-counter rows including the anonymous bucket | 256 |
| Encoded event body bytes | 8192 |
| SQLite database pages of 4096 bytes | 4096 |

Limits may be reduced at creation, subject to a minimum database size of 16 pages.
There are no periodic quota resets and no automatic pruning or re-chaining.
The fixed anonymous bucket prevents spoofed actor names from growing counter state.
Once detailed anonymous retention is exhausted, bounded saturating suppression
counters remain available through trusted-host `audit_status()` inspection and
responses expose `audit_recorded=false`. Principal or global capacity exhaustion
blocks further effects. Anonymous flooding cannot consume more than its detailed
budget, although it can still consume CPU, lock time and disk I/O.

The admission connection enforces DELETE journal mode and 4096-byte pages;
WAL configurations fail closed to avoid unbounded WAL retention by readers.
The main database is capped at 16 MiB by default. Rollback-journal overhead is
additional and bounded by the modified database pages plus journal framing;
no zero-overhead total disk claim is made. Acknowledging an audit write requires
the enclosing transaction to commit. Audit errors roll back effects and nonces.
`AUDIT_OR_INPUT_UNAVAILABLE` is a non-authorizing response with no durability claim.
Suppression counters saturate at 9,007,199,254,740,991 and then retain a lower bound.

This changes failure behavior: a missing/unavailable store now returns a denied
result rather than propagating SQLite errors from `apply()`. No store is recreated.
The separate protected destination retains its own admission contract; shared
generic database/event helpers do not impose the HMAC audit schema on it.

### Existing store migration

Existing HMAC stores lack `audit-limits` and `audit_counters` and are refused by the
new admission path. There is no automatic migration or fresh quota on restart.
Retain old evidence with its original implementation. For synthetic test runs,
create a new isolated store and replay explicit setup with new authority fixtures.
Any migration of retained operational data requires a separately reviewed procedure
that preserves nonces, grant state, effects and hash-chain lineage. This patch
provides no authority-restoring rollover or operational migration mechanism.

## Public evidence navigation

The evidence index uses the public operational-trust status page. The selected
architecture transport link is checked against the authoritative lock by
`tools/verify_selected_documentation.py`. Historical evidence remains attached to
its original revisions. Candidate selection is not changed by a link correction.

## Deployment boundary

Remote reachability and upstream admission controls remain unverified. Transport
byte limits, authenticated source binding, host writer exclusion, service rate
limits and production retention obligations are deployment responsibilities.
C0 retains its check-to-commit race; optional C1 remains cooperative same-host
SQLite. C2/C3, real settlement and production deployment remain unqualified.
Operational trust remains HOLD / NOT ESTABLISHED.
