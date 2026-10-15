#!/usr/bin/env python3
"""Reconstruct only the frozen source-review ZIP; never authorizes publication."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    record = json.loads((here / 'verification.json').read_text())
    raw = (here / 'manifest.json').read_bytes()
    if sha(raw) != record['manifest_sha256']:
        raise ValueError('Manifest commitment changed')
    manifest = json.loads(raw)
    expected = {r['path']: r['sha256'] for r in manifest['files']}
    verifier = args.repository.resolve() / 'tools/verify_publication_inventory.py'
    if sha(verifier.read_bytes()) != expected['tools/verify_publication_inventory.py']:
        raise ValueError('Use the frozen-source inventory verifier')
    if args.output.exists():
        raise ValueError('Output already exists; never overwrite retained evidence')
    with tempfile.TemporaryDirectory(prefix='cognous-frozen-review-') as temporary:
        package = Path(temporary) / 'package'
        subprocess.run([sys.executable, str(verifier), '--repository', str(args.repository.resolve()),
                        '--manifest', str(here / 'manifest.json'), '--package', str(package), '--build'], check=True)
        with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_STORED) as archive:
            for relative in sorted(expected):
                info = zipfile.ZipInfo(relative, (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_STORED
                archive.writestr(info, (package / relative).read_bytes())
    with zipfile.ZipFile(args.output) as archive:
        if archive.namelist() != sorted(expected):
            raise ValueError('Archive membership changed')
        for relative in archive.namelist():
            if sha(archive.read(relative)) != expected[relative]:
                raise ValueError('Archive member changed: ' + relative)
    if sha(args.output.read_bytes()) != record['package']['sha256']:
        raise ValueError('Archive commitment changed')
    print(json.dumps({'source_sha': manifest['source_commit'], 'files': len(expected),
                      'archive_sha256': sha(args.output.read_bytes()),
                      'reference_release_authorized': False, 'production_deployment_authorized': False}))


if __name__ == '__main__':
    main()
