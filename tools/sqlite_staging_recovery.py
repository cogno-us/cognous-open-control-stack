#!/usr/bin/env python3
"""Snapshot or restore a trusted local SQLite store without authorizing activation."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reference_profiles.sqlite_recovery import snapshot, restore


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('operation',choices=('snapshot','restore'))
    ap.add_argument('source',type=Path)
    ap.add_argument('destination',type=Path)
    args = ap.parse_args()
    result = snapshot(args.source,args.destination) if args.operation=='snapshot' else restore(args.source,args.destination)
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
