#!/usr/bin/env python3
"""Run isolated, explicitly scoped v1 reference extension demonstrations."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profile', choices=('governed-context', 'institutional-review', 'temporal-refund'), required=True)
    ap.add_argument('--results-dir', type=Path, required=True)
    ap.add_argument('--scenario', default='allowed')
    ap.add_argument('--execute', action='store_true', help=argparse.SUPPRESS)
    args = ap.parse_args()
    root = args.results_dir.resolve()
    if args.profile == 'temporal-refund':
        from reference_profiles.temporal_refund import SCENARIOS, run_trajectory
        if args.scenario not in SCENARIOS:
            ap.error('unsupported temporal scenario')
        if not args.execute:
            from tools.optional_execution_profile import prepare
            from tools.worker21_authority_effect_qualification import run
            work = ROOT / '.optional-work'
            work.mkdir(exist_ok=True)
            env, pins, lock_digest = prepare(work)
            if root.exists():
                raise FileExistsError(root)
            rec = run([sys.executable, str(Path(__file__).resolve()), '--execute', '--profile', args.profile,
                       '--scenario', args.scenario, '--results-dir', str(root)], env=env, timeout=90)
            if root.is_dir():
                (root / 'execution.log').write_text(rec['output'])
                (root / 'provenance.json').write_text(json.dumps({'tested_revisions': pins, 'component_lock_sha256': lock_digest, 'returncode': rec['returncode']}, indent=2))
            print(rec['output'])
            return rec['returncode']
        value = run_trajectory(root, ROOT / '.optional-work', args.scenario)
    else:
        if args.scenario != 'allowed':
            ap.error('scenario selection applies only to temporal-refund')
        root.mkdir(parents=True, exist_ok=False)
        if args.profile == 'governed-context':
            from reference_profiles.context_memory import ContextMemory
            store = ContextMemory(root / 'context.sqlite3', clock=lambda: 100)
            receipt = store.admit(item_id='synthetic:case', content='Synthetic refund context; no real customer data.',
                                  purposes=['refund-review'], recipients=['synthetic-reviewer'], obligations=['retain-provenance'],
                                  expires_at=200, source_ref='synthetic:source')
            received = []
            delivery = store.deliver('synthetic:case', purpose='refund-review', recipient='synthetic-reviewer',
                                     expected_generation=store.generation(), callback=lambda text: received.append(len(text)))
            store.revoke('synthetic:case')
            try:
                store.deliver('synthetic:case', purpose='refund-review', recipient='synthetic-reviewer',
                              expected_generation=store.generation(), callback=lambda _: None)
            except PermissionError:
                blocked = True
            else:
                blocked = False
            value = {'profile': 'governed-context/1', 'receipt': receipt, 'delivery': delivery,
                     'revoked_recall_blocked': blocked, 'qualified': bool(received) and blocked}
        else:
            from reference_profiles.institutional_review import InstitutionalReview
            store = InstitutionalReview(root / 'reviews.sqlite3', reviewers=['synthetic-owner'])
            a = store.record(scope='synthetic-refund', task='refund', evaluator='synthetic-evaluator', criteria_ref='synthetic:criteria',
                             period='synthetic:run', evidence_refs=['synthetic:evidence'], competence='supported', authority_validity='unknown',
                             boundary_compliance='supported', critical_incident=True)
            p = store.propose(assessment_id=a['id'], change='restore', rationale='Request competent review; no automatic restoration')
            r = store.decide(proposal_id=p['id'], reviewer='synthetic-owner', disposition='defer',
                             rationale='Deployment authority remains unverified', incident_dispositions={a['id']:'synthetic:incident-review'})
            value = {'profile': 'institutional-review/1', 'history': store.history(), 'review': r,
                     'qualified': r['body']['disposition'] == 'defer' and not r['runtime_grant_changed']}
        value.update(authorizing=False, production_ready=False, consumer_chain_qualified=False)
        (root / 'result.json').write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(value, indent=2))
    return 0 if value['qualified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
