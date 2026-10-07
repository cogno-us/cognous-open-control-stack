# Local qualification evidence

These are local candidate results, not accepted release evidence.

- `local-verifier-tests.xml`: 17 passing verifier and actual pinned adapter tests;
  no namespace-isolation success is implied.
- `local-isolation-attempt/summary.json`: initial blocked campaign; source hash
  identifies the earlier runner.
- `final-local-isolation-attempt/summary.json`: blocked campaign with captured
  worker timeout/diagnostic and independently empty destination.

Both campaigns returned nonzero. The private path names in the diagnostics
refer only to disposable synthetic fixtures. No credentials or research source
material are included. CI evidence, if produced, must retain its own source head
and result; it must not overwrite these failed local attempts.
