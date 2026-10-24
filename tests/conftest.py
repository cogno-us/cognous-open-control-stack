"""Hermetic bytecode handling for the suite.

The ingress launcher and the candidate-manifest validator refuse a tools/mvp_ingress (or tools/mvp_env_record) tree that
contains __pycache__ or .pyc files. Importing those packages from the tests must therefore never leave bytecode there:
disable bytecode writing for this process and every child process, and remove stale generated caches at session start.
SPDX-License-Identifier: Apache-2.0
"""
import os
import pathlib
import shutil
import sys

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

_TOOLS = pathlib.Path(__file__).resolve().parents[1] / "tools"
for _pkg in ("mvp_ingress", "mvp_env_record"):
    shutil.rmtree(_TOOLS / _pkg / "__pycache__", ignore_errors=True)
