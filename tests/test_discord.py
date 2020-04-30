import os

import pytest

from usmgpm.app import init_app


@pytest.fixture()
def app():
    return init_app()


def test_post_on_discord():
    from usmgpm.services.discord import DiscordWebhookService

    service = DiscordWebhookService()
    service.post_embed_on_discord('This is a test webhook', 'This is a description for the test embed. If you see '
                                                            'this then it\'s working! But please ignore this'
                                                            ' message')


def test_post_challenge():
    from usmgpm.models.challenge import ChallengeType
    from usmgpm.services.discord import DiscordWebhookService
    from usmgpm.services import WPChallenge

    service = DiscordWebhookService()

    for t in ChallengeType:
        challenge = WPChallenge(f'This is a test {str(t)} challenge', t,
                                f'This challenge consists on doing {str(t)} stuff.')
        service.post_challenge(challenge)
