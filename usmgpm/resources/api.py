from functools import wraps

from flask import request
from flask import Blueprint, g, current_app
from flask_restful import Api

from usmgpm.services.email import EmailService
from usmgpm.resources.auth import Me, Users
from usmgpm.resources.utils import throw_error
from usmgpm.services.exceptions import ForbiddenError
from usmgpm.services import WordPressService


def append_wp_service(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth: str = request.headers.get('Authorization')
        service = WordPressService()
        if auth:
            splitted = auth.split(' ')
            if len(splitted) != 2:
                return throw_error('INVALID_HEADER', 'Invalid Authorization header')
            service.set_token(splitted[1], splitted[0])
            try:
                g.user = service.me()
            except ForbiddenError:
                return throw_error('INVALID_TOKEN')
        g.wordpress = service
        g.mail = EmailService()
        return f(*args, **kwargs)
    return decorated_function


def init_api():
    bp = Blueprint('api', __name__)
    api = Api(bp, decorators=[append_wp_service])

    from usmgpm.resources.auth import Login
    from usmgpm.resources.submission import ChallengeSubmissionList, ChallengeSubmission, UserSubmissionList, Evaluation
    from usmgpm.resources.challenge import ChallengeInstance, ChallengeList

    api.add_resource(ChallengeList, '/challenges')
    api.add_resource(ChallengeInstance, '/challenges/<int:id>')

    api.add_resource(ChallengeSubmissionList, '/challenges/<int:c_id>/submissions')
    api.add_resource(ChallengeSubmission, '/challenges/<int:c_id>/submissions/<int:u_id>')
    api.add_resource(Evaluation, '/challenges/<int:c_id>/submissions/<int:u_id>/evaluate')

    api.add_resource(UserSubmissionList, '/users/<int:u_id>/submissions')
    api.add_resource(Login, '/auth/login')
    api.add_resource(Me, '/auth/me')
    api.add_resource(Users, '/users')

    current_app.register_blueprint(bp, url_prefix='/api')
