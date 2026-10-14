#!/usr/bin/env python3
"""Each removed control must produce an assertion failure, not an import error."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
CASES=(('J1', 'protected_destination.py', "require(g['generation']==a['generation']==fence,'AUTHORITY_STORE_BEHIND_FENCE')", 'pass', 'test_restore_resurrects_revoked_epoch_other_process_refused'), ('J2', 'protected_destination.py', "if after-before: raise Denied('SOFT_PIN_SCOPE_WIDENED')", 'pass', 'test_soft_pin_rotation_superset_holds'), ('J3', 'protected_destination.py', "require(a['verifier_status'] is not None,'VERIFIER_UNREACHABLE')", 'pass', 'test_verifier_unreachable_destination_refuses'), ('J4', 'protected_destination.py', "require(g['modes'].get(kind,'hard')=='soft','HARD_PIN_CHANGED')", 'pass', 'test_hard_pin_default_rotation_holds'), ('J5', 'protected_destination.py', "try: return verify(record,self.registry,at=record['body']['at'],now=self.now())", "try: return record['body']", 'test_agent_computed_claim_refused'), ('J6', 'protocol_evaluation.py', "require(digest(body)==locked['commitment'] and locked['registration']==registration['commitment'],'SCORES_CHANGED')", "require(True,'SCORES_CHANGED')", 'test_scores_locked_before_unblinding'))

def main():
    for identity,filename,before,after,test in CASES:
        with tempfile.TemporaryDirectory(prefix='federated-mutation-') as tmp:
            root=Path(tmp);(root/'reference_profiles').mkdir()
            for f in ('assurance_runtime.py','federated_governance.py','trust_evidence.py','operational_state.py','protected_destination.py','protocol_evaluation.py'):
                text=(ROOT/'reference_profiles'/f).read_text()
                if f==filename:
                    if text.count(before)!=1:raise RuntimeError('mutation target changed '+identity)
                    text=text.replace(before,after)
                (root/'reference_profiles'/f).write_text(text)
            shutil.copy(ROOT/'tests/test_federated_governance.py',root/'test_federated_governance.py')
            shutil.copy(ROOT/'tests/test_protected_destination.py',root/'test_protected_destination.py')
            shutil.copy(ROOT/'tests/test_protocol_evaluation.py',root/'test_protocol_evaluation.py')
            test_class='test_protocol_evaluation.EvaluationTests.' if filename=='protocol_evaluation.py' else 'test_protected_destination.DestinationTests.'
            r=subprocess.run([sys.executable,'-m','unittest',test_class+test],cwd=root,capture_output=True,text=True,timeout=30)
            if r.returncode!=1 or 'FAIL:' not in r.stderr or 'ERROR:' in r.stderr:
                print(r.stdout,r.stderr);raise RuntimeError('control removal not detected '+identity)
            print('DETECTED: '+identity)
    return 0
if __name__=='__main__':raise SystemExit(main())
