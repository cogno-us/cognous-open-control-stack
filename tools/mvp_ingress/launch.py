"""Isolated launcher for the designated ingress process (Python >= 3.11, run with ``-I``).

SPDX-License-Identifier: Apache-2.0

    python -I tools/mvp_ingress/launch.py --state-dir DIR --socket PATH --control-plane ROOT --runtime ROOT

Why: ``python -m tools.mvp_ingress.server`` with the hub as the working directory (or on ``PYTHONPATH``) puts the hub root
ahead of the standard library on ``sys.path``, so a hub-root ``json.py`` (or a package shadowing an ingress import) would be
imported instead of the committed code, and a planted ``__pycache__`` .pyc with a matching header would be read.

What this launcher does (mitigation for these paths only; installed packages are trusted except the checked modules):
``-I`` drops the working directory, the script directory, ``PYTHON*`` variables and the user site from ``sys.path``; a fresh
private ``sys.pycache_prefix`` means no bytecode cache next to the sources is read or written; the launcher refuses to start if
any ``__pycache__`` or .pyc exists under the ingress package; it APPENDS the hub root (computed from this file's own path),
requires each ingress module to resolve to its committed ``.py`` file before running any of them, and removes the hub root
again. ``synthetic_host`` appends the Control Plane / Runtime roots and refuses unless agent_control_plane, engine and tests
(and any other module named like a top-level module of those roots) resolve under them. Non-authorizing; not a defence
against code running as the ingress uid or root, a tampered interpreter, stdlib or site-packages, or the host.
"""
import importlib.machinery
import importlib.util
import os
import sys

import atexit
import shutil
import tempfile

# -I ignores PYTHONDONTWRITEBYTECODE and does not stop the interpreter READING a planted __pycache__/*.pyc. A fresh private
# pycache_prefix (set before any further import) redirects every bytecode cache read/write, for all modules including the
# Control Plane / Runtime, to an empty owner-only temp directory; nothing is written next to the reviewed sources.
sys.dont_write_bytecode = True
_PYC = tempfile.mkdtemp(prefix="mvp-ingress-pyc-")
sys.pycache_prefix = _PYC
atexit.register(shutil.rmtree, _PYC, True)

if sys.version_info < (3, 11) or not sys.flags.isolated:
    sys.stderr.write("launch.py must run with Python >= 3.11 in isolated mode: python -I tools/mvp_ingress/launch.py ...\n")
    sys.exit(2)

HUB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
PKG_DIR = os.path.join(HUB_ROOT, "tools", "mvp_ingress")
MODULES = ("server", "core", "proposal", "synthetic_host")  # every ingress module loaded in the ingress process


def _refuse(why):
    sys.stderr.write("ingress launcher refused: %s\n" % why)
    sys.exit(2)


def _same(origin, expected):
    return bool(origin) and os.path.realpath(origin) == expected


for _dirpath, _dirs, _files in os.walk(PKG_DIR):
    if "__pycache__" in _dirs or any(f.endswith((".pyc", ".pyo")) for f in _files):
        _refuse("bytecode (__pycache__ or .pyc) exists under %s; remove it" % PKG_DIR)

sys.path.append(HUB_ROOT)
try:
    # Resolve (without executing) every ingress module and require the committed source file at the expected path: a package
    # directory, extension module or other file shadowing proposal.py etc. inside the tree is refused before any ingress code runs.
    pkg = importlib.util.find_spec("tools.mvp_ingress")
    if pkg is None or not _same(pkg.origin, os.path.join(PKG_DIR, "__init__.py")):
        _refuse("tools.mvp_ingress does not resolve to this checkout")
    for _name in MODULES:
        _spec = importlib.machinery.PathFinder.find_spec("tools.mvp_ingress." + _name, [PKG_DIR])
        if _spec is None or not isinstance(_spec.loader, importlib.machinery.SourceFileLoader) \
                or not _same(_spec.origin, os.path.join(PKG_DIR, _name + ".py")):
            _refuse("tools.mvp_ingress.%s does not resolve to its source file in this checkout" % _name)
    import tools.mvp_ingress.server as server
    import tools.mvp_ingress.synthetic_host  # noqa: F401  (loaded now, while the hub root is the only extra path entry)
finally:
    sys.path.remove(HUB_ROOT)

if __name__ == "__main__":
    sys.exit(server.main())
