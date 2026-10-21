"""Scan 5 F-T3-2 (cheap forms): abbreviated revisions of 4-6 hex characters and ?ref=<revision>."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selected_docs_scan5', ROOT / 'tools/verify_selected_documentation.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CP = 'cogno-us/cognous-control-plane'
SHORT = 'c52f9f'


@pytest.mark.parametrize('link,expected', [
    (f'https://github.com/{CP}/tree/c52f', 'c52f'),
    (f'https://github.com/{CP}/tree/c52f9', 'c52f9'),
    (f'https://github.com/{CP}/blob/{SHORT}/README.md', SHORT),
    (f'https://github.com/{CP}/commit/{SHORT}', SHORT),
    (f'https://github.com/{CP}/blob/main/README.md?ref={SHORT}', SHORT),
    (f'https://github.com/{CP}/blob/main/README.md?plain=1&ref={SHORT}', SHORT),
    (f'https://github.com/{CP}/tree/main?ref=c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df', 'c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df'),
])
def test_short_and_query_revisions_are_found(link, expected):
    assert module.revision_links(link) == [(CP, expected)]


@pytest.mark.parametrize('link', [
    f'https://github.com/{CP}/tree/2026',
    f'https://github.com/{CP}/tree/face',
    f'https://github.com/{CP}/tree/main',
    f'https://github.com/{CP}/blob/main/README.md?ref=main',
    f'https://github.com/{CP}/pull/1234',
    f'https://github.com/{CP}/issues/123456',
])
def test_years_words_branches_and_numbers_are_not_revisions(link):
    assert module.revision_links(link) == []


def test_stale_short_revision_is_refused_against_the_lock(tmp_path):
    lock = {'components': {'cp': {'repository': CP, 'sha': 'e77fe0ee8714617899592528e660a80fbb2e864a'}}}
    selected = lock['components']['cp']['sha']
    assert module._same_revision('e77fe0', selected)
    assert not module._same_revision(SHORT, selected)
