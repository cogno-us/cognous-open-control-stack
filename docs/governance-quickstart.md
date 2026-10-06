# Governance quickstart

The reference stack separates institutional authority from technical capability.

1. Adopt or select the applicable institutional policy outside the incoming agent request.
2. Represent the bounded authority in the Alvorada Authority Context profile.
3. Configure the trusted resolver used by the Control Plane. Incoming GAX messages may reference authority, but cannot create grants.
4. Declare the proposed operation through Manifest 1.1.
5. Allow the Control Plane to evaluate the proposal and revalidate decision-critical authority/evidence at effect time.
6. Execute only through the constrained Moltbot boundary.
7. Inspect Replay, Governance Evidence Pack and optional ODES artifacts after the attempt.
8. Treat outcome evidence as input to human governance review, not as an automatic constitutional or policy amendment.

For the synthetic reference workflow, run:

```bash
python tools/reference_release.py run --results-dir results/reference
```

The synthetic resolver is explicitly not an authenticated production institutional resolver.
