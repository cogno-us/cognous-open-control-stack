"""Trusted-host builder for the matched $10 synthetic refund: fixed synthetic authority, route B, operation identity.

SPDX-License-Identifier: Apache-2.0

Runs only inside the ingress process, as the ingress uid. Authority is the Control Plane's own deterministic synthetic
resolver fixture (``tests.test_runtime_authority.setup_flow``), as used by the Qualification suites: a fixed, synthetic,
trusted authority source, not production IAM. The destination is the Runtime's synthetic SQLite route B destination with
operation identity. ``simulate`` is never passed. Component checkouts are given explicitly (no discovery).
"""
from __future__ import annotations

import pathlib
import sys

OPERATION = "op-order-100/refund-1"
RESOLVER_ID, RESOLVER_VERSION = "synthetic-resolver", "1"
APPROVED_REQUEST_ID = "case-1"  # the synthetic approval binds exactly this proposal (request id, customer, $10, reason)
APPROVED_AMOUNT = 10.0


class SyntheticHost:
    def __init__(self, *, control_plane_root, runtime_root, state_dir):
        # Operator-supplied component roots are APPENDED (after the standard library and site-packages, so a file such as
        # json.py in a component root cannot shadow them). Order matches the former prepend order: CP root, CP src, Runtime.
        for extra in (str(control_plane_root), str(pathlib.Path(control_plane_root) / "src"), str(runtime_root)):
            if extra not in sys.path:
                sys.path.append(extra)
        import agent_control_plane.bounded as cp
        import tests.test_bounded_authorization as tba
        import tests.test_runtime_authority as tra
        from agent_control_plane.operation_identity import OperationIdentityProfile
        from engine.atomic_local_control_plane_executor import AtomicLocalControlPlaneExecutor
        from engine.operation_identity_atomic_destination import OperationIdentityAtomicAuthorityEffectDestination
        from engine.safe_executor import LocalExecutionPolicy

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
