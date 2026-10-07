import importlib.util
import sys
from pathlib import Path

spec=importlib.util.spec_from_file_location('w21_runner',Path(__file__).resolve().parents[1]/'tools/worker21_authority_effect_qualification.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def test_missing_junit_cannot_pass(tmp_path):
    assert not r.passed_batch({'returncode':0},r.counts(tmp_path/'missing.xml'),7)

def test_required_skip_cannot_pass(tmp_path):
    p=tmp_path/'junit.xml';p.write_text('<testsuites><testsuite tests="7" skipped="1" failures="0" errors="0"/></testsuites>')
    assert not r.passed_batch({'returncode':0},r.counts(p),7)

def test_wrong_count_or_failed_process_cannot_pass():
    c=dict(tests=7,passed=7,failures=0,errors=0,skipped=0)
    assert r.passed_batch({'returncode':0},c,7)
    assert not r.passed_batch({'returncode':1},c,7)
    assert not r.passed_batch({'returncode':0},c,19)

def test_timeout_retains_output_and_nonzero_result():
    result=r.run([sys.executable,'-u','-c','import time; print("entered"); time.sleep(30)'],timeout=.5)
    assert result['returncode']==124
    assert 'entered' in result['output']
    assert 'terminated' in result['output']
