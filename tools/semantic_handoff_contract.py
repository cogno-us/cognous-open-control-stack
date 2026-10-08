"""Opt-in structural SH01 reference checker; never an execution authority."""
import hashlib
import json
import math
from datetime import datetime, timezone

PROFILE = 'semantic-handoff/1'
TEXT_FIELDS = ('handoff_id', 'sender', 'receiver', 'tenant', 'task', 'parent',
               'operation', 'goal', 'dictionary_ref', 'context_generation')
LIST_FIELDS = ('read_scope', 'write_scope', 'preconditions', 'completion_criteria',
               'required_evidence', 'restrictions')
CONTRACT_FIELDS = set(TEXT_FIELDS + LIST_FIELDS + ('profile', 'revision', 'deadline', 'terms'))


def _text(value):
    return type(value) is str and bool(value.strip())


def _time(value):
    if not _text(value) or not value.endswith('Z'):
        raise ValueError('UTC deadline must end with Z')
    result = datetime.fromisoformat(value[:-1] + '+00:00')
    if result.utcoffset().total_seconds() != 0:
        raise ValueError('UTC required')
    return result


def _validate(contract):
    if type(contract) is not dict or set(contract) != CONTRACT_FIELDS:
        raise ValueError('exact versioned contract fields required')
    if contract['profile'] != PROFILE:
        raise ValueError('unsupported profile')
    if type(contract['revision']) is not int or contract['revision'] < 1:
        raise ValueError('positive integer revision required')
    if not all(_text(contract[k]) for k in TEXT_FIELDS):
        raise ValueError('nonempty contract identifiers required')
    for key in LIST_FIELDS:
        values = contract[key]
        if type(values) is not list or any(not _text(v) for v in values) or len(set(values)) != len(values):
            raise ValueError('unique explicit lists required')
    if not contract['completion_criteria'] or not contract['required_evidence']:
        raise ValueError('completion criteria and evidence required')
    _time(contract['deadline'])
    terms = contract['terms']
    if type(terms) is not list or not terms:
        raise ValueError('explicit domain terms required')
    names = set()
    for term in terms:
        if type(term) is not dict or set(term) != {'name', 'value', 'unit', 'namespace', 'time_basis', 'uncertainty'}:
            raise ValueError('complete typed terms required')
        if not all(_text(term[k]) for k in ('name', 'unit', 'namespace', 'time_basis', 'uncertainty')):
            raise ValueError('term interpretation metadata required')
        if term['name'] in names:
            raise ValueError('duplicate term')
        names.add(term['name'])
        value = term['value']
        if not (_text(value) or type(value) is int or (type(value) is float and math.isfinite(value))):
            raise ValueError('finite numeric or nonempty textual value required')


def commitment(contract):
    """Hash the full validated contract, preserving all lists and metadata exactly."""
    _validate(contract)
    encoded = json.dumps(contract, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def check_acceptance(proposal, response, *, current_commitment, current_context_generation, now):
    """Check a caller-supplied current proposal and response without dispatching.

    Trusted caller supplies authoritative current commitment/context/time. This
    pure function cannot authenticate identities or prevent a post-check change.
    """
    def result(state, reason):
        return {'profile': PROFILE, 'state': state, 'reason': reason,
                'authorizing': False, 'observed_effect': False}

    try:
        digest = commitment(proposal)
        if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise ValueError('aware trusted time required')
        if digest != current_commitment or proposal['context_generation'] != current_context_generation:
            return result('blocked', 'superseded_contract_or_context')
        if now.astimezone(timezone.utc) >= _time(proposal['deadline']):
            return result('deferred', 'deadline_expired')
        if type(response) is not dict or set(response) != {'kind', 'sender', 'receiver', 'proposal_commitment', 'interpretation', 'mapping'}:
            raise ValueError('exact response fields required')
        if response['sender'] != proposal['receiver'] or response['receiver'] != proposal['sender']:
            return result('blocked', 'party_mismatch')
        if response['proposal_commitment'] != digest:
            return result('blocked', 'stale_response')
        kind = response['kind']
        if kind not in ('acceptance', 'clarification', 'rejection', 'transport_ack', 'progress', 'completion_assertion'):
            raise ValueError('unknown response kind')
        if kind != 'acceptance':
            return result('rejected' if kind == 'rejection' else 'pending', 'not_semantic_acceptance')
        mapping = response['mapping']
        if type(mapping) is not dict or set(mapping) != {'version', 'source_dictionary', 'target_dictionary', 'normalization', 'lost', 'unresolved'}:
            raise ValueError('explicit mapping fields required')
        if not _text(mapping['version']) or mapping['normalization'] != 'identity':
            raise ValueError('only explicit identity mapping supported')
        for key in ('lost', 'unresolved'):
            if type(mapping[key]) is not list or any(not _text(v) for v in mapping[key]):
                raise ValueError('explicit meaning loss lists required')
        if mapping['lost'] or mapping['unresolved']:
            return result('pending', 'meaning_unresolved')
        interpretation = response['interpretation']
        receiver_digest = commitment(interpretation)
        if mapping['source_dictionary'] != proposal['dictionary_ref'] or mapping['target_dictionary'] != interpretation['dictionary_ref']:
            return result('blocked', 'dictionary_mismatch')
        if receiver_digest != digest:
            return result('pending', 'interpretation_mismatch')
        return dict(result('accepted', 'exact_contract_agreement'), commitment=digest)
    except (ValueError, TypeError, KeyError, OverflowError):
        return result('blocked', 'malformed_contract_or_response')
