# Worker 18 — documentation evidence alignment

## Starting state and scope

Starting/accepted hub SHA: `f8afac8fae9ebcedb207c46cdaba51728a918d5b`.
Branch: `worker18/documentation-evidence-alignment`.
The final commit SHA and one-time final-head CI observation are recorded in the
PR handoff (a commit cannot embed its own SHA).

Read CONTRIBUTING.md and GOVERNANCE.md; no hub AGENTS.md was present. Inspected
README, lock, architecture, compatibility, release status, evidence index, both
quickstarts, risk register and accepted recovery/process/late-commit/integration
checkpoints. Runtime/runner/workflow sources were read to audit commands.
No uploaded DOCX or private research content was used or edited.

At initial inspection, main matched the supplied baseline and the only open hub
PR was draft #8, head `e6f8f8e73666f9cf6758a40caeaaa8897a735ff1`.
Its persistence-adoption checkpoint was read as a proposal, not accepted hub state.
Remote main and branch heads are rechecked before publication; changes must be
reconciled without overwriting concurrent work or force-pushing.

Read-only component clones matched supplied accepted revisions:
Control Plane `248d899634d9db3518e831bc7ab568a48733f825`, Replay
`043830b56595cecddfa65c064afd1c0b95e64792`, Moltbot Safe
`12b9c55637e2472a1a5ce3036c787e9427c6abd8`, and Alvorada
`c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df`. Component acceptance is
kept separate from hub selection. No pending ODES/Evidence Pack/GAX changes were
consumed or anticipated.

## Changed paths and claim corrections

| Paths | Correction and evidence |
|---|---|
| `README.md`, `docs/overview.md` | Engineer/reviewer entry point and synthetic refund; four artifact layers no longer presented as the whole integration. Sources: lock and transported runner. |
| `docs/architecture.md` | Explicit component/transport responsibilities, separate constitutional repository and workbench, optional layers and no authority from signatures/receipt. Sources: selected contracts and runner. |
| `docs/release-status.md`, `docs/compatibility.md` | Mechanism vs execution vs selection; unselected persistence/Replay/image/readiness acceptances and production gaps. Sources: exact upstream checkpoints linked in status and unchanged lock. |
| `docs/evidence-index.md` | Latest selected-pin full/research evidence is Worker 14d; earlier accepted and failure snapshots retain their provenance. Sources: actual pins/source hashes in each generation. |
| `docs/recovery-semantics.md` | Revalidation, unknown acknowledgement, accepted/rejected observations, absence without retry, original reconciliation, current denial versus historical effect and derivative lineage. Sources: Worker 14d summary/checkpoint and separate late-commit/process evidence. |
| `docs/quickstart.md`, `docs/governance-quickstart.md` | Prerequisites, checkout/root, venv/agep PATH, dependency access, results/work-directory replacement behavior and evidence review. Sources: runner and CI inspection. |
| `docs/downstream-readme-corrections.md` | Replaces stale hub profile-1.0.0 status with owner follow-ups; records stale component README claims, naming/navigation gaps and link-audit limits. Sources: exact component revisions above. |
| This checkpoint | Scope, checks and handoff record. |

Historical evidence/checkpoints, lock, runtime code, tests, shared release runner,
acceptance matrices and machine-readable risk register remain unchanged. No adjacent
edits, renames, licensing changes, deployments or self-merge.

## Executed checks and limitations

- `python tools/reference_release.py --help`: passed; actual CLI options checked.
- Scratch-only Markdown check: local file targets and heading anchors in changed
  documents checked; fenced bash blocks parsed using `bash -n`.
- `git diff --check`: passed before publication.
- Component README relative-file check: no missing targets across Alvorada,
  Moltbot Safe, Replay and Control Plane. Clone access verifies repository
  reachability, not every external HTTP link/anchor. No confirmed broken external
  URL is claimed; unverified external targets remain outside the audit scope.
- `python -m pytest -q tests/test_release_gate.py`: initially unavailable because
  pytest was absent. Installed pytest in a scratch-only dependency path, then ran
  with `PYTHONPATH=/tmp/worker18-doc-check-deps`: **6 passed, 68 setup errors**.
  The shared real-transport fixture needs the pinned producer environment; direct
  diagnosis reports `ModuleNotFoundError: experiments`. `.reference-work` and
  runner import wiring were not initialized in this docs-only checkout. This is
  an unsuccessful suite attempt, not a regression pass or new stack qualification.
  No tests were changed, skipped or weakened.
- Environment: Python 3.12.14, Node 24.19.0, npm 11.9.0. CI's Python 3.11/Node 20
  setup and full quickstart execution were not reproduced; end-to-end verification
  here is unavailable. Earlier evidence is not relabeled as this worker's run.
- GitHub-rendered visual QA is unavailable locally; tables, fences and links were
  inspected statically. Final-head CI is checked once after publication, reported
  as observed, and not polled to completion.

## Remaining owner work

See the [follow-up register](../downstream-readme-corrections.md) for stale Moltbot
profile heading, Replay legacy-only pin list, workbench navigation, image-checkpoint
navigation and risk-register metadata. No adjacent-repository correction or
machine-readable integration update is included. Live OpenShell confinement,
production authority, remote finality and distributed guarantees remain unqualified.
Equivalent business intent under different valid proposals can produce multiple
effects; effect-ID deduplication is not business-intent deduplication.
