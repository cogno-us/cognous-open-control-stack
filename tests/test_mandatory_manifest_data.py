"""Step 2.3 data tests: the itemized mandatory-check manifest instance.

Data tests are self-contained except the final integration test, which runs the real manifest through tools/mandatory_checks.py. Non-authorizing candidate data.
"""
import copy
import os
import re
import unittest

from tools import mandatory_checks as mc
from tools import registry_records as rr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'docs', 'program-v0.2', 's05', '2.3-mandatory-manifest.json')
MD_PATH = os.path.join(ROOT, 'docs', 'program-v0.2', 's05', '2.3-mandatory-manifest.md')

TOP = {'profile', 'schema_version', 'canonical_profile', 'manifest_id', 'digest', 'sources',
       'input_kinds', 'not_applicable_reasons', 'checks'}
SOURCE = {'source_id', 'repository', 'revision', 'path', 'lines', 'note'}
CHECK = {'check_id', 'kind', 'source_id', 'input_kind', 'evaluator_id', 'evaluator_version',
         'not_applicable_reasons'}
HEX40 = re.compile(r'^[0-9a-f]{40}$')
DIGEST = re.compile(r'^sha256:[0-9a-f]{64}$')
LINES = re.compile(r'^(\d+(-\d+)?)?$')
KINDS = ['authority_context', 'conflict', 'grant', 'identity', 'mandate', 'policy', 'role_mapping']
REASONS = ['no_items_in_record', 'no_journal_in_record']


def load():
    with open(PATH, 'rb') as fh:
        return rr.loads_strict(fh.read())


def is_text(v):
    return type(v) is str and bool(v.strip())


def strictly_sorted(values):
    return all(a < b for a, b in zip(values, values[1:]))


class ManifestData(unittest.TestCase):
    def setUp(self):
        self.m = load()

    def test_top_level_members_and_constants(self):
        m = self.m
        self.assertEqual(set(m), TOP)
        self.assertEqual(m['profile'], 'ocs-mandatory-manifest/0')
        self.assertEqual(m['schema_version'], 0)
        self.assertIs(type(m['schema_version']), int)
        self.assertEqual(m['canonical_profile'], 'rfc8785-jcs')
        self.assertTrue(is_text(m['manifest_id']))
        self.assertRegex(m['digest'], DIGEST)

    def test_digest_recomputes_and_detects_change(self):
        m = self.m
        self.assertEqual(rr.record_digest(m), m['digest'])
        changed = copy.deepcopy(m)
        changed['checks'][0]['evaluator_version'] += 1
        self.assertNotEqual(rr.record_digest(changed), m['digest'])

    def test_canonical_text_is_stable(self):
        m = self.m
        self.assertEqual(rr.loads_strict(rr.jcs_bytes(m)), m)

    def test_sources(self):
        ids = [s['source_id'] for s in self.m['sources']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(self.m['sources'])
        for s in self.m['sources']:
            self.assertEqual(set(s), SOURCE)
            for key in SOURCE:
                self.assertIs(type(s[key]), str)
            for key in ('source_id', 'repository', 'path', 'note'):
                self.assertTrue(is_text(s[key]), key)
            self.assertRegex(s['revision'], HEX40)
            self.assertRegex(s['lines'], LINES)
            if s['lines']:
                parts = [int(x) for x in s['lines'].split('-')]
                self.assertEqual(parts, sorted(parts))

    def test_one_revision_per_repository(self):
        by_repo = {}
        for s in self.m['sources']:
            by_repo.setdefault(s['repository'], set()).add(s['revision'])
        for repo, revs in by_repo.items():
            self.assertEqual(len(revs), 1, repo)

    def test_input_kinds_and_reasons_exact_sets(self):
        m = self.m
        self.assertEqual(m['input_kinds'], KINDS)
        self.assertEqual(m['not_applicable_reasons'], REASONS)
        for key in ('input_kinds', 'not_applicable_reasons'):
            self.assertTrue(strictly_sorted(m[key]))
            self.assertTrue(all(is_text(x) for x in m[key]))

    def test_checks_shape_sorted_unique(self):
        m = self.m
        ids = [c['check_id'] for c in m['checks']]
        self.assertTrue(strictly_sorted(ids))
        source_ids = {s['source_id'] for s in m['sources']}
        for c in m['checks']:
            self.assertEqual(set(c), CHECK)
            self.assertTrue(is_text(c['check_id']))
            self.assertIn(c['kind'], ('verifier_check', 'input_read'))
            self.assertIn(c['source_id'], source_ids)
            self.assertTrue(is_text(c['evaluator_id']))
            self.assertIs(type(c['evaluator_version']), int)
            self.assertGreaterEqual(c['evaluator_version'], 1)
            reasons = c['not_applicable_reasons']
            self.assertIs(type(reasons), list)
            self.assertTrue(strictly_sorted(reasons))
            self.assertTrue(set(reasons) <= set(m['not_applicable_reasons']))
            if c['kind'] == 'input_read':
                self.assertIn(c['input_kind'], m['input_kinds'])
            else:
                self.assertIsNone(c['input_kind'])

    def test_input_read_checks_one_per_kind(self):
        m = self.m
        reads = [c for c in m['checks'] if c['kind'] == 'input_read']
        self.assertEqual(sorted(c['input_kind'] for c in reads), KINDS)
        for c in reads:
            self.assertEqual(c['check_id'], 'input_read.' + c['input_kind'])
            self.assertEqual(c['not_applicable_reasons'], [])

    def test_verifier_check_counts_and_reasons(self):
        m = self.m
        vc = [c for c in m['checks'] if c['kind'] == 'verifier_check']
        self.assertEqual(len(vc), 51)
        self.assertEqual(len(m['checks']), 58)
        for c in vc:
            self.assertRegex(c['check_id'], r'^v[1-4]\.[a-z_-]+(\.[a-z_-]+)*$')
        # fallback ids used only when a group raises are not checks
        for fallback in ('v2.decisions', 'v2.identity', 'v4.ledger', 'v3.tier'):
            self.assertNotIn(fallback, {c['check_id'] for c in vc})
        journal_only = [c['check_id'] for c in vc if 'no_journal_in_record' in c['not_applicable_reasons']]
        self.assertEqual(journal_only, ['v2.lifecycle.journal_protocol'])
        with_items = [c['check_id'] for c in vc if 'no_items_in_record' in c['not_applicable_reasons']]
        self.assertEqual(len(with_items), 30)

    def test_evaluators_follow_convention(self):
        for c in self.m['checks']:
            self.assertRegex(c['evaluator_id'], r'^cognous-verify\.[a-z_]+$')
            self.assertEqual(c['evaluator_version'], 1)

    def test_sources_name_pinned_components_only(self):
        repos = {s['repository'] for s in self.m['sources']}
        self.assertEqual(repos, {'cogno-us/cognous-control-plane',
                                 'cogno-us/cognous-open-control-stack-verifier',
                                 'cogno-us/open-decision-evidence-standard'})

    def test_boundary_wording_in_md(self):
        with open(MD_PATH, encoding='utf-8') as fh:
            text = fh.read()
        for word in ('non-authorizing', 'HOLD', 'candidate', self.m['digest']):
            self.assertIn(word, text)


class NegativeShapes(unittest.TestCase):
    """The rules above must reject damaged copies (guards against vacuous assertions)."""

    def setUp(self):
        self.m = load()

    def test_unsorted_unique_checks_detected(self):
        ids = [c['check_id'] for c in self.m['checks']]
        self.assertFalse(strictly_sorted(list(reversed(ids))))
        self.assertFalse(strictly_sorted(ids + ids[:1]))

    def test_bad_revision_detected(self):
        self.assertIsNone(HEX40.match('0A41FAA9' + '0' * 32))
        self.assertIsNone(HEX40.match('0a41faa9'))

    def test_extra_member_changes_digest_only_if_redigested(self):
        m = copy.deepcopy(self.m)
        m['extra'] = 1
        self.assertNotEqual(set(m), TOP)
        self.assertEqual(rr.record_digest(m) == m['digest'], False)

    def test_unknown_reason_and_source_detected(self):
        m = copy.deepcopy(self.m)
        m['checks'][0]['not_applicable_reasons'] = ['nope']
        self.assertFalse(set(m['checks'][0]['not_applicable_reasons']) <= set(m['not_applicable_reasons']))
        m['checks'][0]['source_id'] = 'missing'
        self.assertNotIn('missing', {s['source_id'] for s in m['sources']})

    def test_duplicate_member_text_refused(self):
        with self.assertRaises(ValueError):
            rr.loads_strict(b'{"a":1,"a":2}')


class RealManifestThroughModule(unittest.TestCase):
    """Integration: the real manifest instance through the reference module (synthetic 2.1 record)."""

    def test_real_manifest_validates_and_is_complete_against_a_synthetic_record(self):
        m = load()
        self.assertEqual(mc.validate_manifest(m), m['digest'])
        self.assertEqual(mc.validate_manifest(m, pin=m['digest']), m['digest'])
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            mc.validate_manifest(m, pin='')
        self.assertEqual(ctx.exception.code, 'pin_mismatch')
        evaluators = sorted({(c['evaluator_id'], c['evaluator_version']) for c in m['checks']})
        record = dict(
            profile=rr.PROFILE, schema_version=0, registry_id='synthetic-2-3-integration',
            canonical_profile=rr.CANONICAL_PROFILE, digest='sha256:' + '0' * 64, epoch=1,
            predecessor=None,
            rule_table=[{'rule_id': c['check_id'], 'version': 1, 'class': 'synthetic',
                         'profile': 'synthetic', 'status': 'required',
                         'applicability': {'kind': 'always'}, 'evaluator_id': c['evaluator_id'],
                         'evaluator_version': c['evaluator_version'],
                         'failure_disposition': 'deny', 'missing_treatment': 'fail_closed',
                         'reason_code': 'R1', 'source_ref': 'src:synthetic'} for c in m['checks']],
            evaluators=[{'evaluator_id': e, 'version': v, 'qualification_ref': 'synthetic:test-only'}
                        for e, v in evaluators],
            reason_map={'R1': 'synthetic'}, source_refs=['src:synthetic'], issuer='synthetic-test')
        record['digest'] = rr.record_digest(record)
        executed = [{'check_id': c['check_id'], 'outcome': 'passed', 'reason': None,
                     'evaluator_id': c['evaluator_id'], 'evaluator_version': c['evaluator_version']}
                    for c in m['checks']]
        floor = [m['checks'][0]['check_id']]
        report = mc.check_completeness(m, record, executed, floor_check_ids=floor)
        self.assertTrue(report['complete'])
        self.assertEqual(report['manifest_digest'], m['digest'])
        self.assertEqual(report['counts'], {'passed': 58, 'failed': 0, 'not_applicable': 0, 'error': 0})
        self.assertEqual([c['check_id'] for c in report['checks']], [c['check_id'] for c in m['checks']])
        with self.assertRaises(mc.ManifestRefusal) as ctx:
            mc.check_completeness(m, record, executed[1:], floor_check_ids=floor)
        self.assertEqual(ctx.exception.code, 'skipped_mandatory_check')


if __name__ == '__main__':
    unittest.main()
