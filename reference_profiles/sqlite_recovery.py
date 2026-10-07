"""Verified per-database snapshots and staging restore; never activates a deployment."""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile


def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def copy_database(source, destination):
    # Online backup reads committed SQLite state, including WAL. Publication of
    # the staged file is exclusive and does not overwrite an existing store.
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(destination)
    with tempfile.TemporaryDirectory(prefix='cognous-restore-', dir=destination.parent) as tmp:
        candidate = Path(tmp) / 'snapshot.sqlite3'
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as src:
            with closing(sqlite3.connect(candidate)) as dst:
                src.backup(dst)
                if dst.execute('PRAGMA quick_check').fetchall() != [('ok',)]:
                    raise ValueError('SQLite consistency check failed')
        os.chmod(candidate, 0o600)
        os.link(candidate, destination)  # fails if a concurrent creator won


def snapshot(source, package):
    package = Path(package).resolve()
    package.mkdir(parents=True, exist_ok=False, mode=0o700)
    target = package / 'snapshot.sqlite3'
    copy_database(source, target)
    manifest = {'schema_version': 'sqlite-staging-snapshot/1', 'database_sha256': file_digest(target),
                'sqlite_version': sqlite3.sqlite_version, 'scope': 'one committed logical database snapshot',
                'activation_authorized': False, 'freshness_verified': False, 'cross_database_atomic': False}
    (package / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def restore(package, destination):
    package = Path(package).resolve()
    value = json.loads((package / 'manifest.json').read_text())
    if (value.get('schema_version') != 'sqlite-staging-snapshot/1'
            or value.get('activation_authorized') is not False
            or value.get('freshness_verified') is not False
            or value.get('cross_database_atomic') is not False):
        raise ValueError('unsupported snapshot contract')
    source = package / 'snapshot.sqlite3'
    if source.is_symlink() or file_digest(source) != value['database_sha256']:
        raise ValueError('snapshot integrity mismatch')
    copy_database(source, destination)
    return {'restored_to_staging': True, 'activation_authorized': False, 'freshness_verified': False,
            'source_database_sha256': value['database_sha256']}
