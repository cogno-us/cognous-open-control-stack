# V1 extension evidence gate

Contract: `v1-reference-extension-evidence/1`.

The seven synthetic extension batches now run in one Linux workflow against an explicit source head. The former three-profile workflow remains available for manual diagnostics, but no longer repeats automatically on pull requests. No runtime test was removed.

| Batch | Required passing tests |
| --- | ---: |
| Environment prerequisites | 6 |
| Governed context/memory | 16 |
| Institutional review | 5 |
| Temporal refund | 7 |
| Context-bound action, including consumed-state restore | 12 |
| Independently authorized notification | 8 |
| SQLite staging recovery | 4 |
| **Total** | **58** |

Each batch retains environment observations, JUnit, demonstration outputs where applicable, component provenance where applicable, and a digest inventory of all files in its artifact directory. The recorder derives counts from actual JUnit test cases rather than trusting suite totals. Test identities must be unique and belong to the expected module. Missing cases, skips, failures and errors fail the batch contract.

The aggregate requires all seven batches, one exact source revision, the same current component-lock digest, complete unchanged inventories, successful scheduler status, supported environment observations and matching component provenance. It recalculates batch results. Unreported directories, duplicate batches, changed files and cross-revision combinations fail. Scheduler failure or cancellation cannot be hidden by otherwise complete artifacts.

The aggregate's 22 negative/unit checks use explicitly synthetic report fixtures; those fixture records are not represented as runtime execution evidence. The runtime batches supply the separate 58 executed cases.

For locally retained artifacts:

```sh
python tools/v1_release_evidence.py record --batch context-action --results-dir results/context-action-batch
python tools/v1_release_evidence.py aggregate --results-dir results/batches --revision FULL_EXECUTED_HEAD_SHA --jobs-status success
```

Recording expects `tests.xml`, `environment.json`, and the profile-specific paths used by the workflow. Each downloaded batch must occupy its own subdirectory of `results/batches`. Supply actual execution status, not a desired outcome. The CLI refuses to overwrite an existing batch report. The workflow pins checkout to the pull-request head so merge-ref artifacts cannot silently mix with head artifacts.

This gate establishes completeness and consistency of evidence from the trusted runner. Digests are not signatures, independent attestation, trustworthy custody or a defense against coherently forged artifacts. The gate does not independently re-execute every semantic predicate in each test or prove external truth.

A passing extension gate does not replace the existing default reference release, 35-scenario matrix, optional-profile qualification or evidence-consistency gates. The aggregate explicitly reports `full_default_release_qualified=false`, `authorizing=false` and `production_ready=false`. Release acceptance must consider the other applicable checks and the documented profile limits. No version tag or production deployment is created by this workflow.

Production identity/key custody, external destination semantics, context expiry during destination execution, default-path mediation, coordinated restore and deployment activation remain open as described in the existing profile contracts. This gate makes missing evidence visible; it does not turn those limitations into completed work.
