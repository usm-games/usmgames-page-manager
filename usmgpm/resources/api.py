from functools import wraps

from flask import request
from flask import Blueprint, g, current_app
from flask_restful import Api

from services import WordPressService


def append_wp_service(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth: str = request.headers.get('Authorization')
        service = WordPressService()
        if auth:
            splitted = auth.split(' ')
            service.set_token(splitted[1], splitted[0])
        g.wordpress = service
        return f(*args, **kwargs)
    return decorated_function


def init_api():
    bp = Blueprint('api', __name__)
    api = Api(bp, decorators=[append_wp_service])

    from usmgpm.resources.challenge import ChallengeInstance, ChallengeList

    api.add_resource(ChallengeList, '/challenges')
    api.add_resource(ChallengeInstance, '/challenges/<id>')

    current_app.register_blueprint(bp, url_prefix='/api')
