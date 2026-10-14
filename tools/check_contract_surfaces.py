#!/usr/bin/env python3
"""Compare published structural contracts with definitions used by validators."""
import argparse
from dataclasses import fields
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import semantic_handoff_contract as handoff
from reference_profiles import resolver_assurance as resolver

PUBLISHED = ROOT / 'contracts/qualification-surfaces-v1.json'


def exported_surfaces():
    return {
        'format': 'cognous.qualification-surfaces/1',
        'scope': 'structural field sets and enums only; not full schemas or authorization',
        'contracts': {
            handoff.PROFILE: {
                'proposal_fields': sorted(handoff.CONTRACT_FIELDS),
                'text_fields': sorted(handoff.TEXT_FIELDS),
                'list_fields': sorted(handoff.LIST_FIELDS),
                'term_fields': sorted(handoff.TERM_FIELDS),
                'response_fields': sorted(handoff.RESPONSE_FIELDS),
                'response_kinds': sorted(handoff.RESPONSE_KINDS),
                'mapping_fields': sorted(handoff.MAPPING_FIELDS),
            },
            resolver.CONTRACT: {
                'observation_fields': sorted(resolver.OBSERVATION_FIELDS),
                'binding_fields': sorted(f.name for f in fields(resolver.ObjectBinding)),
                'source_statuses': sorted(resolver.STATUSES),
            },
        },
    }


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def check(path=PUBLISHED):
    published = json.loads(Path(path).read_text(), object_pairs_hook=unique_object)
    if published != exported_surfaces():
        raise ValueError('published contract drift; review interface change and regenerate explicitly')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='print runtime definitions; never rewrite the snapshot')
    args = parser.parse_args()
    if args.export:
        print(json.dumps(exported_surfaces(), indent=2, sort_keys=True))
    else:
        try:
            check()
        except (OSError, ValueError) as exc:
            print(f'contract check failed: {exc}', file=sys.stderr)
            return 1
        print('published structural contract surfaces match runtime definitions')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
