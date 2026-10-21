import pytest
from reference_profiles.sqlite_recovery import snapshot, restore
from reference_profiles.institutional_review import InstitutionalReview


def test_restore_refuses_duplicate_manifest_members(tmp_path):
    s = InstitutionalReview(tmp_path / 'review.db', reviewers=['owner'])
    snapshot(s.path, tmp_path / 'backup')
    path = tmp_path / 'backup/manifest.json'
    text = path.read_text()
    assert '"activation_authorized": false,' in text
    # first member says true, the last (which plain json.loads keeps) says false
    path.write_text(text.replace('"activation_authorized": false,',
                                 '"activation_authorized": true,\n  "activation_authorized": false,'))
    with pytest.raises(ValueError, match='duplicate JSON key'):
        restore(tmp_path / 'backup', tmp_path / 'restored.db')
    assert not (tmp_path / 'restored.db').exists()


def test_restore_refuses_non_object_manifest(tmp_path):
    s = InstitutionalReview(tmp_path / 'review.db', reviewers=['owner'])
    snapshot(s.path, tmp_path / 'backup')
    (tmp_path / 'backup/manifest.json').write_text('[]')
    with pytest.raises(ValueError, match='unsupported snapshot contract'):
        restore(tmp_path / 'backup', tmp_path / 'restored.db')
