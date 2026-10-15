"""Consumer-owned evidence acceptance; signatures establish attribution, not truth.

Wire profile: domain-separated ASCII JSON, safe integers, no floats. Not RFC8785.
No execution authority is returned. Keys and resolver inputs are trusted inputs.
"""
import hashlib
import json
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def wire(value, depth=0):
    """Validate the total encoding budget before serializing any container.

    Count repeated references each time: they expand independently in JSON.
    Container cycles fail the depth bound. Bytes remain identical to trust/1.
    """
    remaining = 1048576

    def charge(size):
        nonlocal remaining
        remaining -= size
        if remaining < 0:
            raise ValueError('bounded record required')

    def visit(item, level):
        if level > 20:
            raise ValueError('encoding depth')
        if item is None or type(item) is bool:
            charge(4 if item is None or item is True else 5)
        elif type(item) is int:
            if abs(item) > 9007199254740991:
                raise ValueError('unsafe integer')
            charge(len(str(item)))
        elif type(item) is str:
            if len(item) > 65536 or not item.isascii():
                raise ValueError('ASCII text required')
            # ASCII control characters, quotes and backslashes are escaped.
            charge(2)
            for char in item:
                charge(2 if char in '\"\\\b\f\n\r\t' else 6 if ord(char) < 32 or ord(char) == 127 else 1)
        elif type(item) is list:
            if len(item) > 1024:
                raise ValueError('bounded list required')
            charge(2 + max(0, len(item)-1))
            for child in item:
                visit(child, level+1)
        elif type(item) is dict:
            if len(item) > 256 or any(type(k) is not str for k in item):
                raise ValueError('bounded object required')
            charge(2 + max(0, len(item)-1) + len(item))
            for key, child in item.items():
                visit(key, level+1)
                visit(child, level+1)
        else:
            raise ValueError('unsupported wire type')

    visit(value, depth)
    return json.dumps(value,sort_keys=True,separators=(',', ':'),ensure_ascii=True,allow_nan=False).encode()


def commitment(value): return hashlib.sha256(wire(value)).hexdigest()


def signed(private_key, issuer, kind, body):
    """Client helper: private key never passed to a verifier/runtime."""
    record={'contract':'cognous-trust/1','issuer':issuer,'kind':kind,'body':body}
    return dict(record,signature=private_key.sign(b'COGNOUS-TRUST/1\0'+wire(record)).hex())


def verify(record, registry, *, at, now, current=True):
    """Registry status times must be independently anchored; self timestamps are not proof."""
    if type(record) is not dict or set(record)!={'contract','issuer','kind','body','signature'}:
        raise ValueError('malformed signed record')
    if record['contract']!='cognous-trust/1': raise ValueError('contract')
    if type(at) is not int or type(now) is not int or at<0 or now<0: raise ValueError('integer time required')
    key=registry.get(record['issuer'])
    if key is None: raise ValueError('unknown issuer')
    if not (key['not_before']<=at<key['expires_at']) or at>now: raise ValueError('key time')
    if key['revoked_at'] is not None and (at>=key['revoked_at'] or (current and now>=key['revoked_at'])):
        raise ValueError('key revoked')
    if current and now>=key['expires_at']: raise ValueError('key expired')
    payload={k:v for k,v in record.items() if k!='signature'}
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(key['public_key'])).verify(bytes.fromhex(record['signature']),b'COGNOUS-TRUST/1\0'+wire(payload))
    except (InvalidSignature, ValueError, TypeError) as exc:
        raise ValueError('invalid signature') from exc
    return record['body']


def verdict(failures, missing):
    return {'verdict':'INVALID' if failures else 'INDETERMINATE' if missing else 'VALID',
            'failures':sorted(set(failures)),'missing':sorted(set(missing)),'authorizing':False}


def assess_envelope(envelope, policy, registry, evidence, *, now, historical=False):
    """Offline relying party: no producer DB, private keys, network or effect interface.

    Policy supplies exact manifest commitment and required claim identities; each
    claim requires a consumer-owned evidence commitment. Missing is never a pass.
    """
    failures=[]; missing=[]
    try:
        wire(envelope)
        if set(envelope)!={'manifest','attestations','disclosure'}: raise ValueError('envelope schema')
        manifest_record=envelope['manifest']; m=manifest_record['body']
        if set(m)!={'id','version','producer_domain','consumer_domain','subject','action','resource','audience','purpose','at','expires_at','predecessor'}:
            raise ValueError('manifest schema')
        if type(m['version']) is not int or m['version']<1 or type(m['expires_at']) is not int or m['expires_at']<=m['at']: raise ValueError('manifest interval/version')
        verify(manifest_record,registry,at=m['at'],now=now,current=not historical)
        if manifest_record['kind']!='manifest' or manifest_record['issuer']!=policy['manifest_issuer']: failures.append('MANIFEST_ISSUER')
        if commitment(m)!=policy['manifest_digest']: failures.append('MANIFEST_CHANGED')
        for field in ('audience','purpose','consumer_domain','subject','action','resource'):
            if m[field]!=policy[field]: failures.append('SCOPE_'+field.upper())
        if m['producer_domain']==m['consumer_domain']: failures.append('NO_ADMINISTRATIVE_BOUNDARY')
        if not historical and now>=m['expires_at']: failures.append('MANIFEST_EXPIRED')
        view=envelope['disclosure']
        if set(view)!={'included','omitted','purpose','audience'}: raise ValueError('disclosure schema')
        if view['audience']!=policy['audience'] or view['purpose']!=policy['purpose']: failures.append('DISCLOSURE_SCOPE')
        ids=[]; found={}
        for record in envelope['attestations']:
            b=record['body']; identity=b['id']; ids.append(identity)
            if identity in found: failures.append('DUPLICATE_ATTESTATION')
            found[identity]=record
            if set(b)!={'id','manifest_digest','event','parents','evidence','evidence_digest','at','expires_at','status'}:
                failures.append('ATTESTATION_SCHEMA'); continue
            if type(b['parents']) is not list or len(b['parents'])!=len(set(b['parents'])) or identity in b['parents'] or type(b['expires_at']) is not int or b['expires_at']<=b['at']:
                failures.append('ATTESTATION_INTERVAL_OR_PARENTS'); continue
            try: verify(record,registry,at=b['at'],now=now,current=not historical)
            except (ValueError,TypeError,KeyError): failures.append('ATTESTATION_SIGNATURE'); continue
            if b['manifest_digest']!=commitment(m): failures.append('ATTESTATION_MANIFEST')
            if b['status']!='asserted': failures.append('ADVERSE_STATUS')
            if not historical and now>=b['expires_at']: failures.append('ATTESTATION_EXPIRED')
            if b['at']<m['at'] or b['at']>=m['expires_at']: failures.append('EVENT_TIME')
            requirement=policy['required'].get(identity)
            if requirement is None: failures.append('UNEXPECTED_ATTESTATION'); continue
            if record['issuer']!=requirement['issuer'] or record['kind']!=requirement['kind'] or b['event']!=requirement['event'] or b['parents']!=requirement['parents']:
                failures.append('CLAIM_BINDING')
            if b['evidence_digest']!=requirement['evidence_digest']: failures.append('EVIDENCE_COMMITMENT')
            resolved=evidence.get(b['evidence'])
            if resolved is None: missing.append('EVIDENCE_'+identity)
            elif commitment(resolved)!=requirement['evidence_digest']: failures.append('EVIDENCE_CONTRADICTION')
        if set(view['included'])!=set(ids) or len(view['included'])!=len(ids): failures.append('DISCLOSURE_CONTENTS')
        if set(view['included']) & set(view['omitted']): failures.append('DISCLOSURE_OVERLAP')
        if set(view['included'])-set(policy['allowed']): failures.append('OVER_DISCLOSURE')
        for identity in policy['required']:
            if identity not in found: missing.append('ATTESTATION_'+identity)
        for record in found.values():
            for parent in record['body'].get('parents',[]):
                if parent not in found: missing.append('PARENT_'+parent)
                elif found[parent]['body']['at']>record['body']['at']: failures.append('CAUSAL_TIME')
        # A declared omission is a gap, not an implicitly satisfied claim.
        if set(view['omitted']) != set(policy['required'])-set(ids): failures.append('OMISSION_DECLARATION')
    except (ValueError,TypeError,KeyError,OverflowError,AttributeError):
        failures.append('MALFORMED_OR_UNVERIFIABLE')
    return dict(verdict(failures,missing),inspection_time=now,mode='historical' if historical else 'current')


def work_report(entries, completed):
    categories={'review','exception','verification','correction','support'}
    if type(completed) is not int or completed<0: raise ValueError('invalid denominator')
    totals={k:0 for k in categories}; seen=set()
    for entry in entries:
        if set(entry)!={'id','category','minutes'} or entry['id'] in seen or entry['category'] not in categories or type(entry['minutes']) is not int or entry['minutes']<0:
            raise ValueError('invalid work record')
        seen.add(entry['id']); totals[entry['category']]+=entry['minutes']
    observed={e['category'] for e in entries}; complete=observed==categories
    return {'complete':complete,'missing_categories':sorted(categories-observed),'minutes':totals,
            'completed_outputs':completed,'minutes_per_output':sum(totals.values())/completed if complete and completed else None,
            'substitution_established':False}
