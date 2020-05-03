from flask import current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def init_db():
    global db
    db.init_app(current_app)
    migrate.init_app(current_app, db)

    # noinspection PyUnresolvedReferences
    from usmgpm.models.challenge import Challenge
    # noinspection PyUnresolvedReferences
    from usmgpm.models.requirement import ChallengeRequirement
    # noinspection PyUnresolvedReferences
    from usmgpm.models.evaluation import Submission
