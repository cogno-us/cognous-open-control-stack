"""SEC06/07: current navigation and deliberate provenance drift."""
import importlib.util
from pathlib import Path
import shutil
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('selected_docs',ROOT/'tools/verify_selected_documentation.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def copy_root(tmp_path):
    shutil.copytree(ROOT/'docs',tmp_path/'docs')
    shutil.copy(ROOT/'component-lock.json',tmp_path)
    for name in ('SECURITY.md','README.md','CONTRIBUTING.md','profiles','collateral','examples','contracts'):
        (tmp_path/name).symlink_to(ROOT/name,target_is_directory=(ROOT/name).is_dir())
    return tmp_path


def test_current_selected_links_and_navigation():
    assert module.verify()['selected_revision_links_checked']>=1


def test_stale_selected_link_fails(tmp_path):
    root=copy_root(tmp_path);p=root/'docs/architecture.md'
    p.write_text(p.read_text().replace('a1cbc7b28f702283b0e4f3192bb43e4a9e618ebf','c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df'))
    with pytest.raises(ValueError,match='differs from lock'):module.verify(root)


def test_private_primary_trust_link_fails(tmp_path):
    root=copy_root(tmp_path);p=root/'docs/evidence-index.md'
    p.write_text(p.read_text().replace('(operational-trust-status.md)','(https://github.com/cogno-us/cognous-stack-orchestrator/issues/30)'))
    with pytest.raises(ValueError,match='public operational trust'):module.verify(root)


def test_historical_revisions_remain_valid(tmp_path):
    root=copy_root(tmp_path)
    (root/'docs/verification/explicit-history.md').write_text('Historical reference https://github.com/cogno-us/cognous-governed-exchange/tree/c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df\n')
    assert module.verify(root)['authorizing'] is False
