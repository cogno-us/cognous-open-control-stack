"""Synthetic trusted-host memory admission and delivery; no execution authority."""
from contextlib import closing, contextmanager
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import uuid


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def labels(values):
    if not isinstance(values, (list, tuple)) or not values or any(type(v) is not str or not v.strip() for v in values):
        raise ValueError('nonempty explicit labels required')
    return sorted(set(values))


class ContextMemory:
    """Local reference only: callers, policy configuration and database owner are trusted.

    Time is supplied by a host clock. Content and receipt admission share a
    transaction. Delivery intent commits before a callback sees content.
    """
    def __init__(self, path, *, clock):
        self.path = Path(path).resolve()
        self.clock = clock
        with self.connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS generation (id INTEGER PRIMARY KEY CHECK(id=1), value INTEGER NOT NULL);
                INSERT OR IGNORE INTO generation VALUES (1,0);
                CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY, content TEXT, commitment TEXT NOT NULL,
                    receipt TEXT NOT NULL, status TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY, kind TEXT NOT NULL, item_id TEXT NOT NULL,
                    detail TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS deliveries (
                    id TEXT PRIMARY KEY, item_id TEXT NOT NULL, generation INTEGER NOT NULL,
                    purpose TEXT NOT NULL, recipient TEXT NOT NULL, state TEXT NOT NULL);
            ''')

    def now(self):
        value = self.clock()
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError('finite trusted time required')
        return value

    @contextmanager
    def connection(self):
        with closing(sqlite3.connect(self.path, isolation_level=None, timeout=5)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA synchronous=FULL')
            yield conn

    @staticmethod
    def event(conn, kind, item, detail):
        conn.execute('INSERT INTO events(kind,item_id,detail) VALUES (?,?,?)', (kind, item, canonical(detail)))

    def generation(self):
        with self.connection() as conn:
            return conn.execute('SELECT value FROM generation WHERE id=1').fetchone()[0]

    def admit(self, *, item_id, content, purposes, recipients, obligations, expires_at, source_ref, parents=()):
        purposes, recipients = labels(purposes), labels(recipients)
        obligations = labels(obligations)
        if type(content) is not str or type(item_id) is not str or not item_id or type(source_ref) is not str or not source_ref:
            raise ValueError('content and stable item/source identities required')
        if type(expires_at) not in (int, float) or not self.now() < expires_at < float('inf'):
            raise ValueError('finite future expiry required')
        if not isinstance(parents, (list, tuple)) or any(type(p) is not str for p in parents):
            raise ValueError('parent identities required')
        commitment = hashlib.sha256(content.encode()).hexdigest()
        receipt = {'version': 'context-memory/1', 'item_id': item_id, 'content_sha256': commitment,
                   'purposes': purposes, 'recipients': recipients, 'obligations': obligations,
                   'expires_at': expires_at, 'source_ref': source_ref, 'parents': sorted(set(parents)),
                   'authorizing': False}
        with self.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            try:
                for parent in receipt['parents']:
                    row = conn.execute('SELECT * FROM items WHERE id=?', (parent,)).fetchone()
                    if row is None or row['status'] != 'admitted':
                        raise PermissionError('parent unavailable')
                    prior = json.loads(row['receipt'])
                    if not (self.now() < prior['expires_at'] and expires_at <= prior['expires_at']
                            and set(purposes) <= set(prior['purposes']) and set(recipients) <= set(prior['recipients'])
                            and set(obligations) >= set(prior['obligations'])):
                        raise PermissionError('derivation weakens parent restrictions')
                conn.execute('INSERT INTO items VALUES (?,?,?,?,?)', (item_id, content, commitment, canonical(receipt), 'admitted'))
                conn.execute('UPDATE generation SET value=value+1 WHERE id=1')
                self.event(conn, 'admission', item_id, {'receipt': receipt})
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return receipt

    def revoke(self, item_id):
        with self.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            row = conn.execute('SELECT id FROM items WHERE id=?', (item_id,)).fetchone()
            if row is None:
                conn.rollback()
                raise KeyError(item_id)
            conn.execute("UPDATE items SET status='revoked' WHERE id=?", (item_id,))
            conn.execute('UPDATE generation SET value=value+1 WHERE id=1')
            self.event(conn, 'revocation', item_id, {})
            conn.commit()

    def _readable(self, conn, item_id, purpose, recipient, seen):
        if item_id in seen:
            raise PermissionError('cyclic provenance')
        seen = seen | {item_id}
        row = conn.execute('SELECT * FROM items WHERE id=?', (item_id,)).fetchone()
        if row is None or row['status'] != 'admitted' or row['content'] is None:
            raise PermissionError('item unavailable')
        receipt = json.loads(row['receipt'])
        if (self.now() >= receipt['expires_at'] or purpose not in receipt['purposes'] or recipient not in receipt['recipients']):
            raise PermissionError('current use not permitted')
        if hashlib.sha256(row['content'].encode()).hexdigest() != row['commitment']:
            raise PermissionError('content commitment mismatch')
        for parent in receipt['parents']:
            self._readable(conn, parent, purpose, recipient, seen)
        return row

    def deliver(self, item_id, *, purpose, recipient, expected_generation, callback):
        delivery_id = str(uuid.uuid4())
        with self.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            try:
                generation = conn.execute('SELECT value FROM generation WHERE id=1').fetchone()[0]
                if type(expected_generation) is not int or generation != expected_generation:
                    raise PermissionError('stale context generation')
                row = self._readable(conn, item_id, purpose, recipient, set())
            except PermissionError as exc:
                self.event(conn, 'recall_denied', item_id, {'reason': str(exc)})
                conn.commit()
                raise
            conn.execute('INSERT INTO deliveries VALUES (?,?,?,?,?,?)',
                         (delivery_id, item_id, generation, purpose, recipient, 'pending'))
            self.event(conn, 'delivery_intent', item_id, {'delivery_id': delivery_id, 'generation': generation})
            conn.commit()
        # Revocation after this local dispatch admission cannot retract content.
        # A crash here leaves pending, never a permission to repeat delivery.
        try:
            callback(row['content'])
        except Exception:
            state = 'unknown'
        else:
            state = 'delivered'
        with self.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            conn.execute('UPDATE deliveries SET state=? WHERE id=?', (state, delivery_id))
            self.event(conn, 'delivery_outcome', item_id, {'delivery_id': delivery_id, 'state': state})
            conn.commit()
        return {'delivery_id': delivery_id, 'state': state, 'generation': generation,
                'authorizing': False, 'model_reliance_verified': False}

    def purge_expired(self):
        with self.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            ids = [r['id'] for r in conn.execute("SELECT * FROM items WHERE content IS NOT NULL")
                   if json.loads(r['receipt'])['expires_at'] <= self.now()]
            for item_id in ids:
                conn.execute("UPDATE items SET content=NULL,status='expired' WHERE id=?", (item_id,))
                self.event(conn, 'content_expired', item_id, {})
            if ids:
                conn.execute('UPDATE generation SET value=value+1 WHERE id=1')
            conn.commit()
        return ids
