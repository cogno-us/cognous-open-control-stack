#!/usr/bin/env python3
"""Derive optional-run record consistency from retained artifacts; never authorize."""
from __future__ import annotations
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3

CONTRACT = 'optional-execution-record-consistency/1'
CASES = {'atomic-authority-effect': ('allowed', 'revoked'),
         'refund-intent': ('allowed', 'revoked', 'same-intent', 'distinct-intent')}
COMPONENTS = ('control_plane', 'moltbot_safe', 'action_manifest', 'gax_imx_transport', 'replay_bundle')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def required(condition, message):
    if not condition:
        raise ValueError(message)


def artifact(root, relative):
    path = root / relative
    required(path.resolve().is_relative_to(root.resolve()), 'artifact escapes package')
    required(path.is_file(), 'missing artifact: ' + relative)
    return path


def check_case(root, profile, scenario):
    value = json.loads(artifact(root, scenario + '/result.json').read_text())
    required(value['schema_version'] == '1.0.0' and value['profile'] == profile
             and value['scenario'] == scenario and value['synthetic'] is True, 'case identity mismatch')
    required(value['consumer_chain_qualified'] is False and value['production_ready'] is False, 'unsupported assurance scope')
    database = artifact(root, scenario + '/destination/refunds.sqlite3')
    # Read a coherent logical snapshot, including committed WAL contents.
    with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute('BEGIN')
        rows = [dict(r) for r in conn.execute('SELECT * FROM effects ORDER BY effect_id')]
    outcomes = value['outcomes']
    count = 2 if scenario in ('same-intent', 'distinct-intent') else 1
    required(type(outcomes) is list and len(outcomes) == count, 'outcome population mismatch')
    ids = [o['effect_id'] for o in outcomes]
    required(all(type(i) is str and bool(i) for i in ids) and len(set(ids)) == count, 'effect identities not distinct')
    expected = [] if scenario == 'revoked' else (ids if scenario == 'distinct-intent' else ids[:1])
    observed = [r['effect_id'] for r in rows]
    required(sorted(expected) == observed == sorted(value['effect_ids']), 'destination population mismatch')
    for index, outcome in enumerate(outcomes):
        executed = scenario != 'revoked' and (index == 0 or scenario == 'distinct-intent')
        required(outcome['newly_executed'] is executed, 'execution record mismatch')
        if executed:
            required(outcome['status'] == 'executed' and outcome['acknowledged'] is True
                     and outcome['observed_state'] == 'applied', 'successful outcome mismatch')
            row = next(r for r in rows if r['effect_id'] == outcome['effect_id'])
            state = outcome['observation']['destination_state']
            required(row['state'] == 'applied', 'effect not applied')
            for key in ('effect_id', 'operation_digest', 'grant_id', 'target', 'amount', 'unit', 'state'):
                required(state[key] == row[key], 'retained operation mismatch: ' + key)
            required(state['payload'] == json.loads(row['payload_json']), 'retained payload mismatch')
    # Producer qualified/witness flags are deliberately not premises.
    return {'scenario': scenario, 'eligible': True, 'consistent': True,
            'input_digest': digest({'record': value, 'destination_effects': rows}),
            'effect_count': len(rows)}


def verify(root, lock_path):
    root, lock_path = Path(root).resolve(), Path(lock_path)
    result = {'contract': CONTRACT, 'verification_level': 'retained-record-consistency',
              'authorizing': False, 'external_truth_verified': False,
              'authority_reevaluated': False, 'production_ready': False,
              'errors': [], 'cases': [], 'valid': False}
    try:
        summary = json.loads(artifact(root, 'summary.json').read_text())
        profile = summary['profile']
        required(profile in CASES, 'unsupported profile')
        result.update(profile=profile, scheduled=len(CASES[profile]))
        lock_bytes = lock_path.read_bytes()
        lock = json.loads(lock_bytes)
        pins = {name: lock['components'][name].get('sha') or lock['components'][name]['accepted_sha'] for name in COMPONENTS}
        required(summary['schema_version'] == '1.0.0', 'unsupported summary version')
        required(summary['tested_revisions'] == pins, 'revision mismatch')
        required(summary['component_lock_sha256'] == hashlib.sha256(lock_bytes).hexdigest(), 'lock digest mismatch')
        records = summary['results']
        required(type(records) is list and len(records) == len(CASES[profile]), 'scheduled population mismatch')
        required(sorted(r['scenario'] for r in records) == sorted(CASES[profile]), 'missing, duplicate, or unexpected scenario')
        required(all(type(r['returncode']) is int and r['returncode'] == 0 for r in records), 'failed or interrupted execution')
        dirs = sorted(p.name for p in root.iterdir() if p.is_dir())
        required(dirs == sorted(CASES[profile]), 'unexpected or missing scenario directory')
        result['summary_digest'] = digest(summary)
        result['component_lock_sha256'] = summary['component_lock_sha256']
        for scenario in CASES[profile]:
            try:
                result['cases'].append(check_case(root, profile, scenario))
            except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, StopIteration) as exc:
                result['cases'].append({'scenario': scenario, 'eligible': False, 'consistent': False, 'error': str(exc)})
        result['valid'] = all(case['consistent'] for case in result['cases'])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result['errors'].append(str(exc))
    result['evaluable'] = sum(c['eligible'] for c in result['cases'])
    result['consistent'] = sum(c['consistent'] for c in result['cases'])
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('results_dir', type=Path)
    ap.add_argument('--lock', type=Path, default=Path(__file__).resolve().parents[1] / 'component-lock.json')
    args = ap.parse_args()
    result = verify(args.results_dir, args.lock)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
