from flask import jsonify, g
from flask_restful import Resource, reqparse

from usmgpm.resources.utils import throw_error
from usmgpm.models.requirement import ChallengeRequirement
from usmgpm.services.exceptions import ServiceError, ForbiddenError
from usmgpm.models.db import db
from usmgpm.services import WordPressService, WPChallenge, DiscordWebhookService
from usmgpm.models.challenge import Challenge, ChallengeType

__all__ = ['ChallengeList', 'ChallengeInstance']

challenge_parser = reqparse.RequestParser()
challenge_parser.add_argument('type', type=ChallengeType, choices=list(ChallengeType), required=True)
challenge_parser.add_argument('title', type=str, required=True)
challenge_parser.add_argument('description', type=str, required=True)
challenge_parser.add_argument('status', type=str, choices=['publish', 'private', 'draft'], default='publish')
challenge_parser.add_argument('requirements', type=str, required=True, action='append')
challenge_parser.add_argument('notify', type=bool, default=True)

getter_parser = reqparse.RequestParser()
getter_parser.add_argument('fetch', action='store_true')


class ChallengeList(Resource):
    def get(self):
        try:
            challenges = Challenge.query.all()
            return jsonify(list(map(lambda x: x.json, challenges)))
        except Exception as e:
            print(type(e), e)
            raise e

    def post(self):
        args = challenge_parser.parse_args()
        instance = Challenge(
            type=args['type'],
            title=args['title'],
            description=args['description']
        )

        for requirement in args['requirements']:
            r = ChallengeRequirement(description=requirement)
            instance.requirements.append(r)

        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')
        wp_challenge = WPChallenge.from_challenge(instance)

        try:
            wp_c = service.publish_challenge(wp_challenge, status=args['status'])
            if args['notify']:
                discord = DiscordWebhookService()
                discord.post_challenge(wp_c)
            instance.wp_id = wp_c.id
        except ForbiddenError:
            return throw_error('PERMISSION_NEEDED')
        except ServiceError:
            return throw_error('WORDPRESS_ERROR')

        db.session.add(instance)
        db.session.commit()

        res = jsonify(instance.json)
        return res


class ChallengeInstance(Resource):
    def get(self, id: int):
        challenge = Challenge.query.filter_by(id=id).first()
        if challenge is None:
            return throw_error('NOT_FOUND_ID')
        args = getter_parser.parse_args()
        data = challenge.json
        fetch_wp = args.get('fetch')
        if fetch_wp:
            if challenge.wp_id is None:
                return throw_error('NO_ASSOCIATED_ACHIEV')
            service: WordPressService = g.wordpress
            wp_challenge = service.get_challenge(challenge.wp_id, challenge.type)
            data['wp'] = wp_challenge.json
        return jsonify(data)
