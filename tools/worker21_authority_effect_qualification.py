#!/usr/bin/env python3
"""Run Worker 21 proposed-revision qualification without advancing hub pins."""
from __future__ import annotations
import argparse, json, os, shutil, signal, subprocess, sys, time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/".worker21-work"
CP_SHA="73e3c65acc47dc43593dcb0420d14032ed410b14"
MB_SHA="b1525a7982e52ebb530457f94d5517de032ca4c4"
ACCEPTED_CP_SHA="d3dadee70bd319812b207389ab1e0f6efe511916"
ACCEPTED_MB_SHA="c3c3ee7188b9367cf70b08074b9c40a5c70c94ac"
EXPECTED={"control-plane-focused":7,"profile-compatibility":4,"moltbot-focused":24,"integration-1":19,"integration-2":19}
OTHER={
  "action_manifest":("cogno-us/cognous-action-manifest","46c950bed37fe3812000895430bc0312d29e37ce"),
  "gax_imx_transport":("cogno-us/cognous-governed-exchange","9984d9011568ccdf3d562fa9760ad41368947b34"),
  "replay_bundle":("cogno-us/cognous-replay-bundle","043830b56595cecddfa65c064afd1c0b95e64792"),
}

def run(cmd,*,cwd=None,env=None,timeout=120):
    print("Starting:", " ".join(map(str,cmd)), flush=True)
    t=time.time()
    p=subprocess.Popen(cmd,cwd=cwd or ROOT,env=env,text=True,stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,start_new_session=(os.name=="posix"))
    try:
        output,_=p.communicate(timeout=timeout)
        code=p.returncode
    except subprocess.TimeoutExpired:
        if os.name=="posix": os.killpg(p.pid,signal.SIGKILL)
        else: p.kill()
        output,_=p.communicate()
        output += f"\nBatch exceeded {timeout} seconds; terminated.\n"
        code=124
    return {"cmd":cmd,"returncode":code,"seconds":round(time.time()-t,3),"output":output}

def checkout(name,repo,sha):
    dest=WORK/name
    if dest.exists(): shutil.rmtree(dest)
    r=run(["git","clone","-q","--filter=blob:none","--no-checkout",f"https://github.com/{repo}.git",str(dest)],timeout=300)
    if r["returncode"]: raise RuntimeError(r["output"])
    r=run(["git","checkout","-q","--detach",sha],cwd=dest,timeout=300)
    if r["returncode"]: raise RuntimeError(r["output"])
    got=run(["git","rev-parse","HEAD"],cwd=dest)["output"].strip()
    if got!=sha: raise RuntimeError(f"{name}: {got} != {sha}")
    return dest

def counts(path):
    out={k:0 for k in ("tests","failures","errors","skipped")}
    if path.exists():
        for suite in ET.parse(path).getroot().iter("testsuite"):
            for k in out: out[k]+=int(suite.get(k,0))
    out["passed"]=out["tests"]-out["failures"]-out["errors"]-out["skipped"]
    return out

def passed_batch(rec, totals, expected):
    return (rec["returncode"] == 0 and totals["tests"] == expected
            and totals["passed"] == expected
            and not any(totals[k] for k in ("failures","errors","skipped")))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["run"]); ap.add_argument("--results-dir",default="results/worker21-authority-effect"); ap.add_argument("--accepted-merges",action="store_true"); ap.add_argument("--batch",choices=["all",*EXPECTED],default="all"); args=ap.parse_args()
    cp_sha=ACCEPTED_CP_SHA if args.accepted_merges else CP_SHA
    mb_sha=ACCEPTED_MB_SHA if args.accepted_merges else MB_SHA
    out=(ROOT/args.results_dir).resolve(); shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    shutil.rmtree(WORK,ignore_errors=True); WORK.mkdir()
    roots={}
    roots["control_plane"]=checkout("control_plane","cogno-us/cognous-control-plane",cp_sha)
    roots["moltbot_safe"]=checkout("moltbot_safe","cogno-us/cognous-execution-runtime",mb_sha)
    for name,(repo,sha) in OTHER.items(): roots[name]=checkout(name,repo,sha)
    dep=run([sys.executable,"-m","pip","install","-q","pytest>=8","pydantic>=2"],timeout=300)
    if dep["returncode"]: raise RuntimeError(dep["output"])
    env=os.environ.copy()
    env["PYTHONPATH"]=os.pathsep.join([str(ROOT),str(roots["control_plane"]/ "src"),str(roots["moltbot_safe"]),str(roots["gax_imx_transport"]),env.get("PYTHONPATH","")])
    env["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"]=str(roots["control_plane"])
    env["MOLTBOT_SAFE_ROOT"]=str(roots["moltbot_safe"])
    results=[]; overall=0
    commands=[
      ("control-plane-focused",[sys.executable,"-m","pytest","-q",str(roots["control_plane"]/ "tests/test_local_authority_effect_profile.py")]),
      ("profile-compatibility",[sys.executable,"-m","pytest","-q",str(roots["moltbot_safe"]/ "tests/test_profile_exclusivity.py")]),
      ("moltbot-focused",[sys.executable,"-m","pytest","-q",str(roots["moltbot_safe"]/ "tests/test_local_authority_effect.py")]),
    ]
    for name,cmd in commands:
        if args.batch not in ("all",name): continue
        junit=out/f"{name}.xml"; rec=run(cmd+["--junitxml",str(junit)],env=env); (out/f"{name}.log").write_text(rec["output"])
        if not passed_batch(rec,counts(junit),EXPECTED[name]): overall=1
        results.append({"name":name,"returncode":rec["returncode"],"totals":counts(junit),"seconds":rec["seconds"]})
    for rep in (1,2):
        name=f"integration-{rep}"
        if args.batch not in ("all",name): continue
        junit=out/f"integration-{rep}.xml"
        rec=run([sys.executable,"-m","pytest","-q",str(ROOT/"tests/test_worker21_atomic_authority_effect.py"),"--junitxml",str(junit)],env=env)
        (out/f"integration-{rep}.log").write_text(rec["output"])
        if not passed_batch(rec,counts(junit),EXPECTED[name]): overall=1
        results.append({"name":f"integration-{rep}","returncode":rec["returncode"],"totals":counts(junit),"seconds":rec["seconds"]})
    summary={"schema_version":"2.0","historical_hub_baseline":"502fd12cb49d30f8ea8e12d7968612d55d326f16","hub_revision":run(["git","rev-parse","HEAD"])["output"].strip(),"revision_selection":"accepted_merges" if args.accepted_merges else "reviewed_sources","tested_revisions":{"control_plane":cp_sha,"moltbot_safe":mb_sha},"batch":args.batch,"accepted_supporting_pins":{k:v[1] for k,v in OTHER.items()},"component_lock_changed":False,"qualification_exit":overall,"results":results,"claim_scope":"same-host synthetic SQLite profile only","not_claimed":["hub selection","production readiness","distributed exactly-once","external destination atomicity","EBL-Core conformance"]}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True)); return overall

if __name__=="__main__": raise SystemExit(main())
