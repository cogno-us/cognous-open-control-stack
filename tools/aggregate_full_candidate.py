"""Resolve the unchanged acceptance matrix from all bounded candidate batches."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
from tools.reference_release import BATCHES
from tools.release_gate import parse_junit, resolve_matrix

ROOT=Path(__file__).resolve().parents[1]


def validate_reports(reports, digest):
    if len(reports)!=len(BATCHES) or {r.get('batch') for r in reports}!=set(BATCHES):
        raise ValueError('missing or duplicated qualification batch')
    for report in reports:
        batch=report['batch']
        if report.get('profile_sha256')!=digest or report.get('passed') is not True:
            raise ValueError('failed batch or contradictory candidate profile')
        observed={(run['suite'],run['repetition']) for run in report['suite_runs'] if run['returncode']==0}
        required={(name,rep) for name in BATCHES[batch] for rep in (1,2)}
        if not required.issubset(observed):
            raise ValueError('missing suite repetition')
        if batch=='exchange' and (report.get('representative_repeatable') is not True or len(report.get('representative_runs',[]))!=2 or any(r['returncode'] for r in report['representative_runs'])):
            raise ValueError('transport repeatability not established')
        if batch=='authority' and (len(report.get('extra',[]))!=1 or report['extra'][0]['returncode']!=0):
            raise ValueError('OpenShell mock gate missing or failed')
        if batch=='registry':
            if len(report.get('extra',[]))!=3 or any(r['returncode'] for r in report['extra']):
                raise ValueError('optional static evidence missing or failed')
            if not {('index_local_chain',1),('index_local_chain',2)}.issubset(observed):
                raise ValueError('Index chain evidence missing')


def main():
    p=argparse.ArgumentParser();p.add_argument('--artifacts',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    source=Path(a.artifacts);out=Path(a.out)
    out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()):raise SystemExit('Choose an empty aggregate output directory')
    profile=ROOT/'profiles/full-release-candidate.json'
    digest=hashlib.sha256(profile.read_bytes()).hexdigest()
    paths=list(source.rglob('*-summary.json'))
    reports=[json.loads(path.read_text()) for path in paths]
    validate_reports(reports,digest)
    cases=[]
    for path,report in zip(paths,reports):
        for run in report['suite_runs']:
            if 'junit' not in run:continue
            xml=path.parent/run['junit']
            parsed=parse_junit(xml,run['suite'],run['repetition'])
            if not parsed:raise ValueError('empty suite evidence')
            if run['suite'].endswith('_merged') and any(c['status']!='passed' for c in parsed):raise ValueError('merged compatibility skipped or failed')
            cases.extend(parsed)
    passed,resolved=resolve_matrix(json.loads((ROOT/'scenarios/acceptance-matrix.json').read_text()),cases)
    result={'profile_sha256':digest,'candidate_qualification_passed':passed,'accepted_lock_advanced':False,'release_qualified':False,'scenario_results':resolved,'batches':reports}
    (out/'full-candidate-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'candidate_qualification_passed':passed,'scenarios':len(resolved),'accepted_lock_advanced':False}))
    return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
