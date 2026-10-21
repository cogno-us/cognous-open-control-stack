#!/usr/bin/env python3
"""Fail-closed verifier for a frozen hub-only review package; never authorizes release."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess


try:
    from tools.bounded_input import read_bytes, loads
except ModuleNotFoundError:
    from bounded_input import read_bytes, loads


class InventoryError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise InventoryError('unsafe path')
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ('', '.', '..') for x in value.split('/')):
        raise InventoryError('unsafe path: ' + value)
    return value


def unique_paths(rows):
    result = {}
    folded = set()
    for row in rows:
        p = safe_path(row['path'])
        if p.casefold() in folded:
            raise InventoryError('duplicate path: ' + p)
        folded.add(p.casefold())
        result[p] = row
    return result


def validate_manifest(m):
    if m['schema'] != 'cognous.publication-inventory/1':
        raise InventoryError('unsupported schema')
    if (m['rights_acceptance'] != 'pending_accountable_review'
            or m['reference_release_authorized'] is not False
            or m['production_deployment_authorized'] is not False):
        raise InventoryError('inventory cannot grant acceptance or authorization')
    if not re.fullmatch('[0-9a-f]{40}', m['source_commit']):
        raise InventoryError('source commit must be immutable')
    included = unique_paths(m['files'])
    excluded = unique_paths(m['excluded_files'])
    if not included or set(p.casefold() for p in included) & set(p.casefold() for p in excluded):
        raise InventoryError('empty package or explicitly excluded file included')
    notices = [safe_path(p) for p in m['required_notices']]
    if not notices or len(set(notices)) != len(notices) or not set(notices) <= included.keys():
        raise InventoryError('missing or duplicate required notice')
    for row in excluded.values():
        if (row.get('source_commit') != m['source_commit']
                or not re.fullmatch('[0-9a-f]{64}', row.get('sha256', ''))
                or type(row.get('reason')) is not str or not row['reason'].strip()):
            raise InventoryError('invalid excluded provenance or reason')
    for row in included.values():
        if (row['source_commit'] != m['source_commit']
                or not re.fullmatch('[0-9a-f]{64}', row['sha256'])
                or row['licensing_state'] != 'evidence_verified'
                or not row['inclusion_rationale'] or not row['license_evidence']):
            raise InventoryError('invalid source/digest or unresolved included licensing')
        for evidence in row['license_evidence']:
            if safe_path(evidence) not in notices:
                raise InventoryError('license evidence is not a required notice')
    for row in m['external_components']:
        if (row['redistributed'] is not False or row['rights_accepted'] is not False
                or row['licensing_state'] not in {'notice_evidence_only', 'unresolved'}):
            raise InventoryError('external or unresolved licensing presented as accepted')
    return included, excluded


def load_manifest(path):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise InventoryError('duplicate JSON key')
            obj[key] = value
        return obj
    try:
        m = loads(read_bytes(path))
    except ValueError as exc:
        raise InventoryError(str(exc)) from exc
    validate_manifest(m)
    return m


def source_bytes(repository, commit, path):
    mode = subprocess.check_output(['git', '-C', str(repository), 'ls-tree', commit, '--', path], text=True)
    if not mode.startswith(('100644 blob ', '100755 blob ')) or len(mode.splitlines()) != 1:
        raise InventoryError('source is not a regular tracked file: ' + path)
    size = int(subprocess.check_output(['git', '-C', str(repository), 'cat-file', '-s', commit + ':' + path]))
    if size > 16 * 1024 * 1024:
        raise InventoryError('source file exceeds byte budget')
    return subprocess.check_output(['git', '-C', str(repository), 'show', commit + ':' + path])


def verify_source(m, repository):
    included, excluded = validate_manifest(m)
    if subprocess.check_output(['git', '-C', str(repository), 'cat-file', '-t', m['source_commit']]).strip() != b'commit':
        raise InventoryError('source identity is not a commit')
    tracked = set(subprocess.check_output(['git', '-C', str(repository), 'ls-tree', '-rz', '--name-only', m['source_commit']]).decode().rstrip('\0').split('\0'))
    if tracked != included.keys() | excluded.keys():
        raise InventoryError('source tree inventory is incomplete')
    for row in (*included.values(), *excluded.values()):
        if digest(source_bytes(repository, row['source_commit'], row['path'])) != row['sha256']:
            raise InventoryError('source digest mismatch: ' + row['path'])


def verify_package(m, root):
    included, _ = validate_manifest(m)
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise InventoryError('package root must be a real directory')
    actual = set()
    # A directory is allowed only as an ancestor of a listed file: no empty or unlisted directories.
    listed_dirs = {parent.as_posix() for path in included for parent in PurePosixPath(path).parents}

    def unreadable(exc):
        raise InventoryError('unreadable package directory: ' + str(exc)) from exc

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
        for name in dirs + files:
            p = Path(directory) / name
            if p.is_symlink() or (not p.is_dir() and not p.is_file()):
                raise InventoryError('nonregular package entry')
        for name in dirs:
            relative_dir = safe_path((Path(directory) / name).relative_to(root).as_posix())
            if relative_dir not in listed_dirs:
                raise InventoryError('unlisted package directory: ' + relative_dir)
        for name in files:
            p = Path(directory) / name
            relative = safe_path(p.relative_to(root).as_posix())
            actual.add(relative)
            if relative not in included:
                raise InventoryError('unlisted or excluded package file: ' + relative)
            if digest(read_bytes(p, 16 * 1024 * 1024)) != included[relative]['sha256']:
                raise InventoryError('package digest mismatch: ' + relative)
    if actual != included.keys():
        raise InventoryError('listed file or required notice missing: ' + ', '.join(sorted(included.keys() - actual)))
    return {'technical_inventory': 'complete_for_frozen_scope', 'file_count': len(actual),
            'rights_acceptance': m['rights_acceptance'], 'reference_release_authorized': False,
            'production_deployment_authorized': False}


def build_package(m, repository, output):
    verify_source(m, repository)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for row in m['files']:
        path = output / row['path']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source_bytes(repository, row['source_commit'], row['path']))
    return verify_package(m, output)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True)
    p.add_argument('--package', required=True)
    p.add_argument('--repository', default='.')
    p.add_argument('--build', action='store_true')
    args = p.parse_args()
    try:
        m = load_manifest(args.manifest)
        if args.build:
            result = build_package(m, args.repository, args.package)
        else:
            verify_source(m, args.repository)
            result = verify_package(m, args.package)
        result['manifest_sha256'] = digest(Path(args.manifest).read_bytes())
        print(json.dumps(result, sort_keys=True))
    except (InventoryError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        p.exit(1, 'inventory refused: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
