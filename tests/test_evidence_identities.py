"""SEC03/04: identity types fail before crypto; duplicates skip expensive work."""
from copy import deepcopy
from unittest.mock import patch
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from reference_profiles import trust_evidence as trust


def fixture():
    key=Ed25519PrivateKey.generate()
    registry={'issuer':{'not_before':0,'expires_at':300,'revoked_at':None,'public_key':key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()}}
    m=dict(id='m',version=1,producer_domain='a',consumer_domain='b',subject='agent',action='act',resource='r',audience='review',purpose='audit',at=100,expires_at=200,predecessor=None)
    evidence={'e':{'observed':True}}
    b=dict(id='claim',manifest_digest=trust.commitment(m),event='event',parents=[],evidence='e',evidence_digest=trust.commitment(evidence['e']),at=100,expires_at=200,status='asserted')
    envelope={'manifest':trust.signed(key,'issuer','manifest',m),'attestations':[trust.signed(key,'issuer','claim',b)],'disclosure':{'included':['claim'],'omitted':[],'purpose':'audit','audience':'review'}}
    policy={k:m[k] for k in ('audience','purpose','consumer_domain','subject','action','resource')}
    policy.update(manifest_issuer='issuer',manifest_digest=trust.commitment(m),allowed=['claim'],required={'claim':{'issuer':'issuer','kind':'claim','event':'event','parents':[],'evidence_digest':b['evidence_digest']}})
    return envelope,policy,registry,evidence

@pytest.mark.parametrize('bad',[True,False,1,0,None,'','x'*201,[],{}])
@pytest.mark.parametrize('position',['attestation','parent','evidence_ref','included','omitted','allowed','policy_parent','manifest_id','issuer','policy_key','evidence_key','registry_key'])
def test_identity_positions_reject_before_crypto(bad,position):
    env,p,r,e=fixture()
    if position=='attestation':env['attestations'][0]['body']['id']=bad
    elif position=='parent':env['attestations'][0]['body']['parents']=[bad]
    elif position=='evidence_ref':env['attestations'][0]['body']['evidence']=bad
    elif position in ('included','omitted'):env['disclosure'][position]=[bad]
    elif position=='allowed':p['allowed']=[bad]
    elif position=='policy_parent':p['required']['claim']['parents']=[bad]
    elif position=='manifest_id':env['manifest']['body']['id']=bad
    elif position=='issuer':env['manifest']['issuer']=bad
    else:
        mapping={'policy_key':p['required'],'evidence_key':e,'registry_key':r}[position]
        if type(bad) in (dict,list):
            # Unhashable keys cannot be constructed in Python; test the same
            # value at a policy reference position instead.
            p['allowed']=[bad]
        else:mapping[bad]=next(iter(mapping.values()))
    with patch.object(trust,'verify',side_effect=AssertionError('signature work')):
        result=trust.assess_envelope(env,p,r,e,now=100)
    assert result['verdict']=='INVALID' and result['authorizing'] is False


def test_valid_and_distinct_string_identities():
    env,p,r,e=fixture()
    assert trust.assess_envelope(env,p,r,e,now=100)['verdict']=='VALID'
    # This remains a missing distinct identity, never an alias of claim.
    p['required']['Claim']=deepcopy(p['required']['claim'])
    env['disclosure']['omitted']=['Claim']
    result=trust.assess_envelope(env,p,r,e,now=100)
    assert result['verdict']=='INDETERMINATE' and 'ATTESTATION_Claim' in result['missing']

@pytest.mark.parametrize('conflicting',[False,True])
def test_duplicates_never_repeat_signature_or_commitment_work(conflicting):
    env,p,r,e=fixture()
    duplicate=deepcopy(env['attestations'][0])
    if conflicting:duplicate['body']['evidence_digest']='0'*64
    env['attestations'].extend([duplicate]*100)
    with patch.object(trust,'verify',wraps=trust.verify) as verify,patch.object(trust,'commitment',wraps=trust.commitment) as commitment:
        result=trust.assess_envelope(env,p,r,e,now=100)
    assert result['verdict']=='INVALID' and 'DUPLICATE_ATTESTATION' in result['failures']
    assert verify.call_count==2 # manifest and unique attestation
    assert commitment.call_count==3 # manifest policy, unique binding, unique evidence
