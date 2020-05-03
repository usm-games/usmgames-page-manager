import os

import pytest

from usmgpm.app import init_app


username = os.environ.get('TEST_USERNAME')
password = os.environ.get('TEST_PASSWORD')

admin_username = os.environ.get('TEST_ADMINNAME')
admin_password = os.environ.get('TEST_ADMINPASS')


@pytest.fixture()
def app():
    return init_app()


@pytest.mark.usefixtures('client_class')
class TestSubmissions:
    def test_submit(self):
        from usmgpm.models.challenge import ChallengeType
        from usmgpm.services import WordPressService

        cat_name = str(ChallengeType.MUSIC)
        test_challenge = {
            'type': cat_name,
            'title': f'A test {cat_name} challenge',
            'description': f'This is a test challenge; made for the {cat_name} category',
            'status': 'private',
            'requirements': ['Requirement 1', 'Requirement 2', 'Requirement 3'],
            'notify': False
        }

        service = WordPressService()
        service.login(admin_username, admin_password)
        headers = None
        if service.token:
            headers = {'Authorization': f'Bearer {service.token}'}

        challenge_id = self.client.post('/api/challenges', json=test_challenge, headers=headers).json['id']
        challenge_id_b = self.client.post('/api/challenges', json=test_challenge, headers=headers).json['id']

        submission = {
            'comment': "This is a test submission, let's hope it works",
            'evidence': [
                {'description': 'Evidence 1', 'url': 'http://example.com/1'},
                {'description': 'Evidence 2', 'url': 'http://example.com/2'},
                {'description': 'Evidence 3', 'url': 'http://example.com/3'},
                {'description': 'Evidence 4', 'url': 'http://example.com/4'}
            ]
        }

        service.login(username, password)
        headers = None
        if service.token:
            headers = {'Authorization': f'Bearer {service.token}'}
        res = self.client.post(f'/api/challenges/{challenge_id}/submissions', json=submission, headers=headers)

        user = service.me()
        assert res.status_code == 200
        submission_ = res.json
        assert submission_['user_id'] == user.id
        assert submission_['challenge_id'] == challenge_id

        res = self.client.post(f'/api/challenges/{challenge_id_b}/submissions', json=submission, headers=headers)
        assert res.status_code == 200
        submission_ = res.json
        assert submission_['user_id'] == user.id
        assert submission_['challenge_id'] == challenge_id_b

        # Evaluate without being an administrator
        evaluation = {
            'comment': 'Good job dude',
            'approved': True
        }
        res = self.client.post(f'/api/challenges/{challenge_id}/submissions/{user.id}/evaluate',
                               json=evaluation, headers=headers)
        assert res.status_code == 403

        # Evaluate without being logged in
        evaluation = {
            'comment': 'Good job dude',
            'approved': True
        }
        res = self.client.post(f'/api/challenges/{challenge_id}/submissions/{user.id}/evaluate',
                               json=evaluation)
        assert res.status_code == 401

        # Log-in as admin
        service.login(admin_username, admin_password)
        headers = None
        if service.token:
            headers = {'Authorization': f'Bearer {service.token}'}

        # Evaluate on approval of submission
        evaluation = {
            'comment': 'Good job dude',
            'approved': True
        }
        res = self.client.post(f'/api/challenges/{challenge_id}/submissions/{user.id}/evaluate',
                               json=evaluation, headers=headers)
        assert res.status_code == 200

        # Evaluate an already evaluated submission
        evaluation = {
            'comment': 'Sorry, you missed the second requirement :(',
            'approved': False
        }
        res = self.client.post(f'/api/challenges/{challenge_id}/submissions/{user.id}/evaluate',
                               json=evaluation, headers=headers)
        assert res.status_code == 400

        # Evaluate on rejection of submission
        evaluation = {
            'comment': 'Sorry, you missed the second requirement :(',
            'approved': False
        }
        res = self.client.post(f'/api/challenges/{challenge_id_b}/submissions/{user.id}/evaluate',
                               json=evaluation, headers=headers)
        assert res.status_code == 200

        # Check if submission is evaluated
        res = self.client.get(f'/api/challenges/{challenge_id}/submissions/{user.id}', headers=headers)
        assert res.status_code == 200
        assert res.json['evaluation'] is not None

        res = self.client.get(f'/api/challenges/{challenge_id_b}/submissions/{user.id}', headers=headers)
        assert res.status_code == 200
        assert res.json['evaluation'] is not None
