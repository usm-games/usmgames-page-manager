from enum import Enum

from usmgpm.models.db import db


class ChallengeType(Enum):
    PROGRAMMING = 'programming'  # GAMEDEV
    ART = 'art'          # ARTE
    MUSIC = 'music'        # COMPOSITION

    def __str__(self):
        return self.value


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(ChallengeType), nullable=False)

    title = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText, nullable=False)

    @property
    def json(self):
        return {
            'type': str(self.type),
            'title': self.title,
            'description': self.description,
            'requirements': list(map(lambda x: x.json, self.requirements))
        }
