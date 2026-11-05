#!/usr/bin/env python3
"""Minimal offline final-pin check for the P1 candidate files (stdlib only; reads JSON; writes nothing).

Why it exists: no other Hub test or required check reads these files (the required checks passed while a pin was
still a placeholder), so nothing else enforces "no placeholder pins, profile and lock shape agree, frozen files
unchanged, Registry identity not substituted". It is a file-consistency check only: it runs no tuple test, records no
pass, and is not a qualification result. It cannot resolve SHAs against GitHub offline; commit/tree pairs were read live
when the files were written (see tuple_identity_verification in the profile).

usage: python3 -I tools/validate_p1_candidate.py [--root HUB_ROOT]      (exit 1 on any error)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ARGS = sys.argv[1:]
ROOT = Path(ARGS[ARGS.index("--root") + 1]) if "--root" in ARGS else Path(__file__).resolve().parent.parent
PROFILE = "profiles/current-stack-integration-candidate-20261105-p1.json"
LOCKSHAPE = "profiles/current-stack-lock-candidate-20261105-p1.json"
MATRIX = "scenarios/acceptance-matrix-p1-20261105.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
VOCAB = {"NOT_ASSESSED", "PARTIALLY_UNCOVERED", "UNCOVERED", "BLOCKED", "OUT_OF_TUPLE_NOT_ASSESSED"}
FROZEN = {  # sha256 at Hub 985dfe46; must stay byte-identical
    "component-lock.json": "dcd3ab9e4e737c7e50f4bc38c2439438f156da64c9eb1e46725f477973da59ff",
    "scenarios/acceptance-matrix.json": "7c4325cdf311e4acc6633cc08d5fd54c0d967bceda32ae25e30e4957975cb7ea",
    "profiles/merged-consumer-chain.json": "d6942c417de29dc9dee42b1ee47fb3189b3f816b380c0425ec6461a251db7509",
    "profiles/full-release-candidate.json": "cf4a6c05fb2d78ddd6d3cb6a7e4e17219478f7ac089b70dcd684ae2cfe281b93",
    "profiles/current-stack-integration-candidate-20261102-r3.json": "b3cf1c909750b8f84b93946b93d1298d8c983ad7aa820f6aa946e9ba273ee5cf",
    "profiles/current-stack-integration-candidate-20261031.json": "7f5b4e425c244504494d41c3608580f24921cef9e70a7334af20600e75af77d4",
    "profiles/w7-bounded-v1-component-lock.candidate.json": "4ed11127adc0a05edde6ae3596ac552e0edb0f318b1177bac0c473ccfd1fca12",
}
# slot: (profile key, lock-shape key, lock-shape field, expected merged SHA, expected repository)
TUPLE = {
    "control_plane": ("control_plane", "control_plane", "sha", "484fdbd297235dd24148ddb0703f2055a31eabff", "cogno-us/cognous-control-plane"),
    "runtime": ("runtime", "moltbot_safe", "core_interop_sha", "f7a55e2a8494801e49193f9f46935f0a971c248d", "cogno-us/cognous-execution-runtime"),
    "manifest": ("manifest", "action_manifest", "sha", "fa170815ef96a54c233d0dd9da821b60debabf8b", "cogno-us/cognous-action-manifest"),
    "replay": ("replay", "replay_bundle", "sha", "93a76e281fcae6a65d2cd1d35376f87442dafb95", "cogno-us/cognous-replay-bundle"),
    "odes": ("odes", "odes", "sha", "1e2261289e8ff8e862b697f5c7afcf7007453787", "cogno-us/open-decision-evidence-standard"),
    "evidence_pack": ("evidence_pack", "governance_evidence_pack", "sha", "065150852cc2a8abeb748777bb69d72ccd0e03d8", "cogno-us/cognous-governance-evidence-pack"),
    "exchange": ("exchange", "gax_imx_transport", "sha", "30169b2033398e89299783f8c600181da71713f3", "cogno-us/cognous-governed-exchange"),
    "verifier": ("verifier", "verifier", "sha", "7caf25411b8be61178b12e71c48eeea7f62d8eb9", "cogno-us/cognous-open-control-stack-verifier"),
    "bitrep": ("bitrep", "bitrep", "sha", "981036c315856c71207984797b0c4e48d3b3921d", "cogno-us/cognous-evidence-attestation"),
}
REGISTRY = ("cogno-us/cognous-ocs-registry", "7de0ec9f8471c7a2ff630eb4035fa24d60b5e2eb")
errors = []


def err(m):
    errors.append(m)


def load(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"cannot read {rel}: {exc}")


for rel, want in FROZEN.items():
    try:
        got = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    except OSError as exc:
        err(f"frozen file unreadable: {rel}: {exc}")
        continue
    if got != want:
        err(f"FROZEN FILE CHANGED: {rel}")

B, A, M, lock = load(PROFILE), load(LOCKSHAPE), load(MATRIX), load("component-lock.json")
if not (B and A and M and lock):
    print(json.dumps({"errors": errors}, indent=1))
    sys.exit(1)

for rel in (PROFILE, LOCKSHAPE, MATRIX):
    text = (ROOT / rel).read_text(encoding="utf-8")
    if re.search(r"TBD|PENDING|PLACEHOLDER", text):
        err(f"{rel}: placeholder token present")

for slot, (bk, ak, af, want, repo) in TUPLE.items():
    bc = B["components"][bk]
    av = A["components"][ak][af]
    if bc["revision"] != want or av != want:
        err(f"{slot}: profile {bc['revision']} / lock shape {av} / expected {want}")
    if not HEX40.match(bc["revision"] or "") or not HEX40.match(bc.get("tree", "")):
        err(f"{slot}: revision or tree is not 40-hex")
    if bc["repository"] != repo or A["components"][ak]["repository"] != repo:
        err(f"{slot}: repository must be {repo}")
if A["components"]["moltbot_safe"]["accepted_sha"] != A["components"]["moltbot_safe"]["core_interop_sha"]:
    err("moltbot_safe accepted_sha != core_interop_sha")
six = [B["components"][k]["revision"] for k in ("control_plane", "runtime", "manifest", "replay", "odes", "evidence_pack")]
if len(set(six)) != 6:
    err("the six GAX tuple constants are not all distinct")
reg = B["components"]["registry"]
if (reg["repository"], reg["revision"]) != REGISTRY or A["recorded_only_components"]["ocs_registry"]["sha"] != REGISTRY[1] or "ocs_registry" in A["components"]:
    err("registry must be cognous-ocs-registry " + REGISTRY[1] + " (recorded only, outside components); never cognous-evidence-registry / the_index")
if A["components"]["the_index"]["repository"] != "cogno-us/cognous-evidence-registry" or A["components"]["the_index"]["sha"] != lock["components"]["the_index"]["sha"]:
    err("the_index row must stay the unchanged lock row (out of the minimal tuple)")

for flag in ("selected", "reference_release_authorized", "production_deployment_authorized", "historical_selected_lock_changed_by_this_file"):
    if B.get(flag) is not False:
        err(f"profile {flag} must be false")
if A.get("selected") is not False or A.get("qualification_status") != "candidate" or "qualification_evidence" in A:
    err("lock shape must be selected=false, qualification_status=candidate, without qualification_evidence")
if B["runtime_profile"] != A["runtime_profile"] or B["runtime_profile"] != "security-runtime-p1-20261105":
    err("runtime_profile mismatch")
for k in ("historical_test_dependencies", "previous_selected_test_dependencies", "previous_accepted_test_dependencies"):
    if A.get(k) != lock.get(k):
        err(f"{k} must equal component-lock.json verbatim")
if "UNQUALIFIED" not in B["labels"] or "adoption not recorded" not in B["governing_constitution"]["adoption"]:
    err("labels must say UNQUALIFIED and 'adoption not recorded'")

ids = set()
for s in M["scenarios"]:
    sid = s["id"]
    if sid in ids:
        err("duplicate scenario id " + sid)
    ids.add(sid)
    if s.get("required") is not True:
        err(f"{sid}: must be required")
    if ("gap" in s) != (("UNCOVERED::" + sid) in s["tests"]):
        err(f"{sid}: a recorded gap and its sentinel reference must go together (a gap cell must never read as passed)")
    if not s["tests"] and "gap" not in s:
        err(f"{sid}: empty tests without a gap")
for r in M["invariant_register"]:
    if r["status"] not in VOCAB:
        err(f"register {r['id']}: status {r['status']!r} outside the vocabulary (no value may mean PASS)")
    for c in r["matrix_cells"]:
        if c not in ids:
            err(f"register {r['id']}: unknown cell {c}")

print(json.dumps({"scenarios": len(M["scenarios"]), "register_entries": len(M["invariant_register"]), "frozen_files_checked": len(FROZEN),
                  "pins_checked": len(TUPLE), "errors": errors}, indent=1))
sys.exit(1 if errors else 0)
