"""OG01 supplied-inventory reconciliation; never discovers or authorizes work."""
from collections import Counter

CONTRACT = 'agent-inventory-reconciliation/1'
STATES = {'discovered', 'approved', 'active', 'suspended', 'retiring', 'retired'}


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _time(value):
    return type(value) is int and value >= 0


def reconcile(packet, *, now, max_age):
    """Compare caller-supplied records for one scope using trusted integer UTC seconds.

    Malformed/ambiguous input raises ValueError. Findings and coverage remain separate.
    'No findings' never establishes discovery completeness, authority or deployment safety.
    """
    if not _time(now) or not _time(max_age):
        raise ValueError('now and max_age must be nonnegative integer UTC seconds')
    if not isinstance(packet, dict) or packet.get('contract') != CONTRACT:
        raise ValueError('unsupported contract')
    if not all(_text(packet.get(k)) for k in ('tenant', 'environment')):
        raise ValueError('tenant and environment required')
    start, end = packet.get('window_start'), packet.get('window_end')
    if not _time(start) or not _time(end) or not start <= end <= now:
        raise ValueError('invalid observation window')
    required = packet.get('required_connectors')
    if (not isinstance(required, list) or not required or
            not all(_text(x) for x in required) or len(set(required)) != len(required)):
        raise ValueError('declare unique nonempty required connectors')
    for key in ('connectors', 'agents', 'instances'):
        if not isinstance(packet.get(key), list) or not all(isinstance(x, dict) for x in packet[key]):
            raise ValueError('record lists required')
    scope = {k: packet[k] for k in ('tenant', 'environment')}
    connectors = {}
    for row in packet['connectors']:
        name = row.get('id')
        if not _text(name) or name not in required or name in connectors:
            raise ValueError('unknown or duplicate connector')
        if row.get('status') not in ('complete', 'partial', 'unavailable'):
            raise ValueError('invalid connector status')
        timestamp = row.get('observed_at')
        if not _time(timestamp) or not start <= timestamp <= end:
            raise ValueError('connector observation outside window')
        connectors[name] = row
    incomplete = [name for name in required if name not in connectors or
                  connectors[name]['status'] != 'complete' or
                  now - connectors[name]['observed_at'] > max_age]
    agents = {}
    for row in packet['agents']:
        if any(row.get(k) != v for k, v in scope.items()):
            raise ValueError('agent scope mismatch')
        aid = row.get('agent_id')
        if not _text(aid) or aid in agents or row.get('state') not in STATES:
            raise ValueError('invalid/duplicate logical identity or lifecycle state')
        if not isinstance(row.get('bindings'), list):
            raise ValueError('bindings required')
        seen = set()
        for binding in row['bindings']:
            if (not isinstance(binding, dict) or
                    not all(_text(binding.get(k)) for k in ('instance_id', 'workload_id')) or
                    binding['instance_id'] in seen or
                    not _time(binding.get('valid_from')) or not _time(binding.get('valid_until')) or
                    binding['valid_from'] >= binding['valid_until']):
                raise ValueError('invalid or duplicate binding')
            seen.add(binding['instance_id'])
        agents[aid] = row
    observations = {}
    for row in packet['instances']:
        if any(row.get(k) != v for k, v in scope.items()):
            raise ValueError('instance scope mismatch')
        if not all(_text(row.get(k)) for k in ('agent_id', 'instance_id', 'workload_id', 'release')):
            raise ValueError('observation identities required')
        cid = row.get('connector')
        if not _text(cid) or cid not in connectors or connectors[cid]['status'] == 'unavailable':
            raise ValueError('observation requires available declared connector')
        timestamp = row.get('observed_at')
        if not _time(timestamp) or not start <= timestamp <= end:
            raise ValueError('instance observation outside window')
        # Repeated reports cannot silently overwrite evidence, even across connectors.
        if row['instance_id'] in observations:
            raise ValueError('duplicate observation; caller must reconcile provenance first')
        observations[row['instance_id']] = row
    findings = []

    def add(kind, agent, instance=None):
        findings.append({'kind': kind, 'agent_id': agent, 'instance_id': instance})

    bindings = Counter(b['instance_id'] for a in agents.values() for b in a['bindings'])
    for aid, agent in agents.items():
        if not _text(agent.get('owner')):
            add('missing_owner', aid)
        if not _text(agent.get('backup_owner')):
            add('missing_backup_owner', aid)
        if not _text(agent.get('accepted_release')):
            add('missing_accepted_release', aid)
        if agent['state'] != 'active':
            add('lifecycle_hold', aid)
        for binding in agent['bindings']:
            iid = binding['instance_id']
            if bindings[iid] > 1:
                add('duplicated_instance_binding', aid, iid)
            if not binding['valid_from'] <= now < binding['valid_until']:
                add('binding_not_current', aid, iid)
            if iid not in observations:
                add('registration_not_observed', aid, iid)
    for iid, observed in observations.items():
        aid = observed['agent_id']
        if now - observed['observed_at'] > max_age:
            add('stale_observation', aid, iid)
        agent = agents.get(aid)
        if agent is None:
            add('unregistered_agent', aid, iid)
            continue
        binding = next((b for b in agent['bindings'] if b['instance_id'] == iid), None)
        if binding is None:
            add('unregistered_replica', aid, iid)
        elif binding['workload_id'] != observed['workload_id']:
            add('workload_identity_mismatch', aid, iid)
        if observed['release'] != agent.get('accepted_release'):
            add('release_mismatch', aid, iid)
    return {'contract': CONTRACT, 'scope': scope, 'window_start': start, 'window_end': end,
            'evaluated_at': now, 'max_age': max_age, 'required_connectors': list(required),
            'incomplete_connectors': incomplete,
            'declared_coverage_current': not incomplete,
            'findings': findings, 'authorizing': False, 'deployment_qualified': False,
            'discovery_verified': False,
            'review_status': 'hold' if incomplete or findings else 'no_supplied_discrepancies'}
