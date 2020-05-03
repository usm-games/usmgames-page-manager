from usmgpm.models.challenge import Challenge, ChallengeType


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
        description = f"<p>{challenge.description}</p>"

        req_list = "<ul>"
        for req in challenge.requirements:
            req_list += f"<li>{req.description}</li>"
        req_list += "</ul>"

        return WPChallenge(
            title=challenge.title,
            c_type=challenge.type,
            content=description + req_list,
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

    @property
    def spanish_type(self):
        if self.type == ChallengeType.PROGRAMMING:
            return 'programación'
        if self.type == ChallengeType.ART:
            return 'arte'
        if self.type == ChallengeType.MUSIC:
            return 'música'
        raise ValueError('Unexpected challenge type')

    @property
    def emoji(self):
        if self.type == ChallengeType.PROGRAMMING:
            return '🔧'
        if self.type == ChallengeType.ART:
            return '🖌'
        if self.type == ChallengeType.MUSIC:
            return '🎶'
        raise ValueError('Unexpected challenge type')
