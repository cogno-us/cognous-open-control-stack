#!/usr/bin/env python3
"""Control-removal probes in disposable copies; never edit the working sources."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MUTATIONS = (
    ('payload binding', 'reference_profiles/payload_disclosure.py', "if policy['binding'] != binding:", 'if False:',
     'DisclosureTests.test_permitted_recipient_does_not_permit_secret_payload'),
    ('revision floor', 'reference_profiles/resolver_revision_ledger.py', 'if old is not None and revision < old[0]:', 'if False:',
     'RevisionMemoryTests.test_restart_rejects_rollback'),
    ('trusted checkpoint', 'reference_profiles/context_journal.py', "if prefix_digest(events[:checkpoint['count']]) != checkpoint['sha256']:", 'if False:',
     'JournalTests.test_coherent_rewrite_fails_trusted_checkpoint'),
    ('tail coverage', 'reference_profiles/context_journal.py', 'if len(events) != expected_count:', 'if False:',
     'JournalTests.test_deleted_reordered_duplicate_and_truncated_records_fail'),
)


def main():
    for label, path, before, after, test in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix='research-control-removal-') as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT/'reference_profiles',root/'reference_profiles',ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy(ROOT/'tests/test_research_assurance.py',root/'test_research_assurance.py')
            source = root/path
            text = source.read_text()
            if text.count(before) != 1:
                raise RuntimeError('mutation target changed: '+label)
            source.write_text(text.replace(before,after))
            run = subprocess.run([sys.executable,'-m','unittest','test_research_assurance.'+test],cwd=root,capture_output=True,text=True,timeout=20)
            # A loader/import error is not successful detection of a removed control.
            if run.returncode != 1 or 'FAIL:' not in run.stderr or 'ERROR:' in run.stderr:
                print(run.stdout,run.stderr)
                raise RuntimeError('control removal was not detected: '+label)
            print('DETECTED: '+label)
    return 0


if __name__ == '__main__': raise SystemExit(main())
