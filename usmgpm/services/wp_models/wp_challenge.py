from usmgpm.models.challenge import ChallengeType, Challenge


class WPChallenge:
    id: int
    title: str
    slug: str
    type: ChallengeType

    def __init__(self, title: str, c_type: ChallengeType, content: str, slug: str = None, c_id: int = None):
        self.title = title
        self.slug = slug
        self.type = c_type
        self.content = content
        self.id = c_id

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
        c_type = WPChallenge._serialize_challenge_type(data['type'])
        return WPChallenge(
            title=data['title']['rendered'],
            slug=data['slug'],
            c_type=c_type,
            content=data['content']['rendered'],
            c_id=data['id']
        )

    @staticmethod
    def from_challenge(challenge: Challenge):
        return WPChallenge(
            title=challenge.title,
            c_type=challenge.type,
            content=challenge.description,
            c_id=challenge.wp_id
        )

    @property
    def json(self):
        return {
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
        }

    def __str__(self):
        return f"WPChallenge(title='{self.title}', slug='{self.slug}', type={self.type})"
