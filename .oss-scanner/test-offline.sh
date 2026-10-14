#!/bin/sh
set -eu
cd /src
python -m pytest -q \
  tests/test_protected_destination.py \
  tests/test_protocol_evaluation.py \
  tests/test_operational_state.py \
  tests/test_federated_governance.py \
  tests/test_integrated_assurance.py
python tools/destination_admission_mutations.py
