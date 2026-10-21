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
        if (ROOT/name).is_dir():
            shutil.copytree(ROOT/name,tmp_path/name)
        else:
            shutil.copy(ROOT/name,tmp_path/name)
    return tmp_path


def test_current_selected_links_and_navigation():
    assert module.verify()['selected_revision_links_checked']>=1


def test_stale_selected_link_fails(tmp_path):
    root=copy_root(tmp_path);p=root/'docs/architecture.md'
    p.write_text(p.read_text().replace('7f7569b02666b99669a9fca61117ca1f4bce5f0d','c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df'))
    with pytest.raises(ValueError,match='differs from lock'):module.verify(root)


def test_private_primary_trust_link_fails(tmp_path):
    root=copy_root(tmp_path);p=root/'docs/evidence-index.md'
    p.write_text(p.read_text().replace('(operational-trust-status.md)','(https://github.com/cogno-us/cognous-stack-orchestrator/issues/30)'))
    with pytest.raises(ValueError,match='public operational trust'):module.verify(root)


def test_historical_revisions_remain_valid(tmp_path):
    root=copy_root(tmp_path)
    (root/'docs/verification/explicit-history.md').write_text('Historical reference https://github.com/cogno-us/cognous-governed-exchange/tree/c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df\n')
    assert module.verify(root)['authorizing'] is False


def test_navigation_outside_root_fails(tmp_path):
    root=copy_root(tmp_path/'repo');outside=tmp_path/'outside.md';outside.write_text('outside')
    p=root/'docs/evidence-index.md';p.write_text(p.read_text()+'\n[escape](../../outside.md)\n')
    with pytest.raises(ValueError,match='Broken local navigation'):module.verify(root)


def test_uppercase_stale_selected_link_fails(tmp_path):
    root=copy_root(tmp_path);p=root/'docs/architecture.md'
    p.write_text(p.read_text().replace('7f7569b02666b99669a9fca61117ca1f4bce5f0d','C52F9F0B998A77C0DBAC7E8C56E1BE1B5117E1DF'))
    with pytest.raises(ValueError,match='differs from lock'):module.verify(root)


def test_abbreviated_stale_selected_link_fails(tmp_path):
    root=copy_root(tmp_path);p=root/'docs/architecture.md'
    p.write_text(p.read_text().replace('/blob/7f7569b02666b99669a9fca61117ca1f4bce5f0d','/blob/c52f9f0').replace('/tree/7f7569b02666b99669a9fca61117ca1f4bce5f0d','/tree/c52f9f0'))
    with pytest.raises(ValueError,match='differs from lock'):module.verify(root)


def test_stale_link_to_any_locked_component_on_a_current_surface_fails(tmp_path):
    root=copy_root(tmp_path);p=root/'docs/evidence-index.md'
    p.write_text(p.read_text()+'\nSee https://github.com/cogno-us/cognous-control-plane/tree/'+'0'*40+'\n')
    with pytest.raises(ValueError,match='differs from lock'):module.verify(root)


def test_matching_link_to_another_locked_component_is_accepted(tmp_path):
    root=copy_root(tmp_path);p=root/'docs/evidence-index.md'
    p.write_text(p.read_text()+'\nSee https://github.com/cogno-us/cognous-control-plane/tree/0a41faa972699f7ec3063967a14cd9bdd3e67d27\n')
    assert module.verify(root)['authorizing'] is False
