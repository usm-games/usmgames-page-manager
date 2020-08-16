from typing import List

from usmgpm.services.wp_models.wp_user import WPUser
from usmgpm.models.challenge import ChallengeType

from usmgpm.services.httpservice import HTTPService, ForbiddenError
from usmgpm.services.wp_models import WPAuth
from usmgpm.services.wp_models import WPChallenge


class WordPressService(HTTPService):
    saved_me: WPUser = None

    @property
    def url(self):
        """
        This property returns the URL where requests will be made
        :return: URL where requests are made
        :rtype: str
        """
        return 'http://www.usmgames.cl/wp-json/'

    @property
    def is_logged_in(self):
        """
        This property returns the URL where requests will be made
        :return: URL where requests are made
        :rtype: str
        """
        return self.authorization is not None

    @staticmethod
    def to_challenge_slug(c_type: ChallengeType) -> str:
        if c_type == ChallengeType.ART:
            return 'chllng_art'
        if c_type == ChallengeType.MUSIC:
            return 'chllng_music'
        if c_type == ChallengeType.PROGRAMMING:
            return 'chllng_programming'
        if c_type == ChallengeType.MODELING:
            return 'chllng_modeling'
        if c_type == ChallengeType.GAMEDEV:
            return 'chllng_gamedev'
        raise ValueError('The given type is not valid')

    def login(self, username, password):
        credentials = {
            'username': username,
            'password': password
        }
        auth = WPAuth.from_json(self.post('jwt-auth/v1/token', credentials))
        self.set_token(auth.token)
        return auth

    def logout(self):
        self.remove_token()

    def validate_token(self, token: str, type: str = 'Bearer'):
        old_authorization = self.authorization.split(' ') if self.authorization else None
        self.set_token(token, type)
        try:
            self.post('jwt-auth/v1/token/validate')
        except ForbiddenError:
            if old_authorization:
                self.set_token(old_authorization[1], old_authorization[0])
            else:
                self.remove_token()
            return False
        return True

    def me(self):
        endpoint = f"wp/v2/users/me"
        self.saved_me = WPUser.from_json(self.get(endpoint, {'context': 'edit'}))
        return self.saved_me

    def create_user(self, user: WPUser, password: str, is_admin: bool = False):
        endpoint = f"wp/v2/users"
        data = {
            'email': user.email,
            'username': user.username,
            'name': user.display_name,
            'password': password,
        }
        if is_admin:
            data['roles'] = ['administrator']
        else:
            data['roles'] = ['subscriber']
        return WPUser.from_json(self.post(endpoint, data))

    def get_users(self, context=None, search: str = None, fields: List[str] = None, per_page: int = 50):
        endpoint = f"wp/v2/users"
        params = {}
        if context is not None:
            params['context'] = context
        if search is not None:
            params['search'] = search
            params['per_page'] = per_page
        if fields is not None:
            params['_fields'] = ','.join(fields)
        return list(map(WPUser.from_json, self.get(endpoint, params)))

    def get_user(self, user_id: int, context=None):
        endpoint = f"wp/v2/users/{user_id}"
        params = {}
        if context is not None:
            params['context'] = context
        return WPUser.from_json(self.get(endpoint, params))

    def get_challenges(self, c_type: ChallengeType):
        slug = self.to_challenge_slug(c_type)
        endpoint = f"wp/v2/{slug}"
        return list(map(WPChallenge.from_json, self.get(endpoint)))

    def get_challenge(self, id: int, c_type: ChallengeType):
        slug = self.to_challenge_slug(c_type)
        endpoint = f"wp/v2/{slug}/{id}"
        return WPChallenge.from_json(self.get(endpoint))

    def delete_challenge(self, id: int, c_type: ChallengeType):
        slug = self.to_challenge_slug(c_type)
        endpoint = f"wp/v2/{slug}/{id}"
        return WPChallenge.from_json(self.delete(endpoint))

    def get_earnings(self):
        slug = 'gamipress-user-earnings'
        endpoint = f"wp/v2/{slug}"
        return self.get(endpoint)

    def award_points(self, user_id: int, points: int):
        endpoint = f"wp/v2/users/{user_id}"
        user = self.get_user(user_id, context='edit')
        past_points = user.meta.get('_gamipress_prestigio_points')
        user.meta['_gamipress_prestigio_points'] = past_points + points
        return self.patch(endpoint, {'meta': user.meta})

    def award_user(self, user_id: int, challenge: WPChallenge, points: int):
        slug = 'gamipress-user-earnings'
        endpoint = f"wp/v2/{slug}"
        award = self.post(endpoint, {
            'user_id': user_id,
            'post_id': challenge.id,
            'post_type': self.to_challenge_slug(challenge.type),
            'points': points,
            'points_type': 'prestigio'
        })
        self.award_points(user_id, points)
        return award

    def publish_challenge(self, challenge: WPChallenge, status: str = 'publish'):
        slug = self.to_challenge_slug(challenge.type)
        payload = challenge.json
        del payload['slug']
        payload['status'] = status
        return WPChallenge.from_json(self.post(f'wp/v2/{slug}/', payload))
