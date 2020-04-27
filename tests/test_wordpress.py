import os

import pytest

from services.wp_models import WPChallenge
from usmgpm.models.challenge import ChallengeType
from usmgpm.services.service import UnauthorizedError, ForbiddenError
from usmgpm.services.wordpress import WordPressService

username = os.environ.get('TEST_USERNAME')
password = os.environ.get('TEST_PASSWORD')

admin_username = os.environ.get('TEST_ADMINNAME')
admin_password = os.environ.get('TEST_ADMINPASS')


def test_login():
    service = WordPressService()
    with pytest.raises(UnauthorizedError):
        service.get('wp/v2/users/me')

    auth = service.login(username, password)
    user_data = service.get('wp/v2/users/me')
    assert user_data['name'] == auth.display_name

    auth = service.login(admin_username, admin_password)
    user_data = service.get('wp/v2/users/me')
    assert user_data['name'] == auth.display_name


def test_retrieve_challenges():
    service = WordPressService()
    service.get_challenges(ChallengeType.PROGRAMMING)
    service.get_challenges(ChallengeType.ART)
    service.get_challenges(ChallengeType.MUSIC)


def test_publish_challenge():
    challenge = WPChallenge('Title', ChallengeType.PROGRAMMING, 'Description')

    service = WordPressService()
    with pytest.raises(UnauthorizedError):
        service.publish_challenge(challenge)

    service.login(username, password)
    with pytest.raises(ForbiddenError):
        service.publish_challenge(challenge)

    service.login(admin_username, admin_password)
    service.publish_challenge(challenge, 'private')
