import os

from flask import Flask
from flask_cors import CORS

from usmgpm.models import init_db


def init_app(create_all=False, testing=False):
    app = Flask(__name__)
    CORS(app, resources={r"/api/*"})

    database_url = os.environ.get('DATABASE_URL')
    if database_url is None:
        database_url = os.environ.get('DATABASE_URI', 'sqlite://')

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if testing:
        app.config["TESTING"] = True

    email = os.environ.get('MAIL_USERNAME')
    email_password = os.environ.get('MAIL_PASSWORD')
    if email and email_password:
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USERNAME'] = email
        app.config['MAIL_PASSWORD'] = email_password
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = True

    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', None)
    with app.app_context():
        db = init_db()
        if create_all:
            db.create_all()

    from usmgpm.resources import init_api

    with app.app_context():
        init_api()

    return app
