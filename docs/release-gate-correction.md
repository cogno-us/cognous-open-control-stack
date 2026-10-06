# Targeted release-gate correction

This correction preserves the accepted component pins and compatibility disclosures while tightening only release evidence and acceptance enforcement.

The release gate now requires:

- the pinned governed-message transport integration suite;
- a representative operation delivered through `LocalDurableTransport` and `AcceptedGaxRecipientAdapter`;
- downstream Replay, Governance Evidence Pack, ODES and IMX artifacts reconstructed from the retained records for that transported operation;
- exact destination effect/content/state and cross-artifact identity assertions;
- two isolated representative executions with independent transport, exchange and destination state;
- normalized outcome equivalence across those executions;
- JUnit-backed resolution of every required acceptance-matrix reference in both executions;
- required missing/skipped coverage to fail the release;
- explicit skip accounting;
- a regression proving nonexistent required test references cannot pass.

OpenShell live qualification remains unexecuted. Alvorada PR #2 remains deferred and excluded. Moltbot producer provenance remains pinned as previously disclosed.
