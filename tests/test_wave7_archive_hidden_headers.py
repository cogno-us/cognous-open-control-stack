"""Wave 7 T1-A and T2-F: headers hidden in a non-regular member's 'data', and single-member gzip."""
import bz2
import gzip
import hashlib
import io
import lzma
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import verify_candidate_archive as vca
from tools.verify_candidate_archive import REQUIRED, SELECTION, verify

GOOD = '{"reference_release_authorized": false, "production_deployment_authorized": false}'


def seal(header):
    header = bytearray(header)
    header[148:156] = b' ' * 8
    header[148:156] = b'%06o\0 ' % sum(header)
    return bytes(header)


def block(name, kind, size, mode=0o644):
    info = tarfile.TarInfo(name)
    info.size = size
    info.mode = mode
    buf = bytearray(info.tobuf(tarfile.USTAR_FORMAT))[:512]
    buf[156:157] = kind
    return seal(buf)


def record(key, value):
    body = f' {key}={value}\n'.encode()
    length = len(body) + 1
    while len(str(length).encode() + body) != length:
        length += 1
    return str(length).encode() + body


def pad(data):
    return data + b'\0' * (-len(data) % 512)


class HiddenHeaderTests(unittest.TestCase):
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
        with tarfile.open(fileobj=io.BytesIO(self.tar)) as source:
            self.members = list(source)
        self.directory = next(m for m in self.members if m.isdir())
        self.following = self.members[self.members.index(self.directory) + 1]

    def check(self, payload, name='a.tar'):
        archive = self.root / name
        archive.write_bytes(payload)
        return verify(archive, sha256=hashlib.sha256(payload).hexdigest(), revision=self.revision, repo=self.repo)

    def smuggle(self, hidden, kind=b'5', name=None):
        """Replace the directory header by one of `kind` whose size covers `hidden`, then the hidden bytes."""
        start = self.directory.offset
        header = bytearray(self.tar[start:start + 512])
        header[124:136] = b'%011o\0' % len(hidden)
        header[156:157] = kind
        if name is not None:
            header[0:100] = name.ljust(100, b'\0')
        return self.tar[:start] + seal(header) + hidden + self.tar[start + 512:]

    def pax_mtime(self):
        data = record('mtime', '1')
        return block('PaxHeader', b'x', len(data)) + pad(data)

    def test_direct_pax_mtime_is_refused(self):
        payload = self.tar[:self.following.offset] + self.pax_mtime() + self.tar[self.following.offset:]
        with self.assertRaisesRegex(ValueError, 'key not allowed: mtime'):
            self.check(payload)

    def test_pax_hidden_in_directory_data_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'carries a data area'):
            self.check(self.smuggle(self.pax_mtime()))

    def test_pax_hidden_in_nul_type_directory_data_is_refused(self):
        name = self.directory.name.rstrip('/').encode() + b'/'
        with self.assertRaisesRegex(ValueError, 'carries a data area'):
            self.check(self.smuggle(self.pax_mtime(), kind=b'\0', name=name))

    def test_gnu_longname_hidden_in_directory_data_is_refused(self):
        name = self.following.name.encode() + b'\0'
        hidden = block('././@LongLink', b'L', len(name)) + pad(name)
        with self.assertRaisesRegex(ValueError, 'carries a data area'):
            self.check(self.smuggle(hidden))

    def test_gnu_longlink_and_sparse_hidden_in_directory_data_are_refused(self):
        link = b'x\0'
        for hidden in (block('././@LongLink', b'K', len(link)) + pad(link), block('sparse', b'S', 0)):
            with self.subTest(hidden=hidden[156:157]), self.assertRaisesRegex(ValueError, 'carries a data area'):
                self.check(self.smuggle(hidden))

    def test_other_non_regular_kinds_with_size_are_refused(self):
        hidden = self.pax_mtime()
        for kind in (b'1', b'2', b'3', b'4', b'5', b'6'):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'carries a data area'):
                self.check(self.smuggle(hidden, kind=kind))

    def test_unsupported_kind_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'unsupported tar member type'):
            self.check(self.smuggle(b'', kind=b'Z'))

    def test_clean_archive_still_passes_in_every_encoding(self):
        for name, payload in (('a.tar', self.tar), ('a.tgz', gzip.compress(self.tar)),
                              ('a.bz2', bz2.compress(self.tar)), ('a.xz', lzma.compress(self.tar))):
            with self.subTest(name=name):
                self.assertEqual(self.check(payload, name)['artifact_integrity'], 'PASS')

    def test_raw_pass_returns_member_start_offsets_matching_tarfile(self):
        offsets = vca.require_canonical_tar_headers(io.BytesIO(self.tar), self.revision)
        self.assertEqual(offsets, [m.offset for m in self.members])

    def test_offset_disagreement_is_refused(self):
        real = vca.require_canonical_tar_headers
        with mock.patch.object(vca, 'require_canonical_tar_headers',
                               lambda d, r: [o + 512 for o in real(d, r)]):
            with self.assertRaisesRegex(ValueError, 'offsets differ'):
                self.check(self.tar)

    def test_offset_count_disagreement_is_refused(self):
        real = vca.require_canonical_tar_headers
        with mock.patch.object(vca, 'require_canonical_tar_headers', lambda d, r: real(d, r)[:-1]):
            with self.assertRaisesRegex(ValueError, 'offsets differ'):
                self.check(self.tar)

    # T2-F
    def test_gzip_extra_bytes_are_refused_like_bz2_and_xz(self):
        cases = {
            'multi-member': gzip.compress(self.tar[:2048]) + gzip.compress(self.tar[2048:]),
            'trailing-zeros': gzip.compress(self.tar) + b'\0' * 16,
            'empty-member': gzip.compress(self.tar) + gzip.compress(b''),
            'garbage': gzip.compress(self.tar) + b'x',
        }
        for name, payload in cases.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'after the end of the compressed stream'):
                self.check(payload, name)

    def test_truncated_or_corrupt_gzip_is_refused(self):
        good = gzip.compress(self.tar)
        for name, payload in (('trunc', good[:-8]), ('crc', good[:-8] + b'\0' * 4 + good[-4:])):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.check(payload, name)


if __name__ == '__main__':
    unittest.main()
