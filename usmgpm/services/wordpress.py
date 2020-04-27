from usmgpm.services.wp_models import WPAuth

from services.service import Service


class WordPressService(Service):

    @property
    def url(self):
        """
        This property returns the URL where requests will be made
        :return: URL where requests are made
        :rtype: str
        """
        return 'http://www.usmgames.cl/wp-json/'

    def login(self, username, password):
        credentials = {
            'username': username,
            'password': password
        }
        auth = WPAuth.from_json(self.post('jwt-auth/v1/token', credentials))
        self.set_token(auth.token)
        return auth
