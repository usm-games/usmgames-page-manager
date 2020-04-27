from flask import Blueprint, Flask
from flask_restful import Api


def init_api(app: Flask):
    bp = Blueprint('api', __name__)
    api = Api(bp)

    from usmgpm.resources.challenge import ChallengeInstance, ChallengeList

    api.add_resource(ChallengeList, '/challenges')
    api.add_resource(ChallengeInstance, '/challenges/<id>')

    app.register_blueprint(bp, url_prefix='/api')
