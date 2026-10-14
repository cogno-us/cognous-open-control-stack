#!/usr/bin/env python3
"""Nine isolated control-removal probes; tests must detect each missing control."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
CASES=(
 ('EGA01','require(observed==env[\'manifest\'],\'ENVIRONMENT_MISMATCH\')',"require(True,'ENVIRONMENT_MISMATCH')",'test_environment_drift_and_expired_lease_block_effect'),
 ('EGA02',"if not set(item['labels'])<=set(env['manifest']['sinks'][sink]):",'if False:','test_allowed_public_sink_does_not_allow_secret_payload'),
 ('EGA03',"require(g['status']=='active','GRANT_REVOKED')","require(True,'GRANT_REVOKED')",'test_parent_revocation_refuses_child_and_names_revision'),
 ('EGA04'," and regressions<=oracle['max_regressions']",'','test_unsafe_regression_and_evaluation_budget_are_enforced'),
 ('EGA05',"require(type(request['mac']) is str and hmac.compare_digest(request['mac'],hmac.new(key,canonical(body).encode(),hashlib.sha256).hexdigest()),'BAD_SIGNATURE')","require(True,'BAD_SIGNATURE')",'test_forged_signed_execution_cannot_create_effect'),
 ('EGA06','self.custody(c,env)','pass # removed custody gate','test_missing_or_stale_custody_blocks_effect'),
 ('EGA07',"require(pending<reviewer['capacity'],'REVIEW_CAPACITY_EXHAUSTED')","require(True,'REVIEW_CAPACITY_EXHAUSTED')",'test_review_capacity_unavailable_and_deadline'),
 ('EGA08',"require(run['state']=='active','RUN_STOPPED')","require(True,'RUN_STOPPED')",'test_stopped_run_cannot_receive_fresh_grant'),
 ('EGA09',"if self.now()<obligation['due_at']: reason='OBLIGATION_NOT_DUE'","if False: reason='OBLIGATION_NOT_DUE'",'test_recourse_distinguishes_compliant_violated_unevaluable_and_evidence_failure'),
)


def main():
    for identity,before,after,test in CASES:
        with tempfile.TemporaryDirectory(prefix='integrated-assurance-mutation-') as tmp:
            root=Path(tmp); (root/'reference_profiles').mkdir()
            source=ROOT/'reference_profiles/assurance_runtime.py'; text=source.read_text()
            if text.count(before)!=1: raise RuntimeError('changed mutation target '+identity)
            (root/'reference_profiles/assurance_runtime.py').write_text(text.replace(before,after))
            shutil.copy(ROOT/'tests/test_integrated_assurance.py',root/'test_integrated_assurance.py')
            result=subprocess.run([sys.executable,'-m','unittest','test_integrated_assurance.IntegratedAssuranceTests.'+test],cwd=root,capture_output=True,text=True,timeout=30)
            if result.returncode!=1 or 'FAIL:' not in result.stderr or 'ERROR:' in result.stderr:
                print(result.stdout,result.stderr); raise RuntimeError('control removal not detected '+identity)
            print('DETECTED: '+identity)
    return 0


if __name__=='__main__': raise SystemExit(main())
