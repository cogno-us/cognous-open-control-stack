#!/usr/bin/env python3
"""Run and gate same-host process-boundary qualification against exact pins."""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCK=json.loads((ROOT/"component-lock.json").read_text())
MATRIX_PATH=ROOT/"scenarios/process-boundary-matrix.json"
WORK=ROOT/".process-boundary-work"
NAMES=("action_manifest","control_plane","gax_imx_transport","moltbot_safe","replay_bundle")
PASS_CLASSIFICATION="supported invariant passed"


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


def _junit_cases(path: Path) -> list[dict]:
    if not path.exists():
        return []
    cases=[]
    for case in ET.parse(path).getroot().iter("testcase"):
        state="passed"
        if case.find("failure") is not None: state="failed"
        elif case.find("error") is not None: state="error"
        elif case.find("skipped") is not None: state="skipped"
        cases.append({"name":case.get("name"),"classname":case.get("classname"),"state":state})
    return cases


def evaluate_required_scenarios(matrix: dict, junit_path: Path, evidence_dir: Path, repetition: int) -> dict:
    """Resolve required matrix cases against JUnit and evidence; fail closed."""
    junit=_junit_cases(junit_path)
    resolved=[]; failures=[]
    for case in matrix.get("cases",[]):
        if not case.get("required"):
            continue
        scenario_id=case.get("id")
        expected_test="test_"+str(scenario_id).replace("-","_")
        matches=[x for x in junit if x.get("name")==expected_test]
        evidence_path=evidence_dir/f"{scenario_id}.json"
        evidence=None; evidence_error=None
        if evidence_path.exists():
            try: evidence=json.loads(evidence_path.read_text(encoding="utf-8"))
            except Exception as exc: evidence_error=f"invalid evidence JSON: {exc}"
        reasons=[]
        if len(matches)!=1:
            reasons.append(f"expected exactly one JUnit case {expected_test}, found {len(matches)}")
        elif matches[0]["state"]!="passed":
            reasons.append(f"JUnit case {expected_test} state is {matches[0]['state']}")
        if evidence is None:
            reasons.append(evidence_error or "matching scenario evidence missing")
        else:
            if evidence.get("scenario_id")!=scenario_id:
                reasons.append("scenario evidence identity mismatch")
            if evidence.get("repetition")!=repetition:
                reasons.append("scenario evidence repetition mismatch")
            if evidence.get("classification")!=PASS_CLASSIFICATION:
                reasons.append(f"required scenario classification is {evidence.get('classification')!r}")
        item={"scenario_id":scenario_id,"required":True,"expected_test":expected_test,
              "junit_matches":matches,"evidence_path":str(evidence_path),
              "evidence_classification":evidence.get("classification") if isinstance(evidence,dict) else None,
              "passed":not reasons,"reasons":reasons}
        resolved.append(item)
        if reasons: failures.append({"scenario_id":scenario_id,"reasons":reasons})
    return {"passed":not failures,"required_count":len(resolved),"resolved":resolved,"failures":failures}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["run"])
    ap.add_argument("--results-dir",default="results/process-boundary")
    args=ap.parse_args()
    out=(ROOT/args.results_dir).resolve()
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    matrix=json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    if matrix.get("baseline")!="b457b7e1ebcbb323e88e85b913eaafcb5755317a":
        raise RuntimeError("process-boundary matrix baseline does not match accepted hub baseline")
    if matrix.get("repetitions")!=2:
        raise RuntimeError("process-boundary matrix must require exactly two repetitions")
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
        scenarios=[]
        if evidence.exists():
            for p in sorted(evidence.glob("*.json")):
                scenarios.append(json.loads(p.read_text()))
        matrix_gate=evaluate_required_scenarios(matrix,junit,evidence,rep)
        (rdir/"matrix-gate.json").write_text(json.dumps(matrix_gate,indent=2,sort_keys=True),encoding="utf-8")
        run_passed=rec["returncode"]==0 and matrix_gate["passed"]
        if not run_passed: overall=1
        runs.append({"repetition":rep,"returncode":rec["returncode"],"matrix_gate_passed":matrix_gate["passed"],
                     "qualification_repetition_passed":run_passed,"seconds":rec["seconds"],
                     "junit":str(junit.relative_to(out)),"matrix_gate":str((rdir/"matrix-gate.json").relative_to(out)),
                     "log":str((rdir/"pytest.log").relative_to(out)),"totals":junit_counts(junit),"scenarios":scenarios})
    classes={}
    for r in runs:
        for s in r["scenarios"]:
            classes[s["classification"]]=classes.get(s["classification"],0)+1
    summary={"schema_version":"1.1","hub_baseline":"b457b7e1ebcbb323e88e85b913eaafcb5755317a","component_pins":pins,
             "scenario_matrix":"scenarios/process-boundary-matrix.json","required_scenario_count":sum(1 for c in matrix["cases"] if c.get("required")),
             "repetitions":runs,"classification_totals":classes,"qualification_exit":overall,
             "scope_limitations":["same-host shared-database only","no distributed budgets","no remote exactly-once delivery","no authenticated observations","no destination finality"]}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"results_dir":str(out),"qualification_exit":overall,"classification_totals":classes,
                      "matrix_gates":{str(r["repetition"]):r["matrix_gate_passed"] for r in runs},
                      "test_totals":{str(r["repetition"]):r["totals"] for r in runs}},indent=2))
    return overall


if __name__=="__main__":
    raise SystemExit(main())
