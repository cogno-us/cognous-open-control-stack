import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('embedding',ROOT/'tools/verify_embedding_exposure.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class EmbeddingExposure(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        (self.root/'config.json').write_text('{"synthetic":true}')
        self.ref={'path':'config.json','sha256':hashlib.sha256((self.root/'config.json').read_bytes()).hexdigest()}
        self.packet={'contract':'embedding-exposure/1','source_revision':'a'*40,'component_lock_sha256':hashlib.sha256(b'lock').hexdigest(),'environment_id':'synthetic-only','configuration':self.ref,'surfaces':[{'id':i,'exposure':'local-only','authentication':'trusted-local-host','limits':{k:1 for k in m.LIMITS},'host_permissions':'no-host-effects','storage_bound':'no-durable-writes','evidence':[self.ref]} for i in m.SURFACES]}
    def check(self):return m.validate(self.packet,self.root,b'lock','a'*40)
    def test_complete_synthetic_declarations_never_verify_deployment(self):
        r=self.check();self.assertTrue(r['configuration_requirements_satisfied']);self.assertFalse(r['deployment_verified']);self.assertFalse(r['production_authorized'])
    def test_missing_actual_environment_and_configuration_hold(self):
        self.packet['environment_id']=None;self.packet['configuration']=None
        r=self.check();self.assertFalse(r['configuration_requirements_satisfied']);self.assertIn('DEPLOYMENT_CONFIGURATION_UNAVAILABLE',r['errors'])
    def test_bool_zero_negative_missing_limits_fail(self):
        for value in (True,0,-1,None):
            with self.subTest(value=value):
                self.packet['surfaces'][0]['limits']['predecode_bytes']=value;self.assertFalse(self.check()['configuration_requirements_satisfied'])
    def test_remote_unauthenticated_and_unverified_fail(self):
        for exposure in ('authenticated-remote','unverified'):
            self.packet['surfaces'][0].update(exposure=exposure,authentication='trusted-local-host')
            self.assertFalse(self.check()['configuration_requirements_satisfied'])
    def test_missing_storage_or_surface_cannot_pass(self):
        self.packet['surfaces'][0]['storage_bound']='unknown';self.assertFalse(self.check()['configuration_requirements_satisfied'])
        self.packet['surfaces'].pop();self.assertFalse(self.check()['configuration_requirements_satisfied'])
    def test_changed_or_escaping_configuration_fails(self):
        (self.root/'config.json').write_text('{}');self.assertFalse(self.check()['configuration_requirements_satisfied'])
        self.packet['configuration']={'path':'../escape','sha256':'0'*64};self.assertFalse(self.check()['configuration_requirements_satisfied'])
    def test_unestablished_host_permissions_fail(self):
        self.packet['surfaces'][0]['host_permissions']='unknown';self.assertFalse(self.check()['configuration_requirements_satisfied'])
    def test_wrong_source_or_lock_fails(self):
        self.packet['source_revision']='b'*40;self.assertFalse(self.check()['configuration_requirements_satisfied'])
        self.packet['source_revision']='a'*40;self.packet['component_lock_sha256']='0'*64;self.assertFalse(self.check()['configuration_requirements_satisfied'])

class ExistingPacketAdmission(unittest.TestCase):
    def test_existing_deployment_validator_handles_overdepth_without_crashing(self):
        from tools.deployment_review import validate
        packet=[];child=packet
        for _ in range(30):new=[];child.append(new);child=new
        r=validate(packet,Path('.'),b'lock','a'*40,'2026-10-15T00:00:00Z')
        self.assertFalse(r['review_packet_complete']);self.assertFalse(r['authorizing'])
