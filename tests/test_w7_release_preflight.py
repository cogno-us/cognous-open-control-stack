"""W7 release preflight: accepted producers are not automatically selected release pins."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class W7ReleasePreflight(unittest.TestCase):
    def setUp(self):
        self.matrix = json.loads((ROOT / "scenarios/w7-claim-test-matrix.json").read_text())
        self.lock = json.loads((ROOT / "component-lock.json").read_text())

    def test_accepted_producer_ledger_exact(self):
        p = self.matrix["p2_accepted_producers"]
        self.assertEqual(p["action_manifest"]["sha"], "8d1572d4f926c968a8704cb912a6e9d49166f74a")
        self.assertEqual(p["control_plane"]["sha"], "e66e5f163c5d5c112ff345a2f332b4c3893ee183")
        self.assertEqual(p["execution_runtime"]["sha"], "bd398f16c4cee329d2d0213afc3236ca9232d29e")
        self.assertIsNone(p["replay_bundle"]["sha"])
        self.assertIsNone(p["evidence_pack"]["sha"])

    def test_no_premature_release_claim_or_pin_advance(self):
        self.assertIs(self.matrix["release_qualified"], False)
        self.assertIs(self.matrix["component_lock_advanced"], False)
        if self.lock["runtime_profile"] == "merged-producers-v1":
            self.assertEqual(self.lock["components"]["action_manifest"]["sha"], "46c950bed37fe3812000895430bc0312d29e37ce")
            self.assertEqual(self.lock["components"]["control_plane"]["sha"], "d3dadee70bd319812b207389ab1e0f6efe511916")
            self.assertEqual(self.lock["components"]["moltbot_safe"]["accepted_sha"], "c3c3ee7188b9367cf70b08074b9c40a5c70c94ac")
        else:
            self.assertEqual(self.lock["runtime_profile"], "bounded-v1-local-sqlite-refund-c1-c8")
            self.assertEqual(self.lock["qualification_status"], "governor_acceptance_pending")
            self.assertIs(self.lock["w7_candidate_evidence"]["release_authorized"], False)
            expected = {
                "action_manifest": ("sha", "8d1572d4f926c968a8704cb912a6e9d49166f74a"),
                "control_plane": ("sha", "e66e5f163c5d5c112ff345a2f332b4c3893ee183"),
                "moltbot_safe": ("accepted_sha", "da9f52900ee2596dab087ec6c249ba84915d2b13"),
                "replay_bundle": ("sha", "2069a0ba1398812c3a8669331a7d8b87c80c4a48"),
                "governance_evidence_pack": ("sha", "87293cfcbe8dfa2368d5bf77019945ba8ef1ae71"),
            }
            for component, (field, sha) in expected.items():
                self.assertEqual(self.lock["components"][component][field], sha)

    def test_optional_profiles_nonblocking(self):
        entries = {entry["id"]: entry for entry in self.matrix["claims"]}
        for name in ("optional-openappa", "optional-microsoft-agt", "optional-openshell"):
            self.assertIs(entries[name]["blocking_core"], False)
        self.assertEqual(entries["optional-openshell"]["status"], "deferred_not_live_qualified")

    def test_claim_ids_unique(self):
        ids = [c["id"] for c in self.matrix["claims"]]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
