"""Scan 6 T1-5: encoded or decorated stale-revision links are judged like plain ones."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selected_docs_scan6', ROOT / 'tools/verify_selected_documentation.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CP = 'cogno-us/cognous-control-plane'
SHA = 'c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df'


@pytest.mark.parametrize('link', [
    f'https://github.com/{CP}/tree/{SHA}',
    f'https://github.com/{CP}/tree/{SHA[:12]}',
    f'https://github.com:443/{CP}/tree/{SHA}',
    f'https://github.com./{CP}/tree/{SHA}',
    f'https://github.com.:443/{CP}/tree/{SHA}',
    f'https://www.github.com:443/{CP}/blob/{SHA}/README.md',
    f'https://github.com/{CP}/tree/%63%35%32f9f0b998a',
    f'https://github.com/%63ogno-us/cognous-control-plane/tree/{SHA}',
    f'https://github.com/cogno-us%2Fcognous-control-plane/tree/{SHA}',
    f'https://github.com/{CP}/tree/{SHA[:12]}'.replace('/', '&#x2F;').replace('https:&#x2F;&#x2F;', 'https://'),
    f'https://github.com/{CP}/blob/main/README.md?plain=1&amp;ref={SHA}',
    f'https://github.com/{CP}/blob/main/README.md?plain=1&#38;ref={SHA}',
    f'https://github.com/{CP}/tree/&#99;52f9f0b',
    f'https://github.com/{CP}/tree/%2563%2535%2532f9f0b',
])
def test_decorated_links_are_found(link):
    found = module.revision_links(link)
    assert found and all(name == CP for name, _ in found)


def test_encoded_revision_text_is_the_decoded_revision():
    assert module.revision_links(f'https://github.com:443/{CP}/tree/%63%35%32f9f0b998a') == [(CP, 'c52f9f0b998a')]
    assert module.revision_links(f'https://github.com/{CP}/blob/main/x.md?a=1&amp;ref={SHA[:9]}') == [(CP, SHA[:9])]


@pytest.mark.parametrize('length', [41, 64])
def test_revisions_longer_than_forty_hex_are_found_and_never_match(length):
    revision = (SHA + SHA)[:length]
    assert module.revision_links(f'https://github.com/{CP}/tree/{revision}') == [(CP, revision)]
    assert not module._same_revision(revision, SHA)


def test_ordinary_links_are_unchanged():
    assert module.revision_links(f'https://github.com/{CP}/tree/{SHA}') == [(CP, SHA)]
    assert module.revision_links(f'https://github.com/{CP}/tree/main') == []
    assert module.revision_links('https://example.com:443/a/b/tree/' + SHA) == []
