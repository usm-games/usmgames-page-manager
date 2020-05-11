import secrets
import string

from flask import jsonify, g
from flask_restful import Resource, reqparse

from usmgpm.resources.utils import throw_error
from usmgpm.services.wp_models.wp_user import WPUser
from usmgpm.services.wordpress import WordPressService

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True)

register_parser = reqparse.RequestParser()
register_parser.add_argument('email', type=str, required=True)
register_parser.add_argument('username', type=str, required=True)
register_parser.add_argument('password', type=str, required=True)
register_parser.add_argument('display_name', type=str, required=False)
register_parser.add_argument('admin', type=bool, default=False)


def generate_password(length: int = 20):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


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


class Users(Resource):
    def get(self):
        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')
        user: WPUser = g.user
        if user.is_admin:
            users = service.get_users(context='edit')
        else:
            users = service.get_users()
        return jsonify(list(map(lambda x: x.json, users)))

    def post(self):
        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')
        user: WPUser = g.user
        if not user.is_admin:
            return throw_error('PERMISSION_NEEDED')
        args = register_parser.parse_args()
        user_data = WPUser(args['email'], args['username'], args['display_name'])
        new_user = service.create_user(user_data, generate_password())
        return jsonify(new_user.json)
