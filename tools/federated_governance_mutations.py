#!/usr/bin/env python3
"""Each removed control must produce an assertion failure, not an import error."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
CASES=(
 ('FGA01','trust_evidence.py',"if commitment(resolved)!=requirement['evidence_digest']:","if False:",'test_evidence_consumer_detects_missing_and_contradiction'),
 ('FGA02','federated_governance.py',"for domain,issuer in cfg['anchors'].items():","for domain,issuer in []:",'test_change_requires_every_independent_anchor'),
 ('FGA03','federated_governance.py',"require(f['status']=='active','AUTHORITY_CONFLICT_OR_SUPERSEDED')","require(True,'AUTHORITY_CONFLICT_OR_SUPERSEDED')",'test_conflicting_authority_cannot_establish_relation'),
 ('FGA04','federated_governance.py',"require(len(signers)==len(set(signers)) and len(signers)>=cfg['restart_quorum'],'RESTART_QUORUM')","require(True,'RESTART_QUORUM')",'test_single_or_duplicate_signer_cannot_restart'),
 ('FGA05','federated_governance.py',"require(current['head']==candidate['predecessor'],'PREDECESSOR_STALE')","require(True,'PREDECESSOR_STALE')",'test_competing_successors_and_reopen_preserve_one_head'),
 ('FGA06','federated_governance.py',"require(p['integrity']=='trusted' or a['integrity']=='untrusted','INTEGRITY_PROMOTION')","require(True,'INTEGRITY_PROMOTION')",'test_untrusted_perception_cannot_be_promoted'),
 ('FGA07','federated_governance.py',"require(a['risk']<=m['risk_ceiling'] and a['readiness']>=a['threshold'],'ACTIVATION_NOT_ADMITTED')","require(True,'ACTIVATION_NOT_ADMITTED')",'test_risk_and_readiness_do_not_mint_authority'),
 ('FGA08','trust_evidence.py',"complete=observed==categories","complete=True",'test_work_accounting_keeps_missing_categories_and_zero_denominator'),
)

def main():
    for identity,filename,before,after,test in CASES:
        with tempfile.TemporaryDirectory(prefix='federated-mutation-') as tmp:
            root=Path(tmp);(root/'reference_profiles').mkdir()
            for f in ('assurance_runtime.py','federated_governance.py','trust_evidence.py'):
                text=(ROOT/'reference_profiles'/f).read_text()
                if f==filename:
                    if text.count(before)!=1:raise RuntimeError('mutation target changed '+identity)
                    text=text.replace(before,after)
                (root/'reference_profiles'/f).write_text(text)
            shutil.copy(ROOT/'tests/test_federated_governance.py',root/'test_federated_governance.py')
            r=subprocess.run([sys.executable,'-m','unittest','test_federated_governance.GovernanceTests.'+test],cwd=root,capture_output=True,text=True,timeout=30)
            if r.returncode!=1 or 'FAIL:' not in r.stderr or 'ERROR:' in r.stderr:
                print(r.stdout,r.stderr);raise RuntimeError('control removal not detected '+identity)
            print('DETECTED: '+identity)
    return 0
if __name__=='__main__':raise SystemExit(main())
