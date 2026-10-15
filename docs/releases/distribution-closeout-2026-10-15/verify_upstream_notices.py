#!/usr/bin/env python3
"""Observe the two upstream license files explicitly pinned by the selected device notice."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
retained=(REPO/'docs/releases/selected-notices/moltbot_safe/apps/macos/Sources/Moltbot/Resources/DeviceModels/LICENSE.apple-device-identifiers.txt').read_bytes()
rows=[]
for revision in ('8e7388b29da046183f5d976eb74dbb2f2acda955','98ca75324f7a88c1649eb5edfc266ef47b7b8193'):
    url=f'https://raw.githubusercontent.com/kyle-seongwoo-jun/apple-device-identifiers/{revision}/LICENSE'
    row=dict(url=url,method='unauthenticated HTTP GET',observed_at=datetime.now(timezone.utc).isoformat())
    try:
        with urllib.request.urlopen(url,timeout=25) as response:
            data=response.read()
            row.update(status=response.status,final_url=response.url,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                matches_runtime_retained_license=data==retained,
                selected_copy_adds_exactly_one_terminal_LF=retained==data+b'\n',
                selected_copy_sha256=hashlib.sha256(retained).hexdigest(),selected_copy_bytes=len(retained))
    except Exception as error:
        row.update(inaccessible=True,error_type=type(error).__name__)
    rows.append(row)
(HERE/'upstream-notice-responses.json').write_text(json.dumps(dict(scope='Two original device-mapping commits explicitly named by selected runtime nested notice; existing notice bytes preserved; no source redistribution or legal acceptance',observations=rows),indent=2,sort_keys=True)+'\n')
print('Observed upstream device license provenance; original retained notice unchanged')
