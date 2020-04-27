from flask import jsonify
from flask_restful import Resource, reqparse

from usmgpm.models.db import db
from usmgpm.models.challenge import Challenge, ChallengeType

__all__ = ['ChallengeList', 'ChallengeInstance']

challenge_parser = reqparse.RequestParser()
challenge_parser.add_argument('type', type=ChallengeType, choices=list(ChallengeType), required=True)
challenge_parser.add_argument('title', type=str, required=True)
challenge_parser.add_argument('description', type=str, required=True)


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
        db.session.add(instance)
        db.session.commit()
        return jsonify(instance.json)


class ChallengeInstance(Resource):
    def get(self, id: int):
        challenge = Challenge.query.filter_by(id=id).first()
        return jsonify(challenge.json)
