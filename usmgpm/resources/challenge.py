from flask import jsonify, g
from flask_restful import Resource, reqparse

from usmgpm.services.exceptions import ServiceError, ForbiddenError
from usmgpm.models.db import db
from usmgpm.services import WordPressService, WPChallenge
from usmgpm.models.challenge import Challenge, ChallengeType

__all__ = ['ChallengeList', 'ChallengeInstance']

challenge_parser = reqparse.RequestParser()
challenge_parser.add_argument('type', type=ChallengeType, choices=list(ChallengeType), required=True)
challenge_parser.add_argument('title', type=str, required=True)
challenge_parser.add_argument('description', type=str, required=True)
challenge_parser.add_argument('status', type=str, choices=['publish', 'private', 'draft'], default='publish')

getter_parser = reqparse.RequestParser()
getter_parser.add_argument('fetch', action='store_true')


class ChallengeList(Resource):
    def get(self):
        challenges = Challenge.query.all()
        return jsonify(list(map(lambda x: x.json, challenges)))

    def post(self):
        args = challenge_parser.parse_args()
        instance = Challenge(
            type=args['type'],
            title=args['title'],
            description=args['description']
        )

        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            res = jsonify({'message': 'Not logged in'})
            res.status_code = 401
            return res
        wp_challenge = WPChallenge.from_challenge(instance)

        try:
            wp_c = service.publish_challenge(wp_challenge, status=args['status'])
            instance.wp_id = wp_c.id
        except ForbiddenError:
            res = jsonify({'message': 'You do not have permission to publish a challenge'})
            res.status_code = 403
            return res
        except ServiceError:
            res = jsonify({'message': 'Could not publish challenge on usmgames.cl'})
            res.status_code = 500
            return res

        db.session.add(instance)
        db.session.commit()
        res = jsonify(instance.json)
        res.status_code = 200
        return res


class ChallengeInstance(Resource):
    def get(self, id: int):
        challenge = Challenge.query.filter_by(id=id).first()
        if challenge is None:
            res = jsonify({'message': 'No challenge with this id'})
            res.status_code = 404
            return res
        args = getter_parser.parse_args()
        data = challenge.json
        fetch_wp = args.get('fetch')
        if fetch_wp:
            if challenge.wp_id is None:
                return jsonify({'message': 'This challenge does not have an associated usmgames.cl challenge'}), 400
            service: WordPressService = g.wordpress
            wp_challenge = service.get_challenge(challenge.wp_id, challenge.type)
            data['wp'] = wp_challenge.json
        return jsonify(data)
