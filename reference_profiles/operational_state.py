"""Optional structured-state gates; trusted host, synthetic SQLite effects only.

No natural-language classification, geospatial transformation, fairness certificate,
model identity proof, or enterprise policy language is implemented here.
"""
from .assurance_runtime import exact, require, label, integer, names, sha, digest
from .federated_governance import FederatedGovernanceRuntime


class OperationalStateRuntime(FederatedGovernanceRuntime):
    roles = dict(FederatedGovernanceRuntime.roles, blocker='reviewer', resolve_blocker='reviewer',
                 handoff='agent', execution_contract='operator', population_sample='evaluator',
                 opportunity='agent', opportunity_feedback='reviewer', lineage_claim='agent')

    def op_blocker(self, c, actor, a):
        exact(a, 'id run prerequisite resolver fallback evidence_digest')
        self.reviewer(c, actor); self.get(c, 'run', a['run']); self.reviewer(c, a['resolver'])
        for f in ('id', 'prerequisite', 'fallback'): label(a[f])
        sha(a['evidence_digest'])
        self.put(c, 'blocker', a['id'], dict(a, owner=actor, status='stop'), new=True)
        return {'status': 'stop'}

    def op_resolve_blocker(self, c, actor, a):
        exact(a, 'blocker evidence')
        self.reviewer(c, actor); b = self.get(c, 'blocker', a['blocker'])
        require(actor == b['resolver'] and actor != b['owner'], 'BLOCKER_RESOLVER')
        require(b['status'] == 'stop' and digest(a['evidence']) == b['evidence_digest'], 'BLOCKER_EVIDENCE')
        self.put(c, 'blocker-resolution', a['blocker'], dict(a, actor=actor, at=self.now()), new=True)
        b['status'] = 'resolved'; self.put(c, 'blocker', a['blocker'], b)
        return {'status': 'resolved'}

    def blocker_state(self, c, run):
        return {k: v for k, v in self.population(c, 'blocker').items() if v['run'] == run}

    def op_handoff(self, c, actor, a):
        exact(a, 'id run predecessor state summary_digest')
        self.active_run(c, a['run'], actor); sha(a['summary_digest']); sha(a['predecessor'])
        prior = self.population(c, 'handoff-head').get(a['run'], {'head': '0' * 64})
        require(a['predecessor'] == prior['head'], 'HANDOFF_PREDECESSOR')
        require(a['state'] == self.blocker_state(c, a['run']), 'HANDOFF_STATE_LOSS')
        record = dict(a, actor=actor, at=self.now()); head = digest(record)
        self.put(c, 'handoff', a['id'], record, new=True)
        self.put(c, 'handoff-head', a['run'], {'head': head})
        return {'head': head, 'authorizing': False}

    def op_execution_contract(self, c, actor, a):
        exact(a, 'run version principal action resource context decisions required_obligations completed_obligations spatial population')
        run = self.get(c, 'run', a['run']); integer(a['version'], 1)
        require(a['principal'] == run['agent'] and a['action'] == 'sqlite-insert', 'CONTRACT_SCOPE')
        label(a['resource']); require(a['context'] == self.config(c)['context'], 'CONTRACT_SCOPE')
        require(type(a['decisions']) is list and a['decisions'] and all(x in ('allow', 'deny', 'approve') for x in a['decisions']), 'INVALID_DECISIONS')
        for f in ('required_obligations', 'completed_obligations'):
            require(type(a[f]) is list, 'INVALID_OBLIGATIONS')
            if a[f]: names(a[f])
        require(set(a['completed_obligations']) <= set(a['required_obligations']), 'UNKNOWN_OBLIGATION')
        s = a['spatial']; exact(s, 'crs expected_crs resolution max_resolution uncertainty max_uncertainty observed_at expires_at evidence_digest')
        label(s['crs']); label(s['expected_crs']); sha(s['evidence_digest'])
        for f in ('resolution', 'max_resolution', 'uncertainty', 'max_uncertainty', 'observed_at', 'expires_at'): integer(s[f])
        require(s['observed_at'] <= self.now() < s['expires_at'], 'SPATIAL_TIME')
        p = a['population']; exact(p, 'cohort groups minimum_count max_gap_ppm max_age')
        require(p['cohort'] == run['cohort'], 'POPULATION_SCOPE'); names(p['groups'])
        require(len(p['groups']) >= 2, 'POPULATION_GROUPS'); integer(p['minimum_count'], 1); integer(p['max_age'], 1)
        require(integer(p['max_gap_ppm']) <= 1000000, 'INVALID_GAP')
        old = self.population(c, 'execution-contract').get(a['run'])
        require(old is None or a['version'] > old['version'], 'CONTRACT_VERSION')
        self.put(c, 'execution-contract-history', a['run'] + ':' + str(a['version']), dict(a, actor=actor), new=True)
        self.put(c, 'execution-contract', a['run'], dict(a, actor=actor))
        return {'version': a['version'], 'authorizing': False}

    def op_population_sample(self, c, actor, a):
        exact(a, 'id cohort group observed_at total positive expected_ppm evidence_digest')
        label(a['cohort']); label(a['group']); sha(a['evidence_digest'])
        require(integer(a['observed_at']) <= self.now(), 'FUTURE_OBSERVATION')
        require(integer(a['positive']) <= integer(a['total'], 1), 'INVALID_COUNTS')
        require(integer(a['expected_ppm']) <= 1000000, 'INVALID_RATE')
        self.put(c, 'population-sample', a['id'], dict(a, actor=actor), new=True)
        return {'authorizing': False}

    def operational_binding(self, c, run):
        blockers = self.blocker_state(c, run)
        require(not any(b['status'] == 'stop' for b in blockers.values()), 'UNRESOLVED_BLOCKER')
        contract = self.get(c, 'execution-contract', run)
        require('deny' not in contract['decisions'], 'POLICY_DENY')
        require('approve' not in contract['decisions'], 'POLICY_AWAIT_APPROVAL')
        require(set(contract['completed_obligations']) == set(contract['required_obligations']), 'POLICY_OBLIGATION_PENDING')
        require(contract['resource'] == self.get(c, 'relation', run)['object'], 'CONTRACT_RESOURCE')
        s = contract['spatial']
        require(s['crs'] == s['expected_crs'] and s['resolution'] <= s['max_resolution'] and s['uncertainty'] <= s['max_uncertainty'], 'SPATIAL_UNSUPPORTED')
        require(s['observed_at'] <= self.now() < s['expires_at'], 'SPATIAL_TIME')
        p = contract['population']; samples = self.population(c, 'population-sample'); used = {}
        for group in p['groups']:
            selected = {k: v for k, v in samples.items() if v['cohort'] == p['cohort'] and v['group'] == group and 0 <= self.now() - v['observed_at'] < p['max_age']}
            require(bool(selected), 'POPULATION_INDETERMINATE')
            # Each sample is an independent complete window, not additive telemetry.
            # Check every current window: a benign later sample cannot erase an alarm.
            for k, v in selected.items():
                require(v['total'] >= p['minimum_count'], 'POPULATION_INDETERMINATE')
                require(abs(v['positive'] * 1000000 - v['expected_ppm'] * v['total']) <= p['max_gap_ppm'] * v['total'], 'POPULATION_ALARM')
                used[k] = v
        return {'contract': digest(contract), 'blockers': digest(blockers), 'population': digest(used)}

    def governance_binding(self, c, run, item):
        return dict(super().governance_binding(c, run, item), operational=self.operational_binding(c, run))

    def op_opportunity(self, c, actor, a):
        exact(a, 'id run mode benefit interruption privacy misunderstanding evidence_digest')
        self.active_run(c, a['run'], actor); sha(a['evidence_digest'])
        require(a['mode'] in ('silent', 'ask', 'assist', 'act'), 'INVALID_MODE')
        for f in ('benefit', 'interruption', 'privacy', 'misunderstanding'): integer(a[f])
        # Estimates are observations, never permissions or episode activation.
        self.put(c, 'opportunity', a['id'], dict(a, actor=actor, at=self.now()), new=True)
        return {'estimated_net': a['benefit'] - sum(a[f] for f in ('interruption', 'privacy', 'misunderstanding')), 'authorizing': False}

    def op_opportunity_feedback(self, c, actor, a):
        exact(a, 'id opportunity accepted burden evidence_digest')
        self.reviewer(c, actor); self.get(c, 'opportunity', a['opportunity']); integer(a['burden']); sha(a['evidence_digest'])
        require(type(a['accepted']) is bool, 'INVALID_FEEDBACK')
        self.put(c, 'opportunity-feedback', a['id'], dict(a, actor=actor, at=self.now()), new=True)
        return {'permission_changed': False}

    def op_perceive(self, c, actor, a):
        result = super().op_perceive(c, actor, a)
        self.put(c, 'acquisition', a['id'], {'at': self.now()}, new=True)
        return result

    def op_lineage_claim(self, c, actor, a):
        exact(a, 'run item checkpoint content_digest')
        self.active_run(c, a['run'], actor); integer(a['checkpoint']); sha(a['content_digest'])
        perception, item = self.perception(c, a['item'], a['run'])
        require(self.get(c, 'acquisition', a['item'])['at'] <= a['checkpoint'] <= self.now(), 'LINEAGE_TIME')
        require(digest(item['content']) == a['content_digest'], 'LINEAGE_CONTENT')
        return {'provenance_supported': True, 'identity_established': False, 'authorizing': False}


REPORT_FIELDS = ('task_artifact', 'model_adaptation', 'harness_tools', 'budget_human_input',
                 'data_contamination', 'validation', 'uncertainty_failures', 'reproducibility')
ASSURANCE_AXES = ('functional', 'security', 'operational', 'provenance', 'authority')


def assess_report(report):
    """Completeness only. A functional pass cannot manufacture security acceptance."""
    exact(report, 'disclosures claims')
    exact(report['disclosures'], ' '.join(REPORT_FIELDS))
    for value in report['disclosures'].values(): label(value)
    exact(report['claims'], ' '.join(ASSURANCE_AXES))
    for value in report['claims'].values():
        exact(value, 'status evidence_digest')
        require(value['status'] in ('supported', 'failed', 'not-established', 'not-applicable'), 'INVALID_CLAIM_STATUS')
        if value['status'] == 'supported': sha(value['evidence_digest'])
        else: require(value['evidence_digest'] is None, 'UNSUPPORTED_EVIDENCE_FIELD')
    return {'report_complete': True, 'claims': report['claims'], 'independently_verified': False,
            'reference_release_authorized': False, 'production_deployment_authorized': False}
