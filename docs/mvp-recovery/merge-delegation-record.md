# Merge delegation record (DRAFT, non-authorizing)

Status: DRAFT record of how merge authority was exercised on 2026-10-24. Release and production remain on HOLD. Nothing here is a Qualification verdict, an independent acceptance, a security clearance, a certification or a production-readiness claim. The reviews described below are builder-side inspection.

## 1. Actor

The coordinator Claude session (session URL in the PR description). The GitHub REST field `merged_by` shows `titanicprime` for every merge listed in section 4, because the session acted through that account. REST therefore cannot distinguish the session from the operator, and this record does not claim that it can. The `merged_by` actor observed on GitHub is not proof of prior authorization.

## 2. Instructions relied on, quoted verbatim

Source: session transcript `/root/.claude/projects/-home-claude/a2c4bd54-a19b-573d-9d7a-270aec13d157.jsonl`. The primary instruction (the original operator message) is unavailable: it is not present in that file. The quoted phrases appear only in a context-compaction summary (line 22), written by an earlier part of the session. That summary is a secondhand record. Both instructions below are operator-reported terms, not primary-source text. This record states no instruction time beyond what the summary supports.

A. Qualification repository (`cogno-us/cognous-stack-qualification`).
- Instruction, as quoted in the summary: "Copilot review is sufficient. You merge the qualification repo."
- Date: the summary lists it under "Operator decisions (2026-10-24)". The time of day is unrecoverable.
- Scope: merges on `cogno-us/cognous-stack-qualification` only.

B. Hub documentation and implementation PRs (`cogno-us/cognous-open-control-stack`).
- Standing rule, as paraphrased in the summary under "Standing user rules": "merge docs/implementation PRs autonomously after independent review by a separate worker and exact-head required checks". The summary is a paraphrase, not a verbatim operator quotation.
- Effective date of the historical standing Hub delegation: not established. The primary instruction is unavailable, and this record assigns no date.
- Scope: hub docs and implementation PRs, subject to the review and check conditions in the rule.

## 3. Conditions and limits

- Revocation: the operator may revoke at any time.
- No retroactive authorization. Nothing here authorizes any merge that occurred before the instruction it relies on, and nothing here widens either instruction.
- Reviews by coordinator-directed Claude workers are builder-side inspection. They do not count toward CA04 or CA23 independence.
- Constitution revision 6f7f2731 is provisional guidance, not adopted.
- The Copilot review is recorded as the designated technical review (`copilot-pull-request-reviewer[bot]`, state COMMENTED). It is not a repository approval.

## 4. Merges performed (verified by REST, 2026-10-24 UTC)

Hub, `cogno-us/cognous-open-control-stack`:

| PR | Merged at | Merge commit | PR head |
|---|---|---|---|
| #224 | 01:38:10Z | 1954a986a62056da7af9e43d11b73381f65ed11c | 9fc61a1d |
| #225 | 05:07:27Z | e7c7183687e756ccf839435ef2959fcafa126cdf | 7ff059e0 |
| #227 | 06:01:54Z | 3834ce41de11d08a1b09fe392b37a978addb917f | 838b8387 |
| #228 | 06:26:51Z | 996bb9dd217a8fd4038ae8055de21d49e6ae96ee | 3d53916f |
| #229 | 07:30:03Z | 1668890553e42387c7460f542debd50cbb2c5e50 | 3f868221 |
| #230 | 07:55:55Z | 330ccc315b40d7c32041ab50e0de48ee0fda0ec3 | bec79b7d |
| #231 | 08:16:11Z | c3f052721c7d3e691faf53f06a093a3f1e6d7ba5 | 99e4aa84 |
| #232 | 08:39:22Z | c897266b7ce4b921889519087fa8b1863b4302e3 | cb105d12 |
| #233 | 08:54:25Z | 7661983849474784469f029297fd5bbcccd03ffe | dda05c85 |

Qualification, `cogno-us/cognous-stack-qualification`:

| PR | Merged at | Merge commit | PR head |
|---|---|---|---|
| #226 | 17:32:03Z | 976a8373a175addacad04cebabbaaea8d42406b8 | 94fc06bd |
| #223 | 17:36:40Z | 8087363b9f56f273422e799b2fb6ebc80e789e16 | 0f11f424 |

Not verified here: the separate-worker review and the exact-head required checks for each hub PR, and the time each instruction was given relative to each merge. Those need the PR histories and the original operator messages.
