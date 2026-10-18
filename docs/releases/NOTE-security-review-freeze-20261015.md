# Note on security-review-freeze-20261015

`docs/releases/security-review-freeze-20261015/` is a historical, pre-remediation freeze. It is retained as evidence and is not an integrity reference for the current tree.

- Its `SHA256SUMS` no longer matches its `README.md`, because the README was edited after the sums were written. The current README bytes are the ones recorded by the later freeze manifests.
- The source ZIP listed in `SHA256SUMS` (`cognous-source-review-7f335099.zip`) is not in the repository, so `sha256sum -c` cannot pass for that directory.
- The later freeze manifests (`security-review-freeze-20261016` and `security-review-freeze-f5b-20261016`) record the current bytes of this directory's files.
- `reproduce.py` in that directory is operator-invoked. It is not an integrity check.
- For verification, use the later freeze directories `security-review-freeze-20261016` and `security-review-freeze-f5b-20261016`.
