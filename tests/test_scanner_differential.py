import json
import types
import unittest
from pathlib import Path

from tools import scanner_differential as sd

ROOT = Path(__file__).resolve().parents[1]


class Finding:
    def __init__(self, rule, line):
        self.rule, self.line = rule, line


def fake(rules_by_text, fold=None):
    mod = types.SimpleNamespace()
    mod.scan_text = lambda path, text: [Finding(r, 1) for r in rules_by_text.get(text, [])]
    mod._fold_line = (lambda ch: (fold or {}).get(ch, ch))
    mod._normalise = (lambda ch: ((fold or {}).get(ch, ch), [1]))
    mod.fold_text = lambda ch: (fold or {}).get(ch, ch)
    mod.boundary_wording_findings = lambda text: []
    mod.CONFUSABLES = {'a': 'a'}
    mod.LOOKALIKES = {'a': 'a'}
    mod._LOOKALIKES = {ord('a'): 'a'}
    return mod


class DifferentialTests(unittest.TestCase):
    def test_corpus_is_frozen_synthetic_and_unique(self):
        corpus = json.loads((ROOT / 'fixtures/scanner-differential/corpus.json').read_text(encoding='utf-8'))
        ids = [c['id'] for c in corpus['cases']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(set(c) == {'group', 'id', 'text'} for c in corpus['cases']))

    def test_disagreements_are_reported_not_hidden(self):
        corpus = {'cases': [{'group': 'g', 'id': 'g-0', 'text': 'x'}, {'group': 'g', 'id': 'g-1', 'text': 'y'}]}
        v = fake({'x': ['certified']})
        e = fake({'x': [], 'y': []})
        out = sd.compare((v, e, fake({})), corpus)
        self.assertEqual(out['rule_disagreements'], ['g-0'])
        self.assertEqual(out['line_disagreements'], ['g-0'])

    def test_fold_probe_flags_differing_fold(self):
        corpus = {'cases': [], 'extra_fold_chars': ['q']}
        out = sd.compare((fake({}, {'q': 'q'}), fake({}, {'q': 'k'}), fake({})), corpus)
        self.assertEqual([p['char'] for p in out['fold_probe']], ['q'])

    def test_results_file_matches_corpus_size(self):
        corpus = json.loads((ROOT / 'fixtures/scanner-differential/corpus.json').read_text(encoding='utf-8'))
        results = json.loads((ROOT / 'docs/program-v0.2/s04/2.2-differential-results.json').read_text(encoding='utf-8'))
        self.assertEqual([c['id'] for c in results['cases']], [c['id'] for c in corpus['cases']])
        self.assertEqual(results['table_key_counts'], {'ergonomics': 77, 'hub': 67, 'verifier': 76})


if __name__ == '__main__':
    unittest.main()
