"""SEC02: admission budgets precede hashing and preserve existing encodings."""
from dataclasses import replace
import json
import math
from unittest.mock import patch
import pytest
from reference_profiles.bounded_json import Budget, snapshot
from reference_profiles import resolver_assurance as resolver, context_evidence as evidence, context_journal as journal

@pytest.mark.parametrize('field', ['max_bytes','max_depth','max_nodes','max_items','max_fields','max_string'])
@pytest.mark.parametrize('bad', [0,-1,True,1.5])
def test_reject_invalid_trusted_configuration(field,bad):
    with pytest.raises(ValueError):Budget(**{field:bad})

@pytest.mark.parametrize('field,limit,valid,invalid', [
    ('max_bytes',5,'abc','abcd'),
    ('max_depth',2,[[0]],[[[0]]]),
    ('max_nodes',3,[0,0],[0,0,0]),
    ('max_items',2,[0,0],[0,0,0]),
    ('max_fields',1,{'a':0},{'a':0,'b':0}),
    ('max_string',3,'abc','abcd'),
])
def test_exact_and_one_over(field,limit,valid,invalid):
    budget=Budget(**{field:limit})
    assert snapshot(valid,budget=budget)==valid
    with pytest.raises(ValueError):snapshot(invalid,budget=budget)

@pytest.mark.parametrize('value', [None,True,1,1.25,'é😀\n',{'b':[False,0],'a':'x'}])
def test_snapshots_preserve_existing_canonical_bytes(value):
    detached=snapshot(value)
    assert resolver.canonical(value)==resolver.canonical(detached)
    assert evidence.canonical(value)==evidence.canonical(detached)

@pytest.mark.parametrize('value', [set(),b'bytes',float('nan'),float('inf'),2**100,'\ud800'])
def test_unsupported_values_rejected(value):
    with pytest.raises(ValueError):snapshot(value)

def test_cycles_and_shared_expansion():
    cyclic=[];cyclic.append(cyclic)
    with pytest.raises(ValueError):snapshot(cyclic)
    with pytest.raises(ValueError):snapshot(['x'*65536]*17)
    source={'child':[1]};detached=snapshot(source);source['child'].append(2)
    assert detached=={'child':[1]}

def test_default_exact_byte_limit():
    value=['x'*65536]*15+['x'*(65536-49)]
    assert len(json.dumps(value,separators=(',',':')).encode())==1048576
    assert snapshot(value)==value
    value[-1]+='x'
    with pytest.raises(ValueError):snapshot(value)

@pytest.mark.parametrize('value', ['x'*65537,{'nested':[[[[[[[[[[[[[[[[[[[[[[0]]]]]]]]]]]]]]]]]]]]]]},['x'*65536]*17,list(range(4097)),{str(i):i for i in range(257)}])
def test_all_three_verifiers_reject_before_expensive_operations(value):
    with patch.object(resolver,'canonical',side_effect=AssertionError('canonicalized')):
        assert resolver._check(None,{'observation':{'bad':value},'mac':'0'*64},0)==('UNAUTHENTICATED',None)
    with patch.object(evidence,'digest',side_effect=AssertionError('hashed')):
        with pytest.raises(ValueError):evidence.verify_context_evidence({'payload':{'bad':value},'sha256':'0'*64},binding_id='b',envelope_digest='e',claim_id='c',effect_id='f')
    events=[{'seq':1,'kind':'k','item_id':'i','detail':{'bad':value}}]
    with patch.object(journal,'canonical',side_effect=AssertionError('canonicalized')):
        result=journal.assess_context_journal({'contract':'context-journal/1','events':events,'limits':journal.LIMITS},expected_count=1,checkpoint={'count':0,'sha256':'0'*64})
    assert result['record_coverage']=='violated'

def test_count_mismatch_does_not_visit_event_detail():
    class Unreadable(dict):
        def __iter__(self):raise AssertionError('visited')
    with patch.object(journal,'canonical',side_effect=AssertionError('canonicalized')):
        result=journal.assess_context_journal({'contract':'context-journal/1','events':[Unreadable()],'limits':journal.LIMITS},expected_count=0,checkpoint={'count':0,'sha256':'0'*64})
    assert result['record_coverage']=='violated'

def test_matching_count_still_checks_tail():
    events=[{'seq':1,'kind':'k','item_id':'i','detail':{'bad':set()}}]
    result=journal.assess_context_journal({'contract':'context-journal/1','events':events,'limits':journal.LIMITS},expected_count=1,checkpoint={'count':0,'sha256':journal.prefix_digest([])})
    assert result['record_coverage']=='violated'
