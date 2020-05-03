from functools import wraps

from flask import request, jsonify
from flask import Blueprint, g, current_app
from flask_restful import Api

from usmgpm.services import WordPressService


def append_wp_service(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth: str = request.headers.get('Authorization')
        service = WordPressService()
        if auth:
            splitted = auth.split(' ')
            if len(splitted) != 2:
                res = jsonify({'message': 'Bad formatted authorization header'})
                res.status_code = 403
                return res
            service.set_token(splitted[1], splitted[0])
        g.wordpress = service
        return f(*args, **kwargs)
    return decorated_function


def init_api():
    bp = Blueprint('api', __name__)
    api = Api(bp, decorators=[append_wp_service])

    from usmgpm.resources.auth import Login
    from usmgpm.resources.submission import ChallengeSubmissionList, ChallengeSubmission, UserSubmissionList, Evaluation
    from usmgpm.resources.challenge import ChallengeInstance, ChallengeList

    api.add_resource(ChallengeList, '/challenges')
    api.add_resource(ChallengeInstance, '/challenges/<id>')

    api.add_resource(ChallengeSubmissionList, '/challenges/<c_id>/submissions')
    api.add_resource(ChallengeSubmission, '/challenges/<c_id>/submissions/<u_id>')
    api.add_resource(Evaluation, '/challenges/<c_id>/submissions/<u_id>/evaluate')

    api.add_resource(UserSubmissionList, '/users/<u_id>/submissions')
    api.add_resource(Login, '/auth/login')

    current_app.register_blueprint(bp, url_prefix='/api')
