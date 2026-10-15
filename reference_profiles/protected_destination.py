"""Synthetic destination outside a declared authority restore set.

The destination owns its monotonic fence, effective-grant view, consumption,
credential bindings, audit and SQLite effects in one transaction domain. Restoring
this destination too is OUTSIDE the guarantee. Bootstrap identities, clock, host
and backup-set declarations are trusted; no network or real credential adapter.
"""
from copy import deepcopy
from contextvars import ContextVar
from functools import wraps
import json
from pathlib import Path
import sqlite3
from .assurance_runtime import AssuranceRuntime, Denied, require, exact, label, integer, names, sha, digest, canonical
from .trust_evidence import verify, wire


# Fixed policy, independent of attacker-supplied identifiers. Changing policy is a
# reviewed host upgrade, not a request field. No per-issuer/bucket rows.
ATTEMPTS_PER_INTERVAL = 128
INTERVAL_SECONDS = 60
UNAUTHENTICATED_DETAIL_LIMIT = 64
COUNTER_MAX = 9223372036854775807
_ADMISSION = ContextVar('destination_admission', default=None)


def admitted(method):
    @wraps(method)
    def guarded(self, c, *args):
        require(_ADMISSION.get() == (self, c), 'DESTINATION_ADMISSION_REQUIRED')
        return method(self, c, *args)
    return guarded


class ProtectedDestination:
    # Deliberately do not inherit the unrelated HMAC runtime's admission routes.
    connection = AssuranceRuntime.connection
    get = staticmethod(AssuranceRuntime.get)
    put = staticmethod(AssuranceRuntime.put)
    population = staticmethod(AssuranceRuntime.population)
    now = AssuranceRuntime.now
    head = staticmethod(AssuranceRuntime.head)
    event = AssuranceRuntime.event

    def __init__(self, path, *, registry, admin, custodian, verifier, clock):
        self.path = Path(path).resolve(); self.registry = deepcopy(registry)
        self.admin = admin; self.custodian = custodian; self.verifier = verifier; self.clock = clock
        require(len({admin, custodian, verifier}) == 3, 'CUSTODY_SEPARATION')
        require(len({registry[p]['public_key'] for p in (admin, custodian, verifier)}) == 3, 'CUSTODY_KEY_SEPARATION')

    @classmethod
    def create(cls, path, *, authority_backup_set, destination_backup_set, **kwargs):
        label(authority_backup_set); label(destination_backup_set)
        require(authority_backup_set != destination_backup_set, 'FENCE_IN_SAME_BACKUP_SET')
        runtime = cls(path, **kwargs)
        with runtime.path.open('xb'): pass
        with sqlite3.connect(runtime.path) as c:
            c.executescript('CREATE TABLE objects(kind TEXT,id TEXT,body TEXT,PRIMARY KEY(kind,id)); CREATE TABLE events(seq INTEGER PRIMARY KEY,body TEXT,previous TEXT,head TEXT); CREATE TABLE effects(id TEXT PRIMARY KEY,run TEXT,request TEXT,payload TEXT,evidence TEXT);')
            runtime.put(c,'meta','restore',{'authority_backup_set':authority_backup_set,'destination_backup_set':destination_backup_set,'independent_administration_verified':False})
        return runtime

    def signed_body(self, record, issuer, kind):
        require(type(record) is dict and record.get('issuer') == issuer and record.get('kind') == kind, 'SIGNER_SCOPE')
        try: return verify(record,self.registry,at=record['body']['at'],now=self.now())
        except (ValueError,KeyError,TypeError): raise Denied('SIGNATURE_INVALID')

    @staticmethod
    def _increment(value):
        # Never wrap or silently lose counts. Exhaustion/storage failure raises;
        # the connection closes with the whole admission transaction uncommitted.
        require(value < COUNTER_MAX, 'INGRESS_COUNTER_EXHAUSTED')
        return value + 1

    def _ingress_state(self, c):
        stamp = integer(self.now())
        require(stamp <= COUNTER_MAX - INTERVAL_SECONDS, 'INGRESS_CLOCK_RANGE')
        c.execute('CREATE TABLE IF NOT EXISTS destination_ingress (singleton INTEGER PRIMARY KEY CHECK(singleton=1), body TEXT NOT NULL)')
        row = c.execute('SELECT body FROM destination_ingress WHERE singleton=1').fetchone()
        if row is None:
            # One-time additive migration counts legacy unauthenticated detail;
            # it never deletes/rechains history or grants a fresh retention cap.
            details = sum(json.loads(r[0]).get('command_authenticated') is not True
                          for r in c.execute('SELECT body FROM events'))
            state = dict(version=1, origin=stamp, start=stamp, end=stamp+INTERVAL_SECONDS,
                         used=0, interval_limited=0, requests=0, admitted=0,
                         limited=0, unauthenticated=0, details=details,
                         dropped_detail=0, recoveries=0)
        else:
            state = json.loads(row[0])
            require(state['version'] == 1, 'INGRESS_STATE_VERSION')
        # Regression never refills. A jump opens exactly one current interval;
        # no accumulated credits and no rows for elapsed time buckets.
        if stamp >= state['end']:
            state.update(start=stamp, end=stamp+INTERVAL_SECONDS, used=0, interval_limited=0)
        return state

    @staticmethod
    def _store_ingress(c, state):
        c.execute('INSERT INTO destination_ingress VALUES(1,?) ON CONFLICT(singleton) DO UPDATE SET body=excluded.body', (canonical(state),))

    def apply(self, request):
        return self._apply(request, recovery=False)

    def recover_ingress(self, request):
        """Trusted local administration only; never expose as a network route.

        Only a fresh, sequenced, signed ingress_recover command can bypass the
        regular budget. It cannot dispatch an effect or clear retained evidence.
        Invalid recovery input raises without allocating durable refusal rows.
        """
        return self._apply(request, recovery=True)

    def _apply(self, request, *, recovery):
        try: request = json.loads(wire(request))
        except (TypeError,ValueError): return {'status':'denied','reason':'INVALID_REQUEST'}
        if recovery:
            body = self.signed_body(request, self.admin, 'destination-command')
            exact(body, 'id operation at arguments sequence')
            require(body['operation'] == 'ingress_recover', 'RECOVERY_SCOPE')
            exact(body['arguments'], '')
        with self.connection() as c:
            c.execute('BEGIN IMMEDIATE')
            state = self._ingress_state(c)
            if not recovery:
                state['requests'] = self._increment(state['requests'])
                if state['used'] >= ATTEMPTS_PER_INTERVAL:
                    state['limited'] = self._increment(state['limited'])
                    state['interval_limited'] = self._increment(state['interval_limited'])
                    state['dropped_detail'] = self._increment(state['dropped_detail'])
                    self._store_ingress(c, state)
                    c.commit()
                    return {'status':'denied', 'reason':'INGRESS_SATURATED', 'production_authorized':False}
                state['used'] += 1
                state['admitted'] = self._increment(state['admitted'])
            operation='unknown'; identity='unknown'; claimed_identity='unknown'; authenticated=False
            # Correlation only: a supplied identifier is not proof of authority.
            # Keep the normal schema/signature admission sequence unchanged.
            if type(request) is dict and type(request.get('body')) is dict:
                try: claimed_identity=label(request['body'].get('id'))
                except Denied: pass
            try:
                body=request['body']
                require(type(body) is dict,'INVALID_FIELDS')
                operation=label(body.get('operation'))
                exact(body,'id operation at arguments' if operation=='execute' else 'id operation at arguments sequence')
                identity=label(body['id'])
                issuer=self.custodian if operation=='execute' else self.admin
                self.signed_body(request,issuer,'destination-command')
                authenticated=True
                require(operation in ('fence','destination_grants','provision','revoke','execute','ingress_recover'),'UNKNOWN_OPERATION')
                require(identity not in self.population(c,'command'),'COMMAND_REPLAY')
                if operation!='execute':
                    stamp=integer(body['at']);sequence=integer(body['sequence'],1)
                    require(0 <= self.now()-stamp <= 60,'COMMAND_STALE')
                    previous=self.population(c,'admin-sequence').get(issuer,{'sequence':0})
                    require(sequence>previous['sequence'],'SEQUENCE_REGRESSION')
                require(operation != 'ingress_recover' or recovery, 'RECOVERY_LOCAL_ONLY')
                c.execute('SAVEPOINT admission')
                token = _ADMISSION.set((self, c))
                try:
                    if operation == 'ingress_recover':
                        recoveries = self._increment(state['recoveries'])
                        state.update(used=0, recoveries=recoveries)
                        result = {'budget_reset':True, 'detail_retention_reset':False}
                    else:
                        result=getattr(self,'op_'+operation)(c,body['arguments'],identity)
                except Exception:
                    c.execute('ROLLBACK TO admission');c.execute('RELEASE admission');raise
                finally: _ADMISSION.reset(token)
                c.execute('RELEASE admission')
                self.put(c,'command',identity,{'digest':digest(request)},new=True)
                if operation!='execute':self.put(c,'admin-sequence',issuer,{'sequence':sequence})
                output={'status':'accepted','result':result,'production_authorized':False}
            except (Denied,KeyError,TypeError,ValueError) as exc:
                output={'status':'denied','reason':str(exc) if isinstance(exc,Denied) else 'INVALID_REQUEST','production_authorized':False}
            # Audit storage failure aborts the entire effect/consumption transaction.
            detail = authenticated
            if not recovery and not authenticated:
                state['unauthenticated'] = self._increment(state['unauthenticated'])
                detail = state['details'] < UNAUTHENTICATED_DETAIL_LIMIT
                if detail: state['details'] += 1
                else: state['dropped_detail'] = self._increment(state['dropped_detail'])
            if detail: self.event(c,{'operation':operation,'command':identity if authenticated else 'unknown','claimed_command':claimed_identity,'command_authenticated':authenticated,'request_digest':digest(request),'status':output['status'],'reason':output.get('reason'),'at':self.now()})
            self._store_ingress(c, state)
            c.commit();return output

    @admitted
    def op_fence(self,c,a,identity):
        exact(a,'scope generation');label(a['scope']);integer(a['generation'],1)
        old=self.population(c,'fence').get(a['scope'],{'generation':0})
        require(a['generation']>old['generation'],'FENCE_NOT_MONOTONIC')
        self.put(c,'fence',a['scope'],a);return a

    @admitted
    def op_destination_grants(self,c,a,identity):
        exact(a,'principal credential_version dependency_version grants');label(a['principal'])
        label(a['credential_version']);label(a['dependency_version']);names(a['grants'])
        self.put(c,'destination-grants',a['principal'],dict(a,grants=sorted(a['grants'])))
        return {'view_digest':digest(a),'authoritative_side':'destination'}

    @admitted
    def op_provision(self,c,a,identity):
        exact(a,'id scope generation principal policy target credential_version dependency_version modes max_effects expires_at')
        for f in ('id','scope','principal','policy','target','credential_version','dependency_version'):label(a[f])
        integer(a['generation'],1);integer(a['max_effects'],1);integer(a['expires_at'])
        require(self.now()<a['expires_at'],'GRANT_EXPIRED')
        require(a['generation']==self.get(c,'fence',a['scope'])['generation'],'AUTHORITY_STORE_BEHIND_FENCE')
        require(type(a['modes']) is dict and set(a['modes']) <= {'credential','dependency'},'SOFT_CLASS_FORBIDDEN')
        require(all(v in ('hard','soft') for v in a['modes'].values()),'INVALID_PIN_MODE')
        view=self.get(c,'destination-grants',a['principal'])
        require(view['credential_version']==a['credential_version'] and view['dependency_version']==a['dependency_version'],'PROVISION_VERSION_MISMATCH')
        self.put(c,'grant',a['id'],dict(a,grants=view['grants'],consumed=0,revoked=False,custodian=self.custodian,credential_binding_active=True),new=True)
        return {'grant':a['id'],'custodian':self.custodian,'agent_has_credential':False}

    @admitted
    def op_revoke(self,c,a,identity):
        exact(a,'grant');g=self.get(c,'grant',a['grant']);g['revoked']=True;g['credential_binding_active']=False
        self.put(c,'grant',a['grant'],g);return {'credential_binding_active':False}

    @admitted
    def op_execute(self,c,a,identity):
        exact(a,'grant effect generation policy target payload verifier_status issuer_claims')
        label(a['effect']);g=self.get(c,'grant',a['grant']);integer(a['generation'],1)
        # Destination fence, consumption and effect share the same writer transaction.
        fence=self.get(c,'fence',g['scope'])['generation']
        require(g['generation']==a['generation']==fence,'AUTHORITY_STORE_BEHIND_FENCE')
        require(a['policy']==g['policy'] and a['target']==g['target'],'HARD_PIN_CHANGED')
        request_digest=digest({k:v for k,v in a.items() if k not in ('verifier_status','issuer_claims')})
        prior=c.execute('SELECT request FROM effects WHERE id=?',(a['effect'],)).fetchone()
        if prior:
            require(prior[0]==request_digest,'EFFECT_ID_CONFLICT');return {'duplicate':True,'effect':a['effect']}
        require(not g['revoked'] and g['credential_binding_active'] and g['consumed']<g['max_effects'],'CREDENTIAL_BINDING_CLOSED')
        require(self.now()<g['expires_at'],'CREDENTIAL_EXPIRED')
        require(a['verifier_status'] is not None,'VERIFIER_UNREACHABLE')
        status=self.signed_body(a['verifier_status'],self.verifier,'destination-status')
        exact(status,'at expires_at command request_digest generation active')
        require(status['command']==identity and status['request_digest']==request_digest and status['generation']==fence,'VERIFIER_BINDING')
        require(status['active'] is True and status['at']==self.now()<integer(status['expires_at']),'VERIFIER_NOT_CURRENT')
        view=self.population(c,'destination-grants').get(g['principal'])
        require(view is not None,'SOFT_PIN_DESTINATION_UNREAD')
        before=set(g['grants']);after=set(view['grants'])
        if after-before: raise Denied('SOFT_PIN_SCOPE_WIDENED')
        require(before==after,'SOFT_PIN_SCOPE_CHANGED')
        changes=[]
        for kind in ('credential','dependency'):
            field=kind+'_version'
            if view[field]!=g[field]:
                require(g['modes'].get(kind,'hard')=='soft','HARD_PIN_CHANGED')
                changes.append(kind)
        resolution={'authoritative_side':'destination','principal':g['principal'],'before_digest':digest(g['grants']),'after_digest':digest(view['grants']),'predicate':'exact-effective-grant-set/1','result':'equivalent','changed_classes':changes,'expected_versions':{k:g[k] for k in ('credential_version','dependency_version')},'observed_versions':{k:view[k] for k in ('credential_version','dependency_version')},'issuer_context_digest':digest(a['issuer_claims'])}
        self.put(c,'resolution-input',identity,resolution,new=True)
        g['consumed']+=1
        if g['consumed']==g['max_effects']:g['credential_binding_active']=False
        self.put(c,'grant',a['grant'],g)
        c.execute('INSERT INTO effects VALUES(?,?,?,?,?)',(a['effect'],a['grant'],request_digest,canonical(a['payload']),canonical(resolution)))
        return {'duplicate':False,'effect':a['effect'],'resolution_input':resolution,'credential_binding_active':g['credential_binding_active']}
