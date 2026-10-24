"""Trusted-host builder for the matched $10 synthetic refund: fixed synthetic authority, route B, operation identity.

SPDX-License-Identifier: Apache-2.0

Runs only inside the ingress process, as the ingress uid. Authority is the Control Plane's own deterministic synthetic
resolver fixture (``tests.test_runtime_authority.setup_flow``), as used by the Qualification suites: a fixed, synthetic,
trusted authority source, not production IAM. The destination is the Runtime's synthetic SQLite route B destination with
operation identity. ``simulate`` is never passed. Component checkouts are given explicitly (no discovery).
"""
from __future__ import annotations

import os
import pathlib
import sys

OPERATION = "op-order-100/refund-1"
RESOLVER_ID, RESOLVER_VERSION = "synthetic-resolver", "1"
APPROVED_REQUEST_ID = "case-1"  # the synthetic approval binds exactly this proposal (request id, customer, $10, reason)
APPROVED_AMOUNT = 10.0


def _refuse(why):
    sys.stderr.write("ingress refused: %s\n" % why)
    raise SystemExit(2)


def _under(path, roots):
    real = os.path.realpath(path)
    return any(real == r or real.startswith(r + os.sep) for r in roots)


def _toplevel_names(roots):
    names = set()
    for r in roots:
        try:
            for e in os.scandir(r):
                if e.is_dir() and os.path.isfile(os.path.join(e.path, "__init__.py")):
                    names.add(e.name)
                elif e.is_file() and e.name.endswith(".py") and e.name != "__init__.py":
                    names.add(e.name[:-3])
        except OSError:
            pass
    return names


def _candidate(directory, name):
    """First thing the path finder would load for `name` in `directory` (extension module, package, then module), or None."""
    try:
        if any(e.startswith(name + ".") and e.endswith((".so", ".pyd")) for e in os.listdir(directory)):
            return os.path.join(directory, name + ".<extension>")
    except OSError:
        return None
    pkg = os.path.join(directory, name, "__init__.py")
    if os.path.isfile(pkg):
        return pkg
    mod = os.path.join(directory, name + ".py")
    return mod if os.path.isfile(mod) else None


def _check_component_resolution(cp_root, runtime_root, roots, *, before_import):
    """Installed packages are trusted EXCEPT these checked modules: the Control Plane / Runtime top-level modules must resolve
    under the operator-supplied roots (component roots are appended after the standard library and site-packages, so a stray
    installed agent_control_plane / engine / tests would otherwise win silently)."""
    reals = [os.path.realpath(r) for r in roots]
    if before_import:
        for name, where in (("agent_control_plane", [os.path.join(cp_root, "src"), cp_root]), ("engine", [runtime_root]),
                            ("tests", [cp_root])):
            expected = None
            for w in where:
                expected = _candidate(w, name)
                if expected:
                    break
            first = None
            for entry in sys.path:  # emulate the path finder's order without calling the import machinery
                first = _candidate(entry, name) if entry and os.path.isdir(entry) else None
                if first:
                    break
            loaded = sys.modules.get(name)
            if loaded is not None and not _under(getattr(loaded, "__file__", None) or "", reals):
                _refuse("top-level module %s is already loaded from outside the operator-supplied component roots" % name)
            if not expected or not first or os.path.realpath(first) != os.path.realpath(expected):
                _refuse("top-level module %s does not resolve to the operator-supplied component roots" % name)
        return
    names = _toplevel_names(reals)
    for modname, mod in list(sys.modules.items()):
        if modname.split(".")[0] in names:
            f = getattr(mod, "__file__", None)
            if f is None or not _under(f, reals):
                _refuse("module %s resolved to %s, outside the operator-supplied component roots" % (modname, f))


class SyntheticHost:
    def __init__(self, *, control_plane_root, runtime_root, state_dir):
        # Operator-supplied component roots are APPENDED (after the standard library and site-packages, so a file such as
        # json.py in a component root cannot shadow them). Order matches the former prepend order: CP root, CP src, Runtime.
        roots = [str(control_plane_root), str(pathlib.Path(control_plane_root) / "src"), str(runtime_root)]
        for extra in roots:
            if extra not in sys.path:
                sys.path.append(extra)
        _check_component_resolution(str(control_plane_root), str(runtime_root), roots, before_import=True)
        import agent_control_plane.bounded as cp
        import tests.test_bounded_authorization as tba
        import tests.test_runtime_authority as tra
        from agent_control_plane.operation_identity import OperationIdentityProfile
        from engine.atomic_local_control_plane_executor import AtomicLocalControlPlaneExecutor
        from engine.operation_identity_atomic_destination import OperationIdentityAtomicAuthorityEffectDestination
        from engine.safe_executor import LocalExecutionPolicy

        _check_component_resolution(str(control_plane_root), str(runtime_root), roots, before_import=False)
        self._cp, self._tba = cp, tba
        self.now = tba.NOW
        cp._now = lambda: tba.NOW  # fixed synthetic clock: the fixture authority is dated; this is not a production clock
        state = pathlib.Path(state_dir)
        original = tra.proposal
        tra.proposal = lambda *a, **k: original(*a, **k).model_copy(update={"amount": APPROVED_AMOUNT})
        try:
            self.p0, self.resolver, self.workflow, cfg = tra.setup_flow(state / "cp")
        finally:
            tra.proposal = original
        cfg = cfg.model_copy(update={"operation_identity": OperationIdentityProfile(
            resolver_id=RESOLVER_ID, resolver_version=RESOLVER_VERSION)})
        self.resolver.contexts[tba.PROFILE]["runtime_authority"]["operation_id"] = OPERATION
        tra.bind_approval(self.resolver, cfg)
        self.workflow.runtime_authority_profile = cfg.snapshot()
        self.destination = OperationIdentityAtomicAuthorityEffectDestination(state / "atomic", clock=lambda: tba.NOW)
        policy = LocalExecutionPolicy(
            allowed_institutions=frozenset({tba.INSTITUTION}), allowed_authority_domains=frozenset({"customer-refunds"}),
            allowed_adapters=frozenset({self.p0.adapter_id}), allowed_actions=frozenset({self.p0.action_id}),
            allowed_target_prefixes=("urn:cognous:synthetic-account:",), allowed_units=frozenset({"USD"}),
            max_amount=1000, max_effects=1)
        self.executor = AtomicLocalControlPlaneExecutor(workflow=self.workflow, destination=self.destination,
                                                        policy=policy, operation_identity=True)

    def build_proposal(self, fields):
        """Fixed identity/authority members from the template; only the business members come from the client."""
        cp = self._cp
        payload = {"customer_id": fields["customer_id"], "refund_reason": fields["refund_reason"]}
        return self.p0.model_copy(update={
            "target": "urn:cognous:synthetic-account:" + fields["customer_id"],
            "payload": payload, "payload_commitment": cp.commitment(payload),
            "amount": float(fields["amount"]), "unit": fields["unit"], "correlation_id": fields["request_id"]})

    def envelope(self, d, p):
        from engine.safe_executor import EXECUTION_ENVELOPE_VERSION, ExecutionEnvelope, ExecutionOperation
        cp, tba = self._cp, self._tba
        names = ["actor", "principal", "manifest_id", "manifest_version", "manifest_digest", "action_id", "adapter_id", "target",
                 "payload", "payload_commitment", "amount", "unit", "effects", "requirement_id"]
        op = ExecutionOperation(
            **{k: getattr(p, k) for k in names}, institution_id=tba.INSTITUTION, authority_domain="customer-refunds",
            proposal_commitment=cp.commitment(p.model_dump(mode="json")), requested_permissions=tuple(p.requested_permissions),
            authority_context_id=p.authority_context_ref, grant_id=d.binding.grant_id, grant_revision=d.binding.grant_revision,
            effective_max_effects=d.binding.effective_max_effects)
        return ExecutionEnvelope(EXECUTION_ENVELOPE_VERSION, d.decision_id, d.effect_id, op)
