"""D-H3: every revision-specific link form and old repository name is checked against the lock."""
import importlib.util
import json
import re
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selected_docs_forms', ROOT / 'tools/verify_selected_documentation.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

STALE = 'c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df'
CP = 'cogno-us/cognous-control-plane'
FORMS = {
    'old name tree': f'https://github.com/cogno-us/cognous-agent-control-plane/tree/{STALE}',
    'http': f'http://github.com/{CP}/blob/{STALE}/README.md',
    'www': f'https://www.github.com/{CP}/commit/{STALE}',
    'archive zip': f'https://github.com/{CP}/archive/{STALE}.zip',
    'raw host': f'https://raw.githubusercontent.com/{CP}/{STALE}/README.md',
    'raw host old name': f'https://raw.githubusercontent.com/cogno-us/cognous-agent-control-plane/{STALE}/README.md',
    'pull commits': f'https://github.com/{CP}/pull/12/commits/{STALE}',
    'compare left': f'https://github.com/{CP}/compare/{STALE}...main',
    'compare right': f'https://github.com/{CP}/compare/main...{STALE}',
    'dot git': f'https://github.com/{CP}.git/tree/{STALE}',
    'codeload': f'https://codeload.github.com/{CP}/zip/{STALE}',
}


def copy_root(tmp_path):
    shutil.copytree(ROOT / 'docs', tmp_path / 'docs')
    shutil.copy(ROOT / 'component-lock.json', tmp_path)
    for name in ('SECURITY.md', 'README.md', 'CONTRIBUTING.md', 'profiles', 'collateral', 'examples', 'contracts'):
        if (ROOT / name).is_dir():
            shutil.copytree(ROOT / name, tmp_path / name)
        else:
            shutil.copy(ROOT / name, tmp_path / name)
    return tmp_path


@pytest.fixture(scope='module')
def root(tmp_path_factory):
    path = copy_root(tmp_path_factory.mktemp('selected-docs'))
    yield path
    shutil.rmtree(path, ignore_errors=True)


def with_link(root, link):
    page = root / 'docs/operational-trust-status.md'
    original = page.read_text()
    page.write_text(original + '\nSee ' + link + '\n')
    return page, original


@pytest.mark.parametrize('name', sorted(FORMS))
def test_stale_link_form_is_refused(root, name):
    page, original = with_link(root, FORMS[name])
    try:
        with pytest.raises(ValueError, match='differs from lock'):
            module.verify(root)
    finally:
        page.write_text(original)


@pytest.mark.parametrize('name', sorted(FORMS))
def test_current_revision_in_every_form_is_accepted(root, name):
    lock = json.loads((ROOT / 'component-lock.json').read_text())
    current = lock['components']['control_plane']['sha']
    page, original = with_link(root, FORMS[name].replace(STALE, current))
    try:
        assert module.verify(root)['authorizing'] is False
    finally:
        page.write_text(original)


def test_non_revision_numbers_are_not_mistaken_for_revisions():
    assert module.revision_links(f'https://github.com/{CP}/pull/1234567') == []
    assert module.revision_links(f'https://github.com/{CP}/actions/runs/37694032916') == []


def test_old_name_table_matches_the_rename_record():
    doc = (ROOT / 'docs/repository-renames.md').read_text()
    rows = re.findall(r'\| `(cogno-us/[^`]+)` \| \[`(cogno-us/[^`]+)`\]', doc)
    assert rows and dict(rows) == module.OLD_REPOSITORY_NAMES
