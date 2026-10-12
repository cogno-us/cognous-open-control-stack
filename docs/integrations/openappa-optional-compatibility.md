# Optional OpenAPPA compatibility profile 0.1

Status: **optional candidate; not a core dependency and not production qualification**.

## Selected revisions

- Cognous W0 accepted hub baseline: `6ad8f6a409d3140aa65af19d5c850dd8e58f8a7d`.
- OpenAPPA selected pin: `v0.31.1`, commit `4debcfb695f4f74d0d9a92ebdad15ebcc578c991`.
- Upstream license at the selected pin: MIT, `LICENSE.md`.
- OpenAPPA hook wire protocol used by this profile: protocol 1, parsed from the pinned upstream Python KAgent wire implementation.

The earlier hub PR #44 and Action Manifest PR #10 remain design proposals and are not accepted dependencies for this implementation.

## Scope

This profile is intentionally small. It supports one bounded synthetic refund operation over the accepted Cognous component pins and OpenAPPA's pinned hook-decision semantics.

It implements:

1. exact Cognous/OpenAPPA operation identity mapping;
2. strict conjunction of OpenAPPA `allow_call` and current Cognous action authority;
3. no dispatch on either denial, unusable OpenAPPA input or incomplete identity evidence;
4. a separate incoming-context admission gate;
5. a separate outgoing-result admission gate;
6. result withholding without rewriting an already applied effect;
7. versioned compatibility evidence for W3 and W7.

OpenAPPA flow permission has `authority_effect: none`. Remedies, policy proposals, classification output and flow decisions do not create Cognous grants.

## Qualification

`tests/test_openappa_optional_compat.py` exercises:

- selected OpenAPPA source pin and protocol;
- OpenAPPA allow + Cognous allow;
- OpenAPPA denial;
- Cognous denial while OpenAPPA allows;
- incomplete operation identity;
- unsupported OpenAPPA protocol;
- incoming context allow/refuse;
- a real accepted synthetic refund effect followed by OpenAPPA result withholding;
- proof that `component-lock.json` contains no OpenAPPA component and the selected core runtime profile remains `merged-producers-v1`.

The result-withholding case executes the existing accepted synthetic refund path into its local authoritative SQLite destination, then applies the pinned OpenAPPA wire decision to the result admission boundary. The destination effect remains present when the result is withheld.

This is a pinned-engine compatibility qualification, not a live OpenAPPA service deployment. It does not qualify network transport, tenant-isolated OpenAPPA storage, production credentials, autonomous policy learning, self-improving policy deployment, general memory changes or distributed commit races.

## W3 / W7 handoff

Versioned profile evidence is in `fixtures/openappa/profile-evidence-v0.1.json`.

Consumers must preserve these distinctions:

- flow permission != Cognous authority;
- dispatch != applied effect;
- applied effect != admitted result;
- compatibility evidence != independent destination verification;
- absence or unusability != allow;
- OpenAPPA remains optional.

No change to `component-lock.json` is part of this workstream.
