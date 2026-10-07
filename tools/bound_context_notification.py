#!/usr/bin/env python3
"""Run explicit context-bound execution or independently authorized notification."""
import argparse
import dataclasses
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profile', choices=('context-action','notification'), required=True)
    ap.add_argument('--results-dir', type=Path, required=True)
    ap.add_argument('--execute', action='store_true', help=argparse.SUPPRESS)
    args = ap.parse_args()
    root = args.results_dir.resolve()
    if root.exists(): raise FileExistsError(root)
    if not args.execute:
        from tools.optional_execution_profile import prepare
        from tools.worker21_authority_effect_qualification import run
        work = ROOT / '.optional-work'
        work.mkdir(exist_ok=True)
        env, pins, lock_digest = prepare(work)
        rec = run([sys.executable,str(Path(__file__).resolve()),'--execute','--profile',args.profile,'--results-dir',str(root)],env=env,timeout=90)
        if root.is_dir():
            (root / 'execution.log').write_text(rec['output'])
            (root / 'provenance.json').write_text(json.dumps({'tested_revisions':pins,'component_lock_sha256':lock_digest,'returncode':rec['returncode']},indent=2))
        print(rec['output'])
        return rec['returncode']
    root.mkdir(parents=True)
    from tools.optional_execution import BASE, setup
    if args.profile == 'context-action':
        from reference_profiles.context_memory import ContextMemory
        from reference_profiles.context_action import ContextBoundExecutor
        from engine.local_authority_effect import AtomicAuthorityEffectDestination, AtomicLocalControlPlaneExecutor
        workflow, resolver, proposal, decision, envelope, policy = setup(root, ROOT / '.optional-work')
        destination = AtomicAuthorityEffectDestination(root / 'destination',clock=lambda: BASE)
        executor = AtomicLocalControlPlaneExecutor(workflow=workflow,destination=destination,policy=policy)
        memory = ContextMemory(root / 'context.sqlite3',clock=lambda: BASE.timestamp())
        memory.admit(item_id='synthetic-context',content='Synthetic refund context',purposes=['refund'],recipients=[envelope.operation.actor],
                     obligations=['retain-provenance'],expires_at=BASE.timestamp()+100,source_ref='synthetic:source')
        delivered = memory.deliver('synthetic-context',purpose='refund',recipient=envelope.operation.actor,expected_generation=memory.generation(),callback=lambda _: None)
        gateway = ContextBoundExecutor(memory,executor)
        claim = gateway.provision_claim(delivery_id=delivered['delivery_id'],proposal=proposal,decision=decision,now=BASE)
        binding = gateway.bind(delivery_id=delivered['delivery_id'],envelope=envelope,claim_id=claim.claim_id)
        effect = gateway.execute(binding_id=binding,envelope=envelope,claim_id=claim.claim_id)
        report = {'profile':'context-action/2','binding_id':binding,'delivery':delivered,'effect':dataclasses.asdict(effect),'qualified':effect.status=='executed'}
    else:
        from reference_profiles.notification import notification_case, ADAPTER
        workflow, _, destination, proposal, decision, refund, refund_decision = notification_case(root,ROOT / '.optional-work')
        attempt, observation = workflow.execute(proposal,decision,adapter_id=ADAPTER,now=BASE)
        report = {'profile':'synthetic-notification/1','refund_decision_id':refund_decision.decision_id,'notification_decision_id':decision.decision_id,
                  'notification_grant_id':decision.binding.grant_id,'attempt':attempt.model_dump(mode='json'),
                  'observation':observation.model_dump(mode='json') if observation else None,
                  'external_delivery_verified':False,'qualified':destination.count()==1 and attempt.status=='acknowledged'}
    report.update(production_ready=False,consumer_chain_qualified=False)
    (root / 'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['qualified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
