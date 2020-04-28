import os

from flask import Flask

from usmgpm.models import init_db


def init_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URI', 'sqlite://')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        init_db()

    from usmgpm.resources import init_api

    with app.app_context():
        init_api()

    return app
