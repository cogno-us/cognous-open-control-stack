from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "collateral_evidence_snapshot", ROOT / "tools" / "collateral_evidence_snapshot.py"
)
assert SPEC and SPEC.loader
snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(snapshot)


class CollateralEvidenceSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest_path = ROOT / "collateral" / "evidence-snapshot.json"
        self.data = json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def test_current_snapshot_validates(self) -> None:
        snapshot.validate_data(copy.deepcopy(self.data), ROOT)

    def test_pin_drift_fails(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["accepted_hub_pin"] = "0" * 40
        with self.assertRaisesRegex(snapshot.SnapshotError, "pin drift"):
            snapshot.validate_data(mutated, ROOT)

    def test_wrong_generation_and_count_fail(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["evidence_generation"]["id"] = "historical-generation"
        with self.assertRaisesRegex(snapshot.SnapshotError, "wrong default evidence generation"):
            snapshot.validate_data(mutated, ROOT)

        mutated = copy.deepcopy(self.data)
        mutated["evidence_generation"]["acceptance_scenarios"] = 36
        with self.assertRaisesRegex(snapshot.SnapshotError, "scenario count"):
            snapshot.validate_data(mutated, ROOT)

        mutated = copy.deepcopy(self.data)
        ext = next(x for x in mutated["separate_profile_evidence"] if x["id"] == "v1-reference-extension-evidence/5")
        ext["required_profile_cases"] = 92
        with self.assertRaisesRegex(snapshot.SnapshotError, "extension profile count"):
            snapshot.validate_data(mutated, ROOT)

    def test_document_tampering_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "collateral").mkdir()
            (root / "docs").mkdir()
            (root / "component-lock.json").write_bytes((ROOT / "component-lock.json").read_bytes())
            for doc in self.data["documents"]:
                src = ROOT / doc["path"]
                dst = root / doc["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
            for old in self.data["historical_snapshots"]:
                src = ROOT / old["path"]
                dst = root / old["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
            target = root / self.data["documents"][0]["path"]
            target.write_text(target.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
            with self.assertRaisesRegex(snapshot.SnapshotError, "tampering/drift"):
                snapshot.validate_data(copy.deepcopy(self.data), root)

    def test_historical_snapshot_cannot_be_relabelled_current(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["historical_snapshots"][0]["status"] = "current"
        with self.assertRaisesRegex(snapshot.SnapshotError, "historical snapshot relabeled"):
            snapshot.validate_data(mutated, ROOT)

    def test_c2_c3_claim_inflation_fails(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["assurance_levels"]["C2"] = "qualified"
        with self.assertRaisesRegex(snapshot.SnapshotError, "C2/C3"):
            snapshot.validate_data(mutated, ROOT)

    def _c1(self, data):
        return next(x for x in data["separate_profile_evidence"] if x["id"] == "c1-same-host-authority-effect")

    def test_bool_and_float_counts_fail(self) -> None:
        for member, value in (("failures", False), ("errors", False), ("skips", False), ("passed_tests", 73.0)):
            mutated = copy.deepcopy(self.data)
            self._c1(mutated)[member] = value
            with self.assertRaisesRegex(snapshot.SnapshotError, "must be an integer"):
                snapshot.validate_data(mutated, ROOT)
        for member, value in (("workflow_run", float(37694032916)), ("acceptance_scenarios", 35.0)):
            mutated = copy.deepcopy(self.data)
            mutated["evidence_generation"][member] = value
            with self.assertRaisesRegex(snapshot.SnapshotError, "must be an integer"):
                snapshot.validate_data(mutated, ROOT)
        mutated = copy.deepcopy(self.data)
        next(x for x in mutated["separate_profile_evidence"] if x["id"].startswith("v1-reference"))["required_profile_cases"] = 111.0
        with self.assertRaisesRegex(snapshot.SnapshotError, "must be an integer"):
            snapshot.validate_data(mutated, ROOT)

    def test_undeclared_members_fail(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["production_ready"] = True
        with self.assertRaisesRegex(snapshot.SnapshotError, "not a declared member"):
            snapshot.validate_data(mutated, ROOT)
        mutated = copy.deepcopy(self.data)
        del mutated["limitations"]
        with self.assertRaisesRegex(snapshot.SnapshotError, "is required"):
            snapshot.validate_data(mutated, ROOT)

    def test_lock_derived_claims_must_match_the_lock(self) -> None:
        mutated = copy.deepcopy(self.data)
        mutated["evidence_generation"].update(tested_source_sha="0" * 40, accepted_hub_merge="1" * 40)
        with self.assertRaisesRegex(snapshot.SnapshotError, "differs from the lock"):
            snapshot.validate_data(mutated, ROOT)
        mutated = copy.deepcopy(self.data)
        mutated["component_lock"]["qualification_status"] = "rejected"
        with self.assertRaisesRegex(snapshot.SnapshotError, "qualification_status not allowed"):
            snapshot.validate_data(mutated, ROOT)

    def test_duplicate_members_in_the_file_fail(self) -> None:
        raw = self.manifest_path.read_text(encoding="utf-8").replace(
            '"snapshot_status": "current",', '"snapshot_status": "superseded",\n  "snapshot_status": "current",', 1
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "snapshot.json"
            path.write_text(raw, encoding="utf-8")
            with self.assertRaisesRegex(snapshot.SnapshotError, "duplicate JSON key"):
                snapshot.validate_manifest(path, ROOT)

    def test_the_committed_file_validates_through_the_bounded_loader(self) -> None:
        snapshot.validate_manifest(self.manifest_path, ROOT)


if __name__ == "__main__":
    unittest.main()
