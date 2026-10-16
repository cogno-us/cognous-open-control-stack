"""Byte and syntax budgets for local artifact admission; never grants authority."""
import json
from pathlib import Path

MAX_JSON_BYTES = 8 * 1024 * 1024


def read_bytes(path, limit=MAX_JSON_BYTES):
    with Path(path).open('rb') as stream:
        value = stream.read(limit + 1)
    if len(value) > limit:
        raise ValueError('artifact byte budget exceeded')
    return value


def loads(value, limit=MAX_JSON_BYTES):
    if isinstance(value, str):
        value = value.encode('utf-8')
    if len(value) > limit:
        raise ValueError('JSON byte budget exceeded')
    depth = nodes = 0
    quoted = escaped = False
    for char in value.decode('utf-8'):
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            nodes += 1
            if depth > 32 or nodes > 100000:
                raise ValueError('JSON structural budget exceeded')
        elif char in ']}':
            depth -= 1
    def pairs(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = item
        return result
    def constant(value):
        raise ValueError('nonfinite JSON value')
    return json.loads(value, object_pairs_hook=pairs, parse_constant=constant)
