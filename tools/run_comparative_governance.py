#!/usr/bin/env python3
"""Run a predeclared shared synthetic battery; report mismatches without hiding them."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
import random
import sqlite3
import statistics
import subprocess
import sys
import time
from threading import Barrier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from benchmarks.governance.adapters import Cognous, Conventional, LangGraphOPA
from reference_profiles.assurance_runtime import digest
from reference_profiles.trust_evidence import signed

PLAN = ROOT / 'benchmarks/governance/plan.json'
ADAPTERS = {'cognous-protected-destination': Cognous, 'opa-transactional-application': Conventional,
            'langgraph-opa-transactional-application': LangGraphOPA}


def crash_worker(adapter, request, before_commit):
    if before_commit:
        original = sqlite3.connect
        def connection(*args, **kwargs):
            conn = original(*args, **kwargs)
            if 'destination.sqlite' in str(args[0]):
                def trace(statement):
                    if statement.upper().startswith('INSERT INTO EVENTS'):
                        os._exit(73)
                conn.set_trace_callback(trace)
            return conn
        sqlite3.connect = connection
    adapter.apply(request)
    os._exit(74)


def evaluate(case, outputs, snapshot, profile=None):
    actual = [x['status'] for x in outputs]
    expected = case['expected_statuses']
    # Parallel completion order is nondeterministic; the count of accepted calls matters.
    if case['id'] == 'concurrent_last_budget': actual, expected = sorted(actual), sorted(expected)
    decisions = actual == expected
    expected_reasons=case.get('expected_reasons',{}).get(profile)
    reason_conformance=(expected_reasons is None or [o.get('reason') for o in outputs]==expected_reasons)
    if case['id']=='concurrent_last_budget' and expected_reasons is not None:
        reason_conformance=sorted((o.get('reason') or '') for o in outputs)==sorted(r or '' for r in expected_reasons)
    effect_count = len(snapshot['effects'])
    effects = (effect_count == case['expected_effects'] and
               all(e['id'] in case['allowed_effect_ids'] and
                   json.loads(e['payload']) == case['expected_payload'] for e in snapshot['effects']))
    denials = [o for o in outputs if o['status'] == 'denied']
    covered = sum(any((e.get('command_authenticated') is not True or e.get('command') == o['command']) and e.get('status') == 'denied'
                      and bool(e.get('reason')) and e.get('request_digest') == o['request_digest']
                      and type(e.get('at')) is int for e in snapshot['events']) for o in denials)
    return dict(pass_case=decisions and effects and reason_conformance and covered == len(denials),
        decision_conformance=decisions, reason_conformance=reason_conformance, destination_conformance=effects,
        expected_effects=case['expected_effects'], actual_effects=effect_count,
        unexpected_effect_count=max(0,effect_count-case['expected_effects']),
        missing_effect_count=max(0,case['expected_effects']-effect_count),
        false_allows=sum(a=='accepted' and e=='denied' for a,e in zip(actual,expected)),
        false_blocks=sum(a!='accepted' and e=='accepted' for a,e in zip(actual,expected)),
        denied_calls=len(denials), durably_recorded_denials=covered)


def run_case(adapter_class, case, root, opa, mutation=None):
    adapter = adapter_class(root, opa, mutation); outputs=[]; timings=[]; captured=None; faults=[]
    def execute(request):
        start=time.perf_counter_ns()
        try:
            result=adapter.apply(request)
        except sqlite3.IntegrityError as exc:
            if str(exc) != 'synthetic audit outage':
                raise
            result={'status':'unavailable','reason':'AUDIT_TRANSACTION_ABORTED'}
        elapsed=(time.perf_counter_ns()-start)/1e6
        return dict(status=result['status'],reason=result.get('reason'),command=request['body']['id'],
                    request_digest=digest(request),
                    duplicate=result.get('result',{}).get('duplicate',False)),elapsed
    for step in case['steps']:
        action=step['action']
        if action == 'execute':
            output,elapsed=execute(adapter.request(step.get('args'),step.get('fault')))
            outputs.append(output);timings.append(elapsed)
        elif action == 'capture': captured=adapter.request(step.get('args'))
        elif action == 'alter_captured':
            body=captured['body']; arguments=body['arguments']
            body.update(step.get('body',{})); arguments.update(step.get('args',{}))
            if 'status' in step:
                status=arguments['verifier_status']['body']; status.update(step['status'])
                arguments['verifier_status']=signed(adapter.keys['verifier'],'verifier','destination-status',status)
            if step.get('resign',True):
                captured=signed(adapter.keys['broker'],'broker','destination-command',body)
        elif action == 'submit':
            output,elapsed=execute(captured);outputs.append(output);timings.append(elapsed)
        elif action == 'clock': adapter.now=step['now']
        elif action == 'parallel':
            requests=[adapter.request({'effect':'parallel-'+str(i)}) for i in range(2)]
            barrier=Barrier(2)
            def simultaneous(request):
                barrier.wait(timeout=10)
                return execute(request)
            with ThreadPoolExecutor(max_workers=2) as pool:
                for output,elapsed in pool.map(simultaneous,requests):outputs.append(output);timings.append(elapsed)
        elif action in ('crash_before_commit','crash_after_commit'):
            process=multiprocessing.get_context('fork').Process(target=crash_worker,
                args=(adapter,adapter.request(),action=='crash_before_commit'))
            process.start();process.join(20)
            if process.is_alive():
                process.kill();process.join();raise RuntimeError('crash injection timed out')
            expected_exit=73 if action=='crash_before_commit' else 74
            if process.exitcode != expected_exit:raise RuntimeError('crash injection did not reach intended boundary')
            observed=len(adapter.snapshot()['effects'])
            faults.append(dict(action=action,exitcode=process.exitcode,effects_after_crash=observed,
                               expected_effects_after_crash=step['expected_effects_after']))
            adapter.reopen()
        else: getattr(adapter,action)()
    snapshot=adapter.snapshot()
    profile=next(k for k,v in ADAPTERS.items() if adapter_class is v)
    verdict=evaluate(case,outputs,snapshot,profile)
    verdict['pass_case'] = verdict['pass_case'] and all(f['effects_after_crash']==f['expected_effects_after_crash'] for f in faults)
    return dict(case_id=case['id'], **verdict, outputs=outputs, injected_faults=faults,
                expected_statuses=case['expected_statuses'], elapsed_ms=timings,
                destination=snapshot)


def summarize(rows):
    result={}
    for profile in ADAPTERS:
        selected=[r for r in rows if r['profile']==profile]
        times=[t for r in selected if r['case_id']=='permitted' for t in r['elapsed_ms']]
        result[profile]=dict(case_trials=len(selected),passed=sum(r['pass_case'] for r in selected),
            unexpected_effects=sum(r['unexpected_effect_count'] for r in selected),
            missing_effects=sum(r['missing_effect_count'] for r in selected),
            false_allows=sum(r['false_allows'] for r in selected),false_blocks=sum(r['false_blocks'] for r in selected),
            denied_calls=sum(r['denied_calls'] for r in selected),
            durably_recorded_denials=sum(r['durably_recorded_denials'] for r in selected),
            permitted_latency_samples=len(times),
            permitted_latency_median_ms=statistics.median(times),
            permitted_latency_p95_ms=sorted(times)[math.ceil(.95*len(times))-1])
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--opa',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--plan',type=Path,default=PLAN)
    parser.add_argument('--observe-conformance',action='store_true',help='Report mismatches without making them CI infrastructure failures; mutations must still be detected')
    parser.add_argument('--seed',type=int,choices=[1701,1702],required=True)
    args=parser.parse_args();opa=str(args.opa.resolve());output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    plan_path=args.plan.resolve(); plan=json.loads(plan_path.read_text()); lock=json.loads((ROOT/'benchmarks/governance/dependencies.json').read_text())
    if hashlib.sha256(Path(opa).read_bytes()).hexdigest()!=lock['opa']['sha256']:
        raise ValueError('OPA binary differs from pinned dependency')
    for package,version in lock['python_direct'].items():
        if importlib.metadata.version(package)!=version: raise ValueError('dependency drift: '+package)
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    tracked=['benchmarks/governance','tools/run_comparative_governance.py','reference_profiles',
             '.github/workflows/comparative-governance.yml','tests/test_comparative_governance.py','tools/destination_admission_mutations.py','tests/test_protected_destination.py']
    dirty=subprocess.check_output(['git','status','--porcelain','--',*tracked],cwd=ROOT,text=True)
    if dirty: raise ValueError('commit benchmark and runtime source before qualification')
    schedule=[(rep,case,profile) for rep in range(plan['repetitions']) for case in plan['cases'] for profile in ADAPTERS]
    random.Random(args.seed).shuffle(schedule);rows=[]
    for rep,case,profile in schedule:
        root=output/'destinations'/f'{rep}-{profile}-{case["id"]}'
        row=run_case(ADAPTERS[profile],case,root,opa)
        row.update(repetition=rep,profile=profile);rows.append(row)
    mutants=[]
    for mutation,case_id in plan['mutations'].items():
        case=next(c for c in plan['cases'] if c['id']==case_id)
        result=run_case(Conventional,case,output/'mutations'/mutation,opa,mutation)
        mutants.append(dict(mutation=mutation,detected=not result['pass_case'],result=result))
    control=subprocess.run([sys.executable,str(ROOT/'tools/destination_admission_mutations.py')],cwd=ROOT,capture_output=True,text=True,timeout=120)
    if control.returncode:raise RuntimeError('Cognous control-removal qualification failed: '+control.stdout+control.stderr)
    cognous_mutations=[line for line in control.stdout.splitlines() if line.startswith('DETECTED: J')]
    if len(set(cognous_mutations))!=13:raise RuntimeError('Cognous mutation count drift')
    summary=summarize(rows)
    report=dict(observation_mode=args.observe_conformance, schema='cognous.comparative-governance-results/1',source_revision=revision,
        plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),seed=args.seed,python=platform.python_version(),
        platform=platform.platform(),sqlite=sqlite3.sqlite_version,
        dependencies=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines(),
        opa_version=subprocess.check_output([opa,'version'],text=True),summary=summary,rows=rows,mutations=mutants,
        cognous_unit_mutations=cognous_mutations, not_run=plan['not_run'],independent_review=False,production_deployment_authorized=False,
        reference_release_authorized=False,operational_trust='HOLD / NOT ESTABLISHED',
        benchmark_pass=all(r['pass_case'] for r in rows) and all(m['detected'] for m in mutants))
    (output/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Shared synthetic governance battery','',f'Source: `{revision}`',f'Plan SHA-256: `{report["plan_sha256"]}`',
           '', 'Results describe these configured applications, not whole products or production assurance.','',
           '| Configuration | Passing case trials | Unexpected effects | False allows | False blocks | Durable denials |',
           '| --- | ---: | ---: | ---: | ---: | ---: |']
    for p,s in summary.items():
        lines.append(f'| {p} | {s["passed"]}/{s["case_trials"]} | {s["unexpected_effects"]} | {s["false_allows"]} | {s["false_blocks"]} | {s["durably_recorded_denials"]}/{s["denied_calls"]} |')
    lines+=['', '| Scenario | Cognous passes | OPA application passes | LangGraph + OPA passes |',
            '| --- | ---: | ---: | ---: |']
    for case in plan['cases']:
        counts=[]
        for profile in ADAPTERS:
            selected=[r for r in rows if r['case_id']==case['id'] and r['profile']==profile]
            counts.append(str(sum(r['pass_case'] for r in selected))+'/'+str(len(selected)))
        lines.append('| '+case['id']+' | '+' | '.join(counts)+' |')
    lines+=['',f'Comparator control-removal probes detected: {sum(m["detected"] for m in mutants)}/{len(mutants)}.',
            '', f'Cognous unit-suite control-removal probes detected: {len(cognous_mutations)}/13.',
            '', 'Latency is descriptive only: OPA CLI startup and LangGraph checkpoint/interrupt overhead differ. No speed ranking or human review-time claim.',
            '', '## Not run','']+[f'- {k}: {v}' for k,v in plan['not_run'].items()]
    lines+=['', 'Observation mode: '+str(args.observe_conformance)+'. A completed observation job does not mean all configurations conform.', '', 'No independent reviewer or hidden task set. No release or production authorization.']
    (output/'summary.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:report[k] for k in ('source_revision','plan_sha256','summary','benchmark_pass')},indent=2))
    return 0 if (report['benchmark_pass'] or (args.observe_conformance and all(m['detected'] for m in mutants))) else 1


if __name__=='__main__':raise SystemExit(main())
