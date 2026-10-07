"""Gate-unit fixtures are synthetic reports, not executed runtime evidence."""
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import pytest
from tools.v1_release_evidence import BATCHES, COMPONENTS, DEMO_PROFILES, DEPENDENT, aggregate, inventory, record, sha

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'component-lock.json'
REVISION = 'a' * 40


def write(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value))


@pytest.fixture
def packet(tmp_path):
    lock = json.loads(LOCK.read_text())
    for batch,(module,count,demo) in BATCHES.items():
        root = tmp_path / batch
        root.mkdir()
        suite = ET.Element('testsuite')
        for n in range(count): ET.SubElement(suite,'testcase',classname='tests.'+module,name='synthetic-case-'+str(n))
        ET.ElementTree(suite).write(root / 'tests.xml')
        write(root / 'environment.json',dict(schema_version='1.0.0',purpose='local-reference-prerequisites',
            component_lock_sha256=sha(LOCK),reference_prerequisites_observed=True,deployment_qualified=False,authorizing=False,
            checks=[dict(id=x,status='observed') for x in ('linux','python','wal','competing_writer_excluded','rollback_preserved')],
            environment=dict(os='Linux',python='3.11.16',sqlite='fixture-only')))
        if demo: write(root / batch / demo,dict(profile=DEMO_PROFILES[batch],qualified=True,production_ready=False))
        if batch in DEPENDENT:
            write(root / batch / 'provenance.json',dict(tested_revisions={n:lock['components'][n].get('sha') or lock['components'][n]['accepted_sha'] for n in COMPONENTS},
                component_lock_sha256=sha(LOCK),returncode=0))
        record(root,batch,REVISION,LOCK)
    return tmp_path


def rehash(root):
    path = root / 'batch-report.json'
    value = json.loads(path.read_text())
    value['artifacts'] = inventory(root)
    write(path,value)


def test_complete_packet_is_non_authorizing(packet):
    result = aggregate(packet,REVISION,LOCK)
    assert result['valid'] and result['scheduled_batches']==7 and result['scheduled_tests']==67
    assert result['verified_batches']==7
    assert result['authorizing'] is result['production_ready'] is result['full_default_release_qualified'] is False


@pytest.mark.parametrize('mutation', ['missing-batch','duplicate-batch','revision','lock','artifact','extra-artifact','unreported-directory',
                                      'skip','failure','error','missing-test','duplicate-test','foreign-test','totals',
                                      'environment','demo-profile','pins'])
def test_gate_rejects_incomplete_or_inconsistent_evidence(packet, mutation):
    root = packet / 'context-action'
    p = root / 'batch-report.json'
    report = json.loads(p.read_text())
    if mutation == 'missing-batch': shutil.rmtree(root)
    elif mutation == 'duplicate-batch': report['batch']='notification'; write(p,report)
    elif mutation == 'revision': report['source_revision']='b'*40; write(p,report)
    elif mutation == 'lock': report['component_lock_sha256']='b'*64; write(p,report)
    elif mutation == 'artifact': (root / 'tests.xml').write_text('<testsuite/>')
    elif mutation == 'extra-artifact': (root / 'unreported.txt').write_text('extra')
    elif mutation == 'unreported-directory': (packet / 'unreported').mkdir()
    elif mutation in ('skip','failure','error','missing-test','duplicate-test','foreign-test'):
        xml=ET.parse(root / 'tests.xml'); suite=xml.getroot(); cases=list(suite)
        if mutation == 'missing-test': suite.remove(cases[0])
        elif mutation == 'duplicate-test': cases[1].set('name',cases[0].get('name'))
        elif mutation == 'foreign-test': cases[0].set('classname','tests.unrelated')
        else: ET.SubElement(cases[0], 'skipped' if mutation=='skip' else mutation)
        xml.write(root / 'tests.xml'); rehash(root)  # semantic failure, not stale hash
    elif mutation == 'totals': report['results']['passed']=999; write(p,report)
    elif mutation == 'environment':
        path=root / 'environment.json'; value=json.loads(path.read_text()); value['checks'][0]['status']='unverified'; write(path,value); rehash(root)
    elif mutation == 'demo-profile':
        path=root / 'context-action/result.json'; value=json.loads(path.read_text()); value['profile']='other'; write(path,value); rehash(root)
    elif mutation == 'pins':
        path=root / 'context-action/provenance.json'; value=json.loads(path.read_text()); value['tested_revisions']['control_plane']='c'*40; write(path,value); rehash(root)
    result=aggregate(packet,REVISION,LOCK)
    assert not result['valid'], (mutation,result)
    assert result['scheduled_batches']==7 and result['scheduled_tests']==67 and result['errors']


def test_artifact_symlink_rejected(packet, tmp_path):
    root=packet / 'context-action'
    (root / 'linked').symlink_to(LOCK)
    assert not aggregate(packet,REVISION,LOCK)['valid']

@pytest.mark.parametrize('status',['failure','cancelled','skipped'])
def test_scheduler_failure_cannot_be_hidden_by_good_artifacts(packet,status):
    result=aggregate(packet,REVISION,LOCK,jobs_status=status)
    assert not result['valid'] and result['jobs_status']==status
