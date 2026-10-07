# Governance reviewer quickstart

Begin with [support status](release-status.md) and the [responsibility map](architecture.md).
The public reference uses synthetic authority fixtures. It does not adopt an
institutional constitution, authenticate a production resolver or establish
regulatory compliance on an organization's behalf.

For one synthetic refund, inspect these questions:

1. **Who supplies authority?** The Authority Context is resolved independently
   of the incoming message. Identify the institution, mandate, grant, approval,
   policy and evaluation time; a signature or message receipt cannot create them.
2. **What was proposed?** Check the Manifest-bound operation, target, amount,
   unit and payload commitment against the retained proposal.
3. **What was allowed at effect time?** Inspect the Control Plane decision and
   revalidation. Historical authorization is not permission for a new request.
4. **What happened at the destination?** Separate attempt, acknowledgement,
   accepted observation, rejected evidence and unresolved delivery. Use the
   [recovery rules](recovery-semantics.md), especially after timeout or absence.
5. **Can the record be traced?** Follow original identities and commitments through
   Replay, Evidence Pack and ODES; distinguish original artifacts from derivatives.
   Their validation is not independent real-world verification.
6. **What remains to be qualified?** Review the [risk register](../residual-risks.json)
   alongside current support status and the exact evidence pins. Do not apply a
   newer component's guarantees to the selected hub automatically.

Use the [developer quickstart](quickstart.md) to run the reference and the
[evidence index](evidence-index.md) to review existing runs. The output is input
to human governance review; it does not amend policy, confer authority or approve
deployment. Institutional adoption, credential custody and revocation propagation
require separate organizational decisions and deployment-specific evidence.
