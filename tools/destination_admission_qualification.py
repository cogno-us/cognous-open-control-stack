#!/usr/bin/env python3
"""Exact-source qualification; independent testcase counts, no release authority."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SOURCES=['reference_profiles/protected_destination.py','reference_profiles/protocol_evaluation.py','tests/test_protected_destination.py','tests/test_protocol_evaluation.py','tools/destination_admission_qualification.py','.github/workflows/destination-admission.yml','docs/workstreams/destination-admission-addendum.md','reference_profiles/operational_state.py','reference_profiles/assurance_runtime.py','reference_profiles/federated_governance.py','reference_profiles/trust_evidence.py','tests/test_operational_state.py','tests/test_federated_governance.py','tests/test_integrated_assurance.py','tools/destination_admission_mutations.py','tools/operational_state_qualification.py','tools/requirements-federated-governance.txt','.github/workflows/operational-state.yml','docs/workstreams/operational-state-addendum.md','component-lock.json']


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--results-dir',type=Path,required=True);a=parser.parse_args()
    output=a.results_dir.resolve();output.mkdir(parents=True,exist_ok=True)
    r=subprocess.run([sys.executable,'-m','pytest','-q','tests/test_protected_destination.py','tests/test_protocol_evaluation.py','tests/test_operational_state.py','tests/test_federated_governance.py','tests/test_integrated_assurance.py','--junitxml='+str(output/'tests.xml')],cwd=ROOT,capture_output=True,text=True,timeout=120)
    (output/'tests.log').write_text(r.stdout+r.stderr)
    cases=ET.parse(output/'tests.xml').getroot().findall('.//testcase');passed=[x for x in cases if not any(x.find(k) is not None for k in ('failure','error','skipped'))]
    m=subprocess.run([sys.executable,'tools/destination_admission_mutations.py'],cwd=ROOT,capture_output=True,text=True,timeout=120)
    (output/'mutations.log').write_text(m.stdout+m.stderr)
    mutations=[line for line in m.stdout.splitlines() if line.startswith('DETECTED: J')]
    changes=subprocess.check_output(['git','status','--porcelain','--',*SOURCES],cwd=ROOT,text=True).splitlines()
    qualified=r.returncode==0 and m.returncode==0 and len(cases)==167 and len(passed)==167 and len(set(mutations))==6 and not changes
    report={'local_qualified':qualified,'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'python':platform.python_version(),'testcase_elements':len(cases),'passing_testcase_elements':len(passed),'mutations':mutations,'source_changes':changes,'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},'functional':'bounded synthetic contract verified' if qualified else 'not established','security':'independent acceptance not established','cross_host_restore_qualified':False,'production_credential_custody_established':False,'protocol_effectiveness_measured':False,'reference_release_authorized':False,'production_deployment_authorized':False,'operational_trust':'HOLD / NOT ESTABLISHED'}
    (output/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    return 0 if qualified else 2
if __name__=='__main__':raise SystemExit(main())
