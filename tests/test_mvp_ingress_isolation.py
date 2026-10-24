"""MVP ingress launcher isolation: working-directory / hub-root shadow files must not be imported (synthetic, Linux).

SPDX-License-Identifier: Apache-2.0

Each test copies the ingress package (and launcher) into a scratch "hub root", plants a shadow there, and starts the ingress
with that directory as the working directory and on PYTHONPATH. The supported form (``python -I tools/mvp_ingress/launch.py``)
must not import the shadow; the former form (``python -m tools.mvp_ingress.server``) is shown to import it. Integration tests
need MVP_INGRESS_CP_ROOT / MVP_INGRESS_RUNTIME_ROOT and an interpreter with the hash-locked dependencies. This narrows import
resolution only; it claims nothing about code running as the ingress uid or root, a tampered site-packages, or the host.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import textwrap

import pytest

from tools.mvp_ingress import client as client_mod
from tools.mvp_ingress import proposal as P

HUB = pathlib.Path(__file__).resolve().parents[1]
CP = os.environ.get("MVP_INGRESS_CP_ROOT")
RT = os.environ.get("MVP_INGRESS_RUNTIME_ROOT")
needs_components = pytest.mark.skipif(not (CP and RT), reason="set MVP_INGRESS_CP_ROOT and MVP_INGRESS_RUNTIME_ROOT")
needs_py311 = pytest.mark.skipif(sys.version_info < (3, 11), reason="launcher requires Python >= 3.11")
GOOD = {"schema": P.SCHEMA, "request_id": "case-1", "customer_id": "customer-001", "amount": 10, "unit": "USD",
        "refund_reason": "duplicate"}
MARK = "SHADOW_IMPORTED"


def _marker_module(path: pathlib.Path, marker: pathlib.Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("open(%r, 'a').write('x')\nraise ImportError('shadow module imported')\n" % str(marker))


@pytest.fixture
def hubcopy(tmp_path):
    root = tmp_path / "hub"
    shutil.copytree(HUB / "tools" / "mvp_ingress", root / "tools" / "mvp_ingress", ignore=shutil.ignore_patterns("__pycache__"))
    return root


def _env(root):
    env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE="1")
    return env


def _launch(root, *args, form="new"):
    head = ([sys.executable, "-I", str(root / "tools/mvp_ingress/launch.py")] if form == "new"
            else [sys.executable, "-m", "tools.mvp_ingress.server"])
    return subprocess.run(head + list(args), cwd=str(root), env=_env(root), capture_output=True, text=True, timeout=60)


def test_old_launcher_form_imports_a_hub_root_json_shadow(hubcopy, tmp_path):
    marker = tmp_path / MARK
    _marker_module(hubcopy / "json.py", marker)
    p = _launch(hubcopy, "--help", form="old")
    assert marker.exists() and p.returncode != 0 and "shadow module imported" in p.stderr  # the former form was vulnerable


@needs_py311
def test_launcher_does_not_import_a_hub_root_or_cwd_stdlib_shadow(hubcopy, tmp_path):
    marker = tmp_path / MARK
    for name in ("json", "argparse", "socket", "struct", "sqlite3"):
        _marker_module(hubcopy / (name + ".py"), marker)
    p = _launch(hubcopy, "--help")
    assert p.returncode == 0 and "--state-dir" in p.stdout, p.stderr[-500:]
    assert not marker.exists()


@needs_py311
def test_launcher_refuses_without_isolated_mode(hubcopy):
    p = subprocess.run([sys.executable, str(hubcopy / "tools/mvp_ingress/launch.py"), "--help"], cwd=str(hubcopy),
                       env=_env(hubcopy), capture_output=True, text=True, timeout=60)
    assert p.returncode == 2 and "isolated mode" in p.stderr


@needs_py311
@pytest.mark.parametrize("shadow", ["package", "namespace", "extension", "sibling-dotted"])
def test_launcher_refuses_a_shadow_of_an_ingress_module_before_running_it(hubcopy, tmp_path, shadow):
    marker = tmp_path / MARK
    if shadow == "package":
        _marker_module(hubcopy / "tools/mvp_ingress/proposal/__init__.py", marker)
    elif shadow == "namespace":
        (hubcopy / "tools/mvp_ingress/proposal").mkdir()
    elif shadow == "sibling-dotted":
        (hubcopy / "tools/mvp_ingress/proposal.txt").write_text("x")
    else:
        (hubcopy / "tools/mvp_ingress" / ("proposal" + importlib.machinery.EXTENSION_SUFFIXES[0])).write_bytes(b"not an extension")
    p = _launch(hubcopy, "--help")
    assert p.returncode == 2 and "proposal" in p.stderr and "refused" in p.stderr, p.stderr[-500:]
    assert not marker.exists() and "READY" not in p.stdout  # refused before any ingress module was executed


@needs_py311
def test_component_roots_are_appended_after_the_standard_library(tmp_path):
    """synthetic_host must not let a file in an operator-supplied component root shadow a stdlib module."""
    cp, rt = tmp_path / "cp", tmp_path / "rt"
    for d in (cp, rt, cp / "src"):
        d.mkdir(parents=True, exist_ok=True)
    marker = tmp_path / MARK
    for d in (cp, rt):
        _marker_module(d / "colorsys.py", marker)
    code = textwrap.dedent("""
        import sys
        sys.path.append(%r)
        from tools.mvp_ingress.synthetic_host import SyntheticHost
        sys.path.remove(%r)
        try:
            SyntheticHost(control_plane_root=%r, runtime_root=%r, state_dir=%r)
        except (ImportError, SystemExit):
            pass
        import colorsys
        print(colorsys.__file__)
        print(sys.path.index(%r) > max(i for i, p in enumerate(sys.path) if p.endswith('lib/python' + sys.version[:4])))
    """ % (str(HUB), str(HUB), str(cp), str(rt), str(tmp_path / "st"), str(cp)))
    p = subprocess.run([sys.executable, "-I", "-B", "-c", code], cwd=str(tmp_path), capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr[-500:]
    assert not marker.exists() and str(cp) not in p.stdout.splitlines()[0]
    assert p.stdout.splitlines()[1] == "True"


# --------------------------------------------------------------------------------------------------------- integration
def _start(root, base):
    base.mkdir()
    os.chmod(base, 0o755)
    sock = str(base / "ingress.sock")
    proc = subprocess.Popen([sys.executable, "-I", str(root / "tools/mvp_ingress/launch.py"), "--state-dir", str(base / "state"),
                             "--socket", sock, "--control-plane", CP, "--runtime", RT, "--allow-uid", str(os.geteuid())], cwd=str(root), env=_env(root),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.stdout.readline().strip() != "READY":
        proc.kill()
        raise RuntimeError("ingress did not start: " + proc.stderr.read()[-2000:])
    return proc, sock


@needs_components
@needs_py311
def test_real_ingress_ignores_cwd_shadows_and_handles_the_synthetic_refund(hubcopy, tmp_path):
    marker = tmp_path / MARK
    # stdlib shadow, Control Plane / Runtime top-level shadows and a package shadow, all in the hub root = working directory
    for name in ("json.py", "colorsys.py", "engine/__init__.py", "agent_control_plane/__init__.py", "tests/__init__.py",
                 "pydantic/__init__.py", "tests/test_bounded_authorization.py", "tests/test_runtime_authority.py"):
        _marker_module(hubcopy / name, marker)
    proc, sock = _start(hubcopy, tmp_path / "b")
    try:
        out = client_mod.submit(sock, GOOD)
        assert out["outcome"] == "executed", out
    finally:
        proc.terminate()
        proc.wait(15)
    assert not marker.exists(), "a shadow file in the working directory / hub root was imported"


@needs_py311
def test_launcher_writes_no_bytecode_into_the_reviewed_tree(hubcopy):
    """-I ignores PYTHONDONTWRITEBYTECODE; the launcher itself must keep the tree free of __pycache__ (validator refuses it)."""
    env = {k: v for k, v in _env(hubcopy).items() if k != "PYTHONDONTWRITEBYTECODE"}
    p = subprocess.run([sys.executable, "-I", str(hubcopy / "tools/mvp_ingress/launch.py"), "--help"], cwd=str(hubcopy), env=env,
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr[-500:]
    assert not list(hubcopy.rglob("__pycache__"))


def _crafted_pyc(root, marker):
    """A timestamp .pyc for proposal.py whose header matches the real source (mtime, size), executing the marker write."""
    import marshal
    import struct as st
    src = root / "tools/mvp_ingress/proposal.py"
    code = compile("open(%r, 'a').write('x')\n" % str(marker), "proposal.py", "exec")
    pyc = root / "tools/mvp_ingress/__pycache__" / ("proposal.%s.pyc" % sys.implementation.cache_tag)
    pyc.parent.mkdir(exist_ok=True)
    stt = src.stat()
    pyc.write_bytes(importlib.util.MAGIC_NUMBER + st.pack("<III", 0, int(stt.st_mtime) & 0xFFFFFFFF, stt.st_size & 0xFFFFFFFF)
                    + marshal.dumps(code))
    return pyc


@pytest.fixture
def hubcopy_raw(tmp_path):
    root = tmp_path / "hubraw"
    shutil.copytree(HUB / "tools" / "mvp_ingress", root / "tools" / "mvp_ingress", ignore=shutil.ignore_patterns("__pycache__"))
    return root  # same as hubcopy; the crafted pyc is planted by the test itself (no ignore_patterns applied afterwards)


def test_old_form_executes_a_planted_matching_pyc(hubcopy_raw, tmp_path):
    marker = tmp_path / MARK
    _crafted_pyc(hubcopy_raw, marker)
    _launch(hubcopy_raw, "--help", form="old")
    assert marker.exists()


@needs_py311
def test_launcher_refuses_a_planted_pyc_and_never_executes_it(hubcopy_raw, tmp_path):
    marker = tmp_path / MARK
    _crafted_pyc(hubcopy_raw, marker)
    p = _launch(hubcopy_raw, "--help")
    assert p.returncode == 2 and "bytecode" in p.stderr and not marker.exists(), p.stderr[-400:]


@needs_py311
def test_pycache_prefix_alone_ignores_a_planted_matching_pyc(hubcopy_raw, tmp_path):
    """Defence in depth: even without the launcher's refusal, a fresh pycache_prefix means the planted .pyc is not read."""
    marker = tmp_path / MARK
    _crafted_pyc(hubcopy_raw, marker)
    code = ("import sys,tempfile; sys.pycache_prefix=tempfile.mkdtemp(); sys.path.append(%r); import tools.mvp_ingress.proposal as p; "
            "print(hasattr(p,'SCHEMA'))" % str(hubcopy_raw))
    p = subprocess.run([sys.executable, "-I", "-B", "-c", code], cwd=str(tmp_path), capture_output=True, text=True, timeout=60)
    assert p.returncode == 0 and p.stdout.strip() == "True" and not marker.exists(), p.stderr[-300:]


@needs_components
@needs_py311
@pytest.mark.parametrize("stray", ["agent_control_plane", "engine", "tests"])
def test_stray_installed_component_module_is_refused(hubcopy, tmp_path, stray):
    """A same-named package earlier on sys.path than the appended component roots (as a site-packages copy would be)."""
    marker = tmp_path / MARK
    site = tmp_path / "fake-site"
    _marker_module(site / stray / "__init__.py", marker)
    base = tmp_path / "b"
    base.mkdir()
    os.chmod(base, 0o755)
    code = ("import sys,runpy; sys.path.append(%r); sys.argv=[%r]+%r; runpy.run_path(%r, run_name='__main__')"
            % (str(site), str(hubcopy / "tools/mvp_ingress/launch.py"),
               ["--state-dir", str(base / "state"), "--socket", str(base / "s.sock"), "--control-plane", CP, "--runtime", RT,
                "--allow-uid", str(os.geteuid())], str(hubcopy / "tools/mvp_ingress/launch.py")))
    p = subprocess.run([sys.executable, "-I", "-c", code], cwd=str(hubcopy), capture_output=True, text=True, timeout=120)
    assert p.returncode == 2 and "component roots" in p.stderr, p.stderr[-500:]
    assert not marker.exists() and not (base / "s.sock").exists()


def test_server_module_is_not_a_supported_entry_point(hubcopy):
    p = _launch(hubcopy, "--help", form="old")
    assert p.returncode == 2 and "launch.py" in p.stderr
