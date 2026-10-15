"""Bind embedding admission declarations to retained configuration evidence.

A complete packet validates declarations and bytes, not deployed truth or authority.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from reference_profiles.bounded_json import snapshot
from tools.deployment_review import committed_file, PacketError, read_bounded, strict_json

SURFACES=('resolver-observations','context-evidence','context-journal','evidence-assessment',
          'assurance-apply','protected-destination','attestation-http','registry-http','upstream-gateway')
LIMITS=('predecode_bytes','depth','items','string_bytes','requests_per_interval','interval_seconds','timeout_seconds')


def validate(packet,root,lock_bytes,expected_revision):
    result={'contract':'embedding-exposure-assessment/1','configuration_requirements_satisfied':False,
            'deployment_verified':False,'production_authorized':False,'authorizing':False,'errors':[],
            'surfaces':[]}
    try:
        packet=snapshot(packet)
        if type(packet) is not dict or set(packet)!={'contract','source_revision','component_lock_sha256','environment_id','configuration','surfaces'}:
            raise ValueError('INVALID_PACKET_FIELDS')
        if packet['contract']!='embedding-exposure/1':raise ValueError('UNSUPPORTED_CONTRACT')
        if not re.fullmatch('[0-9a-f]{40}',expected_revision) or packet['source_revision']!=expected_revision:
            raise ValueError('SOURCE_REVISION_MISMATCH')
        if packet['component_lock_sha256']!=hashlib.sha256(lock_bytes).hexdigest():raise ValueError('LOCK_MISMATCH')
        result['source_revision']=expected_revision
        if type(packet['environment_id']) is not str or not packet['environment_id']:
            result['errors'].append('DEPLOYMENT_ENVIRONMENT_UNAVAILABLE')
        if packet['configuration'] is None:result['errors'].append('DEPLOYMENT_CONFIGURATION_UNAVAILABLE')
        else:committed_file(Path(root).resolve(),packet['configuration'])
        rows=packet['surfaces']
        if type(rows) is not list or len(rows)!=len(SURFACES) or {r.get('id') for r in rows if type(r) is dict}!=set(SURFACES):
            raise ValueError('SURFACE_SET_MISMATCH')
        for row in rows:
            issues=[];identity=row['id']
            if set(row)!={'id','exposure','authentication','limits','storage_bound','host_permissions','evidence'}:raise ValueError('INVALID_SURFACE_FIELDS')
            if row['exposure'] not in ('local-only','loopback','authenticated-remote','unverified'):
                issues.append('UNSUPPORTED_EXPOSURE')
            if row['exposure']=='unverified':issues.append('EXPOSURE_UNVERIFIED')
            if row['authentication'] not in ('trusted-local-host','authenticated-principal','capability'):
                issues.append('AUTHENTICATION_UNESTABLISHED')
            if row['exposure']=='authenticated-remote' and row['authentication'] not in ('authenticated-principal','capability'):
                issues.append('REMOTE_AUTHENTICATION_REQUIRED')
            if row['host_permissions'] not in ('restricted-principal','no-host-effects'):
                issues.append('HOST_PERMISSIONS_UNESTABLISHED')
            limits=row['limits']
            if type(limits) is not dict or set(limits)!=set(LIMITS) or any(type(v) is not int or v<=0 for v in limits.values()):
                issues.append('EXPLICIT_POSITIVE_ADMISSION_LIMITS_REQUIRED')
            if row['storage_bound'] not in ('durable-quota-and-retention','no-durable-writes'):
                issues.append('STORAGE_BOUND_UNESTABLISHED')
            evidence=row['evidence']
            if type(evidence) is not list or not 1<=len(evidence)<=20:issues.append('CONFIGURATION_EVIDENCE_UNAVAILABLE')
            else:
                for reference in evidence:committed_file(Path(root).resolve(),reference)
            result['surfaces'].append({'id':identity,'requirements_satisfied':not issues,'errors':issues})
        result['configuration_requirements_satisfied']=not result['errors'] and all(r['requirements_satisfied'] for r in result['surfaces'])
    except (ValueError,TypeError,KeyError,OSError,PacketError):
        result['errors'].append('INVALID_OR_UNAVAILABLE_EXPOSURE_PACKET')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('packet',type=Path);p.add_argument('--lock',required=True,type=Path);p.add_argument('--expected-revision',required=True);a=p.parse_args()
    try:value=validate(strict_json(read_bounded(a.packet)),a.packet.parent,read_bounded(a.lock),a.expected_revision)
    except (ValueError,OSError,RecursionError):value={'configuration_requirements_satisfied':False,'deployment_verified':False,'authorizing':False,'errors':['INVALID_PACKET_INPUT']}
    print(json.dumps(value,indent=2,sort_keys=True));return 0 if value['configuration_requirements_satisfied'] else 2


if __name__=='__main__':raise SystemExit(main())
