"""Step 2.3 reference: mandatory-check manifest validation and completeness checking.

Non-authorizing. This module validates a mandatory-check manifest (profile
`ocs-mandatory-manifest/0`, a candidate wire name) and checks that a set of executed
check results is complete against the manifest and a step 2.1 registry record. It
returns a report or raises ManifestRefusal. It has no verdict, no pass/fail judgment,
no grant, never selects a pin, never activates anything and has no effect surface (no
network, subprocess, file or credential access). Standard library plus
tools/registry_records.py only. Inputs are never mutated. There is no default floor:
the floor check ids are passed explicitly. Release and production remain on HOLD.

Canonical form and digest are those of step 2.1 and are reused, not reimplemented
(registry_records.jcs_dumps, record_digest, validate_record).

Order of steps (fixed; the first failing step names the refusal)
  validate_manifest: shape (schema_invalid) -> digest (digest_mismatch) -> pin
  (pin_mismatch) -> duplicate check ids (duplicate_check) -> source reference
  (unknown_source) -> input kind (unknown_input_kind) -> reason (unknown_reason).
  check_completeness: validate_manifest -> floor shape (schema_invalid) -> floor subset
  of the manifest (floor_not_in_manifest) -> registry_records.validate_record
  (registry_record_invalid) -> a rule entry for each manifest check in manifest order
  (registry_rule_missing, registry_rule_not_required) -> executed list shape
  (schema_invalid) -> per executed entry, in the order given: unexpected_check,
  duplicate_result, invalid_outcome, evaluator_mismatch, unknown_evaluator,
  unqualified_evaluator, not_applicable_reason_not_allowed -> skipped_mandatory_check.

Design decisions where the specification left room
  D1  Bounds (refused above as schema_invalid): MAX_CHECKS 512, MAX_SOURCES 256,
      MAX_EXECUTED 512, MAX_INPUT_KINDS 64, MAX_REASONS 64 (closed set and each check's
      list), MAX_TEXT 512 characters for any text member, MAX_FLOOR 512 ids.
  D2  Ordering is by UTF-16 code units, the RFC 8785 key order, for check_id,
      input_kinds and reason lists. input_kinds, the closed reason set and each check's
      reason list must be strictly increasing (sorted and unique). checks must be
      non-decreasing by check_id so a duplicate reaches duplicate_check rather than
      being hidden as an ordering fault. Unsorted input is schema_invalid, never
      silently sorted.
  D3  Duplicate source_id is schema_invalid (the specification gives duplicate_check
      only for checks). Source `lines` may be "" or text; `note` may be "".
  D4  A verifier_check may carry input_kind null or a member of input_kinds; an
      input_read must carry a member (null is schema_invalid, a non-member is
      unknown_input_kind). A non-text, non-null input_kind is schema_invalid.
  D5  Text members must be str with at least one non-whitespace character where the
      specification says non-empty (matching registry_records). `revision` is exactly
      40 lowercase hex. Booleans are not integers; floats and any non-JSON type are
      schema_invalid (shape checks run before canonicalization; a canonicalization
      ValueError, including a lone surrogate, is also schema_invalid).
  D6  pin must be None or a digest-form string; any other pin is schema_invalid. A
      pin never selects anything: it is only compared with the computed digest.
  D7  floor_check_ids must be a set, frozenset, tuple or list of non-empty texts and
      must not be empty (an empty floor would mean nothing is protected). Duplicates
      in it are tolerated and treated as a set. Any other type is schema_invalid.
  D8  Any RegistryRefusal from validate_record, and any ValueError from digesting a
      malformed record, is wrapped as registry_record_invalid; the inner code is in
      the message only.
  D9  A manifest check may have several rule entries in the record (different class or
      profile); every entry with that rule_id must be required and always, else
      registry_rule_not_required. The rule's own evaluator is not compared with the
      manifest's evaluator: the manifest and the executed entry are compared
      (evaluator_mismatch) and the manifest's evaluator is looked up in the record.
  D10 executed must be a list (not a tuple). Each entry must be a dict with exactly
      the five members; wrong member sets or types are schema_invalid, except that
      any outcome that is not one of the four strings is invalid_outcome. For
      not_applicable, reason must be text in the check's list, otherwise
      not_applicable_reason_not_allowed (a null, blank or non-listed reason; a reason that
      is neither text nor null is schema_invalid). For
      the other outcomes, reason must be null, otherwise schema_invalid. A check with
      an empty allowed list can never be closed not_applicable.
  D11 The executed entry's evaluator is looked up by (evaluator_id, version) in the
      record's evaluators: absent is unknown_evaluator, a blank qualification_ref is
      unqualified_evaluator. All shape checks of the executed list precede its
      semantic checks.
  D12 counts has all four outcome keys, zero when absent. The report's checks are in
      manifest order. skipped_mandatory_check lists missing ids in manifest order in
      the message. The report has exactly manifest_digest, record_digest, complete,
      counts and checks.
"""
import re

from tools import registry_records as rr

PROFILE = 'ocs-mandatory-manifest/0'
SCHEMA_VERSION = 0
CANONICAL_PROFILE = rr.CANONICAL_PROFILE
MAX_SAFE_INT = rr.MAX_SAFE_INT

MAX_CHECKS = 512
MAX_SOURCES = 256
MAX_EXECUTED = 512
MAX_INPUT_KINDS = 64
MAX_REASONS = 64
MAX_TEXT = 512
MAX_FLOOR = 512

MANIFEST_FIELDS = {'profile', 'schema_version', 'canonical_profile', 'manifest_id', 'digest',
                   'sources', 'input_kinds', 'not_applicable_reasons', 'checks'}
SOURCE_FIELDS = {'source_id', 'repository', 'revision', 'path', 'lines', 'note'}
CHECK_FIELDS = {'check_id', 'kind', 'source_id', 'input_kind', 'evaluator_id', 'evaluator_version',
                'not_applicable_reasons'}
EXECUTED_FIELDS = {'check_id', 'outcome', 'reason', 'evaluator_id', 'evaluator_version'}
KINDS = ('verifier_check', 'input_read')
OUTCOMES = ('passed', 'failed', 'not_applicable', 'error')
REFUSAL_CODES = frozenset({
    'schema_invalid', 'digest_mismatch', 'pin_mismatch', 'duplicate_check', 'unknown_source',
    'unknown_input_kind', 'unknown_reason', 'unknown_evaluator', 'unqualified_evaluator',
    'floor_not_in_manifest', 'skipped_mandatory_check', 'unexpected_check', 'duplicate_result',
    'not_applicable_reason_not_allowed', 'evaluator_mismatch', 'invalid_outcome',
    'registry_record_invalid', 'registry_rule_missing', 'registry_rule_not_required'})
DIGEST_RE = re.compile(r'^sha256:[0-9a-f]{64}$')
REVISION_RE = re.compile(r'^[0-9a-f]{40}$')


class ManifestRefusal(Exception):
    """A typed refusal. The code is from a closed set; a refusal changes nothing."""

    def __init__(self, code, message=''):
        if code not in REFUSAL_CODES:
            raise ValueError('refusal code outside the closed set')
        super().__init__(f'{code}: {message}' if message else code)
        self.code = code


def _refuse(code, message=''):
    raise ManifestRefusal(code, message)


def _text(value, allow_empty=False):
    if type(value) is not str or len(value) > MAX_TEXT:
        return False
    return allow_empty or bool(value.strip())


def _int(value, minimum):
    return type(value) is int and minimum <= value <= MAX_SAFE_INT


def _key(value):
    return value.encode('utf-16-be', 'surrogatepass')


def _text_list(value, bound, what, *, strict):
    """A list of non-empty texts, strictly increasing (sorted and unique) when strict."""
    if type(value) is not list or len(value) > bound or not all(_text(v) for v in value):
        _refuse('schema_invalid', f'{what} must be a bounded list of non-empty texts')
    keys = [_key(v) for v in value]
    if keys != sorted(keys) or (strict and len(set(keys)) != len(keys)):
        _refuse('schema_invalid', f'{what} must be sorted and unique')
    return value


# --- manifest validation ----------------------------------------------------------------

def _validate_shape(manifest):
    if type(manifest) is not dict or set(manifest) != MANIFEST_FIELDS:
        _refuse('schema_invalid', 'exact manifest members required')
    if manifest['profile'] != PROFILE or type(manifest['profile']) is not str:
        _refuse('schema_invalid', 'unsupported profile')
    if type(manifest['schema_version']) is not int or manifest['schema_version'] != SCHEMA_VERSION:
        _refuse('schema_invalid', 'unsupported schema version')
    if manifest['canonical_profile'] != CANONICAL_PROFILE or type(manifest['canonical_profile']) is not str:
        _refuse('schema_invalid', 'unsupported canonical profile')
    if not _text(manifest['manifest_id']):
        _refuse('schema_invalid', 'manifest_id required')
    if type(manifest['digest']) is not str or not DIGEST_RE.match(manifest['digest']):
        _refuse('schema_invalid', 'digest form')
    kinds = _text_list(manifest['input_kinds'], MAX_INPUT_KINDS, 'input_kinds', strict=True)
    reasons = _text_list(manifest['not_applicable_reasons'], MAX_REASONS, 'not_applicable_reasons',
                         strict=True)
    sources = manifest['sources']
    if type(sources) is not list or len(sources) > MAX_SOURCES:
        _refuse('schema_invalid', 'sources must be a bounded list')
    source_ids = set()
    for src in sources:
        if type(src) is not dict or set(src) != SOURCE_FIELDS:
            _refuse('schema_invalid', 'exact source members required')
        for name in ('source_id', 'repository', 'path'):
            if not _text(src[name]):
                _refuse('schema_invalid', f'source {name} required')
        if type(src['revision']) is not str or not REVISION_RE.match(src['revision']):
            _refuse('schema_invalid', 'source revision must be 40 lowercase hex')
        for name in ('lines', 'note'):
            if not _text(src[name], allow_empty=True):
                _refuse('schema_invalid', f'source {name} must be text')
        if src['source_id'] in source_ids:
            _refuse('schema_invalid', 'duplicate source_id')
        source_ids.add(src['source_id'])
    checks = manifest['checks']
    if type(checks) is not list or len(checks) > MAX_CHECKS:
        _refuse('schema_invalid', 'checks must be a bounded list')
    previous = None
    for check in checks:
        if type(check) is not dict or set(check) != CHECK_FIELDS:
            _refuse('schema_invalid', 'exact check members required')
        for name in ('check_id', 'source_id', 'evaluator_id'):
            if not _text(check[name]):
                _refuse('schema_invalid', f'check {name} required')
        if type(check['kind']) is not str or check['kind'] not in KINDS:
            _refuse('schema_invalid', 'check kind')
        if check['input_kind'] is not None and not _text(check['input_kind']):
            _refuse('schema_invalid', 'input_kind must be text or null')
        if check['kind'] == 'input_read' and check['input_kind'] is None:
            _refuse('schema_invalid', 'input_read requires an input_kind')
        if not _int(check['evaluator_version'], 1):
            _refuse('schema_invalid', 'evaluator_version must be a positive integer')
        _text_list(check['not_applicable_reasons'], MAX_REASONS, 'check not_applicable_reasons',
                   strict=True)
        current = _key(check['check_id'])
        if previous is not None and current < previous:
            _refuse('schema_invalid', 'checks must be sorted by check_id')
        previous = current
    return kinds, reasons, source_ids


def validate_manifest(manifest, *, pin=None):
    """Validate a manifest against the shape, the digest and, when given, a pin.

    pin is the digest the manifest must have (held outside the manifest). Returns the
    manifest digest. Raises ManifestRefusal; changes nothing.
    """
    kinds, reasons, source_ids = _validate_shape(manifest)
    if pin is not None and (type(pin) is not str or not DIGEST_RE.match(pin)):
        _refuse('schema_invalid', 'pin must be a digest')
    try:
        computed = rr.record_digest(manifest)
    except (ValueError, RecursionError):
        _refuse('schema_invalid', 'manifest is not canonicalizable')
    if manifest['digest'] != computed:
        _refuse('digest_mismatch', 'declared digest differs from the canonical digest')
    if pin is not None and pin != computed:
        _refuse('pin_mismatch', 'digest differs from the configured pin')
    seen = set()
    for check in manifest['checks']:
        if check['check_id'] in seen:
            _refuse('duplicate_check', check['check_id'])
        seen.add(check['check_id'])
    kind_set, reason_set = set(kinds), set(reasons)
    for check in manifest['checks']:
        if check['source_id'] not in source_ids:
            _refuse('unknown_source', check['check_id'])
    for check in manifest['checks']:
        if check['input_kind'] is not None and check['input_kind'] not in kind_set:
            _refuse('unknown_input_kind', check['check_id'])
    for check in manifest['checks']:
        for reason in check['not_applicable_reasons']:
            if reason not in reason_set:
                _refuse('unknown_reason', check['check_id'])
    return computed


# --- completeness -----------------------------------------------------------------------

def _validate_floor(floor_check_ids):
    if type(floor_check_ids) not in (set, frozenset, tuple, list):
        _refuse('schema_invalid', 'floor_check_ids must be passed explicitly as a collection')
    if not floor_check_ids or len(floor_check_ids) > MAX_FLOOR \
            or not all(_text(f) for f in floor_check_ids):
        _refuse('schema_invalid', 'floor_check_ids must be a bounded non-empty collection of ids')
    return frozenset(floor_check_ids)


def _validate_executed_shape(executed):
    if type(executed) is not list or len(executed) > MAX_EXECUTED:
        _refuse('schema_invalid', 'executed must be a bounded list')
    for entry in executed:
        if type(entry) is not dict or set(entry) != EXECUTED_FIELDS:
            _refuse('schema_invalid', 'exact executed members required')
        if not _text(entry['check_id']) or not _text(entry['evaluator_id']):
            _refuse('schema_invalid', 'executed check_id and evaluator_id required')
        if not _int(entry['evaluator_version'], 1):
            _refuse('schema_invalid', 'executed evaluator_version must be a positive integer')
        if entry['reason'] is not None and not _text(entry['reason'], allow_empty=True):
            _refuse('schema_invalid', 'reason must be text or null')


def check_completeness(manifest, record, executed, *, floor_check_ids, pin=None):
    """Check that every mandatory check ran or was closed not applicable.

    Returns a report with manifest_digest, record_digest, complete (always True: an
    incomplete result raises), counts and checks. The report holds no verdict, grant,
    pin selection or activation: failed and error outcomes are reported as given.
    Raises ManifestRefusal; changes nothing and mutates none of its inputs.
    """
    manifest_digest = validate_manifest(manifest, pin=pin)
    floor = _validate_floor(floor_check_ids)
    manifest_checks = manifest['checks']
    by_id = {c['check_id']: c for c in manifest_checks}
    if not floor <= set(by_id):
        _refuse('floor_not_in_manifest', ', '.join(sorted(floor - set(by_id), key=_key)))
    try:
        record_digest = rr.validate_record(record, floor_mandatory_rule_ids=floor)
    except rr.RegistryRefusal as exc:
        _refuse('registry_record_invalid', exc.code)
    except (ValueError, RecursionError):
        _refuse('registry_record_invalid', 'record is not canonicalizable')
    rules = {}
    for rule in record['rule_table']:
        rules.setdefault(rule['rule_id'], []).append(rule)
    for check in manifest_checks:
        entries = rules.get(check['check_id'])
        if not entries:
            _refuse('registry_rule_missing', check['check_id'])
        for rule in entries:
            if rule['status'] != 'required' or rule['applicability'] != {'kind': 'always'}:
                _refuse('registry_rule_not_required', check['check_id'])
    qualified = {(ev['evaluator_id'], ev['version']): ev['qualification_ref']
                 for ev in record['evaluators']}
    _validate_executed_shape(executed)
    results = {}
    for entry in executed:
        check = by_id.get(entry['check_id'])
        if check is None:
            _refuse('unexpected_check', entry['check_id'])
        if entry['check_id'] in results:
            _refuse('duplicate_result', entry['check_id'])
        outcome = entry['outcome']
        if type(outcome) is not str or outcome not in OUTCOMES:
            _refuse('invalid_outcome', entry['check_id'])
        if entry['evaluator_id'] != check['evaluator_id'] \
                or entry['evaluator_version'] != check['evaluator_version']:
            _refuse('evaluator_mismatch', entry['check_id'])
        key = (check['evaluator_id'], check['evaluator_version'])
        if key not in qualified:
            _refuse('unknown_evaluator', check['evaluator_id'])
        if not _text(qualified[key]):
            _refuse('unqualified_evaluator', check['evaluator_id'])
        if outcome == 'not_applicable':
            if not _text(entry['reason']) or entry['reason'] not in check['not_applicable_reasons']:
                _refuse('not_applicable_reason_not_allowed', entry['check_id'])
        elif entry['reason'] is not None:
            _refuse('schema_invalid', 'reason must be null unless not_applicable')
        results[entry['check_id']] = entry
    missing = [c['check_id'] for c in manifest_checks if c['check_id'] not in results]
    if missing:
        _refuse('skipped_mandatory_check', ', '.join(missing))
    counts = {name: 0 for name in OUTCOMES}
    report_checks = []
    for check in manifest_checks:
        entry = results[check['check_id']]
        counts[entry['outcome']] += 1
        report_checks.append({'check_id': check['check_id'], 'outcome': entry['outcome'],
                              'reason': entry['reason']})
    return {'manifest_digest': manifest_digest, 'record_digest': record_digest, 'complete': True,
            'counts': counts, 'checks': report_checks}
