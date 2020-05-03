import validators

from flask import jsonify, g
from flask_restful import Resource, reqparse

from usmgpm.services import WordPressService
from usmgpm.services.exceptions import UnauthorizedError

from usmgpm.models.db import db
from usmgpm.models.evaluation import Submission

evaluation_parser = reqparse.RequestParser()
evaluation_parser.add_argument('comment', type=str, required=True)
evaluation_parser.add_argument('approved', type=bool, required=True)

submission_parser = reqparse.RequestParser()
submission_parser.add_argument('comment', type=str, required=True)
submission_parser.add_argument('evidence', type=dict, required=True, action='append')


class ChallengeSubmissionList(Resource):
    def get(self, c_id: int):
        subs: list = Submission.query.filter(Submission.challenge_id == c_id).all()
        return jsonify(list(map(lambda x: x.json, subs)))

    def post(self, c_id: int):
        service: WordPressService = g.wordpress
        try:
            user = service.me()
        except UnauthorizedError:
            res = jsonify({'message': 'Unauthorized user'})
            res.status_code = 401
            return res

        sub: Submission = Submission.query. \
            filter(Submission.user_id == user.id). \
            filter(Submission.challenge_id == c_id). \
            first()
        if sub is not None:
            res = jsonify({'message': 'You have already made a submission for this challenge'})
            res.status_code = 400
            return res
        args = submission_parser.parse_args()
        evidences = list()
        for evidence in args['evidence']:
            evidence: dict = evidence
            description: str = evidence.get('description').replace(';', '')
            url: str = evidence.get('url').replace(';', '')
            if not validators.url(url):
                res = jsonify({'mmessage': f'An evidence has an invalid url: {url}'})
                res.status_code = 400
                return res
            if url and description:
                url = url.replace(';', '')
                description = description.replace(';', '')
                evidences.append(f'{url};{description}')
            else:
                res = jsonify({'message': 'An evidence is missing a description or URL'})
                res.status_code = 400
                return res

        comment = args['comment'].replace(';', '')
        content = ';'.join([comment] + evidences)

        sub = Submission(content=content, challenge_id=c_id, user_id=user.id)
        db.session.add(sub)
        db.session.commit()

        return jsonify(sub.json)


class UserSubmissionList(Resource):
    def get(self, u_id: int):
        subs: list = Submission.query.filter(Submission.user_id == u_id).all()
        return jsonify(list(map(lambda x: x.json, subs)))


class ChallengeSubmission(Resource):
    def get(self, c_id: int, u_id: int):
        sub: Submission = Submission.query.\
            filter(Submission.user_id == u_id).\
            filter(Submission.challenge_id == c_id).\
            first()
        if sub is None:
            res = jsonify({'message': 'No submission has been made by this user'})
            res.status_code = 404
            return res
        else:
            return jsonify(sub.json)


class Evaluation(Resource):
    def post(self, c_id: int, u_id: int):
        service: WordPressService = g.wordpress
        try:
            user = service.me()
        except UnauthorizedError:
            res = jsonify({'message': 'You need to be authenticated to evaluate a submission'})
            res.status_code = 401
            return res

        if "administrator" not in user.roles:
            res = jsonify({'message': 'Only an administrator can evaluate a submission'})
            res.status_code = 403
            return res

        sub: Submission = Submission.query.\
            filter(Submission.user_id == u_id).\
            filter(Submission.challenge_id == c_id).\
            first()
        if sub.approved is not None:
            res = jsonify({'message': 'This submission has already been evaluated'})
            res.status_code = 400
            return res

        args = evaluation_parser.parse_args()
        comment, approved = args['comment'], args['approved']

        sub.evaluation_note = comment
        sub.approved = approved
        db.session.commit()

        return jsonify(sub.json)

    def put(self, c_id: int, u_id: int):
        service: WordPressService = g.wordpress
        try:
            user = service.me()
        except UnauthorizedError:
            res = jsonify({'message': 'You need to be authenticated to evaluate a submission'})
            res.status_code = 401
            return res

        if "administrator" not in user.roles:
            res = jsonify({'message': 'Only an administrator can evaluate a submission'})
            res.status_code = 403
            return res

        sub: Submission = Submission.query.\
            filter(Submission.user_id == u_id).\
            filter(Submission.challenge_id == c_id).\
            first()
        if sub.approved is None:
            res = jsonify({'message': 'This submission has not been evaluated'})
            res.status_code = 400
            return res

        args = evaluation_parser.parse_args()
        comment, approved = args['comment'], args['approved']

        sub.evaluation_note = comment
        sub.approved = approved
        db.session.commit()

        return jsonify(sub.json)
