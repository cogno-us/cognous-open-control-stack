import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from deployment_review import RESPONSIBILITIES, VERSION, strict_json, validate

REVISION = 'a' * 40
NOW = '2026-10-08T01:00:00Z'


class DeploymentReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.lock = b'{"synthetic_lock":true}'
        self.configuration = b'{"synthetic_environment":true}'
        (self.root / 'configuration.json').write_bytes(self.configuration)
        (self.root / 'evidence.txt').write_text('Synthetic evidence; not a deployment observation.')
        self.scope = {
            'deployment_id': 'synthetic-pilot', 'environment_id': 'synthetic-host',
            'profile': 'ordinary-bounded', 'source_revision': REVISION,
            'component_lock_sha256': hashlib.sha256(self.lock).hexdigest(),
            'configuration_sha256': hashlib.sha256(self.configuration).hexdigest(),
        }
        self.packet = {key: value for key, value in self.scope.items() if key != 'configuration_sha256'}
        self.packet.update({
            'contract': VERSION,
            'configuration': {'path': 'configuration.json', 'sha256': self.scope['configuration_sha256']},
            'responsibilities': [{
                'id': identity, 'owner_ref': 'synthetic-owner', 'status': 'provided',
                'evidence': [{'file': {'path': 'evidence.txt', 'sha256': hashlib.sha256((self.root / 'evidence.txt').read_bytes()).hexdigest()},
                             'scope': copy.deepcopy(self.scope), 'observed_at': '2026-10-07T01:00:00Z',
                             'expires_at': '2026-10-09T01:00:00Z'}],
            } for identity in RESPONSIBILITIES],
        })

    def check(self):
        return validate(self.packet, self.root, self.lock, REVISION, NOW)

    def blocked(self, code):
        result = self.check()
        self.assertFalse(result['review_packet_complete'])
        self.assertIn(code, [e['code'] for e in result['errors']])
        self.assertFalse(result['authorizing'])
        return result

    def first(self):
        return self.packet['responsibilities'][0]

    def test_complete_synthetic_packet_never_grants_authority_or_assurance(self):
        result = self.check()
        self.assertTrue(result['review_packet_complete'])
        self.assertEqual(len(result['checked_responsibilities']), 10)
        for key in ('authorizing', 'production_ready', 'external_truth_verified',
                    'identity_verified', 'independent_review_verified'):
            self.assertIs(result[key], False)

    def test_missing_responsibility(self):
        self.packet['responsibilities'].pop()
        self.blocked('RESPONSIBILITY_SET_MISMATCH')

    def test_duplicate_responsibility_does_not_hide_missing_one(self):
        self.packet['responsibilities'][-1] = copy.deepcopy(self.first())
        self.blocked('RESPONSIBILITY_SET_MISMATCH')

    def test_unknown_responsibility(self):
        self.first()['id'] = 'other'
        self.blocked('RESPONSIBILITY_SET_MISMATCH')

    def test_missing_owner(self):
        self.first()['owner_ref'] = ''
        self.blocked('INVALID_LABEL')

    def test_missing_or_waived_evidence_cannot_pass(self):
        for status in ('missing', 'not_applicable', 'approved', True):
            with self.subTest(status=status):
                self.first()['status'] = status
                self.blocked('EVIDENCE_NOT_PROVIDED')

    def test_empty_evidence(self):
        self.first()['evidence'] = []
        self.blocked('INVALID_EVIDENCE_SET')

    def test_repeated_evidence_is_not_extra_coverage(self):
        self.first()['evidence'] *= 2
        self.blocked('DUPLICATE_EVIDENCE')

    def test_changed_configuration_bytes(self):
        (self.root / 'configuration.json').write_text('{}')
        self.blocked('CONTENT_DIGEST_MISMATCH')

    def test_recommitted_configuration_requires_fresh_evidence_scope(self):
        (self.root / 'configuration.json').write_text('{}')
        self.packet['configuration']['sha256'] = hashlib.sha256(b'{}').hexdigest()
        self.blocked('EVIDENCE_SCOPE_MISMATCH')

    def test_wrong_lock_or_revision(self):
        self.packet['component_lock_sha256'] = '0' * 64
        self.blocked('COMPONENT_LOCK_MISMATCH')
        self.packet['component_lock_sha256'] = self.scope['component_lock_sha256']
        self.packet['source_revision'] = 'b' * 40
        self.blocked('SOURCE_REVISION_MISMATCH')

    def test_scope_substitution(self):
        for key in self.scope:
            with self.subTest(key=key):
                self.first()['evidence'][0]['scope'][key] = 'substituted'
                self.blocked('EVIDENCE_SCOPE_MISMATCH')
                self.first()['evidence'][0]['scope'][key] = self.scope[key]

    def test_expiry_and_future_observation(self):
        item = self.first()['evidence'][0]
        item['expires_at'] = NOW
        self.blocked('EVIDENCE_NOT_CURRENT')
        item['expires_at'] = '2026-10-09T01:00:00Z'
        item['observed_at'] = '2026-10-08T01:00:01Z'
        self.blocked('EVIDENCE_NOT_CURRENT')

    def test_missing_timezone_and_invalid_calendar(self):
        for time in ('2026-10-07T01:00:00', '2026-02-30T00:00:00Z', True):
            self.first()['evidence'][0]['observed_at'] = time
            self.blocked('INVALID_TIME')

    def test_content_substitution_and_missing_file(self):
        (self.root / 'evidence.txt').write_text('Changed bytes')
        self.blocked('CONTENT_DIGEST_MISMATCH')
        (self.root / 'evidence.txt').unlink()
        self.blocked('MISSING_FILE')

    def test_empty_file_cannot_count_as_evidence(self):
        (self.root / 'evidence.txt').write_bytes(b'')
        self.first()['evidence'][0]['file']['sha256'] = hashlib.sha256(b'').hexdigest()
        self.blocked('EMPTY_FILE')

    def test_unsafe_paths(self):
        for path in ('../evidence.txt', '/etc/passwd', 'https://example.com/data', 'C:\\file', './evidence.txt'):
            with self.subTest(path=path):
                self.first()['evidence'][0]['file']['path'] = path
                self.blocked('INVALID_PATH')

    def test_symlink_reference_is_rejected(self):
        (self.root / 'alias.txt').symlink_to(self.root / 'evidence.txt')
        self.first()['evidence'][0]['file']['path'] = 'alias.txt'
        self.blocked('SYMLINK_NOT_ALLOWED')

    def test_unsupported_contract_and_unknown_fields(self):
        self.packet['contract'] = 'next'
        self.blocked('UNSUPPORTED_CONTRACT')
        self.packet['contract'] = VERSION
        self.packet['production_ready'] = True
        self.blocked('INVALID_FIELDS')

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_values(self):
        for data in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                strict_json(data)

    def test_cli_reports_failure_without_echoing_evidence_content(self):
        packet = self.root / 'packet.json'
        packet.write_text(json.dumps(self.packet))
        lock = self.root / 'lock.json'
        lock.write_bytes(self.lock)
        script = Path(__file__).resolve().parents[1] / 'tools/deployment_review.py'
        command = [sys.executable, str(script), str(packet), '--lock', str(lock),
                   '--expected-revision', REVISION, '--evaluated-at', NOW]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn('Synthetic evidence;', completed.stdout)
        packet.write_text('{"x":1,"x":2}')
        failed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 2)
        self.assertFalse(json.loads(failed.stdout)['production_ready'])


if __name__ == '__main__':
    unittest.main()
