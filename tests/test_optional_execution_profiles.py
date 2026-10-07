"""Exercise the selectable hub paths against real accepted component APIs."""
import os
from pathlib import Path
import sqlite3
import sys

import pytest

from tools.optional_execution import PROFILES, BASE, run_case
from tools.optional_execution_profile import prepare

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.optional-work'
SELECTED = [os.environ['OPTIONAL_EXECUTION_PROFILE']] if os.environ.get('OPTIONAL_EXECUTION_PROFILE') else list(PROFILES)
CASES = [(p, s) for p in SELECTED for s in
         (['allowed', 'revoked'] if p == 'atomic-authority-effect' else
          ['allowed', 'revoked', 'same-intent', 'distinct-intent'])]


@pytest.fixture(scope='module', autouse=True)
def dependencies():
    env, _, _ = prepare(WORK)
    os.environ.update(env)
    sys.path[:0] = env['PYTHONPATH'].split(os.pathsep)


@pytest.mark.parametrize('profile,scenario', CASES)
def test_selected_execution(tmp_path, profile, scenario):
    value = run_case(profile, scenario, tmp_path / 'case', WORK)
    assert value['qualified']
    assert not value['consumer_chain_qualified']
    if profile == 'atomic-authority-effect':
        evidence = value['profile_evidence']
        assert evidence['claim_state'] == ('issued' if scenario == 'revoked' else 'consumed')
        assert evidence['reconciliation']['observed_state'] == ('unknown' if scenario == 'revoked' else 'applied')
    else:
        assert value['profile_evidence']['authority_established_by_registry'] is False
        assert value['profile_evidence']['retry_eligible'] is False
        if scenario == 'same-intent':
            assert value['outcomes'][0]['effect_id'] != value['outcomes'][1]['effect_id']
            assert value['effect_ids'] == [value['outcomes'][0]['effect_id']]
            assert value['outcomes'][1]['control_plane_evidence']['reconciliation']['retry_eligible'] is False


@pytest.mark.parametrize('profile', SELECTED)
def test_existing_output_preserved(tmp_path, profile):
    root = tmp_path / 'case'
    root.mkdir()
    marker = root / 'keep.txt'
    marker.write_text('retained')
    with pytest.raises(FileExistsError):
        run_case(profile, 'allowed', root, WORK)
    assert marker.read_text() == 'retained'


def rows(path):
    with sqlite3.connect(path) as conn:
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {t: conn.execute('SELECT * FROM "' + t + '"').fetchall() for t in tables}


@pytest.mark.parametrize('profile', SELECTED)
def test_selected_database_rejects_other_profile(tmp_path, profile):
    from engine.local_authority_effect import AtomicAuthorityEffectDestination
    from engine.refund_intent import RefundIntentRegistry
    from engine.safe_executor import DurableRefundDestination
    root = tmp_path / 'case'
    run_case(profile, 'allowed', root, WORK)
    destination = DurableRefundDestination(root / 'destination')
    before = rows(destination.path)
    with pytest.raises(PermissionError, match='cannot share'):
        if profile == 'atomic-authority-effect':
            RefundIntentRegistry(destination)
        else:
            AtomicAuthorityEffectDestination(root / 'destination', clock=lambda: BASE)
    assert rows(destination.path) == before
