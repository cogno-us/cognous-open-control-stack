"""Separately authorized synthetic notification outbox; no external message delivery."""
from contextlib import closing
import copy
import json
from pathlib import Path
import sqlite3
from tools.optional_execution import BASE, setup

ADAPTER = 'urn:cognous:adapter:synthetic-notification-v1'
ACTION = 'urn:cognous:action:refund-notification-v1'
TARGET = 'urn:cognous:synthetic-inbox:customer-001'
GRANT = 'urn:cognous:grant:notification-1'


class NotificationOutbox:
    def __init__(self, path, *, refund_database, clock):
        self.path, self.refund_database, self.clock = Path(path).resolve(), Path(refund_database).resolve(), clock
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS notifications (effect_id TEXT PRIMARY KEY, grant_id TEXT, target TEXT, amount REAL, unit TEXT, payload TEXT, state TEXT)')
            conn.commit()

    def apply(self, *, effect_id, grant_id, max_effects, target, amount, unit, payload, lose_ack=False, partial=False):
        if (target != TARGET or amount != 1 or unit != 'message' or type(max_effects) is not int or max_effects != 1
                or partial or set(payload) != {'customer_id','refund_effect_id','message'}
                or any(type(v) is not str or not v for v in payload.values())):
            raise PermissionError('notification contract mismatch')
        with closing(sqlite3.connect(self.refund_database.as_uri() + '?mode=ro', uri=True)) as source:
            row = source.execute('SELECT state,payload_json FROM effects WHERE effect_id=?', (payload['refund_effect_id'],)).fetchone()
            if row is None or row[0] != 'applied' or json.loads(row[1])['customer_id'] != payload['customer_id']:
                raise PermissionError('committed refund prerequisite missing')
        encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        with closing(sqlite3.connect(self.path, isolation_level=None)) as conn:
            conn.execute('BEGIN IMMEDIATE')
            prior = conn.execute('SELECT grant_id,target,amount,unit,payload FROM notifications WHERE effect_id=?', (effect_id,)).fetchone()
            if prior is not None:
                if prior != (grant_id,target,amount,unit,encoded):
                    raise PermissionError('notification identity substitution')
                duplicate = True
            else:
                if conn.execute('SELECT count(*) FROM notifications WHERE grant_id=?', (grant_id,)).fetchone()[0] >= max_effects:
                    raise PermissionError('notification grant budget exhausted')
                conn.execute('INSERT INTO notifications VALUES (?,?,?,?,?,?,?)', (effect_id,grant_id,target,amount,unit,encoded,'applied'))
                duplicate = False
            conn.commit()
        if lose_ack:
            raise TimeoutError('notification outbox acknowledgement lost')
        return {'duplicate': duplicate, 'effect': self.observe(effect_id).destination_state}

    def observe(self, effect_id):
        from agent_control_plane.bounded import EffectObservation
        with closing(sqlite3.connect(self.path)) as conn:
            row = conn.execute('SELECT grant_id,target,amount,unit,payload,state FROM notifications WHERE effect_id=?', (effect_id,)).fetchone()
        state = {} if row is None else dict(effect_id=effect_id,grant_id=row[0],target=row[1],amount=row[2],unit=row[3],payload=json.loads(row[4]),state=row[5])
        return EffectObservation(effect_id=effect_id, observed_at=self.clock().isoformat(), state='absent' if row is None else row[5], destination_state=state)

    def count(self):
        with closing(sqlite3.connect(self.path)) as conn:
            return conn.execute('SELECT count(*) FROM notifications').fetchone()[0]


def notification_case(root, work):
    from engine.local_authority_effect import AtomicAuthorityEffectDestination, AtomicLocalControlPlaneExecutor
    from engine.safe_executor import commitment
    from experiments.odex_gax_imx_reference.synthetic_fixture import build_synthetic_resolver, synthetic_observation_policy
    from agent_control_plane.bounded import BoundedAuthorizationWorkflow, BoundedRecordStore
    workflow, resolver, proposal, decision, envelope, policy = setup(root, work)
    refund = AtomicAuthorityEffectDestination(root / 'refund', clock=lambda: BASE)
    executor = AtomicLocalControlPlaneExecutor(workflow=workflow, destination=refund, policy=policy)
    claim = executor.provision_claim(proposal=proposal, decision=decision, now=BASE)
    result = executor.execute(envelope=envelope, claim_id=claim.claim_id)
    if result.status != 'executed': raise RuntimeError('refund prerequisite failed')
    manifest = copy.deepcopy(workflow.manifest)
    manifest.update(manifest_id='synthetic-refund-notification-v1', agent_name='Synthetic notification reference')
    manifest['tools'] = [dict(tool_name='notification_outbox', adapter_id=ADAPTER, allowed=True, description='Local synthetic outbox only')]
    action = copy.deepcopy(manifest['actions'][0])
    action.update(action_name='refund_notify', action_id=ACTION, tool_name='notification_outbox', description='Append one authorized synthetic notification to a local outbox')
    action['authority_required'] = [dict(scope='refund.notify', required=True)]
    action['payload_policy'] = dict(required_fields=['customer_id','refund_effect_id','message'], optional_fields=[], forbidden_fields=[])
    action['target_policy'] = dict(allowed_targets=[TARGET], allow_any_target=False)
    action['effect_limits'] = dict(max_amount=1, unit='message', max_effects=1)
    action['authority_context']['requirement_id'] = 'urn:cognous:requirement:notification-v1'
    manifest['actions'] = [action]
    payload = dict(customer_id='customer-001', refund_effect_id=decision.effect_id, message='Synthetic refund recorded')
    p = proposal.model_copy(update=dict(manifest_id=manifest['manifest_id'],manifest_digest=commitment(manifest),action_id=ACTION,
        adapter_id=ADAPTER,requirement_id=action['authority_context']['requirement_id'],target=TARGET,amount=1.0,unit='message',
        payload=payload,payload_commitment=commitment(payload),requested_permissions=['refund.notify']))
    authority = build_synthetic_resolver(p, now=BASE)
    context = authority.contexts[p.authority_context_ref]
    permission = dict(action='refund_notify',targets=[TARGET],data_scopes=['refund.notify'],max_amount=1,unit='message',max_effects=1)
    context['requirement']['permissions'] = [copy.deepcopy(permission)]
    context['grant']['permissions'] = [copy.deepcopy(permission)]
    old = context['grant']['grant_id']
    context['grant']['grant_id'] = GRANT
    context['grant']['status_ref'] = 'urn:cognous:status:notification-grant'
    authority.statuses[GRANT] = authority.statuses.pop(old).model_copy(update=dict(grant_id=GRANT,status_ref=context['grant']['status_ref']))
    ref = context['grant']['approval_refs'][0]
    new_ref = 'urn:cognous:approval:notification-1'
    approval = authority.approvals.pop(ref)
    context['grant']['approval_refs'] = [new_ref]
    policy_ref, version = 'urn:cognous:policy:synthetic-notification-v1', 'notification-policy-v1'
    old_policy = next(iter(authority.policies))
    authority.policies = {policy_ref: authority.policies[old_policy].model_copy(update=dict(ref=policy_ref,version=version))}
    policy_versions = [dict(ref=policy_ref,version=version)]
    context['requirement']['governing_sources'] = policy_versions
    context['grant']['policy_versions'] = policy_versions
    context['conflicts']['precedence_refs'] = [policy_ref]
    authority.approvals[new_ref] = approval.model_copy(update=dict(approval_ref=new_ref,grant_id=GRANT,policy_versions=policy_versions))
    for key,value in authority.conflicts.items():
        authority.conflicts[key] = value.model_copy(update=dict(conflict_refs=[policy_ref]))
    destination = NotificationOutbox(root / 'outbox.sqlite3', refund_database=refund.path, clock=lambda: BASE)
    notification = BoundedAuthorizationWorkflow(manifest=manifest,resolver=authority,destination=destination,
        records=BoundedRecordStore(root / 'notification-records.json','notification-run'),observation_policy=synthetic_observation_policy())
    d = notification.decide(p, now=BASE)
    if d.result != 'authorized': raise RuntimeError(str(d.reasons))
    return notification, authority, destination, p, d, refund, decision
