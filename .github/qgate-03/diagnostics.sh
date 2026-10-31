#!/usr/bin/env bash
# OCS-MVP-QGATE-03 Worker C: READ-ONLY host diagnostics. Usage: diagnostics.sh EVDIR
# Optional env: QG03_STATE_DIR, QG03_SOCKET_DIR (extra candidate paths; their ancestors are examined, nonexistent paths are walked
# up to the existing ancestors and also recorded as missing). Writes only under EVDIR. No chmod/setfacl/mkdir elsewhere/sysctl writes.
# Not a qualification step; records observations only. No "set -e": every command's output and exit code is saved separately.
EVDIR="${1:-}"
if [ -z "$EVDIR" ]; then echo "usage: diagnostics.sh EVDIR" >&2; exit 64; fi
mkdir -p "$EVDIR" || exit 65
EVDIR=$(cd "$EVDIR" && pwd) || exit 65

# cmd NAME CMD... : run CMD, stdout+stderr into diag-NAME.txt, exit code into diag-NAME.rc
cmd() {
  local name="$1"; shift
  "$@" > "$EVDIR/diag-$name.txt" 2>&1
  echo "$?" > "$EVDIR/diag-$name.rc"
}
# note NAME TEXT : record that a tool is unavailable, rc 127
note() { printf '%s\n' "$2" > "$EVDIR/diag-$1.txt"; echo 127 > "$EVDIR/diag-$1.rc"; }

# ---- host-wide facts
cmd uname uname -a
cmd os-release cat /etc/os-release
cmd image-env bash -c 'echo "ImageOS=${ImageOS-<unset>}"; echo "ImageVersion=${ImageVersion-<unset>}"; echo "RUNNER_OS=${RUNNER_OS-<unset>}"; echo "RUNNER_ENVIRONMENT=${RUNNER_ENVIRONMENT-<unset>}"'
cmd id id
cmd proc-status-caps grep -E '^(Uid|Gid|Groups|NoNewPrivs|Seccomp|Cap(Inh|Prm|Eff|Bnd|Amb)):' /proc/self/status
cmd yama-ptrace-scope cat /proc/sys/kernel/yama/ptrace_scope
cmd yama-listing ls -la /proc/sys/kernel/yama
cmd python-version python3 --version
cmd tools-present bash -c 'for t in getfacl getfattr lsattr stat python3 findmnt; do printf "%s=%s\n" "$t" "$(command -v $t || echo MISSING)"; done'

# ---- candidate paths
CANDS=(/ /opt /var /var/lib /srv /tmp /home)
for v in "${QG03_STATE_DIR:-}" "${QG03_SOCKET_DIR:-}"; do [ -n "$v" ] && CANDS+=("$v"); done

# every ancestor (including the path itself) of each candidate, de-duplicated, nonexistent ones kept (recorded as missing)
declare -A SEEN
ALL=()
for c in "${CANDS[@]}"; do
  p="$c"
  case "$p" in /*) ;; *) p="$PWD/$p" ;; esac
  while :; do
    if [ -z "${SEEN[$p]+x}" ]; then SEEN[$p]=1; ALL+=("$p"); fi
    [ "$p" = "/" ] && break
    p=$(dirname "$p")
  done
done
printf '%s\n' "${ALL[@]}" > "$EVDIR/diag-path-list.txt"; echo 0 > "$EVDIR/diag-path-list.rc"

# raw xattr dump with python (stdlib, read-only, lstat semantics like the capture script)
PYDUMP='
import os, sys
p = sys.argv[1]
try:
    names = os.listxattr(p, follow_symlinks=False)
except OSError as e:
    print("listxattr_error", e.errno, os.strerror(e.errno)); sys.exit(3)
print("listxattr_all", sorted(names))
rc = 0
for n in ("system.posix_acl_access", "system.posix_acl_default"):
    try:
        v = os.getxattr(p, n, follow_symlinks=False)
        print(n, "PRESENT hex=" + v.hex())
    except OSError as e:
        print(n, "absent_or_error", e.errno, os.strerror(e.errno))
'

i=0
for p in "${ALL[@]}"; do
  i=$((i+1))
  tag=$(printf '%02d' "$i")
  # filename-safe slug of the path
  slug=$(printf '%s' "$p" | sed 's#^/$#root#; s#^/##; s#[^A-Za-z0-9._-]#_#g')
  base="p${tag}-${slug}"
  printf '%s\n' "$p" > "$EVDIR/diag-$base-path.txt"; echo 0 > "$EVDIR/diag-$base-path.rc"
  cmd "$base-stat" stat -c 'mode=%a (%A) uid=%u gid=%g type=%F dev=%D ino=%i name=%n' -- "$p"
  if command -v getfacl >/dev/null 2>&1; then cmd "$base-getfacl" getfacl -p -- "$p"; else note "$base-getfacl" "getfacl not installed"; fi
  if command -v getfattr >/dev/null 2>&1; then cmd "$base-getfattr" getfattr -h -d -m - -e hex -- "$p"; else note "$base-getfattr" "getfattr not installed (python dump below covers it)"; fi
  if command -v python3 >/dev/null 2>&1; then cmd "$base-pyxattr" python3 -I -c "$PYDUMP" "$p"; else note "$base-pyxattr" "python3 not installed"; fi
  if command -v lsattr >/dev/null 2>&1; then cmd "$base-lsattr" lsattr -d -- "$p"; else note "$base-lsattr" "lsattr not installed"; fi
  # mount: longest matching mount point from /proc/self/mountinfo of the real path (or nearest existing ancestor)
  cmd "$base-mount" python3 -I -c '
import os, sys
p = sys.argv[1]
real = os.path.realpath(p)
best = None
for line in open("/proc/self/mountinfo"):
    f = line.split()
    if " - " not in line or len(f) < 10: continue
    mp = f[4].replace("\\040", " ")
    if real == mp or real.startswith(mp.rstrip("/") + "/"):
        if best is None or len(mp) >= len(best[0]):
            i = f.index("-")
            best = (mp, f[5], f[i+1], f[i+2], f[i+3])
print("realpath", real)
print("mount_point,mount_options,fstype,source,super_options =", best)
' "$p"
done
cmd mountinfo-full cat /proc/self/mountinfo
echo "done" > "$EVDIR/diag-complete.txt"; echo 0 > "$EVDIR/diag-complete.rc"
exit 0
