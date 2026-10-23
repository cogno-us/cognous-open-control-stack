# Restricted ancestor-symlink qualification profile (Q15): strict first profile, proposal

**Non-authorizing record. Release, publication and production remain on HOLD.** Nothing here claims clearance, certification, qualification or readiness for any use. Source of the rulings: the architect disposition Q1-Q17 (binding for this programme). The Hub coordinates; component owners own components; independent Qualification owns oracles and verdicts; the operator owns authority decisions.

This is a specification proposal for the first restricted qualification profile, per architect ruling Q15. It authorizes no code and changes no locked component. Related: [disposition record](architect-disposition-q1-q17.md).

## 1. Requirements (proposed)

1. Declared custody root: the profile takes a declared, normalized custody root. The qualification environment owner declares it; Qualification independently evaluates it.
2. No unapproved symlink components between the custody boundary and the handoff root. In the first profile the exception set is empty.
3. Validation is bound to the actual opened directory handles (descend component by component from the root handle with no-follow semantics), not to a path string resolved separately and used later.
4. Refusal (fail closed, with a recorded reason) for: path traversal, root escape, swap races (a component replaced between check and use), and platforms lacking the necessary no-follow primitives.
5. Enumerated exception mechanism: a narrowly enumerated symlink exception may be introduced later, only if a supported platform requires it, as a separate versioned change.
6. The general handoff profile keeps its truthful ancestor-resolution disclosure unchanged. This profile is additional and opt-in; it must not alter or soften that disclosure.
7. Operator approval is required to expand the restricted profile to new custody environments or trust boundaries.
8. A pass under this profile is a statement about handle-bound path structure only. It is not a claim of security clearance, certification or production readiness.

## 2. Scope note

Ancestors above the custody boundary are out of scope: the profile makes no statement about them (the general profile's truthful disclosure covers them). Only components from the declared custody root down to the handoff root are validated.

## 3. Negative-control tests (proposed list)

Each N control is refused with the profile's fail-closed outcome and a recorded reason, except N14, which is a regression control. A paired positive control shows that a plain real-directory layout is accepted.

| # | Control | Expected |
|---|---|---|
| N1 | Symlink component between custody root and handoff root | Refuse |
| N2 | Symlink as the handoff root itself | Refuse |
| N3 | Declared custody root is itself a symlink | Refuse |
| N4 | Relative `..` traversal in a component | Refuse |
| N5 | Absolute or rooted component replacing the relative remainder | Refuse |
| N6 | Handoff root resolving outside the custody root (root escape) | Refuse |
| N7 | Swap race: a component is replaced by a symlink after its handle was opened and before the next descent (injected between steps) | Refuse |
| N8 | Identity change: the directory behind a held handle no longer matches, detected by comparing fstat device and inode of the held handle with a re-stat of the same component at use | Refuse. N7 injects a symlink swap during descent; N8 injects a same-type directory replacement and is detected only by the identity comparison |
| N9 | Platform or runtime without no-follow open or directory-descriptor primitives (simulated absence) | Refuse; no silent fallback to path resolution |
| N10 | Declared custody root not normalized (trailing separators, `.` or `..` components, duplicate separators) | Refuse |
| N11 | Symlink exception requested while the exception set is empty | Refuse |
| N12 | Dangling symlink or symlink loop in an ancestor | Refuse |
| N13 | Mount or bind point crossing the boundary | Refuse. Where the platform cannot expose the crossing, the profile treats the platform as lacking the required primitive (N9) |
| N14 | Regression control: general handoff profile run on a symlinked ancestor | Not refused by this profile; the general profile's ancestor-resolution disclosure text is unchanged |
| N15 | Expansion to a new custody environment without recorded operator approval | Refuse |
| N16 | Custody root is not a directory (regular file, device, FIFO) | Refuse |
| N17 | Handoff root is not a directory | Refuse |
| N18 | Windows reparse point or junction in a component (the first profile supports none) | Refuse; Windows is unsupported unless a later reviewed profile says otherwise |
| N19 | Embedded NUL byte in a component or path | Refuse |
| N20 | Empty component or empty path | Refuse |
| N21 | Case-insensitive aliasing: a component whose case differs from the on-disk name, or two names that alias on a case-insensitive filesystem | Refuse |
