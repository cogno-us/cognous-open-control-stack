# SQLite staging recovery addenda follow-up

This bounded follow-up starts from accepted hub main
`649df22a1392af2c4fa77e4c71749c482f82649c`. It addresses one remaining
backup/restoration correctness requirement: publishing a verified standalone
image must refuse a staging basename that already has SQLite recovery inputs.

The accepted restore checks the two-file package and verifies the exact staged
database bytes. However, an absent destination database can still have a
`-wal`, `-shm`, or `-journal` entry beside it. Publishing there leaves inputs
outside the package digest available to a subsequent SQLite open. A disposable
synthetic journal sentinel reproduced publication on the accepted base; no
existing application database was opened or modified for this check.

Restore now rejects an existing destination or any of these three sidecar
entries, including dangling symlinks. It checks before staging and again just
before exclusive publication. Rejection preserves those entries and publishes
no database; operators must choose a clean staging basename and retain the
prior recovery material for their recovery procedure. The utility does not
delete sidecars or infer that an absent database means no effect occurred.

The caller must reserve a trusted, quiescent staging directory and basename
through publication and later use. The second check detects entries created
during verification, but does not atomically exclude another directory writer
from introducing a sidecar after the check. This is not hostile-host protection.

The `sqlite-staging-snapshot/2` format, manifest fields and CLI remain unchanged.
Checksums identify the copied bytes; they do not authenticate custody, establish
freshness, reconcile destinations, or authorize activation. Consumed claims and
refund-intent ownership remain separate retained histories in separate profiles.
No live deployment is switched, no old history is reset, and no coordinated
production restore, external destination atomicity, crash/power-loss durability
or production recovery objective is qualified.

## Local qualification

The existing nine-case recovery module passes using the already available
Python/pytest environment. Its overwrite test now also covers all three
sidecar suffixes, preservation of their bytes, a dangling sidecar symlink,
and a sidecar introduced between staging and publication. Existing WAL,
uncommitted-transaction exclusion, revocation, exact-byte, corruption,
package-content and prior-contract checks remain intact. Existing collected
test identities and the accepted evidence-gate count are unchanged; the extra
assertions are additional regression coverage, not an expanded release claim.

The base-only disposable sentinel check confirmed the missing refusal.
`git diff --check` passes. Full release qualification and deployment-specific
restoration evidence are not claimed by this follow-up.
