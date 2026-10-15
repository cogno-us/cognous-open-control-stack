#!/usr/bin/env python3
"""Fail when hosted actions are mutable or release dependencies lose hash locks."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def check():
 for path in (ROOT/'.github/workflows').glob('*.yml'):
  for line in path.read_text().splitlines():
   match=re.search(r'\buses:\s+([^\s#]+)',line)
   if match:
    action=match[1]
    if not action.startswith('./') and not re.fullmatch(r'[\w./-]+@[0-9a-f]{40}',action):
     raise ValueError('mutable action in '+str(path.relative_to(ROOT)))
 text=(ROOT/'tools/requirements-release.lock').read_text()
 entries=re.split(r'\n(?=[a-zA-Z0-9])',text)
 for entry in entries:
  if entry.startswith('#'):entry='\n'.join(l for l in entry.splitlines() if not l.startswith('#')).strip()
  if entry and ('==' not in entry or '--hash=sha256:' not in entry):raise ValueError('unlocked release dependency')
 runner=(ROOT/'tools/reference_release.py').read_text()
 if '"--require-hashes"' not in runner:raise ValueError('release dependency hash enforcement missing')
 if 'summary["release_qualified"]=False' not in runner:raise ValueError('execution must not grant release authorization')
 print('Immutable action refs, hashed release dependencies and non-authorizing execution: PASS')
if __name__=='__main__':check()
