"""MVP trusted-host ingress (single designated process, governed proposals only).

SPDX-License-Identifier: Apache-2.0

Hub-owned, non-locked module. It composes pinned Control Plane and Runtime components; it modifies neither.
The only supported client interface is ``client.submit`` (a JSON proposal over a Unix socket). See BOUNDARY.md
(delivered with the worker report) for what the boundary does and does not guarantee. Synthetic effects only.
"""
