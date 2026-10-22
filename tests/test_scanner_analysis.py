import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import scanner_analysis_model as m
from tools import scanner_tree_analysis as t

TAG = re.compile(r"</?([a-z][a-z0-9-]*)[^<>]*>")
ELEMENTS = {"b", "br", "sup", "em", "strong"}


def scan(text):
    return m.scan_text("f.txt", text, table=m.union_table({}), tag=TAG, html_elements=ELEMENTS)


def rules(text, visibility="visible"):
    return {f.rule for f in scan(text) if f.visibility == visibility}


class ModelTests(unittest.TestCase):
    def test_escaped_whitespace_in_source_strings_is_a_break(self):
        self.assertIn("certified", rules('x = "certified\\n"'))
        self.assertIn("production-ready", rules('x = "production\\tready"'))

    def test_production_safe_is_deferred_not_matched(self):
        self.assertEqual(rules("production safe"), set())
        for lead in ("enterprise", "prod", "deployment", "deploy", "audit"):
            self.assertEqual(rules(f"{lead} safe"), set(), lead)

    def test_for_and_approved_forms_are_adopted(self):
        for text in ("safe for deploy", "ready for production", "deploy approved", "deployment cleared"):
            self.assertIn("production-ready", rules(text), text)

    def test_attested_union(self):
        for text in ("SOC 2 audit", "SOC 2 Type II audit", "attestation for SOC 2", "attested SOC 1"):
            self.assertIn("attested", rules(text), text)
        self.assertEqual(rules("SOC 4 audit"), set())

    def test_dual_view_markup_and_underscores(self):
        for text in ("cert<br>ified", "cert<!-- c -->ified", "cert_ified", "__certified__", "_certified_", "cert*ifi*ed"):
            self.assertIn("certified", rules(text), text)

    def test_unknown_tag_text_is_not_deleted(self):
        self.assertIn("certified", rules("if a<b certified c>d"))

    def test_comment_only_claim_is_reported_hidden(self):
        found = scan("<!-- certified -->")
        self.assertEqual([(f.rule, f.visibility) for f in found], [("certified", "hidden_comment")])
        self.assertEqual(rules("<!-- certified -->"), set())
        self.assertEqual(rules("<!-- certified --> certified"), {"certified"})

    def test_sigma_variants_fold_to_c(self):
        self.assertIn("certified", rules("ςertified"))
        self.assertIn("certified", rules("ϲertified"))

    def test_lines_are_reported_from_the_source(self):
        f = scan("ok\nplain\n certified \n")[0]
        self.assertEqual((f.line, f.text), (3, "certified"))


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


class TreeTests(unittest.TestCase):
    def make(self, tmp):
        root = Path(tmp)
        git(root, "init", "-q")
        git(root, "config", "user.email", "t@example.invalid")
        git(root, "config", "user.name", "t")
        (root / "scripts").mkdir()
        (root / "a.md").write_text("certified\n", encoding="utf-8")
        (root / "b.png").write_bytes(b"certified")
        (root / "n.bin").write_bytes(b"cert\0ified")
        (root / "bad.txt").write_bytes(b"\xff\xfe")
        (root / t.ALLOWLIST).write_text("{}", encoding="utf-8")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "x")
        return root

    def test_file_selection_and_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            items = list(t.read_texts(root))
            texts = [i for i in items if i[0]]
            skipped = dict(items[-1][1])
            self.assertEqual([p for p, _ in texts], ["a.md"])
            self.assertEqual(set(skipped), {"b.png", "n.bin", "bad.txt", t.ALLOWLIST})

    def test_excusal_is_exact_path_rule_and_line(self):
        allow = {"excluded_paths": [{"path": "docs/"}, {"path": "x.md"}],
                 "allowed": [{"path": "a.md", "rule": "certified", "line": "certified"}]}
        hit = {"path": "a.md", "rule": "certified", "text": "certified"}
        self.assertTrue(t.excused(hit, allow))
        self.assertFalse(t.excused({**hit, "rule": "compliant"}, allow))
        self.assertFalse(t.excused({**hit, "text": "certified!"}, allow))
        self.assertFalse(t.excused({**hit, "path": "b.md"}, allow))
        self.assertTrue(t.excluded("docs/x.md", allow) and t.excluded("x.md", allow))
        self.assertFalse(t.excluded("docsx/y.md", allow) or t.excluded("x.md.bak", allow))

    def test_cli_absent_is_none_and_missing_allowlist_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(t.cli(tmp))
            self.assertEqual(t.load_allowlist(tmp), {"excluded_paths": [], "allowed": []})


if __name__ == "__main__":
    unittest.main()
