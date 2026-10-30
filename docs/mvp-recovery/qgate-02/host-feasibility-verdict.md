# QGATE-02 D2: host feasibility verdict

Non-authorizing. Not qualification, not certification, not a host designation. No weaker profile adopted; no successor profile selected; D3/D4 unapproved; candidate PROVISIONAL, UNFROZEN, UNQUALIFIED.

## Verdict: INCONCLUSIVE

Reason (exact): the single authorized run (https://github.com/cogno-us/cognous-open-control-stack/actions/runs/41125818207) ended in job failure, and its raw observations (job log, artifact `13010567298`, digest `sha256:412eb8649a05ff272c17b932c002920e5da2e5ccebd13be59321849f0d211c3f`) could not be read by the builder because the session egress policy denies the blob host that serves them. The required properties therefore "cannot be adequately observed or established" by this deliverable. This is **not** a finding about the GitHub runner: nothing here shows the runner satisfies, or fails, the original profile. The failed step's cause is unestablished (see the evidence reference).

## Requirement matrix (H-01..H-30 from `host-profile-requirements-matrix.md`)

| Result | Requirements |
|---|---|
| PASSED | none |
| FAILED | none |
| UNKNOWN (all 30) | H-01..H-30: no runner observation is recorded in this PR |

Of these, H-13 (Yama `ptrace_scope >= 1`, absent = UNSUPPORTED) is the decisive environment property and is UNKNOWN. Per the matrix, ingress/launcher/pin/envelope rows (e.g. H-05, H-07, H-08, H-11, H-19, H-24..H-30) were never observable in this run by design: no ingress, no pinned Control Plane/Runtime checkouts were authorized.

## Recommendation (no automatic action)

Do not provision a replacement and do not adopt a weaker profile. The cheapest way to close the question without a second run: the operator downloads artifact `13010567298` from the run page (it expires 2027-01-28) and attaches it to a session, so the existing records can be read and this verdict re-derived. A second workflow run needs an explicit new authorization (the workflow aborts under `bash -e` before its checksum step if the capture script exits non-zero; a fix would be a new, separately authorized change). A dedicated isolated Linux VM is recommended only if the recovered observations show Yama absent or unmodifiable on the runner (the operator has stated the project is not provisioning a Yama host, so that choice stays with the Architect/operator).

## Non-certification disclosure

All review here is AI, same-lineage, builder-spawned. The D1 Qualification Owner and Adversarial Evidence Reviewer roles are NOT YET INSTANTIATED (see `role-assignments/README.md`). Q7 formal independent certification: NOT ESTABLISHED.
