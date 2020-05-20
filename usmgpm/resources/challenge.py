from flask import jsonify, g
from flask_restful import Resource, reqparse

from usmgpm.models.evaluation import Submission
from usmgpm.services.wp_models.wp_user import WPUser
from usmgpm.resources.utils import throw_error
from usmgpm.models.requirement import ChallengeRequirement
from usmgpm.services.exceptions import ServiceError, ForbiddenError, AlreadyDeletedError, UnauthorizedError
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
        if not g.wordpress.is_logged_in:
            return throw_error('NEEDS_LOGIN')
        user: WPUser = g.user
        results = Challenge.query\
            .outerjoin(Submission, user.id == Submission.user_id)\
            .add_columns(Submission.id)\
            .order_by(Challenge.published.desc())\
            .all()
        data = list(map(lambda x: {**x.Challenge.json, 'your_submission_id': x.id}, results))
        return jsonify(data)

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
            try:
                wp_challenge = service.get_challenge(challenge.wp_id, challenge.type)
                data['wp'] = wp_challenge.json
            except UnauthorizedError:
                return throw_error('DELETED_FROM_WP')
        return jsonify(data)

    def delete(self, id: int):
        if not g.wordpress.is_logged_in:
            return throw_error('NEEDS_LOGIN')

        user: WPUser = g.user
        if not user.is_admin:
            return throw_error('PERMISSION_NEEDED')

        challenge = Challenge.query.filter_by(id=id).first()
        if challenge is None:
            return throw_error('NOT_FOUND_ID')

        service: WordPressService = g.wordpress
        try:
            service.delete_challenge(challenge.wp_id, challenge.type)
        except AlreadyDeletedError:
            pass

        db.session.delete(challenge)
        db.session.commit()
        return jsonify({'message': 'Deleted challenge from https://www.usmgames.cl/ and from server'})
