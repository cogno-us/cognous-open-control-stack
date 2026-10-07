import os
from pathlib import Path
import sys
import pytest
from tools.merged_chain_qualification import junit_passes, run

@pytest.mark.parametrize('content', [None, '<broken', '<testsuites/>', '<testsuite><testcase><skipped/></testcase></testsuite>', '<testsuite><testcase><failure/></testcase></testsuite>', '<testsuite><testcase><error/></testcase></testsuite>'])
def test_incomplete_or_failed_evidence_cannot_pass(tmp_path, content):
    path = tmp_path / 'result.xml'
    if content is not None:
        path.write_text(content)
    assert junit_passes(path)[0] is False


def test_collected_successful_cases_pass(tmp_path):
    path = tmp_path / 'result.xml'
    path.write_text('<testsuite><testcase name="real-case"/></testsuite>')
    assert junit_passes(path) == (True, {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0})


def test_timed_out_batch_returns_failure(tmp_path):
    code = run([sys.executable, '-c', 'import time; time.sleep(10)'], env=os.environ.copy(), log=tmp_path/'timeout.log', timeout=0.1)
    assert code == 124
    assert 'exceeded time limit' in (tmp_path/'timeout.log').read_text()
