from flask import current_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db():
    global db
    db.init_app(current_app)

    # noinspection PyUnresolvedReferences
    from usmgpm.models.challenge import Challenge
    # noinspection PyUnresolvedReferences
    from usmgpm.models.requirement import ChallengeRequirement
    # noinspection PyUnresolvedReferences
    from usmgpm.models.evaluation import Submission

    db.create_all()
