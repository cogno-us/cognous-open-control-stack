#!/usr/bin/env python3
"""Deterministic offline validator for the OCS MVP candidate manifest.

Non-authorizing. This tool checks that the manifest is internally consistent and
that the files it names in this repository still hash to the recorded values.
It produces no verdict about the candidate tuple. Qualification owns verdicts.

Offline checks need only the Python standard library and a checkout.
--online additionally asks GitHub REST (through the gh CLI) whether each pinned
revision is an ancestor of, or equal to, the main branch of its repository.

Exit status: 0 when every check holds, 1 when any check fails, 2 on usage or
unreadable input.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = "cognous.ocs-mvp-candidate-manifest/1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_COMPONENTS = ("control_plane", "runtime", "replay", "evidence_pack", "odes",
                       "action_manifest", "verifier", "hub")
LATER_DOC_VERIFIER = "39d46b494558e271439966bec98b26dc4d040cc4"
CATALOGUE_STATUSES = ("superseded-pending", "superseded", "current")
TOP_REQUIRED = ("schema", "manifest_id", "created", "status", "provisional", "status_note", "authorization",
                "hub_lock_notice", "components", "later_documentation_revisions", "excluded_components",
                "runtime_and_dependencies", "qualification_references", "environment_and_configuration",
                "registry_catalogue", "evidence_and_test_runs", "excluded_claims")
# Wording guard. Text is lowercased and has whitespace, hyphens and underscores normalized to single spaces.
# A listed term may appear only directly after an explicit negation ("not <term>", "no <term>", "does not claim <term>").
FORBIDDEN_TERMS = ("pass", "passes", "passed", "fail", "fails", "failed", "qualified", "frozen", "accepted", "approved",
                   "released", "certified", "compliant", "production ready", "security cleared", "verdict issued")
TERM_RE = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(t) for t in sorted(FORBIDDEN_TERMS, key=len, reverse=True)))
NEG_BEFORE = re.compile(r"(?:\bnot|\bno|\bnever|\bwithout|\bnor|\bneither|\bnone)\s+(?:(?:an?|any|the|yet|been|implicitly|is|was|are|be|claim)\s+)*$")
BOOL_CLAIM_KEY = re.compile(r"(?:^|_)(qualified|frozen|accepted|certified|approved|released|passed)$", re.I)
EXPECTED_COMPONENTS = {
    "control_plane": ("cogno-us/cognous-control-plane", "7a4bcd40b3b49e61ff3c294dcca53b52f460b22c"),
    "runtime": ("cogno-us/cognous-execution-runtime", "c5e97e87dd239c821b1b4a406a55dcd03c5bc61f"),
    "replay": ("cogno-us/cognous-replay-bundle", "40012b8c174c6f25685bd5d9bc93ff46cc9a5842"),
    "evidence_pack": ("cogno-us/cognous-governance-evidence-pack", "7b9511f2c6d56d424f17b078826594abd29f6c96"),
    "odes": ("cogno-us/open-decision-evidence-standard", "1a5e1d300250d832e611633f0bf8f762e398c0ec"),
    "action_manifest": ("cogno-us/cognous-action-manifest", "fa170815ef96a54c233d0dd9da821b60debabf8b"),
    "verifier": ("cogno-us/cognous-open-control-stack-verifier", "c0b8ba1f55b75db787a320f3de0f79342c6f6826"),
}
EXPECTED_HUB_REPOSITORY = "cogno-us/cognous-open-control-stack"
EXPECTED_REGISTRY_DIGEST = "sha256:d6c768c9daae6c31e9c8e5a184f6ddb56f76733ab86cda009f2fb771f00c8057"
EXPECTED_INGRESS_TREE_ID = "656b506d752fb9241181097689054342a8d8fe86"
EXPECTED_ENV_RECORD_TREE_ID = "b446e30acd8727be29a1ebc0204d947874035514"
EXPECTED_ENV_RECORD_FILES = ("capture_env_record.py",)
EXPECTED_INGRESS_FILES = ("BOUNDARY.md", "__init__.py", "client.py", "core.py", "launch.py", "proposal.py", "server.py", "synthetic_host.py")
EXPECTED_INGRESS_DIGEST = "0c0e2cf6a69f4ce69d4ca39ac7a443890a05b50ba420902e2d346912d369f591"
EXPECTED_HUB_REVISION = "330ccc315b40d7c32041ab50e0de48ee0fda0ec3"  # hub provenance revision: merge of PR #230


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def ingress_tree_digest(directory, pattern="*.py"):
    """sha256 over 'basename NUL file-sha256 NEWLINE' lines, files sorted by base name."""
    files = sorted(Path(directory).glob(pattern), key=lambda p: p.name)
    if not files:
        raise FileNotFoundError("no files match %s in %s" % (pattern, directory))
    text = "".join("%s\0%s\n" % (p.name, sha256_bytes(p.read_bytes())) for p in files)
    return sha256_bytes(text.encode("utf-8"))


def _strings(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _strings(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, "%s[%d]" % (path, i))


def _keys(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield "%s.%s" % (path, k), k, v
            yield from _keys(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _keys(v, "%s[%d]" % (path, i))


def _pairs_no_dupes(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise ValueError("duplicate JSON key %r" % k)
        seen.add(k)
    return dict(pairs)


def load_manifest(path):
    raw = Path(path).read_bytes()
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs_no_dupes), raw


def _rev(errors, where, value):
    if not isinstance(value, str) or not HEX40.match(value):
        errors.append("%s: not a full 40-hex lowercase sha (%r)" % (where, value))
        return False
    return True


def check_structure(m, errors):
    for k in TOP_REQUIRED:
        if k not in m:
            errors.append("missing required field %s" % k)
    if m.get("schema") != SCHEMA:
        errors.append("schema must be %s" % SCHEMA)
    if m.get("status") != "UNQUALIFIED":
        errors.append("status must be exactly UNQUALIFIED")
    if m.get("provisional") is not True:
        errors.append("provisional must be true")


def check_authorization(m, errors):
    a = m.get("authorization")
    if not isinstance(a, dict):
        errors.append("authorization block missing")
        return
    if a.get("qualification_verdict") is not None:
        errors.append("authorization.qualification_verdict must be null")
    if a.get("frozen") is not False:
        errors.append("authorization.frozen must be false")
    if a.get("authorizing") is not False:
        errors.append("authorization.authorizing must be false")
    for k in ("release", "publication", "production"):
        if a.get(k) != "HOLD":
            errors.append("authorization.%s must be HOLD" % k)
    for p, k, val in _keys(m):
        if re.search(r"verdict|result|outcome", k, re.I) and val not in (None, [], {}, "", False) and not isinstance(val, (dict, list)):
            errors.append("%s: verdict-like field must be null or empty" % p)


def _norm(text):
    return re.sub(r"[\s_\-]+", " ", text.lower()).strip()


def check_claims(m, errors):
    for p, text in _strings(m):
        t = _norm(text)
        for mt in TERM_RE.finditer(t):
            if not NEG_BEFORE.search(t[:mt.start()]):
                errors.append("%s: forbidden verdict or assurance wording %r outside an explicit negation" % (p, mt.group(0)))
    for p, k, val in _keys(m):
        if BOOL_CLAIM_KEY.search(str(k)) and val is True:
            errors.append("%s: boolean claim key set to true" % p)


def check_components(m, errors):
    comps = m.get("components")
    names = []
    if not isinstance(comps, list):
        errors.append("components must be a list")
        return {}
    by = {}
    for i, c in enumerate(comps):
        if not isinstance(c, dict):
            errors.append("components[%d] must be an object" % i)
            continue
        n = c.get("component")
        names.append(n)
        for f in ("component", "repository", "revision", "origin", "provenance"):
            if not c.get(f):
                errors.append("components[%d] (%s) missing %s" % (i, n, f))
        _rev(errors, "components[%d].revision (%s)" % (i, n), c.get("revision"))
        by[n] = c
    dupes = sorted({str(n) for n in names if names.count(n) > 1})
    if dupes:
        errors.append("duplicate component entries: %s" % ", ".join(dupes))
    for n in REQUIRED_COMPONENTS:
        if n not in by:
            errors.append("component %s missing" % n)
    extra = sorted(set(map(str, by)) - set(REQUIRED_COMPONENTS))
    if extra:
        errors.append("unexpected component(s): %s" % ", ".join(extra))
    repos = [c.get("repository") for c in by.values()]
    if len(set(repos)) != len(repos):
        errors.append("two components name the same repository")
    ver = by.get("verifier", {})
    if str(ver.get("revision", "")).startswith("39d46b49"):
        errors.append("verifier pin must not be 39d46b49 (later documentation revision, not qualified)")
    later = m.get("later_documentation_revisions")
    if not isinstance(later, list):
        errors.append("later_documentation_revisions must be a list")
        later = []
    seen_later = False
    for i, c in enumerate(later):
        w = "later_documentation_revisions[%d]" % i
        _rev(errors, w + ".revision", c.get("revision"))
        if c.get("qualified") is not False or c.get("implicitly_qualified") is not False:
            errors.append("%s must state qualified false and implicitly_qualified false" % w)
        if c.get("component") == "verifier" and c.get("revision") == LATER_DOC_VERIFIER:
            seen_later = True
        if any(c.get("revision") == x.get("revision") for x in by.values()):
            errors.append("%s revision also appears as a pin" % w)
    if not seen_later:
        errors.append("Verifier 39d46b49 must be recorded as a later documentation revision")
    return by


def check_hub_lock_notice(m, root, errors):
    n = m.get("hub_lock_notice", {})
    if n.get("stale") is not True:
        errors.append("hub_lock_notice.stale must be true")
    if n.get("describes_qualified_mvp") is not False:
        errors.append("hub_lock_notice.describes_qualified_mvp must be false")
    if not HEX64.match(str(n.get("sha256", ""))):
        errors.append("hub_lock_notice.sha256 must be 64-hex")
        return
    p = root / str(n.get("path", ""))
    if not p.is_file():
        errors.append("hub lock file not found: %s" % p)
    elif sha256_bytes(p.read_bytes()) != n["sha256"]:
        errors.append("hub lock file hash differs from recorded value (the lock changed; supersede this manifest)")


def git_blob_id(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def git_tree_id(entries):
    """entries: list of (name, sha1hex) of regular files in one directory (git mode 100644)."""
    body = b"".join(b"100644 " + n.encode("utf-8") + b"\0" + bytes.fromhex(h) for n, h in sorted(entries, key=lambda e: e[0].encode("utf-8")))
    return hashlib.sha1(b"tree %d\0" % len(body) + body).hexdigest()


def list_ingress(directory):
    """Return (sorted relative file names, problems). Every directory (including __pycache__), symlink and special file is a problem."""
    names, problems = [], []
    for p in sorted(Path(directory).rglob("*")):
        rel = p.relative_to(directory)
        if p.is_symlink():
            problems.append("symlink %s" % rel.as_posix())
        elif p.is_dir():
            problems.append("subdirectory %s" % rel.as_posix())
        elif p.is_file():
            names.append(rel.as_posix())
        else:
            problems.append("special file %s" % rel.as_posix())
    return names, problems


def check_ingress(it, root, errors):
    if not HEX64.match(str(it.get("sha256", ""))):
        errors.append("ingress_tree.sha256 must be 64-hex")
    if it.get("sha256") != EXPECTED_INGRESS_DIGEST:
        errors.append("ingress_tree.sha256 differs from the validator's expected digest")
    if it.get("interpreter_requirement") != "3.13":
        errors.append("ingress_tree.interpreter_requirement must be 3.13")
    if "NOT covered" not in str(it.get("unclaimed_limitation", "")) or "sys.path" not in str(it.get("unclaimed_limitation", "")):
        errors.append("ingress_tree.unclaimed_limitation must state the sys.path shadowing limitation as NOT covered")
    if list(it.get("expected_files", [])) != list(EXPECTED_INGRESS_FILES):
        errors.append("ingress_tree.expected_files must equal the expected 8-file list")
    if it.get("git_tree_id") != EXPECTED_INGRESS_TREE_ID:
        errors.append("ingress_tree.git_tree_id differs from the expected tree id")
    d = root / str(it.get("path", ""))
    if not d.is_dir():
        errors.append("ingress tree directory not found")
        return
    names, problems = list_ingress(d)
    for pr in problems:
        errors.append("ingress tree contains a disallowed entry: %s" % pr)
    if names != sorted(EXPECTED_INGRESS_FILES):
        errors.append("ingress tree file list %s differs from expected %s" % (names, sorted(EXPECTED_INGRESS_FILES)))
    if not problems:
        got_tree = git_tree_id([(n, git_blob_id((d / n).read_bytes())) for n in names])
        if got_tree != it.get("git_tree_id"):
            errors.append("ingress tree git tree id recomputed %s differs from recorded %s" % (got_tree, it.get("git_tree_id")))
        try:
            got = ingress_tree_digest(d, it.get("glob", "*.py"))
        except (OSError, ValueError) as ex:
            errors.append("ingress tree not readable: %s" % ex)
        else:
            if got != it.get("sha256"):
                errors.append("ingress tree digest recomputed %s differs from recorded %s" % (got, it.get("sha256")))


def check_env_record_tree(et, root, errors):
    if et.get("git_tree_id") != EXPECTED_ENV_RECORD_TREE_ID or list(et.get("expected_files", [])) != list(EXPECTED_ENV_RECORD_FILES):
        errors.append("env_record_tree must record the expected tree id and file list")
    d = root / str(et.get("path", ""))
    if not d.is_dir():
        errors.append("env_record_tree directory not found")
        return
    names, problems = list_ingress(d)
    errors.extend("env_record tree contains a disallowed entry: %s" % pr for pr in problems)
    if names != sorted(EXPECTED_ENV_RECORD_FILES):
        errors.append("env_record tree file list %s differs from expected" % names)
    elif not problems and git_tree_id([(n, git_blob_id((d / n).read_bytes())) for n in names]) != et.get("git_tree_id"):
        errors.append("env_record tree git tree id recomputed differs from recorded")


def check_files(m, root, errors):
    rd = m.get("runtime_and_dependencies", {})
    if rd.get("python") != "3.13":
        errors.append("runtime_and_dependencies.python must be 3.13")
    dl = rd.get("dependency_lock", {})
    if dl.get("install_flag") != "--require-hashes":
        errors.append("dependency_lock.install_flag must be --require-hashes")
    jobs = [("dependency lock", dl.get("path"), dl.get("sha256"))]
    env = m.get("environment_and_configuration", {})
    for key in ("hub_profile_document", "ingress_boundary_document", "capture_script"):
        e = env.get(key, {})
        jobs.append((key, e.get("path"), e.get("sha256")))
    for label, rel, want in jobs:
        if not rel or not HEX64.match(str(want or "")):
            errors.append("%s: path or 64-hex sha256 missing" % label)
            continue
        p = root / rel
        if not p.is_file():
            errors.append("%s: file not found: %s" % (label, rel))
        elif sha256_bytes(p.read_bytes()) != want:
            errors.append("%s: sha256 differs from file at %s" % (label, rel))
    lock_text = ""
    p = root / str(dl.get("path", ""))
    if p.is_file():
        lock_text = p.read_text(encoding="utf-8")
    for name, ver in (dl.get("pins") or {}).items():
        if not re.search(r"^%s==%s\b" % (re.escape(name), re.escape(ver)), lock_text, re.M | re.I):
            errors.append("dependency pin %s==%s not found in the lock file" % (name, ver))
    check_ingress(env.get("ingress_tree", {}), root, errors)
    check_env_record_tree(env.get("env_record_tree", {}), root, errors)
    if env.get("environment_capture_at_this_tuple") != "not yet produced":
        errors.append("environment_capture_at_this_tuple must be 'not yet produced'")


def check_registry(m, root, errors):
    r = m.get("registry_catalogue", {})
    d = r.get("manifest_digest", {})
    val = str(d.get("value", ""))
    if not re.match(r"^sha256:[0-9a-f]{64}$", val):
        errors.append("registry_catalogue.manifest_digest.value must be sha256:<64-hex>")
    st = d.get("status")
    if st not in CATALOGUE_STATUSES:
        errors.append("registry_catalogue.manifest_digest.status must be one of %s" % ", ".join(CATALOGUE_STATUSES))
    sv = d.get("successor_value")
    if st == "superseded" and not re.match(r"^sha256:[0-9a-f]{64}$", str(sv)):
        errors.append("status superseded requires a sha256:<64-hex> successor_value")
    if st not in ("superseded", "superseded-pending") and sv is not None:
        errors.append("successor_value may be set only when status is superseded or superseded-pending")
    if sv is not None and not re.match(r"^sha256:[0-9a-f]{64}$", str(sv)):
        errors.append("successor_value must be sha256:<64-hex> when set")
    if st == "current":
        p = root / str(r.get("manifest_path", ""))
        try:
            repo_digest = json.loads(p.read_text(encoding="utf-8")).get("digest")
        except (OSError, ValueError) as ex:
            errors.append("catalogue manifest unreadable: %s" % ex)
        else:
            if repo_digest != val:
                errors.append("status current but catalogue digest in the repository is %s" % repo_digest)


def check_qualification_and_evidence(m, errors):
    q = m.get("qualification_references", {})
    _rev(errors, "qualification_references.main", q.get("main"))
    for i, pr in enumerate(q.get("builder_prepared_drafts", [])):
        _rev(errors, "builder_prepared_drafts[%d].head" % i, pr.get("head"))
    for k, val in (q.get("commitment_hashes_reported") or {}).items():
        if k != "basis" and not HEX64.match(str(val)):
            errors.append("commitment_hashes_reported.%s must be 64-hex" % k)
    if q.get("candidate_commitment_sha256") is not None:
        errors.append("candidate_commitment_sha256 must be null (Qualification records it elsewhere)")
    e = m.get("evidence_and_test_runs", {})
    if e.get("status") != "not yet produced":
        errors.append("evidence_and_test_runs.status must be 'not yet produced'")
    for k in ("qualification_run_ids", "evidence_bundle_digests", "test_run_identities"):
        if e.get(k) != []:
            errors.append("evidence_and_test_runs.%s must be an empty list" % k)


DICT_PATHS = ("authorization", "hub_lock_notice", "runtime_and_dependencies", "runtime_and_dependencies.dependency_lock",
              "runtime_and_dependencies.dependency_lock.pins", "qualification_references",
              "qualification_references.commitment_hashes_reported", "environment_and_configuration",
              "environment_and_configuration.hub_profile_document", "environment_and_configuration.ingress_boundary_document",
              "environment_and_configuration.capture_script", "environment_and_configuration.ingress_tree",
              "registry_catalogue", "registry_catalogue.manifest_digest", "evidence_and_test_runs")
LIST_OF_DICT_PATHS = ("components", "later_documentation_revisions", "qualification_references.builder_prepared_drafts")


def check_shape(m, errors):
    if not isinstance(m, dict):
        errors.append("manifest top level must be a JSON object")
        return False
    ok = True
    for path in DICT_PATHS:
        node = m
        for part in path.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if not isinstance(node, dict):
            errors.append("%s must be an object" % path)
            ok = False
    for path in LIST_OF_DICT_PATHS:
        node = m
        for part in path.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if not isinstance(node, list) or not all(isinstance(x, dict) for x in node):
            errors.append("%s must be a list of objects" % path)
            ok = False
    for k in ("qualification_run_ids", "evidence_bundle_digests", "test_run_identities"):
        if ok and not isinstance(m["evidence_and_test_runs"].get(k), list):
            errors.append("evidence_and_test_runs.%s must be a list" % k)
            ok = False
    if ok and not isinstance(m["environment_and_configuration"]["ingress_tree"].get("expected_files", []), list):
        errors.append("ingress_tree.expected_files must be a list")
        ok = False
    return ok


def default_expected():
    comps = {n: {"repository": r, "revision": v} for n, (r, v) in EXPECTED_COMPONENTS.items()}
    comps["hub"] = {"repository": EXPECTED_HUB_REPOSITORY, "revision": EXPECTED_HUB_REVISION}
    return {"components": comps, "successor_registry_digest": None,
            "registry_digest": EXPECTED_REGISTRY_DIGEST}


def load_expected(path):
    """Merge a --expect-tuple JSON file over the embedded tuple. Accepts components (incl. hub), registry_digest."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_pairs_no_dupes)
    if not isinstance(raw, dict) or not isinstance(raw.get("components", {}), dict):
        raise ValueError("expect-tuple file must be an object with a components object")
    exp = default_expected()
    for n, c in raw.get("components", {}).items():
        if not isinstance(c, dict) or not HEX40.match(str(c.get("revision", ""))) or not c.get("repository"):
            raise ValueError("expect-tuple component %s needs repository and a full 40-hex revision" % n)
        exp["components"][n] = {"repository": c["repository"], "revision": c["revision"]}
    if "registry_digest" in raw:
        exp["registry_digest"] = raw["registry_digest"]
    if "successor_registry_digest" in raw:
        if not re.match(r"^sha256:[0-9a-f]{64}$", str(raw["successor_registry_digest"])):
            raise ValueError("successor_registry_digest must be sha256:<64-hex>")
        exp["successor_registry_digest"] = raw["successor_registry_digest"]
    return exp


def check_expected(m, by, expected, errors):
    for n, e in expected["components"].items():
        c = by.get(n)
        if c is None:
            errors.append("expected component %s absent from manifest" % n)
            continue
        if c.get("repository") != e["repository"]:
            errors.append("component %s repository %r differs from expected %r" % (n, c.get("repository"), e["repository"]))
        if c.get("revision") != e["revision"]:
            errors.append("component %s revision %s differs from expected %s" % (n, c.get("revision"), e["revision"]))
    d = m["registry_catalogue"]["manifest_digest"]
    want_succ = expected.get("successor_registry_digest")
    if want_succ and d.get("status") == "superseded" and d.get("successor_value") != want_succ:
        errors.append("registry successor_value %s differs from expected successor %s" % (d.get("successor_value"), want_succ))
    if d.get("value") != expected["registry_digest"] and d.get("status") != "superseded":
        errors.append("registry digest %s differs from expected %s while status is not superseded" % (d.get("value"), expected["registry_digest"]))


def _gh_compare(repo, sha):
    try:
        out = subprocess.run(["gh", "api", "repos/%s/compare/%s...main" % (repo, sha), "--jq", ".status"],
                             capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as ex:
        return None, "gh unavailable: %s" % ex
    if out.returncode != 0:
        return None, out.stderr.strip()
    return out.stdout.strip(), ""


def check_online(by, errors):
    # compare base=sha, head=main: 'ahead' means main contains sha; 'identical' means sha is main.
    for n, c in by.items():
        status, err = _gh_compare(c["repository"], c["revision"])
        if status is None:
            errors.append("online: %s lookup failed: %s" % (n, err[:120]))
        elif status not in ("ahead", "identical"):
            errors.append("online: %s revision is not an ancestor of main of %s (compare status %s)" % (n, c["repository"], status))


def validate(manifest, root, online=False, expected=None):
    errors = []
    if not check_shape(manifest, errors):
        return errors
    try:
        check_structure(manifest, errors)
        check_authorization(manifest, errors)
        check_claims(manifest, errors)
        by = check_components(manifest, errors)
        check_expected(manifest, by, expected or default_expected(), errors)
        check_hub_lock_notice(manifest, root, errors)
        check_files(manifest, root, errors)
        check_registry(manifest, root, errors)
        check_qualification_and_evidence(manifest, errors)
        if online and by:
            check_online(by, errors)
    except (AttributeError, TypeError, KeyError, ValueError, IndexError) as ex:
        errors.append("malformed manifest structure (%s: %s)" % (type(ex).__name__, ex))
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--manifest", default=None, help="manifest path (default docs/mvp-package/candidate-manifest.json under --repo-root)")
    ap.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--expect-tuple", default=None, help="JSON file of expected component revisions (may include hub) and registry_digest, merged over the embedded tuple")
    ap.add_argument("--online", action="store_true", help="also check ancestry of each revision against main through gh")
    ap.add_argument("--print-sha256", action="store_true", help="print the sha256 of the exact manifest bytes (candidate input identity)")
    a = ap.parse_args(argv)
    root = Path(a.repo_root)
    path = Path(a.manifest) if a.manifest else root / "docs/mvp-package/candidate-manifest.json"
    try:
        manifest, raw = load_manifest(path)
    except (OSError, ValueError) as ex:
        print("unreadable manifest: %s" % ex, file=sys.stderr)
        return 2
    expected = None
    if a.expect_tuple:
        try:
            expected = load_expected(a.expect_tuple)
        except (OSError, ValueError) as ex:
            print("unreadable expect-tuple: %s" % ex, file=sys.stderr)
            return 2
    errors = validate(manifest, root, a.online, expected)
    if a.print_sha256:
        print("manifest_sha256 %s" % sha256_bytes(raw))
    if errors:
        for e in errors:
            print("INVALID: %s" % e)
        print("%d problem(s). This tool gives no verdict about the candidate." % len(errors))
        return 1
    print("manifest is internally consistent with this checkout (%s). Non-authorizing; no verdict." % ("offline and online" if a.online else "offline"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
