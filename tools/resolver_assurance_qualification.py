#!/usr/bin/env python3
"""Run only the bounded synthetic observation suite and retain exact evidence."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_resolver_assurance.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    source_paths = ["reference_profiles/resolver_assurance.py", "tests/test_resolver_assurance.py",
                    "tools/resolver_assurance_qualification.py", ".github/workflows/resolver-observation-assurance.yml",
                    "docs/workstreams/resolver-observation-assurance.md", "component-lock.json"]
    changes = subprocess.check_output(["git", "status", "--porcelain", "--", *source_paths], cwd=ROOT, text=True).splitlines()
    report = {
        "contract": "synthetic-authority-observation-tests/1",
        "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "component_lock_sha256": hashlib.sha256((ROOT / "component-lock.json").read_bytes()).hexdigest(),
        "python": platform.python_version(), "platform": platform.system(),
        "source_changes": changes,
        "file_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in source_paths},
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "production_qualified": False,
        "qualified": result.wasSuccessful() and result.testsRun == 20 and not result.skipped and not changes,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["qualified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
