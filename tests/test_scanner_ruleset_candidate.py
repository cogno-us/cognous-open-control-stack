"""Consistency checks for the step 2.2 candidate scanner-rule data. Docs-data tests only.

The interpreter below is a test-local reference reading used to check that the declarative data
reproduces the analysis model's rules. It is not a scanner, not an evaluator and is wired into no gate.
"""
import json
import re
import unicodedata
import unittest
from pathlib import Path

from tools import registry_records as rr
from tools import scanner_analysis_model as m

ROOT = Path(__file__).resolve().parents[1]
S04 = ROOT / 'docs/program-v0.2/s04'
FIX = ROOT / 'fixtures/scanner-differential'
KINDS = {'boundary', 'literal', 'terms', 'separator', 'gap', 'optional'}
BOUNDARIES = {'word_boundary': r'\b', 'no_ascii_alnum_follows': r'(?![a-z0-9])'}
TAG = re.compile(r"</?([A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9._]+)*)(?=[\s/>])[^<>\n]*>")


def load(path):
    return rr.loads_strict(Path(path).read_text(encoding='utf-8'))


RULESET = load(S04 / '2.2-scanner-ruleset-candidate.json')
EXAMPLE = load(S04 / '2.2-scanner-registry-record-example.json')
BOUNDARY = load(FIX / 'boundary-cases.json')
CORPUS = load(FIX / 'corpus.json')
FP = load(FIX / 'ergonomics-fp-development-md-50.json')
TABLE = {ord(k): v for k, v in RULESET['normalization']['per_character']['table'].items()}
ELEMENTS = frozenset(RULESET['markup']['recognized_tags']['known_elements'])


def compile_elements(elements):
    out = []
    for el in elements:
        kind = el['kind']
        assert kind in KINDS, kind
        if kind == 'boundary':
            out.append(BOUNDARIES[el['name']])
        elif kind == 'literal':
            out.append(re.escape(el['value']))
        elif kind == 'terms':
            body = '(?:' + '|'.join(re.escape(x) for x in sorted(el['values'], key=lambda s: (-len(s), s))) + ')'
            out.append(body + ('?' if el.get('optional') else ''))
        elif kind == 'separator':
            assert el['name'] == 'separator_run'
            out.append(r'[\s\-_]*')
        elif kind == 'gap':
            assert el['charset'] == 'any_except_lf' and el['lazy'] is True
            out.append('.{0,%d}?' % el['max'])
        else:
            out.append('(?:' + compile_elements(el['elements']) + ')?')
    return ''.join(out)


def compile_rules(spec_rules):
    return {r['rule_id'].split('.', 1)[1]: re.compile('|'.join(compile_elements(a['elements']) for a in r['alternatives']))
            for r in spec_rules}


def normalised(text):
    return m.normalise(text, TABLE)[0]


class RulesetDataTests(unittest.TestCase):
    def test_digest_recomputes_and_profile_names(self):
        self.assertEqual(RULESET['digest'], rr.record_digest(RULESET))
        self.assertEqual((RULESET['profile'], RULESET['canonical_profile'], RULESET['schema_version']),
                         ('ocs-scanner-ruleset/0', 'rfc8785-jcs', 0))
        self.assertIn('not frozen', RULESET['status'])
        self.assertIn('HOLD', RULESET['status'])

    def test_data_is_declarative_only(self):
        ids = set()

        def walk(elements):
            for el in elements:
                self.assertIn(el['kind'], KINDS)
                if el['kind'] == 'boundary':
                    self.assertIn(el['name'], BOUNDARIES)
                if el['kind'] == 'literal':
                    self.assertRegex(el['value'], r'^[a-z0-9]+$')
                if el['kind'] == 'terms':
                    self.assertEqual(el['values'], sorted(el['values']))
                    for value in el['values']:
                        self.assertRegex(value, r'^[a-z0-9]+$')
                if el['kind'] == 'optional':
                    walk(el['elements'])

        for rule in RULESET['rules']:
            for alt in rule['alternatives']:
                self.assertNotIn((rule['rule_id'], alt['id']), ids)
                ids.add((rule['rule_id'], alt['id']))
                walk(alt['elements'])
        for entry in RULESET['deferred']:
            walk(entry['alternative']['elements'])
        self.assertEqual([r['rule_id'] for r in RULESET['rules']], sorted(r['rule_id'] for r in RULESET['rules']))

    def test_exact_members_orders_and_sorted_sets(self):
        self.assertEqual(set(RULESET), {'profile', 'schema_version', 'canonical_profile', 'ruleset_id', 'status', 'evaluator',
                                        'normalization', 'views', 'markup', 'rules', 'deferred', 'compatibility', 'digest'})
        self.assertEqual(RULESET['normalization']['order'],
                         ['html_entities', 'escaped_whitespace', 'pre_fold', 'nfkc', 'per_character'])
        self.assertEqual(RULESET['normalization']['per_character']['order'],
                         ['nfd', 'drop_invisible', 'casefold', 'dash_fold', 'table'])
        marks = RULESET['markup']['markdown_marks']
        self.assertEqual(marks, sorted(marks))
        self.assertEqual(RULESET['markup']['recognized_tags']['known_elements'],
                         sorted(RULESET['markup']['recognized_tags']['known_elements']))
        self.assertEqual(RULESET['normalization']['per_character']['dash_fold']['extra'],
                         sorted(RULESET['normalization']['per_character']['dash_fold']['extra']))
        keys = list(RULESET['normalization']['per_character']['table'])
        self.assertTrue(all(len(k) == 1 for k in keys))
        self.assertEqual(keys, sorted(keys))
        for rule in RULESET['rules']:
            ids = [a['id'] for a in rule['alternatives']]
            self.assertEqual(ids, sorted(ids))

    def test_element_member_sets_are_closed(self):
        allowed = {'boundary': {'kind', 'name'}, 'literal': {'kind', 'value'}, 'terms': {'kind', 'values', 'optional'},
                   'separator': {'kind', 'name'}, 'gap': {'kind', 'max', 'charset', 'lazy'}, 'optional': {'kind', 'elements'}}

        def walk(elements):
            for el in elements:
                self.assertLessEqual(set(el), allowed[el['kind']], el)
                if el['kind'] == 'optional':
                    walk(el['elements'])

        for rule in RULESET['rules']:
            for alt in rule['alternatives']:
                walk(alt['elements'])

    def test_compiled_data_matches_the_analysis_model_rules(self):
        compiled = compile_rules(RULESET['rules'])
        self.assertEqual(set(compiled), set(m.RULES))
        texts = [c['text'] for c in CORPUS['cases']] + [c['text'] for c in BOUNDARY['cases']]
        self.assertGreater(len(texts), 200)
        for text in texts:
            norm = normalised(text)
            for rule, pattern in m.RULES.items():
                self.assertEqual(bool(compiled[rule].search(norm)), bool(pattern.search(norm)), (rule, text))

    def test_deferred_safe_is_preserved_and_not_in_candidate(self):
        production = next(r for r in RULESET['rules'] if r['rule_id'] == 'scan.production-ready')
        first = next(a for a in production['alternatives'] if a['id'] == 'A')
        lead = next(e for e in first['elements'] if e['kind'] == 'terms')['values']
        self.assertEqual(len(lead), 6)
        second = [e['values'] for e in first['elements'] if e['kind'] == 'terms'][1]
        self.assertNotIn('safe', second)
        (entry,) = RULESET['deferred']
        self.assertEqual((entry['status'], entry['not_active']), ('deferred', True))
        deferred_terms = [e['values'] for e in entry['alternative']['elements'] if e['kind'] == 'terms']
        self.assertEqual(deferred_terms, [lead, ['safe']])
        self.assertEqual(entry['origin']['revision'], 'c0b8ba1f55b75db787a320f3de0f79342c6f6826')
        # The union with the deferred alternative equals the historical verifier word list.
        historical = re.compile(r"\b(?:production|prod|deployment|deploy|enterprise|audit)[\s\-_]*"
                                r"(?:ready|grade|quality|safe|worthy)(?![a-z0-9])")
        union = re.compile('|'.join([compile_elements(first['elements']), compile_elements(entry['alternative']['elements'])]))
        for lead_word in lead:
            for tail in ('ready', 'grade', 'quality', 'safe', 'worthy', 'fine', 'safer'):
                sample = f'{lead_word} {tail}'
                self.assertEqual(bool(union.search(sample)), bool(historical.search(sample)), sample)

    def test_table_keys_are_reachable_except_the_declared_one(self):
        pre = RULESET['normalization']['pre_fold']
        self.assertFalse(set(pre) & {chr(k) for k in TABLE})
        unreachable = {}
        for key, value in TABLE.items():
            ch = chr(key)
            self.assertRegex(value, r'^[a-z]$')
            out = ''.join(c for p in unicodedata.normalize('NFD', unicodedata.normalize('NFKC', ch))
                          if not m._invisible(p) for c in p.casefold())
            if out != ch:
                unreachable[ch] = out.translate(TABLE)
        self.assertEqual(unreachable, {'ё': 'e'})
        self.assertEqual(TABLE[ord('ё')], 'e')
        self.assertEqual(len(TABLE), 78)

    def test_registry_example_fits_2_1_without_change_and_refuses_unqualified(self):
        self.assertEqual(EXAMPLE['digest'], rr.record_digest(EXAMPLE))
        ref = f"ocs-scanner-ruleset/0@{RULESET['digest']}"
        self.assertIn(ref, EXAMPLE['source_refs'])
        self.assertEqual({r['rule_id'] for r in EXAMPLE['rule_table']}, {r['rule_id'] for r in RULESET['rules']})
        self.assertTrue(all(r['source_ref'] == ref for r in EXAMPLE['rule_table']))
        self.assertFalse(any('safe-suffix' in r['rule_id'] for r in EXAMPLE['rule_table']))
        with self.assertRaises(rr.RegistryRefusal) as cm:
            rr.validate_record(EXAMPLE, floor_mandatory_rule_ids=())
        self.assertEqual(cm.exception.code, 'unqualified_evaluator')


class BoundaryCaseTests(unittest.TestCase):
    def test_expected_values_match_the_model(self):
        ids = set()
        for case in BOUNDARY['cases']:
            self.assertNotIn(case['id'], ids)
            ids.add(case['id'])
            found = m.scan_text('c.txt', case['text'], table=TABLE, tag=TAG, html_elements=ELEMENTS)
            self.assertEqual(any(f.rule == 'production-ready' for f in found), case['candidate_expected'], case['id'])

    def test_terminator_differences_are_exactly_the_recorded_classes(self):
        by_alt = {}
        for case in BOUNDARY['cases']:
            tail = case['id'].split('-', 1)[1]
            if case['verifier_scan_text'] != case['ergonomics_scan_text']:
                by_alt.setdefault(case['alternative'], set()).add(tail)
        terminator = {'underscore-letter', 'underscore-end', 'cyrillic-unmapped', 'greek-unmapped', 'cjk', 'arabic-indic-digit'}
        other = {'escaped-newline', 'tag-after'}
        self.assertEqual(by_alt['A'], terminator | other)
        self.assertEqual(by_alt['B'], terminator | other)
        # Alternative C is absent from the ergonomics scanner (S-01), so every non-matching tail differs.
        self.assertTrue(terminator <= by_alt['C'])

    def test_not_universally_broader_end_to_end(self):
        cases = BOUNDARY['cases']
        self.assertTrue(any(c['verifier_scan_text'] and not c['ergonomics_scan_text'] for c in cases))
        self.assertTrue(any(c['ergonomics_scan_text'] and not c['verifier_scan_text'] for c in cases))

    def test_ascii_alnum_and_combining_negatives(self):
        expected = {c['id']: c['candidate_expected'] for c in BOUNDARY['cases']}
        for alt in 'ABC':
            for tail in ('ascii-digit', 'ascii-letters', 'uppercase-letters', 'cyrillic-mapped', 'fullwidth-digit',
                         'fullwidth-letter', 'precomposed-e-acute', 'combining-then-letter', 'zwj-then-letter',
                         'soft-hyphen-then-letter'):
                self.assertFalse(expected[f'{alt}-{tail}'], f'{alt}-{tail}')
            for tail in ('end-of-text', 'period', 'combining-on-last-letter', 'combining-then-period', 'underscore-end'):
                self.assertTrue(expected[f'{alt}-{tail}'], f'{alt}-{tail}')


class EntityCaseTests(unittest.TestCase):
    def test_entity_cases_match_the_model(self):
        cases = BOUNDARY['entity_cases']
        self.assertEqual(len(cases), 40)
        ids = [c['id'] for c in cases]
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            found = m.scan_text('c.txt', case['text'], table=TABLE, tag=TAG, html_elements=ELEMENTS)
            self.assertEqual(any(f.rule == case['rule'] for f in found), case['candidate_expected'], case['id'])

    def test_candidate_agrees_with_the_verifier_except_three_documented_non_entity_cases(self):
        differ = [c['id'] for c in BOUNDARY['entity_cases'] if c['verifier_scan_text'] != c['candidate_expected']]
        # N3 custom-tag stripping, N3 tag recognition after NFKC, N2 escaped whitespace after decoding
        self.assertEqual(differ, ['entity-decoded-tag-unknown', 'entity-decoded-backslash-n', 'entity-fullwidth-tag-numeric'])

    def test_semicolonless_references_decode_and_nesting_is_one_layer(self):
        expected = {c['id']: c['candidate_expected'] for c in BOUNDARY['entity_cases']}
        for cid in ('semicolonless-named-nbsp', 'semicolonless-named-amp', 'semicolonless-decimal', 'numeric-control-removed',
                    'numeric-del-removed', 'ambiguous-ampersand-not-it', 'numeric-zero-before-word'):
            self.assertTrue(expected['entity-' + cid], cid)
        for cid in ('semicolonless-hex-greedy', 'named-not-legacy-no-semicolon', 'nested-amp-numeric', 'nested-numeric-amp',
                    'nested-double-amp', 'malformed-hex-no-digits', 'malformed-numeric-no-digits', 'numeric-zero',
                    'ambiguous-ampersand-plain', 'malformed-unterminated-end', 'decoded-newline-in-gap',
                    'midword-zero', 'midword-out-of-range', 'midword-surrogate'):
            self.assertFalse(expected['entity-' + cid], cid)

    def test_entity_data_member_records_the_verifier_compatible_algorithm(self):
        entities = RULESET['normalization']['html_entities']
        self.assertEqual(set(entities), {'semantics', 'decodes', 'malformed', 'repetition', 'contexts', 'decoded_line_breaks', 'ordering'})
        self.assertIn('exactly once', entities['semantics'])
        self.assertIn('never decoded again', entities['repetition'])
        decisions = RULESET['compatibility']['candidate']['decisions']
        self.assertEqual(set(decisions), {'O-1', 'O-2'})

    def test_successor_expectation_differs_only_in_the_six_terminator_classes(self):
        six = {'underscore-letter', 'underscore-end', 'cyrillic-unmapped', 'greek-unmapped', 'cjk', 'arabic-indic-digit'}
        flipped = {c['id'].split('-', 1)[1] for c in BOUNDARY['cases'] if c['successor_expected'] != c['candidate_expected']}
        self.assertEqual(flipped, six)
        self.assertTrue(all(c['candidate_expected'] for c in BOUNDARY['cases'] if c['id'].split('-', 1)[1] in six))
        self.assertFalse(any(c['successor_expected'] for c in BOUNDARY['cases'] if c['id'].split('-', 1)[1] in six))


class FalsePositiveFixtureTests(unittest.TestCase):
    def test_fixture_is_preserved_and_reproduces(self):
        self.assertFalse(FP['allow_list_changed'])
        self.assertEqual(FP['source']['path'], 'docs/development.md')
        self.assertIn('attested', FP['line_text'])
        found = m.scan_text('docs/development.md', FP['line_text'], table=TABLE, tag=TAG, html_elements=ELEMENTS)
        self.assertEqual([(f.rule, f.line) for f in found], [('attested', 1)])
        self.assertEqual(FP['matches_measured_on_this_line_alone']['ergonomics_scan_text'], [])
        self.assertIn('Open', FP['disposition'])


if __name__ == '__main__':
    unittest.main()
