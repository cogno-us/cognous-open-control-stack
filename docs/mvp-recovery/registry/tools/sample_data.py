"""Small synthetic sample dataset for the catalogue tools. Invented content only.

Nothing here is a real governance rule, scenario, test or result. It exists to exercise
the schemas, the generator and the validator, and to document the dataset shape.
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ocs_catalogue_validate_registry', os.path.join(HERE, 'validate_registry.py'))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

SAMPLE_MAX_PER_PARTITION = 4
REPO = 'example/synthetic-source'
REV = '0' * 40


def _d(name):
    return V.canonical_digest({'synthetic_raw_record': name})


def _src(path, anchor=None):
    return {'repo': REPO, 'revision': REV, 'path': path, 'anchor': anchor}


def _mv(value, reason):
    return {'value': value, 'reason': reason}


def _row(raw_set, index, name, tier, disposition, target, native=None, path='synthetic/source.md', reason=None):
    return {'raw_set': raw_set, 'raw_index': index, 'raw_digest': _d(name), 'source_repo': REPO, 'path': path,
            'native_id': native, 'tier': tier, 'disposition': disposition, 'target': target,
            'unresolved_reason': reason, 'annotations': {}}


def _registry_record():
    rule = {'rule_id': 'SYN-REG-1', 'version': 1, 'class': 'catalogue_sample', 'profile': 'synthetic', 'status': 'advisory',
            'applicability': {'kind': 'always'}, 'evaluator_id': 'catalogue-no-op', 'evaluator_version': 1,
            'failure_disposition': 'hold', 'missing_treatment': 'fail_closed', 'reason_code': 'SYN_SAMPLE',
            'source_ref': 'synthetic sample source'}
    rec = {'profile': 'ocs-registry-record/0', 'schema_version': 0, 'registry_id': 'ocs-catalogue-synthetic-sample',
           'canonical_profile': 'rfc8785-jcs', 'digest': 'sha256:' + '0' * 64, 'epoch': 1, 'predecessor': None,
           'rule_table': [rule],
           'evaluators': [{'evaluator_id': 'catalogue-no-op', 'version': 1, 'qualification_ref': 'unqualified: catalogue sample only, evaluates nothing'}],
           'reason_map': {'SYN_SAMPLE': 'synthetic sample row, informational only'}, 'source_refs': ['synthetic sample source'],
           'issuer': 'synthetic-sample'}
    rec['digest'] = V.digest_of(rec)
    return rec, rule


def _base_dataset():
    record, reg_rule = _registry_record()
    rules = [
        {'catalogue_id': 'R-SYN-floor-a-00000001', 'title': 'Synthetic statement A', 'tier': 'GOVERNANCE_RULE',
         'source': _src('synthetic/source.md', 'section 1'), 'native_ids': ['SYN-A'], 'aliases': ['SYN-A-legacy'],
         'raw_refs': ['SYN1:0', 'SYN1:2'], 'lineage': [],
         'rule_ref': {'kind': 'source_statement', 'rule_id': 'SYN-A', 'version': None,
                      'rule_digest': V.canonical_digest({'statement': 'synthetic statement A'}), 'registry_id': None, 'record_digest': None},
         'statement_verbatim': 'Synthetic statement A.', 'refund_specific': False,
         'mvp_applicability': _mv('unresolved', 'the sample source does not state profile membership'),
         'scenario_refs': ['S-SYN-case-1-00000001'], 'test_refs': [], 'evidence_digest_refs': [],
         'annotations': {'owner': 'unknown', 'enforcement_boundary': 'unknown'}},
        {'catalogue_id': 'R-SYN-reg-b-00000002', 'title': 'Synthetic registry rule B', 'tier': 'GOVERNANCE_RULE',
         'source': _src('synthetic/registry.json', 'rule SYN-REG-1'), 'native_ids': ['SYN-REG-1'], 'aliases': [],
         'raw_refs': ['SYN1:1', 'SYN1:3'],
         'lineage': [{'revision_id': 'SYN-REG-1@earlier', 'raw_ref': 'SYN1:3', 'digest': _d('rev-b'), 'relation': 'HISTORICAL_REVISION'}],
         'rule_ref': {'kind': 'registry_record', 'rule_id': reg_rule['rule_id'], 'version': reg_rule['version'],
                      'rule_digest': V.canonical_digest(reg_rule), 'registry_id': record['registry_id'], 'record_digest': record['digest']},
         'statement_verbatim': None, 'refund_specific': True,
         'mvp_applicability': _mv('mvp_fixed', 'the synthetic sample names this row as in profile'),
         'scenario_refs': ['S-SYN-case-1-00000001', 'S-SYN-case-2-00000002'], 'test_refs': ['T-SYN-test-1-00000001'],
         'evidence_digest_refs': [], 'annotations': {}},
    ]
    scenarios = [
        {'catalogue_id': 'S-SYN-case-1-00000001', 'title': 'Synthetic case 1', 'tier': 'LOGICAL_SCENARIO', 'source': _src('synthetic/cases.md'),
         'native_ids': ['SYN-CASE-1'], 'aliases': [], 'raw_refs': ['SYN1:4'], 'lineage': [],
         'rule_refs': ['R-SYN-floor-a-00000001', 'R-SYN-reg-b-00000002'], 'test_refs': ['T-SYN-test-1-00000001'],
         'evidence_digest_refs': [_d('evidence-1')], 'expected_outcome_verbatim': 'REFUSED', 'polarity': 'negative',
         'temporal_or_recovery_flag': False, 'scenario_family': 'synthetic', 'refund_specific': True,
         'mvp_applicability': _mv('mvp_fixed', 'the synthetic sample names this row as in profile'), 'annotations': {}},
        {'catalogue_id': 'S-SYN-case-2-00000002', 'title': 'Synthetic case 2 (recovery)', 'tier': 'LOGICAL_SCENARIO', 'source': _src('synthetic/cases.md'),
         'native_ids': ['SYN-CASE-2'], 'aliases': [], 'raw_refs': ['SYN1:5'], 'lineage': [],
         'rule_refs': ['R-SYN-reg-b-00000002'], 'test_refs': [], 'evidence_digest_refs': [],
         'expected_outcome_verbatim': 'NOT RUN', 'polarity': 'recovery', 'temporal_or_recovery_flag': True,
         'scenario_family': 'synthetic', 'refund_specific': None,
         'mvp_applicability': _mv('requires_unavailable_component', 'the sample case needs a component the fixed profile lacks'), 'annotations': {}},
    ]
    tests = [
        {'catalogue_id': 'T-SYN-test-1-00000001', 'title': 'synthetic_test_one', 'tier': 'TEST_IMPLEMENTATION', 'source': _src('synthetic/test_one.py', 'test_one'),
         'native_ids': ['synthetic/test_one.py::test_one'], 'aliases': [], 'raw_refs': ['SYN1:6', 'SYN1:7', 'SYN1:8'], 'lineage': [],
         'scenario_refs': ['S-SYN-case-1-00000001'], 'rule_refs': ['R-SYN-reg-b-00000002'], 'fixture_refs': ['F-SYN-fixture-1-00000001'],
         'parametrized_instance_count': 2, 'evidence_digest_refs': [],
         'mvp_applicability': _mv('mvp_fixed', 'the synthetic sample names this row as in profile'), 'annotations': {}},
    ]
    fixtures = [
        {'catalogue_id': 'F-SYN-fixture-1-00000001', 'title': 'synthetic fixture 1', 'tier': 'FIXTURE', 'source': _src('synthetic/fixture_1.json'),
         'native_ids': ['fixture-1'], 'aliases': [], 'raw_refs': ['SYN1:9', 'SYN2:1'], 'lineage': [],
         'fixture_identity': {'basis': 'content digest', 'content_sha256': _d('fixture-1-bytes')},
         'locations': [_src('synthetic/fixture_1.json'), _src('vendored/fixture_1.json')],
         'expected_outcome_verbatim': 'DIVERGES', 'evidence_digest_refs': [],
         'mvp_applicability': _mv('needs_migration', 'the sample fixture predates the current profile'), 'annotations': {}},
    ]
    evidence = [
        {'evidence_digest': _d('evidence-1'), 'raw_refs': ['SYN1:10'], 'tier': 'EXECUTION_EVIDENCE', 'evidence_kind': 'run_result',
         'run_id': 'synthetic-run-1', 'test_ref': 'T-SYN-test-1-00000001', 'scenario_ref': 'S-SYN-case-1-00000001',
         'historical_verdict_verbatim': 'FAIL',
         'source_commitment': {'set_id': 'SYN1', 'repo': REPO, 'revision': REV},
         'artifact_commitment': {'path': 'synthetic/run-1.json', 'record_digest': _d('evidence-1'), 'file_digest': 'not computed'},
         'current_qualification_effect': 'none', 'annotations': {}},
        {'evidence_digest': _d('evidence-2'), 'raw_refs': ['SYN2:0'], 'tier': 'EXECUTION_EVIDENCE', 'evidence_kind': 'validation_claim',
         'run_id': None, 'test_ref': None, 'scenario_ref': None, 'historical_verdict_verbatim': None,
         'source_commitment': {'set_id': 'SYN2', 'repo': REPO, 'revision': REV},
         'artifact_commitment': {'path': 'synthetic/CHANGELOG.md', 'record_digest': _d('evidence-2'), 'file_digest': 'not computed'},
         'current_qualification_effect': 'none', 'annotations': {}},
    ]
    X = 'SYN1'
    crosswalk = [
        _row(X, 0, 'rule-a', 'GOVERNANCE_RULE', 'CANONICAL', rules[0]['catalogue_id'], 'SYN-A'),
        _row(X, 1, 'rule-b', 'GOVERNANCE_RULE', 'CANONICAL', rules[1]['catalogue_id'], 'SYN-REG-1'),
        _row(X, 2, 'rule-a-legacy', 'GOVERNANCE_RULE', 'ALIAS_OF', rules[0]['catalogue_id'], 'SYN-A-legacy'),
        _row(X, 3, 'rev-b', 'RULE_REVISION', 'HISTORICAL_REVISION_OF', rules[1]['catalogue_id'], 'SYN-REG-1@earlier'),
        _row(X, 4, 'case-1', 'LOGICAL_SCENARIO', 'CANONICAL', scenarios[0]['catalogue_id'], 'SYN-CASE-1'),
        _row(X, 5, 'case-2', 'LOGICAL_SCENARIO', 'CANONICAL', scenarios[1]['catalogue_id'], 'SYN-CASE-2'),
        _row(X, 6, 'test-1', 'TEST_IMPLEMENTATION', 'CANONICAL', tests[0]['catalogue_id'], 'synthetic/test_one.py::test_one'),
        _row(X, 7, 'test-1-p1', 'PARAMETRIZED_INSTANCE', 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', tests[0]['catalogue_id']),
        _row(X, 8, 'test-1-p2', 'PARAMETRIZED_INSTANCE', 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', tests[0]['catalogue_id']),
        _row(X, 9, 'fixture-1', 'FIXTURE', 'CANONICAL', fixtures[0]['catalogue_id'], 'fixture-1'),
        _row(X, 10, 'evidence-1', 'EXECUTION_EVIDENCE', 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', evidence[0]['evidence_digest']),
        _row(X, 11, 'adjacent-1', 'RULE_ADJACENT', 'SOURCE_ONLY_ARTIFACT', None),
        _row(X, 12, 'unclear-1', 'LOGICAL_SCENARIO', 'UNRESOLVED', None, reason='the sample source gives no identity for this case'),
        _row('SYN2', 0, 'evidence-2', 'EXECUTION_EVIDENCE', 'TEST_INSTANCE_OR_EXECUTION_OCCURRENCE', evidence[1]['evidence_digest']),
        _row('SYN2', 1, 'fixture-1-copy', 'FIXTURE', 'ALIAS_OF', fixtures[0]['catalogue_id'], 'fixture-1'),
    ]
    return {
        'registry_version': '0.1.0', 'synthetic_sample': True,
        'source_inventory': [
            {'set_id': 'SYN1', 'description': 'synthetic raw set one', 'source_repo_revisions': [{'repo': REPO, 'revision': REV}]},
            {'set_id': 'SYN2', 'description': 'synthetic raw set two', 'source_repo_revisions': [{'repo': REPO, 'revision': REV}]}],
        'rules': rules, 'scenarios': scenarios, 'tests': tests, 'fixtures': fixtures, 'evidence': evidence,
        'crosswalk': crosswalk, 'registry_records': [record],
        'completeness_limitations': [
            'SYNTHETIC SAMPLE: invented content that exercises the tools; it is not the V0.1 corpus.',
            'The real partition outputs are loaded by a separate consolidation step and replace this sample.',
            'Informational catalogue only: non-authorizing, authority none, activates nothing, release and production remain on HOLD.',
            'Coverage rows are a derived projection of explicit links, not a qualification statement.'],
    }


def _rel(owner_source, field, to, override=None):
    if override:
        base = {'source': None, 'method': None, 'supporting_refs': [], 'confidence_class': None, 'missing_evidence': None}
        base.update(override)
        prov = override['provenance']
        base.pop('provenance', None)
    else:
        prov = 'SOURCE_STATED'
        base = {'source': {'repo': owner_source['repo'], 'revision': owner_source['revision'],
                           'location': '%s %s' % (owner_source['path'], owner_source['anchor'] or 'whole file')},
                'method': None, 'supporting_refs': [], 'confidence_class': None, 'missing_evidence': None}
    base.update({'field': field, 'to': to, 'provenance': prov, 'establishes_enforcement': False,
                 'establishes_test_coverage': False, 'establishes_qualification': False})
    return base


def with_relationships(layer, entry, overrides=None):
    """Sample helper: one explicit relationship record per declared reference (default SOURCE_STATED)."""
    overrides = overrides or {}
    src = entry['source'] if 'source' in entry else {'repo': entry['source_commitment']['repo'],
                                                    'revision': entry['source_commitment']['revision'],
                                                    'path': entry['artifact_commitment']['path'], 'anchor': None}
    entry['relationships'] = [_rel(src, f, t, overrides.get((f, t))) for f, t in V.ref_pairs(layer, entry)]
    return entry


def sample_dataset():
    d = _base_dataset()
    ra, rb = d['rules']
    c1, c2 = d['scenarios']
    t1 = d['tests'][0]
    f1 = d['fixtures'][0]
    ev1, ev2 = d['evidence']
    for layer in ('rules', 'scenarios', 'tests', 'fixtures'):
        for e in d[layer]:
            e['release_scope'] = 'v0_1'
    ra.update(normative_type='mandatory', adoption_status='unknown', test_refs=['T-SYN-test-1-00000001'])
    rb.update(normative_type='advisory', adoption_status='unknown')
    t1['scenario_refs'] = ['S-SYN-case-1-00000001', 'UNRESOLVED:no-scenario-registry:synthetic/test_one.py::test_one']
    for s_ in d['scenarios']:
        s_['scenario_class'] = 'logical'
    def _scn(cid, native, klass, raw, title):
        return {'catalogue_id': cid, 'title': title, 'tier': 'LOGICAL_SCENARIO', 'source': _src('synthetic/suite.md'), 'native_ids': [native],
                'aliases': [], 'raw_refs': [raw], 'lineage': [], 'rule_refs': [], 'test_refs': [], 'evidence_digest_refs': [],
                'expected_outcome_verbatim': 'NOT RUN', 'polarity': 'unknown', 'temporal_or_recovery_flag': False,
                'scenario_family': 'synthetic', 'refund_specific': None, 'release_scope': 'v0_1', 'scenario_class': klass,
                'mvp_applicability': _mv('unresolved', 'the sample source does not state profile membership'), 'annotations': {}}
    d['scenarios'] += [_scn('S-SYN-suite-1-00000003', 'SYN-SUITE-1', 'suite_level_acceptance', 'SYN1:14', 'Synthetic suite row'),
                       _scn('S-SYN-spec-1-00000004', 'SYN-SPEC-1', 'adversarial_or_unexecuted_spec', 'SYN1:15', 'Synthetic unexecuted specification')]
    d['rules'].append({'catalogue_id': 'R-SYN-reason-c-00000003', 'title': 'Synthetic reason code C', 'tier': 'GOVERNANCE_RULE',
                       'source': _src('synthetic/reasons.md', 'row C'), 'native_ids': ['SYN_REASON_C'], 'aliases': [], 'raw_refs': ['SYN1:13'],
                       'lineage': [], 'rule_ref': {'kind': 'source_statement', 'rule_id': 'SYN_REASON_C', 'version': None,
                       'rule_digest': V.canonical_digest({'statement': 'reason code C'}), 'registry_id': None, 'record_digest': None},
                       'statement_verbatim': 'SYN_REASON_C', 'refund_specific': None, 'release_scope': 'v0_1',
                       'normative_type': 'reason_code_or_refusal_vocabulary', 'adoption_status': 'unknown',
                       'mvp_applicability': _mv('unresolved', 'the sample source does not state profile membership'),
                       'scenario_refs': [], 'test_refs': [], 'evidence_digest_refs': [], 'annotations': {}})
    derived = {'provenance': 'DERIVED', 'method': 'exact-id match on test name', 'supporting_refs': ['T-SYN-test-1-00000001'], 'confidence_class': 'high'}
    unres = {'provenance': 'UNRESOLVED', 'missing_evidence': 'no scenario identity is stated for this test'}
    with_relationships('rules', ra, {('test_refs', 'T-SYN-test-1-00000001'): derived})
    for e in d['rules'][1:]:
        with_relationships('rules', e)
    for e in d['scenarios']:
        with_relationships('scenarios', e)
    with_relationships('tests', t1, {('scenario_refs', t1['scenario_refs'][1]): unres})
    with_relationships('fixtures', f1)
    with_relationships('evidence', ev1)
    with_relationships('evidence', ev2)
    cw = d['crosswalk']
    cw += [_row('SYN1', 13, 'reason-c', 'GOVERNANCE_RULE', 'CANONICAL', 'R-SYN-reason-c-00000003', 'SYN_REASON_C'),
           _row('SYN1', 14, 'suite-1', 'LOGICAL_SCENARIO', 'CANONICAL', 'S-SYN-suite-1-00000003', 'SYN-SUITE-1'),
           _row('SYN1', 15, 'spec-1', 'LOGICAL_SCENARIO', 'CANONICAL', 'S-SYN-spec-1-00000004', 'SYN-SPEC-1')]
    return d
