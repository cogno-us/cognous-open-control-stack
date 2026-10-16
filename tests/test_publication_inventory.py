"""Positive package reproduction and destructive negative controls in temporary roots."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('inventory', ROOT / 'tools/verify_publication_inventory.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
MANIFEST = ROOT / 'docs/releases/distribution-closeout-2026-10-15/manifest.json'


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        self.root.mkdir()
        self.m = dict(schema='cognous.publication-inventory/1',source_commit='a'*40,
            rights_acceptance='pending_accountable_review',reference_release_authorized=False,
            production_deployment_authorized=False,required_notices=['LICENSE'],
            external_components=[dict(redistributed=False,rights_accepted=False,licensing_state='unresolved')],
            excluded_files=[dict(path='excluded.pdf', source_commit='a'*40, sha256='0'*64, reason='excluded fixture')],files=[])
        for p,b in [('LICENSE',b'original notice'),('source.py',b'print(1)')]:
            (self.root/p).write_bytes(b)
            self.m['files'].append(dict(path=p,sha256=v.digest(b),source_commit='a'*40,
                licensing_state='evidence_verified',license_evidence=['LICENSE'],inclusion_rationale='fixture'))

    def refused(self):
        with self.assertRaises(v.InventoryError):
            v.verify_package(self.m,self.root)

    def test_positive_no_rights_acceptance(self):
        result=v.verify_package(self.m,self.root)
        self.assertEqual(result['file_count'],2)
        self.assertEqual(result['rights_acceptance'],'pending_accountable_review')
        self.assertFalse(result['reference_release_authorized'])

    def test_unlisted(self):
        (self.root/'extra').write_bytes(b'x');self.refused()

    def test_missing_listed(self):
        (self.root/'source.py').unlink();self.refused()

    def test_digest(self):
        (self.root/'source.py').write_bytes(b'changed');self.refused()

    def test_missing_notice(self):
        (self.root/'LICENSE').unlink();self.refused()

    def test_missing_notice_from_manifest(self):
        self.m['files']=self.m['files'][1:];self.refused()

    def test_excluded_on_disk(self):
        (self.root/'excluded.pdf').write_bytes(b'x');self.refused()

    def test_excluded_added_to_allowlist(self):
        row=copy.deepcopy(self.m['files'][1]);row['path']='excluded.pdf'
        self.m['files'].append(row);self.refused()

    def test_duplicate(self):
        self.m['files'].append(copy.deepcopy(self.m['files'][0]));self.refused()

    def test_case_duplicate(self):
        row=copy.deepcopy(self.m['files'][0]);row['path']='license'
        self.m['files'].append(row);self.refused()

    def test_unsafe_paths(self):
        for bad in ['../escape','/absolute','a/../../escape','a//b','a/./b','C:/file','a\\b','a\x00b','a\nb','']:
            with self.subTest(path=repr(bad)):
                with self.assertRaises(v.InventoryError):v.safe_path(bad)

    def test_symlink_file(self):
        (self.root/'source.py').unlink();(self.root/'source.py').symlink_to(self.root/'LICENSE');self.refused()

    def test_symlink_directory(self):
        (self.root/'escape').symlink_to(self.root.parent,target_is_directory=True);self.refused()

    def test_symlink_root(self):
        alias=self.root.parent/'alias';alias.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(v.InventoryError):v.verify_package(self.m,alias)

    def test_unresolved_included(self):
        self.m['files'][1]['licensing_state']='unresolved';self.refused()

    def test_unresolved_external_accepted(self):
        self.m['external_components'][0]['rights_accepted']=True;self.refused()

    def test_external_false_accepted_label(self):
        self.m['external_components'][0]['licensing_state']='accepted';self.refused()

    def test_external_redistributed(self):
        self.m['external_components'][0]['redistributed']=True;self.refused()

    def test_false_legal_signoff(self):
        self.m['rights_acceptance']='accepted';self.refused()

    def test_release_authorization(self):
        self.m['reference_release_authorized']=True;self.refused()

    def test_production_authorization(self):
        self.m['production_deployment_authorized']=True;self.refused()

    def test_unbound_evidence(self):
        self.m['files'][1]['license_evidence']=['absent-NOTICE'];self.refused()

    def test_source_revision_substitution(self):
        self.m['files'][1]['source_commit']='b'*40;self.refused()

    def test_duplicate_json_key(self):
        path=self.root.parent/'manifest.json';path.write_text('{"schema":1,"schema":2}')
        with self.assertRaises(v.InventoryError):v.load_manifest(path)

    def test_real_frozen_package(self):
        m=v.load_manifest(MANIFEST)
        package=self.root.parent/'real'
        result=v.build_package(m,ROOT,package)
        self.assertEqual(result['file_count'],len(m['files']))
        self.assertEqual(v.verify_package(m,package),result)
        with self.assertRaises(FileExistsError):v.build_package(m,ROOT,package)

    def test_source_partition_omission(self):
        m=v.load_manifest(MANIFEST);m['excluded_files'].pop()
        with self.assertRaises(v.InventoryError):v.verify_source(m,ROOT)

    def test_actual_source_digest_substitution(self):
        m=v.load_manifest(MANIFEST);m['files'][0]['sha256']='0'*64
        with self.assertRaises(v.InventoryError):v.verify_source(m,ROOT)


if __name__=='__main__':unittest.main()
