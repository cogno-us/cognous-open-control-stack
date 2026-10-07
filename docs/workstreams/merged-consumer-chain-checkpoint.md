# Merged consumer chain candidate checkpoint

Governed Exchange PR #14 is accepted at `a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf`. Evidence Pack PR #16 and ODES PR #31 are accepted at the exact revisions in [the candidate profile](../../profiles/merged-consumer-chain.json). All upstream final-head checks were green before their merges.

The attached Consolidated Engineering Recommendations calls for a reproducible bounded workflow before further expansion. This batch tests the actual merged components together in the hub; it does not repeat every component's already executed unit suite.

## Executed local evidence

- Recovery and authority: 19 tests passed in each of two isolated subprocess repetitions; no failures, errors or skips.
- Transported reference: two successful runs, one applied effect per fresh destination, retained Replay/ODES/Evidence Pack artifacts, no failed destination/lineage assertions, identical normalized outcomes.
- Gate validation: 8 tests cover missing, malformed, empty, skipped and failing evidence, successful evidence and timeout failure.

The existing recovery tests now accept explicit candidate lock and work-directory inputs. Their default inputs and assertions remain unchanged. The candidate requires exact merged dependency heads and rejects modified tracked Python/JSON inputs. New jobs are Linux-only, separated by recovery/transport and Python version. Each subprocess is limited to 150 seconds, with process-group termination on timeout; the job has a twelve-minute maximum. Nonempty evidence output directories are rejected to preserve prior results.

## Boundaries and next gate

This is candidate integration evidence, not the complete reference release matrix. `component-lock.json`, the existing acceptance matrix, and the reference-release workflow remain unchanged. The runner explicitly reports `full_reference_release_qualified=false`.

The selected GAX profile uses the existing bounded path in the newer producers. It does not enable atomic-claim execution or the refund-intent registry, combine their guarantees, establish external truth, authenticate production identities, or qualify distributed execution. The same-business-intent/multiple-operation-identity behavior remains visible in the reused research tests.

Next: reconcile the complete reference-release suite routing with this candidate's exact revisions, preserve its historical compatibility checks, and qualify the full matrix before proposing accepted lock advancement. Separate component and optional instruction-layer checks must not be treated as already executed by this integration batch.
