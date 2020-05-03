from usmgpm.models.db import db


class ChallengeRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)

    @property
    def json(self):
        return {
            'id': self.id,
            'description': self.description
        }
