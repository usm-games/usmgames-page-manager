import validators

from flask import jsonify, g
from flask_restful import Resource, reqparse

from usmgpm.services.wp_models.wp_user import WPUser
from usmgpm.services import WordPressService

from usmgpm.models.db import db
from usmgpm.models.evaluation import Submission
from usmgpm.resources.utils import throw_error

evaluation_parser = reqparse.RequestParser()
evaluation_parser.add_argument('comment', type=str, required=True)
evaluation_parser.add_argument('approved', type=bool, required=True)

submission_parser = reqparse.RequestParser()
submission_parser.add_argument('comment', type=str, required=True)
submission_parser.add_argument('evidence', type=dict, required=True, action='append')

get_submission_parser = reqparse.RequestParser()
get_submission_parser.add_argument('not_evaluated', type=bool, required=False, default=False)


class ChallengeSubmissionList(Resource):
    def get(self, c_id: int):
        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')

        user: WPUser = g.user
        if not user.is_admin:
            return throw_error('PERMISSION_NEEDED')

        subs_q = Submission.query.filter(Submission.challenge_id == c_id).\
            order_by(Submission.submitted.desc())
        args = get_submission_parser.parse_args()
        if args['not_evaluated']:
            subs_q = subs_q.filter(Submission.approved.is_(None))
        subs: list = subs_q.all()
        return jsonify(list(map(lambda x: x.json, subs)))

    def post(self, c_id: int):
        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')
        user = service.me()

        sub: Submission = Submission.query. \
            filter(Submission.user_id == user.id). \
            filter(Submission.challenge_id == c_id). \
            first()
        if sub is not None:
            return throw_error('ALREADY_SUBMITTED')
        args = submission_parser.parse_args()
        evidences = list()
        for evidence in args['evidence']:
            evidence: dict = evidence
            description: str = evidence.get('description').replace(';', '')
            url: str = evidence.get('url').replace(';', '')
            if not validators.url(url):
                return throw_error('INVALID_URL', f'An evidence has an invalid url: {url}')
            if url and description:
                url = url.replace(';', '')
                description = description.replace(';', '')
                evidences.append(f'{url};{description}')
            else:
                return throw_error('MISSING_FIELDS', 'An evidence is missing a description or URL')

        comment = args['comment'].replace(';', '')
        content = ';'.join([comment] + evidences)

        sub = Submission(content=content, challenge_id=c_id, user_id=user.id)
        db.session.add(sub)
        db.session.commit()

        return jsonify(sub.json)


class UserSubmissionList(Resource):
    def get(self, u_id: int):
        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')

        user: WPUser = g.user
        if user.id != u_id and not user.is_admin:
            return throw_error('PERMISSION_NEEDED')

        subs_q = Submission.query.filter(Submission.user_id == u_id)
        args = get_submission_parser.parse_args()
        if args['not_evaluated']:
            subs_q = subs_q.filter(Submission.approved.is_(None))
        subs: list = subs_q.order_by(Submission.submitted.desc()).all()

        return jsonify(list(map(lambda x: x.json, subs)))


class ChallengeSubmission(Resource):
    def get(self, c_id: int, u_id: int):
        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')

        user: WPUser = g.user
        if user.id != u_id and not user.is_admin:
            return throw_error('PERMISSION_NEEDED')

        sub: Submission = Submission.query.\
            filter(Submission.user_id == u_id).\
            filter(Submission.challenge_id == c_id).\
            first()
        if sub is None:
            return throw_error('NOT_FOUND', 'No submission has been made by this user')
        else:
            return jsonify(sub.json)


class Evaluation(Resource):
    def post(self, c_id: int, u_id: int):
        service: WordPressService = g.wordpress
        if not service.is_logged_in:
            return throw_error('NEEDS_LOGIN')

        user: WPUser = g.user
        if not user.is_admin:
            return throw_error('PERMISSION_NEEDED')

        sub: Submission = Submission.query.\
            filter(Submission.user_id == u_id).\
            filter(Submission.challenge_id == c_id).\
            first()
        if sub is None:
            return throw_error('NOT_FOUND')

        if sub.approved is not None:
            return throw_error('ALREADY_EVALUATED')

        args = evaluation_parser.parse_args()
        comment, approved = args['comment'], args['approved']

        sub.evaluation_note = comment
        sub.approved = approved
        db.session.commit()

        return jsonify(sub.json)

    def put(self, c_id: int, u_id: int):
        if g.wordpress.is_logged_in:
            return throw_error('NEEDS_LOGIN')

        user: WPUser = g.user
        if not user.is_admin:
            return throw_error('PERMISSION_NEEDED')

        sub: Submission = Submission.query.\
            filter(Submission.user_id == u_id).\
            filter(Submission.challenge_id == c_id).\
            first()
        if sub.approved is None:
            return throw_error('NOT_EVALUATED')

        args = evaluation_parser.parse_args()
        comment, approved = args['comment'], args['approved']

        sub.evaluation_note = comment
        sub.approved = approved
        db.session.commit()

        return jsonify(sub.json)
