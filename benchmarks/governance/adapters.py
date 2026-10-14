"""Measured configurations, not upstream product certification.

The conventional application supplies transactionality, identity verification,
current state, idempotency and audit; OPA supplies the policy decision. LangGraph
adds a persistent approval interrupt around that same application. Shared Cognous
wire/signature helpers intentionally keep cryptographic inputs identical.
"""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import subprocess
from typing import TypedDict
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from reference_profiles.protected_destination import ProtectedDestination
from reference_profiles.assurance_runtime import digest
from reference_profiles.trust_evidence import signed, verify

POLICY = Path(__file__).with_name('policy.rego')


class Fixture:
    def __init__(self, root, opa, mutation=None):
        self.root = Path(root); self.root.mkdir(parents=True)
        self.path = self.root / 'destination.sqlite'; self.opa = opa
        self.now = 100; self.serial = 0; self.mutation = mutation
        self.keys = {p: Ed25519PrivateKey.generate() for p in ('admin', 'broker', 'verifier', 'agent')}
        self.registry = {p: {'public_key': k.public_key().public_bytes_raw().hex(),
                            'not_before': 0, 'expires_at': 1000, 'revoked_at': None}
                         for p, k in self.keys.items()}

    def request(self, changes=None, fault=None):
        self.serial += 1; identity = 'command-' + str(self.serial)
        args = dict(grant='grant', effect='effect', generation=7, policy='policy1',
                    target='sink', payload='synthetic', issuer_claims={}, verifier_status=None)
        args.update(changes or {})
        committed = {k: v for k, v in args.items() if k not in ('issuer_claims', 'verifier_status')}
        stamp = self.now - 1 if fault == 'stale_verifier' else self.now
        if fault != 'missing_verifier':
            args['verifier_status'] = signed(self.keys['verifier'], 'verifier', 'destination-status',
                dict(at=stamp, expires_at=stamp+1, command=identity,
                     request_digest=digest(committed), generation=args['generation'], active=True))
        actor = 'agent' if fault == 'wrong_actor' else 'broker'
        request = signed(self.keys[actor], actor, 'destination-command',
                         dict(id=identity, operation='execute', at=self.now, arguments=args))
        if fault == 'forged_signature': request['signature'] = '00' * 64
        return request

    def snapshot(self):
        with sqlite3.connect(f'file:{self.path}?mode=ro', uri=True) as c:
            effects = [dict(id=r[0], request=r[1], payload=r[2])
                       for r in c.execute('SELECT id,request,payload FROM effects ORDER BY id')]
            events = [json.loads(r[0]) for r in c.execute('SELECT body FROM events ORDER BY seq')]
        return {'effects': effects, 'events': events}

    def break_audit(self):
        with sqlite3.connect(self.path) as c:
            c.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT,'synthetic audit outage'); END")


class Cognous(Fixture):
    def __init__(self, root, opa, mutation=None):
        super().__init__(root, opa, mutation)
        self.config = dict(registry=self.registry, admin='admin', custodian='broker', verifier='verifier')
        self.runtime = ProtectedDestination.create(self.path, authority_backup_set='authority',
            destination_backup_set='destination', clock=lambda: self.now, **self.config)
        self.control('fence', scope='tenant', generation=7)
        self.control('destination_grants', principal='agent', credential_version='v1',
                     dependency_version='d1', grants=['read', 'write'])
        self.control('provision', id='grant', scope='tenant', generation=7, principal='agent',
                     policy='policy1', target='sink', credential_version='v1', dependency_version='d1',
                     modes={}, max_effects=1, expires_at=200)

    def control(self, operation, **args):
        self.serial += 1
        r = signed(self.keys['admin'], 'admin', 'destination-command',
                   dict(id='control-'+str(self.serial), operation=operation, at=self.now, arguments=args))
        output = self.runtime.apply(r)
        if output['status'] != 'accepted': raise RuntimeError(output)

    def apply(self, request): return self.runtime.apply(request)
    def revoke(self): self.control('revoke', grant='grant')
    def fence(self): self.control('fence', scope='tenant', generation=8)
    def rotate(self):
        self.control('destination_grants', principal='agent', credential_version='v2',
                     dependency_version='d1', grants=['read', 'write'])
    def reopen(self): self.runtime = ProtectedDestination(self.path, clock=lambda: self.now, **self.config)


class Conventional(Fixture):
    def __init__(self, root, opa, mutation=None):
        super().__init__(root, opa, mutation)
        with sqlite3.connect(self.path) as c:
            c.executescript('CREATE TABLE state(body TEXT); CREATE TABLE effects(id TEXT PRIMARY KEY,request TEXT,payload TEXT); CREATE TABLE events(seq INTEGER PRIMARY KEY,body TEXT);')
            c.execute('INSERT INTO state VALUES(?)', (json.dumps(dict(generation=7, grant_generation=7,
                policy='policy1', target='sink', revoked=False, consumed=0, max_effects=1, expires_at=200,
                credential='v1', provisioned_credential='v1', dependency='d1', provisioned_dependency='d1',
                grants=['read','write'], provisioned_grants=['read','write'])),))

    def change(self, **changes):
        with sqlite3.connect(self.path) as c:
            c.execute('BEGIN IMMEDIATE')
            state = json.loads(c.execute('SELECT body FROM state').fetchone()[0]); state.update(changes)
            c.execute('UPDATE state SET body=?', (json.dumps(state),))

    def revoke(self): self.change(revoked=True)
    def fence(self): self.change(generation=8)
    def rotate(self): self.change(credential='v2')
    def reopen(self): pass  # Each call already opens the persisted destination anew.

    def authorize(self, data):
        data = deepcopy(data)
        if self.mutation == 'ignore_revocation': data['state']['revoked'] = False
        if self.mutation == 'ignore_target': data['target'] = data['state']['target']
        if self.mutation == 'ignore_verifier': data['verifier_valid'] = True
        if self.mutation == 'ignore_budget': data['state']['consumed'] = 0
        result = subprocess.run([self.opa, 'eval', '--format=json', '--stdin-input',
                                 '--data', str(POLICY), 'data.comparative.allow'],
                                input=json.dumps(data), text=True, capture_output=True, timeout=10, check=True)
        return json.loads(result.stdout)['result'][0]['expressions'][0]['value'] is True

    def apply(self, request):
        with sqlite3.connect(self.path, timeout=10) as c:
            c.execute('BEGIN IMMEDIATE')
            state = json.loads(c.execute('SELECT body FROM state').fetchone()[0])
            body = request['body']; args = body['arguments']; identity = body['id']
            reason = None; duplicate = False
            try:
                if request['issuer'] != 'broker' or request['kind'] != 'destination-command':
                    raise ValueError('SIGNER_SCOPE')
                verify(request, self.registry, at=body['at'], now=self.now)
            except ValueError:
                reason = 'AUTHENTICATION_DENIED'
            committed = {k:v for k,v in args.items() if k not in ('issuer_claims','verifier_status')}
            binding = digest(committed)
            # Like the tested Cognous profile, a historical receipt can be read
            # after revocation, but only under the unchanged fence and hard pins.
            if reason is None and (args['grant'] != 'grant' or args['generation'] != state['generation']
                or args['generation'] != state['grant_generation'] or args['policy'] != state['policy']
                or (args['target'] != state['target'] and self.mutation != 'ignore_target')):
                reason = 'BINDING_DENIED'
            prior = c.execute('SELECT request FROM effects WHERE id=?', (args['effect'],)).fetchone()
            if reason is None and prior:
                if prior[0] != binding: reason = 'EFFECT_ID_CONFLICT'
                else: duplicate = True
            if reason is None and not duplicate:
                valid = False
                try:
                    status_record = args['verifier_status']; status = status_record['body']
                    verify(status_record, self.registry, at=status['at'], now=self.now)
                    valid = (status_record['issuer'] == 'verifier' and status_record['kind'] == 'destination-status'
                             and status['command'] == identity and status['request_digest'] == binding
                             and status['generation'] == state['generation'] and status['active'] is True
                             and status['at'] == self.now < status['expires_at'])
                except (ValueError, TypeError, KeyError): pass
                allowed = self.authorize(dict(generation=args['generation'], policy=args['policy'],
                    target=args['target'], state=state, now=self.now, verifier_valid=valid))
                if not allowed: reason = 'POLICY_DENIED'
                else:
                    c.execute('INSERT INTO effects VALUES(?,?,?)',
                              (args['effect'], binding, json.dumps(args['payload'],separators=(',',':'),sort_keys=True)))
                    state['consumed'] += 1
                    c.execute('UPDATE state SET body=?', (json.dumps(state),))
            output = {'status': 'denied' if reason else 'accepted', 'reason': reason,
                      'result': {'duplicate': duplicate}}
            c.execute('INSERT INTO events(body) VALUES(?)', (json.dumps(dict(operation='execute', command=identity,
                request_digest=digest(request), status=output['status'], reason=reason, at=self.now)),))
            return output


class GraphState(TypedDict, total=False):
    request: dict
    result: dict


class LangGraphOPA(Conventional):
    def apply(self, request):
        from langgraph.graph import StateGraph, START, END
        from langgraph.types import interrupt, Command
        from langgraph.checkpoint.sqlite import SqliteSaver

        def approval(state):
            approved = interrupt({'request_digest': digest(state['request'])})
            if approved is not True: raise ValueError('approval not granted')
            return {}

        def effect(state):
            return {'result': super(LangGraphOPA, self).apply(state['request'])}

        builder = StateGraph(GraphState)
        builder.add_node('approval', approval); builder.add_node('effect', effect)
        builder.add_edge(START, 'approval'); builder.add_edge('approval', 'effect'); builder.add_edge('effect', END)
        with SqliteSaver.from_conn_string(str(self.root / 'checkpoints.sqlite')) as saver:
            graph = builder.compile(checkpointer=saver)
            config = {'configurable': {'thread_id': request['body']['id']}}
            pending = graph.invoke({'request': request}, config)
            if not pending.get('__interrupt__'): raise RuntimeError('expected durable approval interrupt')
            return graph.invoke(Command(resume=True), config)['result']
