# V1 reference extension profiles

These explicit, isolated reference profiles extend the accepted bounded stack. They are public synthetic examples with executable controls and tests. They do not alter default authorization, migrate producer schemas, compose mutually exclusive executor databases, or establish production readiness. No proprietary reasoning or memory substrate is included.

## Run

Use Python 3.11 or 3.12 and install `pytest>=8,<10` and `pydantic>=2,<3`. Git/network access is needed only to obtain the exact accepted components for the temporal example.

```sh
mkdir -p results
python tools/reference_environment.py --profile ordinary-bounded --storage-dir results > results/environment.json
python tools/v1_reference_profiles.py --profile governed-context --results-dir results/context-1
python tools/v1_reference_profiles.py --profile institutional-review --results-dir results/review-1
python tools/v1_reference_profiles.py --profile temporal-refund --results-dir results/temporal-1
python tools/v1_reference_profiles.py --profile temporal-refund --scenario revoked --results-dir results/temporal-revoked-1
```

Example output directories must be new. SQLite databases and structured reports are retained. All reference clocks and identities are synthetic. Each temporal child process has a 90-second limit. Four separate Linux CI jobs exercise the profiles; tests have a 120-second limit. These are Linux/Python reference checks, with no additional Swift or mobile jobs.

## Environment and deployment prerequisites

Preflight records OS/kernel, architecture, Python and SQLite versions, selected profile, component revisions and lock digest. It exercises WAL, competing-writer exclusion and rollback using a disposable database in the supplied existing directory. It does not touch application databases or certify filesystem crash/power-loss behavior. Its competing connections are within one process; separate-process qualification remains the existing process-boundary suite. Exit 0 means these limited prerequisites were observed; exit 2 means unsupported or unverified prerequisites remain.

The report always leaves deployment qualification false. Filesystem locality, network mounts, host administrators, authority writers, identity/key custody, scoped credentials, backup/restore and incident ownership require deployment-specific evidence. Use [deployment responsibilities](v1-deployment-responsibilities.md) before selecting a pilot.

## Governed context and memory

`reference_profiles/context_memory.py` supplies a trusted-host local SQLite adapter. Admission stores immutable content identity, content hash, source reference, use restrictions, expiry and receipt in one transaction. Duplicate item IDs cannot replace prior content. Derived content can narrow purposes/recipients and expiry, and must retain parent obligations. Parent revocation or expiry prevents later recall of derived items. Host time must be finite.

Recall requires a current generation and exact allowed purpose/recipient. A delivery intent commits before a callback receives content. The result records delivered or unknown; a process crash can leave pending. No automatic redelivery occurs. The callback's successful return is an acknowledgement, not proof of hidden model reliance or downstream deletion. Content receipt and generation are available for future action-binding integration but are not yet bound into live Control Plane decisions.

Revocation blocks subsequent admission to delivery. A delivery already admitted may finish; later revocation does not retract disclosed content. This profile therefore does not claim atomicity between recall validation and an external recipient's use. Logical expiry removes content from the active table while preserving minimal receipt/history; it does not prove erasure from SQLite pages, journals, backups or recipients.

Only trusted host code may admit content, supply policy labels, configure recipients or access the database. Purpose and recipient labels are exact local rules, not jurisdictional legal compliance or cryptographic identity. Custody independence, protected encryption, context isolation across hostile agents, policy reevaluation, and Replay/AGEP/ODES export remain unimplemented in this profile.

## Temporal authority

`reference_profiles/temporal_refund.py` runs two independently approved synthetic refunds through the accepted Control Plane and atomic executor, with a deliberately sufficient shared grant budget. The second installment has a different amount/payload, proposal, approval, decision, effect ID and claim. Sharing an explicit bounded grant does not permit sharing a consumable claim.

Seven cases cover valid continuation, grant revocation, policy change, evidence expiry, stopping undispatched continuation after a cancellation request, unknown acknowledgement of the first step, and attempted first-claim reuse. Invalidation before the second commit prevents it; the first committed effect remains historical. Unknown acknowledgement holds the continuation and grants no retry. A recorded cancellation request is not acknowledgement, verified cessation, rollback or compensation authority.

This profile intentionally uses the existing refund adapter. A refund/notification trajectory needs an independently specified notification adapter and its own authority contract. Remote callbacks, delegation, distributed workflow budgets, crash-resumable scheduling and corrective-action execution remain outside this profile. The trajectory report is retained after the scenario completes; it is not a durable coordinator journal capable of resuming interrupted runs.

## Institutional review

`reference_profiles/institutional_review.py` retains assessments, proposals and explicit reviewer dispositions. Assessments scope the task, evaluator, criteria, evaluation period and evidence references. Competence, authority validity and boundary compliance remain separate typed dimensions. Expansion, contraction, restoration and retention are proposals only. Later favorable observations cannot silently remove critical incidents: an accepting review must reference explicit dispositions for every retained critical incident in that scope.

The configured reviewer set is a trusted-host fixture, not production authentication. Evidence and incident-disposition references are retained, not independently verified. Accepted, rejected and deferred reviews remain in history. Review records never mutate or issue runtime grants; competent institutional adoption and subsequent grant issuance are separate deployment actions. No score automatically expands, contracts or restores authority.

## Coverage and open requirements

| Workstream | Implemented reference coverage | Remaining work |
| --- | --- | --- |
| Environment assurance / RS02 | Observed runtime and limited SQLite prerequisites, exact lock identity | Deployment-specific filesystem, identity, isolation, credentials and recovery qualification |
| IF02, IF06, MG01, MG02, GC 3–5 | Durable receipts, retained restrictions, generation checks, pre-delivery record and outcome | Live action-binding integration, independent custody, legal jurisdiction rules, protected recipient enforcement |
| TCR-1–5 and TCR-8 | Two independently authorized local consequences, fresh claim checks, preserved prior effects and held uncertainty | General trajectory matrix, remote consequences, delegation and crash-resumable orchestration |
| TCR-6 and TCR-7 | No false cancellation/compensation claims; undispatched work can be held | Cancellation acknowledgements, verified cessation and separately authorized corrective effects |
| DA R1–R8 | Scoped separate assessments, immutable history, mandatory incident dispositions, explicit review, no grant mutation | Actual competent institutions, identity/custody, adopted review rules and grant-lifecycle integration |

These are partial source-requirement mappings, not blanket closure or paper conformance. The existing default release, optional execution profiles and evidence-consistency contract retain their own acceptance evidence. Passing one profile does not transfer proof to another.
