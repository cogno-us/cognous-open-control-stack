"""Test the result oracle independently of each application implementation."""
from copy import deepcopy
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from tools.run_comparative_governance import evaluate, PLAN, run_case


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.cases={c['id']:c for c in json.loads(PLAN.read_text())['cases']}
        self.allow=[dict(status='accepted',command='c',request_digest='digest')]
        self.deny=[dict(status='denied',command='c',request_digest='digest')]
        self.effect=dict(id='effect',request='digest',payload='"synthetic"')
        self.event=dict(command='c',status='denied',reason='denied',request_digest='digest',at=100)

    def score(self,name,outputs,effects,events=None):
        return evaluate(self.cases[name],outputs,dict(effects=effects,events=events or []))

    def test_allowed_effect_passes(self):
        self.assertTrue(self.score('permitted',self.allow,[self.effect])['pass_case'])

    def test_missing_effect_fails_even_when_receipt_claims_success(self):
        r=self.score('permitted',self.allow,[])
        self.assertFalse(r['pass_case']);self.assertEqual(r['missing_effect_count'],1)

    def test_deny_with_effect_fails_even_with_durable_denial(self):
        r=self.score('changed_target',self.deny,[self.effect],[self.event])
        self.assertFalse(r['pass_case']);self.assertEqual(r['unexpected_effect_count'],1)

    def test_false_allow_detected_even_without_effect(self):
        r=self.score('changed_target',self.allow,[])
        self.assertFalse(r['pass_case']);self.assertEqual(r['false_allows'],1)

    def test_false_block_detected(self):
        r=self.score('permitted',self.deny,[],[self.event])
        self.assertFalse(r['pass_case']);self.assertEqual(r['false_blocks'],1)

    def test_missing_denial_evidence_fails(self):
        self.assertFalse(self.score('changed_target',self.deny,[])['pass_case'])

    def test_unrelated_denial_evidence_does_not_count(self):
        event=dict(self.event,command='another')
        self.assertFalse(self.score('changed_target',self.deny,[],[event])['pass_case'])

    def test_wrong_request_digest_does_not_count(self):
        self.assertFalse(self.score('changed_target',self.deny,[],[dict(self.event,request_digest='wrong')])['pass_case'])

    def test_incomplete_denial_evidence_fails(self):
        for key in ('reason','request_digest','at'):
            event=deepcopy(self.event);del event[key]
            with self.subTest(key=key):self.assertFalse(self.score('changed_target',self.deny,[],[event])['pass_case'])

    def test_wrong_effect_identity_fails(self):
        self.assertFalse(self.score('permitted',self.allow,[dict(self.effect,id='wrong')])['pass_case'])

    def test_wrong_effect_payload_fails(self):
        self.assertFalse(self.score('permitted',self.allow,[dict(self.effect,payload='"other"')])['pass_case'])

    def test_duplicate_effect_fails(self):
        self.assertFalse(self.score('lost_ack_restart',self.allow*2,[self.effect,self.effect])['pass_case'])

    def test_concurrency_ignores_return_order_only(self):
        outputs=[dict(status='denied',command='c',request_digest='digest'),dict(status='accepted',command='d',request_digest='other')]
        self.assertTrue(self.score('concurrent_last_budget',outputs,[dict(self.effect,id='parallel-1')],[self.event])['pass_case'])
        self.assertTrue(self.score('concurrent_last_budget',outputs[::-1],[dict(self.effect,id='parallel-1')],[self.event])['pass_case'])

    def test_truncated_outcomes_fail(self):
        self.assertFalse(self.score('lost_ack_restart',self.allow,[self.effect])['pass_case'])

    def test_non_audit_database_error_is_not_an_expected_outage(self):
        import sqlite3
        class Broken:
            def __init__(self,*a):pass
            def request(self,*a):return {'body':{'id':'c'}}
            def apply(self,*a):raise sqlite3.IntegrityError('unexpected schema defect')
        with self.assertRaises(sqlite3.IntegrityError):
            run_case(Broken,self.cases['permitted'],Path('/unused'),'unused')


class CornerInjectionTests(unittest.TestCase):
    def test_substitution_distinguishes_outer_signature_and_verifier_binding(self):
        from benchmarks.governance.adapters import Cognous
        plan=json.loads(PLAN.with_name('corner-plan.json').read_text())
        cases={c['id']:c for c in plan['cases']}
        with tempfile.TemporaryDirectory() as directory:
            for name,reason in [('payload_changed_after_verification','VERIFIER_BINDING'),
                                ('payload_changed_without_resigning','SIGNATURE_INVALID')]:
                row=run_case(Cognous,cases[name],Path(directory)/name,'unused')
                self.assertTrue(row['pass_case'])
                self.assertEqual(row['outputs'][0]['reason'],reason)

    def test_schema_denial_retains_command_correlation(self):
        from benchmarks.governance.adapters import Cognous
        plan=json.loads(PLAN.with_name('corner-plan.json').read_text())
        case=next(c for c in plan['cases'] if c['id']=='unknown_body_field')
        with tempfile.TemporaryDirectory() as directory:
            row=run_case(Cognous,case,Path(directory)/'destination','unused')
            self.assertTrue(row['decision_conformance'])
            self.assertTrue(row['destination_conformance'])
            self.assertTrue(row['pass_case'])
            self.assertEqual(row['durably_recorded_denials'],1)


if __name__=='__main__':unittest.main()
