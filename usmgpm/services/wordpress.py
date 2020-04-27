from usmgpm.models.challenge import ChallengeType

from usmgpm.services.service import Service
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

    @staticmethod
    def to_challenge_slug(c_type: ChallengeType) -> str:
        if c_type == ChallengeType.ART:
            return 'chllng_art'
        if c_type == ChallengeType.MUSIC:
            return 'chllng_music'
        if c_type == ChallengeType.PROGRAMMING:
            return 'chllng_programming'
        raise ValueError('The given type is not valid')

    def login(self, username, password):
        credentials = {
            'username': username,
            'password': password
        }
        auth = WPAuth.from_json(self.post('jwt-auth/v1/token', credentials))
        self.set_token(auth.token)
        return auth

    def get_challenges(self, c_type: ChallengeType):
        slug = self.to_challenge_slug(c_type)
        endpoint = f"wp/v2/{slug}"
        return list(map(WPChallenge.from_json, self.get(endpoint)))

    def get_challenge(self, id: int, c_type: ChallengeType):
        slug = self.to_challenge_slug(c_type)
        endpoint = f"wp/v2/{slug}/{id}"
        return WPChallenge.from_json(self.get(endpoint))

    def get_earnings(self):
        slug = 'gamipress-user-earnings'
        endpoint = f"wp/v2/{slug}"
        return self.get(endpoint)

    def award_user(self, user_id: int, challenge: WPChallenge):
        slug = 'gamipress-user-earnings'
        endpoint = f"wp/v2/{slug}"
        return self.post(endpoint, {
            'user_id': user_id,
            'post_id': challenge.id,
            'post_type': self.to_challenge_slug(challenge.type)
        })

    def publish_challenge(self, challenge: WPChallenge, status: str = 'publish'):
        slug = self.to_challenge_slug(challenge.type)
        payload = challenge.json
        del payload['slug']
        payload['status'] = status
        self.post(f'wp/v2/{slug}/', payload)
