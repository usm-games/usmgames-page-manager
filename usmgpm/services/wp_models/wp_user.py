from typing import List

from usmgpm.models.challenge import ChallengeType


class WPUser:
    id: int
    display_name: str
    username: str
    email: str
    roles: List[str]

    def __init__(self, email: str, username: str, display_name: str = None, roles: List[str] = None, u_id: int = None):
        self.email = email
        self.username = username
        self.display_name = display_name
        self.id = u_id
        self.roles = roles

    @staticmethod
    def _serialize_challenge_type(c_type_slug: str):
        if c_type_slug == 'chllng_art':
            return ChallengeType.ART
        if c_type_slug == 'chllng_programming':
            return ChallengeType.PROGRAMMING
        if c_type_slug == 'chllng_music':
            return ChallengeType.MUSIC
        raise ValueError('Unknown Challenge Type slug')

    @staticmethod
    def from_json(data: dict):
        return WPUser(
            email=data.get('email'),
            username=data.get('username'),
            display_name=data.get('name'),
            u_id=data.get('id'),
            roles=data.get('roles')
        )

    @property
    def json(self):
        return {
            'email': self.email,
            'username': self.username,
            'display_name': self.display_name,
            'id': self.id,
            'roles': self.roles
        }

    def __str__(self):
        return f"WPUser(id={self.id}, email='{self.email}'," \
            f" username='{self.username}', display_name='{self.display_name}')"