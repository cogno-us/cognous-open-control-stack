#!/usr/bin/env python3
"""Qualify all nine local assurance groups and retain replayable synthetic evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]

REQUIRED={
 'EGA01':['test_unregistered_route_and_arbitrary_effect_surface_are_blocked','test_environment_drift_and_expired_lease_block_effect'],
 'EGA02':['test_allowed_public_sink_does_not_allow_secret_payload','test_untrusted_labels_and_derived_label_drop_are_rejected','test_explicit_exact_declassification_and_scope','test_payload_cannot_be_replaced_after_review'],
 'EGA03':['test_attenuated_child_uses_parent_budget','test_parent_revocation_refuses_child_and_names_revision','test_two_processes_cannot_spend_last_ancestor_budget_twice','test_revoke_before_effect_and_effect_before_revoke_have_distinct_results'],
 'EGA04':['test_independent_current_oracle_change_admission_and_activation','test_unsafe_regression_and_evaluation_budget_are_enforced','test_new_oracle_invalidates_old_admission_and_change_invalidates_approval','test_new_routes_without_oracle_coverage_cannot_be_admitted','test_rollback_uses_current_oracle_and_never_revives_grants_or_approvals'],
 'EGA05':['test_forged_signed_execution_cannot_create_effect','test_key_rotation_persists_and_old_key_cannot_act','test_same_model_instances_cannot_exchange_authority'],
 'EGA06':['test_missing_or_stale_custody_blocks_effect','test_event_lag_gate_resumes_only_after_checkpoint','test_witness_rejects_gap_fork_and_truncation_across_reopen','test_crash_before_commit_rolls_back_effect_and_budget','test_crash_after_commit_is_observed_without_reexecution'],
 'EGA07':['test_review_capacity_unavailable_and_deadline','test_same_principal_cannot_review_own_request_even_with_both_roles','test_challenge_blocks_approval_and_late_challenge_blocks_execution'],
 'EGA08':['test_stop_covers_children_blocks_new_runs_and_preserves_prior_effect','test_stop_holds_writer_boundary_before_waiting_execution','test_stop_remains_available_during_observer_outage','test_restart_requires_review_and_does_not_restore_grants','test_old_restart_review_cannot_override_newer_same_time_stop','test_stall_and_step_budget_produce_safe_refusal'],
 'EGA09':['test_recourse_distinguishes_compliant_violated_unevaluable_and_evidence_failure','test_remedy_packet_cannot_create_effect_or_restore_authority','test_appeal_preserves_history_and_blocks_existing_corrective_grant'],
}
SOURCES=['reference_profiles/assurance_runtime.py','tests/test_integrated_assurance.py',
 'tools/integrated_assurance_mutations.py','tools/integrated_assurance_qualification.py',
 '.github/workflows/integrated-assurance.yml','docs/workstreams/integrated-assurance-contract.md','component-lock.json']


def representative_evidence():
    from test_integrated_assurance import IntegratedAssuranceTests
    fixture=IntegratedAssuranceTests(); fixture.setUp()
    try:
        fixture.ready(); allowed=fixture.ok('agent','execute',proposal='proposal-1')
        fixture.ready('proposal-2',proposal=fixture.proposal(effect='effect-2'))
        fixture.ok('ops','revoke',grant='root-grant')
        blocked=fixture.denied('agent','execute','GRANT_REVOKED',proposal='proposal-2')
        effects=fixture.effects()
        assert len(effects)==1 and effects[0]['id']=='effect-1'
        journal=fixture.runtime.journal()
        assert journal['events'][-1]['body']['grant_chain']==[{'id':'root-grant','revision':2,'status':'revoked'}]
        receipt=fixture.witness.receive(journal,now=fixture.now)
        return {'profile':'integrated-local-assurance/1','allowed':allowed,'blocked':blocked,
                'destination':[{'id':r['id'],'run':r['run'],'payload_sha256':hashlib.sha256(r['payload'].encode()).hexdigest(),'evidence':json.loads(r['evidence'])} for r in effects],
                'journal':journal,'witness_receipt':receipt,'independent_custody':False,'production_qualified':False}
    finally: fixture.doCleanups()


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--results-dir',type=Path,required=True)
    args=parser.parse_args(); output=args.results_dir.resolve(); output.mkdir(parents=True,exist_ok=True)
    tests=subprocess.run([sys.executable,'-m','pytest','-q','tests/test_integrated_assurance.py','--junitxml='+str(output/'tests.xml')],cwd=ROOT,capture_output=True,text=True,timeout=120)
    (output/'tests.log').write_text(tests.stdout+tests.stderr)
    cases=ET.parse(output/'tests.xml').getroot().findall('.//testcase')
    passed={case.attrib['name'] for case in cases if not any(case.find(k) is not None for k in ('failure','error','skipped'))}
    mutations=subprocess.run([sys.executable,'tools/integrated_assurance_mutations.py'],cwd=ROOT,capture_output=True,text=True,timeout=120)
    (output/'mutations.log').write_text(mutations.stdout+mutations.stderr)
    detected={line.removeprefix('DETECTED: ') for line in mutations.stdout.splitlines() if line.startswith('DETECTED: ')}
    evidence=representative_evidence(); raw=json.dumps(evidence,sort_keys=True,indent=2).encode(); (output/'scenario.json').write_bytes(raw)
    changed=subprocess.check_output(['git','status','--porcelain','--',*SOURCES],cwd=ROOT,text=True).splitlines()
    coverage={key:{'required_cases':names,'all_passed':set(names)<=passed,'control_removal_detected':key in detected} for key,names in REQUIRED.items()}
    report={'contract':'integrated-assurance-qualification/1','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'python':platform.python_version(),'platform':platform.system(),'source_changes':changed,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'testcase_elements':len(cases),'passing_testcase_elements':len(passed),'coverage':coverage,
            'scenario_sha256':hashlib.sha256(raw).hexdigest(),'mutation_exit_code':mutations.returncode,
            'local_qualified':tests.returncode==0 and mutations.returncode==0 and len(cases)==51 and len(passed)==51 and not changed and all(c['all_passed'] and c['control_removal_detected'] for c in coverage.values()),
            'reference_release_authorized':False,'production_deployment_authorized':False,'independent_custody_verified':False,'operational_trust':'HOLD / NOT ESTABLISHED'}
    (output/'qualification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'local_qualified':report['local_qualified'],'testcase_elements':len(cases),'groups':coverage,'source_changes':changed},indent=2))
    return 0 if report['local_qualified'] else 2


if __name__=='__main__': raise SystemExit(main())
