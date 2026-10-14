"""Opt-in trusted-host governance extension. Synthetic SQLite effects only.

Public-key acceptance supplements the existing HMAC transport. No institutional
appointment, OS isolation, external settlement or release authority is implied.
"""
from copy import deepcopy
import hashlib
from .assurance_runtime import AssuranceRuntime, ROLES, require, exact, label, integer, number, names, sha, digest, Denied
from .trust_evidence import verify, commitment, wire, verdict, work_report

DOMAINS={'social','business','process','machine','real-world'}


class FederatedGovernanceRuntime(AssuranceRuntime):
    roles=dict(ROLES, fact='operator', relation='operator', mandate='operator', consent='operator',
               perceive='steward', retrieve='agent', activate_episode='agent',
               change_context='builder', accept_change='operator', condition='reviewer', close_condition='reviewer',
               continuity_propose='agent', continuity_check='reviewer', continuity_activate='operator',
               work='reviewer')

    @classmethod
    def create(cls,path,*,governance,**kwargs):
        wire(governance); exact(governance,'registry anchors restart_signers restart_quorum context source_classes max_source_age')
        require(type(governance['anchors']) is dict and governance['anchors'],'ANCHORS_REQUIRED')
        principals=list(governance['anchors'].values()); restart=names(governance['restart_signers'])
        require(len(principals)==len(set(principals)),'ANCHOR_PRINCIPALS_DISTINCT')
        integer(governance['restart_quorum'],2); require(governance['restart_quorum']<=len(restart),'INVALID_QUORUM')
        keys=[]
        for principal in set(principals)|restart:
            key=governance['registry'][principal]; exact(key,'public_key not_before expires_at revoked_at')
            require(len(bytes.fromhex(key['public_key']))==32,'PUBLIC_KEY_REQUIRED'); keys.append(key['public_key'])
            integer(key['not_before']); integer(key['expires_at']); require(key['not_before']<key['expires_at'],'INVALID_KEY_INTERVAL')
        require(len(keys)==len(set(keys)),'DISTINCT_PUBLIC_KEYS_REQUIRED')
        label(governance['context']); names(governance['source_classes']); integer(governance['max_source_age'],1)
        runtime=super().create(path,**kwargs)
        with runtime.connection() as c:
            c.execute('BEGIN IMMEDIATE'); runtime.put(c,'meta','governance',deepcopy(governance),new=True); c.commit()
        return runtime

    def config(self,c): return self.get(c,'meta','governance')

    def signed_body(self,c,record,kind,expected,allowed):
        require(type(record) is dict and record.get('kind')==kind and record.get('issuer') in allowed,'SIGNER_SCOPE')
        try:
            integer(record['body']['at'])
            b=verify(record,self.config(c)['registry'],at=record['body']['at'],now=self.now())
            require(b==expected,'SIGNED_CONTENT_CHANGED')
        except (ValueError,KeyError,TypeError) as exc:
            raise Denied('SIGNATURE_OR_BINDING_INVALID') from exc
        return record['issuer']

    def op_fact(self,c,actor,a):
        exact(a,'id version object context source_class effective_at expires_at reviewed_at review_due status evidence_digest')
        cfg=self.config(c)
        for f in ('id','object','context','source_class'): label(a[f])
        integer(a['version'],1); sha(a['evidence_digest'])
        for f in ('effective_at','expires_at','reviewed_at','review_due'): integer(a[f])
        require(a['effective_at']<a['expires_at'] and a['reviewed_at']<=self.now()<a['review_due'],'INVALID_FACT_TIME')
        require(a['status'] in ('active','superseded','conflict'),'INVALID_FACT_STATUS')
        old=self.population(c,'fact').get(a['id'])
        require(old is None or a['version']>old['version'],'FACT_VERSION_ROLLBACK')
        if old: self.put(c,'fact-history',a['id']+':'+str(old['version']),old,new=True)
        self.put(c,'fact',a['id'],dict(a,owner=actor)); return {'fact':a['id'],'version':a['version']}

    def fact(self,c,identity):
        f=self.get(c,'fact',identity); cfg=self.config(c); now=self.now()
        require(f['context']==cfg['context'] and f['source_class'] in cfg['source_classes'],'AUTHORITY_CONTEXT')
        require(f['status']=='active','AUTHORITY_CONFLICT_OR_SUPERSEDED')
        require(f['effective_at']<=now<f['expires_at'] and now<f['review_due'] and 0<=now-f['reviewed_at']<=cfg['max_source_age'],'AUTHORITY_STALE')
        return f

    def op_relation(self,c,actor,a):
        exact(a,'run object action context domains facts')
        run=self.get(c,'run',a['run']); label(a['object']); label(a['action'])
        require(a['context']==self.config(c)['context'],'AUTHORITY_CONTEXT')
        require(type(a['domains']) is dict and set(a['domains'])==DOMAINS and all(v==a['object'] for v in a['domains'].values()),'OBJECT_RESOLUTION_MISMATCH')
        names(a['facts'])
        for identity in a['facts']:
            require(self.fact(c,identity)['object']==a['object'],'OBJECT_RESOLUTION_MISMATCH')
        require(a['action']=='sqlite-insert','UNSUPPORTED_ACTION')
        old=self.population(c,'relation').get(a['run']); version=1 if old is None else old['version']+1
        self.put(c,'relation',a['run'],dict(a,version=version,owner=actor)); return {'relation_version':version}

    def relation(self,c,run):
        r=self.get(c,'relation',run); facts={i:self.fact(c,i) for i in r['facts']}
        require(all(f['object']==r['object'] for f in facts.values()),'OBJECT_RESOLUTION_MISMATCH')
        return {'relation':r,'facts':facts}

    def op_run(self,c,actor,a):
        result=super().op_run(c,actor,a)
        state={'history':[],'memory':{},'norms':{'execution':'local-only'},'policy':'continuity/1'}
        self.put(c,'continuity',a['id'],{'state':state,'head':commitment(state),'epoch':0},new=True)
        return result

    def op_mandate(self,c,actor,a):
        exact(a,'run modes channels risk_ceiling expires_at enabled')
        self.get(c,'run',a['run']); require(names(a['modes'])<={'act','ask','monitor','defer','refrain'},'INVALID_MODE')
        names(a['channels']); integer(a['risk_ceiling']); integer(a['expires_at'])
        require(type(a['enabled']) is bool and self.now()<a['expires_at'],'INVALID_MANDATE')
        old=self.population(c,'mandate').get(a['run']); version=1 if old is None else old['version']+1
        self.put(c,'mandate',a['run'],dict(a,version=version,owner=actor)); return {'version':version}

    def mandate(self,c,run):
        m=self.get(c,'mandate',run)
        require(m['enabled'] and self.now()<m['expires_at'],'MANDATE_UNAVAILABLE')
        return m

    def op_consent(self,c,actor,a):
        exact(a,'run channel purpose expires_at enabled')
        run=self.get(c,'run',a['run']); m=self.mandate(c,a['run']); label(a['channel'])
        require(a['channel'] in m['channels'] and a['purpose']==run['purpose'],'CONSENT_SCOPE')
        require(type(a['enabled']) is bool and self.now()<integer(a['expires_at'])<=m['expires_at'],'INVALID_CONSENT')
        self.put(c,'consent',a['run']+':'+a['channel'],dict(a,owner=actor)); return {'enabled':a['enabled']}

    def consent(self,c,run,channel):
        r=self.get(c,'run',run); m=self.mandate(c,run); permission=self.get(c,'consent',run+':'+channel)
        require(permission['enabled'] and self.now()<permission['expires_at'] and permission['purpose']==r['purpose'] and channel in m['channels'],'CONSENT_UNAVAILABLE')
        return permission

    def op_perceive(self,c,actor,a):
        exact(a,'id run channel integrity content labels parents expires_at')
        self.consent(c,a['run'],a['channel'])
        require(a['integrity'] in ('trusted','untrusted'),'INVALID_INTEGRITY')
        for parent in a['parents']:
            p=self.get(c,'perception',parent)
            require(p['run']==a['run'],'PERCEPTION_SCOPE')
            require(p['integrity']=='trusted' or a['integrity']=='untrusted','INTEGRITY_PROMOTION')
        result=super().op_ingest(c,actor,{k:a[k] for k in ('id','content','labels','parents','expires_at')})
        self.put(c,'perception',a['id'],{'run':a['run'],'channel':a['channel'],'integrity':a['integrity'],'instruction_authority':False},new=True)
        return result

    def op_ingest(self,c,actor,a):
        raise Denied('USE_CONSENT_GATED_PERCEPTION')

    def perception(self,c,item,run,seen=None):
        seen=set() if seen is None else seen; require(item not in seen,'CYCLIC_PROVENANCE'); seen=seen|{item}
        p=self.get(c,'perception',item); require(p['run']==run,'PERCEPTION_SCOPE'); self.consent(c,run,p['channel'])
        source=self.item(c,item)
        for parent in source['parents']: self.perception(c,parent,run,seen)
        return p,source

    def op_retrieve(self,c,actor,a):
        exact(a,'run item'); self.active_run(c,a['run'],actor); p,item=self.perception(c,a['item'],a['run'])
        return {'content':item['content'],'integrity':p['integrity'],'labels':item['labels'],'instruction_authority':False}

    def op_activate_episode(self,c,actor,a):
        exact(a,'id run mode risk readiness threshold reason_digest')
        self.active_run(c,a['run'],actor); m=self.mandate(c,a['run']); sha(a['reason_digest'])
        for field in ('risk','readiness','threshold'): integer(a[field])
        require(a['mode'] in m['modes'],'MODE_NOT_PERMITTED')
        if a['mode']=='act':
            require(a['risk']<=m['risk_ceiling'] and a['readiness']>=a['threshold'],'ACTIVATION_NOT_ADMITTED')
        self.put(c,'episode',a['run'],dict(a,mandate_version=m['version'],actor=actor,at=self.now()))
        self.put(c,'episode-history',a['id'],dict(a,mandate_version=m['version'],actor=actor,at=self.now()),new=True)
        return {'mode':a['mode'],'authorizing':False}

    def governance_binding(self,c,run,item):
        r=self.get(c,'run',run); m=self.mandate(c,run); episode=self.get(c,'episode',run)
        require(episode['mode']=='act' and episode['mandate_version']==m['version'],'ACTIVATION_UNAVAILABLE')
        p,_=self.perception(c,item,run)
        return {'authority':digest(self.relation(c,run)),'mandate':digest(m),'episode':digest(episode),
                'continuity':self.get(c,'continuity',run)['head'],'perception':digest(p),'generation':r['generation']}

    def proposal_binding(self,c,actor,a):
        # Existing base validation is preserved; additional current gates run here
        # so inherited review/execution cannot bypass the extension.
        self.governance_binding(c,a['run'],a['item'])
        result=super().proposal_binding(c,actor,a)
        require(self.get(c,'relation',a['run'])['object']==result[3],'AUTHORITY_RESOURCE_MISMATCH')
        return result

    def op_execute(self,c,actor,a):
        exact(a,'proposal'); p=self.get(c,'proposal',a['proposal'])
        # Existing duplicate reconciliation remains available without a new effect.
        prior=c.execute('SELECT 1 FROM effects WHERE id=?',(p['proposal']['effect'],)).fetchone()
        if prior: return super().op_execute(c,actor,a)
        current=self.governance_binding(c,p['proposal']['run'],p['proposal']['item'])
        require(current==p['binding']['governance'],'GOVERNANCE_CHANGED')
        # Base executor recomputes its binding. Feed the additional commitment via
        # the shared binding hook rather than bypassing its checks or committing twice.
        return super().op_execute(c,actor,a)

    def extend_binding(self,c,proposal,binding):
        return dict(binding,governance=self.governance_binding(c,proposal['run'],proposal['item']))

    def op_change_context(self,c,actor,a):
        exact(a,'change facts'); change=self.get(c,'change',a['change']); require(actor==change['proposer'],'CHANGE_PROPOSER')
        names(a['facts']); facts={i:digest(self.fact(c,i)) for i in a['facts']}
        self.put(c,'change-context',a['change'],{'facts':facts},new=True); return {'facts':facts}

    def change_binding(self,c,identity):
        change=self.get(c,'change',identity); context=self.get(c,'change-context',identity)
        for identity,expected in context['facts'].items(): require(digest(self.fact(c,identity))==expected,'CHANGE_CONTEXT_STALE')
        return {'harness_digest':digest(change['harness']),'base_digest':change['base_digest'],'oracle':change['oracle'],'context_digest':digest(context)}

    def op_condition(self,c,actor,a):
        exact(a,'id change evidence_digest'); self.reviewer(c,actor); self.get(c,'change',a['change']); sha(a['evidence_digest'])
        require(self.get(c,'change',a['change'])['state']!='activated','CHANGE_ALREADY_ACTIVATED')
        self.put(c,'condition',a['id'],dict(a,owner=actor,state='open'),new=True); return {'state':'open'}

    def op_close_condition(self,c,actor,a):
        exact(a,'condition evidence'); self.reviewer(c,actor); condition=self.get(c,'condition',a['condition'])
        require(actor!=condition['owner'],'CONDITION_SEPARATION')
        require(condition['state']=='open' and commitment(a['evidence'])==condition['evidence_digest'],'CONDITION_EVIDENCE')
        self.put(c,'condition-closure',a['condition'],dict(a,reviewer=actor,at=self.now()),new=True)
        condition['state']='closed'; self.put(c,'condition',a['condition'],condition); return {'state':'closed'}

    def op_accept_change(self,c,actor,a):
        exact(a,'change record'); cfg=self.config(c); record=a['record']; b=record['body']
        exact(b,'change domain binding at expires_at decision'); require(self.now()<integer(b['expires_at']),'ACCEPTANCE_EXPIRED')
        require(b['change']==a['change'] and b['decision']=='accept' and b['binding']==self.change_binding(c,a['change']),'ACCEPTANCE_BINDING')
        issuer=cfg['anchors'].get(b['domain']); require(issuer is not None,'UNKNOWN_ANCHOR')
        self.signed_body(c,record,'change-acceptance',b,{issuer})
        self.put(c,'acceptance',a['change']+':'+b['domain'],record,new=True); return {'domain':b['domain']}

    def op_activate_change(self,c,actor,a):
        binding=self.change_binding(c,a['change']); cfg=self.config(c)
        require(not any(x['change']==a['change'] and x['state']=='open' for x in self.population(c,'condition').values()),'OPEN_CONDITION')
        for domain,issuer in cfg['anchors'].items():
            record=self.get(c,'acceptance',a['change']+':'+domain); b=record['body']
            require(b['binding']==binding and self.now()<b['expires_at'],'ACCEPTANCE_STALE')
            self.signed_body(c,record,'change-acceptance',b,{issuer})
        return super().op_activate_change(c,actor,a)

    def op_restart(self,c,actor,a):
        exact(a,'incident remediation_digest decision records')
        incident=self.get(c,'incident',a['incident']); d=a['decision']
        exact(d,'event_id incident incident_digest stream generation remediation_digest decision at expires_at')
        require(d['incident']==a['incident'] and d['incident_digest']==digest(incident) and d['stream']==self.get(c,'meta','stream')['id'] and d['generation']==incident['cohort_generation'] and d['remediation_digest']==a['remediation_digest'],'HALT_DECISION_BINDING')
        label(d['event_id']); require(d['decision']=='RESUME' and self.now()<integer(d['expires_at']),'RESUME_NOT_AUTHORIZED')
        require(d['event_id'] not in self.population(c,'halt-decision'),'HALT_DECISION_REPLAY')
        cfg=self.config(c); signers=[]
        for record in a['records']: signers.append(self.signed_body(c,record,'halt-decision',d,set(cfg['restart_signers'])))
        require(len(signers)==len(set(signers)) and len(signers)>=cfg['restart_quorum'],'RESTART_QUORUM')
        result=super().op_restart(c,actor,{k:a[k] for k in ('incident','remediation_digest')})
        self.put(c,'halt-decision',d['event_id'],{'decision':d,'records':a['records']},new=True)
        return result

    def op_continuity_propose(self,c,actor,a):
        exact(a,'id run predecessor operations evidence'); self.active_run(c,a['run'],actor)
        current=self.get(c,'continuity',a['run']); require(a['predecessor']==current['head'],'PREDECESSOR_STALE')
        require(type(a['operations']) is list and 0<len(a['operations'])<=32,'OPERATIONS_REQUIRED'); wire(a)
        state=deepcopy(current['state']); failures=[]; missing=[]
        for op in a['operations']:
            exact(op,'kind key value evidence')
            if op['kind'] not in ('remember','forget','succession'): failures.append('FORBIDDEN_MUTATION'); continue
            if op['kind']=='remember': state['memory'][label(op['key'])]=op['value']
            elif op['kind']=='forget': state['memory'].pop(label(op['key']),None)
            state['history'].append(commitment(op))
            expected=commitment({'kind':op['kind'],'key':op['key'],'value':op['value']})
            # Evidence content comes from authenticated steward perception, not a
            # candidate-provided assertion. Missing and contradictory remain distinct.
            identity=op['evidence']
            if identity not in a['evidence']: failures.append('UNDECLARED_DEPENDENCY'); continue
            if identity not in self.population(c,'item'): missing.append(identity); continue
            _,item=self.perception(c,identity,a['run'])
            if item['content']!=expected: failures.append('CONTRADICTORY_EVIDENCE')
        self.put(c,'continuity-candidate',a['id'],dict(a,state=state,next_head=commitment(state),epoch=current['epoch']+1,
                 checks=verdict(failures,missing),owner=actor,persisted_at=self.now(),activated=False),new=True)
        return {'candidate':a['id'],'persisted':True,'activated':False,'verdict':verdict(failures,missing)['verdict']}

    def op_continuity_check(self,c,actor,a):
        exact(a,'candidate'); self.reviewer(c,actor); candidate=self.get(c,'continuity-candidate',a['candidate'])
        require(actor!=candidate['owner'],'CONTINUITY_SEPARATION')
        # Freeze the initial evidence assessment. Missing dependencies need a new
        # proposal rather than silently rewriting the persisted candidate witness.
        self.put(c,'continuity-review',a['candidate'],{'candidate_digest':digest(candidate),'reviewer':actor,'key_version':self.get(c,'principal',actor)['version']},new=True)
        return candidate['checks']

    def op_continuity_activate(self,c,actor,a):
        exact(a,'candidate'); candidate=self.get(c,'continuity-candidate',a['candidate']); current=self.get(c,'continuity',candidate['run'])
        if candidate['activated']:
            return {'head':candidate['next_head'],'epoch':candidate['epoch'],'duplicate':True,'current_head':current['head'],'authorizing':False}
        review=self.get(c,'continuity-review',a['candidate']); r=self.reviewer(c,review['reviewer'])
        require(actor not in (candidate['owner'],review['reviewer']) and r['key_version']==review['key_version'],'CONTINUITY_SEPARATION')
        require(review['candidate_digest']==digest(candidate) and candidate['checks']['verdict']=='VALID','CONTINUITY_NOT_VALID')
        require(current['head']==candidate['predecessor'],'PREDECESSOR_STALE')
        self.active_run(c,candidate['run'])
        for op in candidate['operations']:
            _,item=self.perception(c,op['evidence'],candidate['run'])
            require(item['content']==commitment({'kind':op['kind'],'key':op['key'],'value':op['value']}),'CONTINUITY_EVIDENCE_CHANGED')
        require(current['state']['policy']==candidate['state']['policy'] and current['state']['norms']==candidate['state']['norms'],'IMMUTABLE_POLICY')
        self.put(c,'continuity',candidate['run'],{'head':candidate['next_head'],'state':candidate['state'],'epoch':candidate['epoch']})
        run=self.get(c,'run',candidate['run']); run['generation']+=1; self.put(c,'run',candidate['run'],run)
        for identity,g in self.population(c,'grant').items():
            if g['run']==candidate['run']: g.update(status='revoked',revision=g['revision']+1); self.put(c,'grant',identity,g)
        for identity,p in self.population(c,'proposal').items():
            if p['proposal']['run']==candidate['run'] and p['state'] in ('pending','approved'): p['state']='superseded'; self.put(c,'proposal',identity,p)
        candidate['activated']=True; self.put(c,'continuity-candidate',a['candidate'],candidate)
        return {'head':candidate['next_head'],'epoch':candidate['epoch'],'duplicate':False,'fresh_grants_required':True}

    def op_work(self,c,actor,a):
        exact(a,'id category minutes'); work_report([a],0)
        self.put(c,'work',a['id'],dict(a),new=True); return {'recorded':True,'substitution_established':False}
