"""Scan 6 T1-6 and T2-1: bz2/xz trailing bytes, extended-header keys, directory modes and tar padding."""
import bz2
import copy
import gzip
import hashlib
import io
import lzma
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from tools.verify_candidate_archive import REQUIRED, SELECTION, verify

GOOD = '{"reference_release_authorized": false, "production_deployment_authorized": false}'


class ArchiveStructureTests(unittest.TestCase):
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

    def check(self, payload, name='a.tar'):
        archive = self.root / name
        archive.write_bytes(payload)
        return verify(archive, sha256=hashlib.sha256(payload).hexdigest(), revision=self.revision, repo=self.repo)

    def rebuild(self, change=None, global_headers=True):
        with tarfile.open(fileobj=io.BytesIO(self.tar)) as source:
            entries = [(copy.copy(m), source.extractfile(m).read() if m.isfile() else None) for m in source]
        for member, _ in entries:
            member.pax_headers = {}
        if change:
            change(entries)
        out = io.BytesIO()
        headers = {'comment': self.revision} if global_headers else None
        with tarfile.open(fileobj=out, mode='w', format=tarfile.PAX_FORMAT, pax_headers=headers) as target:
            for member, content in entries:
                target.addfile(member, io.BytesIO(content) if content is not None else None)
        return out.getvalue()

    # T1-6
    def test_bz2_and_xz_pass_when_clean(self):
        self.assertEqual(self.check(bz2.compress(self.tar), 'a.tar.bz2')['artifact_integrity'], 'PASS')
        self.assertEqual(self.check(lzma.compress(self.tar), 'a.tar.xz')['artifact_integrity'], 'PASS')

    def test_trailing_bytes_after_bz2_or_xz_stream_are_refused(self):
        cases = {
            'bz2-garbage': bz2.compress(self.tar) + b'x',
            'bz2-zeros': bz2.compress(self.tar) + b'\0' * 16,
            'bz2-second-stream': bz2.compress(self.tar) + bz2.compress(b'\0' * 1024),
            'xz-garbage': lzma.compress(self.tar) + b'x',
            'xz-padding': lzma.compress(self.tar) + b'\0' * 4,
            'xz-second-stream': lzma.compress(self.tar) + lzma.compress(b'\0' * 1024),
        }
        for name, payload in cases.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'after the end of the compressed stream'):
                self.check(payload, name)

    def test_truncated_bz2_or_xz_stream_is_refused(self):
        for name, payload in (('t.bz2', bz2.compress(self.tar)[:-8]), ('t.xz', lzma.compress(self.tar)[:-8])):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.check(payload, name)

    # T2-1
    def test_rebuilt_baseline_passes(self):
        self.assertEqual(self.check(self.rebuild())['artifact_integrity'], 'PASS')

    def test_pax_xattr_and_other_keys_are_refused(self):
        for key in ('SCHILY.xattr.user.evil', 'SCHILY.xattr.security.capability', 'mtime', 'uname', 'size', 'LIBARCHIVE.xattr.x'):
            def change(entries, key=key):
                entries[-1][0].pax_headers = {key: '1'}
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'extended header key not allowed'):
                self.check(self.rebuild(change))

    def test_pax_xattr_in_global_header_is_refused(self):
        payload = self.rebuild(global_headers=False)
        out = io.BytesIO()
        with tarfile.open(fileobj=io.BytesIO(payload)) as source:
            entries = [(copy.copy(m), source.extractfile(m).read() if m.isfile() else None) for m in source]
        with tarfile.open(fileobj=out, mode='w', format=tarfile.PAX_FORMAT,
                          pax_headers={'comment': self.revision, 'SCHILY.xattr.user.x': 'y'}) as target:
            for member, content in entries:
                target.addfile(member, io.BytesIO(content) if content is not None else None)
        with self.assertRaisesRegex(ValueError, 'extended header key not allowed'):
            self.check(out.getvalue())

    def test_comment_must_name_the_trusted_revision(self):
        def change(entries):
            entries[-1][0].pax_headers = {'comment': 'f' * 40}
        with self.assertRaisesRegex(ValueError, 'comment header'):
            self.check(self.rebuild(change))

    def test_gnu_long_name_extension_is_refused(self):
        out = io.BytesIO()
        with tarfile.open(fileobj=io.BytesIO(self.tar)) as source:
            entries = [(copy.copy(m), source.extractfile(m).read() if m.isfile() else None) for m in source]
        with tarfile.open(fileobj=out, mode='w', format=tarfile.GNU_FORMAT) as target:
            for member, content in entries:
                if member.name == 'README.md':
                    member.name = 'README.md' + '/' * 0 + 'x' * 120
                target.addfile(member, io.BytesIO(content) if content is not None else None)
        with self.assertRaisesRegex(ValueError, 'GNU or vendor'):
            self.check(out.getvalue())

    def test_directory_modes_are_bound(self):
        for mode in (0o4755, 0o2775, 0o1777, 0o000, 0o755 & ~0o100, 0o777):
            def change(entries, mode=mode):
                directory = next(m for m, _ in entries if m.isdir())
                directory.mode = mode
            with self.subTest(mode=oct(mode)), self.assertRaisesRegex(ValueError, 'directory mode'):
                self.check(self.rebuild(change))

    def test_ordinary_directory_modes_pass(self):
        for mode in (0o755, 0o775, 0o700):
            def change(entries, mode=mode):
                for member, _ in entries:
                    if member.isdir():
                        member.mode = mode
            with self.subTest(mode=oct(mode)):
                self.assertEqual(self.check(self.rebuild(change))['artifact_integrity'], 'PASS')

    def test_nonzero_padding_is_refused(self):
        with tarfile.open(fileobj=io.BytesIO(self.tar)) as source:
            member = next(m for m in source if m.isfile() and 0 < m.size < 500)
        for offset in (0, 100, 503 - member.size):
            data = bytearray(self.tar)
            data[member.offset_data + member.size + offset] = 0x41
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, 'padding is not zero'):
                self.check(bytes(data))

    def test_nonzero_padding_is_refused_inside_compressed_archives(self):
        with tarfile.open(fileobj=io.BytesIO(self.tar)) as source:
            member = next(m for m in source if m.isfile() and 0 < m.size < 500)
        data = bytearray(self.tar)
        data[member.offset_data + member.size] = 0x41
        for compress in (gzip.compress, bz2.compress, lzma.compress):
            with self.subTest(compress=compress.__module__), self.assertRaisesRegex(ValueError, 'padding is not zero'):
                self.check(compress(bytes(data)), 'p.tar.z')


if __name__ == '__main__':
    unittest.main()
