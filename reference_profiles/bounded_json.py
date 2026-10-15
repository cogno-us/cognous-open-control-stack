"""Bounded detached JSON inputs for synthetic reference verifiers.

This is an admission budget, not a new canonical wire format. Valid JSON bytes
remain the responsibility of each existing canonical encoder. Hosts must cap
incoming bytes before decoding; these helpers accept already allocated values.
"""
from dataclasses import dataclass, fields
import json
import math


@dataclass(frozen=True)
class Budget:
    max_bytes: int = 1048576
    max_depth: int = 20
    max_nodes: int = 16384
    max_items: int = 4096
    max_fields: int = 256
    max_string: int = 65536

    def __post_init__(self):
        if any(type(getattr(self, f.name)) is not int or getattr(self, f.name) <= 0 for f in fields(self)):
            raise ValueError('positive integer JSON budgets required')


DEFAULT_BUDGET = Budget()


def snapshot(value, *, budget=DEFAULT_BUDGET):
    """Stop within each trusted budget and detach exactly the values inspected.

    Only built-in JSON types are accepted. Shared references are charged for
    every occurrence, cycles fail the depth bound, and Unicode stays unchanged.
    Byte accounting uses the conservative ASCII JSON representation so it also
    bounds the existing UTF-8 canonical format. No full container is serialized.
    """
    if type(budget) is not Budget:
        raise ValueError('typed trusted JSON budget required')
    remaining = budget.max_bytes
    nodes = 0

    def charge(n):
        nonlocal remaining
        remaining -= n
        if remaining < 0:
            raise ValueError('JSON byte budget exceeded')

    def visit(item, depth):
        nonlocal nodes
        nodes += 1
        if nodes > budget.max_nodes or depth > budget.max_depth:
            raise ValueError('JSON node or depth budget exceeded')
        kind = type(item)
        if kind is str:
            if len(item) > budget.max_string:
                raise ValueError('JSON string budget exceeded')
            charge(2)
            for char in item:
                n = ord(char)
                if 0xD800 <= n <= 0xDFFF:
                    raise ValueError('unpaired Unicode surrogate')
                charge(2 if char in '\"\\\b\f\n\r\t' else 6 if n < 32 or n > 126 and n <= 65535 else 12 if n > 65535 else 1)
            return item
        if item is None or kind is bool:
            charge(4 if item is None or item is True else 5)
            return item
        if kind is int:
            if abs(item) > 9007199254740991:
                raise ValueError('safe JSON integer required')
            charge(len(str(item))); return item
        if kind is float:
            if not math.isfinite(item):
                raise ValueError('finite JSON number required')
            charge(len(json.dumps(item, allow_nan=False))); return item
        if kind is list:
            if len(item) > budget.max_items:
                raise ValueError('JSON item budget exceeded')
            charge(2 + max(0, len(item)-1))
            return [visit(child, depth+1) for child in item]
        if kind is dict:
            if len(item) > budget.max_fields:
                raise ValueError('JSON field budget exceeded')
            charge(2 + max(0, len(item)-1) + len(item))
            result = {}
            for key, child in item.items():
                if type(key) is not str:
                    raise ValueError('JSON string keys required')
                result[visit(key, depth+1)] = visit(child, depth+1)
            return result
        raise ValueError('unsupported JSON type')

    try:
        return visit(value, 0)
    except RuntimeError as exc:
        raise ValueError('JSON container changed during admission') from exc
