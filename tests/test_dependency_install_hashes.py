"""Every CI and scanner-image pip install must be bound to the hashed lock."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = sorted((ROOT / '.github/workflows').glob('*.yml')) + [ROOT / '.oss-scanner/Dockerfile']
INSTALL = re.compile(r'pip\s+install\b[^\n]*')


def installs():
    for path in SOURCES:
        for match in INSTALL.finditer(path.read_text()):
            yield path.relative_to(ROOT).as_posix(), match.group(0)


def test_sources_contain_installs():
    assert any(path == '.oss-scanner/Dockerfile' for path, _ in installs())


def test_pip_installs_require_hashes():
    unbound = [(p, line) for p, line in installs() if '--require-hashes' not in line]
    assert not unbound, unbound


def test_scanner_image_excludes_git_metadata():
    entries = (ROOT / '.dockerignore').read_text().split()
    assert '.git' in entries
