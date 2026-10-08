# Deployment review packet

Contract: `deployment-review-packet/1`. This optional local checker makes missing
deployment evidence visible before a competent owner reviews a bounded pilot.
It checks declared scope, retained bytes, dates and responsibility coverage.
It does not evaluate whether a document proves its associated responsibility.
Even a complete packet has `authorizing=false` and `production_ready=false`.

## Run

Use Python 3.11 or 3.12; no third-party dependencies, network, credentials or
component installations are needed. Work on a trusted, quiescent local copy.

```sh
python tools/deployment_review.py examples/deployment-review/packet.json \
  --lock component-lock.json \
  --expected-revision 649df22a1392af2c4fa77e4c71749c482f82649c \
  --evaluated-at 2026-10-08T01:00:00Z
```

The committed template deliberately exits **2**, because all ten deployment
responsibilities are missing. It is not a completed pilot. Copy it to protected
local storage before filling in owner references and real evidence. Do not
commit customer records, credentials, private source material or key material.
Use a reviewed, non-secret configuration descriptor rather than a secret-bearing
configuration file. For a new source/lock/environment/configuration selection,
recollect applicable evidence and update the declared scope; do not merely
relabel old evidence to force a pass.

Exit 0 means only that the review packet passed these structural checks at the
supplied evaluation time. Exit 2 means missing or invalid input/evidence. The
tool prints JSON to stdout and does not write files, activate profiles, contact
destinations, issue grants or change accepted pins. Archive reports through the
deployment's existing custody process; this tool provides no custody service.

## Input contract

Top-level fields are exactly `contract`, `deployment_id`, `environment_id`,
`profile`, `source_revision`, `component_lock_sha256`, `configuration` and
`responsibilities`. Unknown fields and duplicate JSON keys are rejected.
Profiles are `ordinary-bounded`, `atomic-authority-effect` and `refund-intent`.
`source_revision` must match the separately supplied 40-character expected
revision. The lock digest is SHA-256 of the exact separately supplied lock bytes.
Neither comparison discovers what is actually deployed on a host.

`configuration` is a file reference with exactly `path` and `sha256`. References
use relative POSIX paths beneath the packet directory. Absolute paths, parent
traversal, URLs, symlinks, missing/empty files and files over 8 MiB are rejected.
The packet and lock are also bounded to 8 MiB. Files are checked but their contents
are not copied into the output report. The output retains declared scope and
owner-independent responsibility identifiers, not evidence payloads.

There must be exactly one entry for each responsibility from
[deployment responsibilities](v1-deployment-responsibilities.md):

| Identifier | Accountable role |
| --- | --- |
| institutional-authority | Customer authority owner |
| identity-key-custody | Security owner |
| host-writer-boundary | Platform owner |
| profile-selection | Integration owner |
| data-context | Data owner |
| destination-contract | Adapter owner |
| backup-restoration | Operations owner |
| incident-response | Operations and authority owners |
| useful-outcomes | Pilot owner |
| release-acceptance | Release owner |

Each entry contains exactly `id`, `owner_ref`, `status` and `evidence`. A complete
entry needs a nonempty accountable-owner reference, status `provided`, and 1–20
evidence items. The template's `missing` entries remain blockers. There is no
`not_applicable` or waiver route that silently removes a responsibility. A
different responsibility set requires a separately reviewed contract version.

Each evidence item contains exactly `file`, `scope`, `observed_at` and
`expires_at`. File references use the format above. `scope` must match all six
values: deployment ID, environment ID, selected profile, source revision,
component lock digest and configuration digest. Dates use exact UTC
`YYYY-MM-DDTHH:MM:SSZ`; observation must be no later than evaluation, and expiry
must be strictly later. No clock tolerance is assumed. A supplied evaluation
time is reproducible input, not a trusted-clock attestation.

```json
{
  "file": {"path": "evidence/restore-report.json", "sha256": "<64 lowercase hex characters>"},
  "scope": {
    "deployment_id": "pilot-a",
    "environment_id": "staging-a",
    "profile": "atomic-authority-effect",
    "source_revision": "<40 lowercase hex characters>",
    "component_lock_sha256": "<64 lowercase hex characters>",
    "configuration_sha256": "<64 lowercase hex characters>"
  },
  "observed_at": "2026-10-08T01:00:00Z",
  "expires_at": "2026-10-09T01:00:00Z"
}
```

The placeholders above are explanatory and deliberately invalid. Set evidence
expiry according to the adopted deployment policy; this checker neither supplies
that policy nor infers freshness from a filename. Repeating a file within one
responsibility fails; sharing a document across responsibilities is permitted
but establishes neither independent evidence nor semantic coverage.

## Assurance and adoption boundary

Owner identities, issuer signatures, reviewer competence and separation, custody,
external truth, policy sufficiency and actual host/configuration equivalence are
not verified. Coherently forged/relabelled files can pass structural checks.
Symlink rejection is input hygiene on a trusted host, not a race-proof filesystem
sandbox. Concurrent hostile filesystem changes and direct host access are outside
this profile. Logical expiry of a packet does not erase retained files.

This supports parts of RS02, ES05 and RS12 as review preparation. It does not
close those addenda, qualify production deployment, or replace reference-release
and v1-extension gates. The deployment owner must assess substantive evidence,
resolve remaining risks and obtain competent approval through the adopted
institutional process. Approval still does not substitute for runtime grants.
