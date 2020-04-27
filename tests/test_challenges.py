import json
from tests import client


def test_empty_db(client):
    rv = client.get('/api/challenges')

    assert len(json.loads(rv.data)) == 0
