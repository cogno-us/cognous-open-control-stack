"""Trusted-host institutional review records. Never issues or changes a runtime grant."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import uuid


class InstitutionalReview:
    def __init__(self, path, *, reviewers):
        if not reviewers or any(type(r) is not str or not r for r in reviewers):
            raise ValueError('explicit trusted reviewer identities required')
        self.path, self.reviewers = Path(path), frozenset(reviewers)
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS records (seq INTEGER PRIMARY KEY, id TEXT UNIQUE, kind TEXT, scope TEXT, body TEXT)')
            conn.commit()

    def _append(self, conn, kind, scope, body):
        identity = str(uuid.uuid4())
        conn.execute('INSERT INTO records(id,kind,scope,body) VALUES (?,?,?,?)',
                     (identity, kind, scope, json.dumps(body, sort_keys=True, allow_nan=False)))
        return {'id': identity, 'kind': kind, 'scope': scope, 'body': body,
                'authorizing': False, 'runtime_grant_changed': False}

    def record(self, *, scope, task, evaluator, criteria_ref, period, evidence_refs,
               competence, authority_validity, boundary_compliance, critical_incident=False):
        if any(type(v) is not str or not v.strip() for v in (scope, task, evaluator, criteria_ref, period)):
            raise ValueError('complete assessment scope required')
        if not isinstance(evidence_refs, list) or not evidence_refs or any(type(r) is not str or not r for r in evidence_refs):
            raise ValueError('evidence references required')
        if type(critical_incident) is not bool:
            raise ValueError('incident flag must be boolean')
        dimensions = dict(competence=competence, authority_validity=authority_validity, boundary_compliance=boundary_compliance)
        if any(v not in ('supported', 'failed', 'unknown') for v in dimensions.values()):
            raise ValueError('typed independent dimensions required')
        body = dict(task=task, evaluator=evaluator, criteria_ref=criteria_ref, period=period,
                    evidence_refs=evidence_refs, dimensions=dimensions, critical_incident=critical_incident)
        with closing(sqlite3.connect(self.path)) as conn:
            result = self._append(conn, 'assessment', scope, body)
            conn.commit()
            return result

    def propose(self, *, assessment_id, change, rationale):
        if change not in ('expand', 'contract', 'restore', 'retain') or type(rationale) is not str or not rationale.strip():
            raise ValueError('explicit proposed change and rationale required')
        with closing(sqlite3.connect(self.path)) as conn:
            row = conn.execute("SELECT scope FROM records WHERE id=? AND kind='assessment'", (assessment_id,)).fetchone()
            if row is None:
                raise KeyError(assessment_id)
            result = self._append(conn, 'proposal', row[0], dict(assessment_id=assessment_id, change=change, rationale=rationale))
            conn.commit()
            return result

    def decide(self, *, proposal_id, reviewer, disposition, rationale, incident_dispositions):
        if reviewer not in self.reviewers:
            raise PermissionError('reviewer not admitted by trusted configuration')
        if disposition not in ('accept', 'reject', 'defer') or type(rationale) is not str or not rationale.strip():
            raise ValueError('explicit review disposition required')
        if type(incident_dispositions) is not dict or any(type(v) is not str or not v.strip() for v in incident_dispositions.values()):
            raise ValueError('incident dispositions must be explicit references')
        with closing(sqlite3.connect(self.path, isolation_level=None)) as conn:
            conn.execute('BEGIN IMMEDIATE')
            row = conn.execute("SELECT scope FROM records WHERE id=? AND kind='proposal'", (proposal_id,)).fetchone()
            if row is None:
                raise KeyError(proposal_id)
            prior = conn.execute("SELECT body FROM records WHERE kind='review'").fetchall()
            if any(json.loads(r[0])['proposal_id'] == proposal_id for r in prior):
                raise PermissionError('proposal already reviewed; create a new proposal')
            incidents = {r[0] for r in conn.execute("SELECT id,body FROM records WHERE kind='assessment' AND scope=?", (row[0],))
                         if json.loads(r[1])['critical_incident']}
            if disposition == 'accept' and not incidents <= incident_dispositions.keys():
                raise PermissionError('critical incidents require explicit review dispositions')
            if not incident_dispositions.keys() <= incidents:
                raise ValueError('unknown incident reference')
            result = self._append(conn, 'review', row[0], dict(proposal_id=proposal_id, reviewer=reviewer,
                                  disposition=disposition, rationale=rationale, incident_dispositions=incident_dispositions))
            conn.commit()
            return result

    def history(self):
        with closing(sqlite3.connect(self.path)) as conn:
            return [dict(seq=r[0], id=r[1], kind=r[2], scope=r[3], body=json.loads(r[4]))
                    for r in conn.execute('SELECT * FROM records ORDER BY seq')]
