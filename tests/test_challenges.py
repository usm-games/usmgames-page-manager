import json
import os

import pytest

from usmgpm.models.requirement import ChallengeRequirement
from usmgpm.services import WordPressService
from usmgpm.app import init_app


username = os.environ.get('TEST_USERNAME')
password = os.environ.get('TEST_PASSWORD')

admin_username = os.environ.get('TEST_ADMINNAME')
admin_password = os.environ.get('TEST_ADMINPASS')


@pytest.fixture()
def app():
    return init_app(create_all=True, testing=True)


@pytest.mark.usefixtures('client_class')
class TestChallenges:
    def test_empty_db(self):
        service = WordPressService()
        service.login(username, password)
        rv = self.client.get('/api/challenges', headers={'Authorization': f'Bearer {service.token}'})

        assert rv.status_code == 200
        assert len(json.loads(rv.data)) == 0

    def test_publish_challenge(self):
        from usmgpm.models.challenge import ChallengeType

        service = WordPressService()

        def publish_challenge(cat_name: str, token: str = None):
            test_challenge = {
                'type': cat_name,
                'title': f'A test {cat_name} challenge',
                'description': f'This is a test challenge made for the {cat_name} category',
                'status': 'private',
                'requirements': ['Requirement 1', 'Requirement 2', 'Requirement 3'],
                'notify': False
            }
            headers = None
            if token:
                headers = {'Authorization': f'Bearer {token}'}
            return self.client.post('/api/challenges', json=test_challenge, headers=headers)

        res = publish_challenge('asdf')
        assert res.status_code == 400

        res = publish_challenge(str(ChallengeType.ART))
        assert res.status_code == 401

        service.login(username, password)
        res = publish_challenge(str(ChallengeType.ART), service.token)
        assert res.status_code == 403

        service.login(admin_username, admin_password)
        ids = list()
        for cat in ChallengeType:
            res = publish_challenge(str(cat), service.token)
            assert res.status_code == 200
            ids.append(json.loads(res.data)['id'])

        res = self.client.get('/api/challenges', headers={'Authorization': f'Bearer {service.token}'})
        assert res.status_code == 200
        challenges = json.loads(res.data)
        assert len(challenges) == len(ChallengeType)
        for c in challenges:
            assert len(c['requirements']) == 3

        for _id in ids:
            res = self.client.delete(f"/api/challenges/{_id}", headers={'Authorization': f'Bearer {service.token}'})
            assert res.status_code == 200

        res = self.client.get('/api/challenges', headers={'Authorization': f'Bearer {service.token}'})
        assert res.status_code == 200
        challenges = json.loads(res.data)
        assert len(challenges) == 0
        assert len(ChallengeRequirement.query.all()) == 0
