#!/usr/bin/env python3
"""Validate a local deployment review packet; never authorize deployment."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

VERSION = 'deployment-review-packet/1'
RESPONSIBILITIES = (
    'institutional-authority', 'identity-key-custody', 'host-writer-boundary',
    'profile-selection', 'data-context', 'destination-contract',
    'backup-restoration', 'incident-response', 'useful-outcomes', 'release-acceptance',
)
PROFILES = ('ordinary-bounded', 'atomic-authority-effect', 'refund-intent')
MAX_BYTES = 8 * 1024 * 1024


class PacketError(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise PacketError(code)


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected), 'INVALID_FIELDS')


def label(value):
    require(type(value) is str and 0 < len(value) <= 200 and value == value.strip(),
            'INVALID_LABEL')


def digest(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'INVALID_DIGEST')


def instant(value):
    require(type(value) is str and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value),
            'INVALID_TIME')
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise PacketError('INVALID_TIME') from exc


def read_bounded(path):
    with path.open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, 'FILE_TOO_LARGE')
    return data


def committed_file(root, reference):
    keys(reference, ('path', 'sha256'))
    digest(reference['sha256'])
    name = reference['path']
    require(type(name) is str and name and '\\' not in name and ':' not in name,
            'INVALID_PATH')
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(p not in ('', '.', '..') for p in name.split('/')),
            'INVALID_PATH')
    current = root
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), 'SYMLINK_NOT_ALLOWED')
    require(current.is_file(), 'MISSING_FILE')
    data = read_bounded(current)
    require(bool(data), 'EMPTY_FILE')
    require(hashlib.sha256(data).hexdigest() == reference['sha256'], 'CONTENT_DIGEST_MISMATCH')


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result

    def constant(_):
        raise PacketError('NON_JSON_NUMBER')

    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def validate(packet, root, lock_bytes, expected_revision, evaluated_at):
    """Check declared scope and retained bytes on a trusted, quiescent local host."""
    result = {
        'contract': VERSION, 'review_packet_complete': False, 'authorizing': False,
        'production_ready': False, 'external_truth_verified': False,
        'identity_verified': False, 'independent_review_verified': False,
        'errors': [], 'checked_responsibilities': [],
    }
    try:
        now = instant(evaluated_at)
        require(type(expected_revision) is str and re.fullmatch('[0-9a-f]{40}', expected_revision),
                'INVALID_EXPECTED_REVISION')
        keys(packet, ('contract', 'deployment_id', 'environment_id', 'profile',
                      'source_revision', 'component_lock_sha256', 'configuration', 'responsibilities'))
        require(packet['contract'] == VERSION, 'UNSUPPORTED_CONTRACT')
        for field in ('deployment_id', 'environment_id'):
            label(packet[field])
        require(packet['profile'] in PROFILES, 'UNSUPPORTED_PROFILE')
        require(packet['source_revision'] == expected_revision, 'SOURCE_REVISION_MISMATCH')
        require(packet['component_lock_sha256'] == hashlib.sha256(lock_bytes).hexdigest(),
                'COMPONENT_LOCK_MISMATCH')
        root = Path(root).resolve(strict=True)
        require(root.is_dir(), 'INVALID_PACKET_ROOT')
        committed_file(root, packet['configuration'])
        scope = {key: packet[key] for key in ('deployment_id', 'environment_id', 'profile',
                 'source_revision', 'component_lock_sha256')}
        scope['configuration_sha256'] = packet['configuration']['sha256']
        result.update({'scope': scope, 'evaluated_at': evaluated_at})
        records = packet['responsibilities']
        require(type(records) is list and len(records) == len(RESPONSIBILITIES),
                'RESPONSIBILITY_SET_MISMATCH')
        ids = [r.get('id') if type(r) is dict else None for r in records]
        require(all(type(i) is str for i in ids) and set(ids) == set(RESPONSIBILITIES),
                'RESPONSIBILITY_SET_MISMATCH')
        for record in records:
            try:
                keys(record, ('id', 'owner_ref', 'status', 'evidence'))
                label(record['owner_ref'])
                require(record['status'] == 'provided', 'EVIDENCE_NOT_PROVIDED')
                evidence = record['evidence']
                require(type(evidence) is list and 1 <= len(evidence) <= 20, 'INVALID_EVIDENCE_SET')
                paths = []
                for item in evidence:
                    keys(item, ('file', 'scope', 'observed_at', 'expires_at'))
                    require(item['scope'] == scope, 'EVIDENCE_SCOPE_MISMATCH')
                    observed, expires = instant(item['observed_at']), instant(item['expires_at'])
                    require(observed <= now < expires, 'EVIDENCE_NOT_CURRENT')
                    committed_file(root, item['file'])
                    paths.append(item['file']['path'])
                require(len(set(paths)) == len(paths), 'DUPLICATE_EVIDENCE')
                result['checked_responsibilities'].append(record['id'])
            except (PacketError, OSError) as exc:
                result['errors'].append({'responsibility': record['id'],
                                         'code': str(exc) if isinstance(exc, PacketError) else 'FILE_UNAVAILABLE'})
        result['review_packet_complete'] = not result['errors']
    except (PacketError, OSError) as exc:
        result['errors'].append({'code': str(exc) if isinstance(exc, PacketError) else 'FILE_UNAVAILABLE'})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--lock', type=Path, required=True)
    parser.add_argument('--expected-revision', required=True)
    parser.add_argument('--evaluated-at', required=True, help='Explicit UTC time YYYY-MM-DDTHH:MM:SSZ')
    args = parser.parse_args()
    try:
        raw = read_bounded(args.packet)
        result = validate(strict_json(raw), args.packet.parent, read_bounded(args.lock),
                          args.expected_revision, args.evaluated_at)
        result['packet_sha256'] = hashlib.sha256(raw).hexdigest()
    except (ValueError, OSError, UnicodeError):
        result = {'contract': VERSION, 'review_packet_complete': False, 'authorizing': False,
                  'production_ready': False, 'errors': [{'code': 'INVALID_PACKET_INPUT'}]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['review_packet_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
