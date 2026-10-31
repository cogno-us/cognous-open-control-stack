#!/usr/bin/env python3
"""render_demo.py - deterministic, read-only walkthrough renderer for the synthetic $10 refund MVP (OCS-MVP-FINAL, Worker B).

It READS the artifacts retained by the existing suites/mvp-chain harness (observations.json, results.json, artifacts/...) plus the run-level files the
mvp-acceptance workflow adds (run-identity.json, gate-verdict.json, custody-evidence.json, SHA256SUMS ...) and renders a markdown walkthrough on stdout.

Rules it keeps:
  * stdlib only; never writes into the evidence directory (the SQLite destination copy is copied to a private temp dir before it is opened);
  * shows only what the artifacts contain; an absent or unreadable artifact or field is printed as MISSING / UNREADABLE, never as zero, never defaulted;
  * statuses and Verifier dispositions are reproduced as recorded (ABSTAIN stays ABSTAIN; this script never writes PASS for a Verifier disposition);
  * no verdict is computed here; the oracle row statuses are the suite's, the gate verdict is the gate's;
  * output is a pure function of the evidence directory and the arguments (no clock, no randomness).

Not an acceptance, certification, Tier 1, Q7, release or production claim. Standing holds are unchanged.

Usage: python3 render_demo.py EVIDENCE_DIR [--label TEXT]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import sqlite3
import sys
import tempfile
from pathlib import Path

Q14 = ("The frozen pinned classes compose end-to-end in the qualification harness, while the trusted ingress boundary is separately exercised on the real "
       "socket under the same frozen candidate.")
PROHIBITED = "A live socket request produced the reconstructed Replay, Evidence Pack and Verifier evidence."

# ARCHITECT-STATED / common brief (used only to display MATCH / MISMATCH against what the artifacts record)
FROZEN_QUAL = "fa12c699939880149ed3997cbc2b11b264b23acd"
FROZEN_COMMITMENT = "814430869c63ab57cae091624c512bb119a3291e39e043827ae180ad59d3ca49"
FROZEN_TUPLE = {
    "control_plane": "7a4bcd40b3b49e61ff3c294dcca53b52f460b22c", "runtime": "c5e97e87dd239c821b1b4a406a55dcd03c5bc61f",
    "replay": "40012b8c174c6f25685bd5d9bc93ff46cc9a5842", "evidence_pack": "7b9511f2c6d56d424f17b078826594abd29f6c96",
    "odes": "1a5e1d300250d832e611633f0bf8f762e398c0ec", "action_manifest": "fa170815ef96a54c233d0dd9da821b60debabf8b",
    "verifier": "c0b8ba1f55b75db787a320f3de0f79342c6f6826", "hub": "c897266b7ce4b921889519087fa8b1863b4302e3",
}
MISSING = "MISSING"


# ---------------------------------------------------------------- helpers
def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(p: Path):
    """-> (obj, state) with state in OK / MISSING / UNREADABLE (type)."""
    try:
        return json.loads(p.read_text(encoding="utf-8")), "OK"
    except FileNotFoundError:
        return None, MISSING
    except (OSError, ValueError) as exc:
        return None, f"UNREADABLE ({type(exc).__name__})"


def g(d, *path):
    """Safe getter. Returns the module-level MISSING sentinel string when any step is absent."""
    cur = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        elif isinstance(cur, list) and isinstance(k, int) and -len(cur) <= k < len(cur):
            cur = cur[k]
        else:
            return MISSING
    return cur


def v(x) -> str:
    """Display a recorded value verbatim; None is shown as 'null' (recorded), absent as MISSING."""
    if x is None:
        return "null"
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, (dict, list)):
        return json.dumps(x, sort_keys=True, separators=(",", ":"))
    return str(x)


def short(x, n=16) -> str:
    s = v(x)
    if s.startswith("sha256:"):
        return s[:7 + n] + "..."
    return s if len(s) <= n + 8 else s[:n + 8] + "..."


class Out:
    def __init__(self):
        self.L: list[str] = []

    def add(self, s: str = ""):
        self.L.append(s)

    def h(self, n: int, s: str):
        self.add()
        self.add("#" * n + " " + s)
        self.add()

    def kv(self, rows):
        self.add("| item | recorded value |")
        self.add("|---|---|")
        for k, val in rows:
            self.add(f"| {k} | {str(val).replace('|', '/')} |")
        self.add()

    def text(self):
        return "\n".join(self.L) + "\n"


class Ev:
    """Locates the run directory and the chain results directory."""

    def __init__(self, root: Path):
        self.arg = root
        self.run: Path | None = None
        self.chain: Path | None = None
        self.note = ""
        self._locate(root)

    def _locate(self, d: Path):
        if (d / "mvp-chain" / "observations.json").is_file() or (d / "mvp-chain" / "results.json").is_file():
            self.run, self.chain = d, d / "mvp-chain"
        elif (d / "observations.json").is_file() or (d / "results.json").is_file():
            self.run, self.chain = None, d
            self.note = "directory is a bare chain results directory (no run-level files)"
        elif (d / "runs").is_dir():
            runs = sorted(p for p in (d / "runs").iterdir() if p.is_dir())
            if len(runs) == 1:
                self.note = f"evidence branch root; using the only run directory {runs[0].name}"
                self._locate(runs[0])
            else:
                self.note = "evidence branch root with %d run directories (%s): pass exactly one of them" % (len(runs), ", ".join(p.name for p in runs))
        else:
            self.note = "no mvp-chain/observations.json, no observations.json and no runs/ directory found"

    def run_file(self, name):
        return (self.run / name) if self.run else None



def junit_line(p: Path) -> str:
    try:
        root = ET.parse(p).getroot()
    except FileNotFoundError:
        return MISSING
    except (OSError, ET.ParseError) as exc:
        return f"UNREADABLE ({type(exc).__name__})"
    n = f = e = sk = 0
    for c in root.iter("testcase"):
        n += 1
        f += c.find("failure") is not None
        e += c.find("error") is not None
        sk += c.find("skipped") is not None
    return f"tests {n}, failed {f}, error {e}, skipped {sk}, passed {n - f - e - sk}"


def row_map(results):
    rows = g(results, "rows")
    return {r.get("id"): r for r in rows} if isinstance(rows, list) else {}


def row_line(rm, rid):
    r = rm.get(rid)
    if r is None:
        return f"{rid}: {MISSING} (no such row in results.json)"
    return f"{rid}: **{r.get('status')}** - {str(r.get('title', ''))[:140]}"


def file_state(p: Path | None) -> str:
    if p is None:
        return MISSING + " (no run-level directory)"
    return "present" if p.is_file() else MISSING


# ---------------------------------------------------------------- sections
def render(ev: Ev, label: str) -> str:
    o = Out()
    chain = ev.chain
    obs, ost = load(chain / "observations.json") if chain else (None, MISSING)
    res, rst = load(chain / "results.json") if chain else (None, MISSING)
    art = (chain / "artifacts") if chain else None
    rm = row_map(res)

    def A(rel):  # retained artifact JSON
        return load(art / rel) if art else (None, MISSING)

    banner = []
    if label:
        banner = [f"> **{label}**", "> This rendering is labelled by the operator. Treat it exactly as labelled."]
    o.add("# Synthetic $10 refund MVP - demonstration walkthrough (rendered from retained artifacts)")
    o.add()
    for b in banner:
        o.add(b)
    if banner:
        o.add()
    o.add("Read-only rendering. It shows only what the retained artifacts contain; anything absent is marked MISSING. It is not an acceptance, certification, "
          "Tier 1, Q7, release or production claim; standing holds are unchanged. Oracle statuses are the suite's; the gate verdict is the gate's; neither is computed here.")

    # ---- Q14
    o.h(2, "0. Scope statement (Architect ruling Q14)")
    o.add("Permitted claim, verbatim:")
    o.add()
    o.add(f"> {Q14}")
    o.add()
    o.add(f"PROHIBITED claim (do not make it): \"{PROHIBITED}\"")
    o.add()
    o.add("Why: the Replay, Evidence Pack and Verifier evidence below is reconstructed from the in-process composed chain (Control Plane, route-B executor, Replay, Evidence Pack, "
          "Verifier) run inside the qualification harness. The real-socket trusted ingress is exercised separately (section 13). No socket request produced the reconstructed evidence.")

    # ---- locate
    o.h(2, "1. Evidence directory and run identity")
    rows = [("evidence directory argument", str(ev.arg)), ("run directory resolved", str(ev.run) if ev.run else MISSING),
            ("chain results directory resolved", str(chain) if chain else MISSING)]
    if ev.note:
        rows.append(("locator note", ev.note))
    rows += [("observations.json", ost if ost != "OK" else "present, readable"), ("results.json", rst if rst != "OK" else "present, readable")]
    o.kv(rows)
    if chain is None or (obs is None and res is None):
        o.add("**No chain results could be read. Nothing further can be rendered; no value has been invented.**")
        return finish(o, label)

    ri, ris = load(ev.run_file("run-identity.json")) if ev.run else (None, MISSING)
    RI, RIs = load(ev.run_file("RUN-IDENTITY.json")) if ev.run else (None, MISSING)
    o.add("Run identity (as recorded by the run job and by the evidence job):")
    o.add()
    rows = []
    for nm, d, stt in (("run-identity.json (run job)", ri, ris), ("RUN-IDENTITY.json (evidence job)", RI, RIs)):
        if d is None:
            rows.append((nm, stt))
        else:
            for k in ("run_url", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_REF", "GITHUB_SHA", "GITHUB_EVENT_NAME", "RUNNER_OS", "ImageVersion", "QG5_JOB_STATUS", "yama_ptrace_scope", "kernel"):
                if k in d:
                    rows.append((f"{nm}: {k}", v(d[k])))
    o.kv(rows)
    gsha = g(ri, "GITHUB_SHA")
    if gsha != MISSING:
        o.add(f"Qualification commit recorded by the run: `{gsha}`; frozen candidate (Architect-stated) `{FROZEN_QUAL}`: **{'MATCH' if gsha == FROZEN_QUAL else 'MISMATCH'}**.")
        o.add()
    if ev.run is None:
        o.add("NOTE: no run-level directory; the run cannot be identified as the authorized frozen run from these files alone.")
        o.add()
    elif ris == MISSING and RIs == MISSING:
        o.add("NOTE: neither run-identity.json nor RUN-IDENTITY.json is present; this directory is not identifiable as the authorized frozen run. If this is a local dry run it is NOT evidence.")
        o.add()

    # ---- tuple
    heads = g(res, "tuple", "heads")
    o.h(3, "Component tuple recorded in results.json versus the frozen tuple")
    if heads == MISSING or not isinstance(heads, dict):
        o.add(f"tuple heads: {MISSING}")
        o.add()
    else:
        o.add("| component | recorded head | frozen (Architect-stated) |")
        o.add("|---|---|---|")
        for k in sorted(FROZEN_TUPLE):
            rec = heads.get(k, MISSING)
            o.add(f"| {k} | `{rec}` | {'MATCH' if rec == FROZEN_TUPLE[k] else 'MISMATCH'} |")
        o.add()
        o.add(f"overrides recorded: {v(g(res, 'tuple', 'overrides'))}; cp_revision_override: {v(g(res, 'tuple', 'cp_revision_override'))}")
        o.add()
    o.add(f"oracle expectations file: `{Path(str(g(res, 'expectations_file'))).name}`; sha256 `{v(g(res, 'expectations_sha256'))}`; git blob `{v(g(res, 'expectations_git_blob'))}`; "
          f"acceptance_declared: {v(g(res, 'acceptance_declared'))}")
    o.add()

    # ---- overall oracle
    o.h(3, "Oracle row statuses (the suite's computation, reproduced)")
    cnt = g(res, "counts")
    o.add(f"suite-reported counts: {v(cnt)}; pytest_exit_status recorded: {v(g(res, 'pytest_exit_status'))}; rows in results.json: {len(rm) if rm else MISSING}")
    o.add()
    notpass = [r for r in (g(res, "rows") if isinstance(g(res, "rows"), list) else []) if r.get("status") != "PASS"]
    if notpass:
        o.add("Rows that are not PASS (each is shown as recorded, none is promoted):")
        o.add()
        for r in notpass:
            o.add(f"- {r.get('id')}: **{r.get('status')}** (mandatory: {v(r.get('mandatory'))}) - {str(r.get('reason', ''))[:260]}")
        o.add()
    elif rm:
        o.add("Every row in results.json is PASS.")
        o.add()
    gv, gvs = load(ev.run_file("gate-verdict.json")) if ev.run else (None, MISSING)
    if gv is None:
        o.add(f"gate-verdict.json: {gvs}. No gate verdict is available to this rendering.")
    else:
        o.add(f"gate verdict (the gate's, as recorded): **{v(gv.get('verdict'))}**; authorizes: {v(gv.get('authorizes'))}; release: {v(gv.get('release'))}")
    o.add()
    cu, cus = load(ev.run_file("custody-evidence.json")) if ev.run else (None, MISSING)
    if cu is None:
        o.add(f"custody-evidence.json: {cus}")
    else:
        o.add(f"commitment custody check: result {v(cu.get('result'))}; recomputed commitment sha256 `{v(cu.get('recomputed_commitment_sha256'))}` "
              f"({'MATCH' if cu.get('recomputed_commitment_sha256') == FROZEN_COMMITMENT else 'MISMATCH'} with the frozen commitment v5)")
    o.add()

    if ev.run is not None:
        o.add("pytest groups (run-level files; the gate, not this script, judges them):")
        o.add()
        for grp in ("mvp-chain", "d2-route-b", "applicability"):
            ex = ev.run / f"pytest-exit-{grp}.txt"
            exit_s = ex.read_text().strip() if ex.is_file() else MISSING
            o.add(f"- {grp}: pytest exit {exit_s}; junit: {junit_line(ev.run / f'junit-{grp}.xml')}")
        o.add()

    # ---- 2 proposal and decision
    prop, ps = A("chain/proposal.json")
    rec, rs = A("chain/cp-run-record.json")
    exp, es = A("chain/executor-export.json")
    o.h(2, "2. Governed synthetic $10 refund proposal and decision")
    if prop is None:
        o.add(f"chain/proposal.json: {ps}")
        o.add()
    else:
        o.kv([("action_id", v(g(prop, "action_id"))), ("actor", v(g(prop, "actor"))), ("principal", v(g(prop, "principal"))), ("target (synthetic account)", v(g(prop, "target"))),
              ("amount / unit", f"{v(g(prop, 'amount'))} {v(g(prop, 'unit'))}"), ("effects requested", v(g(prop, "effects"))), ("requested_permissions", v(g(prop, "requested_permissions"))),
              ("payload", v(g(prop, "payload"))), ("manifest_id / version", f"{v(g(prop, 'manifest_id'))} / {v(g(prop, 'manifest_version'))}"),
              ("payload_commitment (proposal file)", short(g(prop, 'payload_commitment'))),
              ("proposal_commitment (from the executor export's envelope; the proposal file does not carry it)", short(g(exp, 'execution_envelope', 'operation', 'proposal_commitment')))])
    dec = g(rec, "decisions", 0)
    if rec is None:
        o.add(f"chain/cp-run-record.json: {rs}")
        o.add()
    else:
        o.kv([("decision_id", v(g(dec, "decision_id"))), ("decision result (Control Plane)", f"**{v(g(dec, 'result'))}**"), ("reasons", v(g(dec, "reasons"))),
              ("effect_id", v(g(dec, "effect_id"))), ("decided_at", v(g(dec, "decided_at"))), ("time_source", v(g(dec, "time_source"))),
              ("decisions in record / refusals / attempts", f"{len(g(rec, 'decisions')) if isinstance(g(rec, 'decisions'), list) else MISSING} / "
                                                           f"{len(g(rec, 'refusals')) if isinstance(g(rec, 'refusals'), list) else MISSING} / {len(g(rec, 'attempts')) if isinstance(g(rec, 'attempts'), list) else MISSING}")])
    oc = g(obs, "chain", "decision")
    o.add(f"Cross-check with the harness observation: decision result {v(g(oc, 'result'))}, decision_id {'MATCH' if g(oc, 'decision_id') == g(dec, 'decision_id') and g(dec, 'decision_id') != MISSING else 'NOT CONFIRMED'} "
          f"with the retained record. Oracle: {row_line(rm, 'CHAIN-01')}")
    o.add()
    o.add("Time note: the record's time_source is as printed above (the harness fixes the clock; it is not wall-clock evidence).")
    o.add()

    # ---- 3 authority and approval
    o.h(2, "3. Valid authority and approval")
    ins = g(dec, "resolution_inputs")
    if isinstance(ins, list):
        o.add("Resolution inputs the Control Plane consulted at decision time (recorded `observed` state):")
        o.add()
        o.add("| input_type | input_id | expected | observed | missing |")
        o.add("|---|---|---|---|---|")
        for i in ins:
            o.add(f"| {i.get('input_type', MISSING)} | {str(i.get('input_id', MISSING))[:60]} | {v(i.get('expected'))[:200]} | {v(i.get('observed'))[:260]} | {v(i.get('missing'))} |")
        o.add()
    else:
        o.add(f"resolution inputs: {MISSING}")
        o.add()
    ar = g(exp, "control_plane_evidence", "authority_receipt")
    o.add(f"Authority receipt retained in the executor export: grant {v(g(ar, 'grant_id'))} revision {v(g(ar, 'grant_revision'))} status {v(g(ar, 'grant_status'))}; "
          f"claim {v(g(ar, 'claim_id'))}; profile {v(g(ar, 'profile'))}")
    o.add()
    cl = g(obs, "chain", "claim")
    o.add(f"Claim provisioning (real `provision_claim`): ok {v(g(cl, 'ok'))}, state after provision {v(g(cl, 'state_after_provision'))}, error {v(g(cl, 'error'))}. Oracle: {row_line(rm, 'CHAIN-02')}")
    o.add()

    # ---- 4 route B and single effect
    o.h(2, "4. Route-B atomic execution and the single destination effect")
    ex = g(obs, "chain", "execute")
    de = g(obs, "chain", "destination")
    o.kv([("execute status / observed_state", f"{v(g(ex, 'status'))} / {v(g(ex, 'observed_state'))}"), ("attempted / acknowledged / newly_executed",
          f"{v(g(ex, 'attempted'))} / {v(g(ex, 'acknowledged'))} / {v(g(ex, 'newly_executed'))}"), ("execute error", v(g(ex, 'error'))),
          ("destination effect_count (independent read-only readback, harness observation)", v(g(de, "effect_count"))),
          ("destination claim_state_after", v(g(de, "claim_state_after"))), ("operation-identity destination", v(g(de, "operation_identity_destination"))),
          ("effect_id equals the decision's expected effect_id", "yes" if g(de, "effect_ids") == [g(de, "expected_effect_id")] and g(de, "expected_effect_id") != MISSING else "NOT CONFIRMED")])
    effs = g(exp, "effects")
    if isinstance(effs, list):
        o.add(f"Effect rows retained in the executor export (chain/executor-export.json): **{len(effs)}**")
        o.add()
        for e in effs:
            o.add(f"- effect `{v(e.get('effect_id'))}` state {v(e.get('state'))} amount {v(e.get('amount'))} {v(e.get('unit'))} target {v(e.get('target'))} grant {v(e.get('grant_id'))}")
        o.add()
    else:
        o.add(f"effect rows in executor export: {MISSING if es == MISSING else es}")
        o.add()
    o.add(render_sqlite(art))
    o.add(f"Oracle: {row_line(rm, 'CHAIN-03')}")
    o.add()

    # ---- 5 operation identity and journal
    o.h(2, "5. Operation identity and journal continuity")
    op = g(obs, "chain", "operation")
    ops = g(rec, "operations")
    o.kv([("operation_id (harness observation)", v(g(op, "operation_id"))), ("identity profile on / status", f"{v(g(op, 'identity_profile_on'))} / {v(g(op, 'status'))}"),
          ("operations in the retained CP record", " ; ".join(f"{x.get('operation_id')} grant {x.get('grant_id')} first_revision {x.get('first_grant_revision')}" for x in ops) if isinstance(ops, list) else MISSING)])
    ce = g(rec, "check_events")
    if isinstance(ce, list):
        by: dict = {}
        for e in ce:
            by.setdefault(e.get("check_id"), []).append((e.get("stage"), e.get("phase")))
        o.add("Journal continuity recomputed from the retained record's check_events (the recorded events only; no new inference):")
        o.add()
        o.add("| check_id | stage | phases in recorded order | opened and completed |")
        o.add("|---|---|---|---|")
        for cid in sorted(by, key=lambda c: min(i for i, e in enumerate(ce) if e.get("check_id") == c)):
            ph = [p for _, p in by[cid]]
            o.add(f"| {cid} | {by[cid][0][0]} | {' > '.join(ph)} | {'yes' if ph[0] == 'opened' and ph[-1] == 'completed' else 'NO'} |")
        o.add()
        o.add(f"events: {len(ce)}; harness-observed n_events {v(g(obs, 'chain', 'journal', 'n_events'))}; completed stages {v(g(obs, 'chain', 'journal', 'completed_stages'))}; "
              f"distinct completed check ids {v(g(obs, 'chain', 'journal', 'distinct_completed_check_ids'))}")
    else:
        o.add(f"check_events: {MISSING}")
    o.add()
    o.add(f"Oracle: {row_line(rm, 'CHAIN-01')}; NC3-04 (operation-ledger pruning, section 9).")
    o.add()

    # ---- 6 refusal of unauthorized
    o.h(2, "6. Refusal of unauthorized effects")
    ag = g(obs, "nc_authority_gates")
    if ag == MISSING:
        o.add(f"nc_authority_gates observation: {MISSING}")
    else:
        o.add("Control case (the chain still works): " + describe_exec(g(ag, "control")))
        o.add()
        o.add("| case | outcome | effects | error |")
        o.add("|---|---|---|---|")
        for grp in ("unauthorized", "stale_or_mismatched", "evidence"):
            sub = g(ag, grp)
            if isinstance(sub, dict):
                for k in sorted(sub):
                    c = sub[k]
                    if isinstance(c, dict) and ("status" in c or "claim_ok" in c or "error" in c):
                        outc = (f"status {c['status']}, attempted {v(c.get('attempted'))}" if "status" in c else f"claim_ok {v(c.get('claim_ok'))}")
                        o.add(f"| {grp}/{k} | {outc} | {v(c.get('effect_count'))} | {str(v(c.get('error')))[:90]} |")
        o.add()
        o.add("(Cases not listed above were not present as flat records in the observation; see observations.json for the full structure.)")
    o.add()
    for rid in ("NC7-01", "NC7-02", "NC7-03", "NC5-01", "NC5-02", "NC5-03", "NC5-04", "NC5-05", "NC6-01", "NC6-02", "NC6-03", "NC6-04"):
        o.add(f"- {row_line(rm, rid)}")
    o.add()
    o.add("Boundary: these are executor-level controls on the in-process chain. The unmediated-path rows over the real socket are in section 13.")
    o.add()

    # ---- 7 revocation
    o.h(2, "7. Revocation handling")
    nr = g(obs, "nc_revocation")
    if nr == MISSING:
        o.add(f"nc_revocation observation: {MISSING}")
    else:
        o.add("| scenario | status | attempted | effects | refusal reason |")
        o.add("|---|---|---|---|---|")
        for k in ("grant_revoked", "approval_withdrawn", "grant_terminality", "approval_terminality"):
            c = g(nr, k)
            if isinstance(c, dict):
                o.add(f"| {k} | {v(c.get('status'))} | {v(c.get('attempted'))} | {v(c.get('effect_count'))} | {v(c.get('error'))} |")
            else:
                o.add(f"| {k} | {MISSING} | | | |")
        c = g(nr, "resolver_revoked")
        o.add(f"| resolver_revoked (before claim) | claim_ok {v(g(c, 'claim_ok'))} | n/a | {v(g(c, 'effect_count'))} | {v(g(c, 'error', 'message'))} |" if isinstance(c, dict) else f"| resolver_revoked | {MISSING} | | | |")
        o.add()
        for k in ("grant_terminality", "approval_terminality"):
            c = g(nr, k)
            if isinstance(c, dict):
                o.add(f"- {k}: reactivation accepted {v(c.get('reactivation_accepted'))}; reactivation error: {v(g(c, 'reactivation_error', 'message'))}")
        o.add()
    for rid in ("NC1-01", "NC1-02", "NC1-03", "NC1-04", "NC1-05"):
        o.add(f"- {row_line(rm, rid)}")
    o.add()

    # ---- 8 duplicate and lost-ack
    o.h(2, "8. Duplicate effect and lost-acknowledgement behaviour")
    du = g(obs, "nc_duplicate")
    o.add("Duplicate effect (route B, executor level):")
    o.add()
    if du == MISSING:
        o.add(f"nc_duplicate observation: {MISSING}")
    else:
        o.kv([("first execute", describe_exec(g(du, "first"))), ("same claim replayed", describe_exec(g(du, "same_claim"), True)), ("second claim for the same decision", describe_exec(g(du, "second_claim"), True)),
              ("cap-2 renewal, same operation id: r1 / r2", f"{describe_exec(g(du, 'renewal_cap2', 'r1'))} // {describe_exec(g(du, 'renewal_cap2', 'r2'), True)}")])
    am = g(obs, "nc_ambiguous")
    o.add("Lost acknowledgement (`simulate='lost_ack'`, fault injected by the trusted harness at the executor; EXECUTOR-LEVEL evidence):")
    o.add()
    if am == MISSING:
        o.add(f"nc_ambiguous observation: {MISSING}")
    else:
        fr = g(am, "first")
        o.kv([("first result", f"status {v(g(fr, 'status'))}, acknowledged {v(g(fr, 'acknowledged'))}, attempted {v(g(fr, 'attempted'))}, retry_eligible {v(g(fr, 'observation', 'retry_eligible'))}; error: {v(g(fr, 'error'))}"),
              ("destination after", f"claim {v(g(am, 'destination', 'claim_state_after_first'))}, effects {v(g(am, 'destination', 'effect_count'))}"),
              ("retry of same claim", describe_exec(g(am, "retry"), True)),
              ("reconcile_claim", f"status {v(g(am, 'reconcile', 'value', 'status'))}, effect {short(g(am, 'reconcile', 'value', 'effect_id'))}, retry_eligible {v(g(am, 'reconcile', 'value', 'retry_eligible'))}; effects after reconcile {v(g(am, 'destination', 'effect_count_after_reconcile'))}"),
              ("reconcile route unavailable", f"status {v(g(am, 'reconcile_unavailable', 'status'))}, retry_eligible {v(g(am, 'reconcile_unavailable', 'retry_eligible'))}"),
              ("export + Replay of the unknown outcome", f"export ok {v(g(am, 'export', 'ok'))}; Replay ok {v(g(am, 'replay', 'ok'))}, records {v(g(am, 'replay', 'n_records'))}, all reports complete {v(g(am, 'replay', 'all_reports_complete'))}")])
    ia = g(obs, "nc_ingress_ambiguity")
    o.add("Ambiguous acknowledgement through the supported ingress (NC2-06; evidence level as recorded below; real socket, so see section 13 for what it does and does not show):")
    o.add()
    if ia == MISSING:
        o.add(f"nc_ingress_ambiguity observation: {MISSING}")
    else:
        o.add(f"evidence_level {v(g(ia, 'evidence_level'))}; client response {v(g(ia, 'ack', 'client_response'))}; effect_count_after_first {v(g(ia, 'boundary', 'effect_count_after_first'))}; blocked/other reason: {v(g(ia, 'blocked_reason'))}")
    o.add()
    for rid in ("NC3-01", "NC3-02", "NC3-03", "NC2-01", "NC2-02", "NC2-03", "NC2-04", "NC2-05", "NC2-06"):
        o.add(f"- {row_line(rm, rid)}")
    o.add()

    # ---- 9 kill and pruning
    o.h(2, "9. Real process kill and operation-ledger pruning observations")
    pk = g(obs, "nc_process_kill")
    o.add("Real OS process death (A1): a child process running the pinned route-B atomic executor on a durable on-disk store is killed with SIGKILL by another process; a fresh observer process reopens the store.")
    o.add()
    if pk == MISSING:
        o.add(f"nc_process_kill observation: {MISSING}")
    else:
        o.add(f"observation status: {v(g(pk, 'status'))}; seams recorded: {v(g(pk, 'seams'))}")
        o.add()
        o.add("| seam | killed by SIGKILL | victim returncode | on reopen (effects / claim) | reconcile_first | reconcile_second | final (effects / claim) |")
        o.add("|---|---|---|---|---|---|---|")
        seams = g(pk, "seams")
        names = seams if isinstance(seams, list) and seams else [k for k in ("after_begin", "after_effect_insert_before_commit", "after_commit") if k in pk]
        for s in names:
            sm = g(pk, s)
            if not isinstance(sm, dict):
                o.add(f"| {s} | {MISSING} | | | | | |")
                continue
            r = g(sm, "recovered")
            o.add(f"| {s} | {v(g(sm, 'victim', 'killed_by_sigkill'))} | {v(g(sm, 'victim', 'returncode'))} | {v(g(r, 'on_reopen', 'effect_count'))} / {v(g(r, 'on_reopen', 'claim_state'))} | "
                  f"{v(g(r, 'reconcile_first', 'status'))} ({v(g(r, 'reconcile_first', 'reason'))}) | {v(g(r, 'reconcile_second', 'status'))} | {v(g(r, 'final', 'effect_count'))} / {v(g(r, 'final', 'claim_state'))} |")
        o.add()
        o.add("Retained kill artifacts (nc_process_kill/<seam>/): " + ", ".join(f"{s}: {file_state(art / 'nc_process_kill' / s / 'observations.json') if art else MISSING}" for s in names))
        o.add()
    o.add("Scope limit as stated by the harness: SIGKILL of a process at three seams on a durable store. Power loss, OS crash and recovery of a lost acknowledgement stay UNQUALIFIED.")
    o.add()
    o.add(f"- {row_line(rm, 'NC2-07')}")
    o.add()
    lp = g(obs, "nc_ledger_pruning")
    o.add("Operation-ledger pruning (A2, documented limit): the Control Plane operation ledger is pruned after one committed effect.")
    o.add()
    if lp == MISSING:
        o.add(f"nc_ledger_pruning observation: {MISSING}")
    else:
        o.kv([("control (unpruned) second decision", f"{v(g(lp, 'control', 'decision_result'))}; reasons {v(g(lp, 'control', 'decision_reasons'))}"),
              ("ledger rows before / after pruning", f"{v(g(lp, 'pruned', 'rows_before'))} / {v(g(lp, 'pruned', 'rows_after'))}"),
              ("Control Plane decision on the pruned record", f"{v(g(lp, 'pruned', 'cp_decision_result'))}; reasons {v(g(lp, 'pruned', 'cp_decision_reasons'))}"),
              ("claim issued for the second decision", v(g(lp, "pruned", "claim_issued"))),
              ("second execute", describe_exec(g(lp, "pruned", "second_execute"), True)),
              ("destination effects after (still only the original)", f"{v(g(lp, 'pruned', 'effect_count'))}; only_original_effect {v(g(lp, 'pruned', 'only_original_effect'))}"),
              ("Verifier on the pruned record (informational)", f"overall {v(g(lp, 'verifier_informational', 'overall'))}; exit {v(g(lp, 'verifier_informational', 'exit_code'))}; finding codes {v(g(lp, 'verifier_informational', 'finding_codes'))}")])
        o.add("Reading of the recorded values: pruning the Control Plane ledger lets the Control Plane authorize again (the oracle titles this a documented limit, row NC3-04); the destination's operation identity refuses the second effect. The Verifier's reaction above is informational.")
    o.add()
    o.add(f"- {row_line(rm, 'NC3-04')}")
    o.add()

    # ---- 10 Replay
    o.h(2, "10. Replay reconstruction")
    rp = g(obs, "chain", "replay")
    bun, bs = A("chain/replay-bundle.json")
    o.kv([("harness observation: ok / n_records / n_reports / all_reports_complete", f"{v(g(rp, 'ok'))} / {v(g(rp, 'n_records'))} / {v(g(rp, 'n_reports'))} / {v(g(rp, 'all_reports_complete'))}"),
          ("harness observation: error", v(g(rp, "error")))])
    if bun is None:
        o.add(f"chain/replay-bundle.json: {bs}")
    else:
        irs = g(bun, "import_reports")
        o.kv([("bundle status (retained file)", v(g(bun, "status"))), ("bundle_id / run_id", f"{v(g(bun, 'bundle_id'))} / {v(g(bun, 'run_id'))}"), ("records in bundle", len(g(bun, "records")) if isinstance(g(bun, "records"), list) else MISSING),
              ("import reports: complete flags", v([r.get("complete") for r in irs]) if isinstance(irs, list) else MISSING),
              ("Replay semantics: record_reconstruction", v(g(bun, "semantics", "record_reconstruction"))),
              ("Replay semantics: external_effect_execution", v(g(bun, "semantics", "external_effect_execution"))),
              ("Replay semantics: independent_effect_verification", v(g(bun, "semantics", "independent_effect_verification"))),
              ("Replay semantics: destination_observation", v(g(bun, "semantics", "destination_observation"))), ("Replay semantics: notes", v(g(bun, "semantics", "notes")))])
        o.add("Reading: Replay reconstructs recorded events only; it re-executes nothing and the destination observation is producer-reported (as the retained semantics above state).")
    o.add()
    o.add(f"- {row_line(rm, 'CHAIN-05')}")
    o.add()

    # ---- 11 Evidence pack
    o.h(2, "11. Evidence Pack reconstruction")
    pk2 = g(obs, "chain", "pack")
    pack, pks = A("chain/evidence-pack.json")
    o.kv([("harness observation: ok / valid / error", f"{v(g(pk2, 'ok'))} / {v(g(pk2, 'valid'))} / {v(g(pk2, 'error'))}")])
    if pack is None:
        o.add(f"chain/evidence-pack.json: {pks}")
    else:
        vs = g(pack, "validation_summary")
        rb = g(pack, "replay_bundles")
        o.kv([("pack_id / pack_version", f"{v(g(pack, 'pack_id'))} / {v(g(pack, 'pack_version'))}"), ("review_status", v(g(pack, "review_status"))),
              ("validation_summary", f"valid {v(g(vs, 'valid_bundle_count'))}, invalid {v(g(vs, 'invalid_bundle_count'))}, errors {v(g(vs, 'error_count'))}, warnings {v(g(vs, 'warning_count'))}"),
              ("retained replay bundle reference", v([{"status": b.get("status"), "validation_status": b.get("validation_status"), "signed": b.get("signed"), "bundle_id": b.get("bundle_id")} for b in rb]) if isinstance(rb, list) else MISSING)])
        o.add(f"Pack caveat as the pack itself states: {v(g(vs, 'summary'))}")
    o.add()
    o.add(f"- {row_line(rm, 'CHAIN-06')}")
    o.add()

    # ---- 12 Verifier
    render_verifier(o, obs, art, rm)

    # ---- 13 socket
    o.h(2, "13. The real-socket trusted ingress, kept separate")
    o.add(f"> {Q14}")
    o.add()
    o.add(f"PROHIBITED: \"{PROHIBITED}\" The rows below are separate observations of the ingress boundary; they are not the source of sections 2 to 12.")
    o.add()
    for rid in sorted(k for k in rm if k.startswith("NC4-") or k == "KL-01"):
        r = rm[rid]
        o.add(f"- {rid}: **{r.get('status')}** (mandatory: {v(r.get('mandatory'))}) - {str(r.get('reason', ''))[:240]}")
    if not any(k.startswith("NC4-") for k in rm):
        o.add(f"- no NC4 rows: {MISSING}")
    o.add()
    nu = g(obs, "nc_unmediated")
    if nu != MISSING:
        o.add(f"NC4 observation: profile {v(g(nu, 'profile'))}, ingress probe ran: {v(g(nu, 'ingress', 'probe_ran'))}; blocked_reason: {v(g(nu, 'blocked_reason'))}")
        o.add()
        o.add("Any BLOCKED row above means the exact approved host profile was not available on the machine that produced these artifacts; it is reported BLOCKED, never PASS.")
    o.add()

    # ---- 14 custody
    render_custody(o, ev, chain, art, obs, res)

    o.h(2, "15. Artifact inventory (expected files)")
    exp_files = ["observations.json", "results.json", "artifacts/chain/cp-run-record.json", "artifacts/chain/proposal.json", "artifacts/chain/executor-export.json", "artifacts/chain/replay-bundle.json",
                 "artifacts/chain/evidence-pack.json", "artifacts/chain-destination.sqlite", "artifacts/verifier/A-report.json", "artifacts/verifier/B-report.json",
                 "artifacts/nc_process_kill/after_begin/observations.json", "artifacts/nc_process_kill/after_effect_insert_before_commit/observations.json",
                 "artifacts/nc_process_kill/after_commit/observations.json", "artifacts/nc_ledger_pruning/cp-run-record.pruned.json", "artifacts/verifier/pruned-report.json"]
    o.add("| file under the chain results directory | state |")
    o.add("|---|---|")
    for f in exp_files:
        o.add(f"| {f} | {'present' if (chain / f).is_file() else MISSING} |")
    o.add()
    o.add("| run-level file | state |")
    o.add("|---|---|")
    for f in ("run-identity.json", "RUN-IDENTITY.json", "gate-verdict.json", "custody-evidence.json", "tuple-resolved.json", "SHA256SUMS", "ARTIFACT-SHA256SUMS-VERIFY.txt", "environment-record (mvp-chain/artifacts/environment-record.json)"):
        p = (chain / "artifacts" / "environment-record.json") if f.startswith("environment-record") else ev.run_file(f)
        o.add(f"| {f} | {file_state(p) if p is not None else MISSING + ' (no run-level directory)'} |")
    o.add()
    return finish(o, label)


def finish(o: Out, label: str) -> str:
    o.add("---")
    o.add("Standing holds unchanged: no acceptance, certification, Tier 1, Q7, release or production claim is made or implied by this rendering.")
    if label:
        o.add()
        o.add(f"**{label}**")
    return o.text()


def describe_exec(c, refusal=False) -> str:
    if not isinstance(c, dict):
        return MISSING
    parts = [f"status {v(c.get('status'))}", f"attempted {v(c.get('attempted'))}", f"acknowledged {v(c.get('acknowledged'))}"]
    if "newly_executed" in c:
        parts.append(f"newly_executed {v(c.get('newly_executed'))}")
    if "effect_count" in c:
        parts.append(f"effects {v(c.get('effect_count'))}")
    if c.get("error") is not None or refusal:
        parts.append(f"error: {v(c.get('error'))}")
    return ", ".join(parts)


def render_sqlite(art: Path | None) -> str:
    L = []
    p = (art / "chain-destination.sqlite") if art else None
    if p is None or not p.is_file():
        return f"Destination database copy (artifacts/chain-destination.sqlite): {MISSING}\n"
    td = Path(tempfile.mkdtemp(prefix="render_demo_"))
    try:
        for suf in ("", "-wal", "-shm"):
            s = Path(str(p) + suf)
            if s.is_file():
                shutil.copy(s, td / ("d.sqlite" + suf))
        c = sqlite3.connect(f"file:{td / 'd.sqlite'}?mode=ro", uri=True)
        try:
            tabs = [r[0] for r in c.execute("select name from sqlite_master where type='table' order by name")]
            L.append(f"Destination database copy (artifacts/chain-destination.sqlite, sha256 `{sha256_file(p)}`), opened read-only on a private temporary copy:")
            L.append("")
            for t in tabs:
                n = c.execute(f'select count(*) from "{t}"').fetchone()[0]
                L.append(f"- table `{t}`: {n} row(s)")
                if t == "effects":
                    cols = [r[1] for r in c.execute('pragma table_info("effects")')]
                    for row in c.execute('select * from "effects" order by 1').fetchall():
                        L.append("  - " + ", ".join(f"{k}={short(x, 20)}" for k, x in zip(cols, row)))
            L.append("")
            L.append(f"Sidecar files retained beside the copy: wal {'present' if Path(str(p) + '-wal').is_file() else MISSING}, shm {'present' if Path(str(p) + '-shm').is_file() else MISSING}. "
                     "If the copy shows fewer effect rows than the harness's independent readback above, the copy is not a complete picture of the destination: "
                     "the harness copies only the main database file (INFERENCE: committed rows may still sit in the write-ahead log); the effect rows retained in the executor export are the authoritative retained record here.")
        finally:
            c.close()
    except sqlite3.Error as exc:
        L.append(f"Destination database copy: UNREADABLE ({type(exc).__name__})")
    finally:
        shutil.rmtree(td, ignore_errors=True)
    return "\n".join(L) + "\n"


def render_verifier(o: Out, obs, art, rm):
    o.h(2, "12. Verifier disposition")
    o.add("The pinned Verifier ran as a subprocess over the raw Control Plane record. Dispositions below are the Verifier's own words (from the harness observation); "
          "**ABSTAIN is reported as ABSTAIN and is never a PASS.** An oracle row PASS (VER-01..04) means the harness's expectation held (for example, that exit code 0 or 3 occurred, no crash, no refutation); "
          "it does not mean the Verifier accepted.")
    o.add()
    vr = g(obs, "chain", "verifier")
    if vr == MISSING:
        o.add(f"chain.verifier observation: {MISSING}")
        o.add()
        return
    o.add("| run | inputs | overall (as recorded) | exit code | checks | confirmed | could not check | refuted | crashed | refuting finding codes |")
    o.add("|---|---|---|---|---|---|---|---|---|---|")
    for k, desc in (("A", "record + proposal + manifest"), ("B", "A + harness-derived ledger")):
        r = g(vr, k)
        if not isinstance(r, dict):
            o.add(f"| {k} | {desc} | {MISSING} | | | | | | | |")
            continue
        ov = r.get("overall")
        shown = (str(ov).upper() if isinstance(ov, str) else MISSING)
        o.add(f"| {k} | {desc} | **{shown}** | {v(r.get('exit_code'))} | {v(g(r, 'summary', 'checks'))} | {v(g(r, 'summary', 'confirmed'))} | {v(g(r, 'summary', 'could_not_check'))} | "
              f"{v(g(r, 'summary', 'refuted'))} | {v(r.get('crashed'))} | {v(r.get('finding_codes'))} |")
    o.add()
    for k in ("A", "B"):
        r = g(vr, k)
        if not isinstance(r, dict):
            continue
        cnc = r.get("could_not_check_reasons")
        o.add(f"Run {k} could-not-check checks: " + ("; ".join(f"{c} ({why})" for c, why in sorted(cnc.items())) if isinstance(cnc, dict) and cnc else "none recorded"))
        # cross-check the report file against the observation
        rep, rst = load(art / "verifier" / f"{k}-report.json") if art else (None, MISSING)
        if rep is None:
            o.add(f"- verifier/{k}-report.json: {rst}")
        else:
            fsum = g(rep, "summary")
            same = (isinstance(fsum, dict) and fsum == r.get("summary"))
            o.add(f"- retained report verifier/{k}-report.json (sha256 `{sha256_file(art / 'verifier' / f'{k}-report.json')}`): summary {v(fsum)} - {'MATCHES' if same else 'DIFFERS FROM'} the harness observation; "
                  f"observation's report_sha256 {'MATCHES' if r.get('report_sha256') == sha256_file(art / 'verifier' / f'{k}-report.json') else 'does not match (it hashes canonical JSON, not file bytes, or the file differs)'}")
            if k == "A":
                dnp = g(rep, "does_not_prove")
                if isinstance(dnp, list):
                    o.add(f"- the report's own does_not_prove list ({len(dnp)} items): " + ", ".join(str(x.get('id')) for x in dnp))
    o.add()
    # link: verifier inputs vs retained chain files
    if art:
        pairs = (("record", "chain/cp-run-record.json"), ("proposal", "chain/proposal.json"))
        a = g(vr, "A", "inputs")
        for role, rel in pairs:
            p = art / rel
            if isinstance(a, dict) and p.is_file():
                o.add(f"- Verifier run A input `{role}` {short(a.get(role), 12)} vs sha256 of retained {rel}: **{'MATCH' if a.get(role) == sha256_file(p) else 'MISMATCH'}**")
        o.add()
    o.add("Reading of ABSTAIN here: the Verifier did not refute and could not check the ledger-based items in run A because no ledger input was supplied; run B supplies a harness-derived ledger and narrows the "
          "could-not-check set (as recorded above). This is an abstention on part of the checks, not an acceptance of the record.")
    o.add()
    for rid in ("VER-01", "VER-02", "VER-03", "VER-04"):
        o.add(f"- {row_line(rm, rid)}")
    o.add()
    # differential controls
    for k, nm in (("T0", "untampered control"), ("T1", "decision-altered")):
        rep, rst = load(art / "verifier" / f"{'T0-untampered' if k == 'T0' else 'T1-decision-altered'}-report.json") if art else (None, MISSING)
        o.add(f"- differential Verifier input {k} ({nm}): report {rst if rep is None else 'present, summary ' + v(g(rep, 'summary'))}")
    o.add(f"- {row_line(rm, 'NC5-04')}")
    o.add()


def render_custody(o: Out, ev: Ev, chain: Path, art, obs, res):
    o.h(2, "14. Evidence custody hashes")
    f_obs, f_res = chain / "observations.json", chain / "results.json"
    rows = []
    if f_obs.is_file():
        h = sha256_file(f_obs)
        rows.append(("observations.json sha256", h))
        rec = g(res, "observations_sha256")
        rows.append(("results.json observations_sha256", f"{rec} - {'MATCH' if rec == h else 'MISMATCH'}"))
    else:
        rows.append(("observations.json", MISSING))
    rows.append(("results.json sha256", sha256_file(f_res) if f_res.is_file() else MISSING))
    o.kv(rows)
    # SHA256SUMS verification (read only)
    for nm, base in (("SHA256SUMS (committed tree)", ev.run), ("SHA256SUMS.run-job (run job's own)", ev.run)):
        fn = nm.split(" ")[0]
        p = (ev.run / fn) if ev.run else None
        if p is None or not p.is_file():
            o.add(f"{fn}: {MISSING}")
            o.add()
            continue
        ok = bad = miss = 0
        bads = []
        for line in p.read_text(errors="replace").splitlines():
            if not line.strip() or "  " not in line:
                continue
            h, rel = line.split("  ", 1)
            rel = rel.strip()
            rel = rel[2:] if rel.startswith("./") else rel
            q = ev.run / rel
            if not q.is_file():
                miss += 1
                bads.append(f"{rel}: MISSING")
            elif sha256_file(q) == h:
                ok += 1
            else:
                bad += 1
                bads.append(f"{rel}: MISMATCH")
        o.add(f"{fn} (sha256 `{sha256_file(p)}`): {ok} file(s) verified, {bad} MISMATCH, {miss} MISSING.")
        for b in bads[:25]:
            o.add(f"- {b}")
        o.add()
    vf = ev.run_file("ARTIFACT-SHA256SUMS-VERIFY.txt") if ev.run else None
    if vf is not None and vf.is_file():
        o.add("ARTIFACT-SHA256SUMS-VERIFY.txt (recorded by the evidence job; last line): " + (vf.read_text(errors="replace").strip().splitlines() or ["(empty)"])[-1])
        o.add()
    # per-artifact hashes
    if art and art.is_dir():
        o.add("Hashes of the retained chain artifacts (computed now, file bytes):")
        o.add()
        o.add("| file | sha256 | bytes |")
        o.add("|---|---|---|")
        for p in sorted(art.rglob("*")):
            if p.is_file() and p.suffix in (".json", ".sqlite") and not p.name.endswith(("-wal", "-shm")):
                o.add(f"| {p.relative_to(chain).as_posix()} | `{sha256_file(p)}` | {p.stat().st_size} |")
        o.add()
    else:
        o.add(f"artifacts directory: {MISSING}")
        o.add()
    omit = ev.run_file("OMITTED-LARGE-FILES.txt") if ev.run else None
    if omit is not None and omit.is_file():
        o.add("OMITTED-LARGE-FILES.txt is present: some files were not committed to the evidence branch (listed with their hashes there).")
        o.add()
    if ev.run is not None:
        top = ev.run / "tuple-resolved.json"
        tr, ts = load(top)
        o.add(f"tuple-resolved.json: {ts if tr is None else 'present, qualification_sha ' + v(g(tr, 'qualification_sha'))}")
        o.add()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read-only demonstration renderer for the synthetic $10 refund MVP evidence.")
    ap.add_argument("evidence_dir")
    ap.add_argument("--label", default="", help="banner printed at the top and bottom, for example 'DRY RUN, NOT EVIDENCE'")
    a = ap.parse_args(argv)
    d = Path(a.evidence_dir)
    if not d.is_dir():
        sys.stderr.write(f"evidence directory {d} does not exist\n")
        return 2
    sys.stdout.write(render(Ev(d), a.label))
    return 0


if __name__ == "__main__":
    sys.exit(main())
