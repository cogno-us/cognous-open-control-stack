#!/usr/bin/env python3
"""Read-only HTTP GET ledger for bounded public entries and exact notice references."""
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import html
import json
import posixpath
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
BASE='592919dd95396f3f6164cf0ceec1fd15c065691b'
SOURCES=['README.md','SECURITY.md','CONTRIBUTING.md','LICENSING.md','docs/start-here.md',
         'docs/quickstart.md','docs/release-status.md','docs/releases/selected-notices/README.md',
         'docs/releases/publication-acceptance-2026-10-13.md']

def source(p):
    return subprocess.check_output(['git','-C',str(REPO),'show',BASE+':'+p]).decode()

def main():
    targets={}
    for p in SOURCES:
        for u in re.findall(r'https?://[^\s<>\[\]`"\)]+',source(p)):
            targets.setdefault(html.unescape(u.rstrip('.,;')),[]).append(p)
    for p in SOURCES:
        for target in re.findall(r'!?\[[^\]]*\]\(([^\s\)]+)\)',source(p)):
            if urllib.parse.urlsplit(target).scheme or target.startswith('//'):
                continue
            parsed=urllib.parse.urlsplit(target)
            path=posixpath.normpath(posixpath.join(posixpath.dirname(p),parsed.path)) if parsed.path else p
            target_url=f'https://github.com/cogno-us/cognous-open-control-stack/blob/{BASE}/{path}'
            if parsed.fragment:target_url+='#'+parsed.fragment
            targets.setdefault(target_url,[]).append(p+' (rendered local reference)')
    ledger=json.loads(source('docs/releases/selected-notices.json'))
    for c in ledger['components']:
        for n in c['notices']:
            targets.setdefault(n['source_url'],[]).append(n['retained_path'])
            text=source(n['retained_path'])
            for u in re.findall(r'https?://[^\s<>\[\]`\"\)]+',text):
                targets.setdefault(html.unescape(u.rstrip('.,;')),[]).append(n['retained_path']+' (notice outbound reference)')
            for relative in re.findall(r'\[[^\]]*\]\(([^\s\)]+)\)',text):
                if not urllib.parse.urlsplit(relative).scheme:
                    targets.setdefault(urllib.parse.urljoin(n['source_url'],relative),[]).append(n['retained_path']+' (original source-relative notice link)')
    targets.setdefault('https://github.com/cogno-us/cognous-open-control-stack/issues/new/choose',[]).append('explicit chooser probe (GET only)')
    previous = None
    if '--retry-inaccessible' in sys.argv:
        previous=json.loads((HERE/'link-responses.json').read_text())
        pending={r['url'] for r in previous['targets'] if r.get('status') != 200}
        targets={u:refs for u,refs in targets.items() if u in pending}
    def check(item):
        url,refs=item
        row=dict(url=url,referenced_from=sorted(set(refs)),method='unauthenticated HTTP GET',
                 observed_at=datetime.now(timezone.utc).isoformat())
        class Redirects(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,req,fp,code,msg,headers,newurl):
                row.setdefault('redirects',[]).append(dict(status=code,to=newurl))
                return super().redirect_request(req,fp,code,msg,headers,newurl)
        try:
            opener=urllib.request.build_opener(Redirects())
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'Cognous-S4-read-only-inventory'}),timeout=25) as r:
                b=r.read(8*1024*1024)
                row.update(status=r.status,final_url=r.url,bytes_read=len(b),response_sha256=hashlib.sha256(b).hexdigest(),
                           content_type=r.headers.get('Content-Type'),disposition='accessible')
                frag=urllib.parse.unquote(urllib.parse.urlsplit(url).fragment)
                if frag:
                    text=b.decode(errors='replace')
                    ids=set(html.unescape(x) for x in re.findall(r'(?:id|name)=[\"\']([^\"\']+)',text))
                    row['fragment']=frag
                    row['rendered_fragment_found']=frag in ids or 'user-content-'+frag in ids
                    if not row['rendered_fragment_found']:row['disposition']='HTTP accessible; fragment unverified or absent'
                if url.endswith('/issues/new/choose'):
                    row['issue_template_links_present']=b'issues/new?template=' in b
                    row['form_submission']='not performed'
                    if urllib.parse.urlsplit(r.url).path == '/login':
                        row['disposition']='sign-in boundary accessible; chooser form unverified'
                if url.startswith('https://raw.githubusercontent.com/'):
                    expected=[n['sha256'] for c in ledger['components'] for n in c['notices'] if n['source_url']==url]
                    if expected:
                        row['notice_digest_matches_retained']=hashlib.sha256(b).hexdigest() in expected
        except urllib.error.HTTPError as e:
            row.update(status=e.code,final_url=e.url,disposition='inaccessible HTTP target')
        except Exception as e:
            row.update(disposition='inaccessible from this environment',error_type=type(e).__name__)
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        rows=list(pool.map(check,sorted(targets.items())))
    if previous is not None:
        updated={r['url']:r for r in rows}
        merged=[]
        for old in previous['targets']:
            if old['url'] in updated:
                new=updated[old['url']]
                new['prior_observations']=[old]
                merged.append(new)
            else:merged.append(old)
        rows=merged
    (HERE/'link-responses.json').write_text(json.dumps(dict(source_commit=BASE,sources=SOURCES,targets=rows,
        scope='Outbound HTTP URLs and rendered local references on named entry surfaces, all 28 exact notice URLs, notice outbound/relative references and chooser; not every historical Markdown URL. No forms, mail or reports submitted.'),indent=2,sort_keys=True)+'\n')
    print('Targets',len(rows),'HTTP 200',sum(r.get('status')==200 for r in rows),'inaccessible',sum(r.get('status')!=200 for r in rows))

if __name__=='__main__':main()
