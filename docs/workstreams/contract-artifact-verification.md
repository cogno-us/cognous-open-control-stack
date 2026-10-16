# Contract and candidate artifact verification

This release-checking batch adds two bounded checks: published structural
contracts must match the definitions used by existing validators, and an
unpublished hub source archive must match an explicitly selected Git commit.
Neither check authorizes publication or production. Operational trust remains
**HOLD / NOT ESTABLISHED**; component pins and release-selection files are unchanged.

## Contract scope

`contracts/qualification-surfaces-v1.json` describes the exact field sets and enums
for the optional semantic handoff and synthetic resolver observation contracts.
The checker imports the same constants consumed by the validators and the actual
binding dataclass fields. Missing, malformed, duplicate-key or changed published
content fails. Changes require explicit interface review, followed by regeneration:

```sh
python tools/check_contract_surfaces.py --export
python tools/check_contract_surfaces.py
```

The export command prints a candidate; CI never overwrites the published snapshot.
These are structural descriptors, **not full JSON Schemas**: type, temporal,
cryptographic and semantic behavior remains covered by the existing validators
and their positive/negative tests. This initial inventory does not claim coverage
of external component schemas, all adapters, all record exports or a live MCP server.

## Candidate verification

From a trusted checkout containing the intended exact commit:

```sh
python tools/verify_candidate_archive.py /path/to/candidate.tar \
  --revision FULL_40_CHARACTER_COMMIT \
  --sha256 INDEPENDENT_EXPECTED_SHA256 --smoke
```

The verifier requires all tracked files, including README, LICENSE, NOTICE,
selected notice records, component lock and the release-selection record. It
compares every regular file's Git blob identity, size and executable status to
the trusted commit. It rejects missing, extra, duplicate and unsafe members,
path traversal, links, nonregular files and enabled release/production flags.
It supports an unprefixed `git archive --format=tar COMMIT` source archive; it
fails closed on repositories containing submodules or tracked symlinks.

The expected checksum must come from a trusted channel for a downloaded artifact.
CI generates its own candidate and checksum to test the packaging path; that is
not independent provenance. The source revision must be chosen by the reviewer,
not copied from an untrusted archive. This tool verifies trusted source identity;
it does not decide whether that source is safe to execute.

`--smoke` writes verified files into a fresh temporary directory, then runs the
packaged contract checker and existing handoff, resolver and protected-destination
unittest suites. No Git checkout or network request is needed by those tests.
Destination cases assert successful effects, refusal records, revocation and
lost-ack redelivery against synthetic SQLite state. Missing dependencies, failed
or skipped tests, and timeouts fail the command. Without `--smoke`, the result
explicitly reports `NOT_RUN`. The extraction is disposable, not a security sandbox.

With `--qualification-root` and `--qualification-revision`, the smoke runner is
taken from an external qualification suite checkout. Before anything runs, the
verifier requires that checkout's `HEAD` to equal the given exact revision, with
no tracked modifications, no untracked or ignored files (`git status --porcelain
--untracked-files=all --ignored` must be empty) and no skip-worktree or
assume-unchanged index entries. The harness then runs under `python -I`, so
`PYTHON*` variables, the user site directory and the harness script directory are
not on the import path. These checks bind the checkout's working tree to a
commit; they do not establish that the commit itself is trustworthy, which is the
caller's choice of revision. Interpreter-wide site-packages remain trusted.

## Limits and provenance

This is a **hub source candidate**, not a redistributable component bundle. It
does not reproduce the complete selected component chain, establish independent
security/legal acceptance, verify reporting-mailbox delivery, or close release
issues #70, #73, #86 or #87. C0 check-to-commit limitations, optional same-host C1,
unqualified C2/C3 and the prohibition on real settlement remain unchanged.

The design was informed by Xerj at commit
`3a4374d64aa0fca32497b165bbcdf982b32034b3`, specifically
[`published_schema_drift.rs`](https://github.com/xerj-org/xerj/blob/3a4374d64aa0fca32497b165bbcdf982b32034b3/engine/crates/xerj-mcp/tests/published_schema_drift.rs)
and [`verify-release.sh`](https://github.com/xerj-org/xerj/blob/3a4374d64aa0fca32497b165bbcdf982b32034b3/scripts/verify-release.sh).
This is an original Python implementation of those checking patterns; no Xerj
source code is copied or vendored and no Xerj runtime dependency is introduced.
Retrieval budgeting and index-generation selection remain deferred.
