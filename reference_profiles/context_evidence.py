"""Non-authorizing context lineage export; no raw content or external custody claim."""
import hashlib
import json
import math
from reference_profiles.context_memory import canonical
from reference_profiles.bounded_json import snapshot


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def receipt_commitment(receipt):
    # Accepted executor commitment format, including Unicode encoding and prefix.
    encoded = json.dumps(receipt, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=False, allow_nan=False).encode('utf-8')
    return 'sha256:' + hashlib.sha256(encoded).hexdigest()


LIMITS = {
    'authorizing': False, 'model_reliance_verified': False,
    'independent_custody_verified': False, 'physical_erasure_verified': False,
    'consumer_chain_qualified': False, 'production_ready': False,
}


def export_context_evidence(memory, *, binding_id, envelope_digest, claim_id, effect_id):
    # One read transaction prevents mixed generations during export. It does
    # not snapshot the separate destination or authenticate a hostile writer.
    with memory.connection() as conn:
        conn.execute('BEGIN')
        binding = conn.execute('SELECT * FROM context_actions WHERE id=?', (binding_id,)).fetchone()
        if (binding is None or binding['envelope_digest'] != envelope_digest
                or binding['claim_id'] != claim_id):
            raise PermissionError('evidence binding mismatch')
        delivery = conn.execute('SELECT * FROM deliveries WHERE id=?', (binding['delivery_id'],)).fetchone()
        if delivery is None:
            raise ValueError('delivery evidence missing')
        item = conn.execute('SELECT receipt, status FROM items WHERE id=?', (delivery['item_id'],)).fetchone()
        if item is None:
            raise ValueError('receipt missing')
        results = []
        for event in conn.execute("SELECT detail FROM events WHERE kind='bound_action_result' AND item_id=? ORDER BY seq", (delivery['item_id'],)):
            value = json.loads(event['detail'])
            if value.get('binding_id') == binding_id:
                results.append(value)
        payload = {
            'schema_version': 'context-action-evidence/1', 'effect_id': effect_id,
            'binding': dict(binding), 'delivery': dict(delivery),
            'receipt': json.loads(item['receipt']), 'item_status': item['status'],
            'result': results[0] if len(results) == 1 else None,
            'result_count': len(results),
            'limits': dict(LIMITS),
        }
    package = {'payload': payload, 'sha256': digest(payload)}
    verify_context_evidence(package, binding_id=binding_id,
                            envelope_digest=envelope_digest, claim_id=claim_id, effect_id=effect_id)
    return package


def verify_context_evidence(package, *, binding_id, envelope_digest, claim_id, effect_id, expected_digest=None):
    """Check integrity and lineage against caller-held identities.

    expected_digest must come from a separately retained checkpoint to detect
    coherent replacement. Matching it proves byte commitment, not authenticity,
    freshness, custody independence, factual truth or a live destination effect.
    """
    try:
        if type(package) is not dict or len(package) != 2 or set(package) != {'payload', 'sha256'}:
            raise ValueError('invalid context package')
        payload = snapshot(package['payload'])
        expected_payload = {'schema_version', 'effect_id', 'binding', 'delivery', 'receipt',
                            'item_status', 'result', 'result_count', 'limits'}
        if type(payload) is not dict or set(payload) != expected_payload:
            raise ValueError('non-exact context payload')
        actual = digest(payload)
        if (package['sha256'] != actual or (expected_digest is not None and expected_digest != actual)
                or payload['schema_version'] != 'context-action-evidence/1'
                or payload['limits'] != LIMITS or payload['effect_id'] != effect_id):
            raise ValueError('unsupported or changed evidence')
        binding, delivery, receipt = payload['binding'], payload['delivery'], payload['receipt']
        for value, expected in (
            (binding, {'id', 'delivery_id', 'generation', 'envelope_digest', 'claim_id', 'state', 'receipt_digest'}),
            (delivery, {'id', 'item_id', 'generation', 'purpose', 'recipient', 'state'}),
        ):
            if type(value) is not dict or set(value) != expected:
                raise ValueError('non-exact lineage record')
            if any(type(v) is not str or not v for k, v in value.items() if k != 'generation'):
                raise ValueError('lineage identities must be nonempty strings')
            if type(value['generation']) is not int or value['generation'] < 0:
                raise ValueError('invalid lineage generation')
        if any(type(v) is not str or not v for v in (binding_id, envelope_digest, claim_id, effect_id)):
            raise ValueError('trusted identities must be strings')
        receipt_fields = {'version', 'item_id', 'content_sha256', 'purposes', 'recipients',
                          'obligations', 'expires_at', 'source_ref', 'parents', 'authorizing'}
        if (set(receipt) != receipt_fields or receipt['version'] != 'context-memory/1'
                or type(receipt['item_id']) is not str or not receipt['item_id']
                or type(receipt['content_sha256']) is not str or len(receipt['content_sha256']) != 64
                or any(c not in '0123456789abcdef' for c in receipt['content_sha256'])
                or not isinstance(receipt['source_ref'], str) or not receipt['source_ref']
                or type(receipt['expires_at']) not in (int, float) or not math.isfinite(receipt['expires_at'])
                or type(binding['generation']) is not int or type(delivery['generation']) is not int
                or payload['item_status'] not in ('admitted', 'revoked', 'expired')
                or type(payload['result_count']) is not int
                or any(type(payload['limits'].get(k)) is not bool for k in LIMITS)):
            raise ValueError('invalid receipt or evidence metadata')
        for field in ('purposes', 'recipients', 'obligations', 'parents'):
            values = receipt[field]
            if (type(values) is not list or (field != 'parents' and not values)
                    or any(type(v) is not str or not v for v in values)):
                raise ValueError('invalid receipt labels')
        if (binding['id'] != binding_id or binding['envelope_digest'] != envelope_digest
                or binding['claim_id'] != claim_id or binding['delivery_id'] != delivery['id']
                or binding['generation'] != delivery['generation'] or delivery['state'] != 'delivered'
                or delivery['item_id'] != receipt['item_id'] or binding['receipt_digest'] != receipt_commitment(receipt)
                or receipt['authorizing'] is not False
                or delivery['purpose'] not in receipt['purposes']
                or delivery['recipient'] not in receipt['recipients']):
            raise ValueError('context lineage mismatch')
        state, result = binding['state'], payload['result']
        if state not in ('issued', 'started', 'finished'):
            raise ValueError('unknown binding state')
        if state != 'finished':
            if result is not None or payload['result_count'] != 0:
                raise ValueError('premature outcome')
            outcome = 'not_started' if state == 'issued' else 'unknown'
        else:
            if (payload['result_count'] != 1 or type(result) is not dict
                    or set(result) != {'binding_id', 'effect_id', 'status', 'attempted', 'acknowledged', 'observed_state'}
                    or result['binding_id'] != binding_id or result['effect_id'] != effect_id
                    or type(result['attempted']) is not bool or type(result['acknowledged']) is not bool):
                raise ValueError('complete unique outcome required')
            status, observed = result['status'], result['observed_state']
            if status not in ('executed', 'partial', 'denied', 'unknown'):
                raise ValueError('unknown result status')
            if observed not in ('applied', 'partial', 'absent', 'unknown'):
                raise ValueError('unknown observation state')
            if status in ('executed', 'partial'):
                if (not result['attempted'] or not result['acknowledged']
                        or observed != ('applied' if status == 'executed' else 'partial')):
                    raise ValueError('unsupported success claim')
            if status == 'denied' and (result['attempted'] or result['acknowledged'] or observed != 'unknown'):
                raise ValueError('inconsistent denial')
            if status == 'unknown' and result['acknowledged']:
                raise ValueError('inconsistent uncertainty')
            outcome = status
        return {'integrity_verified': True, 'lineage_verified': True,
                'checkpoint_matched': expected_digest is not None,
                'recorded_outcome': outcome, **LIMITS}
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError('incomplete context evidence') from exc
