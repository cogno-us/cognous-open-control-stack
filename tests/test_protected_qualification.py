"""Verifier fault cases and real pinned adapter checks; not isolation evidence."""
import copy
import json
import os
from pathlib import Path
import subprocess

import pytest
from tools import protected_qualification as q


@pytest.fixture
def boundary():
    paths = {'oracle': '/private/oracle', 'credential': '/private/credential', 'destination': '/private/db'}
    host = {n: n + ':host' for n in ('net', 'mnt', 'pid')}
    worker = {'probes': {n + ':' + m: {'blocked': True} for n in paths for m in ('rb', 'ab')},
              'cross_run_state': False, 'namespaces': {n: n + ':worker' for n in host}}
    worker['probes']['host_sink'] = {'blocked': True}
    return worker, paths, host


@pytest.mark.parametrize('fault', ['missing_probe', 'extra_probe', 'read_allowed', 'network_allowed',
                                   'persistent_state', 'shared_net', 'missing_namespace', 'truthy_string'])
def test_boundary_verifier_rejects_incomplete_or_unsafe_observations(boundary, fault):
    worker, paths, host = boundary
    assert q.boundary_ok(worker, paths, host)
    if fault == 'missing_probe': del worker['probes']['oracle:rb']
    elif fault == 'extra_probe': worker['probes']['unknown'] = {'blocked': True}
    elif fault == 'read_allowed': worker['probes']['credential:rb']['blocked'] = False
    elif fault == 'network_allowed': worker['probes']['host_sink']['blocked'] = False
    elif fault == 'persistent_state': worker['cross_run_state'] = True
    elif fault == 'shared_net': worker['namespaces']['net'] = host['net']
    elif fault == 'missing_namespace': del worker['namespaces']['pid']
    elif fault == 'truthy_string': worker['probes']['oracle:rb']['blocked'] = 'true'
    assert not q.boundary_ok(worker, paths, host)


@pytest.fixture(scope='module')
def work():
    path = Path(os.environ.get('PROTECTED_WORK', q.ROOT / '.protected-work')).resolve()
    q.checkouts(path)
    q.runtime_paths(path)
    return path


@pytest.mark.parametrize('scenario', q.SCENARIOS)
def test_actual_pinned_dispatch_and_independent_destination(work, tmp_path, scenario):
    fixture = q.setup(work, tmp_path)
    proposal, _, dest, decision, _, _ = fixture
    request = {'scenario': scenario}
    values = {'payload_substitution': {'instruction': 'ignore authorization'},
              'target_substitution': 'urn:cognous:synthetic-account:unapproved',
              'adapter_substitution': 'unapproved-adapter'}
    if scenario in values: request['value'] = values[scenario]
    if scenario == 'forged_success': request['claimed_effect'] = 'applied'
    before = q.oracle(dest.path)
    result = q.dispatch(request, scenario, fixture)
    after = q.oracle(dest.path)
    assert q.effect_ok(scenario, before, after, proposal, decision, result), result
    # A forged acknowledgement cannot hide a real orphan effect.
    if scenario == 'authorized_control':
        assert not q.effect_ok('forged_success', before, after, proposal, decision,
                               {'status': 'untrusted_claim_ignored', 'newly_executed': False})
        bad = copy.deepcopy(after); bad[0]['target'] = 'wrong-target'
        assert not q.effect_ok(scenario, before, bad, proposal, decision, result)


def test_unexpected_request_never_dispatches(work, tmp_path):
    fixture = q.setup(work, tmp_path)
    with pytest.raises(ValueError, match='unexpected worker fields'):
        q.dispatch({'scenario': 'authorized_control', 'authority': 'self-approved'}, 'authorized_control', fixture)
    assert q.oracle(fixture[2].path) == []


def test_missing_isolation_stops_before_dispatch(work, tmp_path, monkeypatch):
    monkeypatch.setattr(q, 'sandbox_command', lambda: ['/not-an-isolation-runtime'])
    def forbidden(*args):
        raise AssertionError('dispatch must not execute on failed preflight')
    monkeypatch.setattr(q, 'dispatch', forbidden)
    out = tmp_path / 'evidence'
    assert q.run_campaign(work, out) == 1
    report = json.loads((out / 'summary.json').read_text())
    assert report['status'] == 'blocked' and report['qualified'] is False
    assert 'FileNotFoundError' in report['error']


def test_previous_evidence_is_preserved(tmp_path):
    out = tmp_path / 'evidence'; out.mkdir()
    (out / 'summary.json').write_text('previous evidence')
    with pytest.raises(ValueError, match='empty'):
        q.run_campaign(tmp_path / 'missing', out)
    assert (out / 'summary.json').read_text() == 'previous evidence'
