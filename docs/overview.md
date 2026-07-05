# Stack Overview

Cognous Open Control Stack exists because agent governance needs an artifact chain, not just prompts, tool listings, logs, or dashboards. Teams need durable records that connect what an agent may propose, what it did propose, how those proposals were handled, how a run can be reconstructed, and what business-facing evidence can be reviewed.

The stack has four layers:
- Declare with Agent Action Manifest;
- Control with Agent Control Plane;
- Replay with Agent Replay Bundle;
- Evidence with Agent Governance Evidence Pack.

Each layer feeds the next:
- declaration defines the expected action surface;
- runtime control records proposals and policy decisions against that declared surface;
- replay packaging preserves the run for reconstruction and validation;
- evidence packaging turns the runtime record into business-facing governance evidence.

The stack is open-source so teams can inspect the formats, schemas, validators, reference behavior, examples, and tests that shape the artifact chain. That openness makes the records easier to review, compare, and extend across different governed deployments.

This repository is only the public hub. It links the four component repositories, explains how they relate, and provides public-safe examples and collateral. The implementation detail for each layer lives in the corresponding component repository.
