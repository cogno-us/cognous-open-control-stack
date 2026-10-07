#!/usr/bin/env python3
"""Separate, fail-closed Linux namespace qualification of the pinned reference.

The trusted parent holds authority and the destination. The fixed worker has
neither host state nor host network access. This profile is NOT OpenShell.
"""
from __future__ import annotations
import argparse
import dataclasses
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import socketserver
import sqlite3
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'protected-local-worker/0.1.0'
NAMES = ('action_manifest', 'control_plane', 'gax_imx_transport', 'moltbot_safe', 'replay_bundle')
SCENARIOS = ('authorized_control', 'payload_substitution', 'target_substitution',
             'adapter_substitution', 'missing_authority', 'forged_success')
NOW = datetime(2026, 8, 8, 1, tzinfo=timezone.utc)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def checkouts(work, *, clone=False):
    lock = json.loads((ROOT / 'component-lock.json').read_text())
    pins = {}
    for name in NAMES:
        spec = lock['components'][name]
        sha = spec['core_interop_sha'] if name == 'moltbot_safe' else spec['sha']
        path = work / name
        if not path.exists() and clone:
            subprocess.run(['git', 'clone', '-q', 'https://github.com/' + spec['repository'] + '.git', str(path)], check=True)
            subprocess.run(['git', '-C', str(path), 'checkout', '-q', '--detach', sha], check=True)
        if git(path, 'rev-parse', 'HEAD') != sha:
            raise RuntimeError(name + ': pin mismatch')
        # Untracked Python source could shadow the accepted imports too.
        if git(path, 'status', '--porcelain', '--untracked-files=all'):
            raise RuntimeError(name + ': checkout not clean')
        pins[name] = sha
    return pins


def runtime_paths(work):
    lock=json.loads((ROOT / "component-lock.json").read_text())
    os.environ["GAX_RUNTIME_COMPATIBILITY_PROFILE"]=lock.get("runtime_profile","persistence-v1")
    for path in (work / 'control_plane/src', work / 'moltbot_safe', work / 'gax_imx_transport'):
        sys.path.insert(0, str(path))
    os.environ['MOLTBOT_SAFE_CONTROL_PLANE_ROOT'] = str(work / 'control_plane')
    os.environ['MOLTBOT_SAFE_ROOT'] = str(work / 'moltbot_safe')
    sys.dont_write_bytecode = True


def setup(work, case):
    from experiments.odex_gax_imx_reference.gax_ref_runtime import load_executor_runtime, runtime_proposal_model
    from experiments.odex_gax_imx_reference.synthetic_fixture import build_synthetic_resolver, synthetic_observation_policy, synthetic_refund_policy
    rt = load_executor_runtime()
    cp = rt['cp']
    manifest = json.loads((work / 'action_manifest/examples/refund_integration_v1_1.manifest.json').read_text())
    proposal = runtime_proposal_model(json.loads((work / 'replay_bundle/examples/bounded_success_reconstruction_v0_2.json').read_text()))
    resolver = build_synthetic_resolver(proposal, now=NOW)
    destination = rt['DurableRefundDestination'](case / 'destination')
    workflow = cp.BoundedAuthorizationWorkflow(manifest=manifest, resolver=resolver,
        destination=destination, records=cp.BoundedRecordStore(case / 'records.json', 'protected-qualification'),
        observation_policy=synthetic_observation_policy())
    decision = workflow.decide(proposal, now=NOW)
    if decision.result != 'authorized':
        raise RuntimeError('authorized fixture failed: ' + str(decision.reasons))
    binding = decision.binding
    context = resolver.authority_context(proposal.authority_context_ref)
    values = proposal.model_dump(mode='json', exclude_none=False)
    values.update(institution_id=context['institution']['institution_id'],
        authority_domain=context['institution']['authority_domain'],
        authority_context_id=proposal.authority_context_ref,
        proposal_commitment=binding.proposal_commitment, grant_id=binding.grant_id,
        grant_revision=binding.grant_revision, effective_max_effects=binding.effective_max_effects,
        requested_permissions=tuple(proposal.requested_permissions))
    operation = rt['ExecutionOperation'](**{f.name: values[f.name] for f in dataclasses.fields(rt['ExecutionOperation'])})
    envelope = rt['ExecutionEnvelope'](version='0.2.0', decision_id=decision.decision_id,
        effect_id=decision.effect_id, operation=operation)
    executor = rt['PinnedControlPlaneExecutor'](workflow=workflow, destination=destination,
        policy=synthetic_refund_policy(operation), observation_clock=lambda: NOW)
    return proposal, resolver, destination, decision, envelope, executor


def oracle(path):
    # A separate host read connection: no worker/executor acknowledgement used.
    with sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute('SELECT * FROM effects ORDER BY effect_id')]


def dispatch(request, expected_scenario, fixture):
    """Fixed campaign dispatcher, not a new runtime authorization implementation."""
    if not isinstance(request, dict) or request.get('scenario') != expected_scenario:
        raise ValueError('worker scenario mismatch')
    proposal, resolver, destination, decision, envelope, executor = fixture
    if expected_scenario == 'forged_success':
        if set(request) != {'scenario', 'claimed_effect'} or request['claimed_effect'] != 'applied':
            raise ValueError('malformed forged-result control')
        return {'status': 'untrusted_claim_ignored', 'newly_executed': False}
    field = {'payload_substitution': 'payload', 'target_substitution': 'target',
             'adapter_substitution': 'adapter_id'}.get(expected_scenario)
    if set(request) != ({'scenario', 'value'} if field else {'scenario'}):
        raise ValueError('unexpected worker fields')
    if field:
        updates = {field: request['value']}
        if field == 'payload':
            from engine.producer_contract import commitment
            updates['payload_commitment'] = commitment(request['value'])
        envelope = dataclasses.replace(envelope, operation=dataclasses.replace(envelope.operation, **updates))
    if expected_scenario == 'missing_authority':
        resolver.contexts.clear()
    result = executor.execute(envelope=envelope, proposal=proposal, decision=decision, now=NOW)
    return dataclasses.asdict(result)


def sandbox_command():
    bwrap = shutil.which('bwrap')
    if not bwrap:
        raise RuntimeError('bubblewrap is unavailable')
    cmd = [bwrap, '--unshare-all', '--die-with-parent', '--new-session', '--cap-drop', 'ALL',
           '--clearenv', '--setenv', 'PATH', '/usr/bin', '--setenv', 'PYTHONDONTWRITEBYTECODE', '1']
    for path in ('/usr', '/lib', '/lib64'):
        if Path(path).exists():
            cmd += ['--ro-bind', path, path]
    return cmd + ['--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
                  '--ro-bind', str(ROOT / 'tools/protected_worker.py'), '/worker.py',
                  '--chdir', '/tmp', '/usr/bin/python3', '-I', '/worker.py']


class Sink(socketserver.TCPServer):
    allow_reuse_address = True


class SinkHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Count a connection, even if a peer transmits no data. No external service.
        self.server.hits.append(True)


def boundary_ok(worker, expected_paths, namespaces):
    keys = {name + ':' + mode for name in expected_paths for mode in ('rb', 'ab')} | {'host_sink'}
    probes = worker.get('probes')
    return (isinstance(probes, dict) and set(probes) == keys
        and all(isinstance(p, dict) and p.get('blocked') is True for p in probes.values())
        and worker.get('cross_run_state') is False
        and isinstance(worker.get('namespaces'), dict)
        and set(worker['namespaces']) == set(namespaces)
        and all(isinstance(worker['namespaces'][n], str) and worker['namespaces'][n] != namespaces[n] for n in namespaces))


def effect_ok(scenario, before, after, proposal, decision, result):
    if before:
        return False
    if scenario != 'authorized_control':
        return after == [] and result.get('newly_executed') is False and result.get('status') in ('denied', 'untrusted_claim_ignored')
    return (len(after) == 1 and after[0]['effect_id'] == decision.effect_id
        and after[0]['state'] == 'applied' and after[0]['target'] == proposal.target
        and after[0]['amount'] == proposal.amount and after[0]['unit'] == proposal.unit
        and json.loads(after[0]['payload_json']) == proposal.payload
        and result.get('newly_executed') is True)


def run_campaign(work, out, *, clone=False):
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError('evidence directory must be empty; previous evidence is preserved')
    report = {'profile': PROFILE, 'status': 'blocked', 'qualified': False,
              'live_openshell_qualified': False, 'production_qualified': False,
              'repetitions': [], 'component_lock_sha256': digest(ROOT / 'component-lock.json')}
    try:
        report['pins'] = checkouts(work, clone=clone)
        runtime_paths(work)
        cmd = sandbox_command()
        report['worker_sha256'] = digest(ROOT / 'tools/protected_worker.py')
        report['runner_sha256'] = digest(Path(__file__))
        report['hub_head'] = git(ROOT, 'rev-parse', 'HEAD')
        report['hub_tracked_diff'] = git(ROOT, 'diff', '--stat')
        report['bubblewrap_version'] = subprocess.check_output([cmd[0], '--version'], text=True).strip()
        namespaces = {n: os.readlink('/proc/self/ns/' + n) for n in ('net', 'mnt', 'pid')}
        report['host_namespaces'] = namespaces
        report['host_python'] = sys.version
        with Sink(('127.0.0.1', 0), SinkHandler) as sink, tempfile.TemporaryDirectory(prefix='protected-qualification-') as tmp:
            sink.hits = []
            thread = threading.Thread(target=sink.serve_forever, daemon=True)
            thread.start()
            try:
                private = Path(tmp)
                canary = private / 'oracle-canary'; canary.write_text('synthetic host oracle canary')
                credential = private / 'credential-canary'; credential.write_text('synthetic fixture only; not a real credential')
                before_canaries = {str(p): digest(p) for p in (canary, credential)}
                for repetition in (1, 2):
                    cases = []
                    report['repetitions'].append({'number': repetition, 'cases': cases})
                    for scenario in SCENARIOS:
                        case = private / f'{repetition}-{scenario}'; case.mkdir()
                        fixture = setup(work, case)
                        proposal, _, destination, decision, _, _ = fixture
                        paths = {'oracle': str(canary), 'credential': str(credential), 'destination': str(destination.path)}
                        before = oracle(destination.path)
                        cfg = {'scenario': scenario, 'private_paths': paths, 'sink_port': sink.server_address[1]}
                        evidence = {'scenario': scenario, 'repetition': repetition,
                                    'destination_before': before, 'passed': False}
                        cases.append(evidence)
                        try:
                            proc = subprocess.run(cmd, input=json.dumps(cfg), text=True, capture_output=True, timeout=10)
                        except subprocess.TimeoutExpired as exc:
                            evidence.update(worker_timeout=True, destination_after=oracle(destination.path),
                                stdout=str(exc.stdout or ''), stderr=str(exc.stderr or ''))
                            raise
                        evidence.update(worker_exit=proc.returncode, stderr=proc.stderr, stdout=proc.stdout,
                                        pre_dispatch_destination=oracle(destination.path))
                        if proc.returncode:
                            raise RuntimeError('namespace worker did not complete; isolation preflight blocked')
                        worker = json.loads(proc.stdout)
                        evidence['boundary_passed'] = boundary_ok(worker, paths, namespaces)
                        if not evidence['boundary_passed']:
                            report['status'] = 'failed'
                            raise RuntimeError('worker isolation preflight failed; no dispatch permitted')
                        evidence['canaries_unchanged'] = before_canaries == {str(p): digest(p) for p in (canary, credential)}
                        evidence['prohibited_sink_connections'] = len(sink.hits)
                        if not evidence['canaries_unchanged'] or sink.hits or evidence['pre_dispatch_destination'] != before:
                            report['status'] = 'failed'
                            raise RuntimeError('independent oracle detected a prohibited effect before dispatch')
                        result = dispatch(worker['request'], scenario, fixture)
                        after = oracle(destination.path)
                        evidence.update(executor_result=result, destination_after=after,
                                        passed=effect_ok(scenario, before, after, proposal, decision, result))
                        if not evidence['passed']:
                            report['status'] = 'failed'
                            raise RuntimeError('destination/authorization invariant failed')
                sink.shutdown(); thread.join(timeout=2)
                report['prohibited_sink_connections'] = len(sink.hits)
                report['canaries_unchanged'] = before_canaries == {str(p): digest(p) for p in (canary, credential)}
                report['qualified'] = not sink.hits and report['canaries_unchanged'] and all(
                    len(rep['cases']) == len(SCENARIOS) and all(c['passed'] for c in rep['cases']) for rep in report['repetitions'])
                report['status'] = 'passed' if report['qualified'] else 'failed'
            finally:
                sink.shutdown(); thread.join(timeout=2)
    except Exception as exc:
        report['error'] = type(exc).__name__ + ': ' + str(exc)
    dump(out / 'summary.json', report)
    print(json.dumps({'status': report['status'], 'qualified': report['qualified'], 'summary': str(out / 'summary.json')}))
    return 0 if report['qualified'] else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work-dir', type=Path, default=ROOT / '.protected-work')
    ap.add_argument('--results-dir', type=Path, required=True)
    ap.add_argument('--clone', action='store_true', help='clone missing exact-pin dependencies; never overwrite checkouts')
    args = ap.parse_args()
    return run_campaign(args.work_dir.resolve(), args.results_dir.resolve(), clone=args.clone)


if __name__ == '__main__':
    raise SystemExit(main())
