# Security Policy

This repository is the public stack hub. It includes documentation, qualification
tools, tests and synthetic evidence. It is not a production deployment or a
security boundary for downstream systems. Repository contents and scanner
results must not be interpreted as a guarantee that sensitive information is
absent; report suspected exposure privately through the route below.

## Reporting a vulnerability

GitHub Private Vulnerability Reporting is the primary route. To report a
suspected vulnerability in this repository, use **Security > Report a
vulnerability** on the repository's
[Security tab](https://github.com/cogno-us/cognous-open-control-stack/security),
or open the advisory report form directly:
<https://github.com/cogno-us/cognous-open-control-stack/security/advisories/new>.
The report is visible only to you and the repository maintainers. GitHub sign-in
is required to submit.

Please include, using synthetic or redacted data wherever possible:

- the affected file, document, workflow or component and the exact commit SHA;
- a description of the issue and its security impact;
- minimal steps to reproduce, or a proof of concept that avoids real secrets,
  customer data or production systems;
- any suggested remediation, and how you would like to be credited, if at all.

Do not post sensitive exploit details, secrets or personal data in public
issues, pull requests, discussions or the public feedback form. If you are
unsure whether something is sensitive, report it privately first.

We will acknowledge valid reports as soon as practicable and coordinate remediation privately.

Other Cognous repositories maintain their own reporting routes.

## Scope

In scope:
- accidental disclosure of sensitive information;
- broken links to malicious or incorrect locations;
- documentation errors that could create unsafe implementation assumptions.

Out of scope:
- requests for security guarantees;
- compliance certification claims;
- production deployment review;
- vulnerabilities in downstream systems not maintained by Cognous.

## Intake and verification status

See [reporting and triage](docs/security-reporting-and-triage.md) for maintainer
responsibilities and observed route coverage. GitHub Private Vulnerability
Reporting was observed enabled on 2026-11-03 (see
[reporting route observation](docs/releases/reporting-route-verification-20261103.json));
no private report was submitted. No response-time guarantee or production
assurance is implied.
