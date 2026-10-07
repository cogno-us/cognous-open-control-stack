import os
from pathlib import Path
import sys
import pytest
from tools.optional_execution_profile import prepare
from tools.optional_execution import BASE
from reference_profiles.notification import ADAPTER, GRANT, notification_case

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.optional-work'


@pytest.fixture(scope='module', autouse=True)
def dependencies():
    env, _, _ = prepare(WORK)
    os.environ.update(env)
    sys.path[:0] = env['PYTHONPATH'].split(os.pathsep)


@pytest.fixture
def case(tmp_path):
    return notification_case(tmp_path, WORK)


def test_separate_grant_and_duplicate_outbox(case):
    workflow, authority, outbox, p, d, refund, refund_decision = case
    assert d.binding.grant_id == GRANT != refund_decision.binding.grant_id
    assert d.decision_id != refund_decision.decision_id and d.effect_id != refund_decision.effect_id
    workflow.execute(p,d,adapter_id=ADAPTER,now=BASE)
    workflow.execute(p,d,adapter_id=ADAPTER,now=BASE)
    assert outbox.count() == 1
    assert outbox.observe(d.effect_id).state == 'applied'


@pytest.mark.parametrize('change', ['revoked','payload','target','adapter','refund-decision'])
def test_refund_does_not_authorize_notification(case, change):
    workflow, authority, outbox, p, d, refund, refund_decision = case
    adapter = ADAPTER
    if change == 'revoked': authority.statuses[GRANT].status = 'revoked'
    elif change == 'payload': p = p.model_copy(update={'payload':dict(p.payload,message='substituted')})
    elif change == 'target': p = p.model_copy(update={'target':'urn:cognous:synthetic-inbox:other'})
    elif change == 'adapter': adapter = 'refund-adapter'
    else: d = refund_decision
    with pytest.raises(PermissionError): workflow.execute(p,d,adapter_id=adapter,now=BASE)
    assert outbox.count() == 0
    assert refund.claim_state(next(iter_claim(refund))) == 'consumed'


def iter_claim(refund):
    import sqlite3
    with sqlite3.connect(refund.path) as conn:
        return iter(r[0] for r in conn.execute('SELECT claim_id FROM execution_claims_v1'))


def test_lost_ack_preserves_one_outbox_effect(case):
    workflow, authority, outbox, p, d, _, _ = case
    workflow.execute(p,d,adapter_id=ADAPTER,now=BASE,lose_ack=True)
    assert outbox.count() == 1
    workflow.execute(p,d,adapter_id=ADAPTER,now=BASE)
    assert outbox.count() == 1


def test_outbox_requires_retained_refund_prerequisite(case):
    import sqlite3
    workflow, _, outbox, p, d, refund, _ = case
    with sqlite3.connect(refund.path) as conn:
        conn.execute('DELETE FROM effects')
    attempt, observation = workflow.execute(p,d,adapter_id=ADAPTER,now=BASE)
    assert outbox.count() == 0
    assert attempt.status != 'acknowledged'
