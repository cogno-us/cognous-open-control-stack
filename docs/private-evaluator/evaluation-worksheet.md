# Private technical evaluator — observation worksheet

For an invitation-only read-only synthetic evidence review. **Not** a security signoff, production authorization, acceptance certificate or public-preview release approval. Do not enter credentials, customer information, confidential implementation details, security exploitation steps or personal contact details into public issue trackers.

**Evaluation date:** __________________  
**Evaluator role (not personal identity):** __________________  
**Evidence baseline:** [Integrated preview PR #84](https://github.com/cogno-us/cognous-open-control-stack/pull/84), head `62c93784f34f6ad0a3f63a5efac04a948e826ae1`  
**Reference:** [Selected archive inspection](../workstreams/pv-artifact-evidence-inspection-2026-10-10.md) and [resource-constrained disposition](../verification/pv-resource-constrained-disposition-2026-10-10.md)

## Evidence comprehension

| Question | Observation / linked evidence | Open question |
| --- | --- | --- |
| Where is an action declared, and what is **not** authorization? | | |
| Where does institution-supplied Authority Context enter? | | |
| What is C0's check-to-commit limitation? | | |
| What changes, and does **not** change, with optional same-host C1? | | |
| What must happen after timeout or absent observation before any new attempt? | | |
| What can the archived SQLite destination prove, versus real settlement? | | |
| How are Replay, Evidence Pack and ODES related but not independent proof? | | |
| What is the meaning of 34 passed / one characterized out of 35? | | |

## Observation classification

For each finding: identify an exact source SHA, path, archive, scenario or line; classify as **confirmed observation**, **inference**, **unverified hypothesis**, or **unavailable evidence**. A CI success conclusion is not the same as independently inspected contents.

| Finding and consequence | Classification | Source pointer and exact SHA | Discriminating follow-up |
| --- | --- | --- | --- |
| | | | |
| | | | |
| | | | |

## Material limitations acknowledged

- [ ] Evidence is a bounded synthetic reference, not a live payment integration.
- [ ] C0 is **not** atomic with destination commit; C1 is optional cooperating same-host only; C2/C3 are unqualified.
- [ ] Timeout or absent observation does not itself authorize retry. Effect-ID dedupe is not equivalent-intent dedupe.
- [ ] Selected evidence includes **34 passed and one characterized** required case; optional C1 73 and historical 915 are separate populations.
- [ ] No independent clean-room current-selected execution was completed by the final worker.
- [ ] Comprehensive Git-history/artifact/credential/PII/private-IP safety screening and third-party licensing clearance are incomplete.
- [ ] No code redistribution, production execution, release permission, grant issuance or deployment trust is implied.
- [ ] Public-preview gates remain unaccepted; [operational trust #30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30) is **HOLD**.

## Priority feedback

**Most credible capability shown by the evidence:** __________________

**Most important observed limitation:** __________________

**One falsifiable question to investigate next, without production data or effects:** __________________

**Requested follow-up (documentation, test evidence, license review, security review, or none):** __________________

**Facilitator disposition:** Feedback recorded / more evidence requested / session incomplete.  
**No release or production approval can be granted by this worksheet.**

For suspected vulnerabilities or sensitive exposure, stop public documentation and use the private [security reporting route](../../SECURITY.md).
