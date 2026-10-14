# Cognous Open Control Stack security scan scope

## Purpose and boundaries

This public repository is an integration and evidence hub with optional synthetic
reference implementations for agent authority, execution admission and audit.
It is not a deployed SaaS product. Production deployment and reference release
authorizations remain false; operational trust is HOLD / NOT ESTABLISHED.
Do not interpret synthetic qualification, benchmark wins or enrollment as
independent security acceptance, production readiness, or remote isolation.

The Docker image contains the public hub checkout at /src. It installs the
Python dependencies for local reference profiles and runs their tests. It does
not fetch the separate repositories in component-lock.json. Review the hub's
source and tools; do not represent this as scanning all component histories or
the selected integrated chain. External component enrollment is separate.

## Untrusted inputs and security properties

Prioritize reference_profiles/protected_destination.py, assurance_runtime.py,
trust_evidence.py, federated_governance.py and operational_state.py. These process
structured requests, signatures, supplied identifiers, evidence and state changes.
The caller may control request fields and replay previously observed requests,
but does not possess the trusted admin, custodian or verifier keys.

Check admission validation, signer/role separation, grant and verifier bindings,
revocation, expiration and generation changes, budget consumption, concurrent
writers, replay and conflicting effect identifiers, SQLite atomicity and restart
behavior. Refusals should preserve safe correlation, reason, timestamp and exact
request digest without creating effects or consuming authority. Supplied command
identifiers are not authenticated authority; inspect command_authenticated.
Audit persistence failure must roll back an effect. No raw secret material should
be emitted into ordinary evidence or diagnostic paths.

Trusted assumptions include the process, local OS/SQLite, bootstrap public-key
registry and clock. A host administrator can modify storage and keys; total
rollback of the destination database is outside the claimed protection. Same-host
transactional guarantees do not establish cross-host or external-provider atomicity.
Selected legacy C0 check-to-commit limitations and optional same-host C1 boundaries
remain documented; no C2/C3 or real settlement is claimed. Report concrete defects
even when they intersect a documented limitation, distinguishing the assumption
from an additional bypass rather than treating exclusions as evidence of safety.

## Offline reproduction

Run `sh .oss-scanner/test-offline.sh` from /src. It executes 171 testcase elements
across five local profile suites plus six control-removal mutation probes at the
enrollment-preparation revision. Counts may evolve; inspect actual outputs.
The tests generate ephemeral synthetic keys and use temporary SQLite databases.
No API credentials, payment processor, email delivery or model access is needed.
The comparative benchmark's OPA/LangGraph dependencies and other component test
chains are not installed by this bounded image. Network isolation is imposed by
the scanner or `docker run --network none`, not by the test script itself.

## Severity and private reports

Prioritize reachable unauthorized effects, authority escalation, replay causing
extra effects, signature/role bypass and silent loss of refusal evidence. Assess
impact against the actual optional synthetic profile and prerequisites; do not
label every fixture defect a production compromise. Crashes or denial of service
need a concrete input and resource-bound analysis. A malformed request producing
a safe refusal is not itself an authorization failure.

For each finding provide exact source revision, affected function, attacker
capabilities, minimal synthetic reproducer, expected/observed result, persisted
effects/events, and a proposed regression test or patch if possible. Preserve
failure evidence; distinguish confirmed behavior from hypotheses. Send reports
privately through the enrollment contact. Do not open public exploit issues,
publish unpatched findings, use private repositories or real credentials, or
perform production/network effects. Model-generated reports require maintainer
review and do not constitute independent security signoff.
