#!/usr/bin/env python3
"""Reproducible integration evidence runner for the Cognous Open Control Stack."""
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

def checkout(name,spec,sha_key="sha"):
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
    components={}; setup=[]
    for name,spec in LOCK["components"].items():
        key="core_interop_sha" if name=="moltbot_safe" else "sha"
        components[name]=checkout(name,spec,key)
    components["moltbot_safe_accepted"]=checkout("moltbot_safe_accepted",LOCK["components"]["moltbot_safe"],"accepted_sha")

    dep=run([sys.executable,"-m","pip","install","-q","pytest>=8","pytest-cov>=4","pydantic>=2","jsonschema>=4.21","cryptography","fastapi","httpx","sqlalchemy","python-dotenv"])
    setup.append({k:v for k,v in dep.items() if k!="output"})
    if dep["returncode"]: raise RuntimeError(dep["output"])

    cp=components["control_plane"]; replay=components["replay_bundle"]; agep=components["governance_evidence_pack"]
    odes=components["odes"]; gax=components["gax_imx_transport"]; molt=components["moltbot_safe"]
    manifest=components["action_manifest"]; bitrep=components["bitrep"]; index=components["the_index"]
    agep_install=run([sys.executable,"-m","pip","install","-q","-e",str(agep)])
    setup.append({k:v for k,v in agep_install.items() if k!="output"})
    if agep_install["returncode"]: raise RuntimeError(agep_install["output"])

    py=[str(ROOT),str(cp/"src"),str(replay/"src"),str(agep/"src"),str(odes/"src"),str(gax),str(molt),str(bitrep),str(index/"chain/python")]
    env=os.environ.copy()
    env["PYTHONPATH"]=os.pathsep.join(py+[env.get("PYTHONPATH","")])
    env["BITREP_ROOT"]=str(bitrep)
    env["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"]=str(cp)
    env["MOLTBOT_SAFE_ROOT"]=str(molt)
    env["MOLTBOT_SAFE_MANIFEST_FIXTURE"]=str(manifest/"examples/refund_integration_v1_1.manifest.json")
    env["UPSTREAM_MANIFEST_EXAMPLE"]=env["MOLTBOT_SAFE_MANIFEST_FIXTURE"]
    env["UPSTREAM_REPLAY_SUCCESS_EXAMPLE"]=str(replay/"examples/bounded_success_reconstruction_v0_2.json")
    env["UPSTREAM_REPLAY_LOST_ACK_EXAMPLE"]=str(replay/"examples/bounded_lost_ack_reconstruction_v0_2.json")
    env["UPSTREAM_GAX_ROOT"]=str(gax)
    env["UPSTREAM_CONTROL_PLANE_ROOT"]=str(cp)
    env["UPSTREAM_MOLTBOT_SAFE_ROOT"]=str(molt)
    env["ARB_PINNED_CONTROL_PLANE_ROOT"]=str(cp)
    env["ARB_PINNED_MOLTBOT_ROOT"]=str(molt)
    env["ARB_PINNED_MANIFEST_FIXTURE"]=env["MOLTBOT_SAFE_MANIFEST_FIXTURE"]

    npm=run(["npm","ci","--ignore-scripts"],cwd=index/"chain")
    setup.append({k:v for k,v in npm.items() if k!="output"})
    if npm["returncode"]: raise RuntimeError(npm["output"])

    suites=[
      ("gax_reference",[sys.executable,"-m","pytest","-q",str(gax/"tests/test_gax_imx_reference.py"),str(gax/"tests/test_gax_imx_redelivery.py")],ROOT),
      ("governed_transport",[sys.executable,"-m","pytest","-q",str(gax/"tests/test_governed_message_transport.py")],ROOT),
      ("governed_transport_integration",[sys.executable,"-m","pytest","-q",str(gax/"tests/test_governed_message_transport_integration.py")],ROOT),
      ("control_plane",[sys.executable,"-m","pytest","-q",str(cp/"tests/test_bounded_authorization.py")],ROOT),
      ("replay",[sys.executable,"-m","pytest","-q",str(replay/"tests")],ROOT),
      ("evidence_pack",[sys.executable,"-m","pytest","-q",str(agep/"tests")],ROOT),
      ("odes",[sys.executable,"-m","pytest","-q",str(odes/"tests")],ROOT),
      ("bitrep_verification",[sys.executable,"-m","pytest","-q",str(bitrep/"tests/test_verification.py"),str(bitrep/"tests/test_api.py")],bitrep),
      ("index_bitrep_binding",[sys.executable,"-m","pytest","-q",str(index/"chain/python/test_bitrep.py")],ROOT),
      ("hub_release_gate",[sys.executable,"-m","pytest","-q",str(ROOT/"tests/test_release_gate.py")],ROOT),
    ]

    runs=[]; representative_runs=[]; normalized=[]
    for repetition in (1,2):
        rdir=out/f"run-{repetition}"
        rdir.mkdir()
        repdir=rdir/"representative"
        rep=run([
            sys.executable,str(ROOT/"tools/transported_reference.py"),
            "--manifest",str(manifest/"examples/refund_integration_v1_1.manifest.json"),
            "--replay",str(replay/"examples/bounded_success_reconstruction_v0_2.json"),
            "--out",str(repdir),
        ],env=env)
        (rdir/"representative.log").write_text(rep["output"],encoding="utf-8")
        rep.update({"repetition":repetition,"log":str((rdir/"representative.log").relative_to(out))})
        rep.pop("output")
        representative_runs.append(rep)
        evo=repdir/"expected-vs-observed.json"
        if rep["returncode"]==0 and evo.exists():
            normalized.append(load:=json.loads(evo.read_text(encoding="utf-8"))["normalized"])
        else:
            normalized.append(None)

        for name,cmd,cwd in suites:
            actual=list(cmd)
            junit=rdir/f"{name}.xml"
            actual.extend(["--junitxml",str(junit)])
            rec=run(actual,cwd=cwd,env=env)
            (rdir/f"{name}.log").write_text(rec["output"],encoding="utf-8")
            rec.update({"suite":name,"repetition":repetition,"log":str((rdir/f"{name}.log").relative_to(out)),"junit":str(junit.relative_to(out))})
            rec.pop("output")
            runs.append(rec)

        node=run(["npm","test"],cwd=index/"chain",env=env)
        (rdir/"index_local_chain.log").write_text(node["output"],encoding="utf-8")
        node.update({"suite":"index_local_chain","repetition":repetition,"log":str((rdir/"index_local_chain.log").relative_to(out))})
        node.pop("output"); runs.append(node)

    representative_repeatable=bool(normalized[0] is not None and normalized[0]==normalized[1])
    (out/"representative-repeatability.json").write_text(json.dumps({
        "passed":representative_repeatable,
        "comparison":"normalized expected outcomes only; generated identifiers and timestamps excluded",
        "run_1":normalized[0],"run_2":normalized[1],
    },indent=2,sort_keys=True),encoding="utf-8")

    matrix_run=run([
        sys.executable,str(ROOT/"tools/release_gate.py"),
        "--matrix",str(ROOT/"scenarios/acceptance-matrix.json"),
        "--results",str(out),
    ],env=env)
    (out/"matrix-resolution.log").write_text(matrix_run["output"],encoding="utf-8")
    matrix_run["log"]="matrix-resolution.log"; matrix_run.pop("output")
    matrix_results={}
    matrix_path=out/"scenario-matrix-results.json"
    if matrix_path.exists():
        matrix_results=json.loads(matrix_path.read_text(encoding="utf-8"))

    acc=components["moltbot_safe_accepted"]
    open_env=env.copy()
    open_env["PYTHONPATH"]=os.pathsep.join([str(cp/"src"),str(acc),open_env.get("PYTHONPATH","")])
    open_env["MOLTBOT_SAFE_ROOT"]=str(acc)
    open_xml=out/"openshell-mock.xml"
    openshell=run([sys.executable,"-m","pytest","-q",str(acc/"tests/test_openshell_environment.py"),"--junitxml",str(open_xml)],env=open_env)
    (out/"openshell-mock.log").write_text(openshell["output"],encoding="utf-8")
    openshell.update({"scope":"mocked adapter only","evidence_state":execution_state if openshell["returncode"]==0 else "blocked","log":"openshell-mock.log","junit":"openshell-mock.xml"})
    openshell.pop("output")

    optional={}
    for name in ("prp","research_intelligence","tfa"):
        failures=static_json_check(components[name])
        optional[name]={"state":execution_state if not failures else "blocked","check":"JSON syntax/static artifact parse only; model-behavior evaluations unexecuted","failures":failures}

    actual_pins={name:run(["git","rev-parse","HEAD"],cwd=path,check=True)["output"].strip() for name,path in components.items()}
    suite_pass=all(x["returncode"]==0 for x in runs)
    representative_pass=all(x["returncode"]==0 for x in representative_runs) and representative_repeatable
    matrix_pass=matrix_run["returncode"]==0 and matrix_results.get("gate_passed") is True

    summary={
      "evidence_state":execution_state,
      "environment":{"python":sys.version,"platform":platform.platform()},
      "setup_commands":setup,
      "actual_pins":actual_pins,
      "representative_runs":representative_runs,
      "representative_repeatability":representative_repeatable,
      "suite_runs":runs,
      "scenario_gate":matrix_results,
      "openshell":openshell,
      "optional_instruction_layers":optional,
      "compatibility":{
        "core_moltbot_pin":LOCK["components"]["moltbot_safe"]["core_interop_sha"],
        "accepted_moltbot_head":LOCK["components"]["moltbot_safe"]["accepted_sha"],
        "moltbot_provenance_gap":LOCK["components"]["moltbot_safe"]["core_interop_sha"]!=LOCK["components"]["moltbot_safe"]["accepted_sha"],
        "gax_public_entrypoint_gap":"accepted GAX runtime resolves Moltbot integration helpers through tests/test_safe_executor.py even though Moltbot exports engine.control_plane_adapter.PinnedControlPlaneExecutor; hub does not patch adjacent repository",
        "transport_replay_retention_gap":"AcceptedGaxRecipientAdapter retains the original GAX Replay bundle identifier but not the original Replay artifact. The hub regenerates Replay only from retained CP/executor records and separately verifies regenerated Replay identity/digest through Evidence Pack and ODES.",
      },
      "live_openshell":{
        "state":"unexecuted",
        "command":"MOLTBOT_SAFE_OPENSHELL_CONFIG=/path/to/qualified-config.json MOLTBOT_SAFE_OPENSHELL_BINARY=/path/to/openshell MOLTBOT_SAFE_OPENSHELL_HOME=/path/to/isolated-home python -m pytest -q .reference-work/moltbot_safe_accepted/tests/test_openshell_live.py",
        "reason":"requires pre-authorized live OpenShell gateway, worker image and isolated home; runner never provisions paid or external infrastructure"
      },
    }
    summary["release_gate_passed"]=bool(suite_pass and representative_pass and matrix_pass and openshell["returncode"]==0)
    (out/"scenario-results.json").write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")
    (out/"component-pins.json").write_text(json.dumps(actual_pins,indent=2,sort_keys=True),encoding="utf-8")
    artifacts=[]
    for f in sorted(out.rglob("*")):
        if f.is_file(): artifacts.append({"path":str(f.relative_to(out)),"sha256":sha256(f),"bytes":f.stat().st_size})
    (out/"artifact-index.json").write_text(json.dumps({"artifacts":artifacts},indent=2),encoding="utf-8")
    print(json.dumps({
        "results_dir":str(out),
        "evidence_state":execution_state,
        "release_gate_passed":summary["release_gate_passed"],
        "representative_repeatable":representative_repeatable,
        "scenario_gate_passed":matrix_pass,
        "openshell_mock":openshell["returncode"]==0,
    },indent=2))
    return 0 if summary["release_gate_passed"] else 1

if __name__=="__main__": raise SystemExit(main())
