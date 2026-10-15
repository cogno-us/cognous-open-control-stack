"""S1 actual-component integration gate; incompatibilities fail, never xfail.
Only dated fixture clocks and declared faults are injected; no adapter patches.
"""
import dataclasses
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import pytest
from tools.remediation_candidate import PROFILE, dump, verify

WORK=Path(os.environ.get('S1_WORK','/nonexistent-s1-work'))
OUT=Path(os.environ.get('S1_RESULTS','/nonexistent-s1-output'))
pytestmark=pytest.mark.skipif(not os.environ.get('S1_WORK'),reason='Opt-in S1 exact-component harness; invoke tools/remediation_candidate.py')
NOW=datetime(2026,8,8,1,tzinfo=timezone.utc)
CASES={'denied-destination':'target_out_of_scope','schema-mismatch':'missing_required_payload_field',
       'stale-required-context':'context_unknown_requires_hold','principal-self-approval':'approval_independence_violation',
       'unsupported-delegation':'delegation_profile_unsupported'}


def value(x):
    if hasattr(x,'model_dump'): return x.model_dump(mode='json',exclude_none=False)
    if dataclasses.is_dataclass(x): return dataclasses.asdict(x)
    return x


def rows(d,table='effects'):
    with sqlite3.connect(d.path) as c:
        c.row_factory=sqlite3.Row
        return [dict(r) for r in c.execute(f'SELECT * FROM {table} ORDER BY rowid')]


def save(name,artifacts,checks):
    folder=OUT/name;folder.mkdir(exist_ok=True)
    for key,artifact in artifacts.items(): dump(folder/(key+'.json'),value(artifact))
    normalized={k:{'expected':v[1],'observed':v[0],'passed':v[0]==v[1]} for k,v in checks.items()}
    dump(folder/'checks.json',normalized)
    return normalized


def require(checks):
    assert all(v['passed'] for v in checks.values()),{k:v for k,v in checks.items() if not v['passed']}


@pytest.fixture(autouse=True)
def exact_components(monkeypatch):
    verify(WORK,json.loads(PROFILE.read_text()))
    import agent_control_plane.bounded as cp
    monkeypatch.setattr(cp,'_now',lambda:NOW)


@pytest.fixture
def tmp_path(request):
    # Retain the actual destination, exchange and CP stores as artifacts.
    folder=OUT/'state'/re.sub(r'[^a-zA-Z0-9_-]','_',request.node.name)
    folder.mkdir(parents=True)
    return folder


def setup(folder):
    from experiments.odex_gax_imx_reference import gax_ref_runtime as gax
    from experiments.odex_gax_imx_reference.synthetic_fixture import build_synthetic_resolver,synthetic_observation_policy
    rt=gax.load_executor_runtime();cp=rt['cp']
    manifest=json.loads((WORK/'action_manifest/examples/refund_integration_v1_1.manifest.json').read_text())
    seed=json.loads((WORK/'replay_bundle/examples/bounded_success_reconstruction_v0_2.json').read_text())
    p=gax.runtime_proposal_model(seed);r=build_synthetic_resolver(p,now=NOW)
    d=rt['DurableRefundDestination'](folder/'destination')
    f=cp.BoundedAuthorizationWorkflow(manifest=manifest,resolver=r,destination=d,
        records=cp.BoundedRecordStore(folder/'control-plane.json',p.run_id or 's1'),observation_policy=synthetic_observation_policy())
    return rt,p,r,d,f,seed


def authorize(rt,p,r,f):
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_refund_policy
    decision=f.decide(p,now=NOW)
    assert decision.result=='authorized',decision.reasons
    context=r.contexts[p.authority_context_ref];b=decision.binding;v=value(p)
    v.update(institution_id=context['institution']['institution_id'],authority_domain=context['institution']['authority_domain'],
        authority_context_id=p.authority_context_ref,proposal_commitment=b.proposal_commitment,grant_id=b.grant_id,
        grant_revision=b.grant_revision,effective_max_effects=b.effective_max_effects,requested_permissions=tuple(p.requested_permissions))
    op=rt['ExecutionOperation'](**{x.name:v[x.name] for x in dataclasses.fields(rt['ExecutionOperation']) if x.name in v})
    env=rt['ExecutionEnvelope'](version='0.2.0',decision_id=decision.decision_id,effect_id=decision.effect_id,operation=op)
    executor=rt['PinnedControlPlaneExecutor'](workflow=f,destination=f.destination,policy=synthetic_refund_policy(op),observation_clock=lambda:NOW)
    return decision,env,executor


def mutate(case,p,r):
    from agent_control_plane.bounded import commitment
    ctx=r.contexts[p.authority_context_ref]
    if case=='denied-destination': p.target='urn:cognous:synthetic-denied:account'
    elif case=='schema-mismatch':
        del p.payload['customer_id'];p.payload_commitment=commitment(p.payload)
    elif case=='stale-required-context':
        ctx['requirement']['evidence'][0]['kind']='context';next(iter(r.evidence.values())).state='stale'
    elif case=='principal-self-approval': next(iter(r.approvals.values())).approver=p.principal
    elif case=='unsupported-delegation': ctx['grant']['delegation']['parent_grant_id']='urn:cognous:synthetic:parent'
    else: raise AssertionError(case)


def import_consumers(f,p,producer=None):
    """Pass the actual revision; never substitute an accepted historical SHA."""
    from agent_replay_bundle.importers import import_bounded_workflow
    from agent_governance_evidence_pack.importer import build_evidence_pack_from_artifacts
    from odes import export_cognous_stack_package
    result={'source':value(f.records.load()),'executor_export':producer,'replay':None,'odes':None,'evidence_pack':None,'errors':{}}
    from agent_control_plane.bounded import EffectTimeRefusal,ResolutionInput,RefusalInputVersion,OperationHorizon
    result['interface_inventory']={
        'EffectTimeRefusal':list(EffectTimeRefusal.model_fields),
        'ResolutionInput':list(ResolutionInput.model_fields),
        'RefusalInputVersion':list(RefusalInputVersion.model_fields),
        'OperationHorizon':list(OperationHorizon.model_fields),
        'source_top_level_fields':list(result['source']),
        'source_decision_fields':sorted({k for d in result['source']['decisions'] for k in d}),
        'source_refusal_fields':sorted({k for d in result['source']['refusals'] for k in d}),
        'executor_control_plane_evidence_fields':list((producer or {}).get('control_plane_evidence',{})),
    }

    revision=json.loads(PROFILE.read_text())['components']['control_plane']['sha']
    try: result['replay']=value(import_bounded_workflow(result['source'],proposal=value(p),moltbot_export=producer,control_plane_revision=revision))
    except ValueError as e: result['errors']['replay']=str(e)
    if result['replay'] is not None:
        for name,fn in [('odes',export_cognous_stack_package),('evidence_pack',build_evidence_pack_from_artifacts)]:
            try: result[name]=value(fn(f.manifest,result['replay']))
            except ValueError as e: result['errors'][name]=str(e)
    else:
        result['errors'].update(odes='not invoked: no exact-revision Replay record',evidence_pack='not invoked: no exact-revision Replay record')
    return result


@pytest.mark.parametrize('case,reason',CASES.items())
def test_decision_refusal_zero_effect_and_actual_bindings(tmp_path,case,reason):
    rt,p,r,d,f,_=setup(tmp_path);mutate(case,p,r);decision=f.decide(p,now=NOW);record=value(f.records.load())
    with pytest.raises(PermissionError): f.execute(p,decision,adapter_id=p.adapter_id,now=NOW)
    kinds=[x['input_type'] for x in value(decision)['resolution_inputs']]
    require(save('decision-'+case,{'proposal':p,'decision':decision,'control-plane':record,'destination':rows(d)}, {
        'held':(decision.result,'hold'),'typed_reason_retained':(reason in decision.reasons,True),'effects':(len(rows(d)),0),
        'attempts':(len(record['attempts']),0),'policy_binding':('policy' in kinds,True),'grant_binding':('grant' in kinds,True),
        'evidence_binding':('evidence' in kinds,True),'no_authorization_binding':(decision.binding,None),
        'durable_decision_equal':(record['decisions'][0],value(decision))}))


@pytest.mark.parametrize('case,reason',[('revoke','grant_not_active'),('withdraw','approval_not_active'),('policy','policy_version_changed'),('evidence','required_evidence_not_current')])
def test_effect_refusal_propagates_executor_and_consumers(tmp_path,case,reason):
    rt,p,r,d,f,_=setup(tmp_path);decision,env,executor=authorize(rt,p,r,f)
    if case=='revoke': next(iter(r.statuses.values())).status='revoked'
    elif case=='withdraw': next(iter(r.approvals.values())).status='revoked'
    elif case=='policy': next(iter(r.policies.values())).version='changed'
    else: next(iter(r.evidence.values())).state='stale'
    result=executor.execute(envelope=env,proposal=p,decision=decision,now=NOW)
    producer=rt['export_execution_artifacts'](env,result,d,repository_revision=json.loads(PROFILE.read_text())['components']['moltbot_safe']['sha'])
    consumers=import_consumers(f,p,producer);record=value(f.records.load());refusal=record['refusals'][0]
    require(save('effect-'+case,{'proposal':p,'envelope':env,'execution':result,'control-plane':record,'executor-export':producer,'consumers':consumers,'destination':rows(d)}, {
        'denied':(result.status,'denied'),'effects':(len(rows(d)),0),'attempted':(result.attempted,False),
        'source_reason':(reason in refusal['reasons'],True),'source_lineage':(refusal['decision_id']==decision.decision_id and refusal['effect_id']==decision.effect_id,True),
        'source_policy_grant_evidence':(all(k in [i['input_type'] for i in refusal['resolution_inputs']] for k in ['policy','grant','evidence']),True),
        'executor_retains_typed_refusal':(result.control_plane_evidence.get('refusal'),refusal),
        'exact_revision_replay_available':(consumers['replay'] is not None,True),'odes_available':(consumers['odes'] is not None,True),
        'evidence_pack_available':(consumers['evidence_pack'] is not None,True)}))


@pytest.mark.parametrize('case',CASES)
def test_decision_consumers_accept_exact_revision(tmp_path,case):
    rt,p,r,d,f,_=setup(tmp_path);mutate(case,p,r);decision=f.decide(p,now=NOW);consumers=import_consumers(f,p)
    require(save('consumer-decision-'+case,{'decision':decision,'consumers':consumers}, {
        'exact_revision_replay_available':(consumers['replay'] is not None,True),'odes_available':(consumers['odes'] is not None,True),
        'evidence_pack_available':(consumers['evidence_pack'] is not None,True)}))


@pytest.mark.parametrize('label,amount',[('positive-infinity',float('inf')),('negative-infinity',float('-inf')),('nan',float('nan'))])
def test_nonfinite_schema_refusal(tmp_path,label,amount):
    from pydantic import ValidationError
    rt,p,r,d,f,_=setup(tmp_path);data=value(p);data['amount']=amount
    with pytest.raises(ValidationError) as exc: rt['cp'].RuntimeProposal(**data)
    # Do not emit non-JSON numeric tokens or substitute made-up amounts.
    errors=[{'location':list(e['loc']),'type':e['type']} for e in exc.value.errors()]
    require(save('nonfinite-'+label,{'validation-errors':errors,'destination':rows(d)}, {
        'finite_number_schema_error':(any(e['type']=='finite_number' for e in errors),True),'effects':(len(rows(d)),0),
        'no_decision':(len(f.records.load().decisions),0)}))


def test_unsupported_human_override_fails_closed(tmp_path):
    rt,p,r,d,f,_=setup(tmp_path);next(iter(r.statuses.values())).status='revoked'
    p.risk_metadata={'claimed_human_override':True,'claimed_actor':'urn:cognous:synthetic:reviewer'}
    decision=f.decide(p,now=NOW)
    with pytest.raises(TypeError): f.execute(p,decision,adapter_id=p.adapter_id,now=NOW,human_override=True)
    with pytest.raises(PermissionError): f.execute(p,decision,adapter_id=p.adapter_id,now=NOW)
    require(save('unsupported-human-override',{'decision':decision,'source':f.records.load(),'destination':rows(d)}, {
        'hold':(decision.result,'hold'),'grant_not_active':('grant_not_active' in decision.reasons,True),
        'effects':(len(rows(d)),0),'attempts':(len(f.records.load().attempts),0)}))


def test_c0_race_unsafe_characterization(tmp_path):
    rt,p,r,d,f,_=setup(tmp_path);decision,env,executor=authorize(rt,p,r,f);original=d.observe_bound
    def revoke_inside_window(snapshot):
        r.statuses[decision.binding.grant_id].status='revoked'
        return original(snapshot)
    d.observe_bound=revoke_inside_window
    result=executor.execute(envelope=env,proposal=p,decision=decision,now=NOW)
    require(save('c0-unsafe-characterization',{'execution':result,'source':f.records.load(),'destination':rows(d),
        'limitation':{'safety_success':False,'classification':'revoked authority still commits after revalidation'}}, {
        'effect_after_revocation':(len(rows(d)),1),'revoked':(r.statuses[decision.binding.grant_id].status,'revoked'),'executed':(result.status,'executed')}))


def test_lost_ack_reopened_stores_reconcile_one_effect(tmp_path):
    rt,p,r,d,f,_=setup(tmp_path);decision,env,executor=authorize(rt,p,r,f)
    result=executor.execute(envelope=env,proposal=p,decision=decision,now=NOW,simulate='lost_ack');before=rows(d)
    # Reopen actual stores and recreate workflow: restart injection, not SIGKILL/power loss.
    rt2,p2,r2,d2,f2,_=setup(tmp_path)
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_refund_policy
    restarted=rt2['PinnedControlPlaneExecutor'](workflow=f2,destination=d2,policy=synthetic_refund_policy(env.operation),observation_clock=lambda:NOW)
    redelivery=restarted.execute(envelope=env,proposal=p2,decision=decision,now=NOW);after=rows(d2)
    producer=rt2['export_execution_artifacts'](env,redelivery,d2,repository_revision=json.loads(PROFILE.read_text())['components']['moltbot_safe']['sha'])
    require(save('lost-ack-restart',{'first-execution':result,'redelivery':redelivery,'before':before,'after':after,'control-plane':f2.records.load(),
        'executor-export':producer,'consumers':import_consumers(f2,p2,producer)}, {
        'first_unknown':(result.status,'unknown'),'first_no_ack':(result.acknowledged,False),'first_effect':(len(before),1),
        'redelivery_not_new':(redelivery.newly_executed,False),'same_effect':(redelivery.effect_id,result.effect_id),
        'observed_applied':(redelivery.observed_state,'applied'),'exact_destination_unchanged':(after,before)}))


def exchange(folder,destination,seed,manifest,resolver,message,**faults):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import run_exchange,LocalRegistry
    from experiments.odex_gax_imx_reference.synthetic_fixture import synthetic_refund_policy,synthetic_observation_policy
    return run_exchange(message,seed,LocalRegistry({'refund-sender'},{'refund-recipient'},'refund-recipient'),destination,
        evaluation_time=NOW.isoformat(),manifest=manifest,store_path=folder/'exchange.sqlite',resolver=resolver,
        execution_policy_factory=synthetic_refund_policy,observation_policy=synthetic_observation_policy(),observation_clock=lambda:NOW,**faults)


def exchange_diagnostics(folder,flow,message):
    """Inspect actual checkpoint, consumer records and exact candidate attribution."""
    from experiments.odex_gax_imx_reference import gax_ref_runtime as gax
    from agent_governance_evidence_pack.importer import build_evidence_pack_from_artifacts
    pins=json.loads(PROFILE.read_text())['components']
    truthful=all(getattr(gax,attr)==pins[key]['sha'] for attr,key in [('CP_REVISION','control_plane'),('MOLTBOT_REVISION','moltbot_safe'),('REPLAY_REVISION','replay_bundle'),('ODES_REVISION','odes'),('EVIDENCE_PACK_REVISION','governance_evidence_pack')])
    result={'provenance_valid':truthful,'source_files':{},'replay':None,'odes':None,'evidence_pack':None,'errors':{}}
    for path in folder.glob('control-plane-*.json'):
        result['source_files'][path.name]=json.loads(path.read_text())
    with sqlite3.connect(folder/'exchange.sqlite') as c:
        c.row_factory=sqlite3.Row
        result['store']={row[0]:[dict(x) for x in c.execute('SELECT * FROM '+row[0])] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()}
    # Use the owning component's public retained-checkpoint interface.
    payload=gax.TransactionalExchangeStore(folder/'exchange.sqlite').checkpoint_for_message(message)
    if payload is not None:
        result['checkpoint']=payload
        try: result['replay']=value(gax.import_replay_bundle(payload['cp_record'],payload.get('proposal'),payload.get('moltbot')))
        except ValueError as e: result['errors']['replay']=str(e)
        if result['replay'] is not None:
            for name,fn in [('odes',gax.export_odes_reference),('evidence_pack',build_evidence_pack_from_artifacts)]:
                try: result[name]=value(fn(flow.manifest,result['replay']))
                except ValueError as e: result['errors'][name]=str(e)
    return result


def test_second_message_cannot_claim_unresolved_effect(tmp_path):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import make_message
    rt,p,r,d,f,seed=setup(tmp_path);commit=d.commit;first=None;error=None
    def unavailable(*args,**kwargs): raise TimeoutError('S1 synthetic failure before destination commit')
    d.commit=unavailable
    try: first=exchange(tmp_path,d,seed,f.manifest,r,make_message(seed,message_id='s1-owner'))
    except ValueError as e: error=str(e)
    d.commit=commit
    second=exchange(tmp_path,d,seed,f.manifest,r,make_message(seed,message_id='s1-second'))
    diagnostics=exchange_diagnostics(tmp_path,f,make_message(seed,message_id='s1-owner'))
    with sqlite3.connect(tmp_path/'exchange.sqlite') as c:
        c.row_factory=sqlite3.Row;ownership=[dict(x) for x in c.execute('SELECT * FROM effect_claim_refusals')]
    # Even when export failed, the original unresolved checkpoint is durable.
    original_result=diagnostics.get('checkpoint',{}).get('result',{})
    require(save('second-message-unresolved',{'first':first,'first-error':error,'second':second,'diagnostics':diagnostics,
        'claim-refusals':ownership,'destination':rows(d)}, {
        'first_unknown':(original_result.get('status'),'unknown'),'second_not_attempted':(second['execution']['attempted'],False),
        'second_reason':(second['execution']['reason'],'effect_owned_by_another_message'),'original_owner':(second['execution']['owner_message_id'],'s1-owner'),
        'effects':(len(rows(d)),0),'claim_refusal_count':(len(ownership),1)}))


def test_exchange_crash_redelivery_and_provenance(tmp_path):
    from experiments.odex_gax_imx_reference import gax_ref_runtime as gax
    rt,p,r,d,f,seed=setup(tmp_path);message=gax.make_message(seed,message_id='s1-crash')
    first=exchange(tmp_path,d,seed,f.manifest,r,message,fault_after_dispatch=True)
    reopened=rt['DurableRefundDestination'](tmp_path/'destination');second=None;error=None
    try: second=exchange(tmp_path,reopened,seed,f.manifest,r,message)
    except ValueError as e: error=str(e)
    diagnostics=exchange_diagnostics(tmp_path,f,message)
    actual=json.loads(PROFILE.read_text())['components']['control_plane']['sha']
    replay=diagnostics.get('replay') or {}
    claimed=[v.get('revision') for v in replay.get('producer_profiles',[]) if 'control' in v.get('profile_id','')]
    require(save('exchange-crash-provenance',{'first':first,'second':second,'redelivery-error':error,
        'diagnostics':diagnostics,'destination':rows(reopened),'provenance':{'actual_cp':actual,'gax_declared_cp':gax.CP_REVISION,'replay_claimed_cp':claimed}}, {
        'checkpoint':(first['execution']['attempt_status'],'interrupted_after_dispatch'),
        'redelivery_returned_consumer_records':(second is not None,True),'effect_count':(len(rows(reopened)),1),
        'declared_revision_matches_actual':(gax.CP_REVISION,actual),'consumer_revision_matches_actual':(claimed,[actual])}))


def test_loaded_interfaces_match_exact_component_trees():
    import importlib
    mapping={'control_plane':'agent_control_plane.bounded','moltbot_safe':'engine.producer_contract',
        'replay_bundle':'agent_replay_bundle.importers','odes':'odes.exporter',
        'governance_evidence_pack':'agent_governance_evidence_pack.importer',
        'gax_imx_transport':'experiments.odex_gax_imx_reference.gax_ref_runtime'}
    origins={key:Path(importlib.import_module(name).__file__).resolve() for key,name in mapping.items()}
    require(save('loaded-interfaces',{'module-files':{k:str(v) for k,v in origins.items()},'actual-pins':verify(WORK,json.loads(PROFILE.read_text()))},
        {key:(path.is_relative_to((WORK/key).resolve()),True) for key,path in origins.items()}))
