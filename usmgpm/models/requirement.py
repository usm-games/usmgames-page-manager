from usmgpm.models.db import db


class ChallengeRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    evaluation_note = db.Column(db.Text, nullable=True, default=None)
    checked = db.Column(db.Boolean, nullable=True, default=None)

    challenge = db.relationship('Challenge', backref=db.backref('requirements', lazy=False))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)

    @property
    def json(self):
        return {
            'id': self.id,
            'description': self.description,
            'evaluation_note': self.evaluation_note,
            'checked': self.checked
        }
