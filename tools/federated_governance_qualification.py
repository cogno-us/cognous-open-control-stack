#!/usr/bin/env python3
"""Exact-source qualification of the optional federated governance profile."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'tools')]
SOURCES=['reference_profiles/assurance_runtime.py','reference_profiles/federated_governance.py','reference_profiles/trust_evidence.py',
         'tests/test_federated_governance.py','tools/federated_governance_mutations.py','tools/federated_governance_qualification.py',
         'tools/requirements-federated-governance.txt','.github/workflows/federated-governance.yml',
         'docs/workstreams/federated-governance-addendum.md','component-lock.json']


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--results-dir',type=Path,required=True);a=parser.parse_args()
    output=a.results_dir.resolve();output.mkdir(parents=True,exist_ok=True)
    r=subprocess.run([sys.executable,'-m','pytest','-q','tests/test_federated_governance.py','tests/test_integrated_assurance.py','--junitxml='+str(output/'tests.xml')],cwd=ROOT,capture_output=True,text=True,timeout=120)
    (output/'tests.log').write_text(r.stdout+r.stderr)
    cases=ET.parse(output/'tests.xml').getroot().findall('.//testcase');passed={x.attrib['name'] for x in cases if not any(x.find(k) is not None for k in ('failure','error','skipped'))}
    m=subprocess.run([sys.executable,'tools/federated_governance_mutations.py'],cwd=ROOT,capture_output=True,text=True,timeout=120)
    (output/'mutations.log').write_text(m.stdout+m.stderr)
    from federated_governance_mutations import CASES
    groups={identity:{'acceptance_test_passed':test in passed,'control_removal_detected':('DETECTED: '+identity) in m.stdout.splitlines()} for identity,_,_,_,test in CASES}
    from test_federated_governance import GovernanceTests
    fixture=GovernanceTests();fixture.setUp()
    try:
        fixture.ready();allowed=fixture.ok('agent','execute',proposal='proposal')
        fixture.ready('blocked',effect='blocked-effect');fixture.consent(enabled=False)
        blocked=fixture.deny('agent','execute','CONSENT_UNAVAILABLE',proposal='blocked')
        assert fixture.effects()==1
        env,policy,evidence=fixture.envelope();assessment=fixture.assess(env,policy,evidence)
        assert assessment['verdict']=='VALID' and assessment['authorizing'] is False
        replay={'allowed':allowed,'blocked':blocked,'effect_count':fixture.effects(),'journal':fixture.runtime.journal(),
                'envelope':env,'consumer_policy':policy,'public_registry':fixture.registry,'evidence':evidence,'assessment':assessment,
                'independent_administration_verified':False,'production_qualified':False}
        (output/'replay.json').write_text(json.dumps(replay,sort_keys=True,indent=2)+'\n')
    finally:fixture.doCleanups()
    changes=subprocess.check_output(['git','status','--porcelain','--',*SOURCES],cwd=ROOT,text=True).splitlines()
    qualified=(r.returncode==0 and m.returncode==0 and len(cases)==92 and len(passed)==92 and not changes and all(all(g.values()) for g in groups.values()))
    report={'local_qualified':qualified,'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'testcase_elements':len(cases),'groups':groups,'source_changes':changes,'python':platform.python_version(),
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'replay_sha256':hashlib.sha256((output/'replay.json').read_bytes()).hexdigest(),
            'reference_release_authorized':False,'production_deployment_authorized':False,'operational_trust':'HOLD / NOT ESTABLISHED'}
    (output/'qualification.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report,indent=2))
    return 0 if qualified else 2
if __name__=='__main__':raise SystemExit(main())
