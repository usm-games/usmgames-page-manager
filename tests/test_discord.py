import time

import pytest

from usmgpm.app import init_app


@pytest.fixture()
def app():
    return init_app(testing=True)


def test_post_on_discord():
    from usmgpm.services.discord import DiscordWebhookService

    service = DiscordWebhookService()
    service.post_embed('This is a test webhook', 'This is a description for the test embed. If you see '
                                                 'this then it\'s working! But please ignore this'
                                                 ' message')
    time.sleep(1)


def test_post_challenge(app):
    from usmgpm.models.challenge import ChallengeType, Challenge
    from usmgpm.models.requirement import ChallengeRequirement
    from usmgpm.services.discord import DiscordWebhookService

    service = DiscordWebhookService()

    for t in ChallengeType:
        challenge = Challenge(title=f'This is a test {str(t)} challenge',
                              description=f'This challenge consists on doing {str(t)} stuff.',
                              type=t)
        challenge.requirements.append(ChallengeRequirement(description='Requirement A'))
        challenge.requirements.append(ChallengeRequirement(description='Requirement B'))
        service.post_challenge(challenge)
        time.sleep(1)
