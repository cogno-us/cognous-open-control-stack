"""Trusted-host rollback memory for synthetic resolver observations, not permission.

The database must be provisioned explicitly. Deletion, unreadability or schema
failure never recreates an empty ledger during resolution. A hostile database
owner, backup rollback and a later authority change remain outside this profile.
"""
from contextlib import closing
import hashlib
from pathlib import Path
import sqlite3
from reference_profiles.resolver_assurance import canonical


class RevisionLedger:
    def __init__(self, path):
        self.path = Path(path).resolve()

    @classmethod
    def create(cls, path):
        ledger = cls(path)
        # Exclusive creation prevents an accidental reinitialization of history.
        with ledger.path.open('xb'):
            pass
        with closing(sqlite3.connect(ledger.path)) as conn:
            conn.execute('PRAGMA synchronous=FULL')
            conn.execute('CREATE TABLE revisions (scope TEXT PRIMARY KEY, revision INTEGER NOT NULL, facts TEXT NOT NULL, conflicted INTEGER NOT NULL)')
            conn.commit()
        return ledger

    def observe(self, profile, record):
        """Called only after source authentication, scope and freshness checks.

        Profile/key versions intentionally do not partition the revision floor.
        Source identity and exact object scope must survive key rotation. The
        source contract requires revision increments for status/fact changes.
        """
        scope = canonical({'source_id': profile.source_id, 'binding': record['binding']}).decode()
        facts = hashlib.sha256(canonical({k: record[k] for k in ('status', 'facts_digest', 'effective_at')})).hexdigest()
        revision = record['revision']
        with closing(sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, isolation_level=None, timeout=5)) as conn:
            conn.execute('PRAGMA synchronous=FULL')
            conn.execute('BEGIN IMMEDIATE')
            old = conn.execute('SELECT revision, facts, conflicted FROM revisions WHERE scope=?', (scope,)).fetchone()
            if old is not None and revision < old[0]:
                conn.rollback()
                return 'STALE'
            if old is not None and revision == old[0]:
                if old[2] or facts != old[1]:
                    conn.execute('UPDATE revisions SET conflicted=1 WHERE scope=?', (scope,))
                    conn.commit()
                    return 'CONFLICT'
                conn.commit()
                return record['status']
            conn.execute('INSERT INTO revisions VALUES (?,?,?,0) ON CONFLICT(scope) DO UPDATE SET revision=excluded.revision,facts=excluded.facts,conflicted=0',
                         (scope, revision, facts))
            conn.commit()
        return record['status']
