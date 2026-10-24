# Dependency manifest: supported environment (Linux, CPython 3.13, single host)

Status: DRAFT, non-authorizing. Not a Qualification environment record; the environment record is captured in the run by Qualification. Label: VERIFIED for the install and import checks below (run 2026-10-24 on a Linux x86_64 host, CPython 3.13.16); the pins themselves are REPORTED from the Qualification files named.

## What the MVP chain installs

The Qualification workflow `mvp-acceptance.yml` (draft PR #223, head `df4c6b76`) runs `python -m pip install --require-hashes -r .github/locks/cryptography-pydantic-pytest-a9a750.txt` on CPython 3.13 and nothing else; the component repositories are checked out at exact shas and put on the path, not pip-installed. The lock is reproduced byte-for-byte here as [requirements-mvp-py313.txt](requirements-mvp-py313.txt) (sha256 `84caee9ea5fcc297270d1b0a8c68f279e849c814b8052b2a54bb618bd9ef9ff5`).

| Package | Pin | Why |
|---|---|---|
| pydantic | 2.13.5 (pydantic-core 2.46.5, annotated-types 0.8.0, typing-extensions 4.16.0, typing-inspection 0.4.4) | Control Plane declares `pydantic>=2.12`; 2.11.9 gives false Verifier refusals (REPORTED); the workflow asserts `>= 2.12` |
| pytest | 8.3.5 (pluggy 1.7.0, iniconfig 2.3.1, packaging 26.3) | runs the mandatory battery and the gate tests |
| cryptography | 50.0.0 (cffi 2.1.1, pycparser 3.11) | Control Plane optional `runtime-authority` extra (`cryptography>=43`) |

Component declarations read at the final tuple shas (Evidence Pack's optional `replay` extra names Replay `40012b8c`, the tuple's Replay): Control Plane `pydantic>=2.12`; Evidence Pack, Replay, Action Manifest `pydantic>=2.0`; Verifier no runtime dependencies (stdlib only, enforced by its tests); ODES `jsonschema>=4.21`, which is not in the lock because the chain never imports ODES (the tuple records it as pin-checked only). The Runtime has no `pyproject.toml`; its `CLAUDE.md` test command installs `pydantic==2.11.9`, below the MVP floor, so the Runtime's documented component test environment is not the MVP environment.

The Qualification gate itself uses the standard library only.

## Install check (VERIFIED)

Clean venv, `python3.13 -m venv`, then `pip install --require-hashes -r requirements-mvp-py313.txt`: installed without error; `pip freeze` matches the table (pydantic 2.13.5, pytest 8.3.5, cryptography 50.0.0). In that venv:
- `tools/mvp_acceptance_gate.py resolve` and `preflight-hub` ran (with `hub_revision` `5b76c58a`, whose capture script has the pinned sha256 `5ae7beca645bf9cf6676c77996656ba7cdaaf4e5413c8c69741e1c7f269f1a51`).
- `tests/test_mvp_acceptance_gate.py` at Qualification `df4c6b76`: 114 passed.
- `pytest --collect-only` of the battery: 45 tests in `suites/mvp-chain` (3 modules) and 6 in `suites/mvp-applicability`, collected without import errors.
- Components at the final tuple shas (Control Plane `7a4bcd40`, Runtime `c5e97e87`, Replay `40012b8c`, Evidence Pack `7b9511f2`, ODES `1a5e1d30`, Verifier `c0b8ba1f`, Action Manifest `fa170815`, hub `5b76c58a`) import (`agent_control_plane`, `engine`, `agent_replay_bundle`, `agent_governance_evidence_pack`, `odes`, `cognous_verify`, `agent_action_manifest`, `tools.mvp_ingress`) from pristine checkouts, each at its pinned sha with a clean tree (VERIFIED, 2026-10-24, CPython 3.13.16, pydantic 2.13.5).
Not run: the full battery. It needs root, the dedicated `mvp-ingress`/`mvp-client` users, `kernel.yama.ptrace_scope >= 1` and a live ingress; that is Qualification's run, not this record's.

## Regenerate

The lock was compiled by its header command: `uv pip compile .github/locks/cryptography-pydantic-pytest-a9a750.in --universal --generate-hashes --python-version 3.11 --no-annotate` from inputs `pytest==8.3.5`, `pydantic==2.13.5`, `cryptography==50.0.0`. A change to any pin is a Qualification-owned change to a committed file (the lock is under the candidate commitment) and a new candidate. Verify with `python3.13 -m venv v && v/bin/python -m pip install --require-hashes -r requirements-mvp-py313.txt && v/bin/python -m pip freeze`.

## Limits
- Hash-locked for the package set only; the OS, kernel, Yama setting and interpreter build are captured by the in-run environment record, not by this file.
- Python 3.11 and 3.12 are not qualified for this profile; a 3.12 result is supplementary only (ruling 6).
