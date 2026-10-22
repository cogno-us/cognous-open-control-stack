"""Step 2.1 reference: versioned registry records and a bounded append-only store.

Non-authorizing. This module validates, digests and stores governance registry
records. It never activates a record, never selects a pin, never changes a
decision and has no effect surface. Publication is not activation: activation
belongs to the Control Plane gate (contract 1.3, section 5). Records are data;
the constitutional floor stays in code and is supplied explicitly by the caller
(there is no default floor). Standard library only.

Profile names are candidates for the M0 wire-name freeze and are recorded in
docs/program-v0.2/s04/2.1-registry-records.md.
"""
import hashlib
import json
import os
import re

PROFILE = 'ocs-registry-record/0'
SCHEMA_VERSION = 0
CANONICAL_PROFILE = 'rfc8785-jcs'
MAX_SAFE_INT = 2 ** 53 - 1

RECORD_FIELDS = {'profile', 'schema_version', 'registry_id', 'canonical_profile', 'digest', 'epoch',
                 'predecessor', 'rule_table', 'evaluators', 'reason_map', 'source_refs', 'issuer'}
RULE_FIELDS = {'rule_id', 'version', 'class', 'profile', 'status', 'applicability', 'evaluator_id',
               'evaluator_version', 'failure_disposition', 'missing_treatment', 'reason_code',
               'source_ref'}
EVALUATOR_FIELDS = {'evaluator_id', 'version', 'qualification_ref'}
STATUSES = {'required', 'advisory'}
DISPOSITIONS = {'deny', 'hold', 'quarantine', 'require_authority', 'require_evidence'}
MISSING_TREATMENTS = {'fail_closed'}
DIGEST_RE = re.compile(r'^sha256:[0-9a-f]{64}$')


class RegistryRefusal(Exception):
    """A typed refusal. The code is from a closed set; a refusal changes nothing."""

    def __init__(self, code, message=''):
        super().__init__(f'{code}: {message}' if message else code)
        self.code = code


def _refuse(code, message=''):
    raise RegistryRefusal(code, message)


def _text(value):
    return type(value) is str and bool(value.strip())


def _int(value, minimum):
    return type(value) is int and minimum <= value <= MAX_SAFE_INT


# --- canonical JSON (RFC 8785 subset: no floats) -----------------------------------------

_ESCAPES = {'"': '\\"', '\\': '\\\\', '\b': '\\b', '\f': '\\f', '\n': '\\n', '\r': '\\r', '\t': '\\t'}


def _jcs_string(value):
    out = []
    for ch in value:
        if ch in _ESCAPES:
            out.append(_ESCAPES[ch])
        elif ord(ch) < 0x20:
            out.append('\\u%04x' % ord(ch))
        else:
            out.append(ch)
    text = '"' + ''.join(out) + '"'
    text.encode('utf-8')  # lone surrogates are not well-formed JSON text
    return text


def jcs_dumps(value):
    """RFC 8785 canonical form for dict, list, str, bool, None and safe integers.

    Floats are refused: the registry profile has none, and a float has more than one
    textual form. Keys sort by UTF-16 code units as the RFC requires.
    """
    if value is None:
        return 'null'
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if type(value) is int:
        if abs(value) > MAX_SAFE_INT:
            raise ValueError('integer outside the safe range')
        return str(value)
    if type(value) is str:
        return _jcs_string(value)
    if type(value) is list:
        return '[' + ','.join(jcs_dumps(v) for v in value) + ']'
    if type(value) is dict:
        if any(type(k) is not str for k in value):
            raise ValueError('object keys must be strings')
        keys = sorted(value, key=lambda k: k.encode('utf-16-be', 'surrogatepass'))
        return '{' + ','.join(_jcs_string(k) + ':' + jcs_dumps(value[k]) for k in keys) + '}'
    raise ValueError('type not representable in the registry profile')


def jcs_bytes(value):
    return jcs_dumps(value).encode('utf-8')


def loads_strict(data):
    """Parse JSON refusing duplicate keys, floats and non-finite constants."""
    def pairs(items):
        keys = [k for k, _ in items]
        if len(set(keys)) != len(keys):
            raise ValueError('duplicate object key')
        return dict(items)

    def no_float(text):
        raise ValueError('floating point numbers are not part of the profile')

    def no_constant(text):
        raise ValueError('non-finite constant')

    return json.loads(data, object_pairs_hook=pairs, parse_float=no_float, parse_constant=no_constant)


def record_digest(record):
    """sha256 over the canonical form of the record without its own digest member."""
    body = {k: v for k, v in record.items() if k != 'digest'}
    return 'sha256:' + hashlib.sha256(jcs_bytes(body)).hexdigest()


# --- validation -------------------------------------------------------------------------

def _validate_shape(record):
    if type(record) is not dict or set(record) != RECORD_FIELDS:
        _refuse('schema_invalid', 'exact record members required')
    if record['profile'] != PROFILE or record['schema_version'] != SCHEMA_VERSION \
            or type(record['schema_version']) is not int:
        _refuse('schema_invalid', 'unsupported profile or schema version')
    if record['canonical_profile'] != CANONICAL_PROFILE:
        _refuse('unknown_canonical_profile', str(record['canonical_profile'])[:40])
    if not _text(record['registry_id']) or not _text(record['issuer']):
        _refuse('schema_invalid', 'registry_id and issuer required')
    if not _int(record['epoch'], 1):
        _refuse('schema_invalid', 'epoch must be a positive integer')
    if type(record['digest']) is not str or not DIGEST_RE.match(record['digest']):
        _refuse('schema_invalid', 'digest form')
    predecessor = record['predecessor']
    if predecessor is not None and (type(predecessor) is not str or not DIGEST_RE.match(predecessor)):
        _refuse('schema_invalid', 'predecessor form')
    refs = record['source_refs']
    if type(refs) is not list or not refs or any(not _text(r) for r in refs) or len(set(refs)) != len(refs):
        _refuse('schema_invalid', 'unique nonempty source_refs required')
    reasons = record['reason_map']
    if type(reasons) is not dict or not reasons or any(not _text(k) or not _text(v) for k, v in reasons.items()):
        _refuse('schema_invalid', 'reason_map must be a nonempty map of text')
    evaluators = record['evaluators']
    if type(evaluators) is not list or not evaluators:
        _refuse('schema_invalid', 'evaluators required')
    for ev in evaluators:
        if type(ev) is not dict or set(ev) != EVALUATOR_FIELDS:
            _refuse('schema_invalid', 'exact evaluator members required')
        if not _text(ev['evaluator_id']) or not _int(ev['version'], 1):
            _refuse('schema_invalid', 'evaluator id and version')
        if type(ev['qualification_ref']) is not str:
            _refuse('schema_invalid', 'qualification_ref must be text')
    table = record['rule_table']
    if type(table) is not list or not table:
        _refuse('schema_invalid', 'rule_table required')
    for rule in table:
        _validate_rule(rule)


def _validate_rule(rule):
    if type(rule) is not dict or set(rule) != RULE_FIELDS:
        _refuse('schema_invalid', 'exact rule members required')
    for key in ('rule_id', 'class', 'profile', 'evaluator_id', 'reason_code', 'source_ref'):
        if not _text(rule[key]):
            _refuse('schema_invalid', f'rule {key} required')
    if not _int(rule['version'], 1) or not _int(rule['evaluator_version'], 1):
        _refuse('schema_invalid', 'rule versions must be positive integers')
    if type(rule['status']) is not str or rule['status'] not in STATUSES:
        _refuse('schema_invalid', 'status is required or advisory')
    if type(rule['failure_disposition']) is not str or rule['failure_disposition'] not in DISPOSITIONS:
        _refuse('schema_invalid', 'unknown failure disposition')
    if type(rule['missing_treatment']) is not str or rule['missing_treatment'] not in MISSING_TREATMENTS:
        _refuse('schema_invalid', 'missing input must fail closed')
    app = rule['applicability']
    if type(app) is not dict or app.get('kind') not in ('always', 'predicate'):
        _refuse('schema_invalid', 'applicability kind')
    if app['kind'] == 'always' and set(app) != {'kind'}:
        _refuse('schema_invalid', 'always takes no members')
    if app['kind'] == 'predicate' and (set(app) != {'kind', 'predicate', 'source_ref'}
                                       or not _text(app['predicate']) or not _text(app['source_ref'])):
        _refuse('schema_invalid', 'predicate needs text and a source reference')


def validate_record(record, *, floor_mandatory_rule_ids, pin=None):
    """Validate a record against the shape, the floor and the digest.

    floor_mandatory_rule_ids is required and has no default: the floor lives in code
    and is passed in by the component that owns the gate. A registry entry cannot
    disable, weaken, make advisory or make conditional a rule in that set.
    pin, when given, is the digest the record must have (held outside the store).
    Returns the record's digest. Raises RegistryRefusal; changes nothing.
    """
    _validate_shape(record)
    if type(floor_mandatory_rule_ids) not in (set, frozenset, tuple, list):
        _refuse('schema_invalid', 'floor must be passed explicitly')
    computed = record_digest(record)
    if record['digest'] != computed:
        _refuse('digest_mismatch', 'declared digest differs from the canonical digest')
    if pin is not None and pin != computed:
        _refuse('pin_mismatch', 'digest differs from the configured pin')
    rules = record['rule_table']
    scopes = set()
    for rule in rules:
        scope = (rule['rule_id'], rule['class'], rule['profile'])
        if scope in scopes:
            _refuse('duplicate_or_shadowed_rule', f"{rule['rule_id']}")
        scopes.add(scope)
        if rule['reason_code'] not in record['reason_map']:
            _refuse('schema_invalid', 'reason_code not in reason_map')
        if rule['source_ref'] not in record['source_refs']:
            _refuse('schema_invalid', 'source_ref not in source_refs')
        if rule['applicability']['kind'] == 'predicate' and \
                rule['applicability']['source_ref'] not in record['source_refs']:
            _refuse('schema_invalid', 'predicate source_ref not in source_refs')
    qualified = {}
    for ev in record['evaluators']:
        key = (ev['evaluator_id'], ev['version'])
        if key in qualified:
            _refuse('duplicate_or_shadowed_rule', f'duplicate evaluator {key[0]}')
        qualified[key] = ev['qualification_ref']
    for rule in rules:
        key = (rule['evaluator_id'], rule['evaluator_version'])
        if key not in qualified:
            _refuse('unknown_evaluator', rule['evaluator_id'])
        if not _text(qualified[key]):
            _refuse('unqualified_evaluator', rule['evaluator_id'])
    by_id = {}
    for rule in rules:
        by_id.setdefault(rule['rule_id'], []).append(rule)
    for rule_id in floor_mandatory_rule_ids:
        entries = by_id.get(rule_id)
        if not entries:
            _refuse('mandatory_check_missing', rule_id)
        for rule in entries:
            if rule['status'] != 'required':
                _refuse('mandatory_check_not_required', rule_id)
            if rule['applicability']['kind'] != 'always':
                _refuse('mandatory_check_conditional', rule_id)
    return computed


def check_succession(record, active):
    """Refuse a record that does not strictly follow the active one (no downgrade, no fork)."""
    if active is None:
        if record['predecessor'] is not None or record['epoch'] < 1:
            _refuse('predecessor_mismatch', 'first record has no predecessor')
        return
    if record['epoch'] <= active['epoch']:
        _refuse('epoch_not_increasing', f"{record['epoch']} <= {active['epoch']}")
    if record['predecessor'] != active['digest']:
        _refuse('predecessor_mismatch', 'predecessor is not the active digest')


# --- bounded append-only store ----------------------------------------------------------

class RegistryStore:
    """Immutable, bounded, append-only directory of published records.

    Publication is not activation: nothing here selects an active record. Every load
    re-verifies the digest, the file name and the profile. Bounds are explicit.
    """

    def __init__(self, directory, *, max_records, max_record_bytes, floor_mandatory_rule_ids):
        if not _int(max_records, 1) or not _int(max_record_bytes, 1):
            raise ValueError('explicit positive bounds required')
        self.directory = directory
        self.max_records = max_records
        self.max_record_bytes = max_record_bytes
        self.floor = frozenset(floor_mandatory_rule_ids)
        os.makedirs(directory, exist_ok=True)

    @staticmethod
    def _name(record):
        return f"{record['epoch']:012d}-{record['digest'].split(':', 1)[1]}.json"

    def _names(self):
        names = sorted(n for n in os.listdir(self.directory) if n.endswith('.json'))
        for n in names:
            if not re.match(r'^\d{12}-[0-9a-f]{64}\.json$', n):
                _refuse('store_integrity', 'unexpected file name')
        return names

    def _read(self, name):
        path = os.path.join(self.directory, name)
        if os.path.islink(path) or os.path.getsize(path) > self.max_record_bytes:
            _refuse('store_integrity', 'unreadable or oversized record')
        with open(path, 'rb') as handle:
            data = handle.read(self.max_record_bytes + 1)
        try:
            record = loads_strict(data.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            _refuse('store_integrity', 'record is not strict JSON')
        validate_record(record, floor_mandatory_rule_ids=self.floor)
        if self._name(record) != name:
            _refuse('store_integrity', 'file name does not match record identity')
        return record

    def list_digests(self):
        return [n.split('-', 1)[1][:-5] for n in self._names()]

    def latest(self):
        names = self._names()
        return self._read(names[-1]) if names else None

    def load(self, digest):
        if type(digest) is not str or not DIGEST_RE.match(digest):
            _refuse('schema_invalid', 'digest form')
        hexpart = digest.split(':', 1)[1]
        for name in self._names():
            if name.split('-', 1)[1][:-5] == hexpart:
                return self._read(name)
        return None

    def publish(self, record, *, pin=None):
        """Validate, check succession against the latest stored record, then append."""
        validate_record(record, floor_mandatory_rule_ids=self.floor, pin=pin)
        data = jcs_bytes(record)
        if len(data) > self.max_record_bytes:
            _refuse('store_bound_exceeded', 'record too large')
        names = self._names()
        if len(names) >= self.max_records:
            _refuse('store_bound_exceeded', 'record count bound reached')
        check_succession(record, self._read(names[-1]) if names else None)
        path = os.path.join(self.directory, self._name(record))
        try:
            handle = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
        except FileExistsError:
            _refuse('store_conflict', 'record already published')
        with os.fdopen(handle, 'wb') as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        return record['digest']
