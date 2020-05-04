from flask import jsonify, g
from flask_restful import Resource, reqparse

from usmgpm.resources.utils import throw_error
from usmgpm.services.wp_models.wp_user import WPUser
from usmgpm.services.wordpress import WordPressService

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True)
login_parser.add_argument('password', type=str, required=True)


class Login(Resource):
    def post(self):
        args = login_parser.parse_args()
        service: WordPressService = g.wordpress
        auth = service.login(args['username'], args['password'])
        user = service.me()
        return jsonify({'user': user.json, 'token': auth.token})


class Me(Resource):
    def get(self):
        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')
        user: WPUser = g.user
        return jsonify(user.json)
