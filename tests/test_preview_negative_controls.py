#!/usr/bin/env python3
"""Adversarial, offline mutation controls for the PR #77 preview checker.

Each broken fixture MUST fail the unmodified checker. A matching checker mutant
MUST accept that broken fixture, proving the fixture actually exercises its guard.
If a guard is removed from production, the first assertion kills the regression.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHECKER = "tools/check_preview_entries.py"
EXCLUDE = shutil.ignore_patterns(".git", ".reference-work", "node_modules", ".venv",
                                 "__pycache__", ".pytest_cache", "results")


class PreviewNegativeControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="preview-negative-")
        self.addCleanup(self.temp.cleanup)
        self.repo = pathlib.Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.repo, ignore=EXCLUDE)
        self.checker = self.repo / CHECKER
        self.original = self.checker.read_text(encoding="utf-8")
        self.assert_checker(0, "clean baseline")

    def run_checker(self):
        return subprocess.run([sys.executable, str(self.checker)], cwd=self.repo,
                              capture_output=True, text=True, timeout=30)

    def assert_checker(self, expected, label):
        result = self.run_checker()
        self.assertEqual(result.returncode, expected,
                         f"{label}: stdout={result.stdout!r} stderr={result.stderr!r}")

    def append_link(self, link):
        page = self.repo / "README.md"
        page.write_text(page.read_text(encoding="utf-8") + "\n" + link + "\n",
                        encoding="utf-8")

    def assert_guard_sensitive(self, replacement_from, replacement_to, label):
        self.assertIn(replacement_from, self.original, f"{label}: guard source changed")
        self.assert_checker(1, f"{label} negative fixture")
        self.checker.write_text(self.original.replace(replacement_from, replacement_to, 1),
                                encoding="utf-8")
        self.assert_checker(0, f"{label} bypass mutant must evade detection")

    def test_missing_local_file(self):
        self.append_link("[missing](docs/pv-neg-definitely-absent.md)")
        self.assert_guard_sensitive(
            "if not target.is_relative_to(ROOT.resolve()) or not target.exists():",
            "if False:", "missing local file")

    def test_invalid_anchor(self):
        self.append_link("[bad anchor](docs/start-here.md#pv-neg-absent-anchor)")
        self.assert_guard_sensitive(
            "if unquote(parsed.fragment).lower() not in anchors(target.read_text(encoding=\"utf-8\")):",
            "if False:", "invalid anchor")

    def test_repository_escape(self):
        outside = pathlib.Path(self.temp.name) / "outside.md"
        outside.write_text("# Outside repository\n", encoding="utf-8")
        self.append_link("[escape](../outside.md)")
        self.assert_guard_sensitive(
            "if not target.is_relative_to(ROOT.resolve()) or not target.exists():",
            "if not target.exists():", "repository escape to existing file")

    def test_operational_hold_disclaimer(self):
        start = self.repo / "docs/start-here.md"
        text = start.read_text(encoding="utf-8")
        self.assertIn("#30", text)
        start.write_text(text.replace("#30", "#XX"), encoding="utf-8")
        self.assert_guard_sensitive(
            '"operational HOLD": "#30" in start and "HOLD" in start,',
            '"operational HOLD": True,', "operational HOLD")

    def test_c0_disclaimer(self):
        release = self.repo / "docs/release-status.md"
        start = self.repo / "docs/start-here.md"
        original_release = release.read_text(encoding="utf-8")
        original_start = start.read_text(encoding="utf-8")
        self.assertIn("not destination commit atomicity", original_release.lower())
        self.assertIn("not atomic with the destination commit", original_start.lower())
        release.write_text(original_release.replace("not destination commit atomicity",
                                                   "atomic with the destination commit"),
                           encoding="utf-8")
        start.write_text(original_start.replace("not atomic with the destination commit",
                                               "atomic with the destination commit"),
                         encoding="utf-8")
        self.assert_guard_sensitive(
            '"C0 not atomic": "not destination commit atomicity" in release.lower() or "not atomic with the destination commit" in start.lower(),',
            '"C0 not atomic": True,', "C0 disclaimer")

    def test_c1_disclaimer(self):
        release = self.repo / "docs/release-status.md"
        text = release.read_text(encoding="utf-8")
        self.assertIn("optional", text.lower())
        release.write_text(text.replace("optional", "separately available").replace(
            "Optional", "Separately available"), encoding="utf-8")
        self.assert_guard_sensitive(
            '"C1 optional": "C1" in release and "optional" in release.lower(),',
            '"C1 optional": True,', "C1 optional disclaimer")

    def test_c2_c3_disclaimer(self):
        release = self.repo / "docs/release-status.md"
        text = release.read_text(encoding="utf-8")
        self.assertIn("No release claim", text)
        release.write_text(text.replace("No release claim", "Release claim"),
                           encoding="utf-8")
        self.assert_guard_sensitive(
            '"C2/C3 unqualified": "C2/C3" in release and "No release claim" in release,',
            '"C2/C3 unqualified": True,', "C2/C3 disclaimer")


if __name__ == "__main__":
    unittest.main()
