"""Context journal coverage against caller-held commitments, never authority.

A trusted caller obtains expected_count and checkpoint independently of the
received journal. This verifies retained bytes and sequence coverage, not event
truth, capture completeness, custody independence, or current permission.
"""
import hashlib
import json
from reference_profiles.context_memory import canonical
from reference_profiles.bounded_json import snapshot

LIMITS = {'authorizing': False, 'independent_custody_verified': False,
          'capture_completeness_verified': False, 'production_ready': False}


def prefix_digest(events):
    return hashlib.sha256(canonical(events).encode()).hexdigest()


def export_context_journal(memory):
    with memory.connection() as conn:
        conn.execute('BEGIN')
        rows = conn.execute('SELECT seq,kind,item_id,detail FROM events ORDER BY seq').fetchall()
        events = [dict(seq=r['seq'], kind=r['kind'], item_id=r['item_id'], detail=json.loads(r['detail'])) for r in rows]
    return {'contract': 'context-journal/1', 'events': events, 'limits': dict(LIMITS)}


def assess_context_journal(package, *, expected_count, checkpoint, max_uncommitted_events=0):
    """Tri-state record predicates; violated means a record contract violation.

    expected_count, checkpoint and lag policy are trusted caller inputs. The
    checkpoint is {count, sha256}; obtaining an independent acknowledgment and
    enforcing any time-based outage policy are deployment responsibilities.
    """
    def count(v):
        return type(v) is int and v >= 0
    if (not count(expected_count) or not count(max_uncommitted_events)
            or type(checkpoint) is not dict or set(checkpoint) != {'count', 'sha256'}
            or not count(checkpoint['count']) or checkpoint['count'] > expected_count
            or type(checkpoint['sha256']) is not str or len(checkpoint['sha256']) != 64
            or any(c not in '0123456789abcdef' for c in checkpoint['sha256'])):
        raise ValueError('trusted expected count, checkpoint and lag policy required')
    result = {'contract': 'context-journal-assessment/1', **LIMITS,
              'record_coverage': 'unevaluable', 'checkpoint_match': 'unevaluable',
              'custody_lag': 'unevaluable', 'uncommitted_events': None,
              'reason': 'MISSING_JOURNAL'}
    if package is None:
        return result
    try:
        if (type(package) is not dict or set(package) != {'contract', 'events', 'limits'}
                or package['contract'] != 'context-journal/1' or package['limits'] != LIMITS
                or any(type(v) is not bool for v in package['limits'].values())
                or type(package['events']) is not list):
            raise ValueError('INVALID_JOURNAL')
        events = package['events']
        if len(events) != expected_count:
            raise ValueError('EXPECTED_EVENT_COUNT_MISMATCH')
        events = snapshot(events)
        for seq, event in enumerate(events, 1):
            if (type(event) is not dict or set(event) != {'seq', 'kind', 'item_id', 'detail'}
                    or type(event['seq']) is not int or event['seq'] != seq
                    or any(type(event[k]) is not str or not event[k] for k in ('kind', 'item_id'))
                    or type(event['detail']) is not dict):
                raise ValueError('SEQUENCE_OR_RECORD_INVALID')
        # Reject non-JSON values even in a tail beyond the checkpoint.
        canonical(events)
        result['record_coverage'] = 'compliant'
        if prefix_digest(events[:checkpoint['count']]) != checkpoint['sha256']:
            result.update(checkpoint_match='violated', reason='CHECKPOINT_MISMATCH')
            return result
        lag = expected_count - checkpoint['count']
        result.update(checkpoint_match='compliant', uncommitted_events=lag,
                      custody_lag='compliant' if lag <= max_uncommitted_events else 'violated',
                      reason='RECORD_CONTRACT_SATISFIED' if lag <= max_uncommitted_events else 'CHECKPOINT_LAG_EXCEEDED')
        return result
    except (KeyError, TypeError, ValueError, OverflowError):
        result.update(record_coverage='violated', reason='INVALID_OR_INCOMPLETE_JOURNAL')
        return result
