"""Integrated optional assurance reference with one local SQLite effect boundary.

All effects are synthetic SQLite rows; there is no shell, network or arbitrary
callback adapter. HMAC principals are synthetic trust fixtures. The host, initial
role/key configuration, observation adapter and clock are trusted. Not a selected
executor replacement, production identity system or independent custody service.
"""
from contextlib import closing, contextmanager
import hashlib
import hmac
import json
import math
from pathlib import Path
import sqlite3
from reference_profiles.bounded_json import snapshot

VERSION = 'integrated-local-assurance/1'
ZERO = '0' * 64
AUDIT_DEFAULTS = {'events': 4096, 'anonymous': 64, 'per_principal': 1024,
                  'sources': 256, 'event_bytes': 8192, 'database_pages': 4096}


def audit_configuration(value):
    if type(value) is not dict or set(value) != set(AUDIT_DEFAULTS):
        raise ValueError('explicit audit budget fields required')
    if any(type(v) is not int or not 0 < v <= 9007199254740991 for v in value.values()):
        raise ValueError('positive integer audit limits required')
    if value['database_pages'] > 4096 or value['event_bytes'] > 8192 or value['sources'] > 256 or value['events'] > 4096:
        raise ValueError('audit configuration cannot exceed reference storage ceiling')
    if value['database_pages'] < 16:
        raise ValueError('audit database requires at least 16 pages')
    return dict(value)



def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def require(condition, code):
    if not condition:
        raise Denied(code)


class Denied(ValueError):
    pass


def exact(value, fields):
    require(type(value) is dict and set(value) == set(fields.split()), 'INVALID_FIELDS')


def label(value):
    require(type(value) is str and 0 < len(value) <= 200 and value == value.strip(), 'INVALID_LABEL')
    return value


def integer(value, minimum=0):
    require(type(value) is int and value >= minimum, 'INVALID_INTEGER')
    return value


def number(value):
    require(type(value) in (int, float) and math.isfinite(value), 'INVALID_TIME')
    return value


def sha(value):
    require(type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value), 'INVALID_DIGEST')
    return value


def names(value):
    require(type(value) is list and 0 < len(value) <= 64 and len(value) == len(set(map(str, value))), 'INVALID_SET')
    for item in value: label(item)
    return set(value)


def sign_request(key, *, stream, actor, key_version, nonce, expires_at, operation, arguments):
    """Synthetic client fixture. Signing is not institutional adoption."""
    body = dict(contract=VERSION, stream=stream, actor=actor, key_version=key_version,
                nonce=nonce, expires_at=expires_at, operation=operation, arguments=arguments)
    return {'body': body, 'mac': hmac.new(key, canonical(body).encode(), hashlib.sha256).hexdigest()}


ROLES = {
    'environment': 'operator', 'run': 'operator', 'grant': 'operator',
    'revoke': 'operator', 'rotate': 'operator', 'reviewer': 'operator',
    'ingest': 'steward', 'declassify': 'steward',
    'delegate': 'agent', 'queue': 'agent', 'execute': 'agent', 'observe': 'agent',
    'progress': 'agent', 'review': 'reviewer', 'challenge': 'reviewer',
    'resolve_challenge': 'reviewer', 'checkpoint': 'custodian',
    'stop': 'incident', 'restart_review': 'reviewer', 'restart': 'operator',
    'oracle': 'evaluator', 'select_oracle': 'operator', 'propose_change': 'builder', 'evaluate_change': 'evaluator',
    'admit_change': 'reviewer', 'activate_change': 'operator',
    'obligation': 'operator', 'recourse': 'adjudicator', 'adjudicate': 'adjudicator',
    'appeal': 'operator', 'decide_appeal': 'adjudicator',
}


class AssuranceRuntime:
    roles = ROLES

    def __init__(self, path, *, keys, clock, observe_environment):
        self.path = Path(path).resolve()
        self.keys = dict(keys)  # (principal, version) -> fixture HMAC verification key
        self.clock = clock
        self.observe_environment = observe_environment

    @classmethod
    def create(cls, path, *, stream, principals, keys, clock, observe_environment, audit_limits=None):
        limits = audit_configuration(AUDIT_DEFAULTS if audit_limits is None else audit_limits)
        label(stream)
        require(type(principals) is dict and principals, 'PRINCIPALS_REQUIRED')
        for actor, spec in principals.items():
            label(actor); exact(spec, 'version roles'); integer(spec['version'], 1); names(spec['roles'])
            key = keys.get((actor, spec['version']))
            require(type(key) is bytes and len(key) >= 32, 'FIXTURE_KEY_REQUIRED')
        runtime = cls(path, keys=keys, clock=clock, observe_environment=observe_environment)
        with runtime.path.open('xb'): pass
        with closing(sqlite3.connect(runtime.path)) as conn:
            conn.executescript('''
                CREATE TABLE audit_counters (source TEXT PRIMARY KEY,used INTEGER NOT NULL,suppressed INTEGER NOT NULL);
                CREATE TABLE objects (kind TEXT NOT NULL,id TEXT NOT NULL,body TEXT NOT NULL,PRIMARY KEY(kind,id));
                CREATE TABLE nonces (actor TEXT,version INTEGER,nonce TEXT,PRIMARY KEY(actor,version,nonce));
                CREATE TABLE events (seq INTEGER PRIMARY KEY,body TEXT NOT NULL,previous TEXT NOT NULL,head TEXT NOT NULL);
                CREATE TABLE effects (id TEXT PRIMARY KEY,run TEXT NOT NULL,request TEXT NOT NULL,payload TEXT NOT NULL,evidence TEXT NOT NULL);
            ''')
            runtime.put(conn,'meta','audit-limits',limits)
            runtime.put(conn,'meta','stream',{'id':stream})
            runtime.put(conn,'meta','harness',{'instruction_digest':ZERO,'routes':{}})
            for actor, spec in principals.items():
                runtime.put(conn,'principal',actor,dict(spec,enabled=True,key_digest=hashlib.sha256(keys[(actor,spec['version'])]).hexdigest()))
            conn.commit()
        return runtime

    @contextmanager
    def connection(self):
        # Fail closed if storage is lost; never bootstrap during admission.
        with closing(sqlite3.connect(self.path.as_uri()+'?mode=rw',uri=True,isolation_level=None,timeout=5)) as conn:
            conn.row_factory=sqlite3.Row
            conn.execute('PRAGMA synchronous=FULL')
            yield conn

    @contextmanager
    def audit_connection(self):
        # The generic connection/event helpers are also reused by the separate
        # protected destination, which owns a different admission contract.
        with self.connection() as conn:
            # Fixed-size rollback journals avoid unbounded WAL retention by readers.
            if conn.execute('PRAGMA journal_mode').fetchone()[0] != 'delete':
                raise sqlite3.OperationalError('audit requires DELETE journal mode')
            if conn.execute('PRAGMA page_size').fetchone()[0] != 4096:
                raise sqlite3.OperationalError('audit requires 4096-byte pages')
            limits = audit_configuration(self.get(conn, 'meta', 'audit-limits'))
            actual_limit = conn.execute('PRAGMA max_page_count=' + str(limits['database_pages'])).fetchone()[0]
            if actual_limit > limits['database_pages']:
                raise sqlite3.OperationalError('audit database already exceeds page budget')
            yield conn

    @staticmethod
    def get(conn, kind, identity):
        row=conn.execute('SELECT body FROM objects WHERE kind=? AND id=?',(kind,identity)).fetchone()
        require(row is not None,'MISSING_'+kind.upper())
        return json.loads(row[0])

    @staticmethod
    def put(conn, kind, identity, body, *, new=False):
        label(identity)
        if new:
            require(conn.execute('SELECT 1 FROM objects WHERE kind=? AND id=?',(kind,identity)).fetchone() is None,'DUPLICATE_ID')
        conn.execute('INSERT INTO objects VALUES (?,?,?) ON CONFLICT(kind,id) DO UPDATE SET body=excluded.body',(kind,identity,canonical(body)))

    @staticmethod
    def population(conn, kind):
        return {r[0]:json.loads(r[1]) for r in conn.execute('SELECT id,body FROM objects WHERE kind=?',(kind,))}

    def now(self): return number(self.clock())

    @staticmethod
    def head(conn):
        row=conn.execute('SELECT seq,head FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        return (row[0],row[1]) if row else (0,ZERO)

    def event(self, conn, body):
        seq, previous=self.head(conn)
        head=digest({'seq':seq+1,'body':body,'previous':previous})
        conn.execute('INSERT INTO events VALUES (?,?,?,?)',(seq+1,canonical(body),previous,head))

    def audit_event(self, conn, body):
        limits = self.get(conn, 'meta', 'audit-limits')
        require(self.head(conn)[0] < limits['events'], 'AUDIT_CAPACITY')
        require(len(canonical(body).encode()) <= limits['event_bytes'], 'AUDIT_CAPACITY')
        self.event(conn, body)

    def audit_source(self, conn, source):
        limits = self.get(conn, 'meta', 'audit-limits')
        row = conn.execute('SELECT used,suppressed FROM audit_counters WHERE source=?', (source,)).fetchone()
        if row is None:
            require(conn.execute('SELECT count(*) FROM audit_counters').fetchone()[0] < limits['sources'], 'AUDIT_CAPACITY')
            conn.execute('INSERT INTO audit_counters VALUES (?,0,0)', (source,))
            return 0
        return row[0]

    @staticmethod
    def suppress(conn, source):
        conn.execute('UPDATE audit_counters SET suppressed=min(suppressed+1,9007199254740991) WHERE source=?', (source,))

    def audit_status(self):
        """Trusted-host inspection; suppression counts are bounded and saturating."""
        with self.audit_connection() as conn:
            return {'limits': self.get(conn, 'meta', 'audit-limits'),
                    'sources': [dict(row) for row in conn.execute('SELECT * FROM audit_counters ORDER BY source')],
                    'retention': 'append-only lifetime budget; no automatic pruning',
                    'authorizing': False}

    def apply(self, request):
        try:
            request = snapshot(request)
        except (ValueError, TypeError, OverflowError):
            return {'status':'denied','reason':'INVALID_REQUEST','authorizing':False}
        try:
            return self._apply(request)
        except (sqlite3.Error, Denied, ValueError, TypeError, OverflowError):
            # Closing the transaction rolls back effects and nonce consumption.
            return {'status': 'denied', 'reason': 'AUDIT_OR_INPUT_UNAVAILABLE', 'authorizing': False, 'audit_recorded': False}

    def _apply(self, request):
        """Authenticate exact operation; record durable refusal or one transaction.

        Expected denials roll back operation writes while retaining the consumed
        nonce and minimal refusal record. Crashes roll back all uncommitted work.
        """
        # Detach all caller-owned input before checking or using it.
        try:
            encoded=canonical(request)
            if len(encoded.encode())>1024*1024: raise ValueError('request too large')
            request=json.loads(encoded)
        except (TypeError,ValueError): return {'status':'denied','reason':'INVALID_REQUEST','authorizing':False}
        with self.audit_connection() as conn:
            conn.execute('BEGIN IMMEDIATE')
            limits = self.get(conn, 'meta', 'audit-limits')
            # Reserve the single anonymous bucket before any principal buckets.
            self.audit_source(conn, 'anonymous')
            if self.head(conn)[0] >= limits['events']:
                self.suppress(conn, 'anonymous'); conn.commit()
                return {'status':'denied','reason':'AUDIT_CAPACITY','authorizing':False,'audit_recorded':False}
            source = 'anonymous'
            actor='unverified'; operation='unknown'; metadata={}; authenticated=False; key_version=None; refs={}
            try:
                exact(request,'body mac'); body=request['body']
                exact(body,'contract stream actor key_version nonce expires_at operation arguments')
                actor=label(body['actor']); operation=label(body['operation'])
                require(body['contract']==VERSION and body['stream']==self.get(conn,'meta','stream')['id'],'AUDIENCE_MISMATCH')
                principal=self.get(conn,'principal',actor)
                require(principal['enabled'] and body['key_version']==principal['version'] and type(body['key_version']) is int,'KEY_RETIRED')
                key=self.keys.get((actor,body['key_version']))
                require(type(key) is bytes and hashlib.sha256(key).hexdigest()==principal['key_digest'],'KEY_UNAVAILABLE')
                require(type(request['mac']) is str and hmac.compare_digest(request['mac'],hmac.new(key,canonical(body).encode(),hashlib.sha256).hexdigest()),'BAD_SIGNATURE')
                authenticated=True; key_version=body['key_version']
                source = 'principal:' + actor
                used = self.audit_source(conn, source)
                if used >= limits['per_principal']:
                    self.suppress(conn, source); conn.commit()
                    return {'status':'denied','reason':'AUDIT_CAPACITY','authorizing':False,'audit_recorded':False}
                require(self.now()<number(body['expires_at']),'REQUEST_EXPIRED')
                nonce=label(body['nonce'])
                require(conn.execute('SELECT 1 FROM nonces WHERE actor=? AND version=? AND nonce=?',(actor,principal['version'],nonce)).fetchone() is None,'REPLAYED_REQUEST')
                conn.execute('INSERT INTO nonces VALUES (?,?,?)',(actor,principal['version'],nonce))
                require(operation in self.roles and self.roles[operation] in principal['roles'],'ROLE_NOT_PERMITTED')
                args=body['arguments']; require(type(args) is dict,'INVALID_ARGUMENTS')
                refs={k:args[k] for k in ('id','run','grant','proposal','change','oracle','incident','packet','principal','appeal') if type(args.get(k)) is str}
                # Retain the exact configured grant chain even on effect-time refusal.
                if operation=='execute' and type(args.get('proposal')) is str:
                    proposal=self.get(conn,'proposal',args['proposal'])
                    identity=proposal['proposal']['grant']; snapshots=[]; seen=set()
                    while identity and identity not in seen:
                        seen.add(identity); g=self.get(conn,'grant',identity)
                        snapshots.append({'id':identity,'revision':g['revision'],'status':g['status']})
                        identity=g['parent']
                    metadata={'grant_chain':snapshots}
                if type(args.get('grant')) is str:
                    row=conn.execute("SELECT body FROM objects WHERE kind='grant' AND id=?",(args['grant'],)).fetchone()
                    if row:
                        grant=json.loads(row[0]); metadata={'grant':args['grant'],'grant_revision':grant['revision']}
                conn.execute('SAVEPOINT operation')
                try:
                    output=getattr(self,'op_'+operation)(conn,actor,args)
                    require(self.now()<body['expires_at'],'REQUEST_EXPIRED')
                except Denied:
                    conn.execute('ROLLBACK TO operation'); conn.execute('RELEASE operation'); raise
                except (TypeError, KeyError, OverflowError) as exc:
                    conn.execute('ROLLBACK TO operation'); conn.execute('RELEASE operation')
                    raise Denied('INVALID_ARGUMENTS') from exc
                conn.execute('RELEASE operation')
                result={'status':'accepted','result':output,'authorizing':False}
            except Denied as exc:
                result={'status':'denied','reason':str(exc),'authorizing':False}
            if not authenticated and self.audit_source(conn, 'anonymous') >= limits['anonymous']:
                self.suppress(conn, 'anonymous'); conn.commit()
                return dict(result, audit_recorded=False, audit_suppressed=True)
            # No payload, keys, MACs, rationale or arbitrary exception bodies in log.
            self.audit_event(conn,dict(actor=actor,authenticated=authenticated,key_version=key_version,object_refs=refs,operation=operation,request_digest=digest(request),result_digest=digest(result),
                                 status=result['status'],reason=result.get('reason'),at=self.now(),**metadata))
            conn.execute('UPDATE audit_counters SET used=used+1 WHERE source=?', (source,))
            conn.commit()
            return result

    def op_environment(self,c,actor,a):
        exact(a,'id manifest expires_at max_event_lag max_checkpoint_age')
        label(a['id']); require(self.now()<number(a['expires_at']),'LEASE_EXPIRED')
        integer(a['max_event_lag'],2); require(number(a['max_checkpoint_age'])>0,'INVALID_CHECKPOINT_AGE')
        m=a['manifest']; exact(m,'adapter network subprocess shared_cache sinks')
        require(m['adapter']=='sqlite-local/1' and m['network'] is False and m['subprocess'] is False and m['shared_cache'] is False,'UNSUPPORTED_SURFACE')
        require(type(m['sinks']) is dict and m['sinks'],'SINKS_REQUIRED')
        for sink,labels in m['sinks'].items(): label(sink); names(labels)
        try: observed=self.observe_environment()
        except Exception: raise Denied('ENVIRONMENT_UNAVAILABLE')
        require(observed==m,'ENVIRONMENT_MISMATCH')
        self.put(c,'environment',a['id'],dict(a,manifest_digest=digest(m),owner=actor))
        # Bootstrap routes from immutable registered sinks; later changes use admission.
        harness=self.get(c,'meta','harness')
        if not harness['routes']:
            harness['routes']={k:k for k in m['sinks']}; self.put(c,'meta','harness',harness)
        return {'manifest_digest':digest(m)}

    def environment(self,c,identity):
        env=self.get(c,'environment',identity)
        try: observed=self.observe_environment()
        except Exception: raise Denied('ENVIRONMENT_UNAVAILABLE')
        require(observed==env['manifest'],'ENVIRONMENT_MISMATCH')
        require(self.now()<env['expires_at'],'LEASE_EXPIRED')
        return env

    def op_run(self,c,actor,a):
        exact(a,'id agent environment cohort parent purpose max_steps stall_seconds provenance')
        for f in ('id','agent','environment','cohort','purpose'): label(a[f])
        exact(a['provenance'],'model_ref configuration_digest assurance')
        label(a['provenance']['model_ref']); sha(a['provenance']['configuration_digest'])
        require(a['provenance']['assurance']=='declared','MODEL_ATTESTATION_NOT_ESTABLISHED')
        cohorts=self.population(c,'cohort')
        if a['cohort'] in cohorts: require(cohorts[a['cohort']]['state']=='active','COHORT_STOPPED')
        else: self.put(c,'cohort',a['cohort'],{'state':'active','generation':0},new=True)
        principal=self.get(c,'principal',a['agent']); require(principal['enabled'] and 'agent' in principal['roles'],'AGENT_UNAVAILABLE')
        self.environment(c,a['environment']); integer(a['max_steps'],1); require(number(a['stall_seconds'])>0,'INVALID_STALL_LIMIT')
        if a['parent'] is not None:
            parent=self.get(c,'run',a['parent']); require(parent['state']=='active' and parent['cohort']==a['cohort'],'PARENT_RUN_UNAVAILABLE')
        self.put(c,'run',a['id'],dict(a,owner=actor,state='active',generation=1,steps=0,last_progress=self.now()),new=True)
        return {'run':a['id']}

    def active_run(self,c,identity,actor=None):
        run=self.get(c,'run',identity)
        require(run['state']=='active','RUN_STOPPED')
        principal=self.get(c,'principal',run['agent']); require(principal['enabled'] and 'agent' in principal['roles'],'AGENT_UNAVAILABLE')
        if actor is not None: require(run['agent']==actor,'INSTANCE_MISMATCH')
        require(run['steps']<run['max_steps'],'STEP_BUDGET_EXHAUSTED')
        require(self.now()<run['last_progress']+run['stall_seconds'],'RUN_STALLED')
        self.environment(c,run['environment'])
        return run

    def op_progress(self,c,actor,a):
        exact(a,'run'); run=self.active_run(c,a['run'],actor)
        run.update(steps=run['steps']+1,last_progress=self.now()); self.put(c,'run',a['run'],run)
        return {'steps':run['steps']}

    def op_ingest(self,c,actor,a):
        exact(a,'id content labels parents expires_at')
        require(type(a['content']) is str and len(a['content'].encode())<=65536,'BOUNDED_TEXT_REQUIRED'); names(a['labels'])
        require(type(a['parents']) is list and len(a['parents'])<=8 and len(a['parents'])==len(set(a['parents'])),'INVALID_PARENTS')
        require(self.now()<number(a['expires_at']),'CONTENT_EXPIRED')
        for parent in a['parents']:
            item=self.item(c,parent)
            require(set(a['labels'])>=set(item['labels']) and a['expires_at']<=item['expires_at'],'PROVENANCE_WEAKENED')
        self.put(c,'item',a['id'],dict(a,source=actor,content_digest=hashlib.sha256(a['content'].encode()).hexdigest()),new=True)
        return {'item':a['id'],'content_digest':hashlib.sha256(a['content'].encode()).hexdigest()}

    def item(self,c,identity,seen=()):
        require(identity not in seen and len(seen)<32,'PROVENANCE_CYCLE_OR_DEPTH')
        item=self.get(c,'item',identity); require(self.now()<item['expires_at'],'CONTENT_EXPIRED')
        for parent in item['parents']: self.item(c,parent,(*seen,identity))
        return item

    def op_declassify(self,c,actor,a):
        exact(a,'id item sink payload_digest expires_at')
        item=self.item(c,a['item']); label(a['sink'])
        require(sha(a['payload_digest'])==item['content_digest'],'PAYLOAD_MISMATCH')
        require(self.now()<number(a['expires_at'])<=item['expires_at'],'DECLASSIFICATION_EXPIRED')
        self.put(c,'declassification',a['id'],dict(a,steward=actor),new=True)
        return {'declassification':a['id']}

    def op_grant(self,c,actor,a):
        exact(a,'id run sinks labels budget expires_at depth corrects')
        run=self.active_run(c,a['run']); names(a['sinks']); names(a['labels']); integer(a['budget'],1); require(integer(a['depth'])<=16,'DELEGATION_DEPTH_TOO_LARGE')
        require(self.now()<number(a['expires_at']),'GRANT_EXPIRED')
        env=self.environment(c,run['environment']); require(set(a['sinks'])<=set(env['manifest']['sinks']),'UNKNOWN_SINK')
        if a['corrects'] is not None:
            self.correction_permitted(c,a['corrects'])
        self.put(c,'grant',a['id'],dict(a,actor=run['agent'],purpose=run['purpose'],generation=run['generation'],parent=None,used=0,revision=1,status='active',issuer=actor),new=True)
        return {'grant':a['id'],'revision':1}

    def chain(self,c,identity,seen=()):
        require(identity not in seen,'GRANT_CYCLE')
        g=self.get(c,'grant',identity); run=self.active_run(c,g['run'])
        require(g['status']=='active','GRANT_REVOKED'); require(self.now()<g['expires_at'],'GRANT_EXPIRED')
        require(g['generation']==run['generation'],'GRANT_GENERATION_STALE')
        require(g['used']<g['budget'],'GRANT_BUDGET_EXHAUSTED')
        if g['corrects'] is not None: self.correction_permitted(c,g['corrects'])
        return [(identity,g)]+(self.chain(c,g['parent'],(*seen,identity)) if g['parent'] else [])

    def op_delegate(self,c,actor,a):
        exact(a,'id parent run sinks labels budget expires_at depth')
        chain=self.chain(c,a['parent']); parent=chain[0][1]
        require(parent['actor']==actor,'GRANT_HOLDER_MISMATCH')
        child=self.active_run(c,a['run']); parent_run=self.get(c,'run',parent['run'])
        require(child['parent']==parent['run'] and child['cohort']==parent_run['cohort'] and child['purpose']==parent['purpose'],'DELEGATION_SCOPE_MISMATCH')
        require(names(a['sinks'])<=set(parent['sinks']) and names(a['labels'])<=set(parent['labels']),'DELEGATION_EXPANDED')
        require(0<integer(a['budget'])<=parent['budget'] and 0<=integer(a['depth'])<parent['depth'],'DELEGATION_EXPANDED')
        require(self.now()<number(a['expires_at'])<=parent['expires_at'],'DELEGATION_EXPIRED')
        self.put(c,'grant',a['id'],dict(a,actor=child['agent'],purpose=parent['purpose'],generation=child['generation'],used=0,revision=1,status='active',issuer=actor,corrects=None),new=True)
        return {'grant':a['id']}

    def op_revoke(self,c,actor,a):
        exact(a,'grant'); g=self.get(c,'grant',a['grant']); g.update(status='revoked',revision=g['revision']+1)
        self.put(c,'grant',a['grant'],g); return {'grant_revision':g['revision']}

    def op_rotate(self,c,actor,a):
        exact(a,'principal version enabled'); p=self.get(c,'principal',a['principal'])
        require(type(a['enabled']) is bool and integer(a['version'],1)>p['version'],'KEY_VERSION_MUST_ADVANCE')
        key=self.keys.get((a['principal'],a['version'])); require(type(key) is bytes and len(key)>=32,'KEY_UNAVAILABLE')
        p.update(version=a['version'],enabled=a['enabled'],key_digest=hashlib.sha256(key).hexdigest())
        self.put(c,'principal',a['principal'],p); return {'version':a['version']}

    def op_reviewer(self,c,actor,a):
        exact(a,'id available capacity expires_at'); p=self.get(c,'principal',a['id'])
        require('reviewer' in p['roles'] and p['enabled'],'REVIEWER_UNAVAILABLE')
        require(type(a['available']) is bool,'INVALID_AVAILABILITY'); integer(a['capacity'],1)
        require(self.now()<number(a['expires_at']),'REVIEWER_EXPIRED')
        self.put(c,'reviewer',a['id'],dict(a,key_version=p['version'])); return {'reviewer':a['id']}

    def reviewer(self,c,identity):
        r=self.get(c,'reviewer',identity); p=self.get(c,'principal',identity)
        require(r['available'] and p['enabled'] and 'reviewer' in p['roles'] and r['key_version']==p['version'] and self.now()<r['expires_at'],'REVIEWER_UNAVAILABLE')
        return r

    def proposal_binding(self,c,actor,a):
        exact(a,'effect run grant item route declassification harness_digest')
        for f in ('effect','run','grant','item','route'): label(a[f])
        run=self.active_run(c,a['run'],actor); chain=self.chain(c,a['grant']); grant=chain[0][1]
        require(grant['actor']==actor and grant['run']==a['run'],'GRANT_HOLDER_MISMATCH')
        harness=self.get(c,'meta','harness'); require(sha(a['harness_digest'])==digest(harness),'HARNESS_CHANGED')
        require(a['route'] in harness['routes'],'UNKNOWN_ROUTE'); sink=harness['routes'][a['route']]
        env=self.environment(c,run['environment']); require(sink in env['manifest']['sinks'],'UNKNOWN_SINK')
        item=self.item(c,a['item'])
        for _,g in chain:
            require(sink in g['sinks'] and set(item['labels'])<=set(g['labels']),'ACTION_OUTSIDE_GRANT')
        if not set(item['labels'])<=set(env['manifest']['sinks'][sink]):
            d=self.get(c,'declassification',a['declassification'])
            require(d['item']==a['item'] and d['sink']==sink and d['payload_digest']==item['content_digest'] and self.now()<d['expires_at'],'DECLASSIFICATION_MISMATCH')
        elif a['declassification'] is not None:
            # Any supplied declassification reference must also be valid and exact.
            d=self.get(c,'declassification',a['declassification'])
            require(d['item']==a['item'] and d['sink']==sink and d['payload_digest']==item['content_digest'] and self.now()<d['expires_at'],'DECLASSIFICATION_MISMATCH')
        return run,chain,item,sink,env

    def extend_binding(self,c,proposal,binding):
        return binding

    def op_queue(self,c,actor,a):
        exact(a,'id proposal reviewer expires_at')
        run,chain,item,sink,env=self.proposal_binding(c,actor,a['proposal'])
        reviewer=self.reviewer(c,a['reviewer']); require(a['reviewer']!=actor,'SELF_APPROVAL_FORBIDDEN')
        require(self.now()<number(a['expires_at'])<=reviewer['expires_at'],'REVIEW_DEADLINE_INVALID')
        pending=sum(p['reviewer']==a['reviewer'] and p['state'] in ('pending','approved') and self.now()<p['expires_at'] for p in self.population(c,'proposal').values())
        require(pending<reviewer['capacity'],'REVIEW_CAPACITY_EXHAUSTED')
        binding=dict(a['proposal'],generation=run['generation'],payload_digest=item['content_digest'],sink=sink,environment_digest=digest({k:env[k] for k in ('manifest_digest','max_event_lag','max_checkpoint_age')}))
        binding=self.extend_binding(c,a['proposal'],binding)
        self.put(c,'proposal',a['id'],dict(a,actor=actor,binding=binding,binding_digest=digest(binding),state='pending',queued_at=self.now(),reviewed_at=None,reviewer_version=reviewer['key_version']),new=True)
        return {'proposal':a['id'],'binding_digest':digest(binding)}

    def op_challenge(self,c,actor,a):
        exact(a,'id proposal reason_digest'); p=self.get(c,'proposal',a['proposal'])
        require(p['state'] in ('pending','approved') and self.now()<p['expires_at'],'PROPOSAL_UNAVAILABLE')
        self.put(c,'challenge',a['id'],dict(a,challenger=actor,state='open',reason_digest=sha(a['reason_digest'])),new=True)
        return {'challenge':a['id']}

    def op_resolve_challenge(self,c,actor,a):
        exact(a,'challenge disposition reason_digest'); ch=self.get(c,'challenge',a['challenge']); p=self.get(c,'proposal',ch['proposal'])
        require(p['reviewer']==actor and ch['state']=='open','CHALLENGE_REVIEWER_MISMATCH')
        self.reviewer(c,actor); require(a['disposition'] in ('accept','override'),'INVALID_DISPOSITION'); sha(a['reason_digest'])
        ch.update(state=a['disposition'],decision_by=actor,decision_at=self.now(),decision_reason=a['reason_digest']); self.put(c,'challenge',a['challenge'],ch)
        if a['disposition']=='accept': p['state']='rejected'; self.put(c,'proposal',ch['proposal'],p)
        return {'state':ch['state']}

    def op_review(self,c,actor,a):
        exact(a,'proposal binding_digest disposition'); p=self.get(c,'proposal',a['proposal'])
        self.reviewer(c,actor); require(actor==p['reviewer'] and actor!=p['actor'],'REVIEWER_MISMATCH')
        require(p['state']=='pending' and self.now()<p['expires_at'],'PROPOSAL_UNAVAILABLE')
        require(a['binding_digest']==p['binding_digest'],'PROPOSAL_CHANGED')
        require(a['disposition'] in ('approve','reject'),'INVALID_DISPOSITION')
        require(not any(ch['proposal']==a['proposal'] and ch['state']=='open' for ch in self.population(c,'challenge').values()),'UNRESOLVED_CHALLENGE')
        p.update(state='approved' if a['disposition']=='approve' else 'rejected',reviewed_at=self.now())
        self.put(c,'proposal',a['proposal'],p); return {'state':p['state'],'review_latency':p['reviewed_at']-p['queued_at']}

    def op_checkpoint(self,c,actor,a):
        exact(a,'stream count head observed_at')
        require(a['stream']==self.get(c,'meta','stream')['id'],'AUDIENCE_MISMATCH'); integer(a['count']); sha(a['head'])
        observed=number(a['observed_at']); require(observed<=self.now(),'FUTURE_CHECKPOINT')
        row=c.execute('SELECT head FROM events WHERE seq=?',(a['count'],)).fetchone()
        require((a['count']==0 and a['head']==ZERO) or (row is not None and row[0]==a['head']),'CHECKPOINT_MISMATCH')
        old=self.population(c,'checkpoint').get('current')
        if old: require(a['count']>=old['count'] and observed>=old['observed_at'],'CHECKPOINT_ROLLBACK')
        self.put(c,'checkpoint','current',dict(a,custodian=actor,key_version=self.get(c,'principal',actor)['version']))
        return {'count':a['count']}

    def custody(self,c,env):
        cp=self.get(c,'checkpoint','current'); principal=self.get(c,'principal',cp['custodian'])
        require(principal['enabled'] and cp['key_version']==principal['version'],'CUSTODIAN_KEY_RETIRED')
        require(self.now()-cp['observed_at']<=env['max_checkpoint_age'],'CUSTODY_TIME_LAG')
        require(self.head(c)[0]-cp['count']+1<=env['max_event_lag'],'CUSTODY_EVENT_LAG')

    def op_execute(self,c,actor,a):
        exact(a,'proposal'); p=self.get(c,'proposal',a['proposal'])
        require(p['actor']==actor,'INSTANCE_MISMATCH')
        prior=c.execute('SELECT request FROM effects WHERE id=?',(p['proposal']['effect'],)).fetchone()
        if prior:
            require(prior[0]==p['binding_digest'],'EFFECT_ID_CONFLICT')
            return {'effect':p['proposal']['effect'],'observed_state':'applied','duplicate':True}
        require(p['state']=='approved' and self.now()<p['expires_at'],'APPROVAL_UNAVAILABLE')
        reviewer=self.reviewer(c,p['reviewer']); require(reviewer['key_version']==p['reviewer_version'],'REVIEWER_KEY_CHANGED')
        require(not any(ch['proposal']==a['proposal'] and ch['state']=='open' for ch in self.population(c,'challenge').values()),'UNRESOLVED_CHALLENGE')
        run,chain,item,sink,env=self.proposal_binding(c,actor,p['proposal'])
        binding=dict(p['proposal'],generation=run['generation'],payload_digest=item['content_digest'],sink=sink,environment_digest=digest({k:env[k] for k in ('manifest_digest','max_event_lag','max_checkpoint_age')}))
        binding=self.extend_binding(c,p['proposal'],binding)
        require(digest(binding)==p['binding_digest'],'PROPOSAL_CHANGED')
        self.custody(c,env)
        # A single SQLite transaction orders current authority, shared ancestor
        # budget, review consumption, audit intent and this synthetic effect.
        # Recheck all local deadlines after the final environment observation.
        current=self.now()
        require(current<p['expires_at'] and current<reviewer['expires_at'],'APPROVAL_EXPIRED_AT_COMMIT')
        require(current<env['expires_at'] and current<run['last_progress']+run['stall_seconds'],'BOUNDARY_EXPIRED_AT_COMMIT')
        for _,g in chain:
            ancestor_run=self.get(c,'run',g['run'])
            ancestor_env=self.get(c,'environment',ancestor_run['environment'])
            require(current<g['expires_at'] and current<ancestor_env['expires_at'] and current<ancestor_run['last_progress']+ancestor_run['stall_seconds'],'GRANT_EXPIRED_AT_COMMIT')
        if p['proposal']['declassification'] is not None:
            require(current<self.get(c,'declassification',p['proposal']['declassification'])['expires_at'],'DECLASSIFICATION_EXPIRED')
        evidence={'binding':binding,'corrections':{g['corrects']:self.correction_permitted(c,g['corrects']) for _,g in chain if g['corrects'] is not None},'grants':[{'id':i,'revision':g['revision']} for i,g in chain],
                  'reviewer':p['reviewer'],'reviewed_at':p['reviewed_at'],'committed_at':self.now()}
        c.execute('INSERT INTO effects VALUES (?,?,?,?,?)',(p['proposal']['effect'],p['proposal']['run'],p['binding_digest'],item['content'],canonical(evidence)))
        for identity,g in chain:
            g['used']+=1; self.put(c,'grant',identity,g)
        p['state']='consumed'; self.put(c,'proposal',a['proposal'],p)
        run.update(steps=run['steps']+1,last_progress=self.now()); self.put(c,'run',p['proposal']['run'],run)
        return {'effect':p['proposal']['effect'],'observed_state':'applied','duplicate':False}

    def op_observe(self,c,actor,a):
        exact(a,'effect run'); run=self.get(c,'run',a['run']); require(run['agent']==actor,'INSTANCE_MISMATCH')
        row=c.execute('SELECT run,evidence FROM effects WHERE id=?',(a['effect'],)).fetchone()
        require(row is None or row['run']==a['run'],'EFFECT_SCOPE_MISMATCH')
        return {'effect':a['effect'],'observed_state':'applied' if row else 'absent','authorizes_retry':False}

    def op_stop(self,c,actor,a):
        exact(a,'run incident_digest detected_at'); target=self.get(c,'run',a['run']); sha(a['incident_digest'])
        detected=number(a['detected_at']); require(detected<=self.now(),'FUTURE_INCIDENT')
        cohort=self.get(c,'cohort',target['cohort']); cohort.update(state='stopped',generation=cohort['generation']+1)
        self.put(c,'cohort',target['cohort'],cohort)
        stopped=[]
        for identity,run in self.population(c,'run').items():
            if run['cohort']==target['cohort']:
                run.update(state='stopped',generation=run['generation']+1); self.put(c,'run',identity,run); stopped.append(identity)
        for identity,g in self.population(c,'grant').items():
            if g['run'] in stopped:
                g.update(status='revoked',revision=g['revision']+1); self.put(c,'grant',identity,g)
        for identity,p in self.population(c,'proposal').items():
            if p['proposal']['run'] in stopped and p['state'] in ('pending','approved'):
                p['state']='cancelled'; self.put(c,'proposal',identity,p)
        incident=dict(a,cohort=target['cohort'],cohort_generation=cohort['generation'],owner=actor,stopped=sorted(stopped),stopped_at=self.now(),state='quiescent-local',effect_count=c.execute('SELECT count(*) FROM effects').fetchone()[0])
        identity=digest(incident); self.put(c,'incident',identity,incident,new=True)
        return {'incident':identity,'runs':sorted(stopped),'state':'quiescent-local','stop_latency':incident['stopped_at']-detected}

    def op_restart_review(self,c,actor,a):
        exact(a,'incident remediation_digest expires_at'); incident=self.get(c,'incident',a['incident']); self.reviewer(c,actor)
        require(actor!=incident['owner'],'RESTART_SEPARATION_REQUIRED'); sha(a['remediation_digest']); require(self.now()<number(a['expires_at']),'RESTART_REVIEW_EXPIRED')
        self.put(c,'restart',a['incident'],dict(a,reviewer=actor,key_version=self.get(c,'principal',actor)['version'],used=False),new=True)
        return {'incident':a['incident']}

    def op_restart(self,c,actor,a):
        exact(a,'incident remediation_digest'); incident=self.get(c,'incident',a['incident']); approval=self.get(c,'restart',a['incident'])
        reviewer=self.reviewer(c,approval['reviewer'])
        require(actor!=approval['reviewer'] and reviewer['key_version']==approval['key_version'],'RESTART_SEPARATION_REQUIRED')
        require(not approval['used'] and self.now()<approval['expires_at'] and a['remediation_digest']==approval['remediation_digest'],'RESTART_UNAVAILABLE')
        cohort=self.get(c,'cohort',incident['cohort'])
        require(cohort['generation']==incident['cohort_generation'],'NEWER_INCIDENT')
        # Do not allow an old incident review to reopen a run stopped again later.
        for identity in incident['stopped']:
            run=self.get(c,'run',identity); require(run['state']=='stopped','RUN_NOT_STOPPED')
            others=[i for i in self.population(c,'incident').values() if identity in i['stopped'] and i['stopped_at']>incident['stopped_at']]
            require(not others,'NEWER_INCIDENT'); self.environment(c,run['environment'])
            run.update(state='active',steps=0,last_progress=self.now()); self.put(c,'run',identity,run)
        cohort['state']='active'; self.put(c,'cohort',incident['cohort'],cohort)
        approval['used']=True; self.put(c,'restart',a['incident'],approval)
        return {'runs':incident['stopped'],'fresh_grants_required':True}

    def op_oracle(self,c,actor,a):
        exact(a,'id cases max_evaluations min_improvement max_regressions')
        require(type(a['cases']) is list and a['cases'],'CASES_REQUIRED'); integer(a['max_evaluations'],1); integer(a['min_improvement'],1); integer(a['max_regressions'])
        for case in a['cases']:
            exact(case,'route expected_sink'); label(case['route'])
            if case['expected_sink'] is not None: label(case['expected_sink'])
        require(len({x['route'] for x in a['cases']})==len(a['cases']),'DUPLICATE_CASE')
        self.put(c,'oracle',a['id'],dict(a,owner=actor,evaluations=0),new=True); return {'oracle':a['id']}

    def op_select_oracle(self,c,actor,a):
        exact(a,'oracle'); self.get(c,'oracle',a['oracle'])
        self.put(c,'meta','current-oracle',{'id':a['oracle']}); return {'oracle':a['oracle']}

    def op_propose_change(self,c,actor,a):
        exact(a,'id base_digest harness oracle cause_digest')
        sha(a['cause_digest']); sha(a['base_digest']); exact(a['harness'],'instruction_digest routes'); sha(a['harness']['instruction_digest'])
        require(type(a['harness']['routes']) is dict and a['harness']['routes'],'ROUTES_REQUIRED')
        for route,sink in a['harness']['routes'].items(): label(route); label(sink)
        require(a['base_digest']==digest(self.get(c,'meta','harness')),'CHANGE_BASE_STALE')
        require(self.get(c,'meta','current-oracle')['id']==a['oracle'],'ORACLE_NOT_CURRENT')
        oracle=self.get(c,'oracle',a['oracle']); require(oracle['owner']!=actor,'EVALUATOR_SEPARATION_REQUIRED')
        self.put(c,'change',a['id'],dict(a,proposer=actor,state='proposed'),new=True); return {'change':a['id']}

    def op_evaluate_change(self,c,actor,a):
        exact(a,'change'); change=self.get(c,'change',a['change']); oracle=self.get(c,'oracle',change['oracle'])
        require(actor==oracle['owner'] and actor!=change['proposer'],'EVALUATOR_SEPARATION_REQUIRED')
        require(change['state']=='proposed','CHANGE_ALREADY_EVALUATED')
        require(self.get(c,'meta','current-oracle')['id']==change['oracle'],'ORACLE_NOT_CURRENT')
        baseline=self.get(c,'meta','harness'); require(digest(baseline)==change['base_digest'],'CHANGE_BASE_STALE')
        require(oracle['evaluations']<oracle['max_evaluations'],'EVALUATION_BUDGET_EXHAUSTED')
        changed={route for route in set(baseline['routes'])|set(change['harness']['routes'])
                 if baseline['routes'].get(route)!=change['harness']['routes'].get(route)}
        require(changed<={x['route'] for x in oracle['cases']},'UNEVALUATED_ROUTE')
        old=[baseline['routes'].get(x['route'])==x['expected_sink'] for x in oracle['cases']]
        new=[change['harness']['routes'].get(x['route'])==x['expected_sink'] for x in oracle['cases']]
        improvement=sum(new)-sum(old); regressions=sum(before and not after for before,after in zip(old,new))
        accepted=improvement>=oracle['min_improvement'] and regressions<=oracle['max_regressions']
        change.update(state='evaluated' if accepted else 'rejected',evaluator=actor,improvement=improvement,regressions=regressions,oracle_digest=digest(oracle['cases']))
        oracle['evaluations']+=1; self.put(c,'oracle',change['oracle'],oracle); self.put(c,'change',a['change'],change)
        return {'state':change['state'],'improvement':improvement,'regressions':regressions}

    def op_admit_change(self,c,actor,a):
        exact(a,'change harness_digest'); change=self.get(c,'change',a['change']); self.reviewer(c,actor)
        require(change['state']=='evaluated' and actor not in (change['proposer'],change['evaluator']),'CHANGE_NOT_INDEPENDENTLY_EVALUATED')
        require(a['harness_digest']==digest(change['harness']),'CANDIDATE_CHANGED')
        require(not any(ch['state']=='open' for ch in self.population(c,'challenge').values()),'UNRESOLVED_REVIEW_DEBT')
        change.update(state='admitted',reviewer=actor,reviewer_version=self.get(c,'principal',actor)['version']); self.put(c,'change',a['change'],change)
        return {'change':a['change']}

    def op_activate_change(self,c,actor,a):
        exact(a,'change'); change=self.get(c,'change',a['change'])
        require(change['state']=='admitted' and actor not in (change['proposer'],change['evaluator'],change['reviewer']),'CHANGE_SEPARATION_REQUIRED')
        require(self.get(c,'meta','current-oracle')['id']==change['oracle'],'ORACLE_NOT_CURRENT')
        reviewer=self.reviewer(c,change['reviewer']); require(reviewer['key_version']==change['reviewer_version'],'REVIEWER_KEY_CHANGED')
        require(digest(self.get(c,'meta','harness'))==change['base_digest'],'CHANGE_BASE_STALE')
        require(not any(ch['state']=='open' for ch in self.population(c,'challenge').values()),'UNRESOLVED_REVIEW_DEBT')
        self.put(c,'meta','harness',change['harness'])
        for identity,p in self.population(c,'proposal').items():
            if p['state'] in ('pending','approved'):
                p.update(state='superseded',superseded_by=a['change']); self.put(c,'proposal',identity,p)
        change['state']='activated'; self.put(c,'change',a['change'],change)
        return {'harness_digest':digest(change['harness'])}

    def op_obligation(self,c,actor,a):
        exact(a,'id effect predicate expected due_at')
        require(self.now()<number(a['due_at']),'OBLIGATION_DEADLINE_INVALID')
        label(a['effect']); require(a['predicate'] in ('effect_present','exact_payload','evidence_available','subjective'),'UNKNOWN_PREDICATE')
        if a['predicate']=='exact_payload': sha(a['expected'])
        elif a['predicate'] in ('effect_present','evidence_available'): require(type(a['expected']) is bool,'BOOLEAN_EXPECTED')
        else: label(a['expected'])
        require(c.execute('SELECT 1 FROM effects WHERE id=?',(a['effect'],)).fetchone() is None,'OBLIGATION_AFTER_EFFECT')
        self.put(c,'obligation',a['id'],dict(a,owner=actor,at=self.now()),new=True); return {'obligation':a['id']}

    def op_recourse(self,c,actor,a):
        exact(a,'id obligation'); obligation=self.get(c,'obligation',a['obligation'])
        row=c.execute('SELECT payload,evidence FROM effects WHERE id=?',(obligation['effect'],)).fetchone()
        outcome='unevaluable'; reason='SUBJECTIVE_OBLIGATION'
        if self.now()<obligation['due_at']: reason='OBLIGATION_NOT_DUE'
        elif obligation['predicate']=='effect_present':
            outcome='compliant' if bool(row)==obligation['expected'] else 'violated'; reason='LOCAL_DESTINATION_OBSERVED'
        elif obligation['predicate']=='exact_payload':
            if row: outcome='compliant' if hashlib.sha256(row['payload'].encode()).hexdigest()==obligation['expected'] else 'violated'; reason='LOCAL_PAYLOAD_OBSERVED'
            else: reason='EFFECT_EVIDENCE_UNAVAILABLE'
        elif obligation['predicate']=='evidence_available':
            available=bool(row and row['evidence']); outcome='compliant' if available==obligation['expected'] else 'violated'; reason='EVIDENCE_AVAILABILITY_ONLY'
        packet=dict(a,obligation_digest=digest(obligation),outcome=outcome,reason=reason,adjudicator=actor,at=self.now(),disposition=None,authorizing=False)
        self.put(c,'recourse',a['id'],packet,new=True); return packet

    def op_adjudicate(self,c,actor,a):
        exact(a,'packet disposition reason_digest'); packet=self.get(c,'recourse',a['packet'])
        require(a['packet'] not in self.population(c,'adjudication'),'ALREADY_ADJUDICATED'); require(a['disposition'] in ('no-remedy','remedy-approved','disputed'),'INVALID_DISPOSITION'); sha(a['reason_digest'])
        self.put(c,'adjudication',a['packet'],dict(packet=a['packet'],disposition=a['disposition'],decision_by=actor,decision_reason=a['reason_digest'],at=self.now()),new=True)
        self.put(c,'resolution',a['packet'],{'kind':'adjudication','id':a['packet']})
        return {'disposition':a['disposition'],'authorizing':False,'payment_issued':False}

    def correction_permitted(self,c,packet):
        self.get(c,'recourse',packet)
        require(not any(x['packet']==packet and x['state']=='pending' for x in self.population(c,'appeal').values()),'CORRECTION_APPEALED')
        resolution=self.get(c,'resolution',packet); decision=self.get(c,resolution['kind'],resolution['id'])
        require(decision['disposition']=='remedy-approved','CORRECTION_NOT_ADJUDICATED')
        return digest(decision)

    def op_appeal(self,c,actor,a):
        exact(a,'id packet reason_digest'); sha(a['reason_digest']); packet=self.get(c,'recourse',a['packet'])
        obligation=self.get(c,'obligation',packet['obligation']); require(obligation['owner']==actor,'APPEAL_OWNER_MISMATCH')
        resolution=self.get(c,'resolution',a['packet']); prior=self.get(c,resolution['kind'],resolution['id'])
        require(not any(x['packet']==a['packet'] and x['state']=='pending' for x in self.population(c,'appeal').values()),'APPEAL_PENDING')
        self.put(c,'appeal',a['id'],dict(a,state='pending',owner=actor,prior=resolution,prior_digest=digest(prior)),new=True)
        return {'appeal':a['id'],'authorizing':False}

    def op_decide_appeal(self,c,actor,a):
        exact(a,'appeal disposition reason_digest'); sha(a['reason_digest']); appeal=self.get(c,'appeal',a['appeal'])
        prior=self.get(c,appeal['prior']['kind'],appeal['prior']['id'])
        require(appeal['state']=='pending' and digest(prior)==appeal['prior_digest'],'APPEAL_UNAVAILABLE')
        require(actor!=prior['decision_by'],'APPEAL_SEPARATION_REQUIRED')
        require(a['disposition'] in ('no-remedy','remedy-approved','disputed'),'INVALID_DISPOSITION')
        self.put(c,'appeal-decision',a['appeal'],dict(a,packet=appeal['packet'],decision_by=actor,at=self.now()),new=True)
        appeal['state']='resolved'; self.put(c,'appeal',a['appeal'],appeal)
        self.put(c,'resolution',appeal['packet'],{'kind':'appeal-decision','id':a['appeal']})
        return {'disposition':a['disposition'],'authorizing':False,'payment_issued':False}

    def journal(self):
        with self.connection() as c:
            c.execute('BEGIN')
            return {'stream':self.get(c,'meta','stream')['id'],'events':[dict(seq=r['seq'],body=json.loads(r['body']),previous=r['previous'],head=r['head']) for r in c.execute('SELECT * FROM events ORDER BY seq')]}


class LocalWitness:
    """Separate durable prefix receiver; same-host use is not independent custody.

    No private payloads are retained. The operator supplies the expected stream,
    initial trusted prefix, clock and signing configuration outside this class.
    """
    def __init__(self,path,*,stream): self.path=Path(path).resolve(); self.stream=label(stream)

    @classmethod
    def create(cls,path,*,stream):
        witness=cls(path,stream=stream)
        with witness.path.open('xb'): pass
        with closing(sqlite3.connect(witness.path)) as c:
            c.execute('CREATE TABLE prefix (id INTEGER PRIMARY KEY CHECK(id=1),stream TEXT,count INTEGER,head TEXT)')
            c.execute('INSERT INTO prefix VALUES (1,?,0,?)',(stream,ZERO)); c.commit()
        return witness

    def receive(self,journal,*,now):
        journal=json.loads(canonical(journal))
        exact(journal,'stream events'); require(journal['stream']==self.stream,'AUDIENCE_MISMATCH'); number(now)
        require(type(journal['events']) is list,'EVENTS_REQUIRED')
        previous=ZERO
        for seq,e in enumerate(journal['events'],1):
            exact(e,'seq body previous head')
            require(type(e['seq']) is int and e['seq']==seq and e['previous']==previous,'JOURNAL_SEQUENCE_INVALID')
            require(e['head']==digest({'seq':seq,'body':e['body'],'previous':previous}),'JOURNAL_HASH_INVALID'); previous=e['head']
        with closing(sqlite3.connect(self.path.as_uri()+'?mode=rw',uri=True,isolation_level=None)) as c:
            c.execute('PRAGMA synchronous=FULL'); c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT stream,count,head FROM prefix WHERE id=1').fetchone(); require(old is not None and old[0]==self.stream,'WITNESS_SCOPE_MISMATCH')
            require(len(journal['events'])>=old[1],'JOURNAL_TRUNCATED')
            require(old[1]==0 or journal['events'][old[1]-1]['head']==old[2],'JOURNAL_FORK')
            c.execute('UPDATE prefix SET count=?,head=? WHERE id=1',(len(journal['events']),previous)); c.commit()
        return dict(stream=self.stream,count=len(journal['events']),head=previous,observed_at=now)
