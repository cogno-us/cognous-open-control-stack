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
        ext = next(x for x in mutated["separate_profile_evidence"] if x["id"] == "v1-reference-extension-evidence/4")
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


if __name__ == "__main__":
    unittest.main()
