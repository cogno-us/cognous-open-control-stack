"""S2 lane B: deterministic local ingress schedules, not network qualification."""
import json
import multiprocessing
from pathlib import Path
import sqlite3
import subprocess
import sys
from unittest.mock import patch

import pytest
import test_protected_destination as legacy
from reference_profiles.assurance_runtime import Denied
from reference_profiles.protected_destination import (
    ProtectedDestination, ATTEMPTS_PER_INTERVAL, UNAUTHENTICATED_DETAIL_LIMIT,
    COUNTER_MAX,
)


@pytest.fixture
def fixture():
    case = legacy.DestinationTests()
    case.setUp()
    yield case
    case.doCleanups()


def state(case):
    with case.runtime.connection() as c:
        return json.loads(c.execute('SELECT body FROM destination_ingress').fetchone()[0])


def invalid(i):
    return {'issuer':'admin' if i % 2 else 'broker', 'body':{
        'id':'forged-'+str(i), 'operation':'execute', 'at':100, 'arguments':{}},
        'signature':'00'*64}


def flood(case, count):
    return [case.runtime.apply(invalid(i)) for i in range(count)]


def test_fixed_schedule_resource_bounds(fixture, tmp_path):
    f = fixture
    # setUp admits three legitimate administrative commands at t=100.
    before = f.path.stat().st_size
    results = flood(f, 400)
    s = state(f)
    assert sum(r['reason']=='INGRESS_SATURATED' for r in results) == 275
    assert s['admitted'] == 128 and s['requests'] == 403
    assert s['unauthenticated'] == 125 and s['limited'] == 275
    assert s['details'] == 64 and s['dropped_detail'] == 336
    with f.runtime.connection() as c:
        rows = {t:c.execute('SELECT count(*) FROM '+t).fetchone()[0]
                for t in ('objects','events','effects','destination_ingress')}
        pages = c.execute('PRAGMA page_count').fetchone()[0]
        size = c.execute('PRAGMA page_size').fetchone()[0]
        events = [json.loads(r[0]) for r in c.execute('SELECT body FROM events')]
    assert rows == {'objects':8,'events':67,'effects':0,'destination_ingress':1}
    assert all(e['command']=='unknown' for e in events if not e['command_authenticated'])
    after = f.path.stat().st_size
    # Additional identical-shape traffic must not grow the file or rows.
    flood(f, 400)
    assert f.path.stat().st_size == after
    assert state(f)['dropped_detail'] == 736
    measurement = dict(schedule='t=100; 3 setup commands; 400 distinct forgeries; 400 more',
        initial_bytes=before, after_first_flood_bytes=after,
        final_bytes=f.path.stat().st_size, page_count=pages, page_size=size,
        rows=rows, first_flood_accepted=0, first_flood_denied=400,
        persisted_unauthenticated_detail=64, state=state(f))
    print('INGRESS_MEASUREMENT='+json.dumps(measurement, sort_keys=True))


def test_restart_and_fixed_advancing_regressing_clocks(fixture):
    f=fixture
    flood(f, 200)
    for stamp in (100, 99, 0, 159):
        f.now=stamp
        f.runtime=ProtectedDestination(f.path, clock=lambda:f.now, **f.config)
        assert f.runtime.apply(invalid(stamp))['reason']=='INGRESS_SATURATED'
    for stamp in (160, 10000, 100000):
        f.now=stamp
        # Invalid shapes avoid key expiry affecting the schedule.
        for _ in range(128): assert f.runtime.apply({})['reason']=='INVALID_REQUEST'
        assert f.runtime.apply({})['reason']=='INGRESS_SATURATED'
    s=state(f)
    assert s['start']==100000 and s['end']==100060
    assert s['details']==64 and s['used']==128
    with f.runtime.connection() as c:
        assert c.execute('SELECT count(*) FROM destination_ingress').fetchone()[0]==1
        assert c.execute('SELECT count(*) FROM events').fetchone()[0]==67


def competing(path, config, count, queue):
    r=ProtectedDestination(path, clock=lambda:100, **config)
    queue.put([r.apply(invalid(i))['reason'] for i in range(count)])


def test_processes_share_one_limit(fixture):
    f=fixture;ctx=multiprocessing.get_context('spawn');q=ctx.Queue()
    ps=[ctx.Process(target=competing,args=(str(f.path),f.config,50,q)) for _ in range(4)]
    for p in ps:p.start()
    results=[]
    for _ in ps:results.extend(q.get(timeout=30))
    for p in ps:p.join(10);assert p.exitcode==0
    assert results.count('INGRESS_SATURATED')==75
    assert state(f)['admitted']==128 and state(f)['details']==64
    assert f.count()==0


def test_saturation_recovery_and_legitimate_effect(fixture):
    f=fixture; flood(f,200)
    execute=f.request('execute',f.args())
    assert f.runtime.apply(execute)['reason']=='INGRESS_SATURATED'
    recovery=f.request('ingress_recover',{})
    assert f.runtime.apply(recovery)['reason']=='INGRESS_SATURATED'
    assert f.runtime.recover_ingress(recovery)['status']=='accepted'
    assert state(f)['details']==64
    assert f.runtime.apply(execute)['status']=='accepted'
    assert f.count()==1
    assert f.call('fence',scope='tenant',generation=8)['status']=='accepted'
    assert f.runtime.recover_ingress(recovery)['reason']=='COMMAND_REPLAY'
    # Replay cannot refill again.
    assert state(f)['recoveries']==1 and state(f)['used']==2


@pytest.mark.parametrize('shape',[None,[],{},'text',{'body':[]}, {'body':{'operation':'execute'}}])
def test_malformed_routes_are_metered(fixture,shape):
    f=fixture;before=state(f)['used']
    assert f.runtime.apply(shape)['status']=='denied'
    assert state(f)['used']==before+1
    assert f.count()==0


@pytest.mark.parametrize('operation',['fence','destination_grants','provision','revoke','execute'])
def test_direct_operation_cannot_bypass_admission(fixture,operation):
    f=fixture
    with f.runtime.connection() as c:
        with pytest.raises(Denied,match='DESTINATION_ADMISSION_REQUIRED'):
            getattr(f.runtime,'op_'+operation)(c,{},'forged')
    assert not hasattr(f.runtime,'op_queue')
    assert f.count()==0


def test_recovery_cannot_dispatch_effect_or_forgery(fixture):
    f=fixture
    with pytest.raises(Denied,match='RECOVERY_SCOPE'):
        f.runtime.recover_ingress(f.request('fence',{'scope':'tenant','generation':8}))
    r=f.request('ingress_recover',{});r['signature']='00'*64
    with pytest.raises(Denied,match='SIGNATURE_INVALID'):f.runtime.recover_ingress(r)
    assert f.count()==0


def test_authenticated_refusals_keep_full_evidence_after_detail_saturation(fixture):
    f=fixture;flood(f,80)
    r=f.request('execute',f.args(verifier_status=None))
    assert f.runtime.apply(r)['reason']=='VERIFIER_UNREACHABLE'
    with f.runtime.connection() as c:
        event=json.loads(c.execute('SELECT body FROM events ORDER BY seq DESC LIMIT 1').fetchone()[0])
    assert event['command_authenticated'] is True and event['command']==r['body']['id']
    assert event['reason']=='VERIFIER_UNREACHABLE'
    assert state(f)['details']==64 and state(f)['dropped_detail']==16


def test_legacy_migration_retains_cap_and_history(fixture):
    f=fixture;flood(f,10)
    with f.runtime.connection() as c:
        history=c.execute('SELECT * FROM events').fetchall()
        c.execute('DROP TABLE destination_ingress')
    f.runtime=ProtectedDestination(f.path,clock=lambda:100,**f.config)
    flood(f,100)
    assert state(f)['details']==64
    with f.runtime.connection() as c:
        assert c.execute('SELECT * FROM events LIMIT 13').fetchall()==history
        assert c.execute('SELECT count(*) FROM events').fetchone()[0]==67


@pytest.mark.parametrize('failure',['event','counter','full_disk'])
def test_required_storage_failure_rolls_back_effect(fixture,failure):
    f=fixture;r=f.request('execute',f.args())
    if failure=='event':
        with f.runtime.connection() as c:
            c.execute("CREATE TRIGGER fail BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT,'audit fixture'); END")
        context=pytest.raises(sqlite3.IntegrityError)
        with context:f.runtime.apply(r)
    elif failure=='counter':
        with patch.object(f.runtime,'_store_ingress',side_effect=sqlite3.OperationalError('disk I/O error')):
            with pytest.raises(sqlite3.OperationalError):f.runtime.apply(r)
    else:
        # SQLite actually returns SQLITE_FULL when audit insertion needs a page.
        with f.runtime.connection() as c:
            pages=c.execute('PRAGMA page_count').fetchone()[0]
            c.execute('CREATE TABLE disk_fixture(payload BLOB)')
            c.execute("CREATE TRIGGER fill_audit BEFORE INSERT ON events BEGIN INSERT INTO disk_fixture VALUES(zeroblob(1048576)); END")
        original=f.runtime.connection
        from contextlib import contextmanager
        @contextmanager
        def full():
            with original() as c:
                c.execute('PRAGMA max_page_count='+str(pages+1))
                yield c
        with patch.object(f.runtime,'connection',full):
            with pytest.raises(sqlite3.OperationalError,match='full') as exc:f.runtime.apply(r)
        assert exc.value.sqlite_errorcode==sqlite3.SQLITE_FULL
    assert f.count()==0 and f.get('grant','grant')['consumed']==0
    with f.runtime.connection() as c:
        assert r['body']['id'] not in f.runtime.population(c,'command')


def test_counter_exhaustion_fails_closed(fixture):
    f=fixture;s=state(f);s['requests']=COUNTER_MAX
    with f.runtime.connection() as c:f.runtime._store_ingress(c,s)
    with pytest.raises(Denied,match='INGRESS_COUNTER_EXHAUSTED'):
        f.runtime.apply(f.request('execute',f.args()))
    assert f.count()==0


def test_enforcement_removal_negative_control(tmp_path):
    root=Path(__file__).resolve().parents[1]
    import shutil
    shutil.copytree(root/'reference_profiles',tmp_path/'reference_profiles',ignore=shutil.ignore_patterns('__pycache__'))
    p=tmp_path/'reference_profiles/protected_destination.py'
    source=p.read_text();target="if state['used'] >= ATTEMPTS_PER_INTERVAL:"
    assert source.count(target)==1
    p.write_text(source.replace(target,'if False:'))
    shutil.copy(root/'tests/test_protected_destination.py',tmp_path/'test_protected_destination.py')
    script="""from test_protected_destination import DestinationTests
f=DestinationTests(); f.setUp()
try:
    results=[f.runtime.apply({}) for _ in range(200)]
    assert sum(r.get('reason')=='INGRESS_SATURATED' for r in results)==75, 'budget enforcement removed'
finally: f.doCleanups()
"""
    r=subprocess.run([sys.executable,'-c',script],cwd=tmp_path,capture_output=True,text=True,timeout=30)
    assert r.returncode==1 and 'AssertionError: budget enforcement removed' in r.stderr
    print('MUTATION_DETECTED: pre-signature admission budget removal (assertion failure)')


def test_saturated_path_skips_signature_and_request_digest(fixture):
    f=fixture;flood(f,200)
    with patch.object(f.runtime,'signed_body',side_effect=AssertionError('signature work')):
        with patch('reference_profiles.protected_destination.digest',side_effect=AssertionError('digest work')):
            assert f.runtime.apply(invalid(999))['reason']=='INGRESS_SATURATED'


def test_retention_limit_removal_negative_control(fixture):
    f=fixture
    with patch('reference_profiles.protected_destination.UNAUTHENTICATED_DETAIL_LIMIT',100000):
        flood(f,100)
        with pytest.raises(AssertionError):
            assert state(f)['details'] <= 64
