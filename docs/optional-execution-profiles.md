# Optional synthetic execution profiles

The hub offers two explicit execution commands using the exact accepted component lock. Each activates a real executor profile in fresh local SQLite destinations. The ordinary reference release remains the default.

| Option | Execution boundary | Demonstrated cases |
| --- | --- | --- |
| `atomic-authority-effect` | Trusted Control Plane handoff provisions a claim; local authority, claim consumption, budget, and effect share SQLite ordering | Authorized effect; revoked grant prevents effect; exact claim recovery |
| `refund-intent` | Trusted synthetic domain identity binds one intent to its original effect and dispatch claim, with current Control Plane revalidation | Authorized effect; revoked grant prevents effect; two authorized operation identities for one intent retain one effect; distinct intents can execute |

Use a Python 3.11 virtual environment with Git and network access to the public component repositories:

```sh
python -m pip install 'pytest>=8,<10' 'pydantic>=2,<3'
python tools/optional_execution_profile.py --profile atomic-authority-effect --results-dir results/atomic-example-1
python tools/optional_execution_profile.py --profile refund-intent --results-dir results/intent-example-1
```

Results directories must not exist. The runner never deletes or migrates a destination. Each scenario gets its own database. The `.optional-work` component cache must match the accepted revisions and have no tracked modifications; use `--work-dir` with a fresh directory after a pin change. Each synthetic execution has a 90-second process-group timeout. CI runs the two options as independent Linux jobs; no Swift or other OS jobs are added.

`summary.json` records the profile, exact source revisions, lock digest, scenario exit results, and scope. Each scenario retains the real database and `result.json` with execution outcomes and profile-specific evidence. The fixture uses a fixed synthetic time and trusted synthetic authority/domain sources; it does not accept real customer requests. Refund scenarios deliberately allow three effects in their grant so duplicate-intent protection is distinguished from budget exhaustion.

These are separate options, not a combined guarantee. Atomic and refund-intent profiles cannot share a database. Cross-profile activation must fail without modifying retained state. Neither command enables both profiles or changes the default release profile.

The atomic profile requires cooperating authority writers and executors participating in the same-host handoff and authoritative SQLite store. A later invalidation cannot erase an already committed effect. Refund-intent registration does not grant authority; a consumed dispatch claim cannot be reassigned or retried merely because an effect is currently absent. This can sacrifice availability after a crash.

The retained optional evidence is not claimed as a qualified Replay/AGEP/ODES consumer-chain export. These commands establish no distributed or external-destination atomicity, hostile-host isolation, production identity custody, production readiness, or EBL-Core conformance. The Decision Input Commitment sidecar remains non-authorizing. The earlier Worker 21 runner and results remain historical qualification evidence.

After execution, use the [retained-record consistency verifier](optional-evidence-contract.md) to check completeness, revision applicability, operation binding and the full retained synthetic effect population. Its versioned result is non-authorizing and narrower than independent policy or external-truth verification.
