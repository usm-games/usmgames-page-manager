import os

from usmgpm.models.challenge import Challenge
from usmgpm.services.service import Service


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

    @staticmethod
    def generate_embed(title: str, description: str, title_url: str = None, footer_text: str = None,
                       hex_color: str = None):
        embed = {
            'title': title,
            'description': description
        }
        if hex_color:
            embed['color'] = hex_color
        if footer_text:
            embed['footer'] = {'text': footer_text}
        if title_url:
            embed['url'] = title_url
        return embed

    def post_message(self, message: str):
        return self.post(data={'content': message})

    def post_embed(self, title: str, description: str, message: str = None):
        payload = {
            'embeds': [DiscordWebhookService.generate_embed(title, description)]
        }
        if message:
            payload['content'] = message
        return self.post(data=payload)

    def post_challenge(self, challenge: Challenge):
        message = f"{challenge.discord_emoji*3} ¡Se ha publicado un nuevo desafío de {challenge.spanish_type}! {challenge.discord_emoji*3}"
        content = f'{challenge.description}\n'
        content += '**Requisitos:**\n'
        for req in challenge.requirements:
            content += f'* {req.description}\n'
        return self.post_embed(challenge.title, content, message)
