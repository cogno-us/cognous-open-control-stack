"""Scan 5 F-T2-3: gzip candidate archives verify, and data after the tar end marker is refused."""
import gzip
import hashlib
import io
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from tools.verify_candidate_archive import REQUIRED, SELECTION, verify

GOOD = '{"reference_release_authorized": false, "production_deployment_authorized": false}'


class ArchiveFormatTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        for name in REQUIRED | {'docs/releases/selected-notices/example/NOTICE'}:
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture\n')
        (self.repo / SELECTION).write_text(GOOD)
        git = lambda *a: subprocess.check_output(['git', '-C', str(self.repo), *a], stderr=subprocess.PIPE)
        git('init', '-q')
        git('add', '.')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
        self.revision = git('rev-parse', 'HEAD').decode().strip()
        self.tar = git('archive', '--format=tar', self.revision)

    def check(self, payload, name):
        archive = self.root / name
        archive.write_bytes(payload)
        return verify(archive, sha256=hashlib.sha256(payload).hexdigest(), revision=self.revision, repo=self.repo)

    def second_tar(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w') as bundle:
            info = tarfile.TarInfo('evil/backdoor.py')
            info.size = 4
            bundle.addfile(info, io.BytesIO(b'evil'))
        return buffer.getvalue()

    def test_plain_tar_passes(self):
        self.assertEqual(self.check(self.tar, 'a.tar')['artifact_integrity'], 'PASS')

    def test_gzip_tar_passes_instead_of_raising_typeerror(self):
        self.assertEqual(self.check(gzip.compress(self.tar), 'a.tar.gz')['artifact_integrity'], 'PASS')

    def test_second_tar_after_the_end_marker_is_refused(self):
        for name, payload in (('a.tar', self.tar + self.second_tar()), ('a.tar.gz', gzip.compress(self.tar + self.second_tar()))):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'after the end-of-archive marker'):
                self.check(payload, name)

    def test_trailing_garbage_byte_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'after the end-of-archive marker'):
            self.check(self.tar + b'\0' * 4096 + b'x', 'a.tar')

    def test_zero_padding_is_accepted(self):
        self.assertEqual(self.check(self.tar + b'\0' * 20480, 'a.tar')['artifact_integrity'], 'PASS')


if __name__ == '__main__':
    unittest.main()
