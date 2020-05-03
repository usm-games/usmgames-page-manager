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

    challenge = db.relationship('Challenge', backref=db.backref('challenges', lazy=False))
    user_id = db.Column(db.Integer, nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey(Challenge.id), nullable=False)

    def _parse_content(self):
        splitted = self.content.split(';')
        comment = splitted[0]
        evidence = splitted[1:]
        if len(evidence) % 2 != 0:
            raise ValueError("The contet is invalid")
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
            'challenge_id': self.challenge_id,
            'submission': self._parse_content(),
            'evaluation': evaluation
        }
