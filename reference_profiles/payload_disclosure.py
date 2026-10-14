"""Exact-payload disclosure checks for one trusted configured local sink.

This is an additional restriction, not an action grant or a content classifier.
The host binds this gate and callback to the same actual sink. Source labels,
policy resolver, clock and callback are trusted; full mediation is not claimed.
"""
import hashlib
import math
from reference_profiles.context_memory import canonical


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


class PayloadDisclosureGate:
    def __init__(self, *, sink_id, exposure, policy_version, resolve):
        if any(type(v) is not str or not v.strip() for v in (sink_id, exposure, policy_version)) or not callable(resolve):
            raise ValueError('trusted sink, exposure, policy version and resolver required')
        self.sink_id, self.exposure, self.policy_version = sink_id, exposure, policy_version
        self.resolve = resolve

    def check(self, *, content, receipt, purpose, recipient, clock):
        if type(content) is not str or not callable(clock):
            raise ValueError('exact text and trusted clock required')
        binding = {'payload_sha256': hashlib.sha256(content.encode()).hexdigest(),
                   'receipt_sha256': digest(receipt), 'sink_id': self.sink_id,
                   'exposure': self.exposure, 'policy_version': self.policy_version,
                   'purpose': purpose, 'recipient': recipient}
        result = {'contract': 'payload-disclosure-check/1', 'binding': binding,
                  'allowed': False, 'reason': 'POLICY_UNAVAILABLE',
                  'grant_id': None, 'grant_revision': None, 'authorizing_execution': False}
        try:
            # Resolver receives a detached binding; it cannot mutate the checked bytes.
            policy = self.resolve(dict(binding))
        except Exception:
            return result
        fields = {'binding', 'grant_id', 'grant_revision', 'status', 'valid_from', 'expires_at'}
        if (type(policy) is not dict or set(policy) != fields
                or type(policy['grant_id']) is not str or not policy['grant_id'].strip()
                or type(policy['grant_revision']) is not int or policy['grant_revision'] < 0
                or not all(finite(policy[k]) for k in ('valid_from', 'expires_at'))
                or policy['valid_from'] >= policy['expires_at']):
            result['reason'] = 'POLICY_MALFORMED'
            return result
        now = clock()  # Resolver work can outlast the preflight permission lifetime.
        if not finite(now):
            raise ValueError('trusted finite time required')
        result.update(grant_id=policy['grant_id'], grant_revision=policy['grant_revision'])
        if policy['binding'] != binding:
            result['reason'] = 'DISCLOSURE_BINDING_MISMATCH'
        elif policy['status'] == 'revoked':
            result['reason'] = 'DISCLOSURE_REVOKED'
        elif policy['status'] != 'active':
            result['reason'] = 'POLICY_STATUS_UNKNOWN'
        elif not policy['valid_from'] <= now < policy['expires_at']:
            result['reason'] = 'DISCLOSURE_EXPIRED_OR_NOT_YET_VALID'
        else:
            result.update(allowed=True, reason='EXACT_DISCLOSURE_MATCH')
        return result
