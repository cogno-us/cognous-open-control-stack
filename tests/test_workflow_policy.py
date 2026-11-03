"""Regression tests for tools/check_workflow_policy.py (P1 item 11: workflow credential policy).

Needs PyYAML (tools/requirements-workflow-policy.lock). It is not in the release lock, so the
tests skip when PyYAML is absent unless REQUIRE_PYYAML=1 (set by the workflow-policy CI job).
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

try:
    import yaml  # noqa: F401
except ImportError:
    yaml = None
    if os.environ.get("REQUIRE_PYYAML") == "1":
        raise

import importlib

policy = importlib.import_module("check_workflow_policy") if yaml else None
SHA = "a" * 40
CHECKOUT = "actions/checkout@" + SHA
TODAY = datetime.date(2026, 11, 3)

GOOD = """\
name: ok
on:
  pull_request:
permissions:
  contents: read
jobs:
  j:
    runs-on: ubuntu-22.04
    steps:
      - uses: %s
        with:
          persist-credentials: false
      - run: echo hi
""" % CHECKOUT


def repl(**kw):
    text = GOOD
    for old, new in kw.items():
        text = text.replace(old, new)
    return text


@unittest.skipIf(yaml is None, "PyYAML not installed")
class Base(unittest.TestCase):
    def check(self, files, exceptions=None, today=TODAY):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            for rel, text in files.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
            ex = root / "ex.json"
            ex.write_text(json.dumps(exceptions if exceptions is not None else {"schema_version": 1, "exceptions": []}))
            return policy.run(root, ex, today)

    def wf(self, text, name="w.yml"):
        return self.check({".github/workflows/" + name: text})

    def rules(self, text):
        violations, errors, _ = self.wf(text)
        self.assertEqual(errors, [])
        return sorted({v["rule"] for v in violations})


class RepositoryPolicy(Base):
    def test_repository_is_clean_with_empty_exception_set(self):
        violations, errors, count = policy.run(ROOT)
        self.assertEqual(violations, [])
        self.assertEqual(errors, [])
        self.assertGreaterEqual(count, 44)

    def test_exception_set_starts_empty(self):
        data = json.loads((ROOT / policy.EXCEPTIONS_REL).read_text())
        self.assertEqual(data, {"schema_version": 1, "exceptions": []})

    def test_cli_exit_codes(self):
        ok = subprocess.run([sys.executable, str(ROOT / "tools/check_workflow_policy.py")], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        with tempfile.TemporaryDirectory() as d:
            wf = pathlib.Path(d, ".github/workflows")
            wf.mkdir(parents=True)
            (wf / "w.yml").write_text(repl(**{"persist-credentials: false": "persist-credentials: true"}))
            (pathlib.Path(d) / "docs/security").mkdir(parents=True)
            (pathlib.Path(d) / policy.EXCEPTIONS_REL).write_text('{"schema_version":1,"exceptions":[]}')
            bad = subprocess.run([sys.executable, str(ROOT / "tools/check_workflow_policy.py"), "--root", d], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("WP01", bad.stdout)

    def test_every_repo_checkout_is_explicitly_false(self):
        seen = 0
        for path in policy.workflow_files(ROOT):
            doc = policy.load_yaml_text(path.read_text())
            for job in (doc.get("jobs") or {}).values():
                for step in job.get("steps") or []:
                    if str(step.get("uses", "")).startswith("actions/checkout"):
                        seen += 1
                        self.assertIs((step.get("with") or {}).get("persist-credentials"), False, path.name)
        self.assertGreaterEqual(seen, 27)

    def test_reusable_cognous_callers_are_full_sha_pinned(self):
        calls = 0
        for path in policy.workflow_files(ROOT):
            doc = policy.load_yaml_text(path.read_text())
            for job in (doc.get("jobs") or {}).values():
                if str(job.get("uses", "")).startswith("cogno-us/"):
                    calls += 1
                    self.assertRegex(job["uses"], r"@[0-9a-f]{40}$")
                    self.assertNotIn("secrets", job)
        self.assertEqual(calls, 21)

    def test_policy_workflow_itself_complies(self):
        doc = policy.load_yaml_text((ROOT / ".github/workflows/workflow-policy.yml").read_text())
        self.assertEqual(doc["permissions"], {"contents": "read"})
        self.assertEqual(policy.check_doc("workflow-policy.yml", doc), [])


class PositiveFixture(Base):
    def test_good_fixture_passes(self):
        self.assertEqual(self.rules(GOOD), [])

    def test_on_key_is_parsed_as_trigger(self):
        doc = policy.load_yaml_text(GOOD)
        self.assertIn("on", doc)
        self.assertNotIn(True, doc)
        self.assertEqual(policy.triggers(doc), ["pull_request"])

    def test_local_action_path_is_exempt_from_pinning(self):
        self.assertEqual(self.rules(repl(**{"      - run: echo hi": "      - uses: ./.github/actions/x"})), [])

    def test_docker_digest_pin_passes(self):
        digest = "docker://alpine@sha256:" + "b" * 64
        self.assertEqual(self.rules(repl(**{"      - run: echo hi": "      - uses: " + digest})), [])


class NegativeRules(Base):
    # WP01
    def test_wp01_unset(self):
        t = repl(**{"        with:\n          persist-credentials: false\n": ""})
        self.assertEqual(self.rules(t), ["WP01"])

    def test_wp01_true(self):
        self.assertEqual(self.rules(repl(**{"credentials: false": "credentials: true"})), ["WP01"])

    def test_wp01_string_false_rejected(self):
        self.assertEqual(self.rules(repl(**{"credentials: false": "credentials: 'false'"})), ["WP01"])

    def test_wp01_expression_rejected(self):
        self.assertEqual(self.rules(repl(**{"credentials: false": "credentials: ${{ inputs.x }}"})), ["WP01"])

    def test_wp01_with_present_but_key_missing(self):
        t = repl(**{"          persist-credentials: false": "          fetch-depth: 0"})
        self.assertEqual(self.rules(t), ["WP01"])

    def test_wp01_uppercase_checkout_and_subpath(self):
        t = repl(**{CHECKOUT: "Actions/Checkout@" + SHA})
        t = t.replace("          persist-credentials: false\n", "")
        self.assertIn("WP01", self.rules(t))

    def test_wp01_reports_file_job_step(self):
        t = repl(**{"        with:\n          persist-credentials: false\n": ""})
        violations, _, _ = self.wf(t)
        v = violations[0]
        self.assertEqual((v["file"], v["job"], v["step"], v["rule"]), (".github/workflows/w.yml", "j", 0, "WP01"))

    def test_wp01_composite_action(self):
        action = ("name: a\nruns:\n  using: composite\n  steps:\n    - uses: %s\n    - run: x\n      shell: bash\n" % CHECKOUT)
        violations, errors, _ = self.check({".github/actions/a/action.yml": action})
        self.assertEqual([v["rule"] for v in violations], ["WP01"])
        self.assertEqual(violations[0]["job"], "(composite)")

    # WP02
    def test_wp02_missing_workflow_permissions(self):
        self.assertEqual(self.rules(repl(**{"permissions:\n  contents: read\n": ""})), ["WP02"])

    def test_wp02_string_permissions_rejected(self):
        self.assertEqual(self.rules(repl(**{"permissions:\n  contents: read\n": "permissions: read-all\n"})), ["WP02"])

    def test_wp02_job_widening_rejected(self):
        t = repl(**{"    runs-on: ubuntu-22.04\n": "    runs-on: ubuntu-22.04\n    permissions:\n      contents: read\n      issues: read\n"})
        self.assertEqual(self.rules(t), ["WP02"])

    def test_wp02_job_narrowing_allowed(self):
        t = repl(**{"    runs-on: ubuntu-22.04\n": "    runs-on: ubuntu-22.04\n    permissions: {}\n"})
        self.assertEqual(self.rules(t), [])

    def test_wp02_invalid_level(self):
        self.assertEqual(self.rules(repl(**{"contents: read": "contents: admin"})), ["WP02"])

    # WP03
    def test_wp03_workflow_write(self):
        self.assertEqual(self.rules(repl(**{"contents: read": "contents: write"})), ["WP03"])

    def test_wp03_job_write(self):
        t = repl(**{"    runs-on: ubuntu-22.04\n": "    runs-on: ubuntu-22.04\n    permissions:\n      contents: write\n"})
        self.assertIn("WP03", self.rules(t))

    def test_wp03_write_all_string(self):
        self.assertEqual(self.rules(repl(**{"permissions:\n  contents: read\n": "permissions: write-all\n"})), ["WP02"])

    # WP04
    def test_wp04_pull_request_target(self):
        self.assertEqual(self.rules(repl(**{"  pull_request:\n": "  pull_request_target:\n"})), ["WP04"])

    def test_wp04_workflow_run(self):
        t = repl(**{"  pull_request:\n": "  workflow_run:\n    workflows: [x]\n    types: [completed]\n"})
        self.assertEqual(self.rules(t), ["WP04"])

    def test_wp04_list_and_string_forms(self):
        self.assertEqual(self.rules(repl(**{"on:\n  pull_request:\n": "on: [push, pull_request_target]\n"})), ["WP04"])
        self.assertEqual(self.rules(repl(**{"on:\n  pull_request:\n": "on: workflow_run\n"})), ["WP04"])

    def test_wp04_quoted_on_key(self):
        self.assertEqual(self.rules(repl(**{"on:\n  pull_request:\n": "'on':\n  pull_request_target:\n"})), ["WP04"])

    # WP05
    def test_wp05_secrets_expression(self):
        t = repl(**{"      - run: echo hi": "      - run: echo hi\n        env:\n          X: ${{ secrets.FOO }}"})
        self.assertEqual(self.rules(t), ["WP05"])

    def test_wp05_github_token_expression(self):
        t = repl(**{"      - run: echo hi": "      - run: echo hi\n        env:\n          T: ${{ github.token }}"})
        self.assertEqual(self.rules(t), ["WP05"])

    def test_wp05_GITHUB_TOKEN_env_name(self):
        t = repl(**{"      - run: echo hi": "      - run: python x.py\n        env:\n          GITHUB_TOKEN: abc"})
        self.assertEqual(self.rules(t), ["WP05"])

    def test_wp05_checkout_token_input(self):
        t = repl(**{"          persist-credentials: false": "          persist-credentials: false\n          token: ${{ inputs.t }}"})
        self.assertEqual(self.rules(t), ["WP05"])

    def test_wp05_reusable_secrets_inherit(self):
        t = ("name: c\non: pull_request\npermissions:\n  contents: read\njobs:\n  c:\n    uses: cogno-us/x/.github/workflows/y.yml@%s\n"
             "    secrets: inherit\n" % SHA)
        self.assertEqual(self.rules(t), ["WP05"])

    # WP06
    def test_wp06_tag_ref(self):
        self.assertEqual(self.rules(repl(**{CHECKOUT: "actions/checkout@v4"})), ["WP06"])

    def test_wp06_branch_ref(self):
        self.assertEqual(self.rules(repl(**{CHECKOUT: "actions/checkout@main"})), ["WP06"])

    def test_wp06_short_sha(self):
        self.assertEqual(self.rules(repl(**{CHECKOUT: "actions/checkout@" + "a" * 39})), ["WP06"])

    def test_wp06_uppercase_sha(self):
        self.assertEqual(self.rules(repl(**{CHECKOUT: "actions/checkout@" + "A" * 40})), ["WP06"])

    def test_wp06_missing_ref(self):
        self.assertEqual(self.rules(repl(**{CHECKOUT: "actions/checkout"})), ["WP06"])

    def test_wp06_third_party_action_unpinned(self):
        self.assertEqual(self.rules(repl(**{"      - run: echo hi": "      - uses: someone/tool@v1"})), ["WP06"])

    def test_wp06_docker_tag(self):
        self.assertEqual(self.rules(repl(**{"      - run: echo hi": "      - uses: docker://alpine:3.19"})), ["WP06"])

    def test_wp06_cognous_reusable_floating_ref(self):
        base = "name: c\non: pull_request\npermissions:\n  contents: read\njobs:\n  c:\n    uses: cogno-us/cognous-stack-qualification/.github/workflows/y.yml@%s\n"
        self.assertEqual(self.rules(base % "main"), ["WP06"])
        self.assertEqual(self.rules(base % ("0" * 7)), ["WP06"])
        self.assertEqual(self.rules(base % SHA), [])

    # WP07
    def test_wp07_duplicate_key(self):
        self.assertIn("WP07", self.rules(GOOD + "permissions:\n  contents: read\n"))

    def test_wp07_unsafe_python_tag_not_executed(self):
        violations, _, _ = self.wf("name: !!python/object/apply:os.system ['true']\non: push\n")
        self.assertEqual([v["rule"] for v in violations], ["WP07"])

    def test_wp07_non_mapping_and_syntax_error(self):
        self.assertIn("WP07", self.rules("- a\n- b\n"))
        self.assertIn("WP07", self.rules("a: [unclosed\n"))

    def test_violations_sorted_deterministic(self):
        files = {".github/workflows/%s.yml" % n: repl(**{"credentials: false": "credentials: true"}) for n in "zma"}
        v1, _, _ = self.check(files)
        v2, _, _ = self.check(files)
        self.assertEqual(v1, v2)
        self.assertEqual([v["file"] for v in v1], sorted(v["file"] for v in v1))


class Exceptions(Base):
    BAD = repl(**{"credentials: false": "credentials: true"})

    def ex(self, **kw):
        e = {"workflow": ".github/workflows/w.yml", "job": "j", "step": 0, "rule": "WP01",
             "rationale": "needed for push", "expires": "2027-01-01"}
        e.update(kw)
        return {"schema_version": 1, "exceptions": [e]}

    def run_ex(self, ex, text=None):
        return self.check({".github/workflows/w.yml": text or self.BAD}, ex)

    def test_valid_exception_suppresses_matching_violation_only(self):
        violations, errors, _ = self.run_ex(self.ex())
        self.assertEqual((violations, errors), ([], []))

    def test_exception_does_not_suppress_other_step_or_rule(self):
        violations, errors, _ = self.run_ex(self.ex(step=1))
        self.assertTrue(violations)
        self.assertTrue(any("stale" in e for e in errors))

    def test_stale_exception_when_no_violation(self):
        _, errors, _ = self.run_ex(self.ex(), GOOD)
        self.assertTrue(any("stale" in e and "suppresses no violation" in e for e in errors))

    def test_stale_exception_missing_job_or_workflow(self):
        _, errors, _ = self.run_ex(self.ex(job="nope"))
        self.assertTrue(any("does not exist" in e for e in errors))
        _, errors, _ = self.run_ex(self.ex(workflow=".github/workflows/gone.yml"))
        self.assertTrue(any("does not exist" in e for e in errors))

    def test_expired_exception_fails(self):
        violations, errors, _ = self.run_ex(self.ex(expires="2026-11-02"))
        self.assertTrue(violations)
        self.assertTrue(any("expired" in e for e in errors))

    def test_schema_violations_fail(self):
        for bad in (
            {"schema_version": 1},
            {"schema_version": 2, "exceptions": []},
            {"schema_version": 1, "exceptions": [], "extra": 1},
            {"schema_version": 1, "exceptions": {}},
            self.ex(rationale=""),
            self.ex(rationale="   "),
            self.ex(expires="soon"),
            self.ex(expires="2027-13-45"),
            self.ex(step="0"),
            self.ex(step=-1),
            self.ex(rule="WP04"),
            self.ex(rule="WP06"),
            self.ex(rule="WP99"),
        ):
            with self.subTest(bad=bad):
                _, errors, _ = self.run_ex(bad)
                self.assertTrue(errors, bad)

    def test_extra_exception_key_rejected(self):
        ex = self.ex()
        ex["exceptions"][0]["note"] = "x"
        _, errors, _ = self.run_ex(ex)
        self.assertTrue(errors)

    def test_missing_or_invalid_json_file_fails(self):
        exc, errors = policy.load_exceptions(ROOT / "does-not-exist.json")
        self.assertTrue(errors)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as f:
            f.write("{nope")
            f.flush()
            self.assertTrue(policy.load_exceptions(f.name)[1])

    def test_write_exception_refused_for_pr_reachable_workflow(self):
        text = repl(**{"contents: read": "contents: write"})
        violations, errors, _ = self.run_ex(self.ex(rule="WP03", step=None), text)
        self.assertTrue(violations)
        self.assertTrue(any("fork/PR-reachable" in e for e in errors))

    def test_write_exception_allowed_for_job_in_non_pr_workflow(self):
        text = repl(**{"  pull_request:\n": "  workflow_dispatch:\n",
                       "    runs-on: ubuntu-22.04\n": "    runs-on: ubuntu-22.04\n    permissions:\n      contents: write\n"})
        violations, errors, _ = self.run_ex(self.ex(rule="WP03", step=None), text)
        self.assertEqual((violations, errors), ([], []))
        # without the exception the same workflow fails on WP03 only
        self.assertEqual(self.rules(text), ["WP03"])


if __name__ == "__main__":
    unittest.main()
