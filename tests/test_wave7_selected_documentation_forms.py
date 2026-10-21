"""Wave 7 T1-C: ported, fullwidth, backslash, doubled-slash, over-encoded and api forms of stale-revision links."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selected_docs_wave7', ROOT / 'tools/verify_selected_documentation.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CP = 'cogno-us/cognous-control-plane'
SHA = 'c52f9f0b998a77c0dbac7e8c56e1be1b5117e1df'


def deep(text, rounds):
    for _ in range(rounds):
        text = text.replace('%', '%25')
    return text


@pytest.mark.parametrize('link', [
    f'https://github.com:/{CP}/tree/{SHA}',
    f'https://github.com.:/{CP}/tree/{SHA}',
    'https:\\\\github.com\\' + CP.replace('/', '\\') + f'\\tree\\{SHA}',
    f'https://github。com/{CP}/tree/{SHA}',
    f'https://github｡com/{CP}/tree/{SHA}',
    f'https://ｇithub.com/{CP}/tree/{SHA}',
    f'https://github.com//{CP}/tree/{SHA}',
    f'https://github.com/{CP}/tree//{SHA}',
    f'https://github.com/cogno-us//cognous-control-plane/tree/{SHA}',
    f'https://github.com////{CP}/tree/{SHA}',
    f'https://github.com../{CP}/tree/{SHA}',
    f'https://github.com/{CP}/tree/%20{SHA}',
    f'https://github.com/{CP}/tree/ {SHA}',
    f'https://github.com/{CP}/tree/%0A{SHA}',
    f'https://github.com/{CP}/tree/{deep("%63", 12)}52f9f0b',
    f'https://api.github.com/repos/{CP}/git/trees/{SHA}',
    f'https://api.github.com/repos/{CP}/statuses/{SHA}',
    f'https://github.com/{CP}/find/{SHA}',
    f'https://github.com/{CP}/pull/7/files/{SHA}',
    f'https://api.github.com/repos/{CP}/pull/7/files/{SHA}',
    f'https://github.com/{CP}/trees/{SHA}',
    f'https://github.com/{CP}/statuses/{SHA}',
    f'https://github.com/{CP}/files/{SHA}',
])
def test_decorated_links_name_the_revision(link):
    found = module.revision_links(link)
    assert found, link
    assert all(name == CP for name, _ in found), found
    assert any(SHA.startswith(sha) for _, sha in found), found


def test_over_encoded_link_is_refused_not_passed():
    link = 'https://github.com/' + CP + '/tree/' + deep('%63', module.MAX_DECODE_ROUNDS + 8) + '52f9f0b'
    assert module.link_problems(link)
    assert module.revision_links(link)[0][0] == module.UNDECODABLE


def test_moderate_encoding_is_not_refused():
    assert module.link_problems(f'https://github.com/{CP}/tree/{deep("%63", 20)}52f9f0b') == []
    assert module.link_problems(f'https://github.com/{CP}/tree/{SHA}') == []


def test_verify_refuses_over_encoded_page(tmp_path):
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'component-lock.json').write_text((ROOT / 'component-lock.json').read_text())
    for name in ('docs/evidence-index.md', 'docs/architecture.md', 'docs/operational-trust-status.md'):
        (tmp_path / name).write_text((ROOT / name).read_text())
    bad = (tmp_path / 'docs/operational-trust-status.md')
    bad.write_text(bad.read_text() + '\n[x](https://github.com/' + CP + '/tree/' + deep('%63', 60) + 'x)\n')
    with pytest.raises(ValueError, match='cannot be judged'):
        module.verify(tmp_path)


def test_plain_and_unrelated_links_are_unchanged():
    assert module.revision_links(f'https://github.com/{CP}/tree/{SHA}') == [(CP, SHA)]
    assert module.revision_links(f'https://github.com/{CP}/tree/main') == []
    assert module.revision_links(f'https://github.com/{CP}/pull/1234567') == []
    assert module.revision_links(f'https://github.com/{CP}/files/2026') == []
