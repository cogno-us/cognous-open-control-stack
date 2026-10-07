"""Negative cases must fail on semantics even when producer flags say pass."""
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys

import pytest
from tools.optional_execution import run_case
from tools.optional_execution_profile import prepare
from tools.verify_optional_evidence import verify

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.optional-work'
PROFILE = os.environ.get('OPTIONAL_EXECUTION_PROFILE', 'refund-intent')


@pytest.fixture(scope='module')
def packet(tmp_path_factory):
    env, pins, lock_digest = prepare(WORK)
    os.environ.update(env)
    sys.path[:0] = env['PYTHONPATH'].split(os.pathsep)
    root = tmp_path_factory.mktemp('contract-source')
    scenarios = ['allowed', 'revoked'] + ([] if PROFILE == 'atomic-authority-effect' else ['same-intent', 'distinct-intent'])
    for scenario in scenarios:
        record = run_case(PROFILE, scenario, root / scenario, WORK)
        (root / scenario / 'result.json').write_text(json.dumps(record))
    summary = {'schema_version': '1.0.0', 'profile': PROFILE, 'qualified': True,
               'tested_revisions': pins, 'component_lock_sha256': lock_digest,
               'results': [{'scenario': s, 'returncode': 0} for s in scenarios]}
    (root / 'summary.json').write_text(json.dumps(summary))
    return root


def report(root):
    return verify(root, ROOT / 'component-lock.json')


def edit(path, fn):
    value = json.loads(path.read_text())
    fn(value)
    path.write_text(json.dumps(value))


def test_record_consistency_and_scope(packet):
    result = report(packet)
    assert result['valid']
    assert result['scheduled'] == result['consistent'] == result['evaluable']
    assert result['authorizing'] is result['authority_reevaluated'] is result['external_truth_verified'] is False
    assert all(c['input_digest'] for c in result['cases'])


def test_producer_flags_are_not_premises(packet, tmp_path):
    root = tmp_path / 'packet'
    shutil.copytree(packet, root)
    edit(root / 'summary.json', lambda v: v.update(qualified=False))
    edit(root / 'allowed/result.json', lambda v: v.update(qualified=False))
    assert report(root)['valid']


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'unexpected', 'failed', 'revision', 'lock',
                                      'missing-db', 'extra-effect', 'changed-effect', 'false-outcome', 'scope'])
def test_rejects_incomplete_or_inconsistent_packet(packet, tmp_path, mutation):
    root = tmp_path / 'packet'
    shutil.copytree(packet, root)
    summary = root / 'summary.json'
    if mutation == 'missing':
        (root / 'revoked/result.json').unlink()
    elif mutation == 'duplicate':
        edit(summary, lambda v: v['results'].__setitem__(1, v['results'][0]))
    elif mutation == 'unexpected':
        (root / 'unreported-case').mkdir()
    elif mutation == 'failed':
        edit(summary, lambda v: v['results'][0].update(returncode=124))
    elif mutation == 'revision':
        edit(summary, lambda v: v['tested_revisions'].update(control_plane='0' * 40))
    elif mutation == 'lock':
        edit(summary, lambda v: v.update(component_lock_sha256='0' * 64))
    elif mutation == 'missing-db':
        (root / 'allowed/destination/refunds.sqlite3').unlink()
    elif mutation in ('extra-effect', 'changed-effect'):
        with sqlite3.connect(root / 'allowed/destination/refunds.sqlite3') as conn:
            if mutation == 'changed-effect':
                conn.execute('UPDATE effects SET amount=amount+1')
            else:
                conn.execute("INSERT INTO effects SELECT 'unexplained', operation_digest, grant_id, target, amount, unit, payload_json, state FROM effects LIMIT 1")
    elif mutation == 'false-outcome':
        edit(root / 'allowed/result.json', lambda v: v['outcomes'][0].update(newly_executed=False))
    else:
        edit(root / 'allowed/result.json', lambda v: v.update(consumer_chain_qualified=True))
    result = report(root)
    assert not result['valid'], (mutation, result)
    assert result['scheduled'] == (2 if PROFILE == 'atomic-authority-effect' else 4)
