"""Allocation-bound regressions for the shared signed wire format."""
import json
from unittest.mock import patch
import pytest
from reference_profiles.trust_evidence import wire
from reference_profiles.protected_destination import ProtectedDestination


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


@pytest.mark.parametrize('value', [None, True, False, 0, -9007199254740991,
    ''.join(map(chr, range(128))), {'b': [True, None, '\\"\x7f'], 'a': {}}])
def test_preserves_signed_bytes(value):
    assert wire(value) == encoded(value)


def test_serializes_containers_only_once():
    value = {'nested': [[{'payload': 'x'}] for _ in range(100)]}
    original = json.dumps
    with patch('reference_profiles.trust_evidence.json.dumps', wraps=original) as dumps:
        assert wire(value) == encoded(value)
        # encoded() is the independent comparison call.
        assert dumps.call_count == 2


def test_aggregate_budget_rejects_before_serialization():
    # Each child meets its local size bound; the combined record does not.
    value = ['x' * 65536] * 17
    with patch('reference_profiles.trust_evidence.json.dumps', side_effect=AssertionError('serialized')):
        with pytest.raises(ValueError, match='bounded record'):
            wire(value)


def test_exact_byte_limit_and_one_byte_over():
    # 16 strings and 15 commas: 16*65536 + 49 = 1048625.
    value = ['x' * 65536] * 15 + ['x' * (65536-49)]
    assert len(wire(value)) == 1048576
    value[-1] += 'x'
    with pytest.raises(ValueError, match='bounded record'):
        wire(value)


def test_escaped_bytes_count_against_budget():
    value = ['\x00' * 65536] * 3
    with patch('reference_profiles.trust_evidence.json.dumps', side_effect=AssertionError('serialized')):
        with pytest.raises(ValueError, match='bounded record'):
            wire(value)


def test_shared_subtrees_count_each_expansion():
    child = ['x' * 65536] * 8
    with pytest.raises(ValueError, match='bounded record'):
        wire([child, child, child])


def test_cycles_and_excess_depth_fail_before_serialization():
    cyclic = []; cyclic.append(cyclic)
    with patch('reference_profiles.trust_evidence.json.dumps', side_effect=AssertionError('serialized')):
        with pytest.raises(ValueError, match='encoding depth'):
            wire(cyclic)


def test_oversize_destination_input_never_opens_database():
    runtime = object.__new__(ProtectedDestination)
    with patch.object(runtime, 'connection', side_effect=AssertionError('database accessed')):
        assert runtime.apply(['x' * 65536] * 17) == {'status': 'denied', 'reason': 'INVALID_REQUEST'}
