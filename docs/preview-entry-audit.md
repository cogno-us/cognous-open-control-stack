# Preview entry points and feedback audit (PV-DOCS, issue #70)

Scope: public navigation, feedback intake and release-claim hygiene only. **No runtime, lock, institutional authority, credential, deployment or release-gate modification.** The component lock remains the sole selection source; this audit does not reselect a revision.

## Navigation inventory

| Public surface | Primary route | Boundary to preserve |
| --- | --- | --- |
| [README](../README.md) | [Start here](start-here.md) | Synthetic bounded reference, not production approval |
| [Start here](start-here.md) | [Developer quickstart](quickstart.md), [governance quickstart](governance-quickstart.md), [release status](release-status.md) | Selected source vs accepted newer vs historical evidence |
| [Developer quickstart](quickstart.md) | [evidence index](evidence-index.md), [reference runner](../tools/reference_release.py) | Checkout command is an earlier checkpoint, not current main proof |
| [Governance quickstart](governance-quickstart.md) | [architecture](architecture.md), [residual risks](../residual-risks.json) | Evidence and protocol validation do not issue institutional grants |
| [Release status](release-status.md) | [component lock](../component-lock.json), [full candidate CI](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37694032916), [C1 CI](https://github.com/cogno-us/cognous-open-control-stack/actions/runs/37682165860) | C0 pre-effect revalidation is not commit atomicity; optional same-host C1 is not the default; C2/C3 are unqualified |
| [Security policy](../SECURITY.md) | Private report contact | No vulnerability details in public issues |
| [Contributing](../CONTRIBUTING.md) | Issue forms in [GitHub issue chooser](https://github.com/cogno-us/cognous-open-control-stack/issues/new/choose) | Small, reviewable, public-safe contributions |

## Trust and claims check

- **Operational trust [#30](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30): HOLD / NOT ESTABLISHED.** This preview audit does not change its status.
- **C0:** current-input validation immediately before dispatch; destination commit atomicity is not established and a race remains.
- **C1:** separately qualified *optional*, cooperating same-host SQLite path; not a selected default or external payment guarantee.
- **C2/C3:** no release claim. No remote commit, distributed transaction, external settlement finality or production exactly-once guarantee.
- Effect-ID deduplication does not prove business-intent deduplication; timeout/absent observation does not authorize retry.

## License/security provenance and outstanding verification

The hub has [Apache-2.0 LICENSE](../LICENSE), [license inventory](../LICENSING.md), [SECURITY.md](../SECURITY.md) and [CONTRIBUTING.md](../CONTRIBUTING.md). Every component named by [component-lock.json](../component-lock.json) must be checked **at its selected revision**, with later `licensing_head` explicitly treated as later distribution guidance, not retroactively substituted into the selected tree. Component repository security-reporting paths may differ; the hub contact does not prove component policies. Neither the license inventory nor a repository URL alone proves redistributable downstream dependencies.

| Item | Evidence available here | Qualification state |
| --- | --- | --- |
| Hub license/security/contribution paths | Local files present | Confirmed from repository tree |
| Selected component license at each locked commit | Lock and hub licensing inventory identify revisions and exceptions | **Requires per-commit file and notice verification** |
| Selected component security disclosure path | No per-component disclosure evidence retained here | **Unverified**; do not claim all repositories expose SECURITY.md |
| External GitHub repository and CI URLs | Source text supplies targets including CI runs 37694032916 and 37682165860 | **Targets listed, not live HTTP-verified by this audit** |
| Preview Markdown local files/anchors | Scoped offline verifier `tools/check_preview_entries.py` | Automated local structural checks; does not check external HTTP, permission, redirects or private pages |
| Feedback intake | New public issue forms and private security route | Structural review only; GitHub-rendered form submission not end-to-end exercised |

Do not promote an unverified remote link or licensing path to verified merely because this local checker succeeds. Check external target URLs with authenticated repository/CI access and record HTTP status, redirect destination, observation date and SHA before a public release-signoff; do not publish private endpoints or tokens. For CI evidence, independently inspect the referenced run's conclusion, source SHA and artifacts; a reachable run URL alone is not evidence of passing qualification.

## Triage

Choose **Documentation or preview link** for broken URLs/anchors or inaccurate wording; use **Bounded reference feedback** for sanitized synthetic reproduction discrepancies with an exact revision. Maintainers should label by observed defect, request missing *non-sensitive* evidence, link the owning component issue for runtime defects and keep the hub issue public-safe. Send vulnerability disclosures to [SECURITY.md](../SECURITY.md) privately; do not reproduce exploitation details in public triage. Neither an issue close nor a green docs check releases operational trust #30.
