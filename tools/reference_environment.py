#!/usr/bin/env python3
"""Observe prerequisites for local reference qualification, not production assurance."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sqlite3
import sys
import tempfile

PROFILES = ('ordinary-bounded', 'atomic-authority-effect', 'refund-intent')


def sqlite_probe(directory):
    """Use disposable storage only; exercise exclusion and rollback on this host."""
    with tempfile.TemporaryDirectory(prefix='cognous-preflight-', dir=directory) as tmp:
        path = Path(tmp) / 'probe.sqlite3'
        first = sqlite3.connect(path, timeout=0, isolation_level=None)
        second = sqlite3.connect(path, timeout=0, isolation_level=None)
        try:
            journal = first.execute('PRAGMA journal_mode=WAL').fetchone()[0]
            first.execute('PRAGMA synchronous=FULL')
            first.execute('CREATE TABLE probe (id INTEGER PRIMARY KEY)')
            first.execute('BEGIN IMMEDIATE')
            first.execute('INSERT INTO probe VALUES (1)')
            excluded = False
            try:
                second.execute('BEGIN IMMEDIATE')
            except sqlite3.OperationalError as exc:
                if getattr(exc, 'sqlite_errorcode', None) != sqlite3.SQLITE_BUSY:
                    raise
                excluded = True
            finally:
                if second.in_transaction:
                    second.rollback()
            first.rollback()
            rolled_back = second.execute('SELECT count(*) FROM probe').fetchone()[0] == 0
            return {'wal': journal == 'wal', 'competing_writer_excluded': excluded,
                    'rollback_preserved': rolled_back}
        finally:
            second.close()
            first.close()


def inspect_environment(profile, directory, lock_path):
    if profile not in PROFILES:
        raise ValueError('unknown reference profile')
    directory = Path(directory).resolve()
    lock_bytes = Path(lock_path).read_bytes()
    lock = json.loads(lock_bytes)
    checks = [{'id': 'linux', 'status': 'observed' if sys.platform == 'linux' else 'unsupported'},
              {'id': 'python', 'status': 'observed' if sys.version_info[:2] in ((3, 11), (3, 12)) else 'unverified'}]
    try:
        probe = sqlite_probe(directory)
        checks += [{'id': key, 'status': 'observed' if value else 'unsupported'} for key, value in probe.items()]
    except (OSError, sqlite3.Error) as exc:
        checks.append({'id': 'sqlite_storage_probe', 'status': 'unverified', 'error': str(exc)})
    return {'schema_version': '1.0.0', 'profile': profile,
            'purpose': 'local-reference-prerequisites',
            'environment': {'os': platform.system(), 'release': platform.release(),
                            'machine': platform.machine(), 'python': platform.python_version(),
                            'sqlite': sqlite3.sqlite_version},
            'component_lock_sha256': hashlib.sha256(lock_bytes).hexdigest(),
            'components': {name: {'repository': spec['repository'],
                                  'revision': spec.get('core_interop_sha') or spec.get('sha') or spec.get('accepted_sha')}
                           for name, spec in lock['components'].items()},
            'checks': checks,
            'reference_prerequisites_observed': all(c['status'] == 'observed' for c in checks),
            'deployment_qualified': False, 'authorizing': False,
            'unverified': ['filesystem crash/power-loss durability', 'network-filesystem semantics',
                           'trusted authority writers and host administrators', 'identity and key custody',
                           'credential scope and rotation', 'backup and restore',
                           'operator ownership and incident response', 'external destinations'],
            'assumptions': ['cooperating same-host processes', 'local filesystem',
                            'separate databases for mutually exclusive profiles']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profile', choices=PROFILES, required=True)
    ap.add_argument('--storage-dir', type=Path, required=True)
    ap.add_argument('--lock', type=Path, default=Path(__file__).resolve().parents[1] / 'component-lock.json')
    args = ap.parse_args()
    result = inspect_environment(args.profile, args.storage_dir, args.lock)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['reference_prerequisites_observed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
