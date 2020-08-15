from typing import List

import unidecode
import secrets
import string

from flask import jsonify, g
from flask_restful import Resource, reqparse

from usmgpm.services.email import EmailService
from usmgpm.resources.utils import throw_error
from usmgpm.services.wp_models.wp_user import WPUser
from usmgpm.services.wordpress import WordPressService

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True)
login_parser.add_argument('password', type=str, required=True)

register_parser = reqparse.RequestParser()
register_parser.add_argument('email', type=str, required=True)
register_parser.add_argument('display_name', type=str, required=False)
register_parser.add_argument('admin', type=bool, default=False)


def generate_username(real_name: str, used_usernames: List[str] = None):
    username = unidecode.unidecode(real_name)
    username = '.'.join(username.split()).lower()

    alphabet = string.ascii_letters + string.digits + '.'
    username = ''.join([c for c in username if c in alphabet])
    if used_usernames is None:
        return username

    count = 0
    suffix = ''
    while username + suffix in used_usernames:
        count += 1
        suffix = '' if count == 0 else '.' + str(count)
    return username + suffix


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

        email = args['email']
        display_name = args['display_name']
        is_admin = args['admin']

        users = service.get_users(context='edit', search=generate_username(display_name), fields=['username'])
        if email in [user.email for user in users]:
            return throw_error('EMAIL_IN_USE')
        username = generate_username(display_name, [user.username for user in users])
        password = generate_password()

        user_data = WPUser(email, username, display_name)
        new_user = service.create_user(user_data, password, is_admin=is_admin)
        mail: EmailService = g.mail
        if mail.is_valid:
            with open('./usmgpm/services/assets/email.html', 'r') as f:
                content = ''.join(f.readlines()) % (user_data.display_name, user_data.username, password)
            mail.send(email, '[USM Games] Bienvenido a usmgames.cl!', content)

        return jsonify(new_user.json)
