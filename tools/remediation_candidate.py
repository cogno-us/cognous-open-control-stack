#!/usr/bin/env python3
"""S1 opt-in actual-component qualification. Never selects or authorizes a release."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'profiles/remediation-candidate-20261015.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def verify(work, profile):
    """Reject dirty inputs, including untracked import shadows; never change a checkout."""
    actual = {}
    for name, spec in profile['components'].items():
        path = work / name
        head = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        dirty = subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain', '--untracked-files=all'], text=True).strip()
        if head != spec['sha'] or dirty:
            raise ValueError(f'{name}: exact clean pin required; head={head}, dirty={bool(dirty)}')
        actual[name] = head
    if profile['selected'] is not False or any(profile[k] is not False for k in (
            'reference_release_authorized', 'production_deployment_authorized')):
        raise ValueError('candidate must remain nonselected and non-authorizing')
    return actual


def environment(work, out):
    env = os.environ.copy()
    env.update({
        'PYTHONDONTWRITEBYTECODE': '1', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
        'PYTHONPATH': os.pathsep.join(map(str, [ROOT, work/'control_plane/src', work/'moltbot_safe',
            work/'gax_imx_transport', work/'replay_bundle/src', work/'odes/src', work/'governance_evidence_pack/src'])),
        'S1_WORK': str(work), 'S1_RESULTS': str(out),
        'GAX_RUNTIME_COMPATIBILITY_PROFILE': 'merged-producers-v1',
        'MOLTBOT_SAFE_CONTROL_PLANE_ROOT': str(work/'control_plane'),
        'MOLTBOT_SAFE_ROOT': str(work/'moltbot_safe'),
        'UPSTREAM_MANIFEST_EXAMPLE': str(work/'action_manifest/examples/refund_integration_v1_1.manifest.json'),
        'MOLTBOT_SAFE_MANIFEST_FIXTURE': str(work/'action_manifest/examples/refund_integration_v1_1.manifest.json'),
        'UPSTREAM_REPLAY_SUCCESS_EXAMPLE': str(work/'replay_bundle/examples/bounded_success_reconstruction_v0_2.json'),
    })
    return env


def inspect_junit(path):
    cases = list(ET.parse(path).getroot().iter('testcase')) if path.exists() else []
    # Do not trust aggregate testsuite counters, which can include unittest subtests.
    rows = [{'class': c.get('classname'), 'name': c.get('name'),
             'outcome': next((k for k in ('failure', 'error', 'skipped') if c.find(k) is not None), 'passed')}
            for c in cases]
    return {'testcase_elements': len(cases), 'cases': rows,
            'failures': sum(c['outcome']=='failure' for c in rows),
            'errors': sum(c['outcome']=='error' for c in rows),
            'skips': sum(c['outcome']=='skipped' for c in rows),
            'subtests': {'executed': 0, 'note': 'No unittest subtests in this explicitly parametrized pytest suite.'}}


def execute(command, env, log):
    with log.open('w') as stream:
        p = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return p.wait(timeout=180)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            return 124


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--prepare-work', action='store_true', help='Clone only missing checkouts and detach at exact candidate pins.')
    args = parser.parse_args()
    work, out = args.work.resolve(), args.out.resolve()
    profile = json.loads(PROFILE.read_text())
    if args.prepare_work:
        work.mkdir(parents=True, exist_ok=True)
        for name, spec in profile['components'].items():
            dest = work/name
            if not dest.exists():
                subprocess.run(['git','clone','--quiet','https://github.com/'+spec['repository']+'.git',str(dest)],check=True)
                subprocess.run(['git','-C',str(dest),'checkout','--quiet','--detach',spec['sha']],check=True)
    actual = verify(work, profile)
    out.mkdir(parents=True, exist_ok=True)
    if list(out.iterdir()):
        raise SystemExit('Output directory must be empty; evidence is never overwritten.')
    dump(out/'candidate.json', profile)
    dump(out/'environment.json', {'python':sys.version, 'pins': actual,
         'hub_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         'dependency_lock_sha256':digest(ROOT/'tools/requirements-release.lock'),
         'installed':subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines(),
         'source_hashes':{p:digest(ROOT/p) for p in ('tools/remediation_candidate.py','tests/test_remediation_candidate.py',str(PROFILE.relative_to(ROOT)))}})
    results = []
    for repetition in (1,2):
        folder = out/f'run-{repetition}'
        folder.mkdir()
        junit = folder/'junit.xml'
        command = [sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests/test_remediation_candidate.py','--junitxml',str(junit)]
        code = execute(command, environment(work,folder), folder/'execution.log')
        inspection = inspect_junit(junit)
        dump(folder/'junit-inspection.json', inspection)
        results.append({'repetition':repetition,'command':command,'returncode':code,**inspection})
    verify(work,profile)
    normalized = []
    for repetition in (1,2):
        checks = {}
        for p in sorted((out/f'run-{repetition}').glob('*/checks.json')):
            checks[p.parent.name] = {k:v['passed'] for k,v in json.loads(p.read_text()).items()}
        normalized.append(checks)
    repeatable = bool(normalized[0]) and normalized[0] == normalized[1]
    passed = repeatable and all(r['returncode']==0 and r['testcase_elements'] and not (r['failures'] or r['errors'] or r['skips']) for r in results)
    summary = {'assignment':'S1 / lane A','actual_pins':actual,'repetitions':results,
               'check_outcomes_repeatable':repeatable,'repeatability_scope':'Per-named-assertion outcomes; raw UUIDs, times and artifact hashes are retained separately, not byte-repeatability.','candidate_integration_passed':bool(passed),
               'selected':False,'reference_release_authorized':False,'production_deployment_authorized':False,
               'operational_trust':'HOLD / NOT ESTABLISHED',
               'scope':'C0 synthetic SQLite; optional C1 same-host only; no C2/C3 or real settlement',
               'clock':'Injected service clock for dated fixtures; no clock trust qualification',
               'limitations':['C0 revocation-after-revalidation remains unsafe; passing its characterization is not safety.',
                              'No supported human override transition; denied operation must remain denied.',
                              'Two recreated workflows/reopened stores are crash/restart injection, not a killed process or host power failure.']}
    dump(out/'summary.json', summary)
    hashes = {str(p.relative_to(out)):digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
    dump(out/'sha256.json', hashes)
    print(json.dumps({k:v for k,v in summary.items() if k!='repetitions'},indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
