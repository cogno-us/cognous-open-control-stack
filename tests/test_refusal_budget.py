"""SEC05 lifetime limits, transaction failure and bounded durable growth."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
from unittest.mock import patch
import pytest
from reference_profiles.assurance_runtime import AssuranceRuntime, AUDIT_DEFAULTS, sign_request

KEY=b'synthetic-budget-test-key-00000000'
class ProbeRuntime(AssuranceRuntime):
    roles={'probe':'agent'}
    def op_probe(self,conn,actor,args):
        conn.execute('INSERT INTO effects VALUES (?,?,?,?,?)',(args['id'],'run','request',''.join(args.get('parts',['synthetic'])),'evidence'))
        return {'observed_state':'applied'}


def runtime(tmp_path, **limits):
    return ProbeRuntime.create(tmp_path/'audit.db',stream='s',principals={'known':{'version':1,'roles':['agent']}},keys={('known',1):KEY},clock=lambda:100,observe_environment=lambda:{},audit_limits=dict(AUDIT_DEFAULTS,**limits))


def request(n,actor='unknown',operation='unsupported',arguments=None):
    return sign_request(KEY,stream='s',actor=actor,key_version=1,nonce='n'+str(n),expires_at=200,operation=operation,arguments=arguments or {})


def counts(rt):
    with rt.connection() as c:
        return {t:c.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ('events','nonces','effects','audit_counters')}


def reopen(rt):
    return ProbeRuntime(rt.path,keys={('known',1):KEY},clock=lambda:99999,observe_environment=lambda:{})


def test_anonymous_churn_is_globally_bounded_across_restart_and_time(tmp_path):
    rt=runtime(tmp_path,anonymous=3)
    for n in range(40):assert rt.apply(request(n,actor='unknown-'+str(n)))['status']=='denied'
    before=counts(rt); assert before=={'events':3,'nonces':0,'effects':0,'audit_counters':1}
    rt=reopen(rt)
    for n in range(40,80):rt.apply(request(n,actor='new-'+str(n)))
    assert counts(rt)==before
    row=rt.audit_status()['sources'][0]
    assert row['used']==3 and row['suppressed']==77


def test_invalid_signatures_share_anonymous_bucket(tmp_path):
    rt=runtime(tmp_path,anonymous=2)
    for n in range(8):
        r=request(n,actor='known');r['mac']='0'*64
        assert rt.apply(r)['reason']=='BAD_SIGNATURE'
    assert counts(rt)['events']==2 and counts(rt)['nonces']==0
    assert rt.audit_status()['sources'][0]['suppressed']==6


def test_concurrent_refusals_do_not_exceed_limit(tmp_path):
    rt=runtime(tmp_path,anonymous=5)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(lambda n:rt.apply(request(n)),range(100)))
    assert all(r['status']=='denied' for r in results)
    assert counts(rt)['events']==5
    assert rt.audit_status()['sources'][0]['suppressed']==95


def test_authenticated_refusals_bounded_without_losing_retained_history(tmp_path):
    rt=runtime(tmp_path,per_principal=3)
    for n in range(10):assert rt.apply(request(n,actor='known'))['status']=='denied'
    assert counts(rt)=={'events':3,'nonces':3,'effects':0,'audit_counters':2}
    journal=rt.journal();assert all(x['body']['authenticated'] for x in journal['events'])
    assert rt.audit_status()['sources'][1]['suppressed']==7
    assert reopen(rt).journal()==journal


def test_global_capacity_blocks_new_effects(tmp_path):
    rt=runtime(tmp_path,events=2)
    rt.apply(request(0));rt.apply(request(1))
    result=rt.apply(request(2,actor='known',operation='probe',arguments={'id':'effect'}))
    assert result['reason']=='AUDIT_CAPACITY' and result['audit_recorded'] is False
    assert counts(rt)['effects']==0 and counts(rt)['nonces']==0

@pytest.mark.parametrize('failure',[sqlite3.OperationalError('database or disk is full'),sqlite3.OperationalError('audit write failed')])
def test_audit_write_failure_rolls_back_effect_and_nonce(tmp_path,failure):
    rt=runtime(tmp_path)
    with patch.object(rt,'event',side_effect=failure):
        result=rt.apply(request(0,actor='known',operation='probe',arguments={'id':'effect'}))
    assert result['status']=='denied' and result['audit_recorded'] is False
    assert counts(rt)['effects']==0 and counts(rt)['nonces']==0


def test_event_payload_budget_rolls_back_effect(tmp_path):
    rt=runtime(tmp_path,event_bytes=32)
    assert rt.apply(request(0,actor='known',operation='probe',arguments={'id':'effect'}))['status']=='denied'
    assert counts(rt)['events']==0 and counts(rt)['effects']==0


def test_suppression_counter_saturates(tmp_path):
    rt=runtime(tmp_path,anonymous=1);rt.apply(request(0))
    with rt.connection() as c:c.execute("UPDATE audit_counters SET suppressed=9007199254740991")
    rt.apply(request(1));assert rt.audit_status()['sources'][0]['suppressed']==9007199254740991


def test_retention_keeps_authority_records_and_checks_source_capacity(tmp_path):
    rt=runtime(tmp_path,anonymous=1,sources=1)
    for n in range(4):rt.apply(request(n))
    result=rt.apply(request(5,actor='known',operation='probe',arguments={'id':'effect'}))
    assert result['status']=='denied' and counts(rt)['effects']==0
    with rt.connection() as c:assert rt.get(c,'principal','known')['enabled']


def test_durable_files_stay_bounded_through_repeated_floods(tmp_path):
    rt=runtime(tmp_path,anonymous=3,database_pages=32)
    sizes=[]
    for wave in range(3):
        for n in range(200):rt.apply(request(wave*200+n))
        sizes.append(sum(p.stat().st_size for p in tmp_path.iterdir() if p.is_file()))
    assert max(sizes)<=32*4096 and sizes[0]==sizes[-1]
    assert not Path(str(rt.path)+'-wal').exists()
    with rt.audit_connection() as c:assert c.execute('PRAGMA max_page_count').fetchone()[0]==32


def test_wal_configuration_and_missing_storage_fail_closed(tmp_path):
    rt=runtime(tmp_path)
    with sqlite3.connect(rt.path) as c:c.execute('PRAGMA journal_mode=WAL')
    result=rt.apply(request(0));assert result['status']=='denied' and result['audit_recorded'] is False
    rt.path.unlink();assert rt.apply(request(1))['status']=='denied';assert not rt.path.exists()


def test_pre_auth_input_rejection_never_opens_database(tmp_path):
    rt=runtime(tmp_path)
    with patch.object(rt,'connection',side_effect=AssertionError('database opened')):
        assert rt.apply(['x'*65536]*17)['reason']=='INVALID_REQUEST'


def test_real_sqlite_page_limit_rolls_back_effect(tmp_path):
    rt=runtime(tmp_path,database_pages=16)
    result=rt.apply(request(0,actor='known',operation='probe',arguments={'id':'oversized','parts':['x'*32768]*3}))
    assert result['status']=='denied' and result['audit_recorded'] is False
    assert counts(rt)['effects']==0 and counts(rt)['nonces']==0
    assert rt.path.stat().st_size<=16*4096
