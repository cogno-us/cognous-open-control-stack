"""Step 2.2: differential comparison of the claim and wording scanner copies (static, read-only).

Loads the pure text functions of the verifier and ergonomics claim-boundary scripts and the hub
collateral wording scanner from checked-out source and compares them on a frozen synthetic corpus.
It has no effect of its own: it runs no scanner CLI, scans no repository tree, writes no file and opens
no network connection. It does import third-party code from the given roots (module-level code and
imports of those scripts run), so the roots must be trusted, pinned checkouts; bytecode writing is
disabled while loading. It changes no scanner and classifies nothing: classification is a human record in
docs/program-v0.2/s04/2.2-scanner-reconciliation.md. Non-authorizing.

Usage: scanner_differential.py --verifier-root DIR --ergonomics-root DIR [--hub-root DIR] --corpus FILE
"""
import argparse
import importlib.util
import json
import sys
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True


def _load(name, path, extra_paths=()):
    for extra in extra_paths:
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_scanners(verifier_root, ergonomics_root, hub_root):
    verifier = _load('verifier_claims', Path(verifier_root) / 'scripts/check_claim_boundaries.py',
                     [Path(verifier_root) / 'src'])
    ergonomics = _load('ergonomics_claims', Path(ergonomics_root) / 'scripts/check_claim_boundaries.py',
                       [Path(ergonomics_root) / 'scripts'])
    hub = _load('hub_collateral', Path(hub_root) / 'tools/collateral_evidence_snapshot.py', [Path(hub_root)])
    return verifier, ergonomics, hub


def rules_of(module, text):
    return sorted({f.rule for f in module.scan_text('x', text)})


def lines_of(module, text):
    return sorted({(f.rule, f.line) for f in module.scan_text('x', text)})


def run_case(scanners, case):
    verifier, ergonomics, hub = scanners
    text = case['text']
    return {
        'id': case['id'],
        'group': case['group'],
        'verifier': rules_of(verifier, text),
        'ergonomics': rules_of(ergonomics, text),
        'hub_wording_findings': len(hub.boundary_wording_findings(text)),
        'verifier_lines': lines_of(verifier, text),
        'ergonomics_lines': lines_of(ergonomics, text),
    }


def fold_probe(scanners, chars):
    """Fold single characters through each copy's folding step; report disagreements."""
    verifier, ergonomics, hub = scanners
    out = []
    for ch in chars:
        v = verifier._fold_line(ch)
        e = ergonomics._normalise(ch)[0]
        h = hub.fold_text(ch)
        out.append({'char': ch, 'codepoint': 'U+%04X' % ord(ch), 'name': unicodedata.name(ch, '?'),
                    'verifier': v, 'ergonomics': e, 'hub': h})
    return out


def _chars(table):
    return sorted(chr(k) if isinstance(k, int) else k for k in table)


def table_keys(scanners):
    verifier, ergonomics, hub = scanners
    return {
        'verifier': _chars(verifier.CONFUSABLES),
        'ergonomics': _chars(ergonomics.LOOKALIKES),
        'hub': _chars(hub._LOOKALIKES),
    }


def compare(scanners, corpus):
    results = [run_case(scanners, c) for c in corpus['cases']]
    keys = table_keys(scanners)
    probe_chars = sorted(set(keys['verifier']) | set(keys['ergonomics']) | set(keys['hub']) | set(corpus.get('extra_fold_chars', [])))
    probe = fold_probe(scanners, probe_chars)
    return {
        'cases': results,
        'rule_disagreements': [r['id'] for r in results if r['verifier'] != r['ergonomics']],
        'line_disagreements': [r['id'] for r in results if r['verifier_lines'] != r['ergonomics_lines']],
        'table_key_counts': {k: len(v) for k, v in keys.items()},
        'fold_probe': [p for p in probe if len({p['verifier'], p['ergonomics'], p['hub']}) > 1],
        'fold_probe_size': len(probe),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verifier-root', required=True)
    parser.add_argument('--ergonomics-root', required=True)
    parser.add_argument('--hub-root', default='.')
    parser.add_argument('--corpus', required=True)
    args = parser.parse_args()
    corpus = json.loads(Path(args.corpus).read_text(encoding='utf-8'))
    scanners = load_scanners(args.verifier_root, args.ergonomics_root, args.hub_root)
    print(json.dumps(compare(scanners, corpus), ensure_ascii=False, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
