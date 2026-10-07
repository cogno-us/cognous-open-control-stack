# Authority/effect race qualification evidence

This directory is reserved for Worker 19 retained qualification material.

The executable evidence is produced by:

```bash
python tools/authority_effect_race_qualification.py run \
  --results-dir results/authority-effect-race
```

The dedicated GitHub Actions workflow uploads the complete
`authority-effect-race-qualification` artifact, including:

- `summary.json`;
- two isolated repetitions;
- JUnit XML;
- pytest logs;
- per-scenario JSON with ordered events, authority observations, dispatch
  status and authoritative destination state; and
- per-run matrix-gate results.

No precomputed pass result is committed here. The branch was constructed in an
environment that could inspect and modify the repositories through the connected
GitHub interface but could not resolve `github.com` from the local execution
container. Exact-pin runtime results must therefore come from the PR workflow and
must not be inferred from source inspection.
