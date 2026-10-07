# Optional execution selection checkpoint

Starting accepted hub: `14696c231e00433161396cfa3093e3e007372fc1`.

The hub now exposes explicit `atomic-authority-effect` and `refund-intent` commands against `component-lock.json`, without changing pins. The commands exercise actual Control Plane and executor APIs, retain separate local databases/results, and reject an existing results directory. Optional evidence is not promoted into the ordinary consumer-chain profile.

Local validation: both atomic scenarios and all four refund-intent scenarios passed. Ten integration checks passed, covering exact recovery state, independent authorized replans, separate-intent positive control, refusal to reuse output, and unchanged retained database contents after cross-profile activation rejection. All scenarios use synthetic authority and fixed time.

CI is split into two bounded Linux jobs. Final-head CI status belongs to the PR checks; this checkpoint does not infer success from local runs. Broader historical concurrency/crash qualifications remain in their existing component suites and Worker 21 records.
