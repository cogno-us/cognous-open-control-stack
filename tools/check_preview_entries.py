#!/usr/bin/env python3
"""Offline, non-authorizing preview entrypoint link/anchor and trust-claim smoke check."""
import pathlib
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGES = ["README.md", "docs/start-here.md", "docs/quickstart.md",
         "docs/governance-quickstart.md", "docs/release-status.md",
         "docs/preview-entry-audit.md", "CONTRIBUTING.md", "SECURITY.md"]
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.+)$", re.M)


def anchors(text):
    seen = {}
    ids = set()
    for heading in HEADING.findall(text):
        h = re.sub(r"<[^>]+>", "", heading).lower()
        h = re.sub(r"[^\w -]", "", h).strip().replace(" ", "-")
        n = seen.get(h, 0)
        seen[h] = n + 1
        ids.add(h if n == 0 else f"{h}-{n}")
    ids.update(re.findall(r'<a\s+(?:name|id)="([^"]+)"', text))
    return ids


def check():
    failures = []
    checked = 0
    for name in PAGES:
        path = ROOT / name
        if not path.is_file():
            failures.append(f"{name}: missing entrypoint")
            continue
        text = path.read_text(encoding="utf-8")
        for raw in LINK.findall(text):
            url = raw.strip().split(" ", 1)[0].strip("<>")
            parsed = urlsplit(url)
            if parsed.scheme in ("http", "https", "mailto"):
                continue  # External status requires online independent verification.
            if parsed.scheme or url.startswith("//"):
                failures.append(f"{name}: unsupported link {url}")
                continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not target.is_relative_to(ROOT.resolve()) or not target.exists():
                failures.append(f"{name}: missing/escaping target {url}")
                continue
            checked += 1
            if parsed.fragment and target.is_file() and target.suffix.lower() == ".md":
                if unquote(parsed.fragment).lower() not in anchors(target.read_text(encoding="utf-8")):
                    failures.append(f"{name}: missing anchor {url}")
    start = (ROOT / "docs/start-here.md").read_text()
    release = (ROOT / "docs/release-status.md").read_text()
    for label, found in {
        "operational HOLD": "#30" in start and "HOLD" in start,
        "C0 not atomic": "not destination commit atomicity" in release.lower() or "not atomic with the destination commit" in start.lower(),
        "C1 optional": "C1" in release and "optional" in release.lower(),
        "C2/C3 unqualified": "C2/C3" in release and "No release claim" in release,
    }.items():
        if not found:
            failures.append(f"missing required release disclaimer: {label}")
    print(f"preview entries={len(PAGES)}, local links checked={checked}, failures={len(failures)}")
    for failure in failures:
        print("FAIL:", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(check())
