from typing import List

from usmgpm.models.challenge import ChallengeType


class WPUser:
    id: int
    display_name: str
    username: str
    email: str
    roles: List[str]
    meta: dict

    def __init__(self, email: str, username: str, display_name: str = None, roles: List[str] = None,
                 u_id: int = None, meta: dict = None):
        self.email = email
        self.username = username
        self.display_name = display_name
        self.id = u_id
        self.roles = roles
        self.meta = meta

    @staticmethod
    def _serialize_challenge_type(c_type_slug: str):
        if c_type_slug == 'chllng_art':
            return ChallengeType.ART
        if c_type_slug == 'chllng_programming':
            return ChallengeType.PROGRAMMING
        if c_type_slug == 'chllng_music':
            return ChallengeType.MUSIC
        if c_type_slug == 'chllng_modeling':
            return ChallengeType.MODELING
        if c_type_slug == 'chllng_gamedev':
            return ChallengeType.GAMEDEV
        raise ValueError('Unknown Challenge Type slug')

    @staticmethod
    def from_json(data: dict):
        meta = data.get('meta')
        return WPUser(
            email=data.get('email'),
            username=data.get('username'),
            display_name=data.get('name'),
            u_id=data.get('id'),
            roles=data.get('roles'),
            meta=meta
        )

    @property
    def json(self):
        return {
            'email': self.email,
            'username': self.username,
            'display_name': self.display_name,
            'id': self.id,
            'roles': self.roles,
            'points': self.meta.get('_gamipress_prestigio_points') if self.meta is not None else None
        }

    @property
    def is_admin(self):
        return "administrator" in self.roles

    def __str__(self):
        return f"WPUser(id={self.id}, email='{self.email}'," \
            f" username='{self.username}', display_name='{self.display_name}')"
