import os

from usmgpm.models.challenge import Challenge
from usmgpm.services.httpservice import HTTPService


class DiscordWebhookService(HTTPService):

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
                       hex_color: int = None):
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
        embed['thumbnail'] = {
            "url": "http://www.usmgames.cl/wp-content/uploads/2020/03/Logotipo3@0.25x-150x150.png"
        }
        return embed

    def post_message(self, message: str):
        return self.post(data={'content': message})

    def post_embed(self, title: str, description: str, message: str = None):
        payload = {
            'embeds': [DiscordWebhookService.generate_embed(title, description, hex_color=16724273)],
        }
        if message:
            payload['content'] = message
        return self.post(data=payload)

    def post_challenge(self, challenge: Challenge):
        production = os.environ.get('FLASK_ENV') == 'production'

        message = f"{challenge.discord_emoji*3} **¡ALERTA DE DESAFÍO DE {challenge.spanish_type.upper()}!** {challenge.discord_emoji*3}"
        if production:
            message = '<@&708244306246369352>\n' + message
        content = f'{challenge.description}\n'
        content += '**Requisitos:**\n'
        for req in challenge.requirements:
            content += f'* {req.description}\n'
        return self.post_embed(challenge.title, content, message)
