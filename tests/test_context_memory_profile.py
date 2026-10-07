import sqlite3
import pytest
from reference_profiles.context_memory import ContextMemory


@pytest.fixture
def store(tmp_path):
    clock = [100]
    s = ContextMemory(tmp_path / 'context.sqlite3', clock=lambda: clock[0])
    s.admit(item_id='source', content='synthetic context', purposes=['refund'], recipients=['reviewer'],
            obligations=['retain-provenance'], expires_at=200, source_ref='synthetic:source')
    return s, clock


def deliver(s, **kw):
    return s.deliver('source', purpose='refund', recipient='reviewer', expected_generation=s.generation(), callback=lambda c: None, **kw)


def test_admission_and_reopen(store):
    s, clock = store
    reopened = ContextMemory(s.path, clock=lambda: clock[0])
    result = deliver(reopened)
    assert result['state'] == 'delivered'
    assert result['authorizing'] is result['model_reliance_verified'] is False


@pytest.mark.parametrize('field,value', [('purpose','marketing'), ('recipient','other'), ('expected_generation',0)])
def test_current_use_rejected_and_recorded(store, field, value):
    s, _ = store
    args = dict(purpose='refund', recipient='reviewer', expected_generation=s.generation(), callback=lambda _: pytest.fail('must not disclose'))
    args[field] = value
    with pytest.raises(PermissionError):
        s.deliver('source', **args)
    with sqlite3.connect(s.path) as conn:
        assert conn.execute("SELECT count(*) FROM events WHERE kind='recall_denied'").fetchone()[0] == 1
        assert conn.execute('SELECT count(*) FROM deliveries').fetchone()[0] == 0


def test_intent_committed_before_delivery_and_uncertainty_retained(store):
    s, _ = store
    def receive(content):
        with sqlite3.connect(s.path) as conn:
            assert conn.execute('SELECT state FROM deliveries').fetchone()[0] == 'pending'
        raise TimeoutError('acknowledgement lost')
    result = s.deliver('source', purpose='refund', recipient='reviewer', expected_generation=s.generation(), callback=receive)
    assert result['state'] == 'unknown'


def test_derivation_preserves_restrictions_and_parent_revocation(store):
    s, _ = store
    kwargs = dict(item_id='summary', content='short', purposes=['refund'], recipients=['reviewer'],
                  obligations=['retain-provenance'], expires_at=190, source_ref='synthetic:summary', parents=['source'])
    with pytest.raises(PermissionError):
        s.admit(**dict(kwargs, recipients=['reviewer','other']))
    s.admit(**kwargs)
    s.revoke('source')
    with pytest.raises(PermissionError):
        s.deliver('summary', purpose='refund', recipient='reviewer', expected_generation=s.generation(), callback=lambda _: pytest.fail('must not disclose'))


def test_expiry_removes_content_preserves_receipt(store):
    s, clock = store
    clock[0] = 200
    with pytest.raises(PermissionError):
        deliver(s)
    assert s.purge_expired() == ['source']
    with sqlite3.connect(s.path) as conn:
        content, receipt = conn.execute('SELECT content, receipt FROM items').fetchone()
        assert content is None and 'content_sha256' in receipt


def test_duplicate_identity_does_not_replace_receipt(store):
    s, _ = store
    with pytest.raises(sqlite3.IntegrityError):
        s.admit(item_id='source', content='changed', purposes=['refund'], recipients=['reviewer'], obligations=['retain-provenance'], expires_at=200, source_ref='other')
    assert s.generation() == 1

@pytest.mark.parametrize('change', [dict(purposes=['marketing']), dict(obligations=['other']), dict(expires_at=201)])
def test_derivation_cannot_remove_obligations_or_expand_scope(store, change):
    s, _ = store
    args = dict(item_id='summary', content='short', purposes=['refund'], recipients=['reviewer'], obligations=['retain-provenance'],
                expires_at=190, source_ref='synthetic:summary', parents=['source'])
    with pytest.raises(PermissionError):
        s.admit(**dict(args, **change))
    assert s.generation() == 1


def test_logs_do_not_copy_content(store):
    s, _ = store
    deliver(s)
    with sqlite3.connect(s.path) as conn:
        assert all('synthetic context' not in r[0] for r in conn.execute('SELECT detail FROM events'))


def test_inflight_disclosure_is_not_retracted_by_later_revocation(store):
    s, _ = store
    seen = []
    def receive(content):
        s.revoke('source')
        seen.append(content)
    result = s.deliver('source', purpose='refund', recipient='reviewer', expected_generation=s.generation(), callback=receive)
    assert result['state'] == 'delivered' and seen
    with pytest.raises(PermissionError):
        deliver(s)

@pytest.mark.parametrize('invalid', [float('nan'), float('inf'), True])
def test_invalid_host_time_cannot_admit_delivery(store, invalid):
    s, clock = store
    clock[0] = invalid
    with pytest.raises(ValueError, match='finite trusted time'):
        deliver(s)
