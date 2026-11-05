#!/usr/bin/env python3
"""Offline structural checks for the P1 current-stack candidate files (stdlib only; reads JSON; writes nothing).

The candidate is UNQUALIFIED and NOT ADOPTED. This tool checks file consistency only. It does not run any
tuple test, does not establish a pass for any matrix cell, and is not a qualification result.

usage: python3 -I tools/validate_p1_candidate.py [--root HUB_ROOT] [--final] [--gax-file gax_ref_runtime.py]

Without --final the tool passes only while the Governed Exchange pin is still the single documented placeholder.
With --final it FAILS until components.gax_imx_transport.sha in the lock-shape file is a full 40-hex merge SHA.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ARGS = sys.argv[1:]
FINAL = "--final" in ARGS
ROOT = Path(ARGS[ARGS.index("--root") + 1]) if "--root" in ARGS else Path(__file__).resolve().parent.parent
GAX_FILE = ARGS[ARGS.index("--gax-file") + 1] if "--gax-file" in ARGS else None

PROFILE = "profiles/current-stack-integration-candidate-20261105-p1.json"
LOCKSHAPE = "profiles/current-stack-lock-candidate-20261105-p1.json"
MATRIX = "scenarios/acceptance-matrix-p1-20261105.json"
GAX_PLACEHOLDER = "PENDING-GAX-PR68-MERGE-SHA"  # lives ONLY in LOCKSHAPE components.gax_imx_transport.sha
HEX40 = re.compile(r"^[0-9a-f]{40}$")
VOCAB = {"NOT_ASSESSED", "PARTIALLY_UNCOVERED", "UNCOVERED", "BLOCKED", "OUT_OF_TUPLE_NOT_ASSESSED"}
SENTINEL = "UNCOVERED::"

# sha256 of files that must stay byte-identical (values at Hub 985dfe46, the base of this candidate)
FROZEN = {
    "component-lock.json": "dcd3ab9e4e737c7e50f4bc38c2439438f156da64c9eb1e46725f477973da59ff",
    "scenarios/acceptance-matrix.json": "7c4325cdf311e4acc6633cc08d5fd54c0d967bceda32ae25e30e4957975cb7ea",
    "profiles/merged-consumer-chain.json": "d6942c417de29dc9dee42b1ee47fb3189b3f816b380c0425ec6461a251db7509",
    "profiles/full-release-candidate.json": "cf4a6c05fb2d78ddd6d3cb6a7e4e17219478f7ac089b70dcd684ae2cfe281b93",
    "profiles/current-stack-integration-candidate-20261102-r3.json": "b3cf1c909750b8f84b93946b93d1298d8c983ad7aa820f6aa946e9ba273ee5cf",
    "profiles/current-stack-integration-candidate-20261031.json": "7f5b4e425c244504494d41c3608580f24921cef9e70a7334af20600e75af77d4",
    "profiles/w7-bounded-v1-component-lock.candidate.json": "4ed11127adc0a05edde6ae3596ac552e0edb0f318b1177bac0c473ccfd1fca12",
}
FIXED = {  # slot -> (B key, A key, A field, expected full SHA)
    "control_plane": ("control_plane", "control_plane", "sha", "484fdbd297235dd24148ddb0703f2055a31eabff"),
    "runtime": ("runtime", "moltbot_safe", "core_interop_sha", "f7a55e2a8494801e49193f9f46935f0a971c248d"),
    "manifest": ("manifest", "action_manifest", "sha", "fa170815ef96a54c233d0dd9da821b60debabf8b"),
    "replay": ("replay", "replay_bundle", "sha", "93a76e281fcae6a65d2cd1d35376f87442dafb95"),
    "odes": ("odes", "odes", "sha", "1e2261289e8ff8e862b697f5c7afcf7007453787"),
    "evidence_pack": ("evidence_pack", "governance_evidence_pack", "sha", "065150852cc2a8abeb748777bb69d72ccd0e03d8"),
    "verifier": ("verifier", "verifier", "sha", "7caf25411b8be61178b12e71c48eeea7f62d8eb9"),
    "bitrep": ("bitrep", "bitrep", "sha", "981036c315856c71207984797b0c4e48d3b3921d"),
}
REGISTRY_SHA = "7de0ec9f8471c7a2ff630eb4035fa24d60b5e2eb"
GAX_SIX = ("control_plane", "runtime", "manifest", "replay", "odes", "evidence_pack")

errors = []


def err(msg):
    errors.append(msg)


def load(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:  # missing or malformed file is a hard error
        err(f"cannot read {rel}: {exc}")
        return None


for rel, want in FROZEN.items():
    try:
        got = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    except OSError as exc:
        err(f"frozen file unreadable: {rel}: {exc}")
        continue
    if got != want:
        err(f"FROZEN FILE CHANGED: {rel} sha256 {got}")

B, A, M = load(PROFILE), load(LOCKSHAPE), load(MATRIX)
lock = load("component-lock.json")
if not (B and A and M and lock):
    print(json.dumps({"final": FINAL, "errors": errors}, indent=1))
    sys.exit(1)

# ---- the single GAX placeholder -------------------------------------------------------------
gax_sha = A["components"]["gax_imx_transport"]["sha"]
raw = {p: (ROOT / p).read_text(encoding="utf-8") for p in (PROFILE, LOCKSHAPE, MATRIX)}
occurrences = {p: t.count(GAX_PLACEHOLDER) for p, t in raw.items()}
total_ph = sum(occurrences.values())
gax_resolved = bool(HEX40.match(gax_sha))
if gax_resolved:
    if total_ph:
        err(f"GAX pin is a SHA but the placeholder token still appears: {occurrences}")
else:
    if gax_sha != GAX_PLACEHOLDER:
        err(f"GAX pin is neither the placeholder nor a 40-hex SHA: {gax_sha!r}")
    if occurrences[LOCKSHAPE] != 1 or occurrences[PROFILE] or occurrences[MATRIX]:
        err(f"the GAX placeholder must appear exactly once, in {LOCKSHAPE} only: {occurrences}")
if FINAL and not gax_resolved:
    err(f"--final: the GAX pin is still unresolved ({gax_sha}); PR cogno-us/cognous-governed-exchange#68 must be merged and its merge SHA written to {LOCKSHAPE} components.gax_imx_transport.sha")
if B["components"]["exchange"].get("revision") is not None:
    err("profile B must not carry its own GAX revision (single location rule)")
if re.search(r'"(sha|revision)":\s*"(TBD|PENDING)', raw[PROFILE] + raw[MATRIX]):
    err("placeholder-like pin outside the lock-shape file")

# ---- pins ---------------------------------------------------------------------------------------
six = []
for slot, (bk, ak, af, want) in FIXED.items():
    bv, av = B["components"][bk]["revision"], A["components"][ak][af]
    if bv != want:
        err(f"profile pin for {slot} is {bv}, expected {want}")
    if av != want:
        err(f"lock-shape pin for {slot} is {av}, expected {want}")
    if not HEX40.match(bv or ""):
        err(f"profile pin for {slot} is not 40-hex")
    if slot in GAX_SIX:
        six.append(bv)
if A["components"]["moltbot_safe"]["accepted_sha"] != A["components"]["moltbot_safe"]["core_interop_sha"]:
    err("moltbot_safe accepted_sha != core_interop_sha")
if B["components"]["registry"]["revision"] != REGISTRY_SHA or A["recorded_only_components"]["ocs_registry"]["sha"] != REGISTRY_SHA:
    err("registry pin must be cognous-ocs-registry " + REGISTRY_SHA)
if "ocs_registry" in A["components"]:
    err("ocs_registry must stay outside components (the runner checks out every component)")
if B["components"]["registry"]["repository"] != "cogno-us/cognous-ocs-registry":
    err("registry repository must be cogno-us/cognous-ocs-registry, not cognous-evidence-registry")
if len(set(six)) != 6:
    err("the six GAX tuple constants (control_plane, runtime, manifest, replay, odes, evidence_pack) are not all distinct")
if B["components"]["replay"]["revision"] == "fe848cf1e4f6ee272712edc63f5d4bbbfc4e66a7":
    err("replay is pinned to the #87 merge; the tuple requires the #88 merge")
if A["components"]["the_index"] != lock["components"]["the_index"] and {k: v for k, v in A["components"]["the_index"].items() if k != "tuple_membership"} != lock["components"]["the_index"]:
    err("the_index row must equal the lock row (it is out of the minimal tuple)")

# ---- honesty invariants ---------------------------------------------------------------------------
for flag in ("selected", "reference_release_authorized", "production_deployment_authorized", "historical_selected_lock_changed_by_this_file"):
    if B.get(flag) is not False:
        err(f"profile {flag} must be false")
if A.get("selected") is not False or A.get("historical_selected_lock_changed_by_this_file") is not False:
    err("lock-shape selected / historical_selected_lock_changed_by_this_file must be false")
if B["runtime_profile"] != A["runtime_profile"] or B["runtime_profile"] != "security-runtime-p1-20261105":
    err("runtime_profile mismatch or not security-runtime-p1-20261105")
if A.get("qualification_status") != "candidate":
    err("lock-shape qualification_status must be 'candidate'")
if "qualification_evidence" in A:
    err("qualification_evidence (acceptance record of an older tuple) must not be copied")
for k in ("historical_test_dependencies", "previous_selected_test_dependencies", "previous_accepted_test_dependencies"):
    if A.get(k) != lock.get(k):
        err(f"{k} must equal component-lock.json verbatim (the runner dereferences it)")
for word in ("UNQUALIFIED", "NOT ADOPTED"):
    if word not in B["labels"] or word not in A["labels"]:
        err(f"label missing {word}")
if "adoption not recorded" not in B["governing_constitution"]["adoption"]:
    err("constitution wording must say 'adoption not recorded'")

# ---- matrix ---------------------------------------------------------------------------------------
ids = set()
for s in M["scenarios"]:
    sid = s["id"]
    if sid in ids:
        err("duplicate scenario id " + sid)
    ids.add(sid)
    if s.get("required") is not True:
        err(f"{sid}: every cell must be required")
    for ref in s["tests"]:
        if "::" not in ref:
            err(f"{sid}: bad reference {ref}")
    if not s["tests"] and "gap" not in s:
        err(f"{sid}: empty tests without a recorded gap")
    if "gap" in s and (SENTINEL + sid) not in s["tests"]:
        err(f"{sid}: a recorded gap needs the sentinel reference so the cell cannot read as passed")
    if SENTINEL in "".join(s["tests"]) and "gap" not in s:
        err(f"{sid}: sentinel without a gap text")
    for k in ("assessment", "coverage_class"):
        if k not in s:
            err(f"{sid}: missing {k}")
    if "PASS" in str(s.get("assessment", "")).upper().replace("NO RESULT", ""):
        err(f"{sid}: assessment must not claim a pass")
reg_ids = set()
for r in M["invariant_register"]:
    if r["id"] in reg_ids:
        err("duplicate register id " + r["id"])
    reg_ids.add(r["id"])
    if r["status"] not in VOCAB:
        err(f"register {r['id']}: status {r['status']!r} not in the vocabulary (no value may mean PASS)")
    for c in r["matrix_cells"]:
        if c not in ids:
            err(f"register {r['id']}: unknown matrix cell {c}")
for need in ("I-09", "I-17", "I-18", "XC-1", "XC-3", "TB"):
    if need not in reg_ids:
        err(f"register is missing {need}")
for need in ("p1.unsupported.runtime_tenant_aware_execution", "p1.unsupported.caller_asserted_labels", "p1.unsupported.shared_runtime_two_label_admission",
             "p1.unsupported.gax_authority_lifecycle_and_redelivery", "p1.out_of_tuple.I-09_evidence_registry_source_verification", "p1.out_of_tuple.I-17_I-18_ergonomics"):
    if need not in ids:
        err(f"matrix is missing the explicit cell {need}")

# ---- optional: GAX profile block constants equal the tuple ------------------------------------------------
if GAX_FILE:
    src = Path(GAX_FILE).read_text(encoding="utf-8")
    m = re.search(r'elif RUNTIME_COMPATIBILITY_PROFILE == "' + re.escape(B["runtime_profile"]) + r'":(.*?)\n(?=elif |\S)', src, re.S)
    if not m:
        err("GAX profile block not found in " + GAX_FILE)
    else:
        found = set(re.findall(r"[0-9a-f]{40}", m.group(1)))
        if found != set(six):
            err("GAX block constants differ from the tuple: " + ", ".join(sorted(found ^ set(six))))

print(json.dumps({
    "final": FINAL,
    "gax_pin": "RESOLVED" if gax_resolved else "UNRESOLVED (single placeholder in " + LOCKSHAPE + ")",
    "placeholder_occurrences": occurrences,
    "scenarios": len(M["scenarios"]),
    "register_entries": len(M["invariant_register"]),
    "frozen_files_checked": len(FROZEN),
    "errors": errors,
}, indent=1))
sys.exit(1 if errors else 0)
