import datetime
from enum import Enum

from usmgpm.models.db import db


class ChallengeType(Enum):
    PROGRAMMING = 'programming'
    ART = 'art2d'
    MUSIC = 'music'
    GAMEDEV = 'gamedev'
    MODELING = 'art3d'

    def __str__(self):
        return self.value


class Challenge(db.Model):
    __table_name__ = 'challenge'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(ChallengeType), nullable=False)

    title = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText, nullable=False)
    wp_id = db.Column(db.Integer, nullable=True)

    requirements = db.relationship('ChallengeRequirement',
                                   backref=db.backref('challenge', lazy=False),
                                   cascade="all,delete")
    submissions = db.relationship('Submission',
                                  backref=db.backref('challenge', lazy=True),
                                  cascade="all,delete")

    published = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def json(self):
        return {
            'id': self.id,
            'type': str(self.type),
            'title': self.title,
            'description': self.description,
            'requirements': list(map(lambda x: x.json, self.requirements)),
            'published': self.published
        }

    @property
    def discord_emoji(self):
        if self.type == ChallengeType.PROGRAMMING:
            return '<:Coding:715742757335072808>'
        if self.type == ChallengeType.ART:
            return '<:Art:715743312597876881>'
        if self.type == ChallengeType.MUSIC:
            return '<:Music:715742514115772437>'
        if self.type == ChallengeType.GAMEDEV:
            return '<:Design:717218969336938592>'
        if self.type == ChallengeType.MODELING:
            return '<:3D:715742845683630112>'
        raise ValueError('Unexpected challenge type')

    @property
    def spanish_type(self):
        if self.type == ChallengeType.PROGRAMMING:
            return 'programación'
        if self.type == ChallengeType.ART:
            return 'arte 2D'
        if self.type == ChallengeType.MUSIC:
            return 'música'
        if self.type == ChallengeType.GAMEDEV:
            return 'game dev'
        if self.type == ChallengeType.MODELING:
            return 'arte 3D'
        raise ValueError('Unexpected challenge type')
