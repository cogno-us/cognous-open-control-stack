# Downstream documentation corrections

This integration workstream does not modify adjacent repositories. The following corrections should be made by their owners in later reviewable changes.

## cogno-us/alvorada

- Replace the GAX runtime dependency on `moltbot-safe/tests/test_safe_executor.py` with the supported public executor API in `engine.control_plane_adapter`.
- State the exact supported Moltbot producer revision in the GAX profile and generated provenance.
- Preserve PR #2 as deferred until its semantic concerns are resolved; do not describe it as accepted behavior.
- Keep the distinction between the Alvorada constitutional source and this experimental exchange workbench explicit.

## cogno-us/cognous-agent-replay-bundle

- Version/uprev the Moltbot producer profile before accepting evidence generated from `e8a4f8c...`.
- Do not relabel `6b0ba118...` producer evidence as a later executor revision without a tested compatibility migration.

## cogno-us/cognous-agent-governance-evidence-pack

- Advance the declared Moltbot producer revision only after Replay exposes the corresponding supported producer profile.
- Continue distinguishing source assertions, tested state and independent verification.

## cogno-us/moltbot-safe

- Keep OpenShell clearly optional/experimental until the live qualification gate passes on authorized infrastructure.
- Preserve the host-local constrained executor as the bounded public reference path while the OpenShell gate is unexecuted.

## Naming migration proposal

No rename occurs here. Documentation should use:

- **Alvorada Constitution** for `cogno-us/constitutional-governance-for-institutions`;
- **Alvorada Exchange Workbench** for `cogno-us/alvorada`;
- **Moltbot Safe** for the current executor repository/package, with any future product-neutral rename handled through an explicit compatibility migration.
