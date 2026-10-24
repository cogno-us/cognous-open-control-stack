"""Isolated launcher for the designated ingress process (Python >= 3.11, run with ``-I``).

SPDX-License-Identifier: Apache-2.0

    python -I tools/mvp_ingress/launch.py --state-dir DIR --socket PATH --control-plane ROOT --runtime ROOT

Why: ``python -m tools.mvp_ingress.server`` with the hub as the working directory (or on ``PYTHONPATH``) puts the hub root
ahead of the standard library on ``sys.path``, so a hub-root ``json.py`` (or a package shadowing an ingress import) would be
imported instead of the committed code. ``-I`` drops the working directory, the script directory, ``PYTHON*`` environment
variables and the user site from ``sys.path``. This launcher then APPENDS the hub root (computed from this file's own path),
imports the committed ingress package, verifies it came from that root, and removes the hub root again, so the hub's own
``tests`` package cannot shadow the Control Plane's. Component roots are appended later by ``synthetic_host`` (after the
standard library and site-packages). This narrows import resolution only; it is non-authorizing and does not change authority
or provenance logic, and it is not a defence against code running as the ingress uid or root, or against a tampered
site-packages.
"""
import importlib.machinery
import importlib.util
import os
import sys

sys.dont_write_bytecode = True  # -I ignores PYTHONDONTWRITEBYTECODE; never write __pycache__ into the reviewed tree

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
