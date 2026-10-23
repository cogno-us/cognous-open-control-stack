"""Step 2.3 reference: mandatory-check manifest validation and completeness checking.

Non-authorizing. This module validates a mandatory-check manifest (profiles
`ocs-mandatory-manifest/0` and its versioned successor `ocs-mandatory-manifest/1`, candidate
wire names) and checks that a set of executed check results is complete against the
manifest and a step 2.1 registry record. It
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
  duplicate_result, invalid_outcome, evaluator_mismatch,
  not_applicable_reason_not_allowed -> skipped_mandatory_check.
  Repair (architect decisions Q2, Q3, Q7; contract section 13): the rule step also binds the
  evaluator (see D9 and D11 below) and the profile /1 adds predicates, per-check applicability
  and typed inapplicable dispositions (D14 to D17). The /0 profile keeps its data and shape
  rules unchanged.
  Disposition corrections (architect decisions Q7 to Q10; docs 2.3-disposition-corrections.md):
  profile /1 adds the fifth executed outcome `abstained` and the explicit failure-path surrogates
  (D18 to D21). No refusal code is added; /0 behavior (four outcomes, no surrogates) is unchanged.

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
  D13 (review N7) An input_read check's check_id must equal 'input_read.' + input_kind
      (schema_invalid otherwise), so an input kind cannot be listed under a misleading id.
      Review N1: digest and revision forms use fullmatch (no trailing newline accepted).
  D5  Text members must be str with at least one non-whitespace character where the
      specification says non-empty (matching registry_records). `revision` is exactly
      40 lowercase hex. Booleans are not integers; floats and any non-JSON type are
      schema_invalid (shape checks run before canonicalization; a canonicalization
      ValueError, including a lone surrogate, is also schema_invalid).
  D6  (governor ruling) pin is compared with `is not None`: any supplied pin that is not None
      and is not exactly the computed digest (including '', wrong case, truncated, a
      non-str type) is pin_mismatch, never schema_invalid and never treated as no pin. A
      pin never selects anything: it is only compared with the computed digest.
  D7  floor_check_ids must be a set, frozenset, tuple or list of non-empty texts and
      must not be empty (an empty floor would mean nothing is protected). Duplicates
      in it are tolerated and treated as a set. Any other type is schema_invalid.
  D8  Any RegistryRefusal from validate_record, and any ValueError from digesting a
      malformed record, is wrapped as registry_record_invalid; the inner code is in
      the message only.
  D9  (repaired, Q2) A manifest check may have several rule entries in the record (different
      class or profile); every entry with that rule_id must be required and always (profile
      /1: or required_when_applicable naming the check's predicate, see D15), else
      registry_rule_not_required (predicate_mismatch for a /1 predicate disagreement). Every
      entry must also use exactly the manifest check's (evaluator_id, evaluator_version),
      else rule_evaluator_mismatch: a different evaluator is not interchangeable, even one that
      is qualified, without a versioned contract change.
  D10 executed must be a list (not a tuple). Each entry must be a dict with exactly
      the five members; wrong member sets or types (including a non-str outcome) are
      schema_invalid (governor ruling); invalid_outcome is only for an outcome string that
      is not one of the four. For
      not_applicable, reason must be text in the check's list, otherwise
      not_applicable_reason_not_allowed (a null, blank or non-listed reason; a reason that
      is neither text nor null is schema_invalid). For
      the other outcomes, reason must be null, otherwise schema_invalid. A check with
      an empty allowed list can never be closed not_applicable.
  D11 (repaired, Q2) Qualification binds the exact pair. For each manifest check, in manifest
      order, the check's (evaluator_id, version) must be listed in the record's evaluators
      (absent: unknown_evaluator) with a non-blank qualification_ref (blank:
      unqualified_evaluator). Because registry_records.validate_record refuses first any rule
      entry whose evaluator is unlisted or blank, those two 2.1 inner codes are surfaced
      under the same names (unknown_evaluator, unqualified_evaluator) instead of the generic
      registry_record_invalid, so both are reachable through the public function; every other
      2.1 refusal stays registry_record_invalid (D8). The per-check pair look-up is kept as a
      second, independent guard and is exercised through the internal seam (see D17).
  D12 counts has all four outcome keys, zero when absent. The report's checks are in
      manifest order. skipped_mandatory_check lists missing ids in manifest order in
      the message. The report has exactly manifest_digest, record_digest, complete,
      counts and checks. (Profile /1: counts also has `inapplicable`, and each check entry also
      has `predicate`, null unless the entry is an inapplicable disposition.)
  D14 (Q3) Profile /1 members: the /0 members plus `predicates` (sorted by predicate_id, each
      with exactly predicate_id, basis, source_ids, justifications; basis is one of BASES;
      source_ids and justifications are strictly increasing non-empty lists of non-empty
      texts) and, per check, `applicability`: {"kind": "unconditional"} or {"kind":
      "required_when_applicable", "predicate": <id>}. A declared predicate used by no check is
      schema_invalid; a check naming an undeclared predicate is unknown_predicate; a predicate
      source_id naming no source is unknown_source. There is no free text, regex or expression
      anywhere in an applicability: a predicate is a name, a basis and source citations; its
      meaning is documented in the companion record, never evaluated here.
  D15 (Q3) Profile /1 completeness. A floor check must be unconditional (floor_check_conditional).
      An unconditional check needs an executed result. A required_when_applicable check needs
      an executed result OR a disposition. A disposition has exactly check_id, predicate,
      justification, evaluator_id, evaluator_version; it is refused for an unconditional check
      (inapplicable_not_permitted), if its predicate is not the check's (predicate_mismatch), if
      the justification is not in that predicate's closed list (justification_not_allowed), if the
      evaluator differs (evaluator_mismatch), or if the check also has an executed result or
      another disposition (duplicate_result). Absence is never inapplicability:
      skipped_mandatory_check still lists a check with neither.
  D16 (Q3) A required_when_applicable check cannot be matched to a registry record that cannot
      express it. registry_records (profile ocs-registry-record/0) refuses a conditional
      mandatory rule, and that stays: such a check against a /0 record is refused with
      applicability_unsupported_by_registry. Unconditional checks work against /0 records.
  D17 The registry facts used by the rule step are collected into a small internal view
      (_registry_from_record) and the rest of completeness runs on that view (_complete). The
      view has a `conditional_supported` flag, always False for a /0 record. The seam lets the
      tests exercise the proposed successor semantics (a rule entry with applicability
      required_when_applicable, docs 2.1 successor note) without any registry code change; it
      is not a second public entry point and no registry is activated through it.
  D18 (Q7) Profile /1 executed outcomes are the four of /0 plus `abstained`: the check was
      applicable and executed but could not establish its substantive result. `abstained` is never a
      pass, is counted separately, and its report row has result_established False, so it cannot be
      read as satisfying a requirement for successful verification. `error` (failed, crashed, timed
      out or invalid result) also has result_established False. `not_applicable` (executed over zero
      items, section 5) and a disposition (predicate) are neither established nor unestablished
      (result_established None). `passed` and `failed` are established. Completeness (complete True)
      means every mandatory check has an accountable outcome; it never means substantive success.
      A profile /0 manifest still refuses `abstained` as invalid_outcome (unchanged). Where an
      executed entry does not carry one of the typed values it is invalid_outcome; no applicability
      is inferred. An `abstained` entry must carry its could-not-check reason as text (the retained
      diagnostic, not interpreted here), otherwise schema_invalid; an `error` entry may carry its
      diagnostic cause as text or null. In /1 no refusal code was added: outcome typing fits the
      existing codes (invalid_outcome, schema_invalid) and the report holds no verdict.
  D19 (Q8) Profile /1 manifests carry `surrogates`: a list sorted by unique check_id, each exactly
      check_id (a manifest check that is required_when_applicable, never unconditional and never
      a floor check), failure_condition (closed set FAILURE_CONDITIONS) and source_ids (strictly
      increasing, each a manifest source). A surrogate is a named failure-path identifier, not an
      ordinary check execution and not an independent substitute: its executed outcome must be
      `abstained` or `error` (passed, failed and not_applicable are invalid_outcome) with the
      original trigger as non-blank reason text. A surrogate result never discharges another
      check; each check still needs its own result or disposition.
  D20 (Q8) The report keeps a surrogate's outcome in the ordinary outcome count (an error surrogate
      stays visible in counts.error and an abstained one in counts.abstained) and adds `surrogate`:
      the number of surrogate rows, a tally over those counts and not a bucket that hides them.
      Each /1 row also has `surrogate`: null or the failure_condition.
  D21 (Q10) A crash of verify_document is an `error`, never inapplicable: the candidate data holds
      no inapplicability justification for a checker crash (tests pin this).
"""
import re

from tools import registry_records as rr

PROFILE = 'ocs-mandatory-manifest/0'
SCHEMA_VERSION = 0
PROFILE_1 = 'ocs-mandatory-manifest/1'
SCHEMA_VERSION_1 = 1
CANONICAL_PROFILE = rr.CANONICAL_PROFILE
MAX_SAFE_INT = rr.MAX_SAFE_INT

MAX_CHECKS = 512
MAX_SOURCES = 256
MAX_EXECUTED = 512
MAX_INPUT_KINDS = 64
MAX_REASONS = 64
MAX_TEXT = 512
MAX_FLOOR = 512
MAX_PREDICATES = 256

MANIFEST_FIELDS = {'profile', 'schema_version', 'canonical_profile', 'manifest_id', 'digest',
                   'sources', 'input_kinds', 'not_applicable_reasons', 'checks'}
SOURCE_FIELDS = {'source_id', 'repository', 'revision', 'path', 'lines', 'note'}
CHECK_FIELDS = {'check_id', 'kind', 'source_id', 'input_kind', 'evaluator_id', 'evaluator_version',
                'not_applicable_reasons'}
MANIFEST_FIELDS_1 = MANIFEST_FIELDS | {'predicates', 'surrogates'}
CHECK_FIELDS_1 = CHECK_FIELDS | {'applicability'}
PREDICATE_FIELDS = {'predicate_id', 'basis', 'source_ids', 'justifications'}
DISPOSITION_FIELDS = {'check_id', 'predicate', 'justification', 'evaluator_id', 'evaluator_version'}
APPLICABILITY_KINDS = ('unconditional', 'required_when_applicable')
# What a predicate is about (closed): the record's class, whether an input was supplied, the parse
# or structure state of an input, a member or row present in the record, or the results of peer checks.
BASES = ('input_presence', 'input_state', 'peer_results', 'record_class', 'record_content')
EXECUTED_FIELDS = {'check_id', 'outcome', 'reason', 'evaluator_id', 'evaluator_version'}
KINDS = ('verifier_check', 'input_read')
OUTCOMES = ('passed', 'failed', 'not_applicable', 'error')
OUTCOMES_1 = OUTCOMES + ('abstained',)
SURROGATE_FIELDS = {'check_id', 'failure_condition', 'source_ids'}
FAILURE_CONDITIONS = ('no_items_examined', 'run_record_unparsed_or_checker_crash')
SURROGATE_OUTCOMES = ('abstained', 'error')
REFUSAL_CODES = frozenset({
    'schema_invalid', 'digest_mismatch', 'pin_mismatch', 'duplicate_check', 'unknown_source',
    'unknown_input_kind', 'unknown_reason', 'unknown_evaluator', 'unqualified_evaluator',
    'floor_not_in_manifest', 'skipped_mandatory_check', 'unexpected_check', 'duplicate_result',
    'not_applicable_reason_not_allowed', 'evaluator_mismatch', 'invalid_outcome',
    'registry_record_invalid', 'registry_rule_missing', 'registry_rule_not_required',
    'unknown_predicate', 'applicability_unsupported_by_registry', 'floor_check_conditional',
    'rule_evaluator_mismatch', 'inapplicable_not_permitted', 'predicate_mismatch',
    'justification_not_allowed'})
DIGEST_RE = re.compile(r'sha256:[0-9a-f]{64}')  # used with fullmatch: `$` would accept a trailing newline
REVISION_RE = re.compile(r'[0-9a-f]{40}')  # used with fullmatch


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

def _version(manifest):
    """1 for a manifest that declares profile /1, else 0 (the /0 rules then apply and refuse)."""
    return 1 if type(manifest) is dict and type(manifest.get('profile')) is str \
        and manifest['profile'] == PROFILE_1 else 0


def _validate_predicates(predicates):
    if type(predicates) is not list or len(predicates) > MAX_PREDICATES:
        _refuse('schema_invalid', 'predicates must be a bounded list')
    previous = None
    for pred in predicates:
        if type(pred) is not dict or set(pred) != PREDICATE_FIELDS:
            _refuse('schema_invalid', 'exact predicate members required')
        if not _text(pred['predicate_id']):
            _refuse('schema_invalid', 'predicate_id required')
        if type(pred['basis']) is not str or pred['basis'] not in BASES:
            _refuse('schema_invalid', 'predicate basis outside the closed set')
        for name in ('source_ids', 'justifications'):
            if not _text_list(pred[name], MAX_REASONS, f'predicate {name}', strict=True):
                _refuse('schema_invalid', f'predicate {name} must not be empty')
        current = _key(pred['predicate_id'])
        if previous is not None and current <= previous:
            _refuse('schema_invalid', 'predicates must be sorted by unique predicate_id')
        previous = current
    return predicates


def _validate_surrogates(surrogates):
    if type(surrogates) is not list or len(surrogates) > MAX_PREDICATES:
        _refuse('schema_invalid', 'surrogates must be a bounded list')
    previous = None
    for sur in surrogates:
        if type(sur) is not dict or set(sur) != SURROGATE_FIELDS:
            _refuse('schema_invalid', 'exact surrogate members required')
        if not _text(sur['check_id']):
            _refuse('schema_invalid', 'surrogate check_id required')
        if type(sur['failure_condition']) is not str or sur['failure_condition'] not in FAILURE_CONDITIONS:
            _refuse('schema_invalid', 'surrogate failure_condition outside the closed set')
        if not _text_list(sur['source_ids'], MAX_REASONS, 'surrogate source_ids', strict=True):
            _refuse('schema_invalid', 'surrogate source_ids must not be empty')
        current = _key(sur['check_id'])
        if previous is not None and current <= previous:
            _refuse('schema_invalid', 'surrogates must be sorted by unique check_id')
        previous = current
    return surrogates


def _validate_applicability(app):
    if type(app) is not dict or type(app.get('kind')) is not str \
            or app['kind'] not in APPLICABILITY_KINDS:
        _refuse('schema_invalid', 'applicability kind')
    if app['kind'] == 'unconditional' and set(app) != {'kind'}:
        _refuse('schema_invalid', 'unconditional takes no members')
    if app['kind'] == 'required_when_applicable' \
            and (set(app) != {'kind', 'predicate'} or not _text(app['predicate'])):
        _refuse('schema_invalid', 'required_when_applicable takes exactly a predicate id')


def _validate_shape(manifest):
    version = _version(manifest)
    if type(manifest) is not dict or set(manifest) != (MANIFEST_FIELDS_1 if version else MANIFEST_FIELDS):
        _refuse('schema_invalid', 'exact manifest members required')
    expected_profile = PROFILE_1 if version else PROFILE
    if manifest['profile'] != expected_profile or type(manifest['profile']) is not str:
        _refuse('schema_invalid', 'unsupported profile')
    expected_schema = SCHEMA_VERSION_1 if version else SCHEMA_VERSION
    if type(manifest['schema_version']) is not int or manifest['schema_version'] != expected_schema:
        _refuse('schema_invalid', 'unsupported schema version')
    if manifest['canonical_profile'] != CANONICAL_PROFILE or type(manifest['canonical_profile']) is not str:
        _refuse('schema_invalid', 'unsupported canonical profile')
    if not _text(manifest['manifest_id']):
        _refuse('schema_invalid', 'manifest_id required')
    if type(manifest['digest']) is not str or not DIGEST_RE.fullmatch(manifest['digest']):
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
        if type(src['revision']) is not str or not REVISION_RE.fullmatch(src['revision']):
            _refuse('schema_invalid', 'source revision must be 40 lowercase hex')
        for name in ('lines', 'note'):
            if not _text(src[name], allow_empty=True):
                _refuse('schema_invalid', f'source {name} must be text')
        if src['source_id'] in source_ids:
            _refuse('schema_invalid', 'duplicate source_id')
        source_ids.add(src['source_id'])
    predicates = _validate_predicates(manifest['predicates']) if version else []
    surrogates = _validate_surrogates(manifest['surrogates']) if version else []
    checks = manifest['checks']
    if type(checks) is not list or len(checks) > MAX_CHECKS:
        _refuse('schema_invalid', 'checks must be a bounded list')
    previous = None
    used = set()
    for check in checks:
        if type(check) is not dict or set(check) != (CHECK_FIELDS_1 if version else CHECK_FIELDS):
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
        if check['kind'] == 'input_read' and check['check_id'] != 'input_read.' + check['input_kind']:
            _refuse('schema_invalid', "input_read check_id must be 'input_read.<input_kind>'")
        if not _int(check['evaluator_version'], 1):
            _refuse('schema_invalid', 'evaluator_version must be a positive integer')
        _text_list(check['not_applicable_reasons'], MAX_REASONS, 'check not_applicable_reasons',
                   strict=True)
        if version:
            _validate_applicability(check['applicability'])
            if check['applicability']['kind'] == 'required_when_applicable':
                used.add(check['applicability']['predicate'])
        current = _key(check['check_id'])
        if previous is not None and current < previous:
            _refuse('schema_invalid', 'checks must be sorted by check_id')
        previous = current
    if version and {p['predicate_id'] for p in predicates} - used:
        _refuse('schema_invalid', 'a declared predicate is used by no check')
    return kinds, reasons, source_ids, predicates, surrogates


def validate_manifest(manifest, *, pin=None):
    """Validate a manifest (profile /0 or /1) against the shape, the digest and, when given, a pin.

    pin is the digest the manifest must have (held outside the manifest). Returns the
    manifest digest. Raises ManifestRefusal; changes nothing.
    """
    kinds, reasons, source_ids, predicates, surrogates = _validate_shape(manifest)
    try:
        computed = rr.record_digest(manifest)
    except (ValueError, RecursionError):
        _refuse('schema_invalid', 'manifest is not canonicalizable')
    if manifest['digest'] != computed:
        _refuse('digest_mismatch', 'declared digest differs from the canonical digest')
    if pin is not None and (type(pin) is not str or pin != computed):
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
    for pred in predicates:
        for source_id in pred['source_ids']:
            if source_id not in source_ids:
                _refuse('unknown_source', pred['predicate_id'])
    for sur in surrogates:
        for source_id in sur['source_ids']:
            if source_id not in source_ids:
                _refuse('unknown_source', sur['check_id'])
    by_check = {c['check_id']: c for c in manifest['checks']}
    for sur in surrogates:
        target = by_check.get(sur['check_id'])
        if target is None or target['applicability']['kind'] != 'required_when_applicable':
            _refuse('schema_invalid', 'a surrogate must be a conditional manifest check')
    declared = {p['predicate_id'] for p in predicates}
    for check in manifest['checks']:
        if _version(manifest) and check['applicability']['kind'] == 'required_when_applicable' \
                and check['applicability']['predicate'] not in declared:
            _refuse('unknown_predicate', check['check_id'])
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
        if type(entry['outcome']) is not str:
            _refuse('schema_invalid', 'executed outcome must be text')
        if not _int(entry['evaluator_version'], 1):
            _refuse('schema_invalid', 'executed evaluator_version must be a positive integer')
        if entry['reason'] is not None and not _text(entry['reason'], allow_empty=True):
            _refuse('schema_invalid', 'reason must be text or null')


def _validate_dispositions_shape(dispositions):
    if type(dispositions) is not list or len(dispositions) > MAX_EXECUTED:
        _refuse('schema_invalid', 'dispositions must be a bounded list')
    for entry in dispositions:
        if type(entry) is not dict or set(entry) != DISPOSITION_FIELDS:
            _refuse('schema_invalid', 'exact disposition members required')
        for name in ('check_id', 'predicate', 'justification', 'evaluator_id'):
            if not _text(entry[name]):
                _refuse('schema_invalid', f'disposition {name} required')
        if not _int(entry['evaluator_version'], 1):
            _refuse('schema_invalid', 'disposition evaluator_version must be a positive integer')


# Test seam only, not an API: callers outside the tests must use check_completeness; _complete
# (and a view built by hand) bypasses record validation if imported.
def _registry_from_record(record, record_digest):
    """The registry facts completeness uses, from a validated step 2.1 record.

    conditional_supported is False: profile ocs-registry-record/0 cannot express a conditional
    mandatory rule, and tools/registry_records.py is not changed here (contract section 13).
    """
    rules = {}
    for rule in record['rule_table']:
        rules.setdefault(rule['rule_id'], []).append(rule)
    qualified = {(ev['evaluator_id'], ev['version']): ev['qualification_ref']
                 for ev in record['evaluators']}
    return {'record_digest': record_digest, 'rules': rules, 'qualified': qualified,
            'conditional_supported': False}


def _evaluator_fault(record):
    """Name the first rule (record order, as validate_record) whose evaluator is unlisted or blank.

    The code can concern a rule unrelated to any manifest check; the message says which.
    """
    qualified = {(ev['evaluator_id'], ev['version']): ev['qualification_ref']
                 for ev in record['evaluators']}
    for rule in record['rule_table']:
        key = (rule['evaluator_id'], rule['evaluator_version'])
        if key not in qualified or not _text(qualified[key]):
            return 'rule %s uses evaluator %s version %s' % (rule['rule_id'], key[0], key[1])
    return 'record evaluator fault'


def check_completeness(manifest, record, executed, *, floor_check_ids, pin=None, dispositions=None):
    """Check that every mandatory check ran or was closed not applicable.

    Returns a report with manifest_digest, record_digest, complete (always True: an
    incomplete result raises), counts and checks. The report holds no verdict, grant,
    pin selection or activation: failed and error outcomes are reported as given.
    `dispositions` (profile /1 only, default none) are typed inapplicable dispositions for
    required_when_applicable checks; a /0 manifest takes none. Raises ManifestRefusal;
    changes nothing and mutates none of its inputs.
    """
    manifest_digest = validate_manifest(manifest, pin=pin)
    version = _version(manifest)
    if not version and dispositions is not None:
        _refuse('schema_invalid', 'profile /0 has no inapplicable dispositions')
    floor = _validate_floor(floor_check_ids)
    by_id = {c['check_id']: c for c in manifest['checks']}
    if not floor <= set(by_id):
        _refuse('floor_not_in_manifest', ', '.join(sorted(floor - set(by_id), key=_key)))
    if version:
        for check_id in sorted(floor, key=_key):
            if by_id[check_id]['applicability']['kind'] != 'unconditional':
                _refuse('floor_check_conditional', check_id)
        # a surrogate is conditional by validation, so it can never be a floor check
    try:
        record_digest = rr.validate_record(record, floor_mandatory_rule_ids=floor)
    except rr.RegistryRefusal as exc:
        if exc.code in ('unknown_evaluator', 'unqualified_evaluator'):
            _refuse(exc.code, _evaluator_fault(record))
        _refuse('registry_record_invalid', exc.code)
    except (ValueError, RecursionError):
        _refuse('registry_record_invalid', 'record is not canonicalizable')
    return _complete(manifest, manifest_digest, version, _registry_from_record(record, record_digest),
                     executed, dispositions)


def _bind_registry(manifest, registry):
    """Every manifest check has rule entries that agree with it, and a qualified evaluator pair."""
    for check in manifest['checks']:
        entries = registry['rules'].get(check['check_id'])
        if not entries:
            _refuse('registry_rule_missing', check['check_id'])
        app = check.get('applicability', {'kind': 'unconditional'})
        conditional = app['kind'] == 'required_when_applicable'
        if conditional and not registry['conditional_supported']:
            _refuse('applicability_unsupported_by_registry', check['check_id'])
        for rule in entries:
            if rule['status'] != 'required':
                _refuse('registry_rule_not_required', check['check_id'])
            if conditional:
                want = {'kind': 'required_when_applicable', 'predicate': app['predicate']}
                got = rule['applicability']
                if type(got) is not dict or {k: got.get(k) for k in want} != want:
                    _refuse('predicate_mismatch', check['check_id'])
            elif rule['applicability'] != {'kind': 'always'}:
                _refuse('registry_rule_not_required', check['check_id'])
            if (rule['evaluator_id'], rule['evaluator_version']) \
                    != (check['evaluator_id'], check['evaluator_version']):
                _refuse('rule_evaluator_mismatch', check['check_id'])
        key = (check['evaluator_id'], check['evaluator_version'])
        if key not in registry['qualified']:
            _refuse('unknown_evaluator', check['evaluator_id'])
        if not _text(registry['qualified'][key]):
            _refuse('unqualified_evaluator', check['evaluator_id'])


def _complete(manifest, manifest_digest, version, registry, executed, dispositions):
    manifest_checks = manifest['checks']
    by_id = {c['check_id']: c for c in manifest_checks}
    _bind_registry(manifest, registry)
    _validate_executed_shape(executed)
    if dispositions is not None:
        _validate_dispositions_shape(dispositions)
    results = {}
    surrogates = {s['check_id']: s for s in manifest.get('surrogates', [])}
    for entry in executed:
        check = by_id.get(entry['check_id'])
        if check is None:
            _refuse('unexpected_check', entry['check_id'])
        if entry['check_id'] in results:
            _refuse('duplicate_result', entry['check_id'])
        outcome = entry['outcome']
        if outcome not in (OUTCOMES_1 if version else OUTCOMES):
            _refuse('invalid_outcome', entry['check_id'])
        if check['check_id'] in surrogates and outcome not in SURROGATE_OUTCOMES:
            _refuse('invalid_outcome', entry['check_id'] + ' (a surrogate is abstained or error only)')
        if entry['evaluator_id'] != check['evaluator_id'] \
                or entry['evaluator_version'] != check['evaluator_version']:
            _refuse('evaluator_mismatch', entry['check_id'])
        if outcome == 'not_applicable':
            if not _text(entry['reason']) or entry['reason'] not in check['not_applicable_reasons']:
                _refuse('not_applicable_reason_not_allowed', entry['check_id'])
        elif version and outcome == 'abstained':
            if not _text(entry['reason']):
                _refuse('schema_invalid', 'abstained must carry its could-not-check reason as text')
        elif version and outcome == 'error' and entry['reason'] is not None:
            if not _text(entry['reason']):
                _refuse('schema_invalid', 'error reason must be text or null')
        elif entry['reason'] is not None:
            _refuse('schema_invalid', 'reason must be null unless not_applicable')
        if check['check_id'] in surrogates and not _text(entry['reason']):
            _refuse('schema_invalid', 'a surrogate must retain its trigger as reason text')
        results[entry['check_id']] = entry
    inapplicable = {}
    predicates = {p['predicate_id']: p for p in manifest.get('predicates', [])}
    for entry in dispositions or []:
        check = by_id.get(entry['check_id'])
        if check is None:
            _refuse('unexpected_check', entry['check_id'])
        if entry['check_id'] in results or entry['check_id'] in inapplicable:
            _refuse('duplicate_result', entry['check_id'])
        app = check['applicability']
        if app['kind'] != 'required_when_applicable':
            _refuse('inapplicable_not_permitted', entry['check_id'])
        if entry['predicate'] != app['predicate']:
            _refuse('predicate_mismatch', entry['check_id'])
        if entry['justification'] not in predicates[app['predicate']]['justifications']:
            _refuse('justification_not_allowed', entry['check_id'])
        if entry['evaluator_id'] != check['evaluator_id'] \
                or entry['evaluator_version'] != check['evaluator_version']:
            _refuse('evaluator_mismatch', entry['check_id'])
        inapplicable[entry['check_id']] = entry
    missing = [c['check_id'] for c in manifest_checks
               if c['check_id'] not in results and c['check_id'] not in inapplicable]
    if missing:
        _refuse('skipped_mandatory_check', ', '.join(missing))
    counts = {name: 0 for name in OUTCOMES}
    if version:
        counts['abstained'] = 0
        counts['inapplicable'] = 0
        counts['surrogate'] = 0
    report_checks = []
    for check in manifest_checks:
        row = {'check_id': check['check_id']}
        if check['check_id'] in results:
            entry = results[check['check_id']]
            counts[entry['outcome']] += 1
            row.update(outcome=entry['outcome'], reason=entry['reason'])
            predicate = None
            established = {'passed': True, 'failed': True, 'abstained': False, 'error': False}.get(
                entry['outcome'])
        else:
            entry = inapplicable[check['check_id']]
            counts['inapplicable'] += 1
            row.update(outcome='inapplicable', reason=entry['justification'])
            predicate = entry['predicate']
            established = None
        if version:
            row['predicate'] = predicate
            row['result_established'] = established
            surrogate = surrogates.get(check['check_id'])
            row['surrogate'] = None
            if surrogate is not None and check['check_id'] in results:
                row['surrogate'] = surrogate['failure_condition']
                counts['surrogate'] += 1
        report_checks.append(row)
    return {'manifest_digest': manifest_digest, 'record_digest': registry['record_digest'],
            'complete': True, 'counts': counts, 'checks': report_checks}
