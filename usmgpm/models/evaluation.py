import datetime

from sqlalchemy import UniqueConstraint

from usmgpm.models.db import db
from usmgpm.models.challenge import Challenge


class Submission(db.Model):
    __table_args__ = (
        UniqueConstraint("challenge_id", "user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)

    evaluation_note = db.Column(db.Text, nullable=True, default=None)
    approved = db.Column(db.Boolean, nullable=True, default=None)

    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.Text, nullable=True)

    challenge_id = db.Column(db.Integer, db.ForeignKey(Challenge.id), nullable=False)

    submitted = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def _parse_content(self):
        splitted = self.content.split(';')
        comment = splitted[0]
        evidence = splitted[1:]
        if len(evidence) % 2 != 0:
            raise ValueError("The content is invalid")
        n_evidence = len(evidence) // 2
        parsed_evidence = []
        for i_evidence in range(n_evidence):
            parsed_evidence.append({
                'url': evidence[i_evidence * 2],
                'description': evidence[i_evidence * 2 + 1]
            })
        return {
            'comment': comment,
            'evidence': parsed_evidence
        }

    @property
    def json(self):
        evaluation = {
                'approved': self.approved,
                'comment': self.evaluation_note,
            } if self.approved is not None else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'challenge_id': self.challenge_id,
            'submission': self._parse_content(),
            'evaluation': evaluation,
            'submitted': self.submitted
        }
