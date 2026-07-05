# Customer-Service End-to-End Example

A customer-service agent can read CRM records, search account notes, draft customer emails, and attempt outbound email sends.

The four-layer flow is:

1. Declare: Agent Action Manifest declares CRM read, account-note search, email draft, and email send. Email send requires authority and review.
2. Control: Agent Control Plane records allowed CRM read and account-note search. It records attempted email send as blocked because outbound-send authority is missing.
3. Replay: Agent Replay Bundle packages the run, including proposals, policy decisions, blocked action, authority context, reliance records, validation, redaction, and signature metadata.
4. Evidence: Agent Governance Evidence Pack summarizes the deployment for governance review.

The example is narrative-only in this hub repo. Concrete example files live in the component repositories or may be added later as cross-repo references.
