"""Hub-3 (R0 P1 item 12): durable project-level security reporting route."""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PVR_URL = "https://github.com/cogno-us/cognous-open-control-stack/security/advisories/new"
ACK = "We will acknowledge valid reports as soon as practicable and coordinate remediation privately."
PERSONAL = "andredelima@cogno.us"
OLD = ROOT / "docs/releases/reporting-route-verification.json"
NEW = ROOT / "docs/releases/reporting-route-verification-20261103.json"


def flat(rel):
    """File text with whitespace runs collapsed (Markdown hard wraps)."""
    return " ".join((ROOT / rel).read_text(encoding="utf-8").split())


def security():
    return flat("SECURITY.md")


def test_pvr_link_and_route_present():
    s = security()
    assert PVR_URL in s
    assert "Report a vulnerability" in s
    assert "Private Vulnerability Reporting" in s
    assert ACK in s


def test_reporter_guidance_present_and_no_sla():
    s = security()
    assert "Do not post sensitive exploit details" in s
    assert "Scope" in s and "In scope" in s
    assert not re.search(r"within\s+\d+\s*(hour|day|business)", s, re.I)


def test_no_personal_mailbox_is_sole_route():
    s = security()
    assert PERSONAL not in s
    assert "security@cogno.us" not in s
    assert "mailto:" not in s
    for rel in ("README.md", "CONTRIBUTING.md", "docs/security-reporting-and-triage.md",
                ".github/ISSUE_TEMPLATE/config.yml"):
        assert PERSONAL not in flat(rel), rel
    # any address that remains must not be the only route: PVR link is present
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", s):
        assert PVR_URL in s


def test_other_references_consistent():
    assert PVR_URL in flat(".github/ISSUE_TEMPLATE/config.yml")
    for rel in ("README.md", "CONTRIBUTING.md", "docs/security-reporting-and-triage.md"):
        assert "Private Vulnerability Reporting" in flat(rel), rel


def test_stale_evidence_superseded_by_newer_observation():
    old = json.loads(OLD.read_text())
    new = json.loads(NEW.read_text())
    # history preserved: old record still says what it said on 2026-10-13
    assert old["date"] == "2026-10-13"
    assert old["github_private_reporting_verified"] is False
    assert date.fromisoformat(new["date"]) > date.fromisoformat(old["date"])
    assert new["github_private_reporting_enabled"] is True
    assert new["github_private_reporting_verified"] is True
    assert any(x["path"] == "docs/releases/reporting-route-verification.json" for x in new["supersedes"])
    assert new["report_route_url"] == PVR_URL
    doc = flat("docs/security-reporting-and-triage.md")
    assert "reporting-route-verification-20261103.json" in doc
    assert "superseded" in doc.lower()
    assert "2026-11-03" in doc
