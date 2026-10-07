#!/usr/bin/env python3
"""JUnit-backed acceptance-matrix resolver for the reference release gate."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

STATUSES={"passed","failed","skipped","error"}

def parse_junit(path: Path, suite: str, repetition: int):
    root=ET.parse(path).getroot()
    cases=[]
    for node in root.iter("testcase"):
        name=node.attrib.get("name","")
        classname=node.attrib.get("classname","")
        status="passed"
        reason=""
        for kind in ("failure","error","skipped"):
            child=node.find(kind)
            if child is not None:
                status="failed" if kind=="failure" else kind
                reason=(child.attrib.get("message") or (child.text or "")).strip()
                break
        cases.append({
            "suite":suite,
            "repetition":repetition,
            "name":name,
            "classname":classname,
            "test_id":f"{suite}::{name}",
            "status":status,
            "reason":reason,
            "evidence_path":str(path),
        })
    return cases

def _matches(ref, case):
    if "::" not in ref:
        return False
    suite,name=ref.split("::",1)
    if case["suite"]!=suite:
        return False
    if name=="*":
        return True
    actual=case["name"]
    return actual==name or actual.startswith(name+"[")

def resolve_matrix(matrix, cases, repetitions=(1,2)):
    results=[]
    gate=True
    for scenario in matrix["scenarios"]:
        refs=scenario.get("tests",[])
        required=scenario.get("required",True)
        resolved=[]
        missing=[]
        for ref in refs:
            for rep in repetitions:
                matched=[c for c in cases if c["repetition"]==rep and _matches(ref,c)]
                if not matched:
                    missing.append({"reference":ref,"repetition":rep})
                resolved.extend(matched)
        statuses={c["status"] for c in resolved}
        if missing:
            status="missing"
            reason=f"{len(missing)} required test reference(s) did not resolve"
        elif "failed" in statuses or "error" in statuses:
            status="failed"
            reason="one or more supporting tests failed"
        elif "skipped" in statuses:
            status="skipped"
            reason="required supporting coverage was skipped"
        elif resolved and statuses=={"passed"}:
            status="passed"
            reason="all required references resolved and passed in both repetitions"
        else:
            status="unexecuted"
            reason="no executed supporting test evidence"
        if required and status!="passed":
            gate=False
        classification=scenario.get("classification","required_safety_invariant")
        test_status=status
        if classification=="characterization" and status=="passed":
            status="characterized"
            reason="characterization reproduced; this is not a safety pass"
        results.append({
            "id":scenario["id"],
            "required":required,
            "coverage_scope":scenario.get("coverage_scope","component"),
            "status":status,
            "test_status":test_status,
            "classification":classification,
            "safety_outcome":("not_established" if classification=="characterization" else status),
            "reason":reason,
            "expected":scenario.get("expected"),
            "references":refs,
            "missing":missing,
            "supporting_test_identifiers":[
                {
                    "test_id":c["test_id"],
                    "repetition":c["repetition"],
                    "status":c["status"],
                    "reason":c["reason"],
                    "evidence_path":c["evidence_path"],
                } for c in resolved
            ],
        })
    return gate,results

def skip_accounting(cases, required_results):
    required_ids={
        (x["test_id"],x["repetition"])
        for scenario in required_results if scenario["required"]
        for x in scenario["supporting_test_identifiers"]
    }
    skips=[]
    for c in cases:
        if c["status"]!="skipped":
            continue
        required=(c["test_id"],c["repetition"]) in required_ids
        reason=(c.get("reason") or "").lower()
        missing_prereq=any(token in reason for token in (
            "not supplied","not provided","not configured","checkout","path does not exist","required for this integration test"
        ))
        classification=(
            "required_coverage_skip" if required else
            "missing_integration_prerequisite" if missing_prereq else
            "optional_upstream_skip"
        )
        skips.append({
            **c,
            "classification":classification,
            "blocks_release":required,
        })
    return skips

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--matrix",required=True)
    ap.add_argument("--results",required=True)
    args=ap.parse_args()
    base=Path(args.results)
    cases=[]
    for rep in (1,2):
        rdir=base/f"run-{rep}"
        for path in sorted(rdir.glob("*.xml")):
            if path.name.startswith("representative"):
                continue
            cases.extend(parse_junit(path,path.stem,rep))
    matrix=json.loads(Path(args.matrix).read_text(encoding="utf-8"))
    ok,resolved=resolve_matrix(matrix,cases)
    skips=skip_accounting(cases,resolved)
    out={
        "gate_passed":ok,
        "scenario_count":len(resolved),
        "scenarios":resolved,
        "skip_accounting":skips,
        "collected_test_case_count":len(cases),
    }
    (base/"scenario-matrix-results.json").write_text(json.dumps(out,indent=2,sort_keys=True),encoding="utf-8")
    (base/"skip-accounting.json").write_text(json.dumps({"skips":skips},indent=2,sort_keys=True),encoding="utf-8")
    if not ok:
        raise SystemExit(1)

if __name__=="__main__":
    main()
