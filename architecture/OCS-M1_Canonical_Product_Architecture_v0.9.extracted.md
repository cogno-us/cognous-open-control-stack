# OCS-M1 Canonical Product Architecture — v0.9

**Document ID:** OCS-M1-ARCH-001  
**Original document:** `OCS-M1_Canonical_Product_Architecture_v0.9.docx` (2026-11-07, 11 pages)  
**Representation:** Automated extraction of the submitted DOCX text; tables may be visually flattened. **Not original binary.** Original source is the canonical basis for wording and intent; the Architect's adoption and change-control decision is recorded in the linked static implementation-plan issue. The original DOCX describes its pre-adoption status as proposed: that historical label has not been edited here.

---



---

### Source page 1



                                                             COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION

COGNOUS / CONTROLLED ARCHITECTURE DRAFT


OCS-M1 Canonical Product Architecture
Finite developer-consumable governed action control stack and integration profiles
 Control                                             Value
 Document ID                                         OCS-M1-ARCH-001
 Version                                             0.9 — proposed M1 design baseline
                                                     PROPOSED / NOT ADOPTED / NOT IMPLEMENTATION
 Status
                                                     AUTHORIZATION
 Date                                                7 November 2026
 Owner                                               Cognous Chief Architect (adoption reserved)
                                                     Product architects, component owners, builders,
 Intended readers
                                                     qualification owner
                                                     Repository state examined in this conversation, 7 November
 Source cutoff
                                                     2026



Interpretation rule: SHALL / MUST denotes a proposed normative M1 requirement, not a claim of
existing implementation or adoption. “Existing” applies only to verified source/evidence identified in
the source register. Unknown implementation coverage remains UNVERIFIED until independently
inspected.




                           PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 2



                                                                     COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION


Executive specification and adoption boundary
OCS-M1 is a bounded, nonproduction developer control stack: a consuming application submits a
typed, source-bound synthetic action proposal; native Control Plane evaluates admission; native
Runtime performs only a permitted local effect; Replay yields source-pinned evidence; and the
consumer receives a truthful executed/held/uncertain result with explicit reconciliation semantics. The
stack must not claim authenticated institutional authority, independent custody, chain finality, or
operational certification without actual evidence.

This proposal derives from the OCS Hub #281 Amendment 0.6, Orchestrator F1 and F3 merged
implementations, and preserved G1–G3 qualification limitations. Unlike a freeform “integrate every
component” plan, it defines a mandatory minimal core and optional assurance extensions. It does not
modify existing product contracts or establish organizational adoption.


1. Product identity and bounded first customer
    Dimension                                                 M1 design decision
                                                              Software developer embedding governed local agent/action
    Primary consumer
                                                              execution
                                                              One supported API/CLI, native admission, controlled
    Developer value
                                                              execution, evidence and safe reconciliation
                                                              Local synthetic refund/purchase-style bounded action, with
    First supported business slice
                                                              selectable approved development profiles
                                                              Synthetic actor/issuer fixture, authenticated=false, no real
    Nonproduction trust
                                                              customer or payment
                                                              Existing F1 refund-disposition/0.1.0-dev and F3
    Core implementation
                                                              refund-desk/0.1.0-dev, plus bounded F2a selection
                                                              Independent developer can install a pinned minimal profile,
                                                              submit two distinct allowed action instances, see refusal and
    M1 stop condition
                                                              uncertain reconciliation, and inspect evidence; no broad
                                                              certification inference




2. Existing source baseline and evidence states
      Hub: cogno-us/cognous-open-control-stack main a008b6cac8d12a0ae2a1c4a8591dd69e033ffabf at
       inspected baseline; static roadmap issue #281 Amendment 0.6 controls current planning priority.
      Orchestrator: cogno-us/cognous-stack-orchestrator main
       77701cfcc46d52658ffcec10b6a38516c82feeaf, merging F3 PR #156.
      F1 library: PR #155 merged at 09e1ba3d33aa64dd7054746838d16b64d868cf9f; public
       dispose_refund and effect-free reconcile_refund. Local 20/20 developer tests reported; no matching
       CI collection.
      F3 Refund Desk: merged at 77701cfc; separate CLI consumes only F1 public entrypoints; local 30/30
       developer tests reported; matching Python tests are not collected by CI.
      F4 usability trial: bounded A/B/C evaluator-reported PASS with partial independence and
       documented limitations; not security qualification. Confirmed F3 replay_note presentation defect
       tracked in Orchestrator issue #157.

                                     PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 3



                                                                       COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION

      Original G3 independent qualification: Q1 NOT VERIFIED; Q2 PASS qualified; Q3 FAIL; Q4 FAIL on
       original source; Q5 NOT VERIFIED; six Copilot findings retained. Q4 developer cleanup remediation
       does not retroactively change qualification.
      Verifier is ALPHA/HOLD; P1-EXIT BLOCKED/DEFERRED; Constitution adoption reported
       UNVERIFIED.


3. Product architecture: mandatory core vs optional assurance
OCS-M1 intentionally avoids treating all current components as a mandatory linear pipeline. Each
profile declares its required edges; a consumer SHALL NOT claim an unavailable downstream stage as
run or trusted. A core developer transaction works without Verifier/Registry; their absence is
disclosed, not masked. Optional profile stages may be exercised separately under their native trust
constraints.
    Profile                               Required native components               Purpose / claim ceiling
                                          Institutional Governance synthetic       Governed local synthetic action,
    CORE-LOCAL/0.1-dev                    fixture, Control Plane, Runtime local    hold/refusal, producer-reported
                                          SQLite, Replay, Orchestrator F1/F3       evidence, reconciliation
                                          CORE plus actual Replay→Evidence         Bounded evidence package, not
    EVIDENCE-PACK/0.1-dev (optional)
                                          Pack native compatibility                independent proof
                                          Evidence Pack plus actual Verifier       Verifier actual outcome; ABSTAIN
    VERIFICATION/alpha (optional)
                                          native assessment                        remains ABSTAIN
                                                                                   Synthetic signature/provisional local
                                          Verified source-compatible Attestation
    ATTEST-REGISTRY/dev (optional)                                                 inclusion, not durable custody or
                                          and Registry stage
                                                                                   finality
                                                                                   Recipient/reliance governance; not
    EXCHANGE/odes-gax (optional)          ODES/GAX as applicable side path
                                                                                   automatic payment authority




4. Canonical trust and execution boundaries
1. Application proposes typed intent and, after F2a, references one of a bounded set of approved
       development manifest profiles. Selection by the caller is not a grant.
2. Orchestrator validates the selected profile against a versioned allowlist and native manifest
       semantics; any identity/scope inconsistency fails closed before side effects.
3. Institutional Governance fixture provides synthetic lineage; native Control Plane makes its own
       admission decision under the declared development profile.
4. Only native Control Plane AUTHORIZED permits Runtime local effect invocation.
       HOLD/REVOKED/UNKNOWN cannot silently advance to effect.
5. Runtime records the local destination state; re-invocation and idempotency claims remain limited
       to the native persistence scope.
6. Replay reconstructs actual source-pinned evidence; an imported bundle does not independently
       verify the destination.
7. Optional Pack/Verifier/Attestation/Registry run only where selected and source compatible; no
       claim upgrades occur on missing stages.
8. Application returns executed/held/uncertain status, retains native fields, exposes reconciliation
       only where supported, and makes no real payment.
                                 PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 4



                                                            COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION


5. Finite M1 mandatory capability requirements
OCS-01 — Stable developer consumption
Normative requirement. The stack SHALL provide a supported public callable interface and at least
one separate consuming CLI/application using only the public interface.

Observable acceptance. A fresh consumer imports the F1 entrypoints without private test internals
and processes both positive and refusal paths with structured output.

Owner / source posture. Orchestrator F1/F3 | F1/F3 merged.

OCS-02 — Validated action proposal
Normative requirement. The consumer SHALL submit typed action ID, scope, tenant, target/account,
amount/currency where applicable and correlation identity; the requested profile is versioned and
constrained by approved development selection.

Observable acceptance. Malformed, cross-tenant, over-limit or unapproved action input is refused
before Runtime effect; no implicit policy grant from the caller.

Owner / source posture. Orchestrator F2a + CP | F2a proposed.

OCS-03 — Caller-selectable bounded profile
Normative requirement. The public F1 interface SHALL support more than its historical fixed
customer-001 manifest through a backwards-compatible optional source/provenance-bound
manifest/profile selection, if native CP permits it.

Observable acceptance. Two distinct approved synthetic cases are authorized under their own
manifest bindings; the old fixed profile remains unchanged by default; unsupported selections HOLD.

Owner / source posture. Orchestrator F2a | Hub #281 amendment 0.6.

OCS-04 — Native admission and refusal
Normative requirement. The native Control Plane SHALL remain the authority for action admission.
Runtime is not invoked after HOLD, invalid/revoked scope, wrong issuer or native refusal.

Observable acceptance. Independent local measurement shows no prohibited Runtime dispatch or
destination effect for revoked/wrong-scope case.

Owner / source posture. Control Plane / F1 composition | Existing F1 native integration.

OCS-05 — Native local execution
Normative requirement. Only an admitted action SHALL reach the existing Runtime local SQLite
destination; execution identity and attempt state are preserved.

Observable acceptance. A valid action produces one observed local effect row under the declared
destination; repeat within supported idempotency scope creates no duplicate row.

Owner / source posture. Runtime / F1 | F1 source-pinned path.



                            PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 5



                                                            COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION

OCS-06 — Honest execution disposition
Normative requirement. The public output SHALL separate native Control Plane result, Runtime
result, observed state, effect evidence, execution claim basis and application presentation.

Observable acceptance. Unsupported success evidence downgrades presentation to uncertain; no
inferred absence from a lost acknowledgment.

Owner / source posture. F1/F3 | F3 R1 correction.

OCS-07 — Replay evidence references
Normative requirement. The system SHALL generate resolvable source-pinned Replay evidence for
supported local effects, preserving bundle path/digest, source/profile identity and limitations.

Observable acceptance. An independent read-only process verifies Replay file existence/digest and
destination row agreement for the declared evidence scope; presentation retains failure reasons.

Owner / source posture. Replay / F1/F3 | Issue #157 defect retained.

OCS-08 — UNKNOWN and recovery discipline
Normative requirement. After an unresolved dispatch, the system SHALL NOT redispatch
automatically and SHALL expose effect-free reconciliation supported by actual observed state.

Observable acceptance. Simulated lost acknowledgment produces UNKNOWN/uncertain and reconcile-
only next action; destination readback resolves only if effect actually observed and no duplicate is
created.

Owner / source posture. F1 / Runtime | F1/F3 developer evidence.

OCS-09 — Isolation and local resource ownership
Normative requirement. Each invocation SHALL own exact workspaces and avoid deleting unrelated
resources, report disposal failure, and preserve caller-owned destination state.

Observable acceptance. Two disjoint workspaces do not delete one another; cleanup failure is visible;
no broad temp glob removal.

Owner / source posture. Orchestrator implementation | G3 Q4 developer remediation.

OCS-10 — Component/profile provenance
Normative requirement. The active developer profile SHALL identify exact source commits and
supported contracts for components actually imported; missing/mismatched source fails closed.

Observable acceptance. Tampered or wrong-pin checkout cannot silently load; no label of formal P1
selected source lock.

Owner / source posture. Hub / Orchestrator | F1 source pins.

OCS-11 — Structured refusal and evidence inspection
Normative requirement. The application SHALL expose reason codes, native disposition, limitations,
retry permission and traceable evidence references without hiding a missing stage.


                           PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 6



                                                                     COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION

Observable acceptance. Refused, held, unknown and failed results are distinguishable; Verifier
ABSTAIN never presented as PASS; Pack absence disclosed.

Owner / source posture. F3 developer consumer | F3 README.

OCS-12 — Reproducible nonproduction adoption
Normative requirement. One bounded supported installation procedure SHALL allow independent
developer setup, action, refusal, reconciliation and cleanup without using test-only internals.

Observable acceptance. Fresh Linux local environment completes selected public-path checks;
undocumented required steps reported as defects; F4 partial independence disclosed.

Owner / source posture. OCS Hub / Orchestrator | F4 recorded limited trial.


6. Application-facing interfaces and schema intentions
The interface examples in this section are proposed public contract fields, not an assertion that they
already exist in F1. Current F1 accepts a fixture-bound request and uses an internal fixed CP manifest
path. F2a SHALL choose the smallest native-compatible mechanism: a validated reference to an
allowlisted immutable development manifest is preferred over passing arbitrary caller-authored
policy. The actual CP schema and F1 package signatures control the implementation.
 Public API                                                   Essential semantics
                                                              A versioned typed request, existing fixed profile by default,
 dispose_refund(request)                                      optional approved manifest reference in F2a; may cause
                                                              permitted LOCAL synthetic effect only
                                                              Read-only reconciliation of prior uncertain attempt; SHALL
 reconcile_refund(request)
                                                              NOT dispatch another effect
 Refund Desk process                                          CLI uses only F1 public call and maps result conservatively
 Refund Desk reconcile                                        CLI uses only F1 public read-only reconciliation
                                                              Exact manifest ref+digest, allowed tenant/institution/action,
 Profile descriptor (F2a proposed)                            supported target, currency/limit and applicable source pins;
                                                              never a caller permission grant




6.1 Input identity constraints
A selected manifest MUST bind the business intent and the native proposal with the same tenant,
institution, target, amount/currency, action, adapter, requirement and effect/correlation identity
according to actual CP/Runtime contracts. A profile is not usable merely because its JSON validates;
source identity, trust class and native CP admission must succeed. Arbitrary profile paths, untrusted
new policy grants and unrestricted dynamic manifest creation are excluded from M1.

6.2 Output status discipline
 Condition                             Public presentation                          Permitted next action
                                       held/refused with native reasons; no
 Control Plane HOLD or revoke                                                       None; correct authority elsewhere
                                       current effect claim
 Runtime applied with supported        executed; producer-reported limitation
                                                                                    No automatic retry
 observation                           explicit


                               PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 7



                                                                     COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION

 Acknowledgment missing, effect        uncertain / UNKNOWN; absence not
                                                                                  reconcile only
 uncertain                             established
 Reconcile observes prior applied      observed/executed with
                                                                                  No redispatch
 effect                                acknowledged=false preserved
 Verifier not selected or ABSTAIN      not run or abstain (actual native field)   No upgrade to verification PASS
 Unknown source/profile                refusal or BLOCKED before effect           Correct source/profile only




7. Component interaction and optional edges
 Native edge                           Current posture                            M1 decision
                                       Demonstrated in F1/F3 with                 Mandatory core; no claim of
 IG synthetic → CP
                                       authenticated=false                        institutional identity
                                       Demonstrated local positive and            Mandatory core; native gate cannot be
 CP → Runtime SQLite
                                       revoked HOLD                               bypassed
                                       Demonstrated via exact source-pinned       Mandatory core; evidence producer-
 Runtime → Replay
                                       F1                                         reported
                                                                                  Optional M1 evidence profile; exact
 Replay → Evidence Pack                Previously bounded G2/G3 integration
                                                                                  compatibility required
                                       Native consumption demonstrated            Optional; never a requirement for core
 Pack → Verifier
                                       bounded; ALPHA/HOLD                        local refund
                                       Synthetic reference path; trust/custody
 Verifier → Attestation/Registry                                                  Optional future controlled dev profile
                                       limits
                                       Development integration previously         Optional branch, no universal pipeline
 ODES → GAX
                                       demonstrated                               requirement
                                       Strategic future application-owned         Not an M1 dependency; separate
 CDC/ISS → OCS
                                       proposal                                   contract




8. Failure, recovery and idempotency
8.1 Authority and no-effect behavior
For a refused or held action, the consumer must not call Runtime or create the destination effect. “No
effect from this request” may be asserted only when measured within the selected local native
boundary; it says nothing about earlier attempts or external systems. The synthetic IG resolver is not
institutional identity. A signed artifact or Registry pointer alone never grants action authority.

8.2 Commit uncertainty
An acknowledgment may be lost after a local SQLite commit. The correct response is
UNKNOWN/uncertain until effect-free reconciliation observes the actual destination state. Missing
acknowledgment cannot establish nonexecution. The existing F1 policy conservatively refuses repeat
dispatch even after observed reconciliation in some cases; M1 must document rather than silently
reverse that native behavior. Cross-database exactly-once and distributed transaction guarantees are
excluded.




                               PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 8



                                                                      COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION

8.3 Workspace and cleanup
The library owns per-invocation scratch paths; caller-owned state_dir remains the caller’s. Exact paths
are tracked; broad tempfile directory patterns are prohibited. Failed removal is observable, not
suppressed. No cleanup may delete unrelated process state. This is a real functional invariant but does
not justify a new generalized clean-room infrastructure program.


9. Security and trust model
 Boundary                               M1 obligation                              Excluded stronger claim
                                        Synthetic fixture explicitly labeled, CP   Authenticated real-world institutional
 Identity/authority
                                        native decisions enforced                  delegation
                                        Exact commits, verified imported
 Source provenance                                                                 Formal independent origin certification
                                        modules for used components
                                        SQLite readback and native result with     Independent third-party custody or
 Effect evidence
                                        limitations                                global exactly-once
                                        Explicit actual Pack state where
 Evidence packaging                                                                Automatically verified business action
                                        selected
                                        Report actual                              Verifier ALPHA/HOLD equaling
 Verifier
                                        PASS/FAIL/ABSTAIN/UNKNOWN                  accepted assurance
                                        Synthetic signer and digest binding
 Attestation                                                                       Organizational key custody
                                        only where selected
                                        Provisional local-chain inclusion where    Public-chain finality and durable
 Registry
                                        selected                                   custody
                                        Local Linux synthetic data; no             Production readiness, real refunds or
 Operations
                                        provider/paid/customer effects             hosted enterprise release




10. Finite implementation and verification milestones
 Phase                                  Deliverable                                Exit / boundary
                                        Freeze F1/F3 exact identities and G3       No product edits; historical failures
 M1-0 — Reference baseline
                                        residual record                            preserved
                                                                                   Two distinct permitted synthetic
                                        Versioned allowlisted action/manifest
 M1-1 — F2a caller profiles                                                        customers/actions; old F1 default
                                        selection, native CP admission
                                                                                   unchanged
                                        Refund Desk selects second distinct        Separate public interface only, no
 M1-2 — Consumer update
                                        approved synthetic profile                 private tests in application
 M1-3 — Evidence/presentation           Resolve replay_note issue #157 if          Affected-path checks; no broad Replay
 correction                             affected; honest current status            rebuild
 M1-4 — Usability and nonproduction     One bounded documented installation        Fresh consumer run; no new iterative
 package                                and consumer scenario set                  clean-room program
                                        Trace 12 mandatory requirements to
                                                                                   Chief adopts/holds exact nonproduction
 M1-5 — Acceptance freeze               code/evidence; source-pin exact core
                                                                                   M1; P1/security claims remain separate
                                        profile



The optional Evidence Pack, Verifier, Attestation, Registry, ODES and GAX profiles are outside the
mandatory CORE-LOCAL completion threshold unless the Chief Architect separately selects a stronger
M1 distribution profile. Such a selection must explicitly name added requirements and qualification
                                PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 9



                                                                           COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION

cost; it cannot be inferred from the existence of components. No feature expansion is authorized by
this document alone.


11. Acceptance cases and bounded independent evidence
 Check ID                                 Scenario                                    Expected observation
                                                                                      Native CP authorizes; one local SQLite
                                          Approved synthetic action under first
 T-OCS-A                                                                              effect; Replay digest resolves; correct
                                          selected profile
                                                                                      limitations
                                                                                      Native CP authorizes own bounded
                                          Different permitted synthetic action
 T-OCS-A2                                                                             scope; distinct effect identity; no
                                          under second profile
                                                                                      hardcoded customer restriction
                                          Revoked/wrong                               Native CP HOLD/refusal and no
 T-OCS-B
                                          tenant/over-limit/unsupported manifest      prohibited Runtime invocation
                                                                                      No auto-redelivery; uncertain and
                                          Postcommit lost acknowledgment or
 T-OCS-C                                                                              reconcile-only path; no false absence
                                          unresolved state
                                                                                      claim
                                          Changed manifest checksum / wrong           Refuse before native effect; preserve
 T-OCS-D
                                          profile source                              prior states
                                                                                      No undocumented dependency; actual
                                          Fresh consumer follows published
 T-OCS-E                                                                              raw output/SQLite/Replay evidence
                                          installation instructions
                                                                                      recorded



The architect should select three primary checks per changed functional increment, not
indiscriminately run the historical qualification corpus. Mandatory changed-path tests, CI,
source/security checks and independently prescribed assurance remain. GitHub Copilot may conduct
bounded automated technical review with actual source access; it is not formal independent
institutional certification. Original G3 Q1–Q5 and six review findings must not be relabeled. F4 A/B/C
was a partial-independence developer-usability trial, not a safety guarantee.


12. Residual risk and explicitly excluded release claims
 Known limitation                                                Required posture
                                                                 Disclose as evidence gap; required CI changes need separate
 F1/F3 Python tests not collected by existing CI
                                                                 governance
                                                                 F2a removes hardcoded-only consumer restriction via native
 Fixed historical F1 CP manifest
                                                                 approved profiles
                                                                 Track and correct narrowly, preserve original adverse
 F3 replay_note presentation omission (#157)
                                                                 finding
 Authenticated=false synthetic issuer                            NONPRODUCTION; no institutional-grant claim
 Idempotency only within destination database                    No global exactly-once guarantee
 Verifier ALPHA/HOLD                                             Do not report accepted verification
 G3 Q1–Q5 incomplete qualification                               Retain exact verdicts and source distinctions
 P1 acceptance and constitution adoption                         BLOCKED/UNVERIFIED until separate competent acts
 No customer effects/cloud/custody/finality                      Release is development profile only




                                PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 10



                                                               COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION


13. M1 product acceptance and stopping rule
OCS-M1 CORE-LOCAL is functionally complete when OCS-01–OCS-12 are satisfied for one pinned
development profile and one independent consuming application, with a second permitted caller-
selected action, one native refusal, one uncertainty/reconciliation case, exact source/evidence
references and reproducible installation. All supported behaviors must be described truthfully and
critical negative findings retained. Core completion does not mean the entire OCS component universe
is integrated or independently certified.

On completion freeze a named nonproduction CORE-LOCAL source/profile and begin bounded
developer packaging. Any new module, new effect adapter, enterprise identity, Verifier acceptance,
Registry custody, cloud deployment or production release belongs to a separate version/profile and
Chief Architect decision. A demonstrated safety defect in already supported behavior still requires
correction. Do not let optional capability work postpone the approved CORE-LOCAL stop condition.


14. Reserved architecture and change-control decisions
     Select the minimum native-compatible F2a input mechanism: allowlisted immutable
      manifest/profile reference is preferred; direct caller-authored manifest is not authorized by
      default.
     Freeze exactly which fields may vary across two permitted test instances and which CP
      policy/source/target/tenant restrictions remain immutable.
     Preserve original F1 public request semantics when optional F2a selector is absent.
     Select whether any optional Pack/Verifier path is a separate beta profile; never silently convert it
      into the CORE-LOCAL minimum.
     Maintain one canonical writer for F1 public contract; native component owners control protected
      changes.
     Issue separate exact-source implementation and merge authorization; a plan does not grant either.


Appendix A. Requirement-to-evidence register
                             Code status (source-
    Requirement                                         Evidence gap               Release posture
                             backed)
                                                        Exact-head verification
    OCS-01                   EXISTING / RECHECK                                    NOT ACCEPTED
                                                        required
                                                        Exact-head verification
    OCS-02                   PARTIAL / F2a NEEDED                                  NOT ACCEPTED
                                                        required
                                                        Exact-head verification
    OCS-03                   PARTIAL / F2a NEEDED                                  NOT ACCEPTED
                                                        required
                                                        Exact-head verification
    OCS-04                   EXISTING / RECHECK                                    NOT ACCEPTED
                                                        required
                                                        Exact-head verification
    OCS-05                   EXISTING / RECHECK                                    NOT ACCEPTED
                                                        required
                                                        Exact-head verification
    OCS-06                   EXISTING / RECHECK                                    NOT ACCEPTED
                                                        required
                                                        Exact-head verification
    OCS-07                   EXISTING / RECHECK                                    NOT ACCEPTED
                                                        required


                             PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026



---

### Source page 11



                                                           COGNOUS / PRODUCT ARCHITECTURE SPECIFICATION

                                                    Exact-head verification
 OCS-08                   EXISTING / RECHECK                                  NOT ACCEPTED
                                                    required
                                                    Exact-head verification
 OCS-09                   EXISTING / RECHECK                                  NOT ACCEPTED
                                                    required
                                                    Exact-head verification
 OCS-10                   EXISTING / RECHECK                                  NOT ACCEPTED
                                                    required
                                                    Exact-head verification
 OCS-11                   EXISTING / RECHECK                                  NOT ACCEPTED
                                                    required
                                                    Exact-head verification
 OCS-12                   EXISTING / RECHECK                                  NOT ACCEPTED
                                                    required




Appendix B. Source and decision register
OCS Hub #281 (Amendments 0.5–0.6):
https://github.com/cogno-us/cognous-open-control-stack/issues/281

OCS serial ledger and F1/F3/F4 evidence:
https://github.com/cogno-us/cognous-open-control-stack/issues/273

Orchestrator main and F3: cogno-us/cognous-stack-
orchestrator@77701cfcc46d52658ffcec10b6a38516c82feeaf

F1 public README: orchestration/adapters/refund_disposition/README.md, source as above

F3 public README: applications/refund_desk/README.md, source as above

F1 PR #155 merge: 09e1ba3d33aa64dd7054746838d16b64d868cf9f

F3 PR #156 merge: 77701cfcc46d52658ffcec10b6a38516c82feeaf

Orchestrator #157: F3 replay_note presentation defect retained

Qualification #274 (cogno-us/cognous-stack-qualification), main
b3b65ff6bc6f9760c822b88423fe541c3a7edb97; incomplete verdicts preserved

Cognous Engineering Constitution: cogno-us/cognous-engineering-constitution, exact locally adopted
status to verify




                          PROPOSED — ARCHITECT REVIEW REQUIRED • 7 NOV 2026