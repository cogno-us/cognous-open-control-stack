#!/usr/bin/env python3
"""Build (or --check) the QGATE-05 successor candidate manifest.

Stdlib only, deterministic, no network. Every digest is RECOMPUTED from the files
passed on the command line; nothing is copied from the historical manifest except
structure, schema keys and prose that has no digest behind it. The historical
manifest (docs/mvp-package/candidate-manifest.json) is read, never written.

Registered inconsistencies handled (hub docs/mvp-recovery/qgate-04/freeze-reconciliation.md):
R-01 identity-inputs and tuple-pin digests, R-02 Qualification reference, R-03 registry
catalogue digest, R-04 hub provenance revision history, R-05 "is the main head" wording,
R-06 oracle / battery / environment profile / commitment references.

The script never edits component-lock.json, never substitutes a branch head for a pin,
and leaves `candidate_commitment_sha256` empty unless --external-commitment-sha is given.

Usage (generate):
  python3 build_successor_manifest.py --qa-root DIR --tuple-pin FILE \
      --oracle-v7 FILE [--oracle-v8 FILE] --battery-v1 FILE [--battery-v2 FILE] \
      --profile FILE --commitment FILE [--external-commitment-sha HEX] [--out FILE]
Usage (verify): same arguments plus --check (recomputes in memory, compares byte for byte
with --out, exits non-zero on any mismatch).
"""
import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HUB_ROOT_DEFAULT = Path(__file__).resolve().parents[3]
OLD_MANIFEST_REL = "docs/mvp-package/candidate-manifest.json"
DEFAULT_OUT_REL = "docs/mvp-package/candidate-manifest.successor-2026-10-31.json"
LOCK_REL = "component-lock.json"
REQ_REL = "docs/mvp-package/requirements-mvp-py313.txt"
QA_LOCK_REL = ".github/locks/cryptography-pydantic-pytest-a9a750.txt"
QA_IDENTITY_REL = "process/mvp-acceptance/candidate-identity.inputs.json"
QA_V6_REL = "process/mvp-chain/expectations.proposed.v6.json"
HUB_PROFILE_DOC_REL = "docs/mvp-recovery/ingress-qualification-environment-profile.md"
HUB_BOUNDARY_REL = "tools/mvp_ingress/BOUNDARY.md"
HUB_CAPTURE_REL = "tools/mvp_env_record/capture_env_record.py"
HUB_INGRESS_DIR_REL = "tools/mvp_ingress"
HUB_ENVREC_DIR_REL = "tools/mvp_env_record"
REGISTRY_MANIFEST_REL = "docs/mvp-recovery/registry/catalogue-v0.1/manifest.json"

COMPONENT_KEYS = ["control_plane", "runtime", "replay", "evidence_pack", "odes",
                  "action_manifest", "verifier", "hub"]
# Information only (INFORMATION, not recomputed here): default-branch heads observed by the
# QGATE-04 worker on 2026-10-31, hub docs/mvp-recovery/qgate-04/freeze-reconciliation.md section 1.
INFO_HEADS = {
    "control_plane": ("b19c47ddd020409d24e52e70b11359c46265edbb", "pin is older than head (+72 per readiness report C)"),
    "runtime": ("f7a55e2a8494801e49193f9f46935f0a971c248d", "pin is older than head (+34, behaviorally different)"),
    "replay": ("40012b8c174c6f25685bd5d9bc93ff46cc9a5842", "equals head"),
    "evidence_pack": ("7b9511f2c6d56d424f17b078826594abd29f6c96", "equals head"),
    "odes": ("1a5e1d300250d832e611633f0bf8f762e398c0ec", "equals head"),
    "action_manifest": ("fa170815ef96a54c233d0dd9da821b60debabf8b", "equals head"),
    "verifier": ("39d46b494558e271439966bec98b26dc4d040cc4", "pin is older than head (one later docs-only commit; ruling Q4; not adopted)"),
    "hub": ("c40bfcd893f2e313b683fc589ad5b1abd0e1b76e", "pin is older than hub main; tools/mvp_ingress and tools/mvp_env_record tree ids identical at both"),
}
HUB_SUPERSEDED_HISTORY = [
    {"revision": "5b76c58a8bacb9efe6ed6c08e51ab7db7d03bc12", "where_named": "draft manifest, dependency-manifest.md, source-inventory.md, Qualification PR #226 pin (hub #219)"},
    {"revision": "e7c7183687e756ccf839435ef2959fcafa126cdf", "where_named": "manifest 2026-10-24 discrepancy prose"},
]
OLD_STALE_VALUES = {
    "candidate_identity_inputs_sha256": "0ef8f3fd590bfbc58172735c05aca3b95a97c8dea7af59383c7cf4a938461aa6",
    "tuple_pin_sha256": "bde38aa8aacedf17bf071904aa6dd401d72321ac845567e9551ffdfb6590f4f7",
    "qualification_main": "4298247e860126d04d0bc44e1f2aef0fde1c4c97",
    "registry_catalogue_digest": "sha256:d6c768c9daae6c31e9c8e5a184f6ddb56f76733ab86cda009f2fb771f00c8057",
}
HEX40 = set("0123456789abcdef")


class Fail(Exception):
    pass


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def need_file(p, what):
    p = Path(p)
    if not p.is_file():
        raise Fail("%s not found: %s" % (what, p))
    return p


def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def ingress_tree_digest(d):
    """Manifest algorithm: sha256 over the text of base name, NUL, file sha256, newline for each
    direct *.py file sorted by base name."""
    d = Path(d)
    files = sorted(x.name for x in d.iterdir() if x.is_file() and x.name.endswith(".py"))
    if not files:
        raise Fail("no *.py files in %s" % d)
    text = "".join("%s\0%s\n" % (n, sha256_file(d / n)) for n in files)
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), files


def git(args, cwd):
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True, env=env)
    return r.stdout.strip() if r.returncode == 0 else None


def rel_for_record(path, root):
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(path)


def artifact(path, qa_root, required, label):
    if path is None:
        if required:
            raise Fail("%s is required" % label)
        return {"path": None, "sha256": None, "status": "not supplied to this build; supply the final file and rebuild"}
    p = need_file(path, label)
    return {"path": rel_for_record(p, qa_root), "sha256": sha256_file(p)}


def build(args):
    hub = Path(args.hub_root).resolve()
    qa = Path(args.qa_root).resolve()
    old_path = need_file(hub / OLD_MANIFEST_REL, "historical manifest")
    old = load_json(old_path)
    lock_p = need_file(hub / LOCK_REL, "component-lock.json")
    req_p = need_file(hub / REQ_REL, "hub requirements lock")
    qalock_p = need_file(qa / QA_LOCK_REL, "Qualification lock")
    ident_p = need_file(args.identity_inputs or (qa / QA_IDENTITY_REL), "candidate identity inputs")
    pin_p = need_file(args.tuple_pin, "tuple pin")
    reg_p = need_file(hub / REGISTRY_MANIFEST_REL, "registry catalogue manifest")

    # 1. tuple pins: tuple-pin file vs identity inputs vs historical manifest must agree exactly.
    pin = load_json(pin_p)["components"]
    ident = load_json(ident_p)
    old_rev = {c["component"]: c["revision"] for c in old["components"]}
    for k in COMPONENT_KEYS:
        sha = pin[k]["sha"]
        if len(sha) != 40 or set(sha) - HEX40:
            raise Fail("tuple pin %s is not a full 40-hex sha: %r" % (k, sha))
        if ident["components"][k]["sha"] != sha:
            raise Fail("identity inputs and tuple pin disagree for %s" % k)
        if old_rev[k] != sha:
            raise Fail("historical manifest names a different revision for %s" % k)

    # 2. locks must be unmoved (R-07): the historical lock hash is a precondition, not an output.
    lock_sha = sha256_file(lock_p)
    old_lock_sha = old["hub_lock_notice"]["sha256"]
    if lock_sha != old_lock_sha:
        raise Fail("component-lock.json moved: %s != recorded %s" % (lock_sha, old_lock_sha))
    req_sha = sha256_file(req_p)
    qalock_sha = sha256_file(qalock_p)
    if req_sha != qalock_sha:
        raise Fail("hub requirements lock and Qualification lock differ: %s vs %s" % (req_sha, qalock_sha))
    if ident["composite"]["python"]["lock_files_sha256"].get(QA_LOCK_REL) != qalock_sha:
        raise Fail("identity inputs declare a different lock sha than the Qualification lock file")

    # 3. recomputed digests
    ident_sha = sha256_file(ident_p)
    pin_sha = sha256_file(pin_p)
    qa_sha = args.qa_sha or git(["rev-parse", "HEAD"], qa)
    if not qa_sha or len(qa_sha) != 40 or set(qa_sha) - HEX40:
        raise Fail("cannot determine the Qualification reference sha (not a git tree and no --qa-sha)")
    reg_digest = load_json(reg_p)["digest"]
    prof_art = artifact(args.profile, qa, True, "environment profile")
    if ident["composite"]["environment_profile"]["sha256"] != prof_art["sha256"]:
        raise Fail("identity inputs declare environment profile sha %s, recomputed %s"
                   % (ident["composite"]["environment_profile"]["sha256"], prof_art["sha256"]))
    if reg_digest != ident["composite"]["hub"]["registry_catalogue_manifest"]["digest"]:
        raise Fail("live registry digest %s != identity inputs digest" % reg_digest)
    cm_art = artifact(args.commitment, qa, True, "commitment file")
    cm_sha = cm_art["sha256"]
    ext = args.external_commitment_sha
    if ext:
        if len(ext) != 64 or set(ext.lower()) - set("0123456789abcdef"):
            raise Fail("--external-commitment-sha is not a 64-hex sha256")
        if ext.lower() != cm_sha:
            raise Fail("externally recorded commitment %s != recomputed %s" % (ext.lower(), cm_sha))
        ext = ext.lower()
    v6 = qa / QA_V6_REL
    arts = {
        "oracle_v6_historical": artifact(v6, qa, True, "oracle v6"),
        "oracle_v7": artifact(args.oracle_v7, qa, True, "oracle v7"),
        "oracle_v8": artifact(args.oracle_v8, qa, args.require_final, "oracle v8"),
        "battery_v1": artifact(args.battery_v1, qa, True, "battery v1"),
        "battery_v2": artifact(args.battery_v2, qa, args.require_final, "battery v2"),
        "environment_profile": prof_art,
        "commitment_file": dict(cm_art, recomputed_as="sha256 of file bytes (gate sha256_file, tools/mvp_acceptance_gate.py)"),
    }
    arts["oracle_v7"]["note"] = "byte-pinned, never edited (v8 is a NEW file)"
    arts["battery_v1"]["note"] = "never edited (v2 is a NEW file)"

    hub_profile = need_file(hub / HUB_PROFILE_DOC_REL, "hub profile doc")
    hub_boundary = need_file(hub / HUB_BOUNDARY_REL, "BOUNDARY.md")
    hub_capture = need_file(hub / HUB_CAPTURE_REL, "capture script")
    tree_sha, tree_files = ingress_tree_digest(hub / HUB_INGRESS_DIR_REL)
    comp_ident = ident["composite"]["hub"]
    if comp_ident["capture_script_sha256"] != sha256_file(hub_capture):
        raise Fail("capture script sha differs from identity inputs composite")
    hub_tree_ids = {HUB_INGRESS_DIR_REL: git(["rev-parse", "HEAD:" + HUB_INGRESS_DIR_REL], hub),
                    HUB_ENVREC_DIR_REL: git(["rev-parse", "HEAD:" + HUB_ENVREC_DIR_REL], hub)}
    for k, v in comp_ident["git_tree_ids"].items():
        if hub_tree_ids.get(k) is not None and hub_tree_ids[k] != v:
            raise Fail("hub tree id for %s is %s, identity inputs say %s" % (k, hub_tree_ids[k], v))

    # 4. assemble the successor from the historical structure
    m = copy.deepcopy(old)
    m["manifest_id"] = "ocs-mvp-candidate-manifest-successor-2026-10-31"
    m["supersedes_manifest"] = {
        "manifest_id": old["manifest_id"], "path": OLD_MANIFEST_REL, "sha256": sha256_file(old_path),
        "state": "historical; left byte-identical; superseded in metadata only (R-01..R-06); the tuple SHAs in it are correct",
    }
    m["created"] = args.created
    m["status_note"] = (old["status_note"] + " This successor (QGATE-05) repairs source-backed metadata only: digests are recomputed by "
                        "docs/mvp-recovery/qgate-05/build_successor_manifest.py and checked with --check; no pin, oracle, lock or production "
                        "file is changed or substituted. It is not a freeze; a freeze requires the Qualification Owner approval record.")
    m["hub_lock_notice"]["sha256"] = lock_sha
    m["hub_lock_notice"]["statement"] += (" QGATE-05 successor note: the lock is re-hashed by the build and the build refuses to run if it moved "
                                         "(R-07). The lock is a historical record; the qualification tuple is this manifest and "
                                         "process/mvp-chain/tuple-pin.proposed.json. They are deliberately different and must not be mixed.")
    for c in m["components"]:
        k = c["component"]
        c["revision"] = pin[k]["sha"]
        head, rel = INFO_HEADS[k]
        old_prov = c["provenance"]
        c["provenance"] = ("HISTORY (2026-10-24): " + old_prov + ". Superseded wording (R-05): 'main head' was true on 2026-10-24 only. "
                           "Tuple pin is unchanged and is never replaced by a head.")
        c["information_only_current_head"] = {
            "default_branch_head_2026_10_31": head, "relation_to_pin": rel,
            "substituted_for_pin": False, "pin_equals_head": head == pin[k]["sha"],
            "source": "docs/mvp-recovery/qgate-04/freeze-reconciliation.md section 1 (OBSERVED by the QGATE-04 worker 2026-10-31; not re-observed by this build)",
        }
        if k == "hub":
            c["origin"] = old["components"][[x["component"] for x in old["components"]].index("hub")]["origin"]
            c["superseded_history_revisions"] = HUB_SUPERSEDED_HISTORY
            c["history_note"] = ("R-04: the 2026-10-24 manifest prose named e7c71836 and Qualification #226 named 5b76c58a; the component list and both "
                                 "Qualification files name c897266b, which is the only hub provenance revision of this candidate.")
    rt = m["runtime_and_dependencies"]["dependency_lock"]
    rt["sha256"] = req_sha
    rt["identical_to_qualification_lock"] = ("cogno-us/cognous-stack-qualification %s: same sha256 %s, recomputed by this build from both files" % (QA_LOCK_REL, qalock_sha))

    q = m["qualification_references"]
    q["main"] = qa_sha
    q["main_provenance"] = "RECOMPUTED by this build: git rev-parse HEAD of the supplied Qualification tree (or --qa-sha); supersedes the 2026-10-24 value"
    q["superseded_main_history"] = [OLD_STALE_VALUES["qualification_main"]]
    for d in q["builder_prepared_drafts"]:
        d["historical"] = True
        d["head_provenance"] = "HISTORY, point-in-time record of 2026-10-24 (R-02); not a current head and not relied on"
    q["commitment_hashes_reported"] = {
        "candidate_identity_inputs_sha256": ident_sha,
        "tuple_pin_sha256": pin_sha,
        "basis": "RECOMPUTED by this build: sha256 of file bytes of the identity-inputs and tuple-pin files supplied on the command line, at Qualification %s" % qa_sha,
        "superseded_values_history": {"candidate_identity_inputs_sha256": OLD_STALE_VALUES["candidate_identity_inputs_sha256"],
                                     "tuple_pin_sha256": OLD_STALE_VALUES["tuple_pin_sha256"]},
        "files": {"identity_inputs": rel_for_record(ident_p, qa), "tuple_pin": rel_for_record(pin_p, qa)},
    }
    q["artifacts"] = arts
    q["candidate_commitment_sha256"] = ext if ext else ""
    q["candidate_commitment_note"] = ("Produced and recorded by Qualification outside its checkout. Never set by this manifest: it is empty unless the externally "
                                      "recorded value is passed with --external-commitment-sha, in which case it must equal the recomputed file sha256. "
                                      "The recomputed file digest is shown under artifacts.commitment_file for comparison only.")
    # keep the old schema key at top level of qualification_references (it was there in the old manifest)
    # (candidate_commitment_sha256 already lives in qualification_references)

    e = m["environment_and_configuration"]
    e["hub_profile_document"]["sha256"] = sha256_file(hub_profile)
    e["ingress_boundary_document"]["sha256"] = sha256_file(hub_boundary)
    e["capture_script"]["sha256"] = sha256_file(hub_capture)
    e["ingress_tree"]["sha256"] = tree_sha
    if tree_files != sorted(f for f in e["ingress_tree"]["expected_files"] if f.endswith(".py")):
        raise Fail("*.py files under tools/mvp_ingress differ from the expected list: %s" % tree_files)
    e["ingress_tree"]["git_tree_id"] = comp_ident["git_tree_ids"][HUB_INGRESS_DIR_REL]
    e["env_record_tree"]["git_tree_id"] = comp_ident["git_tree_ids"][HUB_ENVREC_DIR_REL]
    e["ingress_tree"]["digest_basis"] = "RECOMPUTED by this build from the supplied hub tree; tree ids are the git tree ids at the hub provenance revision, cross-checked against the hub checkout when it is a git tree"
    e["ipc_directory_mode"] = {
        "bounded_synthetic_test_configuration": "2751",
        "scope": "TEST configuration only (Architect D3 ratified, Issue #215 comment 6537418060); socket mode 0660, peer-UID allowlisting; not production; the original supported profile text (2750) is unchanged and not relaxed",
        "historical_evidence": "the 2750 capture evidence is preserved and immutable",
        "accepted_residual": "an outsider can stat a known socket name; no connect, listing or state disclosure",
    }
    e["environment_profile_reference"] = prof_art

    r = m["registry_catalogue"]["manifest_digest"]
    r["value"] = reg_digest
    r["status"] = "current"
    r["superseded_values_history"] = [OLD_STALE_VALUES["registry_catalogue_digest"]]
    r["successor_value"] = None
    r["successor_pull_request"] = ident["composite"]["hub"]["registry_catalogue_manifest"]["hub_pr"]
    r["update_rule"] = ("RECOMPUTED by this build from the live file's digest field (R-03); the earlier superseded-pending digest is history. "
                        "Only the digest field of the live file is read.")
    m["excluded_claims"] = list(old["excluded_claims"]) + [
        "the QGATE-05 metadata repair is not a freeze, Qualification verdict, certification, Q7, Tier 1, release, publication or production statement",
    ]
    return m


def render(m):
    return json.dumps(m, indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qa-root", required=True)
    ap.add_argument("--tuple-pin", required=True)
    ap.add_argument("--identity-inputs")
    ap.add_argument("--oracle-v7", required=True)
    ap.add_argument("--oracle-v8")
    ap.add_argument("--battery-v1", required=True)
    ap.add_argument("--battery-v2")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--commitment", required=True)
    ap.add_argument("--external-commitment-sha", default="")
    ap.add_argument("--qa-sha", default="")
    ap.add_argument("--hub-root", default=str(HUB_ROOT_DEFAULT))
    ap.add_argument("--out")
    ap.add_argument("--created", default="2026-10-31")
    ap.add_argument("--require-final", action="store_true", help="refuse a build without oracle v8 and battery v2")
    ap.add_argument("--check", action="store_true", help="recompute and compare byte for byte with --out; exit 1 on mismatch")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else Path(a.hub_root) / DEFAULT_OUT_REL
    try:
        text = render(build(a))
    except (Fail, KeyError, OSError, ValueError) as ex:
        print("FAIL: %s" % ex, file=sys.stderr)
        return 2
    if a.check:
        if not out.is_file():
            print("CHECK FAIL: %s does not exist" % out, file=sys.stderr)
            return 1
        have = out.read_text(encoding="utf-8")
        if have != text:
            import difflib
            for line in list(difflib.unified_diff(have.splitlines(), text.splitlines(), "recorded", "recomputed", lineterm="", n=0))[:40]:
                print(line, file=sys.stderr)
            print("CHECK FAIL: recomputed manifest differs from %s" % out, file=sys.stderr)
            return 1
        print("CHECK OK: %s matches recomputation (sha256 %s)" % (out, hashlib.sha256(text.encode("utf-8")).hexdigest()))
        return 0
    if a.stdout:
        sys.stdout.write(text)
        return 0
    out.write_text(text, encoding="utf-8")
    print("wrote %s sha256 %s" % (out, hashlib.sha256(text.encode("utf-8")).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
