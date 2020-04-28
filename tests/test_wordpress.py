import os

import pytest

from usmgpm.app import init_app


username = os.environ.get('TEST_USERNAME')
password = os.environ.get('TEST_PASSWORD')

admin_username = os.environ.get('TEST_ADMINNAME')
admin_password = os.environ.get('TEST_ADMINPASS')


@pytest.fixture()
def app():
    return init_app()


def test_login():
    from usmgpm.services.service import UnauthorizedError
    from usmgpm.services.wordpress import WordPressService

    service = WordPressService()
    with pytest.raises(UnauthorizedError):
        service.me()

    auth = service.login(username, password)
    user_data = service.me()
    assert user_data.email == auth.email
    assert user_data.username == auth.username
    assert user_data.display_name == auth.display_name

    auth = service.login(admin_username, admin_password)
    user_data = service.me()
    assert user_data.email == auth.email
    assert user_data.username == auth.username
    assert user_data.display_name == auth.display_name

    assert not service.validate_token('asdf')
    assert service.validate_token(service.token, service.token_type)


def test_retrieve_challenges():
    from usmgpm.models.challenge import ChallengeType
    from usmgpm.services.wordpress import WordPressService

    service = WordPressService()
    service.get_challenges(ChallengeType.PROGRAMMING)
    service.get_challenges(ChallengeType.ART)
    service.get_challenges(ChallengeType.MUSIC)


def test_publish_challenge():
    from usmgpm.models.challenge import ChallengeType
    from usmgpm.services.wp_models import WPChallenge
    from usmgpm.services.service import UnauthorizedError, ForbiddenError
    from usmgpm.services.wordpress import WordPressService

    challenge = WPChallenge('Title', ChallengeType.PROGRAMMING, 'Description')

    service = WordPressService()
    with pytest.raises(UnauthorizedError):
        service.publish_challenge(challenge)

    service.login(username, password)
    with pytest.raises(ForbiddenError):
        service.publish_challenge(challenge)

    service.login(admin_username, admin_password)
    service.publish_challenge(challenge, 'private')


def test_retrieve_earnings():
    from usmgpm.services.wordpress import WordPressService

    service = WordPressService()
    service.login(admin_username, admin_password)
    service.get_earnings()
