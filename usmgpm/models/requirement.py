from usmgpm.models.db import db
from usmgpm.models.challenge import Challenge


class ChallengeRequirement(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey(Challenge.id), nullable=False)

    @property
    def json(self):
        return {
            'id': self.id,
            'description': self.description
        }
