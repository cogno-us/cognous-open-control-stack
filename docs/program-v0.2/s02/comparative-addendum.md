# Addendum to the S01 comparative assessment (sources newly read)

**Proposed record, documentation only.** It adds source readings to [s01/comparative.md](../s01/comparative.md), which is kept unchanged as history. It records no decision, adopts no ADR, and changes no priority. Release and production remain on HOLD. Reading was read-only and static.

## 1. What was read in this pass

| Source | Result |
|---|---|
| "From Mainline to Governed Cognition" (de Lima, August 2026), all 15 pages | Read. Owner-authored conceptual paper; it states it is comparative and conceptual and that Linux does not prove Cognous correct. Treated as the owner's stated principles, not as independent evidence |
| APPA paper, "Recoverable Information-Flow Control for Real-World LLM Agents" (arXiv 2607.24625), via its PDF address | Read through a fetch summary answering five specific questions, not page by page |
| Microsoft blog "Introducing the Agent Governance Toolkit" (2026-04-02) | Read through a fetch summary |
| AGT repository (`microsoft/agent-governance-toolkit`) and the OpenAPPA "how it works" page | Not retrievable in this pass (the fetch tool refused both addresses). REQUIRES INVESTIGATION stays for anything that depends on the repository code or that page |

Figures and statements about Linux and Git that the owner's paper cites from kernel and Git documentation were not re-checked here and are not used as OCS evidence.

## 2. CA-06: promotion and no-regressions (now sourced)

S01 had only the owner's stated principles and marked paper-specific content REQUIRES INVESTIGATION. The paper is now read. It states seven principles; the mapping below is a translation, not a one-to-one technical equivalence (the paper says the same).

| Paper principle | OCS counterpart | Home |
|---|---|---|
| Operational legibility | Decision context binds rule-set digest, evaluator versions and epoch; identity crosswalk; evidence handoff | CA-03 minimum; [1.4](contracts/1.4-evidence-handoff.md); [1.5](../s03/identity-and-lifecycle.md) |
| Mainline (a distinguishable canonical state and an authorized path into it; ambiguous standing is a defect) | Component lock as canonical selection; promotion-boundary table with a status for each artifact class | [1.2 section 4](contracts/1.2-authority-and-separation.md) |
| Scoped authority (identity, role, domain, action, context, time) | Exclusive-powers table; existing grant, role mapping and freshness inputs | [1.2 section 2](contracts/1.2-authority-and-separation.md) |
| Lineage-preserving memory (history is part of recoverability, not exhaust) | Append-only revision rows, journals, supersession instead of edit | [1.3](contracts/1.3-registry-r0.md) |
| Boundary commitment (internal change must not silently invalidate external dependencies) | Opt-in committed fields, omit-when-unset, exact profile dispatch, surface comparison | [1.2 section 4](contracts/1.2-authority-and-separation.md); step 4.1 |
| Reversible possibility (canonicalize without destroying alternatives) | Supersession and retained negatives; irreversible effects classed apart | promotion table |
| Accountable certification (inspector and certifier kept separate where risk warrants) | Producer cannot write oracles; Qualification owns verdicts | forbidden transitions F-02, F-03 |

Paper section 7 limits carried into OCS constraints: software correctness is not organizational correctness (claims stay narrow and scoped); lineage is necessary but semantically incomplete (records do not prove authority); probabilistic cognition has a larger state surface (reconstruct the authoritative pathway, not replay); maintainer review does not guarantee separation; human sign-off is not governance (the validity of the approval context matters). Whether OCS evaluates approval-context validity beyond an approval status is REQUIRES INVESTIGATION.

Disposition: unchanged. CA-06 remains ADOPT as an ADR table plus a compatibility gate, priority v0.2 mandatory. The paper also names Cognous components that are not part of this repository's execution boundary (Idea-Space Substrate, Reasoning State Store, Clearframe, Governance Telemetry Events, Governance Correctness Object). They were not read; any mapping to OCS records stays REQUIRES INVESTIGATION.

## 3. CA-01 and CA-05: what the APPA paper settles

| S01 gap | What the paper says (summary) | Effect on the OCS record |
|---|---|---|
| Summarization and paraphrase handling undefined | No general method; handled through registered sanitizers and verified exit transformations; sanitizer correctness is inside the trusted base; confinement inside an authorized send is not claimed | Confirms S01: the summarization case needs an owner-stated host rule. The case stays BLOCKED |
| Reliability versus confidentiality not separated | Label is a reader set plus a trust level, combined by meet | OCS keeps confidentiality, reliability and authority as separate fields (CA-01 item 5) |
| No baseline for false blocks | The paper reports no false-block rate; it reports utility, attack success and remedy counts; synthetic benchmark | No source baseline exists for the measured comparison the owner brief asks for. CA-05 measurement stays deferred |
| Recovery routes | Authorize (a ruling by a registered authority whose mandate covers the gap), Accept (agent narrows its label), or both; Redispatch and Branch are advisory; external rulings cannot accept narrowing for the agent | Consistent with the OCS rule that a remedy must bind the exact denied operation and enter the gate only through a newly issued grant |
| Limits | Covert timing channels out of scope; trust in declared labels and sanitizers; undeclared write-side contracts allow laundering through a store; branching does not roll back external egress; real-world generalization untested | Supports ADR-P09: an external flow framework can supply evidence but is not constitutionally privileged |

## 4. CA-04: AGT enforcement layer

The Microsoft blog describes enforcement as an interception layer on the agent's execution path (policy engine with YAML, Rego and Cedar support, framework hooks), not OS or kernel enforcement, and acknowledges that no security layer is a silver bullet. This matches the S01 reading used for CA-04 and the rule that OCS makes no OS-confinement claim. Repository-level claims remain REQUIRES INVESTIGATION.

## 5. Sources

- From Mainline to Governed Cognition (owner's paper, August 2026): supplied by the operator as an attached file; no public link is recorded here.
- [APPA: Recoverable Information-Flow Control for Real-World LLM Agents](https://arxiv.org/pdf/2607.24625)
- [Introducing the Agent Governance Toolkit (Microsoft Open Source Blog)](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit/)
