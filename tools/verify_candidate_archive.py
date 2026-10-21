#!/usr/bin/env python3
"""Verify an unpublished hub source tar against a trusted exact Git revision.

No component checkout, release creation, credential issuance or production effect.
Only --smoke executes the already verified source in a fresh temporary directory.
"""
import argparse
import bz2
import gzip
import lzma
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile

try:
    from tools.bounded_input import loads as bounded_loads
except ModuleNotFoundError:
    from bounded_input import loads as bounded_loads

ROOT = Path(__file__).resolve().parents[1]
SELECTION = 'profiles/bounded-v1-reference-release-selection.json'
REQUIRED = {'README.md', 'LICENSE', 'NOTICE', 'component-lock.json', SELECTION,
            'docs/releases/selected-notices.json', 'contracts/qualification-surfaces-v1.json',
            'tools/check_contract_surfaces.py'}


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def safe_path(name):
    p = PurePosixPath(name)
    if not name or '\\' in name or p.is_absolute() or any(x in ('', '.', '..') for x in name.split('/')):
        raise ValueError('noncanonical archive path')
    return p


def source_tree(repo, revision):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('exact lowercase 40-character commit required')
    if git(repo, 'cat-file', '-t', revision).strip() != b'commit':
        raise ValueError('source revision is not a commit')
    result = {}
    for record in git(repo, 'ls-tree', '-r', '-z', revision).split(b'\0'):
        if not record:
            continue
        metadata, raw_path = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        path = raw_path.decode('utf-8')
        safe_path(path)
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('only regular tracked source files are supported')
        result[path] = (mode, oid, int(git(repo, 'cat-file', '-s', oid)))
    if not REQUIRED <= result.keys():
        raise ValueError('source missing required candidate verification files')
    if len(result) > 10000 or sum(v[2] for v in result.values()) > 256 * 1024 * 1024 or any(v[2] > 16 * 1024 * 1024 for v in result.values()):
        raise ValueError('source archive inventory exceeds budget')
    return result


def run_smoke(directory, qualification_root=None):
    env = dict(os.environ, PYTHONPATH=directory, PYTHONNOUSERSITE='1')
    runner = Path(directory) / 'tools/candidate_smoke.py'
    command = [sys.executable, str(runner)]
    if qualification_root is not None:
        runner = Path(qualification_root) / 'suites/cognous-open-control-stack/tools/candidate_smoke.py'
        # -I: ignore PYTHON* variables, user site and the harness script directory.
        command = [sys.executable, '-I', str(runner), '--source-root', str(directory)]
    subprocess.run(command, cwd=directory,
                   env=env, check=True, timeout=120)


@contextmanager
def bounded_tar_stream(stream):
    """Cap total expansion before tarfile processes extension headers or members."""
    magic = stream.read(6)
    stream.seek(0)
    opener = gzip.GzipFile if magic.startswith(b'\x1f\x8b') else bz2.BZ2File if magic.startswith(b'BZh') else lzma.LZMAFile if magic.startswith(b'\xfd7zXZ\x00') else None
    decoded = opener(stream, 'rb') if opener else stream
    try:
        with tempfile.TemporaryFile() as spool:
            total = 0
            while True:
                block = decoded.read(min(1048576, 256 * 1024 * 1024 - total + 1))
                if not block:
                    break
                total += len(block)
                if total > 256 * 1024 * 1024:
                    raise ValueError('archive expansion budget exceeded')
                spool.write(block)
            spool.seek(0)
            yield spool
    finally:
        if decoded is not stream:
            decoded.close()


def verify(archive, *, sha256, revision, repo=ROOT, smoke=False, qualification_root=None, qualification_revision=None):
    if not re.fullmatch(r'[0-9a-f]{64}', sha256):
        raise ValueError('trusted archive SHA-256 required')
    if qualification_root is not None:
        qualification_root = Path(qualification_root).resolve()
        if not qualification_revision or not re.fullmatch(r'[0-9a-f]{40}', qualification_revision):
            raise ValueError('exact qualification revision required for external smoke')
        if git(qualification_root, 'rev-parse', 'HEAD').decode().strip() != qualification_revision:
            raise ValueError('qualification checkout revision mismatch')
        if git(qualification_root, 'diff', 'HEAD', '--'):
            raise ValueError('qualification checkout has modified tracked files')
        if git(qualification_root, 'status', '--porcelain', '--untracked-files=all', '--ignored'):
            raise ValueError('qualification checkout has untracked, ignored or modified files')
        if any(line[:2] != b'H ' for line in git(qualification_root, 'ls-files', '-v', '-z').split(b'\0') if line):
            raise ValueError('qualification checkout has skip-worktree or assume-unchanged entries')
    elif qualification_revision is not None:
        raise ValueError('qualification root required')
    expected = source_tree(repo, revision)
    seen = set()
    directories = {str(p) for name in expected for p in PurePosixPath(name).parents if str(p) != '.'}
    with open(archive, 'rb') as stream, tempfile.TemporaryDirectory(prefix='cognous-candidate-') as temp:
        if os.fstat(stream.fileno()).st_size > 256 * 1024 * 1024:
            raise ValueError('archive byte budget exceeded')
        if hashlib.file_digest(stream, 'sha256').hexdigest() != sha256:
            raise ValueError('archive checksum mismatch')
        stream.seek(0)
        with bounded_tar_stream(stream) as decoded, tarfile.open(fileobj=decoded, mode='r:') as bundle:
            for index, member in enumerate(bundle):
                if index >= 10000 or sum(len(k) for k in member.pax_headers) > 65536:
                    raise ValueError('archive metadata budget exceeded')
                # Git archive emits explicit directories; never extract links or devices.
                name = member.name.rstrip('/') if member.isdir() else member.name
                safe_path(name)
                if name in seen:
                    raise ValueError('duplicate archive member')
                seen.add(name)
                if member.isdir():
                    if name not in directories:
                        raise ValueError('unexpected archive directory')
                    continue
                if not member.isfile() or name not in expected:
                    raise ValueError('unexpected or unsafe archive member')
                mode, oid, size = expected[name]
                if member.size != size or member.mode & 0o7000 or bool(member.mode & 0o111) != (mode == '100755'):
                    raise ValueError('archive size or executable mode mismatch')
                source = bundle.extractfile(member)
                content = source.read(size + 1)
                actual = hashlib.sha1(b'blob ' + str(size).encode() + b'\0' + content).hexdigest()
                if len(content) != size or actual != oid:
                    raise ValueError('archive file differs from source revision')
                if name == SELECTION:
                    try:
                        selection = bounded_loads(content)
                    except ValueError as exc:
                        raise ValueError('candidate selection is not bounded strict JSON: ' + str(exc)) from exc
                    if type(selection) is not dict:
                        raise ValueError('candidate selection must be a JSON object')
                    if any(selection.get(k) is not False for k in ('reference_release_authorized', 'production_deployment_authorized')):
                        raise ValueError('candidate must preserve false authorization fields')
                if smoke:
                    target = Path(temp) / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
                    target.chmod(0o755 if mode == '100755' else 0o644)
        if not expected.keys() <= seen:
            raise ValueError('archive missing tracked source files')
        if smoke:
            run_smoke(temp, qualification_root)
    return {'format': 'cognous.candidate-archive-verification/1', 'source_revision': revision,
            'qualification_revision': qualification_revision,
            'archive_sha256': sha256, 'verified_files': len(expected),
            'artifact_integrity': 'PASS', 'synthetic_smoke': 'PASS' if smoke else 'NOT_RUN',
            'scope': 'hub source only; no component bundle or full selected-chain reproduction',
            'reference_release_authorized': False, 'production_deployment_authorized': False,
            'operational_trust': 'HOLD / NOT ESTABLISHED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--sha256', required=True, help='expected digest obtained independently from the archive')
    parser.add_argument('--revision', required=True, help='trusted exact source commit; not an archive-provided value')
    parser.add_argument('--smoke', action='store_true', help='execute verified synthetic tests in clean extraction')
    parser.add_argument('--qualification-root', type=Path, help='clean checkout at --qualification-revision containing relocated smoke tests')
    parser.add_argument('--qualification-revision', help='trusted exact suite commit; separate from archive identity')
    args = parser.parse_args()
    try:
        report = verify(args.archive, sha256=args.sha256, revision=args.revision, smoke=args.smoke, qualification_root=args.qualification_root, qualification_revision=args.qualification_revision)
    except (OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as exc:
        print(f'candidate verification failed: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
