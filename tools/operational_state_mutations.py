#!/usr/bin/env python3
"""Each removed control must produce an assertion failure, not an import error."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
CASES=(('OPS01', 'operational_state.py', "require(not any(b['status'] == 'stop' for b in blockers.values()), 'UNRESOLVED_BLOCKER')", "require(True, 'MUTATED')", 'test_blocker_after_review_blocks_effect'), ('OPS02', 'operational_state.py', "require(a['state'] == self.blocker_state(c, a['run']), 'HANDOFF_STATE_LOSS')", "require(True, 'MUTATED')", 'test_missing_handoff_state_rejected'), ('OPS03', 'operational_state.py', "require('deny' not in contract['decisions'], 'POLICY_DENY')", "require(True, 'MUTATED')", 'test_policy_deny_overrides_allow'), ('OPS04', 'operational_state.py', "require(set(contract['completed_obligations']) == set(contract['required_obligations']), 'POLICY_OBLIGATION_PENDING')", "require(True, 'MUTATED')", 'test_pending_obligation_blocks'), ('OPS05', 'operational_state.py', "require(s['crs'] == s['expected_crs'] and s['resolution'] <= s['max_resolution'] and s['uncertainty'] <= s['max_uncertainty'], 'SPATIAL_UNSUPPORTED')", "require(True, 'MUTATED')", 'test_spatial_crs_mismatch'), ('OPS06', 'operational_state.py', "require(abs(v['positive'] * 1000000 - v['expected_ppm'] * v['total']) <= p['max_gap_ppm'] * v['total'], 'POPULATION_ALARM')", "require(True, 'MUTATED')", 'test_population_alarm_blocks_effect'), ('OPS07', 'operational_state.py', "require(self.get(c, 'acquisition', a['item'])['at'] <= a['checkpoint'] <= self.now(), 'LINEAGE_TIME')", "require(True, 'MUTATED')", 'test_lineage_pre_acquisition_rejected'))

def main():
    for identity,filename,before,after,test in CASES:
        with tempfile.TemporaryDirectory(prefix='federated-mutation-') as tmp:
            root=Path(tmp);(root/'reference_profiles').mkdir()
            shutil.copy(ROOT/'reference_profiles/bounded_json.py',root/'reference_profiles/bounded_json.py')
            for f in ('assurance_runtime.py','federated_governance.py','trust_evidence.py','operational_state.py'):
                text=(ROOT/'reference_profiles'/f).read_text()
                if f==filename:
                    if text.count(before)!=1:raise RuntimeError('mutation target changed '+identity)
                    text=text.replace(before,after)
                (root/'reference_profiles'/f).write_text(text)
            shutil.copy(ROOT/'tests/test_federated_governance.py',root/'test_federated_governance.py')
            shutil.copy(ROOT/'tests/test_operational_state.py',root/'test_operational_state.py')
            r=subprocess.run([sys.executable,'-m','unittest','test_operational_state.OperationalTests.'+test],cwd=root,capture_output=True,text=True,timeout=30)
            if r.returncode!=1 or 'FAIL:' not in r.stderr or 'ERROR:' in r.stderr:
                print(r.stdout,r.stderr);raise RuntimeError('control removal not detected '+identity)
            print('DETECTED: '+identity)
    return 0
if __name__=='__main__':raise SystemExit(main())
