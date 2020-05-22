from usmgpm.services.wp_models.wp_user import WPUser
from usmgpm.models.challenge import ChallengeType

from usmgpm.services.service import Service, ForbiddenError
from usmgpm.services.wp_models import WPAuth
from usmgpm.services.wp_models import WPChallenge


class WordPressService(Service):

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
        return WPUser.from_json(self.get(endpoint, {'context': 'edit'}))

    def create_user(self, user: WPUser, password: str, is_admin: bool = False):
        endpoint = f"wp/v2/users"
        data = {
            'email': user.email,
            'username': user.username,
            'display_name': user.display_name,
            'password': password,
        }
        if is_admin:
            data['roles'] = ['administrator']
        else:
            data['roles'] = ['subscriber']
        return WPUser.from_json(self.post(endpoint, data))

    def get_users(self, context=None):
        endpoint = f"wp/v2/users"
        params = {}
        if context is not None:
            params['context'] = context
        return list(map(WPUser.from_json, self.get(endpoint, params)))

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

    def award_user(self, user_id: int, challenge: WPChallenge, points: int):
        slug = 'gamipress-user-earnings'
        endpoint = f"wp/v2/{slug}"
        return self.post(endpoint, {
            'user_id': user_id,
            'post_id': challenge.id,
            'post_type': self.to_challenge_slug(challenge.type),
            'points': points,
            'points_type': 'prestigio'
        })

    def publish_challenge(self, challenge: WPChallenge, status: str = 'publish'):
        slug = self.to_challenge_slug(challenge.type)
        payload = challenge.json
        del payload['slug']
        payload['status'] = status
        return WPChallenge.from_json(self.post(f'wp/v2/{slug}/', payload))
