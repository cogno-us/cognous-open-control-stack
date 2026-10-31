# QGATE-04 Workstream A: bounded security review of IPC directory mode 2751 (Architect decision D3)

Status: non-authorizing. Same-lineage worker analysis, NOT independent certification (D1). Not qualification, not a security clearance, not production. This document does not change the original profile (`ingress-qualification-environment-profile.md`, which states 2750), production, or the historical 2750 evidence. Standing holds unchanged (F3 CLOSED, Q2/Q3 UNRESOLVED, Q7 NOT ESTABLISHED, candidate PROVISIONAL/UNFROZEN/UNQUALIFIED, Tier 1 DEFERRED not waived, publication/release/production HOLD).

Tags: SOURCE (read in the hub checkout at base c40bfcd8), DERIVED (reasoned from SOURCE/kernel semantics), DRY-RUN-OBSERVED (throwaway sandbox experiment, not evidence), ARCHITECT-STATED (QGATE-03 numbers, second-hand), UNVERIFIED.

## 0. What 2751 changes

Only one bit: other-execute (search) on the IPC directory. 2750 = setgid + rwx(owner) + r-x(group) + ---(other). 2751 = same + --x(other). [DERIVED]
`x` on a directory permits resolving a name inside it when the name is known. It does not permit listing (needs r), creating/removing/renaming entries (needs w), or any access to the socket's data/connect path (governed by the socket inode's own mode). [DERIVED; DRY-RUN-OBSERVED below]

## 1. Dry-run (sandbox; root, no Yama, ext4; DRY RUN, not evidence)

Setup: `/var/lib/qg4a-dry` (0755 root) with `state/` (0700, owner X, containing a 0600 file) and `ipc/` (owner X, group G, mode 2750 then 2751). A stand-in listener (uid X, no capabilities, umask 077, bind then chmod 0660) in a setgid dir; numeric uids only, no accounts created, no `/etc/passwd` or `/etc/group` change. Three probe identities with empty capabilities (CapEff 0): outsider O (no group, no ownership), non-allowlisted member of G, member of G acting as the client. Directory removed afterwards (verified absent). Script: `/tmp/claude-0/qg4a/exp.py` (scratch, not committed). The stand-in is not the real ingress; it tests DIRECTORY-LEVEL consequences only. Peer-uid allowlisting was not exercised here.

| Probe (as outsider O) | 2750 | 2751 |
|---|---|---|
| socket inherited group G, mode 0660, owner X (setgid) | yes | yes |
| stat known name `ingress.sock` | EACCES | ALLOWED (mode 660, uid, gid, size 0, mtime, ino) |
| stat nonexistent name | EACCES | ENOENT (existence is distinguishable) |
| list IPC dir | EACCES | EACCES |
| connect to socket | EACCES | EACCES |
| create / symlink / unlink / rename in IPC dir | EACCES | EACCES |
| list/open/stat state dir contents; `../state` via IPC | EACCES | EACCES |
| open `/proc/<pid>/mem`, `environ`; list `/proc/<pid>/fd`; readlink `exe` | EACCES | EACCES |
| kill -0 ingress | EPERM | EPERM |
| read `/proc/<pid>/status` | allowed | allowed (not mode dependent; normal Linux default) |
| stat of state dir itself (inode of a 0700 dir) | allowed | allowed (not mode dependent: base is 0755) |

Non-allowlisted G member: identical to the outsider at 2751 except list IPC dir allowed (r-x via group) and connect ALLOWED at the kernel level (group write on 0660 socket); identical at 2750 for these two. That is the intended design: the kernel lets any G member connect, the ingress refuses non-allowlisted peers at the application layer. Group-member state/proc/create/rename/unlink probes all denied. Client identity: same results as the G member. [DRY-RUN-OBSERVED]
The 2750 vs 2751 difference for group members is nil; for the outsider the only differences are the metadata rows above. [DRY-RUN-OBSERVED]

## 2. D3 conditions

**(1) Does other-x expose socket access? No.** Connect to a Unix stream socket needs write permission on the socket inode; mode 0660 gives other nothing; outsider is neither owner nor in G, so EACCES. [DERIVED; SOURCE: server.py `make_listener` chmods the socket to the requested mode, launch/run_integration passes `--socket-mode 660`; DRY-RUN-OBSERVED EACCES at 2751] Caveat: this holds for filesystem sockets with the exact mode 0660 and group G containing no one else; the capture check `ipc.socket_mode_owner_group` verifies exactly that (mode == 0660, owner == ingress uid, gid not 0/ingress/client primary, group membership exactly {ingress, client}). [SOURCE capture_env_record.py ~L509-526]. If the group ever had extra members, 2751 vs 2750 would not change their access (they have group r-x already).

**(2) State contents: not exposed by the extra bit.** The state dir is not under the IPC dir. In `run_integration.sh` it is `BASE/state`, mode 0700, owned by the ingress uid, sibling of `BASE/ipc`; BASE is `mkdir -m 0755` root-owned. [SOURCE run_integration.sh] The capture checks `filesystem.state_tree_owner_only` (dirs exactly 0700, files exactly 0600, one owner, no group/other bits, no symlinks), `filesystem.no_extra_group_access`, `ipc.directory_separate_and_protected` (IPC dir not equal to or inside state dir), and, via the client probe, listdir/unlink/open/stat denial. [SOURCE capture_env_record.py L460-475, 531-542, 545-558, client_probe L205-260] Dry-run: outsider and G members denied listdir/open/stat of state contents and `../state` via the IPC dir at both modes. [DRY-RUN-OBSERVED] Residual: the inode metadata of the state dir itself is stat-able by anyone through base 0755 at either mode, so not a 2751 effect. [DRY-RUN-OBSERVED]

**(3) Unauthorized metadata, exact enumeration (outsider at 2751).** Learnable: whether an entry with a guessed name exists in the IPC dir; for `ingress.sock` (name is fixed and public in the config/docs, so effectively known): type socket, mode 0660, owner uid, group gid, size, atime/mtime/ctime, inode; also that the IPC dir is mode 2751 / owner / group. [DRY-RUN-OBSERVED] Not learnable: directory listing (no r), any other file names unless guessed, state tree names/contents/sizes, process memory/environ/fds/exe, ability to connect. `/proc/<pid>/status` readability is independent of the mode. [DRY-RUN-OBSERVED] The same stat is already available to a G member at 2750, and to anyone able to read this repo's configuration (uids are synthetic test accounts). Assessment: low-sensitivity metadata for a synthetic test configuration; no secret, key, or authority material is in it. [DERIVED] Not tested: ctime/atime change observability as a liveness side channel (it is liveness metadata only, DERIVED).

**(4) The profile's own text.** SOURCE (profile, IPC row): "Outsider denial counts for the socket only if the outsider can traverse every ancestor including the IPC directory; otherwise `qualification.outsider_denied_socket` is BLOCKED ('not conclusive for the socket') and `qualification.outsider_denied_by_ipc_directory` records that directory-level denial is what was proven so the socket cannot be replaced." SOURCE capture L645-659: `untraversable_for` uses the other-x bit (0o001) for the outsider; at 2750 the outsider is blocked at the IPC dir, so the check is BLOCKED plus `outsider_denied_by_ipc_directory` PASS; at 2751 the outsider traverses, and the connect result (EACCES) is attributed to the socket's own mode/group, so `outsider_denied_socket` can PASS. DERIVED: 2751 is precisely what makes the socket-level negative test conclusive; at 2750 it cannot be (the profile's own check design guarantees a BLOCKED, as `h-matrix-reconciliation.md` already derived). SOURCE: no capture check tests the exact directory mode 2750, the setgid bit, or the group of the IPC dir: `ipc.directory_separate_and_protected` tests only separation, owner in {root, ingress uid}, and `mode & 0o022 == 0` (2751 passes: 0o022 bits clear). `filesystem.ancestors_not_writable_by_others` likewise tests `& 0o022`. `server.check_parents` tests ownership and group/other-write only. So no check depends on exact 2750. [SOURCE, plus h-matrix-reconciliation L165]. The profile text states 2750 in the socket-profile paragraph and the IPC row ("a separate IPC directory the client can traverse"), so 2751 is a deviation from the stated mode, which D3 permits only as a narrowly scoped test configuration; it is not an amendment. [SOURCE; ARCHITECT-STATED authorization]

**Note, symmetrical risk of the other-x bit:** the same bit also makes the socket-replacement protection depend only on `w` absence, which 2751 does not alter (other has no w; verified: create/unlink/rename/symlink all EACCES). [DRY-RUN-OBSERVED]

**(5) Coverage of the other isolation items**

| Item | Existing evidence | Read by this session? |
|---|---|---|
| UID/group separation (ingress, client, outsider, dedicated group exactly {ingress, client}; gid=uid accounts; group not primary of anyone) | `run_integration.sh` creates accounts and group; capture checks `identity.*`, `ipc.socket_mode_owner_group`. ARCHITECT-STATED: 2751 supplementary capture 31 PASS / 0 BLOCKED / 0 FAIL, profile_supported=true; 2750: 31 PASS / 1 BLOCKED / 0 FAIL | Script and design SOURCE: yes. Artifact results: NO |
| Allowlisted client accepted | `peer-uid-controls.json` positive-client (design: expects non-`PEER_NOT_ALLOWED`, outcome held/refused); `server.py` allowlist SOURCE L149-176; sandbox dry-run in synthetic-ingress-configuration.md (held, DECISION_HELD; second-hand doc text) | Design: yes. Result: NO |
| Non-allowlisted group member refused | control "negative-group-member-not-allowlisted": member `qg3-wrong` joins G after the capture, expects `PEER_NOT_ALLOWED` (SOURCE run_integration.sh). Note: the group-exact-membership capture check runs BEFORE this join, so the extra-member state is not in the capture record. Kernel-level connect is allowed for such a member (DRY-RUN-OBSERVED), so refusal is application-layer only. Control is mode-independent (member has r-x on the dir at both modes) | Design: yes. Result: NO |
| Outsider refusal | Capture outsider probe + control "negative-outsider" (expects EACCES/EPERM). At 2751 conclusive for socket; at 2750 directory-level only | Design: yes. Result: NO |
| Yama | `isolation.ptrace_scope` / `profile_supported`; sandbox has none; not influenced by 2751. ARCHITECT-STATED: profile_supported=true on both captures; QGATE-02 facts say 1 (second-hand) | NO (not observed; not testable here) |
| Capabilities | Ingress started with `setpriv --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs`; capture checks ingress and client CapEff empty. Dry-run probes had CapEff 0 | Design: yes. Result: NO |
| State-tree confinement | Section (2) above; client probe denied checks | Design: yes. Result: NO |
| Mode-independence of all of the above | Controls and checks other than the outsider/traversal ones do not read the IPC dir's other bit [DERIVED from SOURCE] | n/a |

## 3. Other observations and residual risks

- Hosted-runner context: the `runner` user normally has passwordless root. Root, the ingress uid, and same-privilege code are explicitly out of scope of the profile's claims (profile "What is not claimed"). 2751 neither helps nor harms against root. [SOURCE; UNVERIFIED for runner specifics]
- Other local accounts on the hosted image (daemon, www-data, runner, etc.) are "outsiders" under 2751; they could stat `ingress.sock` if they know the path, which is a synthetic base `/var/lib/qgate03-ocs`. No effect on connect/state. [DERIVED]
- Exposure window: the supplementary 2751 variant in `run_integration.sh` toggles the directory to 2751 for the second capture and restores 2750 (script L: `supp-ipc-chmod-2751`). A permanent 2751 test configuration would mean setting `QG3_IPC_MODE=2751` (variable exists, SOURCE). Whether the Architect-stated 2751 capture used the toggle or a direct setting is UNVERIFIED by me; the toggle meant the ingress ran continuously across the chmod, which is fine for the directory-level analysis.
- The dry run used a stand-in listener and an arbitrary kernel (6.18, ext4). Kernel semantics of directory x/w/r and socket write-for-connect are long-standing POSIX/Linux behavior [DERIVED]; GitHub runner kernel and filesystem differences are UNVERIFIED. Fine-grained LSM (AppArmor/SELinux) could only further restrict, but the runner's AppArmor state is UNVERIFIED.
- ACLs/namespace/overlay tricks: no ACLs expected (capture checks `filesystem.no_acl_entries` on the IPC dir and ancestors); a default ACL on `/var/lib` would be caught there. Not tested here.

## 4. SCOPED HOST ACCEPTANCE RECOMMENDATION

**ACCEPT 2751 for the bounded synthetic test configuration, conditional on the Reviewer confirming the items in section 5 against artifact 13023553992.**

Exact conditions:
1. Scope: only the QGATE synthetic test ingress on a GitHub-hosted ubuntu-24.04 run, IPC dir owner = ingress uid, group = dedicated group G, setgid, mode exactly 2751 (and only that one extra bit versus 2750); never production; the profile text is unchanged and the 2750 evidence stays as the historical baseline.
2. Socket stays exactly 0660, owner ingress uid, group G; G contains exactly {ingress, designated client} at capture time (capture check `ipc.socket_mode_owner_group` PASS); `--allow-uid` allowlist unchanged.
3. State dir remains a sibling (not inside IPC dir) at 0700 owned by the ingress uid, tree 0700/0600 (capture checks `filesystem.state_tree_owner_only`, `ipc.directory_separate_and_protected`, `filesystem.no_extra_group_access` PASS); base dir root-owned 0755 with no ACL.
4. IPC dir other-write bit clear and no ACL (`filesystem.ancestors_not_writable_by_others`, `filesystem.no_acl_entries` PASS).
5. The 2751 capture must be reported as a distinct record labeled as the D3 test configuration; `qualification.outsider_denied_socket` PASS is valid only because of this exception and must not be cited as satisfying the original 2750 profile. The metadata exposure in section 2(3) is accepted and disclosed.
6. Yama (`isolation.ptrace_scope` PASS), empty capabilities, and the three peer-uid controls (positive, non-allowlisted member, outsider) must be as Architect-stated; any FAIL or contradiction means fall back to the alternative below.

Alternative if the Reviewer cannot establish items in section 5: RETAIN 2750 and report `qualification.outsider_denied_socket` BLOCKED with `qualification.outsider_denied_by_ipc_directory` PASS (the originally profile-conformant outcome).

This recommendation does not change the original profile, production, or the historical 2750 evidence; it is a same-lineage review, not independent certification.

## 5. What the recommendation rests on that this session did NOT read (Reviewer must verify against artifact 13023553992)

1. The per-check results in `capture-record.json` (2750) and `capture-record-supp-ipc2751.json`: the Architect-stated 31/1/0 and 31/0/0 counts; that the single 2750 BLOCKED is `qualification.outsider_denied_socket`; that the 2751 record lists `outsider_denied_socket` PASS with `traversal_blocked_above_socket` empty and `connect: denied`.
2. `filesystem.*`, `ipc.*`, `identity.*` check detail strings in both records (recorded modes/owners of IPC dir, socket, state tree; group membership exactly the two users; no ACL).
3. `peer-uid-controls.json`: statuses of positive-client, negative-group-member-not-allowlisted (PEER_NOT_ALLOWED), negative-outsider (EACCES/EPERM), and that the ingress was alive (`control-ingress-alive`).
4. `isolation.ptrace_scope` value (>=1), `profile_supported=true`, ingress/client CapEff, and `qualification.client_denied_ingress_process` / `client_denied_state_access` details.
5. `diagnostics/` (ancestor ACL state), `final-state-listing.out`, `ingress-state-listing.out` and `supp-ipc-stat-2751.out` (actual mode 2751 and setgid/group at the time of the supplementary capture) and `cleanup-*`.
6. That the 2751 record was captured against the same pins, copied sources, and running ingress (SHA256SUMS 366/366 is Architect-stated only).
7. Nothing from GitHub was read by this session; no workflow action was taken or repeated.

## Lead addendum after adversarial review (supersedes the headline above where they differ)

The adversarial review (`adversarial-review.md`) reproduced that an outsider uid **can stat the socket** by its known name at 2751 (mode, owner, group, size, times). Directory listing, create/unlink/rename, connect, state access and `/proc/<pid>/{mem,environ}` stay denied. Whether that stat exposure is "unauthorized metadata" under D3 is an interpretation the Architect must ratify; the lead therefore records the determination as **ACCEPT FOR THE SYNTHETIC TEST CONFIGURATION ONLY, WITH A DISCLOSED RESIDUAL (stat of a known socket name), PENDING (a) Architect ratification of that residual and (b) the Reviewer's check against artifact 13023553992**. Fallback if either fails: retain 2750 and report `qualification.outsider_denied_socket` BLOCKED. This review also did not address the QGATE-02 ACL FAIL on the hosted runner (an ACL on `/opt` or `/`, path unknown); the QGATE-03 chain used `/var/lib` and the Architect-stated 2751 capture reports 0 FAIL, which this session did not read. The committed Qualification suite hard-codes 2751 without labelling it as the D3 test configuration; the original profile and the historical 2750 evidence are unchanged.
