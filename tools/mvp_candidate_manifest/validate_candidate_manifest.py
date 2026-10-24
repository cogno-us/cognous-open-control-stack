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
NEGATION = re.compile(r"\b(not|no|never|none|without|neither|nor)\b", re.I)
# Words that must not appear at all in a string value.
ALWAYS_FORBIDDEN = re.compile(r"\b(PASS|PASSED|FAIL|FAILED|certified|certification granted|compliant|production[- ]ready|"
                              r"security[- ]cleared)\b")
# Words that may appear only in a string that also carries a negation.
NEGATION_ONLY = re.compile(r"\b(qualified|frozen|accepted|approved|released|verdict issued)\b", re.I)


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


def check_claims(m, errors):
    for p, s in _strings(m):
        if ALWAYS_FORBIDDEN.search(s):
            errors.append("%s: forbidden verdict or assurance wording" % p)
        elif NEGATION_ONLY.search(s) and not NEGATION.search(s) and "UNQUALIFIED" not in s:
            errors.append("%s: affirmative qualified/frozen/accepted style claim without negation" % p)


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
    it = env.get("ingress_tree", {})
    if not HEX64.match(str(it.get("sha256", ""))):
        errors.append("ingress_tree.sha256 must be 64-hex")
    else:
        try:
            got = ingress_tree_digest(root / it.get("path", ""), it.get("glob", "*.py"))
        except (OSError, ValueError) as ex:
            errors.append("ingress tree not readable: %s" % ex)
        else:
            if got != it["sha256"]:
                errors.append("ingress tree digest recomputed %s differs from recorded %s" % (got, it["sha256"]))
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
    if st != "superseded" and sv is not None:
        errors.append("successor_value may be set only when status is superseded")
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


def _gh_compare(repo, sha):
    out = subprocess.run(["gh", "api", "repos/%s/compare/%s...main" % (repo, sha), "--jq", ".status"],
                         capture_output=True, text=True, timeout=60)
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


def validate(manifest, root, online=False):
    errors = []
    check_structure(manifest, errors)
    check_authorization(manifest, errors)
    check_claims(manifest, errors)
    by = check_components(manifest, errors)
    check_hub_lock_notice(manifest, root, errors)
    check_files(manifest, root, errors)
    check_registry(manifest, root, errors)
    check_qualification_and_evidence(manifest, errors)
    if online and by:
        check_online(by, errors)
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--manifest", default=None, help="manifest path (default docs/mvp-package/candidate-manifest.json under --repo-root)")
    ap.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
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
    errors = validate(manifest, root, a.online)
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
