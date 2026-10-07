import os
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
