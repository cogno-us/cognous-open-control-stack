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
    run(["git","clone","-q","--no-checkout",f"https://github.com/{repo}.git",str(dest)],check=True)
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

    execution_state="tested in pinned CI" if os.environ.get("GITHUB_ACTIONS")=="true" else "tested locally"

    components={}
    commands=[]
    for name,spec in LOCK["components"].items():
        key="core_interop_sha" if name=="moltbot_safe" else "sha"
        components[name]=checkout(name,spec,key)
    components["moltbot_safe_accepted"]=checkout(
        "moltbot_safe_accepted",LOCK["components"]["moltbot_safe"],"accepted_sha"
    )

    dep=run([sys.executable,"-m","pip","install","-q","pytest>=8","pytest-cov>=4","pydantic>=2","jsonschema>=4.21","cryptography","fastapi","httpx","sqlalchemy","python-dotenv"])
    commands.append({k:v for k,v in dep.items() if k!="output"})
    if dep["returncode"]: raise RuntimeError(dep["output"])

    cp=components["control_plane"]; replay=components["replay_bundle"]; agep=components["governance_evidence_pack"]
    odes=components["odes"]; gax=components["gax_imx_transport"]; molt=components["moltbot_safe"]
    agep_install=run([sys.executable,"-m","pip","install","-q","-e",str(agep)])
    commands.append({k:v for k,v in agep_install.items() if k!="output"})
    if agep_install["returncode"]: raise RuntimeError(agep_install["output"])

    manifest=components["action_manifest"]; bitrep=components["bitrep"]; index=components["the_index"]
    py=[
        str(cp/"src"),str(replay/"src"),str(agep/"src"),str(odes/"src"),str(gax),str(molt),
        str(bitrep),str(index/"chain/python")
    ]
    env=os.environ.copy()
    env["PYTHONPATH"]=os.pathsep.join(py+[env.get("PYTHONPATH","")])
    env["BITREP_ROOT"]=str(bitrep)
    env["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"]=str(cp)
    env["MOLTBOT_SAFE_ROOT"]=str(molt)
    env["MOLTBOT_SAFE_MANIFEST_FIXTURE"]=str(manifest/"examples/refund_integration_v1_1.manifest.json")
    env["UPSTREAM_MANIFEST_EXAMPLE"]=env["MOLTBOT_SAFE_MANIFEST_FIXTURE"]
    env["UPSTREAM_REPLAY_SUCCESS_EXAMPLE"]=str(replay/"examples/bounded_success_reconstruction_v0_2.json")

    npm=run(["npm","ci","--ignore-scripts"],cwd=index/"chain")
    commands.append({k:v for k,v in npm.items() if k!="output"})
    if npm["returncode"]: raise RuntimeError(npm["output"])

    # Generate one representative end-to-end artifact chain through accepted CLIs.
    representative_dir=out/"representative"; representative_dir.mkdir()
    gax_out=representative_dir/"gax-success.json"
    rep_cmd=[
        sys.executable,"-c",
        "import sys; from experiments.odex_gax_imx_reference.gax_ref_runtime import run_demo; run_demo(sys.argv[1], sys.argv[2], sys.argv[3])",
        str(manifest/"examples/refund_integration_v1_1.manifest.json"),
        str(replay/"examples/bounded_success_reconstruction_v0_2.json"),
        str(gax_out)
    ]
    representative_run=run(rep_cmd,env=env)
    (representative_dir/"gax-success.log").write_text(representative_run["output"],encoding="utf-8")
    representative_run["log"]="representative/gax-success.log"
    representative_run.pop("output")
    evidence_pack_run={"returncode":1,"reason":"GAX representative generation failed"}
    if representative_run["returncode"]==0 and gax_out.exists():
        gax_data=json.loads(gax_out.read_text(encoding="utf-8"))
        reconstruction=gax_data.get("current_reconstruction_bundle")
        if reconstruction is None:
            evidence_pack_run={"returncode":1,"reason":"GAX output missing current_reconstruction_bundle"}
        else:
            reconstruction_path=representative_dir/"reconstruction-bundle.json"
            reconstruction_path.write_text(json.dumps(reconstruction,indent=2,sort_keys=True),encoding="utf-8")
            pack_path=representative_dir/"governance-evidence-pack.json"
            pack_md=representative_dir/"governance-evidence-pack.md"
            evidence_pack_run=run([
                sys.executable,"-m","agent_governance_evidence_pack.cli","import",
                "--manifest",str(manifest/"examples/refund_integration_v1_1.manifest.json"),
                "--reconstruction",str(reconstruction_path),
                "--out",str(pack_path),"--render",str(pack_md)
            ],env=env)
            (representative_dir/"evidence-pack.log").write_text(evidence_pack_run["output"],encoding="utf-8")
            evidence_pack_run["log"]="representative/evidence-pack.log"
            evidence_pack_run.pop("output")
            execution=gax_data.get("execution") or {}
            facts=gax_data.get("execution_facts") or {}
            expected_observed={
                "expected":{"effect_count":1,"destination_state":"applied","newly_executed":True},
                "observed":{
                    "effect_id":execution.get("effect_id"),
                    "attempt_id":execution.get("attempt_id"),
                    "destination_state":execution.get("destination_observed"),
                    "newly_executed":execution.get("newly_executed"),
                    "unresolved_delivery":facts.get("unresolved_delivery")
                },
                "assertion_source":"accepted GAX runtime output; test suites independently assert destination state"
            }
            (representative_dir/"expected-vs-observed.json").write_text(
                json.dumps(expected_observed,indent=2,sort_keys=True),encoding="utf-8"
            )
            if "odes_reference" in gax_data:
                (representative_dir/"odes-reference.json").write_text(
                    json.dumps(gax_data["odes_reference"],indent=2,sort_keys=True),encoding="utf-8"
                )
            if "successor_packet" in gax_data:
                (representative_dir/"imx-successor.json").write_text(
                    json.dumps(gax_data["successor_packet"],indent=2,sort_keys=True),encoding="utf-8"
                )

    suites=[
      ("gax_reference", [sys.executable,"-m","pytest","-q",str(gax/"tests/test_gax_imx_reference.py"),str(gax/"tests/test_gax_imx_redelivery.py")], ROOT),
      ("governed_transport", [sys.executable,"-m","pytest","-q",str(gax/"tests/test_governed_message_transport.py")], ROOT),
      ("control_plane", [sys.executable,"-m","pytest","-q",str(cp/"tests/test_bounded_authorization.py")], ROOT),
      ("replay", [sys.executable,"-m","pytest","-q",str(replay/"tests")], ROOT),
      ("evidence_pack", [sys.executable,"-m","pytest","-q",str(agep/"tests")], ROOT),
      ("odes", [sys.executable,"-m","pytest","-q",str(odes/"tests")], ROOT),
      ("bitrep_verification", [sys.executable,"-m","pytest","-q",str(bitrep/"tests/test_verification.py"),str(bitrep/"tests/test_api.py")], ROOT),
      ("index_bitrep_binding", [sys.executable,"-m","pytest","-q",str(index/"chain/python/test_bitrep.py")], ROOT),
      ("index_local_chain", ["npm","test"], index/"chain"),
    ]

    runs=[]
    for repetition in (1,2):
        rdir=out/f"run-{repetition}"; rdir.mkdir()
        for name,cmd,cwd in suites:
            actual_cmd=list(cmd)
            junit=None
            if len(actual_cmd)>=3 and actual_cmd[1:3]==["-m","pytest"]:
                junit=rdir/f"{name}.xml"
                actual_cmd.extend(["--junitxml",str(junit)])
            rec=run(actual_cmd,cwd=cwd,env=env)
            rec["suite"]=name; rec["repetition"]=repetition
            (rdir/f"{name}.log").write_text(rec["output"],encoding="utf-8")
            rec["log"]=str((rdir/f"{name}.log").relative_to(out))
            if junit is not None: rec["junit"]=str(junit.relative_to(out))
            rec.pop("output")
            runs.append(rec)

    acc=components["moltbot_safe_accepted"]
    open_env=env.copy()
    open_env["PYTHONPATH"]=os.pathsep.join([str(cp/"src"),str(acc),open_env.get("PYTHONPATH","")])
    open_env["MOLTBOT_SAFE_ROOT"]=str(acc)
    open_xml=out/"openshell-mock.xml"
    openshell=run([
        sys.executable,"-m","pytest","-q",str(acc/"tests/test_openshell_environment.py"),
        "--junitxml",str(open_xml)
    ],env=open_env)
    (out/"openshell-mock.log").write_text(openshell["output"],encoding="utf-8")
    openshell.update({
        "scope":"mocked adapter only",
        "evidence_state":execution_state if openshell["returncode"]==0 else "blocked",
        "log":"openshell-mock.log",
        "junit":"openshell-mock.xml"
    })
    openshell.pop("output")

    optional={}
    for name in ("prp","research_intelligence","tfa"):
        failures=static_json_check(components[name])
        optional[name]={
            "state":execution_state if not failures else "blocked",
            "check":"JSON syntax/static artifact parse only; model-behavior evaluations unexecuted",
            "failures":failures
        }

    actual_pins={}
    for name,path in components.items():
        actual_pins[name]=run(["git","rev-parse","HEAD"],cwd=path,check=True)["output"].strip()

    compatibility={
      "core_moltbot_pin":LOCK["components"]["moltbot_safe"]["core_interop_sha"],
      "accepted_moltbot_head":LOCK["components"]["moltbot_safe"]["accepted_sha"],
      "moltbot_provenance_gap":LOCK["components"]["moltbot_safe"]["core_interop_sha"]!=LOCK["components"]["moltbot_safe"]["accepted_sha"],
      "gax_public_entrypoint_gap":"accepted GAX runtime resolves Moltbot integration helpers through tests/test_safe_executor.py even though Moltbot exports engine.control_plane_adapter.PinnedControlPlaneExecutor; hub does not patch adjacent repository",
      "note":"Replay 0.2.0 and Evidence Pack importer 0.2.6 declare the core_interop_sha. Accepted Moltbot head is qualified separately until producer provenance is versioned/uprevved upstream."
    }
    summary={
      "evidence_state":execution_state,
      "environment":{"python":sys.version,"platform":platform.platform()},
      "setup_commands":commands,
      "actual_pins":actual_pins,
      "representative_chain":{"gax":representative_run,"evidence_pack":evidence_pack_run},
      "runs":runs,
      "openshell":openshell,
      "optional_instruction_layers":optional,
      "compatibility":compatibility,
      "live_openshell":{
        "state":"unexecuted",
        "command":"MOLTBOT_SAFE_OPENSHELL_CONFIG=/path/to/qualified-config.json MOLTBOT_SAFE_OPENSHELL_BINARY=/path/to/openshell MOLTBOT_SAFE_OPENSHELL_HOME=/path/to/isolated-home python -m pytest -q .reference-work/moltbot_safe_accepted/tests/test_openshell_live.py",
        "reason":"requires pre-authorized live OpenShell gateway, worker image and isolated home; runner never provisions paid or external infrastructure"
      },
    }
    summary["all_core_suites_passed"]=(representative_run["returncode"]==0 and evidence_pack_run["returncode"]==0 and all(x["returncode"]==0 for x in runs))
    (out/"scenario-results.json").write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")
    (out/"component-pins.json").write_text(json.dumps(actual_pins,indent=2,sort_keys=True),encoding="utf-8")
    artifacts=[]
    for f in sorted(out.rglob("*")):
        if f.is_file(): artifacts.append({"path":str(f.relative_to(out)),"sha256":sha256(f),"bytes":f.stat().st_size})
    (out/"artifact-index.json").write_text(json.dumps({"artifacts":artifacts},indent=2),encoding="utf-8")
    print(json.dumps({
        "results_dir":str(out),
        "evidence_state":execution_state,
        "all_core_suites_passed":summary["all_core_suites_passed"],
        "openshell_mock":openshell["returncode"]==0
    },indent=2))
    return 0 if summary["all_core_suites_passed"] and openshell["returncode"]==0 else 1

if __name__=="__main__": raise SystemExit(main())
