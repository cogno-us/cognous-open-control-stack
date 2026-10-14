from copy import deepcopy
import unittest
from reference_profiles.protocol_evaluation import preregister, blinded_outcomes, lock_scores, unblind


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.r=preregister(cases=['stable','change','held-stable','held-change','extra-change','extra-stable'],model='fixed-model-version',tools_digest='0'*64,budget=100,seed=42,false_positive_cost=2,false_negative_cost=5)
        self.rows=[]
        for run in self.r['plan']['allocation']:
            relevant='change' in run['case']
            self.rows.append(dict(id=run['id'],case=run['case'],observations=['curated-discriminator' if relevant else 'irrelevant-salience'],before_action=False,action=relevant,confidence_ppm=1000000 if relevant else 0,truth=relevant,relevant=relevant,held_out=run['case'].startswith('held')))
    def result(self, guesses=None):
        if guesses is None:guesses={x['id']:'off' for x in self.r['plan']['allocation']}
        return unblind(self.r,lock_scores(self.r,self.rows),guesses)
    def test_prp_nondiscriminating_observation_action_stable(self):
        self.assertEqual(self.result()['groups']['on']['nondiscriminating_stability'],1)
    def test_prp_discriminating_observation_action_changes(self):
        self.assertEqual(self.result()['groups']['on']['discriminating_action_change'],1)
    def test_prp_grader_blinding_check(self):
        r=self.result({x['id']:x['condition'] for x in self.r['plan']['allocation']})
        self.assertTrue(r['blinding_failed']);self.assertAlmostEqual(r['blinding_pvalue'],1/64)
    def test_chance_guess_does_not_establish_blinding_failure(self):
        r=self.result();self.assertFalse(r['blinding_failed']);self.assertEqual(r['blinding_guess_accuracy'],.5)
    def test_mechanism_transcript_excluded(self):
        self.rows[0]['transcript']='protocol on'
        with self.assertRaises(ValueError):blinded_outcomes(self.r,self.rows)
    def test_condition_label_excluded(self):
        self.rows[0]['condition']='on'
        with self.assertRaises(ValueError):blinded_outcomes(self.r,self.rows)
    def test_missing_pair_refused(self):
        with self.assertRaises(ValueError):blinded_outcomes(self.r,self.rows[:-1])
    def test_duplicate_run_refused(self):
        self.rows[-1]=self.rows[0]
        with self.assertRaises(ValueError):blinded_outcomes(self.r,self.rows)
    def test_preregistration_change_refused(self):
        self.r['plan']['budget']+=1
        with self.assertRaises(ValueError):lock_scores(self.r,self.rows)
    def test_scores_locked_before_unblinding(self):
        scores=lock_scores(self.r,self.rows);scores['scores'][0]['correct']=False
        with self.assertRaises(ValueError):unblind(self.r,scores,{x['id']:'off' for x in self.rows})
    def test_false_negative_cost_and_calibration(self):
        row=next(x for x in self.rows if x['truth']);row['action']=False;row['confidence_ppm']=0
        result=self.result();self.assertEqual(sum(x['error_cost'] for x in result['groups'].values()),5)
        self.assertGreater(sum(x['brier'] for x in result['groups'].values()),0)
    def test_no_model_effectiveness_claim(self):
        result=self.result();self.assertFalse(result['measured_effectiveness']);self.assertEqual(result['groups']['on']['held_out_accuracy'],1)
