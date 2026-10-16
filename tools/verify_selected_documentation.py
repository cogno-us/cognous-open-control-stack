"""Check current architecture links against the selected lock, not history.

Historical reports and explicitly separate candidate manifests are outside this
selected-entry-page check. This performs no network requests or authorization.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    lock=json.loads((root/'component-lock.json').read_text())
    selected={spec['repository']:(spec.get('sha') or spec['accepted_sha'])
              for spec in lock['components'].values()}
    architecture=(root/'docs/architecture.md').read_text()
    current=architecture.split('## Component responsibilities',1)[1].split('\n## ',1)[0]
    checked=0
    for owner,sha in re.findall(r'https://github\.com/([^/\s)]+/[^/\s)]+)/(?:tree|blob)/([0-9a-f]{40})(?:[/\s)]|$)',current):
        if owner not in selected or sha != selected[owner]:
            raise ValueError('Selected architecture link differs from lock: '+owner+'@'+sha)
        checked+=1
    if not checked:
        raise ValueError('Selected architecture must retain a revision-specific implementation link')
    index=(root/'docs/evidence-index.md').read_text()
    if 'https://github.com/cogno-us/cognous-stack-orchestrator/issues/30' in index:
        raise ValueError('Public evidence entry must use the public operational trust status')
    if not re.search(r'\[[^\]]+\]\(operational-trust-status\.md\)',index):
        raise ValueError('Missing public trust status evidence link')
    # Check local navigation on the three current entry surfaces only. Historical
    # reports have independent source scope and are not rewritten by this check.
    for name in ('docs/evidence-index.md','docs/architecture.md','docs/operational-trust-status.md'):
        path=root/name
        for target in re.findall(r'\]\(([^\s)]+)\)',path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            candidate = path.parent/target.split('#',1)[0]
            if (not candidate.resolve().is_relative_to(root.resolve())
                    or any(part.is_symlink() for part in (candidate, *candidate.parents) if part != root.parent)
                    or not candidate.resolve().exists()):
                raise ValueError('Broken local navigation: '+name+' -> '+target)
    return {'selected_revision_links_checked':checked,'network_checked':False,'authorizing':False}


if __name__=='__main__':
    print(json.dumps(verify(),sort_keys=True))
