"""Bind delivered context to one actual atomic execution in a trusted local host.

Context and destination are separate SQLite stores. The context write lock
orders cooperating context changes against the destination call; this is not a
cross-database commit. A durable started marker forbids blind retries.
"""
import dataclasses
from contextlib import closing
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR
import sqlite3
import json
import uuid
from engine.safe_executor import commitment, snapshot_envelope
from engine.atomic_local_control_plane_executor import AtomicLocalControlPlaneExecutor


class ContextBoundExecutor:
    PURPOSES = {'urn:cognous:action:refund-issue-routine-v1': 'refund'}

    def check_use(self, delivery, envelope):
        if (self.PURPOSES.get(envelope.operation.action_id) != delivery['purpose']
                or delivery['recipient'] != envelope.operation.actor):
            raise PermissionError('context purpose or recipient does not match action')

    def __init__(self, memory, executor):
        if not isinstance(executor, AtomicLocalControlPlaneExecutor):
            raise TypeError('accepted local atomic executor required')
        self.memory, self.executor = memory, executor
        with memory.connection() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS context_actions (
                id TEXT PRIMARY KEY, delivery_id TEXT NOT NULL, generation INTEGER NOT NULL,
                envelope_digest TEXT NOT NULL, claim_id TEXT NOT NULL, state TEXT NOT NULL, receipt_digest TEXT NOT NULL)''')

    @staticmethod
    def envelope_digest(envelope):
        return commitment(dataclasses.asdict(snapshot_envelope(envelope)))

    @staticmethod
    def context_deadline(receipt):
        # Epoch seconds in the shared trusted UTC time domain. Round toward the
        # past to avoid extending a fractional deadline at datetime precision.
        micros = int((Decimal(str(receipt['expires_at'])) * 1000000).to_integral_value(rounding=ROUND_FLOOR))
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=micros)

    def current_delivery(self, conn, delivery_id):
        delivery = conn.execute('SELECT * FROM deliveries WHERE id=?', (delivery_id,)).fetchone()
        if delivery is None or delivery['state'] != 'delivered':
            raise PermissionError('acknowledged context delivery required')
        generation = conn.execute('SELECT value FROM generation WHERE id=1').fetchone()[0]
        if generation != delivery['generation']:
            raise PermissionError('context changed since delivery')
        row = self.memory._readable(conn, delivery['item_id'], delivery['purpose'], delivery['recipient'], set())
        return delivery, generation, json.loads(row['receipt'])

    def provision_claim(self, *, delivery_id, proposal, decision, now):
        # Clamp at issuance; no existing authority or claim is mutated.
        with self.memory.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            delivery, _, receipt = self.current_delivery(conn, delivery_id)
            if (self.PURPOSES.get(proposal.action_id) != delivery['purpose']
                    or delivery['recipient'] != proposal.actor):
                raise PermissionError('context purpose or recipient does not match action')
            claim = self.executor.provision_claim(proposal=proposal, decision=decision, now=now,
                       expires_at=self.context_deadline(receipt).isoformat())
            conn.commit()
        return claim

    def check_claim_deadline(self, claim_id, receipt):
        # This adapter reads the accepted local profile's persisted claim. The
        # destination still performs its own complete claim validation at commit.
        with closing(sqlite3.connect(self.executor.destination.path.as_uri() + '?mode=ro', uri=True)) as conn:
            row = conn.execute('SELECT claim_json FROM execution_claims_v1 WHERE claim_id=?', (claim_id,)).fetchone()
        if row is None:
            raise PermissionError('execution claim unavailable')
        expires = datetime.fromisoformat(json.loads(row[0])['expires_at'])
        if expires.tzinfo is None or expires > self.context_deadline(receipt):
            raise PermissionError('execution claim exceeds context deadline')

    def bind(self, *, delivery_id, envelope, claim_id):
        if type(claim_id) is not str or not claim_id:
            raise ValueError('exact execution claim required')
        identity = str(uuid.uuid4())
        with self.memory.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            delivery, generation, receipt = self.current_delivery(conn, delivery_id)
            self.check_use(delivery, envelope)
            self.check_claim_deadline(claim_id, receipt)
            receipt_digest = commitment(receipt)
            conn.execute('INSERT INTO context_actions VALUES (?,?,?,?,?,?,?)',
                         (identity, delivery_id, generation, self.envelope_digest(envelope), claim_id, 'issued', receipt_digest))
            self.memory.event(conn, 'action_binding', delivery['item_id'], {'binding_id': identity, 'delivery_id': delivery_id})
            conn.commit()
        return identity

    def execute(self, *, binding_id, envelope, claim_id):
        digest = self.envelope_digest(envelope)
        # Commit uncertainty before entering the effect path. No started binding
        # can execute again, even if an earlier call produced no observed effect.
        with self.memory.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            binding = conn.execute('SELECT * FROM context_actions WHERE id=?', (binding_id,)).fetchone()
            if (binding is None or binding['state'] != 'issued' or binding['envelope_digest'] != digest
                    or binding['claim_id'] != claim_id):
                raise PermissionError('binding unavailable or substituted')
            conn.execute("UPDATE context_actions SET state='started' WHERE id=?", (binding_id,))
            conn.commit()
        with self.memory.connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            generation = conn.execute('SELECT value FROM generation WHERE id=1').fetchone()[0]
            if generation != binding['generation']:
                raise PermissionError('context changed before effect')
            delivery = conn.execute('SELECT * FROM deliveries WHERE id=?', (binding['delivery_id'],)).fetchone()
            if delivery is None or delivery['state'] != 'delivered':
                raise PermissionError('delivery evidence unavailable')
            self.check_use(delivery, envelope)
            row = self.memory._readable(conn, delivery['item_id'], delivery['purpose'], delivery['recipient'], set())
            if commitment(json.loads(row['receipt'])) != binding['receipt_digest']:
                raise PermissionError('context receipt changed')
            self.check_claim_deadline(claim_id, json.loads(row['receipt']))
            # All cooperating memory mutations need this write lock. The actual
            # executor independently checks authority and commits its own store.
            result = self.executor.execute(envelope=envelope, claim_id=claim_id)
            self.memory.event(conn, 'bound_action_result', delivery['item_id'],
                              {'binding_id': binding_id, 'effect_id': result.effect_id, 'status': result.status})
            conn.execute("UPDATE context_actions SET state='finished' WHERE id=?", (binding_id,))
            conn.commit()
        return result

    def reconcile(self, *, binding_id, envelope, claim_id):
        with self.memory.connection() as conn:
            binding = conn.execute('SELECT * FROM context_actions WHERE id=?', (binding_id,)).fetchone()
        if (binding is None or binding['envelope_digest'] != self.envelope_digest(envelope)
                or binding['claim_id'] != claim_id):
            raise PermissionError('recovery binding mismatch')
        return self.executor.reconcile(envelope=envelope, claim_id=claim_id)
