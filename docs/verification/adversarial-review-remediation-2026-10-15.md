# Adversarial review remediation

This disposition compares two privately supplied external-model reviews against
hub source 1c522ec2146f2c4d7a9f47e4a0ed7cd890147820 and current upstream code.
Their supplied execution claims are not independent acceptance by the maintainers.
Raw reports and unpublished reproduction archives are not published here.

## Implemented changes and qualification scope

- Optional destination administrative commands now require a positive monotonic
  per-admin sequence and a maximum age of 60 clock units. The same writer
  transaction commits accepted commands and their sequence. A failed command
  does not consume the sequence. Existing administrative producers must add
  `sequence`; the broker execute envelope is unchanged.
- Unauthenticated supplied identifiers are retained as `claimed_command`.
  Only authenticated commands populate `command`. Denial coverage uses the exact
  request digest; authenticated identity matching is an additional requirement.
  This prevents a claimed ID from being treated as authenticated authority.
- Destination tests directly exercise noncurrent verifier status with an
  otherwise unexpired timestamp, digest/generation substitution, inactive status,
  exact replay reasons and delayed/out-of-order administration. Thirteen local
  control-removal probes must fail by assertion, including the seven new probes.
- Both comparison plans now specify exact per-configuration reason codes.
  Cognous unit mutation sensitivity and comparator policy mutations are reported
  separately. Historical plan hashes and runs remain the evidence for earlier
  comparison numbers; the reason contracts change the current plan hashes.
- Cryptography is updated to 50.0.0 in the optional-profile requirements,
  comparison requirements and measured dependency manifest together. The
  supplied advisory was checked against upstream advisory GHSA-p423-j2cm-9vmq;
  this does not assert reachability of that buffer issue in the Ed25519 fixtures.
- Hosted workflow actions use full commit IDs resolved from their existing
  upstream tags. The always-run source integrity workflow rejects mutable refs.
  Release dependencies are version- and hash-locked; their lock digest is
  recorded in reports. Evidence Pack package metadata is built in a disposable
  copy, avoiding modification of tracked metadata in the pinned checkout.
- `release_qualified` remains as a compatibility field but is always false.
  `gate_passed_for_selected_lock` describes successful execution without granting
  publication permission. README scope now distinguishes the frozen selected
  profile from subsequently added optional implementations.
- The selected C0 check-to-commit interval has an explicit required test in the
  existing matrix scenario: revocation injected after revalidation still permits
  the local effect. Passing this characterization does not establish safety.

Local destination qualification has 179 testcase elements, with unittest
subtests reported separately. Comparison oracle/injection tests number 19.
Hosted results must be checked at the PR's final commit before merge; workflow
success alone is not an independent security review.

## Upstream changes are separate from selected acceptance

Control Plane PR 31 adds refusal of unsupported delegated grants, explicit
noncurrent-context holds, stronger principal/actor independence, finite-amount
schema validation and process-safe local destination persistence. Three targeted
mutation probes protect the authority checks. Current upstream already contained
durable effect-time refusal and service evaluation-time work that was absent
from the older selected source examined by the reviews.

Governed Exchange PR 22 adds persistent effect ownership before dispatch. A
second message must reconcile using the original message, even if the effect has
already been observed. This conservative rule is local to one exchange store;
it is not a distributed fence or business-intent deduplication mechanism.

The selected component-lock and release authorizations are unchanged. These
upstream changes do not close findings in the selected integration until an
explicit candidate promotion and consumer qualification are accepted. Review
findings are not marked resolved merely because a newer implementation exists.

## Still open

- Selected-chain adoption of newer Control Plane, executor and exchange behavior,
  including durable reason propagation through Replay/ODES/Evidence Pack.
- C0 commit-time authority fencing; optional C1 remains same-host and cooperative.
- Authenticated institutional resolvers, real credential custody and trusted
  clock acceptance in an actual deployment.
- Full-destination restore protection using an external monotonic anchor.
- Bounded ingress and unauthenticated refusal write amplification; signed input
  is still processed by a trusted local caller, not an Internet-facing service.
- Independent security/operational acceptance and unexamined component histories.
- GitHub ruleset/required-check enforcement and independent reviewer staffing.
  An always-run workflow does not itself configure branch protection. The
  connected API does not expose ruleset administration in this session.

The comparative baseline remains a parity result. Strict corner differences
measure checks present in the Cognous profile and absent in our comparator
applications, not limitations of OPA or LangGraph. Both share Cognous signature
helpers; LangGraph's automatic approval adds no independent policy enforcement.
No commercial-system ranking or production assurance follows.

Operational trust remains HOLD / NOT ESTABLISHED. No release/tag or production
activation is authorized by this remediation.
