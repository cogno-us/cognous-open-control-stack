#!/usr/bin/env python3
"""Run the same-host process-boundary qualification twice against exact pins."""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCK=json.loads((ROOT/"component-lock.json").read_text())
WORK=ROOT/".process-boundary-work"
NAMES=("action_manifest","control_plane","gax_imx_transport","moltbot_safe","replay_bundle")

def run(cmd, *, cwd=None, env=None):
    started=time.time()
    p=subprocess.run(cmd,cwd=cwd or ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return {"command":cmd,"cwd":str(cwd or ROOT),"returncode":p.returncode,"seconds":round(time.time()-started,3),"output":p.stdout}

def checkout(name):
    spec=LOCK["components"][name]
    key="core_interop_sha" if name=="moltbot_safe" else "sha"
    sha=spec[key]; dest=WORK/name
    if dest.exists(): shutil.rmtree(dest)
    rec=run(["git","clone","-q",f"https://github.com/{spec['repository']}.git",str(dest)])
    if rec["returncode"]: raise RuntimeError(rec["output"])
    rec=run(["git","checkout","-q","--detach",sha],cwd=dest)
    if rec["returncode"]: raise RuntimeError(rec["output"])
    got=run(["git","rev-parse","HEAD"],cwd=dest)["output"].strip()
    if got!=sha: raise RuntimeError(f"{name}: expected {sha}, got {got}")
    return dest,sha

def junit_counts(path):
    counts={k:0 for k in ("tests","failures","errors","skipped")}
    if path.exists():
        for suite in ET.parse(path).getroot().iter("testsuite"):
            for key in counts: counts[key]+=int(suite.get(key,0))
    counts["passed"]=counts["tests"]-counts["failures"]-counts["errors"]-counts["skipped"]
    return counts

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["run"])
    ap.add_argument("--results-dir",default="results/process-boundary")
    args=ap.parse_args()
    out=(ROOT/args.results_dir).resolve()
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.rmtree(WORK,ignore_errors=True); WORK.mkdir()
    components={}; pins={}
    for name in NAMES:
        components[name],pins[name]=checkout(name)
    dep=run([sys.executable,"-m","pip","install","-q","pytest>=8","pydantic>=2"])
    if dep["returncode"]: raise RuntimeError(dep["output"])
    cp=components["control_plane"]; gax=components["gax_imx_transport"]; molt=components["moltbot_safe"]
    manifest=components["action_manifest"]; replay=components["replay_bundle"]
    env=os.environ.copy()
    env["PYTHONPATH"]=os.pathsep.join([str(ROOT),str(cp/"src"),str(gax),str(molt),env.get("PYTHONPATH","")])
    env["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"]=str(cp)
    env["MOLTBOT_SAFE_ROOT"]=str(molt)
    env["MOLTBOT_SAFE_MANIFEST_FIXTURE"]=str(manifest/"examples/refund_integration_v1_1.manifest.json")
    env["UPSTREAM_CONTROL_PLANE_ROOT"]=str(cp)
    env["UPSTREAM_MOLTBOT_SAFE_ROOT"]=str(molt)
    env["UPSTREAM_GAX_ROOT"]=str(gax)
    env["UPSTREAM_REPLAY_SUCCESS_EXAMPLE"]=str(replay/"examples/bounded_success_reconstruction_v0_2.json")
    runs=[]; overall=0
    for rep in (1,2):
        rdir=out/f"run-{rep}"; rdir.mkdir()
        evidence=rdir/"evidence"; junit=rdir/"junit.xml"
        renv=env.copy()
        renv["PROCESS_BOUNDARY_RESULTS_DIR"]=str(evidence)
        renv["PROCESS_BOUNDARY_REPETITION"]=str(rep)
        rec=run([sys.executable,"-m","pytest","-q",str(ROOT/"tests/test_process_boundary_qualification.py"),"--junitxml",str(junit)],env=renv)
        (rdir/"pytest.log").write_text(rec["output"],encoding="utf-8")
        overall=max(overall,1 if rec["returncode"] else 0)
        scenarios=[]
        if evidence.exists():
            for p in sorted(evidence.glob("*.json")):
                scenarios.append(json.loads(p.read_text()))
        runs.append({"repetition":rep,"returncode":rec["returncode"],"seconds":rec["seconds"],"junit":str(junit.relative_to(out)),"log":str((rdir/"pytest.log").relative_to(out)),"totals":junit_counts(junit),"scenarios":scenarios})
    classes={}
    for r in runs:
        for s in r["scenarios"]:
            classes[s["classification"]]=classes.get(s["classification"],0)+1
    summary={"schema_version":"1.0","hub_baseline":"b457b7e1ebcbb323e88e85b913eaafcb5755317a","component_pins":pins,"repetitions":runs,"classification_totals":classes,"qualification_exit":overall,
             "scope_limitations":["same-host shared-database only","no distributed budgets","no remote exactly-once delivery","no authenticated observations","no destination finality"]}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"results_dir":str(out),"qualification_exit":overall,"classification_totals":classes,"test_totals":{str(r["repetition"]):r["totals"] for r in runs}},indent=2))
    return overall

if __name__=="__main__":
    raise SystemExit(main())
