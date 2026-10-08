# Context admission deadline follow-up

Reviewed base: `649df22a1392af2c4fa77e4c71749c482f82649c`.

The accepted governed-context profile checks future expiry before acquiring its
SQLite writer lock. A delayed lock acquisition could therefore persist content
whose lifetime had already ended. This is an admission correctness gap, not a
claim that the separate recall or execution checks disclose expired content.

The adapter now reads finite trusted time again after `BEGIN IMMEDIATE` and
before storing content, receipt, admission event or generation. Expired or
invalid time rolls back admission. The existing strict future-expiry boundary,
receipt format, parent restrictions and duplicate-identity behavior remain.

This advances the bounded MG01 admission and IF/MG/GC restrictions documented in
`docs/v1-reference-profiles.md` and `docs/engineering-register.md`. It does not
close those source requirements. Delivery intent still commits before callback;
later revocation cannot retract already admitted disclosure. Trusted host policy,
clock and database custody are assumed. No hidden model reliance, external
deletion, production readiness or external-destination atomicity is established.

## Verification and integration dependency

Five new pytest cases advance the clock immediately after the real SQLite writer
lock is acquired. They cover exact expiry, later time, NaN, infinity and boolean
time; every rejection must leave the item, event history and generation unchanged.
This deterministic hook checks transaction ordering without a timing-sensitive
sleep or a claim of real contention qualification.

Local `timeout 30s python -m pytest -q tests/test_context_memory_profile.py` could
not run because pytest is not installed. The system Python also lacks pytest.
No dependency was installed. Six equivalent standard-library focused checks
passed, including a still-valid admission at time 149 for expiry 150 and all five
rejection cases. Inspection and a local accepted-base check confirmed that base
admission reads its clock only before lock acquisition.

The shared evidence gate currently requires exactly 16 governed-context test
cases. These additions produce 21, bringing the seven-profile total from 67 to
72. Before merge, the gate owner must revise its population/contract, associated
tests and release documentation, then run all required checks on the integrated
exact head. This workstream does not edit those shared files and does not claim
the existing release gate passes. No new workflow, component pin or dependency
is introduced. Deployment packet PR #32 and executor PRs #29/#30/#31 are separate.
