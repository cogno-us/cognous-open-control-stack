#!/usr/bin/env bash
# OCS-MVP-QGATE-03 / Worker B: TEST-ONLY synthetic ingress setup + unmodified environment-record capture.
#
# Usage (as root, e.g. under sudo, on a GitHub-hosted ubuntu-24.04 runner):
#   run_integration.sh REPO_ROOT CP_ROOT RT_ROOT EVDIR
#   Optional environment: PY (interpreter that runs BOTH the ingress and the capture; default python3.13/python3/python on PATH),
#   QG3_BASE (default /var/lib/qgate03-ocs, must not exist), QG3_UID_BASE (default 61200), QG3_MAXREQ (default 16),
#   QG3_IPC_MODE (default 2750, the profile value), QG3_PIN_CP / QG3_PIN_RT (component commits, defaults = the pins).
#
# What it does (see docs/mvp-recovery/qgate-03/synthetic-ingress-configuration.md): creates throwaway test accounts and a
# root-owned test directory, starts the REAL supported ingress launcher with synthetic data under an unprivileged uid with an
# empty capability set, calls diagnostics.sh (if present), runs the UNMODIFIED capture script, then records non-effecting
# peer-uid controls through the existing client entry point, and finally removes everything it created.
#
# Non-authorizing. Not a qualification. Synthetic data only: no network, no secrets, no production interface.
# Deliberately no `set -e`: every command's stdout/stderr/exit status is saved under EVDIR (<name>.out/.err/.rc) and the script
# always runs to cleanup and exits 0 unless it is itself broken (bad usage -> 2).

umask 022
if [ "$#" -ne 4 ]; then
  echo "usage: $0 REPO_ROOT CP_ROOT RT_ROOT EVDIR" >&2
  exit 2
fi
REPO_ROOT=$(cd "$1" 2>/dev/null && pwd -P) || { echo "bad REPO_ROOT $1" >&2; exit 2; }
CP_SRC=$(cd "$2" 2>/dev/null && pwd -P) || { echo "bad CP_ROOT $2" >&2; exit 2; }
RT_SRC=$(cd "$3" 2>/dev/null && pwd -P) || { echo "bad RT_ROOT $3" >&2; exit 2; }
mkdir -p "$4" || { echo "cannot create EVDIR $4" >&2; exit 2; }
EV=$(cd "$4" && pwd -P)

PIN_CP=${QG3_PIN_CP:-7a4bcd40b3b49e61ff3c294dcca53b52f460b22c}
PIN_RT=${QG3_PIN_RT:-c5e97e87dd239c821b1b4a406a55dcd03c5bc61f}
BASE=${QG3_BASE:-/var/lib/qgate03-ocs}
UID_BASE=${QG3_UID_BASE:-61200}
MAXREQ=${QG3_MAXREQ:-16}
IPC_MODE=${QG3_IPC_MODE:-2750}
LABEL="github-hosted ubuntu-24.04 QGATE-03 synthetic ingress; unfrozen; NOT qualified"
PY=${PY:-$(command -v python3.13 || command -v python3 || command -v python)}

N_ING=qg3-ingress; N_CLI=qg3-client; N_OUT=qg3-outsider; N_WRG=qg3-wrong; N_IPC=qg3-ipc
CREATED_BASE=0; CREATED=""            # space-separated list of "u:name" / "g:name" this script created
ING_PID=""; CLEANED=0
STATE=""; IPC=""; SOCK=""; HUB=""; CP=""; RT=""

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$EV/run_integration.log"; }
# run NAME CMD...: save stdout, stderr and exit status of CMD under EVDIR; never aborts.
run() { local n=$1; shift; "$@" >"$EV/$n.out" 2>"$EV/$n.err"; local rc=$?; echo "$rc" >"$EV/$n.rc"; log "$n rc=$rc"; return $rc; }
# runin DIR NAME CMD...: same, with a working directory.
runin() { local d=$1; shift; ( cd "$d" 2>/dev/null || exit 126; run "$@" ); }
phase() { echo "$1 $2" >>"$EV/phases.txt"; log "phase $1: $2"; }

pick_id() { local n=$1; while getent passwd "$n" >/dev/null 2>&1 || getent group "$n" >/dev/null 2>&1; do n=$((n+1)); done; echo "$n"; }

mkacct() {  # mkacct NAME -> sets ACCT_ID; creates group NAME (gid=uid) and system-style user NAME, no home, no login
  local name=$1 id; id=$(pick_id "$NEXT_ID"); NEXT_ID=$((id+1))
  run "setup-groupadd-$name" groupadd --gid "$id" "$name" || return 1
  CREATED="$CREATED g:$name"
  run "setup-useradd-$name" useradd --system --uid "$id" --gid "$id" --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin "$name" || return 1
  CREATED="$CREATED u:$name"
  ACCT_ID=$id
}

cleanup() {
  [ "$CLEANED" = 1 ] && return
  CLEANED=1
  trap - EXIT
  phase cleanup start
  if [ -n "$ING_PID" ] && kill -0 "$ING_PID" 2>/dev/null; then
    kill -TERM "$ING_PID" 2>/dev/null
    for _ in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$ING_PID" 2>/dev/null || break; sleep 1; done
    kill -0 "$ING_PID" 2>/dev/null && kill -KILL "$ING_PID" 2>/dev/null
    echo "ingress stopped (pid $ING_PID)" >"$EV/cleanup-ingress.out"
  fi
  if [ "$CREATED_BASE" = 1 ] && [ -n "$BASE" ] && [ "$BASE" != "/" ]; then
    run cleanup-rm-base rm -rf -- "$BASE"
  fi
  for item in $(echo "$CREATED" | tr ' ' '\n' | tac); do
    case $item in
      u:*) run "cleanup-userdel-${item#u:}" userdel "${item#u:}" ;;
    esac
  done
  for item in $(echo "$CREATED" | tr ' ' '\n' | tac); do
    case $item in
      g:*) getent group "${item#g:}" >/dev/null 2>&1 && run "cleanup-groupdel-${item#g:}" groupdel "${item#g:}" ;;  # userdel already removes a user's private group
    esac
  done
  { for n in $N_ING $N_CLI $N_OUT $N_WRG $N_IPC; do getent passwd "$n"; getent group "$n"; done; ls -ld "$BASE"; } >"$EV/cleanup-residue-check.out" 2>&1
  phase cleanup done
  exit 0
}
trap cleanup EXIT
trap 'log "signal received"; exit 0' INT TERM HUP

: >"$EV/phases.txt"
phase start "REPO_ROOT=$REPO_ROOT CP_ROOT=$CP_SRC RT_ROOT=$RT_SRC BASE=$BASE PY=$PY"
{ echo "euid=$(id -u)"; id; uname -a; date -u; echo "PY=$PY"; echo "BASE=$BASE UID_BASE=$UID_BASE MAXREQ=$MAXREQ IPC_MODE=$IPC_MODE"; echo "PIN_CP=$PIN_CP"; echo "PIN_RT=$PIN_RT"; echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}"; } >"$EV/env-summary.out" 2>&1
run os-release cat /etc/os-release
run tools-present bash -c 'command -v setpriv useradd groupadd gpasswd userdel groupdel getfacl'
run python-version "$PY" -c 'import sys,platform;print(sys.version);print(sys.executable);print(platform.python_implementation())'
run python-realpath readlink -f "$PY"
run deps-check-as-root "$PY" -I -c 'import pydantic,sys;print("pydantic",pydantic.VERSION)'
for d in "$CP_SRC" "$RT_SRC" "$REPO_ROOT"; do
  b=$(basename "$d")
  [ -e "$d/.git" ] && runin "$d" "git-head-$b" git rev-parse HEAD
done
run base-ancestors-before bash -c 'for d in /var/lib /var /; do stat -c "%n %U:%G %a" "$d"; command -v getfacl >/dev/null && getfacl -p "$d" 2>&1; done'

SETUP_OK=1
if [ "$(id -u)" != 0 ]; then echo "not root" >"$EV/setup-fatal.out"; SETUP_OK=0; fi
[ -x "$PY" ] || { echo "no usable python interpreter: $PY" >"$EV/setup-fatal.out"; SETUP_OK=0; }
[ -e "$BASE" ] && { echo "BASE $BASE already exists; refusing to reuse or remove it" >"$EV/setup-fatal.out"; SETUP_OK=0; }

# ---- (1) synthetic identities --------------------------------------------------------------------------------------------
if [ "$SETUP_OK" = 1 ]; then
  NEXT_ID=$UID_BASE
  mkacct "$N_ING" && ING_UID=$ACCT_ID || SETUP_OK=0
  mkacct "$N_CLI" && CLI_UID=$ACCT_ID || SETUP_OK=0
  mkacct "$N_OUT" && OUT_UID=$ACCT_ID || SETUP_OK=0
  mkacct "$N_WRG" && WRG_UID=$ACCT_ID || SETUP_OK=0
  NEXT_ID=$((NEXT_ID+1))
  IPC_GID=$(pick_id "$NEXT_ID")
  run setup-groupadd-ipc groupadd --gid "$IPC_GID" "$N_IPC" && CREATED="$CREATED g:$N_IPC" || SETUP_OK=0
  # dedicated group holds EXACTLY ingress + client (nobody has it as a primary group). The wrong-member user is added later,
  # AFTER the capture, only for the negative control.
  run setup-gpasswd-ingress gpasswd -a "$N_ING" "$N_IPC" || SETUP_OK=0
  run setup-gpasswd-client gpasswd -a "$N_CLI" "$N_IPC" || SETUP_OK=0
  ING_GID=$ING_UID; CLI_GID=$CLI_UID; OUT_GID=$OUT_UID; WRG_GID=$WRG_UID
  { echo "ingress $N_ING uid=$ING_UID gid=$ING_GID"; echo "client $N_CLI uid=$CLI_UID gid=$CLI_GID"; echo "outsider $N_OUT uid=$OUT_UID gid=$OUT_GID"
    echo "wrong-member $N_WRG uid=$WRG_UID gid=$WRG_GID (joins $N_IPC only after the capture)"; echo "ipc group $N_IPC gid=$IPC_GID"; } >"$EV/identities.out"
  run identities-getent bash -c "getent passwd $N_ING $N_CLI $N_OUT $N_WRG; getent group $N_ING $N_CLI $N_OUT $N_WRG $N_IPC"
fi
phase identities "SETUP_OK=$SETUP_OK"

# ---- (2) directories and a root-owned, ACL-free copy of the sources ------------------------------------------------------
if [ "$SETUP_OK" = 1 ]; then
  run setup-mkdir-base mkdir -m 0755 -- "$BASE" && CREATED_BASE=1 || SETUP_OK=0
fi
if [ "$SETUP_OK" = 1 ]; then
  BASE=$(cd "$BASE" && pwd -P)
  STATE=$BASE/state; IPC=$BASE/ipc; SOCK=$IPC/ingress.sock; HUB=$BASE/src/hub; CP=$BASE/src/cp; RT=$BASE/src/rt
  run setup-mkdir-src mkdir -p -- "$HUB/tools" "$CP" "$RT"
  # Why a copy: /home/runner (the checkout location) is mode 0750 on ubuntu-24.04, so the ingress uid could not read the
  # sources there. Only the two hub tool directories the run needs are copied (the supported launcher and the capture script),
  # plus the pinned CP and RT trees; .git and any bytecode are excluded (the launcher refuses to start if bytecode exists).
  run copy-hub-ingress   bash -c "tar -C '$REPO_ROOT/tools' --exclude=__pycache__ --exclude='*.pyc' -cf - mvp_ingress mvp_env_record | tar -C '$HUB/tools' --no-same-owner -xf -"
  run copy-cp            bash -c "tar -C '$CP_SRC' --exclude=.git --exclude=__pycache__ --exclude='*.pyc' -cf - . | tar -C '$CP' --no-same-owner -xf -"
  run copy-rt            bash -c "tar -C '$RT_SRC' --exclude=.git --exclude=__pycache__ --exclude='*.pyc' -cf - . | tar -C '$RT' --no-same-owner -xf -"
  run copy-perms         bash -c "chown -R root:root '$BASE/src' && chmod -R go-w,a+rX '$BASE/src'"
  run copy-verify-hub    bash -c "cd '$REPO_ROOT/tools' && for f in mvp_ingress/*.py mvp_env_record/capture_env_record.py; do a=\$(sha256sum \"\$f\" | cut -d' ' -f1); b=\$(sha256sum '$HUB/tools/'\"\$f\" | cut -d' ' -f1); [ \"\$a\" = \"\$b\" ] && echo \"same \$f \$a\" || echo \"DIFFERENT \$f\"; done"
  run copy-verify-bytecode bash -c "find '$BASE/src' -name __pycache__ -o -name '*.pyc' | head"
  # state directory: owner-only, owned by the ingress uid, created before the ingress starts (the ingress then creates 0600 files)
  run setup-state mkdir -m 0700 -- "$STATE"
  run setup-state-chown chown "$ING_UID:$ING_GID" "$STATE"
  # IPC directory: owner ingress uid (it must create the socket), group = dedicated group, setgid so the socket inherits it
  run setup-ipc mkdir -- "$IPC"
  run setup-ipc-chown chown "$ING_UID:$IPC_GID" "$IPC"
  run setup-ipc-chmod chmod "$IPC_MODE" "$IPC"
  run setup-stat bash -c "stat -c '%n %U:%G %a %F' '$BASE' '$STATE' '$IPC'; command -v getfacl >/dev/null && getfacl -p '$BASE' '$STATE' '$IPC' 2>&1"
  # synthetic manifest (test data only; digest pinned below)
  printf '%s\n' '{"synthetic":true,"purpose":"OCS-MVP-QGATE-03 host-integration feasibility; NOT a frozen manifest","note":"no authority, no credentials, no production data"}' >"$EV/synthetic-manifest.json"
  MANIFEST_SHA=$(sha256sum "$EV/synthetic-manifest.json" | cut -d' ' -f1)
fi
phase directories "SETUP_OK=$SETUP_OK"

# ---- (3) the real ingress, unprivileged, empty capability set --------------------------------------------------------------
INGRESS_UP=0
if [ "$SETUP_OK" = 1 ]; then
  # interpreter and dependency visibility as the ingress uid (the launcher runs `python -I`, which ignores PYTHONPATH)
  run preflight-ingress-deps setpriv --reuid="$ING_UID" --regid="$ING_GID" --clear-groups --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs \
      env -i PATH=/usr/bin:/bin LANG=C.UTF-8 ${LD_LIBRARY_PATH:+LD_LIBRARY_PATH="$LD_LIBRARY_PATH"} "$PY" -I -B -c 'import sys,pydantic;print(sys.version_info[:3],pydantic.VERSION)'
  cd / || true
  env -i PATH=/usr/bin:/bin LANG=C.UTF-8 HOME=/nonexistent ${LD_LIBRARY_PATH:+LD_LIBRARY_PATH="$LD_LIBRARY_PATH"} \
    setpriv --reuid="$ING_UID" --regid="$ING_GID" --clear-groups --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs \
    "$PY" -I -B "$HUB/tools/mvp_ingress/launch.py" --state-dir "$STATE" --socket "$SOCK" --control-plane "$CP" --runtime "$RT" \
    --socket-mode 660 --allow-uid "$CLI_UID" --max-requests "$MAXREQ" >"$EV/ingress.out" 2>"$EV/ingress.err" &
  ING_PID=$!
  log "ingress pid $ING_PID"
  for _ in $(seq 1 90); do
    grep -q '^READY' "$EV/ingress.out" 2>/dev/null && { INGRESS_UP=1; break; }
    kill -0 "$ING_PID" 2>/dev/null || break
    sleep 1
  done
  echo "INGRESS_UP=$INGRESS_UP pid=$ING_PID alive=$(kill -0 "$ING_PID" 2>/dev/null && echo yes || echo no)" >"$EV/ingress-start.out"
  if [ "$INGRESS_UP" = 1 ]; then
    run ingress-proc-status cat "/proc/$ING_PID/status"
    run ingress-proc-cmdline bash -c "tr '\\0' ' ' < /proc/$ING_PID/cmdline; echo; readlink /proc/$ING_PID/exe"
    run ingress-state-listing bash -c "stat -c '%n %U:%G %a %F' '$IPC' '$SOCK'; find '$STATE' -printf '%p %U:%G %m %y\\n' | sort"
  fi
fi
phase ingress "INGRESS_UP=$INGRESS_UP"

# ---- (6) diagnostics, BEFORE the capture ------------------------------------------------------------------------------------
DIAG=$REPO_ROOT/.github/qgate-03/diagnostics.sh
if [ -f "$DIAG" ]; then
  mkdir -p "$EV/diagnostics"
  run diagnostics bash "$DIAG" "$EV/diagnostics"
else
  echo "diagnostics.sh not present at $DIAG" >"$EV/diagnostics.out"
fi

# ---- (4) the UNMODIFIED capture script, as root, with the interpreter that runs the ingress --------------------------------------
CAPTURE_DONE=0
if [ "$SETUP_OK" = 1 ] && [ "$INGRESS_UP" = 1 ]; then
  DB=$STATE/atomic/refunds.sqlite3
  PINS=(--pin "control_plane=$PIN_CP" --pin "runtime=$PIN_RT" --pin "manifest_sha256.synthetic-manifest.json=$MANIFEST_SHA")
  for f in __init__ client core launch proposal server synthetic_host; do
    PINS+=(--pin "source_sha256.tools/mvp_ingress/$f.py=$(sha256sum "$HUB/tools/mvp_ingress/$f.py" | cut -d' ' -f1)")
  done
  runin "$HUB" capture env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m tools.mvp_env_record.capture_env_record \
      --state-dir "$STATE" --socket "$SOCK" --ingress-pid "$ING_PID" --ingress-uid "$ING_UID" --ingress-gid "$ING_GID" \
      --client-uid "$CLI_UID" --client-gid "$CLI_GID" --allow-uid "$CLI_UID" --outsider-uid "$OUT_UID" \
      --db "$DB" --authority-store "$DB" --ledger "$STATE/ingress.db" --journal-mode wal \
      "${PINS[@]}" --manifest "$EV/synthetic-manifest.json" --accept-unverified-pins \
      --repo-root "$HUB" --label "$LABEL" --out "$EV/capture-record.json"
  CAPTURE_DONE=1
  { printf 'capture command (unmodified script, copy verified byte-identical in copy-verify-hub.out):\n  %s -B -m tools.mvp_env_record.capture_env_record --state-dir %s --socket %s --ingress-pid %s ...\n' "$PY" "$STATE" "$SOCK" "$ING_PID"; } >"$EV/capture-command.out"
  run capture-after-proc-status cat "/proc/$ING_PID/status"
  # SUPPLEMENTARY, NOT the verdict basis: the hub profile says IPC dir 2750, other documents say 2751. At 2750 the outsider cannot
  # traverse the IPC directory, so qualification.outsider_denied_socket can only be BLOCKED. Re-run the SAME unmodified capture once
  # with the IPC directory (our own synthetic dir, no system path) at 2751 and put it back. Separate record; the verdict uses the 2750 record.
  if [ "$IPC_MODE" = "2750" ]; then
    run supp-ipc-chmod-2751 chmod 2751 "$IPC"
    run supp-ipc-stat-2751 stat -c '%n %U:%G %a' "$IPC"
    runin "$HUB" capture-supp-ipc2751 env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m tools.mvp_env_record.capture_env_record \
        --state-dir "$STATE" --socket "$SOCK" --ingress-pid "$ING_PID" --ingress-uid "$ING_UID" --ingress-gid "$ING_GID" \
        --client-uid "$CLI_UID" --client-gid "$CLI_GID" --allow-uid "$CLI_UID" --outsider-uid "$OUT_UID" \
        --db "$DB" --authority-store "$DB" --ledger "$STATE/ingress.db" --journal-mode wal \
        "${PINS[@]}" --manifest "$EV/synthetic-manifest.json" --accept-unverified-pins \
        --repo-root "$HUB" --label "SUPPLEMENTARY ipc-dir 2751 variant; $LABEL" --out "$EV/capture-record-supp-ipc2751.json"
    run supp-ipc-chmod-restore chmod "$IPC_MODE" "$IPC"
    run supp-ipc-stat-restored stat -c '%n %U:%G %a' "$IPC"
  fi
fi
phase capture "CAPTURE_DONE=$CAPTURE_DONE"

# ---- (5) non-effecting peer-uid controls through tools.mvp_ingress.client:submit (separate test-only file) --------------------
CTL_CODE='
import sys, json, os, errno
hub, sock, kind = sys.argv[1:4]
out = {"kind": kind, "uid": os.getuid(), "gid": os.getgid(), "groups": sorted(os.getgroups())}
try:
    out["CapEff"] = [l.split()[1] for l in open("/proc/self/status") if l.startswith("CapEff")][0]
except Exception as e:
    out["CapEff"] = "unreadable:" + type(e).__name__
sys.path.append(hub)
try:
    from tools.mvp_ingress.client import submit
except Exception as e:
    out["stage"] = "import"; out["error"] = type(e).__name__
    print(json.dumps(out, sort_keys=True)); sys.exit(0)
prop = {"schema": "mvp-refund-proposal/1", "request_id": "qg3-ctl-" + kind, "customer_id": "customer-001", "amount": 10.01,
        "unit": "USD", "refund_reason": "duplicate"}
out["stage"] = "submit"
try:
    out["result"] = submit(sock, prop, timeout=10)
except OSError as e:
    out["error"] = type(e).__name__; out["errno"] = errno.errorcode.get(e.errno, str(e.errno))
except Exception as e:
    out["error"] = type(e).__name__
print(json.dumps(out, sort_keys=True))
'
ctl() {  # ctl NAME UID GID GROUPS
  local n=$1 u=$2 g=$3 grp=$4
  run "control-$n" setpriv --reuid="$u" --regid="$g" --groups="$grp" --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs \
      env -i PATH=/usr/bin:/bin LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 ${LD_LIBRARY_PATH:+LD_LIBRARY_PATH="$LD_LIBRARY_PATH"} "$PY" -I -B -c "$CTL_CODE" "$HUB" "$SOCK" "$n"
}
if [ "$SETUP_OK" = 1 ] && [ "$INGRESS_UP" = 1 ] && kill -0 "$ING_PID" 2>/dev/null; then
  ctl positive-client "$CLI_UID" "$CLI_GID" "$IPC_GID"
  # the wrong-member user joins the dedicated group only now (after the capture recorded exact membership)
  run control-gpasswd-wrong gpasswd -a "$N_WRG" "$N_IPC"
  ctl negative-group-member-not-allowlisted "$WRG_UID" "$WRG_GID" "$IPC_GID"
  ctl negative-outsider "$OUT_UID" "$OUT_GID" "$OUT_GID"
  run control-ingress-alive bash -c "kill -0 $ING_PID && echo alive"
fi
"$PY" -I -B - "$EV" >"$EV/peer-uid-controls-assemble.out" 2>"$EV/peer-uid-controls-assemble.err" <<'PYEOF'
import json, os, sys
ev = sys.argv[1]
def load(name):
    try:
        with open(os.path.join(ev, "control-%s.out" % name)) as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
        return json.loads(lines[-1]) if lines else None
    except Exception as e:
        return {"unreadable": type(e).__name__}
def rc(name):
    try:
        return int(open(os.path.join(ev, "control-%s.rc" % name)).read().strip())
    except Exception:
        return None
def verdict(name, expect):
    r = load(name)
    if r is None or "unreadable" in (r or {}) and not os.path.exists(os.path.join(ev, "control-%s.rc" % name)):
        return {"control": name, "expected": expect["text"], "status": "NOT-RUN", "reason": "control did not execute (setup or ingress not available)"}
    res = r.get("result")
    ok = expect["test"](r, res)
    return {"control": name, "expected": expect["text"], "status": "MET" if ok else "NOT-MET", "process_rc": rc(name), "observed": r}
controls = [
    ("positive-client", {"text": "designated client (allow-listed uid) is accepted: result is not PEER_NOT_ALLOWED (non-effecting proposal expected held/refused by policy, no execution)",
        "test": lambda r, res: bool(res) and res.get("code") != "PEER_NOT_ALLOWED" and res.get("outcome") in ("held", "refused")}),
    ("negative-group-member-not-allowlisted", {"text": "dedicated-group member that is not the allow-listed uid reaches the socket but is refused with PEER_NOT_ALLOWED",
        "test": lambda r, res: bool(res) and res.get("code") == "PEER_NOT_ALLOWED" and res.get("outcome") == "refused"}),
    ("negative-outsider", {"text": "unrelated uid outside the dedicated group is denied (connect EACCES/EPERM). With the profile IPC directory 2750 this denial is by the DIRECTORY, not proof of the socket mode",
        "test": lambda r, res: res is None and r.get("errno") in ("EACCES", "EPERM")}),
]
doc = {"schema": "qgate03-peer-uid-controls/1", "test_only": True, "non_authorizing": True, "synthetic": True,
       "note": "Separate from the capture record; exercised only through tools.mvp_ingress.client:submit; proposals are schema-valid but do not match the synthetic approval, so no effect is expected; NOT qualification evidence",
       "controls": [verdict(n, e) for n, e in controls]}
with open(os.path.join(ev, "peer-uid-controls.json"), "w") as f:
    json.dump(doc, f, indent=2, sort_keys=True)
    f.write("\n")
PYEOF
echo "$?" >"$EV/peer-uid-controls-assemble.rc"
phase controls done

# final state evidence while everything still exists
if [ "$SETUP_OK" = 1 ]; then
  run final-state-listing bash -c "stat -c '%n %U:%G %a %F' '$IPC' '$SOCK' 2>&1; find '$STATE' -printf '%p %U:%G %m %y\\n' | sort; echo; getent group $N_IPC"
  [ -n "$ING_PID" ] && { kill -0 "$ING_PID" 2>/dev/null && echo "ingress alive at end" || echo "ingress already exited (max-requests or error)"; } >"$EV/ingress-end.out"
  cp "$EV/ingress.err" "$EV/ingress.err.before-stop" 2>/dev/null
fi
exit 0
