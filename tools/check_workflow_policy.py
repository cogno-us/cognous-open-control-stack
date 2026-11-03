#!/usr/bin/env python3
"""Deterministic, offline GitHub Actions workflow policy checker (P1 item 11).

Scans every `.github/workflows/*.y{,a}ml` and every `action.y{,a}ml` under `.github/` and enforces:

  WP01 checkout-persist-credentials  every actions/checkout step has `with.persist-credentials: false`
                                     (literal boolean; unset, true, strings and expressions all fail)
  WP02 permissions-missing           workflow-level `permissions:` must be present and a mapping
                                     (string forms such as read-all / write-all are rejected);
                                     a job-level block may only narrow the workflow-level one
                                     (a job-level write is reported once, as WP03)
  WP03 write-permission              no `write` scope at workflow or job level
  WP04 forbidden-trigger             no `pull_request_target`, no `workflow_run`
  WP05 secret-exposure               no `secrets.*`, `secrets:` key (including `inherit`),
                                     `github.token`/`GITHUB_TOKEN`, or checkout `token:` input
  WP06 action-not-pinned             every `uses:` (steps and reusable-workflow calls, including
                                     cogno-us/*) is `owner/repo[/path]@<40 lowercase hex>`; local
                                     `./` paths are exempt; docker:// needs `@sha256:<64 hex>`
  WP07 parse-error                   unreadable / unsafe / duplicate-key / non-mapping YAML

Exceptions live in docs/security/workflow-policy-exceptions.json (schema-checked; initial set is
EMPTY). Only WP01, WP03 and WP05 can be excepted. Every exception must carry a rationale and an
unexpired `expires` date, must name an existing workflow and job (and step index, if given), and
must suppress at least one real violation, otherwise the run fails (stale exception). A WP03
exception is refused for any workflow reachable by fork/PR-controlled events.

YAML is read with a safe loader. YAML 1.1 parses the bare key `on` as boolean True; the loader
result is normalised so triggers are always read from the key "on".

Usage: check_workflow_policy.py [--root DIR] [--exceptions FILE] [--today YYYY-MM-DD]
Exit: 0 clean, 1 violations or exception errors, 2 usage/environment error (e.g. PyYAML missing).
Output is sorted and deterministic.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only when PyYAML is absent
    yaml = None

DEFAULT_ROOT = pathlib.Path(__file__).resolve().parents[1]
EXCEPTIONS_REL = "docs/security/workflow-policy-exceptions.json"
EXCEPTABLE = {"WP01", "WP03", "WP05"}
FORBIDDEN_TRIGGERS = {"pull_request_target", "workflow_run"}
FORK_REACHABLE = {"pull_request", "pull_request_target", "pull_request_review",
                  "pull_request_review_comment", "issue_comment", "issues", "fork",
                  "workflow_run", "discussion", "discussion_comment", "watch"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
DOCKER_PIN = re.compile(r"^docker://[^@\s]+@sha256:[0-9a-f]{64}$")
USES_REF = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(/[^@\s]+)?@(?P<ref>\S+)$")
SECRET_TEXT = re.compile(r"\bsecrets\s*(\.|\[)|\bgithub\s*\.\s*token\b|GITHUB_TOKEN", re.I)
LEVEL = {"none": 0, "read": 1, "write": 2}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _make_loader():
    class Loader(yaml.SafeLoader):
        pass

    def mapping(loader, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=True)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, "duplicate key %r" % (key,), key_node.start_mark)
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    return Loader


def load_yaml_text(text):
    doc = yaml.load(text, Loader=_make_loader())  # noqa: S506 - SafeLoader subclass
    if isinstance(doc, dict) and True in doc and "on" not in doc:
        doc["on"] = doc.pop(True)  # YAML 1.1: bare `on` is boolean True
    return doc


def triggers(doc):
    t = doc.get("on")
    if isinstance(t, str):
        return [t]
    if isinstance(t, list):
        return [str(x) for x in t]
    if isinstance(t, dict):
        return [str(k) for k in t]
    return []


def walk_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for k, v in node.items():
            if isinstance(k, str):
                yield k
            yield from walk_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_strings(v)


def workflow_files(root):
    gh = root / ".github"
    found = set()
    for pattern in ("workflows/*.yml", "workflows/*.yaml", "**/action.yml", "**/action.yaml"):
        found.update(p for p in gh.glob(pattern) if p.is_file())
    return sorted(found)


def check_permissions(perms, where, add, workflow_level=None):
    """Return the normalised {scope: level} mapping or None; report WP02/WP03 problems."""
    if not isinstance(perms, dict):
        add("WP02", None, where + " permissions must be an explicit mapping, got %r" % (perms,))
        return None
    out = {}
    for scope, level in sorted(perms.items(), key=lambda kv: str(kv[0])):
        if level not in LEVEL:
            add("WP02", None, "%s permissions.%s has invalid level %r" % (where, scope, level))
            continue
        out[scope] = level
        if level == "write":
            add("WP03", None, "%s permissions.%s is write" % (where, scope))
        if workflow_level is not None and level != "write" and LEVEL[level] > LEVEL[workflow_level.get(scope, "none")]:
            add("WP02", None, "%s permissions.%s=%s widens the workflow-level grant (%s)" % (
                where, scope, level, workflow_level.get(scope, "none")))
    return out


def check_uses(uses, add, step):
    if not isinstance(uses, str):
        add("WP06", step, "uses must be a string, got %r" % (uses,))
        return
    if uses.startswith("./"):
        return
    if uses.startswith("docker://"):
        if not DOCKER_PIN.match(uses):
            add("WP06", step, "docker action not pinned to @sha256 digest: %s" % uses)
        return
    m = USES_REF.match(uses)
    if not m or not SHA40.match(m.group("ref")):
        add("WP06", step, "not pinned to a full 40-hex SHA: %s" % uses)


def check_steps(steps, job, add_job):
    if not isinstance(steps, list):
        return
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            continue

        def add(rule, _s, msg, i=i):
            add_job(rule, i, msg)

        uses = step.get("uses")
        if uses is not None:
            check_uses(uses, add, i)
            if isinstance(uses, str) and uses.strip().lower().split("@")[0].split("/")[:2] == ["actions", "checkout"]:
                with_ = step.get("with")
                value = with_.get("persist-credentials", "<unset>") if isinstance(with_, dict) else "<unset>"
                if value is not False:
                    add("WP01", i, "actions/checkout must set with.persist-credentials: false (found %r)" % (value,))
                if isinstance(with_, dict) and "token" in with_:
                    add("WP05", i, "actions/checkout must not be given a token input")


def check_doc(rel, doc):
    """Return a list of (rule, job, step, message) for one parsed workflow/action document."""
    problems = []

    def adder(job):
        def add(rule, step, msg):
            problems.append((rule, job, step, msg))
        return add

    top = adder(None)
    if not isinstance(doc, dict):
        top("WP07", None, "document is not a mapping")
        return problems

    # secrets / token exposure anywhere in the document
    for s in sorted(set(walk_strings(doc))):
        if SECRET_TEXT.search(s):
            top("WP05", None, "secret/token reference: %s" % s.strip().splitlines()[0][:120])
    jobs_for_secrets = doc.get("jobs") if isinstance(doc.get("jobs"), dict) else {}
    for jn, j in sorted(jobs_for_secrets.items(), key=lambda kv: str(kv[0])):
        if isinstance(j, dict) and "secrets" in j:
            adder(str(jn))("WP05", None, "job passes `secrets:` (%r)" % (j["secrets"],))

    is_action = "runs" in doc and "jobs" not in doc
    if is_action:
        runs = doc.get("runs")
        if isinstance(runs, dict):
            check_steps(runs.get("steps"), "(composite)", adder("(composite)"))
        return problems

    for t in sorted(set(triggers(doc)) & FORBIDDEN_TRIGGERS):
        top("WP04", None, "forbidden trigger: %s" % t)
    if "on" not in doc:
        top("WP07", None, "no `on:` trigger block found")

    wperms = None
    if "permissions" not in doc:
        top("WP02", None, "workflow-level permissions block is missing")
    else:
        wperms = check_permissions(doc["permissions"], "workflow", top)

    jobs = doc.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        top("WP07", None, "no jobs mapping")
        return problems
    for jn, job in sorted(jobs.items(), key=lambda kv: str(kv[0])):
        jn = str(jn)
        add = adder(jn)
        if not isinstance(job, dict):
            add("WP07", None, "job is not a mapping")
            continue
        if "permissions" in job:
            check_permissions(job["permissions"], "job", add, wperms if wperms is not None else {})
        if "uses" in job:
            check_uses(job["uses"], add, None)
        check_steps(job.get("steps"), jn, add)
    return problems


def scan(root):
    """Return ({rel: doc-or-None}, [violation dict])."""
    violations = []
    docs = {}
    for path in workflow_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            doc = load_yaml_text(path.read_text(encoding="utf-8"))
        except Exception as exc:  # yaml errors, decode errors
            violations.append(dict(file=rel, job=None, step=None, rule="WP07",
                                   message="YAML parse error: %s" % str(exc).splitlines()[0]))
            docs[rel] = None
            continue
        docs[rel] = doc
        for rule, job, step, msg in check_doc(rel, doc):
            violations.append(dict(file=rel, job=job, step=step, rule=rule, message=msg))
    return docs, violations


def load_exceptions(path):
    """Schema-check the exceptions file. Returns (exceptions, errors)."""
    errors = []
    try:
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [], ["exceptions file missing: %s" % path]
    except ValueError as exc:
        return [], ["exceptions file is not valid JSON: %s" % exc]
    if not isinstance(data, dict) or set(data) != {"schema_version", "exceptions"}:
        return [], ["exceptions file must be an object with exactly schema_version and exceptions"]
    if data["schema_version"] != 1:
        errors.append("schema_version must be 1")
    items = data["exceptions"]
    if not isinstance(items, list):
        return [], errors + ["exceptions must be a list"]
    required = {"workflow", "job", "step", "rule", "rationale", "expires"}
    clean = []
    for n, e in enumerate(items):
        tag = "exceptions[%d]" % n
        if not isinstance(e, dict) or set(e) != required:
            errors.append("%s must have exactly keys %s" % (tag, sorted(required)))
            continue
        ok = True
        for k in ("workflow", "job", "rule", "rationale", "expires"):
            if not isinstance(e[k], str) or not e[k].strip():
                errors.append("%s.%s must be a non-empty string" % (tag, k))
                ok = False
        if not (e["step"] is None or (isinstance(e["step"], int) and not isinstance(e["step"], bool) and e["step"] >= 0)):
            errors.append("%s.step must be null or a non-negative integer" % tag)
            ok = False
        if ok and e["rule"] not in EXCEPTABLE:
            errors.append("%s.rule %r cannot be excepted (allowed: %s)" % (tag, e["rule"], sorted(EXCEPTABLE)))
            ok = False
        if ok and not DATE.match(e["expires"]):
            errors.append("%s.expires must be YYYY-MM-DD" % tag)
            ok = False
        elif ok:
            try:
                datetime.date.fromisoformat(e["expires"])
            except ValueError:
                errors.append("%s.expires is not a real date" % tag)
                ok = False
        if ok:
            clean.append(e)
    return clean, errors


def apply_exceptions(root, docs, violations, exceptions, today):
    errors = []
    remaining = list(violations)
    for e in exceptions:
        tag = "exception %s:%s:%s:%s" % (e["workflow"], e["job"], e["step"], e["rule"])
        if datetime.date.fromisoformat(e["expires"]) < today:
            errors.append("%s expired on %s" % (tag, e["expires"]))
            continue
        doc = docs.get(e["workflow"])
        jobs = doc.get("jobs") if isinstance(doc, dict) else None
        if not isinstance(jobs, dict) or e["job"] not in {str(k) for k in jobs}:
            errors.append("%s is stale: workflow/job does not exist" % tag)
            continue
        if e["rule"] == "WP03" and set(triggers(doc)) & FORK_REACHABLE:
            errors.append("%s refused: write permission excepted for a fork/PR-reachable workflow" % tag)
            continue
        matched = [v for v in remaining if v["file"] == e["workflow"] and v["job"] == e["job"]
                   and v["rule"] == e["rule"] and (e["step"] is None or v["step"] == e["step"])]
        if not matched:
            errors.append("%s is stale: it suppresses no violation" % tag)
            continue
        remaining = [v for v in remaining if v not in matched]
    return remaining, errors


def run(root, exceptions_path=None, today=None):
    root = pathlib.Path(root)
    today = today or datetime.date.today()
    exceptions_path = exceptions_path or root / EXCEPTIONS_REL
    docs, violations = scan(root)
    exceptions, errors = load_exceptions(exceptions_path)
    violations, more = apply_exceptions(root, docs, violations, exceptions, today)
    errors.extend(more)
    violations.sort(key=lambda v: (v["file"], v["job"] or "", -1 if v["step"] is None else v["step"], v["rule"], v["message"]))
    return violations, sorted(errors), len(docs)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--exceptions")
    ap.add_argument("--today", help="YYYY-MM-DD override for expiry checks")
    args = ap.parse_args(argv)
    if yaml is None:
        print("PyYAML is required: pip install --require-hashes -r tools/requirements-workflow-policy.lock", file=sys.stderr)
        return 2
    today = datetime.date.fromisoformat(args.today) if args.today else None
    violations, errors, count = run(args.root, args.exceptions, today)
    for v in violations:
        print("%s:%s:%s: %s %s" % (v["file"], v["job"] or "-", "-" if v["step"] is None else v["step"], v["rule"], v["message"]))
    for e in errors:
        print("exceptions: " + e)
    print("workflow policy: %d files, %d violations, %d exception errors" % (count, len(violations), len(errors)))
    return 1 if violations or errors else 0


if __name__ == "__main__":
    sys.exit(main())
