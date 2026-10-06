#!/usr/bin/env python3
"""Reproducible integration evidence runner for the Cognous Open Control Stack.

This script owns checkout, pin verification, test orchestration and evidence indexing.
Runtime behavior remains in the pinned component repositories.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCK=json.loads((ROOT/"component-lock.json").read_text())
WORK=ROOT/".reference-work"

def run(cmd, *, cwd=None, env=None, check=False):
    started=time.time()
    p=subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    rec={"command":cmd,"cwd":str(cwd or ROOT),"returncode":p.returncode,"seconds":round(time.time()-started,3),"output":p.stdout}
    if check and p.returncode: raise RuntimeError(p.stdout)
    return rec

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def checkout(name, spec, sha_key="sha"):
    repo=spec["repository"]; sha=spec[sha_key]
    dest=WORK/name
    if dest.exists(): shutil.rmtree(dest)
    r=run(["git","clone","-q","--no-checkout",f"https://github.com/{repo}.git",str(dest)],check=True)
    run(["git","checkout","-q","--detach",sha],cwd=dest,check=True)
    actual=run(["git","rev-parse","HEAD"],cwd=dest,check=True)["output"].strip()
    if actual!=sha: raise RuntimeError(f"{name}: expected {sha}, got {actual}")
    return dest

def static_json_check(path):
    failures=[]
    for f in path.rglob("*.json"):
        if ".git" in f.parts: continue
        try: json.loads(f.read_text(encoding="utf-8"))
        except Exception as e: failures.append({"file":str(f.relative_to(path)),"error":str(e)})
    return failures

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["run"])
    ap.add_argument("--results-dir",default="results/reference")
    args=ap.parse_args()
    out=(ROOT/args.results_dir).resolve()
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir()

    components={}
    commands=[]
    for name,spec in LOCK["components"].items():
        key="core_interop_sha" if name=="moltbot_safe" else "sha"
        components[name]=checkout(name,spec,key)
    # accepted Moltbot head is checked out separately for OpenShell qualification
    components["moltbot_safe_accepted"]=checkout("moltbot_safe_accepted",LOCK["components"]["moltbot_safe"],"accepted_sha")

    dep=run([sys.executable,"-m","pip","install","-q","pytest>=8","pydantic>=2","jsonschema>=4.21","cryptography","fastapi","httpx"],check=False)
    commands.append(dep)
    if dep["returncode"]: raise RuntimeError(dep["output"])

    cp=components["control_plane"]; replay=components["replay_bundle"]; agep=components["governance_evidence_pack"]
    odes=components["odes"]; gax=components["gax_imx_transport"]; molt=components["moltbot_safe"]
    manifest=components["action_manifest"]; bitrep=components["bitrep"]; index=components["the_index"]
    py=[str(cp/"src"),str(replay/"src"),str(agep/"src"),str(odes/"src"),str(gax),str(molt)]
    env=os.environ.copy()
    env["PYTHONPATH"]=os.pathsep.join(py+[env.get("PYTHONPATH","")])
    env["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"]=str(cp)
    env["MOLTBOT_SAFE_ROOT"]=str(molt)
    env["MOLTBOT_SAFE_MANIFEST_FIXTURE"]=str(manifest/"examples/refund_integration_v1_1.manifest.json")
    env["UPSTREAM_MANIFEST_EXAMPLE"]=env["MOLTBOT_SAFE_MANIFEST_FIXTURE"]
    env["UPSTREAM_REPLAY_SUCCESS_EXAMPLE"]=str(replay/"examples/bounded_success_reconstruction_v0_2.json")

    suites=[
      ("gax_reference", [sys.executable,"-m","pytest","-q",str(gax/"tests/test_gax_imx_reference.py"),str(gax/"tests/test_gax_imx_redelivery.py")]),
      ("control_plane", [sys.executable,"-m","pytest","-q",str(cp/"tests/test_bounded_authorization.py")]),
      ("replay", [sys.executable,"-m","pytest","-q",str(replay/"tests")]),
      ("evidence_pack", [sys.executable,"-m","pytest","-q",str(agep/"tests")]),
      ("odes", [sys.executable,"-m","pytest","-q",str(odes/"tests")]),
      ("bitrep_verification", [sys.executable,"-m","pytest","-q",str(bitrep/"tests/test_verification.py"),str(bitrep/"tests/test_api.py")]),
      ("index_local_reference", [sys.executable,"-m","pytest","-q",str(index/"chain/python/tests")]),
    ]

    runs=[]
    for repetition in (1,2):
        rdir=out/f"run-{repetition}"; rdir.mkdir()
        for name,cmd in suites:
            rec=run(cmd,env=env)
            rec["suite"]=name; rec["repetition"]=repetition
            (rdir/f"{name}.log").write_text(rec["output"],encoding="utf-8")
            rec["log"]=str((rdir/f"{name}.log").relative_to(out))
            rec.pop("output")
            runs.append(rec)

    # OpenShell mock scope at accepted head, not part of core execution pin.
    acc=components["moltbot_safe_accepted"]
    open_env=env.copy()
    open_env["PYTHONPATH"]=os.pathsep.join([str(cp/"src"),str(acc),open_env.get("PYTHONPATH","")])
    open_env["MOLTBOT_SAFE_ROOT"]=str(acc)
    openshell=run([sys.executable,"-m","pytest","-q",str(acc/"tests/test_openshell_environment.py")],env=open_env)
    (out/"openshell-mock.log").write_text(openshell["output"],encoding="utf-8")
    openshell.update({"scope":"mocked adapter only","evidence_state":"tested locally" if openshell["returncode"]==0 else "blocked","log":"openshell-mock.log"})
    openshell.pop("output")

    optional={}
    for name in ("prp","research_intelligence","tfa"):
        failures=static_json_check(components[name])
        optional[name]={"state":"tested locally" if not failures else "blocked","check":"JSON syntax/static artifact parse only; model-behavior evaluations unexecuted","failures":failures}

    actual_pins={}
    for name,path in components.items():
        actual_pins[name]=run(["git","rev-parse","HEAD"],cwd=path,check=True)["output"].strip()

    compatibility={
      "core_moltbot_pin":LOCK["components"]["moltbot_safe"]["core_interop_sha"],
      "accepted_moltbot_head":LOCK["components"]["moltbot_safe"]["accepted_sha"],
      "moltbot_provenance_gap":LOCK["components"]["moltbot_safe"]["core_interop_sha"]!=LOCK["components"]["moltbot_safe"]["accepted_sha"],
      "note":"Replay 0.2.0 and Evidence Pack importer 0.2.6 declare the core_interop_sha. Accepted Moltbot head is qualified separately until producer provenance is versioned/uprevved upstream."
    }
    summary={
      "evidence_state":"tested locally",
      "environment":{"python":sys.version,"platform":platform.platform()},
      "actual_pins":actual_pins,
      "runs":runs,
      "openshell":openshell,
      "optional_instruction_layers":optional,
      "compatibility":compatibility,
      "live_openshell":{"state":"unexecuted","command":"COGN0US_OPENSHELL_LIVE=1 python -m pytest -q <moltbot-safe>/tests/test_openshell_live.py","reason":"requires pre-authorized live OpenShell/Docker infrastructure; runner never provisions paid or external infrastructure"},
    }
    summary["all_core_suites_passed"]=all(x["returncode"]==0 for x in runs)
    (out/"scenario-results.json").write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")
    (out/"component-pins.json").write_text(json.dumps(actual_pins,indent=2,sort_keys=True),encoding="utf-8")
    artifacts=[]
    for f in sorted(out.rglob("*")):
        if f.is_file(): artifacts.append({"path":str(f.relative_to(out)),"sha256":sha256(f),"bytes":f.stat().st_size})
    (out/"artifact-index.json").write_text(json.dumps({"artifacts":artifacts},indent=2),encoding="utf-8")
    print(json.dumps({"results_dir":str(out),"all_core_suites_passed":summary["all_core_suites_passed"],"openshell_mock":openshell["returncode"]==0},indent=2))
    return 0 if summary["all_core_suites_passed"] and openshell["returncode"]==0 else 1

if __name__=="__main__": raise SystemExit(main())
