"""Step 2.2 tree analysis: compare the current scanners and the N1-N4 analysis model on pinned checkouts.

Local and offline. Reads tracked files of exact-pinned local checkouts (git ls-files and rev-parse only),
runs the pure text functions of each scanner on the same file set, and runs each repository's own
claim-boundary CLI once per tree as a recorded observation (stdout, stderr, exit code). It alters no
allow-list, scanner or repository file, writes no file (output goes to stdout) and opens no network
connection. It imports third-party scanner modules from the given roots: use trusted pinned checkouts.
Non-authorizing; not a gate.

Usage: scanner_tree_analysis.py --verifier-root D --ergonomics-root D --hub-root D
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from tools import scanner_analysis_model as model  # noqa: E402
from tools import scanner_differential as sd  # noqa: E402

ALLOWLIST = 'scripts/claim_boundaries_allowlist.json'
BINARY = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.bmp', '.pdf', '.zip', '.gz', '.tgz', '.bz2', '.xz',
          '.whl', '.woff', '.woff2', '.ttf', '.otf', '.eot', '.pyc', '.so', '.db', '.sqlite', '.mp4', '.mov'}


def git(root, *args):
    return subprocess.run(['git', '--no-optional-locks', '-C', str(root), *args], check=True, capture_output=True).stdout


def tracked(root):
    return sorted(p for p in git(root, 'ls-files', '-z').decode().split('\0') if p)


def read_texts(root):
    skipped = []
    for rel in tracked(root):
        path = Path(root) / rel
        if rel == ALLOWLIST:
            skipped.append((rel, 'the scanner own allow-list (the scanners skip it)'))
            continue
        if path.suffix.lower() in BINARY or not path.is_file() or path.is_symlink():
            skipped.append((rel, 'binary_suffix_or_not_regular'))
            continue
        data = path.read_bytes()
        if b'\0' in data:
            skipped.append((rel, 'nul_bytes'))
            continue
        try:
            yield rel, data.decode('utf-8')
        except UnicodeDecodeError:
            skipped.append((rel, 'not_utf8'))
    yield None, skipped


def load_allowlist(root):
    path = Path(root) / 'scripts/claim_boundaries_allowlist.json'
    if not path.is_file():
        return {'excluded_paths': [], 'allowed': []}
    return json.loads(path.read_text(encoding='utf-8'))


def excluded(rel, allow):
    return any(rel == e['path'] or (e['path'].endswith('/') and rel.startswith(e['path'])) for e in allow['excluded_paths'])


def excused(f, allow):
    return any(e['path'] == f['path'] and e['rule'] == f['rule'] and e['line'] == f['text'] for e in allow['allowed'])


def cli(root):
    script = Path(root) / 'scripts/check_claim_boundaries.py'
    if not script.is_file():
        return None
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run([sys.executable, '-I', str(script), '--root', str(root)], capture_output=True, text=True,
                       env=env, cwd=str(root))
    return {'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}


def key(f):
    return (f['path'], f['line'], f['rule'])


def analyse(name, root, scanners, table):
    verifier, ergonomics, _ = scanners
    allow = load_allowlist(root)
    out = {'tree': name, 'revision': git(root, 'rev-parse', 'HEAD').decode().strip(),
           'dirty': bool(git(root, 'status', '--porcelain').strip()), 'cli': cli(root)}
    found = {'verifier': [], 'ergonomics': [], 'model': []}
    skipped = []
    files = 0
    for rel, text in read_texts(root):
        if rel is None:
            skipped = text
            break
        files += 1
        for label, fn in (('verifier', lambda: verifier.scan_text(rel, text)),
                          ('ergonomics', lambda: ergonomics.scan_text(rel, text)),
                          ('model', lambda: model.scan_text(rel, text, table=table, tag=ergonomics.TAG,
                                                            html_elements=ergonomics.HTML_ELEMENTS))):
            for f in fn():
                d = {'path': f.path, 'line': f.line, 'rule': f.rule, 'text': f.text,
                     'visibility': getattr(f, 'visibility', 'visible')}
                d['in_excluded_path'] = excluded(rel, allow)
                d['excused_by_allowlist'] = excused(d, allow)
                found[label].append(d)
    out['files_scanned'] = files
    out['files_skipped'] = [{'path': p, 'reason': r} for p, r in skipped]
    out['findings'] = found
    sets = {k: {key(f): f for f in v} for k, v in found.items()}

    def diff(a, b):
        return [sets[a][k] for k in sorted(set(sets[a]) - set(sets[b]))]

    out['comparison'] = {
        'model_added_vs_verifier': diff('model', 'verifier'), 'model_lost_vs_verifier': diff('verifier', 'model'),
        'model_added_vs_ergonomics': diff('model', 'ergonomics'), 'model_lost_vs_ergonomics': diff('ergonomics', 'model'),
        'verifier_only_vs_ergonomics': diff('verifier', 'ergonomics'), 'ergonomics_only_vs_verifier': diff('ergonomics', 'verifier'),
        'model_visibility_changed_vs_verifier': [
            {**sets['model'][k], 'verifier_visibility': 'visible'} for k in sorted(set(sets['model']) & set(sets['verifier']))
            if sets['model'][k]['visibility'] != 'visible'],
    }
    def stale(label):
        used = {(f['path'], f['rule'], f['text']) for f in found[label]}
        return [{'path': e['path'], 'rule': e['rule'], 'line': e['line'][:120]} for e in allow['allowed']
                if (e['path'], e['rule'], e['line']) not in used]

    out['stale_allowlist_entries'] = {k: stale(k) for k in found}
    out['counts'] = {k: {'raw': len(v), 'unexcused_outside_excluded': sum(1 for f in v if not f['in_excluded_path'] and not f['excused_by_allowlist'])}
                     for k, v in found.items()}
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verifier-root', required=True)
    parser.add_argument('--ergonomics-root', required=True)
    parser.add_argument('--hub-root', required=True)
    args = parser.parse_args()
    scanners = sd.load_scanners(args.verifier_root, args.ergonomics_root, args.hub_root)
    verifier, ergonomics, _ = scanners
    table = model.union_table(verifier.CONFUSABLES, ergonomics.LOOKALIKES)
    table[ord('σ')] = 'o'
    trees = [('verifier', args.verifier_root), ('ergonomics', args.ergonomics_root), ('hub', args.hub_root)]
    result = {'schema': 'ocs.scanner-tree-analysis/0', 'trees': [analyse(n, r, scanners, table) for n, r in trees]}
    print(json.dumps(result, ensure_ascii=False, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
