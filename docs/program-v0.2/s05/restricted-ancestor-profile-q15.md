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

## 2. Negative-control tests (proposed list)

Each must be refused with the profile's fail-closed outcome; a paired positive control shows the plain real-directory layout is accepted.

| # | Control | Expected |
|---|---|---|
| N1 | Symlink component between custody root and handoff root | Refuse |
| N2 | Symlink as the handoff root itself | Refuse |
| N3 | Symlink at the custody root itself (declared root not normalized or is a link) | Refuse |
| N4 | Relative `..` traversal in a component | Refuse |
| N5 | Absolute or rooted component replacing the relative remainder | Refuse |
| N6 | Handoff root resolving outside the custody root (root escape) | Refuse |
| N7 | Component swapped for a symlink after check, before use (swap race, injected) | Refuse |
| N8 | Directory replaced by a different directory after handle opened (identity change detected by handle metadata) | Refuse |
| N9 | Platform or runtime without no-follow open or directory-descriptor primitives (simulated absence) | Refuse; not a silent fallback to path resolution |
| N10 | Declared root not normalized (trailing separators, `.` or `..`, duplicate separators, non-canonical case where relevant) | Refuse |
| N11 | Symlink exception requested while the exception set is empty | Refuse |
| N12 | Dangling symlink or symlink loop in an ancestor | Refuse |
| N13 | Mount or bind point crossing the boundary where the platform exposes it | Refuse or record per profile; not silently accepted |
| N14 | General handoff profile run on a symlinked ancestor | Disclosure text unchanged (regression control) |
| N15 | Expansion to a new custody environment without recorded operator approval | Refuse |
