import os
import dataclasses
import sqlite3
from pathlib import Path
import sys
import pytest
from tools.optional_execution_profile import prepare
from reference_profiles.temporal_refund import SCENARIOS, run_trajectory

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.optional-work'


@pytest.fixture(scope='module', autouse=True)
def dependencies():
    env, _, _ = prepare(WORK)
    os.environ.update(env)
    sys.path[:0] = env['PYTHONPATH'].split(os.pathsep)


@pytest.mark.parametrize('scenario', SCENARIOS)
def test_two_step_trajectory(tmp_path, scenario):
    value = run_trajectory(tmp_path / 'run', WORK, scenario)
    assert value['qualified'], value
    assert not value['remote_atomicity'] and not value['compensation_authorized']
    if scenario == 'allowed':
        assert sorted(e['amount'] for e in value['effects']) == [25.0, 50.0]
        assert value['events'][-1]['separate_decision'] and value['events'][-1]['separate_claim']
    elif scenario == 'first-unknown':
        assert value['events'][0]['result']['status'] == 'unknown'
        assert value['events'][1]['retry_authorized'] is False
    elif scenario == 'cancel-requested':
        assert value['events'][1]['cancellation_requested'] is True
        assert value['events'][1]['cessation_verified'] is False


@pytest.mark.parametrize('scenario,mutation', [
    ('allowed', 'second-amount'),
    ('allowed', 'second-effect-id'),
    ('allowed', 'second-state'),
    ('revoked', 'first-state'),
    ('cancel-requested', 'first-status'),
    ('first-unknown', 'acknowledged'),
    ('allowed', 'result-effect-id'),
    ('allowed', 'result-decision-id'),
])
def test_qualification_rejects_inconsistent_observations(tmp_path, monkeypatch, scenario, mutation):
    from engine.local_authority_effect import AtomicLocalControlPlaneExecutor
    original = AtomicLocalControlPlaneExecutor.execute
    calls = 0

    def inconsistent_execute(self, **kwargs):
        nonlocal calls
        calls += 1
        result = original(self, **kwargs)
        if calls == 2 and mutation.startswith('second-'):
            column, value = {
                'second-amount': ('amount', 99.0),
                'second-effect-id': ('effect_id', 'unrelated-effect'),
                'second-state': ('state', 'partial'),
            }[mutation]
            with sqlite3.connect(self.destination.path) as conn:
                conn.execute(f'UPDATE effects SET {column}=? WHERE effect_id=?',
                             (value, kwargs['envelope'].effect_id))
        elif calls == 1 and mutation == 'first-state':
            with sqlite3.connect(self.destination.path) as conn:
                conn.execute("UPDATE effects SET state='partial'")
        elif calls == 1 and mutation == 'first-status':
            result = dataclasses.replace(result, status='denied')
        elif calls == 1 and mutation == 'acknowledged':
            result = dataclasses.replace(result, acknowledged=True)
        elif calls == 2 and mutation == 'result-effect-id':
            result = dataclasses.replace(result, effect_id='unrelated-effect')
        elif calls == 2 and mutation == 'result-decision-id':
            result = dataclasses.replace(result, decision_id='unrelated-decision')
        return result

    monkeypatch.setattr(AtomicLocalControlPlaneExecutor, 'execute', inconsistent_execute)
    value = run_trajectory(tmp_path / 'run', WORK, scenario)
    assert value['qualified'] is False, value
    assert value['remote_atomicity'] is value['compensation_authorized'] is value['production_ready'] is False
