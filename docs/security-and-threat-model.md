# Security and threat model

This document describes the bounded public reference candidate. It is not a production security certification.

## Protected properties

The reference workflow is designed to preserve:

1. **Authority provenance** — request content cannot mint institutional authority.
2. **Action binding** — actor, principal, institution/domain, manifest, action, adapter, target, payload, permissions, amount, and effect identity cannot be materially substituted after authorization.
3. **Effect uniqueness** — retry/recovery preserves stable `effect_id`; each delivery attempt receives its own `attempt_id`.
4. **Evidence lineage** — Replay, ODES and Governance Evidence Pack remain derived evidence and do not create permission.
5. **Continuity integrity** — duplicate, stale, divergent and digest-tampered successor state is rejected or left unresolved.
6. **Truthful uncertainty** — unknown delivery, partial effects and unavailable observations remain unresolved rather than being promoted to success.

## Trust boundaries

| Boundary | Trusted input | Untrusted / insufficient input |
|---|---|---|
| GAX recipient | configured sender/recipient route and retained transport record | message prose, caller authority claims |
| Authority resolution | institution-scoped resolver/status records | proposal fields alone |
| Control Plane | pinned manifest + current authority/evidence/policy state | prior decision after relevant state changes |
| Moltbot Safe | exact bound Execution Envelope + local execution policy | altered target/payload/adapter or caller institution label |
| Replay | validated producer records and explicit links | reconstructed narrative as proof of effect |
| Evidence Pack / ODES | validated upstream artifacts | schema validity as approval, compliance or authority |
| BitRep / Index | verified signature / chain inclusion under declared profile | authorization to execute an action |

## Threats covered by the acceptance matrix

The pinned tests exercise identity and route substitution, payload/target/adapter substitution, forged/copied evidence, stale/revoked authority, policy change after decision, replay/duplicate delivery, lost acknowledgement, process interruption, partial effects, tampered lineage, malformed test provenance and failed test attribution.

## Residual risks and production gaps

The reference candidate does **not** establish production institutional identity, production key custody, distributed revocation propagation, host/network isolation, live OpenShell confinement, fleet coordination, distributed budgets, independent destination verification or operational incident response.

Those are separate deployment capabilities. They require named owners and deployment-specific acceptance tests before a production claim is valid.

## Failure posture

Where state cannot be established safely, the expected posture is deny, hold or unresolved. Recovery must reconcile the existing `effect_id`; it must not mint a replacement effect merely because acknowledgement or evidence persistence failed.
