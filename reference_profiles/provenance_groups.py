"""Conservative grouping of declared dependencies; never an independence proof."""
from __future__ import annotations

AXES = frozenset({'data_snapshot', 'model_version', 'policy_version', 'retrieval_lineage', 'tool', 'provider'})
CONTRACT = 'declared-provenance-groups/1'


def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('expected a nonblank string')
    return value


def summarize(packet: dict) -> dict:
    """Group connected receipts sharing any selected failure-relevant dependency.

    Unknown lineage is excluded from groups. The caller declares relevant axes and
    their basis; neither that declaration nor the dependencies are authenticated.
    """
    if not isinstance(packet, dict) or set(packet) != {
        'contract', 'claim_ref', 'scenario_ref', 'failure_axes', 'basis_ref', 'receipts'
    } or packet['contract'] != CONTRACT:
        raise ValueError('invalid packet contract')
    for field in ('claim_ref', 'scenario_ref', 'basis_ref'):
        _text(packet[field])
    axes = packet['failure_axes']
    if (not isinstance(axes, list) or not axes or
            any(not isinstance(a, str) or a not in AXES for a in axes) or
            len(set(axes)) != len(axes)):
        raise ValueError('explicit unique failure axes required')
    receipts = packet['receipts']
    if not isinstance(receipts, list):
        raise ValueError('receipts must be a list')
    known, unknown, seen = {}, [], set()
    for receipt in receipts:
        if not isinstance(receipt, dict) or set(receipt) != {'receipt_id', 'dependencies'}:
            raise ValueError('invalid receipt')
        rid = _text(receipt['receipt_id'])
        if rid in seen:
            raise ValueError('duplicate receipt identity')
        seen.add(rid)
        deps = receipt['dependencies']
        if not isinstance(deps, dict) or set(deps) != AXES:
            raise ValueError('declare every provenance axis; use null for unknown')
        for values in deps.values():
            if values is not None:
                if not isinstance(values, list) or not values:
                    raise ValueError('dependency values must be nonempty lists or null')
                for value in values:
                    _text(value)
                if len(set(values)) != len(values):
                    raise ValueError('duplicate dependency identifier')
        if any(deps[a] is None for a in axes):
            unknown.append(rid)
        else:
            known[rid] = {(a, value) for a in axes for value in deps[a]}
    # Connected components avoid counting partially overlapping lineages twice.
    remaining, groups = set(known), []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        members, dependencies = {seed}, set(known[seed])
        while True:
            linked = {rid for rid in remaining if known[rid] & dependencies}
            if not linked:
                break
            remaining -= linked
            members |= linked
            for rid in linked:
                dependencies |= known[rid]
        groups.append({'receipt_ids': sorted(members), 'declared_dependencies': [
            {'axis': a, 'dependency_ref': v} for a, v in sorted(dependencies)
        ]})
    return {
        'contract': CONTRACT, 'claim_ref': packet['claim_ref'],
        'scenario_ref': packet['scenario_ref'], 'basis_ref': packet['basis_ref'],
        'failure_axes': sorted(axes), 'receipt_count': len(receipts),
        'declared_group_count': len(groups), 'groups': groups,
        'unestablished_receipts': sorted(unknown),
        'independence': 'not_established', 'authorizes_action': False,
    }
