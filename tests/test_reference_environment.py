import sys
from pathlib import Path
import pytest
from tools.reference_environment import inspect_environment, sqlite_probe

LOCK = Path(__file__).resolve().parents[1] / 'component-lock.json'


def test_local_probe_is_disposable(tmp_path):
    retained = tmp_path / 'retained.txt'
    retained.write_text('keep')
    assert all(sqlite_probe(tmp_path).values())
    assert list(tmp_path.iterdir()) == [retained]
    assert retained.read_text() == 'keep'


def test_report_separates_capabilities_from_assurance(tmp_path):
    result = inspect_environment('atomic-authority-effect', tmp_path, LOCK)
    assert result['reference_prerequisites_observed']
    assert result['deployment_qualified'] is result['authorizing'] is False
    assert result['unverified'] and result['assumptions']
    assert len(result['component_lock_sha256']) == 64
    assert result['components']['control_plane']['revision']


@pytest.mark.parametrize('system,version', [('win32', (3,11)), ('linux', (3,13))])
def test_unsupported_or_unverified_runtime_fails_preflight(tmp_path, monkeypatch, system, version):
    monkeypatch.setattr(sys, 'platform', system)
    monkeypatch.setattr(sys, 'version_info', version)
    result = inspect_environment('refund-intent', tmp_path, LOCK)
    assert not result['reference_prerequisites_observed']


def test_missing_storage_is_not_created(tmp_path):
    target = tmp_path / 'absent'
    result = inspect_environment('ordinary-bounded', target, LOCK)
    assert not result['reference_prerequisites_observed']
    assert not target.exists()


def test_unknown_profile_rejected(tmp_path):
    with pytest.raises(ValueError):
        inspect_environment('combined-atomic-intent', tmp_path, LOCK)
