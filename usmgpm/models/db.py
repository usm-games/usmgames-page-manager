from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = None


def init_db(app):
    global db
    db = SQLAlchemy(app)

    # noinspection PyUnresolvedReferences
    from usmgpm.models.challenge import Challenge
    # noinspection PyUnresolvedReferences
    from usmgpm.models.requirement import ChallengeRequirement

    db.create_all()
