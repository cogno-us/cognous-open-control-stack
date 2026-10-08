import pytest
from reference_profiles.institutional_review import InstitutionalReview


def assessment(s, incident=False):
    return s.record(scope='synthetic-refund', task='refund', evaluator='test-evaluator', criteria_ref='criteria:1', period='synthetic-run:1',
                    evidence_refs=['evidence:1'], competence='supported', authority_validity='failed', boundary_compliance='unknown', critical_incident=incident)


def test_assessment_and_proposal_never_change_authority(tmp_path):
    s = InstitutionalReview(tmp_path / 'reviews.db', reviewers=['owner'])
    a = assessment(s)
    p = s.propose(assessment_id=a['id'], change='expand', rationale='human review requested')
    assert a['body']['dimensions'] == dict(competence='supported', authority_validity='failed', boundary_compliance='unknown')
    assert not p['authorizing'] and not p['runtime_grant_changed']
    assert [r['kind'] for r in s.history()] == ['assessment','proposal']


@pytest.mark.parametrize('change', ['expand','contract','restore'])
def test_each_change_requires_review_and_retains_incidents(tmp_path, change):
    s = InstitutionalReview(tmp_path / 'reviews.db', reviewers=['owner'])
    a = assessment(s, True)
    assessment(s, False)  # later success cannot average away the incident
    p = s.propose(assessment_id=a['id'], change=change, rationale='proposal')
    kwargs = dict(proposal_id=p['id'], reviewer='owner', disposition='accept', rationale='review', incident_dispositions={})
    with pytest.raises(PermissionError):
        s.decide(**kwargs)
    with pytest.raises(PermissionError):
        s.decide(**dict(kwargs, reviewer='untrusted'))
    r = s.decide(**dict(kwargs, incident_dispositions={a['id']:'review:incident-disposition'}))
    assert not r['authorizing'] and not r['runtime_grant_changed']
    with pytest.raises(PermissionError):
        s.decide(**dict(kwargs, incident_dispositions={a['id']:'review:incident-disposition'}))
    assert len(InstitutionalReview(s.path, reviewers=['owner']).history()) == 4


def test_incomplete_scope_and_false_incident_reference_rejected(tmp_path):
    s = InstitutionalReview(tmp_path / 'reviews.db', reviewers=['owner'])
    a = assessment(s)
    p = s.propose(assessment_id=a['id'], change='retain', rationale='proposal')
    with pytest.raises(ValueError):
        s.decide(proposal_id=p['id'], reviewer='owner', disposition='accept', rationale='review', incident_dispositions={'invented':'ref'})


@pytest.mark.parametrize('reviewers', ['owner', b'owner', None, [], [''], ['  '], ['owner', 1]])
def test_invalid_reviewer_configuration_does_not_create_store(tmp_path, reviewers):
    path = tmp_path / 'reviews.db'
    with pytest.raises(ValueError, match='explicit trusted reviewer identities required'):
        InstitutionalReview(path, reviewers=reviewers)
    assert not path.exists()


def test_empty_reviewer_iterator_does_not_create_store(tmp_path):
    path = tmp_path / 'reviews.db'
    with pytest.raises(ValueError, match='explicit trusted reviewer identities required'):
        InstitutionalReview(path, reviewers=iter(()))
    assert not path.exists()


@pytest.mark.parametrize('disposition', ['accept', 'reject', 'defer'])
def test_reviewer_iterator_retains_exact_identities_and_review_history(tmp_path, disposition):
    s = InstitutionalReview(tmp_path / 'reviews.db', reviewers=iter(['owner']))
    assert s.reviewers == frozenset({'owner'})
    a = assessment(s, True)
    p = s.propose(assessment_id=a['id'], change='restore', rationale='explicit proposal')
    before = s.history()
    kwargs = dict(proposal_id=p['id'], disposition=disposition, rationale='explicit review',
                  incident_dispositions={a['id']: 'review:incident-disposition'})
    with pytest.raises(PermissionError):
        s.decide(reviewer='other', **kwargs)
    assert s.history() == before
    review = s.decide(reviewer='owner', **kwargs)
    assert not review['authorizing'] and not review['runtime_grant_changed']
    history = InstitutionalReview(s.path, reviewers=['owner']).history()
    assert history[:-1] == before
    assert history[-1]['body'] == review['body']
    with pytest.raises(PermissionError, match='already reviewed'):
        s.decide(reviewer='owner', **kwargs)
    assert s.history() == history
