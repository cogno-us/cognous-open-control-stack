"""D-H2: the archive verifier reads the selection through the strict bounded loader."""
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.verify_candidate_archive import REQUIRED, SELECTION, verify

GOOD = '{"reference_release_authorized": false, "production_deployment_authorized": false}'


class StrictSelectionTests(unittest.TestCase):
    def build(self, selection_text):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        repo = root / 'repo'
        repo.mkdir()
        for name in REQUIRED | {'docs/releases/selected-notices/example/NOTICE'}:
            path = repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture\n')
        (repo / SELECTION).write_text(selection_text)
        git = lambda *a: subprocess.check_output(['git', '-C', str(repo), *a], stderr=subprocess.PIPE)
        git('init', '-q')
        git('add', '.')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
        revision = git('rev-parse', 'HEAD').decode().strip()
        archive = root / 'candidate.tar'
        git('archive', '--format=tar', '-o', str(archive), revision)
        return verify(archive, sha256=hashlib.sha256(archive.read_bytes()).hexdigest(), revision=revision, repo=repo)

    def test_strict_selection_passes(self):
        self.assertEqual(self.build(GOOD)['artifact_integrity'], 'PASS')

    def test_duplicate_member_is_refused(self):
        text = '{"reference_release_authorized": true, "reference_release_authorized": false, "production_deployment_authorized": false}'
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.build(text)

    def test_nonfinite_value_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            self.build('{"reference_release_authorized": false, "production_deployment_authorized": false, "x": NaN}')

    def test_non_object_root_is_a_typed_failure(self):
        for text in ('[]', '"x"', 'null', '1'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'must be a JSON object'):
                self.build(text)

    def test_malformed_json_is_a_typed_failure(self):
        with self.assertRaisesRegex(ValueError, 'bounded strict JSON'):
            self.build('{')


if __name__ == '__main__':
    unittest.main()
