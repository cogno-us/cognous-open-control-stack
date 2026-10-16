"""Adversarial contract and distribution checks, using an isolated Git fixture."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from tools.check_contract_surfaces import PUBLISHED, check, exported_surfaces
from tools.verify_candidate_archive import REQUIRED, SELECTION, run_smoke, verify


class ContractDriftTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'published.json'

    def write(self, value):
        self.path.write_text(json.dumps(value))

    def test_published_matches_actual_validator_definitions(self):
        check(PUBLISHED)

    def test_missing_snapshot_fails(self):
        with self.assertRaises(OSError):
            check(self.path)

    def test_malformed_snapshot_fails(self):
        self.path.write_text('{')
        with self.assertRaises(ValueError):
            check(self.path)

    def test_duplicate_keys_fail(self):
        self.path.write_text('{"contracts":{},"contracts":{}}')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            check(self.path)

    def test_missing_extra_and_changed_contracts_fail(self):
        for mutation in ('missing', 'extra', 'changed'):
            with self.subTest(mutation=mutation):
                data = exported_surfaces()
                if mutation == 'missing':
                    data['contracts'].pop('semantic-handoff/1')
                elif mutation == 'extra':
                    data['contracts']['undeclared/1'] = {}
                else:
                    data['contracts']['semantic-handoff/1']['response_kinds'].append('implicit_allow')
                self.write(data)
                with self.assertRaises(ValueError):
                    check(self.path)

    def test_runtime_field_drift_fails(self):
        from tools import semantic_handoff_contract as handoff
        with patch.object(handoff, 'RESPONSE_FIELDS', handoff.RESPONSE_FIELDS | {'new_field'}):
            with self.assertRaises(ValueError):
                check(PUBLISHED)

    def test_runtime_status_drift_fails(self):
        from reference_profiles import resolver_assurance as resolver
        with patch.object(resolver, 'STATUSES', resolver.STATUSES | {'IMPLICIT_VALID'}):
            with self.assertRaises(ValueError):
                check(PUBLISHED)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        for name in REQUIRED | {'docs/releases/selected-notices/example/NOTICE'}:
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture\n')
        (self.repo / SELECTION).write_text(json.dumps(dict(reference_release_authorized=False,
                                                         production_deployment_authorized=False)))
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
        self.revision = self.git('rev-parse', 'HEAD').decode().strip()
        self.archive = self.root / 'candidate.tar'
        self.git('archive', '--format=tar', '-o', str(self.archive), self.revision)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.PIPE)

    def verify(self, **kwargs):
        return verify(self.archive, sha256=hashlib.sha256(self.archive.read_bytes()).hexdigest(),
                      revision=self.revision, repo=self.repo, **kwargs)

    def mutate(self, change):
        with tarfile.open(self.archive) as source:
            entries = [(copy.copy(m), source.extractfile(m).read() if m.isfile() else None) for m in source]
        entries = change(entries)
        with tarfile.open(self.archive, 'w') as target:
            for member, content in entries:
                target.addfile(member, io.BytesIO(content) if content is not None else None)

    def test_exact_archive_passes_without_authorization_or_smoke_claim(self):
        report = self.verify()
        self.assertEqual(report['artifact_integrity'], 'PASS')
        self.assertEqual(report['synthetic_smoke'], 'NOT_RUN')
        self.assertFalse(report['reference_release_authorized'])
        self.assertFalse(report['production_deployment_authorized'])

    def test_external_suite_requires_exact_identity(self):
        with self.assertRaisesRegex(ValueError, 'exact qualification'):
            self.verify(qualification_root=self.repo)
        with self.assertRaisesRegex(ValueError, 'revision mismatch'):
            self.verify(qualification_root=self.repo, qualification_revision='0'*40)

    def test_modified_external_suite_rejected(self):
        (self.repo/'README.md').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'modified tracked'):
            self.verify(qualification_root=self.repo, qualification_revision=self.revision)

    def test_untracked_shadow_in_external_suite_rejected(self):
        shadow = self.repo/'suites/cognous-open-control-stack/tools/argparse.py'
        shadow.parent.mkdir(parents=True)
        shadow.write_text('raise SystemExit(0)\n')
        with self.assertRaisesRegex(ValueError, 'untracked'):
            self.verify(qualification_root=self.repo, qualification_revision=self.revision)

    def test_ignored_file_in_external_suite_rejected(self):
        (self.repo/'.gitignore').write_text('*.pth\n')
        self.git('add', '.gitignore')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'ignore')
        self.revision = self.git('rev-parse', 'HEAD').decode().strip()
        (self.repo/'shadow.pth').write_text('import os\n')
        with self.assertRaisesRegex(ValueError, 'ignored'):
            self.verify(qualification_root=self.repo, qualification_revision=self.revision)

    def test_hidden_index_flags_in_external_suite_rejected(self):
        for flag in ('--skip-worktree', '--assume-unchanged'):
            with self.subTest(flag=flag):
                self.git('update-index', flag, 'README.md')
                (self.repo/'README.md').write_text('changed')
                with self.assertRaisesRegex(ValueError, 'skip-worktree or assume-unchanged'):
                    self.verify(qualification_root=self.repo, qualification_revision=self.revision)
                self.git('update-index', flag.replace('--', '--no-'), 'README.md')
                self.git('checkout', '--', 'README.md')

    def test_external_harness_runs_isolated(self):
        with patch('tools.verify_candidate_archive.subprocess.run') as run:
            run_smoke(str(self.root), self.repo)
        command = run.call_args.args[0]
        self.assertEqual(command[1], '-I')

    def test_bad_outer_checksum_fails(self):
        with self.assertRaisesRegex(ValueError, 'checksum'):
            verify(self.archive, sha256='0' * 64, revision=self.revision, repo=self.repo)

    def test_missing_notice_fails_even_with_recomputed_checksum(self):
        self.mutate(lambda entries: [(m, b) for m, b in entries if m.name != 'NOTICE'])
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.verify()

    def test_changed_payload_fails_even_with_recomputed_checksum(self):
        self.mutate(lambda entries: [(m, b'altered\n' if m.name == 'README.md' else b) for m, b in entries])
        with self.assertRaises(ValueError):
            self.verify()

    def test_extra_file_fails(self):
        self.mutate(lambda entries: entries + [(tarfile.TarInfo('unreviewed'), b'')])
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            self.verify()

    def test_duplicate_member_fails(self):
        self.mutate(lambda entries: entries + [next(x for x in entries if x[0].name == 'NOTICE')])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.verify()

    def test_path_traversal_fails_before_smoke(self):
        self.mutate(lambda entries: entries + [(tarfile.TarInfo('../escape'), b'')])
        with patch('tools.verify_candidate_archive.run_smoke') as run:
            with self.assertRaises(ValueError):
                self.verify(smoke=True)
            run.assert_not_called()
        self.assertFalse((self.root / 'escape').exists())

    def test_symlink_fails(self):
        def change(entries):
            for m, _ in entries:
                if m.name == 'README.md':
                    m.type = tarfile.SYMTYPE
                    m.linkname = '/etc/passwd'
            return entries
        self.mutate(change)
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            self.verify()

    def test_added_executable_mode_fails(self):
        def change(entries):
            for m, _ in entries:
                if m.name == 'README.md':
                    m.mode = 0o755
            return entries
        self.mutate(change)
        with self.assertRaisesRegex(ValueError, 'mode'):
            self.verify()

    def test_floating_ref_rejected(self):
        self.revision = 'HEAD'
        with self.assertRaisesRegex(ValueError, 'exact'):
            self.verify()

    def test_true_authorization_rejected_even_when_in_source(self):
        (self.repo / SELECTION).write_text(json.dumps(dict(reference_release_authorized=True,
                                                         production_deployment_authorized=False)))
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'bad authority')
        self.revision = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('archive', '--format=tar', '-o', str(self.archive), self.revision)
        with self.assertRaisesRegex(ValueError, 'false authorization'):
            self.verify()

    def test_smoke_failure_propagates(self):
        with patch('tools.verify_candidate_archive.run_smoke', side_effect=subprocess.CalledProcessError(1, 'smoke')):
            with self.assertRaises(subprocess.CalledProcessError):
                self.verify(smoke=True)


if __name__ == '__main__':
    unittest.main()
