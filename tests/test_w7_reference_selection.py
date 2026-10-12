"""Exact-reference release selection guard; does not activate production."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "profiles/bounded-v1-reference-release-selection.json"

class ReferenceSelection(unittest.TestCase):
    def test_selection_is_immutable_and_historical_lock_unchanged(self):
        rec = json.loads(RELEASE.read_text())
        for key in ("selected_candidate", "historical_lock"):
            item = rec[key]
            blob = subprocess.check_output(["git","hash-object",item["path"]],cwd=ROOT,text=True).strip()
            self.assertEqual(blob,item["git_blob_sha"])
        historic=json.loads((ROOT/rec["historical_lock"]["path"]).read_text())
        proposed=json.loads((ROOT/rec["selected_candidate"]["path"]).read_text())
        self.assertEqual(historic["runtime_profile"],"merged-producers-v1")
        self.assertEqual(proposed["runtime_profile"],rec["selected_candidate"]["profile"])
        self.assertEqual(rec["selected_candidate"]["accepted_hub_commit"],"f7d03c719b9be3b9c3fe0fe300df642b0f408d98")
        self.assertEqual(proposed["qualification_status"],"governor_acceptance_pending")
        self.assertFalse(proposed["w7_candidate_evidence"]["release_authorized"])
        checks={"action_manifest":("sha","action_manifest"),
                "control_plane":("sha","control_plane"),
                "moltbot_safe":("accepted_sha","execution_runtime"),
                "replay_bundle":("sha","replay_bundle"),
                "governance_evidence_pack":("sha","governance_evidence_pack")}
        for component,(field,kind) in checks.items():
            self.assertEqual(proposed["components"][component][field],rec["accepted_revisions"][kind])

    def test_reference_only_release_scope(self):
        rec=json.loads(RELEASE.read_text())
        self.assertEqual(rec["selection_kind"],"scoped_reference_only")
        self.assertTrue(rec["reference_scope_authorized_by_founder"])
        self.assertEqual(rec["reference_scope_authorization_target"],"bounded-v1-local-sqlite-refund-c1-c8")
        self.assertFalse(rec["production_deployment_authorized"])
        self.assertEqual(rec["governor_acceptance"]["status"],"pending")
        self.assertEqual(rec["publication_state"],"governor_final_acceptance_pending")
        self.assertFalse(rec["reference_release_authorized"])
        self.assertEqual(rec["optional_profiles"]["openshell"],"deferred_not_live_qualified")
        for phrase in ("general production deployment or production hardening","generalized all-path stop",
                       "fleet cancellation or remote quiescence","independent original proposal payload verification",
                       "general rollback","universal exactly-once external effects","live OpenShell confinement, credential isolation or egress assurance"):
            self.assertIn(phrase,rec["explicit_exclusions"])

if __name__=="__main__":
    unittest.main()
