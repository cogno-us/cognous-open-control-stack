# OCS October 31 MVP package: index (2026-10-24, point-in-time)

Status: DRAFT, non-authorizing index. It points to records; it creates no verdict. Nothing here is a Qualification verdict, an independent acceptance, a freeze, a security clearance, a certification or a production-readiness claim. Qualification owns oracles and verdicts. Release, publication and production remain on HOLD.

Labels: VERIFIED = read or computed by the author of this index in this session. REPORTED = stated by a record, PR body or operator message, not re-run. Every Qualification-side head below is point-in-time: heads move and must be re-read before use.

Hub base for this index: `main` 76619838 (merge of hub PR #233). The candidate manifest names its own hub revision; the two are different things.

## 1. Candidate manifest

| Item | Location | Note |
|---|---|---|
| Candidate manifest | [candidate-manifest.json](candidate-manifest.json) | One exact tuple, UNQUALIFIED and provisional. Supersedes the draft by name |
| Earlier draft (kept) | [candidate-manifest-draft-2026-10-24.json](candidate-manifest-draft-2026-10-24.json) | Historical; not edited |
| Validator | `tools/mvp_candidate_manifest/validate_candidate_manifest.py` | `python -I tools/mvp_candidate_manifest/validate_candidate_manifest.py` (offline); `--online` also checks ancestry (needs `gh`); `--print-sha256` prints the manifest byte digest |
| Validator test | `tests/test_mvp_candidate_manifest.py` | Run with the full hub suite |
| How to validate, what is not claimed | [README.md](README.md) | Section "Candidate manifest: how to validate it, and what it does not claim" |
| Source inventory | [source-inventory.md](source-inventory.md) | Tuple revisions, CI, previous tuple |
| Supported capabilities and limitations | [supported-capabilities-and-limitations.md](supported-capabilities-and-limitations.md) | |
| Qualification initiation | [qualification-initiation.md](qualification-initiation.md) | |

Tuple recorded in the manifest at hub `main` 76619838 (VERIFIED by reading the file; full 40-hex values are in the manifest, which is the record):

| Component | Revision (short) |
|---|---|
| control_plane | 7a4bcd40 |
| runtime | c5e97e87 |
| replay | 40012b8c |
| evidence_pack | 7b9511f2 |
| odes | 1a5e1d30 |
| action_manifest | fa170815 |
| verifier | c0b8ba1f (39d46b49 is a later documentation revision, not the pin, not implicitly covered) |
| hub (as named by the manifest) | c897266b |

Route C (`cognous-governed-exchange`) is excluded and not invoked. The historical Hub `component-lock.json` is stale and does not describe this tuple.

## 2. Registry catalogue

| Item | Location | Note |
|---|---|---|
| Catalogue manifest | `docs/mvp-recovery/registry/catalogue-v0.1/manifest.json` | File sha256 (VERIFIED at 76619838): `5a91ff1a1da2dde440ec10852ad3818b5205ae09e55f59bc7904a9130afd0123` |
| Catalogue manifest digest recorded by the candidate manifest | candidate manifest `registry_catalogue.manifest_digest` | `sha256:d6c768c9daae6c31e9c8e5a184f6ddb56f76733ab86cda009f2fb771f00c8057`, status superseded-pending, successor `sha256:22f49fd1341cfaa6e46727db9b6153c2073b82a3125fd725173494f3ebb37650` (association only). The catalogue digest is an RFC 8785 canonical-JSON digest, a different quantity from the file sha256 above; re-read the manifest for the current value |
| Generated reports | `docs/mvp-recovery/registry/reports/generated/` | `catalogue-integrity-report`, `governance-coverage-report`, `denominator-report` (`.json` and `.md`); each names the manifest digest it was generated against. Freshness check: `generate_reports.py --check` |
| Per-class reports | `docs/mvp-recovery/registry/catalogue-v0.1/reports/` | |
| Overlays | `docs/mvp-recovery/registry/overlays/mvp-linked-q8.json` | MVP-linked classifications; informational |
| Registry README | `docs/mvp-recovery/registry/README.md` | Layers, hashing, size policy |

The catalogue is informational: authority none, activates nothing.

## 3. Ingress boundary

| Item | Location |
|---|---|
| Boundary description | `tools/mvp_ingress/BOUNDARY.md` (sha256 recorded in the candidate manifest) |
| Launch form (the only supported start command) | `python -I -B tools/mvp_ingress/launch.py --state-dir DIR --socket PATH --control-plane ROOT --runtime ROOT --allow-uid UID` |
| Environment profile | `docs/mvp-recovery/ingress-qualification-environment-profile.md` |
| Environment record (development container, 2026-10-23) | `docs/mvp-recovery/ingress-env-record-dev-container-2026-10-23.json` |
| Capture script | `tools/mvp_env_record/capture_env_record.py` |

`--allow-uid` is mandatory and repeatable; the ingress refuses to start without it. `python -m tools.mvp_ingress.server` is not a supported entry point. `-B` keeps bytecode out of the ingress tree, which the validator refuses to contain. Host process isolation under the restricted-host profile is a limitation; see section 4 and the Post-MVP list. This change touches neither `tools/mvp_ingress` nor `tools/mvp_env_record`, so the candidate identity is unchanged by it.

## 4. Known limitations

Record: `docs/mvp-recovery/architect-rulings-3-and-known-limitations.md`. Read sections 1 to 6 together:

1. Rulings 1-8 and dispositions (NC1-04 revocation, NC4-03 `**` predicate, Verifier limitations, second execute after lost acknowledgement, route C and SCN-D09, ODES export, claim-journal and route-B CI, trusted-host boundary).
2. Known limitations and defect register.
3. Critical path, Oct 24-31.
4. What the record does not do.
5. Addendum 2026-10-24: record of the prior authorization of Runtime PR #144.
6. Addendum 2026-10-24: recorded limitations of the isolated ingress launcher.

Also: [supported-capabilities-and-limitations.md](supported-capabilities-and-limitations.md).

## 5. Architect rulings records

- `docs/mvp-recovery/architect-rulings.md` (first set)
- `docs/mvp-recovery/architect-rulings-2.md` (second set)
- `docs/mvp-recovery/architect-rulings-3-and-known-limitations.md` (third set)
- Context: `docs/mvp-recovery/mvp-definition.md`, `qualification-contract.md`, `scope-reduction-register.md`, `critical-path.md`, `implementation-status-2026-10-23.md`

## 6. Dependency lock

| Item | Value |
|---|---|
| File | [requirements-mvp-py313.txt](requirements-mvp-py313.txt) (install with `--require-hashes`) |
| sha256 (VERIFIED at 76619838) | `84caee9ea5fcc297270d1b0a8c68f279e849c814b8052b2a54bb618bd9ef9ff5` |
| Pins | pydantic 2.13.5, pytest 8.3.5, cryptography 50.0.0 |
| Description | [dependency-manifest.md](dependency-manifest.md) |

Any byte change to the lock is a new candidate and requires a successor manifest. The candidate manifest also records an association with a Qualification lock of the same sha256 (REPORTED).

## 7. Qualification-side references (point-in-time)

Repository `cogno-us/cognous-stack-qualification`. States read by REST on 2026-10-24 (VERIFIED metadata unless marked REPORTED); re-read before relying on any of them.

| Reference | State at read | Revision | Note |
|---|---|---|---|
| Qualification `main` | | 8087363b9f56f273422e799b2fb6ebc80e789e16 | Merge commit of #223 at read time |
| PR #223 | merged 2026-10-24T17:36:40Z | head 0f11f424992b274755baf08006b46d8270f0bdcf; merge 8087363b9f56f273422e799b2fb6ebc80e789e16 | MVP acceptance job, route C exclusion checks, lost-ack assertions. Hub PR #223 is a different PR |
| PR #226 | merged 2026-10-24T17:32:03Z | head 94fc06bd60ae1875f7be719d0edb2ce76fe0f14e; merge 976a8373a175addacad04cebabbaaea8d42406b8 | MVP tuple pin. Hub PR #226 (pytest bump) is a different PR, closed |
| PR #225 | open, draft | head 9456ee10bfc1166dbcafd107196e2717e72e05c6 | Proposed expectations v7 (v6 plus NC7-01..03); not frozen. v7 file `process/mvp-chain/expectations.proposed.v7.json`, sha256 computed by the author from the file at that head: `0dc17a1984e1c3c153f3cb6e3f7fdd4dad87cdc4414728a20df0f8174e402f6b` |
| Commitment values | REPORTED | | `candidate_identity_inputs_sha256` 0ef8f3fd590bfbc58172735c05aca3b95a97c8dea7af59383c7cf4a938461aa6 and `tuple_pin_sha256` bde38aa8aacedf17bf071904aa6dd401d72321ac845567e9551ffdfb6590f4f7, as recorded in the candidate manifest against earlier draft heads; not re-derived, not frozen, may no longer match. `candidate_commitment_sha256` is null in the manifest (Qualification records it) |
| Successor profile proposal | proposal, in #225 | same head as #225 | `process/mvp-acceptance/trusted-host-successor-profile.proposed.md` and `environment-profile.trusted-host-successor.proposed.v1.json`; proposal only |
| Reviewer designation record | proposal, in #225 | same head as #225 | `process/governance/qualification-reviewer-designation.proposed.md`; not adopted |
| Baseline record | prepared, not adopted | same head as #225 | `process/governance/qualification-baseline.proposed.md` |
| Proposed manual runbook and report template | proposal, in #225 | same head as #225 | `process/mvp-acceptance/manual-execution-runbook.proposed.md`, `report-template.proposed.md` |

Nothing in this table is a Qualification verdict. Whether #225 content is adopted is Qualification's decision.

## 8. Final report skeleton

[final-report-template.md](final-report-template.md): the October 31 report skeleton with four separate layers. Post-MVP and deferred items are listed at the end of that file.

## Erratum 2026-10-31 (QGATE-05, R-01/R-02/R-05; append-only, text above unchanged)

Line 103 (`candidate_identity_inputs_sha256` 0ef8f3fd..., `tuple_pin_sha256` bde38aa8...) is stale. Recomputed at Qualification `56a618eb`: identity inputs `e7484a0afa1758b3925801ae6cf70a718f676eaa593addb9c20d739b9654c7fb`, tuple pin `efe9be3eb3a2c68121f9dc1203a5af2d194b24989c617a9029d09b1ccf25844b` (freeze-reconciliation.md section 2). The statement in the 2026-10-24 manifest that the Control Plane and Runtime pins "are the main head" was true on 2026-10-24 only; current heads (Control Plane `b19c47dd`, Runtime `f7a55e2a`, Verifier `39d46b49`) are information only and are never substituted for the pins. The historical manifest is unchanged; the dated successor is `docs/mvp-package/candidate-manifest.successor-2026-10-31.json` (built and checked by `docs/mvp-recovery/qgate-05/build_successor_manifest.py`). Component lock unmoved; qualification tuple is not the lock.
