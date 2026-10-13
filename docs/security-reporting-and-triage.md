# Reporting and triage for the bounded reference

The [security policy](../SECURITY.md) is the canonical private reporting route
for the hub and related Cognous-maintained components. Use its maintained
contact; missing SECURITY.md in an older selected component does not make a
public issue an appropriate place for a sensitive report. Do not send secrets,
customer records or exploit details to the public feedback form.

Non-sensitive reference feedback uses the [issue chooser](https://github.com/cogno-us/cognous-open-control-stack/issues/new/choose)
and its bounded-reference form. GitHub sign-in is required to submit. Supply
exact source SHA, selected profile, sanitized reproduction, expected/observed
result and public evidence link. Never treat form submission as execution authority.

## Maintainer workflow

Cognous repository maintainers own intake under [GOVERNANCE.md](../GOVERNANCE.md).
This documents responsibility, not a claim of staffed coverage or a response SLA.

1. Classify intake as private security or non-sensitive reference feedback.
2. Keep sensitive details in the private route. Public tracking contains only
   sanitized scope, status and affected revision; do not quote leaked content.
3. Identify the affected component and exact selected revision; distinguish
   historical evidence, current selected behavior and optional candidate work.
4. Record an accountable maintainer and a disposition: needs information,
   confirmed, out of scope, or resolved with linked checks. Maintainers must
   confirm availability before promising response times.
5. For a confirmed issue, prepare a bounded reviewable change, verify its exact
   head, and coordinate any disclosure with the reporter. A fix does not itself
   authorize deployment, retry, production use or release publication.

## Verified route status — 2026-10-13

- Public SECURITY.md and repository security page: unauthenticated HTTP 200.
- No “Report a vulnerability” button was visible in the retrieved security HTML;
  do not advertise GitHub private advisory submission as verified.
- Issue chooser: HTTP 200 after redirect to GitHub sign-in. This verifies the
  authentication boundary, not rendered signed-in form behavior or submission.
- The policy contact's domain has an MX record. DNS is not evidence that the
  individual mailbox accepts mail or that a maintainer receives and triages it.
- No test email, private report, public issue-form submission or reporter contact
  was sent. Mailbox delivery and response remain NOT VERIFIED.

A reporting acceptance record still needs a maintainer attestation or an
explicitly authorized delivery/acknowledgement exercise. Do not infer it from
HTTP status, DNS, a configured address or a successful documentation check.
