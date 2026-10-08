"""Two-step synthetic refund trajectory using the accepted atomic executor.

Each step has its own proposal, approval, decision and consumable claim. The
same explicitly bounded grant may cover both. No notification adapter or
remote cancellation semantics are implied.
"""
import dataclasses
from datetime import timedelta
import json
import sqlite3
from tools.optional_execution import BASE, setup

SCENARIOS = ('allowed', 'revoked', 'policy-changed', 'evidence-expired', 'cancel-requested', 'first-unknown', 'reused-claim')


def run_trajectory(root, work, scenario):
    if scenario not in SCENARIOS:
        raise ValueError('unsupported trajectory')
    root.mkdir(parents=True, exist_ok=False)
    workflow, resolver, proposal, decision, envelope, policy = setup(root, work)
    from engine.local_authority_effect import AtomicAuthorityEffectDestination, AtomicLocalControlPlaneExecutor
    from engine.safe_executor import commitment
    clock = [BASE]
    destination = AtomicAuthorityEffectDestination(root / 'destination', clock=lambda: clock[0])
    executor = AtomicLocalControlPlaneExecutor(workflow=workflow, destination=destination, policy=policy)
    first_claim = executor.provision_claim(proposal=proposal, decision=decision, now=BASE)
    first = executor.execute(envelope=envelope, claim_id=first_claim.claim_id,
                             simulate='lost_ack' if scenario == 'first-unknown' else None)
    events = [{'stage': 'first-result', 'result': dataclasses.asdict(first)}]
    expected_effects = [{'effect_id': envelope.effect_id, 'amount': 50.0, 'state': 'applied'}]
    qualified = (first.status == ('unknown' if scenario == 'first-unknown' else 'executed')
                 and first.effect_id == envelope.effect_id
                 and first.decision_id == decision.decision_id)
    if scenario == 'first-unknown':
        qualified = qualified and first.acknowledged is False
    if scenario in ('cancel-requested', 'first-unknown'):
        # Record a stop for undispatched work only. No cancellation or rollback
        # of the first effect, or permission to retry it, follows from this.
        events.append({'stage': 'continuation-held', 'reason': scenario,
                       'cancellation_requested': scenario == 'cancel-requested',
                       'cessation_verified': False, 'retry_authorized': False})
    elif first.status != 'executed':
        raise RuntimeError('positive first step failed')
    else:
        payload = dict(proposal.payload, refund_reason='second approved installment')
        other = proposal.model_copy(update={'correlation_id': 'second-installment', 'amount': 25.0,
                                            'payload': payload, 'payload_commitment': commitment(payload)})
        context = resolver.contexts[proposal.authority_context_ref]
        original_ref = context['grant']['approval_refs'][0]
        second_ref = original_ref + ':second-step'
        digest = commitment(other.model_dump(mode='json', exclude_none=False))
        resolver.approvals[second_ref] = resolver.approvals[original_ref].model_copy(
            update={'approval_ref': second_ref, 'proposal_commitment': digest})
        context['grant']['approval_refs'] = [second_ref]
        second_decision = workflow.decide(other, now=BASE)
        if second_decision.result != 'authorized':
            raise RuntimeError(str(second_decision.reasons))
        second_envelope = dataclasses.replace(envelope, decision_id=second_decision.decision_id,
             effect_id=second_decision.effect_id, operation=dataclasses.replace(envelope.operation,
             proposal_commitment=digest, amount=25.0, payload=payload, payload_commitment=commitment(payload)))
        second_claim = executor.provision_claim(proposal=other, decision=second_decision, now=BASE)
        if scenario == 'revoked':
            destination.set_grant_status(first_claim.grant_id, status='revoked')
        elif scenario == 'policy-changed':
            destination.set_policy_state(first_claim.policy_state[0].ref, version='changed')
        elif scenario == 'evidence-expired':
            clock[0] += timedelta(seconds=301)
        second = executor.execute(envelope=second_envelope,
                                  claim_id=first_claim.claim_id if scenario == 'reused-claim' else second_claim.claim_id)
        events.append({'stage': 'second-result', 'result': dataclasses.asdict(second),
                       'separate_decision': second_decision.decision_id != decision.decision_id,
                       'separate_claim': second_claim.claim_id != first_claim.claim_id})
        qualified = (qualified and events[-1]['separate_decision'] and events[-1]['separate_claim']
                     and second_envelope.effect_id != envelope.effect_id
                     and second.effect_id == second_envelope.effect_id
                     and second.decision_id == second_decision.decision_id
                     and second.status == ('executed' if scenario == 'allowed' else 'denied'))
        if scenario == 'allowed':
            expected_effects.append({'effect_id': second_envelope.effect_id, 'amount': 25.0, 'state': 'applied'})
    with sqlite3.connect(destination.path) as conn:
        effects = [dict(zip(('effect_id','amount','state'), row)) for row in
                   conn.execute('SELECT effect_id,amount,state FROM effects ORDER BY effect_id')]
    # Compare the complete projected effect set to the independently constructed
    # expected operations. Counts alone cannot qualify the second consequence or
    # preservation of the first committed effect's applied state.
    qualified = qualified and effects == sorted(expected_effects, key=lambda effect: effect['effect_id'])
    report = {'profile': 'two-step-synthetic-refund/1', 'scenario': scenario, 'qualified': qualified,
              'events': events, 'effects': effects, 'remote_atomicity': False,
              'compensation_authorized': False, 'production_ready': False}
    (root / 'trajectory.json').write_text(json.dumps(report, indent=2) + '\n')
    return report
