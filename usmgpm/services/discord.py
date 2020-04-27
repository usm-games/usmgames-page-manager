import os

from usmgpm.models.challenge import ChallengeType

from usmgpm.services.service import Service
from usmgpm.services.wp_models import WPChallenge


class DiscordWebhookService(Service):

    @property
    def url(self):
        """
        This property returns the URL where requests will be made
        :return: URL where requests are made
        :rtype: str
        """
        discord_id = os.environ['DISCORD_HOOK_ID']
        discord_pass = os.environ['DISCORD_HOOK_PASS']
        return f"https://discordapp.com/api/webhooks/{discord_id}/{discord_pass}"

    def post_on_discord(self):
        pass
