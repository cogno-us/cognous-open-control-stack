#!/usr/bin/env python3
"""Run Worker 21 proposed-revision qualification without advancing hub pins."""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/".worker21-work"
CP_SHA="73e3c65acc47dc43593dcb0420d14032ed410b14"
MB_SHA="ba0beb714064a225e3def69bb53ee388439ee43e"
OTHER={
  "action_manifest":("cogno-us/cognous-action-manifest","46c950bed37fe3812000895430bc0312d29e37ce"),
  "gax_imx_transport":("cogno-us/cognous-governed-exchange","9984d9011568ccdf3d562fa9760ad41368947b34"),
  "replay_bundle":("cogno-us/cognous-replay-bundle","043830b56595cecddfa65c064afd1c0b95e64792"),
}

def run(cmd,*,cwd=None,env=None):
    t=time.time(); p=subprocess.run(cmd,cwd=cwd or ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return {"cmd":cmd,"returncode":p.returncode,"seconds":round(time.time()-t,3),"output":p.stdout}

def checkout(name,repo,sha):
    dest=WORK/name
    if dest.exists(): shutil.rmtree(dest)
    r=run(["git","clone","-q",f"https://github.com/{repo}.git",str(dest)])
    if r["returncode"]: raise RuntimeError(r["output"])
    r=run(["git","checkout","-q","--detach",sha],cwd=dest)
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

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["run"]); ap.add_argument("--results-dir",default="results/worker21-authority-effect"); args=ap.parse_args()
    out=(ROOT/args.results_dir).resolve(); shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    shutil.rmtree(WORK,ignore_errors=True); WORK.mkdir()
    roots={}
    roots["control_plane"]=checkout("control_plane","cogno-us/cognous-control-plane",CP_SHA)
    roots["moltbot_safe"]=checkout("moltbot_safe","cogno-us/cognous-execution-runtime",MB_SHA)
    for name,(repo,sha) in OTHER.items(): roots[name]=checkout(name,repo,sha)
    dep=run([sys.executable,"-m","pip","install","-q","pytest>=8","pydantic>=2"])
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
        junit=out/f"{name}.xml"; rec=run(cmd+["--junitxml",str(junit)],env=env); (out/f"{name}.log").write_text(rec["output"])
        if rec["returncode"]: overall=1
        results.append({"name":name,"returncode":rec["returncode"],"totals":counts(junit),"seconds":rec["seconds"]})
    for rep in (1,2):
        junit=out/f"integration-{rep}.xml"
        rec=run([sys.executable,"-m","pytest","-q",str(ROOT/"tests/test_worker21_atomic_authority_effect.py"),"--junitxml",str(junit)],env=env)
        (out/f"integration-{rep}.log").write_text(rec["output"])
        if rec["returncode"]: overall=1
        results.append({"name":f"integration-{rep}","returncode":rec["returncode"],"totals":counts(junit),"seconds":rec["seconds"]})
    summary={"schema_version":"1.0","hub_baseline":"502fd12cb49d30f8ea8e12d7968612d55d326f16","proposed_revisions":{"control_plane":CP_SHA,"moltbot_safe":MB_SHA},"accepted_supporting_pins":{k:v[1] for k,v in OTHER.items()},"component_lock_changed":False,"qualification_exit":overall,"results":results,"claim_scope":"same-host synthetic SQLite profile only","not_claimed":["upstream acceptance","hub selection","production readiness","distributed exactly-once","external destination atomicity","EBL-Core conformance"]}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True)); return overall

if __name__=="__main__": raise SystemExit(main())
