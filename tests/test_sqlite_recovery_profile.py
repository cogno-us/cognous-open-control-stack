import json
import sqlite3
import pytest
from reference_profiles.sqlite_recovery import snapshot, restore
from reference_profiles.context_memory import ContextMemory
from reference_profiles.institutional_review import InstitutionalReview


def test_committed_wal_and_uncommitted_transaction(tmp_path):
    source = tmp_path / 'source.db'
    first = sqlite3.connect(source, isolation_level=None)
    first.execute('PRAGMA journal_mode=WAL')
    first.execute('CREATE TABLE retained (id INTEGER PRIMARY KEY)')
    first.execute('INSERT INTO retained VALUES (1)')
    first.execute('BEGIN IMMEDIATE')
    first.execute('INSERT INTO retained VALUES (2)')
    try:
        snapshot(source, tmp_path / 'backup')
    finally:
        first.rollback(); first.close()
    report = restore(tmp_path / 'backup', tmp_path / 'restored.db')
    assert not report['activation_authorized'] and not report['freshness_verified']
    with sqlite3.connect(tmp_path / 'restored.db') as conn:
        assert conn.execute('SELECT * FROM retained').fetchall() == [(1,)]


def test_restore_preserves_context_revocation(tmp_path):
    memory = ContextMemory(tmp_path / 'memory.db', clock=lambda: 100)
    memory.admit(item_id='context', content='synthetic', purposes=['review'], recipients=['worker'], obligations=['source'], expires_at=200, source_ref='synthetic')
    memory.revoke('context')
    snapshot(memory.path, tmp_path / 'backup')
    restore(tmp_path / 'backup', tmp_path / 'restored.db')
    restored = ContextMemory(tmp_path / 'restored.db', clock=lambda: 100)
    with pytest.raises(PermissionError):
        restored.deliver('context', purpose='review', recipient='worker', expected_generation=restored.generation(), callback=lambda _: pytest.fail('must not disclose'))


def test_backup_cannot_claim_current_authority_or_overwrite(tmp_path):
    s = InstitutionalReview(tmp_path / 'review.db', reviewers=['owner'])
    manifest = snapshot(s.path, tmp_path / 'backup')
    assert not manifest['freshness_verified']
    restore(tmp_path / 'backup', tmp_path / 'staging.db')
    with pytest.raises(FileExistsError): restore(tmp_path / 'backup', tmp_path / 'staging.db')
    p = tmp_path / 'backup/manifest.json'
    manifest['activation_authorized'] = True
    p.write_text(json.dumps(manifest))
    with pytest.raises(ValueError): restore(tmp_path / 'backup', tmp_path / 'other.db')
    assert not (tmp_path / 'other.db').exists()


def test_corrupt_snapshot_and_missing_source_fail_closed(tmp_path):
    s = InstitutionalReview(tmp_path / 'review.db', reviewers=['owner'])
    snapshot(s.path, tmp_path / 'backup')
    with (tmp_path / 'backup/snapshot.sqlite3').open('ab') as stream: stream.write(b'changed')
    with pytest.raises(ValueError): restore(tmp_path / 'backup', tmp_path / 'staging.db')
    assert not (tmp_path / 'staging.db').exists()
    with pytest.raises(FileNotFoundError): snapshot(tmp_path / 'missing', tmp_path / 'missing-backup')
    assert not (tmp_path / 'missing').exists()
